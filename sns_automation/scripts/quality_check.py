#!/usr/bin/env python3
import json, os, sys
from pathlib import Path

script = json.loads(Path("news_content_plan.json").read_text())
FORBIDDEN = ["爆速","大幅","劇的","やばい","神","消えた","禁断"]

score = 0
issues = []

hook = script.get("hook",{}).get("narration","")
if len(hook) <= 25: score += 25
else: issues.append(f"Hook長すぎ:{len(hook)}文字")

if not any(w in hook for w in FORBIDDEN): score += 25
else: issues.append("禁止ワード使用")

for s in ["step1","step2"]:
    n = script.get(s,{}).get("narration","") + script.get(s,{}).get("command","")
    if any(c in n for c in ["$","claude","/loop","/babysit",".md",".claude"]): score += 15
    else: issues.append(f"{s}コマンドなし")

cta = script.get("cta",{}).get("narration","")
if any(e in cta for e in [".md",".json",".yaml",".py"]): score += 20
else: issues.append("CTA具体性不足")

valid = score >= 60
print(f"品質スコア: {score}/100 {'合格' if valid else '不合格'}")
if issues: print(f"問題: {issues}")

gh_output = os.environ.get("GITHUB_OUTPUT","")
if gh_output:
    with open(gh_output,"a") as f:
        f.write(f"score={score}\nvalid={'true' if valid else 'false'}\n")

sys.exit(0 if valid else 1)
