# Claude CodeのToolでカスタムエージェントを作成 - 実践テンプレート

## この動画で学んだこと
Claude Code の **Tool** 機能を利用して、独自のエージェントに「Think」ツールを組み込むだけで、思考プロセスを可視化できるようになります。

## すぐに使えるテンプレート
以下のファイル構成をプロジェクトのルートに作成してください。  
※すでに `agents/` ディレクトリがある場合はそのまま上書きしてください。

### 1️⃣ `agents/tools/think.py`  – ThinkTool の実装
```python
# agents/tools/think.py
# -*- coding: utf-8 -*-
"""
ThinkTool
Claude Code の Tool API を利用して、エージェントが「考えている」ことを
テキストとして出力します。デバッグや学習目的で便利です。
"""

from typing import Any, Dict, List
from anthropic import Anthropic  # Claude の Python SDK が必要です

class ThinkTool:
    """
    Claude の Tool として登録できるシンプルなクラス。
    `run` メソッドが呼び出されると、引数をそのまま文字列で返します。
    """
    name = "think"
    description = "エージェントの内部思考をテキストで出力します。"

    def __init__(self):
        # 必要ならここで外部サービスやモデルを初期化できます
        pass

    def run(self, **kwargs: Any) -> str:
        """
        Claude から呼び出されるエントリーポイント。

        Parameters
        ----------
        kwargs : dict
            ユーザーが指定した任意のキーと値。

        Returns
        -------
        str
            受け取った情報を整形した文字列。
        """
        # 受け取った引数を pretty に整形して返すだけのシンプル実装
        if not kwargs:
            return "ThinkTool: 何も情報が渡されていません。"

        lines: List[str] = [f"{k}: {v}" for k, v in kwargs.items()]
        return "ThinkTool の出力 →\n" + "\n".join(lines)
```

### 2️⃣ `agents/agent.py` – カスタムエージェント本体
```python
# agents/agent.py
# -*- coding: utf-8 -*-
"""
Claude Code カスタムエージェント
ThinkTool を組み込んだシンプルなエージェント例です。
"""

from anthropic import Anthropic, AsyncAnthropic  # SDK が必要
from anthropic.types import MessageParam, ToolResultBlock
from agents.tools.think import ThinkTool

# -------------------------------------------------
# ① Claude の API キーを環境変数から取得
# -------------------------------------------------
import os
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise EnvironmentError("ANTHROPIC_API_KEY が環境変数に設定されていません。")

# -------------------------------------------------
# ② エージェント作成
# -------------------------------------------------
client = Anthropic(api_key=ANTHROPIC_API_KEY)

def create_agent():
    """
    ThinkTool を組み込んだエージェントを返す関数。
    必要に応じて他のツールやパラメータを追加してください。
    """
    # ツールはインスタンスのリストで渡す
    tools = [ThinkTool()]

    # エージェントの設定（例: temperature, max_tokens など）
    agent_config = {
        "model": "claude-3-5-sonnet-20240620",   # 変更可
        "temperature": 0.7,
        "max_tokens": 1024,
        "tools": tools,
    }
    return client, agent_config

# -------------------------------------------------
# ③ エージェント呼び出し例（同期版）
# -------------------------------------------------
def run_example(user_prompt: str):
    client, cfg = create_agent()

    # メッセージ履歴にユーザー入力を追加
    messages: List[MessageParam] = [
        {"role": "user", "content": user_prompt}
    ]

    # Claude にリクエスト
    response = client.messages.create(
        model=cfg["model"],
        temperature=cfg["temperature"],
        max_tokens=cfg["max_tokens"],
        tools=[{
            "name": tool.name,
            "description": tool.description,
            "input_schema": {}  # シンプルに空スキーマで OK
        } for tool in cfg["tools"]],
        messages=messages,
    )

    # ツール呼び出しがあれば実行
    if response.content and isinstance(response.content[0], dict) and response.content[0].get("type") == "tool_use":
        tool_use = response.content[0]
        tool_name = tool_use["name"]
        tool_input = tool_use.get("input", {})

        # 現在は ThinkTool のみなので直接呼び出す
        if tool_name == "think":
            tool = next(t for t in cfg["tools"] if t.name == "think")
            result = tool.run(**tool_input)

            # ツール結果を Claude に返す
            tool_result = client.messages.create(
                model=cfg["model"],
                temperature=cfg["temperature"],
                max_tokens=cfg["max_tokens"],
                messages=messages + [
                    {"role": "assistant", "content": tool_use},
                    {"role": "tool", "content": result, "tool_use_id": tool_use["id"]},
                ],
            )
            print("=== Claude の最終応答 ===")
            print(tool_result.content[0].text)
        else:
            print(f"未実装のツール: {tool_name}")
    else:
        # ツール呼び出しが無い場合はそのまま出力
        print("=== Claude の応答 ===")
        print(response.content[0].text)

# -------------------------------------------------
# ④ スクリプト実行エントリーポイント
# -------------------------------------------------
if __name__ == "__main__":
    # 例: 「AI に自己紹介させて、思考過程を見せて」 等のプロンプトを入れる
    prompt = "自己紹介をしながら、考