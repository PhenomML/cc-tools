#!/usr/bin/env bash
# setup-claude.sh — install or update cc-tools configuration for Claude Code
#   - Installs/reinstalls the cc-tools Python package in editable mode (local source)
#   - Manages the cc-tools section in ~/.claude/CLAUDE.md (sentinel-based, idempotent)
#   - Symlinks skills from skills/ into ~/.claude/commands/ (updates on git pull)
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

# ── Git hooks ─────────────────────────────────────────────────────────────────

HOOK_SRC="$SCRIPT_DIR/hooks/pre-commit"
HOOK_DST="$SCRIPT_DIR/.git/hooks/pre-commit"

if [[ -f "$HOOK_SRC" ]]; then
    cp "$HOOK_SRC" "$HOOK_DST"
    chmod +x "$HOOK_DST"
    echo "setup-claude: installed pre-commit hook (math notation check)"
fi
