# 🤖 AI Conduit 無料プレゼント
## Claude Code 完全攻略チートシート - レビュー速度3倍の実践テクニック

---

## 🚀 即戦力！Claude Code 最強コマンド7選

### 1️⃣ コードレビュー高速化コンボ
```bash
# 変更ファイル全体をレビュー（通常の3倍速！）
/review

# 特定のファイルだけを集中レビュー
/review src/app.ts src/utils/helper.ts

# 直近のコミット差分だけをレビュー
/review --diff HEAD~1
```

**プロのコツ**: `/review`実行時に「セキュリティ重視」「パフォーマンス重視」など観点を指定すると、AIの指摘精度が劇的に向上します！

---

### 2️⃣ コード理解を深める /explain 活用法
```bash
# 複雑な関数を日本語で解説してもらう
/explain src/complexAlgorithm.ts

# プロジェクト全体のアーキテクチャを把握
/explain src/ --architecture

# 特定の処理フローを図解付きで理解
/explain src/api/handler.ts --flowchart
```

**活用ポイント**: 新メンバーのオンボーディングや、引き継ぎ資料作成に最適です！

---

### 3️⃣ MCP連携で超効率レビュー
```bash
# MCPサーバー一覧を確認
/mcp list

# 特定のMCPサーバーに接続
/mcp connect github

# MCP経由でGitHubのPR情報を取得しながらレビュー
/review --context "github:PR#123"
```

**おすすめMCPサーバー**:
- **GitHub MCP**: PR情報・Issue連携
- **Database MCP**: スキーマ確認しながらレビュー
- **Jira MCP**: タスク内容と照合しながらレビュー

---

### 4️⃣ カスタムコマンド作成（時間短縮の決定版）
`.claude/commands/review-security.md` を作成：
```markdown
---
description: セキュリティ重視のコードレビュー
argument-hint: [対象ファイル]
---
# セキュリティ観点でのレビュー
1. OWASP Top 10に基づく脆弱性チェック
2. 入力値検証の有無
3. SQLインジェクション対策
4. 認証・認可の実装確認
5. 機密情報のハードコード有無
```

**使い方**: `/review-security src/` で実行！

---

### 5️⃣ プロジェクト全体最適化テクニック
```bash
# コードの重複を一括検出
/review --detect-duplicates

# テストカバレッジが低い箇所を特定
/review --coverage-check

# 非推奨APIの使用箇所を洗い出し
/review --deprecated-scan
```

---

### 6️⃣ レビュー品質を上げるプロンプト集

**基本のプロンプト**:
```
以下のコードをレビューしてください。特に以下をチェック：
1. 潜在的なバグ
2. パフォーマンス問題
3. セキュリティ脆弱性
4. コーディング規約違反
5. テスト不足の箇所

優先度別に指摘し、具体的な修正例も提示してください。
```

---

### 7️⃣ チーム共有用スニペット集

**PR説明文を自動生成**:
```bash
/explain --pr-description
```

**コミットメッセージを自動生成**:
```bash
/commit --conventional
```

---

## ⚡ 実践テクニックまとめ

| 目的 | 最適なコマンド | 所要時間 |
|------|---------------|---------|
| 通常レビュー | `/review` | 3分 |
| セキュリティ特化 | `/review-security` | 5分 |
| コード理解 | `/explain` | 2分 |
| PR確認 | `/review --context "github:PR#123"` | 4分 |
| 重複検出 | `/review --detect-duplicates` | 3分 |

---

## 💡 上級者向けTips

### チーム標準のレビュー基準を設定
`.claude/skills/code-review.md` にチームのコーディング規約を定義しておくと、全メンバーのレビュー品質が統一されます！

### レビュー結果を自動で共有
Hook機能を使ってレビュー結果を自動でSlackやメールに通知可能：
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Review",
        "hooks": [
          {
            "type": "command",
            "command": "notify-slack.sh"
          }
        ]
      }
    ]
  }
}
```

---

## 📋 今すぐ保存！クイックリファレンス

```bash
# このチートシートをClaude Codeで覚えさせる
/remember "レビュー時は必ずセキュリティチェックを含める"
```

---

## このプレゼントはAI Conduitからお届けしています
毎日最新AIニュースを自動配信中！
- YouTube: https://www.youtube.com/@AI.Conduit
- Instagram: https://www.instagram.com/aiconduit/
- X: https://x.com/AIconduit777
コメントに「AI」と書いてくれた方にこのプレゼントをお届けしています🎁