#!/usr/bin/env bash
# setup-claude.sh — install or update cc-tools configuration for Claude Code
#   - Manages the cc-tools section in ~/.claude/CLAUDE.md (sentinel-based, idempotent)
#   - Symlinks skills from skills/ into ~/.claude/commands/ (updates on git pull)
#   - Merges MCP server entries from mcp/ into ~/.claude.json (idempotent)
# Safe to run multiple times.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SECTION="$SCRIPT_DIR/claude-md-section.md"
CLAUDE_MD="$HOME/.claude/CLAUDE.md"
BEGIN="<!-- cc-tools:begin -->"
END="<!-- cc-tools:end -->"

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

# ── MCP servers ──────────────────────────────────────────────────────────────
# Each file in mcp/ is a JSON object whose keys are server names and values
# are server config objects. They are merged into ~/.claude.json under
# "mcpServers". Existing non-cc-tools entries are preserved.

MCP_DIR="$SCRIPT_DIR/mcp"
CLAUDE_JSON="$HOME/.claude.json"

MCP_DIR="$MCP_DIR" CLAUDE_JSON="$CLAUDE_JSON" python3 - <<'PYEOF'
import json, os, pathlib

mcp_dir    = pathlib.Path(os.environ["MCP_DIR"])
claude_json = pathlib.Path(os.environ["CLAUDE_JSON"])

config = json.loads(claude_json.read_text()) if claude_json.exists() else {}
config.setdefault("mcpServers", {})

added = []
for cfg_file in sorted(mcp_dir.glob("*.json")):
    servers = json.loads(cfg_file.read_text())
    for name, entry in servers.items():
        config["mcpServers"][name] = entry
        added.append(name)

claude_json.write_text(json.dumps(config, indent=2) + "\n")
print(f"setup-claude: registered MCP server(s): {', '.join(added)}")
PYEOF
