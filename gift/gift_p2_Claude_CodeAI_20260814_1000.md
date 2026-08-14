# Claude Code の顧客サポート AI - 実践テンプレート

## この動画で学んだこと
Claude の顧客サポートエージェントを **`customer-support-agent`** ディレクトリからすぐに立ち上げ、API キーさえ設定すれば問い合わせ対応を自動化できることを学びました。

---

## すぐに使えるテンプレート

### 1. リポジトリのクローン & ディレクトリ移動
```bash
# 公式クイックスタートリポジトリをクローン
git clone https://github.com/anthropics/anthropic-quickstarts.git

# 顧客サポートエージェントのディレクトリへ移動
cd anthropic-quickstarts/customer-support-agent
```

### 2. 必要パッケージのインストール
```bash
# Python の依存関係を一括インストール
pip install -r requirements.txt
```

### 3. 環境変数に API キーを設定
```bash
# .env ファイルを作成（※必ず .gitignore に入っているので安全です）
cat <<EOF > .env
# Claude の API キー（Anthropic のコンソールで取得してください）
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# デフォルトで使用するモデル（例: claude-3-opus-20240229）
ANTHROPIC_MODEL=claude-3-opus-20240229
EOF
```

### 4. エージェント起動スクリプト（`run_agent.py`）
```python
# -*- coding: utf-8 -*-
"""
customer-support-agent 用のエントリーポイント
- Claude の API を呼び出して問い合わせに自動応答します
- 環境変数 .env から設定を読み込みます
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import anthropic

# -------------------------------------------------
# 1. .env の読み込み
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path)

# -------------------------------------------------
# 2. 必要な環境変数取得
# -------------------------------------------------
API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")

if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY が .env に設定されていません。")

# -------------------------------------------------
# 3. Claude クライアント初期化
# -------------------------------------------------
client = anthropic.Anthropic(api_key=API_KEY)

# -------------------------------------------------
# 4. ユーザーからの問い合わせを受け取る関数
# -------------------------------------------------
def get_user_query() -> str:
    """
    コンソールから問い合わせ内容を取得します。
    実運用では Webhook やチャット UI に置き換えてください。
    """
    print("\n=== 顧客サポート AI ===")
    return input("お問い合わせ内容を入力してください: ").strip()

# -------------------------------------------------
# 5. Claude に問い合わせを投げて回答を取得
# -------------------------------------------------
def get_ai_response(user_query: str) -> str:
    """
    Claude に対してプロンプトを送信し、回答テキストを取得します。
    """
    # シンプルなシステムプロンプト（必要に応じてカスタマイズ）
    system_prompt = (
        "You are a helpful customer support assistant for a SaaS product. "
        "Answer the user query concisely, politely, and provide any necessary next steps."
    )

    # Claude へのリクエスト
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        temperature=0.2,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_query}
        ],
    )
    return response.content[0].text.strip()

# -------------------------------------------------
# 6. メインループ
# -------------------------------------------------
def main():
    while True:
        query = get_user_query()
        if query.lower() in {"exit", "quit", "終了"}:
            print("👋 エージェントを終了します。")
            break

        try:
            answer = get_ai_response(query)
            print("\n--- AI の回答 ---")
            print(answer)
            print("-------------------\n")
        except Exception as e:
            print(f"⚠️ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
```

### 5. 実行コマンド
```bash
python run_agent.py
```

---

## 使い方

1. **リポジトリをクローン**し、`customer-support-agent` ディレクトリへ移動します。  
2. `requirements.txt` を **pip** でインストールします。  
3. **.env** に自分の **Anthropic API キー** と使用したいモデル名を記入します。  
4. `run_agent.py` を **Python で実行**すると、コンソール上で問い合わせを入力できるようになります。  
5. `exit` / `quit` / `終了` と入力すればエージェントを終了します。  

> **実運用への拡張例**  
> - Flask / FastAPI で HTTP エンドポイント化  
> - Slack / Discord Bot と連携してチャットベースに  
> - データベースに問い合わせ履歴を保存  

---

## よくある質問

**Q1. API キーが漏洩したらどうすればいいですか？**  
**A:** すぐに Anthropic のコンソールでキーを **ローテーション** し、`.env` を新しいキーに書き換えて再起動してください。`.env` は `.gitignore` に入っているのでリポジトリにコミットされません。

---

**Q2. `pip install -r requirements.txt` が失敗します。**  
**A:** Python 3.9 以上が必要です。仮想環境 (`python -m venv venv && source venv/bin/activate`) を作ってから再度実行してください。

---

**Q3. 返答が長すぎる／短すぎると感じます。**  
**