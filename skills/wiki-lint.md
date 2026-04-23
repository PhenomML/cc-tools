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

**Missing concept pages** — concepts mentioned by name in multiple papers or methods
pages but lacking their own page in `concepts/`. List the top candidates.

**Stale claims** — pages whose content may be contradicted or superseded by more recently
ingested sources (check log.md dates vs page `updated` frontmatter). Flag pages that
pre-date recent ingests and cover the same topics.

**Papers missing from sub-wikis** — source summary pages in one sub-wiki whose content
clearly informs another sub-wiki that has no corresponding page for it. Suggest additions.

**index.md gaps** — pages that exist in the filesystem but are absent from the sub-wiki's
`index.md`. List them.

**Math notation** — pages containing bare Unicode Greek letters or Unicode subscript
digits used as math notation outside `$...$`. Flag for `/math-review`.

## After reporting

Append to `log.md`:
```
## [<YYYY-MM-DD>] lint | <scope>
Orphans: <n>. Broken links: <n>. Missing concepts: <n>. Stale pages: <n>.
Actions taken: <summary or "none — awaiting researcher direction">.
```
