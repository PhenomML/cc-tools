Promote settled knowledge from a research brief into the wiki: $ARGUMENTS

`$ARGUMENTS` is the path to the brief directory (e.g. `~/Research/Topics/compressed-sensing`
or `../People/ilya-sutskever`). Run from the wiki root.

Promotion is not archival — a brief stays active as long as research continues. Run
`/wiki-promote` again after each significant brief session to accrete newly settled
conclusions into the wiki incrementally.

**New-session requirement:** skill files are cached at session start. If `setup-claude.sh`
was run in this session, start a new session before invoking `/wiki-promote` — otherwise
you are running the previous (or absent) version of the skill.

## Detect mode

Derive the slug from the brief directory basename (it is already kebab-case).
Search for `*/research/<slug>.md` across all sub-wikis in the wiki root:

```bash
find . -path "*/research/<slug>.md" -not -path "./raw/*"
```

- Found → **UPDATE mode**
- Not found → **CREATE mode**

## Step 1 — Read the brief (both modes)

Read the brief's `index.md` to determine: which sub-wiki(s) this brief informs, the
driving question(s), and the brief's internal structure.

Read the full brief: all concept pages, synthesis documents, and any position/evidence
pages. This is the *explicit* knowledge — the written record of what the brief has established.

Identify and note:
- Driving question(s) — verbatim
- Settled conclusions — claims supported by evidence, sorted by confidence (high / medium / low)
- Open questions — threads still being actively pursued
- Concept and method pages that are stable, self-contained, and cross-wiki relevant

**Sub-wiki mapping:** briefs often use their own internal sub-directories (e.g. `algorithms/`,
`theory/`, `history/`) that do not correspond to wiki sub-wikis. Read the wiki root's
`CLAUDE.md` Sub-wikis table, propose a mapping (e.g. "CS algorithms/ → sciai/"), and
confirm with the researcher before writing any files. Do not infer silently.

## Step 2 — Read brief Claude's memories (both modes)

Brief Claude holds tacit knowledge in its memory directory: what failed, what surprised,
the reasoning behind key judgments. Fold this into settled conclusions and open questions —
it must not be lost in translation to the wiki.

**Finding the memory directory:** take the absolute form of `$ARGUMENTS`, replace every
`/` with `-`, then look under `~/.claude/projects/<encoded>/memory/`.

Example: brief at `/Users/awd/Research/Topics/compressed-sensing`
→ `~/.claude/projects/-Users-awd-Research-Topics-compressed-sensing/memory/`

```bash
ls ~/.claude/projects/-Users-awd-Research-Topics-compressed-sensing/memory/
```

Read each `.md` file. Extract:
- What failed or surprised the researcher
- Reasoning behind key judgments and confidence levels
- Tacit knowledge not captured in written brief pages

If the directory does not exist, warn:
> No memory directory found at `<path>` — tacit knowledge from brief sessions will not be
> captured. To fill this gap, run `/wiki-promote` again after a brief session with memory
> configured.

Ask whether to continue without memories before proceeding. Do not block silently.

## Step 3 — Write or update the anchor page

Determine the target sub-wiki from Step 1. If the brief spans multiple sub-wikis, write
the anchor page in the primary one and list the others in the `wikis:` frontmatter field.

### CREATE mode

Create `<subwiki>/research/` if it does not exist.
Create `<subwiki>/research/index.md` if it does not exist:

```markdown
# Research Threads

<!-- Claude maintains this file. -->

## Active

## Settled

## Archived
```

Write `<subwiki>/research/<slug>.md`:

```yaml
---
title: "<brief title> — <driving question fragment>"
type: research-thread
wikis: [<subwiki(s)>]
brief_path: <relative-path-from-wiki-root-to-brief-dir>
status: active
sources: []
related: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
---
```

**`sources: []` convention:** promoted pages derive their evidence from the brief's
`raw/` directory, which is outside the wiki. Use `sources: []` in frontmatter and add
a prose note in the body referencing the brief: "Source material in `<brief_path>/raw/`."
This is the canonical promotion convention — brief provenance is the source, and
`brief_path` makes it traceable. Do not copy source files into wiki `raw/`.

Body sections:

**`## Driving question`** — verbatim from the brief's index.

**`## Settled conclusions`** — 3–8 bullet points. Each opens with a confidence tag:
`**[High]**`, `**[Medium]**`, or `**[Low]**`. Fold in tacit knowledge from Step 2 where it
raises or lowers confidence or adds nuance not visible in the written pages.

**`## Open questions`** — what the brief is still actively pursuing, one bullet per thread.

**`## Key concepts promoted`** — initially empty; populated in Step 4.

**`## Promotion log`**

| Date | What was added |
|---|---|
| YYYY-MM-DD | Initial promotion: N conclusions, N open questions, N concepts promoted |

### UPDATE mode

Read the existing anchor page. Compare its content against the current brief state from
Steps 1–2.

- **Add** new settled conclusions not yet recorded. Match on meaning, not phrasing — do
  not create near-duplicate bullets.
- **Remove or annotate** open questions that are now answered; move resolved ones to
  settled conclusions with an appropriate confidence tag if they became settled knowledge.
- **Update** `status` if the brief has concluded: `active` → `settled` or `archived`.
- **Update** `updated:` frontmatter date to today.
- **Append** a new row to `## Promotion log` describing what changed in this run.

Do not rewrite sections that have not changed since the last promotion.

## Step 4 — Promote settled concepts (selective, both modes)

For each concept or method page in the brief:

1. **Check for promotion marker** — look for `<!-- promoted: wiki/<path> -->` at the top
   of the brief's concept page. If present, skip — already promoted in a prior run.
2. **Apply the promotion table** to decide what moves:

   | Page type | Promote? | Rationale |
   |---|---|---|
   | Concept pages (stable, settled) | Yes | Core purpose of promotion |
   | Method / algorithm pages (standalone) | Yes | Same |
   | Paper summary pages | No | Too brief-specific; anchor page references them |
   | Project pages | No | Stay in brief; open questions reference them |
   | Synthesis documents | No | Distil key findings into anchor `## Settled conclusions` and `## Open questions` — do not copy synthesis files wholesale into wiki `syntheses/` |
   | Implementation scaffolding / working notes | No | Not settled knowledge |

3. **If promoting:**
   - Write the concept into `<subwiki>/concepts/<slug>.md` (or `methods/` for methods).
   - Add `<!-- promoted: wiki/<subwiki>/concepts/<slug>.md -->` to the top of the brief's
     concept page to prevent re-promotion on future runs.
   - Add the promoted wiki page to the `related:` frontmatter of the anchor page.

Promoted concept pages should include a `related:` link back to the anchor page.

## Step 5 — Bidirectional links

### CREATE mode

Add a `## Wiki Anchor` section to the brief's `index.md`:

```markdown
## Wiki Anchor

Promoted to wiki: [<anchor page title>](<relative-path-from-brief-to-anchor>) (YYYY-MM-DD)
```

The relative path runs from the brief directory to `<wiki-root>/<subwiki>/research/<slug>.md`.
Example: brief at `~/Research/Topics/compressed-sensing`, wiki at `~/Research/wiki`,
subwiki `sciai` → `../../wiki/sciai/research/compressed-sensing.md`.

### UPDATE mode

Verify `## Wiki Anchor` exists in the brief's `index.md` and that the link resolves. Add
or repair if missing (e.g. if the brief's index was regenerated since the last promotion).

## Step 6 — Update wiki indexes and log

**`<subwiki>/research/index.md`** — add or move the entry under the correct status heading
(Active / Settled / Archived). Format: `- [<title>](<slug>.md) — promoted YYYY-MM-DD`

**`<subwiki>/index.md`** — add a Research Threads section if absent; list the anchor page.

**Root `log.md`:**
```
## [YYYY-MM-DD] promote | <anchor page title>
Mode: create | update. Conclusions: N (N new). Open questions: N. Concepts promoted: N.
```
