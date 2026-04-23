#!/usr/bin/env bash
# setup-claude.sh — install or update the cc-tools section in ~/.claude/CLAUDE.md
# Safe to run multiple times; uses sentinel comments to locate and replace the managed block.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SECTION="$SCRIPT_DIR/claude-md-section.md"
CLAUDE_MD="$HOME/.claude/CLAUDE.md"
BEGIN="<!-- cc-tools:begin -->"
END="<!-- cc-tools:end -->"

mkdir -p "$HOME/.claude"

if [[ ! -f "$CLAUDE_MD" ]]; then
    printf '# Claude Code Global Configuration\n\n' > "$CLAUDE_MD"
fi

if grep -qF "$BEGIN" "$CLAUDE_MD"; then
    # Update existing managed block in place.
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
    # Append fresh managed block.
    {
        printf '\n%s\n' "$BEGIN"
        cat "$SECTION"
        printf '%s\n' "$END"
    } >> "$CLAUDE_MD"
    echo "setup-claude: added cc-tools section to $CLAUDE_MD"
fi
