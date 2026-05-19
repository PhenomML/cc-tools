import html as _html
import json
import os
import re
import shutil
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


def _parse_simple_macros(root_tex: str) -> dict[str, str]:
    """Return {name: expansion} for no-argument \\newcommand macros in the preamble.

    Skips macros with arguments ([N] after the name) and macros whose expansion
    contains #N parameter references.
    """
    def _extract_brace_group(s: str, pos: int) -> tuple[str, int] | None:
        if pos >= len(s) or s[pos] != '{':
            return None
        depth = 0
        for i in range(pos, len(s)):
            if s[i] == '{':
                depth += 1
            elif s[i] == '}':
                depth -= 1
                if depth == 0:
                    return s[pos + 1:i], i + 1
        return None

    result: dict[str, str] = {}
    cmd_pattern = re.compile(
        r'\\(?:newcommand\*?|renewcommand\*?|providecommand\*?)'
        r'\{?\\(\w+)\}?'   # \name or {\name}
        r'(?!\s*\[)'        # not followed by [N] arg count
    )
    for tex_path in _preamble_files(root_tex):
        try:
            with open(tex_path, encoding="utf-8", errors="replace") as f:
                for line in f:
                    if r"\begin{document}" in line:
                        break
                    m = cmd_pattern.search(line)
                    if m:
                        name = m.group(1)
                        group = _extract_brace_group(line, m.end())
                        if group:
                            defn, _ = group
                            if '#' not in defn and name not in result:
                                result[name] = defn
        except OSError:
            pass
    return result


def _expand_macros(content: str, macros: dict[str, str]) -> str:
    """Expand no-argument macros in markdown content."""
    for name, defn in macros.items():
        content = re.sub(
            r'\\' + re.escape(name) + r'(?![a-zA-Z])',
            lambda m, d=defn: d,
            content,
        )
    return content


def _preamble_files(root_tex: str) -> list[str]:
    """Return root_tex plus files from \\input directives before \\begin{document}."""
    tex_dir = os.path.dirname(root_tex)
    files = [root_tex]
    try:
        with open(root_tex, encoding="utf-8", errors="replace") as f:
            for line in f:
                if r"\begin{document}" in line:
                    break
                m = re.search(r"\\(?:input|include)\{([^}]+)\}", line)
                if m:
                    name = m.group(1)
                    if not name.endswith(".tex"):
                        name += ".tex"
                    path = os.path.join(tex_dir, name)
                    if os.path.exists(path):
                        files.append(path)
    except OSError:
        pass
    return files


def _extract_preamble_macros(root_tex: str) -> str:
    """Extract math macro definitions from TeX preamble and \\input-included files as a MathJax $$-block."""
    macro_pattern = re.compile(
        r"\\(newcommand|renewcommand|providecommand|DeclareMathOperator)\b|\\def\\"
    )
    seen: set[str] = set()
    macros: list[str] = []
    for tex_path in _preamble_files(root_tex):
        try:
            with open(tex_path, encoding="utf-8", errors="replace") as f:
                for line in f:
                    if r"\begin{document}" in line:
                        break
                    stripped = line.strip()
                    if macro_pattern.match(stripped) and stripped not in seen:
                        seen.add(stripped)
                        macros.append(stripped)
        except OSError:
            continue
    if not macros:
        return ""
    return "$$\n" + "\n".join(macros) + "\n$$\n\n"


def _post_process_src(content: str, arxiv_id: str, macro_block: str = "", pipeline: str = "make4ht+mathjax", preserve_images: bool = False, simple_macros: dict[str, str] | None = None) -> str:
    # HTML entities in raw-HTML passthrough blocks (algorithm listings, captions)
    content = content.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    # CSS class spans from make4ht: [text]{.ClassName} -> text  (dot-class variant)
    content = re.sub(r"\[([^\]]*)\]\{\.[\w-]+\}", r"\1", content)
    # Strip empty HTML anchors []{#id} produced by pandoc from make4ht's id attributes
    content = re.sub(r"\[\]\{#[^}]+\}", "", content)
    # Strip span wrappers [text]{#id .class} — keep text, drop attribute
    content = re.sub(r"\[([^\]]*)\]\{#[^}]+\}", r"\1", content)
    # Strip remaining {#id ...} heading/block attributes
    content = re.sub(r"\s*\{#[^}]+\}", "", content)
    # Strip residual HTML: figure captions → italicised plain text
    def _clean_figcaption(m: re.Match) -> str:
        inner = re.sub(r"<[^>]+>", " ", m.group(1))
        inner = _html.unescape(inner)
        inner = re.sub(r"\s+", " ", inner).strip()
        return f"\n\n*{inner}*\n\n"
    content = re.sub(r"<figcaption>(.*?)</figcaption>", _clean_figcaption, content, flags=re.DOTALL)
    # Strip <span> tags (keep content); iterate until convergence (nesting can be 4+ levels deep)
    while True:
        stripped = re.sub(r"<span[^>]*>(.*?)</span>", r"\1", content, flags=re.DOTALL)
        if stripped == content:
            break
        content = stripped
    # Convert or strip <img> tags
    if preserve_images:
        def _img_to_md(m: re.Match) -> str:
            tag = m.group(0)
            src_m = re.search(r'\bsrc=(["\'])([^"\']+)\1', tag)
            alt_m = re.search(r'\balt=(["\'])([^"\']*)\1', tag)
            src = src_m.group(2) if src_m else ""
            alt = alt_m.group(2) if alt_m else "figure"
            return f"\n\n![{alt}]({src})\n\n" if src else ""
        content = re.sub(r"<img\b[^>]*/?>", _img_to_md, content, flags=re.DOTALL)
    else:
        content = re.sub(r"<img[^>]*/?>", "", content)
    # Strip <figure>, <div>, <p> container tags — keep content, drop wrappers
    content = re.sub(r"<(?:figure|div|p)(?:\s[^>]*)?>|</(?:figure|div|p)>", "", content)
    # Strip <br> tags
    content = re.sub(r"<br\s*/?>", "\n", content)
    # Strip internal anchor links — keep link text
    content = re.sub(r'<a\s+href="#[^"]*">(.*?)</a>', r"\1", content, flags=re.DOTALL)
    # Style attributes
    content = re.sub(r'\{style="[^"]*"\}', "", content)
    # Div block markers (::: mathjax-block etc.)
    content = re.sub(r"^:+\s*\S.*$", "", content, flags=re.MULTILINE)
    content = re.sub(r"^:+\s*$", "", content, flags=re.MULTILINE)
    # Collapse excess blank lines
    content = re.sub(r"\n{3,}", "\n\n", content)
    # Expand no-argument macros inline so KaTeX (Obsidian) renders them without needing \newcommand scope
    if simple_macros:
        content = _expand_macros(content, simple_macros)
    header = f"<!-- Source: arXiv:{arxiv_id} TeX source tarball via {pipeline}. Math fidelity: high. -->\n\n"
    return header + macro_block + content.strip() + "\n"


def _fetch_tarball(arxiv_id: str) -> bytes:
    """Download source tarball bytes from arXiv."""
    url = f"https://arxiv.org/src/{arxiv_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "cc-tools/cc-arxiv"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        if e.code == 403:
            raise RuntimeError(
                "no TeX source available (403) — paper was likely submitted as PDF-only; "
                "use cc-markitdown on the PDF as fallback"
            )
        raise RuntimeError(f"source download failed: {e}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"source download failed: {e}")


def _detect_tex_dialect(directory: str) -> str | None:
    """Return dialect name if directory contains AMSTeX/plain TeX but no LaTeX files."""
    for dirpath, _, filenames in os.walk(directory):
        for fname in filenames:
            if not fname.endswith(".tex"):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, "rb") as f:
                    chunk = f.read(512)
                if b"%&amstex" in chunk or b"%&amsppt" in chunk:
                    return "AMSTeX"
                if b"%&plain" in chunk or chunk.lstrip().startswith(b"\\input plain"):
                    return "plain TeX"
            except OSError:
                pass
    return None


# Patterns that indicate active exploitation attempts in TeX source.
# LaTeX is Turing-complete and can execute shell commands, read arbitrary
# files, and make network requests — any of which could exfiltrate data or
# compromise the host when processing untrusted source. See SECURITY.md.
_HAZARD_PATTERNS: list[tuple[re.Pattern, str]] = [
    # Shell execution via \write18 (even in restricted mode, flag it)
    (re.compile(r"\\write18\s*\{"), r"\write18 (shell escape)"),
    (re.compile(r"\\immediate\s*\\write18\s*\{"), r"\immediate\write18 (shell escape)"),
    # Lua interpreter (LuaTeX): shell and network access.
    # CVE-2023-32700: on TeX Live < 2023, \directlua can bypass --no-shell-escape
    # entirely via Lua's debug upvalue API. The pre-scan is the primary defense.
    (re.compile(r"os\.execute\s*\("), "os.execute in Lua (shell execution)"),
    (re.compile(r"require\s*\(\s*[\"']socket"), "require('socket') in Lua (network access)"),
    (re.compile(r"io\.popen\s*\("), "io.popen in Lua (shell execution)"),
    # File I/O to paths outside the working tree
    (re.compile(r"\\openin\b[^\n]*(?:/etc/|/root/|/Users/|/home/|~/|\\string~)"),
     r"\openin with sensitive absolute path"),
    (re.compile(r"\\openout\b[^\n]*(?:/etc/|/root/|/Users/|/home/|~/|\\string~)"),
     r"\openout with sensitive absolute path"),
]


def _scan_tex_for_hazards(tmpdir: str) -> list[str]:
    """Scan extracted TeX source for dangerous execution patterns.

    Returns a list of 'file:line: description' strings. Empty list = clean.
    Scans .tex, .sty, .cls, .dtx, and .ins files.
    """
    findings: list[str] = []
    scannable = {".tex", ".sty", ".cls", ".dtx", ".ins"}
    for dirpath, _, filenames in os.walk(tmpdir):
        for fname in filenames:
            if os.path.splitext(fname)[1].lower() not in scannable:
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, encoding="utf-8", errors="replace") as fh:
                    for lineno, line in enumerate(fh, 1):
                        for pattern, description in _HAZARD_PATTERNS:
                            if pattern.search(line):
                                findings.append(f"{fname}:{lineno}: {description}")
            except OSError:
                pass
    return findings


def _write_bare_tex(data: bytes, arxiv_id: str, tmpdir: str) -> None:
    """Write raw bytes as a bare .tex file into tmpdir."""
    safe_id = arxiv_id.replace("/", "_")
    tex_path = os.path.join(tmpdir, f"{safe_id}.tex")
    with open(tex_path, "wb") as f:
        f.write(data)


def _has_tex_files(directory: str) -> bool:
    return any(
        fname.endswith(".tex")
        for _, _, fnames in os.walk(directory)
        for fname in fnames
    )


def _rewrite_img_src(html: str, tex_dir: str, figures_dir: str, img_rel_prefix: str) -> str:
    """Copy image files referenced in <img> tags to figures_dir; rewrite src to img_rel_prefix/basename."""
    os.makedirs(figures_dir, exist_ok=True)
    copied: set[str] = set()

    def _replace(m: re.Match) -> str:
        tag = m.group(0)
        src_m = re.search(r'\bsrc=(["\'])([^"\']+)\1', tag)
        if not src_m:
            return tag
        src = src_m.group(2)
        if src.startswith(("http", "data:")):
            return tag
        img_path = os.path.join(tex_dir, src)
        if not os.path.exists(img_path):
            return tag
        basename = os.path.basename(src)
        dest = os.path.join(figures_dir, basename)
        if src not in copied:
            shutil.copy2(img_path, dest)
            copied.add(src)
        new_src = f"{img_rel_prefix}/{basename}" if img_rel_prefix else basename
        return tag.replace(src_m.group(0), f'src="{new_src}"', 1)

    return re.sub(r"<img\b[^>]*/?>", _replace, html, flags=re.DOTALL)


def _convert_tarball(src_data: bytes, arxiv_id: str, figures_dir: str | None = None, output_path: str | None = None) -> str:
    """Convert raw tarball bytes to markdown. Called by _src_to_markdown and --local-src."""
    import gzip as _gzip

    with tempfile.TemporaryDirectory() as tmpdir:
        tarpath = os.path.join(tmpdir, "src.tar.gz")
        with open(tarpath, "wb") as f:
            f.write(src_data)

        try:
            with tarfile.open(tarpath) as tar:
                tar.extractall(tmpdir, filter="data")
        except tarfile.TarError:
            # Not a tarball. Try gzip decompression first (arXiv returns gzip'd
            # bare .tex for some old papers); fall back to raw bytes if not gzip.
            try:
                content = _gzip.decompress(src_data)
            except Exception:
                content = src_data
            _write_bare_tex(content, arxiv_id, tmpdir)

        # Safety net: tarfile opens gzip natively but may extract nothing if the
        # content isn't a valid tar. Handle that case too.
        if not _has_tex_files(tmpdir):
            try:
                decompressed = _gzip.decompress(src_data)
            except Exception:
                decompressed = src_data
            _write_bare_tex(decompressed, arxiv_id, tmpdir)

        # Tier-1 security scan: abort before executing TeX if dangerous patterns found.
        # LaTeX is Turing-complete; see SECURITY.md for the threat model.
        hazards = _scan_tex_for_hazards(tmpdir)
        if hazards:
            sample = "\n".join(f"  {h}" for h in hazards[:10])
            if len(hazards) > 10:
                sample += f"\n  ... ({len(hazards) - 10} more)"
            raise RuntimeError(
                "cc-arxiv --src: TeX source contains potentially dangerous patterns "
                "(aborting to protect against code execution / data exfiltration):\n"
                + sample
            )

        root_tex = _find_root_tex(tmpdir)
        if not root_tex:
            # Check if source is AMSTeX or plain TeX (pre-LaTeX dialects, common pre-2000)
            dialect = _detect_tex_dialect(tmpdir)
            if dialect:
                raise RuntimeError(
                    f"{dialect} source detected — no \\documentclass; "
                    "make4ht and pandoc require LaTeX. "
                    "Use PDF fallback: cc-markitdown on the arXiv PDF."
                )
            raise RuntimeError("could not find root .tex file with \\documentclass")

        tex_dir = os.path.dirname(root_tex)
        tex_name = os.path.basename(root_tex)

        # Harden the TeX execution environment:
        #   openout_any=p — write only within current directory tree (paranoid mode)
        #   -no-shell-escape — disable \write18 explicitly (belt-and-suspenders;
        #     restricted shell-escape is already the TeX Live default)
        security_cnf = os.path.join(tmpdir, "texmf.cnf")
        with open(security_cnf, "w") as _f:
            _f.write("openout_any = p\n")
        make_env = os.environ.copy()
        existing_cnf = make_env.get("TEXMFCNF", "")
        make_env["TEXMFCNF"] = (tmpdir + ":" + existing_cnf) if existing_cnf else tmpdir

        r = subprocess.run(
            ["make4ht", tex_name, "mathjax", "-no-shell-escape"],
            cwd=tex_dir, capture_output=True, timeout=180, env=make_env,
        )
        stem = os.path.splitext(tex_name)[0]
        html_path = os.path.join(tex_dir, stem + ".html")
        if r.returncode != 0 and not os.path.exists(html_path):
            print(f"cc-arxiv --src: make4ht failed (exit {r.returncode}), trying pandoc fallback",
                  file=sys.stderr)

        macro_block = _extract_preamble_macros(root_tex)
        simple_macros = _parse_simple_macros(root_tex)

        if os.path.exists(html_path):
            with open(html_path, encoding="utf-8", errors="replace") as f:
                raw_html = f.read()
            normalized_html = _normalize_make4ht_html(raw_html)
            if figures_dir:
                if output_path:
                    output_dir = os.path.dirname(os.path.abspath(output_path))
                    img_rel_prefix = os.path.relpath(os.path.abspath(figures_dir), output_dir)
                else:
                    img_rel_prefix = os.path.abspath(figures_dir)
                normalized_html = _rewrite_img_src(normalized_html, tex_dir, figures_dir, img_rel_prefix)
            p = subprocess.run(
                ["pandoc",
                 "--from", "html+tex_math_dollars+tex_math_single_backslash",
                 "--to", "markdown",
                 "--wrap=none"],
                input=normalized_html, capture_output=True, text=True, timeout=60,
            )
            if p.returncode != 0:
                raise RuntimeError(f"pandoc failed: {p.stderr[:200]}")
            return _post_process_src(p.stdout, arxiv_id, macro_block, preserve_images=figures_dir is not None, simple_macros=simple_macros)

        # make4ht failed to produce HTML (e.g. IEEEtran register overflow).
        # Fall back to pandoc direct LaTeX → markdown — still gives clean math.
        print("cc-arxiv --src: make4ht produced no HTML, falling back to pandoc direct LaTeX conversion",
              file=sys.stderr)
        p = subprocess.run(
            ["pandoc", "--from", "latex", "--to", "markdown", "--wrap=none", root_tex],
            capture_output=True, text=True, timeout=60,
        )
        if p.returncode != 0:
            raise RuntimeError(f"pandoc direct LaTeX conversion failed: {p.stderr[:200]}")
        content = re.sub(r'\{reference-type="[^"]*"\s+reference="[^"]*"\}', "", p.stdout)
        return _post_process_src(content, arxiv_id, macro_block, pipeline="pandoc-latex", simple_macros=simple_macros)


def _src_to_markdown(arxiv_id: str, figures_dir: str | None = None, output_path: str | None = None) -> str:
    return _convert_tarball(_fetch_tarball(arxiv_id), arxiv_id, figures_dir=figures_dir, output_path=output_path)


def _html_available(base_id: str) -> bool:
    url = f"https://arxiv.org/html/{base_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "cc-tools/cc-arxiv"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return b"No HTML" not in resp.read(512)
    except (urllib.error.HTTPError, urllib.error.URLError):
        return False


def main():
    argv = sys.argv[1:]
    src_mode = "--src" in argv
    argv = [a for a in argv if a != "--src"]

    local_src = None
    if "--local-src" in argv:
        idx = argv.index("--local-src")
        if idx + 1 >= len(argv):
            print("cc-arxiv: --local-src requires a path argument", file=sys.stderr)
            sys.exit(1)
        local_src = argv[idx + 1]
        argv = argv[:idx] + argv[idx + 2:]

    output_path = None
    if "--output" in argv:
        idx = argv.index("--output")
        if idx + 1 >= len(argv):
            print("cc-arxiv: --output requires a path argument", file=sys.stderr)
            sys.exit(1)
        output_path = argv[idx + 1]
        argv = argv[:idx] + argv[idx + 2:]

    figures_dir = None
    if "--figures-dir" in argv:
        idx = argv.index("--figures-dir")
        if idx + 1 >= len(argv):
            print("cc-arxiv: --figures-dir requires a path argument", file=sys.stderr)
            sys.exit(1)
        figures_dir = argv[idx + 1]
        argv = argv[:idx] + argv[idx + 2:]

    if len(argv) != 1 or argv[0] in ("-h", "--help"):
        print("Usage: cc-arxiv [--src] [--local-src <path>] [--output <path>] [--figures-dir <path>] <arxiv-id|biorxiv-doi|pmid|doi>", file=sys.stderr)
        print("Fetch metadata for a preprint or published paper.", file=sys.stderr)
        print("  arXiv ID:            2301.07608", file=sys.stderr)
        print("  bioRxiv/medRxiv DOI: 10.1101/2024.01.12.574717", file=sys.stderr)
        print("  PubMed PMID:         12345678", file=sys.stderr)
        print("  Any DOI (CrossRef):  10.1038/s41586-024-00001-0", file=sys.stderr)
        print("Outputs: ID, title, authors, year, PDF URL, HTML availability, abstract.", file=sys.stderr)
        print("  --src: fetch TeX source tarball, convert to markdown via make4ht+pandoc.", file=sys.stderr)
        print("         arXiv IDs only; outputs markdown to stdout.", file=sys.stderr)
        print("  --local-src <path>: use cached tarball instead of fetching from arXiv.", file=sys.stderr)
        print("         Requires --src. Useful for offline re-conversion.", file=sys.stderr)
        print("  --output <path>: write output to file atomically (safe alternative to '>').", file=sys.stderr)
        print("         On failure, the target file is not modified.", file=sys.stderr)
        print("  --figures-dir <path>: extract figures to this directory; embed relative paths in output.", file=sys.stderr)
        print("         Requires --src. Best used with --output so relative paths are correct.", file=sys.stderr)
        sys.exit(0 if (argv and argv[0] in ("-h", "--help")) else 1)

    paper_id = argv[0]

    if src_mode:
        if paper_id.startswith("10.") or paper_id.isdigit():
            print("cc-arxiv: --src only supported for arXiv IDs", file=sys.stderr)
            sys.exit(1)
        try:
            if local_src:
                with open(local_src, "rb") as f:
                    src_data = f.read()
                md = _convert_tarball(src_data, paper_id, figures_dir=figures_dir, output_path=output_path)
            else:
                md = _src_to_markdown(paper_id, figures_dir=figures_dir, output_path=output_path)
        except RuntimeError as e:
            print(f"cc-arxiv --src: {e}", file=sys.stderr)
            sys.exit(1)
        if output_path:
            # Write to temp file alongside target, then move atomically
            tmp = output_path + ".tmp"
            try:
                with open(tmp, "w", encoding="utf-8") as f:
                    f.write(md)
                shutil.move(tmp, output_path)
            except OSError as e:
                print(f"cc-arxiv --src: failed to write output: {e}", file=sys.stderr)
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
                sys.exit(1)
        else:
            print(md, end="")
        return

    if local_src:
        print("cc-arxiv: --local-src requires --src", file=sys.stderr)
        sys.exit(1)

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
