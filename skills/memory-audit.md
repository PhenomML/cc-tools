Audit the auto-memory files for the current project, surface stale or promotable entries, and prompt for each. $ARGUMENTS (optional: `--promote-to <wiki-path>` to set default wiki destination for public memories)

## Step 1 — Locate memory directory

Derive the memory path from the current working directory:

```bash
MEMORY_DIR="$HOME/.claude/projects/$(echo "$PWD" | sed 's|/|-|g')/memory"
ls "$MEMORY_DIR" 2>/dev/null | head -5
```

If the directory does not exist or is empty, report "No memory found for this project" and stop.

## Step 2 — Detect workspace context

```bash
test -d wiki && echo "wiki: yes" || echo "wiki: no"
test -f log.md && echo "log.md: yes" || echo "log.md: no"
test -f ORIENTATION.md && echo "ORIENTATION.md: yes" || echo "ORIENTATION.md: no"
```

This determines which destinations are available when trimming ORIENTATION.md or triaging memories:

| Context | Available destinations |
|---|---|
| Wiki present (`wiki/` exists) | memory files, `log.md`, wiki pages, delete |
| Brief only (no `wiki/`) | memory files, `log.md` (if present), delete |
| No `log.md` | memory files, wiki pages (if wiki present), delete |

Carry these availability flags through all subsequent steps. Do not offer "promote to wiki" if no `wiki/` directory exists.

## Step 3 — Read the index

```bash
cat "$MEMORY_DIR/MEMORY.md"
```

Note the total entry count. This is the audit scope.

## Step 4 — Check ORIENTATION.md size

```bash
wc -l ORIENTATION.md 2>/dev/null || echo "No ORIENTATION.md found"
```

ORIENTATION.md is read at every session start. It should contain *current state only* — not a running history. Size thresholds:

- **Under 150 lines** — healthy; no action needed
- **150–300 lines** — flag; review for resolved items that can be retired to `log.md` or the wiki
- **Over 300 lines** — bloated; session-start overhead is significant; trim before the audit continues

If bloated, read the file and identify sections by destination:

- **Promote to memory file** — settled decisions, environment facts, API quirks, infrastructure conventions, behavioral patterns. These belong in typed memory files (`feedback`, `project`, `reference`) where they persist across sessions and are indexed by MEMORY.md. This is the primary destination for most trimmed content.
- **Retire to `log.md`** — resolved commissions, completed experiment phases, superseded decisions. Historical record, not active knowledge.
- **Promote to wiki** — factual knowledge useful to the whole team (human-visible). Use the wiki path, not memory.
- **Delete** — truly ephemeral state that is no longer true and has no archival value.

Report what should be cut and where each section should go. Ask the researcher to confirm before editing. Create new memory files as needed; update MEMORY.md index for any new entries.

The target is a document a fresh Claude can read in under 2 minutes and have genuine current-state orientation — not a chronicle.

## Step 5 — Scan each memory file

For each `.md` file in the memory directory (excluding `MEMORY.md`), collect:

**Age** — modification time:
```bash
find "$MEMORY_DIR" -name "*.md" ! -name "MEMORY.md" \
  -exec stat -f "%Sm %N" -t "%Y-%m-%d" {} \; | sort
```

**Staleness keywords** — entries that mention pending states, future dates, or unresolved items:
```bash
grep -rl "pending\|awaiting\|TBD\|blocking\|quiescent\|deferred\|not yet\|open\|OPEN" \
  "$MEMORY_DIR" --include="*.md" | grep -v MEMORY.md
```

**`review_after` fields** — entries with explicit expiry signals:
```bash
grep -rl "review_after\|expires" "$MEMORY_DIR" --include="*.md"
```

Read the flagged files in full. Also read any file older than 60 days that has not been updated this session.

## Step 6 — Classify findings

Group entries into three buckets:

**Overdue** — has `review_after` date that has passed, or contains a specific past date that was a milestone (e.g., "deadline 2026-06-18" when today is past that date).

**Stale-likely** — no `review_after` but contains staleness keywords (pending, awaiting, blocking) and is older than 30 days. The pending state may have resolved without the memory being updated.

**Promotable** — contains factual knowledge (API quirks, environment setup, design rationale, infrastructure conventions) that would be useful to human team members, not just AI behavioral corrections. These are candidates for the `public` memory type (issue #41) — currently they should be manually promoted to the wiki.

**Current** — no flags. Report count only; do not enumerate.

## Step 7 — Present findings

Report each flagged entry with:
- Memory name and one-line description from MEMORY.md
- Age
- Flag reason (overdue / stale-likely / promotable)
- Key excerpt showing why it was flagged (1–3 lines)

Format example:
```
STALE-LIKELY (47 days) — project_antigravity_migration.md
  "Gemini CLI → Antigravity CLI migration; hard deadline June 18, 2026"
  Flag: deadline has passed; status may have changed
```

Do not make any changes yet. Present all findings first.

## Step 8 — Triage each flagged entry

For each flagged entry, ask the researcher to choose:

1. **Current** — memory is accurate as-is; no action
2. **Update** — memory needs editing; make the edit now
3. **Retire** — fact is no longer relevant; remove from MEMORY.md index and archive or delete the file
4. **Promote to wiki** — factual knowledge that belongs in the shared wiki; help the researcher identify the right wiki page and add a pointer in the memory file

For **Promote to wiki**: suggest a destination based on content. If `$ARGUMENTS` included `--promote-to <path>`, use that as the default destination directory.

After each decision, apply it before moving to the next entry. Do not batch changes.

## Step 9 — Update MEMORY.md

After all triage decisions:
- Remove retired entries from MEMORY.md
- Update description lines for any updated memories
- Report final count: X reviewed, Y updated, Z retired, W promoted

## Notes

- The memory system reminder warns that memories are point-in-time observations. Treat age as a signal, not a verdict — a 90-day-old memory about a stable convention may be perfectly current.
- Behavioral memories (`feedback` type) rarely go stale; factual memories (`project`, `reference` type) go stale when the project moves.
- If a promoted memory now lives in the wiki, update the memory file to a pointer: "See `path/to/wiki/page.md#Section`" and change its description in MEMORY.md accordingly.
