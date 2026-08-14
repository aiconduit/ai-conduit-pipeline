# Claude CodeのToolでカスタムエージェントを作成 - 実践テンプレート  

## この動画で学んだこと  
Claude Code の **Tool** 機能を利用して、`ThinkTool` を組み込んだオリジナルエージェントを数行のコードで作成できます。  

---

## すぐに使えるテンプレート  

### 1️⃣ `agents/tools/think.py`  – ThinkTool の実装  

```python
# agents/tools/think.py
# -*- coding: utf-8 -*-
"""
ThinkTool: Claude が「考える」ためのシンプルなツールです。
このツールは `tool_input` を受け取り、文字列をそのまま返すだけのデモ実装です。
実際のプロダクションでは、外部API呼び出しや計算ロジックに置き換えてください。
"""

from typing import Any, Dict

# Claude の Tool インターフェースに合わせたベースクラス
class Tool:
    """Claude が期待する最低限のインターフェースです。"""
    name: str = "think"
    description: str = "内部で考えを整理したいときに使用します。入力文字列をそのまま返します。"

    def run(self, tool_input: str) -> Dict[str, Any]:
        """実際にツールが呼び出されたときに実行される処理"""
        # ここでは単に入力をエコーするだけ
        return {"output": tool_input}


class ThinkTool(Tool):
    """ThinkTool のエイリアス（将来的に拡張しやすいようにクラスを分離）"""
    pass
```

> **ポイント**  
> - `Tool` クラスは Claude が内部で期待する `name`, `description`, `run()` を持ちます。  
> - `ThinkTool` は `Tool` を継承しているだけなので、後から機能追加が容易です。  

---

### 2️⃣ `agents/agent.py` – カスタムエージェント本体  

```python
# agents/agent.py
# -*- coding: utf-8 -*-
"""
Claude Code のカスタムエージェント例。
ThinkTool を組み込んだシンプルなエージェントです。
"""

import os
from pathlib import Path

# ① ThinkTool をインポート
from agents.tools.think import ThinkTool

# ② Claude の SDK（例: anthropic）をインポート
#    ここでは `anthropic` パッケージを使用する想定です。
#    実際に利用する SDK に合わせてインポートを書き換えてください。
from anthropic import Anthropic, AIMessage, HumanMessage, SystemMessage

# 環境変数から API キーを取得（.env からもロード可能）
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise RuntimeError("ANTHROPIC_API_KEY が設定されていません。")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# エージェント作成時に tools=[ThinkTool()] を渡す
class CustomAgent:
    """ThinkTool を組み込んだ Claude エージェント"""

    def __init__(self, model: str = "claude-3-5-sonnet-20240620"):
        self.model = model
        self.tools = [ThinkTool()]          # ← ここがポイント
        self.messages = []                  # 会話履歴

    def add_message(self, role: str, content: str):
        """会話履歴にメッセージを追加"""
        if role == "system":
            self.messages.append(SystemMessage(content=content))
        elif role == "human":
            self.messages.append(HumanMessage(content=content))
        elif role == "assistant":
            self.messages.append(AIMessage(content=content))
        else:
            raise ValueError(f"Invalid role: {role}")

    def run(self) -> str:
        """Claude にリクエストを送信し、結果を返す"""
        response = client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=0.7,
            system=self._system_prompt(),
            messages=self.messages,
            tools=[tool.__dict__ for tool in self.tools],  # SDK が要求する形に変換
        )
        # Claude がツール呼び出しを返した場合は自前でハンドリング
        if response.content[0].type == "tool_use":
            tool_name = response.content[0].name
            tool_input = response.content[0].input
            # 登録されたツールを検索
            tool = next(t for t in self.tools if t.name == tool_name)
            tool_result = tool.run(tool_input)
            # ツール結果を再度 Claude に送信
            self.add_message("assistant", response.content[0].text or "")
            self.add_message("tool", f"{tool_name} result: {tool_result['output']}")
            return self.run()  # 再帰で続行
        else:
            # 通常のテキスト応答
            answer = response.content[0].text
            self.add_message("assistant", answer)
            return answer

    def _system_prompt(self) -> str:
        """エージェントの基本指示（必要に応じて編集）"""
        return (
            "You are a helpful assistant that can use the `think` tool to "
            "organize your thoughts. When you need to think about something, "
            "call the tool with the relevant text."
        )

# -------------------------------------------------
# 使い方サンプル（このファイルの末尾に置くだけで実行可能）
if __name__ == "__main__":
    agent = CustomAgent()
    agent.add_message("system", "You are a friendly AI.")
    agent.add_message("human", "今日の天気と、明日の予定を考えてください。")
    answer = agent.run()
    print("\n=== Claude の返答 ===")
    print(answer)
```

> **ポイント**  
> 1. **手順1** で `ThinkTool` をインポートしています。  
> 2. **手順2** でエージェント作成時に `tools=[ThinkTool()]` を渡しています。  
> 3. `client.messages.create` の `tools`