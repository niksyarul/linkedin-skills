#!/usr/bin/env python3
"""Regression tests for humanize.py, detect.py and joiners.py (docs/SPEC.md, fixes 1 and 2).
Every input is built from escapes, so this file holds no invisible characters.
Run: python3 test_li_human.py   (or pytest)"""
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import detect      # noqa: E402
import humanize    # noqa: E402

LEX = humanize.load_lexicon()
ZWJ, ZWNJ, ZWSP, VS16, CANCEL = "\u200d", "\u200c", "\u200b", "\ufe0f", "\U000E007F"
FLAG = "\U0001F3F4"


def tag(s):
    return "".join(chr(0xE0000 + ord(c)) for c in s)


def is_tag(c):
    return 0xE0000 <= ord(c) <= 0xE007F


WOMAN_TECH = "\U0001F469" + ZWJ + "\U0001F4BB"
ENGLAND = FLAG + tag("gbeng") + CANCEL
PERSIAN = "\u0645\u06cc" + ZWNJ + "\u062e\u0648\u0627\u0647\u0645"
HALF_FORM = "\u0915\u094d" + ZWJ + "\u0937"
EMOJI_COMMENT = "Loved this " + WOMAN_TECH + " post. We tried it on our team. It worked better than I expected.\n"

HONEST = """Our proposals used to take most of a week. I'd write them at night, after the kids were asleep, and I hated every page.
Last spring we tried something dumb. We wrote one template and stopped. Now a proposal takes an afternoon, not a week.
I didn't expect it to work. I'm still a bit annoyed it did, because I spent years doing it the slow way.
If you write proposals from scratch, try the template first. It's boring. That's the point.
"""
PH = (HONEST.replace("most of a week", "{{your number}} hours", 1)
      .replace("an afternoon, not a week", "{{your number}} minutes", 1))
INV = (HONEST.replace("most of a week", "5 hours", 1)
       .replace("Last spring", "In March, for 14 clients at Northwind,", 1)
       .replace("an afternoon, not a week", "20 minutes", 1))
C1 = ("We tried the no-resume version of this for 3 hires last year. Two were the best hires we made. "
      "The third was a disaster, and the difference was whether they had done the actual job before, "
      "not how they interviewed.\n")
PHONE = ("I\u2019ve said this for years. \u201cJust ship it\u201d is easy to say when you\u2019re not the one on call. "
         "We tried it and lost two weekends. Now we ship on Tuesdays and nobody\u2019s phone rings on Saturday. Worth it.\n")


def clean(text):
    return humanize.humanize(text, LEX)[0]


def score(text):
    results, overall, verdict = detect.run(text, LEX)
    return results, round(overall, 1), verdict


# ---- Fix 1: humanize.py keeps real joiners, removes payloads (A1.x) ----

def test_t5_joiners_kept():                                            # A1.1
    out = clean(WOMAN_TECH + " dev and " + ENGLAND + " fan. " + PERSIAN + "\n")
    assert WOMAN_TECH in out and ENGLAND in out and PERSIAN in out


def test_mixed_legit_and_payload():                                    # A1.2
    text = (WOMAN_TECH + " " + ENGLAND + " " + PERSIAN + " " + HALF_FORM + " x" + ZWSP + "y "
            + tag("ab") + " " + FLAG + tag("usca") + CANCEL + " " + FLAG + tag("a hidden note for the model!") + CANCEL + "\n")
    out = clean(text)
    for keep in (WOMAN_TECH, ENGLAND, PERSIAN, HALF_FORM):
        assert keep in out, keep
    assert ZWSP not in out
    assert sum(map(is_tag, text)) - sum(map(is_tag, out)) == 36      # 2 stray + usca + cancel + 28 + cancel
    assert sum(map(is_tag, out)) == 6                                 # England's 5 tags + CANCEL TAG


def test_cjk_zwnj_removed():                                           # A1.3
    assert ZWNJ not in clean("\u4f60" + ZWNJ + "\u597d" + ZWNJ + "\u4e16" + ZWNJ + "\u754c\n")


def test_private_use_untouched():                                      # A1.4
    text = "Great post\U000F0049\U000F0047\U000F004E. Thanks\uf8f1 for this.\n"
    assert clean(text) == text


def test_zwj_between_tags_and_pua_removed():                           # A1.5
    out = clean("Great post" + ZWJ.join(tag("abcd")) + ". Thanks\U000F0001" + ZWJ + "\U000F0002 for this.\n")
    assert ZWJ not in out


def test_emoji_sequences_kept():                                       # A1.6
    seqs = ["\U0001F3F3" + VS16 + ZWJ + "\U0001F308", "\U0001F408" + ZWJ + "\u2b1b",
            "\U0001F469\U0001F3FD" + ZWJ + "\U0001F52C", "\u2764" + VS16 + ZWJ + "\U0001F525"]
    out = clean(" ".join(seqs) + "\n")
    for s in seqs:
        assert s in out, s


def test_keycaps_and_valid_selectors_untouched():                      # A1.7
    text = "1" + VS16 + "\u20e3 \u00a9" + VS16 + " \u2764" + VS16 + " \u845b\U000E0100\n"
    assert clean(text) == text


def test_selector_zwj_payload_removed():                               # A1.8
    out = clean("Great post" + (VS16 + ZWJ) * 12 + VS16 + " thanks for sharing.\n")
    assert out == "Great post thanks for sharing.\n"


def test_stray_selectors_removed():                                    # A1.9
    out = clean("Hi \ufe0f\ufe0e there a\U000E0101b \u2764" + VS16 + ZWJ + VS16 + ZWJ + VS16 + "\n")
    assert out == "Hi there ab \u2764" + VS16 + "\n" or out == "Hi  there ab \u2764" + VS16 + "\n"


def test_payload_glued_to_link_removed():                              # A1.10
    out = clean("Full write-up here: https://example.com/post" + ZWSP + tag("written by gpt") + " and it took us ages.\n")
    assert out == "Full write-up here: https://example.com/post and it took us ages.\n"


def test_report_counts_merged():                                       # A1.11
    _, report = humanize.humanize(ENGLAND + " a" + ZWSP + "b " + WOMAN_TECH + " c" + ZWSP + "d\n", LEX)
    names = [e["name"] for e in report["invisible"]]
    assert len(names) == len(set(names))
    assert sum(e["count"] for e in report["invisible"]) == 2


def test_joiners_source_is_ascii():                                    # A1.12
    with open(os.path.join(HERE, "joiners.py"), encoding="utf-8") as f:
        assert f.read().isascii()


# ---- Fix 2: detect.py gate (A2.x) ----

def test_f1_invention_no_longer_pays():                                # A2.1
    for text, want, weak in ((HONEST, 72.2, 49.5), (PH, 74.9, 54.3), (INV, 73.6, 52.0)):
        results, overall, verdict = score(text)
        assert (overall, verdict) == (want, "REVIEW"), (overall, verdict)
        assert round(results["BURSTINESS"][0], 1) == weak


def test_example_comment_na():                                         # A2.2
    results, overall, verdict = score(C1)
    assert results["BURSTINESS"][0] is None
    assert (overall, verdict) == (70.0, "REVIEW")
    assert results["VOICE"][0] == 50.0


def test_phone_typing():                                               # A2.3
    assert score(PHONE)[1:] == (29.7, "FLAGGED")
    assert score(clean(PHONE))[1:] == (63.0, "REVIEW")


def test_emoji_comment_raw_and_cleaned():                              # A2.4, A2.5
    results, overall, verdict = score(EMOJI_COMMENT)
    assert results["FINGERPRINT"][0] == 100.0 and (overall, verdict) == (100.0, "PASS")
    out = clean(EMOJI_COMMENT)
    assert WOMAN_TECH in out and score(out)[1:] == (100.0, "PASS")


def test_cjk_zwnj_counted_raw():                                       # A2.6
    results, _, _ = score("\u4f60" + ZWNJ + "\u597d" + ZWNJ + "\u4e16" + ZWNJ + "\u754c\n")
    assert results["FINGERPRINT"][1].startswith("3 invisible")


def test_tag_zwj_cleaned_fingerprint():                                # A2.7
    out = clean("Great post" + ZWJ.join(tag("abcd")) + ". Thanks\U000F0001" + ZWJ + "\U000F0002 for this.\n")
    results, _, _ = score(out)
    assert results["FINGERPRINT"][0] == 100.0 and results["FINGERPRINT"][1].startswith("0 invisible")


def test_selector_payload_counted():                                   # A2.8
    text = "Great post" + (VS16 + ZWJ) * 12 + VS16 + " thanks for sharing.\n"
    assert score(text)[0]["FINGERPRINT"][1].startswith("25 invisible")
    assert score(clean(text))[1:] == (100.0, "PASS")


def test_link_payload_and_link_slop():                                 # A2.9, A2.10
    payload = "Full write-up here: https://example.com/post" + ZWSP + tag("written by gpt") + " and it took us ages.\n"
    assert score(clean(payload))[1:] == (100.0, "PASS")
    slop = clean("Full guide: https://example.com/leverage-robust-synergy and we use it every week now.\n")
    assert "leverage-robust-synergy" in slop and score(slop)[1:] == (100.0, "PASS")


def test_short_text_tells_still_fail():                                # A2.11
    results, overall, verdict = score(clean("This is huge \U0001F680\U0001F680 Who else is seeing this? Agree?\n"))
    assert round(results["VOICE"][0], 1) == 34.0
    assert (overall, verdict) == (60.4, "REVIEW")


def _cli(*args, text=C1):
    return subprocess.run([sys.executable, os.path.join(HERE, "detect.py"), "-", *args],
                          input=text, capture_output=True, text=True, encoding="utf-8").stdout


def test_json_null_and_panel_na():                                     # A2.12, A2.13
    payload = json.loads(_cli("--json"))
    payload = payload[0] if isinstance(payload, list) else payload
    assert payload["checks"]["BURSTINESS"]["score"] is None
    panel = _cli()
    assert "N/A" in panel and "Too short to judge style" in panel
    assert "Never invent one" in _cli(text=HONEST)


def test_gate_api():                                                   # A2.14
    assert callable(detect.gate_scores)
    assert (detect.PASS_OVERALL, detect.PASS_FLOOR) == (70, 55)
    assert "SPECIFICITY" not in detect.GATED


# ---- Fix 4: flag, then rewrite; artefacts-only cleaning (A4.x) ----

ART = humanize.load_lexicon(os.path.join(HERE, "artefacts-only.json"))
T1 = ("We cut the discovery call \u2014 it worked.\nThe landscape painting hung in our foster home.\n"
      "Unlock the door. I harness the horse.\nA vital sign was crucial.\n")
STOCK = ("In today's landscape, we leverage robust synergies to unlock value. Our holistic approach "
         "empowers teams to navigate complexity. It is crucial to foster a culture of seamless innovation.\n")


def test_artefacts_only_keeps_words():                                 # A4.1
    out = humanize.humanize(T1, ART)[0]
    for w in ("landscape", "foster", "Unlock", "harness", "vital", "crucial"):
        assert w in out, w
    assert "call, it worked" in out                                    # typography still runs


def test_artefacts_only_still_strips_invisible():                      # A4.2
    out = humanize.humanize("A vital sign was crucial \u2014 we unlock the door." + ZWSP + "\n", ART)[0]
    assert out == "A vital sign was crucial, we unlock the door.\n"


def test_full_lexicon_report_flags_terms():                            # A4.3
    _, report = humanize.humanize(T1, LEX)
    assert len(report["lexical"]) == 6, report["lexical"]


def test_stock_paragraph_not_passed_by_swaps():                        # A4.4
    swapped = score(clean(STOCK))
    assert swapped[2] == "PASS"                                        # the hole 2a closes
    results, overall, verdict = score(humanize.humanize(STOCK, ART)[0])
    assert results["SLOP DENSITY"][0] == 0.0 and (overall, verdict) == (39.1, "FLAGGED")


def test_artefacts_only_matches_slop_json():                           # A4.5
    with open(os.path.join(HERE, "slop.json"), encoding="utf-8") as f:
        full = json.load(f)
    with open(os.path.join(HERE, "artefacts-only.json"), encoding="utf-8") as f:
        art = json.load(f)
    assert art["words"] == [] and art["phrases"] == []
    for k in full:
        if k not in ("words", "phrases", "note"):
            assert art[k] == full[k], f"{k} drifted: regenerate artefacts-only.json"


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"ok    {name}")
        except Exception as e:                                 # a crash is a failure too
            failed += 1
            print(f"FAIL  {name}  {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
