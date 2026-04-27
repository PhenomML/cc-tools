import sys
import urllib.request
import urllib.error

MARKDOWN_NEW = "https://markdown.new/"
MIN_CONTENT_BYTES = 500
CLOUDFLARE_MARKERS = [b"just a moment", b"cf-ray", b"cloudflare", b"checking your browser"]


def _fetch_via_markdown_new(url: str) -> bytes:
    req = urllib.request.Request(
        MARKDOWN_NEW + url,
        headers={"User-Agent": "cc-tools/cc-webfetch"},
    )
    with urllib.request.urlopen(req) as response:
        return response.read()


def _is_blocked(content: bytes) -> bool:
    if len(content) < MIN_CONTENT_BYTES:
        return True
    lower = content.lower()
    return any(marker in lower for marker in CLOUDFLARE_MARKERS)


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: cc-webfetch <url>", file=sys.stderr)
        print("Fetch a public URL as clean Markdown via markdown.new.", file=sys.stderr)
        print("Falls back to Wayback Machine if the direct fetch is blocked.", file=sys.stderr)
        print("Output is written to stdout. Redirect to save: cc-webfetch <url> > file.md", file=sys.stderr)
        print("Rate limit: 500 requests/day per IP.", file=sys.stderr)
        sys.exit(0 if "--help" in sys.argv else 1)

    url = sys.argv[1]
    try:
        content = _fetch_via_markdown_new(url)
    except urllib.error.HTTPError as e:
        print(f"cc-webfetch: HTTP {e.code} {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"cc-webfetch: {e.reason}", file=sys.stderr)
        sys.exit(1)

    if _is_blocked(content):
        print(
            f"cc-webfetch: BLOCKED (Cloudflare or thin response, {len(content)} bytes) — trying Wayback Machine",
            file=sys.stderr,
        )
        wayback_url = f"https://web.archive.org/web/{url}"
        try:
            wayback_content = _fetch_via_markdown_new(wayback_url)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            print(f"cc-webfetch: Wayback fetch failed: {e}", file=sys.stderr)
            sys.exit(1)
        if _is_blocked(wayback_content):
            print(
                f"cc-webfetch: Wayback also blocked or empty ({len(wayback_content)} bytes) — use cc-credentialed-fetch for credentialed access",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"cc-webfetch: served from Wayback Machine ({len(wayback_content)} bytes)", file=sys.stderr)
        content = wayback_content

    sys.stdout.buffer.write(content)
