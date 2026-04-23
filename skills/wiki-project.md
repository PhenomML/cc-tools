Add or update a project page in the research wiki: $ARGUMENTS

`$ARGUMENTS` is the local path to the project repo (e.g. `../TSAnalysis-S26`).
If working directory is not the wiki root, navigate there first.

## Step 1 — Read the project

Read the project's `CLAUDE.md` and `README.md` (if present). Identify:
- What the project is and its research goal
- Which papers and concepts from the wiki inform it
- The GitHub remote URL (`git -C $ARGUMENTS remote get-url origin`)

## Step 2 — Determine which sub-wikis should host a project page

A project may be relevant to multiple sub-wikis. State which ones and confirm
with the researcher.

## Step 3 — Write the project page

For each relevant sub-wiki, write or update `<wiki>/projects/<project-slug>.md`:

```yaml
---
title: <Project Name>
type: project
path: <relative filesystem path from wiki root to project repo>
github: <GitHub URL>
wikis: [list of sub-wikis]
related_papers: []
related_concepts: []
created: <today>
updated: <today>
---
```

Content:
- One-paragraph description of the project's research goal
- **Key papers** — links to source summary pages in this wiki that inform the project
- **Key concepts** — links to concept pages this project applies or tests
- **Open questions** — what the project is trying to resolve; update as the project evolves
- **GitHub:** `<URL>` (prominent link)
- **Local path:** `<relative path>` (so Claude can navigate there directly)

## Step 4 — Update index and log

Add the project page to `<wiki>/index.md` under a Projects section.
Append to `log.md`:
```
## [<YYYY-MM-DD>] project | <Project Name>
Sub-wikis: <list>. Path: <relative path>. GitHub: <URL>.
```
