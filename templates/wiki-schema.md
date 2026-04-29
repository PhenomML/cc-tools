## Structure

```
wiki/                   ← repo root (this file lives here)
  .gitignore            ← excludes raw/
  CLAUDE.md             ← this file
  index.md              ← cross-wiki catalog (Claude maintains)
  log.md                ← chronological record of all operations (Claude maintains)
  queue.md              ← candidate books and papers for future ingestion (Claude maintains)
  raw/                  ← source documents — local only, never committed
  <subwiki>/            ← one directory per research domain (see Sub-wikis above)
    CLAUDE.md           ← scope definition for this sub-wiki
    papers/             ← source summary pages, one per ingested paper
    concepts/           ← concept reference pages
    methods/            ← methodological reference pages
    projects/           ← pages for related code projects
    index.md            ← catalog for this sub-wiki (Claude maintains)
  syntheses/            ← cross-wiki analysis pages filed from /wiki-query
```

## Page conventions

**Frontmatter** (required on every page):
```yaml
---
title: "<descriptive title>"
type: paper | concept | method | project | comparison | synthesis
wikis: [list of sub-wikis this page belongs to]
sources: [relative paths to raw/ files that support this page]
related: [relative paths to related pages, including cross-wiki links]
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
---
```

**Naming:** kebab-case filenames. Paper pages: `<firstauthor>-<year>-<slug>.md`.
Concept pages: descriptive noun phrase, e.g. `kalman-filter.md`, `state-space-models.md`.

**Cross-wiki links:** use relative paths from the current file.
Example from `tsa/concepts/state-space.md` to `bayes/concepts/gaussian-update.md`:
`../../bayes/concepts/gaussian-update.md`

**Source references in body content:** use relative markdown links to `raw/` files,
not code spans. Pages in `<subwiki>/concepts/`, `<subwiki>/papers/`, etc. are two
levels from the wiki root, so the relative path to `raw/` is always `../../raw/`.
Example Sources section:
```markdown
## Sources

- Wikipedia, "Kalman Filter" (accessed 2026-04-26) — [raw/wikipedia-kalman.md](../../raw/wikipedia-kalman.md)
- Kalman (1960) — [raw/kalman-1960.md](../../raw/kalman-1960.md)
```

**Math:** always use `$...$` for inline math and `$$...$$` for display math with LaTeX
commands inside. Never use bare Unicode Greek letters or Unicode subscript digits in math.
See cc-tools `AUTHORING.md` for the full standard.

## Ingestion workflow

**All sources must be saved to `raw/` before use.** This applies regardless of source type — every piece of evidence the wiki cites must have a corresponding file in `raw/` so provenance is traceable and the `sources:` frontmatter field is populated.

| Source type | Acquire | Save to raw/ |
|---|---|---|
| arXiv paper | `cc-arxiv <id>` for metadata; fetch HTML or PDF | `raw/<author>-<year>-<slug>.md` or `.pdf` |
| Web page (Wikipedia, blog, company page) | `cc-webfetch <url>` | `raw/<slug>.md` |
| Local PDF or document | — | already in raw/ or copy there first |
| Podcast / interview transcript | `cc-webfetch <transcript-url>` | `raw/<speaker>-<year>-<slug>.md` |

Use `/wiki-ingest <source>` for the full workflow. Claude will:
1. Acquire and save the source to `raw/` (see table above)
2. Determine which sub-wikis the source informs
3. Write source summary pages into each relevant sub-wiki
4. Update concept/method pages with cross-links
5. Update the relevant `index.md` files and root `log.md`

A source spanning multiple subfields is written into all relevant sub-wikis.

## Query workflow

Use `/wiki-query <question>`. Claude reads `index.md`, drills into relevant pages across
sub-wikis, synthesises an answer with citations, and offers to file valuable answers
as new pages in `syntheses/`.

## Maintenance

Use `/wiki-lint` periodically. Claude checks for orphaned pages, broken cross-wiki links,
missing concept pages, stale claims, math notation violations, and stale queue entries
(works listed in `queue.md` that are already present in a sub-wiki index).

**queue.md** tracks candidate sources for future ingestion. Entry format:

```markdown
## Books

### <Title>
- **Authors:** <Authors> (<Publisher>, <Year>)
- **Target:** <sub-wiki(s)>
- **Why:** one sentence on what gap this fills
- **Source:** where this candidate was discovered

## Dissertations

### <Title>
- **Author:** <Author> (<Institution>, <Year>)
- **Target:** <sub-wiki(s)>
- **Why:** one sentence on what gap this fills
- **Source:** where this candidate was discovered
- **Access:** open | institutional login | ILL request | embargoed until <date>

## Preprints

### <Title>
- **Authors:** <Authors> (<arXiv ID or URL>)
- **Target:** <sub-wiki(s)>
- **Why:** one sentence on what gap this fills

## Paywalled Papers

### <Title>
- **Authors:** <Authors> (<Journal>, <Year>)
- **Target:** <sub-wiki(s)>
- **Why:** one sentence on what gap this fills
- **Access:** institutional login / cc-credentialed-fetch / ILL request
```

Claude adds entries when a cited work would fill a wiki gap (discovered during ingest)
and removes entries when a work is ingested.

## Projects

Project pages live in `<subwiki>/projects/`. Each page records:
- A relative filesystem path to the local project repo
- The GitHub URL
- Links to the papers and concepts that inform the project

Use `/wiki-project <path-to-project>` to create or update a project page.

## Log format

Each entry in `log.md` follows this prefix for greppability:
```
## [YYYY-MM-DD] <operation> | <title or description>
```
Operations: `ingest`, `query`, `lint`, `project`, `upgrade`.

## Tools available

Claude has access to the following cc-tools commands for wiki operations:
- `cc-markitdown <file>` — convert PDF, Office, or HTML file on disk to markdown
- `cc-webfetch <url>` — fetch any public URL as clean markdown (500 req/day); redirect to save: `cc-webfetch <url> > file.md`
- `cc-arxiv <arxiv-id>` — fetch paper metadata: title, authors, year, PDF URL, HTML availability, abstract
- `cc-pdfplumber <file>` — extract tables from PDFs
- `/wiki-init`, `/wiki-ingest`, `/wiki-query`, `/wiki-lint`, `/wiki-project`, `/wiki-upgrade` — wiki skills
