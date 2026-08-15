# Claude Code の図生成テンプレート - 実践テンプレート

## この動画で学んだこと
Claude Code の **Code‑to‑Diagram** 機能を使うだけで、プロジェクト全体のアーキテクチャ図を自動生成でき、SVG 形式で即座に取得できます。

---

## すぐに使えるテンプレート

### 1️⃣ 前提条件（インストール）

```bash
# ① Claude CLI をインストール（Node.js が必要です）
npm install -g @anthropic/claude-cli

# ② API キーを環境変数に設定
#    （Anthropic のコンソールから取得したキーを貼り付けてください）
export ANTHROPIC_API_KEY=your_api_key_here
```

### 2️⃣ プロジェクトのパスを指定して図を生成

```bash
# ③ プロジェクトのルートディレクトリを指定し、SVG だけを出力
claude code to-diagram \
  --path ./my-project \          # ← ここを自分のプロジェクトパスに置き換える
  --output ./architecture.svg \   # 出力ファイル名（拡張子は .svg）
  --format svg                    # SVG 形式で出力（省略可：デフォルトは PNG）
```

> **⚡️ポイント**  
> `--format svg` を付けるとベクター形式なので、拡大縮小しても画質が劣化しません。  
> `--output` で出力先をフルパスにすれば、任意のフォルダへ直接保存できます。

### 3️⃣ 生成された SVG を確認

```bash
# ④ デフォルトの画像ビューアで開く（macOS の例）
open ./architecture.svg

# Windows の場合
start ./architecture.svg

# Linux の場合（例: eog, gnome-open, xdg-open など）
xdg-open ./architecture.svg
```

---

## 使い方

1. **Claude CLI をインストール**  
   `npm install -g @anthropic/claude-cli` を実行し、グローバルにインストールします。

2. **API キーを設定**  
   環境変数 `ANTHROPIC_API_KEY` に自分の API キーを設定します。ターミナルを再起動すると有効になります。

3. **プロジェクトのパスを決める**  
   `--path` オプションに対象プロジェクトのルートディレクトリを指定します。相対パスでも絶対パスでも構いません。

4. **コマンドを実行**  
   上記テンプレートの `claude code to-diagram` コマンドをコピーして貼り付け、Enter キーを押すだけです。

5. **SVG を確認・活用**  
   生成された `architecture.svg` を画像ビューアで開くか、ドキュメントや Wiki に埋め込んで活用してください。

---

## よくある質問

**Q1. 出力が PNG になってしまうのですが、SVG にしたいです。**  
**A:** `--format svg` オプションが抜けている可能性があります。必ず `--format svg` を付与してください。例:  
```bash
claude code to-diagram --path ./my-project --output diagram.svg --format svg
```

---

**Q2. 大規模プロジェクトだと処理に時間がかかります。**  
**A:** `--max-depth` オプションで解析深さを制限できます（デフォルトは無制限）。例:  
```bash
claude code to-diagram --path ./my-project --output diagram.svg --format svg --max-depth 5
```
深さを減らすと高速化しますが、図の詳細度が下がります。

---

**Q3. 特定のディレクトリだけを除外したいです。**  
**A:** `--exclude` オプションで除外パターンを指定できます。複数指定はカンマ区切り。例:  
```bash
claude code to-diagram --path ./my-project \
  --output diagram.svg --format svg \
  --exclude node_modules,tests,docs
```

---

**Q4. 生成された SVG が空白です。**  
**A:** プロジェクトに認識可能なコード（Python, JavaScript, TypeScript, Java など）が含まれているか確認してください。  
また、`--path` が正しいディレクトリを指しているかもチェックしてください。

---

**Q5. 日本語のコメントやファイル名が正しく表示されません。**  
**A:** Claude の解析エンジンは UTF‑8 を前提にしています。ファイルは必ず UTF‑8 エンコーディングで保存してください。  

---

> **※補足**  
> 本テンプレートは **Claude Code 2.0 以降** で動作確認済みです。バージョンが古い場合は `claude --version` で確認し、必要に応じて `npm update -g @anthropic/claude-cli` でアップデートしてください。

---

AI Conduit: https://www.youtube.com/@AI.Conduit