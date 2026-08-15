# Claude Codeでコード依存関係を図解する実践テンプレート

## この動画で学んだこと
Python スクリプトとたった 1 行のコマンドで、対象プロジェクトのインポート依存関係を自動解析し、SVG 形式の見やすいグラフを生成できます。

---

## すぐに使えるテンプレート

### 1. 必要なパッケージをインストール
```bash
# Graphviz 本体と Python バインディングをインストール
# macOS: brew install graphviz
# Ubuntu: sudo apt-get install graphviz
# Windows: https://graphviz.org/download/ からインストーラを実行

pip install graphviz tqdm
```

### 2. `dependency_graph.py`（日本語コメント付き）

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
dependency_graph.py
-------------------
対象ディレクトリ以下の Python ファイルを走査し、import 文から
モジュール間の依存関係を抽出して Graphviz の DOT 形式で出力します。
出力形式は SVG（デフォルト）・PNG・PDF など Graphviz がサポートすれば
何でも指定可能です。

使用例:
    python dependency_graph.py --project /path/to/project --output svg --out deps.svg
"""

import argparse
import ast
import os
from pathlib import Path
from collections import defaultdict
import sys

from graphviz import Digraph
from tqdm import tqdm  # 進捗バー表示（任意）

# ------------------------------------------------------------
# 1. 対象プロジェクト内の .py ファイルを再帰的に取得
# ------------------------------------------------------------
def collect_py_files(root: Path):
    """root 以下の全 .py ファイルパスを generator で返す"""
    for path in root.rglob('*.py'):
        # 仮想環境やテスト用ディレクトリは除外したい場合はここでフィルタ
        if any(part.startswith('.') for part in path.parts):
            continue
        yield path

# ------------------------------------------------------------
# 2. AST で import 文を解析し、依存関係を記録
# ------------------------------------------------------------
def parse_imports(file_path: Path):
    """1 ファイルの import / from import を解析し、依存先モジュール名の集合を返す"""
    try:
        tree = ast.parse(file_path.read_text(encoding='utf-8'))
    except SyntaxError as e:
        print(f"[WARN] {file_path} の構文エラー: {e}", file=sys.stderr)
        return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])  # top‑level モジュールだけ取得
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports

# ------------------------------------------------------------
# 3. 依存関係グラフを構築
# ------------------------------------------------------------
def build_dependency_graph(project_root: Path):
    """
    プロジェクト内の全モジュールをノード、import 関係をエッジとして
    辞書 {module: set(依存先モジュール)} を作成する。
    """
    graph = defaultdict(set)  # {module: {dep, ...}}

    py_files = list(collect_py_files(project_root))
    for py_file in tqdm(py_files, desc="Scanning .py files"):
        # モジュール名はプロジェクトルートからの相対パスを '.' 区切りに変換
        rel_path = py_file.relative_to(project_root).with_suffix('')
        module_name = ".".join(rel_path.parts)

        imports = parse_imports(py_file)
        # 標準ライブラリや外部パッケージはそのままノード化
        graph[module_name].update(imports)

    return graph

# ------------------------------------------------------------
# 4. Graphviz で SVG（または指定形式）に出力
# ------------------------------------------------------------
def render_graph(dep_graph: dict, output_format: str, out_path: Path):
    dot = Digraph(comment='Dependency Graph', format=output_format)
    dot.attr('node', shape='box', style='filled', color='lightgrey')

    # すべてのノードを追加
    all_modules = set(dep_graph.keys())
    for deps in dep_graph.values():
        all_modules.update(deps)

    for mod in all_modules:
        dot.node(mod)

    # エッジを追加
    for src, targets in dep_graph.items():
        for tgt in targets:
            dot.edge(src, tgt)

    # 出力
    dot.render(filename=out_path.stem, directory=out_path.parent, cleanup=True)
    print(f"[INFO] {output_format.upper()} ファイルを生成しました: {out_path}")

# ------------------------------------------------------------
# 5. CLI エントリポイント
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Python プロジェクトの import 依存関係を可視化し、SVG などの画像に出力します。"
    )
    parser.add_argument(
        "--project",
        "-p",
        type=Path,
        required=True,
        help="解析対象のプロジェクトディレクトリへのパス"
    )
    parser.add_argument(
        "--output",
        "-o",
        choices=["svg", "png", "pdf", "dot"],
        default="svg",
        help="出力形式（Graphviz がサポートする形式）"
    )
    parser.add_argument(
        "--out",
        "-f",
        type=Path,
        default=Path("dependency_graph.svg"),
        help="出力ファイル名（拡張子は自動で付与されます）"
    )