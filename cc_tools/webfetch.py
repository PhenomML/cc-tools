import sys
import urllib.request
import urllib.error

MARKDOWN_NEW = "https://markdown.new/"


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: cc-webfetch <url>", file=sys.stderr)
        print("Fetch a public URL as clean Markdown via markdown.new.", file=sys.stderr)
        print("Output is written to stdout. Redirect to save: cc-webfetch <url> > file.md", file=sys.stderr)
        print("Rate limit: 500 requests/day per IP.", file=sys.stderr)
        sys.exit(0 if "--help" in sys.argv else 1)

    url = sys.argv[1]
    req = urllib.request.Request(
        MARKDOWN_NEW + url,
        headers={"User-Agent": "cc-tools/cc-webfetch"},
    )
    try:
        with urllib.request.urlopen(req) as response:
            sys.stdout.buffer.write(response.read())
    except urllib.error.HTTPError as e:
        print(f"cc-webfetch: HTTP {e.code} {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"cc-webfetch: {e.reason}", file=sys.stderr)
        sys.exit(1)
