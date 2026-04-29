Health-check the research wiki. $ARGUMENTS (optional: limit to one sub-wiki, e.g. `tsa`)

If working directory is not the wiki root, navigate there first.
Scope: all sub-wikis unless $ARGUMENTS names one specifically.

Work through each check and report findings before making any changes.
Ask the researcher which fixes to apply.

## Checks

**Orphaned pages** — pages with no inbound links from any index.md or other wiki page.
List them; most should be linked or deleted.

**Broken cross-wiki links** — relative links to `../../<other-wiki>/...` that point to
files that do not exist. List with source page and target path.

**Orphaned raw files** — files in `raw/` not referenced by any `sources:` field in any
page. Run `grep -r "sources:" . --include="*.md" | grep -o "raw/[^'\" )]*"` to collect
all cited raw slugs, then compare against `ls raw/`. List uncited files; they were
fetched but never wired up and should either be sourced or deleted.

**Raw path depth** — pages where `sources:` paths don't match the file's depth in the
tree. Concept pages sit two levels from the root (`<wiki>/concepts/<page>.md`) and must
use `../../raw/`; syntheses sit one level from the root (`syntheses/<page>.md`) and must
use `../raw/`. Flag any page where the `sources:` prefix contradicts its depth. These
mismatches are silent at write time — the link looks valid but resolves to the wrong
location.

**Missing concept pages** — concepts mentioned by name across wiki pages but lacking
their own page in `concepts/`. Count mentions across all `.md` files and report in two
tiers:
- **High priority** (≥ 5 mentions): gaps that actively fragment the wiki; create these
  before the next ingest session.
- **Suggestions** (2–4 mentions): worth creating eventually; note but do not block on
  them.

**Stale claims** — pages whose content may be contradicted or superseded by more recently
ingested sources (check log.md dates vs page `updated` frontmatter). Flag pages that
pre-date recent ingests and cover the same topics.

**Papers missing from sub-wikis** — source summary pages in one sub-wiki whose content
clearly informs another sub-wiki that has no corresponding page for it. Suggest additions.

**index.md gaps** — pages that exist in the filesystem but are absent from the sub-wiki's
`index.md`. List them.

**Math notation** — flag two classes of issue, both for `/math-review`:
- Bare Unicode Greek letters or Unicode subscript digits used as math notation outside `$...$`
- Inline `$...$` expressions containing `_` (subscript) where content follows the subscript before the closing `$`, or multiple such expressions on the same line — GitHub italic conflict risk (see AUTHORING.md)

## After reporting

Append to `log.md`:
```
## [<YYYY-MM-DD>] lint | <scope>
Orphans: <n>. Broken links: <n>. Orphaned raw: <n>. Path-depth errors: <n>. Missing concepts (high/suggest): <n>/<n>. Stale pages: <n>.
Actions taken: <summary or "none — awaiting researcher direction">.
```
