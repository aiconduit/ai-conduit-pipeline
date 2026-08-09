# Claude Codeで財務分析を自動化する方法 - 実践テンプレート

## この動画で学んだこと
Claude Codeの**Financial Data Analyst**テンプレートを使えば、複雑な財務データ分析をAIが自動化してくれます。わずか2つのコマンドで環境構築が完了し、高度な財務分析をすぐに始められます。

## すぐに使えるテンプレート

### 1. 環境構築（ターミナルで実行）

```bash
# ステップ1: anthropic-quickstartsリポジトリをクローン
$ git clone https://github.com/anthropics/anthropic-quickstarts

# ステップ2: Financial Data Analystディレクトリに移動
$ cd financial-data-analyst

# ステップ3: 環境変数ファイルを作成
$ cp .env.example .env

# ステップ4: .envファイルを編集してAPIキーを設定
$ nano .env  # または任意のエディタで開く
```

### 2. .envファイルの設定

```env
# Anthropic APIキーを設定（必須）
ANTHROPIC_API_KEY=sk-ant-あなたのAPIキーをここに入力

# 必要に応じてモデルを変更（デフォルトはclaude-3-5-sonnet）
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# 財務データのソース（デフォルトはYahoo Finance）
DATA_SOURCE=yahoo_finance
```

### 3. 依存関係のインストール

```bash
# Pythonパッケージをインストール
$ pip install -r requirements.txt

# またはnpmを使用する場合
$ npm install
```

### 4. 財務分析の実行

```bash
# 基本的な財務分析を実行
$ python financial_analyst.py --ticker AAPL

# 複数の企業を比較分析
$ python financial_analyst.py --tickers AAPL,MSFT,GOOGL

# 特定の期間で分析
$ python financial_analyst.py --ticker AAPL --period 1y

# レポートをファイルに出力
$ python financial_analyst.py --ticker AAPL --output report.md
```

### 5. カスタム分析プロンプトの例

```python
# custom_analysis.py
"""
Claude Codeを使ったカスタム財務分析スクリプト
"""
import os
from anthropic import Anthropic

# APIクライアントの初期化
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def analyze_financials(ticker: str, metrics: list):
    """指定された財務指標を分析する関数"""
    
    prompt = f"""
    あなたは財務アナリストです。{ticker}の以下の指標を分析してください：
    {', '.join(metrics)}
    
    分析結果を以下の形式で出力してください：
    1. 現在の値
    2. 前年比
    3. 業界平均との比較
    4. 投資判断への示唆
    """
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text

# 使用例
if __name__ == "__main__":
    result = analyze_financials(
        ticker="AAPL",
        metrics=["PER", "ROE", "売上高成長率", "営業利益率"]
    )
    print(result)
```

## 使い方

1. **リポジトリのクローン**: ターミナルで`git clone`コマンドを実行し、プロジェクトをローカルにコピーします
2. **APIキーの設定**: `.env`ファイルにAnthropic APIキーを設定します（[console.anthropic.com](https://console.anthropic.com)から取得可能）
3. **依存関係のインストール**: `pip install -r requirements.txt`で必要なパッケージをインストールします
4. **分析の実行**: `python financial_analyst.py --ticker 企業コード`で分析を開始します
5. **結果の確認**: 生成されたレポートを確認し、必要に応じてカスタマイズします

## よくある質問

**Q: APIキーはどこで取得できますか？**
A: [Anthropic Console](https://console.anthropic.com)にサインアップし、API Keysセクションから取得できます。初回は無料クレジットが付与されます。

**Q: 分析できる企業は米国株のみですか？**
A: デフォルトではYahoo Financeを使用するため、世界中の主要な上場企業を分析できます。日本株の場合はティッカーコードに`.T`を付けてください（例: 7203.T）。

**Q: エラー「API key not found」が表示される場合の対処法は？**
A: `.env`ファイルが正しい場所にあるか確認し、`ANTHROPIC_API_KEY=`の後にスペースを入れずにキーを記入してください。また、`.env`ファイルが`.gitignore`に含まれているか確認しましょう。

**Q: 分析結果をExcelやCSVで出力できますか？**
A: はい、`--output`オプションでファイル形式を指定できます。例：`--output report.csv`または`--output report.xlsx`

**Q: 大量のデータを分析する場合のコストは？**
A: 使用量に応じた従量課金制です。小規模な分析は数セント程度ですが、大量のデータ処理にはコストがかかるため、APIの使用量をモニタリングすることをお勧めします。

---
AI Conduit: https://www.youtube.com/@AI.Conduit