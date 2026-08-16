import pytest

from cc_tools.wiki_brief_start import infer_category


@pytest.mark.parametrize(
    "name,expected",
    [
        # Topics: multi-word, title-cased, rejected from People by an abstract
        # noun suffix. Regression coverage for the Matrix Denoising -> Companies
        # misrouting (2026-08-12) — infer_category had no Topics branch at all.
        ("Matrix Denoising", "Topics"),
        ("Compressed Sensing", "Topics"),
        ("Approximate Message Passing", "Topics"),
        # People: multi-word, title-cased, no corporate keyword, no abstract suffix.
        ("Ilya Sutskever", "People"),
        ("Jane Smith", "People"),
        # Companies: single word, or a corporate keyword present.
        ("Databricks", "Companies"),
        ("OpenAI", "Companies"),
        ("Anthropic Research", "Companies"),
        ("Marqov Capital", "Companies"),
    ],
)
def test_infer_category(name, expected):
    assert infer_category(name) == expected
