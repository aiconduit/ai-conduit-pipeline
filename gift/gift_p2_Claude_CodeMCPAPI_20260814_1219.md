# Claude Code の MCP で API 連携が自動になる実践テンプレート

## この動画で学んだこと
Claude Code の **MCP（Model‑Control‑Package）** 設定ファイルに外部 API を記述すれば、コード内で `fetch` や `axios` を書かずに API 呼び出しが自動化されます。  

## すぐに使えるテンプレート
以下のファイルをプロジェクトのルートに **そのままコピー** してください。  
※ファイル名は必ず **`.mcp.json`** にしてください。

```json
{
  // -------------------------------------------------
  // 1️⃣ MCP の基本情報
  // -------------------------------------------------
  "name": "my-project-mcp",
  "version": "1.0.0",
  "description": "Claude Code 用の API 連携テンプレート",

  // -------------------------------------------------
  // 2️⃣ 外部 API 定義
  // -------------------------------------------------
  "apis": {
    // 任意のキー名で API を定義
    "myExternalApi": {
      // API のベース URL
      "baseUrl": "https://api.example.com/v1",

      // デフォルトのヘッダー（認証情報など）
      "defaultHeaders": {
        // Bearer トークン認証例
        "Authorization": "Bearer YOUR_ACCESS_TOKEN",

        // JSON 送受信を前提とした場合
        "Content-Type": "application/json",
        "Accept": "application/json"
      },

      // タイムアウト（ミリ秒）※省略可
      "timeout": 5000,

      // エラーハンドリングのデフォルト設定
      "errorHandling": {
        "retry": 2,               // リトライ回数
        "retryDelayMs": 1000      // リトライ間隔
      }
    }
  },

  // -------------------------------------------------
  // 3️⃣ エンドポイント別設定（オプション）
  // -------------------------------------------------
  "endpoints": {
    // エンドポイント名は自由に付けられます
    "getUser": {
      "api": "myExternalApi",          // どの API を使うか
      "method": "GET",
      "path": "/users/{userId}",       // {userId} は実行時に置換されます
      "query": {                       // クエリパラメータ例
        "include": "profile,settings"
      }
    },

    "createPost": {
      "api": "myExternalApi",
      "method": "POST",
      "path": "/posts",
      "body": {
        // ここに POST で送る JSON のテンプレートを書きます
        "title": "{{title}}",
        "content": "{{content}}",
        "tags": "{{tags}}"
      }
    }
  }
}
```

> **ポイント**  
> - `YOUR_ACCESS_TOKEN` は実際に取得したトークンに置き換えてください。  
> - `{userId}` のようなプレースホルダーは、Claude Code のプロンプトで `{{userId}}` と記述すると自動置換されます。  
> - `{{title}}` などの変数は、Claude Code のコード生成時に **変数名** を指定すれば自動で埋め込まれます。

## 使い方
1. **ファイルを配置**  
   プロジェクトのルートに `.mcp.json` を保存します。

2. **Claude Code にプロジェクトを認識させる**  
   ```bash
   claude-code init   # 初回だけ実行（MCP が自動で読み込まれます）
   ```

3. **コード生成時に API を呼び出す**  
   Claude Code のプロンプトで以下のように指示します。  

   ```markdown
   # 例: ユーザー情報取得
   {{getUser userId="12345"}}
   ```

   すると、Claude Code が自動で `GET https://api.example.com/v1/users/12345?...` を実行し、結果をコードブロックに埋め込みます。

4. **POST リクエストの例**  
   ```markdown
   # 例: 記事作成
   {{createPost title="My first post" content="Hello World!" tags="['tech','ai']"}}
   ```

   これだけで `POST https://api.example.com/v1/posts` が送信され、作成された記事の ID などが返ります。

5. **カスタマイズ**  
   - 新しいエンドポイントを追加したいときは `endpoints` 配下に追記。  
   - 認証方式が Basic 認証や API キーの場合は `defaultHeaders` を適宜変更してください。

## よくある質問

**Q1. トークンが期限切れになったらどうすればいいですか？**  
**A:** `.mcp.json` の `defaultHeaders.Authorization` を新しいトークンに書き換えるだけです。自動リロードは `claude-code reload` で行えます。

---

**Q2. エラー時にリトライしたくない場合は？**  
**A:** `errorHandling.retry` を `0` に設定すればリトライは行われません。

---

**Q3. 複数の API を同時に使いたいときは？**  
**A:** `apis` に別名で API を追加し、`endpoints` の `api` フィールドで対象の API を指定します。例: `"api": "anotherApi"`。

---

**Q4. ローカルでテストしたいが実際の API は呼びたくない**  
**A:** `baseUrl` を `http://localhost:3000/mock` などのモックサーバーに変更すれば、同じエンドポイント定義でテストが可能です。

---

**Q5. `.mcp.json` の書式エラーが出たら？**  
**A:** JSON の構文エラーが多いので、VS Code の「JSON Validator」拡張や `jq` コマンドで検証すると早く見つかります。  

```bash