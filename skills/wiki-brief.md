Create a research brief for a subject: $ARGUMENTS

`$ARGUMENTS` is the subject name, optionally followed by a driving question:
- `/wiki-brief "Ilya Sutskever"` — brief only
- `/wiki-brief "Ilya Sutskever" "Why would a Stanford signal processing mathematician interest a superintelligence researcher?"` — brief with purpose

Run from the parent directory where the brief should be created
(e.g., `~/Research/People/` for a person brief).

## Step 1 — Parse arguments and determine subject type

Extract the subject name from `$ARGUMENTS`. If a driving question follows, capture it.

Infer the subject type from the name and any available context:

| Type | Examples |
|---|---|
| Person | researcher, executive, collaborator, public figure |
| Company / organization | company, lab, institute, NGO |
| Conference / event | NeurIPS 2025, a specific workshop |
| Topic / debate | AI consciousness, the replication crisis |
| Policy / legislation | EU AI Act, a specific regulation |

**Batch mode:** if a driving question was provided and the subject type is unambiguous
from the name alone, proceed without stopping to confirm — asking "is Cycorp a company?"
is friction the researcher does not need. Only pause to confirm if the request is vague
or the type is genuinely unclear.

## Step 2 — Determine sub-wiki dimensions

The defaults below are starting points, not constraints. Add dimensions freely when the
subject warrants it — for a technology company, a `technology/` sub-wiki may be as
essential as `products/`. Err on the side of more dimensions; they are cheap to create
and expensive to retrofit.

| Type | Default directories |
|---|---|
| Person | `biography/`, `research/`, `views/`, `ventures/` |
| Company | `history/`, `products/`, `strategy/`, `team/` |
| Conference | `program/`, `speakers/`, `themes/`, `papers/` |
| Topic | `positions/`, `evidence/`, `key-figures/`, `history/` |
| Policy | `text/`, `sponsors/`, `arguments/`, `status/` |

A person without public ventures gets `biography/`, `research/`, `views/` only. A
technology company may need `technology/` alongside `products/`. Use judgment; the
driving question is often the best guide to which dimensions matter most.

If operating in batch mode (driving question provided, type unambiguous), proceed with
your chosen dimensions. Otherwise confirm the final list with the researcher.

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
- `<dir>/index.md` — include a minimal example link so the format is unambiguous:
```markdown
# <dir> Index

<!-- Claude maintains this file. -->

## Concepts

- [page-name.md](concepts/page-name.md) — one-line description
```

Also create at the brief root if not already present:
- `raw/` directory
- `.gitignore` containing `raw/`
- `index.md` with a brief heading and sub-wiki list (do not add the syntheses entry yet
  — write it after the synthesis exists, in Step 7)
- `log.md` with the standard header

Skip any file or directory that already exists without overwriting.

## Step 5 — Initial fetch

Search for and fetch the most informative public sources for the subject. Every source
must be saved to `raw/` before reading — do not use transient fetch results.

**Typical sources by type:**

**Person:** Wikipedia page, personal/lab/company site, one or two significant interviews
or talks (transcripts preferred over video links), recent news if relevant.

**Company:** Wikipedia page, company website and About page, recent press coverage,
any published research blog.

**Topic / Policy:** Wikipedia overview, primary sources (the actual text if policy),
key advocacy or opposition documents, recent news.

**Seek independent and critical perspectives.** For company and technology subjects,
the company controls most public information and will present itself favorably. Actively
search for critical analyses, post-mortems, competitor assessments, or independent
reviews — they are often the most valuable sources and materially change the synthesis.

Concrete search strategies when the subject lacks obvious adversarial coverage:
- Check Wikipedia's external links and "Criticism" sections — they often surface named
  critics and negative analyses directly
- Query `cc-webfetch` on searches like "[subject] criticism", "[subject] failure",
  "[subject] post-mortem", "[subject] problems"
- For technology claims: look for independent replication attempts or benchmarks that
  tested the subject's stated capabilities
- For people or organizations with academic output: check who has cited them critically
  in Google Scholar or arXiv comments

**arXiv sources:** use `cc-arxiv <id>` to fetch metadata. If the abstract answers your
question, metadata alone may be sufficient — the abstract, authors, year, and PDF URL
are all you need for a citation. Fetch the full text (HTML preferred; PDF via
`cc-markitdown` as fallback) only when you need specific claims, methodology, or data
not visible in the abstract.

**Large fetched files:** the Read tool enforces a 256KB limit. Files larger than this
(long essays, Wikipedia pages for major topics) will be refused. Use `offset` and
`limit` parameters to read relevant sections: read the first 200 lines to assess
structure, then target the sections that matter. Save the full file to `raw/` regardless
— you can always re-read specific sections later.

Save each source with a descriptive slug:
```bash
cc-webfetch <url> > raw/<slug>.md
```

## Step 6 — Write initial concept pages

For each sub-wiki, write at least one concept page synthesizing the relevant fetched
sources. Follow /wiki-ingest conventions:
- Frontmatter with `sources:` pointing to `../../raw/` files (two levels up from
  `<subwiki>/concepts/`)
- `confidence: high | medium | low` reflecting source quality
- `related:` cross-linking to pages in sibling sub-wikis where connections exist —
  cross-wiki paths from `<subwiki>/concepts/` are always `../../<other>/concepts/<page>.md`

In a person brief, the biography sub-wiki's career-timeline page plays the same role
a survey paper plays in a domain wiki — it is the anchor that cross-links everything else.

In the Sources section of every page, link to `raw/` files using relative markdown
links — not code spans. Pages are two levels from the wiki root, so the path is always
`../../raw/<filename>`. Example:
```markdown
## Sources

- Wikipedia, "Ilya Sutskever" (accessed 2026-04-26) — [raw/wikipedia-sutskever.md](../../raw/wikipedia-sutskever.md)
```

Update each sub-wiki's `index.md` with links to the pages just written.

## Step 7 — Answer the driving question

If a driving question was provided in `$ARGUMENTS`, synthesize an answer now by reading
across the concept pages just written. File the result as `syntheses/<slug>.md` with
appropriate frontmatter (`type: synthesis`).

Note: synthesis pages are one level from the wiki root, so `raw/` links use `../raw/`
and cross-wiki links use `../<subwiki>/concepts/<page>.md`.

This is the deliverable the brief was built for. Make it specific and citable.

After writing the synthesis, update the root `index.md` to add the syntheses entry,
and append to root `log.md`. Updating these after the synthesis exists avoids broken
links if the session is interrupted before the synthesis is complete.

## Step 8 — Report

List every file and directory created, grouped by sub-wiki. If a synthesis was written,
report its path and a one-sentence summary of the answer. Note any sub-wikis that
warrant further ingestion before the next session.
