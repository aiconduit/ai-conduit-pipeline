# Claude Codeで自動レビューAIを安全に！ - 実践テンプレート

## この動画で学んだこと
Claude Code のサブエージェント機能を使って、コードレビュー専用の AI エージェントを作成し、**Write** と **Edit** ツールの使用を禁止することで安全に自動レビューを実行できます。

---

## すぐに使えるテンプレート

以下の内容をそのままコピーして、プロジェクトのルートに **`.claude/agents/reviewer.md`** という名前のファイルとして保存してください。

```markdown
# reviewer エージェント設定
# -------------------------------------------------
# このエージェントはコードレビュー専用です。
# Write, Edit ツールは使用できないように制限しています。
# -------------------------------------------------

name: reviewer               # エージェント名（必須）

# 使用禁止にしたいツールをカンマ区切りで列挙
disallowedTools: Write, Edit

# 任意で追加できる設定例
# description: "コードレビューに特化した Claude エージェント"
# temperature: 0.2          # 出力の確定度（低めにすると安定した回答）
# maxTokens: 2000           # 1 回の呼び出しで生成できる最大トークン数
```

> **ポイント**  
> - `name` はエージェントを呼び出す際の識別子です。  
> - `disallowedTools` に `Write, Edit` を入れることで、コードの自動生成・自動修正を防ぎ、レビューのみを行わせます。  
> - 必要に応じて `description` や `temperature` などの追加設定をコメントアウトしたまま残しておくと、後から調整しやすいです。

---

## 使い方

1. **ファイル作成**  
   プロジェクトのルートに `.claude/agents/` ディレクトリが無い場合は作成し、上記テンプレートを `reviewer.md` として保存します。

2. **Claude Code にエージェントをロード**  
   ターミナルでプロジェクトディレクトリに移動し、以下のコマンドを実行します（Claude Code がインストール済みであることが前提です）。

   ```bash
   claude code agent load .claude/agents/reviewer.md
   ```

3. **レビューを実行**  
   任意のコードファイル（例: `src/main.py`）に対してレビューを依頼します。

   ```bash
   claude code review src/main.py --agent reviewer
   ```

   - `--agent reviewer` で先ほど作成したエージェントを指定します。  
   - 出力はターミナルに表示され、必要に応じて `--output review.txt` でファイルに保存できます。

4. **結果を確認**  
   レビュー結果は AI が指摘した問題点や改善提案が列挙されます。`Write` や `Edit` が禁止されているため、**自動修正は行われません**。手動で修正を行う際の参考にしてください。

---

## よくある質問

**Q1: `disallowedTools` に他のツールも追加できますか？**  
A: はい。`Write, Edit, Execute, Browse` など、Claude Code が提供するツール名をカンマ区切りで列挙すれば同様に禁止できます。

**Q2: エージェントが正しくロードされない場合はどうすればいいですか？**  
A:  
1. ファイルパスが正しいか確認（`.claude/agents/reviewer.md` が存在するか）。  
2. `claude code version` で Claude Code のバージョンが最新か確認。  
3. エラーメッセージが出た場合は、`--debug` オプションを付けて詳細情報を取得し、設定ファイルの構文エラーがないかチェックしてください。

**Q3: `temperature` を変更したいのですが、どこに書けばいいですか？**  
A: テンプレートのコメントアウトされた行を参考に、`temperature: 0.2` のように数値を追加してください。低いほど決定的な回答になり、高いほど創造的な回答になります。

**Q4: エージェントに日本語での指示を追加したいです。**  
A: `description` フィールドに日本語の説明を書けば、エージェントの概要として表示されます。例:

```markdown
description: "コードレビューに特化した Claude エージェント（日本語対応）"
```

**Q5: 複数ファイルを一括でレビューしたいです。**  
A: `claude code review` コマンドは glob パターンを受け付けます。例:

```bash
claude code review "src/**/*.js" --agent reviewer
```

---

AI Conduit: https://www.youtube.com/@AI.Conduit