# Claude Codeのログ解析でエラー原因の特定が自動化された - 実践テンプレート  

---

## この動画で学んだこと  
Python スクリプト `analyze_logs.py` を使えば、Claude Code が出力したログを自動で解析し、エラーの原因や頻出パターンを瞬時に抽出できます。出力形式や解析期間をオプションで指定できるので、日々のデバッグ作業が大幅に効率化します。

---

## すぐに使えるテンプレート  

### 1. `analyze_logs.py`（メインスクリプト）

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
analyze_logs.py
----------------
Claude Code のログファイルを解析し、エラー原因・頻出キーワード・発生回数を
レポートとして出力します。

主な機能
  * ログファイルのパス指定
  * 期間フィルタ（開始日時・終了日時）
  * 出力形式の選択（json / csv / text）
  * エラーメッセージの集計と頻度上位 N 件の表示

使用例
  $ python analyze_logs.py logs/claude.log --start "2024-01-01" --end "2024-01-31" --format json
"""

import argparse
import json
import csv
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

# ------------------------------------------------------------
# ログエントリの正規表現（例: 2024-08-15 14:23:07 [ERROR] Something went wrong）
# ------------------------------------------------------------
LOG_PATTERN = re.compile(
    r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\[(?P<level>\w+)\]\s+(?P<message>.+)$'
)

def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパースする"""
    parser = argparse.ArgumentParser(
        description="Claude Code のログを解析し、エラー原因を自動抽出します。"
    )
    parser.add_argument(
        "log_path",
        type=Path,
        help="解析対象のログファイルへのパス（例: logs/claude.log）"
    )
    parser.add_argument(
        "--start",
        type=str,
        default=None,
        help="解析開始日時（ISO 8601 形式: YYYY-MM-DD または YYYY-MM-DDTHH:MM:SS）"
    )
    parser.add_argument(
        "--end",
        type=str,
        default=None,
        help="解析終了日時（ISO 8601 形式）"
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv", "text"],
        default="text",
        help="出力形式（デフォルト: text）"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="エラーメッセージ上位 N 件を表示（デフォルト: 10）"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="結果を書き出すファイルパス（省略した場合は標準出力）"
    )
    return parser.parse_args()

def iso_to_dt(value: Optional[str]) -> Optional[datetime]:
    """ISO 形式文字列 → datetime へ変換（None はそのまま返す）"""
    if value is None:
        return None
    # "2024-08-15" か "2024-08-15T14:23:07" のどちらでも受け付ける
    try:
        return datetime.fromisoformat(value)
    except ValueError as e:
        sys.stderr.write(f"日付形式エラー: {value} ({e})\n")
        sys.exit(1)

def load_log_lines(log_path: Path) -> List[str]:
    """ログファイルを UTF-8 で読み込み、行リストを返す"""
    if not log_path.is_file():
        sys.stderr.write(f"エラー: ログファイルが見つかりません → {log_path}\n")
        sys.exit(1)
    return log_path.read_text(encoding="utf-8").splitlines()

def filter_by_date(
    entries: List[Tuple[datetime, str, str]],
    start: Optional[datetime],
    end: Optional[datetime]
) -> List[Tuple[datetime, str, str]]:
    """開始・終了日時でエントリを絞り込む"""
    if start is None and end is None:
        return entries
    filtered = []
    for ts, level, msg in entries:
        if start and ts < start:
            continue
        if end and ts > end:
            continue
        filtered.append((ts, level, msg))
    return filtered

def parse_log(lines: List[str]) -> List[Tuple[datetime, str, str]]:
    """各行を (timestamp, level, message) のタプルに変換"""
    parsed = []
    for line in lines:
        m = LOG_PATTERN.match(line)
        if not m:
            # パターンに合わない行は無視（必要なら別途処理可）
            continue
        ts = datetime.strptime(m.group("timestamp"), "%Y-%m-%d %H:%M:%S")
        level = m.group("level")
        message = m.group("message")
        parsed.append((ts, level, message))
    return parsed

def aggregate_errors(entries: List[Tuple[datetime, str, str]]) -> Counter:
    """ERROR レベルのメッセージを集計し、出現回数をカウント"""
    error_messages = [msg for _, lvl, msg in entries if lvl.upper() == "ERROR"]
    return Counter(error_messages)

def output_result(
    counter: Counter,
    fmt: str,
    top_n: int,
    output_path: Optional[Path] = None
) -> None:
    """集計結果を指定フォーマットで出力（ファイルまたは標準出力）"""
    most_common = counter.most_common(top_n)

    if fmt == "json":
        data