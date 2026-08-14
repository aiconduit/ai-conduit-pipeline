# Claude Codeで安全な自動コードレビュー – 実践テンプレート

## この動画で学んだこと
Claude Code のエージェントに **Write** と **Edit** のツール使用を禁止する設定を追加するだけで、コードレビューを安全に自動化できます。

---

## すぐに使えるテンプレート  

以下の内容をそのままコピーして、プロジェクトのルートに **`.claude/agents/reviewer.md`** というファイルを作成してください。

```markdown
---
# エージェントの名前
name: reviewer

# 使用禁止ツールを列挙（カンマ区切りで複数指定可）
disallowedTools: Write, Edit
---

# Claude Code Reviewer エージェント

<!--
このエージェントはコードレビュー専用です。
`disallowedTools` に Write と Edit を設定することで、Claude がコードの
自動生成・自動修正を行うことを防ぎ、レビュー結果のみを出力させます。
-->

## 目的
- 既存コードの品質・セキュリティチェック
- バグや潜在的な脆弱性の指摘
- コーディング規約への適合確認

## 使用例
```bash
# 例: プロジェクトの src ディレクトリ全体をレビュー
claude code review --agent reviewer --path ./src
```

## カスタマイズポイント
- `disallowedTools` に追加で禁止したいツールがあればカンマで列挙
- `name` は任意の識別子に変更可能（例: `my-reviewer`）
```

---

## 使い方

1. **ディレクトリを作成**  
   ```bash
   mkdir -p .claude/agents
   ```

2. **テンプレートを貼り付け**  
   上記のコードブロック全体をコピーし、`.claude/agents/reviewer.md` に保存します。

3. **Claude Code を実行**  
   ```bash
   # 例: src ディレクトリをレビュー
   claude code review --agent reviewer --path ./src
   ```

4. **レビュー結果を確認**  
   標準出力または指定した出力ファイルに、コードレビューのコメントが表示されます。

---

## よくある質問

**Q1: `disallowedTools` に他に指定できるツールは？**  
**A:** 現在 Claude Code が提供しているツールは `Write`, `Edit`, `Execute`, `Search` などがあります。禁止したいツールをカンマ区切りで列挙してください。

**Q2: エージェント名を変えても動作しますか？**  
**A:** はい。`name:` の値を任意の文字列に変更し、`--agent` オプションで同じ名前を指定すれば動作します。

**Q3: 既存のエージェント設定と衝突しませんか？**  
**A:** 同一ディレクトリ内に同名のエージェントファイルがある場合は上書きされます。衝突を避けるにはファイル名をユニークにしてください。

**Q4: `Write` や `Edit` が禁止されていると、レビューでコード修正提案は出ませんか？**  
**A:** 修正提案はテキストとして出力されますが、Claude が自動的にコードを書き換えることはありません。手動で適用してください。

**Q5: どうやって出力結果をファイルに保存できますか？**  
**A:** `--output` オプションを付与すると、指定したパスに結果が保存されます。例:  
```bash
claude code review --agent reviewer --path ./src --output review_report.md
```

---

AI Conduit: https://www.youtube.com/@AI.Conduit