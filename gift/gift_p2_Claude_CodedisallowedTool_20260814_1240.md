# Claude Code disallowedTools テンプレート - 実践テンプレート

## この動画で学んだこと
Claude Code のスキル（エージェント）に `disallowedTools` を設定すれば、Write・Edit ツールが誤って実行されてもコードが勝手に書き換えられることを防げます。

## すぐに使えるテンプレート
以下のファイルを **そのままコピー&ペースト** して `.claude/agents/reviewer.md` に保存してください。  

```markdown
---
# ★ エージェント定義 ★
# name: エージェントの識別子（動画では reviewer）
# description: 任意で説明を書けます
name: reviewer
description: "コードレビュー専用エージェント（Write・Edit を禁止）"

# ★ ツール制限 ★
# disallowedTools: このエージェントが使用できないツールを列挙します
#   - Write   : ファイルの新規作成・上書き
#   - Edit    : 既存ファイルのインライン編集
disallowedTools:
  - Write
  - Edit
---

# 🎯 目的
このエージェントは **コードレビュー** のみを行い、実際のコード変更は行わせません。  
不意のコード改変やファイル削除を防ぎ、レビュー結果はコメントとして出力します。

## 使用例
```bash
# Claude Code を起動（例）
claude code --agent reviewer path/to/your/project
```

> **※** `--agent reviewer` の部分は、作成したエージェント名（ここでは `reviewer`）を指定してください。  
> エージェントが起動すると、`Write` と `Edit` ツールは利用できない旨の警告が表示され、レビューのみが実行されます。  
```

## 使い方
1. **ファイル作成**  
   - ターミナルでプロジェクトのルートに `.claude/agents/` ディレクトリが無ければ作成します。  
   ```bash
   mkdir -p .claude/agents
   ```
   - 上記テンプレートをコピーし、`.claude/agents/reviewer.md` として保存します。

2. **Claude Code を起動**  
   - エージェントを指定して Claude Code を実行します。  
   ```bash
   claude code --agent reviewer .
   ```
   - これで `Write` と `Edit` がブロックされ、レビュー結果だけが出力されます。

3. **レビュー結果の確認**  
   - 標準出力または指定したログファイルに、コードレビューのコメントが表示されます。  
   - 必要に応じて手動でコードを修正してください（エージェント自体は変更しません）。

## よくある質問

**Q1: `disallowedTools` に他のツールも追加できますか？**  
**A:** はい。`Write`・`Edit` 以外にも `Delete`、`Rename` など Claude Code が提供するツール名を列挙すれば同様にブロックできます。例:  
```yaml
disallowedTools:
  - Write
  - Edit
  - Delete
```

**Q2: エージェント名を変えたらどうすればいいですか？**  
**A:** `name:` フィールドを好きな名前に変更し、Claude Code 起動時に `--agent <新しい名前>` を指定すれば OK です。

**Q3: それでもコードが書き換わってしまう場合は？**  
**A:**  
1. `.claude/agents/` 配下に正しいファイルがあるか確認。  
2. `claude code --debug` でデバッグ情報を出し、エージェントが正しく読み込まれているかチェック。  
3. 設定ミスが無いか `disallowedTools` のインデントやハイフンが正しいか再確認してください。

**Q4: `Write` と `Edit` を許可したいが、特定のファイルだけブロックしたいですか？**  
**A:** 現在の `disallowedTools` はツール単位のブロックです。ファイル単位で制御したい場合は、エージェント側でカスタムスクリプト（例: `.claude/hooks/`）を組み合わせる必要があります。

---

AI Conduit: https://www.youtube.com/@AI.Conduit