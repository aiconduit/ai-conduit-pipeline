# Claude Code の Code Documenter - 実践テンプレート

## この動画で学んだこと
Code Documenter エージェントを設定すれば、ソースコードから自動でドキュメントを生成できるので、手作業のドキュメント作成にかかる時間を大幅に削減できます。

## すぐに使えるテンプレート  

### 1️⃣ `agents/documenter.md`（エージェント定義）

```markdown
# Code Documenter エージェント
# -------------------------------------------------
# 目的: 指定したソースコードファイル／ディレクトリから
#       Markdown 形式の API ドキュメントを自動生成する
# -------------------------------------------------

name: documenter
description: |
  ソースコードを解析し、関数・クラス・メソッドの概要・引数・戻り値・例外を
  Markdown で出力します。Python、JavaScript、TypeScript、Java など主要言語に対応。

# 使うモデル（Claude のバージョンは環境に合わせて変更してください）
model: claude-3-5-sonnet-20241022

# プロンプトテンプレート
prompt: |
  以下のコードを解析し、Markdown 形式でドキュメントを作成してください。
  - ファイル名・行番号をヘッダーに含める
  - 各関数/メソッドについて、概要、引数、戻り値、例外、使用例を記載する
  - 必要に応じてコードブロックを挿入する

  ```{{code}}```

# 入力形式
# `code` フィールドに対象ファイルの内容を渡す
input_schema:
  type: object
  properties:
    code:
      type: string
      description: 対象ソースコード全体
  required:
    - code

# 出力形式（Markdown テキスト）
output_schema:
  type: string
  description: 生成された Markdown ドキュメント
```

> **ポイント**  
> - `model` は Claude の最新モデルを指定してください（例: `claude-3-5-sonnet-20241022`）。  
> - `prompt` では `{{code}}` プレースホルダーが実際のコードに置き換わります。  
> - `input_schema` と `output_schema` は Claude Code が自動で検証します。

### 2️⃣ ドキュメント生成コマンド例

```bash
# 例: Python ファイル src/main.py のドキュメントを生成
claude-code run documenter \
  --input-file src/main.py \
  --output-file docs/main.md
```

> **オプション解説**  
> - `run` : エージェントを実行するサブコマンド  
> - `documenter` : 作成したエージェント名（上記 `name` と同じ）  
> - `--input-file` : 解析対象のソースコードファイル（相対パスまたは絶対パス）  
> - `--output-file` : 生成された Markdown を保存するパス  

### 3️⃣ 複数ファイル・ディレクトリを一括処理したいとき

```bash
# src ディレクトリ以下の全 .py ファイルをまとめて docs ディレクトリへ出力
find src -name "*.py" -print0 | while IFS= read -r -d '' file; do
  out="docs/$(basename "${file%.*}").md"
  claude-code run documenter --input-file "$file" --output-file "$out"
done
```

## 使い方

1. **エージェントファイルを配置**  
   - プロジェクトのルートにある `agents` フォルダに `documenter.md` を作成し、上記テンプレートを貼り付けます。

2. **Claude Code CLI をインストール**（未インストールの場合）  
   ```bash
   npm install -g @anthropic/claude-code
   # または
   brew install claude-code
   ```

3. **認証情報を設定**（API キーが必要）  
   ```bash
   export CLAUDE_API_KEY=your_api_key_here
   ```

4. **対象ファイルでドキュメント生成**  
   ```bash
   claude-code run documenter --input-file path/to/file.py --output-file path/to/doc.md
   ```

5. **結果を確認**  
   - `path/to/doc.md` をエディタで開くと、Markdown 形式の API ドキュメントが出力されています。

## よくある質問

**Q1. 対応言語は何ですか？**  
A: 現在は Python、JavaScript、TypeScript、Java、Go、C# など主要言語をサポートしています。言語固有の構文解析は Claude の大規模言語モデルが自動で行うため、基本的にどの言語でも同じエージェントで利用可能です。

**Q2. 大きなプロジェクトでファイル数が多いときはどうすればいいですか？**  
A: 上記「複数ファイル・ディレクトリを一括処理したいとき」のシェルスクリプトを活用してください。`find` コマンドで対象ファイルを列挙し、ループ内で `claude-code run` を呼び出すことで自動化できます。

**Q3. 生成されたドキュメントの品質が低い場合は？**  
A: `documenter.md` の `prompt` 部分を調整すると改善できます。たとえば「関数の説明は 2 文以内にまとめる」や「例外は必ず列挙する」など、具体的な指示を追加してください。

**Q4. 出力形式を HTML にしたいです。**  
A: 現在のエージェントは Markdown を出力しますが、`prompt` 内で「HTML 形式で出力してください」と指示すれば、HTML でも生成可能です。その場合は `output_schema` の説明を `HTML` に変更してください。

**Q5. API キーが漏洩したかもしれません。**  
A: すぐに Anthropic の管理コン