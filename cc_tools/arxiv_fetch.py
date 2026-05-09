import json
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import arxiv


def _fetch_biorxiv(doi: str) -> None:
    for server in ("biorxiv", "medrxiv"):
        url = f"https://api.biorxiv.org/details/{server}/{doi}/json"
        req = urllib.request.Request(url, headers={"User-Agent": "cc-tools/cc-arxiv"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
        except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError) as e:
            print(f"cc-arxiv: {e}", file=sys.stderr)
            sys.exit(1)

        collection = data.get("collection", [])
        if not collection:
            continue

        paper = collection[-1]  # latest version
        pdf_url = f"https://www.biorxiv.org/content/{doi}.full.pdf"
        year = paper.get("date", "")[:4]

        print(f"ID:       {doi}")
        print(f"Title:    {paper.get('title', '')}")
        print(f"Authors:  {paper.get('authors', '')}")
        print(f"Year:     {year}")
        print(f"PDF:      {pdf_url}")
        print(f"HTML:     not available")
        print(f"Abstract: {paper.get('abstract', '')}")
        return

    print(f"cc-arxiv: no paper found for DOI {doi!r}", file=sys.stderr)
    sys.exit(1)


def _fetch_pubmed(pmid: str) -> None:
    url = (f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
           f"?db=pubmed&id={pmid}&rettype=xml&retmode=xml")
    req = urllib.request.Request(url, headers={"User-Agent": "cc-tools/cc-arxiv"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            tree = ET.parse(resp)
    except (urllib.error.HTTPError, urllib.error.URLError, ET.ParseError) as e:
        print(f"cc-arxiv: {e}", file=sys.stderr)
        sys.exit(1)

    root = tree.getroot()
    article = root.find(".//PubmedArticle/MedlineCitation/Article")
    if article is None:
        print(f"cc-arxiv: no article found for PMID {pmid!r}", file=sys.stderr)
        sys.exit(1)

    title = article.findtext("ArticleTitle", "").strip()

    authors = []
    for author in article.findall(".//AuthorList/Author"):
        last = author.findtext("LastName", "")
        initials = author.findtext("Initials", "")
        if last:
            authors.append(f"{last} {initials}".strip())
    authors_str = "; ".join(authors)

    pub_date = article.find(".//Journal/JournalIssue/PubDate")
    year = ""
    if pub_date is not None:
        year = pub_date.findtext("Year", "") or (pub_date.findtext("MedlineDate", "") or "")[:4]

    doi = ""
    for id_elem in root.findall(".//PubmedData/ArticleIdList/ArticleId"):
        if id_elem.get("IdType") == "doi":
            doi = id_elem.text or ""
            break

    pdf_url = f"https://doi.org/{doi}" if doi else f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

    abstract_parts = article.findall(".//Abstract/AbstractText")
    if abstract_parts:
        chunks = []
        for p in abstract_parts:
            label = p.get("Label", "")
            text = "".join(p.itertext())
            chunks.append(f"{label}: {text}" if label else text)
        abstract = " ".join(chunks)
    else:
        abstract = "not available"

    print(f"ID:       {pmid}")
    print(f"Title:    {title}")
    print(f"Authors:  {authors_str}")
    print(f"Year:     {year}")
    print(f"PDF:      {pdf_url}")
    print(f"HTML:     not available")
    print(f"Abstract: {abstract}")


def _fetch_crossref(doi: str) -> None:
    encoded = urllib.parse.quote(doi, safe="/")
    url = f"https://api.crossref.org/works/{encoded}"
    req = urllib.request.Request(url, headers={"User-Agent": "cc-tools/cc-arxiv"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"cc-arxiv: no work found for DOI {doi!r}", file=sys.stderr)
        else:
            print(f"cc-arxiv: {e}", file=sys.stderr)
        sys.exit(1)
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"cc-arxiv: {e}", file=sys.stderr)
        sys.exit(1)

    msg = data.get("message", {})
    titles = msg.get("title", [])
    title = titles[0] if titles else ""

    authors_raw = msg.get("author", [])
    authors_str = "; ".join(
        f"{a.get('given', '')} {a.get('family', '')}".strip() for a in authors_raw
    )

    date_parts = msg.get("published", {}).get("date-parts", [[]])[0]
    year = str(date_parts[0]) if date_parts else ""

    pdf_url = f"https://doi.org/{doi}"
    for link in msg.get("link", []):
        if link.get("content-type") == "application/pdf":
            pdf_url = link["URL"]
            break

    raw_abstract = msg.get("abstract", "")
    abstract = re.sub(r"<[^>]+>", "", raw_abstract).strip() if raw_abstract else "not available"

    print(f"ID:       {doi}")
    print(f"Title:    {title}")
    print(f"Authors:  {authors_str}")
    print(f"Year:     {year}")
    print(f"PDF:      {pdf_url}")
    print(f"HTML:     not available")
    print(f"Abstract: {abstract}")


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
        print("Usage: cc-arxiv <arxiv-id|biorxiv-doi|pmid|doi>", file=sys.stderr)
        print("Fetch metadata for a preprint or published paper.", file=sys.stderr)
        print("  arXiv ID:            2301.07608", file=sys.stderr)
        print("  bioRxiv/medRxiv DOI: 10.1101/2024.01.12.574717", file=sys.stderr)
        print("  PubMed PMID:         12345678", file=sys.stderr)
        print("  Any DOI (CrossRef):  10.1038/s41586-024-00001-0", file=sys.stderr)
        print("Outputs: ID, title, authors, year, PDF URL, HTML availability, abstract.", file=sys.stderr)
        sys.exit(0 if "--help" in sys.argv else 1)

    paper_id = sys.argv[1]

    if paper_id.startswith("10.1101/"):
        _fetch_biorxiv(paper_id)
        return 0

    if paper_id.isdigit():
        _fetch_pubmed(paper_id)
        return 0

    if paper_id.startswith("10.") and "/" in paper_id:
        _fetch_crossref(paper_id)
        return 0

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
