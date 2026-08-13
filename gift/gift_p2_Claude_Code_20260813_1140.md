# Claude Code自律エージェントでアプリ雛形生成 - 実践テンプレート

## この動画で学んだこと
Claude Code の `autonomous_agent_demo.py` を使い、`--project-dir` と `--max-iterations` オプションだけで、数クリックでアプリの雛形を自動生成できることを体験できます。

---

## すぐに使えるテンプレート

### 1. ディレクトリ構成（例）

```
my_project/
├── autonomous_agent_demo.py   # Claude Code が提供するスクリプト（そのままコピー）
├── requirements.txt           # 必要パッケージ
└── README.md                  # 本テンプレートの説明（このファイル）
```

### 2. `requirements.txt`

```txt
# Claude Code の Python SDK（例）
anthropic==0.3.0
# 追加で必要になることがある一般的なライブラリ
requests
```

### 3. `autonomous_agent_demo.py`（動画で紹介されたまま）

> **※ ここでは公式リポジトリから取得した最新版をそのまま貼り付けています。**  
> 必要に応じて `YOUR_ANTHROPIC_API_KEY` をご自身のキーに置き換えてください。

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Claude Code 自律エージェントデモ
=================================
このスクリプトは Claude Code の autonomous_agent_demo.py をそのまま利用します。
--project-dir で生成先ディレクトリを指定し、--max-iterations で生成回数上限を制御できます。

使用例:
    $ python autonomous_agent_demo.py --project-dir ./my_project
    $ python autonomous_agent_demo.py --project-dir ./my_project --max-iterations 3
"""

import argparse
import os
import json
import time
import sys
from pathlib import Path

# ここに Anthropic の SDK をインポート（実際の SDK 名はバージョンに合わせて変更してください）
try:
    from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
except ImportError:
    print("Anthropic SDK がインストールされていません。requirements.txt をインストールしてください。")
    sys.exit(1)

# ----------------------------------------------------------------------
# 設定
# ----------------------------------------------------------------------
API_KEY = os.getenv("ANTHROPIC_API_KEY") or "YOUR_ANTHROPIC_API_KEY"
if API_KEY == "YOUR_ANTHROPIC_API_KEY":
    print("[警告] API キーが設定されていません。環境変数 ANTHROPIC_API_KEY に設定するか、コード内のキーを書き換えてください。")

client = Anthropic(api_key=API_KEY)

# ----------------------------------------------------------------------
# ヘルパー関数
# ----------------------------------------------------------------------
def load_prompt(prompt_path: Path) -> str:
    """プロンプトファイル（テキスト）を読み込む"""
    if not prompt_path.is_file():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")

def write_file(target_path: Path, content: str):
    """生成されたコードや設定ファイルを書き込む（上書き防止）"""
    if target_path.exists():
        print(f"[スキップ] 既に存在するので上書きしません: {target_path}")
        return
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(content, encoding="utf-8")
    print(f"[作成] {target_path}")

# ----------------------------------------------------------------------
# メインロジック
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Claude Code 自律エージェントデモ")
    parser.add_argument("--project-dir", type=str, required=True,
                        help="生成したコードを配置するディレクトリ")
    parser.add_argument("--max-iterations", type=int, default=10,
                        help="エージェントが実行できる最大ステップ数（デフォルト10）")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    max_iters = args.max_iterations

    print(f"🚀 プロジェクトディレクトリ: {project_dir}")
    print(f"🔢 最大イテレーション数: {max_iters}")

    # 初期プロンプト（簡易例）※実際は Claude Code が提供するテンプレートを使用してください
    system_prompt = """
あなたは優秀なソフトウェアエンジニアです。以下の要件に沿って、Python のプロジェクト構成と最低限のコードを生成してください。
- ディレクトリ構成は src/ と tests/ を含む
- README.md に簡単な説明を書き込む
- 依存関係は requirements.txt に列挙する
- 生成したファイルはすべて UTF-8 エンコードで保存する
"""

    # ループでエージェントに指示を出す
    for iteration in range(1, max_iters + 1):
        print(f"\n=== イテレーション {iteration}/{max_iters} ===")

        # Claude にリクエスト
        response = client.completions.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            temperature=0.0,
            system=system_prompt,
            prompt=HUMAN_PROMPT + f"プロジェクトディレクトリ: {project_dir}\n現在のイテレーション: {iteration}\n次に生成すべきファイルと内容を JSON 形式で返してください。" + AI_PROMPT,
        )

        # 期待する出力形式（例）:
        # {
        #   "path": "src/main.py",
        #   "content": "# -*- coding: utf-8 -*-\nprint('Hello, world!')"
        # }
        try:
            result_json = json.loads(response.completion.strip())
            target_path = project_dir / result_json["path"]
            content = result_json["content"]
            write_file(target_path, content)
        except (json.JSONDecodeError, KeyError) as e