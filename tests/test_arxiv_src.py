"""Regression harness for cc-arxiv --src pipeline.

Two-level cache — arXiv is hit at most once per paper:

  tests/corpus/tarballs/<id>.tar.gz   raw source tarball (gitignored)
  tests/corpus/expected/<id>.md       converted markdown output (gitignored)

Normal run: skip if no cached expected output.
--regenerate: rebuild expected/ from tarballs/ (fetching from arXiv only if
              the tarball isn't already cached).
--refetch:    force re-download of tarballs from arXiv, then reconvert.
"""
import os
import re
import subprocess
import urllib.request

import pytest
import yaml

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "corpus")
TARBALLS_DIR = os.path.join(CORPUS_DIR, "tarballs")
EXPECTED_DIR = os.path.join(CORPUS_DIR, "expected")


def load_corpus():
    entries = []
    for fname in sorted(os.listdir(CORPUS_DIR)):
        if not fname.endswith(".yaml"):
            continue
        with open(os.path.join(CORPUS_DIR, fname)) as f:
            raw = f.read()
        body = re.sub(r"^---\n", "", raw)
        body = re.sub(r"\n---\n?$", "", body)
        data = yaml.safe_load(body)
        entries.append(data)
    return entries


def corpus_id(entry):
    return entry.get("arxiv_id") or entry.get("title", "unknown").replace(" ", "-")[:30]


def tarball_filename(arxiv_id: str) -> str:
    # math/0409186 → math-0409186.tar.gz (slash not valid in filenames)
    return arxiv_id.replace("/", "-") + ".tar.gz"


def expected_filename(arxiv_id: str) -> str:
    return arxiv_id.replace("/", "-") + ".md"


CORPUS = load_corpus()
ARXIV_ENTRIES = [e for e in CORPUS if e.get("arxiv_id") and e.get("pipeline") != "no-source"]


def fetch_tarball(arxiv_id: str, tarball_path: str) -> None:
    url = f"https://arxiv.org/src/{arxiv_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "cc-tools/test-harness"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    os.makedirs(os.path.dirname(tarball_path), exist_ok=True)
    with open(tarball_path, "wb") as f:
        f.write(data)


def convert_from_tarball(arxiv_id: str, tarball_path: str) -> str:
    result = subprocess.run(
        ["cc-arxiv", "--src", "--local-src", tarball_path, arxiv_id],
        capture_output=True, text=True, timeout=300,
    )
    if result.returncode != 0:
        pytest.fail(f"cc-arxiv --src --local-src {arxiv_id} failed:\n{result.stderr}")
    return result.stdout


def get_expected(entry: dict, regenerate: bool, refetch: bool) -> str:
    arxiv_id = entry["arxiv_id"]
    tarball_path = os.path.join(TARBALLS_DIR, tarball_filename(arxiv_id))
    expected_path = os.path.join(EXPECTED_DIR, expected_filename(arxiv_id))

    if not regenerate and not refetch and os.path.exists(expected_path):
        with open(expected_path) as f:
            return f.read()

    # Need to (re)generate expected output
    if refetch or not os.path.exists(tarball_path):
        fetch_tarball(arxiv_id, tarball_path)

    content = convert_from_tarball(arxiv_id, tarball_path)
    os.makedirs(EXPECTED_DIR, exist_ok=True)
    with open(expected_path, "w") as f:
        f.write(content)
    return content


def assert_clean_html(content: str, arxiv_id: str):
    assert "<span" not in content, f"{arxiv_id}: residual <span> tags"
    assert "<img" not in content, f"{arxiv_id}: residual <img> tags"
    assert "<figure" not in content, f"{arxiv_id}: residual <figure> tags"
    assert "<br" not in content, f"{arxiv_id}: residual <br> tags"


def assert_clean_anchors(content: str, arxiv_id: str):
    assert "[]{#" not in content, f"{arxiv_id}: residual empty anchors []{{#...}}"


def assert_clean_heading_attrs(content: str, arxiv_id: str):
    assert not re.search(r"^#+.*\{#", content, re.MULTILINE), (
        f"{arxiv_id}: residual heading attributes {{#...}}"
    )


def assert_header(content: str, arxiv_id: str):
    first_line = next((l for l in content.splitlines() if l.strip()), "")
    assert first_line.startswith("<!-- Source: arXiv:"), (
        f"{arxiv_id}: first non-empty line not a source comment, got: {first_line!r}"
    )


def assert_pipeline_tag(content: str, entry: dict):
    arxiv_id = entry["arxiv_id"]
    pipeline = entry.get("pipeline")
    if pipeline == "make4ht":
        assert "via make4ht+mathjax" in content, (
            f"{arxiv_id}: expected 'via make4ht+mathjax' pipeline tag"
        )
    elif pipeline == "pandoc-latex":
        assert "via pandoc-latex" in content, (
            f"{arxiv_id}: expected 'via pandoc-latex' pipeline tag"
        )


def assert_macro_count(content: str, entry: dict):
    arxiv_id = entry["arxiv_id"]
    min_count = entry.get("macro_count_min", 0)
    if min_count <= 0:
        return
    macros_found = len(re.findall(
        r"\\(?:newcommand|renewcommand|providecommand|DeclareMathOperator|def\\)",
        content,
    ))
    assert macros_found >= min_count, (
        f"{arxiv_id}: expected ≥{min_count} macro definitions, found {macros_found}"
    )


def pytest_addoption(parser):
    parser.addoption(
        "--regenerate",
        action="store_true",
        default=False,
        help="Reconvert from cached tarballs (fetch tarball from arXiv if not cached).",
    )
    parser.addoption(
        "--refetch",
        action="store_true",
        default=False,
        help="Force re-download of tarballs from arXiv, then reconvert.",
    )


@pytest.fixture
def regenerate(request):
    return request.config.getoption("--regenerate", default=False)


@pytest.fixture
def refetch(request):
    return request.config.getoption("--refetch", default=False)


@pytest.mark.parametrize("entry", ARXIV_ENTRIES, ids=[corpus_id(e) for e in ARXIV_ENTRIES])
def test_arxiv_src_paper(entry, regenerate, refetch):
    arxiv_id = entry["arxiv_id"]
    expected_path = os.path.join(EXPECTED_DIR, expected_filename(arxiv_id))

    if not regenerate and not refetch and not os.path.exists(expected_path):
        pytest.skip(f"No cached output for {arxiv_id}; run with --regenerate to build cache")

    content = get_expected(entry, regenerate, refetch)

    assert_header(content, arxiv_id)
    assert_clean_html(content, arxiv_id)
    assert_clean_anchors(content, arxiv_id)
    assert_clean_heading_attrs(content, arxiv_id)
    assert_pipeline_tag(content, entry)
    assert_macro_count(content, entry)


@pytest.mark.parametrize(
    "entry",
    [e for e in CORPUS if e.get("pipeline") == "no-source"],
    ids=[corpus_id(e) for e in CORPUS if e.get("pipeline") == "no-source"],
)
def test_no_source_papers_graceful(entry):
    """Papers without arXiv preprints should fail gracefully (non-zero exit, not crash)."""
    arxiv_id = entry.get("arxiv_id")
    if arxiv_id is None:
        pytest.skip("No arxiv_id — cannot invoke cc-arxiv")
    result = subprocess.run(
        ["cc-arxiv", "--src", arxiv_id],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode != 0, (
        f"{arxiv_id}: expected non-zero exit for no-source paper, got success"
    )
