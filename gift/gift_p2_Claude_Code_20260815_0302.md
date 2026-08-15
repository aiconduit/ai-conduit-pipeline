# Claude Codeのコード解析で複雑な依存関係が図解化された - 実践テンプレート

## この動画で学んだこと
Python スクリプトとたった 1 行のコマンドで、プロジェクト全体のモジュール依存関係を自動解析し、SVG 形式の見やすい図として出力できることを学びました。

## すぐに使えるテンプレート
以下のファイルを **そのままコピー & ペースト** してプロジェクトのルートに保存してください。  

### 1️⃣ `generate_deps.py`  ― 依存関係を解析して Graphviz の DOT データを生成するスクリプト
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_deps.py
----------------
Python スクリプトで指定したディレクトリ以下の *.py ファイルを走査し、
import 文からモジュール間の依存関係グラフを作成します。
出力は Graphviz の DOT 形式なので、graphviz コマンドで SVG へ変換できます。

使用例:
    $ python generate_deps.py /path/to/project > deps.dot
    $ dot -Tsvg deps.dot -o deps.svg
"""

import argparse
import ast
import os
from pathlib import Path
from collections import defaultdict

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Python プロジェクトの依存関係を DOT 形式で出力")
    parser.add_argument(
        "project_path",
        type=str,
        help="解析対象のプロジェクトディレクトリ (例: ./my_project)",
    )
    parser.add_argument(
        "--exclude",
        type=str,
        default="",
        help="除外したいパッケージやディレクトリをカンマ区切りで指定 (例: tests,venv)",
    )
    return parser.parse_args()

def iter_python_files(root: Path):
    """プロジェクト内の .py ファイルを再帰的に列挙"""
    for path in root.rglob("*.py"):
        # .venv や __pycache__ などは除外
        if any(part.startswith(".") or part == "__pycache__" for part in path.parts):
            continue
        yield path

def extract_imports(file_path: Path) -> set:
    """1 ファイルから import されているモジュール名の集合を取得"""
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except SyntaxError:
        # 解析できないファイルはスキップ
        return set()
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])
    return imports

def build_dependency_graph(project_root: Path, exclude: set) -> dict:
    """{module: set(依存モジュール)} の辞書を作成"""
    graph = defaultdict(set)
    for py_file in iter_python_files(project_root):
        # ファイルパスからモジュール名を推測 (例: src/foo/bar.py → src.foo.bar)
        rel_path = py_file.relative_to(project_root).with_suffix("")
        module_name = ".".join(rel_path.parts)
        if any(exc in module_name for exc in exclude):
            continue
        imports = extract_imports(py_file)
        # プロジェクト内部のモジュールだけを対象にする
        internal_imports = {imp for imp in imports if not imp.startswith(("sys", "os", "re", "json", "typing", "builtins"))}
        graph[module_name].update(internal_imports)
    return graph

def graph_to_dot(graph: dict) -> str:
    """DOT 形式の文字列に変換"""
    lines = ["digraph dependencies {", '    node [shape=box style=filled fillcolor="#E8F0FE"];']
    for src, targets in graph.items():
        for tgt in targets:
            lines.append(f'    "{src}" -> "{tgt}";')
    lines.append("}")
    return "\n".join(lines)

def main():
    args = parse_args()
    project_path = Path(args.project_path).resolve()
    if not project_path.is_dir():
        raise SystemExit(f"Error: {project_path} はディレクトリではありません")
    exclude_set = {e.strip() for e in args.exclude.split(",") if e.strip()}
    dep_graph = build_dependency_graph(project_path, exclude_set)
    dot_output = graph_to_dot(dep_graph)
    print(dot_output)

if __name__ == "__main__":
    main()
```

### 2️⃣ 1 行コマンドで SVG を生成
```bash
# 例: プロジェクトが ./my_project にある場合
python generate_deps.py ./my_project --exclude=tests,venv | dot -Tsvg -o deps.svg
```
> **ポイント**  
> - `--exclude` でテストコードや仮想環境など不要なディレクトリを除外できます。  
> - `dot` コマンドは Graphviz がインストールされていれば利用可能です。  

### 3️⃣ 必要なツールのインストール
```bash
# Python ライブラリは標準ライブラリのみなので追加インストール不要
# ただし Graphviz 本体は