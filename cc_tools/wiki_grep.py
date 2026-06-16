"""
cc-wiki-grep — token-efficient wiki search for Claude Code sessions.

Usage:
  cc-wiki-grep PATTERN [PATH]           Search wiki .md files; show file § heading: match
  cc-wiki-grep --section HEADING FILE   Extract a named section from FILE
  cc-wiki-grep --frontmatter [PATH]     Dump YAML frontmatter from all .md files in PATH
  cc-wiki-grep --tags [PATH]            List all #tags found in INDEX.md files
  cc-wiki-grep -l PATTERN [PATH]        Print matching filenames only

Excludes raw/ directories by default (source material, not knowledge).
Default PATH is wiki/ relative to cwd.
"""

import argparse
import re
import sys
from pathlib import Path


def _to_python_regex(pattern: str) -> str:
    r"""Translate BRE \| alternation to Python | so grep habits work."""
    return re.sub(r"\\\|", "|", pattern)


def _wiki_files(path: Path) -> list[Path]:
    """All .md files under path, excluding raw/ directories."""
    if path.is_file():
        return [path]
    return sorted(f for f in path.rglob("*.md") if "raw" not in f.parts)


def _heading_above(lines: list[str], lineno: int) -> str:
    """Return the nearest # or ## heading above lineno (0-indexed)."""
    for i in range(lineno, -1, -1):
        if re.match(r"^#{1,3} ", lines[i]):
            return lines[i].strip()
    return "(preamble)"


def cmd_search(pattern: str, path: Path, context: int, files_only: bool, ignore_case: bool) -> int:
    flags = re.IGNORECASE if ignore_case else 0
    try:
        regex = re.compile(_to_python_regex(pattern), flags)
    except re.error as e:
        print(f"cc-wiki-grep: invalid pattern: {e}", file=sys.stderr)
        return 2

    found = False
    for filepath in _wiki_files(path):
        try:
            lines = filepath.read_text().splitlines()
        except Exception:
            continue
        matches = [i for i, line in enumerate(lines) if regex.search(line)]
        if not matches:
            continue
        found = True
        if files_only:
            print(filepath)
            continue
        for lineno in matches:
            heading = _heading_above(lines, lineno)
            start = max(0, lineno - context)
            end = min(len(lines), lineno + context + 1)
            print(f"\n{filepath} § {heading} (line {lineno + 1})")
            for i in range(start, end):
                marker = ">" if i == lineno else " "
                print(f"  {marker} {lines[i]}")

    return 0 if found else 1


def cmd_section(heading_pattern: str, filepath: Path, ignore_case: bool) -> int:
    flags = re.IGNORECASE if ignore_case else 0
    try:
        regex = re.compile(_to_python_regex(heading_pattern), flags)
    except re.error as e:
        print(f"cc-wiki-grep: invalid pattern: {e}", file=sys.stderr)
        return 2

    try:
        lines = filepath.read_text().splitlines()
    except Exception as e:
        print(f"cc-wiki-grep: cannot read {filepath}: {e}", file=sys.stderr)
        return 2

    in_section = False
    out = []
    for line in lines:
        if re.match(r"^#{1,3} ", line):
            if in_section:
                break
            if regex.search(line):
                in_section = True
                out.append(line)
        elif in_section:
            out.append(line)

    if not out:
        print(f"cc-wiki-grep: section '{heading_pattern}' not found in {filepath}", file=sys.stderr)
        return 1

    print("\n".join(out))
    return 0


def cmd_frontmatter(path: Path) -> int:
    found = False
    for filepath in _wiki_files(path):
        try:
            lines = filepath.read_text().splitlines()
        except Exception:
            continue
        if not lines or lines[0].strip() != "---":
            continue
        fm = []
        for line in lines[1:]:
            if line.strip() == "---":
                break
            fm.append(line)
        if fm:
            found = True
            print(f"\n--- {filepath}")
            print("\n".join(fm))
    return 0 if found else 1


def cmd_tags(path: Path) -> int:
    tags: set[str] = set()
    for f in path.rglob("INDEX.md") if path.is_dir() else [path]:
        try:
            for m in re.finditer(r"#([\w][\w-]*)", f.read_text()):
                tags.add(m.group(0))
        except Exception:
            continue
    if not tags:
        return 1
    for tag in sorted(tags):
        print(tag)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cc-wiki-grep",
        description="Token-efficient wiki search for Claude Code sessions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  cc-wiki-grep "compaction" wiki/               search all wiki pages
  cc-wiki-grep "#inference" wiki/INDEX.md       find pages by tag
  cc-wiki-grep -l "make4ht" wiki/               filenames only
  cc-wiki-grep -n 5 "REPL" wiki/papers/         5 lines of context
  cc-wiki-grep --section "Results" wiki/papers/zhang-2025-rlm.md
  cc-wiki-grep --frontmatter wiki/papers/
  cc-wiki-grep --tags wiki/
""",
    )
    parser.add_argument("pattern", nargs="?", help="Search pattern (regex) or FILE when using --section")
    parser.add_argument("path", nargs="?", help="File or directory (default: wiki/)")
    parser.add_argument("--section", "-s", metavar="HEADING",
                        help="Extract named ## section from FILE (FILE = positional arg)")
    parser.add_argument("--frontmatter", "-f", action="store_true",
                        help="Dump YAML frontmatter from .md files in PATH")
    parser.add_argument("--tags", "-t", action="store_true",
                        help="List all #tags from INDEX.md files under PATH")
    parser.add_argument("--context", "-n", type=int, default=2,
                        help="Lines of context around each match (default: 2)")
    parser.add_argument("--files-only", "-l", action="store_true",
                        help="Print matching filenames only")
    parser.add_argument("--ignore-case", "-i", action="store_true",
                        help="Case-insensitive matching")

    args = parser.parse_args()

    if args.section:
        # cc-wiki-grep --section HEADING FILE
        filepath = Path(args.pattern or args.path or "")
        if not filepath or not filepath.exists():
            parser.error("--section requires a FILE argument")
        sys.exit(cmd_section(args.section, filepath, args.ignore_case))

    elif args.frontmatter:
        path = Path(args.pattern or args.path or "wiki/")
        sys.exit(cmd_frontmatter(path))

    elif args.tags:
        path = Path(args.pattern or args.path or "wiki/")
        sys.exit(cmd_tags(path))

    elif args.pattern:
        path = Path(args.path or "wiki/")
        sys.exit(cmd_search(args.pattern, path, args.context, args.files_only, args.ignore_case))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
