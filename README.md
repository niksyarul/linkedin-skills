# LinkedIn skills

Eleven skills that run a LinkedIn account, for Claude, Gemini CLI and
ChatGPT/Codex. Free, MIT, no signup, no API key, nothing to connect.

One of them writes your posts off 21 hook formulas. One comments on other
people's posts. One handles the replies under yours. One scores your profile
out of 100 and rewrites what lost points. One plans the week: what to post,
when, and who to engage with.

And one is the humanizer, which is the reason the rest are usable. It strips
the em dashes, the slop vocabulary and the invisible watermark characters out
of a draft, then scores what is left against a five-check detection panel
before you ever see it.

**Nothing gets posted until you say yes.** These skills write. You post.

## What this is

This is a fork of Jake Schincariol's
[linkedin-agent-skill](https://github.com/Jakeschincariol/linkedin-agent-skill).
The skills, the hook formulas, the profile rubric and the humanizer are his
work. This fork adjusts them. It is not a rewrite.

The adjustments come from running the original scripts on test inputs and
finding cases where the humanizer works against its own goals. The full
analysis is in [docs/alternatives.md](docs/alternatives.md). The plan for
fixing it is in [docs/SPEC.md](docs/SPEC.md).

**Is it better?** On the cases we measured, yes. Elsewhere it behaves the same.

| case | original | this fork |
| --- | --- | --- |
| Honest post vs the same post with invented numbers | 41.9 FLAGGED vs 75.1 REVIEW. The score rewarded making numbers up. | 72.2 vs 73.6, both REVIEW. Invention buys almost nothing. |
| The skill's own 3-sentence example comment | 54.9 REVIEW, and PASS was impossible for any short text | 70.0 REVIEW, judged on what can be measured |
| Emoji like woman-technologist, the England flag, Persian and Hindi words | Broken by the cleaner | Kept intact |
| Hidden characters glued to the end of a link | Survived cleaning | Removed |

This is not a claim that the fork beats AI detectors. Neither version promises
that. The aim is narrower: the score should not push you toward inventing
facts, and the cleaner should not break real text.

Also added in this fork:
- **A proof ledger** (`proof.md`). No draft leaves `/li-human` with a number
  that is not in it, in the text being answered, or confirmed by you in chat.
- **Flag, then rewrite.** Stock words are flagged and rewritten with their
  context, instead of swapped blind ("the landscape painting" no longer
  becomes "the market painting").
- **A log of what you published**, not what you approved, keyed on the live
  URL, with the numbers collected at day 7.
- **A follow-up ledger** that remembers who is due a +4 or +10 DM follow-up.
- **A plan the other skills read.** `/li-post` drafts today's planned slot and
  `/li-audit` checks planned against posted.

## Install

Paste this into Claude:

```
https://github.com/niksyarul/linkedin-skills

Install this skill, then confirm /li-post works.
```

Or do it yourself, in Claude Code:

```bash
git clone https://github.com/niksyarul/linkedin-skills.git
cp -r linkedin-skills/skills/li-* ~/.claude/skills/
```

Or as a plugin:

```
/plugin marketplace add niksyarul/linkedin-skills
/plugin install linkedin-skills@linkedin-skills
```

Project-local instead of global: copy the same folders into your repo's
`.claude/skills/`. No Claude Code at all? Paste any single `SKILL.md` at the
top of a chat and it runs as a mode - you lose the two Python tools, which is
most of the point of `/li-human`, but the rest works.

### Gemini CLI

Gemini CLI reads the same `SKILL.md` format. Copy the folders into its user
skills directory, or into `.gemini/skills/` in a project:

```bash
git clone https://github.com/niksyarul/linkedin-skills.git
mkdir -p ~/.gemini/skills
cp -r linkedin-skills/skills/li-* ~/.gemini/skills/
```

Run `/skills list` inside `gemini` to check they loaded. Gemini picks a skill
from its description, so ask in plain words ("write a LinkedIn post about
X", "humanize this draft") instead of typing `/li-post`.

### Any chat app: one file

Works in a normal ChatGPT, Gemini or Claude chat, free accounts included:

1. Download [`skills.md`](chatgpt/skills.md) (open it, click the download button).
2. Start a new chat, attach `skills.md`, and type what you want: "write a
   LinkedIn post about the client we lost", "humanize this", "score my profile".
3. Attach your `voice.md` and `proof.md` too if you have them.

Do this once per chat. For something you set up once and keep, use a Project,
a custom GPT or a Gem below.

### ChatGPT Project or custom GPT

The [`chatgpt/`](chatgpt) folder is a ready-made pack. Download these three
files (open each one and click the download button):

- [`instructions.md`](chatgpt/instructions.md), which tells ChatGPT how to use the rest
- [`skills.md`](chatgpt/skills.md), all eleven skills in one file
- [`tools.zip`](chatgpt/tools.zip), the humanizer scripts. ChatGPT runs them itself.

Then, in ChatGPT:

1. Click **Projects**, then **New project**, and name it "LinkedIn".
2. Open the project settings, find **Instructions**, and paste in everything
   from `instructions.md`.
3. Add `skills.md` and `tools.zip` to the project files. Add your filled-in
   `voice.md` and `proof.md` too (see below).
4. Start a chat inside the project and ask in plain words: "write a LinkedIn
   post about the client we lost", "humanize this", "score my profile", "plan
   my week".

You can also build a custom GPT with the same instructions and files under
**Knowledge**, with **Code Interpreter** switched on. A custom GPT can be
shared as a link, so whoever builds one can hand it to people who would rather
not set anything up.

What you lose in ChatGPT: nothing carries over between chats, so the post log
and the DM follow-up ledger cannot be kept for you. When a skill would log
something, ChatGPT gives you the line to save yourself. If ChatGPT cannot run
the scripts, it checks the draft by hand and says the scores are estimates.

### Gemini (web or phone app, nothing to install)

The same pack works as a Gem:

1. Go to [gemini.google.com](https://gemini.google.com), open **Gems**, then
   **New Gem**, and name it "LinkedIn".
2. Paste everything from `instructions.md` into **Instructions**.
3. Under **Knowledge**, add `skills.md`, plus your `voice.md` and `proof.md`.
   Skip `tools.zip`. Gems cannot run the scripts, so Gemini checks drafts by
   hand and says the scores are estimates.
4. Save, then chat with the Gem in plain words, as above.

A saved Gem can be shared as a link, the same as a custom GPT.

Maintainers: after editing anything under `skills/`, run
`python3 chatgpt/build.py` to rebuild `skills.md` and `tools.zip`.

### Codex and the ChatGPT desktop app's skills

Codex CLI, the Codex IDE extension and the ChatGPT desktop app read the same
format from `~/.agents/skills` (or `.agents/skills/` in a repo):

```bash
git clone https://github.com/niksyarul/linkedin-skills.git
mkdir -p ~/.agents/skills
cp -r linkedin-skills/skills/li-* ~/.agents/skills/
```

Restart Codex if a skill does not show up, then ask in plain words, the same
as with Gemini.

### Where your files live

On a computer, every tool uses the same data folder, `~/.claude/linkedin/`, so switching
between Claude, Gemini and Codex keeps one voice, one proof ledger and one
log. The name is historical; nothing in it needs Claude.

Then spend ten minutes on `templates/voice.md`. Copy it to
`~/.claude/linkedin/voice.md` and fill it in, or paste three of your own posts
into Claude and say "write my voice.md from these". Every skill reads that
file. Skip it and everything comes out sounding like everyone else.

Then copy `templates/proof.md` to `~/.claude/linkedin/proof.md` and add the
numbers you are happy to put your name on. No draft leaves `/li-human` with a
number that is not in that file, in the text being answered, or confirmed by
you in chat.

After you post, paste the live URL back. That is when the post is logged to
`~/.claude/linkedin/events.csv`, with the text as you actually published it.
Seven days later you are asked for four numbers from its analytics, and
`/li-audit` works from that log.

## The eleven

| command | what it does |
| --- | --- |
| `/li-post` | One idea into a post. Three hook options from [21 formulas](skills/li-post/hooks.json), one full draft, humanized before you see it. |
| `/li-comment` | Comments on other people's posts. Nine types, picked by what the post actually is. Never "Great post!". |
| `/li-reply` | The thread under your own post. Sorts every comment into lead / substance / peer / support / noise, then writes in that order. |
| `/li-profile` | Scores your profile against a [12-part rubric](skills/li-profile/rubric.json) out of 100, then rewrites in fix-first order. |
| `/li-plan` | The week. What to post, when to post it, and the 10 people to engage with. Writes `~/.claude/linkedin/plan.md`, which `/li-post` and `/li-audit` read, and lists DM follow-ups due. |
| `/li-human` | The humanizer. Two scripts that actually run. See below. |
| `/li-carousel` | Document posts. Slide-by-slide copy, the cover that earns the swipe, and the PDF to upload. |
| `/li-repurpose` | One video, newsletter or transcript into a week of posts that each stand alone. |
| `/li-dm` | The 200-character invite note, the first message, and the two follow-ups. Two. |
| `/li-inbox` | Triages the inbox into lead / recruiter / peer / ask / spam, and tells you which tell gave the sequence away. |
| `/li-audit` | Post-mortem on what you have already published. Ranks by engagement rate and reach multiple, not impressions. |

## The humanizer

`/li-human` ships two Python scripts with no dependencies. They run on your
machine, on your text, and nothing is uploaded.

```bash
python3 humanize.py draft.txt --report      # clean it, show every change
python3 detect.py draft.txt                  # score it, five checks
python3 detect.py before.txt after.txt       # prove the delta
```

**What comes out automatically:**

- **Invisible characters.** Zero-width spaces and joiners, word joiners, soft
  hyphens, byte-order marks, Unicode tag characters, non-breaking and narrow
  spaces. Your keyboard does not make these. They survive copy-paste and they
  are invisible in every editor you own.
- **Typography.** Em dash to comma, en dash to hyphen, curly quotes to
  straight, ellipsis to three dots.
- **The lexicon.** 113 stock words and phrases with plain-English
  replacements - delve, leverage, robust, seamless, crucial, testament to, "in
  today's fast-paced world", "let that sink in" - with capitalisation preserved
  and URLs untouched. It lives in
  [`slop.json`](skills/li-human/slop.json) and it is meant to be edited.

**What gets flagged instead of fixed:** "It's not just X, it's Y", rule-of-three
triads, one-word rhetorical questions, hashtag walls, reflex engagement bait,
uniform sentence length. Changing the shape of a sentence needs judgement, so
those are handed back for a rewrite rather than mangled by a regex.

**The five checks**, scored 0-100, higher is more human:

| check | what it measures |
| --- | --- |
| BURSTINESS | sentence-length variation. Models write even. |
| SPECIFICITY | numbers, names and concrete markers per 100 words |
| SLOP DENSITY | lexicon hits per 100 words |
| FINGERPRINT | invisible characters, em dashes, curly quotes per 1,000 |
| VOICE | contractions, person, structural tells |

The verdict weights the mean at 60% and the **weakest single check** at 40%,
because a detector only needs one signal to fire. SPECIFICITY is shown as
advice and left out of the verdict, so an invented number cannot buy a PASS.
Checks on text too short to judge show `N/A` and are left out too.

Run against a deliberately terrible draft:

```
  BURSTINESS    ##################......  73.0
  SPECIFICITY   ######################## 100.0    (advice, not gated)
  SLOP DENSITY  ........................   0.0    19 stock terms, 24.1 per 100 words
  FINGERPRINT   ........................   0.0    1 invisible, 1 em dash, 3 curly quote
  VOICE         ########................  33.3    3 structural tells
  ------------------------------------------------------------
  HUMAN SCORE   ####....................  15.9   FLAGGED
```

After `humanize.py`, with the flagged structures still unrewritten:

```
  HUMAN SCORE   #################.......  69.7   REVIEW    (+44.9)
```

The last stretch to PASS is the part the script deliberately leaves to you.

## The fine print, which is the honest part

**These skills do not post to LinkedIn, and they should not.** There is no
official API for posting to a personal profile without an approved partner
app, and automating the site with a browser or a third-party tool violates
[LinkedIn's User Agreement](https://www.linkedin.com/legal/user-agreement) and
gets accounts restricted. So every skill here ends the same way: a copy-ready
block, and you paste it. That is not a limitation bolted on afterwards, it is
the design. It is also why the approval gate is real rather than a setting.

**The five checks are local heuristics, not detector APIs.** They are modelled
on the signals public detectors key on, and they run entirely on your machine.
They are not GPTZero, Originality, Copyleaks, Winston or Turnitin, they do not
call those services, and they cannot promise those verdicts. Fixing what they
measure tends to move those numbers, because they are measuring the same
underlying things. That is the whole claim. Nobody can honestly sell you
"undetectable", and anybody who does is selling you something.

**The invisible-character pass is real and it is narrow.** It removes the
zero-width and format characters that end up in generated text and survive a
copy-paste. That is a genuine, checkable fingerprint. It is not a claim about
defeating a cryptographic watermarking scheme, and this repo does not make
one.

**Nothing here fabricates.** No invented metrics, clients or outcomes go under
your name. If a draft needs a number you have not given, it comes back with
`{{your number}}` in it and a flag, every time.

## Files

```
skills/li-post/hooks.json        21 hook formulas: template, example, what it is for, how it gets ruined
skills/li-post/events.py         the publication log: one row per live post or comment, counts at day 7
skills/li-dm/outreach.py         the follow-up ledger: who is due a +4 or +10 follow-up today
skills/li-human/slop.json        the lexicon: 113 terms, 17 invisible classes, 11 structural tells
skills/li-human/humanize.py      the three cleaning passes
skills/li-human/detect.py        the five-check panel
skills/li-human/provenance.py    fails a draft with a number that is not in your ledger
skills/li-profile/rubric.json    the 100-point profile score
templates/voice.md               your voice profile. Fill this in first.
templates/proof.md               your proof ledger: the numbers you stand behind
```

## Credit

Original pack by **Jake Schincariol**
([opusjake.ai](https://opusjake.ai),
[linkedin-agent-skill](https://github.com/Jakeschincariol/linkedin-agent-skill)).
His write-up is at [opusjake.ai/r/linkedin-agent](https://opusjake.ai/r/linkedin-agent).
Go and star his repo.

Fork and adjustments by [niksyarul](https://github.com/niksyarul).

## License

MIT. Take it, change it, ship it.
