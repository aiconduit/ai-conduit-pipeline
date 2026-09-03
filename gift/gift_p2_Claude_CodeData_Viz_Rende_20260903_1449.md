# Claude CodeのData Viz Rendererでインフォグラフィックが自動生成された - 実践テンプレート

## この動画で学んだこと
この動画では、Claude CodeのData Viz Rendererを使うことで、複雑なインフォグラフィックもJSON形式の設定ファイルを用意し、スクリプトを実行するだけで簡単に自動生成できることが紹介されました。データの可視化にかかる手間を大幅に削減できる画期的なツールです。

## すぐに使えるテンプレート

ここでは、動画で紹介された「Data Viz Renderer」のコンセプトをPythonと`matplotlib`ライブラリで再現した、すぐに使えるテンプレートを提供します。JSON形式の設定ファイルをもとに、グラフを自動生成します。

---

### 1. データ設定ファイル (`config.json`)

可視化したいデータをJSON形式で定義します。このファイルは、グラフの種類、タイトル、軸ラベル、そして具体的なデータポイントを含みます。

{
  "chart_type": "bar",
  "title": "月間製品販売数データ",
  "x_label": "製品カテゴリ",
  "y_label": "販売数 (単位)",
  "data": [
    {"label": "電子機器", "value": 150},
    {"label": "アパレル", "value": 180},
    {"label": "日用品", "value": 120},
    {"label": "食品", "value": 200},
    {"label": "書籍", "value": 90}
  ]
}
---

### 2. 可視化スクリプト (`render_viz.py`)

上記`config.json`を読み込み、グラフを生成して画像ファイルとして保存するPythonスクリプトです。

import json
import matplotlib.pyplot as plt
import sys
import os

def render_visualization(config_path):
    """
    設定ファイルを読み込み、指定されたデータと種類に基づいて可視化を生成する関数。

    Args:
        config_path (str): JSON形式の設定ファイルのパス。
    """
    try:
        # 設定ファイルをUTF-8エンコーディングで読み込む
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"エラー: 設定ファイル '{config_path}' が見つかりません。")
        return
    except json.JSONDecodeError:
        print(f"エラー: 設定ファイル '{config_path}' のJSON形式が不正です。")
        return
    except Exception as e:
        print(f"ファイルの読み込み中に予期せぬエラーが発生しました: {e}")
        return

    # 設定ファイルから各種パラメータを取得（デフォルト値も設定）
    chart_type = config.get("chart_type", "bar")  # グラフの種類 (bar, lineなど)
    title = config.get("title", "データ可視化")    # グラフのタイトル
    x_label = config.get("x_label", "X軸")      # X軸のラベル
    y_label = config.get("y_label", "Y軸")      # Y軸のラベル
    data = config.get("data", [])             # 可視化するデータリスト

    # データが存在しない場合は警告を出して終了
    if not data:
        print("警告: 可視化するデータが設定ファイルに含まれていません。")
        return

    # データリストからラベルと値を取得
    labels = [d["label"] for d in data if "label" in d and "value" in d]
    values = [d["value"] for d in data if "label" in d and "value" in d]

    # 有効なラベルや値が不足している場合も警告
    if not labels or not values or len(labels) != len(values):
        print("警告: 処理できる有効なデータがありません。各データ項目に 'label' と 'value' が必要です。")
        return

    # グラフの生成を開始
    plt.figure(figsize=(10, 6))  # グラフのサイズを幅10インチ、高さ6インチに設定

    if chart_type == "bar":
        # 棒グラフの生成
        plt.bar(labels, values, color='skyblue')  # 棒グラフを描画し、色を指定
        plt.xlabel(x_label)  # X軸ラベルを設定
        plt.ylabel(y_label)  # Y軸ラベルを設定
        plt.title(title)     # グラフタイトルを設定
        plt.xticks(rotation=45, ha='right')  # X軸のラベルを45度回転させて、右揃えにする
        plt.grid(axis='y', linestyle='--', alpha=0.7) # Y軸にグリッドを表示
        plt.tight_layout()   # レイアウトが自動的に調整され、要素が重ならないようにする
    elif chart_type == "line":
        # 折れ線グラフの生成 (config.jsonのchart_typeを"line"に変更して試せます)
        plt.plot(labels, values, marker='o', linestyle='-', color='blue') # 折れ線グラフを描画
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.xticks(rotation=45, ha='right')
        plt.grid(True)       # 全体にグリッドを表示
        plt.tight_layout()
    else:
        # 未対応のグラフ種類の場合の処理
        print(f"警告: 未対応のグラフ種類 '{chart_type}' です。棒グラフを生成します。")
        plt.bar(labels, values, color='skyblue')
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

    # 出力ファイル名を生成（タイトルからスペースをアンダースコアに変換）
    output_filename = f"{title.replace(' ', '_').replace('/', '_')}_viz.png"
    
    try:
        plt.savefig(output_filename, dpi=300, bbox_inches='tight') # 高解像度で画像として保存
        print(f"可視化が '{output_filename}' として正常に保存されました。")
    except Exception as e:
        print(f"画像の保存中にエラーが発生しました: {e}")
    finally:
        plt.close() # グラフ表示ウィンドウを閉じる (スクリプト実行時)

if __name__ == "__main__":
    # スクリプト実行時にコマンドライン引数があればそれを設定ファイルとして使用
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        # 引数がない場合はデフォルトで "config.json" を使用
        config_file = "config.json"
        print(f"設定ファイルが指定されませんでした。デフォルトの '{config_file}' を使用します。")

    # 可視化処理を実行
    render_visualization(config_file)
---

## 使い方

このテンプレートを使用して、インフォグラフィックを生成する手順は以下の通りです。

1.  **Pythonのインストール**:
    お使いのシステムにPythonがインストールされていない場合、[Python公式サイト](https://www.python.org/downloads/)からインストールしてください。

2.  **必要なライブラリのインストール**:
    このスクリプトは`matplotlib`ライブラリを使用します。以下のコマンドでインストールしてください。
    pip install matplotlib
    3.  **テンプレートファイルの保存**:
    *   上記の「1. データ設定ファイル (`config.json`)」の内容を`config.json`という名前でファイルに保存します。
    *   上記の「2. 可視化スクリプト (`render_viz.py`)」の内容を`render_viz.py`という名前でファイルに保存します。
    *   これら2つのファイルは**同じディレクトリ**に保存してください。

4.  **`config.json`の編集**:
    生成したいグラフに合わせて、`config.json`の内容を編集します。
    *   `chart_type`: `"bar"` (棒グラフ) または `"line"` (折れ線グラフ) を指定します。
    *   `title`, `x_label`, `y_label`: グラフのタイトルと軸のラベルを設定します。
    *   `data`: `{"label": "項目名", "value": 数値}`の形式で可視化したいデータを記述します。

5.  **スクリプトの実行**:
    ターミナルまたはコマンドプロンプトを開き、ファイルが保存されているディレクトリに移動して、以下のコマンドを実行します。

    python render_viz.py
    または、特定の設定ファイルを指定する場合は、
    python render_viz.py my_custom_config.json
    6.  **結果の確認**:
    スクリプトが正常に実行されると、`config.json`で指定した`title`に基づいて、`月間製品販売数データ_viz.png`のような名前の画像ファイルが同じディレクトリに生成されます。この画像ファイルを開いて、生成されたインフォグラフィックを確認してください。

## よくある質問

**Q: どのようなグラフが生成できますか？**
A: 提供されたテンプレートでは、`chart_type`を`"bar"`に設定することで棒グラフ、`"line"`に設定することで折れ線グラフを生成できます。`render_viz.py`を編集することで、さらに多くの種類のグラフ（散布図、円グラフなど）に対応させることが可能です。

**Q: 動画で紹介された「Data Viz Renderer」とは具体的に何ですか？**
A: 動画では具体的な製品名やライブラリの詳細は明示されていませんが、本テンプレートは「設定ファイル（JSON）からスクリプト実行で自動的に可視化を生成する」という動画のコンセプトを再現したものです。多くの場合、このようなツールはPythonの`matplotlib`や`seaborn`、JavaScriptの`D3.js`、あるいは専用のBIツールなどを内部で利用しています。

**Q: 他のデータ形式（CSV、Excelなど）は利用できますか？**
A: 現在のテンプレートはJSON形式の`config.json`ファイルにのみ対応しています。`render_viz.py`スクリプトを修正し、`pandas`ライブラリなどを使用することで、CSVやExcelファイルからデータを読み込み、可視化することも可能です。

**Q: グラフの色やフォントを変更したい場合はどうすれば良いですか？**
A: `render_viz.py`スクリプト内の`matplotlib`の設定を変更することで、色、フォント、背景、グラフのスタイルなどをカスタマイズできます。`matplotlib`の公式ドキュメントを参照して、設定を調整してください。

---
AI Conduit: https://www.youtube.com/@AI.Conduit