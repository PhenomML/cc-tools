"""Regression for #74/#76: a timed-out make4ht must not leave a grandchild running."""
import os
import sys
import time

from cc_tools.arxiv_fetch import _run_in_group


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def test_timeout_kills_grandchild(tmp_path):
    pidfile = tmp_path / "grandchild.pid"
    # Parent shell spawns a sleeping grandchild via sh -c, as make4ht does with latex.
    script = f"sh -c 'echo $$ > {pidfile}; exec sleep 300' & wait"
    rc, out, err, timed_out = _run_in_group(["sh", "-c", script], str(tmp_path), os.environ.copy(), 2)
    assert timed_out
    pid = int(pidfile.read_text())
    time.sleep(0.5)
    assert not _alive(pid), "grandchild survived the timeout"


def test_normal_exit_not_timed_out(tmp_path):
    rc, out, err, timed_out = _run_in_group(
        [sys.executable, "-c", "print('ok')"], str(tmp_path), os.environ.copy(), 10)
    assert rc == 0 and not timed_out and out.strip() == b"ok"
