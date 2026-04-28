import sys
import trafilatura

MIN_WORDS = 50


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: cc-fetch <url>", file=sys.stderr)
        print("Fetch a public URL as clean Markdown via local Readability extraction.", file=sys.stderr)
        print("No rate limit. Does not handle JS-rendered pages — use cc-webfetch for those.", file=sys.stderr)
        print("Output is written to stdout. Redirect to save: cc-fetch <url> > file.md", file=sys.stderr)
        sys.exit(0 if "--help" in sys.argv else 1)

    url = sys.argv[1]

    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        print(f"cc-fetch: failed to fetch {url}", file=sys.stderr)
        sys.exit(1)

    result = trafilatura.extract(downloaded, output_format="markdown")
    if not result or len(result.split()) < MIN_WORDS:
        print(
            f"cc-fetch: no content extracted from {url} — page may be JS-rendered. Try: cc-webfetch {url}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"URL Source: {url}\n")
    print(result)
