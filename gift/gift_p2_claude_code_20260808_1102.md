# 🤖 AI Conduit 無料プレゼント

## Claude Code 作業効率化 完全チートシート - 許可自動化で3倍速エンジニアリング

### 📋 動画で紹介した設定を今すぐコピペ！

---

## 1️⃣ 許可自動化の決定版設定（.claude/settings.json）

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(npm test)",
      "Bash(git *)",
      "Bash(ls *)",
      "Bash(cat *)",
      "Read(*)",
      "Write(*)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(sudo *)",
      "Bash(ssh *)"
    ]
  },
  "model": "opus",
  "customInstructions": "変更前に必ず影響範囲を列挙してから実行すること"
}
```

**効果**: 毎回の許可待ちがなくなり、作業時間が **87%短縮**（約3時間→23分）

---

## 2️⃣ プロジェクト別 許可テンプレート 3選

### 🔹 Node.js / TypeScript プロジェクト用
```json
{
  "permissions": {
    "allow": [
      "Bash(npm run dev)",
      "Bash(npm run build)",
      "Bash(npx tsc --noEmit)",
      "Bash(npm install *)"
    ]
  }
}
```

### 🔹 Python プロジェクト用
```json
{
  "permissions": {
    "allow": [
      "Bash(python -m pytest)",
      "Bash(pip install *)",
      "Bash(uv run *)"
    ]
  }
}
```

### 🔹 Git 操作をフル自動化
```json
{
  "permissions": {
    "allow": [
      "Bash(git add *)",
      "Bash(git commit -m *)",
      "Bash(git push *)",
      "Bash(git pull)"
    ]
  }
}
```

---

## 3️⃣ 超実践！Subagent 並列処理プロンプト

```
あなたはプロジェクトマネージャーです。
以下のタスクを3つのSubagentに並列で割り振ってください：

1. **Subagent A**: コードレビュー担当
   対象ファイル: src/**/*.ts
   チェック項目: 型安全性・エッジケース

2. **Subagent B**: テスト設計担当
   対象: 新規機能のユニットテスト
   カバレッジ目標: 90%以上

3. **Subagent C**: ドキュメント担当
   対象: README.md と API仕様書の更新

各Subagentの結果を統合し、最終レポートを
日本語でMarkdown形式で出力してください。
```

---

## 4️⃣ MCP サーバー設定チートシート

```bash
# 主要MCPサーバーのインストールコマンド

# GitHub連携
claude mcp add github -- npx @modelcontextprotocol/server-github

# データベース接続（PostgreSQL）
claude mcp add postgres -- npx @modelcontextprotocol/server-postgres postgresql://localhost:5432/mydb

# ブラウザ操作自動化
claude mcp add playwright -- npx @modelcontextprotocol/server-playwright

# ファイルシステム操作
claude mcp add filesystem -- npx @modelcontextprotocol/server-filesystem ./projects

# カスタムMCP（自作API）
claude mcp add my-api -- node ./mcp-servers/my-api.js
```

---

## 5️⃣ スラッシュコマンド 厳選10選

| コマンド | 効果 | 使用頻度 |
|---------|------|---------|
| `/review` | 変更コードの即時レビュー | ⭐⭐⭐⭐⭐ |
| `/test` | テストコード自動作成 | ⭐⭐⭐⭐⭐ |
| `/fix` | エラー箇所の自動修正 | ⭐⭐⭐⭐⭐ |
| `/refactor` | リファクタリング提案 | ⭐⭐⭐⭐ |
| `/doc` | ドキュメント自動生成 | ⭐⭐⭐⭐ |
| `/commit` | コミットメッセージ自動作成 | ⭐⭐⭐⭐ |
| `/explain` | コードの動作解説 | ⭐⭐⭐ |
| `/optimize` | パフォーマンス最適化 | ⭐⭐⭐ |
| `/security` | セキュリティ診断 | ⭐⭐⭐ |
| `/init` | プロジェクト初期設定 | ⭐⭐⭐ |

---

## 6️⃣ 3倍速を実現する 魔法のプロンプト集

### 🎯 バグ修正を高速化
```
このエラーを修正してください。
手順:
1. エラーの根本原因を特定
2. 修正案を3つ提案（各メリット/デメリット付き）
3. 最適な案を実装
4. テストで検証
5. 修正内容を簡潔に要約

制約: 既存のコードスタイルを維持すること
```

### 🎯 新機能実装を高速化
```
以下の機能を実装してください:
[機能の説明]

要件:
- 既存のアーキテクチャパターンに従う
- エラーハンドリングを含める
- テストコードも作成
- 実装後に自己レビューして改善点があれば修正

出力形式:
- 変更ファイル一覧
- 変更内容の説明
- テスト結果
```

### 🎯 コードレビューを自動化
```
以下のPRのレビューをしてください:
- 変更ファイル: [ファイル名]
- 変更内容: [変更の説明]

チェック項目:
1. バグの可能性
2. パフォーマンス問題
3. セキュリティリスク
4. コードスタイル
5. テスト不足

各項目を5段階で評価し、修正が必要な箇所には
具体的な修正案を提示してください。
```

---

## 7️⃣ Hook 設定で品質を自動担保

```bash
# .claude/hooks.json を作成
{
  "PreToolUse": [
    {
      "matcher": "Write",
      "hook": "npx eslint --fix $FILE_PATH"
    }
  ],
  "PostToolUse": [
    {
      "matcher": "Bash",
      "hook": "echo \"$(date): $TOOL_NAME executed\" >> .claude/audit.log"
    }
  ]
}
```

**効果**: コード品質を自動チェック + 全操作を監査ログに記録

---

## 8️⃣ セッション効率化 3つの極意

### ✅ コンテキストを最大化する
```
このプロジェクトの全体像を把握してください。
以下の情報を読み込んで整理してください:
1. package.json / requirements.txt
2. README.md
3. 主要ディレクトリ構造
4. 直近のgit log（10件）

その後、プロジェクト構成図と設計方針を
日本語で要約してください。
```

### ✅ 継続開発の効率化
```
前回までの作業内容を引き継いでください。
以下の情報を確認してからタスクを開始してください:
1. .claude/development-log.md を確認
2. 未完了のタスクをリストアップ
3. 現在のブランチ状態を確認
4. 次のアクションを提案

タスク: [新しいタスクの説明]
```

### ✅ エラー解決の高速化
```
このエラーを解決してください。
エラーメッセージ: [エラー内容]

手順:
1. エラーの原因を推測
2. 同様のケースを検索
3. 解決策を実装
4. 検証
5. 予防策を提案

エラーが発生したファイル: [ファイルパス]
```

---

## 9️⃣ スピード比較：設定前 vs 設定後

| 作業内容 | 設定前 | 設定後 | 削減率 |
|---------|--------|--------|--------|
| コード修正 | 3時間 | 23分 | **87%減** |
| テスト実行 | 45分 | 5分 | **89%減** |
| コードレビュー | 2時間 | 15分 | **88%減** |
| ドキュメント作成 | 1.5時間 | 10分 | **89%減** |
| Git操作 | 30分 | 3分 | **90%減** |

---

## 🔟 今日から始める 3ステップ

```bash
# ステップ1: 設定ファイルを作成
mkdir -p .claude
touch .claude/settings.json

# ステップ2: 上記の設定をコピペ

# ステップ3: Claude Codeを再起動
claude
```

**わずか5分の設定で、毎日の作業が3倍速になります！**

---

## 🎁 特典: 実践チェックリスト

- [ ] `.claude/settings.json` に許可ルールを設定した
- [ ] プロジェクト専用の許可リストを作成した
- [ ] Subagentの並列処理を試した
- [ ] MCPサーバーを2つ以上設定した
- [ ] スラッシュコマンドを5個以上覚えた
- [ ] Hookで自動品質チェックを設定した
- [ ] セッション開始プロンプトを保存した

---

## このプレゼントはAI Conduitからお届けしています

毎日最新AIニュースを自動配信中！

- 📺 **YouTube**: https://www.youtube.com/@AI.Conduit
- 📸 **Instagram**: https://www.instagram.com/aiconduit/
- 🐦 **X**: https://x.com/AIconduit777

コメントに「**AI**」と書いてくれた方にこのプレゼントをお届けしています🎁

**💡 次回予告**: 「Claude CodeでMCPを活用した自動化の極意」を配信予定！お見逃しなく！

---

*このチートシートは動画「Claude Codeの作業が3倍速くなる設定」の完全連動特典です。*