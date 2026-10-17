#!/usr/bin/env python3
"""The follow-up ledger: one row per person, in ~/.claude/linkedin/outreach.csv.
It remembers due dates. It never sends anything, and it stores no message text.

  outreach.py PERSON STEP [YYYY-MM-DD] [url=PROFILE_URL]
      STEP is invited | accepted | msg1 | fu1 | fu2 | replied. Date defaults to today.
      msg1 sets the +4 and +10 day due dates. fu2 closes the thread. replied stops follow-ups.
  outreach.py due [YYYY-MM-DD]
      follow-ups due on or before that day (default today), oldest first

PERSON is matched case-insensitively. LI_OUTREACH overrides the path."""
import csv
import datetime
import os
import sys

PATH = os.environ.get("LI_OUTREACH") or os.path.expanduser("~/.claude/linkedin/outreach.csv")
COLS = ["person", "profile_url", "invited", "accepted", "msg1", "due_4", "fu1", "due_10", "fu2",
        "replied", "status"]
STEPS = ["invited", "accepted", "msg1", "fu1", "fu2", "replied"]


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


def record(person, step, day, url=""):
    rows = read()
    row = next((r for r in rows if r["person"].lower() == person.lower()), None)
    if row is None:
        row = dict.fromkeys(COLS, "") | {"person": person, "status": "open"}
        rows.append(row)
    row[step] = day.isoformat()
    row["profile_url"] = url or row["profile_url"]
    if step == "msg1":
        row["due_4"] = (day + datetime.timedelta(days=4)).isoformat()
        row["due_10"] = (day + datetime.timedelta(days=10)).isoformat()
    if step == "fu2":
        row["status"] = "closed"
    if step == "replied":
        row["status"] = "replied"
    write(rows)


def due(day):
    out = []
    for r in read():
        if r["status"] != "open":
            continue
        # +10 is due on day 10 even if +4 was skipped ("nothing new, no follow-up").
        if r["due_10"] and not r["fu2"] and r["due_10"] <= day.isoformat():
            out.append((r["due_10"], r["person"], "+10 follow-up: close the loop"))
        elif r["due_4"] and not r["fu1"] and r["due_4"] <= day.isoformat():
            out.append((r["due_4"], r["person"], "+4 follow-up: add something new"))
    return sorted(out)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["due"]:
        when = datetime.date.fromisoformat(args[1]) if len(args) > 1 else datetime.date.today()
        for d, person, what in due(when):
            print(f"{d}  {person}  {what}")
    elif len(args) >= 2 and args[1] in STEPS:
        rest = args[2:]
        url = next((a[4:] for a in rest if a.startswith("url=")), "")
        dates = [a for a in rest if not a.startswith("url=")]
        record(args[0], args[1], datetime.date.fromisoformat(dates[0]) if dates else datetime.date.today(), url)
    else:
        sys.exit(__doc__)
