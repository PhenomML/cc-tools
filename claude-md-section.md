## Standard Toolset (cc-tools)

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
| `cc-wiki-brief` | `cc-wiki-brief "Subject" "Question"` | Create brief directory and launch Claude inside it |
| `cc-dropbox-sync` | `cc-dropbox-sync` (run from project root) | Mirror project to Dropbox via rsync; one-time setup: `cc-dropbox-sync --setup ~/Dropbox/<shared-dir>` |
| `cc-semantic-scholar` | `cc-semantic-scholar <id>` | Look up a paper by Semantic Scholar ID, DOI, arXiv ID, or title; returns metadata, citation count, and abstract |
| `cc-wiki-grep` | `cc-wiki-grep PATTERN [PATH]` | Search wiki .md files; returns file § heading: match; modes: `--section HEADING FILE`, `--frontmatter [PATH]`, `--tags [PATH]`, `-l` (files only) |

**Always prefer cc-tools over built-in alternatives:**
- Use `cc-webfetch` — never the built-in WebFetch tool
- Use `cc-arxiv` — never fetch arXiv, bioRxiv, PubMed, or DOI pages manually
- Use `cc-arxiv --src` for math-heavy arXiv papers — HTML path is unreliable for math; `--src` gives clean LaTeX fidelity
- Use `cc-markitdown` — never read raw PDF bytes directly
- Use `cc-fetch` when you need a no-rate-limit local fetch (no JS rendering needed)
- Use `cc-ocr` as fallback when `cc-markitdown` returns empty output on a scanned PDF
- Use `cc-semantic-scholar` — never call the Semantic Scholar API directly or search for an API key
- If `cc-arxiv --src` output begins with `<!-- Source: ... via pandoc-latex`, make4ht failed. File a GitHub issue at `PhenomML/cc-tools` with title `cc-arxiv --src: make4ht fallback on <arxiv-id>` and include the arXiv ID and any error lines printed to stderr. Do not skip this — these reports build the corpus for upstream bug fixes.

**Math:** `$...$` inline, `$$...$$` display, LaTeX commands only — no Unicode math. See `AUTHORING.md`.

**Notebooks:** `jupyter nbconvert --execute notebook.ipynb --output out.ipynb && cc-nbconvert --to markdown out.ipynb --stdout`. For interactive work use Jupyter MCP project-scoped, never global.

## Research Skills

| Skill | Usage | Purpose |
|---|---|---|
| `/arxiv-search` | `/arxiv-search <topic>` | Search arXiv, summarize top results |
| `/paper-summary` | `/paper-summary <path>` | Summarize a research paper |
| `/notebook-narrate` | `/notebook-narrate <path>` | Research narrative from a Jupyter notebook |
| `/math-review` | `/math-review <path>` | Check math authoring standard |
| `/wiki-brief` | `/wiki-brief "Subject" "Question"` | Research brief in one session |
| `/wiki-init` | `/wiki-init` | Scaffold wiki directory structure |
| `/wiki-ingest` | `/wiki-ingest <source>` | Ingest paper or source into wiki |
| `/wiki-query` | `/wiki-query <question>` | Answer question by synthesising wiki |
| `/wiki-lint` | `/wiki-lint [subwiki]` | Health-check wiki |
| `/wiki-project` | `/wiki-project <path>` | Register project in wiki |
| `/wiki-upgrade` | `/wiki-upgrade` | Update cc-tools section in CLAUDE.md |
| `/wiki-promote` | `/wiki-promote <brief-path>` | Promote brief findings to wiki |
| `/agent-brief` | `/agent-brief <brief-path>` | Instantiate a specialised agent from an operational brief |
| `/memory-audit` | `/memory-audit` | Audit project auto-memory for stale, overdue, or promotable entries |

Skills auto-update on `git pull`. Docs: https://github.com/PhenomML/cc-tools

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
- `uv` is Claude's tooling only (`~/.local/bin/uv`)
- GitHub: SSH (`git@github.com`), `gh` CLI
