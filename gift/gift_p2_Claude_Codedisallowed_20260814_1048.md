# Claude Code の disallowed で不要な書き込み消滅 - 実践テンプレート

## この動画で学んだこと
`disallowedTools` をエージェントの設定ファイルに追加するだけで、レビュー時に不要な書き込み（例: `print` や `console.log`）を自動的に除去できるようになります。

## すぐに使えるテンプレート
以下の内容を **`review_agent.yaml`** という名前で保存してください。  
※ファイルの先頭にある `---` から `---` までが **Front‑Matter** です。  

```yaml
---
# review_agent.yaml
# -------------------------------------------------
#  Claude Code 用エージェント設定ファイル
#  ↓ ここに禁止したいツール（関数・コマンド）を列挙します
# -------------------------------------------------
disallowedTools:
  - print          # Python の標準出力
  - console.log   # JavaScript の標準出力
  - echo           # シェルコマンド
  - logger         # 任意のロガー関数（例: logging.info）
  - debug          # デバッグ用関数全般

# エージェント本体の設定（必要に応じて変更してください）
name: review-agent
description: |
  コードレビュー時に不要な出力を書き込みから除去するエージェントです。
model: claude-3-5-sonnet-20241022   # 使用する Claude モデル
temperature: 0.0
max_output_tokens: 4000

# ここから下は通常のプロンプトや指示を書きます
prompt: |
  あなたはコードレビューエージェントです。以下のコードから
  `disallowedTools` に列挙された関数・コマンドの呼び出しをすべて削除し、
  その結果だけを返してください。削除した行はコメントで残さないでください。
  必要に応じてインデントや構文エラーが出ないように調整してください。
```

## 使い方
1. **ファイルを保存**  
   上記の内容を `review_agent.yaml` としてプロジェクトの任意のディレクトリに保存します。

2. **Claude Code にエージェントをロード**  
   ```bash
   # 例: Claude CLI を使用してエージェントをロード
   claude agents create --file review_agent.yaml
   ```
   *CLI が無い場合は、Claude Code の UI から「エージェント作成」→「YAML を貼り付け」で同様に作成できます。

3. **コードレビューを実行**  
   エージェントが有効になっている状態で、レビューしたいコードを Claude Code に入力すると、`disallowedTools` に列挙した出力系関数が自動的に除去されたコードが返ってきます。

4. **結果を確認・マージ**  
   返されたコードをそのままプロジェクトにマージすれば、不要な `print`/`console.log` 等が残らないクリーンな状態になります。

## よくある質問
**Q1: `disallowedTools` に追加できるのは関数名だけですか？**  
A: 基本は関数名・コマンド名の文字列です。正規表現はサポートされていませんが、`logger` のように汎用的な名前を入れることで、`logger.info` や `logger.debug` もまとめて除去できます。

**Q2: Python 以外の言語でも同じ設定で動きますか？**  
A: はい。Claude Code は言語を意識せずに文字列マッチングで除去を行うため、JavaScript、Go、Ruby などでも同様に機能します。

**Q3: `disallowedTools` に入れた関数が実際には使われていない場合、エラーになりますか？**  
A: いいえ。使用されていないツールは単に無視されます。エラーや警告は出ません。

**Q4: 出力を残したい行だけ除外したい場合はどうすれば？**  
A: その場合はエージェント側の `prompt` をカスタマイズし、除外対象を限定するロジックを書き換えてください。たとえば「`print` は `debug_print` のときだけ残す」等の条件分岐を追加できます。

**Q5: 設定ファイルを複数作りたいときは？**  
A: ファイル名を変えて別々に作成し、用途別にエージェントを切り替えて使用できます。たとえば `review_agent_debug.yaml` と `review_agent_release.yaml` など。

---

AI Conduit: https://www.youtube.com/@AI.Conduit