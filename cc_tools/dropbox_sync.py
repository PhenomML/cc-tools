"""
Mirror the current project or wiki to a shared Dropbox folder.

Setup (run once from the project root):
    cc-dropbox-sync --setup ~/Dropbox/Dave-Andrew-Shared/sync

Sync (run after git push):
    cc-dropbox-sync

Config is stored in .dropbox-sync-target in the project root (gitignored).
The tool creates <target>/<project-name>/ and rsyncs the project into it.
Deletions in the source are propagated (--delete); Dropbox is a mirror,
not an archive.
"""

import argparse
import subprocess
import sys
from pathlib import Path

CONFIG_FILENAME = ".dropbox-sync-target"

RSYNC_EXCLUDES = [
    ".git/",
    "raw/",
    "ideas/",
    "*.pyc",
    "__pycache__/",
    ".venv/",
    "*.egg-info/",
    ".dropbox-sync-target",
]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mirror the current project to a shared Dropbox folder."
    )
    parser.add_argument(
        "--setup", metavar="DIR",
        help="Set sync target directory (written to .dropbox-sync-target in cwd).",
    )
    args = parser.parse_args()

    if args.setup:
        target = Path(args.setup).expanduser().resolve()
        config = Path.cwd() / CONFIG_FILENAME
        config.write_text(str(target) + "\n")
        print(f"Sync target: {target}", file=sys.stderr)
        print(f"Config:      {config}", file=sys.stderr)
        print(f"Ensure {CONFIG_FILENAME} is in .gitignore.", file=sys.stderr)
        return

    config = Path.cwd() / CONFIG_FILENAME
    if not config.exists():
        print(
            f"No {CONFIG_FILENAME} found in {Path.cwd()}.\n"
            f"Run from the project root, or configure with:\n"
            f"  cc-dropbox-sync --setup <dropbox-parent-dir>",
            file=sys.stderr,
        )
        sys.exit(1)

    sync_parent = Path(config.read_text().strip()).expanduser().resolve()
    project_name = Path.cwd().name
    target_dir = sync_parent / project_name

    target_dir.mkdir(parents=True, exist_ok=True)

    exclude_args = []
    for exc in RSYNC_EXCLUDES:
        exclude_args.extend(["--exclude", exc])

    source = str(Path.cwd()) + "/"
    dest = str(target_dir) + "/"

    print(f"Syncing {project_name}/ → {target_dir}", file=sys.stderr)

    result = subprocess.run(
        ["rsync", "-av", "--delete", *exclude_args, source, dest]
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
