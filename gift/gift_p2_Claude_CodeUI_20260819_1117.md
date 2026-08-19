はい、承知いたしました。優秀なエンジニアとして、YouTube Shorts動画の内容に基づき、視聴者がすぐに利用できるClaude CodeのUIデザイナー実践テンプレートを作成します。

---

# Claude Code UIデザイナー - 実践テンプレート

## この動画で学んだこと
この動画では、Anthropic ClaudeのUIデザイナー機能を活用することで、参照画像や製品概要ファイルからデザインシステムを構成するUIコンポーネント、スタイルガイド、そして具体的なWebページのコードまで自動生成できることを学びました。これにより、UIデザインの初期フェーズを効率化し、開発を加速させることが可能です。

## すぐに使えるテンプレート

このテンプレートでは、PythonスクリプトとAnthropic Claude APIを利用して、参照画像と製品概要からUIデザインの提案とHTML/CSS/JSコードを生成します。

### 1. 必要なファイルの準備

以下の3つのファイルを準備してください。

*   `generate_design_system.py`: メインのPythonスクリプト
*   `product_overview.txt`: 製品の概要を記述するテキストファイル
*   `images/`フォルダ: 参照となるUIデザインやロゴの画像を格納するフォルダ

---

**`generate_design_system.py`**
import os
import argparse
import base64
from pathlib import Path
from anthropic import Anthropic

# --- 設定 ---
# Claude APIキーは環境変数 ANTHROPIC_API_KEY に設定してください。
# 例: export ANTHROPIC_API_KEY="sk-..."
ANTHROPIC_MODEL = "claude-3-sonnet-20240229" # 推奨モデル。opusはより高性能ですが、コストが高めです。
OUTPUT_FILENAME = "generated_design_system.html"

def encode_image_to_base64(image_path):
    """画像をBase64形式にエンコードします。"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        print(f"画像をエンコードできませんでした: {image_path} - {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Claude Code UI Designer for generating design systems.")
    parser.add_argument("--product_overview", type=str, required=True,
                        help="製品概要が記述されたテキストファイルのパス")
    parser.add_argument("--image_folder", type=str, required=True,
                        help="参照画像が格納されたフォルダのパス")
    args = parser.parse_args()

    # --- APIキーの確認 ---
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("エラー: 環境変数 'ANTHROPIC_API_KEY' が設定されていません。")
        print("Anthropic APIキーを設定して再実行してください。例: export ANTHROPIC_API_KEY='sk-...'")
        return

    client = Anthropic(api_key=api_key)

    # --- 製品概要の読み込み ---
    product_overview_path = Path(args.product_overview)
    if not product_overview_path.exists():
        print(f"エラー: 製品概要ファイルが見つかりません: {product_overview_path}")
        return
    product_overview_content = product_overview_path.read_text(encoding="utf-8")
    print(f"製品概要ファイルを読み込みました: {product_overview_path}")

    # --- 参照画像の読み込みとエンコード ---
    image_folder_path = Path(args.image_folder)
    if not image_folder_path.is_dir():
        print(f"エラー: 画像フォルダが見つからないか、ディレクトリではありません: {image_folder_path}")
        return

    image_messages = []
    supported_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    for img_file in image_folder_path.iterdir():
        if img_file.is_file() and img_file.suffix.lower() in supported_extensions:
            encoded_image = encode_image_to_base64(img_file)
            if encoded_image:
                print(f"画像をエンコードしました: {img_file}")
                image_messages.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": f"image/{img_file.suffix.lstrip('.')}", # 例: image/png
                        "data": encoded_image,
                    },
                })
        else:
            if img_file.is_file():
                print(f"警告: 非対応の画像形式をスキップしました: {img_file.name}")

    if not image_messages:
        print("警告: 参照画像が見つかりませんでした。画像がなくても処理は続行しますが、精度が低下する可能性があります。")

    # --- プロンプトの構築 ---
    system_prompt = """
    あなたは優秀なUI/UXデザイナーであり、デザインシステムの専門家です。
    提供された製品概要と参照画像を基に、ユーザーフレンドリーで一貫性のあるデザインシステムを提案してください。

    具体的には、以下の要素を含むWebページを構成するHTML、CSS、JavaScriptコードを生成してください。
    - **カラーパレット**: プライマリ、セカンダリ、背景、テキスト、アクセントなどの主要色。
    - **タイポグラフィ**: フォントファミリー、見出し（H1-H6）、本文（Pタグ）のサイズ、行高、ウェイト。
    - **コンポーネント例**: 主要なUIコンポーネント（例: ボタン、入力フィールド、カード、ナビゲーションバーなど）の具体的なHTML構造とCSSスタイル。
    - **レイアウトとスペーシング**: 基本的なレイアウト（例: コンテナ、グリッド）、スペーシングの規則。

    生成されるコードは、単一のHTMLファイル（インラインCSS、または<style>タグ内のCSS、簡単なインラインJS）として完結し、ブラウザで直接開ける形にしてください。
    CSSはモダンな記法を使用し、可読性を重視してください。
    各要素は明確なクラス名を付け、デザインシステムの一部として理解しやすいようにしてください。
    コードブロックとしてのみ出力してください。余計な説明は不要です。
    """

    user_message_content = [
        {"type": "text", "text": f"### 製品概要:\n{product_overview_content}\n\n"}
    ] + image_messages + [
        {"type": "text", "text": "上記の情報を参考に、デザインシステムの主要要素を示すHTML/CSS/JSコードを生成してください。"}
    ]

    print("Claude APIにリクエストを送信しています...")
    try:
        message = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=4000, # 必要に応じて調整
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message_content}
            ]
        )

        response_text = message.content[0].text
        
        # コードブロックを抽出 (必要に応じて調整)
        if "" in response_text:
            start_index = response_text.find("") + len("")
            end_index = response_text.rfind("")
            generated_code = response_text[start_index:end_index].strip()
        else:
            print("警告: コードブロック '' が見つかりませんでした。レスポンス全体をファイルに保存します。")
            generated_code = response_text

        # 生成されたコードをファイルに保存
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            f.write(generated_code)
        print(f"デザインシステムコードが '{OUTPUT_FILENAME}' に保存されました。")
        print("ブラウザでこのファイルを開いて確認してください。")

    except Exception as e:
        print(f"Claude APIからの応答中にエラーが発生しました: {e}")
        # 詳細なエラーメッセージ (例: APIからのHTTPエラー) を表示する場合
        # print(f"APIエラー詳細: {e.response.text}" if hasattr(e, 'response') and hasattr(e.response, 'text') else "")


if __name__ == "__main__":
    main()

---

**`product_overview.txt`** (例)
製品名: AI Smart Assistant Dashboard
目的: ユーザーのAIアシスタント利用状況を可視化し、設定を管理する。
ターゲットユーザー: テクノロジーに慣れているが、使いやすさを求めるビジネスパーソン。
ブランドイメージ: モダン、クリーン、効率的、信頼性。
主要機能:
- ダッシュボードでの利用データ表示
- アシスタント設定のカスタマイズ
- 履歴の参照と管理
- レポートのエクスポート
優先するデザイン要素:
- ダークモード対応
- データ可視化のためのグラフコンポーネント
- 直感的なナビゲーション
- ミニマルなUIデザイン
---

**`images/`フォルダ** (例として、フォルダ内に`logo.png`, `dashboard_mockup.png`などの画像を配置します)
images/
├── logo.png
└── dashboard_mockup.png
---

### 2. コマンド

必要なファイルを配置したら、以下のコマンドで実行します。

# 1. Anthropicライブラリをインストール（初回のみ）
pip install anthropic

# 2. 環境変数にAPIキーを設定
# Mac/Linuxの場合:
export ANTHROPIC_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# Windowsの場合（コマンドプロンプト）:
set ANTHROPIC_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# Windowsの場合（PowerShell）:
$env:ANTHROPIC_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 3. Pythonスクリプトを実行
python generate_design_system.py --product_overview product_overview.txt --image_folder images
---

## 使い方

1.  **Anthropic APIキーの取得**: Anthropicの公式サイトでアカウントを作成し、APIキー（`sk-...`で始まる文字列）を発行します。
2.  **必要なファイルの作成**: 上記の`generate_design_system.py`、`product_overview.txt`、そして`images/`フォルダを、同じディレクトリ内に作成します。
3.  **`product_overview.txt`の編集**: あなたの製品やプロジェクトに関する詳細情報（目的、ターゲット、ブランドイメージ、主要機能、デザインの要望など）を具体的に記述します。Claudeはここからデザインの方向性を理解します。
4.  **`images/`フォルダに参照画像を配置**: UIの参考になるスクリーンショット、既存のロゴ、手書きのスケッチ、インスピレーションとなるウェブサイトのUI画像などを、`images/`フォルダに入れます。ファイル形式はPNG, JPG, GIF, WEBPなどに対応しています。
5.  **Pythonライブラリのインストール**: ターミナルまたはコマンドプロンプトを開き、`pip install anthropic`を実行して、必要なライブラリをインストールします。
6.  **APIキーの環境変数設定**: 取得したAnthropic APIキーを、上記コマンド例に従って環境変数`ANTHROPIC_API_KEY`に設定します。**APIキーをコードに直接書き込まないでください。**
7.  **スクリプトの実行**: `python generate_design_system.py --product_overview product_overview.txt --image_folder images`コマンドを実行します。
8.  **結果の確認**: 実行が完了すると、`generated_design_system.html`というファイルが作成されます。このファイルをWebブラウザで開くと、Claudeが生成したデザインシステムの提案（HTML/CSS/JSコード）を確認できます。

## よくある質問

**Q: どんな画像を用意すればいいですか？**
A: UIの参考になるスクリーンショット、既存のロゴ、手書きのワイヤーフレーム、競合他社の良いUI例、あるいはブランドイメージを伝える写真など、デザインのヒントになるものなら何でも構いません。複数枚用意することで、より多くの情報をClaudeに与えられます。

**Q: 製品概要ファイルには何を書けばいいですか？**
A: 製品の目的、ターゲットユーザー、主要な機能、ブランドの雰囲気やカラーパレットの好み、避けたいデザイン要素など、ClaudeがUIデザインを理解するために必要な情報を具体的に記述してください。箇条書きや短文で分かりやすくまとめると良いでしょう。

**Q: APIキーはどこで取得しますか？**
A: Anthropicの公式サイト（[https://www.anthropic.com/](https://www.anthropic.com/)）でアカウントを作成し、開発者ダッシュボードからAPIキーを発行できます。

**Q: 生成される出力形式は変更できますか？**
A: はい、`generate_design_system.py`スクリプト内の`system_prompt`や`user_message_content`を編集することで、Claudeへの指示を変更できます。例えば、「Reactコンポーネントのコードで出力してください」や「Figmaのデザイン仕様書としてMarkdownで出力してください」といった指示を加えることが可能です。ただし、Claudeの出力能力とプロンプトの具体性に依存します。

**Q: `max_tokens`を調整する意味は？**
A: `max_tokens`はClaudeが生成する応答の最大トークン数です。詳細なコードや多くのコンポーネントを生成したい場合は、この値を大きく設定する必要があります。ただし、トークン数が増えるとAPIの利用料金も増加します。

---
AI Conduit: [https://www.youtube.com/@AI.Conduit](https://www.youtube.com/@AI.Conduit)