# Other ways to solve what linkedin-skills solves

## Assumptions

- "The same problems" means the jobs the eleven skills do for one person running their own LinkedIn account. It does not mean the repo's internals. I took the problems from the repo itself: its README, the eleven `SKILL.md` files, `hooks.json`, `slop.json`, `rubric.json`, `voice.md` and the two Python scripts.
- "Alternative" means a different mechanism for the same outcome, not a tweak. Where a small fix closes a real defect, I give the fix too, labelled as a fix.
- The repo's hard boundaries stay in place unless I say otherwise: no browser automation, no scraping, no invented facts, and the user approves everything. Where an alternative moves one of these boundaries, I say so.
- I ran the repo's own scripts on test inputs to check its behaviour. Each finding marked *(reproduced)* comes from running the code, not from reading it. The inputs are in the appendix, so you can rerun them.
- Several alternatives come with code: `joiners.py` plus a two-line patch to `humanize.py`, one diff to `detect.py` (script-aware invisible count, SPECIFICITY out of the verdict, `N/A` for short text that still counts structural tells, links left out of SLOP DENSITY), `provenance.py`, `calibrate.py` and `compare.py`, all in the appendix. Each was run against the test cases listed next to it, on a scratch copy of the repo; every input that failed under review has been added to those tables. Where a script has a known blind spot, the appendix names the ones I found. Test cases cannot prove there are no others.
- The scripts have to be applied in a fixed order, because some depend on others. The order is in section 5.
- This document contains no literal invisible characters. Where one matters, it is written as a code point (U+200D) or a Python escape (`"\u200d"`), so the text survives being passed through a cleaner such as `humanize.py`.
- In `li-human`'s own order of operations, `detect.py` scores the raw draft only as the "before" side of the before/after (step 3). The PASS/REVIEW/FLAGGED verdict that the loop in step 4 acts on is taken on the cleaned text. Where a finding depends on which of the two is scored, I say which.
- Some claims are about LinkedIn's current products, such as its APIs, native scheduling and the data export. I did not check these against today's documentation, so they are marked **verify**.

---

## 1. The system as it stands

### The problems it solves

| # | Problem (the user's job) | Skill(s) that own it |
|---|---|---|
| P1 | Turn a raw idea into a post that sounds like me | `/li-post`, `templates/voice.md`, `hooks.json` |
| P2 | Don't let the text read as machine-written | `/li-human` (`humanize.py`, `detect.py`, `slop.json`) |
| P3 | Never put a false claim under my name | Cross-cutting. The rule is written in `/li-post` (`{{your number}}`) and partly in `/li-dm` |
| P4 | Be visible on other people's posts | `/li-comment` |
| P5 | Handle the thread under my own post | `/li-reply` |
| P6 | Make the profile convert visitors | `/li-profile`, `rubric.json` |
| P7 | Decide what to post, when, and who to engage with | `/li-plan` |
| P8 | Learn what actually works for my account | `/li-audit` |
| P9 | Produce document posts (carousels) | `/li-carousel` |
| P10 | Never run out of material | `/li-repurpose` |
| P11 | Outbound: invites, first DM, follow-ups | `/li-dm` |
| P12 | Inbound: triage the inbox | `/li-inbox` |
| P13 | Get text onto LinkedIn without risking the account | Built into every skill: a copy-ready block the user pastes |

### How the parts connect

```
            voice.md (static, hand-filled or inferred from 3 posts)
                 |  read by li-post (and "every skill", per README)
                 v
 li-plan ---> plan.md  (written, never read by any skill: F11)
   ^
   |                      li-post ---> li-human ---> copy-ready block ---> USER PASTES
   |                         |  on "yes"                                     |
   |                         v                                               | (nothing flows back)
   |                      log.md  <--- li-comment batch notes                v
   |                         |                                        LinkedIn analytics
   +------ li-audit <--------+---------- user pastes CSV/screenshots --------+
```

Everything else (`li-comment`, `li-reply`, `li-dm`, `li-inbox`, `li-carousel`, `li-repurpose`, `li-profile`) is a stateless worker: paste in, draft out, through `li-human`. Three files carry state: `voice.md`, `plan.md` and `log.md`. Only two of them are ever read: `plan.md` is written by `li-plan` "so the other skills can read it", but no `SKILL.md` reads it (F11). `log.md` has no schema, and two skills write different things into it.

### Load-bearing design choices

1. **Generate, then clean.** The model writes the prose and a regex pipeline removes its fingerprints afterwards.
2. **Generic priors as fixed rules.** 900-1,300 characters, 8-12 slides, Tuesday to Thursday 7:30-9:30am, follow up at +4 and +10 days, 20 invites a day, four posts a week. On top of these sit the hook claims in `hooks.json`, such as "Highest save rate of the 21" and "reach roughly doubles". None of them has a source. They are stated as facts.
3. **A local score as the quality gate.** `detect.py` returns PASS, REVIEW or FLAGGED, and `/li-human` says to loop on "the weakest check" until PASS.
4. **The human is the transport layer.** Text leaves through the clipboard, and results come back only when the user pastes them in again.

Most of the alternatives below swap out one of these four choices. Swapping one changes what happens downstream, so section 4 combines them.

---

## 2. Where the current design works against its own goals

These findings matter because they are second-order effects: each part is reasonable by itself, but connected together they produce outcomes the README says it does not want.

**F1. The quality gate rewards made-up numbers *(reproduced)*.** I took one honest four-paragraph post (full text in the appendix) and made three versions of it. The first used words ("most of a week", "an afternoon"). The second swapped those for the repo's own `{{your number}}` placeholders. The third had invented figures (5 hours, 20 minutes, "for 14 clients at Northwind").

| version | SPECIFICITY | HUMAN SCORE |
|---|---|---|
| honest words | 0.0 | 41.9 FLAGGED |
| `{{your number}}` placeholders | 0.0 | 42.5 FLAGGED |
| invented numbers and names | 100.0 | 75.1 REVIEW |

None of the three texts contains anything `humanize.py` changes, so raw and cleaned scores are the same. The other four checks are almost identical across the three versions, so SPECIFICITY alone is worth about 33 points here. `/li-human` tells the model: "If the verdict is not PASS, fix the weakest check named in the output and go again." For the honest and placeholder versions the weakest check is SPECIFICITY, and `detect.py` prints "Weakest signal: SPECIFICITY. Fix that first." The loop as written therefore pushes the model toward the one thing the README forbids ("Nothing here fabricates"), and the placeholder that is supposed to make honesty safe scores as badly as vague prose. The skill's own example comment hits the same wall: its weakest check is also SPECIFICITY (36.4).

**F2. Most short outputs can never PASS *(reproduced)*.** `detect.py` returns a flat 50 for BURSTINESS when a text has fewer than four sentences of three or more words. It also returns 50 for SPECIFICITY and VOICE when a text has fewer than 25 words. PASS needs every check at 55 or above, so PASS is mathematically impossible for those texts. That covers a 2-3 sentence comment, a 200-character invite note, a 3-8 word support reply and most DMs, yet `li-comment`, `li-dm`, `li-reply` and `li-inbox` all send their output through `li-human`. The skill's own example comment ("We tried the no-resume version of this for 3 hires...") scores **54.9 REVIEW**.

**F3. Two of the five checks only measure whether the cleaner ran.** SLOP DENSITY counts entries from `slop.json`, and `humanize.py` replaces every entry in `slop.json`. FINGERPRINT counts invisible characters, dashes and curly quotes, and `humanize.py` strips all of them. After cleaning, both checks are 100 by construction for anything outside a link *(reproduced: a deliberately bad corporate paragraph went to 100/100 on both and still scored 33.1 FLAGGED)*. Inside a link the opposite happens, and it is a hole in the artefact defence: `humanize()` calls `protect_urls` before `pass_invisible`, and `URL_RE` is `https?://\S+`, where `\S` also matches zero-width and tag characters. So a zero-width space plus a tag-character message glued to the end of a URL is stashed with the URL and restored untouched, and slop words in a URL path are never replaced but are still counted by `check_slop`. *(Reproduced: `Full write-up here: https://example.com/post` + U+200B + "written by gpt" in tag characters + ` and it took us ages.` keeps all 15 format characters after cleaning and scores FINGERPRINT 0.0, 30.0 FLAGGED; `Full guide: https://example.com/leverage-robust-synergy and we use it every week now.` scores SLOP DENSITY 0.0, 30.0 FLAGGED after cleaning.)* Step 4 then says to fix the weakest check, which no rewrite of the prose can do, so the loop never reaches PASS and the hidden payload ships unless someone reads the code points. 2c fixes both. Step 3 of `li-human` compares the raw draft with the cleaned one, so part of the "+44.9" before/after delta in the README is the tool marking its own work. F6 below is one more source of that inflation.

**F4. The context-free lexicon breaks meaning *(reproduced)*.**

```
in:  The landscape painting hung in our foster home.   Unlock the door.   A vital sign was crucial.
out: The market painting hung in our build home.       Get the door.      A important sign was important.
in:  We cut the discovery call — it worked.
out: We cut the discovery call, it worked.        (em dash -> comma creates a comma splice)
```

**F5. The invisible-character pass damages legitimate text *(reproduced)*.** Deleting the zero-width joiner (U+200D) splits the "woman technologist" emoji (U+1F469 U+200D U+1F4BB) into two separate emoji, a woman and a laptop. Deleting tag characters turns the England flag (U+1F3F4 plus the tag spelling "gbeng" and CANCEL TAG) into a plain black flag. Deleting the zero-width non-joiner (U+200C) breaks correct spelling in Persian: in the word for "I want" (U+0645 U+06CC U+200C U+062E U+0648 U+0627 U+0647 U+0645) the prefix fuses onto the verb. Devanagari and other Indic scripts use U+200D and U+200C the same way, to choose a half-form or block a ligature. These are normal characters for people who write in those scripts or use those emoji.

**F6. Normal phone typing scores as machine text, when raw text is scored *(reproduced)*.** iOS turns on Smart Punctuation by default, and it types curly quotes and apostrophes. A 195-character, plainly human comment with five curly marks (input in the appendix) scores FINGERPRINT 0.0 and **35.7 FLAGGED** raw. The code comment calls these "Characters a phone keyboard does not produce". Phone keyboards do produce them. The curly apostrophes also hide the contractions from VOICE (65.0 raw, 100.0 cleaned). Scope: this does **not** affect the verdict the `li-human` loop acts on, because `humanize.py` straightens the quotes first (cleaned: FINGERPRINT 100.0, 65.1 REVIEW). It affects the two places where raw text is scored: the "before" side of step 3, where it makes the before/after delta larger (F3), and a user who pastes their own writing and asks "does this sound like AI?", one of `li-human`'s listed triggers, who is told their own phone typing looks machine-made.

**F7. The learning loop cannot learn at the scale it runs at.**
- `log.md` is written when the user says "yes" to a draft. That records approval, not publication. If the user edits the post before pasting it, the log holds the wrong text and the wrong first line, and `li-audit` matches posts by that first line.
- `li-audit` does tell the model to state confidence and to refuse findings from thin data ("With 30 posts you can see a pattern; with 6 you cannot"). The gap is narrower than that. It treats 30 posts as enough, and its method (top 5 vs bottom 5) has no test for whether a difference is real. Thirty posts spread over 21 hook formulas is about 1.4 posts per hook, before format and theme split them further. So the skill gives the right instruction but no way to tell a 30-post pattern from noise, and hook-level findings at that size will always be noise. Section 3, 8c, gives a test.
- Nothing records the outcome of comments, DMs or replies, so P4, P5, P11 and P12 never learn anything.

**F8. The no-fabrication rule lives in one skill, not in the system.** `{{your number}}` appears only in `li-post` and `voice.md`. `li-dm` forbids invented mutual connections but says nothing about numbers. `li-comment` recommends "Add a datum" and "The receipt", and `li-profile` asks for "outcome bullets with numbers", but neither says where the numbers come from. The `li-reply` example ("Cut a whole review round") contains a specific claim with no source. The README's promise covers the whole pack. The mechanism covers one skill.

**F9. Timed actions have no memory.** `li-dm` prescribes follow-ups at +4 and +10 days, and `li-reply` says the first hour decides reach. Nothing stores a due date or reminds anyone, so the timing advice depends on the user's memory, which is the thing that fails first.

**F10. Priors are presented as facts.** The `best_for` fields in `hooks.json` make comparative claims, for example "Highest comment rate of any formula", "Highest save rate of the 21" and "Pair with an image and reach roughly doubles". None has a source, and `li-audit` says the user's own account is "the only honest source". The pack does not apply to its own claims the evidence standard it applies to the user's posts.

**F11. The plan is write-only.** `li-plan/SKILL.md` says: "Write the plan to `~/.claude/linkedin/plan.md` so the other skills can read it." No other `SKILL.md` mentions `plan.md` (a search of the repo finds it only in `li-plan` and the README). `li-post` reads `voice.md`, `li-audit` reads `log.md`, and nothing reads the plan. So the post drafted on Tuesday does not know it was meant to be the week's "story" slot, the engagement list never reaches `li-comment`, and `li-audit` cannot compare what was planned with what was posted. Any alternative that treats the plan as an experiment (7b, plan C) first has to give it a reader: `li-post` reads today's slot, and `li-audit` reads the week's named variable.

---

## 3. Alternatives, problem by problem

For each problem: what the repo does, the alternatives, what each one fixes, and what it costs, including second-order effects.

### P1. A post that sounds like me

**Repo:** a hand-filled `voice.md` (or one inferred from three posts), 21 hook templates, and a model draft that is then humanized.

| Alternative | How it works | Fixes | Costs / second-order |
|---|---|---|---|
| **1a. Interview, don't draft** | The model asks 3-5 sharp questions (what happened, to whom, what it cost, what you'd tell a friend). The user answers by typing fast or by voice memo, and the model only cuts, orders and shapes the user's own sentences. | The words are the user's, so voice, specificity and fabrication risk mostly go away at the source. It also removes most of P2. | More user effort per post (5-10 minutes of talking). Quality is limited by how well the user talks. Weak for users who freeze when interviewed. |
| **1b. Corpus-grounded voice** | Replace the 3-post sample with the user's whole posting history. The LinkedIn data export includes their past posts (**verify** which file and fields your export has). Retrieve the 5 posts most similar to the new idea and use them as few-shot examples at draft time. | Voice comes from evidence, not self-description. People are poor at describing their own style, which is why `voice.md` asks for samples anyway. | Needs a back catalogue (useless for new accounts). Copies the user's bad habits as faithfully as their good ones. |
| **1c. Learn from edits** | Store each draft and the text the user actually published. Diff them. Words the user always deletes go into a personal ban list, and words they always add go into a personal phrase list. Update `voice.md` every N posts. | Closes a loop the repo leaves open. `voice.md` becomes a measured profile, not a static form. | Needs the published text back (see P13/P8). Diffs are noisy when the user also changes content. Only count repeated edits. |
| **1d. Hooks mined from the user's winners** | Pull the first lines of the user's top-decile posts from `/li-audit` and turn them into templates. Fall back to the 21 generic formulas only when the account has no history. | Replaces generic priors with account evidence (F10). | Needs ~30+ posts and a working P8. Risk of overfitting to two lucky posts. Require repeats before promoting a pattern. |
| **1e. Constrain at generation, not after** | Put the banned list, the user's ban list and the style rules into the drafting prompt, with corpus examples. Use the regex only as a final detector. | Most fingerprints never appear, so the lossy repair step in F4 is rarely needed. | Prompt constraints leak, so a detector is still needed. It is just no longer the main fix. |

### P2. Don't read as machine-written

**Repo:** regex replacement of 113 terms, 11 typographic substitutions and 17 invisible-character classes, then a five-check score and a loop until PASS.

First, decide what this problem actually is. There are three different goals inside it, and each needs a different design:

- **(i) The reader's judgement.** Does the post sound like a person the reader would trust? This is what costs reach and credibility.
- **(ii) Hidden artefacts.** Invisible characters really do survive copy-paste. This is a real problem, it is checkable, and the repo is right to handle it, though it misses characters glued to a link (F3).
- **(iii) Detector evasion.** Avoiding a verdict from GPTZero and similar tools. The README correctly declines to promise this.

| Alternative | How it works | Fixes | Costs / second-order |
|---|---|---|---|
| **2a. Flag, then rewrite with context** | Keep the lexicon and regexes as detectors only. No code change is needed; replace step 1 of `li-human`'s "Order of operations" with two calls to the existing script. (1) `humanize.py draft.txt --report -o /dev/null` runs the full lexicon but throws its text away; its "3. SLOP LEXICON" section is the list of flagged terms (e.g. `1x  leverage  -> use`). (2) `humanize.py draft.txt --lexicon artefacts-only.json -o clean.txt` (the 4d file) removes invisible characters and fixes typography without touching words. The model then rewrites, in `clean.txt`, each sentence containing a flagged term, with the instruction "rewrite this sentence without X, keep the meaning, keep the voice", shows the user a diff, and re-runs both calls until (1) lists nothing it should act on. `detect.py` keeps scoring with the full `slop.json`. | F4 (market painting, "A important", comma splices). Also half of F3: SLOP DENSITY stops being 100 by construction and measures the rewritten draft again. *(Checked: the 3-sentence stock paragraph "In today's landscape, we leverage robust synergies to unlock value. Our holistic approach empowers teams to navigate complexity. It is crucial to foster a culture of seamless innovation." scores **97.4 PASS** on the patched gate after full-lexicon substitution, because the swapped words no longer count and BURSTINESS is `N/A`. Cleaned the 2a way it scores SLOP DENSITY 0.0, 39.1 FLAGGED, until the sentences are actually rewritten.)* | One more model call per flagged sentence. Results are not deterministic, so show a diff. Second-order: the gate gets harder to pass, because SLOP DENSITY is now real. If you calibrate (2e), pass `artefacts-only.json` to `calibrate.py` so the cut-offs are measured on texts cleaned the same way; the calibration then rests on BURSTINESS, SLOP DENSITY and VOICE, with only FINGERPRINT fixed at 100. |
| **2b. Personal allowlist from the corpus** | Any lexicon word that appears in the user's own pre-AI posts is exempt for that user. If they have always said "landscape", it stays. | False positives that strip a real voice. `SKILL.md` already says to edit `slop.json` by hand, and this automates that. | Needs the corpus (1b). Users whose old posts were already AI-assisted carry the slop forward. |
| **2c. Script-aware invisible pass** *(fix)* | Both scripts treat every format character (Unicode category Cf) as an artefact. `humanize.py` deletes them in a per-entry loop *and* again in a catch-all at the end of `pass_invisible`. `detect.py` `check_fingerprint` counts every Cf character at weight 4. A shared helper, `joiners.py` (appendix), finds the legitimate ones by position: U+200D with a visible emoji on both sides (emoji blocks only: U+1F000-U+1FAFF, U+2600-U+27BF, U+2B00-U+2BFF; the emoji before it may carry one VS16, as in the rainbow flag, but a VS16 never counts as an emoji by itself, and tag, private-use and supplementary variation-selector characters never count); U+200C or U+200D between two letters of a script whose spelling uses them (the Arabic-script blocks, used for Persian, Urdu and Kurdish, and Devanagari through Sinhala); and the three subdivision flags in Unicode's recommended set (England, Scotland, Wales), matched exactly. `humanize.py` then runs `pass_invisible` only on the stretches of text *between* those positions and copies the legitimate characters across untouched (`joiners.clean_around`). No stand-in characters are used, so nothing already in the input can be turned into a format character. Two more changes close holes the original has. The invisible pass now runs *before* `protect_urls`, so characters glued to a link are removed (F3). And a variation selector (U+FE00-U+FE0F, U+E0100-U+E01EF) is deleted when it modifies nothing: after whitespace, at the start, after another selector, or after an ASCII character that is not a keycap base (0-9, #, *). These are not format characters, so neither original script sees them, and a run of them after a plain word is an invisible payload of any length. `detect.py` counts the Cf characters the helper does not keep plus those stray selectors, and leaves links out of SLOP DENSITY, because the cleaner never rewrites inside a link. | F5. *(Checked: the woman-technologist emoji, the England flag, the Persian word and a Devanagari half-form survive cleaning. A zero-width space, two stray tag characters, a non-recommended "usca" flag sequence, a 28-character tag message behind a black flag, and U+200C between Chinese characters are all still removed. So are ZWJs placed between tag characters or between private-use characters: `Great post` + four tags joined by three ZWJs + `. Thanks` + U+F0001 U+200D U+F0002 comes out with no ZWJ and FINGERPRINT 100.0, "0 invisible". So is the payload that an earlier version of this helper let through, `Great post` + (U+FE0F U+200D) x 12 + U+FE0F + ` thanks for sharing.`: that version counted VS16 as an emoji, kept all 12 ZWJs and reported "0 invisible", 100.0 PASS, where the original cleaner deleted the ZWJs. Now all 12 ZWJs and all 13 selectors are removed, and the raw text counts 25 invisible. A link with U+200B and a 14-character tag message glued to it comes out clean, where the original kept all 15. Private-use characters in the input, such as U+F0049 and U+F8F1, come out exactly as they went in, as they do with the original script.)* In the `li-human` loop the verdict does **not** change: the original cleaner already deleted the joiner before scoring, so the emoji comment scored 62.0 REVIEW after cleaning both before and after the patch. What changes is that the emoji survives. The `detect.py` half matters only where raw text is scored (see F6). | Two lines changed in `humanize.py` (the call, and its move ahead of `protect_urls`), three in `detect.py`, plus the 81-line helper. Ceiling: U+200D between *any* two visible emoji, and U+200C/U+200D between *any* two letters of the listed scripts, is kept whether or not that spelling is correct, so text in those scripts can still carry one hidden bit per gap, and each bit needs a visible emoji or letter on both sides. Likewise one selector after a digit, a non-ASCII symbol or a CJK character is kept, so one bit can ride on each of those characters; runs of selectors are always removed. If that channel matters for your users, the upgrade is a per-language list of allowed joiner positions. Non-recommended subdivision flags (e.g. California) are reduced to a plain black flag. Emoji detection uses three block ranges, not the full Unicode emoji data, so a ZWJ next to a rare emoji outside them (e.g. U+203C) is deleted, which breaks that sequence but never hides a character. |
| **2d. Score against *your* writing, not a generic panel** | Replace the absolute 0-100 with "how much does this draft look like you?". Steps: (1) collect 20+ posts you wrote before using AI; (2) take the 100 most common words across them (mostly function words: the, I, but, so); (3) for each word, compute its rate per post and z-score it across your posts; (4) a text's distance to one post is the mean absolute z-difference over the 100 words (Burrows' Delta); (5) for each of your posts, compute its mean distance to all your other posts, which gives your normal range; (6) compute the draft's mean distance to all your posts and report its percentile in that range, e.g. "less like you than 90% of your own posts". *(Procedure only, not tested here.)* | F3 (the score no longer measures whether the cleaner ran), and goal (i) more directly. | Needs 20+ posts. Function-word counts on a 150-word post are noisy, so report the percentile as a hint, never a gate. |
| **2e. Calibrate the existing panel** *(fix)* | Apply the `detect.py` diff from 2f first: it adds `N/A` for short text and the `gate_scores()` function this step uses. Then: (1) put 20+ posts you wrote before using AI into `mine/`, one `.txt` each; (2) put 20+ drafts into `model/`, made by running `/li-post` on the same topics as your posts and saving them before your edits; (3) run `calibrate.py` (appendix). It runs **both** sets through `humanize.py` first, because the verdict is taken on cleaned text. *(Checked on a toy set: cleaning raised stock corporate paragraphs from about 13 to about 30, so scoring raw drafts would overstate what the gate catches.)* It scores each text with `detect.run` and takes the floor from `detect.gate_scores`, so it tunes whatever rule is installed, not a copy of it. On an unpatched `detect.py` it stops with an `AttributeError` instead of quietly tuning the old rule. It searches every pair of values for the two cut-offs `PASS_OVERALL` (T) and `PASS_FLOOR` (C), applies `overall >= T and min(gated scores) >= C` to every text, keeps the pairs that flag at most 10% of your posts, and from those picks the one that flags the most model drafts. It prints both rates for that joint rule, and the two numbers to put in `PASS_OVERALL, PASS_FLOOR = 70, 55`. If the rule flags fewer than about 60% of model drafts, the panel cannot tell you apart from the model, so use it as a hint and not a gate. With the default cleaning, SLOP DENSITY and FINGERPRINT are near 100 for both sets (F3), so the calibration rests on BURSTINESS and VOICE. If you use 2a, add `artefacts-only.json` as the last argument; then SLOP DENSITY is measured too. | F2: 70/55 become numbers measured on your writing, with the error rates of the rule you actually install. | About an hour, once. Thresholds are per user. A 10% rate measured on 20 posts is a rough figure: on new posts expect it to run higher. With no posting history, keep 70/55 but still apply the 2f diff. |
| **2f. Remove the incentive to invent, and stop scoring the unscorable** *(fix)* | One diff to `detect.py`, given in full in the appendix, plus a rule in `li-human/SKILL.md`. (1) A `GATED` list holds every check except SPECIFICITY, and `gate_scores()` returns the gated scores. `overall` (both its mean and its `min` term), the floor in the PASS line and the "Weakest signal" line all use only those. SPECIFICITY is still printed, as advice. (2) The three "too short to judge" returns give `None` instead of 50. `gate_scores()` leaves `None` out, the panel prints `N/A`, and `--json` prints `null`. The exception is VOICE: under 25 words it still counts the structural tells in `slop.json` (rocket emoji, reflex engagement bait and the rest) and scores `100 - 22 x tells`, returning `None` only when there are none. Those tells are exactly what `li-human/SKILL.md` lists under "What does NOT get fixed automatically", so short text must not hide them. (3) When SPECIFICITY is under 55, the panel prints "ask the user for a real number or example. Never invent one." (4) `{{...}}` placeholders stay uncounted as concrete markers (they are uncounted today; if they counted, a draft could pass by scattering blanks through empty text). (5) In `SKILL.md`, step 4 gets a second required condition before the copy-ready block: `provenance.py` (3b) prints OK, so any number added during the loop fails unless it is sourced. Sourced means in the ledger, or in a context file for this one draft: the post being commented on (`li-comment`), the comment or message being answered (`li-reply`, `li-inbox`), the user's notes on the person (`li-dm`), the transcript (`li-repurpose`), or a line holding numbers the user confirmed in chat when the model asked "is 15 yours?". Only the user's own message counts as that confirmation. | F1, the most dangerous interaction in the pack. *(Checked: the three F1 versions now score 72.2 honest, 74.9 placeholders, 73.6 invented. The gap between honest and invented falls from 33.2 points to 1.4. None of the three PASSes; all are REVIEW, because BURSTINESS is 49.5, 54.3 and 52.0, under the floor of 55. The weakest signal named is now BURSTINESS, which the model can fix by rewriting, not by inventing.)* Also F2: the skill's example comment now scores 70.0 REVIEW instead of a capped 54.9, with VOICE (50.0) named as the weakest check. *(Checked: short text with tells still fails: `This is huge` + two rocket emoji + ` Who else is seeing this? Agree?` scores VOICE 34.0 (3 tells), 60.4 REVIEW, weakest VOICE; an earlier version of this diff that returned `N/A` for VOICE outright gave it 100.0 PASS, where the original gives 62.0 REVIEW.)* | About 40 changed lines in `detect.py`. Second-order effect of (2): a short text with no stock words and no structural tells, whose only scored checks are SLOP DENSITY and FINGERPRINT, will PASS once cleaned, because both are 100 after cleaning (F3). That PASS means "no artefacts, no stock words, no listed tells", nothing more, and the panel says so ("Too short to judge style: N/A checks are left out of the verdict. VOICE still counts structural tells."). A tell the lexicon does not list is not seen; the user's read covers it. That is the honest answer for a 200-character note. 4d goes further and drops the score for short text. |
| **2g. Human read test** | Before posting, show the draft to one trusted peer, or read it aloud. The model's job is to produce the 3 lines most likely to sound machine-written, so the human checks those first. | Goal (i), measured by the only judge that matters. | Slow, and needs a willing peer. Fine for high-stakes posts, too heavy for comments. |
| **2h. Disclose instead of disguise** | Say plainly that you draft with AI and edit by hand. Then the work becomes making the post good, not making it look unassisted. | Makes goal (iii) irrelevant. Removes the ethical grey zone around "humanizing". | It is a positioning choice. Some audiences will discount the post. The user decides, not the tool. |

### P3. Never put a false claim under my name

**Repo:** a rule in `li-post` and a placeholder convention. Other skills do not have the rule (F8).

| Alternative | How it works | Fixes | Costs |
|---|---|---|---|
| **3a. A proof ledger every skill cites** | Promote "Proof I can use" from `voice.md` into `proof.md`, one fact per line with a date. Every skill may only use numbers and names that appear there, and anything else becomes `{{...}}`. | F8. One rule in one place. | Users have to keep the ledger up to date. |
| **3b. Mechanical provenance check** | A script fails the draft if any number or magnitude claim in it is not in the ledger and not a placeholder. That covers digits with their scale (`$12k`, `1.5M`, `3 million`, `$5m`), number words, "a hundred" or "a thousand", and vague magnitudes a model likes to invent ("thousands", "dozens", "doubled", "tripled", "halved", "twice", "threefold"). A tested 97-line version is in the appendix. Usage: `provenance.py draft.txt proof.md [context.txt ...]`; the optional context files source numbers for this one draft only (see 2f (5)). It treats `$12,000`, `$12k` and `twelve thousand` as the same value and `$12M` as a different one, and `40%`, `40 percent` and `forty percent` as the same value. It ignores the ledger's line dates, clock times ("3pm", "9:30"), links and e-mail addresses, hashtags and @mentions that contain a letter (`#100DaysOfCode`, but not `#1`), calendar dates written with a weekday or month name ("Tuesday the 14th", "March 3rd", "14 May", "the 2nd of June"), digits glued to a letter (B2B, Q3, H1), a short idiom list ("24/7", "2 cents", "double down") and list markers, but only in a real list: lines numbered 1, 2, ... in sequence with text after the marker. A lone "47." or "2019. The year I quit." opening a post is checked like any other number. It reads "five and six" as two numbers but "two hundred and fifty" as one. Bare "double", "half" and words ending in "-fold" are not flagged, because "double down", "the second half" and "scaffold" are ordinary honest English. Run it in the same place `li-human` runs. | F1 and F8 enforced by code, not by asking the model nicely. | Matches a value, not its meaning: a "5" in the ledger allows any "5". It does not check "one", "half", names, comparatives ("most", "far more"), or any number inside a link or hashtag. A year that is not in the ledger fails. When an honest number fails, it goes to one of three places, never more than one: a fact the user will reuse goes in the ledger; a number from the text being answered, or one the user just confirmed, goes in that draft's context file; a phrase that makes no claim ("I thought twice") goes in the idiom list. Never put "double" or "half" in the ledger to silence a false fail: it would let "we doubled revenue" through. The appendix lists the gaps found in testing. |
| **3c. Claim-level source tags** | The draft is returned with each factual sentence annotated, e.g. `[proof.md:3]` or `[you said this in chat]`, then the tags are stripped for the copy-ready block. | Lets the user audit claims in seconds. | Clutters the review view. Only worth it for posts, profile and DMs. |

### P4. Be visible on other people's posts (`/li-comment`)

**Repo:** nine comment types, two options with different types, the user pastes the post text.

| Alternative | How it works | Fixes / costs |
|---|---|---|
| **4a. Gut-reaction first** | The user types a one-line reaction ("this is wrong because we tried it") and the model sharpens it. The comment type follows from what the user actually thinks. | The facts and the opinion are the user's (P3). The datum and receipt types become honest by construction. Costs ten seconds per post. |
| **4b. Experience bank** | Give `proof.md` a short "stories and receipts" section. The model matches the post's topic against it and proposes a receipt only when one exists. Otherwise it picks a question or extension type. | Prevents invented "We saw the same thing: 40%..." comments. |
| **4c. Target list over volume** | Feed `li-plan`'s 10-person list into a structured engagement ledger (who, date, comment type, did they reply). Choose whom to comment on each day from that ledger. | Makes the skill's own "commenting on the same three people" warning checkable. Also gives P8 outcome data for comments. |
| **4d. Shorter scoring rules for short text** | Clean comments, DMs and replies for artefacts only, and skip `detect.py` scoring (see F2). `humanize.py` has no artefact-only flag, but it does take `--lexicon`, so a copy of `slop.json` with empty `words` and `phrases` lists does it today with no code change (appendix). *(Checked: "A vital sign was crucial" stays as written, and the zero-width space is still removed.)* | Removes a gate the output can never pass, and stops F4's word swaps in short text. The typographic pass still turns an em dash into a comma, so the comma-splice part of F4 remains. |

### P5. The thread under my own post (`/li-reply`)

**Repo:** paste comments, sort into five buckets, draft in priority order.

| Alternative | How it works | Fixes / costs |
|---|---|---|
| **5a. Pre-bake answers at posting time** | When a post is approved, also draft the 3-5 most likely questions or objections and answers to them. The user has them ready during the first hour. | The skill itself says the first hour matters most. This moves the work to before that window, where it costs nothing. The cost is that some prepared answers go unused. |
| **5b. Reply skeletons, user fills** | Only for LEAD and SUBSTANCE comments: give a 1-line structure ("concede X, hold Y, offer the template") and let the user write the words. | Replies are where people interact one-to-one, so the user's own voice matters most there. Slower. |
| **5c. Batch at fixed times** | Two fixed check-ins (e.g. +30 min and +3 h after posting) instead of continuous attention. | Less stress, predictable workload. Slightly worse response time than always-on. |

### P6. A profile that converts (`/li-profile`)

**Repo:** a 100-point rubric (12 items) scored by the model, then rewrites ordered by points lost.

| Alternative | How it works | Fixes / costs |
|---|---|---|
| **6a. Binary checklist instead of graded points** | Turn each rubric item into yes/no checks (e.g. "headline is not the job title", "the first 2 lines name a reader problem", "featured has 3 items"). | A graded LLM score varies from run to run, so the before/after delta can be noise. Binary checks repeat reliably. Less nuance. |
| **6b. Five-second test** | Show the headline and first two lines of the About section to 3 people outside your field and ask "what does this person do, for whom?" Score the match with what you intended. | Measures the actual job ("should I message this person") directly. Needs 3 people. |
| **6c. Outcome tracking** | Record the weekly profile-view count and inbound DMs or connection requests for 4 weeks before and after the rewrite (data the user can see on their dashboard). | Shows whether the rewrite worked, not whether it scores well. Small numbers mean wide error, so report the range. |
| **6d. Exemplar benchmark** | The user names 5 profiles of people who already get the clients or jobs they want. The skill extracts what those profiles have in common and compares. | Relevant to the user's niche, unlike a generic rubric. Risk of copying. Extract the structure, not the wording. |

### P7. What to post, when, and who to engage with (`/li-plan`)

**Repo:** a weekly plan built from four generic slot types, fixed time windows, and a 5/3/2 engagement list, written to `plan.md`.

| Alternative | How it works | Fixes / costs |
|---|---|---|
| **7a. Capture backlog, then plan** | Ideas are captured during the week as they happen (one line each into `ideas.md`, a phone note or a voice memo). The weekly plan picks from the backlog instead of asking "what happened this week?" on planning day. | Planning-day recall is poor. Raw material ("a client call, a number, a mistake") is lost by Friday. Needs a capture habit. |
| **7b. Plan as experiment** | Each week tests one variable (e.g. story vs teach format) with everything else held as fixed as practical, and records which variable it was in the log. | Turns the plan into the input P8 needs (F7). Without a deliberate design, 30 posts confound everything. Slower to explore. |
| **7c. Priors replaced by the user's numbers** | Treat the fixed windows (Tue-Thu 7:30-9:30am), the 4-a-week cadence and the post-type mix as defaults, and replace each one as soon as `li-audit` has enough data for that user. | Solves F10 at the plan level. |
| **7d. Cadence matched to capacity** | Ask how many hours a week the user really has, and size the plan to fit (1 post plus 15 minutes a day of comments is a valid plan). | Plans that do not fit get abandoned, and consistency matters more than volume. |

### P8. Learn what works (`/li-audit`)

**Repo:** paste analytics, compute engagement rate, comment ratio and reach multiple, compare top 5 with bottom 5, and pass the conclusions to `/li-plan`.

| Alternative | How it works | Fixes / costs |
|---|---|---|
| **8a. Structured event log** | Replace free-text `log.md` with `events.csv`, one row per action: `date, kind, id/url, first_line, hook, format, theme, published_text, impressions, reactions, comments, reposts`. The row is completed in two steps: when the user pastes the post URL (which is when it is actually published), and 7 days later when they copy the four counts from the post's analytics as plain whole numbers. | F7: logging on approval, the first-line join and edited text. It also gives 8c its input directly. Costs one paste per post plus one at day 7. |
| **8b. Join on the published text, from the account archive** | The repo already asks first for the post-analytics CSV (Analytics -> Content -> Export), with screenshots as the fallback, and joins it to `log.md` by first line. The alternative is the join key and the history. Request the full account archive (Settings -> Data privacy -> Get a copy of your data; **verify** that it includes your posts' text and timestamps). Match each analytics row to the archived post by publish date, then by text, so the audit keys on what was actually published, not on the approved draft in `log.md`. It also brings in every post written before the pack was installed, which `log.md` never saw. | F7's edited-text and first-line problems without the user pasting anything per post, plus a back catalogue for 1b, 1d, 2b and 2d. The archive takes time to arrive and is a snapshot, so it suits a monthly audit, not a weekly one. The hook and format labels still have to come from the log (8a) or be tagged once by hand. |
| **8c. A test behind the confidence statement** | The skill already asks the model to say how confident it is. This gives it a way to measure that. Compare one factor at a time (e.g. story vs everything else) on one metric, engagement rate (reactions + comments + reposts over impressions). If either group has fewer than 5 posts, the answer is "not enough data", which in practice means always for individual hooks. Otherwise report each group's median and range, then shuffle the labels 10,000 times and count how often a shuffled split gives a median gap at least as large as the real one (a permutation test). Testing many factors in one audit manufactures findings: with 14 tests on pure noise, the chance that at least one falls under 5% is 1 - 0.95^14, about 51%. So either name **one** comparison before the audit (in plan C it is the week's chosen variable), or count every comparison you will look at, K, and require p under 0.05/K (Bonferroni, which keeps the chance of any false finding at or below 5%). Under the bar: unlikely to be noise, worth acting on. Above the bar but under 20%: suggestive, test again on new posts. Above 20%: no evidence. `compare.py` in the appendix reads `events.csv` (8a) directly, computes the rate from the counts, and takes `--tests K`. | Turns "say how confident it is" into a number that stays honest when many things are compared. Fewer and duller conclusions, which is correct. |
| **8d. Track leading indicators, not only engagement** | Add the outcomes the user actually wants: DMs from posts, profile views, calls booked. | Engagement rate is a proxy. A post with low engagement that brought one buyer was a success. |

### P9. Document posts (`/li-carousel`)

**Repo:** slide copy rules, then hand-written HTML with one `<section>` per slide, printed to PDF in headless Chrome.

| Alternative | How it works | Fixes / costs |
|---|---|---|
| **9a. Markdown-to-PDF slide tool** | Write the slides as Markdown and render them with Marp (a custom theme with a 1080x1350 size) or with Typst. | Re-renders reliably with no hand-written HTML each time. One tool to install. |
| **9b. One reusable template** | Build a single parameterised HTML template once (brand colour, handle, slide numbering), then feed it slide JSON. | Every deck looks consistent. Removes "design" from the per-deck work. |
| **9c. A design tool the user already has** | Export the copy as structured text to paste into Canva or Google Slides templates. | Uses tools non-technical users already know. More manual. |
| **9d. Is it a carousel at all?** | Keep the repo's sequence test. Also offer a single image of the recap slide plus a text post as a lighter format. | Not every list idea is worth 10 slides. |

### P10. Never run out of material (`/li-repurpose`)

**Repo:** extract claims, numbers, stories, mechanisms, mistakes and lines from one long asset, then a week of standalone posts drafted one at a time.

| Alternative | How it works | Fixes / costs |
|---|---|---|
| **10a. Extracts into the backlog, not a week** | Extracts go into `ideas.md` (7a), tagged with source and timestamp, and the plan draws from the whole backlog. | One video does not take over a week. Material from different sources mixes. |
| **10b. Clip-first** | For video or audio, return timestamps of the 3 best 30-60 s segments to cut as native video clips, alongside the text posts. | Uses the asset in its strongest form. Needs editing effort. |
| **10c. Source-quote check** | Each post records the exact source sentence it came from, and the provenance check (3b) runs with the source transcript as its context file (`provenance.py draft.txt proof.md transcript.txt`). | Repurposed posts often drift from what was actually said. |

### P11. Outbound DMs (`/li-dm`)

**Repo:** an invite note of 200 characters or fewer, a first message, two follow-ups at +4 and +10 days, all sent by hand.

| Alternative | How it works | Fixes / costs |
|---|---|---|
| **11a. Follow-up ledger with due dates** | `outreach.csv` with one row per person: date invited, accepted, msg1 sent, due +4, due +10, replied. `/li-plan` and `/li-inbox` read it and list "due today". | F9. No automation of sending, only of remembering. One more file. |
| **11b. Calendar export** | Write an `.ics` file with the two follow-up reminders per contact. | Reminders arrive in the user's existing calendar. A one-way export, so it cannot know who replied. |
| **11c. Warm before write** | Gate DMs on the person being on the engagement list for 2+ weeks with 2+ substantive comments recorded in the ledger (4c). | Makes the skill's own "comment for weeks before any DM" checkable. Slower pipeline. |

### P12. Inbound triage (`/li-inbox`)

**Repo:** paste or screenshot messages, sort into LEAD / RECRUITER / PEER / ASK / SPAM, flag automated sequences, draft replies.

| Alternative | How it works | Fixes / costs |
|---|---|---|
| **12a. Export-based triage** | Run triage over the messages file in the user's own data export (**verify** it is included). | Handles 50+ threads without screenshots. Not real-time, so best as a weekly sweep. |
| **12b. Personal rules file** | Keep `inbox-rules.md` (senders, phrases and patterns the user has marked as spam or lead) and apply it before the model does. | Gets more consistent each week. The user's corrections stick. |
| **12c. Templates for the repeat cases** | Most replies are recruiter-decline, pick-your-brain decline and referral. Keep 3-5 approved replies in the user's voice and fill them in. | Faster, and voice stays stable. Less tailored. |

### P13. Getting text onto LinkedIn without risk

**Repo:** never post. The user copies and pastes everything. The README says there is no official personal-posting API without an approved partner app, and that browser automation violates the User Agreement.

| Alternative | How it works | Fixes / costs |
|---|---|---|
| **13a. Native scheduling** | The copy-ready block includes the planned time, and the user schedules it in LinkedIn's own composer (**verify** scheduling is available on your account and platform). | The plan's times get used without anyone needing to be online at 8:15am. Still manual. Fully within the rules. |
| **13b. Own-account API posting** | LinkedIn documents a "Share on LinkedIn" product (`w_member_social`) for posting as the authenticated member through your own developer app (**verify** current availability and terms before relying on it. I have not checked today's docs, and the README's claim conflicts with my understanding). If it is available, a human-approved "post now" button can call it. | Removes the paste step and returns the post URN for the log (8a). Adds OAuth tokens and secrets to manage. Approval must stay a real, per-post decision. Reading comments and analytics through the API is generally restricted, so P5 and P8 stay manual. |
| **13c. Paste-back receipt** | Keep manual posting, but ask the user to paste the post URL after publishing, which completes the log row (8a). | Closes the F7 loop at the cost of one paste. The cheapest of the three. |

---

## 4. Whole-system alternatives

Swapping one part at a time leaves the coupling problems (F1, F3, F7) in place. Here are three coherent redesigns. They differ in which of the four load-bearing choices from section 1 they replace.

### A. Ledger-centred (replaces "the human is the transport layer")

Two files sit at the centre of everything:

- `proof.md`: facts the user has approved, which every skill cites (3a, 3b).
- `events.csv`: one row per post, comment, DM, reply or inbox action, with the columns in 8a plus outcome fields for the non-post kinds, such as "replied" (4c, 11a).

Every skill reads both files and appends to `events.csv`. `li-plan` lists what is due today (follow-ups, engagement targets, posts). `li-audit` works on clean, joined data.

- **First-order:** F7, F8 and F9 are fixed.
- **Second-order:** the edit diff (1c) and the personal allowlist (2b) become possible, because the published text is stored.
- **Third-order:** after about 3 months, the generic priors (F10) can be replaced by the user's own numbers (1d, 7c).
- **Cost:** one paste per published item, and discipline about keeping the ledger current.

### B. Interview-first (replaces "generate, then clean")

The model's job changes from writer to interviewer and editor (1a, 4a, 5b). The user speaks or types raw material, and the model structures it.

- **First-order:** voice and fabrication problems mostly disappear because the sentences are the user's.
- **Second-order:** `li-human` shrinks to the artefact pass (2c) plus a light flag pass (2a), and F1, F3 and F4 mostly stop mattering.
- **Third-order:** the detector argument goes away, because the text really is human-written with editing.
- **Cost:** more user minutes per post. It works best for people who think out loud.

### C. Experiment loop (replaces "generic priors as fixed rules")

Combine 7b, 8b, 8c and 1d. First give `plan.md` readers (F11): `li-post` reads the day's slot and writes it into the log row, and `li-audit` reads the week's named variable. Each week's plan names one variable in advance, the audit tests that one variable (or applies the 0.05/K bar if it looks at more), and the plan updates only on evidence.

- **First-order:** F10 is fixed. The pack's claims become the user's measured claims.
- **Second-order:** the user stops tuning things that do not matter. `li-audit` already says posting time "is almost never the cause", and `li-plan` says the day and hour matter far less than the first line. This would let the user check that for their own account.
- **Cost:** slow, because posting at 4 a week gives about one usable comparison a month. It needs patience and enough posts.

The three combine well. A gives C its data, and B lowers the stakes on P2 so A and C can run without the humanizer being a gate. A sensible order is **A → B → C**.

### If you have no posting history yet

Many of the alternatives above (1b, 1d, 2b, 2d, 2e calibration, 7c, 8c, plan C) need past posts. A new account cannot use them yet. These work from day one:

- **Writing:** 1a (interview), 1e (constraints in the prompt), 4a (gut reaction first).
- **Cleaning:** 2a (flag and rewrite), 2c (script-aware invisible pass), 2f (no reward for invention, `N/A` for short text), and 4d (artefact-only lexicon).
- **Honesty:** 3a and 3b. The ledger starts with whatever true facts the user has today.
- **Logging:** 8a and 13c from the first post. This is what makes the history-based alternatives possible later.
- **Planning and outreach:** 7a, 7d, 11a.

Plan A gives the history-based alternatives their data. Plan C becomes possible after about 20-30 logged posts.

---

## 5. If you only do five things

In order of value for effort:

1. **Close the fabrication loop (F1).** Apply the `detect.py` diff from 2f (about 40 changed lines) and make `provenance.py` from 3b (97 lines) a required pass before the copy-ready block, with the pasted source text as a context file for comments, replies, DMs and inbox answers. It removes the score's reward for invention and catches unsourced numbers and the common magnitude words. It does not catch every vague claim ("most", "far more", "half the team"), so the user's read still matters.
2. **Stop gating short text on a score it cannot reach (F2).** The same diff returns `N/A` for texts too short to judge. Short text is still checked for stock words, artefacts and the structural tells the lexicon lists (VOICE keeps scoring those). Optionally also clean comments, DMs and replies with the artefact-only lexicon (4d), which needs no code change.
3. **Replace blind word substitution with flag-and-rewrite, and stop deleting real characters (F4, F5).** Apply 2a (two calls to the existing `humanize.py`, no code), and 2c (`joiners.py` plus its two-line `humanize.py` patch; the `detect.py` lines are already part of the appendix diff). This also closes the link hole in F3.
4. **Log publication, not approval (F7).** Apply 8a and 13c: one paste of the URL per post.
5. **Add a follow-up ledger, and make the plan readable (F9, F11).** Apply 11a, and have `li-plan` list what is due today. In the same edit, have `li-post` and `li-audit` read `plan.md`, so the plan stops being write-only.

Order for the code: `joiners.py` first (the `detect.py` diff imports it), then the `humanize.py` line, then the `detect.py` diff, then `provenance.py`. `calibrate.py` (2e) comes last, once you have 20+ posts, because it reads the installed rule through `detect.gate_scores` and refuses to run without it.

Everything in section 4 builds on these five.

---

## Appendix: reproduction, patches and tested scripts

Commands, run from a scratch directory against the read-only copy of the repo (`S=.../source/skills/li-human`). Every test input that contains a special character is built with Python escapes, so the commands survive copy-paste through any cleaner.

```bash
# F4 / F5: lexicon and invisible-character damage
printf 'We cut the discovery call \xe2\x80\x94 it worked.\nThe landscape painting hung in our foster home.\nUnlock the door. I harness the horse.\nA vital sign was crucial.\n' > t1.txt
python3 -c "
eng = '\U0001F3F4' + ''.join(chr(0xE0000 + ord(c)) for c in 'gbeng') + '\U000E007F'
open('t5.txt', 'w').write('\U0001F469\u200d\U0001F4BB dev and ' + eng + ' fan. \u0645\u06cc\u200c\u062e\u0648\u0627\u0647\u0645\n')"
python3 $S/humanize.py t1.txt --report
python3 $S/humanize.py t5.txt | python3 -c "import sys; print([hex(ord(c)) for c in sys.stdin.read() if ord(c) > 127])"
#   -> no 0x200d, no tag characters, no 0x200c left

# F2: the skill's own example comment can't PASS (3 sentences -> BURSTINESS fixed at 50)
printf 'We tried the no-resume version of this for 3 hires last year. Two were the best hires we made. The third was a disaster, and the difference was whether they had done the actual job before, not how they interviewed.\n' > c1.txt
python3 $S/detect.py c1.txt            # BURSTINESS 50.0, SPECIFICITY 36.4, 54.9 REVIEW

# F6: phone-typed curly quotes and apostrophes only (195 characters, 5 curly marks)
python3 -c "open('phone.txt', 'w').write('I\u2019ve said this for years. \u201cJust ship it\u201d is easy to say when you\u2019re not the one on call. We tried it and lost two weekends. Now we ship on Tuesdays and nobody\u2019s phone rings on Saturday. Worth it.\n')"
python3 $S/detect.py phone.txt                             # raw: FINGERPRINT 0.0, 35.7 FLAGGED
python3 $S/humanize.py phone.txt | python3 $S/detect.py -  # cleaned: FINGERPRINT 100.0, 65.1 REVIEW

# F1: honest.txt below; the other two versions are derived from it
sed -e 's/most of a week/{{your number}} hours/; s/an afternoon, not a week/{{your number}} minutes/' honest.txt > ph.txt
sed -e 's/most of a week/5 hours/; s/Last spring/In March, for 14 clients at Northwind,/; s/an afternoon, not a week/20 minutes/' honest.txt > inv.txt
for f in honest ph inv; do python3 $S/detect.py $f.txt; done   # 41.9 FLAGGED / 42.5 FLAGGED / 75.1 REVIEW
```

`honest.txt`:

```
Our proposals used to take most of a week. I'd write them at night, after the kids were asleep, and I hated every page.
Last spring we tried something dumb. We wrote one template and stopped. Now a proposal takes an afternoon, not a week.
I didn't expect it to work. I'm still a bit annoyed it did, because I spent years doing it the slow way.
If you write proposals from scratch, try the template first. It's boring. That's the point.
```

### Artefact-only lexicon (4d)

```bash
python3 -c "import json; d=json.load(open('$S/slop.json')); d['words']=[]; d['phrases']=[]; json.dump(d, open('artefacts-only.json','w'), ensure_ascii=False)"
python3 $S/humanize.py comment.txt --lexicon artefacts-only.json
```

Checked on `A vital sign was crucial` + em dash + `we unlock the door.` plus a zero-width space: the default lexicon gives "A important sign was important, we get the door."; the artefact-only lexicon gives "A vital sign was crucial, we unlock the door." The invisible character is gone in both. The em dash still becomes a comma, because that is the typographic pass, not the lexicon.

### `joiners.py` and the `humanize.py` patch (2c)

Save as `skills/li-human/joiners.py`. Every special character in it is written as an escape (`"\u200d"`, not the character itself), so the file cannot be blanked by passing it through a cleaner on the way to disk.

```python
"""Format characters that belong to real text, shared by humanize.py and detect.py:
ZWJ inside an emoji sequence, the three RGI subdivision flags (England, Scotland, Wales),
and ZWJ/ZWNJ inside a word in a script that needs them (Arabic script, Indic scripts).
Also removes variation selectors that do not follow a character they can modify.
Every constant is an escape, so copying this file through a text cleaner cannot blank it."""
import re
import unicodedata

ZWNJ, ZWJ, VS16 = "\u200c", "\u200d", "\ufe0f"
BLACK_FLAG, CANCEL_TAG = "\U0001F3F4", "\U000E007F"
# Tag spellings of the only subdivision flags in Unicode's recommended (RGI) set.
RGI_FLAG_TAGS = {"".join(chr(0xE0000 + ord(ch)) for ch in s) for s in ("gbeng", "gbsct", "gbwls")}
# Scripts whose spelling uses ZWNJ/ZWJ: Arabic, Arabic Supplement/Extended-A, Arabic
# presentation forms (Persian, Urdu, Kurdish...), Devanagari through Sinhala (Indic).
JOINER_SCRIPTS = ((0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF),
                  (0xFB50, 0xFDFF), (0xFE70, 0xFEFF), (0x0900, 0x0DFF))
# Emoji blocks only. VS16, tags, private-use planes and the variation selectors supplement
# are deliberately excluded, so a ZWJ needs a visible emoji on both sides to be kept.
EMOJI_RANGES = ((0x1F000, 0x1FAFF), (0x2600, 0x27BF), (0x2B00, 0x2BFF))
# A variation selector (VS1-16, or VS17-256) right after whitespace, the start of the text,
# another selector, or an ASCII character other than a keycap base (0-9 # *) modifies nothing.
STRAY_VS = re.compile(r"(?:(?<=^)|(?<=[\s\ufe00-\ufe0f\U000E0100-\U000E01EF])|"
                      r"(?<=[\x21-\x22\x24-\x29\x2b-\x2f\x3a-\x7e]))[\ufe00-\ufe0f\U000E0100-\U000E01EF]")


def _emoji(c):
    return any(a <= ord(c) <= b for a, b in EMOJI_RANGES)


def _joining_letter(c):
    return (unicodedata.category(c)[0] in "LM"
            and any(a <= ord(c) <= b for a, b in JOINER_SCRIPTS))


def legit_positions(text):
    keep = set()
    for i, c in enumerate(text):
        prev, nxt = text[i - 1] if i else "", text[i + 1] if i + 1 < len(text) else ""
        # emoji, or emoji + VS16, before the ZWJ; a real emoji after it (never a bare VS16)
        emoji_before = prev and (_emoji(prev) or (prev == VS16 and i >= 2 and _emoji(text[i - 2])))
        if c == ZWJ and emoji_before and nxt and _emoji(nxt):
            keep.add(i)                                       # woman + ZWJ + laptop
        elif c in (ZWJ, ZWNJ) and prev and nxt and _joining_letter(prev) and _joining_letter(nxt):
            keep.add(i)                                       # Persian mi + ZWNJ + khaham
        elif c == BLACK_FLAG:
            for tags in RGI_FLAG_TAGS:                        # flag + 5 tags + CANCEL TAG
                if text.startswith(tags + CANCEL_TAG, i + 1):
                    keep.update(range(i + 1, i + 7))
    return keep


def strip_stray_vs(text):
    """Delete variation selectors that modify nothing. Repeated until stable, because
    deleting one can leave the next one stray."""
    while True:
        new = STRAY_VS.sub("", text)
        if new == text:
            return text
        text = new


def clean_around(text, clean):
    """Run clean(segment) -> (segment, hits) on the text between legitimate format
    characters, so the cleaner never sees them. No stand-in characters are used,
    so nothing already in the input can be turned into a format character."""
    out, hits, start = [], {}, 0
    for i in sorted(legit_positions(text)) + [len(text)]:
        seg, h = clean(text[start:i])
        out.append(seg)
        for e in h:                                           # merge per-segment counts
            hits.setdefault(e["name"], dict(e, count=0))["count"] += e["count"]
        out.append(text[i:i + 1])
        start = i + 1
    return strip_stray_vs("".join(out)), list(hits.values())


def stray_cf(text):
    """Count the format characters that are not part of real text, plus stray selectors."""
    keep = legit_positions(text)
    rest = "".join(c for i, c in enumerate(text) if unicodedata.category(c) != "Cf" or i in keep)
    return len(text) - len(strip_stray_vs(rest))
```

```diff
--- humanize.py
+++ humanize.py
@@ -33,6 +33,8 @@
 import sys
 import unicodedata
 
+import joiners
+
 HERE = os.path.dirname(os.path.abspath(__file__))
 LEX = os.path.join(HERE, "slop.json")
 
@@ -180,8 +182,9 @@
 
 
 def humanize(text, lex):
+    # Invisible pass first: a URL match (\S+) would otherwise carry hidden characters through.
+    text, inv = joiners.clean_around(text, lambda t: pass_invisible(t, lex))
     text, urls = protect_urls(text)
-    text, inv = pass_invisible(text, lex)
     text, typo = pass_typographic(text, lex)
     text, lexi = pass_lexical(text, lex)
     text = restore_urls(text, urls)
```

`clean_around` splits the text at the legitimate positions, runs `pass_invisible` on each stretch in between, puts the kept characters back between the cleaned stretches, and merges the per-stretch hit counts so `--report` still prints one line per character class. It then deletes stray variation selectors (`strip_stray_vs`, repeated until nothing changes, because deleting one can strand the next). No character is ever swapped for a stand-in, so nothing the input already contains is turned into something else. The patch also moves the invisible pass ahead of `protect_urls`; `pass_invisible` only deletes or respaces invisible characters, so running it on a link changes nothing visible in it.

### `detect.py` diff (2c, 2f, `N/A`)

This one diff carries the 2c `stray_cf` line, links left out of SLOP DENSITY, SPECIFICITY out of the verdict, `N/A` for short text (VOICE still scores structural tells), the named `PASS_OVERALL, PASS_FLOOR` constants that `calibrate.py` prints values for, and the "never invent one" advice line. It needs `joiners.py` beside it.

```diff
--- detect.py
+++ detect.py
@@ -29,8 +29,11 @@
 import sys
 import unicodedata
 
+import joiners
+
 HERE = os.path.dirname(os.path.abspath(__file__))
 LEX = os.path.join(HERE, "slop.json")
+URL_RE = re.compile(r"https?://\S+|www\.\S+|\S+@\S+\.\S+")   # same pattern as humanize.py
 
 SENT_RE = re.compile(r"[^.!?\n]+[.!?]*")
 WORD_RE = re.compile(r"[A-Za-z']+")
@@ -63,7 +66,7 @@
     """Humans vary sentence length hard. Models write even."""
     lens = [len(s.split()) for s in sentences(text)]
     if len(lens) < 4:
-        return 50.0, "too short to judge"
+        return None, "too short to judge"
     mean = statistics.mean(lens)
     cv = statistics.pstdev(lens) / mean if mean else 0
     score = scale(cv, human=0.70, machine=0.22)
@@ -74,7 +77,7 @@
     """Numbers, names and concrete nouns. Slop is abstract."""
     w = words(text)
     if len(w) < 25:
-        return 50.0, "too short to judge"
+        return None, "too short to judge"
     per100 = 100 / len(w)
     hits = len(NUMBERS.findall(text)) + len(set(PROPER.findall(text)))
     density = hits * per100
@@ -84,6 +87,7 @@
 
 def check_slop(text, lex):
     """Stock vocabulary density against the lexicon."""
+    text = URL_RE.sub(" ", text)          # humanize.py never rewrites inside a link, so do not count it
     w = words(text)
     if not w:
         return 50.0, "empty"
@@ -105,7 +109,7 @@
 
 def check_fingerprint(text):
     """Characters a phone keyboard does not produce."""
-    invisible = sum(1 for c in text if unicodedata.category(c) == "Cf")
+    invisible = joiners.stray_cf(text)
     em = text.count("—")
     curly = sum(text.count(c) for c in "‘’“”")
     ellip = text.count("…")
@@ -121,11 +125,6 @@
 def check_voice(text, lex):
     """Contractions, person, and the shapes models default to."""
     w = words(text)
-    if len(w) < 25:
-        return 50.0, "too short to judge"
-    per100 = 100 / len(w)
-    contractions = len(CONTRACTIONS.findall(text)) * per100
-    person = len(PRONOUNS.findall(text)) * per100
     tells = 0
     names = []
     for s in lex["structures"]:
@@ -136,6 +135,14 @@
         if n:
             tells += n
             names.append(s["id"])
+    if len(w) < 25:
+        # Too short for contractions and pronouns, but rocket emoji and engagement bait still count.
+        if not tells:
+            return None, "too short to judge"
+        return clamp(100 - tells * 22), f"too short for style; {tells} structural tell(s) [" + ", ".join(names[:4]) + "]"
+    per100 = 100 / len(w)
+    contractions = len(CONTRACTIONS.findall(text)) * per100
+    person = len(PRONOUNS.findall(text)) * per100
     bullets = [len(b.split()) for b in re.findall(r"(?m)^\s*[-*•]\s+(.+)$", text)]
     uniform = (len(bullets) >= 3 and statistics.pstdev(bullets) < 1.6)
     score = (scale(contractions, human=3.0, machine=0.0) * 0.35
@@ -152,8 +159,16 @@
 
 
 CHECKS = ["BURSTINESS", "SPECIFICITY", "SLOP DENSITY", "FINGERPRINT", "VOICE"]
+# SPECIFICITY is shown as advice but never gates: otherwise invented numbers buy a PASS.
+GATED = ["BURSTINESS", "SLOP DENSITY", "FINGERPRINT", "VOICE"]
+PASS_OVERALL, PASS_FLOOR = 70, 55
 
 
+def gate_scores(results):
+    """The scores the verdict uses: gated checks only, None (too short) left out."""
+    return [results[c][0] for c in GATED if results[c][0] is not None]
+
+
 def run(text, lex):
     results = {}
     results["BURSTINESS"] = check_burstiness(text)
@@ -161,10 +176,10 @@
     results["SLOP DENSITY"] = check_slop(text, lex)
     results["FINGERPRINT"] = check_fingerprint(text)
     results["VOICE"] = check_voice(text, lex)
-    scores = [results[c][0] for c in CHECKS]
+    scores = gate_scores(results)
     # The weakest check drags the verdict: a detector only needs one signal.
     overall = statistics.mean(scores) * 0.6 + min(scores) * 0.4
-    verdict = "PASS" if overall >= 70 and min(scores) >= 55 else (
+    verdict = "PASS" if overall >= PASS_OVERALL and min(scores) >= PASS_FLOOR else (
         "REVIEW" if overall >= 50 else "FLAGGED")
     return results, overall, verdict
 
@@ -180,13 +195,19 @@
     print("=" * max(len(title), 62), file=out)
     for name in CHECKS:
         score, detail = results[name]
-        print(f"  {name:<13} {bar(score)} {score:5.1f}", file=out)
+        shown = f"{bar(score)} {score:5.1f}" if score is not None else f"{'':<24}   N/A"
+        print(f"  {name:<13} {shown}", file=out)
         print(f"  {'':<13} {detail}", file=out)
     print("-" * 62, file=out)
     print(f"  {'HUMAN SCORE':<13} {bar(overall)} {overall:5.1f}   {verdict}", file=out)
     if verdict != "PASS":
-        weakest = min(CHECKS, key=lambda c: results[c][0])
+        weakest = min((c for c in GATED if results[c][0] is not None), key=lambda c: results[c][0])
         print(f"\n  Weakest signal: {weakest}. Fix that first.", file=out)
+    if any(results[c][0] is None for c in GATED):
+        print("  Too short to judge style: N/A checks are left out of the verdict. VOICE still counts structural tells.", file=out)
+    spec = results["SPECIFICITY"][0]
+    if spec is not None and spec < PASS_FLOOR:
+        print("  SPECIFICITY is low: ask the user for a real number or example. Never invent one.", file=out)
     print("", file=out)
 
 
@@ -210,7 +231,7 @@
         results, overall, verdict = run(text, lex)
         payload.append({
             "source": name,
-            "checks": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
+            "checks": {k: {"score": None if v[0] is None else round(v[0], 1), "detail": v[1]} for k, v in results.items()},
             "human_score": round(overall, 1),
             "verdict": verdict,
         })
```

Checked on a scratch copy (raw = the text as given; cleaned = after `humanize.py`; both scripts patched unless stated):

| input | original scripts | patched scripts |
|---|---|---|
| `honest.txt` / `ph.txt` / `inv.txt` (F1) | 41.9 / 42.5 / 75.1 | 72.2 / 74.9 / 73.6, all REVIEW (BURSTINESS 49.5 / 54.3 / 52.0, under 55) |
| `c1.txt`, the skill's own example comment (F2) | 54.9 REVIEW, capped by two flat 50s | BURSTINESS `N/A`, 70.0 REVIEW, weakest VOICE 50.0 |
| 3-sentence comment with the woman-technologist emoji, raw | FINGERPRINT 0.0, 30.0 FLAGGED | FINGERPRINT 100.0; 100.0 PASS (no stock words, no tells, other style checks `N/A`) |
| the same comment, cleaned (what the loop scores) | 62.0 REVIEW, emoji split in two | emoji intact; 100.0 PASS on artefacts only (from the `N/A` change, not from 2c) |
| `phone.txt` raw / cleaned | 35.7 FLAGGED / 65.1 REVIEW | 29.7 FLAGGED / 63.0 REVIEW (SPECIFICITY no longer lifts the average) |
| woman-technologist emoji, England flag, Persian word, Devanagari half-form, zero-width space, 2 stray tags, a "usca" flag, a 28-character tag message behind U+1F3F4, through `humanize.py` | every joiner and tag deleted | joiners in the emoji, the Persian word and the half-form kept; England's 5 tags + CANCEL TAG kept; the zero-width space and 36 tag characters deleted |
| U+4F60 U+200C U+597D U+200C U+4E16 U+200C U+754C (Chinese with ZWNJs) | all 3 deleted | all 3 deleted, and counted by FINGERPRINT on raw text |
| `Great post` + U+F0049 U+F0047 U+F004E + `. Thanks` + U+F8F1 + ` for this.` | private-use characters left as they are | left as they are (no tag characters or ZWJ appear) |
| `Great post` + tag a, ZWJ, tag b, ZWJ, tag c, ZWJ, tag d + `. Thanks` + U+F0001 U+200D U+F0002 + ` for this.` | no ZWJ left | no ZWJ left; FINGERPRINT 100.0 on the cleaned text (an earlier helper kept 4 ZWJs here) |
| rainbow flag (U+1F3F3 U+FE0F U+200D U+1F308), black cat (U+1F408 U+200D U+2B1B), scientist with skin tone (U+1F469 U+1F3FD U+200D U+1F52C), heart on fire (U+2764 U+FE0F U+200D U+1F525) | joiners deleted | joiners and the VS16s kept |
| keycap one (`1` U+FE0F U+20E3), U+00A9 U+FE0F, U+2764 U+FE0F, CJK U+845B + U+E0100 | left as they are | left as they are |
| `Great post` + (U+FE0F U+200D) x 12 + U+FE0F + ` thanks for sharing.` | 12 ZWJs deleted, 13 VS16s kept; 62.0 REVIEW | all 25 deleted; raw text counts 25 invisible; cleaned 100.0 PASS on plain text (an earlier helper kept all 25 and reported "0 invisible") |
| `Hi ` + U+FE0F U+FE0E + ` there`; `a` + U+E0101 + `b`; U+2764 U+FE0F U+200D U+FE0F U+200D U+FE0F | selectors kept | stray selectors and both ZWJs deleted; the heart keeps one VS16 |
| `Full write-up here: https://example.com/post` + U+200B + 14 tag characters + ` and it took us ages.` | all 15 kept; FINGERPRINT 0.0, 30.0 FLAGGED | all 15 deleted; link intact; 100.0 PASS |
| `Full guide: https://example.com/leverage-robust-synergy and we use it every week now.`, cleaned | SLOP DENSITY 0.0, 30.0 FLAGGED (words in the link counted, never replaced) | link left as is and not counted; 100.0 PASS |
| `This is huge` + U+1F680 U+1F680 + ` Who else is seeing this? Agree?`, cleaned | VOICE 50.0 flat, 62.0 REVIEW | VOICE 34.0 (rocket, engagement-bait), 60.4 REVIEW, weakest VOICE |

### `provenance.py` (3b)

```python
#!/usr/bin/env python3
"""Every number or magnitude claim in a draft must appear in the user's proof ledger, or be a {{placeholder}}.
Usage: python3 provenance.py draft.txt proof.md [context.txt ...]   (exit 1 if any claim is unsourced)
Ledger format: one fact per line, optionally starting with an ISO date (2026-03-14).
context.txt: text that sources THIS draft only - the post being commented on, the message being
answered, a transcript being repurposed, or numbers the user confirmed in chat. Never the ledger."""
import re, sys

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = dict(zip("twenty thirty forty fifty sixty seventy eighty ninety".split(), range(20, 100, 10)))
WORDVAL = {w: i for i, w in enumerate(ONES)} | TENS | {"dozen": 12}
MULT = {"hundred": 100, "thousand": 1000, "million": 10**6, "billion": 10**9}
SUFFIX = {"k": 1000, "K": 1000, "M": 10**6, "m": 10**6, "bn": 10**9,
          "thousand": 1000, "million": 10**6, "billion": 10**9}
# A number, with its scale if it has one: 12,000 / $12k / 1.5M / 3 million / £2m.
# Digits glued to a letter on the left (B2B, Q3, H1) are names, not quantities.
# Lower-case "m" counts as million only after a currency sign ("5m" alone may be minutes or metres).
DIGITS = re.compile(r"(?<![A-Za-z\d.,])(?P<cur>[$£€])?(?P<num>\d[\d,]*(?:\.\d+)?)"
                    r"(?:(?P<suf>[kKMm]|bn)\b|\s?(?P<word>thousand|million|billion)\b)?")
WORDNUM = re.compile(r"\b(?:a\s+(?=(?:%s)\b))?(?:%s)(?:[\s-]+(?:%s|and))*\b" % (
    "|".join(MULT), "|".join(list(WORDVAL) + list(MULT)), "|".join(list(WORDVAL) + list(MULT))), re.I)
# Vague magnitudes a model likes to invent; they pass only if the same word is in the ledger.
VAGUE = re.compile(r"\b(hundreds|thousands|millions|billions|dozens|(?:doubl|tripl|quadrupl)(?:ed|es|ing)|"
                   r"halved|halving|twice|(?:two|three|four|five|ten)fold)\b", re.I)
# Phrases that contain a number or magnitude word but make no claim. Add more as they come up.
IDIOMS = re.compile(r"\b\d{1,2}(?::\d{2})?\s?[ap]\.?m\b\.?|\b\d{1,2}:\d{2}\b|\b24/7\b|\b365\b(?=\s+days a year)|\b(?:2|two)\s+cents\b|\bdoubl\w*\s+down\b", re.I)
# "1. Draft" / "2. Ship" are not claims. Only a run numbered 1, 2, ... with text on the same
# line counts as a list, so a lone "47." or "2019. The year I quit." opening a post is still checked.
# Links, hashtags, @mentions and calendar dates hold digits but make no claim.
LINKS = re.compile(r"https?://\S+|www\.\S+|\S+@\S+\.\S+|(?<!\w)[#@](?=\w*[A-Za-z])\w+")
_MONTH = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sept?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
_DAY = r"(?:Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day"
DATES = re.compile(r"\b(?:%s,?\s+(?:the\s+)?|%s\.?\s+(?:the\s+)?)\d{1,2}(?:st|nd|rd|th)?\b|"
                   r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?%s\b" % (_DAY, _MONTH, _MONTH))   # case-sensitive: "may 5" is not May 5
LIST_MARKER = re.compile(r"^[ \t]*(\d{1,2})[.)][ \t]+(?=\S)", re.M)
LEADING_DATE = re.compile(r"^\s*\d{4}-\d{2}-\d{2}\s*", re.M)

def words_to_int(tokens):
    total = cur = 0
    for w in tokens:
        if w in WORDVAL: cur += WORDVAL[w]
        elif w in MULT:
            cur = max(cur, 1) * MULT[w]
            if MULT[w] >= 1000: total, cur = total + cur, 0
    return total + cur

def spans(phrase):
    """'five and six' -> two numbers; 'two hundred and fifty' -> one."""
    toks = [t for t in re.split(r"[\s-]+", phrase.lower()) if t and t != "a"]
    groups, cur = [], []
    for t in toks:
        if t == "and" and not (cur and cur[-1] in MULT):
            groups.append(cur); cur = []
        elif t != "and":
            cur.append(t)
    return [g for g in groups + [cur] if g]

def key(v):
    v = round(float(v), 6)                                   # 2.01 * 1000 == 2010, not 2009.999...
    return str(int(v)) if v.is_integer() else repr(v)

def strip_list_markers(text):
    nums, n = {int(m[1]) for m in LIST_MARKER.finditer(text)}, 1
    while n in nums: n += 1
    if n < 3: return text                                     # no "1." and "2." -> not a list
    return LIST_MARKER.sub(lambda m: "" if int(m[1]) < n else m.group(), text)

def numbers(text):
    """Values: '$12,000' == '12k' == 'twelve thousand', '40%' == '40 percent' == 'forty percent'."""
    found = {}
    text = IDIOMS.sub(" ", DATES.sub(" ", LINKS.sub(" ", text)))
    def digit(m):
        n = float(m["num"].rstrip(".").replace(",", ""))
        suf = m["suf"] or m["word"] or ""
        scale = 1 if suf == "m" and not m["cur"] else SUFFIX.get(suf, 1)
        found[key(n * scale)] = m.group().strip()
        return " "                                           # so "million" is not read twice
    text = DIGITS.sub(digit, text)
    for m in WORDNUM.finditer(text):
        for g in spans(m.group()):
            if g == ["one"]: continue                         # "one of the" is not a claim
            found[key(words_to_int(g))] = m.group()
    for m in VAGUE.finditer(text):
        w = m.group().lower()
        found["~" + (w if w.endswith("fold") or w == "twice" else re.sub(r"(ed|es|ing)$", "", w))] = m.group()
    return found

if __name__ == "__main__":
    draft, ledger, *context = (open(p, encoding="utf-8").read() for p in sys.argv[1:])
    known = numbers(LEADING_DATE.sub("", ledger))
    for c in context: known |= numbers(c)
    draft = strip_list_markers(re.sub(r"\{\{.*?\}\}", "", draft))   # placeholders are honest gaps
    unsourced = {v: raw for v, raw in numbers(draft).items() if v not in known}
    for v, raw in sorted(unsourced.items()):
        print(f"UNSOURCED  {raw}")
    print("OK" if not unsourced else f"{len(unsourced)} claim(s) not in the ledger")
    sys.exit(1 if unsourced else 0)
```

Tested with this ledger (`L1`):

```
2026-03-14  Proposal time went from 5 hours to 20 minutes.
2026-05-02  Revenue grew 40%.
2026-05-09  Closed a $12,000 contract.
```

| draft | result |
|---|---|
| `We now serve 14 clients across 2026.` | fails on 14 and 2026 (the ledger's dates do not count as facts) |
| `We signed eleven new clients.` | fails on "eleven" |
| `Revenue grew 40 percent.` / `Revenue grew forty percent on a 12,000 dollar deal.` | OK / OK |
| `1. Draft it.` / `2. Review it.` / `3. Ship it.` (one per line) | OK (a list numbered from 1) |
| `47.` + blank line + `That is how many cold DMs I sent before one client replied.` | fails on 47 |
| `2019. That is the year I quit.` | fails on 2019 |
| `1. I sent 47 DMs.` / `2. One replied.` | fails on 47 only |
| `2. Review it.` / `3. Ship it.` (a list that does not start at 1) | fails on 2 and 3 |
| `Free Tuesday at 3pm for 15 minutes? Or 9:30 a.m. Wednesday.` | fails on 15 only; passes once the user confirms 15 into a context file |
| `Your 23% churn drop is higher than I would have guessed.`, with the post being commented on as context | OK |
| `Your 23% churn drop beats our 31%.`, same context | fails on 31 |
| `Loved your SaaStr 2025 talk.`, with the user's note on the person as context | OK |
| `Proposal time fell from 5 hours to 20 minutes. One of the best changes.` | OK |
| `It took {{your number}} weeks and twenty-five calls.` | fails on "twenty-five" only |
| `It took 3 months.` / `We grew 10x.` | fails on 3 / fails on 10 |
| `We hired a hundred people.` / `Thousands of users signed up.` | fails on "a hundred" / "Thousands" |
| `We tripled revenue.` / `We doubled revenue.` / `We halved the cost.` / `Sales went up threefold.` | each fails on its magnitude word |
| `It took five and six weeks.` | fails on 6 only (read as 5 and 6; 5 is in the ledger) |
| `Our B2B team ran Q3 24/7.` | OK |
| `That is the part I would double down on.` / `We doubled down on outbound.` | OK / OK (idiom) |
| `We scaffold every new project the same way.` | OK |
| `The second half of the talk was better.` | OK |
| `My 2 cents: ship it.` | OK (idiom) |
| `We closed a $12k contract.` / `We closed a twelve thousand dollar contract.` | OK / OK (both equal 12,000) |
| `We closed a $12M deal.` | fails on "$12M" (12,000,000 is not 12,000) |
| `Closed a $2.01k deal. Reached 2.05M impressions.`, ledger `Closed a $2,010 deal and reached 2,050,000 impressions.` | OK (values are rounded before comparing; without that, 2.01 * 1000 = 2009.999...) |
| `Closed a $2,011 deal.`, same ledger | fails |
| `Full template here: https://example.com/blog/2024/05/proposal-template-v3` | OK (link) |
| `Doing #100DaysOfCode with my team.` / `Ping @dev42 or mail me at jo99@example.com.` | OK / OK |
| `We have #1 ranked support.` | fails on 1 (a hashtag with no letter is a claim) |
| `Call me on Tuesday the 14th.` / `Free on March 3rd or 14 May? Or the 2nd of June.` | OK / OK (dates) |
| `We grew 300% since May 2024.` | fails on 300 and 2024 (a year is still checked) |
| `Our 14th client signed.` | fails on 14 (an ordinal without a weekday or month is checked) |

With a ledger that says only `We have 12 clients.`: `We hit $12M in revenue.` and `We hit $12m in revenue.` both fail; `We have 12 clients.` passes. With a ledger containing 250, 25, 3,400 and "Revenue doubled": "two hundred and fifty hires", "twenty-five calls", "three thousand four hundred sign-ups", "3.4k sign-ups" and "Revenue doubled again." pass; "a dozen calls" and "We hired a hundred people." fail.

Known gaps found in testing:
- It matches values, not meaning. A "5" in the ledger lets any "5" through (including "5m", read as 5 because a lower-case m without a currency sign may be minutes or metres), and "doubled" in the ledger lets any "doubled" through.
- "one" and bare "half" are never checked ("one of the", "the second half" are too common), so "One client" and "Half the team quit" are not caught. "twice" is checked, so "I thought twice" fails; add such phrases to `IDIOMS`.
- When an honest number fails: reusable fact to the ledger, number from the text being answered or confirmed by the user to that draft's context file, claim-free phrase to `IDIOMS`. Putting "double" or "half" in the ledger to silence a false fail lets matching inventions through.
- A context file sources every number in it, so a comment could restate the original post's "23%" as the user's own result and still pass. The human read covers that.
- Clock times are skipped, so "I wake at 4am every day" is not checked.
- Numbers inside links, e-mail addresses and lettered hashtags are never checked, so a claim written only as a URL slug or a hashtag (`#3xRevenue`) passes. The link itself is the user's to check.
- A month name or weekday right before a number is read as a date, so "In May 14 clients signed" passes. Month names are matched case-sensitively, so "you may 3x it" is still checked. Write "In May, 14 clients signed", or use a placeholder.
- A list that does not start at 1, or a one-item list, is checked number by number.
- Comparatives and quantifiers ("most", "far more", "the majority", "almost everyone") are not checked. They are claims too, but flagging them would fail most honest prose. The human read covers them.
- A year in the draft fails unless the ledger mentions it in the fact text (the leading date is ignored). Add the year to the fact, or use a placeholder.
- Slide counters such as `1/10` are flagged. Remove them before the check, or run the check on slide text only.
- Digits glued to a letter on the left are skipped, so "Q3" passes, and so would a claim written as "x3".
- Names are not checked. Extend it with a list of approved names from the ledger if that matters.

### `calibrate.py` (2e)

Run it only after the `detect.py` diff above is installed. It imports `detect.gate_scores`, so on the unpatched script it stops with an `AttributeError` instead of tuning a rule you are about to replace.

```python
#!/usr/bin/env python3
"""Set detect.py's two thresholds (PASS_OVERALL, PASS_FLOOR) from your own writing.
Run it AFTER the 2f/N/A patch to detect.py: it scores with detect.gate_scores, so it tunes
whichever rule is installed, not a copy of it.
Usage: python3 calibrate.py path/to/li-human mine/ model/ [max_false_flag=0.10] [cleaning_lexicon.json]
Pass artefacts-only.json as the last argument if you use 2a (flag, don't substitute), so the
texts are cleaned the way your loop cleans them. Scoring always uses the full slop.json.
mine/  = 20+ posts you wrote before using AI, one .txt per post
model/ = 20+ /li-post drafts on the same topics, saved before your edits
Both sets go through humanize.py first, because the PASS/REVIEW verdict is taken on cleaned text."""
import pathlib, sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1]); import detect, humanize
lex = humanize.load_lexicon()
max_fp = float(sys.argv[4]) if len(sys.argv) > 4 else 0.10
clean_lex = humanize.load_lexicon(sys.argv[5]) if len(sys.argv) > 5 else lex

def scores(folder):
    out = []
    for p in sorted(pathlib.Path(folder).glob("*.txt")):
        clean, _ = humanize.humanize(p.read_text(encoding="utf-8"), clean_lex)
        res, overall, _ = detect.run(clean, lex)
        out.append((overall, min(detect.gate_scores(res))))
    return out

mine, model = scores(sys.argv[2]), scores(sys.argv[3])
fails = lambda s, T, C: s[0] < T or s[1] < C               # the rule detect.py applies
rate = lambda xs, T, C: sum(fails(s, T, C) for s in xs) / len(xs)
cands = lambda i: sorted({0.0} | {s[i] for s in mine})    # cut points that change the result
T, C = max(((T, C) for T in cands(0) for C in cands(1) if rate(mine, T, C) <= max_fp),
           key=lambda tc: (rate(model, *tc), tc))
print(f"set PASS_OVERALL, PASS_FLOOR = {T:.1f}, {C:.1f} in detect.py")
print(f"your posts flagged by that joint rule: {rate(mine, T, C):.0%} of {len(mine)} (limit {max_fp:.0%})")
print(f"model drafts flagged by that joint rule: {rate(model, T, C):.0%} of {len(model)}")
print("With 20 posts the flag rate on new posts will run higher than shown. "
      "If model drafts flagged is under ~60%, use the score as a hint, not a gate.")
```

Tested on a toy set (24 short first-person texts in `mine/`, 20 shuffles of a stock corporate paragraph in `model/`) against the previous revision of the patched `detect.py` (before the VOICE-tells and link changes; the script was rerun against the current diff and still runs). It printed `PASS_OVERALL, PASS_FLOOR = 63.8, 34.2`, flagging 8% of `mine/` and 100% of `model/` under the joint rule; with a 20% limit it printed 66.0, 38.2 (17% and 100%). The toy numbers only show that the script works. Your thresholds come from your own posts. The optional fifth argument (cleaning lexicon) was checked to run: on a 3-sentence stock paragraph it is the difference between SLOP DENSITY 100.0 (full lexicon, words swapped before scoring) and 0.0 (artefacts only), which is why a 2a user must pass it.

### `compare.py` (8c)

```python
#!/usr/bin/env python3
"""Is one kind of post better, or is it noise?
Usage: python3 compare.py events.csv FACTOR LEVEL [--tests K]
events.csv: the 8a log. Rows with kind=post and a number in impressions are used.
  Needs columns FACTOR, impressions, reactions, comments, reposts (plain counts, no % or commas).
--tests K: how many comparisons you will look at in this audit (default 1).
  The bar becomes 0.05/K (Bonferroni), so running many tests does not manufacture findings."""
import argparse, csv, random, statistics as st, sys
ap = argparse.ArgumentParser(); ap.add_argument("csv"); ap.add_argument("factor"); ap.add_argument("level")
ap.add_argument("--tests", type=int, default=1); a_ = ap.parse_args()
def rate(r):
    n = lambda k: int(r[k].replace(",", "") or 0)
    return (n("reactions") + n("comments") + n("reposts")) / n("impressions")
rows = [r for r in csv.DictReader(open(a_.csv, encoding="utf-8"))
        if r.get("kind", "post") == "post" and r["impressions"].replace(",", "").isdigit() and int(r["impressions"].replace(",", ""))]
a = [rate(r) for r in rows if r[a_.factor] == a_.level]
b = [rate(r) for r in rows if r[a_.factor] != a_.level]
if min(len(a), len(b)) < 5:
    sys.exit(f"not enough data: {len(a)} '{a_.level}' posts vs {len(b)} others (need 5+ each)")
obs = st.median(a) - st.median(b)
pool, rng, hits = a + b, random.Random(0), 0
for _ in range(10_000):
    rng.shuffle(pool)
    hits += abs(st.median(pool[:len(a)]) - st.median(pool[len(a):])) >= abs(obs)
p, bar = (hits + 1) / 10_001, 0.05 / a_.tests
print(f"{a_.level}: median {st.median(a):.2%} (n={len(a)}, range {min(a):.2%}-{max(a):.2%})")
print(f"others: median {st.median(b):.2%} (n={len(b)}, range {min(b):.2%}-{max(b):.2%})")
print(f"p = {p:.4f}, bar = {bar:.4f} for {a_.tests} test(s) -> " + (
      "unlikely to be noise; worth acting on" if p < bar else
      "suggestive, test it again on new posts" if p < 0.2 else "no evidence of a difference"))
```

The p-value is (hits + 1) / 10,001, so it is never reported as exactly 0. Tested on three synthetic `events.csv` files, each with a non-post row that is correctly skipped:
- a real gap (10 story posts at 3-6% vs 20 others at 1-3%): p = 0.0001, under the bar both for one test (0.05) and for 14 tests (0.0036);
- 30 posts with no real difference: p = 0.49, "no evidence of a difference";
- 6 posts: "not enough data: 2 'story' posts vs 4 others".

