# Claude Code の MCP で外部 API を自然言語呼び出し - 実践テンプレート

## この動画で学んだこと
Claude Code の **MCP (Model‑Centric Programming)** を利用すれば、`.claude/mcp.yaml` に設定を書くだけで、自然言語から外部 API をシームレスに呼び出すことができます。  

## すぐに使えるテンプレート
以下のファイル構成・設定・コマンドをそのままコピーしてプロジェクトのルートに貼り付けてください。

```bash
# 1️⃣ .claude ディレクトリと設定ファイルを作成
mkdir -p .claude && touch .claude/mcp.yaml

# 2️⃣ 基本設定を追記（タイムアウトは 30 秒に設定）
cat <<'EOF' >> .claude/mcp.yaml
# -------------------------------------------------
# Claude Code MCP 設定ファイル
# -------------------------------------------------
# タイムアウト: API 呼び出しがこの秒数を超えるとエラーになります
timeout: 30

# デフォルトの HTTP ヘッダー（必要に応じて追加・上書きしてください）
default_headers:
  Content-Type: application/json
  Accept: application/json

# 外部 API のエンドポイント定義
# key: 任意の名前（例: weather_api）
# url: 実際に呼び出す URL（{param} でプレースホルダーを使用可能）
# method: GET / POST / PUT / DELETE など
# auth: 認証情報（Bearer トークン等）※環境変数で管理することを推奨
apis:
  weather_api:
    url: https://api.openweathermap.org/data/2.5/weather?q={city}&appid=${OPENWEATHER_API_KEY}
    method: GET
    # auth: Bearer ${OPENWEATHER_API_KEY}   # 例: Bearer トークン方式の場合
    # 追加ヘッダーが必要なときは下記を有効化
    # headers:
    #   X-Custom-Header: your-value

# 変数置換のルール（必要に応じて拡張可能）
variables:
  city: "Tokyo"   # デフォルトの都市名。CLI から上書き可能

# -------------------------------------------------
# ここまでが設定ファイルです。保存して完了です。
# -------------------------------------------------
EOF
```

### 例: `weather_api` を自然言語で呼び出すコード（Python 例）

```python
# -*- coding: utf-8 -*-
"""
Claude Code の MCP 設定を利用して、自然言語から外部 API を呼び出すサンプルです。
※実行には `anthropic` パッケージと `dotenv` が必要です。
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # .env から環境変数をロード（例: OPENWEATHER_API_KEY）

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# MCP 設定ファイルのパス
mcp_path = ".claude/mcp.yaml"

# 自然言語プロンプト
prompt = """
以下の指示に従って、天気情報を取得してください。
- 都市は「{city}」です。
- 取得した JSON をそのまま返してください。
"""

# MCP を有効化したリクエスト
response = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1024,
    temperature=0,
    system=f"Use the MCP configuration at {mcp_path} to resolve external API calls.",
    messages=[{"role": "user", "content": prompt.format(city="Osaka")}],
)

print("Claude の返答:")
print(response.content[0].text)
```

> **ポイント**  
> - `client.messages.create` の `system` メッセージで MCP 設定ファイルのパスを指示すると、Claude が自動で `weather_api` を解決し、実際の HTTP GET を実行します。  
> - `variables.city` はプロンプト内で `{city}` と書くだけで置換されます。  

## 使い方
1. **環境変数を設定**  
   ```bash
   # .env ファイルを作成（例）
   echo "ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx" >> .env
   echo "OPENWEATHER_API_KEY=your_openweather_key" >> .env
   ```
2. **テンプレートをプロジェクトに貼り付け**  
   上記の **「すぐに使えるテンプレート」** のコマンドを実行し、`.claude/mcp.yaml` を作成します。
3. **コードを実行**  
   ```bash
   pip install anthropic python-dotenv
   python your_script.py   # 例: 上記 Python サンプル
   ```
4. **プロンプトを変更**  
   `prompt` の内容や `variables.city` を変えるだけで、別の API エンドポイントやパラメータにも簡単に対応できます。

## よくある質問

**Q1: `timeout` の単位は何ですか？**  
A: 秒です。デフォルトは 30 秒ですが、長時間かかる API では適宜増やしてください。

**Q2: 認証情報はどこに書けばいいですか？**  
A: 環境変数（例: `${OPENWEATHER_API_KEY}`）で管理し、`apis.<name>.auth` に `Bearer ${VAR_NAME}` の形で記述すると安全です。直接キーを書かないようにしましょう。

**Q3: POST や PUT でリクエストボディを送るには？**  
A: `apis.<name>.body` フィールドを追加し、JSON 文字列またはテンプレート変数を記述します。例:
```yaml
body: |
  {
    "title": "{title}",
    "content": "{content}"
  }
```

**Q4: 複数の API を同時に呼び出したい場合は？**  
A: プロンプト内で