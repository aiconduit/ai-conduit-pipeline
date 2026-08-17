# Claude CodeのTimeline Builderでタイムラインのレイアウトが自在になった - 実践テンプレート

## この動画で学んだこと
Claude CodeのTimeline Builderを使用し、コマンドラインオプションでタイムラインのレイアウトを動的に変更する方法を学びました。特に、設定ファイルで定義された内容をコマンドラインから上書きすることで、柔軟なタイムライン生成が可能になります。

## すぐに使えるテンプレート

まずは、タイムラインの元となるイベントデータと、基本的な設定ファイルを作成します。

### 1. `events.json` (タイムラインイベントデータ)

[
  {
    "id": "event_a",
    "title": "プロジェクトキックオフ",
    "start_date": "2023-01-01",
    "end_date": "2023-01-01",
    "description": "プロジェクトの初期ミーティングを実施",
    "category": "開始"
  },
  {
    "id": "event_b",
    "title": "フェーズ1完了",
    "start_date": "2023-03-15",
    "end_date": "2023-03-15",
    "description": "要件定義と基本設計が完了",
    "category": "マイルストーン"
  },
  {
    "id": "event_c",
    "title": "中間レビュー",
    "start_date": "2023-06-01",
    "end_date": "2023-06-01",
    "description": "進捗状況の共有とフィードバック",
    "category": "レビュー"
  },
  {
    "id": "event_d",
    "title": "最終リリース",
    "start_date": "2023-09-30",
    "end_date": "2023-09-30",
    "description": "製品の正式リリース",
    "category": "完了"
  },
  {
    "id": "event_e",
    "title": "顧客トレーニング",
    "start_date": "2023-10-15",
    "end_date": "2023-10-15",
    "description": "新製品の顧客向けトレーニング",
    "category": "サポート"
  }
]
### 2. `config.yaml` (タイムライン生成設定ファイル)

# タイムライン生成の基本設定ファイル
title: "プロジェクトX 開発タイムライン" # タイムラインのメインタイトル
description: "主要なマイルストーンとイベントを視覚化" # タイムラインの説明文
output_format: "png" # 出力フォーマット (例: png, svg, pdf)
output_filename: "timeline_output" # 出力ファイル名 (拡張子を除く)
layout: "portrait" # デフォルトのレイアウトモード (portrait: 縦向き, landscape: 横向き)
date_format: "%Y/%m/%d" # 日付の表示フォーマット (例: YYYY/MM/DD)
start_date: "2023-01-01" # タイムラインの表示開始日 (オプション)
end_date: "2023-12-31" # タイムラインの表示終了日 (オプション)

# フォント設定
font:
  family: "Noto Sans JP" # 使用するフォントファミリー (システムにインストールされているもの)
  size: 12 # 基本フォントサイズ

# 色設定 (例: カテゴリごとの色分け)
colors:
  開始: "#FFD700" # ゴールド
  マイルストーン: "#4682B4" # スチールブルー
  レビュー: "#DAA520" # ゴールデンロッド
  完了: "#228B22" # フォレストグリーン
  サポート: "#8B0000" # ダークレッド
  # その他のカテゴリを追加可能
### 3. コマンドライン実行例

# Claude Code Timeline Builderのコマンド名 (仮称)
# --config: 設定ファイルを指定するオプション
# --data: タイムラインの元となるイベントデータを指定するオプション
# --output: 出力ファイル名を指定するオプション (config.yaml内の設定を上書き可能)

# 1. デフォルト設定 (縦向き) でタイムラインを生成
#    config.yamlで指定された 'portrait' レイアウトが適用されます。
echo "デフォルト設定 (縦向き) でタイムラインを生成中..."
timeline-builder --config config.yaml --data events.json --output timeline_portrait.png
echo "→ timeline_portrait.png が生成されました。"

# 2. レイアウトモードを横向きに変更してタイムラインを再生成
#    --layout オプションがconfig.yamlのlayout設定よりも優先されます。
echo "レイアウトを横向きに変更してタイムラインを再生成中..."
timeline-builder --config config.yaml --data events.json --layout landscape --output timeline_landscape.png
echo "→ timeline_landscape.png が生成されました。"

# 3. ヘルプメッセージの表示 (利用可能なオプションを確認)
#    -h または --help オプションでコマンドのヘルプ情報を確認できます。
echo "利用可能なオプションを確認するには:"
timeline-builder --help
## 使い方

1.  **Claude Code Timeline Builderをインストール**:
    *   (仮にPythonベースのツールと想定) `pip install claude-timeline-builder` など、公式ドキュメントに従ってツールをインストールしてください。
2.  **イベントデータファイルを作成**: 上記の `events.json` テンプレートを参考に、あなたのタイムラインに必要なイベント情報を記述し、`events.json`という名前で保存します。
3.  **設定ファイルを作成**: 上記の `config.yaml` テンプレートを参考に、タイムラインのタイトル、出力形式、デフォルトのレイアウトなどの表示設定を記述し、`config.yaml`という名前で保存します。
4.  **デフォルト設定でタイムラインを生成**:
    *   ターミナルを開き、`events.json`と`config.yaml`を保存したディレクトリに移動します。
    *   以下のコマンドを実行し、デフォルト設定（`config.yaml`で指定した`portrait`レイアウト）でタイムライン画像を生成します。
        timeline-builder --config config.yaml --data events.json --output timeline_portrait.png
        *   `timeline_portrait.png`というファイルが生成され、縦向きのタイムラインになっていることを確認してください。
5.  **レイアウトを横向きに変更してタイムラインを再生成**:
    *   以下のコマンドを実行し、コマンドラインオプションでレイアウトを`landscape`（横向き）に上書きしてタイムライン画像を再生成します。
        timeline-builder --config config.yaml --data events.json --layout landscape --output timeline_landscape.png
        *   `timeline_landscape.png`というファイルが生成され、横向きのタイムラインになっていることを確認してください。

## よくある質問

**Q: 他のレイアウトモードや詳細なオプションはありますか？**
A: `timeline-builder --help` コマンドを実行すると、利用可能なすべてのオプションと説明が表示されます。ツールによっては、`--layout` の他に `portrait`, `landscape`, `auto` などの値が指定できる場合や、詳細な余白やスケール設定のオプションが用意されていることがあります。

**Q: 設定ファイル (`config.yaml`) とコマンドラインオプションで同じ項目を指定した場合、どちらが優先されますか？**
A: 一般的に、コマンドラインオプションで指定された値が設定ファイルよりも優先されます。これは、一時的な変更や特定の用途のために、基本設定を上書きする便利な方法です。

**Q: 生成されるタイムラインの出力形式を変更できますか？**
A: はい、`config.yaml` の `output_format` や、コマンドラインオプションの `--output-format` (ツールによって異なる場合があります) を使って、`png`, `svg`, `pdf` などの異なる形式を指定できる場合があります。必要に応じて設定を変更してください。

---
AI Conduit: https://www.youtube.com/@AI.Conduit