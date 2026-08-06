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
    {"repo": "jnMetaCode/ai-coding-guide", "file": "claude-code/README.en.md", 
     "category": "claude_code", "title_prefix": "Claude Code"},
    {"repo": "jnMetaCode/ai-coding-guide", "file": "cheatsheet.en.md",
     "category": "ai_tools", "title_prefix": "AIツール比較"},
    {"repo": "jnMetaCode/ai-coding-guide", "file": "README.en.md",
     "category": "ai_coding", "title_prefix": "AI Coding"},
    {"repo": "dontriskit/awesome-ai-system-prompts", "file": "README.md",
     "category": "system_prompts", "title_prefix": "System Prompt"},
    {"repo": "jnMetaCode/ai-coding-guide", "file": "ecosystem.en.md",
     "category": "ai_ecosystem", "title_prefix": "AIエコシステム"},
    {"repo": "jnMetaCode/ai-coding-guide", "file": "resources.en.md",
     "category": "ai_tools", "title_prefix": "AIツールリソース"},
    {"repo": "dontriskit/awesome-ai-system-prompts", "file": "README.md",
     "category": "system_prompts", "title_prefix": "Systemプロンプト"},
    {"repo": "jnMetaCode/ai-coding-guide", "file": "claude-code/README.en.md",
     "category": "claude_code", "title_prefix": "Claude Code応用"},
    {"repo": "jnMetaCode/ai-coding-guide", "file": "cheatsheet.en.md",
     "category": "ai_tools", "title_prefix": "AIツール速攻比較"},
    # Boris Cherny (Claude Code作者) の公式TIPS集（64K★）
    {"repo": "shanraisshan/claude-code-best-practice", "file": "tips/claude-boris-15-tips-30-mar-26.md",
     "category": "claude_code", "title_prefix": "Boris直伝15Tips"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "tips/claude-boris-13-tips-03-jan-26.md",
     "category": "claude_code", "title_prefix": "Boris直伝13Tips"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "tips/claude-boris-12-tips-12-feb-26.md",
     "category": "claude_code", "title_prefix": "Boris直伝12Tips"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "tips/claude-boris-10-tips-01-feb-26.md",
     "category": "claude_code", "title_prefix": "Boris直伝10Tips"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "best-practice/claude-commands.md",
     "category": "claude_code", "title_prefix": "Claude Codeコマンド"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "best-practice/claude-mcp.md",
     "category": "claude_code", "title_prefix": "Claude MCP活用"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "CLAUDE.md",
     "category": "claude_code", "title_prefix": "CLAUDE.md設定術"},
    {"repo": "DenisSergeevitch/agents-best-practices", "file": "README.md",
     "category": "ai_tools", "title_prefix": "Agentベストプラクティス"},
    {"repo": "appcypher/awesome-mcp-servers", "file": "README.md",
     "category": "claude_code", "title_prefix": "MCPサーバー厳選"},
    # Boris追加TIPSシリーズ
    {"repo": "shanraisshan/claude-code-best-practice", "file": "tips/claude-boris-6-tips-16-apr-26.md",
     "category": "claude_code", "title_prefix": "Opus4.7完全活用"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "tips/claude-boris-2-tips-25-mar-26.md",
     "category": "claude_code", "title_prefix": "Boris最新2Tips"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "best-practice/claude-power-ups.md",
     "category": "claude_code", "title_prefix": "Claude Codeパワーアップ"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "best-practice/claude-memory.md",
     "category": "claude_code", "title_prefix": "Claude Codeメモリ設定"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "best-practice/claude-skills.md",
     "category": "claude_code", "title_prefix": "Claude Codeスキル作成"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "best-practice/claude-cli-startup-flags.md",
     "category": "claude_code", "title_prefix": "Claude Code起動フラグ"},
    # agents-best-practices
    {"repo": "DenisSergeevitch/agents-best-practices", "file": "README.md",
     "category": "ai_tools", "title_prefix": "Agentベストプラクティス"},
    # MCP servers awesome list
    {"repo": "wong2/awesome-mcp-servers", "file": "README.md",
     "category": "claude_code", "title_prefix": "MCPサーバー活用"},
    # ワークフロー・エージェント系（新規）
    {"repo": "ithiria894/awesome-claude-code-workflows", "file": "README.md",
     "category": "claude_code", "title_prefix": "Claudeワークフロー"},
    {"repo": "0xfnzero/AI-Code-Tutorials", "file": "README.md",
     "category": "ai_tools", "title_prefix": "AIコーディング入門"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "tips/claude-boris-2-tips-10-mar-26.md",
     "category": "claude_code", "title_prefix": "コードレビュー術"},
    {"repo": "shanraisshan/claude-code-best-practice", "file": "best-practice/claude-settings.md",
     "category": "claude_code", "title_prefix": "Claude Code設定完全版"},
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
    
    prompt = f"""あなたは「AI Conduit」のSNSコンテンツプランナーです。
日本のエンジニア・IT学生・AI初学者向けのYouTube Shorts動画（15〜20秒・5シーン）のスクリプトを生成してください。

## 参考にするGitHubコンテンツ（{source["repo"]}）
{key_content}

## 制作ルール
1. 上記のGitHubコンテンツの中から「視聴者が今すぐ試したい」と思う1つのTIPSを選ぶ
2. 具体的なコマンド・数字・手順を含める（「例：claude codeで/review」等）
3. narrationは各シーン15〜20文字。短くテンポよく。
4. total_duration_secは18以下
5. カテゴリ: {source["category"]}
6. 動画末尾でGitHubリポジトリ（{source["repo"]}）を紹介してプレゼントとして配布

以下のJSON形式のみで返してください（全フィールド必ず日本語で記述。英語タイトル・英語narration禁止）:
{{
  "selected_title": "（動画タイトル30文字以内・日本語）",
  "category": "{source["category"]}",
  "source_repo": "{source["repo"]}",
  "hashtags": ["#AI", "#ClaudeCode", "#エンジニア", "#プログラミング", "#AIツール"],
  "script": {{
    "title": "（日本語タイトル）",
    "total_duration_sec": 18,
    "scenes": [
      {{"scene_title": "Hook", "mood": "hook", "duration_sec": 3, "narration": "（15〜20文字・衝撃フック）", "visual_desc": "terminal screen coding"}},
      {{"scene_title": "Tip", "mood": "value", "duration_sec": 4, "narration": "（15〜20文字・具体的なコマンドor手順）", "visual_desc": "code editor screen"}},
      {{"scene_title": "Demo", "mood": "impact", "duration_sec": 4, "narration": "（15〜20文字・実際の効果・時間短縮）", "visual_desc": "developer working fast"}},
      {{"scene_title": "Twist", "mood": "twist", "duration_sec": 4, "narration": "（15〜20文字・さらに応用・驚き）", "visual_desc": "ai assistant coding"}},
      {{"scene_title": "CTA", "mood": "cta", "duration_sec": 3, "narration": "コメントにAIと書いてプレゼントゲット！", "visual_desc": "smartphone comment notification"}}
    ]
  }},
  "gift_content": "（プレゼントとして配布するGitHubリポジトリの日本語説明・50文字以内）"
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
