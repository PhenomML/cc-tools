import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

S2_BASE = "https://api.semanticscholar.org/graph/v1"
SEARCH_FIELDS = "title,abstract,authors,year,citationCount,externalIds,openAccessPdf"
PAPER_FIELDS = "title,abstract,authors,year,citationCount,externalIds,venue,openAccessPdf"
SEARCH_LIMIT = 10
ABSTRACT_PREVIEW = 300


MAX_RETRIES = 3
BACKOFF_BASE = 5  # seconds: 5, 15, 45


def _get(path: str, params: dict) -> dict:
    url = f"{S2_BASE}/{path}?" + urllib.parse.urlencode(params)
    headers = {"User-Agent": "cc-tools/cc-semantic-scholar"}
    api_key = os.environ.get("S2_API_KEY", "")
    if api_key:
        headers["x-api-key"] = api_key
    req = urllib.request.Request(url, headers=headers)

    for attempt in range(MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < MAX_RETRIES:
                wait = BACKOFF_BASE * (3 ** attempt)
                print(
                    f"cc-semantic-scholar: rate limited — retrying in {wait}s "
                    f"({attempt + 1}/{MAX_RETRIES})",
                    file=sys.stderr,
                )
                time.sleep(wait)
                continue
            body = ""
            try:
                body = e.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            raise RuntimeError(f"HTTP {e.code}: {body[:200] or e.reason}")
        except urllib.error.URLError as e:
            raise RuntimeError(str(e.reason))

    raise RuntimeError("rate limited after retries — set S2_API_KEY for higher limits")


def _format_authors(authors: list) -> str:
    names = [a.get("name", "") for a in authors]
    if len(names) > 5:
        return "; ".join(names[:5]) + f"; ... (+{len(names) - 5} more)"
    return "; ".join(names)


def _pdf_url(paper: dict) -> str:
    oap = paper.get("openAccessPdf") or {}
    if oap.get("url"):
        return oap["url"]
    ext = paper.get("externalIds") or {}
    if ext.get("ArXiv"):
        return f"https://arxiv.org/pdf/{ext['ArXiv']}"
    if ext.get("DOI"):
        return f"https://doi.org/{ext['DOI']}"
    return ""


def _search(query: str) -> None:
    data = _get("paper/search", {"query": query, "fields": SEARCH_FIELDS, "limit": SEARCH_LIMIT})
    total = data.get("total", 0)
    papers = data.get("data", [])

    if not papers:
        print(f"cc-semantic-scholar: no results for {query!r}", file=sys.stderr)
        sys.exit(1)

    print(f"# Semantic Scholar: {query}\n")
    print(f"*{total:,} total results, showing {len(papers)}*\n")

    for i, paper in enumerate(papers, 1):
        ext = paper.get("externalIds") or {}
        arxiv = ext.get("ArXiv", "")
        doi = ext.get("DOI", "")
        year = paper.get("year") or ""
        citations = paper.get("citationCount") or 0
        title = paper.get("title", "")
        authors = _format_authors(paper.get("authors", []))
        abstract = (paper.get("abstract") or "").strip()
        if len(abstract) > ABSTRACT_PREVIEW:
            abstract = abstract[:ABSTRACT_PREVIEW].rstrip() + "…"

        ids = []
        if arxiv:
            ids.append(f"ARXIV:{arxiv}")
        if doi:
            ids.append(f"DOI:{doi}")

        print(f"## {i}. {title}")
        print(f"**{year}** · {citations:,} citations · *{authors}*")
        if ids:
            print("`" + "` · `".join(ids) + "`")
        if abstract:
            print(f"\n{abstract}")
        print()


def _lookup(paper_id: str) -> None:
    data = _get(f"paper/{urllib.parse.quote(paper_id, safe=':/')}", {"fields": PAPER_FIELDS})

    ext = data.get("externalIds") or {}
    arxiv = ext.get("ArXiv", "")
    doi = ext.get("DOI", "")
    year = data.get("year") or ""
    citations = data.get("citationCount") or 0
    venue = data.get("venue") or ""
    abstract = (data.get("abstract") or "").strip()
    pdf = _pdf_url(data)

    print(f"Title:     {data.get('title', '')}")
    print(f"Authors:   {_format_authors(data.get('authors', []))}")
    print(f"Year:      {year}")
    print(f"Citations: {citations:,}")
    if venue:
        print(f"Venue:     {venue}")
    if arxiv:
        print(f"arXiv:     {arxiv}")
    if doi:
        print(f"DOI:       {doi}")
    if pdf:
        print(f"PDF:       {pdf}")
    if abstract:
        print(f"Abstract:  {abstract}")


def _is_paper_id(arg: str) -> bool:
    prefixes = ("ARXIV:", "DOI:", "MAG:", "ACL:", "PMID:", "PMCID:", "CorpusId:")
    if any(arg.upper().startswith(p.upper()) for p in prefixes):
        return True
    return len(arg) == 40 and all(c in "0123456789abcdefABCDEF" for c in arg)


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: cc-semantic-scholar <query>", file=sys.stderr)
        print("       cc-semantic-scholar <paper-id>", file=sys.stderr)
        print("Search Semantic Scholar or look up a specific paper.", file=sys.stderr)
        print("Paper ID formats: ARXIV:2505.00326  DOI:10.x/y  CorpusId:nnn", file=sys.stderr)
        print("Output is written to stdout.", file=sys.stderr)
        print("Rate limit: set S2_API_KEY in env for 1 req/s; unauthenticated is ~100/5min.", file=sys.stderr)
        print("Apply: https://www.semanticscholar.org/product/api", file=sys.stderr)
        sys.exit(0 if "--help" in sys.argv else 1)

    arg = sys.argv[1]

    try:
        if _is_paper_id(arg):
            _lookup(arg)
        else:
            _search(arg)
    except RuntimeError as e:
        print(f"cc-semantic-scholar: {e}", file=sys.stderr)
        sys.exit(1)
