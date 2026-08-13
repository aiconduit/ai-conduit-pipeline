# Claude Code MCPでAPIを自然言語呼び出し - 実践テンプレート

## この動画で学んだこと
Claude Code の **MCP (Multi‑Call Prompt)** 機能を使えば、あらかじめ設定した API エンドポイントを自然言語の質問だけで呼び出すことができます。  

## すぐに使えるテンプレート
以下のファイル・コマンドをそのままコピーして、環境に貼り付けるだけで動作します。

### 1️⃣ `.claude/mcp/config.json`
```json
{
  // -------------------------------------------------
  // ここに呼び出したい API のエイリアスとエンドポイントを記述します
  // 例: 天気情報 API
  // -------------------------------------------------
  "weather": "https://api.weather.com/v3/wx/conditions/current?apiKey=YOUR_API_KEY&format=json",

  // 追加したい API があれば、同様にキーと URL をペアで書いてください
  // "stock": "https://api.example.com/stock?symbol={symbol}&apikey=YOUR_KEY"
}
```

> **⚠️ 注意**  
> - `YOUR_API_KEY` はご自身の API キーに置き換えてください。  
> - 必要に応じてクエリパラメータ（例: `location=東京`）は **Claude Code が自動で付与** しますので、URL には固定部分だけを書きます。

### 2️⃣ 実行コマンド例
```bash
# 天気情報を自然言語で取得
claude --mcp weather "東京の天気"

# 例: 株価情報（上記 config に stock エイリアスを追加した場合）
# claude --mcp stock "AAPL の現在株価"
```

### 3️⃣ 補助シェルスクリプト（任意）
```bash
#!/usr/bin/env bash
# -------------------------------------------------
# Claude Code MCP 用テンプレートスクリプト
# -------------------------------------------------
set -euo pipefail

# 1. config が存在しない場合は作成（初回実行用）
CONFIG_DIR="${HOME}/.claude/mcp"
CONFIG_FILE="${CONFIG_DIR}/config.json"

if [[ ! -d "${CONFIG_DIR}" ]]; then
  echo "Creating config directory at ${CONFIG_DIR}"
  mkdir -p "${CONFIG_DIR}"
fi

if [[ ! -f "${CONFIG_FILE}" ]]; then
  cat > "${CONFIG_FILE}" <<'EOF'
{
  "weather": "https://api.weather.com/v3/wx/conditions/current?apiKey=YOUR_API_KEY&format=json"
}
EOF
  echo "Default config created at ${CONFIG_FILE}"
fi

# 2. 引数チェック
if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <alias> <natural language query>"
  exit 1
fi

ALIAS=$1
shift
NL_QUERY="$*"

# 3. Claude Code を呼び出す
claude --mcp "${ALIAS}" "${NL_QUERY}"
```
> 上記スクリプトは `chmod +x mcp.sh` で実行権限を付与し、`./mcp.sh weather "大阪の天気"` のように使えます。

---

## 使い方
1. **API キーを取得**  
   - 例: `https://weather.com` の開発者ポータルで API キーを取得し、`config.json` の `YOUR_API_KEY` 部分に貼り付けます。

2. **設定ファイルを配置**  
   - 上記の `.claude/mcp/config.json` を自分のホームディレクトリ以下の `~/.claude/mcp/` に保存します。  
   - 既に `~/.claude/mcp/` ディレクトリがある場合は、既存の `config.json` に追記しても構いません。

3. **Claude Code をインストール**（未インストールの場合）  
   ```bash
   # 例: Homebrew でインストール
   brew install anthropic/claude/claude
   ```

4. **MCP コマンドを実行**  
   ```bash
   claude --mcp weather "東京の天気"
   ```
   - Claude Code が `weather` エイリアスに紐付いた URL にリクエストし、返ってきた JSON を自然言語に変換して表示します。

5. **追加の API を使いたいとき**  
   - `config.json` に新しいキーと URL を追記し、同様に `claude --mcp <alias> "<自然言語クエリ>"` で呼び出します。

---

## よくある質問

**Q1: API キーが漏洩したらどうすればいいですか？**  
**A:** すぐに該当サービスの管理画面からキーを再生成し、`config.json` を更新してください。キーは平文で保存されるため、公開リポジトリや共有ディレクトリに置かないよう注意しましょう。

---

**Q2: `claude --mcp` がエラーになるのはなぜですか？**  
**A:** 主な原因は次の通りです。  
| 原因 | 対策 |
|------|------|
| `config.json` のパスが間違っている | `~/.claude/mcp/config.json` に正しく配置されているか確認 |
| URL に `{}` などのプレースホルダーが残っている | プレースホルダーは不要です。Claude がクエリから自動で埋めます |
| API キーが無効または期限切れ | 正しいキーに差し替える |
| ネットワークが遮断されている | プロキシ設定やファイアウォールを確認 |

---

**Q3: 複数のパラメータ（例: 都市名と日時）を同時に渡したい**  
**A:** 現在の MCP は自然言語から必要情報を抽出して URL に組み込みます。  
例: `claude --mcp weather "2024年9月15日の東京の天気"` と入力すれば、Claude が日付と都市を解析し、適切