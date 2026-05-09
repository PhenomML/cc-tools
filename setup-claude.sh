#!/usr/bin/env bash
# setup-claude.sh — install or update cc-tools configuration for Claude Code
#   - Installs/reinstalls the cc-tools Python package in editable mode (local source)
#   - Manages the cc-tools section in ~/.claude/CLAUDE.md (sentinel-based, idempotent)
#   - Symlinks skills from skills/ into ~/.claude/commands/ (updates on git pull)
#   - With --project [dir]: create/update .claude/settings.local.json in that directory
#     with the standard cc-tools allowlist. Safe to run again — merges, never removes.
# Safe to run multiple times.
#
# MCP servers are NOT registered globally by this script. See mcp/ for reference
# configs and README for the project-scoped .mcp.json pattern.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SECTION="$SCRIPT_DIR/claude-md-section.md"
CLAUDE_MD="$HOME/.claude/CLAUDE.md"
BEGIN="<!-- cc-tools:begin -->"
END="<!-- cc-tools:end -->"

# ── --project mode ────────────────────────────────────────────────────────────
# Usage: setup-claude.sh --project [dir]
# Creates or updates .claude/settings.local.json in the target directory with
# the standard cc-tools allowlist. If dir is omitted, uses the current directory.

if [[ "${1:-}" == "--project" ]]; then
    PROJECT_DIR="${2:-$(pwd)}"
    mkdir -p "$PROJECT_DIR"
    PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"
    SETTINGS_DIR="$PROJECT_DIR/.claude"
    SETTINGS_FILE="$SETTINGS_DIR/settings.local.json"
    mkdir -p "$SETTINGS_DIR"
    python3 - "$SETTINGS_FILE" << 'PYEOF'
import json, sys, pathlib

path = pathlib.Path(sys.argv[1])
standard = [
    "Bash(cc-arxiv *)",
    "Bash(cc-fetch *)",
    "Bash(cc-webfetch *)",
    "Bash(cc-markitdown *)",
    "Bash(cc-md2pdf *)",
    "Bash(cc-nbconvert *)",
    "Bash(cc-ocr *)",
    "Bash(cc-pdfplumber *)",
    "Bash(cc-dropbox-sync *)",
    "Bash(curl *)",
    "Bash(mkdir *)",
]

data = json.loads(path.read_text()) if path.exists() else {}
allow = data.setdefault("permissions", {}).setdefault("allow", [])
added = [e for e in standard if e not in allow]
allow.extend(added)
path.write_text(json.dumps(data, indent=2) + "\n")

if added:
    print(f"setup-claude: added {len(added)} entr{'y' if len(added)==1 else 'ies'} to {path}")
    for e in added:
        print(f"  + {e}")
else:
    print(f"setup-claude: {path} already up to date")
PYEOF
    exit 0
fi

# ── Python package ───────────────────────────────────────────────────────────

uv tool install --editable "$SCRIPT_DIR" --quiet
echo "setup-claude: cc-tools Python package installed (editable) from $SCRIPT_DIR"

# ── CLAUDE.md ────────────────────────────────────────────────────────────────

mkdir -p "$HOME/.claude"

if [[ ! -f "$CLAUDE_MD" ]]; then
    printf '# Claude Code Global Configuration\n\n' > "$CLAUDE_MD"
fi

if grep -qF "$BEGIN" "$CLAUDE_MD"; then
    CLAUDE_MD="$CLAUDE_MD" SECTION="$SECTION" python3 - <<'PYEOF'
import os, re, pathlib
path    = pathlib.Path(os.environ["CLAUDE_MD"])
section = pathlib.Path(os.environ["SECTION"]).read_text()
text    = path.read_text()
begin   = "<!-- cc-tools:begin -->"
end     = "<!-- cc-tools:end -->"
block   = begin + "\n" + section.strip() + "\n" + end
result  = re.sub(
    re.escape(begin) + r".*?" + re.escape(end),
    lambda m: block,
    text,
    flags=re.DOTALL,
)
path.write_text(result)
PYEOF
    echo "setup-claude: updated cc-tools section in $CLAUDE_MD"
else
    {
        printf '\n%s\n' "$BEGIN"
        cat "$SECTION"
        printf '%s\n' "$END"
    } >> "$CLAUDE_MD"
    echo "setup-claude: added cc-tools section to $CLAUDE_MD"
fi

# ── Skills ───────────────────────────────────────────────────────────────────

SKILLS_SRC="$SCRIPT_DIR/skills"
COMMANDS_DIR="$HOME/.claude/commands"
mkdir -p "$COMMANDS_DIR"

count=0
for skill in "$SKILLS_SRC"/*.md; do
    [[ -f "$skill" ]] || continue
    name="$(basename "$skill")"
    target="$COMMANDS_DIR/$name"
    if [[ -L "$target" ]]; then
        ln -sf "$skill" "$target"
    elif [[ -e "$target" ]]; then
        echo "setup-claude: skipping $name — exists and is not a symlink (user-created file?)"
        continue
    else
        ln -s "$skill" "$target"
    fi
    (( count++ )) || true
done
echo "setup-claude: $count skill(s) linked to $COMMANDS_DIR"

# ── Optional system dependencies ─────────────────────────────────────────────

for tool in pandoc ffmpeg pdftoppm tesseract; do
    if ! command -v "$tool" &>/dev/null; then
        case "$tool" in
            pdftoppm)  hint="brew install poppler" ;;
            tesseract) hint="brew install tesseract" ;;
            *)         hint="brew install $tool" ;;
        esac
        echo "setup-claude: WARNING: $tool not found — some cc-tools features will be limited ($hint)"
    fi
done

# ── Git hooks ─────────────────────────────────────────────────────────────────

HOOK_SRC="$SCRIPT_DIR/hooks/pre-commit"
HOOK_DST="$SCRIPT_DIR/.git/hooks/pre-commit"

if [[ -f "$HOOK_SRC" ]]; then
    cp "$HOOK_SRC" "$HOOK_DST"
    chmod +x "$HOOK_DST"
    echo "setup-claude: installed pre-commit hook (math notation check)"
fi
