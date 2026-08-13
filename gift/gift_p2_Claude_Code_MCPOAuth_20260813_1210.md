# Claude Code MCPでOAuth認証 - 実践テンプレート

## この動画で学んだこと
この動画では、Claude CodeのMCPでOAuthクライアントを設定する方法を学びました。OAuth認証を実現するために、必要な手順と設定を紹介します。

## すぐに使えるテンプレート
```bash
# Claude CodeのMCPでOAuthクライアントを設定する
$ claude --model claude-opus-4 --oauth-client-id

# redirect URIを設定する
redirect URI: https://example.com/callback
```

## 使い方
1. ターミナルで `$ claude --model claude-opus-4 --oauth-client-id` を実行して、OAuthクライアントを設定します。
2. redirect URIを `https://example.com/callback` に設定します。

## よくある質問
Q: OAuthクライアントを設定する際に、どのような注意点がありますか？
A: OAuthクライアントを設定する際には、クライアントIDとシークレットを安全に保管する必要があります。また、redirect URIを正しく設定する必要があります。

---
AI Conduit: https://www.youtube.com/@AI.Conduit