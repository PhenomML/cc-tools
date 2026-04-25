Upgrade the cc-tools managed section in this wiki's CLAUDE.md: $ARGUMENTS

Run from the wiki root (the directory containing CLAUDE.md).

## Step 1 — Verify sentinels

Check that CLAUDE.md contains both sentinel markers. If either is missing, the file
was not initialised from the template and cannot be upgraded automatically — report
this and stop.

```bash
grep -c "cc-tools:wiki:begin\|cc-tools:wiki:end" CLAUDE.md
```

The output should be `2`. If not, stop and explain.

## Step 2 — Apply the upgrade

Replace the content between the sentinels with the current wiki-schema.md from cc-tools:

```bash
WIKI_CLAUDE="CLAUDE.md"
SCHEMA=~/Projects/PhenomML/cc-tools/templates/wiki-schema.md

WIKI_CLAUDE="$WIKI_CLAUDE" SCHEMA="$SCHEMA" python3 - <<'PYEOF'
import os, re, pathlib
path   = pathlib.Path(os.environ["WIKI_CLAUDE"])
schema = pathlib.Path(os.environ["SCHEMA"]).read_text()
text   = path.read_text()
begin  = "<!-- cc-tools:wiki:begin -->"
end    = "<!-- cc-tools:wiki:end -->"
block  = begin + "\n" + schema.strip() + "\n" + end
result = re.sub(
    re.escape(begin) + r".*?" + re.escape(end),
    lambda m: block,
    text,
    flags=re.DOTALL,
)
path.write_text(result)
PYEOF
```

## Step 3 — Verify and report

Read CLAUDE.md and confirm:
- The Sub-wikis table is unchanged
- The managed section (Structure, Page conventions, workflows, tools) reflects the
  current cc-tools template

Append to `log.md`:
```
## [<YYYY-MM-DD>] upgrade | cc-tools wiki schema updated
```
