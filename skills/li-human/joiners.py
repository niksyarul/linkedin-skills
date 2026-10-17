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
