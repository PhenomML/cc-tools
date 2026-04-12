# cc-tools

This repository is **Claude's toolset**, not a research library. It has nothing to do with your Conda environment or project dependencies. You install it once per machine so that the Claude Code (CC) assistant running in any of your projects has access to a consistent, versioned set of tools regardless of which project you are in.

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
```

That's it. The tools are now available system-wide on this machine. You do not activate anything — the commands are on your PATH automatically.

## Keeping it up to date

When Claude adds new tools to this repository, pull and reinstall:

```bash
cd ~/Projects/PhenomML/cc-tools
git pull
uv tool upgrade cc-tools
```

Claude will tell you when this is needed.

## What's included

| Command | Source | Purpose |
|---|---|---|
| `cc-markitdown` | [microsoft/markitdown](https://github.com/microsoft/markitdown) | Convert PDFs, Office docs, HTML, and other formats to Markdown |
| `cc-nbconvert` | [jupyter/nbconvert](https://github.com/jupyter/nbconvert) | Convert Jupyter notebooks to Markdown and other formats |
| `cc-pdfplumber` | [jsvine/pdfplumber](https://github.com/jsvine/pdfplumber) | Extract tables and text from PDFs with precise layout information |
| `arxiv` (library) | [lukasschwab/arxiv.py](https://github.com/lukasschwab/arxiv.py) | Fetch paper metadata and PDF links from arXiv — used programmatically by Claude |

More tools will be added here as the standard Claude instantiation grows.

## Your Conda environments are unaffected

`uv tool` installs into `~/.local/share/uv/tools/cc-tools/` — a completely separate location from any Conda environment. It does not touch your `base` environment or any project environment. The two systems do not interact.
