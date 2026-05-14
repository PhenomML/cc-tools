import html as _html
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
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


def _find_root_tex(directory: str) -> str | None:
    candidates = []
    for dirpath, _, filenames in os.walk(directory):
        for fname in filenames:
            if not fname.endswith(".tex"):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, "rb") as f:
                    chunk = f.read(8192)
                if b"\\documentclass" in chunk:
                    candidates.append(fpath)
            except OSError:
                pass
    if not candidates:
        return None
    return min(candidates, key=lambda p: p.count(os.sep))


def _normalize_make4ht_html(html: str) -> str:
    # make4ht wraps display math in <div class='mathjax-env ...'>.
    # Pandoc recognizes <script type="math/tex; mode=display"> as display math
    # and outputs $$...$$ with no escaping. div.math.display outputs a fenced div
    # with escaped content, so we use script tags instead.
    # Leave inline spans alone — +tex_math_single_backslash handles \(...\).
    def _to_script(m: re.Match) -> str:
        # HTML-unescape content: div content is HTML-escaped, script content is raw
        content = _html.unescape(m.group(1))
        return f'<script type="math/tex; mode=display">{content}</script>'

    return re.sub(
        r"<div class=['\"]mathjax-env[^'\"]*['\"]>(.*?)</div>",
        _to_script,
        html,
        flags=re.DOTALL,
    )


def _extract_preamble_macros(tex_path: str) -> str:
    """Extract math macro definitions from TeX preamble as a MathJax $$-block."""
    macros = []
    try:
        with open(tex_path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if r"\begin{document}" in line:
                    break
                stripped = line.strip()
                if re.match(r"\\(newcommand|renewcommand|providecommand|DeclareMathOperator)\b|\\def\\", stripped):
                    macros.append(stripped)
    except OSError:
        return ""
    if not macros:
        return ""
    return "$$\n" + "\n".join(macros) + "\n$$\n\n"


def _post_process_src(content: str, arxiv_id: str, macro_block: str = "") -> str:
    # HTML entities in raw-HTML passthrough blocks (algorithm listings, captions)
    content = content.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    # CSS class spans from make4ht: [text]{.ClassName} -> text
    content = re.sub(r"\[([^\]]*)\]\{\.[\w-]+\}", r"\1", content)
    # Style attributes
    content = re.sub(r'\{style="[^"]*"\}', "", content)
    # Div block markers (::: mathjax-block etc.)
    content = re.sub(r"^:+\s*\S.*$", "", content, flags=re.MULTILINE)
    content = re.sub(r"^:+\s*$", "", content, flags=re.MULTILINE)
    # Collapse excess blank lines
    content = re.sub(r"\n{3,}", "\n\n", content)
    header = f"<!-- Source: arXiv:{arxiv_id} TeX source tarball via make4ht+mathjax. Math fidelity: high. -->\n\n"
    return header + macro_block + content.strip() + "\n"


def _src_to_markdown(arxiv_id: str) -> str:
    url = f"https://arxiv.org/src/{arxiv_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "cc-tools/cc-arxiv"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            src_data = resp.read()
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        raise RuntimeError(f"source download failed: {e}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tarpath = os.path.join(tmpdir, "src.tar.gz")
        with open(tarpath, "wb") as f:
            f.write(src_data)

        try:
            with tarfile.open(tarpath) as tar:
                tar.extractall(tmpdir, filter="data")
        except tarfile.TarError:
            # arXiv sometimes returns a bare .tex file rather than a tarball
            tex_path = os.path.join(tmpdir, f"{arxiv_id}.tex")
            with open(tex_path, "wb") as f:
                f.write(src_data)

        root_tex = _find_root_tex(tmpdir)
        if not root_tex:
            raise RuntimeError("could not find root .tex file with \\documentclass")

        tex_dir = os.path.dirname(root_tex)
        tex_name = os.path.basename(root_tex)

        r = subprocess.run(
            ["make4ht", tex_name, "mathjax"],
            cwd=tex_dir, capture_output=True, timeout=180,
        )
        stem = os.path.splitext(tex_name)[0]
        html_path = os.path.join(tex_dir, stem + ".html")
        if not os.path.exists(html_path):
            tail = r.stderr.decode(errors="replace")[-400:] if r.stderr else ""
            raise RuntimeError(f"make4ht produced no HTML (exit {r.returncode})\n{tail}")
        if r.returncode != 0:
            print(f"cc-arxiv --src: make4ht warnings (exit {r.returncode}), continuing", file=sys.stderr)

        macro_block = _extract_preamble_macros(root_tex)
        if macro_block:
            n = macro_block.count("\\newcommand") + macro_block.count("\\DeclareMathOperator") + macro_block.count("\\def\\")
            print(f"cc-arxiv --src: extracted {n} math macro(s) from preamble", file=sys.stderr)

        with open(html_path, encoding="utf-8", errors="replace") as f:
            raw_html = f.read()
        normalized_html = _normalize_make4ht_html(raw_html)

        p = subprocess.run(
            ["pandoc",
             "--from", "html+tex_math_dollars+tex_math_single_backslash",
             "--to", "markdown",
             "--wrap=none"],
            input=normalized_html, capture_output=True, text=True, timeout=60,
        )
        if p.returncode != 0:
            raise RuntimeError(f"pandoc failed: {p.stderr[:200]}")

        return _post_process_src(p.stdout, arxiv_id, macro_block)


def _html_available(base_id: str) -> bool:
    url = f"https://arxiv.org/html/{base_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "cc-tools/cc-arxiv"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return b"No HTML" not in resp.read(512)
    except (urllib.error.HTTPError, urllib.error.URLError):
        return False


def main():
    src_mode = "--src" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--src"]

    if len(args) != 1 or args[0] in ("-h", "--help"):
        print("Usage: cc-arxiv [--src] <arxiv-id|biorxiv-doi|pmid|doi>", file=sys.stderr)
        print("Fetch metadata for a preprint or published paper.", file=sys.stderr)
        print("  arXiv ID:            2301.07608", file=sys.stderr)
        print("  bioRxiv/medRxiv DOI: 10.1101/2024.01.12.574717", file=sys.stderr)
        print("  PubMed PMID:         12345678", file=sys.stderr)
        print("  Any DOI (CrossRef):  10.1038/s41586-024-00001-0", file=sys.stderr)
        print("Outputs: ID, title, authors, year, PDF URL, HTML availability, abstract.", file=sys.stderr)
        print("  --src: fetch TeX source tarball, convert to markdown via make4ht+pandoc.", file=sys.stderr)
        print("         arXiv IDs only; outputs markdown to stdout.", file=sys.stderr)
        sys.exit(0 if (args and args[0] in ("-h", "--help")) else 1)

    paper_id = args[0]

    if src_mode:
        if paper_id.startswith("10.") or paper_id.isdigit():
            print("cc-arxiv: --src only supported for arXiv IDs", file=sys.stderr)
            sys.exit(1)
        try:
            md = _src_to_markdown(paper_id)
        except RuntimeError as e:
            print(f"cc-arxiv --src: {e}", file=sys.stderr)
            sys.exit(1)
        print(md, end="")
        return

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
