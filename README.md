# LinkedIn skills

**Install for the AI you use:**
[ChatGPT](#chatgpt-project-or-custom-gpt) ·
[Gemini](#gemini-gem) ·
[Claude Code](#claude-code) ·
[Gemini CLI](#gemini-cli) ·
[Codex](#codex-and-chatgpt-desktop) ·
[any chat, one file](#any-chat-app-one-file)

Eleven skills that run a LinkedIn account, in ChatGPT, Gemini, Claude and
Codex. Free, MIT, no signup, no API key, nothing to connect.

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

### Claude Code

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
most of the point of `/li-human`, but the rest works. Or use the
[one-file version](#any-chat-app-one-file), which has all eleven.

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

### Any chat app (one file)

Works in a normal ChatGPT, Gemini or Claude chat, free accounts included.
The file carries all eleven skills, the 21 hook formulas, the profile rubric,
the slop lexicon and the humanizer scripts. Where the chat can run Python,
it runs the scripts. Where it can't, it applies the same rules by hand.

1. **[Download skills.md](https://github.com/niksyarul/linkedin-skills/releases/latest/download/skills.md)**
2. Start a new chat, attach `skills.md`, and type what you want: "write a
   LinkedIn post about the client we lost", "humanize this", "score my profile".

Do this once per chat. To set it up once and keep it, use a ChatGPT Project
or a Gemini Gem below.

### ChatGPT Project or custom GPT

1. **[Download skills.md](https://github.com/niksyarul/linkedin-skills/releases/latest/download/skills.md)**
2. In ChatGPT, click **Projects**, then **New project**, and name it "LinkedIn".
3. Open the project settings and paste [the instructions](#the-instructions)
   into **Instructions**.
4. Add `skills.md` to the project files.
5. Start a chat inside the project and ask in plain words: "write a LinkedIn
   post about the client we lost", "humanize this", "score my profile", "plan
   my week".

A custom GPT works the same way: paste the instructions, upload `skills.md`
under **Knowledge**, and switch on **Code Interpreter**. A GPT can be shared
as a link, so other people only have to click it.

What you lose in ChatGPT: nothing carries over between chats, so the post log
and the DM follow-up ledger can't be kept for you. When a skill would log
something, ChatGPT gives you the line to save yourself. If ChatGPT can't run
the scripts, it checks the draft by hand and says the scores are estimates.

### Gemini Gem

1. **[Download skills.md](https://github.com/niksyarul/linkedin-skills/releases/latest/download/skills.md)**
2. Go to [gemini.google.com](https://gemini.google.com), open **Gems**, then
   **New Gem**, and name it "LinkedIn".
3. Paste [the instructions](#the-instructions) into **Instructions**.
4. Under **Knowledge**, add `skills.md`.
5. Save, then chat with the Gem in plain words.

Gems can't run the scripts, so Gemini checks drafts by hand and says the
scores are estimates. A saved Gem can be shared as a link.

### The instructions

Click the copy button on the box, then paste it into your Project, GPT or Gem.

<!-- instructions:start -->
```text
You run a LinkedIn account for the user with eleven skills. The full
instructions for every skill are in `skills.md`, one section per skill, each
starting with `# li-<name>`. Before answering, read the section that fits the
request and follow it exactly.

Pick the skill from what the user asks. They may type the command or just
describe the job:

- li-post: write a post, a hook, "post about X"
- li-comment: comment on someone else's post
- li-reply: answer the comments under the user's own post
- li-profile: score or rewrite a profile, headline, about section
- li-plan: plan the week, content calendar, "what should I post"
- li-human: humanize a draft, "does this sound like AI", remove em dashes
- li-carousel: carousel or document post
- li-repurpose: turn a video, newsletter or transcript into posts
- li-dm: connection note, DM, follow-up
- li-inbox: triage DMs and connection requests
- li-audit: read past posts or analytics, "what's working"

If the request is unclear, list these in one line each and ask which one.

The skills were written for a desktop agent. In this chat app, adapt them like this:

1. The user's files. `voice.md` (their voice), `proof.md` (numbers they stand
   behind) and `plan.md` (this week's plan) are files the user attaches to the
   chat. If one is missing, carry on without it and say once that attaching it
   gives better drafts.
2. Data and scripts. The `# Files` section at the end of `skills.md` holds
   hooks.json (the 21 hook formulas), rubric.json (the profile score),
   slop.json (the lexicon) and the humanizer scripts, each after a
   `<!-- file: name -->` line. When a skill reads one of the JSON files, use
   that copy. When a skill says to run a script and you can run Python,
   extract the files first, then run the script as the skill says:

       import re, pathlib
       src = next(p for d in ("/mnt/data", ".") for p in pathlib.Path(d).glob("skills*.md")).read_text(encoding="utf-8")
       for name, body in re.findall(r"<!-- file: (\S+) -->\n````\w*\n(.*?)\n````", src, re.S):
           pathlib.Path(name).write_text(body + "\n", encoding="utf-8")

   Show the user the score output. If you cannot run code, apply slop.json and
   the scoring rules in detect.py by hand, and say the scores are estimates.
3. Logs. events.py and outreach.py are not available, because nothing here is
   kept between chats. When a skill says to log a post or a follow-up, give the
   user the row to keep instead (date, URL, what was sent, when to follow up).
   If they paste such rows back later, use them.
4. Proof. Never put a number, client or result in a draft unless it is in
   `proof.md`, in the text the user pasted, or confirmed by the user in this
   chat. Otherwise write `{{your number}}` and flag it.
5. Posting. You never post anything. Every skill ends with a copy-ready block
   that the user pastes into LinkedIn.

Every draft goes through li-human before the user sees it.
```
<!-- instructions:end -->

### Make it sound like you

Optional, works in every chat app. Download
**[voice.md](https://github.com/niksyarul/linkedin-skills/releases/latest/download/voice.md)** and **[proof.md](https://github.com/niksyarul/linkedin-skills/releases/latest/download/proof.md)**, fill them in, and
attach them to the chat or add them to your Project or Gem. Don't add them to
a GPT or Gem you share: anyone using it can get the AI to read them out.

Maintainers: after editing anything under `skills/` or
`chatgpt/instructions.md`, run `python3 chatgpt/build.py`. On each release,
attach the files with
`gh release upload <tag> chatgpt/skills.md templates/voice.md templates/proof.md`
so the download links above keep working.

### Codex and ChatGPT desktop

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
