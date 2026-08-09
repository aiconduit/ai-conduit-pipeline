# Claude Codeで財務分析を自動化する方法 - 実践テンプレート

## この動画で学んだこと
Claude Codeの**Financial Data Analyst**テンプレートを使えば、複雑な財務データ分析をAIが自動化してくれます。わずか2つのコマンドで環境構築が完了し、高度な財務分析をすぐに始められます。

## すぐに使えるテンプレート

### 1. 環境構築（ターミナルで実行）

```bash
# ステップ1: anthropic-quickstartsリポジトリをクローン
git clone https://github.com/anthropics/anthropic-quickstarts

# ステップ2: 財務分析ディレクトリに移動
cd financial-data-analyst

# ステップ3: 環境変数ファイルを作成
cp .env.example .env

# ステップ4: .envファイルにAPIキーを設定（エディタで開いて編集）
# nano .env または vim .env で開き、以下を設定:
# ANTHROPIC_API_KEY=あなたのAPIキーをここに入力
```

### 2. .envファイル設定例

```env
# Anthropic API設定
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 必要に応じて追加設定
# デフォルトのモデル設定
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# 出力ディレクトリ設定
OUTPUT_DIR=./output
```

### 3. 財務分析の実行コマンド

```bash
# 基本的な財務分析を実行
claude -p "2023年度の財務諸表を分析し、収益性・安全性・成長性の観点から評価してください"

# CSVデータを読み込んで分析
claude -p "売上データ.csvを分析し、月次のトレンドと異常値を特定してください"

# レポート生成
claude -p "過去3年間のバランスシートを比較し、財務健全性の変化をレポートにまとめてください"
```

### 4. カスタム分析プロンプトテンプレート

```bash
# 財務比率分析
claude -p "
以下の財務指標を計算し、業界平均と比較してください：
1. 流動比率（流動資産 ÷ 流動負債）
2. 自己資本比率（自己資本 ÷ 総資産）
3. ROE（当期純利益 ÷ 自己資本）
4. 売上高成長率

データソース: 財務諸表.xlsx
"

# 投資判断サポート
claude -p "
以下の企業の財務データを分析し、投資判断のためのレポートを作成：
- 売上高の推移
- 利益率の変化
- キャッシュフローの状況
- 負債構造

リスク要因と成長機会を特定してください。
"
```

## 使い方

1. **ターミナルを開き、上記の環境構築コマンドを順番に実行**します
2. **.envファイルにAnthropic APIキーを設定**します（APIキーはAnthropicコンソールから取得）
3. **分析したい財務データを準備**します（CSV、Excel、PDFなど）
4. **`claude -p`コマンドで分析を実行**し、結果を確認します
5. **必要に応じてプロンプトをカスタマイズ**し、より詳細な分析を行います

## よくある質問

**Q: APIキーはどこで取得できますか？**
A: [Anthropic Console](https://console.anthropic.com/)にアクセスし、アカウントを作成後、API Keysセクションから取得できます。初回は無料クレジットが付与されます。

**Q: エラー「command not found: claude」が表示される場合**
A: Claude Code CLIがインストールされていません。`npm install -g @anthropic-ai/claude-code` を実行してインストールしてください。

**Q: 日本語の財務データも分析できますか？**
A: はい、可能です。Claudeは多言語対応しており、日本語の財務諸表やレポートも分析できます。プロンプトを日本語で記述すれば、日本語で結果を出力します。

**Q: 大容量のデータファイルは扱えますか？**
A: 基本的には可能ですが、ファイルサイズが大きすぎる場合は事前に必要なデータのみに絞り込むことをお勧めします。また、機密データを扱う場合は、セキュリティに注意してください。

---
AI Conduit: https://www.youtube.com/@AI.Conduit