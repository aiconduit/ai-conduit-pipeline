#!/usr/bin/env python3
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from sns_automation.scripts.generate_terminal_demo import generate_terminal_demo
try:
    with open('sns_automation/news_content_plan.json') as f:
        plan = json.load(f)
    generate_terminal_demo(plan, 'assets/claude_code_demo.mp4')
except Exception as e:
    print(f'デモ生成スキップ: {e}')
