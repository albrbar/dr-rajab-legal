#!/usr/bin/env python3
"""Supervisor audit for Metricool posts.

Usage: save the JSON returned by Metricool getScheduledPosts to a file, then
  python3 .claude/supervisor/audit_posts.py posts.json [--now 2026-11-20T01:00]
Checks every post against the clinic's publishing rules and runs the humanizer
checker on its text. Exit 1 if any post has a BLOCKER.
"""
import json, re, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "humanizer"))
from humanize_check import check  # noqa: E402

LANDING = "albrbar.github.io/dr-rajab-legal"
DISCLAIMER = re.compile(r"لا يغني عن|للتوعية العامة")
PHONES = {"0910104477", "0931210939", "0918410755", "0926162193",
          "218910104477", "218931210939", "218918410755", "218926162193"}
NEEDS_MEDIA = {"tiktok", "youtube", "instagram", "pinterest"}


def audit(post, now):
    out = []
    def add(level, msg): out.append((level, msg))
    text = post.get("text", "") or ""
    nets = {p["network"] for p in post.get("providers", [])}
    when = post.get("publicationDate", {}).get("dateTime", "")
    if not text.strip():
        add("BLOCKER", "empty text")
    if LANDING not in text:
        add("WARN", "no landing-page link")
    if not DISCLAIMER.search(text):
        add("BLOCKER", "medical disclaimer missing")
    for num in re.findall(r"\+?\d{9,12}", text):
        if num.lstrip("+") not in PHONES:
            add("BLOCKER", f"unknown phone number {num}")
    if nets & NEEDS_MEDIA and not post.get("media"):
        add("BLOCKER", f"{sorted(nets & NEEDS_MEDIA)} require media")
    if when and now and when < now:
        add("WARN", f"publication time {when} is in the past")
    if not post.get("draft") and post.get("autoPublish", True) and "humanizer-ok" not in json.dumps(post, ensure_ascii=False):
        add("INFO", "auto-publishing post: confirm humanizer review happened")
    h = check(text)
    for f in h["findings"]:
        add("BLOCKER" if f["severity"] == "critical" else "WARN" if f["severity"] == "high" else "INFO",
            f"humanizer {f['rule']}: {f['detail']}")
    if h["score"] < 75:
        add("BLOCKER", f"humanizer score {h['score']} < 75")
    return h["score"], out


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    posts = data.get("data", data) if isinstance(data, dict) else data
    now = sys.argv[sys.argv.index("--now") + 1] if "--now" in sys.argv else datetime.now().strftime("%Y-%m-%dT%H:%M")
    blocked = False
    for p in posts:
        score, res = audit(p, now)
        nets = ",".join(x["network"] for x in p.get("providers", []))
        state = "DRAFT" if p.get("draft") else "SCHEDULED"
        print(f"== post {p.get('id')} [{state}] {nets} @ {p.get('publicationDate', {}).get('dateTime')} humanizer={score}")
        for level, msg in res:
            print(f"   {level}: {msg}")
            blocked |= level == "BLOCKER"
    sys.exit(1 if blocked else 0)


if __name__ == "__main__":
    main()
