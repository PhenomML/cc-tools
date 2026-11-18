"""compaction-context hook: output shape for each event, and silence otherwise."""
import json
import os
import subprocess
import sys

HOOK = os.path.join(os.path.dirname(__file__), "..", "hooks", "compaction-context.py")


def run(payload):
    p = subprocess.run([sys.executable, "-I", HOOK], input=json.dumps(payload),
                       capture_output=True, text=True)
    assert p.returncode == 0
    return p.stdout


def test_session_start_compact_injects_facts(tmp_path):
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "operations.md").write_text("# ops\n")
    (tmp_path / "log.md").write_text("## [2026-11-17] a | x\n\n## [2026-11-18] b | y\n")
    out = json.loads(run({"hook_event_name": "SessionStart", "source": "compact", "cwd": str(tmp_path)}))
    h = out["hookSpecificOutput"]
    assert h["hookEventName"] == "SessionStart"
    ctx = h["additionalContext"]
    assert "was compacted" in ctx
    assert "wiki/operations.md" in ctx
    assert "## [2026-11-18] b | y" in ctx and "2026-11-17" not in ctx


def test_session_start_compact_without_files(tmp_path):
    out = json.loads(run({"hook_event_name": "SessionStart", "source": "compact", "cwd": str(tmp_path)}))
    ctx = out["hookSpecificOutput"]["additionalContext"]
    assert "operations document" not in ctx and "log.md" not in ctx


def test_other_sources_are_silent(tmp_path):
    for src in ("startup", "resume", "clear", "fork"):
        assert run({"hook_event_name": "SessionStart", "source": src, "cwd": str(tmp_path)}) == ""


def test_pre_compact_prints_guidance(tmp_path):
    out = run({"hook_event_name": "PreCompact", "trigger": "auto", "cwd": str(tmp_path)})
    assert "last action in flight" in out and len(out) < 10000


def test_bad_input_exits_zero():
    p = subprocess.run([sys.executable, "-I", HOOK], input="not json", capture_output=True, text=True)
    assert p.returncode == 0 and p.stdout == ""
