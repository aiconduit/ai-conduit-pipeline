# Claude Codeのチャート機能で画像生成が高速になった - 実践テンプレート

## この動画で学んだこと
この動画では、Claude Code (Code Interpreter) のチャート機能を利用して、Pythonスクリプトでデータからグラフ画像を生成する方法を学びました。Claudeの強力なコード実行能力と対話性を活用することで、データ分析から視覚化までのプロセスを効率的に、かつ高速に進めることが可能になります。

## すぐに使えるテンプレート

### 1. 必要なライブラリのインストールコマンド
グラフ描画に必要な `matplotlib` ライブラリをインストールします。

# Matplotlibライブラリをインストールします。
# グラフ描画のために広く使われる、Pythonの標準的なライブラリです。
pip install matplotlib
### 2. グラフ生成Pythonスクリプト (`generate_chart.py`)
このスクリプトは、与えられたデータからシンプルな棒グラフを作成し、PNG画像として保存します。

import matplotlib.pyplot as plt
import os

# グラフのデータ定義
# ここに可視化したいデータを設定します
categories = ['売上', '費用', '利益', 'マーケティング', '研究開発']
values = [150, 80, 70, 40, 30]

# グラフの設定
plt.figure(figsize=(10, 6)) # グラフの全体サイズを幅10インチ、高さ6インチに設定
plt.bar(categories, values, color=['skyblue', 'lightcoral', 'lightgreen', 'gold', 'thistle']) # 棒グラフを作成し、色を個別に指定
plt.xlabel('項目') # X軸のラベルを設定
plt.ylabel('金額 (百万円)') # Y軸のラベルを設定
plt.title('2023年度 主要項目別データ') # グラフのタイトルを設定
plt.grid(axis='y', linestyle='--', alpha=0.7) # Y軸にグリッド線を追加し、スタイルと透明度を設定
plt.xticks(rotation=45, ha='right') # X軸のラベルを45度回転させ、右寄せで表示
plt.tight_layout() # レイアウトを自動調整し、ラベルが重ならないようにする

# 画像ファイルの保存先パスを決定
# Claude Code Interpreter環境では、通常 '/mnt/data/' が書き込み可能ディレクトリとして推奨されます。
# ローカル環境で実行する場合は、スクリプトと同じディレクトリに保存されます。
output_dir = os.environ.get('OUTPUT_DIR', '.') # 環境変数 'OUTPUT_DIR' があればそれを使用、なければ現在のディレクトリ
output_filename = os.path.join(output_dir, '2023_financial_data_chart.png')

# グラフを画像ファイルとして保存
plt.savefig(output_filename)
print(f"グラフが '{output_filename}' に保存されました。")

# （Claude Code Interpreterの場合）
# ClaudeのUIは通常、生成されたファイルを自動的に検出・表示しますが、
# プロンプトで明示的に表示を要求することで確実性が高まります。
### 3. Claude Codeへのプロンプト例
Claude Code Interpreterで上記のスクリプトを実行し、グラフ画像を生成させるためのプロンプトです。

以下の手順に従って、データ可視化のためのグラフ画像を生成してください。

**手順:**
1. Pythonスクリプト `generate_chart.py` を作成し、提供されたコードを記述してください。
2. 必要なライブラリ `matplotlib` をインストールしてください（`pip install matplotlib`）。
3. `generate_chart.py` スクリプトを実行してください。
4. 生成された画像ファイル `2023_financial_data_chart.png` の内容を表示してください。

**generate_chart.py:**
import matplotlib.pyplot as plt
import os

categories = ['売上', '費用', '利益', 'マーケティング', '研究開発']
values = [150, 80, 70, 40, 30]

plt.figure(figsize=(10, 6))
plt.bar(categories, values, color=['skyblue', 'lightcoral', 'lightgreen', 'gold', 'thistle'])
plt.xlabel('項目')
plt.ylabel('金額 (百万円)')
plt.title('2023年度 主要項目別データ')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

output_dir = os.environ.get('OUTPUT_DIR', '.')
output_filename = os.path.join(output_dir, '2023_financial_data_chart.png')

plt.savefig(output_filename)
print(f"グラフが '{output_filename}' に保存されました。")
## 使い方
1.  **Python環境の準備**:
    *   **Claude Code Interpreterを使用する場合**: 特別な準備は不要です。Claude 3 (Opus/Sonnet) のCode Interpreter機能が有効なチャットを開いてください。
    *   **ローカル環境で実行する場合**: お使いのPCにPythonがインストールされていることを確認してください。
2.  **ライブラリのインストール**:
    *   上記の「1. 必要なライブラリのインストールコマンド」にある `pip install matplotlib` をターミナル（またはコマンドプロンプト）で実行し、必要なライブラリをインストールします。
    *   Claude Code Interpreterを使用する場合は、後述のプロンプト内でインストールを指示しますので、この手順は不要です。
3.  **スクリプトの準備**:
    *   上記の「2. グラフ生成Pythonスクリプト」の内容をコピーし、`generate_chart.py` という名前でテキストファイルに保存します。
4.  **実行**:
    *   **Claude Code Interpreterで実行する場合**:
        *   Claude 3 (Opus/Sonnet) のCode Interpreter機能が有効なチャットを開きます。
        *   上記の「3. Claude Codeへのプロンプト例」をコピーし、Claudeにペーストして送信します。
        *   Claudeは指示に従ってライブラリをインストールし、スクリプトを実行し、生成されたグラフ画像 (`2023_financial_data_chart.png`) を表示してくれるはずです。
    *   **ローカル環境で実行する場合**:
        *   ターミナルを開き、`generate_chart.py` を保存したディレクトリに移動します。
        *   `python generate_chart.py` コマンドを実行します。
        *   スクリプトが正常に実行されると、同じディレクトリに `2023_financial_data_chart.png` という画像ファイルが生成されます。

## よくある質問
Q: どんな種類の画像を生成できますか？
A: Claude Code (Code Interpreter) は、Pythonなどのプログラミング言語とグラフ描画ライブラリ（Matplotlib, Seaborn, Plotlyなど）を利用して、主にデータ可視化のためのグラフや図を生成するのに適しています。棒グラフ、折れ線グラフ、散布図、ヒストグラム、円グラフなどが含まれます。DALL-Eのような生成AIとは異なり、直接的に写真のようなリアルな画像や複雑なイラストを生成することはできません。

Q: Claude Codeを使うメリットは何ですか？
A:
*   **環境構築不要**: ローカル環境に特定のライブラリをインストールする手間を省き、クラウド上で直接コードを実行できます。
*   **対話的分析**: データ分析の途中で、コードの変更や結果の確認を対話形式で効率的に進められます。
*   **エラー修正支援**: コード実行時にエラーが発生した場合、Claudeがエラーメッセージを理解し、修正案を提案してくれることがあります。
*   **コード生成**: グラフの種類やデータの要件を指示するだけで、Claudeが適切なPythonコードを生成してくれることも期待できます。

Q: どんなデータ形式をClaudeに渡せばいいですか？
A: Pythonで扱いやすい形式であれば何でも可能です。一般的なものとしては、スクリプト内で直接定義するリストや辞書、JSON形式のテキスト、CSV形式のテキストデータなどがあります。より複雑なデータの場合は、Claudeにファイルとしてアップロードし、スクリプト内でそのファイルを読み込むように指示することも可能です。

---
AI Conduit: https://www.youtube.com/@AI.Conduit