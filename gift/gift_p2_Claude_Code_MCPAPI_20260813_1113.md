# Claude Code MCPでAPIを自然言語呼び出し - 実践テンプレート

## この動画で学んだこと
Claude Code の **MCP (Multi‑Call Prompt)** 機能を使えば、事前に設定したエンドポイントを自然言語だけで呼び出すことができます。設定ファイルに API のベース URL を登録すれば、`claude --mcp <alias> "<質問>"` だけで結果が取得できます。

---

## すぐに使えるテンプレート

### 1️⃣ `.claude/mcp/config.json`（設定ファイル）

```json
{
  // -------------------------------------------------
  // MCP 用エイリアス設定
  //  key: エイリアス名（任意の文字列）
  //  value: 呼び出したい API のベース URL
  // -------------------------------------------------
  "weather": "https://api.weather.com"
}
```

> **ポイント**  
> - ファイルはホームディレクトリ直下の `.claude/mcp/` に置きます。  
> - 既に他のエイリアスがある場合は、カンマで区切って追加してください。  

### 2️⃣ 実行コマンド例

```bash
# 天気情報を自然言語で取得
claude --mcp weather "東京の天気"
```

> **備考**  
> - `claude` コマンドは **Claude CLI** がインストールされている前提です。  
> - `--mcp` オプションの後にエイリアス名（ここでは `weather`）を指定し、続けて自然言語のリクエストをダブルクオートで囲みます。  

---

## 使い方

1. **Claude CLI をインストール**  
   ```bash
   # macOS / Linux (Homebrew)
   brew install anthropic/cli/claude

   # Windows (PowerShell)
   iwr https://cli.anthropic.com/install.ps1 -UseBasicParsing | iex
   ```

2. **設定ディレクトリを作成**  
   ```bash
   mkdir -p ~/.claude/mcp
   ```

3. **`config.json` を作成・編集**  
   上記の JSON をコピーして `~/.claude/mcp/config.json` に保存します。  
   既に別のエイリアスがある場合は、カンマで区切って追加してください。

4. **MCP コマンドを実行**  
   ```bash
   claude --mcp weather "東京の天気"
   ```
   すると、Claude が自動で `https://api.weather.com` にリクエストし、返ってきた天気情報を自然言語で返答します。

5. **他の API も同様に登録**  
   例: 株価取得 API  
   ```json
   {
     "weather": "https://api.weather.com",
     "stock": "https://api.stockprice.com"
   }
   ```
   そして  
   ```bash
   claude --mcp stock "Apple の株価は？"
   ```

---

## よくある質問

**Q1: `claude` コマンドが見つからないと表示されます。**  
**A:** PATH に CLI が登録されていない可能性があります。インストール後、ターミナルを再起動するか、`export PATH="$HOME/.local/bin:$PATH"`（Linux/macOS）を実行してください。

---

**Q2: `config.json` が読み込まれないとエラーが出ます。**  
**A:**  
- ファイルの場所が正しいか確認（`~/.claude/mcp/config.json`）。  
- JSON の構文エラーがないかチェック（余計なカンマやコメントは除外）。  
- ファイルの権限が読み取り可能か確認（`chmod 644 ~/.claude/mcp/config.json`）。

---

**Q3: 天気情報が返ってこないのですが、URL が正しいか不安です。**  
**A:**  
- `config.json` に記載したベース URL が実際に有効なエンドポイントか確認してください。  
- 必要に応じて API キーやクエリパラメータを URL に組み込むことも可能です（例: `"weather": "https://api.weather.com/v1/current?apikey=YOUR_KEY"`）。  
- それでも取得できない場合は、Claude のログレベルを上げてデバッグ情報を確認します。  
  ```bash
  CLAUDE_LOG=debug claude --mcp weather "東京の天気"
  ```

---

**Q4: 複数のエイリアスを同時に使いたいです。**  
**A:** 1 回のコマンドで 1 つのエイリアスしか指定できませんが、スクリプトやシェルエイリアスで連続実行できます。例:
```bash
#!/usr/bin/env bash
claude --mcp weather "東京の天気"
claude --mcp stock "Apple の株価は？"
```

---

**Q5: 日本語のプロンプトがうまく解釈されません。**  
**A:** Claude は日本語に対応していますが、質問が曖昧だと期待した結果が返らないことがあります。  
- できるだけ具体的に質問する（例: 「今日の東京の天気（最高気温・最低気温・降水確率）を教えて」）。  
- 必要に応じて「単位は摂氏で」などの付加情報を入れると精度が上がります。

---

### 参考リンク
- **Claude CLI ドキュメント**: https://docs.anthropic.com/claude/cli  
- **MCP 公式ガイド**: https://docs.anthropic.com/claude/mcp  

---

Enjoy coding! 🚀  

---  
AI Conduit: https://www.youtube.com/@AI.Conduit