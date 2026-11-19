#!/usr/bin/env python3
"""Score creative ideas against the goals (ICE + safety gate).

Usage: python3 .claude/creative/score_ideas.py ideas.json
ideas.json: [{"title": "...", "hook": "...", "format": "doctor_video|motion_video|post|reel|series",
              "goal": "tiktok|facebook|whatsapp", "impact": 1-5, "confidence": 1-5, "ease": 1-5,
              "needs_doctor": true, "text": "script or caption (optional)"}]
Score = impact*2 + confidence + ease, +2 if doctor on camera for TikTok, -3 if the hook is > 12 words.
Any medical-risk phrase (from the humanizer list) disqualifies the idea. Prints ideas best-first.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RISK = json.loads((ROOT / "humanizer" / "phrases.json").read_text(encoding="utf-8"))["medical_risk"]

ideas = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
rows = []
for i in ideas:
    blob = (i.get("hook", "") + " " + i.get("text", "")).lower()
    bad = [p for p in RISK if p.lower() in blob]
    s = i.get("impact", 0) * 2 + i.get("confidence", 0) + i.get("ease", 0)
    if i.get("goal") == "tiktok" and i.get("needs_doctor"):
        s += 2
    if len(i.get("hook", "").split()) > 12:
        s -= 3
    rows.append((-1 if bad else s, i, bad))
rows.sort(key=lambda r: r[0], reverse=True)
for s, i, bad in rows:
    flag = f"  DISQUALIFIED: {bad}" if bad else ""
    print(f"{s:>3}  [{i.get('goal')}/{i.get('format')}] {i.get('title')} — «{i.get('hook')}»{flag}")
