#!/usr/bin/env python3
"""
autonomous_agent.py
AI Conduit 完全自律型エージェント

動作フロー:
1. 台本生成（Cerebras/DeepSeek）
2. 品質チェック（quality_standards.py）
3. 映像生成（asciinema + Chrome録画 + Pexels）
4. 音声生成（Edge TTS シーン別設定）
5. 字幕生成（word_timestamps完全同期）
6. 動画合成（FFmpeg）
7. YouTube投稿
8. 24時間後に分析
9. 改善パラメータを自動更新
10. ループ繰り返し
"""
import os, json, time, subprocess, requests
from pathlib import Path
from quality_standards import QUALITY_STANDARDS, score_script

CEREBRAS_KEY = os.environ.get("CEREBRAS_API_KEY", "")
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")
YT_TOKEN     = os.environ.get("YOUTUBE_TOKEN_JSON", "")

# ===================================
# Step 1: 台本生成
# ===================================

SCRIPT_PROMPT = """
あなたはClaude Code専門のYouTube Shortsスクリプトライターです。
以下の厳格なルールで台本を生成してください。

【必須ルール】
- Hook: 「{feature}で{specific_result}ができます」（結果を最初に見せる）
- Why: 「これがないと{specific_problem}が起きます」
- Solution: 「{actual_file_path}で解決します」（実際のパス）
- Step1: 「$ {actual_command}」（実際のコマンドそのまま）
- Step2: 「{file_content}」（実際のコード/設定）
- Result: 「Before: {problem} → After: {specific_result}」
- CTA: 「{specific_filename}を概要欄から受け取れます」

【禁止ワード】
爆速、大幅、劇的、やばい、神、消えた、禁断、革命

【出力形式】JSONのみ・他のテキスト不要】
{
  "title": "99%が知らないClaude Code術",
  "hook":     {"narration": "...", "duration": 4},
  "why":      {"narration": "...", "duration": 6},
  "solution": {"narration": "...", "duration": 8},
  "step1":    {"narration": "...", "duration": 7, "command": "$ ..."},
  "step2":    {"narration": "...", "duration": 7, "command": "..."},
  "result":   {"narration": "...", "duration": 6},
  "cta":      {"narration": "...", "duration": 5, "gift_file": "reviewer.md"}
}

トピック: {topic}
"""

def generate_script(topic: str) -> dict:
    """Cerebras優先・DeepSeekフォールバックで台本生成"""
    prompt = SCRIPT_PROMPT.format(topic=topic, feature="", specific_result="",
                                   specific_problem="", actual_file_path="",
                                   actual_command="", file_content="",
                                   specific_filename="")
    
    # Cerebras試行
    if CEREBRAS_KEY:
        try:
            r = requests.post("https://api.cerebras.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {CEREBRAS_KEY}", "Content-Type": "application/json"},
                json={"model": "gpt-oss-120b",
                      "messages": [{"role": "user", "content": f"{prompt}\n\nトピック: {topic}"}],
                      "max_tokens": 800},
                timeout=30)
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                # JSON抽出
                import re
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    script = json.loads(json_match.group())
                    print(f"✅ Cerebras台本生成成功")
                    return script
        except Exception as e:
            print(f"Cerebras失敗: {e}")
    
    # DeepSeek フォールバック
    if DEEPSEEK_KEY:
        try:
            r = requests.post("https://api.deepseek.com/chat/completions",
                headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"},
                json={"model": "deepseek-chat",
                      "messages": [{"role": "user", "content": f"{prompt}\n\nトピック: {topic}"}],
                      "max_tokens": 800},
                timeout=30)
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                import re
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    script = json.loads(json_match.group())
                    print(f"✅ DeepSeek台本生成成功")
                    return script
        except Exception as e:
            print(f"DeepSeek失敗: {e}")
    
    raise Exception("全LLM失敗")

# ===================================
# Step 2: 品質チェック + 自動修正
# ===================================

def quality_check_and_fix(script: dict, max_retries: int = 3) -> dict:
    """品質チェック → 不合格なら自動修正して再生成"""
    for i in range(max_retries):
        result = score_script(script)
        print(f"品質スコア: {result['score']}/100 (試行{i+1})")
        
        if result["passed"]:
            print(f"✅ 品質基準合格")
            return script
        
        print(f"❌ 不合格: {result['issues']}")
        
        # 問題点を修正プロンプトに反映して再生成
        fix_prompt = f"""
以下の台本に問題があります。修正してください:
問題: {result['issues']}
元の台本: {json.dumps(script, ensure_ascii=False)}
同じJSONフォーマットで修正版を出力してください。
"""
        try:
            r = requests.post("https://api.cerebras.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {CEREBRAS_KEY}", "Content-Type": "application/json"},
                json={"model": "gpt-oss-120b",
                      "messages": [{"role": "user", "content": fix_prompt}],
                      "max_tokens": 800},
                timeout=30)
            if r.status_code == 200:
                import re
                content = r.json()["choices"][0]["message"]["content"]
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    script = json.loads(json_match.group())
        except:
            pass
    
    print(f"⚠️ 最大リトライ後も不合格（続行）")
    return script

# ===================================
# Step 8-9: 分析 + 自動改善
# ===================================

def analyze_and_improve(video_id: str, params_file: str = "auto_params.json"):
    """YouTubeアナリティクスを分析して次回パラメータを自動改善"""
    
    # YouTubeアナリティクス取得
    token_data = json.loads(YT_TOKEN) if YT_TOKEN else {}
    access_token = token_data.get("access_token", "")
    
    if not access_token:
        print("⚠️ YouTubeトークンなし")
        return
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 再生数・リテンション取得
    metrics_url = "https://youtubeanalytics.googleapis.com/v2/reports"
    r = requests.get(metrics_url, headers=headers, params={
        "ids": "channel==MINE",
        "startDate": "2026-01-01",
        "endDate": "2026-12-31",
        "metrics": "views,averageViewPercentage,clickThroughRate",
        "filters": f"video=={video_id}",
        "dimensions": "video",
    }, timeout=10)
    
    if r.status_code != 200:
        print(f"⚠️ アナリティクス取得失敗: {r.status_code}")
        return
    
    data = r.json()
    rows = data.get("rows", [])
    if not rows:
        print("⚠️ データなし（24時間未満）")
        return
    
    views, retention, ctr = rows[0][1], rows[0][2], rows[0][3]
    
    standards = QUALITY_STANDARDS["performance"]
    print(f"\n📊 パフォーマンス分析:")
    print(f"  再生数: {views} (基準: {standards['min_views_24h']})")
    print(f"  視聴維持率: {retention:.1f}% (基準: {standards['min_retention_pct']}%)")
    print(f"  CTR: {ctr:.1f}% (基準: {standards['min_ctr_pct']}%)")
    
    # 自動改善ロジック
    params = {}
    if Path(params_file).exists():
        params = json.loads(Path(params_file).read_text())
    
    improvements = []
    
    if retention < standards["min_retention_pct"]:
        improvements.append("視聴維持率不足→動画尺を5秒短縮")
        params["target_duration"] = params.get("target_duration", 50) - 5
    elif retention >= standards["target_retention_pct"]:
        improvements.append(f"✅ 視聴維持率優秀({retention:.1f}%)→現状維持")
    
    if ctr < standards["min_ctr_pct"]:
        improvements.append("CTR不足→フックパターンを変更")
        params["hook_style"] = "number_first"  # 数字から始めるフックに変更
    
    if views < standards["min_views_24h"]:
        improvements.append("再生数不足→投稿時間を最適化")
        params["next_post_time"] = "20:00"  # ゴールデンタイムに固定
    
    if improvements:
        Path(params_file).write_text(json.dumps(params, ensure_ascii=False, indent=2))
        print(f"\n🔧 自動改善:")
        for imp in improvements:
            print(f"  - {imp}")
        print(f"  パラメータ更新: {params_file}")
    
    return {"views": views, "retention": retention, "ctr": ctr, "improvements": improvements}


if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "Claude Codeのサブエージェント機能"
    
    print(f"\n=== AI Conduit 自律型エージェント ===")
    print(f"トピック: {topic}")
    
    # 台本生成
    script = generate_script(topic)
    
    # 品質チェック
    script = quality_check_and_fix(script)
    
    # 結果保存
    Path("autonomous_script.json").write_text(
        json.dumps(script, ensure_ascii=False, indent=2))
    print(f"\n✅ 台本保存: autonomous_script.json")
    print(json.dumps(script, ensure_ascii=False, indent=2)[:500])
