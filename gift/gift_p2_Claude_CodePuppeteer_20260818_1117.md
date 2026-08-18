# Claude Codeのチャート画像生成でPuppeteer不要の軽量高速グラフ化 - 実践テンプレート

## この動画で学んだこと
この動画では、Claude Codeのチャート画像生成スキルを活用することで、Puppeteerのようなブラウザベースのツールに頼らず、より軽量かつ高速にグラフ画像を生成できるようになったことを学びました。これにより、サーバーリソースの節約や処理速度の向上が期待できます。

## すぐに使えるテンプレート

このテンプレートは、Pythonの`matplotlib`ライブラリを使用して、コマンドラインからデータとタイトルを指定して折れ線グラフのPNG画像を生成するスクリプトです。Claude CodeのCode Interpreter機能で直接実行したり、ご自身のローカル環境で利用したりできます。

### 1. `generate_chart.py` (グラフ生成スクリプト)

# filename: generate_chart.py

import matplotlib.pyplot as plt
import argparse
import os

def generate_chart(data_str: str, title: str, output_filename: str = "chart.png", x_labels: list = None):
    """
    指定されたデータとタイトルに基づいて折れ線グラフを生成し、PNG画像として保存します。

    Args:
        data_str (str): カンマ区切りの数値データ文字列 (例: "10,20,15,30")
        title (str): グラフのタイトル
        output_filename (str): 出力するPNGファイル名 (デフォルト: "chart.png")
        x_labels (list, optional): X軸のラベルリスト。指定しない場合は連番になります。
    """
    try:
        # カンマ区切りの文字列データを数値のリストに変換
        data = [float(d.strip()) for d in data_str.split(',')]
    except ValueError:
        print("エラー: データはカンマ区切りの数値で指定してください。")
        return

    # グラフの作成
    # figsizeで画像サイズを設定 (幅10インチ, 高さ6インチ)
    plt.figure(figsize=(10, 6)) 

    # 折れ線グラフを描画
    # marker='o' でデータ点に丸いマーカーを表示
    # linestyle='-' で線を実線に
    # color='blue' で線の色を青に
    plt.plot(data, marker='o', linestyle='-', color='blue') 

    # グラフのタイトルとラベルを設定
    plt.title(title, fontsize=16) # タイトルを大きく表示
    plt.xlabel("項目", fontsize=12) # X軸ラベル
    plt.ylabel("値", fontsize=12) # Y軸ラベル
    
    # X軸ラベルが指定されている場合、設定する
    if x_labels and len(x_labels) == len(data):
        plt.xticks(range(len(data)), x_labels, rotation=45, ha='right') # X軸のティックとラベルを設定、回転
    elif x_labels and len(x_labels) != len(data):
        print("警告: X軸ラベルの数とデータ数が一致しません。X軸は連番で表示されます。")

    # グリッドの表示 (破線、透明度0.7)
    plt.grid(True, linestyle='--', alpha=0.7) 

    # レイアウトの調整 (ラベルがグラフからはみ出ないように自動調整)
    plt.tight_layout()

    # 出力ディレクトリが存在しない場合、作成する
    output_dir = os.path.dirname(output_filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # グラフをPNGファイルとして保存
    try:
        plt.savefig(output_filename)
        print(f"グラフが '{output_filename}' として正常に保存されました。")
    except Exception as e:
        print(f"エラー: グラフの保存中に問題が発生しました: {e}")

    # メモリ解放のためグラフを閉じる
    plt.close() 

if __name__ == "__main__":
    # コマンドライン引数をパースするための設定
    parser = argparse.ArgumentParser(
        description="Claude Code風のチャート画像を生成するスクリプトです。"
                    "Puppeteer不要で軽量高速なグラフ化を実現します。"
    )
    # --data 引数を必須として追加
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="グラフに表示するカンマ区切りの数値データ (例: '10,20,15,30')"
    )
    # --title 引数を必須として追加
    parser.add_argument(
        "--title",
        type=str,
        required=True,
        help="グラフのタイトル"
    )
    # --output 引数を任意として追加 (デフォルトはchart.png)
    parser.add_argument(
        "--output",
        type=str,
        default="chart.png",
        help="出力するPNGファイル名 (デフォルト: chart.png)"
    )
    # --x_labels 引数を任意として追加 (カンマ区切り文字列)
    parser.add_argument(
        "--x_labels",
        type=str,
        help="X軸のラベルをカンマ区切りで指定 (例: 'Jan,Feb,Mar,Apr')"
    )

    args = parser.parse_args()

    # X軸ラベルが指定されていればリストに変換
    x_labels_list = args.x_labels.split(',') if args.x_labels else None

    # グラフ生成関数を呼び出し
    generate_chart(args.data, args.title, args.output, x_labels_list)

## 使い方

このスクリプトをローカル環境またはClaude Code Interpreterで使用する手順です。

### ローカル環境での使い方

1.  **Pythonとpipの確認**:
    ご自身のPCにPythonがインストールされていることを確認してください。通常、Pythonをインストールするとパッケージ管理ツール`pip`も一緒にインストールされます。
    python --version
    pip --version
    2.  **必要なライブラリのインストール**:
    グラフ描画ライブラリ`matplotlib`をインストールします。
    pip install matplotlib
    3.  **スクリプトの保存**:
    上記のPythonコードを `generate_chart.py` という名前で保存します。

4.  **グラフの生成**:
    コマンドラインから `python` コマンドでスクリプトを実行し、`--data` と `--title` 引数を指定します。`--output` で出力ファイル名を、`--x_labels` でX軸のラベルを指定できます。
    # 基本的な使用例
    python generate_chart.py --data "10,20,15,30,25" --title "月別売上データ" --output "sales_chart.png"

    # X軸ラベルを指定する例
    python generate_chart.py --data "120,150,130,180,160" --title "年間アクセス数" --x_labels "Q1,Q2,Q3,Q4,Q5" --output "access_chart.png"

    # 出力ディレクトリを指定する例 (もし存在しなければ自動で作成されます)
    python generate_chart.py --data "5,8,4,10,7" --title "プロジェクト進捗" --output "output/progress.png"
    実行後、指定したファイル名でPNG画像が生成されます。

### Claude Code Interpreterでの使い方

1.  **Code Interpreterにスクリプトをアップロード**:
    Claude Code Interpreter (またはCode Interpreter機能を持つ他のAIツール) のインターフェースを通じて、上記の `generate_chart.py` スクリプトをアップロードまたは直接貼り付けます。

2.  **実行指示**:
    以下のプロンプトのように、スクリプトを実行するコマンドと、グラフのデータ、タイトル、出力ファイル名を指示します。Claude Codeは必要なライブラリを自動でインストールし、スクリプトを実行してくれます。
    以下のPythonスクリプト `generate_chart.py` を実行してください。
    データは "10,20,15,30,25"、タイトルは "月別売上データ"、出力ファイル名は "sales_chart_claude.png" としてください。
    X軸のラベルは "1月,2月,3月,4月,5月" としてください。

    # (ここに generate_chart.py の内容を貼り付け、またはファイルをアップロードした旨を記述)

    実行コマンド:
    python generate_chart.py --data "10,20,15,30,25" --title "月別売上データ" --x_labels "1月,2月,3月,4月,5月" --output "sales_chart_claude.png"
    Claude Codeがグラフを生成し、結果のPNG画像を提示してくれます。

## よくある質問

**Q1: このスクリプトで他の種類のグラフ（棒グラフ、円グラフなど）も生成できますか？**
A1: はい、可能です。`matplotlib`は非常に多機能なライブラリなので、`plt.plot()`の代わりに`plt.bar()`を使えば棒グラフ、`plt.pie()`を使えば円グラフなど、様々な種類のグラフを生成できます。スクリプトの`generate_chart`関数内部を編集して、目的に応じた`matplotlib`の関数を呼び出すように変更してください。

**Q2: 複数系列のデータを一つのグラフに表示したい場合はどうすればよいですか？**
A2: 現在のスクリプトは単一のデータ系列に対応しています。複数系列を扱う場合は、`--data`引数の形式を工夫するか、引数を増やして複数のデータセットを受け取るようにスクリプトを拡張する必要があります。例えば、JSON形式のデータを受け取るようにしたり、`--data1 "1,2,3"`、`--data2 "4,5,6"` のように複数の引数を定義する方法が考えられます。

**Q3: 生成される画像のサイズや解像度を変更できますか？**
A3: はい、変更できます。`plt.figure(figsize=(10, 6))` の `figsize` 引数で画像の幅と高さをインチ単位で指定できます。また、`plt.savefig()` メソッドに `dpi` (dots per inch) 引数を追加することで、解像度を調整できます。例えば `plt.savefig(output_filename, dpi=300)` とすると、より高解像度の画像が生成されます。

---
AI Conduit: https://www.youtube.com/@AI.Conduit