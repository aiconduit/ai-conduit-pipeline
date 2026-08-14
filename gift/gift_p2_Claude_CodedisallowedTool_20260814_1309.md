# Claude Code の disallowedTools 設定テンプレート - 実践テンプレート

## この動画で学んだこと
Claude Code でエージェントが意図せずファイルを書き換えてしまう問題は、エージェント定義ファイルの **`disallowedTools`** に `Write` と `Edit` を追加するだけで簡単に防げます。

## すぐに使えるテンプレート
以下の内容を **`agent.yaml`**（またはご使用中のエージェント定義ファイル）にそのままコピーして貼り付けてください。  
※フロントマター（`---` で囲まれた部分）に一行だけ追記すれば完了です。

```yaml
---
# -------------------------------------------------
# Claude Code エージェント定義ファイル
# 公式ドキュメント: https://docs.anthropic.com/claude/code
# -------------------------------------------------
name: my-awesome-agent          # ← 任意のエージェント名
description: >-
  ファイル操作を行うが、Write と Edit ツールは使用しないよう制限したエージェントです。
# ここから下が今回追加する行です
disallowedTools:
  - Write                       # ファイルの新規作成・上書きは不可
  - Edit                        # 既存ファイルの編集は不可
# -------------------------------------------------
# 以降は既存のエージェント設定（tools, model, etc.）をそのまま記述
# 例:
tools:
  - name: Read
    description: "Read a file from the workspace"
  - name: List
    description: "List files in a directory"
model: claude-3-5-sonnet-20241022
temperature: 0.2
maxTokens: 4000
# -------------------------------------------------
```

> **ポイント**  
> - `disallowedTools` は YAML のリスト形式で記述します。  
> - `Write` と `Edit` を列挙するだけで、Claude Code がこれらのツールを呼び出すことをブロックします。  
> - 既存の `tools` 定義やその他設定はそのまま残してください。

## 使い方
1. **エージェント定義ファイルを開く**  
   - 例: `~/.claude/agents/my-awesome-agent.yaml` など、Claude Code が参照する場所にあるファイルをテキストエディタで開く。

2. **フロントマターに追記**  
   - 上記テンプレートの `disallowedTools` セクションをフロントマター（`---` と `---` の間）に貼り付けるだけです。  
   - 既に `disallowedTools` が存在する場合は、`Write` と `Edit` をリストに追加してください。

3. **保存して Claude Code を再起動**  
   - ファイルを保存したら、Claude Code の UI か CLI でエージェントを再読み込みします。  
   - 例（CLI）: `claude code reload --agent my-awesome-agent`

4. **動作確認**  
   - エージェントに対してファイル書き換えを指示すると、`Tool not allowed: Write` などのエラーメッセージが返ってくることを確認してください。

## よくある質問

**Q1: `disallowedTools` に他に指定できるツールはありますか**  
A: はい。Claude Code が提供するツールは `Read`, `Write`, `Edit`, `List`, `Search`, `Run` などがあります。不要なツールはすべて列挙してブロックできます。

**Q2: 既に `Write` や `Edit` が `tools` に定義されている場合、エラーになりますか**  
A: いいえ。`tools` に定義されたままでも、`disallowedTools` に列挙すれば実行時にブロックされます。ツール自体はエージェントが認識できる状態を保ちます。

**Q3: 設定が反映されないときはどうすればいいですか**  
A:  
1. ファイルのインデントがスペース 2 個で統一されているか確認。  
2. `---` の前後に余計な文字が入っていないかチェック。  
3. Claude Code を完全に再起動（プロセス終了 → 再起動）してみる。

**Q4: `disallowedTools` を使わずにコード側でチェックしたい**  
A: 可能ですが、エージェントレベルでの制御が最も安全です。どうしてもコード側で制御したい場合は、`tool` 呼び出し前に `if tool.name in ["Write","Edit"]: raise Exception("Forbidden")` などのガードを入れます。

---

AI Conduit: https://www.youtube.com/@AI.Conduit