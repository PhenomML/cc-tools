Create a research brief for a subject: $ARGUMENTS

`$ARGUMENTS` is the subject name, optionally followed by a driving question:
- `/wiki-brief "Ilya Sutskever"` — brief only
- `/wiki-brief "Ilya Sutskever" "Why would a Stanford signal processing mathematician interest a superintelligence researcher?"` — brief with purpose

Run from the parent directory where the brief should be created
(e.g., `~/Research/People/` for a person brief).

## Step 1 — Parse arguments and confirm subject type

Extract the subject name from `$ARGUMENTS`. If a driving question follows, capture it.

Infer the subject type from the name and any available context, then confirm with the
researcher before proceeding:

| Type | Examples |
|---|---|
| Person | researcher, executive, collaborator, public figure |
| Company / organization | company, lab, institute, NGO |
| Conference / event | NeurIPS 2025, a specific workshop |
| Topic / debate | AI consciousness, the replication crisis |
| Policy / legislation | EU AI Act, a specific regulation |

## Step 2 — Determine sub-wiki dimensions

Select sub-wiki dimensions based on type. These are the orthogonal aspects of the
subject that warrant separate coverage:

| Type | Default directories |
|---|---|
| Person | `biography/`, `research/`, `views/`, `ventures/` |
| Company | `history/`, `products/`, `strategy/`, `team/` |
| Conference | `program/`, `speakers/`, `themes/`, `papers/` |
| Topic | `positions/`, `evidence/`, `key-figures/`, `history/` |
| Policy | `text/`, `sponsors/`, `arguments/`, `status/` |

Adjust for the specific subject — a person without public ventures gets
`biography/`, `research/`, `views/` only. Confirm the final list with the researcher.

## Step 3 — Create directory and write CLAUDE.md

Create `<subject-slug>/` in the current directory if it does not exist.
Use kebab-case for the directory name: "Ilya Sutskever" → `ilya-sutskever/`.

Write `<subject-slug>/CLAUDE.md` with three sections in order:

**Section 1 — Title and Purpose:**
```markdown
# <Subject Name> Brief

## Purpose

**Subject:** <Subject Name> (<type>)
**Created:** <YYYY-MM-DD>
**Occasion:** <infer from the driving question context, or leave blank>
**Question:** <driving question verbatim, or "—" if none provided>
```

**Section 2 — Sub-wikis table** (user-owned; never overwritten by /wiki-upgrade):
```markdown
## Sub-wikis

| Directory | Scope | Related |
|---|---|---|
| `biography/` | Career history, education, key events | `research/`, `ventures/` |
| `research/` | Technical contributions, papers, research directions | `biography/`, `views/` |
...
```

Write specific, concrete scope descriptions. Related should be symmetric.

**Section 3 — Managed section:** insert the full current content of
`~/Projects/PhenomML/cc-tools/templates/wiki-schema.md` wrapped in sentinels:
```
<!-- cc-tools:wiki:begin -->
[wiki-schema.md content]
<!-- cc-tools:wiki:end -->
```

## Step 4 — Scaffold directories

For each sub-wiki, create if not already present:
- `<dir>/` directory
- `<dir>/concepts/` directory
- `<dir>/index.md`:
```markdown
# <dir> Index

<!-- Claude maintains this file. -->

## Concepts
```

Also create at the brief root if not already present:
- `raw/` directory
- `.gitignore` containing `raw/`
- `index.md` with a brief heading and sub-wiki list
- `log.md` with the standard header

Skip any file or directory that already exists without overwriting.

## Step 5 — Initial fetch

Search for and fetch the most informative public sources for the subject. Every source
must be saved to `raw/` before reading — do not use transient fetch results.

Typical sources by type:

**Person:** Wikipedia page, personal/lab/company site, one or two significant interviews
or talks (transcripts preferred over video links), recent news if relevant.

**Company:** Wikipedia page, company website and About page, recent press coverage,
any published research blog.

**Topic / Policy:** Wikipedia overview, primary sources (the actual text if policy),
key advocacy or opposition documents, recent news.

Save each source with a descriptive slug:
```bash
cc-webfetch <url> > raw/<slug>.md
```
Read from the saved file for all subsequent steps.

## Step 6 — Write initial concept pages

For each sub-wiki, write at least one concept page synthesizing the relevant fetched
sources. Follow /wiki-ingest conventions:
- Frontmatter with `sources:` pointing to `raw/` files
- `confidence: high | medium | low` reflecting source quality
- `related:` cross-linking to pages in sibling sub-wikis where connections exist

In a person brief, the biography sub-wiki's career-timeline page plays the same role
a survey paper plays in a domain wiki — it is the anchor that cross-links everything else.

In the Sources section of every page, link to `raw/` files using relative markdown
links — not code spans. Pages are two levels from the wiki root, so the path is always
`../../raw/<filename>`. Example:
```markdown
## Sources

- Wikipedia, "Ilya Sutskever" (accessed 2026-04-26) — [raw/wikipedia-sutskever.md](../../raw/wikipedia-sutskever.md)
```

Update each sub-wiki's `index.md` and append to root `log.md`.

## Step 7 — Answer the driving question

If a driving question was provided in `$ARGUMENTS`, synthesize an answer now by reading
across the concept pages just written. File the result as `syntheses/<slug>.md` with
appropriate frontmatter (`type: synthesis`).

This is the deliverable the brief was built for. Make it specific and citable.

## Step 8 — Report

List every file and directory created, grouped by sub-wiki. If a synthesis was written,
report its path and a one-sentence summary of the answer. Note any sub-wikis that
warrant further ingestion before the next session.
