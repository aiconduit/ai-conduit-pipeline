# Claude CodeのMCPで外部API連携が自然言語で完結した – 実践テンプレート

## この動画で学んだこと
Claude CodeのMCP（Multi‑Channel Proxy）を `.claude/mcp.json` に設定するだけで、REST API（例：天気情報）を自然言語で呼び出すことができるようになります。  

## すぐに使えるテンプレート
以下のファイル構成と設定をそのままコピーして、プロジェクトのルートに配置してください。

### 1️⃣ `.claude/mcp.json`
```json
{
  // -------------------------------------------------
  // MCP（Multi‑Channel Proxy）設定ファイル
  // -------------------------------------------------
  "servers": [
    {
      // サーバー名（任意の識別子）
      "name": "weather-api",
      // 種類は必ず "rest"
      "type": "rest",
      // ベースURL（実際に呼び出したい API のエンドポイント）
      "baseUrl": "https://api.open-meteo.com/v1/forecast",
      // デフォルトで付与したいクエリパラメータ（必要に応じて追加）
      "defaultParams": {
        "latitude": "35.6895",   // 東京の緯度
        "longitude": "139.6917", // 東京の経度
        "hourly": "temperature_2m"
      },
      // 必要ならヘッダーも設定可能
      "headers": {
        "Accept": "application/json"
      },
      // 取得したレスポンスを Claude が解釈しやすい形に整形したい場合は
      // `responseTransform` で JavaScript 関数を記述できます（省略可）
      // "responseTransform": "(data) => data.hourly.temperature_2m"
    }
  ]
}
```

### 2️⃣ `run-mcp.sh`（Unix/macOS 用）  
```bash
#!/bin/bash
# -------------------------------------------------
# Claude Code の MCP サーバーを起動するスクリプト
# -------------------------------------------------
# 1. .claude ディレクトリが無ければ作成
mkdir -p .claude

# 2. 上記の .claude/mcp.json をプロジェクトルートにコピー
#    （このスクリプトと同じディレクトリに置いてある前提です）
cp ./mcp-template/.claude/mcp.json .claude/mcp.json

# 3. Claude Code の MCP を起動
#    `claude-code` コマンドは公式 CLI がインストールされている前提です
#    （インストール方法は https://claude.ai/docs/cli 参照）
claude-code mcp start --config .claude/mcp.json

# 起動後は、Claude が自然言語で以下のように指示できます
# 例）「東京の現在の気温を教えて」 → Claude が自動で weather‑api にリクエスト
```

### 3️⃣ `run-mcp.ps1`（Windows PowerShell 用）  
```powershell
# -------------------------------------------------
# Claude Code の MCP サーバーを起動するスクリプト（PowerShell）
# -------------------------------------------------
# 1. .claude ディレクトリが無ければ作成
New-Item -ItemType Directory -Force -Path .claude | Out-Null

# 2. テンプレートをコピー
Copy-Item -Path ".\mcp-template\.claude\mcp.json" -Destination ".claude\mcp.json" -Force

# 3. MCP を起動
#    `claude-code` CLI がインストールされていることが前提です
claude-code mcp start --config .claude\mcp.json

# 起動後は Claude に自然言語で質問できます
# 例）「東京の現在の気温は？」 と投げるだけで API が呼び出されます
```

> **※ 重要**  
> - `claude-code` CLI がインストールされていない場合は、公式サイトの手順に従ってインストールしてください。  
> - `mcp-template` フォルダはこのリポジトリ（または配布 ZIP）に同梱されています。  

## 使い方
1. **リポジトリをクローン** または ZIP を解凍し、プロジェクトのルートに配置します。  
2. **CLI をインストール**  
   ```bash
   npm i -g @anthropic/claude-code-cli   # 例：npm 経由でインストール
   # または公式サイトの手順に従う
   ```
3. **MCP を起動**  
   - macOS/Linux: `bash run-mcp.sh`  
   - Windows: `powershell -ExecutionPolicy Bypass -File run-mcp.ps1`
4. **Claude に質問**  
   Claude のチャット画面で「東京の現在の気温を教えて」など自然な日本語で指示すると、設定した `weather-api` が自動で呼び出され、結果が返ってきます。

## よくある質問

**Q1. `claude-code` コマンドが見つからないとエラーが出ます。**  
**A:** CLI がインストールされていないか、PATH に登録されていません。公式ページ（https://claude.ai/docs/cli）からインストールし、`claude-code --version` が正しく表示されることを確認してください。

---

**Q2. API キーが必要な外部サービスを使いたい場合はどうすればいいですか？**  
**A:** `servers[].headers` に `Authorization` ヘッダーを追加します。例）  
```json
"headers": {
  "Accept": "application/json",
  "Authorization": "Bearer YOUR_API_KEY"
}
```
※ キーは環境変数や `.env` ファイルで管理し、直接ファイルに書かないようにしてください。

---

**Q3. `defaultParams` 以外のクエリを動的に指定したいです。**  
**A:** Claude に「`weather-api` に `hour=14` を付けてリクエストして」などと指示すれば