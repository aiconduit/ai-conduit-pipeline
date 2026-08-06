# 🤖 AI Conduit 無料プレゼント
## Claude Code爆速開発マスターガイド - スキル・MCP完全チートシート

この動画で紹介した「Claude Codeスキル活用術」の内容を、すぐに実践できる形にまとめました！保存して今日から活用しましょう👇

---

### 🚀 5つの即戦力スキルテンプレート

#### 1️⃣ スキル基本構造（frontmatter必須）

```markdown
# .claude/skills/your-skill/SKILL.md
---
name: your-skill-name
description: このスキルの説明を具体的に記述（例: プロジェクトのコードレビューを自動化するスキル）
---

# 手順
1. ステップ1（具体的なアクション）
2. ステップ2
3. ステップ3
```

**ポイント**: `description`を詳細に書くほど、Claude Codeが適切なタイミングでスキルを自動呼び出しします！

#### 2️⃣ コードレビュースキル

```yaml
name: code-review
description: PRのコードをレビューし、バグ・セキュリティ問題・改善点を報告する
```

```markdown
# レビュー手順
1. `git diff main...HEAD` で差分を取得
2. 以下の観点でチェック:
   - バグの可能性（Null参照、無限ループ等）
   - セキュリティ（SQLインジェクション、XSS等）
   - パフォーマンス（N+1問題等）
3. 重要度別に問題をリストアップ（Critical / Warning / Suggestion）
4. 修正コードの提案を含める
```

#### 3️⃣ テスト自動生成スキル

```yaml
name: generate-tests
description: 指定された関数やモジュールのユニットテストを自動生成する
```

```markdown
# 手順
1. テスト対象の関数・モジュールを確認
2. 以下をカバーするテストを作成:
   - 正常系（境界値含む）
   - 異常系・エラーハンドリング
   - エッジケース
3. テストコードは`tests/`ディレクトリに配置
4. `npm test`で実行確認
```

#### 4️⃣ リファクタリングスキル

```yaml
name: refactor-code
description: コードの可読性と保守性を向上させるリファクタリングを実行する
```

```markdown
# 手順
1. 対象ファイルの複雑度を分析（行数・ネスト深さ・関数長）
2. 以下のリファクタリングを適用:
   - 共通処理の関数抽出
   - マジックナンバーの定数化
   - 早期リターンでネスト削減
3. リファクタリング後もテストが通ることを確認
4. 変更点をコミットメッセージに明記
```

#### 5️⃣ セキュリティ監査スキル

```yaml
name: security-audit
description: 依存パッケージとコードのセキュリティ脆弱性をチェックする
```

```markdown
# 手順
1. `npm audit` または `pip-audit` で依存関係をチェック
2. コード内の危険パターンをスキャン:
   - `eval()` の使用
   - ハードコードされた認証情報
   - 不適切な入力バリデーション
3. 脆弱性が見つかった場合の修正案を提示
```

---

### ⚡ 作業時間を半減させる5つのスキル呼び出しプロンプト

| 目的 | プロンプト例 |
|------|------------|
| スキル一覧表示 | `/skills` |
| 特定スキル呼び出し | `@code-review を実行して` |
| スキル新規作成 | `新しいスキル「db-migration」を作成して` |
| スキル改善 | `「generate-tests」スキルをPytest対応に更新して` |
| スキル組み合わせ | `code-review後、generate-testsも実行して` |

---

### 🔧 公式バンドルスキル一覧（即利用可能）

```bash
# スキルディレクトリを確認
ls ~/.claude/skills/

# 公式スキルを追加
claude skills add official/code-review
claude skills add official/test-generator
claude skills add official/debug-analyzer
claude skills add official/db-optimizer
claude skills add official/api-designer
```

---

### 📋 MCPチートシート（Model Context Protocol）

| 操作 | コマンド | 説明 |
|------|---------|------|
| MCPサーバー追加 | `claude mcp add github -- transport: "stdio"` | GitHub連携 |
| MCP一覧表示 | `claude mcp list` | 設定済みMCPの確認 |
| MCPテスト | `claude mcp test github` | 接続確認 |
| ファイルサーバー | `claude mcp add filesystem -- transport: "stdio"` | ローカルファイル操作 |

**代表的なMCPサーバー**:
- `@modelcontextprotocol/server-github` — Issue/PR管理
- `@modelcontextprotocol/server-filesystem` — ファイル操作
- `server-puppeteer` — ブラウザ自動操作

---

### 🎯 サブエージェント活用術

```yaml
# .claude/agents/ に配置
---
name: bug-hunter
description: バグの根本原因を特定する専門エージェント
tools: [Read, Grep, Bash, Write]
---

あなたはバグハンターです。以下の手順で調査してください:
1. エラーメッセージを正確に把握
2. 関連ファイルを検索・読解
3. 仮説を立てて検証
4. 根本原因と修正案を報告
```

---

### 💡 上級者向けフック活用

```bash
# .claude/hooks/ に配置するプリフック例
#!/bin/bash
# コミット前にテストを自動実行
if [ "$CLAUDE_TOOL" = "Write" ]; then
  echo "🔄 テスト自動実行中..."
  npm test
fi
```

---

## 🔑 今日から使える5つの重要コマンド

| コマンド | 用途 |
|---------|------|
| `claude skill create my-skill` | スキルを対話式で作成 |
| `claude skill list` | 全スキル一覧を表示 |
| `claude think` | AIに思考プロセスを強制 |
| `claude compact` | 会話コンテキストを最適化 |
| `claude --dangerously-skip-permissions` | 全権限で高速実行 |

---

## このプレゼントはAI Conduitからお届けしています
毎日最新AIニュースを自動配信中！
- YouTube: https://www.youtube.com/@AI.Conduit
- Instagram: https://www.instagram.com/aiconduit/
- X: https://x.com/AIconduit777

コメントに「AI」と書いてくれた方にこのプレゼントをお届けしています🎁
**保存して、動画と一緒に実践してみてください！**