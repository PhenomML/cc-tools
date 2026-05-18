# cc-tools

An AI agent doing real research work needs to read research — and reading research means ingesting PDFs without garbling the math, extracting tables without losing column structure, fetching papers from arXiv, and converting executed notebooks into readable records. These are not exotic requirements. They are the minimum for an agent doing useful work in a research project, and they have to be installed somewhere before the agent can call them.

cc-tools is that somewhere. It packages the essential ingestion stack into an isolated environment managed by `uv`, completely separate from your research project dependencies. You install it once per machine; after that, Claude manages it and uses it from any project, without touching your Conda environments.

cc-tools also ships the wiki skills that implement [Karpathy's LLM wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — where the agent reads a paper, writes a structured summary, updates the concept pages it touches, and maintains a cross-linked index across sessions. The knowledge accumulates because it is written down, not held in chat history. A lighter brief variant builds a subject-oriented wiki in a single session for a meeting or time-sensitive question — a person, company, topic, or policy assembled from public sources around a driving question.

## Articles

The design choices behind cc-tools are explained in three pieces:

| Article | Description |
|---|---|
| [Help Your AI Read Research — and Remember It](articles/help-your-ai-read-research.md) | The ingestion stack, math notation standard, research skills, and the permanence pattern that underlies the wiki |
| [The Multi-Subject Personal Research Wiki](articles/multi-subject-personal-research-wiki.md) | Why one wiki is not enough, the multi-sub-wiki architecture, and the skills that maintain it |
| [The Research Brief](articles/the-research-brief.md) | A subject-oriented wiki assembled in one session for a meeting or time-sensitive question — person, company, topic, or policy |
| [Jupyter and the MCP Trade-off](articles/jupyter-and-the-mcp-tradeoff.md) | When static notebook conversion is sufficient and when the Jupyter MCP is worth its token cost |

## Companion

[cc-code-tools](https://github.com/PhenomML/cc-code-tools) — extends cc-tools for researchers working scientific codebases. Adds `/wiki-codebase` with paper ingestion and paper–code correspondence tracking.

## Installation

**Prerequisites:** Install `uv` (Claude's package manager — distinct from conda):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then restart your shell (or run `source ~/.zshrc`) so that `~/.local/bin` is on your PATH.

**Install:**

```bash
git clone git@github.com:PhenomML/cc-tools.git ~/cc-tools   # or any path you prefer
cd ~/cc-tools
bash setup-claude.sh
```

The clone location can be anywhere — skills and templates reference it via `$CC_TOOLS`, which `setup-claude.sh` writes at install time. `setup-claude.sh` does the following (safe to re-run after updates):

- Installs the cc-tools Python package into an isolated `uv` environment (`~/.local/share/uv/tools/cc-tools/`) — completely separate from Conda, no interaction
- Writes `CC_TOOLS=<install-path>` to `~/.config/cc-tools/env.sh` and adds a one-line source to `~/.zshrc` / `~/.bashrc` so skills can resolve template paths at runtime
- Adds the cc-tools section to `~/.claude/CLAUDE.md` (creating it if needed), replacing it on re-run
- Symlinks every skill from `skills/` into `~/.claude/commands/` so Claude Code can invoke them as slash commands, refreshing symlinks on re-run

## Keeping it up to date

When Claude adds new tools or skills to this repository, pull and re-run setup:

```bash
cd $CC_TOOLS && git pull && bash setup-claude.sh
```

To set up a new project directory with the standard cc-tools allowlist (so Claude doesn't prompt for `cc-arxiv`, `curl`, `mkdir`, etc.):

```bash
bash $CC_TOOLS/setup-claude.sh --project ~/Research/Topics/new-topic
```

If the directory doesn't exist yet it will be created. Safe to re-run — merges missing entries without removing existing ones.

Claude will tell you when this is needed.

After pulling, **start a new Claude session** before invoking updated skills. Claude Code caches skill file content within a session — a running instance will not pick up changes to skill files mid-session. A fresh session reads all skills from scratch. If a new session is not practical, you can tell Claude explicitly: "Re-read `~/.claude/commands/<skill-name>.md` before proceeding."

## What's included

| Command | Source | Purpose |
|---|---|---|
| `cc-markitdown` | [microsoft/markitdown](https://github.com/microsoft/markitdown) | Convert PDFs, Office docs, and HTML files on disk to Markdown |
| `cc-webfetch` | [markdown.new](https://markdown.new) | Fetch any public URL as clean Markdown; detects Cloudflare blocks and falls back to Jina (r.jina.ai) then Wayback Machine automatically. 500 req/day free. |
| `cc-fetch` | cc-tools (built-in) | Fetch a URL as clean Markdown via local Readability extraction (trafilatura). No rate limit; no JS rendering. First attempt for simple static pages; fall back to `cc-webfetch` for JS-heavy or blocked sites. |
| `cc-md2pdf` | cc-tools (built-in) | Convert Markdown to PDF via pandoc + XeLaTeX |
| `cc-nbconvert` | [jupyter/nbconvert](https://github.com/jupyter/nbconvert) | Convert Jupyter notebooks to Markdown and other formats |
| `cc-pdfplumber` | [jsvine/pdfplumber](https://github.com/jsvine/pdfplumber) | Extract tables and text from PDFs with precise layout information |
| `cc-arxiv` | [lukasschwab/arxiv.py](https://github.com/lukasschwab/arxiv.py) + built-in | Fetch paper metadata by ID; auto-routes: arXiv ID → arXiv, `10.1101/` DOI → bioRxiv/medRxiv, integer → PubMed (eUtils), any other DOI → CrossRef. Outputs title, authors, year, PDF URL, abstract. |
| `cc-ocr` | cc-tools (built-in) | OCR a scanned PDF (no text layer) using pdftoppm + tesseract; fallback for historic papers that `cc-markitdown` cannot extract |
| `cc-wiki-brief` | cc-tools (built-in) | Scaffold a research brief directory and launch Claude inside it, scoping memory and settings to that subject. Auto-detects People vs. Companies; supports `--person`, `--company`, `--topic`, `--dir`. |

More tools will be added here as the standard Claude instantiation grows.

### System prerequisites

Several cc-tools commands depend on system binaries not managed by uv. Install once per machine.

**pandoc** — required by `cc-arxiv --src` (HTML → Markdown conversion) and `cc-md2pdf`:

```bash
brew install pandoc
```

**TeX Live** — required by `cc-arxiv --src` (LaTeX → HTML via make4ht) and `cc-md2pdf` (PDF typesetting via XeLaTeX). Install **one** of the following (MacTeX and BasicTeX conflict):

```bash
brew install --cask mactex      # full TeX distribution (~4 GB), recommended
# or
brew install --cask basictex    # minimal TeX (~100 MB); then:
# sudo tlmgr update --self && sudo tlmgr install collection-fontsrecommended make4ht
```

MacTeX includes `make4ht`, `pdflatex`, `xelatex`, and `lualatex`. BasicTeX requires installing `make4ht` explicitly via `tlmgr`.

If MacTeX is already installed (common for researchers writing LaTeX), only `brew install pandoc` is needed.

**Without TeX Live:** `cc-arxiv` (metadata only), `cc-markitdown`, `cc-webfetch`, `cc-fetch`, `cc-pdfplumber`, `cc-semantic-scholar`, and all wiki skills work without TeX. Only `cc-arxiv --src` and `cc-md2pdf` require it. [cc-code-tools](https://github.com/PhenomML/cc-code-tools) is fully functional without TeX for codebase work; paper ingestion falls back to PDF conversion.

### cc-md2pdf prerequisites

`cc-md2pdf` requires pandoc and TeX Live — see [System prerequisites](#system-prerequisites) above.

### cc-markitdown audio support

`cc-markitdown` can convert audio files (podcasts, recorded interviews) to text when ffmpeg is installed:

```bash
brew install ffmpeg
```

Without ffmpeg, PDF, Office, and HTML conversion still work; only audio input is unavailable. `setup-claude.sh` will warn if ffmpeg is missing.

### cc-ocr: scanned PDF support

Historic papers (pre-2000) are often scanned bitmap images with no text layer. `cc-markitdown` and `cc-pdfplumber` produce empty or binary output for these files. Use `cc-ocr` instead:

```bash
cc-ocr input.pdf > output.md
```

Requires two Homebrew packages:

```bash
brew install poppler    # provides pdftoppm
brew install tesseract  # OCR engine
```

`cc-ocr` converts each page to a 300 dpi JPEG with `pdftoppm`, runs `tesseract`, and concatenates the results. Output is plain text with a one-line header noting it was OCR'd. If `cc-markitdown` detects a text layer, `cc-ocr` will warn and suggest using `cc-markitdown` instead — but will proceed.

**macOS note:** `tesseract` fails with a sandboxing error when image files are in `/tmp`. `cc-ocr` uses a temp directory under `$HOME` to avoid this.

**Authoring standard:** use `$...$` LaTeX math for all mathematical expressions. This renders correctly as typeset math in both the PDF output and in Obsidian (which uses MathJax with the same syntax). See [AUTHORING.md](AUTHORING.md) for the full guide, including a table of common LaTeX commands and a compatibility matrix.

### cc-wiki-brief: brief launcher

`cc-wiki-brief` creates the brief directory and launches Claude from inside it, so memory and accumulated permissions are scoped to that subject rather than the parent `People/` or `Companies/` directory.

```bash
cc-wiki-brief "David Donoho" "How well has Frictionless Reproducibility been adopted?"
cc-wiki-brief "Databricks" --company "Is Databricks winning the data lakehouse war?"
cc-wiki-brief "CRISPR" --topic
cc-wiki-brief "Jane Smith" --dir ~/Research/Advisors
```

Subject type is inferred automatically (multi-word title-cased names without corporate keywords → People; everything else → Companies). Override with `--person`, `--company`, `--topic`, or `--dir`.

**Embedding a wiki inside a code repo:** use `--brief-dir` to target an existing directory as the brief root directly, with no slug appended. This is the right pattern when a wiki lives inside a code repo (e.g. `myrepo/wiki/`):

```bash
cc-wiki-brief "My Experiment" "driving question" --brief-dir ~/Projects/myrepo/wiki
```

`cc-wiki-brief` will automatically copy `templates/repo-CLAUDE.md` to the repo root (`../CLAUDE.md`) if none exists there yet — fill in the placeholders before launching the brief Claude. The standard cc-tools allowlist is installed into `wiki/.claude/settings.local.json`.

**Instantiating a role-defined agent:** use `--agent` to point at an operational brief written by a theory Claude. This seeds `/agent-brief` instead of `/wiki-brief`, replacing the need for a carefully crafted driving question:

```bash
cc-wiki-brief "iSATx Experiment Manager" \
  --agent ~/Research/Topics/transformers/syntheses/isatx-experiment-manager-brief.md \
  --brief-dir ~/Projects/iSATx-Toy-System-Experiment/wiki
```

The agent reads the operational brief, reads `../CLAUDE.md` for repo context, writes an orientation synthesis as a confirmation gate, and waits for your approval before starting any work.

### /agent-brief: role instantiation from an operational brief

`/agent-brief` is the skill for the dual-agent research-to-code pattern: a theory Claude writes an operational brief defining the agent's role, phase targets, constraints, and log format; `/agent-brief` instantiates a second Claude from that brief. The orientation synthesis it writes is the confirmation gate — the agent does nothing until the researcher approves it.

The multi-agent file convention (`syntheses/<topic>-<agent-slug>.md`, `## Questions for <Agent>` sections) is documented in the skill and lets two Claude instances collaborate through a shared `syntheses/` directory with the researcher as relay.

## Unsupported tools

The following tools ship in this repository but are **not supported** — no bug reports or feature requests. Use at your own risk.

| Command | Purpose |
|---|---|
| `cc-dropbox-sync` | Sync research files via Dropbox for collaborators not using GitHub |

## MCP Servers

MCP servers add their tool schemas to every session context whether or not they are used — typically 1,000–4,000 tokens per server. For a token-light toolset, **no MCP servers are registered globally by `setup-claude.sh`.**

Instead, activate MCP servers **project-scoped** when a specific project needs them. Add a `.mcp.json` at the project root (not committed if it contains tokens):

```json
{
  "mcpServers": {
    "jupyter": {
      "command": "uvx",
      "args": ["jupyter-mcp-server@latest"],
      "env": {
        "JUPYTER_URL": "http://localhost:8888",
        "JUPYTER_TOKEN": "${JUPYTER_TOKEN}",
        "ALLOW_IMG_OUTPUT": "true"
      }
    }
  }
}
```

The `mcp/` directory in this repo contains reference configs for available servers.

### Jupyter and notebooks

For most notebook work the shell execution pattern is sufficient and costs no MCP tokens:

```bash
jupyter nbconvert --to notebook --execute notebook.ipynb --output executed.ipynb
cc-nbconvert --to markdown executed.ipynb --stdout
```

Use the Jupyter MCP only for genuinely interactive work — writing new cells, testing hypotheses iteratively — where two-way access is required. Activate it via `.mcp.json` in that project, not globally.
