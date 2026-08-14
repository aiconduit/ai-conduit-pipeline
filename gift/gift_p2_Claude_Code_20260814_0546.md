# Claude Codeでレビューが読み取り専用化 - 実践テンプレート  

## この動画で学んだこと  
Claude Code のエージェント「reviewer」を **書き込み・編集ツールを禁止** する設定だけで、レビューを読み取り専用にできます。  

## すぐに使えるテンプレート  

```markdown
# .claude/agents/reviewer.md
---
# エージェント名（必須）
name: reviewer

# 書き込み・編集ツールを禁止する設定
# これにより reviewer はコードの変更やファイル書き込みができなくなります
disallowedTools:
  - Write
  - Edit
---

# ここからはエージェントのプロンプトや説明を書きます
# 例: レビュー時に守るべきガイドラインや、出力フォーマットなど
# （必要に応じて自由にカスタマイズしてください）

## Review Guidelines
- 変更は提案のみ、実際のコードは触らないこと
- 変更箇所は Markdown のコードブロックで示す
- 変更理由は簡潔にコメントとして付与

## Output Format
```suggestion
// 変更前
function foo() { … }

// 変更後（提案）
function foo() { … } // ← ここを修正
```
```

> **※ポイント**  
> - `---` で囲まれた部分が **frontmatter** です。  
> - `disallowedTools` に `Write` と `Edit` を入れるだけで、reviewer は **読み取り専用** になります。  
> - 必要に応じて `allowedTools` で許可したいツールを追加できます。  

## 使い方  

1. **ファイルを作成**  
   ```bash
   mkdir -p .claude/agents
   touch .claude/agents/reviewer.md
   ```
2. **上記テンプレートを貼り付け**  
   エディタで `reviewer.md` を開き、全内容をコピー＆ペーストします。  
3. **Claude Code を再起動**（または設定をリロード）  
   ```bash
   claude code reload   # 例: CLI がある場合
   ```
4. **レビューを実行**  
   例えば `claude code review src/` と実行すると、`reviewer` エージェントが **読み取り専用** でレビューを行います。  

## よくある質問  

**Q1: 既に `reviewer.md` がある場合はどうすればいいですか？**  
A: 既存ファイルの `---` ブロック内に `name: reviewer` と `disallowedTools:` を追記すれば OKです。重複しないように注意してください。  

**Q2: 書き込み禁止にしたくないツールはありますか？**  
A: `allowedTools` キーで明示的に許可したいツールを列挙できます。例:  
```yaml
allowedTools:
  - Read
  - Search
```  

**Q3: 設定が反映されないときは？**  
A:  
1. ファイルのインデントやスペースが YAML の構文エラーになっていないか確認  
2. Claude Code のキャッシュをクリアして再起動（`claude code reload`）  

**Q4: 他のエージェントでも同様の設定はできますか？**  
A: はい。任意のエージェントの `.md` ファイルに同様の `disallowedTools` を追加すれば、ツールの使用を制御できます。  

---  
AI Conduit: https://www.youtube.com/@AI.Conduit