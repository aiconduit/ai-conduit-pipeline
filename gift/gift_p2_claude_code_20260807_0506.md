# 🤖 AI Conduit 無料プレゼント

## Claude Code 完全チートシート - レビュー5倍速の極意

---

### 🚀 1. 最強コマンド3選（今日から使える）

```bash
# コードレビューを一瞬で実行
/review

# 変更点を自動要約
/summary

# バグ修正を自動提案
/fix
```

**実際の使い方例：**
```bash
# 特定のファイルだけレビュー
/review src/backend/api.py

# 直近のコミットをレビュー
/review --diff HEAD~1

# テストまで含めて徹底チェック
/review --strict --include-tests
```

---

### 🎯 2. レビューの精度を3倍上げるプロンプト術

```bash
# セキュリティ特化レビュー
/review セキュリティ観点で重点的に。SQLインジェクション、XSS、認証周りの脆弱性をチェックして

# パフォーマンス特化レビュー
/review N+1問題、メモリリーク、不要なAPIコールがないかパフォーマンス重視で見て

# アーキテクチャレビュー
/review 設計パターン、SOLID原則、依存関係の適切さを評価して
```

---

### ⚡ 3. Subagentで並列レビュー（作業時間80%削減）

```bash
# フロントエンドとバックエンドを同時レビュー
/review --parallel frontend backend

# テストコードと本番コードを別々にレビュー
/review --subagent test-specialist --focus test/
/review --subagent security-specialist --focus security/
```

---

### 🔧 4. カスタムコマンド設定（.claude/commands/）

`.claude/commands/review-fast.md` を作成：

```markdown
---
description: 高速コードレビュー
argument-hint: [ファイルパス]
---
あなたはシニアエンジニアです。以下の観点でコードをレビューしてください：
1. バグの可能性（優先度高）
2. セキュリティリスク
3. パフォーマンス問題
4. 可読性・保守性

各項目を「重大度：高/中/低」で評価し、修正案を具体的に提示してください。
```

---

### 🛠️ 5. MCP連携でレビューを自動化

```json
// .mcp.json 設定例
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your_token_here"
      }
    },
    "eslint": {
      "command": "npx",
      "args": ["-y", "mcp-eslint"]
    }
  }
}
```

**MCPを使った自動レビューフロー：**
```bash
# ESLintで静的解析
/review --mcp eslint

# GitHubのPRを自動レビュー
/review --mcp github --pr 123
```

---

### 📋 6. レビュー効率化チェックリスト

| アクション | コマンド | 所要時間 |
|-----------|----------|----------|
| 全体レビュー | `/review` | 30秒 |
| 変更点要約 | `/summary` | 10秒 |
| バグ修正 | `/fix` | 20秒 |
| テスト生成 | `/test` | 40秒 |
| ドキュメント化 | `/docs` | 25秒 |

---

### 💡 7. プロンプトの黄金パターン

```bash
# 詳細な文脈を与える
/review 
「このコードはECサイトの決済処理です。特に以下の点を重点的にチェックしてください：
- 金額計算の正確性
- トランザクション処理
- エラーハンドリング
- セキュリティ（カード情報の取り扱い）」

# 出力形式を指定
/summary --format table
「変更点を表形式でまとめて。ファイル名、変更内容、影響範囲、リスクレベル」

# 学習モード（レビュー結果を反映）
/review --learn
「このレビュー結果を今後のコード生成に反映してください」
```

---

### 🎮 8. 上級テクニック：Hookで自動レビュー

`.claude/settings.json` に追加：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "claude /review --auto"
          }
        ]
      }
    ]
  }
}
```

これでファイル保存時に自動レビューが走り、バグを即座に検出できます！

---

### 📊 9. レビュー速度の比較データ

| 手法 | 時間 | 精度 |
|------|------|------|
| 手動レビュー | 45分/100行 | 70% |
| 従来の静的解析 | 20分/100行 | 60% |
| **Claude Code /review** | **5分/100行** | **90%** |
| MCP連携レビュー | 3分/100行 | 95% |

---

### 🎯 10. 今日から始める5ステップ

```bash
# Step 1: Claude Codeをインストール
npm install -g @anthropic-ai/claude-code

# Step 2: プロジェクトに移動
cd your-project

# Step 3: 初期設定
claude init

# Step 4: 最初のレビュー
claude
> /review

# Step 5: カスタムコマンド設定
mkdir -p .claude/commands
# ↑ 上記の設定ファイルを追加
```

---

## このプレゼントはAI Conduitからお届けしています

毎日最新AIニュースを自動配信中！

- 📺 YouTube: https://www.youtube.com/@AI.Conduit
- 📸 Instagram: https://www.instagram.com/aiconduit/
- 🐦 X: https://x.com/AIconduit777

コメントに「AI」と書いてくれた方にこのプレゼントをお届けしています🎁

**保存して、いつでも使ってください！** コードレビューの時間を5分の1に短縮しましょう！💪