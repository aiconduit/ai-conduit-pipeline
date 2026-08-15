#!/usr/bin/env python3
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from sns_automation.scripts.generate_before_after import generate_before_after_video
try:
    with open('sns_automation/news_content_plan.json') as f:
        plan = json.load(f)
    generate_before_after_video(plan, 'assets/before_after.mp4')
except Exception as e:
    print(f'Before/After生成スキップ: {e}')
