import sys
import json
import re
import subprocess
import argparse
from pathlib import Path
from urllib.parse import urlparse

CHROME_PREF_PATH = Path.home() / "Library/Application Support/Google/Chrome/Default/Preferences"
DEFAULT_DELAY = 7
DOMAINS_FILENAME = ".credentialed-domains"


def find_domains_file() -> Path | None:
    current = Path.cwd().resolve()
    while True:
        candidate = current / DOMAINS_FILENAME
        if candidate.exists():
            return candidate
        parent = current.parent
        if parent == current:
            return None
        current = parent


def load_allowed_domains(path: Path) -> set[str]:
    domains = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            domains.add(line.lower())
    return domains


def is_domain_allowed(url: str, allowed: set[str]) -> bool:
    try:
        hostname = (urlparse(url).hostname or "").lower()
    except Exception:
        hostname = ""
    return any(hostname == d or hostname.endswith("." + d) for d in allowed)


def check_apple_events_enabled() -> bool | None:
    try:
        with open(CHROME_PREF_PATH) as f:
            prefs = json.load(f)
        return prefs.get("browser", {}).get("allow_javascript_apple_events", False)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _slug_from_url(url: str) -> str:
    try:
        parsed = urlparse(url)
        host = parsed.hostname or "unknown"
        path = parsed.path.strip("/").replace("/", "-") or "index"
        slug = f"{host}-{path}"
    except Exception:
        slug = "fetched"
    return re.sub(r"[^\w\-.]", "-", slug)[:80]


def fetch_via_chrome(url: str, delay: int) -> tuple[str | None, str]:
    # AppleScript does not support backslash escaping inside string literals.
    # Double-quotes in URLs must be rejected rather than escaped.
    if '"' in url:
        return None, "URL contains a literal double-quote character — invalid URL"
    script = f'''
tell application "Google Chrome"
    if (count windows) is 0 then
        error "No Chrome windows open — open a Chrome window first"
    end if
    set newTab to make new tab at end of tabs of window 1
    set URL of newTab to "{url}"
    delay {delay}
    set tabContent to execute newTab javascript "document.body.innerText"
    if tabContent is missing value or tabContent is "" then
        delay {delay * 2}
        set tabContent to execute newTab javascript "document.body.innerText"
    end if
    delete newTab
    return tabContent
end tell
'''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=delay * 5,
        )
    except subprocess.TimeoutExpired:
        return None, f"timed out after {delay * 5}s"

    if result.returncode != 0:
        return None, f"AppleScript error: {result.stderr.strip()}"

    content = result.stdout.strip()
    if not content or content == "missing value":
        return None, "empty response (page may not have loaded — try --delay with a larger value)"

    return content, f"{len(content.encode('utf-8'))} bytes"


def disable_apple_events() -> tuple[bool, str]:
    """Attempt to disable Apple Events access in Chrome's Preferences JSON.

    Chrome may overwrite this change while running; the caller should instruct
    the user to verify via the menu and restart Chrome to confirm.
    """
    try:
        with open(CHROME_PREF_PATH) as f:
            prefs = json.load(f)
        if not prefs.get("browser", {}).get("allow_javascript_apple_events", False):
            return True, "already disabled"
        prefs.setdefault("browser", {})["allow_javascript_apple_events"] = False
        with open(CHROME_PREF_PATH, "w") as f:
            json.dump(prefs, f)
        return True, "disabled"
    except FileNotFoundError:
        return False, "Chrome preferences file not found"
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(
        prog="cc-credentialed-fetch",
        description=(
            "Fetch URLs using Chrome's authenticated browser session.\n\n"
            "Prerequisites:\n"
            "  1. Chrome open with at least one window\n"
            "  2. View → Developer → Allow JavaScript from Apple Events  (enabled)\n"
            "  3. .credentialed-domains file in your wiki root listing allowed domains\n\n"
            "Security: disable 'Allow JavaScript from Apple Events' when done."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("urls", nargs="*", help="URL(s) to fetch")
    parser.add_argument(
        "--delay", type=int, default=DEFAULT_DELAY,
        help=f"Seconds to wait for page load (default: {DEFAULT_DELAY}; retry uses 2×)",
    )
    parser.add_argument(
        "--url-file", metavar="FILE",
        help="File of URLs to fetch (one per line; # comments ignored)",
    )
    parser.add_argument(
        "--output-dir", metavar="DIR",
        help="Directory to write fetched files; required when fetching multiple URLs",
    )
    args = parser.parse_args()

    # Collect URLs
    urls = list(args.urls)
    if args.url_file:
        try:
            for line in Path(args.url_file).read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)
        except FileNotFoundError:
            print(f"cc-credentialed-fetch: file not found: {args.url_file}", file=sys.stderr)
            sys.exit(1)

    if not urls:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if len(urls) > 1 and not args.output_dir:
        print(
            "cc-credentialed-fetch: --output-dir is required when fetching multiple URLs",
            file=sys.stderr,
        )
        sys.exit(1)

    # Locate per-wiki allowlist
    domains_file = find_domains_file()
    if domains_file is None:
        print(
            f"cc-credentialed-fetch: no {DOMAINS_FILENAME} found in this directory or any parent.\n"
            f"Create one in your wiki root with one allowed domain per line.",
            file=sys.stderr,
        )
        sys.exit(1)

    allowed = load_allowed_domains(domains_file)
    if not allowed:
        print(
            f"cc-credentialed-fetch: {domains_file} contains no domains — add allowed domains (one per line).",
            file=sys.stderr,
        )
        sys.exit(1)

    # Allowlist check — fail fast before touching Chrome
    blocked = [u for u in urls if not is_domain_allowed(u, allowed)]
    if blocked:
        print("cc-credentialed-fetch: domain(s) not in allowlist:", file=sys.stderr)
        for u in blocked:
            print(f"  {u}", file=sys.stderr)
        print(f"Add the domain(s) to {domains_file} to proceed.", file=sys.stderr)
        sys.exit(1)

    # Pre-flight: verify Apple Events permission
    apple_events_on = check_apple_events_enabled()
    if apple_events_on is False:
        print(
            "cc-credentialed-fetch: 'Allow JavaScript from Apple Events' is disabled in Chrome.\n"
            "Enable it: Chrome → View → Developer → Allow JavaScript from Apple Events\n"
            "Then re-run this command.",
            file=sys.stderr,
        )
        sys.exit(1)
    if apple_events_on is None:
        print(
            "cc-credentialed-fetch: could not read Chrome preferences — proceeding.\n"
            "Ensure Chrome has View → Developer → Allow JavaScript from Apple Events enabled.",
            file=sys.stderr,
        )

    # Output dir
    out_dir = Path(args.output_dir) if args.output_dir else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"cc-credentialed-fetch: {len(urls)} URL(s)  delay={args.delay}s  allowlist={domains_file}",
        file=sys.stderr,
    )

    # Fetch loop
    failed = 0
    for i, url in enumerate(urls, 1):
        print(f"  [{i}/{len(urls)}] {url} ... ", file=sys.stderr, end="", flush=True)
        content, status = fetch_via_chrome(url, args.delay)
        print(status, file=sys.stderr)

        if content is None:
            failed += 1
            continue

        if out_dir:
            out_path = out_dir / f"{_slug_from_url(url)}.md"
            out_path.write_text(content, encoding="utf-8")
            print(f"      → {out_path}", file=sys.stderr)
        else:
            sys.stdout.write(content)

    # Summary for multi-URL runs
    if len(urls) > 1:
        n_ok = len(urls) - failed
        print(
            f"\ncc-credentialed-fetch: {n_ok}/{len(urls)} succeeded"
            + (f", {failed} failed" if failed else ""),
            file=sys.stderr,
        )

    # Post-fetch: attempt to disable Apple Events automatically
    if apple_events_on:
        ok, msg = disable_apple_events()
        if ok and msg == "already disabled":
            pass  # nothing to do
        elif ok:
            print(
                "\nSECURITY: Apple Events access disabled in Chrome preferences.\n"
                "Restart Chrome to confirm, then verify:\n"
                "  Chrome → View → Developer → Allow JavaScript from Apple Events  (should be unchecked)",
                file=sys.stderr,
            )
        else:
            print(
                f"\nSECURITY: could not auto-disable Apple Events ({msg}).\n"
                "Disable manually now:\n"
                "  Chrome → View → Developer → Allow JavaScript from Apple Events  (uncheck)",
                file=sys.stderr,
            )

    sys.exit(1 if failed else 0)
