# Claude Codeのデータ可視化でKPIが自動グラフ化 - 実践テンプレート

## この動画で学んだこと
この動画では、`Data Viz Renderer`というツールを活用し、`config.json`ファイルを定義することでKPIを自動的にグラフ化する方法が紹介されました。特に、`dataType`を"stats"に設定し、表示したい「数値」と「傾向」を`dataFields`に追記することで、設定ベースでのデータ可視化が可能になります。

## すぐに使えるテンプレート

このテンプレートでは、動画で紹介された概念に基づき、Pythonを使ってJSON設定ファイルから主要なKPIの「数値」と「傾向」を抽出し、シンプルなダッシュボードグラフを自動生成する例を提供します。

### 1. `config.json`

このファイルに、表示したいKPIの設定を記述します。

{
  "dataType": "stats",
  "dataConfig": [
    {
      "kpiName": "売上高",
      "dataKey": "sales",
      "trendDisplay": "前日比"
    },
    {
      "kpiName": "顧客獲得数",
      "dataKey": "new_customers",
      "trendDisplay": "前週比"
    },
    {
      "kpiName": "Webサイト訪問数",
      "dataKey": "website_visits",
      "trendDisplay": "前日比"
    }
  ],
  "outputFile": "kpi_dashboard.png",
  "title": "主要KPI自動グラフ化ダッシュボード"
}
### 2. `data_viz_renderer.py`

このPythonスクリプトが`config.json`を読み込み、ダミーデータからKPIの「数値」と「傾向」を計算し、グラフを生成します。

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from datetime import datetime, timedelta

def generate_dummy_data(start_date, periods):
    """
    ダミーのKPIデータを生成します。
    ここでは、日々の売上、新規顧客、Webサイト訪問数のデータを生成します。
    """
    dates = [start_date - timedelta(days=i) for i in range(periods)]
    data = {
        'date': dates[::-1], # 日付を昇順にする
        'sales': np.random.randint(10000, 50000, periods) + np.arange(periods) * 100,
        'new_customers': np.random.randint(50, 200, periods) + np.arange(periods) * 5,
        'website_visits': np.random.randint(1000, 5000, periods) + np.arange(periods) * 10
    }
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index() # 日付をインデックスにしてソート
    return df

def calculate_trend(df, data_key, trend_type):
    """
    指定されたKPIの傾向（変化率）を計算します。
    trend_typeに応じて、前日比、前週比、前月比などを計算します。
    """
    if df.empty:
        return 0.0

    current_value = df[data_key].iloc[-1]
    if len(df) < 2: # データが1つしかない場合は傾向を計算できない
        return 0.0

    if trend_type == "前日比":
        previous_value = df[data_key].iloc[-2] if len(df) >= 2 else 0
    elif trend_type == "前週比":
        # 過去7日前からのデータを取得
        prev_date = df.index[-1] - timedelta(days=7)
        if prev_date in df.index:
            previous_value = df.loc[prev_date, data_key]
        else:
            previous_value = df[data_key].iloc[-2] # ない場合は前日比で代用
    elif trend_type == "前月比":
        # 過去30日前からのデータを取得（簡略化のため）
        prev_date = df.index[-1] - timedelta(days=30)
        if prev_date in df.index:
            previous_value = df.loc[prev_date, data_key]
        else:
            previous_value = df[data_key].iloc[-2] # ない場合は前日比で代用
    else: # デフォルトは前日比
        previous_value = df[data_key].iloc[-2] if len(df) >= 2 else 0

    if previous_value == 0:
        return 0.0 # ゼロ割を防ぐ
    
    return ((current_value - previous_value) / previous_value) * 100

def format_currency(x, pos):
    """通貨フォーマット関数"""
    if x >= 1_000_000:
        return f'¥{x/1_000_000:.1f}M'
    elif x >= 1_000:
        return f'¥{x/1_000:.1f}K'
    return f'¥{int(x)}'

def render_data_viz(config_path="config.json"):
    """
    config.jsonを読み込み、KPIデータを可視化します。
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"エラー: 設定ファイル '{config_path}' が見つかりません。")
        return
    except json.JSONDecodeError:
        print(f"エラー: 設定ファイル '{config_path}' のJSON形式が不正です。")
        return

    # ダミーデータを生成 (ここでは過去30日間のデータ)
    today = datetime.now()
    df_kpi = generate_dummy_data(today, 30)

    # グラフの作成
    fig, axes = plt.subplots(len(config['dataConfig']), 1, figsize=(12, 5 * len(config['dataConfig'])), sharex=True)
    if len(config['dataConfig']) == 1: # 項目が1つの場合、axesは一次元配列ではなくなるので調整
        axes = [axes]

    fig.suptitle(config.get("title", "KPIダッシュボード"), fontsize=16, y=1.02)

    for i, kpi_config in enumerate(config['dataConfig']):
        kpi_name = kpi_config['kpiName']
        data_key = kpi_config['dataKey']
        trend_display_type = kpi_config['trendDisplay'] # config.jsonに定義された表示用テキスト

        if data_key not in df_kpi.columns:
            print(f"警告: データキー '{data_key}' がダミーデータに見つかりません。スキップします。")
            continue

        # 最新の数値
        current_value = df_kpi[data_key].iloc[-1]
        
        # 傾向（変化率）の計算
        # trend_typeは内部計算用で、trend_display_typeは表示用テキスト
        trend_type_calc = trend_display_type # 簡単化のため、表示用テキストをそのまま計算タイプとして使用
        trend_percentage = calculate_trend(df_kpi, data_key, trend_type_calc)

        ax = axes[i]
        
        # 時系列折れ線グラフ
        ax.plot(df_kpi.index, df_kpi[data_key], marker='o', linestyle='-', color='skyblue', label=f'{kpi_name} 推移')
        ax.fill_between(df_kpi.index, df_kpi[data_key], color='skyblue', alpha=0.1) # 面積グラフ
        ax.set_ylabel(kpi_name, fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.6)
        
        # y軸のフォーマット（通貨など）
        if "売上高" in kpi_name:
             formatter = mticker.FuncFormatter(format_currency)
             ax.yaxis.set_major_formatter(formatter)
        
        # 最新の数値と傾向をタイトルに追加
        trend_color = 'green' if trend_percentage >= 0 else 'red'
        trend_arrow = '▲' if trend_percentage >= 0 else '▼'
        
        # 数値のフォーマットを調整
        formatted_current_value = f"{current_value:,.0f}" # 整数でカンマ区切り

        ax.set_title(
            f"{kpi_name}: {formatted_current_value} "
            f"(<span style='color:{trend_color};'>{trend_arrow}{trend_percentage:.1f}% {trend_display_type}</span>)", 
            loc='left', fontsize=12
        )
        # matplotlibのタイトルはHTMLタグを直接解釈しないため、
        # ここではテキストとして表示し、色付けは別途アノテーションなどで考慮するが、
        # よりリッチな表現のためにはPlotlyなどのインタラクティブなライブラリが適している。
        # シンプルにテキスト表示のみにする
        ax.set_title(
            f"{kpi_name}: {formatted_current_value} "
            f"({trend_arrow}{trend_percentage:.1f}% {trend_display_type})", 
            loc='left', fontsize=12, color='black' # ここはHTMLタグではなく、テキストとして表示
        )
        
        # 最終データポイントに注釈を追加
        ax.annotate(f'{formatted_current_value}', 
                    (df_kpi.index[-1], current_value), 
                    textcoords="offset points", 
                    xytext=(0,10), 
                    ha='center', 
                    color='blue', 
                    fontsize=9, 
                    weight='bold')

    # X軸のラベルは一番下のグラフにのみ表示
    plt.xlabel("日付", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout(rect=[0, 0.03, 1, 0.98]) # 全体のレイアウト調整 (suptitleと重ならないように)
    
    # 画像として保存
    output_file = config.get("outputFile", "kpi_dashboard.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"ダッシュボードを '{output_file}' に保存しました。")
    plt.close() # メモリ解放

if __name__ == "__main__":
    render_data_viz()
## 使い方

1.  **ファイルの作成**:
    *   上記の`config.json`の内容をコピーし、`config.json`という名前でファイルを作成します。
    *   上記の`data_viz_renderer.py`の内容をコピーし、`data_viz_renderer.py`という名前でファイルを作成します。
    *   両方のファイルを同じディレクトリに保存してください。

2.  **必要なライブラリのインストール**:
    Pythonの実行環境に、以下のライブラリがインストールされていることを確認します。インストールされていない場合は、コマンドプロンプトやターミナルで以下のコマンドを実行してインストールしてください。

    pip install pandas matplotlib numpy
    3.  **スクリプトの実行**:
    コマンドプロンプトやターミナルで、ファイルを作成したディレクトリに移動し、以下のコマンドを実行します。

    python data_viz_renderer.py
    4.  **結果の確認**:
    スクリプトが正常に実行されると、同じディレクトリ内に`kpi_dashboard.png`という名前の画像ファイルが生成されます。このファイルを開いて、自動生成されたKPIダッシュボードを確認してください。

## よくある質問

Q: スクリプトを実行するとエラーが出ます。どうすればよいですか？
A:
1.  **ライブラリのインストール不足**: `pip install pandas matplotlib numpy` コマンドを再度実行し、すべてのライブラリがインストールされているか確認してください。
2.  **`config.json`の形式エラー**: `config.json`ファイルの内容が正しいJSON形式であるか確認してください。特に、カンマの抜けや余分な文字がないか注意してください。
3.  **ファイル名やパスの問題**: `config.json`と`data_viz_renderer.py`が同じディレクトリにあるか、またはスクリプト内の`config_path`が正しく設定されているか確認してください。

Q: グラフのデータソースを自分のデータにしたいです。どうすればよいですか？
A: `data_viz_renderer.py`スクリプト内の`generate_dummy_data`関数を変更するか、別の関数を作成して、CSVファイルやデータベース、APIなどからデータを読み込むように修正してください。読み込んだデータは`pd.DataFrame`形式にし、`data_key`で指定されたカラム名を持つようにしてください。

Q: どのようなグラフが作れますか？他のグラフ種類に変更できますか？
A: 現在のスクリプトでは、各KPIの時系列折れ線グラフと、最新の数値および傾向（変化率）を表示するシンプルなダッシュボード形式で出力されます。
より多様なグラフ（棒グラフ、円グラフなど）やインタラクティブなダッシュボードを作成したい場合は、`matplotlib`の描画関数をさらに活用するか、`Plotly`や`Seaborn`などの別のPython可視化ライブラリを検討してください。`config.json`にグラフタイプを指定するフィールドを追加し、それに基づいてスクリプトが異なる描画ロジックを選択するように拡張することも可能です。

---
AI Conduit: https://www.youtube.com/@AI.Conduit