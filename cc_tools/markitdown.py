import sys
from markitdown.__main__ import main


def main_wrapper():
    for arg in sys.argv[1:]:
        if not arg.startswith("-") and arg.lower().endswith(".md"):
            print(
                f"cc-markitdown: refusing to convert '{arg}' — "
                "input is already Markdown. Use the Read tool instead.",
                file=sys.stderr,
            )
            sys.exit(1)
    main()
