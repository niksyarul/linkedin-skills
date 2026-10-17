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
