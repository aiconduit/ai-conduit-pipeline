# Claude Code 自律エージェントでアプリ雛形生成 - 実践テンプレート

## この動画で学んだこと
Claude Code の `autonomous_agent_demo.py` を使い、`--project-dir` と `--max-iterations` オプションだけで、数クリックでアプリの雛形を自動生成できることを体感できます。

---

## すぐに使えるテンプレート

### 1. ディレクトリ構成

```
my_project/
├─ .env                # Claude API キーなど
├─ autonomous_agent_demo.py   # Claude Code が提供するスクリプト（そのままコピー可）
└─ run.sh              # 本テンプレートのエントリーポイント
```

### 2. `.env`（必ず自分の API キーを設定してください）

```dotenv
# .env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# 必要に応じて他の環境変数を追加
```

### 3. `run.sh`（実行用シェルスクリプト）

```bash
#!/usr/bin/env bash
# --------------------------------------------------------------
# Claude Code 自律エージェント デモ実行スクリプト
# --------------------------------------------------------------
# 使い方:
#   1️⃣ 1回目の実行（無制限イテレーション）
#        $ ./run.sh
#   2️⃣ 3回だけ実行したいとき
#        $ ./run.sh --max-iterations 3
# --------------------------------------------------------------

# プロジェクトディレクトリ（このスクリプトと同じ階層にある my_project を対象）
PROJECT_DIR="./my_project"

# デフォルトのオプション
OPTIONS="--project-dir $PROJECT_DIR"

# 引数で --max-iterations が渡されたらオプションに追加
if [[ "$1" == "--max-iterations" ]]; then
    OPTIONS="$OPTIONS $@"
fi

# Python 実行
python autonomous_agent_demo.py $OPTIONS
```

> **ポイント**  
> * `run.sh` は **そのままコピー & ペースト** で使えます。  
> * `chmod +x run.sh` で実行権限を付与してください。

### 4. `autonomous_agent_demo.py`（Claude Code 公式スクリプト）

> 公式リポジトリから取得した最新版をそのまま `my_project/` 配下に置くだけです。  
> ここでは簡易的に **抜粋** だけ掲載します。実際は公式リポジトリのファイルをコピーしてください。

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
autonomous_agent_demo.py
Claude Code の自律エージェントデモスクリプト
公式リポジトリ: https://github.com/anthropic/claude-code
"""

import argparse
import os
import sys
from pathlib import Path

# --------------------------------------------------------------
# ここから下は公式スクリプト本体です（省略可）。
# 必要に応じてコメントを追加してください。
# --------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Claude Code Autonomous Agent Demo")
    parser.add_argument(
        "--project-dir",
        type=str,
        required=True,
        help="生成したコードを格納するプロジェクトディレクトリ"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="エージェントが実行する最大イテレーション数（省略時は無制限）"
    )
    args = parser.parse_args()

    project_path = Path(args.project_dir).resolve()
    if not project_path.exists():
        print(f"[INFO] プロジェクトディレクトリを作成します: {project_path}")
        project_path.mkdir(parents=True)

    # ここで Claude API を呼び出し、コード雛形を生成するロジックが走ります。
    # 実装は公式スクリプトをそのまま使用してください。
    # --------------------------------------------------------------
    # 例: agent = ClaudeAutonomousAgent(api_key=os.getenv("ANTHROPIC_API_KEY"))
    #      agent.run(project_path, max_iterations=args.max_iterations)
    # --------------------------------------------------------------

    print("[DONE] アプリ雛形の生成が完了しました！")
    print(f"生成されたファイルは {project_path} 以下をご確認ください。")

if __name__ == "__main__":
    main()
```

> **※** 上記は **抜粋** です。実際に動かす際は公式リポジトリの `autonomous_agent_demo.py` をそのまま `my_project/` に配置してください。

---

## 使い方

1. **リポジトリをクローンまたはダウンロード**  
   ```bash
   git clone https://github.com/anthropic/claude-code.git
   cd claude-code
   ```

2. **本テンプレートのファイルを `my_project/` 配下に配置**  
   - `.env` に自分の `ANTHROPIC_API_KEY` を記入  
   - `autonomous_agent_demo.py` を公式リポジトリからコピー  
   - `run.sh` を作成し、実行権限を付与  
   ```bash
   chmod +x run.sh
   ```

3. **エージェントを実行**  
   - **無制限イテレーション**（デフォルト）  
     ```bash
     ./run.sh
     ```
   - **3回だけ実行**（テストやデバッグ向け）  
     ```bash
     ./run.sh --max-iterations 3
     ```

4. **生成されたコードを確認**  
   `my_project/` ディレクトリ内に、README、src ディレクトリ、テストコードなどが自動生成されます。好きなエディタで開いて、必要に応じてカスタマイズしてください。

---

## よくある質問

**Q1. `ANTHROPIC_API_KEY` が無効だと言われます。**  
**A:**  
- `.env` ファイルに正しいキーが記入されている