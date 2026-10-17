#!/usr/bin/env python3
"""Tests for provenance.py, taken from the table in docs/alternatives.md (fix 3 in docs/SPEC.md).
Run: python3 test_provenance.py   (or pytest)"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
L1 = ("2026-03-14  Proposal time went from 5 hours to 20 minutes.\n"
      "2026-05-02  Revenue grew 40%.\n"
      "2026-05-09  Closed a $12,000 contract.\n")
TWELVE = "We have 12 clients.\n"
ROUNDING = "Closed a $2,010 deal and reached 2,050,000 impressions.\n"
BIG = "We hired 250 people over 25 calls and got 3,400 sign-ups. Revenue doubled.\n"
POST = "We cut churn by 23% after one onboarding change.\n"
NOTE = "Spoke at SaaStr 2025 on pricing.\n"

# (draft, ledger, context or None, unsourced claims as printed; empty set means OK)
CASES = [
    ("We now serve 14 clients across 2026.", L1, None, {"14", "2026"}),
    ("We signed eleven new clients.", L1, None, {"eleven"}),
    ("Revenue grew 40 percent.", L1, None, set()),
    ("Revenue grew forty percent on a 12,000 dollar deal.", L1, None, set()),
    ("1. Draft it.\n2. Review it.\n3. Ship it.", L1, None, set()),
    ("47.\n\nThat is how many cold DMs I sent before one client replied.", L1, None, {"47"}),
    ("2019. That is the year I quit.", L1, None, {"2019"}),
    ("1. I sent 47 DMs.\n2. One replied.", L1, None, {"47"}),
    ("2. Review it.\n3. Ship it.", L1, None, {"2", "3"}),
    ("Free Tuesday at 3pm for 15 minutes? Or 9:30 a.m. Wednesday.", L1, None, {"15"}),
    ("Free Tuesday at 3pm for 15 minutes? Or 9:30 a.m. Wednesday.", L1, "Yes, 15 minutes is fine.\n", set()),
    ("Your 23% churn drop is higher than I would have guessed.", L1, POST, set()),
    ("Your 23% churn drop beats our 31%.", L1, POST, {"31"}),
    ("Loved your SaaStr 2025 talk.", L1, NOTE, set()),
    ("Proposal time fell from 5 hours to 20 minutes. One of the best changes.", L1, None, set()),
    ("It took {{your number}} weeks and twenty-five calls.", L1, None, {"twenty-five"}),
    ("It took 3 months.", L1, None, {"3"}),
    ("We grew 10x.", L1, None, {"10"}),
    ("We hired a hundred people.", L1, None, {"a hundred"}),
    ("Thousands of users signed up.", L1, None, {"Thousands"}),
    ("We tripled revenue.", L1, None, {"tripled"}),
    ("We doubled revenue.", L1, None, {"doubled"}),
    ("We halved the cost.", L1, None, {"halved"}),
    ("Sales went up threefold.", L1, None, {"threefold"}),
    ("It took five and six weeks.", L1, None, {"five and six"}),
    ("Our B2B team ran Q3 24/7.", L1, None, set()),
    ("That is the part I would double down on.", L1, None, set()),
    ("We doubled down on outbound.", L1, None, set()),
    ("We scaffold every new project the same way.", L1, None, set()),
    ("The second half of the talk was better.", L1, None, set()),
    ("My 2 cents: ship it.", L1, None, set()),
    ("We closed a $12k contract.", L1, None, set()),
    ("We closed a twelve thousand dollar contract.", L1, None, set()),
    ("We closed a $12M deal.", L1, None, {"$12M"}),
    ("Closed a $2.01k deal. Reached 2.05M impressions.", ROUNDING, None, set()),
    ("Closed a $2,011 deal.", ROUNDING, None, {"$2,011"}),
    ("Full template here: https://example.com/blog/2024/05/proposal-template-v3", L1, None, set()),
    ("Doing #100DaysOfCode with my team.", L1, None, set()),
    ("Ping @dev42 or mail me at jo99@example.com.", L1, None, set()),
    ("We have #1 ranked support.", L1, None, {"1"}),
    ("Call me on Tuesday the 14th.", L1, None, set()),
    ("Free on March 3rd or 14 May? Or the 2nd of June.", L1, None, set()),
    ("We grew 300% since May 2024.", L1, None, {"300", "2024"}),
    ("Our 14th client signed.", L1, None, {"14"}),
    ("We hit $12M in revenue.", TWELVE, None, {"$12M"}),
    ("We hit $12m in revenue.", TWELVE, None, {"$12m"}),
    ("We have 12 clients.", TWELVE, None, set()),
    ("two hundred and fifty hires, twenty-five calls, three thousand four hundred sign-ups", BIG, None, set()),
    ("3.4k sign-ups. Revenue doubled again.", BIG, None, set()),
    ("a dozen calls", BIG, None, {"dozen"}),
    ("We hired a hundred people.", BIG, None, {"a hundred"}),
]


def run(draft, ledger, context):
    with tempfile.TemporaryDirectory() as d:
        paths = []
        for name, text in (("draft.txt", draft), ("proof.md", ledger), ("context.txt", context)):
            if text is None:
                continue
            p = os.path.join(d, name)
            with open(p, "w", encoding="utf-8") as f:
                f.write(text)
            paths.append(p)
        r = subprocess.run([sys.executable, os.path.join(HERE, "provenance.py"), *paths],
                           capture_output=True, text=True, encoding="utf-8")
    flagged = {line.split("UNSOURCED", 1)[1].strip() for line in r.stdout.splitlines() if line.startswith("UNSOURCED")}
    return r.returncode, flagged, r.stdout


def test_table():
    bad = []
    for draft, ledger, context, want in CASES:
        code, flagged, out = run(draft, ledger, context)
        if flagged != want or code != (1 if want else 0) or (not want and "OK" not in out):
            bad.append(f"{draft!r}: want {sorted(want) or 'OK'}, got {sorted(flagged) or 'OK'} (exit {code})")
    assert not bad, "\n" + "\n".join(bad)


def test_f1_versions_with_empty_ledger():                             # A3.12, A3.13
    from test_li_human import INV, PH
    code, flagged, _ = run(INV, "", None)
    assert code == 1 and flagged == {"5", "20", "14"}, flagged
    code, flagged, _ = run(PH, "", None)
    assert code == 0 and not flagged, flagged


def test_template_ledger_sources_nothing():
    with open(os.path.join(HERE, "..", "..", "templates", "proof.md"), encoding="utf-8") as f:
        template = f.read()
    code, flagged, _ = run("We closed a $12,000 deal and grew 40%.", template, None)
    assert code == 1 and flagged == {"$12,000", "40"}, flagged


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted((n, f) for n, f in globals().items() if n.startswith("test_")):
        try:
            fn()
            print(f"ok    {name}")
        except Exception as e:                                 # a crash is a failure too
            failed += 1
            print(f"FAIL  {name}  {e}")
    sys.exit(1 if failed else 0)
