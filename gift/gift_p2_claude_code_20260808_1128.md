# 🤖 AI Conduit 無料プレゼント

## 10倍速で動くAI組織の作り方 - 完全チートシート

**「CLAUDE.mdに全てを集約する」だけでは終わらせない。**
このチートシートには、20人組織を9ヶ月で構築した実践的なノウハウと、**今すぐコピペできるプロンプト・設定ファイル**を詰め込みました。

---

## 🚀 1. CLAUDE.md 完全テンプレート（コピペOK）

この1ファイルで、AIエージェントの作業速度が5倍に変わります。

```markdown
# プロジェクト概要
- プロダクト: [プロダクト名]
- 技術スタック: [Next.js / TypeScript / Supabase など]
- ターゲットユーザー: [ペルソナ定義]

# コーディング規約
- 型定義は必ず `types/` に集約する
- コンポーネントは `components/ui/` に配置
- エラーハンドリングはカスタムフック `useErrorHandler` を使用

# テスト戦略
- ユニットテスト: Vitest + Testing Library
- E2Eテスト: Playwright
- カバレッジ目標: 80%以上

# デプロイフロー
- ステージング: PR作成時に自動デプロイ
- 本番: mainブランチマージ後、GitHub Actionsで自動デプロイ

# AIエージェントへの指示
- タスクを開始する前に、必ず関連ファイルを確認する
- 変更内容は必ずコミットメッセージに日本語で記載する
- 不明点があれば、推測せずに質問する
```

---

## ⚡ 2. 5倍速になる必須プロンプト集

### プロンプト①：仕様理解をスキップ
```
このリポジトリのCLAUDE.mdを読んで、プロジェクトの目的とコーディング規約を理解した上で、
以下のタスクを実行してください:
[タスク内容]
```

### プロンプト②：並列処理でタスク分割
```
このプロジェクトで以下の3つのタスクを並列で実行してください:
1. APIエンドポイントの作成
2. フロントエンドのUI実装
3. テストコードの作成

各タスクは独立したサブエージェントで処理し、最後に統合してください。
```

### プロンプト③：レビュー品質を上げる
```
変更したコードをレビューしてください。以下の観点でチェック:
- 型安全性
- エラーハンドリング
- パフォーマンス
- 命名規則の一貫性

問題があれば、修正案付きで指摘してください。
```

---

## 🔧 3. 実践MCP設定 - 3つの必須サーバー

```json
// .mcp.json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your_token_here"
      }
    },
    "supabase": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-supabase"],
      "env": {
        "SUPABASE_URL": "https://your-project.supabase.co",
        "SUPABASE_KEY": "your_anon_key"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./"]
    }
  }
}
```

---

## 📋 4. 最強コマンドチートシート

```bash
# プロジェクト全体の理解をスキップして即実行
claude -p "このリポジトリを分析して、READMEを生成して"

# 複数ファイルの一括リファクタリング
claude -p "src/ディレクトリ内の全てのコンポーネントをアーキテクチャパターンに従ってリファクタリング"

# テスト駆動開発で新機能を実装
claude -p "まずテストを書き、その後テストが通るように実装してください"

# バグの自動修正
claude -p "npm testを実行して、失敗しているテストを修正してください"

# コミットメッセージの自動生成
claude -p "git diffを確認して、適切なコミットメッセージを提案してください"
```

---

## 📚 5. Claude Code設定ファイル（.claude/settings.json）

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run build)",
      "Bash(npm test)",
      "Read(**)",
      "Edit(**)"
    ],
    "deny": [
      "Bash(git push)",
      "Bash(rm -rf *)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "npx eslint --fix $CLAUDE_FILE"
          }
        ]
      }
    ]
  },
  "model": "claude-sonnet-4-20250514"
}
```

---

## 🎯 6. 20人組織を9ヶ月で構築するロードマップ

| フェーズ | 期間 | 重点タスク |
|---------|------|-----------|
| **Phase 1** | 1-2ヶ月目 | CLAUDE.md作成、MCP設定、CI/CDパイプライン構築 |
| **Phase 2** | 3-5ヶ月目 | サブエージェント活用、コードレビュー自動化、ドキュメント自動生成 |
| **Phase 3** | 6-9ヶ月目 | スケーリング、ナレッジベース構築、AI組織文化の定着 |

---

## 💡 7. 今日から使える3つの秘訣

1. **CLAUDE.mdは毎週更新する**
   チームの学びを毎週金曜日にCLAUDE.mdに反映。これが組織のナレッジベースになります。

2. **サブエージェントを最大活用する**
   1つのタスクを3つのサブエージェントに分割して並列実行。作業時間が3分の1に短縮されます。

3. **フィードバックループを作る**
   `claude -p "このPRのコード品質を評価して改善点を提案して"` を毎日実行。コード品質が劇的に向上します。

---

## 🎁 このプレゼントはAI Conduitからお届けしています

毎日最新AIニュースを自動配信中！

- 📺 **YouTube**: [https://www.youtube.com/@AI.Conduit](https://www.youtube.com/@AI.Conduit)
- 📸 **Instagram**: [https://www.instagram.com/aiconduit/](https://www.instagram.com/aiconduit/)
- 𝕏 **X**: [https://x.com/AIconduit777](https://x.com/AIconduit777)

コメントに「**AI**」と書いてくれた方にこのプレゼントをお届けしています🎁

---

*このチートシートは動画「10倍速で動くAI組織の作り方」と完全連動しています。GitHubのリポジトリもチェックしてみてください！*