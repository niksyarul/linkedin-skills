#!/usr/bin/env python3
"""Tests for outreach.py (fix 6 in docs/SPEC.md). Run: python3 test_outreach.py   (or pytest)"""
import csv
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))


def cli(path, *args):
    env = dict(os.environ, LI_OUTREACH=path)
    return subprocess.run([sys.executable, os.path.join(HERE, "outreach.py"), *args],
                          capture_output=True, text=True, encoding="utf-8", env=env)


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_msg1_sets_due_dates():                                         # A6.1
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "outreach.csv")
        assert cli(p, "Ana Lima", "msg1", "2026-10-01", "url=https://linkedin.com/in/x").returncode == 0
        (r,) = rows(p)
        assert (r["due_4"], r["due_10"], r["status"]) == ("2026-10-05", "2026-10-11", "open")
        assert r["profile_url"] == "https://linkedin.com/in/x"


def test_due_lists_each_follow_up_once():                               # A6.2
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "outreach.csv")
        cli(p, "Ana Lima", "msg1", "2026-10-01")
        assert cli(p, "due", "2026-10-04").stdout == ""
        assert "Ana Lima  +4" in cli(p, "due", "2026-10-05").stdout
        cli(p, "ana lima", "fu1", "2026-10-05")                          # name matched case-insensitively
        assert cli(p, "due", "2026-10-06").stdout == ""
        assert "+10" in cli(p, "due", "2026-10-11").stdout
        cli(p, "Ana Lima", "fu2", "2026-10-11")
        assert cli(p, "due", "2026-12-01").stdout == "" and rows(p)[0]["status"] == "closed"
        assert len(rows(p)) == 1


def test_skipped_plus_4_still_gets_plus_10():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "outreach.csv")
        cli(p, "Cy Moe", "msg1", "2026-10-01")
        out = cli(p, "due", "2026-10-11").stdout
        assert "+10" in out and "+4" not in out


def test_reply_stops_follow_ups():                                      # A6.3
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "outreach.csv")
        cli(p, "Ben Ito", "msg1", "2026-10-01")
        cli(p, "Ben Ito", "replied", "2026-10-03")
        assert rows(p)[0]["status"] == "replied"
        assert cli(p, "due", "2026-10-20").stdout == ""


def test_bad_input_is_refused():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "outreach.csv")
        assert cli(p, "Ana", "pitched").returncode != 0
        assert cli(p, "Ana", "msg1", "Oct 1").returncode != 0
        assert not os.path.exists(p)


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted((n, f) for n, f in globals().items() if n.startswith("test_")):
        try:
            fn()
            print(f"ok    {name}")
        except Exception as e:                                 # a crash is a failure too
            failed += 1
            print(f"FAIL  {name}  {e!r}")
    sys.exit(1 if failed else 0)
