#!/usr/bin/env python3
"""Budget check for the accountant agent (month starts 2026-12-01).

Usage: python3 .claude/accountant/budget.py --today 2026-12-10 --tiktok-spent 4 \
          --runs 9 --limit-hits 1 [--runs-expected 10]
Claude is a flat $20 plan: cost is fixed, the risk is hitting usage limits.
TikTok ads cap $10/month. Status: OK / WATCH / ALERT.
"""
import argparse, calendar
from datetime import date

p = argparse.ArgumentParser()
p.add_argument("--today", default=date.today().isoformat())
p.add_argument("--tiktok-spent", type=float, default=0)
p.add_argument("--tiktok-cap", type=float, default=10)
p.add_argument("--runs", type=int, default=0, help="daily runs completed this month")
p.add_argument("--runs-expected", type=int, default=None)
p.add_argument("--limit-hits", type=int, default=0, help="runs stopped by a usage limit this month")
a = p.parse_args()
t = date.fromisoformat(a.today)
if t < date(2026, 12, 1):
    print("BUDGET not started (starts 2026-12-01): $0 ad spend allowed"); raise SystemExit(0)
dim = calendar.monthrange(t.year, t.month)[1]
elapsed = t.day / dim
exp = a.runs_expected or t.day
rows = []
tt_share = a.tiktok_spent / a.tiktok_cap if a.tiktok_cap else 0
tt = "ALERT" if a.tiktok_spent > a.tiktok_cap else "WATCH" if tt_share > elapsed + 0.2 else "OK"
rows.append(("TikTok ads", f"${a.tiktok_spent:.2f}/${a.tiktok_cap:.0f}", f"{tt_share:.0%} spent, {elapsed:.0%} of month", tt))
cl = "ALERT" if a.limit_hits >= 3 else "WATCH" if a.limit_hits >= 1 or a.runs < exp - 1 else "OK"
rows.append(("Claude $20", f"{a.runs}/{exp} runs", f"{a.limit_hits} usage-limit stops", cl))
for r in rows:
    print(" | ".join(r))
worst = "ALERT" if any(r[3] == "ALERT" for r in rows) else "WATCH" if any(r[3] == "WATCH" for r in rows) else "OK"
print("OVERALL", worst)
if cl != "OK":
    print("HINT lighten load: video every 2 days, supervisor full SOP every 2 days, keep humanizer daily")
