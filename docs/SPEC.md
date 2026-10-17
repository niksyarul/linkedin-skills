# Spec: six fixes from `docs/alternatives.md`

Status: **draft for review. No code has been changed.**
Source: section 5 and the appendix of [`alternatives.md`](alternatives.md). Section numbers like 2c and 8a refer to that doc.

## Order

| # | Fix | Closes | Doc ref |
|---|---|---|---|
| 1 | `joiners.py` + `humanize.py` patch | F5, link half of F3 | 2c |
| 2 | `detect.py` diff | F1, F2, link half of F3 | 2c, 2f, `N/A` |
| 3 | `provenance.py` + `proof.md` ledger | F1, F8 | 3a, 3b, 2f (5) |
| 4 | Flag-then-rewrite + artefacts-only lexicon | F4, word half of F3 | 2a, 4d |
| 5 | `events.csv` log + URL paste-back | F7 | 8a, 13c |
| 6 | Follow-up ledger + `plan.md` readers | F9, F11 | 11a, F11 |

**Fixes 1 and 2 must land in the same commit.** `detect.py` imports `joiners.py`, and the patched cleaner keeps real joiners that the unpatched `detect.py` still counts as invisible. *Checked on a scratch copy:* with only fix 1 applied, a 3-sentence comment with the woman-technologist emoji went from 62.0 REVIEW to **30.0 FLAGGED** (FINGERPRINT 0.0, "1 invisible") in the `li-human` loop. Fixes 1 and 2 are kept separate below so each can be reviewed on its own. They ship together.

Both appendix diffs apply cleanly to the current `humanize.py` and `detect.py` (`patch --dry-run`, no fuzz).

---

## Baseline (unpatched scripts)

Run 2026-10-17 on `main` @ `28a2b21`, Python 3.13.2, from a scratch directory with `S=skills/li-human`. The commands are the ones in the appendix's reproduction block. Every number matches the doc's "original scripts" column.

### Appendix reproduction block

| ID | Input | Command | Result |
|---|---|---|---|
| B1 | `t1.txt` (F4) | `humanize.py t1.txt --report` | `We cut the discovery call, it worked.` / `The market painting hung in our build home.` / `Get the door. I use the horse.` / `A important sign was important.` 6 lexicon swaps, 1 em dash. |
| B2 | `t5.txt` (F5) | `humanize.py t5.txt` then list code points | `1f469 1f4bb 1f3f4 645 6cc 62e 648 627 647 645`: no U+200D, no tags, no U+200C |
| B3 | `c1.txt` (F2) | `detect.py c1.txt` | BURSTINESS 50.0, SPECIFICITY 36.4, VOICE 50.0, **54.9 REVIEW**, weakest SPECIFICITY |
| B4 | `phone.txt` raw (F6) | `detect.py phone.txt` | FINGERPRINT 0.0, VOICE 65.0, **35.7 FLAGGED** |
| B5 | `phone.txt` cleaned | `humanize.py phone.txt \| detect.py -` | FINGERPRINT 100.0, VOICE 100.0, **65.1 REVIEW** |
| B6 | `honest.txt` (F1) | `detect.py honest.txt` | SPECIFICITY 0.0, BURSTINESS 49.5, **41.9 FLAGGED**, weakest SPECIFICITY |
| B7 | `ph.txt` | `detect.py ph.txt` | SPECIFICITY 0.0, BURSTINESS 54.3, **42.5 FLAGGED**, weakest SPECIFICITY |
| B8 | `inv.txt` | `detect.py inv.txt` | SPECIFICITY 100.0, BURSTINESS 52.0, **75.1 REVIEW** |

### Appendix table inputs ("original scripts" column)

Built with Python escapes, run through `humanize.py -` and `detect.py - --json`. Rows marked † are my own construction because the doc describes the input but does not give its exact text.

| ID | Input | Raw | Cleaned | Code points left after cleaning |
|---|---|---|---|---|
| B9 † | 3-sentence comment with woman-technologist emoji | FINGERPRINT 0.0, 30.0 FLAGGED | 62.0 REVIEW | `1F469 1F4BB` (emoji split) |
| B10 † | emoji + England flag + Persian word + Devanagari half-form + U+200B + 2 stray tags + "usca" flag + tag message | 30.0 FLAGGED | 62.0 REVIEW | every joiner and tag deleted |
| B11 | Chinese with 3 ZWNJs | 24.0 FLAGGED | 56.0 REVIEW | `4F60 597D 4E16 754C` |
| B12 | `Great post` + U+F0049 U+F0047 U+F004E + `. Thanks` + U+F8F1 + ` for this.` | 62.0 REVIEW | 62.0 REVIEW | private-use characters unchanged |
| B13 | tags joined by ZWJs + U+F0001 U+200D U+F0002 | 30.0 FLAGGED | 62.0 REVIEW | no ZWJ left |
| B14 | rainbow flag, black cat, scientist with skin tone, heart on fire | 24.0 FLAGGED | 56.0 REVIEW | all ZWJs deleted, VS16s kept |
| B15 | keycap one, U+00A9 U+FE0F, U+2764 U+FE0F, U+845B U+E0100 | 56.0 REVIEW | 56.0 REVIEW | unchanged |
| B16 | `Great post` + (U+FE0F U+200D) x 12 + U+FE0F + ` thanks for sharing.` | 30.0 FLAGGED | 62.0 REVIEW | 12 ZWJs deleted, **13 VS16 kept** |
| B17 | `Hi ` U+FE0F U+FE0E ` there`, `a` U+E0101 `b`, U+2764 U+FE0F U+200D U+FE0F U+200D U+FE0F | 30.0 FLAGGED | 62.0 REVIEW | every selector kept |
| B18 | link + U+200B + 14 tag characters (F3) | FINGERPRINT 0.0, 30.0 FLAGGED | **30.0 FLAGGED**, FINGERPRINT 0.0 | **all 15 kept** |
| B19 | `Full guide: https://example.com/leverage-robust-synergy and we use it every week now.` | SLOP 0.0, 30.0 FLAGGED | **30.0 FLAGGED**, SLOP 0.0 | none |
| B20 | `This is huge` + 2 rockets + ` Who else is seeing this? Agree?` | VOICE 50.0, 62.0 REVIEW | 62.0 REVIEW | rockets |
| B21 | 3-sentence stock paragraph (2a) | 29.5 FLAGGED | full lexicon: SLOP 100.0, 41.5 FLAGGED. Artefacts-only: SLOP 0.0, 29.5 FLAGGED | none |
| B22 | `A vital sign was crucial` + em dash + `we unlock the door.` + U+200B (4d) | 18.0 FLAGGED | full lexicon: `A important sign was important, we get the door.` Artefacts-only: `A vital sign was crucial, we unlock the door.` | U+200B removed in both |

Also recorded:
- `detect.py` exits 1 on any non-PASS verdict.
- `joiners.py` and `provenance.py` do not exist.
- `humanize.py draft.txt --report -o /dev/null` already prints the "3. SLOP LEXICON" flag list that 2a needs.

---

## Fix 1: `joiners.py` + `humanize.py` patch (2c)

**Goal.** Stop deleting format characters that belong to real text (emoji ZWJ sequences, RGI subdivision flags, ZWJ/ZWNJ in Arabic-script and Indic words). Remove characters glued to a link. Remove variation selectors that modify nothing.

**Files touched**
- `skills/li-human/joiners.py`: **new**, 81 lines, copied verbatim from the appendix. Every special character is written as an escape, never as a literal.
- `skills/li-human/humanize.py`: `import joiners`. In `humanize()`, call `joiners.clean_around(text, lambda t: pass_invisible(t, lex))` *before* `protect_urls`, and remove the old `pass_invisible` call.

**Acceptance tests.** Run `humanize.py`; the score columns depend on fix 2.

| ID | Input | Expected after fix |
|---|---|---|
| A1.1 | B2 `t5.txt` | U+200D in the emoji, England's 5 tags + U+E007F, and U+200C in the Persian word are all **kept** |
| A1.2 | B10 | Joiners in the emoji, the Persian word and the Devanagari half-form are kept. England's tags are kept. U+200B and the 36 other tag characters are deleted. "usca" becomes a plain black flag. |
| A1.3 | B11 | All 3 ZWNJs deleted (unchanged) |
| A1.4 | B12 | Private-use characters unchanged |
| A1.5 | B13 | No ZWJ left |
| A1.6 | B14 | All joiners and VS16s kept |
| A1.7 | B15 | Unchanged |
| A1.8 | B16 | All 12 ZWJs **and** all 13 VS16s deleted |
| A1.9 | B17 | Stray selectors and both ZWJs deleted. The heart keeps one VS16. |
| A1.10 | B18 | All 15 characters deleted, link text intact |
| A1.11 | `--report` on B10 | One line per character class (hit counts merged across segments) |
| A1.12 | `joiners.py` itself | Has no literal non-ASCII characters (`grep -P '[^\x00-\x7F]'` finds nothing) |

**Out of scope**
- Per-language lists of allowed joiner positions. One hidden bit per gap between emoji or letters remains possible; this is the doc's stated ceiling.
- Full Unicode emoji data. The fix uses 3 block ranges, so a ZWJ next to U+203C is still deleted.
- Non-RGI subdivision flags. These are reduced to a plain black flag, as today.

---

## Fix 2: `detect.py` diff (2c, 2f, `N/A`)

**Goal.**
- SPECIFICITY no longer counts toward the verdict, so the score stops rewarding invented numbers.
- Text too short to judge gets `N/A` instead of a flat 50.
- VOICE still counts structural tells on short text.
- Links are left out of SLOP DENSITY.
- FINGERPRINT counts invisible characters with `joiners.stray_cf`.
- New `gate_scores()` and `PASS_OVERALL, PASS_FLOOR` (needed later by `calibrate.py`).

**Files touched**
- `skills/li-human/detect.py`: the appendix diff verbatim, about 40 lines.
- `skills/li-human/SKILL.md`, step 4 wording: "fix the weakest *gated* check". SPECIFICITY advice means "ask the user for a real number, never invent one".
- `README.md`: the sample panel (`69.7 REVIEW (+44.9)`) must be re-run and replaced, because SPECIFICITY no longer gates and the numbers change.

**Acceptance tests.** Scored with the patched `detect.py`, plus fix 1.

| ID | Input | Expected |
|---|---|---|
| A2.1 | B6 / B7 / B8 | 72.2 / 74.9 / 73.6, all REVIEW. Weakest is BURSTINESS (49.5 / 54.3 / 52.0). SPECIFICITY is still printed, with the "Never invent one" line on B6 and B7. |
| A2.2 | B3 `c1.txt` | BURSTINESS `N/A`, **70.0 REVIEW**, weakest VOICE 50.0 |
| A2.3 | B4 / B5 `phone.txt` | 29.7 FLAGGED / 63.0 REVIEW |
| A2.4 | B9 raw | FINGERPRINT 100.0, 100.0 PASS |
| A2.5 | B9 cleaned | Emoji intact, 100.0 PASS |
| A2.6 | B11 raw | FINGERPRINT counts the 3 ZWNJs |
| A2.7 | B13 cleaned | FINGERPRINT 100.0, "0 invisible" |
| A2.8 | B16 raw / cleaned | Raw counts 25 invisible / cleaned 100.0 PASS |
| A2.9 | B18 cleaned | 100.0 PASS |
| A2.10 | B19 cleaned | Link not counted, 100.0 PASS |
| A2.11 | B20 cleaned | VOICE 34.0 (3 tells), **60.4 REVIEW**, weakest VOICE. **Must not PASS.** |
| A2.12 | `--json` on B3 | `"score": null` for BURSTINESS |
| A2.13 | Panel on B3 | Prints `N/A` and the "Too short to judge style" line |
| A2.14 | `import detect; detect.gate_scores` | Exists. `PASS_OVERALL, PASS_FLOOR == 70, 55` |

**Out of scope**
- `calibrate.py` (2e). It needs 20+ of the user's own posts and comes after all six fixes.
- Changing the 70/55 thresholds.
- Scoring against the user's own writing (2d).
- Fixing F6 for raw text beyond what this diff does. Curly quotes still score as machine-made on raw text.

---

## Fix 3: `provenance.py` + `proof.md` ledger (3a, 3b, 2f (5))

**Goal.** Every number or magnitude claim in any outgoing draft must be one of:
- in the user's ledger,
- in a context file for this draft,
- a `{{placeholder}}`.

This is enforced by code, in every skill that goes through `li-human`.

**Files touched**
- `skills/li-human/provenance.py`: **new**, 97 lines, copied verbatim from the appendix.
- `templates/proof.md`: **new**. Format: one fact per line, with an optional ISO date first. It replaces the "Proof I can use" section of `templates/voice.md`, which becomes a one-line pointer to `~/.claude/linkedin/proof.md`.
- `skills/li-human/SKILL.md`: step 4 gets a second required condition. `provenance.py clean.txt ~/.claude/linkedin/proof.md [context...]` must print `OK` before the copy-ready block is shown. The doc's three-way routing rule for false fails goes here:
  - a fact the user will reuse goes in the ledger;
  - a number from the text being answered, or one the user confirmed in chat, goes in this draft's context file;
  - a phrase that makes no claim goes in `IDIOMS`.

  Only the user's own chat message counts as confirmation.
- Context-file line, one per skill:
  - `li-comment/SKILL.md`: the post being commented on.
  - `li-reply/SKILL.md` and `li-inbox/SKILL.md`: the comment or message being answered.
  - `li-dm/SKILL.md`: the user's notes on the person.
  - `li-repurpose/SKILL.md`: the transcript.
- Source rule, one line per skill:
  - `li-post/SKILL.md`: numbers come from `proof.md`. Replaces the `voice.md` reference.
  - `li-profile/SKILL.md`: "outcome bullets with numbers" take their numbers from `proof.md`.
  - `li-carousel/SKILL.md`: run on slide text with `1/10` counters removed.
- `README.md`: list `proof.md` among the state files.

**Acceptance tests**

The full appendix table for `provenance.py` (32 rows), run with ledger `L1`, is the test. Each row's expected result is in the doc. The main rows:

| ID | Draft | Expected |
|---|---|---|
| A3.1 | `We now serve 14 clients across 2026.` | Fails on 14 and 2026 |
| A3.2 | `Revenue grew 40 percent.` / `...forty percent on a 12,000 dollar deal.` | OK / OK |
| A3.3 | `1. Draft it.` `2. Review it.` `3. Ship it.` | OK |
| A3.4 | `47.` + blank line + `That is how many cold DMs...` / `2019. That is the year I quit.` | Fails on 47 / on 2019 |
| A3.5 | `Your 23% churn drop beats our 31%.`, with the post as context | Fails on 31 only |
| A3.6 | `We tripled / doubled / halved... / threefold` | Each fails on its magnitude word |
| A3.7 | `We closed a $12M deal.` | Fails (12,000,000 is not 12,000) |
| A3.8 | `Closed a $2.01k deal. Reached 2.05M impressions.`, with the rounding ledger | OK |
| A3.9 | `It took {{your number}} weeks and twenty-five calls.` | Fails on "twenty-five" only |
| A3.10 | `We doubled down on outbound.` / `My 2 cents: ship it.` | OK (idiom) |
| A3.11 | Exit code | 0 on OK, 1 on any unsourced claim |
| A3.12 | Integration: `inv.txt` (B8) through the `li-human` loop with an empty `proof.md` | Copy-ready block is **not** shown. 5, 20 and 14 are listed as UNSOURCED. |
| A3.13 | Integration: `ph.txt` (B7) | `provenance.py` OK (placeholders are honest gaps) |

**Out of scope.** These are the known gaps the doc lists; the human read covers them.
- Names.
- Comparatives ("most", "far more").
- "one" and bare "half".
- Clock times.
- Claims inside a link or hashtag.
- Matching by meaning: a "5" in the ledger lets any "5" through.
- Claim-level source tags (3c).
- Experience bank for comments (4b).

---

## Fix 4: Flag-then-rewrite + artefacts-only lexicon (2a, 4d)

**Goal.** The lexicon becomes a detector, not a blind substituter. The model rewrites each flagged sentence with context, and the cleaner only removes artefacts. SLOP DENSITY then measures the draft, not whether the cleaner ran.

**Files touched**
- `skills/li-human/artefacts-only.json`: **new**. A copy of `slop.json` with `words` and `phrases` emptied, generated with the appendix one-liner and committed.
- `skills/li-human/SKILL.md`, "Order of operations" step 1 becomes three steps:
  1. Flag: `humanize.py draft.txt --report -o /dev/null`. The "3. SLOP LEXICON" section lists the flagged terms.
  2. Clean: `humanize.py draft.txt --lexicon artefacts-only.json -o clean.txt`.
  3. Rewrite: in `clean.txt`, rewrite each flagged sentence with the instruction "rewrite without X, keep meaning and voice". Show the user a diff, and repeat until step 1 lists nothing worth acting on.

  `detect.py` keeps scoring with the full `slop.json`.
- `li-comment`, `li-dm`, `li-reply`, `li-inbox` `SKILL.md`: short text is cleaned with `artefacts-only.json`. It is still scored; fix 2's `N/A` handles length.

**Acceptance tests**

| ID | Input | Expected |
|---|---|---|
| A4.1 | B1 `t1.txt` with `--lexicon artefacts-only.json` | No word swaps ("landscape", "foster", "Unlock", "harness", "vital", "crucial" all kept). Em dash still becomes a comma. |
| A4.2 | B22 | `A vital sign was crucial, we unlock the door.`, U+200B removed |
| A4.3 | B1 with `--report -o /dev/null` | Lists the 6 flagged terms. Writes no text. |
| A4.4 | B21, cleaned the 2a way and scored with patched `detect.py` | **SLOP DENSITY 0.0, 39.1 FLAGGED** (not the 97.4 PASS that full-lexicon substitution gets on the patched gate) |
| A4.5 | `artefacts-only.json` | Every key except `words` and `phrases` equals `slop.json` (a guard against drift when `slop.json` is edited) |
| A4.6 | Scenario: `/li-human` on B21 | Model rewrites all 3 sentences. Shows a diff. Re-flag lists nothing to act on. |

**Out of scope**
- The em dash to comma splice (F4 part 2). This is the typographic pass, not the lexicon.
- Personal allowlist from the user's corpus (2b).
- Constraining generation (1e).
- Making rewrites deterministic.

---

## Fix 5: `events.csv` log + URL paste-back (8a, 13c)

**Goal.**
- Log what was *published*, not what was approved.
- Key the log on the URL and the published text, not on the first line.
- Give `li-audit` (and later `compare.py`) a structured input.

**Schema.** `~/.claude/linkedin/events.csv`, CSV with a header row, written with Python's `csv` module so that multi-line text is quoted correctly:

```
date,kind,person,url,first_line,hook,format,theme,slot,published_text,impressions,reactions,comments,reposts
```

- `kind`: `post` | `comment`.
- `person`: for a comment, whose post it was on. Empty for posts.
- `slot`: empty until fix 6.
- The four counts: plain whole numbers, empty until day 7.

**Files touched**
- `skills/li-post/SKILL.md`, step 4/5:
  - On "yes", do **not** log. Ask the user to paste the post URL after publishing.
  - On the URL paste, ask the user to paste the post as published if they edited it, then append the row.
  - At +7 days (next session that touches the log), ask for the four counts and fill them in on the row with that `url`.
  - Change "Reply 'yes' to log it" to "Paste the URL once it is live".
- `skills/li-comment/SKILL.md`: the engagement-round note moves from `log.md` to `kind=comment` rows. These hold the target's name and the post URL only. No third-party post text is stored.
- `skills/li-audit/SKILL.md`:
  - Read `events.csv`, and join analytics rows by URL, then by `published_text`.
  - Fall back to `log.md` if `events.csv` does not exist (existing users).
- `skills/li-plan/SKILL.md`: read `events.csv` (falling back to `log.md`) for the last fortnight's themes.
- `README.md`: list `events.csv` among the state files.

**Acceptance tests**

| ID | Scenario | Expected |
|---|---|---|
| A5.1 | `/li-post`, user says "yes" | No row written. URL requested. |
| A5.2 | User pastes URL and an edited text | One row. `published_text` is the edited text. `first_line` is taken from it. |
| A5.3 | `published_text` containing commas, quotes and newlines | `csv.DictReader` reads it back as one row with the exact text |
| A5.4 | Day-7 counts pasted as `1,204` | Stored as `1204` |
| A5.5 | Appendix `compare.py` (unchanged) on a fixture `events.csv` in this schema, 6 posts + 1 non-post row | `not enough data: 2 'story' posts vs 4 others`. The non-post row is skipped. |
| A5.6 | Same, with a 30-row fixture (10 story at 3-6%, 20 others at 1-3%) | p = 0.0001 |
| A5.7 | `/li-audit` with only a legacy `log.md` | Still works, and says the join is by first line |

**Out of scope**
- `compare.py` in the repo (8c). It is used here only as a schema check.
- Account-archive join (8b).
- API posting (13b).
- Native scheduling (13a).
- `kind` values for DMs, replies and inbox (plan A).
- Migrating old `log.md` rows into `events.csv`.

---

## Fix 6: Follow-up ledger + `plan.md` readers (11a, F11)

**Goal.**
- Follow-ups at +4 and +10 days get due dates and a reader (F9).
- `plan.md` stops being write-only (F11).

**Schema.** `~/.claude/linkedin/outreach.csv`, one row per person, updated in place:

```
person,profile_url,invited,accepted,msg1_sent,due_4,due_10,replied,status
```

- `status`: `open` | `replied` | `closed`.
- `due_4` and `due_10` are computed from `msg1_sent`.
- No message bodies are stored.

**Files touched**
- `skills/li-dm/SKILL.md`: when the user confirms message 1 was sent, add or update the row with both due dates. When they confirm a follow-up was sent, record it. After +10, set `status=closed`.
- `skills/li-inbox/SKILL.md`:
  - A reply from someone in `outreach.csv` sets `replied` and `status=replied`.
  - Start triage by listing "follow-ups due today".
- `skills/li-plan/SKILL.md`:
  - The plan lists "due today / this week" from `outreach.csv`.
  - Write `plan.md` with a `week_of: YYYY-MM-DD` line and one line per day in the existing `DAY TIME TYPE #hook name - idea` format, so it can be read by line.
- `skills/li-post/SKILL.md`: read `plan.md`. If today has a slot, draft for it and write the slot type into the `slot` column of the `events.csv` row (fix 5).
- `skills/li-audit/SKILL.md`: read `plan.md` and report planned slots against posted rows for the audited weeks.
- `README.md`: remove "so the other skills can read it" as a promise, or make it true. With this fix it is true.

**Acceptance tests**

| ID | Scenario | Expected |
|---|---|---|
| A6.1 | `/li-dm`, user confirms message 1 sent on 2026-10-01 | Row with `due_4=2026-10-05`, `due_10=2026-10-11` |
| A6.2 | `/li-plan` on 2026-10-05 | Lists that person under "due today" |
| A6.3 | `/li-inbox` with a pasted reply from that person | Row becomes `replied`. The person is no longer listed as due. |
| A6.4 | `/li-plan` writes the appendix-style week | `plan.md` has `week_of:` and 7 parseable day lines |
| A6.5 | `/li-post` on a planned Tuesday | Uses Tuesday's slot without being told. The `events.csv` row has `slot=STORY` (or whatever was planned). |
| A6.6 | `/li-audit` | Reports e.g. "planned 4, posted 3, STORY slot skipped" |
| A6.7 | `grep -rl plan.md skills/` | Matches `li-plan`, `li-post` and `li-audit` (today: `li-plan` only) |

**Out of scope**
- Sending or scheduling anything. Reminders only.
- `.ics` export (11b).
- Warm-before-write gating (11c).
- The engagement list reaching `li-comment`.
- The plan as an experiment with a named weekly variable (7b, plan C).
- Backlog capture in `ideas.md` (7a).

---

## Cross-cutting

- **Data handling.** `events.csv` and `outreach.csv` hold names and profile URLs of third parties. They stay local under `~/.claude/linkedin/` and store no message bodies from other people. They must not be committed. `.gitignore` already scopes the repo, and these files live outside it.
- **Test harness.** The script tests (fixes 1 to 4) become one `skills/li-human/test_li_human.py`. It uses stdlib only, builds every input with escapes and asserts the expected values above, so the repo keeps no fixture files with invisible characters. The skill-behaviour tests (fixes 5 and 6) are manual scenarios, run once and recorded in the PR.
- **Rollout.** One PR per fix, except 1+2 (one PR). After each PR, rerun the baseline commands and update this table's "expected" values where the doc's numbers no longer hold.

## Open questions

1. Fix 5 writes CSV with an inline `python3 -c` `csv.writer` snippet in `SKILL.md`, not a helper script. Is that acceptable, or do you want a small `events.py`?
2. Fix 4: should short-text skills skip `detect.py` entirely (4d as written), or keep scoring now that fix 2 gives `N/A`? This spec keeps scoring.
3. Fix 3: should `voice.md`'s "Proof I can use" section be deleted outright, or kept as a pointer for existing users who already filled it in? This spec keeps it as a pointer.
