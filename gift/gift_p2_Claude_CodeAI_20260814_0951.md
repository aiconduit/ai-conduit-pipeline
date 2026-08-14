# Claude Code の顧客サポート AI - 実践テンプレート

## この動画で学んだこと
Claude の顧客サポートエージェントを **`customer-support-agent`** ディレクトリにクローンし、数行の設定だけで問い合わせ対応を自動化できることを学びました。

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
# .env ファイルを作成（※必ずプロジェクトルートに置く）
cat <<EOF > .env
ANTHROPIC_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EOF

# .env を自動で読み込む（bash/zsh の場合）
export $(grep -v '^#' .env | xargs)
```

### 4. `app.py`（メインスクリプト）  
以下のコードを **`app.py`** として保存してください。日本語コメント付きで、実際に動作します。

```python
# -*- coding: utf-8 -*-
"""
customer-support-agent/app.py
Claude を使ったシンプルな顧客サポートエージェント
"""

import os
import json
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

# -------------------------------------------------
# 1️⃣ 環境変数から API キーを取得
# -------------------------------------------------
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise RuntimeError("環境変数 ANTHROPIC_API_KEY が設定されていません。")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# -------------------------------------------------
# 2️⃣ エージェントのプロンプト（ベースとなる指示文）
# -------------------------------------------------
BASE_PROMPT = f"""\
あなたはカスタマーサポートエージェントです。以下のルールを守って、ユーザーからの問い合わせに対して丁寧かつ正確に回答してください。

- まずはユーザーの質問を要約し、問題点を明確にします。
- 必要に応じて、公式ドキュメントや社内ナレッジベースを参照してください。（今回はサンプルなので、架空の情報で構いません）
- 回答は日本語で、ビジネスライクかつフレンドリーに。
- 不明点がある場合は「確認中です」と伝えて、後ほど回答すると約束してください。

以下はサンプルの問い合わせです。
"""

# -------------------------------------------------
# 3️⃣ メイン関数：ユーザー入力 → Claude へリクエスト → 結果表示
# -------------------------------------------------
def get_support_reply(user_query: str) -> str:
    """
    ユーザーの問い合わせ文字列を受け取り、Claude に回答させる関数。
    """
    # 完全なプロンプトを組み立てる
    prompt = f"{BASE_PROMPT}{HUMAN_PROMPT} {user_query}{AI_PROMPT}"

    # Claude にリクエスト
    response = client.completions.create(
        model="claude-3-sonnet-20240229",   # もしくは "claude-3-opus-20240229"
        max_tokens=1024,
        temperature=0.0,
        top_p=1,
        prompt=prompt,
    )
    # 返却されたテキストだけを抽出
    return response.completion.strip()


# -------------------------------------------------
# 4️⃣ CLI で簡易テストできるエントリーポイント
# -------------------------------------------------
if __name__ == "__main__":
    print("=== Claude Customer Support Agent ===")
    print("質問を入力してください (Ctrl+C で終了)")

    try:
        while True:
            user_input = input("\n> ")
            if not user_input.strip():
                continue
            reply = get_support_reply(user_input)
            print("\n--- Claude の回答 ---")
            print(reply)
    except KeyboardInterrupt:
        print("\n終了します。")
```

### 5. 実行コマンド
```bash
python app.py
```

---

## 使い方

1. **リポジトリをクローン**し、`customer-support-agent` ディレクトリへ移動します。  
2. `pip install -r requirements.txt` で依存ライブラリをインストールします。  
3. **Anthropic の API キー**（[Anthropic Console](https://console.anthropic.com/) で取得）を `.env` に記入し、環境変数として読み込ませます。  
4. `app.py` をそのままコピーして保存し、**`python app.py`** を実行。  
5. ターミナル上で質問を入力すると、Claude が自動で回答を生成します。  

> **ポイント**  
> - `model` パラメータは `claude-3-sonnet-20240229`（コストと速度のバランスが良い）か、より高性能な `claude-3-opus-20240229` に変更可能です。  
> - `temperature=0.0` にすると決定的な回答が得られます。柔軟な回答が欲しい場合は `0.2~0.5` に調整してください。

---

## よくある質問

**Q1. API キーが漏洩したかもしれません。どうすればいいですか？**  
**A:** すぐに Anthropic コンソールでキーを **Revoke**（無効化）し、新しいキーを生成して `.env` を更新してください。キーは決してリポジトリにコミットしないように注意しましょう。

---

**Q2. `pip install -r requirements