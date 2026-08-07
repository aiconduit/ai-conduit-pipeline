# 🤖 AI Conduit 無料プレゼント

## Claude Code 神機能・完全チートシート（モバイル & MCP & 時短テク集）

---

### 🚀 神機能1: モバイルでコードレビュー＆PR承認を完了する

**スマホでClaude Codeを使う3ステップ:**

```bash
# 1. Claudeアプリをインストール（iOS/Android対応）
# 2. 右上の「Code」タブをタップ
# 3. GitHubリポジトリに接続して、そのままPR承認！

# おすすめモバイルコマンド:
gh pr list          # レビュー待ちPRを一覧表示
gh pr review --approve   # モバイルから1タップで承認！
gh pr merge --squash     # マージまで完結
```

**モバイルで使える最強ショートカット:**

| コマンド | 効果 | 時短効果 |
|---------|------|---------|
| `/review` | 変更ファイル全レビュー | 約10分→1分 |
| `/fix` | 指摘箇所を自動修正 | 手修正の5倍速 |
| `/test` | テストコード自動生成 | 30分→3分 |

---

### 🚀 神機能2: MCPでClaude Codeを無限に拡張する

**MCP（Model Context Protocol）とは:** Claude Codeに外部ツール連携機能を追加するプロトコル

**今すぐ追加すべきMCPサーバー5選:**

```bash
# 1. GitHub MCP - イシュー・PR管理を自動化
claude mcp add github -- npx @modelcontextprotocol/server-github

# 2. ファイルシステムMCP - プロジェクト横断で検索
claude mcp add filesystem -- npx @modelcontextprotocol/server-filesystem ./projects

# 3. Notion MCP - ドキュメント連携
claude mcp add notion -- npx @modelcontextprotocol/server-notion

# 4. PostgreSQL MCP - DBスキーマ確認しながら開発
claude mcp add postgres -- npx @modelcontextprotocol/server-postgres

# 5. Fetch MCP - ドキュメント自動取得
claude mcp add fetch -- npx @modelcontextprotocol/server-fetch
```

**MCP活用プロンプト例:**
```
「このPRの変更内容をNotionのプロジェクトページに要約して投稿して」
「DBスキーマを確認して、usersテーブルにemail_indexを追加するマイグレーションを作成して」
```

---

### 🚀 神機能3: Subagent並列処理で時短5倍

**並列処理で複数タスクを同時実行:**

```bash
# 従来: 1つずつ実行 → 15分
# 並列: 3つのSubagentで同時実行 → 3分!

claude --multi-agent "フロントエンドのバグ修正、APIの単体テスト作成、README更新を並列で実行して"
```

**Subagentを使いこなすプロンプト:**
```
「Subagentを3つ起動して:
 1. 認証モジュールのコードレビュー
 2. バックエンドのテストカバレッジ計測
 3. 型定義の整合性チェック
 をそれぞれ実行して、結果をまとめて報告して」
```

---

### ⚡ 今日から使える5つの超実用コマンド

```bash
# 1. プロジェクト全体の技術負債を可視化
claude "TODO・FIXME・HACKコメントを全ファイルから抽出して、重要度別に分類して"

# 2. コードベースのドキュメント自動作成
claude "各モジュールの役割を説明するdocs/modules.mdを自動作成して"

# 3. リファクタリング提案を30秒で取得
claude "このプロジェクトのアーキテクチャ改善ポイントを5つ提示して"

# 4. 依存パッケージの脆弱性チェック
claude "package.jsonの依存関係を監査して、アップデートすべきパッケージを挙げて"

# 5. コミットメッセージ自動生成
claude "ステージングされた変更を分析して、Conventional Commits形式でコミットメッセージを提案して"
```

---

### 📋 保存版! Claude Code 必携チートシート

| カテゴリ | コマンド/プロンプト | 用途 |
|---------|-------------------|------|
| **基本** | `/init` | プロジェクト初期セットアップ |
| **基本** | `/clear` | コンテキストリセット |
| **レビュー** | `/review` | コードレビュー実行 |
| **デバッグ** | `/debug` | エラー箇所を自動特定 |
| **テスト** | `/test` | テストコード生成 |
| **リファクタ** | `/refactor` | リファクタリング提案 |
| **高速化** | `--model claude-sonnet-4-20250514` | 最速モデル指定 |
| **並列** | `--agents 3` | 3つのSubagentで並列実行 |
| **自動化** | `--dangerously-skip-permissions` | 確認なしで高速実行 ※要注意 |
| **継続** | `--resume` | 前回のセッション再開 |

---

### 🎯 モバイル開発者向け 時短5倍テンプレ

**移動中に全部終わらせるプロンプト集:**

```
# 朝の通勤中（5分で完了）
「昨夜の全PRの変更をレビューして、問題点をリストアップして。緊急対応が必要なものだけ詳細に説明して」

# ランチ中（3分で完了）
「今日のイシューを優先度順に並べて、最初の3つを実装する計画を立てて」

# 帰宅中（10分で完了）
「developブランチの未マージ変更をテストして、マージ可否を判断して。問題なければマージまで実行して」
```

---

## このプレゼントはAI Conduitからお届けしています

毎日最新AIニュースを自動配信中！

- YouTube: https://www.youtube.com/@AI.Conduit
- Instagram: https://www.instagram.com/aiconduit/
- X: https://x.com/AIconduit777

コメントに「AI」と書いてくれた方にこのプレゼントをお届けしています🎁

**💡 次回動画の予告:** 「Claude Codeでモバイル開発を完全自動化する方法」をお届け予定! チャンネル登録をお忘れなく!