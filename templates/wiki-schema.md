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
    research/           ← research-thread anchor pages, one per promoted brief
    index.md            ← catalog for this sub-wiki (Claude maintains)
  syntheses/            ← cross-wiki analysis pages filed from /wiki-query
```

## Page conventions

**Frontmatter** (required on every page):
```yaml
---
title: "<descriptive title>"
type: paper | concept | method | project | comparison | synthesis | research-thread
wikis: [list of sub-wikis this page belongs to]
sources: [relative paths to raw/ files that support this page]
related: [relative paths to related pages, including cross-wiki links]
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
---
```

**Additional fields for `research-thread` pages** (add after `confidence:`):
```yaml
brief_path: ../Topics/compressed-sensing   # relative from wiki root (not from this file's directory)
status: active                             # active | settled | archived
```

**Naming:** kebab-case filenames. Paper pages: `<firstauthor>-<year>-<slug>.md`.
Concept pages: descriptive noun phrase, e.g. `gradient-descent.md`, `transformer-architecture.md`.

**Line wrapping:** do not hard-wrap prose paragraphs. Each paragraph is one line in the source; the renderer handles wrapping. Code blocks and tables are exempt.

**Diagrams:** use Mermaid fenced code blocks (`\`\`\`mermaid`) for all flow diagrams, sequences, and architecture sketches. ASCII art is a fallback only; SVG/PNG are not used in wiki documents.

**Cross-wiki links:** use relative paths from the current file.
Example from `tsa/concepts/state-space.md` to `bayes/concepts/gaussian-update.md`:
`../../bayes/concepts/gaussian-update.md`

**Source references in body content:** use relative markdown links to `raw/` files,
not code spans. Pages in `<subwiki>/concepts/`, `<subwiki>/papers/`, etc. are two
levels from the wiki root, so the relative path to `raw/` is always `../../raw/`.
Example Sources section:
```markdown
## Sources

- Author (Year), "Title" — [raw/author-year-slug.md](../../raw/author-year-slug.md)
- Wikipedia, "Topic" (accessed YYYY-MM-DD) — [raw/wikipedia-topic.md](../../raw/wikipedia-topic.md)
```

**Math:** always use `$...$` for inline math and `$$...$$` for display math with LaTeX
commands inside. Never use bare Unicode Greek letters or Unicode subscript digits in math.
See cc-tools `AUTHORING.md` for the full standard.

**Imputed connections:** when a page draws an inference or connection not present in its source material — a cross-domain analogy, a synthesis across briefs, an editorial interpretation — mark it inline with `*[Imputed]*` immediately after the claim. This signals to readers and future Claude instances that the claim is plausible synthesis, not evidenced fact. Example: *"The phase transition diagram is CS's version of the Common Task Framework leaderboard. \*[Imputed\]*"* Do not use `*[Imputed]*` for claims that are directly supported by a cited source.

**Citation years:** use the arXiv posting year for papers with significant arXiv presence; use the journal publication year otherwise. On first mention of a paper that has both, add a parenthetical to disambiguate: "(arXiv 2011)" or "(*Annals of Statistics*, 2013)". Within a wiki, citation years must be consistent with the brief's existing paper-entry filenames — e.g., a file named `donoho-johnstone-montanari-2011-amp-minimax.md` fixes the citation year as 2011 for that paper throughout the wiki.

## Ingestion workflow

**All sources must be saved to `raw/` before use.** This applies regardless of source type — every piece of evidence the wiki cites must have a corresponding file in `raw/` so provenance is traceable and the `sources:` frontmatter field is populated.

| Source type | Acquire | Save to raw/ |
|---|---|---|
| arXiv paper (HTML) | `cc-webfetch https://arxiv.org/html/<id>` | `raw/<author>-<year>-<slug>.md` |
| arXiv paper (PDF fallback) | `curl -L <pdf-url>` then `cc-markitdown` | PDF → `raw/pdf/<author>-<year>-<slug>.pdf`; markdown → `raw/<author>-<year>-<slug>.md` |
| bioRxiv / medRxiv paper | `cc-arxiv 10.1101/<id>` then `curl -L <pdf-url>` + `cc-markitdown` | PDF → `raw/pdf/<author>-<year>-<slug>.pdf`; markdown → `raw/<author>-<year>-<slug>.md` |
| Published paper (PubMed / CrossRef DOI) | `cc-arxiv <pmid-or-doi>`; open-access: `cc-webfetch <pdf-url>` or `curl` + `cc-markitdown`; paywalled: queue.md | `raw/<author>-<year>-<slug>.md` (or abstract-only with `confidence: medium`) |
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

## Promotion workflow

Use `/wiki-promote path/to/brief/` to crystallise settled knowledge from an active research
brief into the wiki. Promotion is not archival — a brief stays active as long as research
continues; its settled conclusions accrete into the wiki incrementally across multiple runs.

The skill detects CREATE vs UPDATE mode automatically: if no anchor page exists for the
brief it creates one; if one exists it updates it with newly settled conclusions, newly
answered questions, and newly promoted concepts. Run it again after each significant brief
session.

Anchor pages live in `<subwiki>/research/<slug>.md` with `type: research-thread`. The
`brief_path` field links back to the brief directory; the brief's `index.md` carries a
`## Wiki Anchor` section linking forward to the anchor page.

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
- **Authors:** <Authors> (<arXiv ID, bioRxiv DOI, or URL>)
- **Target:** <sub-wiki(s)>
- **Why:** one sentence on what gap this fills

## Paywalled Papers

### <Title>
- **Authors:** <Authors> (<Journal>, <Year>)
- **URL:** <full publisher URL — https://doi.org/<doi> or https://pubmed.ncbi.nlm.nih.gov/<pmid>/>
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

**Research wiki operations:** `ingest`, `query`, `lint`, `project`, `upgrade`, `promote`.

**Experiment wiki operations:** `experiment`, `commission`, `synthesis`, `review`, `decision`, `query`.

Experiment wikis should define their operation vocabulary in their `CLAUDE.md` — the list above is a starting point, not a constraint. A worked example is more useful than a label list; see `templates/experiment-wiki-CLAUDE.md` for concrete entries covering each operation type.

## Tools available

Claude has access to the following cc-tools commands for wiki operations:
- `cc-markitdown <file>` — convert PDF, Office, or HTML file on disk to markdown
- `cc-webfetch <url>` — fetch any public URL as clean markdown (500 req/day); redirect to save: `cc-webfetch <url> > file.md`
- `cc-arxiv <id>` — fetch paper metadata (title, authors, year, PDF URL, abstract); auto-routes: arXiv ID → arXiv, `10.1101/` → bioRxiv/medRxiv, integer → PubMed, any DOI → CrossRef
- `cc-pdfplumber <file>` — extract tables from PDFs
- `/wiki-init`, `/wiki-ingest`, `/wiki-query`, `/wiki-lint`, `/wiki-project`, `/wiki-upgrade`, `/wiki-promote` — wiki skills
