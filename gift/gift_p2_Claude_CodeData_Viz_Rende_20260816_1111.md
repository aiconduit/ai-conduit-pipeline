# Claude CodeのData Viz Rendererでデータ可視化がコマンド一つで自動生成された - 実践テンプレート

## この動画で学んだこと
この動画では、データ可視化を効率的に行う新しいアプローチが紹介されました。JSON形式の設定ファイルを記述し、シンプルなコマンドを実行するだけで、自己完結型のデータ可視化HTMLファイルが自動生成されるという画期的な手法です。

## すぐに使えるテンプレート

ここでは、動画で紹介された「Data Viz Renderer」の概念をPythonとD3.js（JavaScriptライブラリ）で再現した、すぐに使えるテンプレートを提供します。JSON形式でデータの種類や軸を設定し、Pythonスクリプトを実行することで、インタラクティブな棒グラフを含むHTMLファイルを生成できます。

---

### 1. 設定ファイル: `config.json`

このJSONファイルで、グラフのタイトル、データ、軸のラベルなどを定義します。

{
  "chartTitle": "2023年 月別売上データ",
  "chartType": "bar",
  "data": [
    {"label": "1月", "value": 150},
    {"label": "2月", "value": 180},
    {"label": "3月", "value": 120},
    {"label": "4月", "value": 200},
    {"label": "5月", "value": 170},
    {"label": "6月", "value": 220},
    {"label": "7月", "value": 190},
    {"label": "8月", "value": 210},
    {"label": "9月", "value": 240},
    {"label": "10月", "value": 230},
    {"label": "11月", "value": 250},
    {"label": "12月", "value": 280}
  ],
  "xAxisLabel": "月",
  "yAxisLabel": "売上 (万円)"
}
### 2. 生成スクリプト: `generate_viz.py`

このPythonスクリプトは、`config.json`を読み込み、D3.jsを利用したデータ可視化HTMLファイルを生成します。

import json
import sys

def generate_html(config_file_path, output_file_path):
    """
    JSON設定ファイルからデータ可視化用のHTMLファイルを生成します。
    """
    try:
        # 設定ファイルをUTF-8エンコーディングで読み込み
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"エラー: 設定ファイル '{config_file_path}' が見つかりません。")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"エラー: 設定ファイル '{config_file_path}' のJSON形式が不正です。")
        sys.exit(1)

    # 設定ファイルから各種情報を取得（デフォルト値も設定）
    chart_title = config.get("chartTitle", "データ可視化")
    # 今回は棒グラフに限定していますが、chartTypeで分岐することも可能です
    chart_type = config.get("chartType", "bar") 
    data = config.get("data", [])
    x_axis_label = config.get("xAxisLabel", "X軸")
    y_axis_label = config.get("yAxisLabel", "Y軸")

    # JavaScriptで扱いやすいようにデータをJSON文字列に変換
    data_js = json.dumps(data, ensure_ascii=False) # 日本語対応

    # HTMLテンプレート文字列
    # D3.jsをCDN経由で読み込み、棒グラフを描画するJavaScriptコードを埋め込みます
    html_template = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{chart_title}</title>
    <!-- D3.jsをCDN経由で読み込む -->
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 20px; 
            background-color: #f4f4f4;
            color: #333;
        }}
        .chart-container {{
            max-width: 900px;
            margin: 40px auto;
            border: 1px solid #ddd;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            background-color: #fff;
            border-radius: 8px;
        }}
        h1 {{ 
            text-align: center; 
            color: #2c3e50; 
            margin-bottom: 30px;
            font-size: 2em;
        }}
        .axis-label {{ 
            font-size: 15px; 
            fill: #555; 
            font-weight: bold;
        }}
        .tick text {{ 
            font-size: 12px; 
            fill: #666;
        }}
        .bar {{ 
            fill: #4682b4; /* SteelBlue */
            transition: fill 0.2s ease;
        }}
        .bar:hover {{ 
            fill: #5fa8e3; /* 明るいSteelBlue */
        }}
        .bar-value {{
            font-size: 11px;
            fill: #333;
            pointer-events: none; /* テキストがバーのホバーイベントを邪魔しないように */
        }}
    </style>
</head>
<body>
    <div class="chart-container">
        <h1>{chart_title}</h1>
        <svg id="chart"></svg>
    </div>

    <script>
        // 設定ファイルから読み込んだデータ
        const data = {data_js};

        // SVGのサイズとマージン設定
        const margin = {{ top: 50, right: 40, bottom: 80, left: 80 }};
        const width = 900 - margin.left - margin.right;
        const height = 550 - margin.top - margin.bottom;

        // SVG要素を選択し、描画エリアのグループを追加
        const svg = d3.select("#chart")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
          .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // X軸のスケール (ラベル)
        const x = d3.scaleBand()
            .range([0, width])
            .padding(0.1)
            .domain(data.map(d => d.label));

        // Y軸のスケール (値)
        const y = d3.scaleLinear()
            .range([height, 0])
            .domain([0, d3.max(data, d => d.value) * 1.15]); // 最大値の少し上までを上限に

        // X軸を描画
        svg.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(x))
            .selectAll("text")
                .attr("transform", "rotate(-45)")
                .style("text-anchor", "end")
                .style("font-size", "13px");

        // Y軸を描画
        svg.append("g")
            .call(d3.axisLeft(y));

        // X軸ラベル
        svg.append("text")
            .attr("class", "axis-label")
            .attr("x", width / 2)
            .attr("y", height + margin.bottom - 15)
            .style("text-anchor", "middle")
            .text("{x_axis_label}");

        // Y軸ラベル
        svg.append("text")
            .attr("class", "axis-label")
            .attr("transform", "rotate(-90)")
            .attr("y", -margin.left + 30)
            .attr("x", -height / 2)
            .style("text-anchor", "middle")
            .text("{y_axis_label}");

        // バーを描画
        svg.selectAll(".bar")
            .data(data)
            .enter().append("rect")
            .attr("class", "bar")
            .attr("x", d => x(d.label))
            .attr("width", x.bandwidth())
            .attr("y", d => y(d.value))
            .attr("height", d => height - y(d.value));

        // バーの上に値のテキストを追加
        svg.selectAll(".bar-value")
            .data(data)
            .enter().append("text")
            .attr("class", "bar-value")
            .attr("x", d => x(d.label) + x.bandwidth() / 2)
            .attr("y", d => y(d.value) - 8) // バーの上に少し隙間を空けて表示
            .attr("text-anchor", "middle")
            .text(d => d.value);

    </script>
</body>
</html>
"""

    try:
        # 生成されたHTMLファイルをUTF-8エンコーディングで書き出し
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        print(f"データ可視化HTMLファイル '{output_file_path}' が正常に生成されました。")
    except IOError as e:
        print(f"エラー: HTMLファイルの書き込み中に問題が発生しました - {e}")
        sys.exit(1)

# スクリプトが直接実行された場合の処理
if __name__ == '__main__':
    # 引数の数をチェック
    if len(sys.argv) != 3:
        print("使用方法: python generate_viz.py <設定ファイル名.json> <出力ファイル名.html>")
        sys.exit(1)

    # コマンドライン引数からファイルパスを取得
    config_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # HTML生成関数を実行
    generate_html(config_file, output_file)
---

## 使い方

以下の手順で、`config.json`からデータ可視化HTMLを生成できます。

1.  **ファイルの準備:**
    *   上記の`config.json`の内容をコピーし、`config.json`という名前でファイルを作成します。
    *   上記の`generate_viz.py`の内容をコピーし、`generate_viz.py`という名前でファイルを作成します。
    *   これら2つのファイルを同じディレクトリに保存します。

2.  **設定ファイルの編集 (オプション):**
    *   `config.json`を開き、`chartTitle` (グラフのタイトル)、`data` (可視化したいデータ)、`xAxisLabel` (X軸のラベル)、`yAxisLabel` (Y軸のラベル) を自由に変更してください。
        *   `data`配列内の各オブジェクトは`label` (項目名) と`value` (値) を持つ必要があります。

3.  **コマンドの実行:**
    *   ターミナルまたはコマンドプロンプトを開き、ファイルが保存されているディレクトリに移動します。
    *   以下のコマンドを実行します。

    python generate_viz.py config.json output.html
    *   `config.json`は入力となる設定ファイル名、`output.html`は生成されるHTMLファイル名です。出力ファイル名は任意に変更可能です。

4.  **結果の確認:**
    *   コマンドが正常に完了すると、指定した名前（例: `output.html`）のHTMLファイルが生成されます。
    *   このHTMLファイルをWebブラウザで開いて、生成されたデータ可視化を確認してください。インタラクティブな棒グラフが表示されます。

## よくある質問

**Q1: この「Data Viz Renderer」はどこで入手できますか？**
A1: 動画で紹介された「Claude CodeのData Viz Renderer」は、LLM（大規模言語モデル）によって自動生成される、またはそのコンセプトを指している可能性があります。ここに提供した`generate_viz.py`スクリプトは、その「JSON設定からコマンド一つでHTMLを生成する」という動画のコンセプトをPythonとD3.jsを使って再現したものです。これをベースに、ご自身のニーズに合わせて拡張していくことが可能です。

**Q2: 棒グラフ以外のグラフタイプ（円グラフ、散布図など）は作れますか？**
A2: 現在提供している`generate_viz.py`スクリプトは棒グラフに特化しています。他のグラフタイプに対応するには、スクリプト内のHTMLテンプレート（D3.jsの部分）を、それぞれのグラフタイプを描画するコードに書き換える必要があります。`config.json`に`chartType`フィールドを追加し、Pythonスクリプトでその値に応じて異なるHTML/JavaScriptコードを埋め込むようにすることで、複数のグラフタイプに対応できます。

**Q3: データソースはJSONファイル以外（CSVなど）でも対応できますか？**
A3: はい、可能です。`generate_viz.py`スクリプト内でCSVファイルを読み込む処理（Pythonの`csv`モジュールなどを使用）を追加し、そのデータをJSONの`data`形式に変換してからHTMLテンプレートに埋め込むように変更すれば対応できます。

---
AI Conduit: https://www.youtube.com/@AI.Conduit