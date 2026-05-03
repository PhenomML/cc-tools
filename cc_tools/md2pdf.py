"""cc-md2pdf — convert Markdown to PDF via pandoc + XeLaTeX.

Handles Unicode text (Greek letters, math-like notation), HTML
<details>/<summary> blocks, and &nbsp; entities.
"""

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


_SUMMARY_RE = re.compile(r"<summary>(.*?)</summary>", re.IGNORECASE | re.DOTALL)
_DETAILS_RE = re.compile(r"</?details[^>]*>", re.IGNORECASE)
# Unicode subscript digits ₀–₉ (U+2080–U+2089): absent from most serif fonts.
# Convert "X₁₂" → "X$_{12}$" so XeLaTeX renders them as proper subscripts.
_SUB_DIGIT_RE = re.compile(r"([\wͰ-Ͽ])([₀-₉]+)")
_SUB_DIGIT_MAP = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def _find_engine(name: str) -> str | None:
    """Find a TeX engine binary, falling back to known MacTeX locations.

    shutil.which() fails in non-login shells because MacTeX registers via
    /etc/paths.d/TeX, which path_helper only processes in login shells.
    Claude Code's Bash tool, VS Code terminals, and launchd agents are all
    non-login shells — so we check known locations explicitly as a fallback.
    """
    found = shutil.which(name)
    if found:
        return found
    candidates = [Path("/Library/TeX/texbin") / name]
    for pattern in [
        f"/usr/local/texlive/*/bin/universal-darwin/{name}",
        f"/usr/local/texlive/*/bin/aarch64-darwin/{name}",
        f"/usr/local/texlive/*/bin/x86_64-darwin/{name}",
    ]:
        candidates += [Path(p) for p in sorted(glob.glob(pattern), reverse=True)]
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def _preprocess(text: str) -> str:
    text = _SUMMARY_RE.sub(r"**\1:**", text)
    text = _DETAILS_RE.sub("", text)
    text = _SUB_DIGIT_RE.sub(
        lambda m: m.group(1) + "$_{" + m.group(2).translate(_SUB_DIGIT_MAP) + "}$",
        text,
    )
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
    engine_path = _find_engine(args.engine)
    if engine_path is None:
        sys.exit(
            f"cc-md2pdf: {args.engine} not found.\n"
            f"  MacTeX:   brew install --cask mactex-no-gui\n"
            f"  BasicTeX: brew install --cask basictex\n"
            f"  Or add your TeX bin directory to PATH."
        )
    # Patch subprocess PATH so pandoc can also resolve the engine.
    # Needed in non-login shells where /etc/paths.d/TeX is not processed.
    engine_dir = str(Path(engine_path).parent)
    env = os.environ.copy()
    env["PATH"] = engine_dir + os.pathsep + env.get("PATH", "")

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
            cmd = [
                "pandoc", str(tmp),
                f"--pdf-engine={engine_path}",
                "--from=markdown+raw_html+smart",
                "-V", "geometry:margin=1in",
                "-V", "papersize:letter",
                "-V", "fontsize:11pt",
                "-V", "colorlinks=true",
                "--standalone",
                "-o", str(out),
            ]
            # XeLaTeX/LuaLaTeX: default font (Latin Modern) has no Greek glyphs.
            # TeX Gyre Termes (Times clone, ships with MacTeX) covers Latin+Greek+subscripts.
            # Fontspec can't find it by "nice name" (not in macOS CoreText), so use file name —
            # fontspec resolves .otf names through kpsewhich instead.
            if args.engine in ("xelatex", "lualatex"):
                cmd += [
                    "-V", "mainfont=texgyretermes-regular.otf",
                    "-V", (
                        "mainfontoptions="
                        "BoldFont=texgyretermes-bold.otf,"
                        "ItalicFont=texgyretermes-italic.otf,"
                        "BoldItalicFont=texgyretermes-bolditalic.otf"
                    ),
                ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
            )
            if result.returncode == 0:
                print(f"cc-md2pdf: wrote {out}")
            else:
                print(f"cc-md2pdf: FAILED on {src}", file=sys.stderr)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)


if __name__ == "__main__":
    main()
