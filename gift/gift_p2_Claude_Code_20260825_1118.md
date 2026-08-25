# Claude Codeによる高速グラフ生成 - 実践テンプレート

## この動画で学んだこと
この動画では、Claude AIのコード生成能力を活用して、グラフやチャートを高速に作成する方法を紹介しています。必要なデータを準備し、適切なプロンプトを与えることで、煩雑なグラフ描画コードを手動で書く手間を省き、効率的なデータ可視化を実現します。

## すぐに使えるテンプレート

ここでは、Claude AIにグラフ描画用のPythonコードを生成させ、それを実行する一連のワークフローをテンプレートとして提供します。

### 1. 必要なパッケージのインストール

グラフ描画にはPythonの`matplotlib`ライブラリを使用します。日本語表示に対応するために`japanize_matplotlib`もインストールします。

# まず、プロジェクト用のディレクトリを作成し、移動します
# このディレクトリを「スキルフォルダ」と見立てて作業を進めます
mkdir claude_chart_skill
cd claude_chart_skill

# 必要なPythonパッケージをインストールします
# pandasはデータの準備によく使うため、含めています
pip install matplotlib pandas japanize_matplotlib
### 2. Claude AIへのプロンプト例（グラフ生成Pythonコードの作成依頼）

以下のプロンプトをClaude AIに渡して、グラフ描画用のPythonコードを生成してもらいます。

あなたはデータ分析とグラフ作成のエキスパートです。
以下のデータを使って、棒グラフを描画するPythonコードを作成してください。

データ:
Category,Value
A,25
B,40
C,30
D,55

要件:
- matplotlibライブラリを使用すること。
- グラフのタイトルを「サンプル棒グラフ」とすること。
- X軸ラベルを「カテゴリー」、Y軸ラベルを「値」とすること。
- グラフを 'sample_chart.png' というファイル名で保存すること。
- 日本語表示に対応するため、`japanize_matplotlib`をimportし、適切な設定をすること。
- グラフを表示する`plt.show()`はコメントアウトしてください。
### 3. Claude AIが生成するであろうPythonコードの例

上記プロンプトに基づいてClaude AIが生成する、実行可能なPythonコードの例です。
これを `generate_chart.py` などのファイル名で保存します。

import matplotlib.pyplot as plt
import pandas as pd
import japanize_matplotlib # 日本語表示に対応するためのライブラリ

# データを用意
# Claude AIに与えたデータを使用します
data = {
    'Category': ['A', 'B', 'C', 'D'],
    'Value': [25, 40, 30, 55]
}
df = pd.DataFrame(data)

# グラフのタイプを指定して描画 (棒グラフ)
plt.figure(figsize=(8, 6)) # グラフのサイズを設定
plt.bar(df['Category'], df['Value'], color='skyblue') # 棒グラフを作成

# グラフの装飾
plt.xlabel('カテゴリー', fontsize=12) # X軸ラベル
plt.ylabel('値', fontsize=12)       # Y軸ラベル
plt.title('サンプル棒グラフ', fontsize=14) # グラフタイトル
plt.grid(axis='y', linestyle='--', alpha=0.7) # Y軸にグリッド線を追加

# レイアウトの調整
plt.tight_layout()

# グラフを画像ファイルとして保存
# プロンプトで指定したファイル名 'sample_chart.png' で保存
output_path = 'sample_chart.png'
plt.savefig(output_path)
print(f"グラフが '{output_path}' に保存されました。")

# 画面に表示する場合は以下のコメントを外してください
# plt.show()
### 4. グラフ生成コマンドの実行

保存したPythonスクリプトを実行して、グラフ画像を生成します。

# Pythonスクリプトを実行します
python generate_chart.py
## 使い方
1.  **環境構築**: まず、上記「1. 必要なパッケージのインストール」のコマンドを実行し、Python環境を準備します。これにより、`matplotlib`や`pandas`などのライブラリが使えるようになります。
2.  **プロンプトの入力**: 上記「2. Claude AIへのプロンプト例」をコピーし、Claude AIのチャットインターフェースに貼り付けて、Pythonコードの生成を依頼します。
3.  **コードの保存**: Claude AIが生成したPythonコード（上記「3. Claude AIが生成するであろうPythonコードの例」のようなもの）をコピーし、先ほど作成した `claude_chart_skill` ディレクトリ内に `generate_chart.py` といった名前で保存します。
4.  **スクリプトの実行**: ターミナルで `claude_chart_skill` ディレクトリに移動した状態で、上記「4. グラフ生成コマンドの実行」のコマンド (`python generate_chart.py`) を実行します。
5.  **結果の確認**: コマンド実行後、`claude_chart_skill` ディレクトリ内に `sample_chart.png` という画像ファイルが生成されていることを確認してください。

## よくある質問
Q: **Claude Code**とは具体的に何を指しますか？
A: ここでの「Claude Code」は、Anthropic社が開発したAIモデルClaudeに、プログラミングコード（特にPythonコード）を生成させる能力、またはその能力を活用したワークフローを指します。動画では、この能力を使ってグラフ描画コードを生成し、高速にグラフを作成する手法が紹介されました。

Q: どんな種類のグラフでも生成できますか？
A: Claude AIの理解度と、利用可能なPythonライブラリ（matplotlib, seaborn, plotlyなど）の機能によります。基本的な棒グラフ、折れ線グラフ、散布図、円グラフなどは得意ですが、非常に複雑なカスタムグラフやインタラクティブなグラフは、より詳細なプロンプトや手動での調整が必要になる場合があります。

Q: グラフに使うデータはどのように渡せば良いですか？
A: プロンプト内で直接CSV形式やJSON形式でデータを記述する方法（今回の例）、外部ファイルのパスを指定してそのファイルを読み込ませる方法、あるいはデータベースやAPIからデータを取得するコードをClaudeに書かせる方法などがあります。目的に応じて最適な方法を選択してください。

Q: 日本語が表示されません。どうすれば良いですか？
A: 日本語フォントがインストールされていない環境や、`japanize_matplotlib`が正しく機能していない可能性があります。`japanize_matplotlib`をインストールし、スクリプト内で正しくインポートされているか確認してください。また、環境によっては特定の日本語フォントを別途インストールする必要がある場合があります。

---
AI Conduit: https://www.youtube.com/@AI.Conduit