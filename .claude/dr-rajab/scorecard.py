#!/usr/bin/env python3
"""Daily accountability scorecard for the agent team.

Usage: python3 .claude/dr-rajab/scorecard.py ledger.json
ledger.json (written by the orchestrator during the run, one entry per agent):
{"date": "2026-11-21",
 "agents": {"creative":  {"assigned": 4, "done": 4, "errors": 0, "rework": 1, "false_claims": 0, "skipped": [], "notes": "..."},
            "humanizer": {...}, "supervisor": {...}, "motivator": {...}, "production": {...}, "archivist": {...}},
 "blockers": ["Gmail connector missing", "..."]}
- errors: tool failures or wrong output caught later; rework: times its output had to be redone;
  false_claims: said "done" without a successful tool result (from the supervisor); skipped: steps not attempted.
Score/100 = 100*done/assigned - 15*errors - 5*rework - 30*false_claims - 10*len(skipped).
Verdict: ممتاز >= 90, مقبول 70-89, متكاسل (skipped or done < assigned), مخطئ (errors or false claims).
"""
import json, sys
from pathlib import Path

NAMES = {"creative": "وكيل الإبداع", "humanizer": "المراجع البشري", "supervisor": "المراقب",
         "motivator": "الوكيل المحفز", "production": "وكيل الإنتاج", "archivist": "وكيل الأرشفة",
         "orchestrator": "المنسق"}

d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
rows = []
for key, a in d["agents"].items():
    assigned = max(a.get("assigned", 0), 1)
    skipped = a.get("skipped", [])
    score = round(100 * a.get("done", 0) / assigned - 15 * a.get("errors", 0) - 5 * a.get("rework", 0)
                  - 30 * a.get("false_claims", 0) - 10 * len(skipped))
    score = max(0, min(100, score))
    if a.get("false_claims") or a.get("errors"):
        verdict = "مخطئ"
    elif skipped or a.get("done", 0) < a.get("assigned", 0):
        verdict = "متكاسل"
    else:
        verdict = "ممتاز" if score >= 90 else "مقبول"
    rows.append((score, NAMES.get(key, key), verdict, a))
rows.sort()
print(f"DATE {d.get('date')}")
for score, name, verdict, a in rows:
    why = []
    if a.get("false_claims"): why.append(f"ادعاء إنجاز بلا دليل ×{a['false_claims']}")
    if a.get("errors"): why.append(f"أخطاء ×{a['errors']}")
    if a.get("skipped"): why.append("تخطى: " + "، ".join(a["skipped"]))
    if a.get("rework"): why.append(f"إعادة عمل ×{a['rework']}")
    print(f"{score:>3}  {name}: {verdict}" + (f" — {'؛ '.join(why)}" if why else ""))
worst = rows[0] if rows else None
if worst and worst[2] in ("مخطئ", "متكاسل"):
    print(f"WORST {worst[1]} ({worst[2]})")
best = rows[-1] if rows else None
if best:
    print(f"BEST {best[1]} ({best[0]})")
for b in d.get("blockers", []):
    print(f"BLOCKER {b}")
