# Claude Code の disallowedTools 設定テンプレート - 実践テンプレート

## この動画で学んだこと
`disallowedTools` をエージェントの設定ファイルに追加するだけで、危険なツール（bash・curl など）の実行を完全にブロックできることを学びました。  

## すぐに使えるテンプレート
以下の内容を **そのままコピー＆ペースト** して、プロジェクトのルートにある `.claude/agents/reviewer.md` に保存してください。  

```markdown
# .claude/agents/reviewer.md
---
# エージェントの基本情報
name: reviewer                     # エージェント名（ファイル名と同じにしてください）
description: "コードレビューを自動化するエージェント"   # 任意の説明
model: claude-3-5-sonnet-20240620  # 使用したい Claude モデル

# エージェントが利用できるツール（必要なものだけ列挙）
tools:
  - search                         # ウェブ検索
  - python                         # Python REPL

# ★危険なツールはここでブロック ★
# disallowedTools に列挙したツールはエージェントから呼び出せません。
# 例: bash, exec, curl, wget, sql, ... など
disallowedTools:
  - bash
  - exec
  - curl
  - wget
  - python                         # 必要に応じて除外（上の tools で許可したい場合は削除）
  - sql
  - javascript
  - ruby
  - php
  - perl
  - powershell
  - system
  - subprocess
  - eval
  - open
  - write_file
  - delete_file
  - rename_file
  - list_directory
  - make_directory
  - remove_directory

# エージェントのプロンプト（任意でカスタマイズ）
prompt: |
  あなたは優秀なコードレビューアです。以下のコードを読み、バグやセキュリティリスク、可読性の改善点を指摘してください。
  - 変更は必ず具体的に示すこと
  - 実装例は提示しない（実装は別エージェントに任せる）
  - 禁止されたツールは絶対に使用しないこと
---
```

> **ポイント**  
> - `tools` に列挙したものだけが利用可能です。  
> - `disallowedTools` に入れたツールは **すべて** ブロックされます。  
> - `python` を許可したい場合は `tools` に残し、`disallowedTools` からは削除してください。

## 使い方
1. **ディレクトリを作成**  
   ```bash
   mkdir -p .claude/agents
   ```
2. **テンプレートを保存**  
   上記の Markdown を ` .claude/agents/reviewer.md ` に貼り付けて保存します。  
3. **エージェントを起動**（例）  
   ```bash
   # Claude Code CLI がインストールされている前提
   claude code run reviewer --input "以下のコードをレビューしてください。" 
   ```
   - `--input` にはレビューしたいコードやファイルパスを渡します。  
   - エージェントは `disallowedTools` に列挙された危険なコマンドを実行しようとした場合、エラーを返します。

## よくある質問

**Q1: `disallowedTools` に何を入れれば安全ですか？**  
**A:** 公式ドキュメントに記載されている「危険なツール」リスト（`bash`, `exec`, `curl`, `wget`, `python` など）をすべて列挙してください。必要に応じて自分のプロジェクトで危険と判断したツールを追加します。

---

**Q2: `python` を使いたいがブロックしたくない場合は？**  
**A:** `tools` セクションに `python` を残し、`disallowedTools` から `python` 行を削除すれば利用可能になります。

---

**Q3: 既存のエージェントに後から `disallowedTools` を追加できますか？**  
**A:** はい。対象の `.md` ファイルを編集し、`disallowedTools` セクションを追記または更新すれば即時反映されます。