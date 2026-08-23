# Claude CodeのChart Image Generator - Node.jsでブラウザ不要のチャート画像生成 - 実践テンプレート

## この動画で学んだこと
この動画では、Claude CodeのChart Image Generatorスキルを活用することで、重いブラウザを使うことなくNode.js環境のみで効率的にチャート画像を生成できることがわかりました。これにより、サーバーサイドでの画像処理が非常に簡単になります。

## すぐに使えるテンプレート

動画で紹介されたClaude CodeのChart Image Generatorスキルは、Node.js環境でチャート画像を生成する強力な機能を提供します。具体的なスキルコマンドが公開されていない場合でも、Node.jsには類似の機能を持つライブラリが存在し、動画のコンセプトをすぐに実践できます。ここでは、`quickchart-js` を利用して、データとタイプを指定してチャート画像を生成するテンプレートを紹介します。

// generateChart.js
// Node.jsでチャート画像を生成し、ファイルとして保存するスクリプト

// 必要なモジュールをインストールします。
// 動画で「必要なモジュールをスキルディレクトリにインストール」と紹介された機能が、
// Node.jsライブラリとして提供される場合を想定しています。
// ここでは、同様の機能を提供する「quickchart-js」を使用します。
// 実行前にターミナルで `$ npm install quickchart-js` を実行してください。
// `fs`と`path`はNode.jsの組み込みモジュールなので、別途インストールは不要です。
const QuickChart = require('quickchart-js');
const fs = require('fs');
const path = require('path');

// チャートのデータとタイプを指定します（動画で紹介された方法に倣います）
const chartData = {
    labels: ['1月', '2月', '3月', '4月', '5月'], // X軸のラベル
    datasets: [{
        label: '月別売上', // データセットの名称
        data: [65, 59, 80, 81, 56], // データポイント
        backgroundColor: [ // 棒の色
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)'
        ],
        borderColor: [ // 棒の境界線の色
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)'
        ],
        borderWidth: 1 // 棒の境界線の幅
    }]
};

const chartType = 'bar'; // 生成するチャートのタイプを定義します ('bar', 'line', 'pie'など)

async function generateChartImage() {
    // QuickChartインスタンスを作成
    const qc = new QuickChart();
    
    // チャートの設定をJSON形式で指定
    qc.setConfig({
        type: chartType,
        data: chartData,
        options: {
            title: {
                display: true,
                text: '月別売上グラフ' // チャートのタイトル
            },
            scales: {
                y: {
                    beginAtZero: true // Y軸の原点を0から開始
                }
            }
        }
    });

    // 生成する画像のサイズと背景色を設定
    qc.setWidth(800);  // 幅を800ピクセルに設定
    qc.setHeight(400); // 高さを400ピクセルに設定
    qc.setBackgroundColor('white'); // 背景色を白に設定

    // 生成されたチャート画像のURLを取得（デバッグ用）
    const imageUrl = qc.getUrl();
    console.log(`生成されたチャート画像のURL: ${imageUrl}`);

    // 画像をバッファとして取得し、ファイルとして保存
    try {
        const imageBuffer = await qc.toBuffer(); // 画像データをバッファ形式で取得
        const outputPath = path.join(__dirname, 'chart.png'); // 保存するファイルのパス
        fs.writeFileSync(outputPath, imageBuffer); // ファイルを書き込み
        console.log(`チャート画像が ${outputPath} に保存されました。`);
    } catch (error) {
        console.error('チャート画像の生成または保存中にエラーが発生しました:', error);
    }
}

// スクリプトを実行
generateChartImage();
## 使い方

1.  **プロジェクトディレクトリの作成と移動**
    まず、新しいプロジェクト用のディレクトリを作成し、その中に移動します。
    mkdir my-chart-project
    cd my-chart-project
    2.  **Node.jsプロジェクトの初期化とモジュールのインストール**
    Node.jsプロジェクトを初期化し、チャート生成に必要なライブラリ `quickchart-js` をインストールします。これは動画で紹介された「スキルディレクトリへのインストール」に相当します。
    npm init -y
    npm install quickchart-js
    3.  **スクリプトファイルの作成**
    上記の「すぐに使えるテンプレート」のコードをコピーし、`generateChart.js` というファイル名でプロジェクトディレクトリ内に保存します。

4.  **チャート画像の生成**
    以下のコマンドでスクリプトを実行します。
    node generateChart.js
    実行が完了すると、`my-chart-project` ディレクトリ内に `chart.png` という名前のチャート画像ファイルが生成されます。

## よくある質問

Q: Claude CodeのChart Image Generatorスキルを直接利用するにはどうすれば良いですか？
A: 動画で紹介された「Claude CodeのChart Image Generatorスキル」の具体的な利用方法やAPI（特にNode.jsからの直接的な呼び出しコマンドやモジュール名）については、Claude Codeの公式ドキュメントや提供元のアナウンスをご確認ください。本テンプレートは、動画のコンセプト（Node.jsでのブラウザ不要な画像生成）をすぐに実践できるよう、`quickchart-js`ライブラリを使用して実装しています。

Q: 異なる種類のチャート（棒グラフ、円グラフなど）を生成できますか？
A: はい、テンプレート内の `const chartType = 'bar';` の部分を `'line'`, `'pie'`, `'doughnut'`, `'radar'` などに変更し、`chartData` の構造もそれに合わせて調整することで、様々な種類のチャートを生成できます。詳細はQuickChart.jsの公式ドキュメントをご参照ください。

Q: 生成される画像のサイズや背景色を変更できますか？
A: はい、`qc.setWidth(800);`, `qc.setHeight(400);`, `qc.setBackgroundColor('white');` の各メソッドの値を変更することで、画像のサイズや背景色を自由に調整できます。

---
AI Conduit: https://www.youtube.com/@AI.Conduit