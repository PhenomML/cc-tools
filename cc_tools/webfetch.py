import sys
import urllib.parse
import urllib.request
import urllib.error

MARKDOWN_NEW = "https://markdown.new/"
MIN_CONTENT_BYTES = 500
CLOUDFLARE_MARKERS = [b"just a moment", b"cf-ray", b"cloudflare", b"checking your browser"]

# Workaround (commit 424e94f): markdown.new (a Cloudflare service) is blocked by
# other CF-protected sites. Skip both markdown.new and Wayback for known-blocked
# domains and advise alternatives instead. Remove entries here and in _CF_BLOCKED_ADVICE
# when markdown.new resolves CF-to-CF blocking.
# Tracked in: https://github.com/PhenomML/cc-tools/issues/3
# Upstream bug: https://github.com/markdown-new/url-to-markdown-skill/issues/1
_KNOWN_CF_BLOCKED = {
    "scholar.google.com",
    "api.semanticscholar.org",
}

_CF_BLOCKED_ADVICE = {
    "scholar.google.com": (
        "Google Scholar is structurally blocked (Cloudflare-to-Cloudflare).\n"
        "Alternatives:\n"
        "  cc-arxiv <arxiv-id>   — paper metadata by arXiv ID\n"
        "  cc-webfetch 'https://export.arxiv.org/api/query?search_query=all:TERM&max_results=10'\n"
        "  cc-webfetch 'https://api.semanticscholar.org/graph/v1/paper/search"
        "?query=TERM&fields=title,authors,year,abstract,externalIds'"
    ),
    "api.semanticscholar.org": (
        "Semantic Scholar is structurally blocked via markdown.new (Cloudflare-to-Cloudflare).\n"
        "Use the API directly — it works without markdown.new:\n"
        "  cc-webfetch 'https://api.semanticscholar.org/graph/v1/paper/search"
        "?query=TERM&fields=title,authors,year,abstract,externalIds'"
    ),
}


def _strip_wayback_boilerplate(content: bytes) -> bytes:
    """Strip Archive.org toolbar boilerplate that precedes the archived content.

    markdown.new renders the full Wayback page, including Archive.org navigation
    and notices, before the actual article. We keep the URL Source header and
    everything from the first markdown heading onward.
    """
    try:
        text = content.decode("utf-8", errors="replace")
    except Exception:
        return content

    lines = text.splitlines(keepends=True)
    if not lines:
        return content

    # Preserve URL Source header lines at the top (up to the first blank line).
    header: list[str] = []
    body_start = 0
    for i, line in enumerate(lines[:3]):
        if line.startswith("URL Source:") or (header and not line.strip()):
            header.append(line)
            body_start = i + 1
        else:
            break

    # Find the first markdown heading in the body and drop everything before it.
    for i, line in enumerate(lines[body_start:], body_start):
        if line.startswith("#"):
            return "".join(header + lines[i:]).encode("utf-8")

    return content  # No heading found; return unchanged.


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

    domain = urllib.parse.urlparse(url).netloc.removeprefix("www.")
    if domain in _KNOWN_CF_BLOCKED:
        advice = _CF_BLOCKED_ADVICE.get(domain, "Use a direct API or alternative source.")
        print(f"cc-webfetch: {advice}", file=sys.stderr)
        sys.exit(1)

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
        wayback_content = _strip_wayback_boilerplate(wayback_content)
        print(f"cc-webfetch: served from Wayback Machine ({len(wayback_content)} bytes, boilerplate stripped)", file=sys.stderr)
        content = wayback_content

    sys.stdout.buffer.write(content)
