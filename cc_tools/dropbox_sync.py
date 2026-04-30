"""
Mirror the current project or wiki to a shared Dropbox folder.

Setup (run once from the project root):
    cc-dropbox-sync --setup ~/Dropbox/Shared_DLD_AWD/Projects

Sync (run after git push):
    cc-dropbox-sync

Preview without transferring:
    cc-dropbox-sync --dry-run

Config is stored in .dropbox-sync-target in the project root (gitignored).
The tool creates <target>/<project-name>/ and rsyncs the project into it.
Respects .gitignore automatically — gitignored content is never transferred.
Deletions in the source are propagated (--delete); Dropbox is a mirror,
not an archive.
"""

import argparse
import subprocess
import sys
from pathlib import Path

CONFIG_FILENAME = ".dropbox-sync-target"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mirror the current project to a shared Dropbox folder."
    )
    parser.add_argument(
        "--setup", metavar="DIR",
        help="Set sync target directory (written to .dropbox-sync-target in cwd).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be transferred without making any changes.",
    )
    args = parser.parse_args()

    if args.setup:
        target = Path(args.setup).expanduser().resolve()
        config = Path.cwd() / CONFIG_FILENAME
        config.write_text(str(target) + "\n")
        print(f"Sync target: {target}", file=sys.stderr)
        print(f"Config:      {config}", file=sys.stderr)

        gitignore = Path.cwd() / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            if CONFIG_FILENAME not in content:
                gitignore.write_text(content.rstrip() + f"\n{CONFIG_FILENAME}\n")
                print(f"Added {CONFIG_FILENAME} to .gitignore", file=sys.stderr)
            else:
                print(f"{CONFIG_FILENAME} already in .gitignore", file=sys.stderr)
        else:
            print(f"No .gitignore found — add {CONFIG_FILENAME} manually", file=sys.stderr)
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

    source = str(Path.cwd()) + "/"
    dest = str(target_dir) + "/"

    dry_run_flag = ["-n"] if args.dry_run else []
    if args.dry_run:
        print(f"Dry run — no files will be transferred.", file=sys.stderr)
    print(f"Syncing {project_name}/ → {target_dir}", file=sys.stderr)

    result = subprocess.run([
        "rsync", "-av", "--delete",
        "--exclude=.git/",
        "--filter=:- .gitignore",
        *dry_run_flag,
        source, dest,
    ])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
