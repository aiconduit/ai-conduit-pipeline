# Claude Code MCPでOAuth認証 - 実践テンプレート

## この動画で学んだこと
Claude Code の MCP（Model‑Control‑Panel）を使って、簡単に OAuth クライアントを作成し、リダイレクト URI を設定できることを学びました。  

## すぐに使えるテンプレート
以下の手順をそのままコピーしてターミナルに貼り付ければ、OAuth クライアントが作成されます。  
※ `example.com` はご自身のドメインに置き換えてください。

```bash
# 1️⃣ Claude Code の MCP で OAuth クライアント ID を取得
#    --model で使用するモデルを指定し、--oauth-client-id フラグでクライアントを生成します
claude --model claude-opus-4 --oauth-client-id

# 2️⃣ 取得したクライアント ID とシークレットを環境変数ファイルに保存
#    (※ ここでは .env.example を作成し、後で .env にリネームします)
cat <<EOF > .env.example
# -------------------------------------------------
# Claude Code MCP OAuth 設定
# -------------------------------------------------
CLAUDE_OAUTH_CLIENT_ID=YOUR_CLIENT_ID_HERE          # ← 1️⃣ の出力結果を貼り付け
CLAUDE_OAUTH_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE  # ← 1️⃣ の出力結果を貼り付け

# リダイレクト URI（動画と同じ例）
CLAUDE_OAUTH_REDIRECT_URI=https://example.com/callback
EOF

# 3️⃣ .env ファイルにリネームして、実際に使用する環境変数をロード
mv .env.example .env

# 4️⃣ (任意) Node.js / Python などで OAuth フローを実装する場合のサンプルコード
#    ここでは Node.js (express) の最小構成例を示します
cat <<'EOS' > oauth-server.js
/**
 * Claude Code MCP 用 OAuth 2.0 認証サーバー（サンプル実装）
 * ---------------------------------------------------------
 * 必要パッケージ: express, axios, dotenv
 *   $ npm install express axios dotenv
 *
 * このサーバーは以下を行います
 * 1. /login で Claude の認可エンドポイントへリダイレクト
 * 2. /callback で認可コードを受け取り、アクセストークンを取得
 */

require('dotenv').config();
const express = require('express');
const axios = require('axios');
const app = express();
const port = 3000;

// Claude の認可エンドポイント（公式ドキュメントで確認してください）
const AUTH_ENDPOINT = 'https://api.anthropic.com/oauth/authorize';
const TOKEN_ENDPOINT = 'https://api.anthropic.com/oauth/token';

app.get('/login', (req, res) => {
  const params = new URLSearchParams({
    response_type: 'code',
    client_id: process.env.CLAUDE_OAUTH_CLIENT_ID,
    redirect_uri: process.env.CLAUDE_OAUTH_REDIRECT_URI,
    scope: 'read write', // 必要に応じて調整
  });
  // ユーザーを Claude の認可画面へリダイレクト
  res.redirect(`${AUTH_ENDPOINT}?${params.toString()}`);
});

app.get('/callback', async (req, res) => {
  const { code } = req.query;
  if (!code) {
    return res.status(400).send('認可コードがありません');
  }

  try {
    // 認可コードをアクセストークンに交換
    const tokenResp = await axios.post(
      TOKEN_ENDPOINT,
      new URLSearchParams({
        grant_type: 'authorization_code',
        code,
        redirect_uri: process.env.CLAUDE_OAUTH_REDIRECT_URI,
        client_id: process.env.CLAUDE_OAUTH_CLIENT_ID,
        client_secret: process.env.CLAUDE_OAUTH_CLIENT_SECRET,
      }).toString(),
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    );

    const { access_token, refresh_token, expires_in } = tokenResp.data;
    // 取得したトークンを表示（実際のアプリではセッションや DB に保存してください）
    res.send(`
      <h2>認証成功 🎉</h2>
      <p>Access Token: <code>${access_token}</code></p>
      <p>Refresh Token: <code>${refresh_token}</code></p>
      <p>Expires In: ${expires_in} 秒</p>
    `);
  } catch (err) {
    console.error(err.response?.data || err);
    res.status(500).send('トークン取得に失敗しました');
  }
});

app.listen(port, () => {
  console.log(`OAuth デモサーバー起動 → http://localhost:${port}`);
});
EOS

# 5️⃣ サーバー起動（デモ用）
#    $ node oauth-server.js
#    ブラウザで http://localhost:3000/login にアクセスして認証フローを体験
```

## 使い方
1. **Claude Code の MCP で OAuth クライアントを作成**  
   `claude --model claude-opus-4 --oauth-client-id` を実行し、表示された `client_id` と `client_secret` をメモします。

2. **環境変数を設定**  
   上記テンプレートの `.env.example` に取得した情報を貼り付け、`.env` にリネームします。

3. **サンプルサーバーを起動**（Node.js がインストールされている前提）  
   ```bash
   npm install express axios dotenv   # 依存パッケージをインストール
   node oauth-server.js               # サーバー起動
   ```
   ブラウザで `http://localhost:3000/login` にアクセスし、Claude の認可画面が表示されたら許可をクリックします。

4. **アクセストークン取得**  
   認可が完了すると `/callback` が呼び出され、取得したアクセストークンが画面に表示されます。実際のアプリではこのトークンを API 呼び出しに利用してください。

## よくある質問

**Q: `claude` コマンドが