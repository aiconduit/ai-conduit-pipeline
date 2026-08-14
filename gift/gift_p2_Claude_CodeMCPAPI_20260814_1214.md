# Claude Code の MCP で API 連携が自動になった – 実践テンプレート

## この動画で学んだこと
Claude Code の **MCP（Model Configuration Package）** を使うだけで、外部 API のエンドポイントや認証情報を JSON で定義し、コードを書かずに自動で呼び出すことができます。

---

## すぐに使えるテンプレート

### 1️⃣ `.mcp.json`（MCP 設定ファイル）

```json
{
  // -------------------------------------------------
  // ① API サーバー定義
  // -------------------------------------------------
  "apiServers": {
    "myExternalApi": {
      // API のベース URL（例: https://api.example.com/v1）
      "baseUrl": "https://api.example.com/v1",

      // -------------------------------------------------
      // ② 認証情報（必要に応じて）
      // -------------------------------------------------
      // ここでは Bearer Token を使用する例です。
      // 環境変数から安全に取得することを推奨します。
      "auth": {
        "type": "bearer",
        "token": "${MY_API_BEARER_TOKEN}"
      },

      // -------------------------------------------------
      // ③ エンドポイント定義
      // -------------------------------------------------
      "endpoints": {
        // GET /users/{userId}
        "getUser": {
          "method": "GET",
          "path": "/users/{userId}",
          "description": "ユーザー情報を取得"
        },

        // POST /orders
        "createOrder": {
          "method": "POST",
          "path": "/orders",
          "description": "新規注文を作成",
          "requestBody": {
            // JSON スキーマの例（省略可）
            "type": "object",
            "properties": {
              "productId": { "type": "string" },
              "quantity":  { "type": "integer" }
            },
            "required": ["productId", "quantity"]
          }
        }
      }
    }
  },

  // -------------------------------------------------
  // ④ グローバル設定（任意）
  // -------------------------------------------------
  "settings": {
    // タイムアウト（ミリ秒）
    "timeout": 15000,
    // 失敗時のリトライ回数
    "retry": 2
  }
}
```

> **ポイント**  
> * `baseUrl` は API のベース URL を記述。  
> * 認証情報は環境変数 `${MY_API_BEARER_TOKEN}` で管理すると安全です。  
> * `endpoints` ではメソッド、パス、簡単な説明を記載。必要なら `requestBody` のスキーマも入れられます。

---

### 2️⃣ 環境変数の設定（例：Linux/macOS）

```bash
# .bashrc / .zshrc などに追記
export MY_API_BEARER_TOKEN="YOUR_BEARER_TOKEN_HERE"
```

> **Tip**: トークンは GitHub Secrets や `.env` ファイルで管理し、`source .env` で読み込むと便利です。

---

### 3️⃣ Claude Code での呼び出し例（プロンプト）

```markdown
以下の設定ファイル `.mcp.json` を読み込んで、`myExternalApi` の `getUser` エンドポイントを呼び出してください。  
ユーザー ID は `12345` です。結果は JSON で返してください。
```

Claude Code が自動で以下のような HTTP リクエストを生成し、実行します（内部で `curl` などを使用）。

```bash
curl -X GET "https://api.example.com/v1/users/12345" \
     -H "Authorization: Bearer $MY_API_BEARER_TOKEN" \
     -H "Accept: application/json"
```

---

## 使い方

1. **プロジェクトのルートに `.mcp.json` を作成**  
   上記テンプレートをコピーして、`myExternalApi` の `baseUrl` や認証情報を自分の環境に合わせて編集。

2. **認証情報を環境変数に設定**  
   ```bash
   export MY_API_BEARER_TOKEN="実際のトークン"
   ```

3. **Claude Code にプロンプトを投げる**  
   *「`myExternalApi` の `createOrder` エンドポイントで、productId が `abc123`、quantity が `2` の注文を作成してください」* など、自然言語で指示。

4. **結果を確認**  
   Claude Code が返す JSON をそのまま利用可能。エラーが出た場合は `.mcp.json` の `settings.timeout` や `retry` を調整。

5. **必要に応じてエンドポイントを追加**  
   新しい API が増えたら `endpoints` に項目を足すだけで、再デプロイ不要で即利用可能。

---

## よくある質問

**Q1: 認証方式が Basic 認証や API Key の場合はどう書けばいいですか？**  
**A:** `auth` オブジェクトを以下のように変更します。

```json
// Basic 認証
"auth": {
  "type": "basic",
  "username": "${API_USER}",
  "password": "${API_PASS}"
}

// API Key（ヘッダーに付与）
"auth": {
  "type": "header",
  "headerName": "X-API-KEY",
  "value": "${API_KEY}"
}
```

---

**Q2: POST のリクエストボディを動的に変えたいです。**  
**A:** プロンプト内で「`createOrder` エンドポイントに以下の JSON を送って」などと指示すれば、Claude Code が自動で `curl -d` 部分を生成します。例:

```markdown
productId が "xyz789"、quantity が 5 の注文を作成してください。
```

---

**Q3: エラーが返ってきたときのデバッグ方法は？**  
**A:**  
1. `.mcp.json` の `settings.debug` を `true` にすると、Claude Code が実行した cURL コマンドとレスポンスヘ