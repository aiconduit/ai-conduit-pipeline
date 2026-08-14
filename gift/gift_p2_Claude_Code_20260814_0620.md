# Claude Codeでコードレビューを自動化 - 実践テンプレート

## この動画で学んだこと
Claude Code のエージェント設定に `disallowedTools` を追加するだけで、レビュー時に **Write** と **Edit** ツールを無効化し、純粋なコードレビューだけを実行させることができます。

---

## すぐに使えるテンプレート

### 1️⃣ `.claude/frontmatter.yml`（または `.claude/frontmatter.yaml`）  
```yaml
# .claude/frontmatter.yml
# ここに全体設定を書きます。エージェントごとの設定は個別ファイルで上書きします。
# 例: デフォルトで有効にしたいツールやモデルを指定できます。
# 今回は reviewer エージェントだけで disallowedTools を設定します。
```

### 2️⃣ `.claude/agents/reviewer.md`  
```markdown
---
name: reviewer                # エージェント名（必須）
description: "コードレビュー専用エージェント"  # 任意の説明
disallowedTools:              # ここで無効化したいツールを列挙
  - Write
  - Edit
# 以上で reviewer エージェントは Write/Edit ツールを使用できません。
# 以降は純粋にコードの品質・バグ・ベストプラクティスをチェックします。
---
# reviewer エージェントのプロンプト（必要に応じてカスタマイズ）
以下のコードをレビューしてください。  
- バグやロジックエラーがないか  
- 可読性・保守性の観点で改善点がないか  
- 可能な限り具体的な指摘と修正案を提示してください。

```{{code}}```   # ← 実際にレビューしたいコードをここに埋め込みます
```

---

## 使い方

1. **リポジトリのルートに `.claude` ディレクトリを作成**  
   ```bash
   mkdir -p .claude/agents
   ```

2. **上記テンプレートをそれぞれのパスに保存**  
   - `echo "..." > .claude/frontmatter.yml`  
   - `echo "..." > .claude/agents/reviewer.md`

3. **Claude Code を起動**（例: `claude code run` など、使用している CLI/IDE に合わせて）  
   ```bash
   claude code run --agent reviewer --file path/to/your/code.js
   ```

4. **レビュー結果がターミナル/IDE に表示**されます。  
   必要に応じて指摘を反映し、再度同コマンドでレビューを繰り返すことが可能です。

---

## よくある質問

**Q1. `disallowedTools` に他のツールも追加できますか？**  
**A:** はい。`Write` や `Edit` 以外にも `Search`, `Browse`, `Run` など、Claude Code が提供するツール名を列挙すれば無効化できます。例: `disallowedTools: [Write, Edit, Run]`

---

**Q2. エージェントのプロンプトをカスタマイズしたいです。**  
**A:** `reviewer.md` の `---` 区切りの下にある Markdown 部分がプロンプトです。好きな指示を書き加えるだけで、レビューの方針を変えられます。

---

**Q3. 既存の `.claude/frontmatter.yml` がある場合はどうすれば？**  
**A:** 既存ファイルに追記する形で問題ありません。エージェント固有の設定は `reviewer.md` の `disallowedTools` が優先されます。

---

**Q4. 設定が反映されないときは？**  
**A:**  
1. ファイルのパスが正しいか確認（`.claude/agents/reviewer.md`）。  
2. CLI/IDE のキャッシュをクリアして再起動。  
3. YAML のインデントが正しいか（スペース2つが推奨）をチェック。

---

**Q5. 日本語のコメントが表示されない場合は？**  
**A:** Claude Code は UTF‑8 を前提に動作します。ファイルのエンコーディングが UTF‑8 であることを確認してください。

---

> **AI Conduit**: https://www.youtube.com/@AI.Conduit  

このテンプレートをそのままコピーして、すぐにコードレビュー自動化を体験してください！ 🚀