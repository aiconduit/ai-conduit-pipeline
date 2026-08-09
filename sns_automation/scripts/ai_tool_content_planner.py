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
    
    prompt = f"""あなたはYouTube Shortsの台本ライターです。
以下のGitHubドキュメントから1つの具体的なTIPSを選んで60秒の台本を作ってください。

## ソースドキュメント（{source["repo"]}）
{key_content}

## 台本の絶対ルール

### ルール1: Hookは必ず「ツール名」から始める
フォーマット：「[ツール名]の[具体的な問題]で困っていませんか？」
視聴者は0.5秒でスワイプするかを決める。ツール名がないと「自分に関係ない話」と判断される。

良い例：
- 「Claude Codeのサブエージェントが勝手にファイルを書き換えていませんか？」
- 「Claude Codeに毎回同じ指示を打ち込んでいませんか？」
- 「Gemini CLIの使い方がわからず毎回ドキュメントを調べていませんか？」
- 「GitHub Copilotのレビューが的外れで困っていませんか？」

悪い例：
- 「サブエージェントが勝手にファイルを書き換えていませんか？」→ 何のツール？
- 「毎回同じ指示を打ち込んでいませんか？」→ 何のツール？
- 「Claude Codeで作業を自動化できます」→ 問題起点になっていない
- 「このツールがやばい」→ ツール名も問題も不明

必ずHookの1文目にツール名（Claude Code/Gemini CLI/GitHub Copilot等）を入れること。

### ルール2: 解決策は実際のコード・コマンド・ファイルパスをそのまま使う
ドキュメントに書いてある実際のフィールド名・コマンド・パスをそのまま台本に入れる。
「設定する」「作るだけ」で終わらず「具体的に何をどこに書くか」まで言う。

良い例：
- 「.claude/agents/reviewer.mdを作り、1行目にname: reviewer と書きます」
- 「disallowedTools: Write, Edit と書くと書き換えを禁止できます」
- 「CLAUDE.mdのトップに# Rules for Claude と書いてルールを追加します」

悪い例：
- 「設定ファイルを作るだけです」→ どこに何を書く？
- 「フィールドを追加します」→ どのフィールドを？どこに？

### ルール3: 説明は段階的に・具体的に
- Step1: 何を準備するか
- Step2: 実際に何をするか（コマンド・コードそのまま）
- Step3: 実行するとどうなるか
各ステップは視聴者がその場で試せるレベルで具体的に説明する。

### ルール4: Before→Afterで変化を具体的に示す
Before: 今まで何が起きていたか（1文・具体的）
After: これで何がどう変わるか（1文・具体的）
絶対禁止: 「爆速」「大幅」「劇的に」などの曖昧な言葉

### ルール5: CTAは動画の内容と完全一致
「この[動画で紹介したもの]を概要欄から受け取れます」
例: 「このdisallowedToolsの設定テンプレートを概要欄から受け取れます」

## 台本構成（60秒・7シーン）
Scene1 Hook（0-5秒）: 視聴者の具体的な問題提起（「〜で困っていませんか？」）
Scene2 Problem（5-13秒）: その問題がなぜ起きるのか・どれだけ困るか説明
Scene3 Solution（13-23秒）: ツール名+機能名+何をするか（実際のパス・フィールドを含む）
Scene4 Step1（23-33秒）: 実際にやること手順1（コマンドそのまま・ファイルパスそのまま）
Scene5 Step2（33-45秒）: 実際にやること手順2（コードそのまま・設定そのまま）
Scene6 Result（45-53秒）: Before→After（何がどう変わるか具体的に）
Scene7 CTA（53-60秒）: 動画内容と直結したプレゼント

## 禁止
- 根拠のない数字（「10倍速」「3秒で」「爆速」）
- 曖昧な言葉（「やばい」「すごい」「大幅」「神」「消えた」「禁断」）
- 「〜するだけ」で終わる説明（必ず具体的に続ける）
- 問題が不明なフック

## カテゴリ: {source["category"]}
## リポジトリ: {source["repo"]}

JSONのみ出力（前置き不要）:
{{
  "selected_title": "問題と解決策が伝わる30文字以内のタイトル（ツール名必須）",
  "problem": "視聴者の具体的な問題（1文）",
  "hook_text_overlay": "8文字以内・問題のキーワード",
  "scenes": [
    {{"title": "Hook", "narration": "具体的な問題（「〜ていませんか？」で終わる・30文字以内）", "caption": "問題", "mood": "hook", "visual_prompt": "frustrated developer typing"}},
    {{"title": "Problem", "narration": "問題の背景・なぜ困るか（30文字以内）", "caption": "背景", "mood": "hook", "visual_prompt": "developer frustrated screen"}},
    {{"title": "Solution", "narration": "ツール名+機能名+解決手順概要（実際のファイルパス・フィールドを含む・35文字以内）", "caption": "解決策", "mood": "value", "visual_prompt": "terminal command coding dark"}},
    {{"title": "Step1", "narration": "手順1: 実際のコマンドやファイルパス（ドキュメントそのまま・35文字以内）", "caption": "手順1", "mood": "value", "visual_prompt": "code editor file creation"}},
    {{"title": "Step2", "narration": "手順2: 実際のコードや設定値（ドキュメントそのまま・35文字以内）", "caption": "手順2", "mood": "value", "visual_prompt": "code writing terminal"}},
    {{"title": "Result", "narration": "Before: [具体的な問題] → After: [具体的な変化]（35文字以内）", "caption": "変化", "mood": "value", "visual_prompt": "developer happy success productive"}},
    {{"title": "CTA", "narration": "この[動画で紹介したもの]のテンプレートを概要欄から受け取れます。コメントにAIと書いてください。", "caption": "プレゼント", "mood": "cta", "visual_prompt": "gift download link"}}
  ],
  "total_duration_sec": 60,
  "pexels_keywords": ["developer coding terminal", "programming screen dark", "code editor"]
}}"""

    r = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.85,
            "max_tokens": 1500,
        },
        timeout=60
    )
    
    if r.status_code != 200:
        raise Exception(f"DeepSeek error: {r.status_code}")
    
    text = r.json()["choices"][0]["message"]["content"]
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if not m:
        raise Exception("JSON not found")
    
    data = json.loads(m.group())
    logger.info(f"スクリプト生成完了: {data.get('selected_title', '')}")
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
