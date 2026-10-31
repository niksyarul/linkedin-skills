#!/usr/bin/env python3
"""Build chatgpt/skills.md: the instructions, every SKILL.md, then the data
files and humanizer scripts, so one file works dropped into any chat.

  python3 chatgpt/build.py

Run it after editing anything under skills/ or chatgpt/instructions.md, then
commit skills.md and README.md.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
OUT = os.path.join(ROOT, "chatgpt")
TOOLS = [
    "li-post/hooks.json", "li-profile/rubric.json", "li-human/slop.json",
    "li-human/artefacts-only.json", "li-human/humanize.py", "li-human/detect.py",
    "li-human/joiners.py", "li-human/provenance.py",
]

read = lambda p: open(p, encoding="utf-8").read()

# instructions.md goes first, so skills.md alone works dropped into any chat.
parts = [read(os.path.join(OUT, "instructions.md"))]

# A chat that cannot run code skims a JSON file at the end. Put the lexicon up
# front as plain lines, longest phrase first so "in today's fast-paced world"
# wins over "fast-paced".
lex = json.loads(read(os.path.join(SKILLS, "li-human/slop.json")))
swaps = sorted(lex["phrases"] + lex["words"], key=lambda e: -len(e["find"]))
sheet = ["# Humanizer cheat sheet\n\nThe same rules as slop.json. Check the text "
         "against every line.\n\n## Swap these (whole phrase, any capitalisation)\n"]
sheet += [f"- {e['find']} -> {e['replace'] or '(delete)'}" for e in swaps]
sheet += ["\n## Characters\n"]
sheet += [f"- {e['name']} ({e['from']}) -> {e['to']!r}" for e in lex["typographic"]]
sheet += ["- Any zero-width or invisible character -> (delete)",
          "\n## Structural tells: rewrite by hand\n"]
sheet += [f"- {e['name']}: {e['fix']}" for e in lex["structures"]]
parts.append("\n".join(sheet))

for name in sorted(os.listdir(SKILLS)):
    path = os.path.join(SKILLS, name, "SKILL.md")
    if os.path.exists(path):
        # The data folder is a Claude Code path; in a chat these are attachments.
        parts.append(read(path).replace("~/.claude/linkedin/", ""))

# Four-backtick fences: none of these files contain one, and a ``` inside a
# script cannot end the block early. The marker line is what the extract
# snippet in instructions.md looks for.
files = ["# Files\n\nThe data and scripts the skills use, byte for byte."]
for rel in TOOLS:
    name = os.path.basename(rel)
    body = read(os.path.join(SKILLS, rel))
    assert "````" not in body, name
    lang = "json" if name.endswith(".json") else "python"
    files.append(f"<!-- file: {name} -->\n````{lang}\n{body.rstrip(chr(10))}\n````")
parts.append("\n\n".join(files))

with open(os.path.join(OUT, "skills.md"), "w", encoding="utf-8") as fh:
    fh.write("\n\n---\n\n".join(parts) + "\n")

# Copy instructions.md into the README box people paste from.
readme_path = os.path.join(ROOT, "README.md")
readme = read(readme_path)
head, rest = readme.split("<!-- instructions:start -->\n", 1)
_, tail = rest.split("<!-- instructions:end -->", 1)
with open(readme_path, "w", encoding="utf-8") as fh:
    fh.write(head + "<!-- instructions:start -->\n```text\n" + parts[0].rstrip()
             + "\n```\n<!-- instructions:end -->" + tail)
print("wrote chatgpt/skills.md and the README instructions")
