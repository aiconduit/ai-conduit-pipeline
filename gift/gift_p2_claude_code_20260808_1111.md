# 🤖 AI Conduit 無料プレゼント

## 【3倍速】MCPサーバー完全チートシート - 開発効率を劇的に変える7つの黄金ルール

---

### 🔥 まず知るべき最重要コマンド3選

```bash
# 1. プロジェクトにMCPサーバーを追加（最速ルート）
claude mcp add github -- npx @modelcontextprotocol/server-github

# 2. 追加済みMCPサーバー一覧を確認
claude mcp list

# 3. MCPサーバーの接続テスト
claude mcp test github
```

**所要時間: 約30秒。これだけでAPI接続の手書きコードが完全に消えます。**

---

### 📦 開発が10倍速くなる必須MCPサーバー5選

| ランク | MCPサーバー名 | 導入コマンド | 消える作業 |
|--------|--------------|--------------|-----------|
| 🥇 | **GitHub MCP** | `claude mcp add github -- npx @modelcontextprotocol/server-github` | PR作成・Issue管理・コードレビューの自動化 |
| 🥈 | **Filesystem MCP** | `claude mcp add fs -- npx @modelcontextprotocol/server-filesystem ./` | ファイル操作・プロジェクト横断検索 |
| 🥉 | **Puppeteer MCP** | `claude mcp add puppeteer -- npx @modelcontextprotocol/server-puppeteer` | ブラウザ操作・スクリーンショット・E2Eテスト |
| 4位 | **PostgreSQL MCP** | `claude mcp add pg -- npx @modelcontextprotocol/server-postgres "postgresql://user:pass@localhost:5432/db"` | SQLクエリ生成・スキーマ設計 |
| 5位 | **Slack MCP** | `claude mcp add slack -- npx @modelcontextprotocol/server-slack` | 通知・チャットからのタスク作成 |

**✅ 導入チェックリスト:**
- [ ] `claude mcp list` で全サーバーが「✓ connected」表示
- [ ] `.mcp.json` ファイルがプロジェクト直下に存在
- [ ] チームメンバーと `claude mcp` 設定を共有済み

---

### 🎯 即効性のあるプロンプト実例5選（コピペOK）

#### 1. 新規機能開発を3分で開始
```
このリポジトリの既存パターンを分析して、/src/components に
新しいボタンコンポーネントを作成してください。
テストコードとStorybookも自動生成して。
```

#### 2. バグ修正が10倍速くなる魔法のプロンプト
```
tests/ ディレクトリの失敗テストを全て実行して、
失敗原因を特定したら自動修正してください。
修正後は再テストして全てグリーンにするまで繰り返して。
```

#### 3. コードレビューの自動化
```
`git diff main...HEAD` の変更をレビューして。
バグの可能性、セキュリティリスク、パフォーマンス改善点を
3つのカテゴリに分けて報告してください。
```

#### 4. ドキュメント自動作成
```
プロジェクト全体のアーキテクチャを分析して、
docs/ARCHITECTURE.md に日本語で詳細な設計ドキュメントを作成。
Mermaid図も含めて。
```

#### 5. リファクタリングの完全自動化
```
src/utils/ 配下の全ファイルを分析し、
重複コードを抽出して共通モジュールにまとめてください。
既存テストが全て通ることを確認したら完了です。
```

---

### ⚡ 上級者向け: 3倍速を実現するSubagent活用術

**並列処理で待ち時間ゼロを実現:**

```bash
# 3つのSubagentを同時起動して並列処理
claude --agents 3 --prompt "
1. Agent A: フロントエンドのテスト作成
2. Agent B: バックエンドのAPIドキュメント生成
3. Agent C: データベーススキーマの最適化提案
各エージェントは独立して実行し、結果を /tmp/output に保存して。
"
```

**コンテキスト分離の極意:**
- 大規模プロジェクトは`claude --resume`でセッション分割
- タスクごとに`/clear`でコンテキストリセット
- メモリ使用量が70%超えたら`/compact`実行

---

### 🚀 1日の開発フロー最適化テンプレート

| 時間帯 | 作業 | MCP活用ポイント |
|--------|------|----------------|
| 9:00 | タスク整理 | GitHub MCPでIssue一覧を自動取得 |
| 9:30 | コーディング | Filesystem MCPでファイル横断検索 |
| 13:00 | テスト実行 | Puppeteer MCPでE2Eテスト自動化 |
| 15:00 | コードレビュー | GitHub MCPでPR自動作成 |
| 17:00 | ドキュメント | 全変更を自動でCHANGELOG.mdに反映 |

---

### 💎 最終チェックリスト（保存して毎日確認）

```
□ claude mcp list で全接続が正常稼働
□ Claude Codeのバージョンが最新（claude --version で確認）
□ プロンプトに必ず「テスト実行して確認」を含める
□ エラー時は `claude --debug` でログ確認
□ 週1回はMCPサーバーのアップデート確認
```

---

## このプレゼントはAI Conduitからお届けしています

毎日最新AIニュースを自動配信中！

- 📺 YouTube: https://www.youtube.com/@AI.Conduit
- 📸 Instagram: https://www.instagram.com/aiconduit/
- 🐦 X: https://x.com/AIconduit777

コメントに「AI」と書いてくれた方にこのプレゼントをお届けしています🎁

**動画の3倍速テクニックを今すぐ実践してください！**