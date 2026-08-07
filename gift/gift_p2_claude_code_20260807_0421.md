# 🤖 AI Conduit 無料プレゼント
## 【スマホでClaude Code完全攻略】モバイルAIコーディングチートシート

動画で紹介した「スマホでClaude Code使う裏技3選」を、さらに深掘りした完全版チートシートをお届けします！

---

## 📱 スマホ×Claude Code の基本セットアップ

### 裏技①：ClaudeアプリのCodeタブ活用
スマホ版Claudeアプリには、デスクトップ版とほぼ同等の機能が搭載されています。

**おすすめ設定：**
```
1. Claudeアプリを開く → 下部タブから「Code」を選択
2. GitHub連携を有効化（Settings → Connections → GitHub）
3. リポジトリを選択して即コーディング開始
```

### 裏技②：モバイル最適化プロンプト
スマホでClaude Codeを使う際は、**短く具体的な指示**が鍵です。

**基本テンプレート：**
```
[ファイルパス]の[機能]を修正して。変更点は[要件]に従って。
テストも忘れずに。
```

---

## 🚀 すぐ使える！実践プロンプト集

### 1. 電車内3分コードレビュー用プロンプト
```bash
# PRレビューをスマホで完結させる魔法のプロンプト
@claude /review
# 対象: 最新のPR diff
# チェック項目: バグ、セキュリティ、パフォーマンス、コードスタイル
# 出力形式: 重要度順にリストアップ、修正案も提示
```

### 2. モバイルコミットメッセージ生成
```
git diff を分析して、以下の形式でコミットメッセージを3つ提案して：
- 1行要約（50文字以内）
- 変更内容の箇条書き
- 影響範囲の説明
```

### 3. 緊急バグ修正プロンプト
```
[エラーログ]を分析して：
1. 原因の特定（コード行まで）
2. 最小限の修正コード
3. 修正後のテスト手順
※スマホ閲覧用に簡潔に出力して
```

---

## 🛠️ MCP（Model Context Protocol）モバイル活用術

### スマホで使える必須MCPサーバー設定
```json
// .mcp.json に追加
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    },
    "supabase": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-supabase"]
    }
  }
}
```

### MCPクイックコマンド
```bash
# スマホからGitHub操作
/mcp github search "repo:user/repo issue"

# データベース直接クエリ
/mcp supabase query "SELECT * FROM users LIMIT 10"
```

---

## 📋 Claude Code スマホ用チートシート

### 必須スラッシュコマンド
| コマンド | 用途 | スマホでの活用法 |
|---------|------|----------------|
| `/review` | コードレビュー | 電車内でPR確認 |
| `/fix` | バグ修正 | 緊急対応に最適 |
| `/test` | テスト実行 | ビルド確認を外出先で |
| `/explain` | コード解説 | 学習・理解を加速 |
| `/compact` | 会話整理 | トークン節約に必須 |

### モバイル便利ショートカット
```bash
# クイックコード生成
/claude "ReactでTODOアプリ作って"

# ファイル横断検索
/claude "auth関連のファイルを全部見つけて"

# リファクタリング提案
/claude "この関数をよりシンプルに"
```

---

## 💡 上級者向けテクニック

### 1. Subagentによる並列処理
```bash
# スマホでも複数タスクを同時実行
/claude "3つのsubagentで並列処理して：
1. フロントエンドのバグ修正
2. バックエンドのテスト追加  
3. ドキュメント更新"
```

### 2. Hookでモバイル開発を自動化
```yaml
# .claude/hooks.yml
hooks:
  PreToolUse:
    - matcher: "Edit"
      hooks:
        - type: "command"
          command: "npx eslint --fix"
  PostToolUse:
    - matcher: "Test"
      hooks:
        - type: "command" 
          command: "notify-send 'テスト完了'"
```

### 3. Skillでスマホ操作を最適化
```markdown
# .claude/skills/mobile-dev/SKILL.md
---
name: mobile-dev
description: スマホ開発に最適化したコード生成
---
- レスポンシブ対応必須
- タッチ操作を考慮したUI設計
- モバイルファーストで実装
- パフォーマンス最適化を常に意識
```

---

## 📊 モバイルコーディング生産性3倍テンプレ

### 朝の通勤時（15分）
```bash
/claude "今日のタスクを整理して"
# → 前日の続きから自動で再開
```

### 昼休み（10分）
```bash
/claude "PRのレビューリクエストを確認して"
# → コメントに返信まで自動化
```

### 夜の帰宅時（20分）
```bash
/claude "今日の変更をテストして問題ないか確認"
# → 明日に備えた準備完了
```

---

## 🎯 まとめ：スマホでClaude Codeを使いこなす3つのポイント

1. **短く具体的なプロンプト**で指示する
2. **MCPサーバー**でデータベースやGitHubに直接アクセス
3. **スラッシュコマンド**を駆使して素早く操作

ぜひ、このチートシートをスマホのメモに保存して、毎日の開発に活用してください！

---

## このプレゼントはAI Conduitからお届けしています
毎日最新AIニュースを自動配信中！
- YouTube: https://www.youtube.com/@AI.Conduit
- Instagram: https://www.instagram.com/aiconduit/
- X: https://x.com/AIconduit777
コメントに「AI」と書いてくれた方にこのプレゼントをお届けしています🎁