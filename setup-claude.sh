#!/usr/bin/env bash
# setup-claude.sh — install or update cc-tools configuration for Claude Code
#   - Installs/reinstalls the cc-tools Python package in editable mode (local source)
#   - Manages the cc-tools section in ~/.claude/CLAUDE.md (sentinel-based, idempotent)
#   - Symlinks skills from skills/ into ~/.claude/commands/ (updates on git pull)
#   - With --project [dir]: create/update .claude/settings.local.json in that directory
#     with the standard cc-tools allowlist. Safe to run again — merges, never removes.
#   - With --adversary <brief-dir>: initialize an AG adversary workspace as a sibling
#     of the brief directory. Creates <brief-name>-adversary/ with GEMINI.md, cold-reads/,
#     critiques/, and settings.local.json. Also marks the brief as agent_role=primary.
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

# ── --adversary mode ──────────────────────────────────────────────────────────
# Usage: setup-claude.sh --adversary <brief-dir>
# Initializes an AG adversary workspace as a sibling of the brief directory.
# Creates <brief-name>-adversary/ with GEMINI.md, cold-reads/, critiques/,
# and .claude/settings.local.json (agent_role: adversary).
# Also writes agent_role: primary to the brief's settings.local.json.
# Works in non-git directories (e.g., iCloud Obsidian vaults).

if [[ "${1:-}" == "--adversary" ]]; then
    if [[ -z "${2:-}" ]]; then
        echo "setup-claude: --adversary requires a brief directory path" >&2
        echo "  Usage: setup-claude.sh --adversary <brief-dir>" >&2
        exit 1
    fi
    BRIEF_DIR="$(cd "$2" && pwd)"
    BRIEF_NAME="$(basename "$BRIEF_DIR")"
    PARENT_DIR="$(dirname "$BRIEF_DIR")"
    ADVERSARY_DIR="$PARENT_DIR/${BRIEF_NAME}-adversary"
    BRIEF_RELATIVE="../${BRIEF_NAME}"

    echo "setup-claude: initializing adversary workspace"
    echo "  Brief:    $BRIEF_DIR"
    echo "  Adversary: $ADVERSARY_DIR"

    # Create adversary workspace structure
    mkdir -p "$ADVERSARY_DIR/cold-reads"
    mkdir -p "$ADVERSARY_DIR/critiques"
    mkdir -p "$ADVERSARY_DIR/.claude"

    # Write adversary settings.local.json
    python3 - "$ADVERSARY_DIR/.claude/settings.local.json" "$BRIEF_RELATIVE" << 'PYEOF'
import json, sys, pathlib

path = pathlib.Path(sys.argv[1])
brief_root = sys.argv[2]
# Adversary allowlist: read tools only — AG is a read-only computational reviewer.
# cc-md2pdf excluded (AG does not generate PDFs).
# cc-dropbox-sync excluded (AG does not sync to Dropbox).
standard = [
    "Bash(cc-arxiv *)",
    "Bash(cc-fetch *)",
    "Bash(cc-webfetch *)",
    "Bash(cc-markitdown *)",
    "Bash(cc-nbconvert *)",
    "Bash(cc-ocr *)",
    "Bash(cc-pdfplumber *)",
    "Bash(curl *)",
    "Bash(mkdir *)",
]

data = json.loads(path.read_text()) if path.exists() else {}
allow = data.setdefault("permissions", {}).setdefault("allow", [])
added = [e for e in standard if e not in allow]
allow.extend(added)
data["agent_role"] = "adversary"
data["brief_root"] = brief_root
path.write_text(json.dumps(data, indent=2) + "\n")

if added:
    print(f"setup-claude: adversary settings: added {len(added)} permission entr{'y' if len(added)==1 else 'ies'}")
else:
    print(f"setup-claude: adversary settings: permissions already up to date")
print(f"setup-claude: adversary settings: agent_role=adversary, brief_root={brief_root}")
PYEOF

    # Write GEMINI.md from template, substituting brief name
    GEMINI_TEMPLATE="$SCRIPT_DIR/templates/gemini-workspace.md"
    GEMINI_DST="$ADVERSARY_DIR/GEMINI.md"
    if [[ -f "$GEMINI_TEMPLATE" ]]; then
        sed "s/\[brief-name\]/${BRIEF_NAME}/g; s/\[Project Name\]/${BRIEF_NAME}/g" \
            "$GEMINI_TEMPLATE" > "$GEMINI_DST"
        echo "setup-claude: wrote GEMINI.md from template (brief: ${BRIEF_NAME})"
    else
        echo "setup-claude: WARNING: template not found at $GEMINI_TEMPLATE — GEMINI.md not written"
    fi

    # Add cold-reads to .gitignore if inside a git repo
    GIT_ROOT="$(git -C "$ADVERSARY_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
    if [[ -n "$GIT_ROOT" ]]; then
        GITIGNORE="$GIT_ROOT/.gitignore"
        ADVERSARY_RELPATH="$(realpath --relative-to="$GIT_ROOT" "$ADVERSARY_DIR" 2>/dev/null \
            || python3 -c "import os; print(os.path.relpath('$ADVERSARY_DIR', '$GIT_ROOT'))")"
        IGNORE_ENTRY="${ADVERSARY_RELPATH}/cold-reads/"
        if ! grep -qF "$IGNORE_ENTRY" "$GITIGNORE" 2>/dev/null; then
            printf '\n# FR adversary cold reads — not shared before adjudication\n%s\n' \
                "$IGNORE_ENTRY" >> "$GITIGNORE"
            echo "setup-claude: added $IGNORE_ENTRY to $GITIGNORE"
        else
            echo "setup-claude: $IGNORE_ENTRY already in .gitignore"
        fi
    else
        echo "setup-claude: not in a git repo — skipping .gitignore update"
    fi

    # Mark brief as primary in its own settings.local.json
    BRIEF_SETTINGS="$BRIEF_DIR/.claude/settings.local.json"
    mkdir -p "$BRIEF_DIR/.claude"
    python3 - "$BRIEF_SETTINGS" "$ADVERSARY_DIR" << 'PYEOF'
import json, sys, pathlib

path = pathlib.Path(sys.argv[1])
adversary_path = sys.argv[2]
data = json.loads(path.read_text()) if path.exists() else {}
data["agent_role"] = "primary"
# Store adversary workspace path relative to the brief directory
import os
adversary_rel = os.path.relpath(adversary_path, str(path.parent.parent))
data["adversary_root"] = "../" + os.path.basename(adversary_path)
path.write_text(json.dumps(data, indent=2) + "\n")
print(f"setup-claude: brief settings: agent_role=primary, adversary_root set")
PYEOF

    echo "setup-claude: adversary workspace initialized at $ADVERSARY_DIR"
    echo ""
    echo "Next steps:"
    echo "  1. Edit $ADVERSARY_DIR/GEMINI.md — fill in project context and driving question"
    echo "  2. Launch AG from $ADVERSARY_DIR via /agent-brief or direct session"
    echo "  3. AG reads cold sources from ${BRIEF_RELATIVE}/raw/ — never from ${BRIEF_RELATIVE}/claims/drafts/"
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
