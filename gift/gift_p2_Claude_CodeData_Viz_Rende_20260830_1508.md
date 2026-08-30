# Claude CodeのData Viz Renderer - 実践テンプレート

## この動画で学んだこと
この動画では、Claude CodeのData Viz Renderer機能を使うことで、JSON形式の設定ファイルを準備するだけで簡単にインフォグラフィックを生成できることを学びました。複雑なコーディングなしに、データから視覚的な洞察を得るための強力なアプローチです。

## すぐに使えるテンプレート

ここでは、動画で紹介された概念を具体的にPythonの`matplotlib`ライブラリを使って実現するテンプレートを提供します。これにより、`config.json`ファイルとスクリプトを使ってインフォグラフィックを生成できます。

---

**1. `config.json` (インフォグラフィックの設定ファイル)**

このファイルに、生成したいグラフの種類、タイトル、データなどを記述します。

// config.json
{
  // グラフの種類を指定します。"bar" (棒グラフ), "line" (折れ線グラフ), "pie" (円グラフ) が選択可能です。
  "chart_type": "bar",
  
  // グラフのタイトル
  "title": "地域別利用者数",
  
  // X軸のラベル（棒グラフ、折れ線グラフの場合）
  "x_label": "地域",
  
  // Y軸のラベル（棒グラフ、折れ線グラフの場合）
  "y_label": "利用者数 (人)",
  
  // 生成される画像ファイルのファイル名
  "output_filename": "region_users_infographic.png",
  
  // グラフに表示するデータ
  // chart_typeが"bar"または"line"の場合: {"category": "ラベル", "value": 数値} または {"x": x値, "y": y値}
  // chart_typeが"pie"の場合: {"label": "ラベル", "size": 割合}
  "data": [
    { "category": "東京", "value": 500 },
    { "category": "大阪", "value": 350 },
    { "category": "名古屋", "value": 200 },
    { "category": "福岡", "value": 180 },
    { "category": "札幌", "value": 120 }
  ]
}
---

**2. `generate_infographic.py` (インフォグラフィック生成スクリプト)**

このPythonスクリプトは、上記`config.json`を読み込み、それに基づいてインフォグラフィックを生成し、画像ファイルとして保存します。

# generate_infographic.py
import json        # JSONファイルを扱うためのモジュール
import matplotlib.pyplot as plt # データ可視化ライブラリ
import sys         # コマンドライン引数を扱うためのモジュール
import os          # ファイルパスを扱うためのモジュール

def generate_infographic(config_path):
    """
    設定ファイルに基づいてインフォグラフィックを生成します。
    """
    # 設定ファイルが存在するか確認
    if not os.path.exists(config_path):
        print(f"エラー: 設定ファイル '{config_path}' が見つかりません。")
        sys.exit(1)

    # 設定ファイルを読み込む
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 設定値の取得（デフォルト値を設定して、設定漏れによるエラーを回避）
    chart_type = config.get('chart_type', 'bar') # グラフの種類 (例: bar, line, pie)
    title = config.get('title', 'インフォグラフィック') # グラフのタイトル
    x_label = config.get('x_label', 'カテゴリ') # X軸のラベル
    y_label = config.get('y_label', '値') # Y軸のラベル
    data = config.get('data', []) # グラフのデータ
    output_filename = config.get('output_filename', 'infographic.png') # 出力ファイル名

    # データが空の場合は警告を表示して終了
    if not data:
        print("警告: グラフのデータが空です。グラフは生成されません。")
        return

    # グラフの生成を開始
    plt.figure(figsize=(10, 6)) # グラフのサイズを設定（幅10インチ、高さ6インチ）

    if chart_type == 'bar':
        # 棒グラフのデータ準備
        categories = [d.get('category', '') for d in data]
        values = [d.get('value', 0) for d in data]
        plt.bar(categories, values, color='skyblue') # 棒グラフを生成
        plt.xlabel(x_label) # X軸ラベルを設定
        plt.ylabel(y_label) # Y軸ラベルを設定
    elif chart_type == 'line':
        # 折れ線グラフのデータ準備
        x_values = [d.get('x', i) for i, d in enumerate(data)] # 'x'がなければインデックスを使用
        y_values = [d.get('y', 0) for d in data]
        plt.plot(x_values, y_values, marker='o', linestyle='-', color='green') # 折れ線グラフを生成
        plt.xlabel(x_label)
        plt.ylabel(y_label)
    elif chart_type == 'pie':
        # 円グラフのデータ準備
        labels = [d.get('label', '') for d in data]
        sizes = [d.get('size', 0) for d in data]
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors) # 円グラフを生成
        plt.axis('equal')  # アスペクト比を等しくして円を真円にする
    else:
        # 未知のグラフタイプが指定された場合
        print(f"エラー: 未知のグラフタイプ '{chart_type}' です。'bar', 'line', 'pie' のいずれかを指定してください。")
        return

    plt.title(title) # グラフのタイトルを設定
    plt.grid(axis='y', linestyle='--', alpha=0.7) # グリッド線を追加（Y軸のみ、破線、透明度0.7）
    plt.tight_layout() # レイアウトを自動調整して、要素が重なるのを防ぐ

    # グラフを画像ファイルとして保存
    try:
        plt.savefig(output_filename)
        print(f"インフォグラフィックが '{output_filename}' に正常に保存されました。")
    except Exception as e:
        print(f"エラー: インフォグラフィックの保存中に問題が発生しました: {e}")

    plt.close() # プロットを閉じてメモリを解放

if __name__ == '__main__':
    # コマンドライン引数がない場合、使い方を表示
    if len(sys.argv) < 2:
        print("使い方: python generate_infographic.py <設定ファイル名.json>")
        sys.exit(1)
    
    # コマンドライン引数から設定ファイル名を取得して実行
    config_file = sys.argv[1]
    generate_infographic(config_file)
---

**3. コマンド**

スクリプトを実行してインフォグラフィックを生成します。

# Pythonスクリプトを実行し、設定ファイル名を引数として渡します
python generate_infographic.py config.json
---

## 使い方

1.  **必要なライブラリのインストール**:
    Pythonがインストールされていることを確認し、データ可視化ライブラリ`matplotlib`をインストールします。
    pip install matplotlib
    2.  **ファイルの作成**:
    *   上記「1. `config.json`」の内容をコピーし、`config.json`という名前でファイルを作成します。
    *   上記「2. `generate_infographic.py`」の内容をコピーし、`generate_infographic.py`という名前でファイルを作成します。
    *   これら2つのファイルは同じディレクトリに保存してください。

3.  **`config.json`の編集**:
    生成したいインフォグラフィックに合わせて、`config.json`ファイルの内容を編集します。`chart_type`、`title`、`data`などを変更してみましょう。

4.  **スクリプトの実行**:
    ターミナル（コマンドプロンプトやPowerShellなど）を開き、`config.json`と`generate_infographic.py`を保存したディレクトリに移動します。
    そして、以下のコマンドを実行します。
    python generate_infographic.py config.json
    5.  **結果の確認**:
    実行が成功すると、`config.json`で指定した`output_filename`（例: `region_users_infographic.png`）の画像ファイルが同じディレクトリに生成されます。この画像ファイルを開いて、生成されたインフォグラフィックを確認してください。

## よくある質問

**Q: どのような種類のグラフが作成できますか？**
A: 提供されたテンプレートでは、`bar` (棒グラフ)、`line` (折れ線グラフ)、`pie` (円グラフ) の3種類のグラフをサポートしています。`config.json`の`chart_type`を変更することで切り替えられます。

**Q: グラフのデータを変更するにはどうすれば良いですか？**
A: `config.json`ファイル内の`"data"`セクションを直接編集してください。例えば、棒グラフや折れ線グラフの場合は`"category"`/`"x"`と`"value"`/`"y"`のペアを、円グラフの場合は`"label"`と`"size"`のペアを、目的のデータに合わせて調整します。

**Q: Claude CodeのData Viz Rendererとは具体的に何ですか？**
A: この動画で紹介されている「Claude CodeのData Viz Renderer」は、AIアシスタントのClaudeがコード生成を行う際に、データ可視化のニーズに応じてJSON設定を基にインフォグラフィックを生成する機能や、そのようなスクリプトを提示する能力を指していると推測されます。提供されたテンプレートは、その概念をPythonと`matplotlib`で実現した具体的な例です。AIが直接描画するのではなく、AIが生成した設定ファイルとスクリプトによって描画されるイメージです。

---
AI Conduit: https://www.youtube.com/@AI.Conduit