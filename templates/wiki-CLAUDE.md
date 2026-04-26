# Research Wiki

This is a personal LLM-maintained research wiki. Claude writes and maintains all content;
the researcher curates sources and directs analysis.

## Sub-wikis

<!-- List each sub-wiki, its scope, and related sub-wikis.

Sub-wikis are not limited to research domains. They can represent any orthogonal
dimension of a subject: for a person wiki, sub-wikis might be biography, research,
ai-safety, and ventures; for a company wiki, history, products, strategy, and team.
Use whatever decomposition makes sense for your subject.

The Scope column should be specific enough that an agent can decide unambiguously
whether a source belongs in this sub-wiki. Prefer concrete topic lists over broad labels.

The Related column lists other sub-wikis in this table whose concepts frequently
overlap with this one. The agent uses it when writing concept and method pages: if a
concept in tsa/ is deeply connected to Bayesian inference, knowing that bayes/ is
related tells the agent to check bayes/concepts/ for an existing page to link to, or
to create a cross-wiki link there. List only sub-wikis defined in this table.
Relationships should be symmetric: if A lists B, B should list A.

Example: -->

| Directory | Scope | Related |
|---|---|---|
| `tsa/` | Time series analysis, forecasting, state space models, ARIMA, spectral methods | `bayes/` |
| `bayes/` | Bayesian inference, MCMC, hierarchical models, prior elicitation | `tsa/` |

<!-- Add rows as new sub-wikis are created. -->

<!-- cc-tools:wiki:begin -->
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
<!-- cc-tools:wiki:end -->
