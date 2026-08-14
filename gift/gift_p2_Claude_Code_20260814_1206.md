# Claude Code の自律エージェントでアプリ構築が自動になった – 実践テンプレート

## この動画で学んだこと
Claude Agent SDK を使えば、Anthropic API キーさえ設定すれば、数秒で自律エージェントが起動し、コード生成・テスト・デプロイまで自動で行ってくれます。

---

## すぐに使えるテンプレート

### 1️⃣ ① Anthropic API キーを環境変数に設定  
（※ まだ取得していない方は https://console.anthropic.com/ から取得してください）

```bash
# .env ファイルをプロジェクト直下に作成
cat > .env <<'EOF'
# -------------------------------------------------
# Anthropic API キー（必ず自分のキーに置き換えてください）
# -------------------------------------------------
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
EOF

# .env を自動で読み込むために dotenv-cli をインストール（まだの場合）
pip install python-dotenv
```

> **ポイント**  
> `dotenv` が自動で読み込まれない環境（例: VS Code のターミナル）では、`source .env` で手動ロードしてください。

---

### 2️⃣ ② Claude Agent SDK のインストール

```bash
# Python 用 SDK
pip install claude-agent-sdk

# もしくは、CLI 版を直接インストール（推奨）
pip install claude-agent
```

---

### 3️⃣ ③ デモ用エージェント設定ファイル（`agent_config.yaml`）

```yaml
# agent_config.yaml
# -------------------------------------------------
# Claude Agent の基本設定
# -------------------------------------------------
name: "auto-app-builder"
description: "自然言語で指示すれば、フロントエンド・バックエンド・テストまで自動生成するエージェント"
model: "claude-3-5-sonnet-20241022"   # 最新モデルを指定
max_iterations: 10                  # 生成・修正を最大10回まで繰り返す
temperature: 0.2                    # 生成の確定度
# -------------------------------------------------
# 生成対象のプロジェクト情報
# -------------------------------------------------
project:
  language: "python"
  framework: "fastapi"
  output_dir: "./generated_app"
# -------------------------------------------------
# 追加のプロンプト（必要に応じてカスタマイズ）
# -------------------------------------------------
system_prompt: |
  あなたは熟練のフルスタックエンジニアです。
  与えられた要件をもとに、FastAPI アプリとそのテストコード、Dockerfile まで自動生成してください。
  生成したファイルはすべて `{{project.output_dir}}` 配下に保存します。
```

---

### 4️⃣ ④ エージェントを起動するコマンド

```bash
# .env をロード（bash/zsh の場合）
source .env

# エージェントを実行
claude-agent run --config agent_config.yaml
```

> **実行結果**  
> - `generated_app/` ディレクトリに `main.py`, `requirements.txt`, `test_main.py`, `Dockerfile` が自動生成されます。  
> - コンソール上に「ステップ 1/10 完了」などの進捗がリアルタイムで表示されます。

---

## 使い方

1. **API キーを設定**  
   `.env` に自分の `ANTHROPIC_API_KEY` を貼り付け、`source .env` でロードします。

2. **SDK / CLI をインストール**  
   `pip install claude-agent`（または `claude-agent-sdk`）で必要なパッケージを取得します。

3. **設定ファイルを作成**  
   上記の `agent_config.yaml` をプロジェクト直下に保存し、必要に応じて言語・フレームワークを変更します。

4. **エージェントを起動**  
   `claude-agent run --config agent_config.yaml` を実行すると、エージェントが指示通りにコードを生成します。

5. **生成されたアプリを確認**  
   `cd generated_app && pip install -r requirements.txt && uvicorn main:app --reload` でローカルサーバーを起動し、動作を確認します。

---

## よくある質問

**Q1: API キーが漏洩したかもしれない場合はどうすればいいですか？**  
**A:** すぐに Anthropic コンソールでキーを無効化し、新しいキーを発行して `.env` を上書きしてください。キーは決してリポジトリにコミットしないように注意しましょう。

---

**Q2: 生成されたコードが期待と違うときは？**  
**A:** `agent_config.yaml` の `system_prompt` を具体的に書き換えるか、`max_iterations` を増やして再実行すると、エージェントが修正・再生成を試みます。

---

**Q3: Windows の PowerShell でも動作しますか？**  
**A:** はい。PowerShell では `Get-Content .env | ForEach-Object { $name,$value = $_ -split '='; Set-Item -Path Env:$name -Value $value }` のように環境変数をロードした後、同様に `claude-agent run --config agent_config.yaml` を実行してください。

---

**Q4: 生成された Dockerfile でビルドできません。**  
**A:** `generated_app` ディレクトリに移動し、`docker build -t auto-app .` を実行してください。エラーが出たら、`Dockerfile` のベースイメージや依存パ