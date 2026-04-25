Ingest a source into the research wiki: $ARGUMENTS

`$ARGUMENTS` is one of:
- An arXiv ID (e.g. `2301.07608`)
- A path inside `raw/` (e.g. `raw/kalman-1960.pdf`)
- Any filesystem path to a PDF, Office doc, or HTML file (e.g. `~/Books/textbook.pdf`)

If working directory is not the wiki root, navigate there first.

## Step 1 — Acquire the source

**If arXiv ID:** fetch metadata first — this gives the title, authors, year, PDF URL,
and whether an HTML version exists:
```bash
cc-arxiv <id>
```
If HTML is available (reported in the output), fetch it directly into raw/ as markdown:
```bash
cc-webfetch https://arxiv.org/html/<id> > raw/<author>-<year>-<slug>.md
```
If HTML is not available, download the PDF using the URL from cc-arxiv output and convert:
```bash
curl -L <pdf-url> -o raw/<author>-<year>-<slug>.pdf
cc-markitdown raw/<author>-<year>-<slug>.pdf > raw/<author>-<year>-<slug>.md
```

**If a filesystem path:** convert once and save into `raw/` using the source filename's
basename:
```bash
cc-markitdown /path/to/source.pdf > raw/<basename>.md
```
The source file stays where it is; only the converted markdown lands in `raw/`.

In all cases the saved `.md` file in `raw/` is the working copy for all subsequent
steps — do not re-run the conversion.

## Step 2 — Read and discuss

Read the full converted text from the saved `.md` file. Briefly summarise the paper's contribution and ask the
researcher to confirm emphasis or redirect focus before writing anything.

## Step 3 — Determine scope (multi-wiki routing)

Read the top-level `CLAUDE.md` to learn each sub-wiki's scope. Identify every sub-wiki
this source informs — a single paper may belong in several. State which sub-wikis you
will write into and why; confirm with the researcher before proceeding.

## Step 4 — Write into each relevant sub-wiki

For **each** sub-wiki identified in Step 3:

**4a. Source summary page** → `<wiki>/papers/<author>-<year>-<slug>.md`
YAML frontmatter: `title, type: paper, wikis: [list], sources: [raw path],
related: [], created: <today>, updated: <today>, confidence: high`
Content: citation, research question, methods, key results, limitations.
Use `$...$` LaTeX for all math.

**4b. Concept and method pages** — update or create pages in `<wiki>/concepts/` and
`<wiki>/methods/` touched by this source. Add a citation back to the paper page.
For concepts that appear in multiple sub-wikis, add a cross-wiki link:
`../../<other-wiki>/concepts/<page>.md`

**4c. Update `<wiki>/index.md`** — add the new paper page and any new concept/method
pages under the appropriate category headings.

## Step 5 — Update root log

Append to `log.md`:
```
## [<YYYY-MM-DD>] ingest | <Author> (<Year>) — <Title>
Sub-wikis: <list>. Pages written: <count>. Key concepts updated: <list>.
```

## Step 6 — Report

List every file created or modified, grouped by sub-wiki. Note any cross-wiki links
created. Flag any concepts that warrant their own page but don't have one yet.
