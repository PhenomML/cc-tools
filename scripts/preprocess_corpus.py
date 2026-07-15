#!/usr/bin/env python3
"""
Conference-paper LaTeX preprocessor for the cc-tools corpus.

Strategy (discovered on arXiv:2603.05498, Sun et al. 2026):
  1. Follow \\input{} calls in main.tex body — naturally skips conference
     header blocks (\\twocolumn[...], \\icmltitle{}, etc.)
  2. Strip xcolor table-coloring commands (colorbox, rowcolor, cellcolor)
     that break pandoc's LaTeX parser
  3. Convert \\begin{abstract} → \\section*{Abstract} so pandoc emits it
     as a body section rather than storing it as document metadata
  4. Extract user \\newcommand definitions from preamble and re-emit them
  5. Concatenate section files with minimal \\documentclass{article} stub

Each strip operation is logged. The REPORT.md ranks rules by corpus-wide
fire count → direct priority list for tex4md.sty hooks.

Usage:
    uv run python scripts/preprocess_corpus.py

Outputs:
    tests/corpus/preprocessed/<id>.md       preprocessed Markdown per paper
    tests/corpus/preprocessed/REPORT.md     rule frequencies + quality table
"""
import re
import subprocess
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

CORPUS_DIR = Path(__file__).parent.parent / "tests" / "corpus"
TARBALLS_DIR = CORPUS_DIR / "tarballs"
OUTPUT_DIR = CORPUS_DIR / "preprocessed"

GENERIC_PREAMBLE = r"""\usepackage{amsmath,amssymb,amsthm,mathtools,booktabs,graphicx,multirow}
\newtheorem{theorem}{Theorem}
\newtheorem{lemma}{Lemma}
\newtheorem{proposition}{Proposition}
\newtheorem{corollary}{Corollary}
\newtheorem{definition}{Definition}
\newtheorem{remark}{Remark}
\newtheorem{example}{Example}
\newenvironment{tcolorbox}[1][]{}{}
"""

# Conference .sty names to strip from \usepackage{} in preamble when
# processing single-file papers (their macros break pandoc's LaTeX reader)
CONFERENCE_PACKAGES = {
    "coling", "acl_latex", "acl2023", "acl2024", "acl2025",
    "emnlp", "naacl", "eacl", "findings",
    "iclr2023_conference", "iclr2024_conference",
    "icml2024", "icml2025", "icml2026",
    "neurips_2022", "neurips_2023", "neurips_2024", "nips",
    "cvpr", "iccv", "eccv",
    "colortbl", "xcolor",      # xcolor causes \colorbox parse errors
    "siunitx",                  # \num{} causes issues in some contexts
}

# ---------------------------------------------------------------------------
# Strip rules — each is named for the tex4md hook it corresponds to
# ---------------------------------------------------------------------------

@dataclass
class Rule:
    name: str
    pattern: str
    replacement: str
    flags: int = 0


RULES: list[Rule] = [
    # xcolor / colortbl — table cell coloring; no Markdown equivalent
    Rule("rowcolor",    r'\\rowcolor(\[.*?\])?\{[^}]*\}',              ''),
    Rule("columncolor", r'\\columncolor(\[.*?\])?\{[^}]*\}',           ''),
    Rule("cellcolor",   r'\\cellcolor(\[.*?\])?\{[^}]*\}',             ''),
    # colorbox: strip container, keep content
    Rule("colorbox",    r'\\colorbox\{[^}]*\}\{([^}]*)\}',             r'\1'),
    Rule("fcolorbox",   r'\\fcolorbox\{[^}]*\}\{[^}]*\}\{([^}]*)\}',  r'\1'),
    Rule("textcolor",   r'\\textcolor\{[^}]*\}\{([^}]*)\}',            r'\1'),
    # spacing / layout — no Markdown equivalent
    Rule("setlength",   r'\\setlength\{[^}]*\}\{[^}]*\}',             ''),
    Rule("vhspace",     r'\\[vh]space\*?\{[^}]*\}',                    ''),
    Rule("noindent",    r'\\noindent\b',                               ''),
    Rule("centering",   r'\\centering\b',                              ''),
    Rule("strut",       r'\\strut\b',                                  ''),
    # siunitx — number formatting; keep the number
    Rule("siunitx_num", r'\\num\{([^}]*)\}',                           r'\1'),
    # tcolorbox — strip environment, keep body
    Rule("tcolorbox",   r'\\begin\{tcolorbox\}(\[.*?\])?',             '', re.DOTALL),
    Rule("tcolorbox_e", r'\\end\{tcolorbox\}',                         ''),
    # abstract environment → section so pandoc emits it in the body
    Rule("abstract",    r'\\begin\{abstract\}',                        r'\\section*{Abstract}\n'),
    Rule("abstract_e",  r'\\end\{abstract\}',                          ''),
    # conference geometry macros — silent no-ops
    Rule("twocolumn",   r'\\twocolumn\b',                              ''),
    Rule("onecolumn",   r'\\onecolumn\b',                              ''),
    Rule("clearpage",   r'\\clearpage\b',                              ''),
    Rule("newpage",     r'\\newpage\b',                                ''),
    # TeX primitives — not in pandoc's grammar
    # \vskip / \hskip followed by a dimension (e.g. 0.3in, -2pt, \baselineskip)
    Rule("vskip",       r'\\vskip\s*[+-]?\s*(?:\d+(?:\.\d+)?\w+|\\[a-zA-Z]+)', ''),
    Rule("hskip",       r'\\hskip\s*[+-]?\s*(?:\d+(?:\.\d+)?\w+|\\[a-zA-Z]+)', ''),
    Rule("penalty",     r'\\penalty\s*-?\d+',                          ''),
    Rule("kern",        r'\\kern\s*-?\d+(?:\.\d+)?\w+',               ''),
]


def apply_rules(text: str, counters: dict) -> str:
    for rule in RULES:
        new_text, n = re.subn(rule.pattern, rule.replacement, text, flags=rule.flags)
        if n:
            counters[rule.name] = counters.get(rule.name, 0) + n
        text = new_text
    return text


# ---------------------------------------------------------------------------
# Tarball analysis helpers
# ---------------------------------------------------------------------------

def find_main_tex(work_dir: Path) -> Optional[Path]:
    for name in ["main.tex", "paper.tex", "ms.tex", "article.tex"]:
        p = work_dir / name
        if p.exists():
            return p
    for p in sorted(work_dir.glob("*.tex")):
        try:
            if r"\documentclass" in p.read_text(errors="replace"):
                return p
        except OSError:
            pass
    return None


def extract_field(text: str, cmd: str) -> str:
    m = re.search(rf'\\{cmd}(?:\[.*?\])?\{{([^}}]+)\}}', text)
    return m.group(1).strip() if m else "(unknown)"


def extract_preamble_macros(preamble: str) -> str:
    """Return \\newcommand / \\DeclareMathOperator lines from the preamble."""
    keep = []
    for line in preamble.splitlines():
        s = line.strip()
        if any(s.startswith(c) for c in (
            r"\newcommand", r"\renewcommand", r"\providecommand",
            r"\DeclareMathOperator", r"\newtheorem", r"\theoremstyle",
        )):
            keep.append(line)
    return "\n".join(keep)


def strip_conference_packages(preamble: str) -> str:
    """Remove \\usepackage{} calls for known conference / xcolor packages."""
    def replace(m):
        pkg = m.group(1).strip()
        if pkg in CONFERENCE_PACKAGES:
            return f"% stripped: {m.group(0).strip()}"
        return m.group(0)
    return re.sub(r'\\usepackage(?:\[.*?\])?\{([^}]+)\}', replace, preamble)


def find_input_files(body: str, work_dir: Path) -> list[Path]:
    """Follow \\input{} and \\include{} in document body, in order."""
    refs = re.findall(r'\\(?:input|include)\{([^}]+)\}', body)
    files = []
    for ref in refs:
        for candidate in [ref, ref + ".tex"]:
            p = work_dir / candidate
            if p.exists():
                files.append(p)
                break
    return files


def find_abstract_in_body(body: str, work_dir: Path) -> Optional[str]:
    """
    Extract abstract text from main.tex body when it's NOT in an \\input{} file.

    Returns the raw abstract content (no \\begin{abstract} wrapper), or None
    if the abstract lives in a section file (will be handled by the rule).
    """
    m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', body, re.DOTALL)
    if not m:
        return None
    content = m.group(1).strip()
    # If it's just an \input{} call, read the file
    inp = re.match(r'^\\(?:input|include)\{([^}]+)\}$', content)
    if inp:
        for candidate in [inp.group(1), inp.group(1) + ".tex"]:
            f = work_dir / candidate
            if f.exists():
                return f.read_text(errors="replace").strip()
        return None
    return content if content else None


# ---------------------------------------------------------------------------
# Main preprocessing function
# ---------------------------------------------------------------------------

def preprocess_tarball(tarball_path: Path) -> dict:
    result = dict(
        title="(unknown)", docclass="(unknown)",
        files_found=0, abstract_source="none",
        counters={}, output_lines=0,
        pandoc_warnings=0, success=False, error=None, md="",
    )

    with tempfile.TemporaryDirectory() as tmp:
        work_dir = Path(tmp)
        try:
            with tarfile.open(tarball_path) as tf:
                tf.extractall(work_dir)
        except Exception as e:
            result["error"] = f"extract: {e}"
            return result

        main_tex = find_main_tex(work_dir)
        if not main_tex:
            result["error"] = "no main .tex found"
            return result

        try:
            source = main_tex.read_text(errors="replace")
        except OSError as e:
            result["error"] = f"read: {e}"
            return result

        body_m = re.search(
            r'\\begin\{document\}(.*?)\\end\{document\}', source, re.DOTALL
        )
        if not body_m:
            result["error"] = "no \\begin{document}"
            return result

        preamble = source[: body_m.start()]
        body = body_m.group(1)

        result["title"] = extract_field(preamble, "title")
        result["docclass"] = extract_field(preamble, "documentclass")

        user_macros = extract_preamble_macros(preamble)
        section_files = find_input_files(body, work_dir)
        result["files_found"] = len(section_files)

        counters: dict = {}
        parts = []

        if section_files:
            # --- Multi-file path: concat section files, bypass conference header ---
            result["strategy"] = "section-concat"

            abstract_body = find_abstract_in_body(body, work_dir)
            abstract_in_sections = any(
                r"\begin{abstract}" in f.read_text(errors="replace")
                for f in section_files if f.exists()
            )

            if abstract_body and not abstract_in_sections:
                parts.append(apply_rules(
                    f"\\section*{{Abstract}}\n{abstract_body}", counters
                ))
                result["abstract_source"] = "main.tex"
            elif abstract_in_sections:
                result["abstract_source"] = "section_file"
            else:
                result["abstract_source"] = "none"

            for sf in section_files:
                try:
                    content = sf.read_text(errors="replace")
                except OSError:
                    continue
                parts.append(apply_rules(content, counters))

            preamble_block = GENERIC_PREAMBLE + "\n" + user_macros

        else:
            # --- Single-file path: use body directly, strip conference packages ---
            result["strategy"] = "body-direct"

            # Abstract is in the body — the abstract rule will convert it
            if r"\begin{abstract}" in body:
                result["abstract_source"] = "body"
            else:
                result["abstract_source"] = "none"

            parts.append(apply_rules(body, counters))
            clean_preamble = strip_conference_packages(preamble)
            preamble_block = (
                GENERIC_PREAMBLE + "\n"
                + extract_preamble_macros(clean_preamble)
            )

        result["counters"] = counters

        doc = (
            "\\documentclass{article}\n"
            + preamble_block + "\n"
            + "\\begin{document}\n"
            + "\n".join(parts) + "\n"
            + "\\end{document}\n"
        )

        try:
            proc = subprocess.run(
                ["pandoc", "-", "--from=latex", "--to=markdown", "--wrap=preserve"],
                input=doc, capture_output=True, text=True, timeout=120,
            )
            result["md"] = proc.stdout
            result["output_lines"] = len(proc.stdout.splitlines())
            result["pandoc_warnings"] = proc.stderr.count("[WARNING]")
            result["success"] = bool(proc.stdout.strip())
            if not result["success"] and proc.stderr:
                # Capture first two diagnostic lines
                diag = [
                    l.strip() for l in proc.stderr.splitlines()
                    if any(kw in l for kw in ("Error", "unexpected", "error"))
                ]
                result["error"] = " | ".join(diag[:2])[:160] if diag else "no output"
        except subprocess.TimeoutExpired:
            result["error"] = "pandoc timeout (>120s)"
        except Exception as e:
            result["error"] = f"pandoc: {e}"

    return result


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------

def build_report(results: dict[str, dict]) -> str:
    all_rule_names = [r.name for r in RULES]

    # Aggregate rule stats
    rule_totals: dict[str, int] = {}
    rule_papers: dict[str, int] = {}
    for r in results.values():
        for rule, count in r["counters"].items():
            rule_totals[rule] = rule_totals.get(rule, 0) + count
            rule_papers[rule] = rule_papers.get(rule, 0) + 1

    n = len(results)
    lines = [
        "# LaTeX Preprocessor — Corpus Report",
        "",
        f"Papers processed: {n}  ",
        f"Succeeded: {sum(1 for r in results.values() if r['success'])}  ",
        f"Failed: {sum(1 for r in results.values() if not r['success'])}",
        "",
        "## Per-Paper Results",
        "",
        "| arXiv ID | Class | Strategy | Lines | ✓ | Abstract | Files | Warns |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for arxiv_id, r in results.items():
        lines.append(
            f'| {arxiv_id} | `{r["docclass"]}` | {r.get("strategy","?")} '
            f'| {r["output_lines"]} '
            f'| {"✓" if r["success"] else "✗"} '
            f'| {r["abstract_source"]} '
            f'| {r["files_found"]} '
            f'| {r["pandoc_warnings"]} |'
        )

    lines += [
        "",
        "## Rule Fire Counts",
        "",
        "Ranked by corpus-wide frequency. "
        "Each rule corresponds to one no-op hook in `tex4md.sty`. "
        "Rules with 0 fires are omitted.",
        "",
        "| Rank | Rule | Total fires | Papers affected | tex4md hook sketch |",
        "|---|---|---|---|---|",
    ]

    hook_sketch = {
        "rowcolor":    r"`\renewcommand{\rowcolor}[2][]{}`",
        "columncolor": r"`\renewcommand{\columncolor}[2][]{}`",
        "cellcolor":   r"`\renewcommand{\cellcolor}[2][]{}`",
        "colorbox":    r"`\renewcommand{\colorbox}[2]{#2}`",
        "fcolorbox":   r"`\renewcommand{\fcolorbox}[3]{#3}`",
        "textcolor":   r"`\renewcommand{\textcolor}[2]{#2}`",
        "setlength":   r"`\renewcommand{\setlength}[2]{}`",
        "vhspace":     r"strip `\vspace`/`\hspace` in hooks",
        "noindent":    r"`\renewcommand{\noindent}{}`",
        "centering":   r"`\renewcommand{\centering}{}`",
        "strut":       r"`\renewcommand{\strut}{}`",
        "siunitx_num": r"`\renewcommand{\num}[1]{#1}`",
        "tcolorbox":   r"`\renewenvironment{tcolorbox}[1][]{}{}`",
        "tcolorbox_e": "(paired with tcolorbox)",
        "abstract":    r"emit `# Abstract\n` hook in `\begin{abstract}`",
        "abstract_e":  r"paired with abstract",
        "twocolumn":   r"`\renewcommand{\twocolumn}[1][]{}`",
        "onecolumn":   r"`\renewcommand{\onecolumn}{}`",
        "clearpage":   r"`\renewcommand{\clearpage}{}`",
        "newpage":     r"`\renewcommand{\newpage}{}`",
        "vskip":       r"Lua callback on `\vskip` primitive — no LaTeX hook equivalent",
        "hskip":       r"Lua callback on `\hskip` primitive — no LaTeX hook equivalent",
        "penalty":     r"Lua callback on `\penalty` primitive",
        "kern":        r"Lua callback on `\kern` primitive",
    }

    ranked = sorted(
        [(name, rule_totals.get(name, 0)) for name in all_rule_names],
        key=lambda x: -x[1],
    )
    for rank, (name, total) in enumerate(ranked, 1):
        if total == 0:
            continue
        papers = rule_papers.get(name, 0)
        sketch = hook_sketch.get(name, "—")
        lines.append(f"| {rank} | `{name}` | {total} | {papers}/{n} | {sketch} |")

    # Errors section
    errors = [(k, v["error"]) for k, v in results.items() if v.get("error")]
    if errors:
        lines += ["", "## Errors", ""]
        for arxiv_id, err in errors:
            lines.append(f"- **{arxiv_id}:** {err}")

    # tex4md priority list
    lines += [
        "",
        "## tex4md Hook Priority",
        "",
        "Hooks to implement first in `tex4md.sty`, ordered by corpus frequency:",
        "",
    ]
    fired = [(name, total) for name, total in ranked if total > 0]
    for i, (name, total) in enumerate(fired, 1):
        papers = rule_papers.get(name, 0)
        lines.append(
            f"{i}. **`{name}`** — {total} fires across {papers} paper(s). "
            f"{hook_sketch.get(name, '')}"
        )

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tarballs = sorted(TARBALLS_DIR.glob("*.tar.gz"))
    if not tarballs:
        print(f"No tarballs in {TARBALLS_DIR}")
        print("Run: uv run pytest --regenerate  (or --refetch) to populate the cache")
        return

    results: dict[str, dict] = {}
    for tb in tarballs:
        # Reconstruct display ID from filename
        stem = tb.stem
        arxiv_id = "math/" + stem[5:] if stem.startswith("math-") else stem

        print(f"  {arxiv_id:<20}", end=" ", flush=True)
        result = preprocess_tarball(tb)
        results[arxiv_id] = result

        md = result.pop("md", "")
        if result["success"]:
            (OUTPUT_DIR / (stem + ".md")).write_text(md)
            print(
                f"✓  {result['output_lines']:>4} lines  "
                f"{result['pandoc_warnings']} warns  "
                f"[{result['docclass']}]"
            )
        else:
            print(f"✗  {result.get('error', 'no output')!r}  [{result['docclass']}]")

    report = build_report(results)
    report_path = OUTPUT_DIR / "REPORT.md"
    report_path.write_text(report)

    succeeded = sum(1 for r in results.values() if r["success"])
    print(f"\n{succeeded}/{len(results)} succeeded")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
