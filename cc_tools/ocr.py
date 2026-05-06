import sys
import subprocess
import shutil
import tempfile
from pathlib import Path


def _check_dep(cmd: str, install: str) -> bool:
    if shutil.which(cmd) is None:
        print(f"cc-ocr: {cmd} not found — install with: {install}", file=sys.stderr)
        return False
    return True


def _has_text_layer(pdf_path: str) -> bool:
    if shutil.which("pdftotext") is None:
        return False
    try:
        result = subprocess.run(
            ["pdftotext", pdf_path, "-"],
            capture_output=True, text=True, timeout=30,
        )
        return len(result.stdout.replace(" ", "").replace("\n", "")) > 10
    except (subprocess.TimeoutExpired, OSError):
        return False


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: cc-ocr <file.pdf>", file=sys.stderr)
        print("OCR a scanned PDF using pdftoppm + tesseract.", file=sys.stderr)
        print("Output is written to stdout. Redirect to save: cc-ocr file.pdf > out.md", file=sys.stderr)
        print("Requires: pdftoppm (brew install poppler), tesseract (brew install tesseract)", file=sys.stderr)
        sys.exit(0 if "--help" in sys.argv else 1)

    pdf_path = sys.argv[1]

    if not Path(pdf_path).exists():
        print(f"cc-ocr: file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    if not pdf_path.lower().endswith(".pdf"):
        print("cc-ocr: expected a .pdf file", file=sys.stderr)
        sys.exit(1)

    if not all([
        _check_dep("pdftoppm", "brew install poppler"),
        _check_dep("tesseract", "brew install tesseract"),
    ]):
        sys.exit(1)

    if _has_text_layer(pdf_path):
        print(
            "cc-ocr: PDF appears to have a text layer — cc-markitdown may produce better output.",
            file=sys.stderr,
        )

    # Use a temp dir under HOME, not /tmp — tesseract fails with a Leptonica
    # sandboxing error when image files are under /tmp on macOS.
    tmp_dir = Path(tempfile.mkdtemp(dir=Path.home()))
    try:
        print("cc-ocr: converting pages to images ...", file=sys.stderr)
        result = subprocess.run(
            ["pdftoppm", "-r", "300", "-jpeg", pdf_path, str(tmp_dir / "page")],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode != 0:
            print(f"cc-ocr: pdftoppm failed: {result.stderr.strip()}", file=sys.stderr)
            sys.exit(1)

        pages = sorted(tmp_dir.glob("page-*.jpg"))
        if not pages:
            print("cc-ocr: pdftoppm produced no page images", file=sys.stderr)
            sys.exit(1)

        print(f"cc-ocr: running OCR on {len(pages)} page(s) ...", file=sys.stderr)

        parts = []
        failed = 0
        for page in pages:
            # tesseract must be invoked with cwd=tmp_dir so it can open the file
            r = subprocess.run(
                ["tesseract", page.name, "stdout", "-l", "eng"],
                capture_output=True, text=True,
                cwd=tmp_dir, timeout=60,
            )
            if r.returncode != 0 or not r.stdout.strip():
                print(f"cc-ocr: tesseract failed on {page.name}: {r.stderr.strip()}", file=sys.stderr)
                failed += 1
                continue
            parts.append(r.stdout.rstrip())

        if not parts:
            print("cc-ocr: OCR produced no output", file=sys.stderr)
            sys.exit(1)

        if failed:
            print(f"cc-ocr: {failed}/{len(pages)} pages failed OCR", file=sys.stderr)

        source = Path(pdf_path).name
        sys.stdout.write(f"<!-- OCR output from {source} — may contain recognition artifacts -->\n\n")
        sys.stdout.write("\n\n".join(parts))
        sys.stdout.write("\n")
        print(f"cc-ocr: done ({len(parts)}/{len(pages)} pages)", file=sys.stderr)

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
