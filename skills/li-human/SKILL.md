---
name: li-human
description: >-
  Strip the machine fingerprint out of any draft - em dashes, AI slop words,
  invisible watermark characters - and score it against a five-check detection
  panel before it goes out. Use whenever text needs to sound human, when the
  user says humanize, "does this sound like AI", "remove the em dashes", "de-slop
  this", "will this get flagged", or before any LinkedIn post, comment, reply
  or DM is shown to the user.
---

# li-human

Two tools live in this folder and they both actually run. Use them. Do not
eyeball this.

```bash
python3 humanize.py draft.txt --report        # clean it, show what changed
python3 detect.py draft.txt                    # score it, five checks
python3 detect.py before.txt after.txt         # prove the delta
```

Both read `slop.json`, which is the lexicon: 100+ stock words and phrases with
plain-English replacements, 17 invisible character classes, 11 typographic
substitutions, and 11 structural tells. It is meant to be edited. If the user
has a word they always use that the lexicon strips, remove it from the file.

## What gets fixed automatically

**1. Invisible characters.** Zero-width spaces and joiners, word joiners,
soft hyphens, byte-order marks, Unicode tag characters, non-breaking and
narrow spaces. A keyboard does not produce these. They survive copy-paste,
they are invisible in every editor, and they are the single most mechanical
thing in generated text. `humanize.py` deletes every one, including any
remaining Unicode format character it does not have a name for, and any
invisible character glued to the end of a link. The exceptions are characters
that belong to real text, which `joiners.py` finds by position: the joiner
inside an emoji like woman-technologist, the tags in the England, Scotland and
Wales flags, and the joiners inside Persian, Urdu, Hindi and other words in
scripts that need them. Those are kept.

**2. Typography.** Em dash to comma, en dash to hyphen, curly quotes to
straight, ellipsis to three dots, bullet character to hyphen. The em dash pass
is the one that matters: it collapses ` — ` to `, ` and then cleans up the
double punctuation that leaves behind.

**3. The slop lexicon is flagged, not swapped.** delve, leverage, robust,
seamless, crucial, tapestry, testament to, moreover, "in today's fast-paced
world", "let that sink in" and the rest. A blind swap breaks meaning ("the
landscape painting" becomes "the market painting", "a vital sign" becomes "a
important sign"), so the skill cleans with `artefacts-only.json`, which keeps
the words, and you rewrite each flagged sentence with its context.
`humanize.py` run on its own still swaps words, for anyone who wants that.
`artefacts-only.json` is `slop.json` with the word and phrase lists empty.
Regenerate it when you edit `slop.json`.

## What does NOT get fixed automatically

Structural tells get **flagged, not rewritten**, because changing the shape of
a sentence needs judgement:

- "It's not just X, it's Y" and "not only X but also Y"
- Rule-of-three triads
- Rhetorical one-word question lines: "The result?"
- Rocket, fire, bulb, sparkle and dart emoji
- Hashtag walls
- Reflex engagement bait: "Thoughts?", "Agree?", "Who else?"
- Uniform sentence length and uniform bullet length

That list is your job. Rewrite each flagged line by hand, keeping the meaning,
then re-run `detect.py`. This is the part that moves the score from REVIEW to
PASS, and it is the part a script cannot do.

## The five checks

`detect.py` scores five signals 0-100, higher is more human:

| check | what it measures | machine looks like |
| --- | --- | --- |
| BURSTINESS | sentence-length variation | every sentence the same length |
| SPECIFICITY | numbers, names, concrete markers per 100 words | abstract nouns, no figures |
| SLOP DENSITY | lexicon hits per 100 words | stock vocabulary |
| FINGERPRINT | invisible chars, em dashes, curly quotes per 1k chars | typographically perfect |
| VOICE | contractions, person, structural tells | no contractions, staged reveals |

The verdict weights the mean at 60% and the **weakest single check** at 40%,
because a detector only needs one signal to fire. PASS needs an overall of 70+
with no check below 55.

SPECIFICITY is printed as advice but does not count toward the verdict,
otherwise an invented number would buy a PASS. A low SPECIFICITY means ask the
user for a real number or example, or leave `{{your number}}`. Never invent one.

A check too short to judge prints `N/A` and is left out of the verdict. VOICE
still counts structural tells on short text, so a rocket emoji or "Agree?" in
a two-line comment still costs points.

## Say this honestly

These are five local heuristics modelled on the signals public detectors key
on. They run entirely on the user's machine and nothing is uploaded. They are
**not** GPTZero, Originality, Copyleaks, Winston or Turnitin, they do not call
those APIs, and they cannot promise those verdicts. Fixing what they measure
does tend to move those numbers, because they are measuring the same
underlying things. That is the claim. Do not make a bigger one on the user's
behalf, and do not tell a user their text is undetectable.

## Numbers must be sourced

Every number or magnitude claim in a draft ("40%", "$12k", "eleven clients",
"thousands", "doubled") must come from somewhere the user stands behind.
`provenance.py` checks this mechanically:

```bash
python3 provenance.py clean.txt ~/.claude/linkedin/proof.md [context.txt ...]
```

- `proof.md` is the user's ledger: one fact per line, optionally starting with
  a date. Copy `templates/proof.md` there if it does not exist.
- A context file sources numbers for this one draft only. Write it from:
  - the post being commented on (`/li-comment`);
  - the comment or message being answered (`/li-reply`, `/li-inbox`);
  - the user's notes on the person (`/li-dm`);
  - the transcript or source (`/li-repurpose`);
  - numbers the user confirmed in chat.
- Only the user's own message counts as confirmation. Ask "is 15 yours?";
  never assume it.
- `{{placeholders}}` are honest gaps and always pass.

When a number fails, it goes to exactly one place, with the user's say-so:

1. A fact they will reuse goes into `proof.md`.
2. A number from the text being answered, or one they just confirmed, goes
   into this draft's context file.
3. A phrase that makes no claim ("I thought twice") goes into `IDIOMS` in
   `provenance.py`.

Never put "double" or "half" in the ledger to silence a false fail. That lets
"we doubled revenue" through.

## Order of operations

1. Flag: `humanize.py draft.txt --report -o /dev/null`. Its "3. SLOP LEXICON"
   section lists the stock terms, and "4. STRUCTURAL TELLS" lists the shapes.
   The text it would write is thrown away.
2. Clean: `humanize.py draft.txt --lexicon artefacts-only.json -o clean.txt`.
   This removes invisible characters and fixes typography without touching
   a word.
3. Rewrite: in `clean.txt`, rewrite each sentence that holds a flagged term
   or tell. The instruction to yourself is "rewrite this sentence without X,
   keep the meaning, keep the voice". Show the user the changed sentences as
   a before/after, then run step 1 on `clean.txt` again until it lists
   nothing worth acting on. A flagged word the user actually uses can stay.
   Say so, and offer to remove it from `slop.json`.
4. `detect.py draft.txt clean.txt` to show the before and after. It scores
   with the full `slop.json`, so SLOP DENSITY measures what is still there.
5. If the verdict is not PASS, fix the weakest check named in the output and
   go again. It only ever names a gated check, never SPECIFICITY. Two rounds
   is normal. Five means the draft was written by formula, and the fix is a
   different draft, not more passes.
6. `provenance.py clean.txt ~/.claude/linkedin/proof.md [context...]` must
   print `OK`. This is a second required condition, alongside the verdict.
   Any number added during step 5 fails unless it is sourced. If a number
   fails, ask the user or put `{{your number}}` back. Never invent a source.
7. Show the user the cleaned text and the score. Never the score alone.
