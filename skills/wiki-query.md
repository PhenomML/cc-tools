Answer a research question against the wiki: $ARGUMENTS

If working directory is not the wiki root, navigate there first.

## Step 1 — Plan the search

Read the top-level `index.md` to identify which sub-wikis and which pages are
likely relevant to `$ARGUMENTS`. State your plan before reading anything.

## Step 2 — Read relevant pages

Read the identified pages across all relevant sub-wikis. Follow cross-wiki links
where they add context. Read `log.md` tail to understand what has been ingested
recently — it may affect the answer.

## Step 3 — Synthesise

Write a clear answer with inline citations to wiki pages (relative markdown links).
Use `$...$` LaTeX for math. Structure the answer appropriately for the question:
prose summary, comparison table, derivation, or a list of open questions — whatever
fits best.

## Step 4 — File valuable answers back

If the answer is substantive — a synthesis, comparison, or analysis that took real
work — offer to save it as a new wiki page. Appropriate types:
- `<wiki>/comparisons/<slug>.md` for compare/contrast answers
- `<wiki>/concepts/<slug>.md` if the answer defines or clarifies a concept
- Root `syntheses/<slug>.md` for cross-wiki answers that span multiple sub-wikis

If saved, update the relevant `index.md` and append to `log.md`:
```
## [<YYYY-MM-DD>] query | <short question summary>
Answer filed as: <path>.
```
