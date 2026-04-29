"""
Scaffold a research brief directory and launch Claude to run /wiki-brief.

Usage:
    cc-wiki-brief "Databricks" "Is Databricks winning the data lakehouse war?"
    cc-wiki-brief "Ilya Sutskever" --person "What is Ilya doing after OpenAI?"
    cc-wiki-brief "CRISPR" --dir ~/Research/Topics
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

RESEARCH_DIR = Path.home() / "Research"

# Words that signal a corporate entity even when title-cased.
_COMPANY_WORDS = {
    "inc", "llc", "corp", "ltd", "co", "ai", "technologies", "technology",
    "software", "labs", "research", "systems", "solutions", "services",
    "capital", "ventures", "group", "partners", "therapeutics", "robotics",
}

# Suffixes that appear in abstract nouns and technical terms but not person names.
# "Compressed Sensing" → "sensing" ends in "ing" → not a person name.
_ABSTRACT_SUFFIXES = ("ing", "tion", "sion", "ence", "ance", "ics", "ism", "ity", "ogy")


def to_slug(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^\w\s-]", "", s)   # drop punctuation, keep hyphens
    s = re.sub(r"[\s_]+", "-", s)    # spaces → hyphens
    return re.sub(r"-+", "-", s).strip("-")


def infer_category(name: str) -> str:
    """Heuristic: multi-word title-cased names with no corporate keywords or abstract
    noun suffixes are treated as People; everything else falls to Companies.
    Use --topic, --person, --company, or --dir to override."""
    words = name.strip().split()
    if len(words) < 2:
        return "Companies"
    if {w.lower() for w in words} & _COMPANY_WORDS:
        return "Companies"
    if all(w[0].isupper() for w in words):
        # Reject if any word ends in a suffix common to abstract nouns/concepts.
        if any(w.lower().endswith(s) for w in words for s in _ABSTRACT_SUFFIXES):
            return "Companies"
        return "People"
    return "Companies"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a wiki brief directory and invoke /wiki-brief in Claude."
    )
    parser.add_argument("subject", help='Subject name, e.g. "Databricks"')
    parser.add_argument("question", nargs="?", default="", help="Driving research question")

    placement = parser.add_mutually_exclusive_group()
    placement.add_argument(
        "--person", action="store_true",
        help="Place under ~/Research/People/ (default: auto-detected)",
    )
    placement.add_argument(
        "--company", action="store_true",
        help="Place under ~/Research/Companies/ (default: auto-detected)",
    )
    placement.add_argument(
        "--topic", action="store_true",
        help="Place under ~/Research/Topics/",
    )
    placement.add_argument(
        "--dir", metavar="DIR",
        help="Explicit parent directory; slug appended automatically",
    )

    args = parser.parse_args()

    # Resolve parent directory
    if args.dir:
        parent = Path(args.dir).expanduser().resolve()
    elif args.person:
        parent = RESEARCH_DIR / "People"
    elif args.company:
        parent = RESEARCH_DIR / "Companies"
    elif args.topic:
        parent = RESEARCH_DIR / "Topics"
    else:
        parent = RESEARCH_DIR / infer_category(args.subject)

    slug = to_slug(args.subject)
    brief_dir = parent / slug

    brief_dir.mkdir(parents=True, exist_ok=True)
    print(f"Brief directory: {brief_dir}", file=sys.stderr)

    # Build the /wiki-brief invocation that Claude will receive as its first message.
    if args.question:
        prompt = f'/wiki-brief "{args.subject}" "{args.question}"'
    else:
        prompt = f'/wiki-brief "{args.subject}"'

    # Launch an interactive Claude Code session anchored at the brief directory.
    # Passing the prompt as a positional argument seeds it as the first user message.
    result = subprocess.run(["claude", prompt], cwd=brief_dir)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
