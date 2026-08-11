#!/usr/bin/env python3
"""
quality_standards.py
動画品質基準の定義と評価システム

CREATOR_SECRETS.md + 実績データから導出した厳格な基準
"""

# ===================================
# 品質基準（妥協なし）
# ===================================

QUALITY_STANDARDS = {
    # 台本品質
    "script": {
        "hook_patterns": [
            "【数字】%のエンジニアが知らない",
            "これ知らないと【損】する",
            "【数字】分でできる",
            "プロが絶対教えない",
            "コードレビューに【数字】時間？",
            "残業が消えた理由は",
            "【機能名】で【具体的結果】ができます",
        ],
        "forbidden_words": [
            "爆速", "大幅", "劇的", "やばい", "神", "消えた",
            "禁断", "革命", "衝撃", "神アプデ",
        ],
        "required_elements": {
            "hook": {"max_chars": 25, "must_include": "result_first"},
            "why": {"must_include": "specific_problem"},
            "solution": {"must_include": "actual_path_or_command"},
            "step1": {"must_include": "exact_command"},
            "step2": {"must_include": "exact_command"},
            "result": {"must_include": "before_after"},
            "cta": {"must_include": "specific_filename"},
        },
        "total_duration": {"min": 40, "max": 55},  # 秒
        "scene_duration": {"min": 3, "max": 10},    # 秒
    },

    # 映像品質
    "video": {
        "resolution": "1080x1920",
        "fps": 30,
        "bitrate_kbps": 4000,
        "scene_mapping": {
            "hook":     "asciinema",       # ターミナルアニメーション
            "why":      "pexels_broll",    # B-roll感情映像
            "solution": "chrome_recording", # Claude.ai実画面
            "step1":    "asciinema",       # コマンドアニメーション
            "step2":    "asciinema",       # コマンドアニメーション
            "result":   "pexels_broll",    # B-roll達成映像
            "cta":      "ffmpeg_drawtext", # テキストアニメーション
        },
        "pexels_queries": {
            "why":    "developer frustrated error computer dark",
            "result": "developer celebrating success computer screens",
        },
    },

    # 字幕品質
    "subtitle": {
        "font": "NotoSansCJK-Black",
        "size": 95,
        "color": "FFD700",  # 金色
        "outline": "000000",
        "chunk_words": 3,    # 1チャンク=3語
        "chunk_duration_ms": 700,  # 700ms表示
        "sync_tolerance_ms": 100,  # ズレ許容100ms以内
        "position": "center",  # CREATOR_SECRETS.md準拠
    },

    # 音声品質
    "tts": {
        "engine": "edge-tts",
        "voice": "ja-JP-KeitaNeural",
        "scene_params": {
            "hook":     {"rate": "+15%", "pitch": "+3Hz"},
            "why":      {"rate": "-8%",  "pitch": "-2Hz"},
            "solution": {"rate": "+8%",  "pitch": "+2Hz"},
            "step1":    {"rate": "-12%", "pitch": "-3Hz"},
            "step2":    {"rate": "-12%", "pitch": "-3Hz"},
            "result":   {"rate": "+12%", "pitch": "+4Hz"},
            "cta":      {"rate": "+5%",  "pitch": "+5Hz"},
        },
        "audio_bitrate": "128k",
    },

    # BGM品質
    "bgm": {
        "volume_pct": 8,
        "genre": "lofi_hiphop",
        "source": "pixabay",
        "keywords": ["lofi", "jazz hip hop", "coding", "chill"],
        "forbidden": ["piano", "acoustic", "pop", "upbeat"],
    },

    # YouTube投稿品質
    "youtube": {
        "title_patterns": [
            "{number}%のエンジニアが知らないClaude Code術",
            "コードレビューに{time}？{feature}で解決",
            "残業が消えた理由は{feature}だった",
            "プロが絶対教えない{feature}の裏技",
            "え、マジ？{feature}でこんなことができるの",
        ],
        "hashtags": [
            "#ClaudeCode", "#Claude", "#AI開発", "#プログラミング",
            "#エンジニア", "#生成AI",
        ],
        "thumbnail_rule": "dark_bg_white_text_gold_accent",
        "post_times_jst": [20, 21, 22, 23, 0, 1, 2, 3, 4, 5],
    },

    # パフォーマンス基準
    "performance": {
        "min_retention_pct": 83,   # 83%未満は改善対象
        "target_retention_pct": 88, # 88%以上でバイラル期待
        "min_ctr_pct": 5,           # CTR 5%未満は改善対象
        "min_views_24h": 100,       # 24時間100再生未満は要改善
        "check_interval_hours": 24,
    },
}

def score_script(script: dict) -> dict:
    """台本品質スコアリング（100点満点）"""
    score = 0
    issues = []
    
    # フック評価（30点）
    hook = script.get("hook", {}).get("narration", "")
    if len(hook) <= 25:
        score += 10
    else:
        issues.append(f"Hook長すぎ: {len(hook)}文字")
    
    forbidden = QUALITY_STANDARDS["script"]["forbidden_words"]
    if not any(w in hook for w in forbidden):
        score += 20
    else:
        bad = [w for w in forbidden if w in hook]
        issues.append(f"禁止ワード: {bad}")
    
    # コマンド具体性評価（30点）
    for scene in ["step1", "step2"]:
        narration = script.get(scene, {}).get("narration", "")
        if any(c in narration for c in ["$", "/", ".claude", ".md", "yaml"]):
            score += 15
        else:
            issues.append(f"{scene}にコマンドなし")
    
    # CTA評価（20点）
    cta = script.get("cta", {}).get("narration", "")
    if any(ext in cta for ext in [".md", ".json", ".yaml", ".py"]):
        score += 20
    else:
        issues.append("CTAに具体的ファイル名なし")
    
    # 尺評価（20点）
    total_duration = sum(
        script.get(s, {}).get("duration", 0)
        for s in ["hook", "why", "solution", "step1", "step2", "result", "cta"]
    )
    if 40 <= total_duration <= 55:
        score += 20
    else:
        issues.append(f"尺不適切: {total_duration}秒")
    
    return {"score": score, "issues": issues, "passed": score >= 70}

if __name__ == "__main__":
    import json
    print("品質基準ロード完了")
    print(f"必須シーン: {list(QUALITY_STANDARDS['script']['required_elements'].keys())}")
    print(f"禁止ワード: {QUALITY_STANDARDS['script']['forbidden_words']}")
