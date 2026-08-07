# 🤖 AI Conduit 無料プレゼント

## Claude Code 5倍速化 完全チートシート - settings.json・環境変数・MCP完全版

---

### 🚀 1. settings.json 基本テンプレート（コピペでOK）

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git *)",
      "Read",
      "Write",
      "Edit"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(sudo *)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "node .claude/check-lint.js"
          }
        ]
      }
    ]
  },
  "model": "claude-sonnet-4-20250514",
  "includeCoAuthoredBy": true,
  "cleanupPeriodDays": 30
}
```

**✅ 効果**: コマンド確認が毎回消えて、作業スピードが約5倍に！

---

### ⚡ 2. 環境変数でできるカスタマイズ7選

| 環境変数 | 設定値 | 効果 |
|---------|--------|------|
| `ANTHROPIC_API_KEY` | `sk-ant-...` | APIキーを直接設定 |
| `ANTHROPIC_MODEL` | `claude-opus-4-20250514` | 最強モデルに切替 |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | `32000` | 出力トークン数拡大 |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | `1` | 不要な通信を遮断して高速化 |
| `CLAUDE_CODE_ENABLE_COREPACK` | `1` | Corepack有効化 |
| `HTTPS_PROXY` | `http://proxy:8080` | プロキシ環境対応 |
| `NO_COLOR` | `1` | 色なしモードでログ解析しやすく |

**設定コマンド例**:
```bash
export ANTHROPIC_MODEL=claude-opus-4-20250514
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=32000
```

---

### 🛠️ 3. 最強MCPサーバー厳選5選

| MCPサーバー | 用途 | 導入コマンド |
|------------|------|-------------|
| **Playwright MCP** | ブラウザ自動操作・E2Eテスト | `npx @playwright/mcp@latest` |
| **GitHub MCP** | issue管理・PR自動作成 | `npx @modelcontextprotocol/server-github` |
| **Filesystem MCP** | 高度なファイル操作 | `npx @modelcontextprotocol/server-filesystem` |
| **Supabase MCP** | DB操作・SQL自動生成 | `npx @supabase/mcp-server-supabase` |
| **Memory MCP** | プロジェクト記憶の永続化 | `npx @modelcontextprotocol/server-memory` |

**設定ファイル（`.mcp.json`）**:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "your_token_here" }
    }
  }
}
```

---

### 🔥 4. 即効性のある便利コマンド10選

```bash
# プロジェクト全体のコード品質チェック
/claude review

# テスト自動作成（全ファイル対象）
/テスト作成

# コードリファクタリング
/リファクタリング 対象: src/

# コミットメッセージ自動作成
git diff | claude -p "コミットメッセージを生成して"

# バグ原因の特定
claude -p "エラーを分析して修正案を3つ提示して" --include-error

# サブエージェントで並列処理
claude --agents code-reviewer,test-writer

# 既存コードのドキュメント生成
claude -p "プロジェクトのREADME.mdを自動生成して"

# セキュリティ監査
claude -p "依存パッケージの脆弱性をチェックして"

# パフォーマンス改善提案
claude -p "ボトルネックを特定して最適化案を提示して"

# コードレビュー自動化（GitHub Actions連携）
claude -p "PRの変更点をレビューして指摘事項を列挙して"
```

---

### 📝 5. 超実践プロンプト集（コピペで使用）

```markdown
# 1. フルスタック実装プロンプト
「この要件を実装してください。
- フロント: React + TypeScript + Tailwind
- バック: Node.js + Express
- DB: PostgreSQL + Prisma
- テスト: Jest + React Testing Library
- エラー処理: 全APIにtry-catch実装
- コメント: 日本語でJSDoc付与
まず設計書を作成し、承認後に実装を開始してください。」

# 2. バグ修正プロンプト
「以下のエラーを修正してください。
1. エラーログを分析
2. 根本原因を特定
3. 修正コードを実装
4. テストを追加
5. 修正内容を要約して報告
エラー: [エラー内容を貼り付け]」

# 3. コードレビュープロンプト
「このコードをシニアエンジニア目線でレビューしてください。
- セキュリティ脆弱性
- パフォーマンス問題
- コード重複
- 命名規則
- テスト網羅性
- 改善提案（具体的なコード付き）」
```

---

### 🎯 6. Subagent 並列処理テンプレート

```bash
# 3つのSubagentを同時起動して効率化
claude --agents \
  "code-generator: 新機能の実装コードを生成" \
  "test-writer: テストコードを並行して作成" \
  "documenter: ドキュメントを更新" \
  --task "ログイン機能を実装して"
```

**Subagent用スキルファイル（`.claude/skills/`）**:

```markdown
# スキル: コードレビュー
## 実行手順
1. 変更ファイル一覧を取得
2. 各ファイルをセキュリティ・パフォーマンス・可読性でチェック
3. 問題点を優先度付きでリスト化
4. 具体的な修正コードを3案提示
## 注意点
- プルリクエストの差分のみを対象にする
- 指摘は必ずコード例を添える
```

---

### 📊 7. 5倍速化チェックリスト

| 設定項目 | 完了 | 効果 |
|---------|-----|------|
| permissions.allow 設定 | ☐ | コマンド確認が激減 |
| hooks 自動チェック設定 | ☐ | 手動チェック不要に |
| 環境変数でモデル最適化 | ☐ | 処理速度・品質向上 |
| MCPサーバー追加 | ☐ | できることが爆発的に拡大 |
| Subagent設定 | ☐ | 並列処理で時間短縮 |
| スキルファイル作成 | ☐ | AIの精度が向上 |

---

### 💡 8. トラブルシューティング

```bash
# 設定をリセットしたい場合
rm -rf ~/.claude/settings.json

# キャッシュクリアで高速化
rm -rf ~/.claude/cache

# デバッグモードで動作確認
claude --debug

# 現在の設定確認
claude config list

# MCPサーバーの状態確認
claude mcp list
```

---

## 📚 保存推奨リンク集

- **公式ドキュメント**: https://docs.anthropic.com/claude-code
- **GitHubリポジトリ**: https://github.com/anthropics/claude-code
- **MCPサーバー一覧**: https://github.com/modelcontextprotocol/servers
- **Best Practices**: https://github.com/anthropics/claude-code-best-practices

---

## このプレゼントはAI Conduitからお届けしています

毎日最新AIニュースを自動配信中！

- 📺 YouTube: https://www.youtube.com/@AI.Conduit
- 📸 Instagram: https://www.instagram.com/aiconduit/
- 🐦 X: https://x.com/AIconduit777

**コメントに「AI」と書いてくれた方にこのプレゼントをお届けしています🎁**

このチートシートを保存して、Claude Codeで最速コーディングを実現してください！💪