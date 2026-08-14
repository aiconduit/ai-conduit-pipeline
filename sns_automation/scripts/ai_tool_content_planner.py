#!/usr/bin/env python3
"""
AI Conduit - AIツール特化コンテンツプランナー v2
jnMetaCode/ai-coding-guideから実際のコンテンツを取得してショート動画化
"""
import os, json, requests, random, logging, base64, re
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ai_tool_planner")

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
CEREBRAS_API_KEY = os.environ.get("CEREBRAS_API_KEY", "csk-t9j3w5ne42jphxcj54x532hn8hhcv8cvk4r96563xrvvfvnp")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
SAVE_PATH = "sns_automation/news_content_plan.json"
USED_PATH = "sns_automation/used_topics.json"

# コンテンツソース（GitHubリポジトリ）
CONTENT_SOURCES = [
    # ===== Claude Code Best Practice（最優先・具体的なコマンド豊富）=====
    {"repo": "shanraisshan/claude-code-best-practice", "file": "best-practice/claude-subagents.md",
     "category": "claude_code", "title_prefix": "Claude Codeサブエージェント"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "best-practice/claude-commands.md",
     "category": "claude_code", "title_prefix": "Claude Codeカスタムコマンド"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "best-practice/claude-memory.md",
     "category": "claude_code", "title_prefix": "Claude CodeメモリCLAUDE.md"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "best-practice/claude-settings.md",
     "category": "claude_code", "title_prefix": "Claude Code設定"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "best-practice/claude-mcp.md",
     "category": "claude_code", "title_prefix": "Claude Code MCP連携"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "best-practice/claude-skills.md",
     "category": "claude_code", "title_prefix": "Claude Codeスキル"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "best-practice/claude-power-ups.md",
     "category": "claude_code", "title_prefix": "Claude Codeパワーアップ"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "best-practice/claude-cli-startup-flags.md",
     "category": "claude_code", "title_prefix": "Claude Code起動フラグ"},
    # ===== Claude Code公式CHANGELOG（最新機能）=====
    {"repo": "anthropics/claude-code", "file": "CHANGELOG.md",
     "category": "claude_news", "title_prefix": "Claude Code最新機能"},
    # ===== Anthropic Cookbook（実践レシピ）=====
    {"repo": "anthropics/anthropic-cookbook", "file": "README.md",
     "category": "claude_api", "title_prefix": "Claude API活用"},
    # ===== Anthropic Quickstarts（実用ユースケース）=====
    {"repo": "anthropics/anthropic-quickstarts", "file": "README.md",
     "category": "claude_usecase", "title_prefix": "Claude実用ユースケース"},
    {"repo": "anthropics/anthropic-quickstarts", "file": "computer-use-best-practices/README.md",
     "category": "claude_code", "title_prefix": "Claude Computer Use"},
    {"repo": "anthropics/anthropic-quickstarts", "file": "agents/README.md",
     "category": "claude_code", "title_prefix": "Claudeエージェント構築"},
    {"repo": "anthropics/anthropic-quickstarts", "file": "autonomous-coding/README.md",
     "category": "claude_code", "title_prefix": "Claude自律コーディング"},
    # ===== Boris直伝Tips（人気コンテンツ）=====
    {"repo": "shanraisshan/claude-code-best-practice", "file": "tips/claude-boris-15-tips-30-mar-26.md",
     "category": "claude_code", "title_prefix": "Boris直伝15Tips"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "tips/claude-boris-13-tips-03-jan-26.md",
     "category": "claude_code", "title_prefix": "Boris直伝13Tips"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "tips/claude-boris-12-tips-12-feb-26.md",
     "category": "claude_code", "title_prefix": "Boris直伝12Tips"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "tips/claude-boris-10-tips-01-feb-26.md",
     "category": "claude_code", "title_prefix": "Boris直伝10Tips"},
]

# トピックテンプレート（カテゴリ別）
TOPIC_TEMPLATES = {
    "claude_code": [
        "Claude Codeで{具体的な作業}が{X}倍速に",
        "Claude Codeの神機能：{機能名}の使い方",
        "Claude Codeで{問題}を解決する方法",
    ],
    "ai_tools": [
        "{ツール名} vs {ツール名}：どっちを使うべき？",
        "AIツール選び：{用途}なら{ツール名}一択",
    ],
    "ai_coding": [
        "AIでコーディングが{X}倍速になる方法",
        "エンジニア必見：AIコーディングの最新トレンド",
    ],
    "system_prompts": [
        "このSystem Promptで{ツール名}が神になる",
        "プロが使う{ツール名}のSystem Prompt公開",
    ],
    "ai_ecosystem": [
        "2026年AIツールの全体像を3分で解説",
        "MCPで{ツール名}の可能性が無限大に",
    ],
}

def fetch_github_content(repo, filepath):
    """GitHubから実際のコンテンツを取得"""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(
        f"https://api.github.com/repos/{repo}/contents/{filepath}",
        headers=headers, timeout=15
    )
    if r.status_code == 200:
        content = base64.b64decode(r.json()["content"]).decode("utf-8", errors="ignore")
        return content
    return ""

def extract_key_sections(content, max_chars=2000):
    """コンテンツから重要なセクションを抽出"""
    # コードブロックとセクションを重視
    sections = re.findall(r'#{1,3} .+?\n.*?(?=#{1,3} |$)', content, re.DOTALL)
    result = []
    total = 0
    for s in sections:
        if total + len(s) > max_chars:
            break
        result.append(s)
        total += len(s)
    return "\n".join(result) if result else content[:max_chars]

def pick_source():
    """未使用のソースからランダムに選択"""
    used_titles = set()
    if os.path.exists(USED_PATH):
        try:
            with open(USED_PATH, encoding='utf-8') as f:
                used_data = json.load(f)
            used_titles = {u["title"][:30] for u in used_data}
        except:
            pass
    
    available = [s for s in CONTENT_SOURCES 
                 if s["title_prefix"][:30] not in used_titles]
    if not available:
        available = CONTENT_SOURCES
    
    return random.choice(available)

def generate_script(source, raw_content):
    """DeepSeekでショート動画スクリプトを生成"""
    key_content = extract_key_sections(raw_content, 1500)
    
    prompt = f"""あなたはYouTube Shortsの台本ライターです。必ずJSONのみ出力してください。前置き・説明・マークダウン不要。
以下のGitHubドキュメントから1つの具体的なTIPSを選んで60秒の台本を作ってください。

## ソースドキュメント（{source["repo"]}）
{key_content}

## 台本の絶対ルール

### ルール1: Hookは「結果を最初に見せる」
視聴者は最初の3秒で「これは自分に関係あるか」を判断する。
問題起点ではなく「完成した結果・できること」を最初に見せる。
フォーマット：「Claude Code[機能名]で[具体的な結果]ができます」

良い例：
- 「Claude Codeのdisallowedツールで、コードレビューが読み取り専用で自動化されます」
- 「Claude CodeのCLAUDE.mdに書くだけで、毎回の指示が不要になります」
- 「Claude CodeのMCPで、外部APIを自然言語で直接操作できます」

悪い例：
- 「サブエージェントで困っていませんか？」→ 結果が見えない
- 「Claude Codeをもっと活用しましょう」→ 何ができるか不明

### ルール2: 構成は「結果→理由→手順→確認」
- Hook: 完成した結果・できること（ツール名必須）
- Why: なぜこれが必要か・使わないと何が起きるか
- Solution: 何をどこに書くか（実際のパス・コマンド）
- Step1: 手順1（実際のコード・コマンドそのまま）
- Step2: 手順2（実際のコード・設定値そのまま）
- Result: 実際にどう変わるか（具体的・定量的）
- CTA: この設定ファイルを受け取れる

### ルール3: 実際のコード・パスをそのまま使う
- 「.claude/agents/reviewer.md」「disallowedTools: Write, Edit」等をそのまま入れる
- 「設定するだけ」「書くだけ」で終わらず「何をどこに書くか」まで言う
- コマンドは $ から始まる実際のコマンドを使う

良い例：
- 「.claude/agents/reviewer.mdの1行目にname: reviewer と書きます」
- 「frontmatterにdisallowedTools: Write, Edit と記述します」
- 「$ claude --model claude-opus-4 と入力するだけです」

悪い例：
- 「設定ファイルを作るだけです」→ どこに何を？
- 「コマンドを実行します」→ どのコマンド？

### ルール4: Before→Afterは具体的に
Before: 今まで何をしていたか（具体的・時間や手順数）
After: これで何がどう変わるか（具体的・測定可能）
禁止: 「爆速」「大幅」「劇的に」「やばい」

### ルール5: CTAは動画内容と完全一致
「この[動画で紹介したもの]のテンプレートを概要欄から受け取れます」

## 台本構成（60秒・7シーン）
Scene1 Hook（0-5秒）: Claude Codeの[機能]で[具体的な結果]ができます（結果を最初に見せる）
Scene2 Why（5-13秒）: これがないと何が起きるか・なぜ必要か
Scene3 Solution（13-23秒）: 何をどこに書くか（実際のパス・ファイル名）
Scene4 Step1（23-33秒）: 手順1の実際のコード・コマンドそのまま
Scene5 Step2（33-45秒）: 手順2の実際のコード・設定値そのまま
Scene6 Result（45-53秒）: Before→After（具体的な変化）
Scene7 CTA（53-60秒）: 動画内容と直結したプレゼント

## 禁止ワード
爆速・大幅・劇的・やばい・すごい・神・消えた・禁断・根拠のない数字

## カテゴリ: {source["category"]}
## リポジトリ: {source["repo"]}

JSONのみ出力（前置き不要）:
{{
  "selected_title": "結果が伝わる30文字以内のタイトル（Claude Code/Claude必須）",
  "result_first": "最初に見せる結果（1文・具体的）",
  "hook_text_overlay": "8文字以内・できることのキーワード",
  "scenes": [
    {{"title": "Hook", "narration": "Claude Code[機能]で[具体的な結果]ができます（30文字以内）", "caption": "できること", "mood": "hook", "visual_prompt": "claude code terminal success result screen"}},
    {{"title": "Why", "narration": "これがないと[具体的な問題]が起きます（30文字以内）", "caption": "必要な理由", "mood": "hook", "visual_prompt": "developer frustrated problem screen"}},
    {{"title": "Solution", "narration": "Claude Codeの[機能名]・[実際のファイルパス]で解決（35文字以内）", "caption": "解決策", "mood": "value", "visual_prompt": "terminal file creation coding dark"}},
    {{"title": "Step1", "narration": "手順1: [実際のコマンド・パスそのまま]（35文字以内）", "caption": "手順1", "mood": "value", "visual_prompt": "code editor typing command terminal"}},
    {{"title": "Step2", "narration": "手順2: [実際のコード・設定値そのまま]（35文字以内）", "caption": "手順2", "mood": "value", "visual_prompt": "code writing configuration file"}},
    {{"title": "Result", "narration": "Before: [問題] → After: [具体的な変化]（35文字以内）", "caption": "変化", "mood": "value", "visual_prompt": "developer happy productive success screen"}},
    {{"title": "CTA", "narration": "この[紹介したもの]のテンプレートを概要欄から受け取れます。コメントにAIと書いてください。", "caption": "無料プレゼント", "mood": "cta", "visual_prompt": "gift download template file"}}
  ],
  "total_duration_sec": 60,
  "pexels_keywords": ["claude code terminal", "developer coding dark screen", "programming workspace"]
}}"""

    # Cerebras → Groq フォールバック
    text = None
    for api_name, api_url, api_key, model in [
        ("OpenRouter", "https://openrouter.ai/api/v1/chat/completions", OPENROUTER_API_KEY, "meta-llama/llama-3.3-70b-instruct"),
        ("Cerebras", "https://api.cerebras.ai/v1/chat/completions", CEREBRAS_API_KEY, "gpt-oss-120b"),
        ("Groq",     "https://api.groq.com/openai/v1/chat/completions", GROQ_API_KEY, "llama-3.3-70b-versatile"),
        ("OpenRouter", "https://openrouter.ai/api/v1/chat/completions", OPENROUTER_API_KEY, "meta-llama/llama-3.3-70b-instruct"),
    ]:
        if not api_key:
            continue
        try:
            req_body = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.85,
                "max_tokens": 1500,
            }
            if api_name == "OpenRouter":
                req_body["response_format"] = {"type": "json_object"}
            r = requests.post(
                api_url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=req_body,
                timeout=60
            )
            if r.status_code == 200:
                msg = r.json()["choices"][0]["message"]
                # contentとreasoningの両方からJSONを探す
                content_text = msg.get("content") or ""
                reasoning_text = msg.get("reasoning") or ""
                combined = content_text + "\n" + reasoning_text
                import re as _re
                _m = _re.search(r'\{[\s\S]*\}', combined)
                if _m:
                    text = _m.group()
                    logger.info(f"{api_name} でスクリプト生成成功")
                    break
                elif combined.strip():
                    text = combined
                    logger.info(f"{api_name} でスクリプト生成成功（テキスト）")
                    break
                else:
                    logger.warning(f"{api_name}: 空レスポンス")
            else:
                logger.warning(f"{api_name} error: {r.status_code}")
        except Exception as e:
            logger.warning(f"{api_name} 例外: {e}")
    if text is None:
        raise Exception("全APIでスクリプト生成失敗")
    # JSON抽出（textが既にJSONの場合も対応）
    _text_stripped = text.strip()
    if _text_stripped.startswith("{"):
        # 最初の完全なJSONオブジェクトのみ抽出
        import re as _re4
        _m2 = _re4.search(r'\{[\s\S]*\}', _text_stripped)
        m = _m2 if _m2 else type("M", (), {"group": lambda self: _text_stripped})()
    else:
        m = re.search(r'\{[\s\S]*\}', text)
    if not m:
        logger.warning(f"JSON not found in text (len={len(text)}): {text[:200]}")
        raise Exception("JSON not found")
    try:
        data = json.loads(m.group())
    except json.JSONDecodeError:
        import re as _re2
        # 制御文字除去
        clean = _re2.sub(r'[\x00-\x1f\x7f]', ' ', m.group())
        try:
            data = json.loads(clean)
        except json.JSONDecodeError:
            # 無効なエスケープ文字も除去
            import re as _re3
            clean2 = _re3.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', clean)
            try:
                data = json.loads(clean2)
            except json.JSONDecodeError:
                # 末尾の不完全なJSONを修復
                _txt = clean2.strip()
                _open = _txt.count('{') - _txt.count('}')
                _txt += '}' * max(0, _open)
                try:
                    data = json.loads(_txt)
                except json.JSONDecodeError as _je:
                    # "Extra data"の場合は最初のJSONオブジェクトのみ取得
                    if "Extra data" in str(_je):
                        try:
                            import json as _json2
                            data = _json2.loads(_txt[:int(str(_je).split("(char ")[1].split(")")[0])])
                        except Exception:
                            logger.warning(f"JSON修復失敗: {_je} / text: {clean[:200]}")
                            raise Exception(f"JSONDecodeError: {_je}")
                    else:
                        logger.warning(f"JSON修復失敗: {_je} / text: {clean[:200]}")
                        raise Exception(f"JSONDecodeError: {_je}")
    logger.info(f"スクリプト生成完了: {data.get('selected_title', '')}")
    
    # 新旧フォーマット統一: scenesがトップレベルにある場合script.scenesに変換
    if "scenes" in data and "script" not in data:
        data["script"] = {
            "title": data.get("selected_title", ""),
            "scenes": data["scenes"]
        }
    
    return data

def update_used_topics(title):
    """使用済みとして記録"""
    try:
        existing = []
        if os.path.exists(USED_PATH):
            with open(USED_PATH, encoding='utf-8') as f:
                existing = json.load(f)
        existing.append({"title": title, "used_at": datetime.now().isoformat()})
        with open(USED_PATH, 'w', encoding='utf-8') as f:
            json.dump(existing[-100:], f, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"used_topics記録エラー: {e}")

def main():
    # コンテンツソースを選択
    source = pick_source()
    logger.info(f"ソース選択: {source['repo']} / {source['file']}")
    
    # GitHubからコンテンツ取得
    raw_content = fetch_github_content(source["repo"], source["file"])
    if not raw_content:
        raise Exception(f"コンテンツ取得失敗: {source['file']}")
    logger.info(f"コンテンツ取得完了: {len(raw_content)}文字")
    
    # スクリプト生成
    plan = generate_script(source, raw_content)
    
    # used_topicsに記録
    update_used_topics(plan.get("selected_title", ""))
    
    # 保存
    with open(SAVE_PATH, 'w', encoding='utf-8') as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Selected Top1: [{source['category']}] {plan.get('selected_title', '')}")
    logger.info(f"Fireship script ready for {plan.get('selected_title', '')}")

if __name__ == "__main__":
    main()
