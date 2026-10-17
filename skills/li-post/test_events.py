#!/usr/bin/env python3
"""Tests for events.py (fix 5 in docs/SPEC.md). Run: python3 test_events.py   (or pytest)"""
import csv
import datetime
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))


def cli(path, *args, stdin=None):
    env = dict(os.environ, LI_EVENTS=path)
    return subprocess.run([sys.executable, os.path.join(HERE, "events.py"), *args], input=stdin,
                          capture_output=True, text=True, encoding="utf-8", env=env)


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


TEXT = 'Our proposals took "most of a week".\nNow, an afternoon.\n\nTry the template, first.'


def test_add_round_trips_published_text():                             # A5.2, A5.3
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "events.csv")
        r = cli(p, "add", stdin=json.dumps({"kind": "post", "url": "https://lnkd.in/a", "hook": "#17",
                                            "published_text": TEXT, "date": "2026-10-01"}))
        assert r.returncode == 0, r.stderr
        (row,) = rows(p)
        assert row["published_text"] == TEXT
        assert row["first_line"] == 'Our proposals took "most of a week".'
        assert row["impressions"] == ""


def test_update_normalises_counts():                                    # A5.4
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "events.csv")
        cli(p, "add", stdin=json.dumps({"kind": "post", "url": "u1", "published_text": "x"}))
        r = cli(p, "update", "u1", "impressions=1,204", "reactions=37", "comments=9", "reposts=0")
        assert r.returncode == 0, r.stderr
        assert [rows(p)[0][k] for k in ("impressions", "reactions", "comments", "reposts")] == ["1204", "37", "9", "0"]
        assert cli(p, "update", "u1", "impressions=1.2k").returncode != 0
        assert cli(p, "update", "nope", "impressions=1").returncode != 0


def test_rejects_duplicate_url_and_unknown_column():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "events.csv")
        row = json.dumps({"kind": "post", "url": "u1"})
        assert cli(p, "add", stdin=row).returncode == 0
        assert cli(p, "add", stdin=row).returncode != 0
        assert cli(p, "add", stdin=json.dumps({"kind": "post", "impresions": "5"})).returncode != 0
        assert len(rows(p)) == 1


def test_pending_lists_posts_due_for_counts():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "events.csv")
        old = (datetime.date.today() - datetime.timedelta(days=8)).isoformat()
        for url, date, kind in (("old", old, "post"), ("new", datetime.date.today().isoformat(), "post"),
                                ("cmt", old, "comment")):
            cli(p, "add", stdin=json.dumps({"kind": kind, "url": url, "date": date, "published_text": url}))
        out = cli(p, "pending").stdout
        assert "old" in out and "new" not in out and "cmt" not in out
        cli(p, "update", "old", "impressions=10")
        assert cli(p, "pending").stdout == ""


def test_schema_feeds_engagement_rate():                               # A5.5: what compare.py (8c) reads
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "events.csv")
        cli(p, "add", stdin=json.dumps({"kind": "post", "url": "u", "format": "story", "impressions": "1,000",
                                        "reactions": "30", "comments": "15", "reposts": "5"}))
        (r,) = rows(p)
        assert (int(r["reactions"]) + int(r["comments"]) + int(r["reposts"])) / int(r["impressions"]) == 0.05


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
