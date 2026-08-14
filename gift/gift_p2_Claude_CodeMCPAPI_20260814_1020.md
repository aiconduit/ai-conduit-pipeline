# Claude CodeのMCPで外部API連携が自然言語で完結した – 実践テンプレート

## この動画で学んだこと
Claude Code の **MCP (Multi‑Channel Proxy)** を使えば、`.claude/mcp.json` に API 定義を書くだけで、自然言語のプロンプトだけで外部 REST API とやり取りできるようになります。

---

## すぐに使えるテンプレート

### 1️⃣ ディレクトリと設定ファイルの作成
```bash
# プロジェクトのルートに .claude ディレクトリを作成
mkdir -p .claude

# 空の mcp.json を作成（以下の内容で上書きしてください）
cat > .claude/mcp.json <<'EOF'
{
  // -------------------------------------------------
  // MCP サーバー定義
  // -------------------------------------------------
  "servers": [
    {
      // サーバー名（任意の識別子）
      "name": "weather-api",
      // タイプは必ず "rest"
      "type": "rest",
      // ベース URL（実際に呼び出したい API のエンドポイント）
      "baseUrl": "https://api.open-meteo.com/v1/forecast",
      // 必要に応じてデフォルトヘッダーを設定
      "defaultHeaders": {
        "Accept": "application/json"
      },
      // エンドポイントごとの設定（GET/POST など）
      "endpoints": [
        {
          // エンドポイントの識別子（プロンプトで呼び出すときに使う）
          "name": "weather",
          // HTTP メソッド
          "method": "GET",
          // パス（baseUrl の後に付く部分）
          "path": "?latitude={lat}&longitude={lon}&hourly=temperature_2m",
          // パラメータ置換用のテンプレート
          // 例: {lat}=35.6895, {lon}=139.6917
          "queryParams": {
            "latitude": "{lat}",
            "longitude": "{lon}",
            "hourly": "temperature_2m"
          },
          // 必要ならレスポンスの変換ルールも書けます（省略可）
          "responseTransform": null
        }
      ]
    },

    // -------------------------------------------------
    // ここに別の API を追加できる例
    // -------------------------------------------------
    {
      "name": "joke-api",
      "type": "rest",
      "baseUrl": "https://official-joke-api.appspot.com",
      "endpoints": [
        {
          "name": "random-joke",
          "method": "GET",
          "path": "/random_joke",
          "queryParams": {}
        }
      ]
    }
  ]
}
EOF
```

### 2️⃣ Claude Code で MCP を有効化して実行
```bash
# 例: プロンプトを直接渡す（CLI がインストール済みの場合）
claude code --mcp .claude/mcp.json "東京の現在の気温を教えて"

# 例: インタラクティブモードで対話しながら利用
claude code --mcp .claude/mcp.json
```

> **ポイント**  
> - `--mcp` オプションで設定ファイルのパスを指定します。  
> - プロンプト内で `weather-api.weather` のようにサーバー名とエンドポイント名を組み合わせて呼び出すことができます（内部的に Claude が自動変換します）。

### 3️⃣ 実際に動くサンプルプロンプト例
```
weather-api.weather lat=35.6895 lon=139.6917 の現在の気温を教えて
```
> 上記のプロンプトを Claude Code に投げると、`weather-api` の `weather` エンドポイントが呼び出され、東京（緯度 35.6895、経度 139.6917）の 2 時間ごとの気温データが返ります。

---

## 使い方

1. **.claude ディレクトリを作成**  
   `mkdir -p .claude` でプロジェクト直下に隠しディレクトリを作ります。

2. **mcp.json に API 定義を書き込む**  
   上記テンプレートをコピーし、`baseUrl` や `path`、`queryParams` を自分が使いたい API に合わせて編集します。

3. **Claude Code に MCP 設定を渡す**  
   `claude code --mcp .claude/mcp.json "プロンプト"` の形で実行。  
   - **対話モード**: `claude code --mcp .claude/mcp.json` とだけ入力すると、対話的にプロンプトを入力できます。

4. **プロンプトで API を呼び出す**  
   `サーバー名.エンドポイント名 パラメータ=値 ...` の形で自然言語に混ぜて指示します。Claude が自動で HTTP リクエストを組み立て、結果を返します。

5. **追加の API が必要になったら**  
   `servers` 配列に新しいオブジェクトを追記すれば OK。設定ファイルを保存すればすぐに利用可能です。

---

## よくある質問

**Q1. `claude code` コマンドが見つからないんですが…**  
**A:** Claude Code の CLI は公式サイト（https://claude.ai/cli）からインストールできます。