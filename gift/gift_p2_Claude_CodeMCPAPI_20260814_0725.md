# Claude Code の MCP で外部 API を自然言語呼び出し – 実践テンプレート

## この動画で学んだこと
Claude Code の **MCP (Model‑Controlled Programming)** 設定を `.claude/mcp.yaml` に追加するだけで、自然言語から外部 API をシームレスに呼び出せるようになります。  

## すぐに使えるテンプレート
以下のコマンドと設定ファイルをそのままコピー＆ペーストすれば、すぐに動作します。  

```bash
# 1️⃣ .claude ディレクトリと設定ファイルを作成
mkdir -p .claude && touch .claude/mcp.yaml

# 2️⃣ 基本設定 (タイムアウト等) を追記
cat <<'EOF' >> .claude/mcp.yaml
# -------------------------------------------------
# MCP 共通設定
# -------------------------------------------------
timeout: 30               # API 呼び出しのタイムアウト (秒)

# -------------------------------------------------
# 外部 API 定義例
# -------------------------------------------------
apis:
  # 任意の名前で API を定義
  weather_api:
    # エンドポイント URL（{{city}} などのプレースホルダーが使える）
    url: "https://api.openweathermap.org/data/2.5/weather?q={{city}}&appid={{api_key}}"
    method: GET            # HTTP メソッド
    headers:
      Accept: "application/json"
    # 必要に応じて認証情報やデフォルトパラメータを記述
    auth:
      type: query          # 認証方式 (query / header / bearer)
      key: "appid"
      value: "{{api_key}}"
    # 返却された JSON を Claude が扱いやすい形に変換したいときは
    # response_transform: |
    #   return {
    #     "temp": data.main.temp,
    #     "weather": data.weather[0].description
    #   }

  # もう一つの例: 翻訳 API
  translate_api:
    url: "https://api.example.com/translate"
    method: POST
    headers:
      Content-Type: "application/json"
      Authorization: "Bearer {{api_token}}"
    body: |
      {
        "text": "{{text}}",
        "target_lang": "{{target_lang}}"
      }
    response_transform: |
      return data.translated_text
EOF
```

> **ポイント**  
> - `{{...}}` は Claude が実行時に自動置換するプレースホルダーです。  
> - `response_transform` は任意です。返却 JSON を Claude が扱いやすい形に整形できます。  

## 使い方
1. **上記コードをターミナルに貼り付けて実行**  
   - `.claude/mcp.yaml` が作成され、サンプル API 定義が書き込まれます。  

2. **自分のプロジェクトに合わせて設定を編集**  
   - `apis:` 以下に自分が呼び出したい API を追加・修正。  
   - `{{city}}`、`{{api_key}}` などのプレースホルダーに実際の値を環境変数や Claude のプロンプトで渡します。  

3. **Claude Code で自然言語プロンプトを作成**  
   ```markdown
   # 例: 天気情報を取得したい
   Claude に対して:
   「{{city}} の天気を教えて」  
   ```
   - Claude が `weather_api` を認識し、`{{city}}` と `{{api_key}}` を埋めて API を呼び出します。  

4. **結果が自然言語で返ってくる**  
   - `response_transform` を設定していれば、温度や天気概要だけがシンプルに返ります。  

## よくある質問

**Q1: API キーやトークンはどこに書けばいいですか？**  
A: プレースホルダー `{{api_key}}` や `{{api_token}}` に実際の値を渡す方法は 2 通りあります。  
1. **環境変数** – ターミナルで `export OPENWEATHER_API_KEY=xxxx` など設定し、Claude のプロンプトで `{{api_key}}` と書くだけで自動展開されます。  
2. **プロンプト内で直接指定** – 「API キーは `xxxx` です」と指示すれば、Claude がその値を埋めます。  

---

**Q2: `response_transform` って何ですか？**  
A: API の生 JSON をそのまま返すと情報が多すぎて扱いにくいことがあります。`response_transform` では JavaScript‑like なコードで必要な部分だけを抽出し、Claude が返すテキストをシンプルにできます。記述は YAML の文字列ブロック (`|`) で行います。  

---

**Q3: タイムアウトが足りない場合はどうすれば？**  
A: `timeout` の数値を大きくすれば OK です。例: `timeout: 60`（秒）。  

---

**Q4: POST で送る JSON のフォーマットはどう書くの？**  
A: `body:` に YAML のマルチライン文字列 (`|`) で JSON を記述します。プレースホルダーは同様に `{{...}}` で埋められます。  

---

**Q5: 設定ファイルを削除したらどうなる？**  
A: `.claude/mcp.yaml` が無い状態では MCP の拡張機能は無効化され、Claude は普通のコード生成だけを行います。再度作成すればすぐに復活します。  

---

**Q6: 複数の API を同時に呼び出すことは可能ですか？**  
A