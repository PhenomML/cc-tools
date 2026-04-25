# cc-tools

An AI agent doing real research work needs to read research — and reading research means ingesting PDFs without garbling the math, extracting tables without losing column structure, fetching papers from arXiv, and converting executed notebooks into readable records. These are not exotic requirements. They are the minimum for an agent doing useful work in a research project, and they have to be installed somewhere before the agent can call them.

cc-tools is that somewhere. It packages the essential ingestion stack into an isolated environment managed by `uv`, completely separate from your research project dependencies. You install it once per machine; after that, Claude manages it and uses it from any project, without touching your Conda environments.

cc-tools also ships the wiki skills that implement [Karpathy's LLM wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — where the agent reads a paper, writes a structured summary, updates the concept pages it touches, and maintains a cross-linked index across sessions. The knowledge accumulates because it is written down, not held in chat history.

## Articles

The design choices behind cc-tools are explained in three pieces:

| Article | Description |
|---|---|
| [Help Your AI Read Research — and Remember It](articles/help-your-ai-read-research.md) | The ingestion stack, math notation standard, research skills, and the permanence pattern that underlies the wiki |
| [The Multi-Subject Personal Research Wiki](articles/multi-subject-personal-research-wiki.md) | Why one wiki is not enough, the multi-sub-wiki architecture, and the skills that maintain it |
| [Jupyter and the MCP Trade-off](articles/jupyter-and-the-mcp-tradeoff.md) | When static notebook conversion is sufficient and when the Jupyter MCP is worth its token cost |

## Installation

**Prerequisites:** Install `uv` (Claude's package manager — distinct from conda):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then restart your shell (or run `source ~/.zshrc`) so that `~/.local/bin` is on your PATH.

**Install:**

```bash
git clone git@github.com:PhenomML/cc-tools.git ~/Projects/PhenomML/cc-tools
uv tool install --editable ~/Projects/PhenomML/cc-tools
bash ~/Projects/PhenomML/cc-tools/setup-claude.sh
```

The first two commands install the tools into an isolated `uv` environment — completely separate from your Conda setup, no interaction between them. `uv tool` installs into `~/.local/share/uv/tools/cc-tools/`, which does not touch your `base` environment or any project environment. The third command adds the cc-tools section to `~/.claude/CLAUDE.md` (creating it if needed), so every Claude Code session on this machine automatically knows what tools are available and how to use them. Safe to run again after updates — it replaces the managed section in place without touching anything else in the file.

## Keeping it up to date

When Claude adds new tools to this repository, pull, reinstall, and refresh CLAUDE.md:

```bash
cd ~/Projects/PhenomML/cc-tools
git pull
uv tool upgrade cc-tools
bash setup-claude.sh
```

Claude will tell you when this is needed.

After pulling, **start a new Claude session** before invoking updated skills. Claude Code caches skill file content within a session — a running instance will not pick up changes to skill files mid-session. A fresh session reads all skills from scratch. If a new session is not practical, you can tell Claude explicitly: "Re-read `~/.claude/commands/<skill-name>.md` before proceeding."

## What's included

| Command | Source | Purpose |
|---|---|---|
| `cc-markitdown` | [microsoft/markitdown](https://github.com/microsoft/markitdown) | Convert PDFs, Office docs, and HTML files on disk to Markdown |
| `cc-webfetch` | [markdown.new](https://markdown.new) | Fetch any public URL as clean Markdown to stdout (500 req/day free); redirect to save: `cc-webfetch <url> > file.md` |
| `cc-md2pdf` | cc-tools (built-in) | Convert Markdown to PDF via pandoc + XeLaTeX |
| `cc-nbconvert` | [jupyter/nbconvert](https://github.com/jupyter/nbconvert) | Convert Jupyter notebooks to Markdown and other formats |
| `cc-pdfplumber` | [jsvine/pdfplumber](https://github.com/jsvine/pdfplumber) | Extract tables and text from PDFs with precise layout information |
| `cc-arxiv` | [lukasschwab/arxiv.py](https://github.com/lukasschwab/arxiv.py) | Fetch arXiv paper metadata by ID: title, authors, year, PDF URL, HTML availability, abstract |

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
