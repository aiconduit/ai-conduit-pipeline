# Claude Codeでレビューが読み取り専用化 - 実践テンプレート

## この動画で学んだこと
Claude Code のエージェント「reviewer」に対して **Write** と **Edit** のツール使用を禁止し、レビューを読み取り専用にする設定方法を学びました。

## すぐに使えるテンプレート
以下の内容を **`.claude/agents/reviewer.md`** というファイルにそのまま貼り付けてください。  
※既に同名ファイルがある場合は上書きするか、必要に応じてマージしてください。

```markdown
---
# reviewer エージェントの設定
# ここに記述した frontmatter がエージェントの振る舞いを決定します

name: reviewer               # エージェントの名前（必須）
description: "コードレビューを行うが、書き込み・編集は行わない"  # 任意の説明

# ツール使用制限
# Write と Edit のツールを禁止することで、レビューは読み取り専用になります
disallowedTools:
  - Write
  - Edit

# 必要に応じて許可したいツールがあればここに列挙
# allowedTools:
#   - Search
#   - Browse
---

# 使い方のヒント
以下は reviewer エージェントを呼び出す際の例です。実際のコマンドはご利用の Claude Code 環境に合わせてください。

```bash
# 例: reviewer エージェントにコードを渡してレビューを依頼
claude code run reviewer --file src/main.py
```

```

## 使い方
1. **ファイル作成**  
   プロジェクトのルートに `.claude/agents/` ディレクトリが無い場合は作成し、`reviewer.md` を作成します。

2. **テンプレート貼り付け**  
   上記のテンプレート全体（コードブロック部分）を `reviewer.md` にコピー＆ペーストします。

3. **保存**  
   ファイルを保存し、Claude Code が自動的に設定を読み込みます。

4. **レビュー実行**  
   ターミナルやエディタの統合コマンドから `claude code run reviewer --file <対象ファイル>` を実行すると、書き込み・編集が禁止された状態でレビュー結果が出力されます。

## よくある質問

**Q1: 既に `reviewer.md` が存在しますが、設定だけ追加したいです。**  
**A:** 既存ファイルの frontmatter 部分に以下を追記してください。  
```yaml
disallowedTools:
  - Write
  - Edit
```  
既に `disallowedTools` がある場合は `Write` と `Edit` をリストに加えるだけで OK です。

---

**Q2: `disallowedTools` を設定したのに、まだ書き込みができてしまいます。**  
**A:**  
1. ファイルを保存した後、Claude Code が設定を再読み込みしたか確認してください。  
2. 設定ファイルのインデントが正しく YAML 形式になっているかチェックします（スペース2つが一般的です）。  
3. それでも解決しない場合は、Claude Code のキャッシュをクリアして再起動してみてください。

---

**Q3: 書き込みは禁止したいが、コメント追加は許可したいです。**  
**A:** 現在の Claude Code の設定ではツール単位での許可/禁止が基本です。`Comment` のような専用ツールが提供されていれば `allowedTools` に列挙し、`Write` と `Edit` を除外してください。ツールが無い場合は、エージェント側でコメントのみを出力するようプロンプトを調整する必要があります。

---

**Q4: `disallowedTools` に他にどんなツールがありますか？**  
**A:** 主なツールは以下の通りです（バージョンにより追加・削除があります）。  
- `Write` – ファイル書き込み  
- `Edit` – 既存ファイル編集  
- `Create` – 新規ファイル作成  
- `Delete` – ファイル削除  
- `Search` – コード検索  
- `Browse` – 外部リソース参照  

必要に応じて `allowedTools` と組み合わせて細かく制御してください。

---

AI Conduit: https://www.youtube.com/@AI.Conduit