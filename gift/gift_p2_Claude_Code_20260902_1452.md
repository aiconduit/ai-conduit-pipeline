# Claude Codeのタイムライン表示が自在になった - 実践テンプレート

## この動画で学んだこと
この動画では、Claude Codeの作業履歴（タイムライン）表示を、コマンドラインオプションを使って柔軟にカスタマイズする方法が紹介されました。特に、`layout`オプションに`horizontal`を指定することで、タイムラインを横スクロール表示に切り替えられることが示されています。

## すぐに使えるテンプレート

動画で言及されている「タイムライン生成コマンド」は、ユーザーがClaude Code（AnthropicのClaude AIを活用したコード生成・分析プロセス）の履歴を可視化するために用いる、独自のスクリプトやツールを指していると考えられます。ここでは、その概念をPythonスクリプトとして具体化し、`--layout`オプションで表示形式を変更できる汎用的なテンプレートを提供します。

まず、以下の内容で `timeline_generator.py` というファイルを作成してください。

import argparse
import os

def generate_timeline(data_source: str, layout: str = "vertical", output_file: str = "claude_timeline.html"):
    """
    Claude Codeのタイムラインを生成するダミー関数。
    実際のデータ処理やHTML生成はここで行われます。
    """
    print(f"--- タイムライン生成開始 ---")
    print(f"データソース: {data_source}")
    print(f"指定されたレイアウト: {layout}")
    print(f"出力ファイル: {output_file}")

    # ここに実際のタイムライン生成ロジックを記述します。
    # 例: Claudeとの対話履歴をパースし、指定されたレイアウトでHTMLを生成
    # ------------------------------------------------------------------
    # 以下は、レイアウトオプションに基づいてスタイルが変化する簡単なHTML生成例です。
    # 実際のClaudeの出力履歴を反映させるには、別途データ処理が必要です。
    html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Code タイムライン ({layout})</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f0f2f5; color: #333; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        p {{ line-height: 1.6; }}
        .timeline-container {{
            display: flex;
            {"flex-direction: row; overflow-x: auto; white-space: nowrap; padding-bottom: 15px;" if layout == "horizontal" else "flex-direction: column;"}
            border: 1px solid #dcdcdc;
            padding: 15px;
            border-radius: 8px;
            background-color: #ffffff;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            gap: 15px; /* アイテム間の間隔 */
        }}
        .timeline-item {{
            border: 1px solid #e0e0e0;
            padding: 15px;
            border-radius: 6px;
            background-color: #fdfdfd;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            min-width: 300px; /* 横スクロール時のアイテム最小幅 */
            flex-shrink: 0; /* 横スクロール時にアイテムが縮まないように */
        }}
        .item-header {{ font-weight: bold; margin-bottom: 8px; color: #34495e; font-size: 1.1em; }}
        .item-body {{ font-size: 0.95em; color: #666; }}
        .timestamp {{ font-size: 0.8em; color: #999; margin-top: 5px; text-align: right; }}
    </style>
</head>
<body>
    <h1>Claude Code タイムライン</h1>
    <p>現在のレイアウト: <strong>{layout}</strong></p>
    <div class="timeline-container">
        <div class="timeline-item">
            <div class="item-header">ステップ 1: プロジェクト要件定義</div>
            <div class="item-body">Claudeに「PythonとFastAPIを使ったTODOアプリの要件」について相談し、初期設計案を作成しました。</div>
            <div class="timestamp">2023-10-26 09:30</div>
        </div>
        <div class="timeline-item">
            <div class="item-header">ステップ 2: APIエンドポイント設計</div>
            <div class="item-body">TODOリストのCRUD操作に対応するAPIエンドポイントのコードスニペットをClaudeに生成させました。</div>
            <div class="timestamp">2023-10-26 10:15</div>
        </div>
        <div class="timeline-item">
            <div class="item-header">ステップ 3: データベース連携</div>
            <div class="item-body">PostgreSQLとの連携方法とSQLAlchemyのモデル定義について、Claudeから具体的なアドバイスを受け実装しました。</div>
            <div class="timestamp">2023-10-26 11:00</div>
        </div>
        <div class="timeline-item">
            <div class="item-header">ステップ 4: テストコード実装</div>
            <div class="item-body">生成されたAPIエンドポイントに対するpytestを利用したユニットテストコードをClaudeに依頼し、レビューを受けました。</div>
            <div class="timestamp">2023-10-26 13:30</div>
        </div>
        <div class="timeline-item">
            <div class="item-header">ステップ 5: ドキュメント生成</div>
            <div class="item-body">FastAPIのOpenAPIドキュメントを基に、API仕様書のドラフトをClaudeに作成させました。</div>
            <div class="timestamp">2023-10-26 14:45</div>
        </div>
    </div>
    <p>タイムラインが '<a href="{output_file}" target="_blank">{output_file}</a>' に出力されました。</p>
</body>
</html>
"""
    # ------------------------------------------------------------------

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"タイムラインが '{output_file}' に正常に出力されました。")
    except IOError as e:
        print(f"エラー: ファイル '{output_file}' への書き込みに失敗しました: {e}")

    print(f"--- タイムライン生成終了 ---")

def main():
    parser = argparse.ArgumentParser(
        description="Claude Codeのタイムラインを生成するツール。",
        formatter_class=argparse.RawTextHelpFormatter # ヘルプメッセージの整形を保持
    )
    # タイムライン生成の元となるデータソース（ここではダミー）
    parser.add_argument(
        "data_source",
        help="タイムライン生成に使用するデータソースのパスまたは識別子。\n"
             "例: 'claude_chat_history.json' や 'project_log_id_123'"
    )
    # レイアウトを指定するオプション
    parser.add_argument(
        "--layout",
        type=str,
        default="vertical", # デフォルトは垂直スクロール
        choices=["vertical", "horizontal", "grid"], # 選択可能なレイアウトオプション
        help="タイムラインの表示レイアウトを指定します。\n"
             "  - vertical: 垂直スクロール (デフォルト)\n"
             "  - horizontal: 横スクロール\n"
             "  - grid: グリッド表示 (このテンプレートではダミー実装)"
    )
    # 出力ファイル名を指定するオプション
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="claude_timeline.html",
        help="出力するHTMLファイルの名前とパス。"
    )

    args = parser.parse_args()

    generate_timeline(args.data_source, args.layout, args.output)

if __name__ == "__main__":
    main()

## 使い方

1.  **ファイルの保存:**
    上記のPythonコードを `timeline_generator.py` という名前で保存します。

2.  **コマンドの実行:**
    ターミナル（コマンドプロンプト）を開き、`timeline_generator.py` を保存したディレクトリに移動します。

    *   **デフォルト（垂直スクロール）でタイムラインを生成する場合:**
        python timeline_generator.py "my_claude_project_log"
        `"my_claude_project_log"` の部分は、実際にタイムライン生成の元となるデータソース名やパスを想定しています。（このテンプレートではダミーデータが使われます。）

    *   **動画で紹介された横スクロールでタイムラインを生成する場合:**
        python timeline_generator.py "my_claude_project_log" --layout horizontal
        *   **出力ファイル名を指定する場合:**
        python timeline_generator.py "my_claude_project_log" --layout horizontal -o custom_timeline.html
        3.  **結果の確認:**
    コマンドを実行すると、指定されたディレクトリに `claude_timeline.html` (または`-o`で指定したファイル名) が生成されます。このファイルをウェブブラウザで開くことで、生成されたタイムライン表示を確認できます。`--layout horizontal` を指定した場合は、横スクロール可能なタイムラインが表示されます。

## よくある質問

**Q: `layout`オプションには他に何を指定できますか？**
A: このテンプレートの例では `vertical` (垂直スクロール、デフォルト)、`horizontal` (横スクロール)、`grid` (グリッド表示) の3つをサポートしています。ただし、`grid`は現在のところダミーの実装です。実際のツールでは、`compact`や`expanded`など、さらに多様な表示オプションが提供される可能性があります。

**Q: このコマンドはどのような「タイムライン生成コマンド」を想定していますか？**
A: 動画では具体的なツール名が明示されていませんが、AI Conduitチャンネルの内容から、Claude AIとの対話履歴や、LangChain/AutoGenなどのLLMエージェントフレームワークの実行ログを可視化するツールを想定していると考えられます。本テンプレートは、そのようなツールがコマンドライン引数でレイアウトを制御する一般的な方法を模倣したものです。

**Q: Claude Codeとは具体的に何を指しますか？**
A: 「Claude Code」は、Anthropic社のAIモデル「Claude」を利用して、コードの生成、レビュー、デバッグ、リファクタリング、あるいはソフトウェア開発プロセス全体を支援する取り組みやワークフローを指すことが多いです。その過程で発生するAIとの対対話や指示の履歴を「タイムライン」として可視化することで、開発プロセスを追跡しやすくする目的があると考えられます。

---
AI Conduit: https://www.youtube.com/@AI.Conduit