#!/usr/bin/env python3
"""Goal pace calculator for the motivator agent.

Usage:
  python3 .claude/motivator/pace.py --today 2026-11-21 \
      --metric "TikTok:current=2600,gain7=120,target=10000" \
      --metric "Facebook:current=640,gain7=40,target=2000" \
      --metric "WhatsApp/week:current=12,target=30,weekly" \
      --metric "Patients/week:current=3,target=10,weekly"
Defaults: deadline 2027-02-17. Status: ON_TRACK >= 90% of required pace,
AT_RISK 50-90%, OFF_TRACK < 50%. Exit 1 if any metric is OFF_TRACK.
"""
import argparse, math, sys
from datetime import date, timedelta

p = argparse.ArgumentParser()
p.add_argument("--today", default=date.today().isoformat())
p.add_argument("--deadline", default="2027-02-17")
p.add_argument("--metric", action="append", required=True)
a = p.parse_args()
today, deadline = date.fromisoformat(a.today), date.fromisoformat(a.deadline)
days_left = max((deadline - today).days, 1)
worst = "ON_TRACK"
print(f"Days left to {deadline}: {days_left}\n")
print(f"{'metric':<16}{'now':>8}{'target':>8}{'need/day':>10}{'actual/day':>12}{'pace%':>8}  status     projection")
for m in a.metric:
    name, kv = m.split(":", 1)
    parts = dict(x.split("=") if "=" in x else (x, "1") for x in kv.split(","))
    cur, tgt = float(parts["current"]), float(parts["target"])
    if "weekly" in parts:  # rate goal: compare this week's count with the weekly target
        pct = 100 * cur / tgt if tgt else 0
        need, act, proj = tgt / 7, cur / 7, "weekly goal"
    else:
        gain7 = float(parts.get("gain7", 0))
        need = max(tgt - cur, 0) / days_left
        act = gain7 / 7
        pct = 100 if need == 0 else 100 * act / need
        proj = (today + timedelta(days=math.ceil((tgt - cur) / act))).isoformat() if act > 0 and cur < tgt else ("reached" if cur >= tgt else "never at current pace")
    status = "ON_TRACK" if pct >= 90 else "AT_RISK" if pct >= 50 else "OFF_TRACK"
    if status == "OFF_TRACK" or (status == "AT_RISK" and worst == "ON_TRACK"):
        worst = status
    print(f"{name:<16}{cur:>8.0f}{tgt:>8.0f}{need:>10.1f}{act:>12.1f}{pct:>7.0f}%  {status:<10} {proj}")
print(f"\nOVERALL: {worst}")
sys.exit(1 if worst == "OFF_TRACK" else 0)
