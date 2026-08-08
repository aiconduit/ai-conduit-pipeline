# 🤖 AI Conduit 無料プレゼント
## Claude Code 完全チートシート - レビュー3秒化＆爆速コーディング術

動画で紹介した「**CLIモードでレビュー時間が3秒に**」を実践するための、すぐ使えるチートシートを大公開！コピペですぐに使えます👇

---

### 🚀 1. コードレビュー自動化の決定版コマンド

```bash
# 変更ファイル全体をレビュー（日本語で指摘）
claude -P "変更されたコードをレビューして。バグ・セキュリティ問題・改善点を日本語で簡潔に指摘して"

# 特定ファイルをレビュー
claude -P "app.pyをレビューして。コードの品質を10点満点で評価して"

# Gitの差分だけをレビュー
git diff | claude -P "この差分をレビューして。問題点だけ箇条書きで"
```

**🎯 ポイント**: `-P`（printモード）を使うと、対話なしで結果だけが即座に返ってきます！

---

### 🛠️ 2. 最強の自作コマンド（スラッシュコマンド）

`.claude/commands/` フォルダに保存するだけで、`/レビュー` と打つだけで実行可能に！

**`.claude/commands/review.md`** を作成:
```markdown
---
description: コードレビューを実行
argument_hint: レビューしたいファイル名
---
変更されたコードをレビューしてください。
以下の観点で指摘してください：
1. バグの可能性
2. セキュリティリスク
3. パフォーマンス問題
4. 命名・可読性
日本語で簡潔に、重要度順にまとめてください。
```

---

### ⚡ 3. 3秒で終わる「エラー解決」プロンプト

```bash
# エラーメッセージをそのまま貼り付けるだけ！
claude -P "このエラーを解決してください。原因と修正コードを教えて: $(cat error.log)"
```

```bash
# エイリアス登録で爆速化
alias fix='claude -P "このエラーの原因と修正方法を教えて: $(cat /tmp/error.txt)"'
```

---

### 📋 4. MCP（Model Context Protocol）設定チートシート

**MCPサーバー追加コマンド**:
```bash
# GitHub MCP（PR管理・Issue操作をAIで自動化）
claude mcp add github --env GITHUB_TOKEN=your_token -- npx @modelcontextprotocol/server-github

# ファイルシステムMCP（プロジェクト外のファイルも操作可能に）
claude mcp add fs -- npx @modelcontextprotocol/server-filesystem /Users/yourname/Documents
```

**おすすめMCPサーバー5選**:
| MCPサーバー | 用途 | インストール |
|------------|------|------------|
| Playwright | ブラウザ操作自動化 | `npx @playwright/mcp@latest` |
| GitHub | PR・Issue管理 | `npx @modelcontextprotocol/server-github` |
| PostgreSQL | DBクエリ実行 | `npx @modelcontextprotocol/server-postgres` |
| Fetch | Webページ取得 | `npx @modelcontextprotocol/server-fetch` |
| Puppeteer | スクレイピング | `npx @modelcontextprotocol/server-puppeteer` |

---

### 🧠 5. Subagentを活用した並列処理

**`.claude/agents/` に作成するだけで、専門エージェントとして動作！**

**`.claude/agents/security-expert.md`**:
```markdown
---
name: security-expert
description: セキュリティ専門家としてコードを監査します
---
あなたはセキュリティ専門家です。
XSS、SQLインジェクション、認証バイパスなどの
脆弱性がないかコードを監査し、日本語で報告してください。
```

```bash
# 使い方: コードレビュー時にセキュリティ専門家を呼ぶ
claude -P "このコードをセキュリティの観点で監査して。@security-expert を呼んで"
```

---

### 🎨 6. 日本語で動かすための必須設定

**`.claude/settings.json`** に追加:
```json
{
  "language": "ja",
  "model": "claude-sonnet-4-20250514",
  "permissions": {
    "allow": ["Bash", "Read", "Edit", "Write"],
    "deny": ["Delete"]
  }
}
```

**日本語プロンプトのコツ**:
- 「〜して」「〜してください」で締める
- 出力形式を指定する（「表で」「箇条書きで」）
- 長さを指定する（「3行以内で」）

---

### 📊 7. Git操作をAIで自動化

```bash
# コミットメッセージ自動作成
claude -P "git diffを確認して、適切なコミットメッセージを日本語で提案して: $(git diff --stat)"

# ブランチ名を提案
claude -P "この機能追加に適切なブランチ名を提案して: ユーザー認証にGoogleログインを追加"
```

---

### 💰 8. 料金を抑える裏ワザ

```bash
# 大量ファイルを扱う場合: ファイル数を制限
claude -P --max-turns 5 "このプロジェクトの構造を解析して"

# 使用量を確認
claude --usage

# モデルを切り替えてコスト削減（Sonnet vs Opus）
claude -P --model claude-sonnet-4-20250514 "コードレビューして"
```

---

### 🏆 9. 今日から使える「神プロンプト」集

| 目的 | プロンプト |
|------|-----------|
| **リファクタリング** | `この関数をリファクタリングして。可読性とパフォーマンスを改善して` |
| **テスト生成** | `このコードのユニットテストを生成して。pytestで` |
| **ドキュメント化** | `このプロジェクトのREADME.mdを日本語で生成して` |
| **コード解説** | `このコードが何をしているか、初心者にもわかるように解説して` |
| **バグ予測** | `このコードに潜む潜在的なバグを予測して` |
| **セキュリティ監査** | `XSSとSQLインジェクションの観点でコードを監査して` |

---

### 🔥 10. 今日のアクション（今すぐやること）

```bash
# 1. エイリアスを設定（.zshrc または .bashrc に追加）
alias review='claude -P "変更されたコードを日本語でレビューして。問題点を重要度順に:"'
alias explain='claude -P "このコードを日本語で解説して: "'
alias fixit='claude -P "このエラーを修正して。修正後のコードを表示して: "'

# 2. 設定を反映
source ~/.zshrc

# 3. 試してみる
review "app.py"
```

---

## 🎁 このプレゼントはAI Conduitからお届けしています

毎日最新AIニュースを自動配信中！
- 📺 YouTube: https://www.youtube.com/@AI.Conduit
- 📸 Instagram: https://www.instagram.com/aiconduit/
- 🐦 X: https://x.com/AIconduit777

**コメントに「AI」と書いてくれた方にこのプレゼントをお届けしています🎁**

次回の動画もお楽しみに！Claude Codeで開発速度10倍を目指しましょう！🚀