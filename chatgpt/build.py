#!/usr/bin/env python3
"""Build the ChatGPT pack from skills/: skills.md (every SKILL.md in one file)
and tools.zip (the humanizer scripts and the JSON they read).

  python3 chatgpt/build.py

Run it after editing anything under skills/, then commit both outputs.
"""
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
OUT = os.path.join(ROOT, "chatgpt")
TOOLS = [
    "li-human/humanize.py", "li-human/detect.py", "li-human/joiners.py",
    "li-human/provenance.py", "li-human/slop.json", "li-human/artefacts-only.json",
    "li-post/hooks.json", "li-profile/rubric.json",
]

# instructions.md goes first, so skills.md alone works dropped into any chat.
parts = [open(os.path.join(OUT, "instructions.md"), encoding="utf-8").read()]
for name in sorted(os.listdir(SKILLS)):
    path = os.path.join(SKILLS, name, "SKILL.md")
    if os.path.exists(path):
        parts.append(open(path, encoding="utf-8").read())
with open(os.path.join(OUT, "skills.md"), "w", encoding="utf-8") as fh:
    fh.write("\n\n---\n\n".join(parts))

# Fixed timestamps so an unchanged build gives a byte-identical zip.
with zipfile.ZipFile(os.path.join(OUT, "tools.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    for rel in TOOLS:
        info = zipfile.ZipInfo("tools/" + os.path.basename(rel), (2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, open(os.path.join(SKILLS, rel), "rb").read())
# Copy instructions.md into the README box people paste from.
readme_path = os.path.join(ROOT, "README.md")
readme = open(readme_path, encoding="utf-8").read()
head, rest = readme.split("<!-- instructions:start -->\n", 1)
_, tail = rest.split("<!-- instructions:end -->", 1)
with open(readme_path, "w", encoding="utf-8") as fh:
    fh.write(head + "<!-- instructions:start -->\n```text\n" + parts[0].rstrip()
             + "\n```\n<!-- instructions:end -->" + tail)
print("wrote chatgpt/skills.md, chatgpt/tools.zip and the README instructions")
