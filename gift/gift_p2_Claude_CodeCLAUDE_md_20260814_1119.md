# Claude CodeのCLAUDE.mdで指示の手間がゼロになった - 実践テンプレート

## この動画で学んだこと
プロジェクトのルートに **CLAUDE.md** を置くだけで、Claude Code にコーディング規約やスタイルガイドを自動的に認識させ、毎回の指示を書かずに済むようになります。

---

## すぐに使えるテンプレート
以下の内容をそのままコピーして、プロジェクトのルートディレクトリに **`CLAUDE.md`** として保存してください。  
※必要に応じて自分のチームやプロジェクトに合わせて編集してください。

```markdown
# CLAUDE.md – Claude Code 用プロンプトテンプレート

## 📌 目的
このファイルは Claude Code に対して、プロジェクト全体で守るべき **コーディング規約・スタイルガイド・設計方針** を一括で指示するためのテンプレートです。  
Claude Code はこのファイルを自動的に読み取り、以降のコード生成・レビュー・リファクタリングで常にこの指示を適用します。

---

## 🛠️ コーディング規約（例）

### 1. 言語・フレームワーク
- 使用言語: **TypeScript (strict mode)**  
- フレームワーク: **React 18 + Next.js 14**  
- パッケージマネージャ: **pnpm**  

### 2. コーディングスタイル
- **Prettier** と **ESLint** を必ず適用（`npm run lint` / `npm run format` が成功すること）  
- 1 行の最大文字数は **100文字**  
- 変数・関数名は **camelCase**、クラス・型は **PascalCase**  
- 可能な限り **型注釈** を付与し、`any` の使用は禁止  

### 3. コメント・ドキュメント
- 関数・メソッドの上に **JSDoc** 形式で必ずコメントを書く  
- 重要なロジックやアルゴリズムには **TODO** / **FIXME** タグを付け、理由を明記  

### 4. テスト
- ユニットテストは **Jest**、E2E テストは **Playwright** を使用  
- すべての新規機能は **テストカバレッジ 80%以上** を目指す  

### 5. セキュリティ・パフォーマンス
- ユーザー入力は必ず **バリデーション** し、サニタイズすること  
- 重い処理は **Web Workers** または **Serverless Functions** にオフロード  

---

## 📦 必要なツール・コマンド

```bash
# 1️⃣ プロジェクト作成（例）
pnpm create next-app my-project --ts

# 2️⃣ 必要パッケージのインストール
cd my-project
pnpm add -D eslint prettier eslint-config-prettier eslint-plugin-react eslint-plugin-react-hooks @typescript-eslint/parser @typescript-eslint/eslint-plugin jest @types/jest ts-jest playwright

# 3️⃣ ESLint と Prettier の初期設定
pnpm exec eslint --init   # 途中で "To check syntax, find problems, and enforce code style" を選択
pnpm exec prettier --write .   # すべてのファイルを整形

# 4️⃣ テストスクリプトの追加（package.json の scripts 部分）
#   "test": "jest",
#   "test:e2e": "playwright test",
#   "lint": "eslint . --ext .ts,.tsx",
#   "format": "prettier --write ."

# 5️⃣ Claude Code の起動（例）
# Claude Code がインストール済みの場合、プロジェクトルートで以下を実行
claude-code .
```

> **ポイント**  
> `claude-code .` を実行すると、Claude Code が自動的に `CLAUDE.md` を読み込み、以降のコード生成・レビューで上記規約を適用します。

---

## 使い方
1. **テンプレートを保存**  
   - 上記の Markdown 全文を `CLAUDE.md` という名前でプロジェクトのルートに保存します。

2. **プロジェクトに合わせてカスタマイズ**  
   - 言語・フレームワーク、使用している Linter/Formatter、テストツールなどが異なる場合は、該当箇所を書き換えてください。

3. **Claude Code を起動**  
   - ターミナルでプロジェクトディレクトリに移動し、`claude-code .` を実行します。  
   - 以降、Claude Code にコード生成やレビューを依頼すると、`CLAUDE.md` の指示が自動的に適用されます。

4. **変更が必要になったら**  
   - `CLAUDE.md` を編集し、保存すれば次回以降の Claude Code の挙動が即座に反映されます。

---

## よくある質問

**Q1. CLAUDE.md が認識されない場合はどうすればいいですか？**  
**A:**  
1. ファイル名が正しく `CLAUDE.md`（大文字・拡張子含む）になっているか確認。  
2. プロジェクトのルートディレクトリで `claude-code .` を実行しているか確認。  
3. Claude Code のバージョンが最新か `claude-code --version` で確認し、必要ならアップデートしてください。

---

**Q2. 既存プロジェクトに導入したいのですが、設定が衝突しそうです。**  
**A:**  
- まずは `CLAUDE.md` に **「現在の設定を上書きしない」** 旨を書き加