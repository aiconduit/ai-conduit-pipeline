# Claude Code で美しいデータ可視化！JSON設定＆Pythonスクリプト実践テンプレート

## この動画で学んだこと
このYouTube Shorts動画では、Claude Codeのインフォグラフィック機能、特にData Viz Rendererを活用することで、データ可視化プロセスを劇的に効率化できることを学びました。JSON設定ファイルを用意し、簡単なスクリプトを実行するだけで、複雑なデータも美しく、そして自動的に可視化される強力な機能です。

## すぐに使えるテンプレート

### 1. データ可視化設定ファイル (`data_viz_config.json`)

これは、可視化したいデータの構造や種類、グラフの要望をClaudeに伝えるためのJSONファイルです。

{
  "title": "地域別月間売上高",
  "type": "bar_chart",
  "data": [
    {"region": "北海道", "sales": 350000},
    {"region": "関東", "sales": 820000},
    {"region": "関西", "sales": 610000},
    {"region": "九州", "sales": 480000}
  ],
  "x_axis": {"field": "region", "label": "地域"},
  "y_axis": {"field": "sales", "label": "売上高 (JPY)"},
  "description": "各地域における月間売上高を比較する棒グラフを生成してください。可能であれば、可視化に直接使えるHTML/JavaScriptコード（Vega-Lite、Plotlyなど）も提供し、コードの前にグラフの主要な洞察を日本語で説明してください。",
  "format_hint": "HTMLファイルとして出力し、ブラウザで表示できるようにしてください。"
}
### 2. 可視化生成スクリプト (`generate_viz.py`)

上記のJSON設定ファイルを読み込み、Anthropic Claude APIにリクエストを送信して可視化を生成するPythonスクリプトです。

import os
import json
import anthropic

# ⚠ 注意: 環境変数 'ANTHROPIC_API_KEY' にAPIキーを設定してください。
# 例: export ANTHROPIC_API_KEY="YOUR_API_KEY_HERE"
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError(
        "ANTHROPIC_API_KEY環境変数が設定されていません。"
        "APIキーを環境変数に設定してからスクリプトを実行してください。"
    )

# Anthropic APIクライアントの初期化
# Claude 3 Opusは高性能ですが、SonnetやHaikuも利用可能です。
# 必要に応じて 'model' パラメータを変更してください。
client = anthropic.Anthropic(api_key=api_key)
LLM_MODEL = "claude-3-opus-20240229" # claude-3-sonnet-20240229 や claude-3-haiku-20240307 も選択可能

# 可視化設定ファイル名
CONFIG_FILE = "data_viz_config.json"
# 出力ファイル名 (Claudeからの応答を保存する場合)
OUTPUT_FILE = "visualization_output.html"

def generate_data_visualization():
    """
    JSON設定ファイルに基づいてClaude Codeにデータ可視化を依頼し、結果を表示または保存します。
    """
    try:
        # 設定ファイルを読み込む
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"--- '{CONFIG_FILE}' を読み込みました ---")
        print(json.dumps(config, indent=2, ensure_ascii=False))
        print("--------------------------------------")

    except FileNotFoundError:
        print(f"エラー: 設定ファイル '{CONFIG_FILE}' が見つかりません。")
        print("`data_viz_config.json` がスクリプトと同じディレクトリにあるか確認してください。")
        return
    except json.JSONDecodeError:
        print(f"エラー: 設定ファイル '{CONFIG_FILE}' のJSON形式が不正です。")
        print("JSON構文が正しいか確認してください。")
        return

    # Claudeへのシステムプロンプト (役割と指示)
    system_prompt = """
    あなたは熟練したデータアナリストであり、データ可視化の専門家です。
    提供されたJSON設定に基づき、最も適切で分かりやすいデータ可視化を提案・生成してください。
    特に、可視化の目的、データの種類、最適なグラフ形式を考慮してください。
    可能な限り、ブラウザで直接表示できるHTML/JavaScriptコード（例: Vega-Lite、Plotly、D3.js）を提供してください。
    可視化コードの前に、グラフの目的、主要な洞察、そしてコードの使用方法を日本語で簡潔に説明してください。
    コードは完全なHTMLファイルとして記述し、スタイルやスクリプトはHTML内に含めてください。
    """

    # Claudeへのユーザープロンプト (具体的なリクエスト)
    user_prompt = f"""
    以下のJSON設定ファイルの内容に基づいて、データ可視化を生成してください。
    '{config.get("description", "データ可視化")}'という指示に従い、'{config.get("format_hint", "HTML/JavaScriptコード")}'形式で出力してください。

    {json.dumps(config, indent=2, ensure_ascii=False)}
    """

    print(f"\n--- Claude ({LLM_MODEL}) にデータ可視化をリクエスト中... ---")
    try:
        # Claude APIを呼び出す
        message = client.messages.create(
            model=LLM_MODEL,
            max_tokens=4000, # 応答が長くなる可能性があるので、max_tokensを増やす
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        response_content = message.content[0].text
        print("\n--- Claudeからの応答 ---")
        print(response_content)
        print("-------------------------")

        # 応答をファイルに保存
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(response_content)
        print(f"\nClaudeからの応答を '{OUTPUT_FILE}' に保存しました。")
        print(f"ブラウザで '{OUTPUT_FILE}' を開いて可視化を確認できます。")

    except anthropic.APIStatusError as e:
        print(f"APIエラーが発生しました: ステータスコード {e.status_code} - 応答: {e.response}")
        print("APIキーが正しいか、Claudeの利用制限に達していないか確認してください。")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")

if __name__ == '__main__':
    generate_data_visualization()
## 使い方

1.  **Anthropic APIキーの取得と設定**:
    *   Anthropicの公式サイト (https://console.anthropic.com/ ) にアクセスし、アカウントを作成またはログインします。
    *   APIキーを生成し、これを環境変数 `ANTHROPIC_API_KEY` に設定します。
        *   Linux/macOSの場合: `export ANTHROPIC_API_KEY="YOUR_API_KEY_HERE"`
        *   Windows (PowerShell) の場合: `$env:ANTHROPIC_API_KEY="YOUR_API_KEY_HERE"`
        *   Windows (cmd) の場合: `set ANTHROPIC_API_KEY="YOUR_API_KEY_HERE"`
        (この設定はターミナルセッション中のみ有効です。永続化するには、それぞれのOSの環境変数設定方法に従ってください。)

2.  **Python環境の準備**:
    *   Python 3.8以上がインストールされていることを確認してください。
    *   必要なライブラリ `anthropic` をインストールします。
        pip install anthropic
        3.  **テンプレートファイルの保存**:
    *   上記の「データ可視化設定ファイル」の内容を `data_viz_config.json` という名前で保存します。
    *   上記の「可視化生成スクリプト」の内容を `generate_viz.py` という名前で保存します。
    *   これら2つのファイルを**同じディレクトリ**に置いてください。

4.  **`data_viz_config.json` の編集**:
    *   あなたの可視化したいデータや、グラフの種類、軸のラベルなどを自由に編集してください。
    *   `description` フィールドには、Claudeにどのようなグラフを生成してほしいか、より具体的な指示を日本語で記述できます。
    *   `format_hint` には、コードの形式（例: `HTMLファイルとして出力し、ブラウザで表示できるようにしてください。`）を指示できます。

5.  **スクリプトの実行**:
    *   ターミナルを開き、`generate_viz.py` があるディレクトリに移動します。
    *   以下のコマンドを実行します。
        python generate_viz.py
        6.  **結果の確認**:
    *   スクリプトが正常に実行されると、Claudeからの応答がターミナルに表示され、`visualization_output.html` というファイルに保存されます。
    *   この `visualization_output.html` ファイルをウェブブラウザで開くと、Claudeが生成したデータ可視化を確認できます。

## よくある質問

**Q: Claude APIキーはどこで取得できますか？**
A: Anthropicの公式ウェブサイト（https://console.anthropic.com/ ）でアカウントを登録し、プロジェクト設定からAPIキーを生成できます。利用にはクレジット決済情報が必要となる場合があります。

**Q: どのような種類のグラフを生成できますか？**
A: Claude 3モデルは非常に柔軟で、棒グラフ、折れ線グラフ、円グラフ、散布図、ヒートマップなど、多岐にわたる一般的なグラフ形式に対応できます。プロンプト（`data_viz_config.json` の `description` フィールドなど）で具体的に指示することで、より望ましい結果が得られます。

**Q: 生成された可視化コード（HTML/JavaScript）はどうやって使えばいいですか？**
A: スクリプトが生成した `visualization_output.html` ファイルは、そのままウェブブラウザで開くことができます。ブラウザはHTML、CSS、JavaScriptを解釈してグラフを表示します。必要であれば、そのHTMLコードを自身のウェブサイトやダッシュボードに組み込むことも可能です。

**Q: 別のデータソース（CSVファイル、データベースなど）を使うにはどうすればいいですか？**
A: `data_viz_config.json` の `data` フィールドに直接データを記述する代わりに、`generate_viz.py` スクリプト内でCSVファイルを読み込んだり、データベースからデータを取得したりする処理を追加し、そのデータをJSONの `data` フィールドに動的に挿入するように変更することで対応できます。

---
AI Conduit: https://www.youtube.com/@AI.Conduit