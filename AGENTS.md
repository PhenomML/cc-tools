# cc-tools — Codex guidance

This is the Codex-readable counterpart to `~/.claude/CLAUDE.md`. Same toolset,
same conventions — rendered as prose instead of Claude slash-commands, because
Codex has no `$ARGUMENTS` substitution and no per-command `.md` file convention.

**Canonical source:** `claude-md-section.md` in `PhenomML/cc-tools`. If this file
and `claude-md-section.md` ever disagree, `claude-md-section.md` is correct —
this file is hand-maintained and can drift. Report drift as a GitHub issue.

**Scope note:** this file supports one working Codex user, not a general
multi-provider abstraction. It intentionally does not build a plugin system,
an installer flag, or a parallel Agent-Skills directory tree. See the
"Growing this file" section at the bottom before adding structure.

## Standard Toolset (cc-tools)

These are plain Python entry points installed via `uv tool install --reinstall
--force .` from the `PhenomML/cc-tools` repo. They work identically regardless
of which agent invokes them.

| Command | Usage | Purpose |
|---|---|---|
| `cc-markitdown` | `cc-markitdown <file>` | Convert PDFs, Office docs, HTML → Markdown |
| `cc-fetch` | `cc-fetch <url>` | Fetch URL as Markdown via local extraction; no rate limit; no JS |
| `cc-webfetch` | `cc-webfetch <url>` | Fetch URL as Markdown; auto-fallback if blocked (Jina → Wayback); 500 req/day |
| `cc-arxiv` | `cc-arxiv <id>` | Fetch paper metadata; auto-routes by ID: arXiv ID, bioRxiv/medRxiv DOI (`10.1101/`), PubMed PMID (integer), or any DOI via CrossRef |
| `cc-arxiv --src` | `cc-arxiv --src <arxiv-id>` | Fetch arXiv TeX source tarball, convert to Markdown via make4ht+pandoc; high math fidelity; outputs to stdout; arXiv IDs only |
| `cc-md2pdf` | `cc-md2pdf file.md` | Convert Markdown → PDF via pandoc + XeLaTeX |
| `cc-nbconvert` | `cc-nbconvert --to markdown notebook.ipynb` | Convert Jupyter notebook → Markdown |
| `cc-pdfplumber` | `cc-pdfplumber <file.pdf>` | Extract tables and text from PDFs |
| `cc-ocr` | `cc-ocr <file.pdf>` | OCR scanned PDFs (no text layer); fallback when cc-markitdown returns nothing |
| `cc-wiki-brief` | `cc-wiki-brief "Subject" "Question"` | Create a brief directory (does not launch Claude when run under Codex — see Research Workflows below) |
| `cc-dropbox-sync` | `cc-dropbox-sync` (run from project root) | Mirror project to Dropbox via rsync; one-time setup: `cc-dropbox-sync --setup ~/Dropbox/<shared-dir>` |
| `cc-semantic-scholar` | `cc-semantic-scholar <id>` | Look up a paper by Semantic Scholar ID, DOI, arXiv ID, or title; returns metadata, citation count, and abstract |
| `cc-wiki-grep` | `cc-wiki-grep PATTERN [PATH]` | Search wiki .md files; returns file § heading: match; modes: `--section HEADING FILE`, `--frontmatter [PATH]`, `--tags [PATH]`, `-l` (files only) |

**Always prefer cc-tools over built-in alternatives:**
- Use `cc-webfetch` — never fetch a URL by any other built-in means
- Use `cc-arxiv` — never fetch arXiv, bioRxiv, PubMed, or DOI pages manually
- Use `cc-arxiv --src` for math-heavy arXiv papers — HTML is unreliable for math; `--src` gives clean LaTeX fidelity
- Use `cc-markitdown` — never read raw PDF bytes directly
- Use `cc-fetch` when you need a no-rate-limit local fetch (no JS rendering needed)
- Use `cc-ocr` as fallback when `cc-markitdown` returns empty output on a scanned PDF
- Use `cc-semantic-scholar` — never call the Semantic Scholar API directly or search for an API key
- If `cc-arxiv --src` output begins with `<!-- Source: ... via pandoc-latex`, make4ht failed. File a GitHub issue at `PhenomML/cc-tools` with title `cc-arxiv --src: make4ht fallback on <arxiv-id>` and include the arXiv ID and any error lines printed to stderr.

**Math:** `$...$` inline, `$$...$$` display, LaTeX commands only — no Unicode math. See `AUTHORING.md`.

**Notebooks:** `jupyter nbconvert --execute notebook.ipynb --output out.ipynb && cc-nbconvert --to markdown out.ipynb --stdout`.

## Wiki convention: read CLAUDE.md when present

Research wikis and project repos in this ecosystem carry a `CLAUDE.md` at
their root describing that specific wiki's sub-wiki structure, page
conventions, and local rules. That file is shared project content, not an
agent-specific config — it predates Codex support and stays `CLAUDE.md` by
name regardless of which agent is reading it.

**If you are working inside a directory that has a `CLAUDE.md` and no local
`AGENTS.md`, read `CLAUDE.md` first and treat it as this project's operating
instructions.** This is the single rule that lets existing wikis work under
Codex without every wiki template needing a duplicate `AGENTS.md`.

## Research Workflows

These are Claude's `/skill-name` slash commands, described here as plain
procedures. Follow them as written — there is no separate Codex skill object
to invoke; the instructions below are the whole recipe.

**Starting a new research brief.** Run `cc-wiki-brief "Subject" "driving
question"` to scaffold the brief directory (auto-detects People/Companies/
Topics, or pass `--company`/`--topic`/`--dir` explicitly). Then open a Codex
session with that directory as the working root — each brief should be its
own session, anchored at the brief root, so its context stays isolated from
other briefs. If you're doing this manually instead: `mkdir -p
~/Research/<category>/<slug>` and start Codex there.

**Initializing a wiki's directory structure.** From the wiki root (the
directory containing `CLAUDE.md`), read the Sub-wikis table in `CLAUDE.md`
and create, for each sub-wiki that doesn't already exist: `<dir>/`,
`<dir>/papers/`, `<dir>/concepts/`, `<dir>/methods/`, and an `index.md`.
Safe to re-run — skip anything that already exists.

**Ingesting a source into the wiki** (paper, essay, URL, or local file).
See `AUTHORING.md` and the acquisition rules in `claude-md-section.md`
above for which `cc-*` command to use per source type. After fetching:
read the raw file directly (not a summary) and confirm the title matches
before using it as a source — fetches can silently return a compilation
stub or the wrong paper. Determine which sub-wiki(s) the source informs,
write a paper summary page with YAML frontmatter (`title`, `type`,
`wikis`, `sources`, `confidence`, `fetch_provenance`), update or create
touched concept/method pages, update each relevant sub-wiki's `index.md`,
and append an entry to `log.md`.

**Answering a question from the wiki.** Read the top-level `index.md` to
plan which sub-wikis and pages are relevant. Read those pages (and follow
cross-wiki links). Check the tail of `log.md` for recent changes that might
affect the answer. Write a cited answer using relative markdown links to
wiki pages. If the answer took real synthesis work, offer to save it as a
new page under `comparisons/`, `concepts/`, or root `syntheses/`.

**Health-checking a wiki.** Walk each sub-wiki (or one named sub-wiki) and
check for structural problems — broken links, missing frontmatter, stale
`index.md` entries, pages not reachable from any index. Report findings
before making any changes; apply fixes only after confirmation.

**Registering a project in the wiki.** Given a project repo path, read its
`CLAUDE.md` and `README.md`, then write or update a project page in the
wiki summarizing purpose, key files, and current state.

**Promoting a brief into the wiki.** Given a brief directory path, read
its `syntheses/` and working notes, identify conclusions that are settled
(not just in-progress), and write them into the appropriate wiki pages.
A brief stays active as long as research continues — repeat this
periodically, not once.

**Searching arXiv / summarizing a paper / narrating a notebook / reviewing
math formatting** — these are single-shot tasks with no multi-step state.
Use the matching `cc-*` command to fetch or convert, then do the requested
task directly: search-and-summarize, summarize, narrate, or check against
the math convention in `AUTHORING.md`.

## Claude-only for now

These are not available under Codex because they depend on Claude Code's
in-app project memory (`~/.claude/projects/.../memory`) or its Agent /
subagent dispatch tool, and porting either is out of scope until a second
Codex user creates real demand:

- **Memory audit** — reads Claude's per-project memory files; no Codex
  equivalent state store exists yet.
- **Agent-brief** — instantiates a specialized subagent via Claude's Agent
  tool from an operational brief document; Codex's subagent model differs
  enough that this needs its own design, not a mechanical port.
- **wiki-upgrade's CLAUDE.md sentinel-block rewrite** — updates the
  managed cc-tools section of a wiki's `CLAUDE.md`. Do this manually under
  Codex for now: diff the wiki's managed block against the current
  `templates/wiki-schema.md` and reconcile by hand.

## Epistemic Conventions

**`*[Imputed]*`** — use inline after any statement in session output that is not grounded in an enumerated wiki claim with a supporting quotation.

Two forms:

**Unlinked** — no known grounding claim exists:
```
A sub-quadratic approximation may be viable. *[Imputed]*
```

**Linked** — a specific enumerated claim would ground this statement if it existed:
```
This generalizes to the noisy case. *[Imputed — [[donoho-2023-claims#DON23-004]]]*
```

A linked imputed statement is a work order: it names the enumeration gap precisely so it can be tracked and filled. High `*[Imputed]*` density in session output signals the session wandered off-wiki. Low density signals it stayed grounded. The human uses density as an attention filter — do not force dense sessions to be read with the same scrutiny as grounded ones.

This convention is active in all sessions, not just promotion sessions.

## Environment

- Research deps: **Conda** — never uv for researcher projects
- `uv` is agent tooling only (`~/.local/bin/uv`)
- GitHub: SSH (`git@github.com`), `gh` CLI

## Growing this file

This file is deliberately hand-maintained and scoped to what one Codex user
needs. Before adding automation (installer flags, sentinel-block rewriting,
a `.codex-plugin` manifest, a formal Agent-Skills directory tree), confirm
there's a second Codex user whose friction this would actually resolve —
otherwise it's speculative infrastructure for a population of one. See
`PhenomML/cc-tools` issue #61 for the fuller multi-provider proposal this
file deliberately does *not* implement yet.
