# Claude Codeのグラフ生成でブラウザが不要になった - 実践テンプレート

## この動画で学んだこと
この動画では、AIアシスタントClaude Codeのチャートイメージ生成スキルを活用し、純粋なNode.js環境でブラウザを使わずにグラフ画像を生成する方法を学びました。これにより、サーバーサイドでの動的なグラフ生成が容易になります。

## すぐに使えるテンプレート

以下の手順とコードを使って、Node.jsでグラフ画像を生成できます。

1.  **プロジェクトの初期化と依存関係のインストール**

    まず、新しいディレクトリを作成し、プロジェクトを初期化します。次に、グラフ描画ライブラリ`chart.js`と、Node.jsでキャンバス描画を行うための`canvas`ライブラリをインストールします。

    # 1. 新しいプロジェクトディレクトリを作成し、移動します
    mkdir node-chart-generator
    cd node-chart-generator

    # 2. Node.jsプロジェクトを初期化します
    npm init -y

    # 3. 必要な依存関係をインストールします
    npm install chart.js canvas
    2.  **グラフ生成スクリプト**

    `generate-chart.js` というファイルを作成し、以下のコードをコピー＆ペーストしてください。

    // generate-chart.js

    // Chart.jsとNode.jsのcanvasライブラリをインポート
    const { Chart, registerables } = require('chart.js');
    const { createCanvas } = require('canvas');
    const fs = require('fs');

    // Chart.jsに必要なコントローラや要素を登録
    // これがないとグラフが正しく描画されません (Chart.js v3以降の仕様)
    Chart.register(...registerables);

    // --- グラフの設定ここから ---
    const chartType = 'bar'; // 'bar', 'line', 'pie', 'doughnut' など、グラフの種類を指定
    const chartTitle = '週ごとの売上グラフ'; // グラフのタイトル

    const chartData = {
        labels: ['月', '火', '水', '木', '金', '土', '日'], // x軸のラベル
        datasets: [{
            label: '売上', // データセットのラベル
            data: [12, 19, 3, 5, 2, 3, 7], // グラフのデータ
            backgroundColor: [ // 各バー/セグメントの背景色
                'rgba(255, 99, 132, 0.7)',
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 206, 86, 0.7)',
                'rgba(75, 192, 192, 0.7)',
                'rgba(153, 102, 255, 0.7)',
                'rgba(255, 159, 64, 0.7)',
                'rgba(200, 200, 200, 0.7)'
            ],
            borderColor: [ // 各バー/セグメントの枠線色
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)',
                'rgba(200, 200, 200, 1)'
            ],
            borderWidth: 1 // 枠線の太さ
        }]
    };

    const chartOptions = {
        scales: {
            y: {
                beginAtZero: true // y軸を0から始める
            }
        },
        plugins: {
            title: {
                display: true,
                text: chartTitle // グラフタイトルを表示
            }
        }
    };

    const imageWidth = 800;  // 生成する画像の幅 (ピクセル)
    const imageHeight = 600; // 生成する画像の高さ (ピクセル)
    const outputPath = 'chart.png'; // 出力ファイル名とパス
    // --- グラフの設定ここまで ---

    /**
     * 指定された設定に基づいてグラフ画像を生成し、ファイルとして保存します。
     */
    async function generateChartImage() {
        // Node.jsでキャンバスを作成
        const canvas = createCanvas(imageWidth, imageHeight);
        const ctx = canvas.getContext('2d');

        // Chart.jsでグラフを描画
        new Chart(ctx, {
            type: chartType,    // グラフの種類
            data: chartData,    // グラフのデータ
            options: chartOptions // グラフのオプション
        });

        // キャンバスの内容をPNG画像としてバッファに変換し、ファイルに保存
        const buffer = canvas.toBuffer('image/png');
        fs.writeFileSync(outputPath, buffer);

        console.log(`🚀 グラフ画像を ${outputPath} に生成しました！`);
        console.log(`ファイルサイズ: ${Math.round(buffer.length / 1024)} KB`);
    }

    // グラフ生成関数を実行
    generateChartImage().catch(console.error);
    ## 使い方

1.  上記「プロジェクトの初期化と依存関係のインストール」セクションのコマンドをターミナルで実行し、`chart.js`と`canvas`をインストールします。
2.  `node-chart-generator`ディレクトリ内に`generate-chart.js`ファイルを作成し、上記の「グラフ生成スクリプト」のコードをコピー＆ペーストして保存します。
3.  ターミナルで以下のコマンドを実行し、スクリプトを実行します。

    node generate-chart.js
    4.  実行後、同じディレクトリ内に`chart.png`というファイルが生成されていることを確認してください。これがNode.jsで生成されたグラフ画像です。

## よくある質問

Q: `canvas`のインストールでエラーが出ます。どうすればよいですか？
A: `canvas`ライブラリは、内部的にC++のネイティブモジュールに依存しています。そのため、システムにビルドツール（Python、`build-essential`など）がインストールされていないとエラーになることがあります。
    *   **Ubuntu/Debian系:** `sudo apt-get install build-essential libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev`
    *   **macOS (Homebrew):** `brew install pkg-config cairo pango libjpeg giflib librsvg`
    *   **Windows:** [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/ja-jp/windows/wsl/install) を利用するか、[Node.js公式ドキュメント](https://nodejs.org/ja/download/package-manager)や`node-gyp`のインストールに関する情報を参照してください。多くの場合、Visual Studioのビルドツールが必要になります。

Q: どんなグラフタイプが使えますか？
A: `chart.js`がサポートする全てのグラフタイプ（`bar`, `line`, `pie`, `doughnut`, `radar`, `polarArea`, `bubble`, `scatter`など）が利用可能です。`chartType`変数の値を変更して試してみてください。

Q: グラフのデータや見た目を変更するにはどうすればよいですか？
A: `generate-chart.js`ファイル内の`chartData`オブジェクトを編集してデータを変更したり、`chartOptions`オブジェクトを編集してタイトル、軸の設定、凡例などの見た目をカスタマイズできます。`chart.js`の公式ドキュメントを参照すると、さらに詳細な設定が可能です。

Q: 出力ファイル名や画像のサイズを変更できますか？
A: はい、`outputPath`変数の値を変更して出力ファイル名（例: `'my-sales-chart.jpg'`）を変更できます。また、`imageWidth`と`imageHeight`の値を変更することで、生成される画像のサイズを調整できます。

---
AI Conduit: https://www.youtube.com/@AI.Conduit