"""Regression harness for cc-arxiv --src pipeline.

Usage:
    pytest tests/test_arxiv_src.py                   # run against cached outputs only
    pytest tests/test_arxiv_src.py --regenerate      # re-fetch from arXiv, update cache

Cached expected outputs live in tests/corpus/expected/<arxiv_id>.md.
Files in that directory are .gitignore'd (network artifacts, not source).
"""
import os
import re
import subprocess
import sys

import pytest
import yaml

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "corpus")
EXPECTED_DIR = os.path.join(CORPUS_DIR, "expected")


def load_corpus():
    entries = []
    for fname in sorted(os.listdir(CORPUS_DIR)):
        if not fname.endswith(".yaml"):
            continue
        with open(os.path.join(CORPUS_DIR, fname)) as f:
            raw = f.read()
        # Strip YAML frontmatter delimiters if present
        body = re.sub(r"^---\n", "", raw)
        body = re.sub(r"\n---\n?$", "", body)
        data = yaml.safe_load(body)
        entries.append(data)
    return entries


def corpus_id(entry):
    return entry.get("arxiv_id") or entry.get("title", "unknown").replace(" ", "-")[:30]


CORPUS = load_corpus()
ARXIV_ENTRIES = [e for e in CORPUS if e.get("arxiv_id") and e.get("pipeline") != "no-source"]


def fetch_paper(arxiv_id: str) -> str:
    result = subprocess.run(
        ["cc-arxiv", "--src", arxiv_id],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        pytest.fail(f"cc-arxiv --src {arxiv_id} failed:\n{result.stderr}")
    return result.stdout


def get_or_fetch(entry: dict, regenerate: bool) -> str:
    arxiv_id = entry["arxiv_id"]
    cache_path = os.path.join(EXPECTED_DIR, f"{arxiv_id}.md")
    if regenerate or not os.path.exists(cache_path):
        content = fetch_paper(arxiv_id)
        with open(cache_path, "w") as f:
            f.write(content)
    else:
        with open(cache_path) as f:
            content = f.read()
    return content


def assert_clean_html(content: str, arxiv_id: str):
    assert "<span" not in content, f"{arxiv_id}: residual <span> tags"
    assert "<img" not in content, f"{arxiv_id}: residual <img> tags"
    assert "<figure" not in content, f"{arxiv_id}: residual <figure> tags"
    assert "<br" not in content, f"{arxiv_id}: residual <br> tags"


def assert_clean_anchors(content: str, arxiv_id: str):
    assert "[]{#" not in content, f"{arxiv_id}: residual empty anchor []{{#...}}"


def assert_clean_heading_attrs(content: str, arxiv_id: str):
    # {#id .class} style attrs on headings
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
    # Preamble block: $$\newcommand... lines
    macros_found = len(re.findall(r"\\(?:newcommand|renewcommand|providecommand|DeclareMathOperator|def\\)", content))
    assert macros_found >= min_count, (
        f"{arxiv_id}: expected ≥{min_count} macro definitions, found {macros_found}"
    )


@pytest.fixture
def regenerate(request):
    return request.config.getoption("--regenerate", default=False)


def pytest_addoption(parser):
    parser.addoption(
        "--regenerate",
        action="store_true",
        default=False,
        help="Re-fetch papers from arXiv and update cached expected outputs",
    )


@pytest.mark.parametrize("entry", ARXIV_ENTRIES, ids=[corpus_id(e) for e in ARXIV_ENTRIES])
def test_arxiv_src_paper(entry, regenerate):
    arxiv_id = entry["arxiv_id"]
    cache_path = os.path.join(EXPECTED_DIR, f"{arxiv_id}.md")

    if not regenerate and not os.path.exists(cache_path):
        pytest.skip(f"No cached output for {arxiv_id}; run with --regenerate to fetch")

    content = get_or_fetch(entry, regenerate)

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
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode != 0, (
        f"{arxiv_id}: expected non-zero exit for no-source paper, got success"
    )
