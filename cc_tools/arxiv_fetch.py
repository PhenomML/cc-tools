import sys
import time
import urllib.request
import urllib.error
import arxiv


def _html_available(base_id: str) -> bool:
    url = f"https://arxiv.org/html/{base_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "cc-tools/cc-arxiv"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return b"No HTML" not in resp.read(512)
    except (urllib.error.HTTPError, urllib.error.URLError):
        return False


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: cc-arxiv <arxiv-id>", file=sys.stderr)
        print("Fetch metadata for an arXiv paper by ID.", file=sys.stderr)
        print("Outputs: ID, title, authors, year, PDF URL, HTML availability, abstract.", file=sys.stderr)
        sys.exit(0 if "--help" in sys.argv else 1)

    paper_id = sys.argv[1]
    client = arxiv.Client()
    results = None
    for attempt in range(3):
        try:
            results = list(client.results(arxiv.Search(id_list=[paper_id])))
            break
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                wait = (attempt + 1) * 10
                print(f"cc-arxiv: rate limited (429), retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
            else:
                print(f"cc-arxiv: {e}", file=sys.stderr)
                sys.exit(1)
    if results is None:
        print("cc-arxiv: failed after retries", file=sys.stderr)
        sys.exit(1)

    if not results:
        print(f"cc-arxiv: no paper found for ID {paper_id!r}", file=sys.stderr)
        sys.exit(1)

    paper = results[0]
    short_id = paper.get_short_id()
    base_id = short_id.split("v")[0]
    html_url = f"https://arxiv.org/html/{base_id}"
    html_note = "available" if _html_available(base_id) else "not available"
    authors = "; ".join(a.name for a in paper.authors)

    print(f"ID:       {short_id}")
    print(f"Title:    {paper.title}")
    print(f"Authors:  {authors}")
    print(f"Year:     {paper.published.year}")
    print(f"PDF:      {paper.pdf_url}")
    print(f"HTML:     {html_url}  ({html_note})")
    print(f"Abstract: {paper.summary}")
