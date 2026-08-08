# 🤖 AI Conduit 無料プレゼント

## Claude Codeで社内AI基盤を10分で構築する - 完全チートシート

---

## 📋 CLAUDE.md マスター術（社内AI基盤の核）

### 1. 最強のCLAUDE.mdテンプレート（即コピペOK）

```markdown
# プロジェクト基本情報
- プロジェクト名: [プロジェクト名]
- 技術スタック: TypeScript / Next.js / PostgreSQL
- パッケージマネージャー: pnpm
- テストフレームワーク: Vitest

# コーディング規約
- 関数名: camelCase / コンポーネント名: PascalCase
- インポート順: 外部 → 内部 → 相対パス
- エラーハンドリング: 必ずtry-catchでラップする
- 型定義: 必ず明示的にexportする

# 会社固有の用語集
- 「顧客」→ `customer`（`user`は使わない）
- 「受注」→ `order`（`purchase`は使わない）
- ステータス: `draft` → `confirmed` → `shipped` → `delivered`

# 禁止事項
- `any`型の使用禁止
- `console.log`の本番コードへの残置禁止
- 既存APIエンドポイントの変更は必ず承認を得る

# コミットメッセージ規約
- 形式: `type(scope): 説明`
- 例: `feat(auth): ログイン機能を追加`
- 種類: feat / fix / refactor / docs / test / chore
```

### 2. 10分で社内AI基盤を構築する手順

```bash
# 1. プロジェクト直下に移動
cd your-project

# 2. CLAUDE.mdを作成
touch CLAUDE.md

# 3. チーム共有のCLAUDE.mdをコピー
cp /社内共有/CLAUDE.md ./CLAUDE.md

# 4. サブディレクトリごとにカスタマイズ
mkdir -p .claude/skills

# 5. 動作確認
claude "このプロジェクトの構造を教えて"
```

---

## 🚀 即戦力プロンプト集（5選）

### 3. 毎日使える超人気プロンプト

**① コードレビュー依頼**
```
このPRの変更点をレビューして。特に以下をチェック：
1. セキュリティリスク
2. パフォーマンス問題
3. コード規約違反
修正提案は具体的なコード付きでお願いします。
```

**② バグ調査アシスタント**
```
このエラーログを分析して：
[エラーログを貼り付け]
考えられる原因を3つ挙げて、それぞれの解決策を教えて。
```

**③ リファクタリング提案**
```
このファイルをリファクタリングしたい：
- 現在のコード: [コードを貼り付け]
- 改善ポイントを5つ挙げて
- 各ポイントに修正後のコード例を含めて
```

**④ テストコード自動生成**
```
この関数のテストコードを生成して：
[関数を貼り付け]
- 正常系・異常系・境界値のケースを含めて
- Vitestの形式で出力して
```

**⑤ ドキュメント自動生成**
```
このコードのJSDocコメントとREADMEを作成して：
- 引数と戻り値の説明
- 使用例
- 注意点・制約事項
```

---

## 🔧 MCPサーバー活用チートシート

### 4. 社内AI基盤を強化するMCP設定

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
    "database": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/db"
      }
    },
    "internal-docs": {
      "command": "python",
      "args": ["path/to/internal-docs-server.py"],
      "env": {
        "DOCS_PATH": "/社内ドキュメント"
      }
    }
  }
}
```

### 5. 社内MCPサーバーを自作する最小コード

```python
# internal-tools-server.py
from mcp.server import Server
import json

app = Server("internal-tools")

@app.tool()
def get_employee_info(employee_id: str) -> dict:
    """社員情報を取得する"""
    # 社内DBから取得する処理
    return {"id": employee_id, "name": "山田太郎"}

@app.tool()
def search_internal_docs(query: str) -> list:
    """社内ドキュメントを検索する"""
    # 社内Wikiを検索する処理
    return [{"title": "入社手続き", "url": "https://wiki.internal/handbook"}]

if __name__ == "__main__":
    app.run()
```

---

## 📊 コマンドチートシート

### 6. 覚えておくと生産性が10倍になるコマンド

| コマンド | 効果 | 使用頻度 |
|---------|------|---------|
| `/compact` | 会話を圧縮してコンテキストを整理 | ⭐⭐⭐⭐⭐ |
| `/context` | 現在のコンテキストを確認 | ⭐⭐⭐⭐ |
| `/model` | 使用モデルを切り替え（Opus→Sonnet） | ⭐⭐⭐ |
| `shift+tab` | コードブロックを折りたたむ | ⭐⭐⭐⭐ |
| `claude --resume` | 最後のセッションを再開 | ⭐⭐⭐⭐⭐ |
| `claude --continue` | 特定セッションを継続 | ⭐⭐⭐⭐ |
| `/add-dir` | プロジェクトの一部だけをコンテキストに追加 | ⭐⭐⭐⭐ |
| `/pr` | 現在のブランチのPRを作成 | ⭐⭐⭐⭐ |

### 7. 効率化のためのエイリアス設定

```bash
# ~/.zshrc に追加
alias cc="claude"
alias cc-continue="claude --continue"
alias cc-resume="claude --resume"
alias cc-mcp="claude --mcp-config .mcp.json"
alias cc-debug="claude --debug -v"
alias cc-print="claude --print 'このプロジェクトの要約を3行で'"
```

---

## 🎯 スキルファイル活用術

### 8. チームで共有するスキル定義

```markdown
# .claude/skills/code-review/SKILL.md

# コードレビュースキル

## チェックリスト
1. **セキュリティ**: インジェクション、認証・認可の漏れ
2. **パフォーマンス**: N+1クエリ、不要な再レンダリング
3. **可読性**: 変数名、関数の長さ（20行以内）
4. **テスト**: エッジケースのカバレッジ

## 出力形式
- 問題点を重要度（🔴必須 / 🟡推奨 / 🟢任意）で分類
- 各指摘に修正例のコードを必ず含める
- 最後に総合評価（5段階）と次のアクションを提案
```

---

## 📝 新入社員オンボーディング用プロンプト

### 9. プロジェクト理解を爆速化するプロンプト

```
このプロジェクトに新しくアサインされました。
以下の観点でプロジェクトを解説してください：

1. アーキテクチャ全体図（ディレクトリ構造から推測）
2. 主要なビジネスロジックの流れ
3. データベーススキーマの概要
4. デバッグ・テストの実行方法
5. 開発フロー（ブランチ戦略、デプロイ手順）

各項目3分で理解できるレベルに要約してください。
```

---

## 💡 実践テクニック集

### 10. チームで9ヶ月使い続けるための運用ルール

```yaml
# CLAUDE.md運用ルール
# 1. 毎週金曜日にCLAUDE.mdをレビュー
# 2. 新しく学んだベストプラクティスは即追記
# 3. プロジェクト構造が変わったら必ず更新
# 4. 用語集は新しいビジネス用語が出たらすぐ追加
# 5. エラー事例と解決策も記録していく
```

---

## ⚡ 即効テクニックまとめ

- **CLAUDE.md** → 会社のルール・用語・規約を書くだけで毎回文脈を自動理解
- **MCPサーバー** → 社内DB・ドキュメント・ツールをClaudeに接続
- **スキルファイル** → チームのノウハウをAIに教え込む
- **プロンプト集** → 定型作業を一発で実行

---

## このプレゼントはAI Conduitからお届けしています

毎日最新AIニュースを自動配信中！
- **YouTube**: https://www.youtube.com/@AI.Conduit
- **Instagram**: https://www.instagram.com/aiconduit/
- **X**: https://x.com/AIconduit777

コメントに「AI」と書いてくれた方にこのプレゼントをお届けしています🎁

**#ClaudeCode #AIコーディング #MCP #チートシート #社内AI基盤 #AIConduit**