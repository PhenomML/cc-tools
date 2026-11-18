#!/usr/bin/env python3
"""Compaction hook for Claude Code (SessionStart `compact` and PreCompact).

Reads the hook input JSON on stdin and writes the hook output on stdout.

SessionStart (source == "compact"): inject a few factual statements into the
compacted context. Statements, not instructions: imperative text injected by a
hook can trip prompt-injection defences. Nothing is read beyond the last log.md
heading, so the cost is a few hundred tokens.

PreCompact: print guidance for the summariser (stdout on exit 0 steers the
summary, capped at 10,000 characters by the harness).

Any other event or source prints nothing. Never fails the session: errors exit 0.
"""
import json
import os
import re
import sys

OPERATIONS_CANDIDATES = ("operations.md", "wiki/operations.md", "OPERATIONS.md")


def last_log_heading(cwd):
    path = os.path.join(cwd, "log.md")
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            headings = [l.strip() for l in f if l.startswith("## [")]
    except OSError:
        return None
    return headings[-1] if headings else None


def operations_doc(cwd):
    for rel in OPERATIONS_CANDIDATES:
        if os.path.isfile(os.path.join(cwd, rel)):
            return rel
    return None


def session_start(cwd):
    lines = [
        "This conversation was compacted. The summary replaces the earlier context; "
        "documents read earlier in the session are in this context only where the summary quotes them.",
    ]
    ops = operations_doc(cwd)
    if ops:
        lines.append(
            f"The project has an operations document at {ops}. No read of it is recorded in this context."
        )
    heading = last_log_heading(cwd)
    if heading:
        lines.append(f"The most recent log.md entry heading is: {heading}")
    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(lines),
        }
    }


PRE_COMPACT_GUIDANCE = (
    "In the summary, keep verbatim: the paths of the project's procedure documents "
    "(CLAUDE.md Session Start list, operations document) and the fact that they must be "
    "re-read before the first command that touches a machine or shared resource; "
    "the standing orders that govern outward-facing actions; "
    "and the last action in flight, with its target."
)


def main():
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    event = data.get("hook_event_name", "")
    cwd = data.get("cwd") or os.getcwd()
    if event == "SessionStart" and data.get("source") == "compact":
        print(json.dumps(session_start(cwd)))
    elif event == "PreCompact":
        print(PRE_COMPACT_GUIDANCE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
