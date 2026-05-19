import subprocess
import sys
import time

import trafilatura

LOAD_POLL_INTERVAL = 0.5
LOAD_TIMEOUT = 30.0
POST_LOAD_SETTLE = 5.0  # extra wait after readyState=complete for JS-rendered content
MIN_WORDS = 50


def _run(script: str) -> subprocess.CompletedProcess:
    return subprocess.run(["osascript", "-e", script], capture_output=True, text=True)


def _open_url(url: str) -> None:
    script = f"""
tell application "Safari"
    if (count of windows) = 0 then
        make new document with properties {{URL:"{url}"}}
    else
        tell window 1
            set current tab to (make new tab with properties {{URL:"{url}"}})
        end tell
    end if
end tell
"""
    r = _run(script)
    if r.returncode != 0:
        raise RuntimeError(f"Safari navigation failed: {r.stderr.strip()}")


def _wait_for_load() -> None:
    deadline = time.monotonic() + LOAD_TIMEOUT
    while time.monotonic() < deadline:
        r = _run(
            'tell application "Safari" to do JavaScript "document.readyState" in current tab of window 1'
        )
        if r.returncode == 0 and r.stdout.strip() == "complete":
            return
        if r.returncode != 0 and "apple events" in r.stderr.lower():
            raise RuntimeError(
                "Safari JavaScript from Apple Events is not enabled.\n"
                "  Enable: Safari → Settings → Developer → Allow JavaScript from Apple Events"
            )
        time.sleep(LOAD_POLL_INTERVAL)
    raise TimeoutError(f"page did not finish loading within {LOAD_TIMEOUT}s")


def _extract_html() -> str:
    r = _run(
        'tell application "Safari" to set the clipboard to '
        '(do JavaScript "document.documentElement.outerHTML" in current tab of window 1)'
    )
    if r.returncode != 0:
        err = r.stderr.strip()
        if "not allowed" in err.lower() or "apple events" in err.lower():
            raise RuntimeError(
                "Safari JavaScript from Apple Events is not enabled.\n"
                "  Enable: Safari → Develop → Allow JavaScript from Apple Events"
            )
        raise RuntimeError(f"HTML extraction failed: {err}")
    return subprocess.run(["pbpaste"], capture_output=True, text=True).stdout


def _close_tab() -> None:
    _run('tell application "Safari" to tell window 1 to close current tab')


def main():
    args = sys.argv[1:]
    settle = POST_LOAD_SETTLE

    if "--wait" in args:
        idx = args.index("--wait")
        try:
            settle = float(args[idx + 1])
            args = args[:idx] + args[idx + 2:]
        except (IndexError, ValueError):
            print("cc-safari-fetch: --wait requires a number of seconds", file=sys.stderr)
            sys.exit(1)

    if len(args) != 1 or args[0] in ("-h", "--help"):
        print("Usage: cc-safari-fetch [--wait N] <url>", file=sys.stderr)
        print("Fetch a URL via Safari using your session and credentials.", file=sys.stderr)
        print("  --wait N   seconds to wait after page load for JS rendering (default: 5)", file=sys.stderr)
        print("Requires: Safari open; Develop → Allow JavaScript from Apple Events enabled.", file=sys.stderr)
        print("Output is written to stdout.", file=sys.stderr)
        sys.exit(0 if "--help" in args else 1)

    url = args[0]

    try:
        _open_url(url)
        _wait_for_load()
        if settle > 0:
            print(f"cc-safari-fetch: waiting {settle:.0f}s for JS rendering…", file=sys.stderr)
            time.sleep(settle)
        html = _extract_html()
    except (RuntimeError, TimeoutError) as e:
        print(f"cc-safari-fetch: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        _close_tab()

    if not html.strip():
        print("cc-safari-fetch: no content extracted", file=sys.stderr)
        sys.exit(1)

    result = trafilatura.extract(html, output_format="markdown", url=url)
    if not result or len(result.split()) < MIN_WORDS:
        print("cc-safari-fetch: trafilatura extraction thin — writing raw HTML", file=sys.stderr)
        print(html)
        return

    print(f"URL Source: {url}\n")
    print(result)
