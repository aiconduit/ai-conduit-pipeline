# Claude Code の Code Documenter - 実践テンプレート

## この動画で学んだこと
Code Documenter エージェントを設定すれば、ソースコードから自動でドキュメントを生成でき、手作業のドキュメント作成が不要になります。

## すぐに使えるテンプレート

### 1️⃣ `agents/documenter.md`（エージェント定義）

```markdown
# Documenter エージェント
# -------------------------------------------------
# 目的: 指定されたソースコードファイルから
#       Markdown 形式の API ドキュメントを自動生成する
# -------------------------------------------------

## 設定
name: documenter
description: |
  ソースコード（Python, JavaScript, TypeScript など）を解析し、
  関数・クラス・メソッドの概要、引数、戻り値、例外、使用例を
  Markdown 形式で出力します。

## プロンプト
You are a professional software documentation writer.
Given the following source code, generate a concise but complete
Markdown documentation that includes:

- File overview
- Each public class / function / method
  - Description
  - Parameters (name, type, description)
  - Return value (type, description)
  - Raises / Exceptions (if any)
  - Example usage (if applicable)

Please keep the output in valid Markdown and do not add any extra text
outside the documentation.

## 入力例
```
// ここに対象ファイルのパスを入力してください
/path/to/your/file.py
```

## 出力例
```markdown
# file.py

## 概要
このモジュールは...

### `def foo(bar: int) -> str`
**説明**: ...

**引数**
- `bar` (int): ...

**戻り値**
- `str`: ...

**例**
```python
result = foo(42)
```
```

```

### 2️⃣ ドキュメント生成コマンド（ターミナルで実行）

```bash
# Claude Code のルートディレクトリで実行
# agents フォルダに上記の documenter.md を置いた後、以下のコマンドで任意のファイルをドキュメント化

claude-code run documenter --file /path/to/your/file.py > docs/file.md
```

> **ポイント**  
> - `--file` オプションで対象ファイルを指定  
> - `> docs/file.md` で出力結果を `docs` ディレクトリ配下の Markdown ファイルにリダイレクト  
> - 複数ファイルをまとめて処理したいときはシェルスクリプトや `find` コマンドと組み合わせても OK

### 3️⃣ 便利なワンライナー（複数ファイル一括処理）

```bash
# src ディレクトリ以下の .py ファイルをすべてドキュメント化
mkdir -p docs
find src -name "*.py" -print0 | while IFS= read -r -d '' file; do
  out="docs/$(basename "${file}" .py).md"
  claude-code run documenter --file "$file" > "$out"
  echo "✅ $file → $out"
done
```

## 使い方

1. **Claude Code リポジトリをクローン**（または既にインストール済みの場合はスキップ）  
   ```bash
   git clone https://github.com/anthropic/claude-code.git
   cd claude-code
   ```

2. **`agents` フォルダにテンプレートを配置**  
   ```bash
   mkdir -p agents
   cp /path/to/your/documenter.md agents/
   ```

3. **対象ファイルを指定してドキュメント生成**  
   ```bash
   claude-code run documenter --file /absolute/path/to/your/file.py > docs/file.md
   ```

4. **生成された Markdown を確認**  
   ```bash
   cat docs/file.md
   # 必要に応じて README.md へ統合したり、GitHub Pages で公開したりできます
   ```

5. **（任意）複数ファイルを一括で処理**  
   上記の「便利なワンライナー」を利用して、プロジェクト全体の API ドキュメントを自動生成。

## よくある質問

**Q1: 対応しているプログラミング言語は？**  
**A:** 現在は Python、JavaScript、TypeScript、Go、Java など、主流の言語でうまく動作します。言語固有の構文が正しく解析できない場合は、エージェントの `description` を調整してください。

---

**Q2: 出力される Markdown のスタイルをカスタマイズしたい**  
**A:** `agents/documenter.md` の `## プロンプト` 部分を書き換えることで、項目の順序や見出しレベル、追加したいセクション（例: `Dependencies`）を自由に指定できます。

---

**Q3: 大規模プロジェクトで処理が遅いと感じる**  
**A:** `claude-code` は API 呼び出しベースなので、同時に複数のファイルを並列実行すると高速化できます。`xargs -P` や GNU Parallel を併用してください。例:
```bash
find src -name "*.py" -print0 | xargs -0 -n1 -P4 -I{} sh -c '
  out="docs/$(basename "{}" .py).md"
  claude-code run documenter --file "{}" > "$out"
  echo "✅ {} → $out"
'
```

---

**Q4: 生成されたドキュメントに誤情報が混ざっている**  
**A:** Claude は生成モデルなので、完全に正確とは限りません。自動生成後は必ず人間がレビューし、必要に応じて手修正してください。特に **例外 (Raises)** や **例示コード** は実際の挙動と照らし合わせることが重要です。

---

**Q5: エージェントが見つからない、または `run` コマンドが失敗する**  
**A:**  
1.