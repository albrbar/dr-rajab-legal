#!/usr/bin/env python3
"""Humanizer checker: flags machine-sounding patterns in Arabic/English copy.

Usage:
  python3 .claude/humanizer/humanize_check.py FILE [FILE...]   # .txt .md .html .srt
  echo "text" | python3 .claude/humanizer/humanize_check.py -
  add --json for machine-readable output.
Exit code: 0 = PASS (score >= 75), 1 = needs rewrite.
"""
import json, re, statistics, sys
from html import unescape
from pathlib import Path

HERE = Path(__file__).parent
PHRASES = json.loads((HERE / "phrases.json").read_text(encoding="utf-8"))

EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\u2705\u274C\u26A0]")
SENT_SPLIT = re.compile(r"(?<=[\.\!\?؟!…])\s+|\n+")
WORD = re.compile(r"[\w\u0600-\u06FF]+")


def load(arg):
    raw = sys.stdin.read() if arg == "-" else Path(arg).read_text(encoding="utf-8")
    if arg.endswith((".html", ".htm")):
        raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
        raw = re.sub(r"(?s)<[^>]+>", "\n", raw)
    if arg.endswith(".srt"):
        raw = re.sub(r"(?m)^\d+\s*$|^\d\d:\d\d:\d\d,\d+ --> .*$", "", raw)
    return unescape(raw)


def check(text):
    findings, penalty = [], 0
    words = WORD.findall(text)
    n = max(len(words), 1)
    low = text.lower()

    def add(sev, rule, detail, cost):
        nonlocal penalty
        penalty += cost
        findings.append({"severity": sev, "rule": rule, "detail": detail})

    for group, cost, sev in (("ai_cliches_ar", 6, "high"), ("ai_cliches_en", 6, "high"),
                             ("marketing_fluff", 4, "medium"), ("medical_risk", 15, "critical")):
        for p in PHRASES[group]:
            c = low.count(p.lower())
            if c:
                add(sev, group, f"«{p}» ×{c}", cost * c)

    dashes = text.count("—") + text.count(" – ")
    if dashes > max(2, n / 120):
        add("medium", "dash_overuse", f"{dashes} long dashes in {n} words", 5)

    emojis = EMOJI.findall(text)
    if len(emojis) > max(3, n / 35):
        add("medium", "emoji_density", f"{len(emojis)} emoji in {n} words", 6)

    tags = re.findall(r"#\S+", text)
    if len(tags) > 4:
        add("low", "hashtag_stuffing", f"{len(tags)} hashtags (human posts rarely exceed 3-4)", 3)

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    bullets = [l for l in lines if re.match(r"^([\-\*•✅✔️▪️]|\d+[\.\)]\s)", l)]
    if lines and len(bullets) / len(lines) > 0.5 and len(bullets) >= 5:
        add("medium", "list_heavy", f"{len(bullets)}/{len(lines)} lines are bullets: reads like a template", 6)
    starts = [l.split()[0] for l in bullets if l.split()]
    if len(starts) >= 4 and len(set(starts)) == 1:
        add("medium", "uniform_bullets", f"every bullet starts with «{starts[0]}»", 4)

    sents = [s for s in SENT_SPLIT.split(text) if len(WORD.findall(s)) >= 3]
    if len(sents) >= 5:
        lens = [len(WORD.findall(s)) for s in sents]
        cv = statistics.pstdev(lens) / statistics.mean(lens)
        if cv < 0.35:
            add("medium", "flat_rhythm", f"sentence-length variation {cv:.2f} (<0.35 = monotone)", 6)

    triads = len(re.findall(r"[\u0600-\u06FF\w]+،\s*[\u0600-\u06FF\w]+،?\s*و[\u0600-\u06FF\w]+", text))
    if triads >= 3:
        add("low", "rule_of_three", f"{triads} three-item lists (A، B، وC)", 3)

    if re.search(r"(?m)^(في الختام|ختامًا|ختاما|خلاصة القول|In conclusion)", text):
        add("high", "essay_closer", "formulaic conclusion opener", 6)

    score = max(0, 100 - penalty)
    return {"score": score, "verdict": "PASS" if score >= 75 else "REWRITE",
            "words": n, "findings": findings}


def main():
    args = [a for a in sys.argv[1:] if a != "--json"]
    if not args:
        print(__doc__); sys.exit(2)
    worst = 100
    for a in args:
        r = check(load(a)); worst = min(worst, r["score"])
        if "--json" in sys.argv:
            print(json.dumps({"file": a, **r}, ensure_ascii=False, indent=2))
        else:
            print(f"== {a}: {r['score']}/100 {r['verdict']} ({r['words']} words)")
            for f in r["findings"]:
                print(f"  [{f['severity']}] {f['rule']}: {f['detail']}")
    sys.exit(0 if worst >= 75 else 1)


if __name__ == "__main__":
    main()
