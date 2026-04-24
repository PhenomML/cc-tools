# cc-tools

This repository is **Claude's toolset**, not a research library. It has nothing to do with your Conda environment or project dependencies. You install it once per machine so that the Claude Code (CC) assistant running in any of your projects has access to a consistent, versioned set of tools regardless of which project you are in.

## Articles

Background reading on the patterns cc-tools supports:

| Article | Description |
|---|---|
| [Help Your AI Read Research — and Remember It](articles/help-your-ai-read-research.md) | The ingestion stack, math notation standard, research skills, and the permanence pattern that underlies the wiki |
| [The Multi-Subject Personal Research Wiki](articles/multi-subject-personal-research-wiki.md) | Why one wiki is not enough, the multi-sub-wiki architecture, and the skills that maintain it |
| [Jupyter and the MCP Trade-off](articles/jupyter-and-the-mcp-tradeoff.md) | When static notebook conversion is sufficient and when the Jupyter MCP is worth its token cost |

## Why you need to do this

Claude Code runs as an AI agent that can invoke shell commands. Several of the tools it uses — document conversion, markdown extraction, and others added over time — are Python programs that must be installed before Claude can call them. This repository pins those tools to known-good versions and installs them into an isolated environment managed by `uv`, completely separate from your Conda setup.

**You install this once. After that, Claude manages it.**

## Prerequisites

Install `uv` (Claude's package manager — distinct from conda):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then restart your shell (or run `source ~/.zshrc`) so that `~/.local/bin` is on your PATH.

## Installation

```bash
git clone git@github.com:PhenomML/cc-tools.git ~/Projects/PhenomML/cc-tools
uv tool install --editable ~/Projects/PhenomML/cc-tools
bash ~/Projects/PhenomML/cc-tools/setup-claude.sh
```

The first two commands install the tools. The third adds the cc-tools section to `~/.claude/CLAUDE.md` (creating it if needed), so every Claude Code session on this machine automatically knows what tools are available. Safe to run again after updates — it replaces the managed section in place without touching anything else in the file.

## Keeping it up to date

When Claude adds new tools to this repository, pull, reinstall, and refresh CLAUDE.md:

```bash
cd ~/Projects/PhenomML/cc-tools
git pull
uv tool upgrade cc-tools
bash setup-claude.sh
```

Claude will tell you when this is needed.

## What's included

| Command | Source | Purpose |
|---|---|---|
| `cc-markitdown` | [microsoft/markitdown](https://github.com/microsoft/markitdown) | Convert PDFs, Office docs, and HTML files to Markdown |
| `cc-webfetch` | [markdown.new](https://markdown.new) | Fetch any public URL as clean Markdown (500 req/day free) |
| `cc-md2pdf` | cc-tools (built-in) | Convert Markdown to PDF via pandoc + XeLaTeX |
| `cc-nbconvert` | [jupyter/nbconvert](https://github.com/jupyter/nbconvert) | Convert Jupyter notebooks to Markdown and other formats |
| `cc-pdfplumber` | [jsvine/pdfplumber](https://github.com/jsvine/pdfplumber) | Extract tables and text from PDFs with precise layout information |
| `arxiv` (library) | [lukasschwab/arxiv.py](https://github.com/lukasschwab/arxiv.py) | Fetch paper metadata and PDF links from arXiv — used programmatically by Claude |

More tools will be added here as the standard Claude instantiation grows.

### cc-md2pdf prerequisites

`cc-md2pdf` requires system packages not managed by uv. Install once per machine:

```bash
brew install pandoc
```

For the LaTeX engine, install **one** of the following (MacTeX and BasicTeX conflict — if you have one, skip the other):

```bash
brew install --cask mactex      # full TeX distribution (~4 GB), recommended
# or
brew install --cask basictex    # minimal TeX (~100 MB); then:
# sudo tlmgr update --self && sudo tlmgr install collection-fontsrecommended
```

If MacTeX is already installed, only `brew install pandoc` is needed.

**Authoring standard:** use `$...$` LaTeX math for all mathematical expressions. This renders correctly as typeset math in both the PDF output and in Obsidian (which uses MathJax with the same syntax). See [AUTHORING.md](AUTHORING.md) for the full guide, including a table of common LaTeX commands and a compatibility matrix.

## MCP Servers

MCP servers add their tool schemas to every session context whether or not they are
used — typically 1,000–4,000 tokens per server. For a token-light toolset, **no MCP
servers are registered globally by `setup-claude.sh`.**

Instead, activate MCP servers **project-scoped** when a specific project needs them.
Add a `.mcp.json` at the project root (not committed if it contains tokens):

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

Use the Jupyter MCP only for genuinely interactive work — writing new cells, testing
hypotheses iteratively — where two-way access is required. Activate it via `.mcp.json`
in that project, not globally.

## Research Skills

`setup-claude.sh` also installs slash-command skills into `~/.claude/commands/` as symlinks to this repo. They are available in any Claude Code session:

| Skill | Purpose |
|---|---|
| `/arxiv-search <topic>` | Search arXiv and summarize top results |
| `/paper-summary <path>` | Extract and summarize a research paper PDF |
| `/notebook-narrate <path>` | Write a research narrative from a Jupyter notebook |
| `/math-review <path>` | Check .md files against the `$...$` authoring standard |

Skills update automatically when you `git pull` — no need to re-run `setup-claude.sh` for skill content changes. Re-run it only when new skills are added to the repo.

## Your Conda environments are unaffected

`uv tool` installs into `~/.local/share/uv/tools/cc-tools/` — a completely separate location from any Conda environment. It does not touch your `base` environment or any project environment. The two systems do not interact.
