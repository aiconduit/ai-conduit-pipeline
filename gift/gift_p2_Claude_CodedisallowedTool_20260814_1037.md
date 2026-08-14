# Claude CodeのdisallowedToolsで危険なエージェント操作を防止できた – 実践テンプレート

## この動画で学んだこと
`disallowedTools` をエージェント設定に追加するだけで、Claude Code が実行できるツールを制限し、危険な操作や情報漏洩を防げます。

---

## すぐに使えるテンプレート
以下のファイル構成と内容をそのままコピーして、プロジェクトのルートに貼り付けてください。  

```bash
# 1️⃣ ディレクトリを作成（まだ無い場合）
mkdir -p .claude/agents

# 2️⃣ エージェント設定ファイルを作成
cat > .claude/agents/reviewer.md <<'EOF'
# reviewer エージェント設定

## 基本情報
name: reviewer               # エージェント名（任意の名前）
description: "コードレビューを行うエージェントです。"  # 説明文

## ツール制限
# ↓ ここに disallowedTools を列挙します。下記は危険とされる代表例です。
disallowedTools:
  - bash                     # シェルコマンドの実行を禁止
  - python                   # 任意の Python スクリプト実行を禁止
  - node                     # Node.js 実行を禁止
  - curl                     # 外部への HTTP リクエストを禁止
  - wget                     # 外部からファイル取得を禁止
  - exec                     # 任意の外部コマンド実行を禁止
  - eval                     # 動的コード評価を禁止
  - system                   # OS コマンド呼び出しを禁止
  - subprocess               # Python のサブプロセス起動を禁止
  - os                       # Python の os モジュール使用を禁止

## 許可したいツール（必要に応じて追加）
# allowedTools:
#   - git
#   - grep

EOF
```

> **ポイント**  
> - `disallowedTools` に列挙したツールは **すべて** 使用できなくなります。  
> - 必要に応じて `allowedTools` を別途設定し、許可したいツールだけを明示的にリストしてください。  
> - ファイルは **UTF‑8** で保存してください（日本語コメントが正しく表示されます）。

---

## 使い方

1. **プロジェクトのルートに `.claude/agents` ディレクトリを作成**  
   上記の `mkdir -p .claude/agents` コマンドで自動的に作成できます。

2. **エージェント設定ファイル `reviewer.md` を作成**  
   `cat > .claude/agents/reviewer.md` の部分を実行すると、テンプレートがそのまま書き込まれます。  
   エージェント名や説明文は好きなものに書き換えて OK。

3. **Claude Code にエージェントをロード**  
   ```bash
   claude agents load .claude/agents/reviewer.md
   ```
   これで `reviewer` エージェントが起動し、`disallowedTools` に列挙したツールは使用できなくなります。

4. **実際にコードレビューを依頼**  
   ```bash
   claude agents run reviewer "以下の Python スクリプトをレビューしてください。" \
       --code "$(cat path/to/your_script.py)"
   ```
   禁止ツールが呼び出されようとした場合、エージェントはエラーを返します。

5. **必要に応じてツールリストを調整**  
   - **追加したいツール** → `allowedTools` に列挙  
   - **さらに禁止したいツール** → `disallowedTools` に追記  

---

## よくある質問

**Q1. すでに `disallowedTools` を設定しているエージェントがある場合、どうすれば上書きできますか？**  
**A:** 同名のエージェント設定ファイルを再度 `claude agents load` すれば上書きされます。既存ファイルを編集してから再ロードしてください。

---

**Q2. `allowedTools` と `disallowedTools` を同時に書くと矛盾しませんか？**  
**A:** `allowedTools` は **明示的に許可したい** ツールだけを列挙します。`disallowedTools` が優先され、リストに含まれるツールはすべてブロックされます。実務では `disallowedTools` だけで十分なことが多いです。

---

**Q3. `disallowedTools` に入れたツールが実際にブロックされたか確認したいです。**  
**A:** エージェントに対して禁止ツールを使うリクエストを送ると、次のようなエラーメッセージが返ります。  
```bash
$ claude agents run reviewer "bash -c 'ls -la'"
Error: Tool "bash" is disallowed for this agent.
```
このメッセージが出れば設定は正しく機能しています。

---

**Q4. `disallowedTools` にリストできないツールはありますか？**  
**A:** 現在の Claude Code の仕様では、内部で呼び出すすべてのツール名（CLI コマンドや Python モジュール名）を列挙できます。未対応のツールがあれば、公式ドキュメントの「Tool Whitelist/Blacklist」セクションを参照してください。

---

**Q5. 設定ファイルのパスは固定ですか？**  
**A:** デフォルトは `.claude/agents/<agent_name>.md` ですが、`claude agents load <path>` で任意の場所からロード可能です。プロジェクトごとに別のディレクトリに置いても問題ありません。

---

**Q6. Windows 環境でも同じ設定は使えますか？**