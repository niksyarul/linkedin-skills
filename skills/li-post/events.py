#!/usr/bin/env python3
"""The publication log: one row per published post or comment, in ~/.claude/linkedin/events.csv.
Rows are added when the user pastes the live URL, not when they approve a draft.

  events.py add < row.json            add one row; JSON object, any of the columns below
  events.py update URL key=value ...  fill in fields on the row with that URL (e.g. day-7 counts)
  events.py pending                   posts 7+ days old with no impressions yet

Missing date defaults to today, missing first_line is taken from published_text.
Counts are stored as plain whole numbers ("1,204" -> 1204). LI_EVENTS overrides the path."""
import csv
import datetime
import json
import os
import sys

PATH = os.environ.get("LI_EVENTS") or os.path.expanduser("~/.claude/linkedin/events.csv")
COLS = ["date", "kind", "person", "url", "first_line", "hook", "format", "theme", "slot",
        "published_text", "impressions", "reactions", "comments", "reposts"]
COUNTS = COLS[-4:]


def count(v):
    v = str(v).replace(",", "").strip()
    if v and not v.isdigit():
        sys.exit(f"not a whole number: {v!r}")
    return v


def read():
    if not os.path.exists(PATH):
        return []
    with open(PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(rows):
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    with open(PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, COLS)
        w.writeheader()
        w.writerows(rows)


def add(row):
    unknown = set(row) - set(COLS)
    if unknown:
        sys.exit(f"unknown column(s): {', '.join(sorted(unknown))}")
    row = {c: str(row.get(c, "")) for c in COLS}
    row["date"] = row["date"] or datetime.date.today().isoformat()
    text = row["published_text"].strip()
    row["first_line"] = row["first_line"] or (text.splitlines()[0] if text else "")
    for c in COUNTS:
        row[c] = count(row[c])
    rows = read()
    if row["url"] and any(r["url"] == row["url"] for r in rows):
        sys.exit(f"already logged: {row['url']} (use update)")
    write(rows + [row])


def update(url, pairs):
    rows = read()
    hit = [r for r in rows if r["url"] == url]
    if not hit:
        sys.exit(f"no row with url {url}")
    for k, v in (p.split("=", 1) for p in pairs):
        if k not in COLS:
            sys.exit(f"unknown column: {k}")
        hit[0][k] = count(v) if k in COUNTS else v
    write(rows)


def pending(today=None):
    cutoff = (today or datetime.date.today()) - datetime.timedelta(days=7)
    return [r for r in read() if r["kind"] == "post" and not r["impressions"]
            and datetime.date.fromisoformat(r["date"]) <= cutoff]


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "add":
        add(json.load(sys.stdin))
    elif cmd == "update" and len(sys.argv) > 3:
        update(sys.argv[2], sys.argv[3:])
    elif cmd == "pending":
        for r in pending():
            print(f"{r['date']}  {r['url']}  {r['first_line'][:60]}")
    else:
        sys.exit(__doc__)
