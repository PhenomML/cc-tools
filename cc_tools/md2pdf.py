"""cc-md2pdf — convert Markdown to PDF via pandoc + XeLaTeX.

Handles Unicode text (Greek letters, math-like notation), HTML
<details>/<summary> blocks, and &nbsp; entities.
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


_SUMMARY_RE = re.compile(r"<summary>(.*?)</summary>", re.IGNORECASE | re.DOTALL)
_DETAILS_RE = re.compile(r"</?details[^>]*>", re.IGNORECASE)


def _preprocess(text: str) -> str:
    text = _SUMMARY_RE.sub(r"**\1:**", text)
    text = _DETAILS_RE.sub("", text)
    return text


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cc-md2pdf",
        description=(
            "Convert Markdown to PDF via pandoc + XeLaTeX. "
            "Preprocesses HTML <details>/<summary> blocks into visible text."
        ),
        epilog=(
            "Requirements: brew install pandoc && brew install --cask basictex\n"
            "              sudo tlmgr update --self && sudo tlmgr install collection-fontsrecommended"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("files", nargs="+", metavar="file.md")
    parser.add_argument("-o", "--outdir", metavar="DIR",
                        help="write PDFs to DIR (default: same directory as source)")
    parser.add_argument("-e", "--engine", default="xelatex",
                        choices=["xelatex", "lualatex", "pdflatex"],
                        help="PDF engine (default: xelatex)")
    args = parser.parse_args()

    if not shutil.which("pandoc"):
        sys.exit("cc-md2pdf: pandoc not found — install: brew install pandoc")
    if not shutil.which(args.engine):
        sys.exit(
            f"cc-md2pdf: {args.engine} not found — install: brew install --cask basictex"
        )

    outdir = Path(args.outdir) if args.outdir else None
    if outdir:
        outdir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cc-md2pdf-") as tmpdir:
        for src_str in args.files:
            src = Path(src_str)
            if not src.is_file():
                print(f"cc-md2pdf: not found: {src}", file=sys.stderr)
                continue

            out = (outdir or src.parent) / (src.stem + ".pdf")
            tmp = Path(tmpdir) / src.name

            tmp.write_text(_preprocess(src.read_text(encoding="utf-8")), encoding="utf-8")

            print(f"cc-md2pdf: rendering {src} → {out}")
            result = subprocess.run(
                [
                    "pandoc", str(tmp),
                    f"--pdf-engine={args.engine}",
                    "--from=markdown+raw_html+smart",
                    "-V", "geometry:margin=1in",
                    "-V", "papersize:letter",
                    "-V", "fontsize:11pt",
                    "-V", "colorlinks=true",
                    "--standalone",
                    "-o", str(out),
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print(f"cc-md2pdf: wrote {out}")
            else:
                print(f"cc-md2pdf: FAILED on {src}", file=sys.stderr)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)


if __name__ == "__main__":
    main()
