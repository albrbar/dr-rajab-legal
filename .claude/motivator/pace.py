#!/usr/bin/env python3
"""Goal pace calculator for the motivator agent.

Usage:
  python3 .claude/motivator/pace.py --today 2026-11-21 \
      --metric "TikTok:current=2600,gain7=120 " \
      --metric "Facebook:current=640,gain7=40" \
      --metric "WhatsApp/week:current=12,weekly" \
      --metric "Patients/week:current=3,weekly"
Targets default to the current milestone (2027-01-01: TikTok 5700, Facebook 1200,
WhatsApp 15/wk, Patients 5/wk; 2027-03-01: 10000, 2000, 30/wk, 10/wk); target= overrides. Status: ON_TRACK >= 90% of required pace,
AT_RISK 50-90%, OFF_TRACK < 50%. Exit 1 if any metric is OFF_TRACK.
"""
import argparse, math, sys
from datetime import date, timedelta

p = argparse.ArgumentParser()
p.add_argument("--today", default=date.today().isoformat())
p.add_argument("--deadline", default=None, help="override; default = next milestone (2027-01-01, then 2027-03-01)")
p.add_argument("--metric", action="append", required=True)
a = p.parse_args()
today = date.fromisoformat(a.today)
# Milestone targets: (deadline, TikTok, Facebook, WhatsApp/week, Patients/week)
MILESTONES = [(date(2027, 1, 1), 5700, 1200, 15, 5), (date(2027, 3, 1), 10000, 2000, 30, 10)]
ms = next((m for m in MILESTONES if m[0] >= today), MILESTONES[-1])
deadline = date.fromisoformat(a.deadline) if a.deadline else ms[0]
DEFAULT_TARGET = {"tiktok": ms[1], "facebook": ms[2], "whatsapp/week": ms[3], "patients/week": ms[4]}
days_left = max((deadline - today).days, 1)
worst = "ON_TRACK"
print(f"Milestone {deadline}: TikTok {ms[1]}, Facebook {ms[2]}, WhatsApp {ms[3]}/wk, Patients {ms[4]}/wk. Days left: {days_left}\n")
print(f"{'metric':<16}{'now':>8}{'target':>8}{'need/day':>10}{'actual/day':>12}{'pace%':>8}  status     projection")
for m in a.metric:
    name, kv = m.split(":", 1)
    parts = dict(x.split("=") if "=" in x else (x, "1") for x in kv.split(","))
    cur = float(parts["current"])
    tgt = float(parts.get("target", DEFAULT_TARGET.get(name.lower(), 0)))
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
