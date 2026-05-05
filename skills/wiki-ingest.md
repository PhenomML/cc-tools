Ingest a source into the research wiki: $ARGUMENTS

`$ARGUMENTS` is one of:
- An arXiv ID (e.g. `2301.07608`)
- A public URL (e.g. `https://en.wikipedia.org/wiki/Ilya_Sutskever`)
- A path inside `raw/` (e.g. `raw/author-year-slug.pdf`)
- Any filesystem path to a PDF, Office doc, or HTML file (e.g. `~/Books/textbook.pdf`)

If working directory is not the wiki root, navigate there first.

## Step 1 — Acquire the source

**If arXiv ID:** fetch metadata first — this gives the title, authors, year, PDF URL,
and whether an HTML version exists:
```bash
cc-arxiv <id>
```
If the abstract answers your question, metadata alone may be sufficient — you have the
title, authors, year, and PDF URL for a citation without fetching further. Fetch the
full text when you need specific claims, methodology, or data not visible in the abstract.

If HTML is available (reported in the output), fetch it directly into raw/ as markdown:
```bash
cc-webfetch https://arxiv.org/html/<id> > raw/<author>-<year>-<slug>.md
```
If HTML is not available, download the PDF using the URL from cc-arxiv output and convert:
```bash
curl -L <pdf-url> -o raw/<author>-<year>-<slug>.pdf
cc-markitdown raw/<author>-<year>-<slug>.pdf > raw/<author>-<year>-<slug>.md
```

**If a public URL:** fetch once and save to `raw/` with a descriptive slug:
```bash
cc-webfetch <url> > raw/<slug>.md
```
Choose a slug that identifies the source: `wikipedia-sutskever.md`, `ssi-inc-homepage.md`, `patel-sutskever-2023-interview.md`.

**If a filesystem path:** convert once and save into `raw/` using the source filename's
basename:
```bash
cc-markitdown /path/to/source.pdf > raw/<basename>.md
```
The source file stays where it is; only the converted markdown lands in `raw/`.

In all cases the saved `.md` file in `raw/` is the working copy for all subsequent
steps — do not re-run the conversion.

**After saving any arXiv file, verify the title.** Read the first 10 lines of the saved
file and confirm the title matches the intended paper. A fetch can silently return the
wrong paper (bad redirect, ID collision, cached error page) — a mismatch caught here
prevents wrong content from propagating into the wiki.

## Step 2 — Read and discuss

**Read the raw file directly** — do not rely on brief summaries, frontmatter, or
session notes. Brief-level descriptions can be stale or wrong; the raw file is the
ground truth. This catches wrong-content fetches (e.g. an arXiv file saved under the
right slug but containing a different paper) before bad content propagates into the wiki.

Read the full converted text from the saved `.md` file. Briefly summarise the paper's
contribution and ask the researcher to confirm emphasis or redirect focus before writing
anything.

**Note cited works that would fill wiki gaps.** While reading, flag any cited paper,
book, or source that addresses a known gap in the wiki or is referenced in existing
concept pages without a corresponding source page. Offer to add candidates to `queue.md`
using the standard entry format (title, authors, target sub-wiki, why it matters, source
of discovery). Do not add automatically — confirm with the researcher first.

**When promoting from a brief:** apply the editorial test at item granularity, not
brief granularity. Ask for each concept or result: does this generalize beyond the
specific subject of the brief? Biographical detail, company-specific strategy, and
subject-specific career context belong in the brief. Frameworks, methods, and findings
that inform the broader research domain belong in the wiki. A brief will typically
yield a mix of promotable and non-promotable content — do not treat the brief as a
unit.

**Large files:** the Read tool enforces a 256KB limit. If a file in `raw/` exceeds
this, use `offset` and `limit` to read it in sections — read the first 200 lines to
assess structure, then target the sections relevant to your sub-wikis.

## Step 3 — Determine scope (multi-wiki routing)

Read the top-level `CLAUDE.md` to learn each sub-wiki's scope. Identify every sub-wiki
this source informs — a single paper may belong in several. State which sub-wikis you
will write into and why; confirm with the researcher before proceeding.

## Step 4 — Write into each relevant sub-wiki

For **each** sub-wiki identified in Step 3:

**4a. Source summary page** → `<wiki>/papers/<author>-<year>-<slug>.md`

YAML frontmatter:
```yaml
title: "<quoted title>"
type: paper          # allowed: paper | essay | manifesto | concept | method | project | comparison | synthesis
wikis: [list]
sources: [../../raw/filename.md]   # always ../../raw/ — pages sit two levels from root
related: []
created: <today>
updated: <today>
confidence: high     # high = primary source read directly; medium = secondhand/abstract only; low = inferred
```

**Before writing any pages, verify one `sources:` path resolves** by checking the file
exists — path errors are silent at write time and propagate to every page in the session.

Content: citation, research question, methods, key results, limitations.
Use `$...$` LaTeX for all math. In the Sources section, link to `raw/` files
using relative markdown links — not code spans — since pages are two levels
from the wiki root: `[raw/file.md](../../raw/file.md)`.

**Non-peer-reviewed sources:** credible researcher essays and manifestos (position
papers, research program articulations, practitioner-authored arguments) are promotable
when they capture the *why* behind a research direction in a way technical papers don't.
Use `type: essay` or `type: manifesto` rather than `paper`. Apply the same confidence
rubric: `high` if the full text was read directly, `medium` if only excerpts or
summaries were used.

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

If this source was listed in `queue.md`, note that it should be removed now that it has
been ingested. Do not remove it automatically — confirm with the researcher, as they may
want to keep the entry for reference or update it to point to the wiki page created.
