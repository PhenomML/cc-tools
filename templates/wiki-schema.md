## Structure

```
wiki/                   ← repo root (this file lives here)
  .gitignore            ← excludes raw/
  CLAUDE.md             ← this file
  index.md              ← cross-wiki catalog (Claude maintains)
  log.md                ← chronological record of all operations (Claude maintains)
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
title: <descriptive title>
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

**Math:** always use `$...$` for inline math and `$$...$$` for display math with LaTeX
commands inside. Never use bare Unicode Greek letters or Unicode subscript digits in math.
See cc-tools `AUTHORING.md` for the full standard.

## Ingestion workflow

Use `/wiki-ingest <raw/filename or arXiv ID>`. Claude will:
1. Run `cc-arxiv <id>` to fetch metadata and check HTML availability (arXiv sources)
2. Fetch HTML via `cc-webfetch` if available, otherwise download PDF and run `cc-markitdown`
3. Determine which sub-wikis the source informs
4. Write source summary pages into each relevant sub-wiki
5. Update concept/method pages with cross-links
6. Update the relevant `index.md` files and root `log.md`

A paper spanning multiple subfields is written into all relevant sub-wikis.

## Query workflow

Use `/wiki-query <question>`. Claude reads `index.md`, drills into relevant pages across
sub-wikis, synthesises an answer with citations, and offers to file valuable answers
as new pages in `syntheses/`.

## Maintenance

Use `/wiki-lint` periodically. Claude checks for orphaned pages, broken cross-wiki links,
missing concept pages, stale claims, and math notation violations.

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
- `/wiki-ingest`, `/wiki-query`, `/wiki-lint`, `/wiki-project`, `/wiki-upgrade` — wiki skills
