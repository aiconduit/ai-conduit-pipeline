# Claude Codeのログ解析でエラー原因の特定が自動化された - 実践テンプレート  

## この動画で学んだこと  
Python スクリプト **`analyze_logs.py`** にログファイルのパスを渡すだけで、エラーの頻度・発生時刻・スタックトレースを自動で集計し、CSV・JSON・テキストのいずれかの形式で出力できることを学びました。  

---

## すぐに使えるテンプレート  

### 1. `analyze_logs.py` 本体  

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
analyze_logs.py
----------------
Claude Code の実行ログを解析し、エラーの原因・頻度・発生時間帯を自動で抽出します。

主な機能
  * 指定したログファイル（またはディレクトリ）を走査
  * エラーメッセージ・スタックトレースを抽出
  * 発生回数・最初・最後の出現時刻を集計
  * CSV / JSON / テキスト のいずれかで出力
  * 任意の期間（開始日時・終了日時）でフィルタリング可能

使用例
  $ python analyze_logs.py /path/to/log.txt --output csv --since "2024-01-01" --until "2024-01-31"
"""

import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ------------------------------------------------------------
# 正規表現パターン（ログのフォーマットに合わせて調整してください）
# ------------------------------------------------------------
# 例: 2024-08-15 14:23:01,234 - ERROR - Something went wrong
TIMESTAMP_REGEX = re.compile(
    r'(?P<ts>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d{3})?)'
)
ERROR_REGEX = re.compile(
    r'(?i)error|exception|traceback'  # 大文字小文字を無視してエラー行を検出
)

# ------------------------------------------------------------
# ユーティリティ関数
# ------------------------------------------------------------
def parse_timestamp(ts_str: str) -> datetime:
    """文字列 → datetime へ変換（複数フォーマットに対応）"""
    for fmt in ('%Y-%m-%d %H:%M:%S,%f',
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(ts_str, fmt)
        except ValueError:
            continue
    raise ValueError(f'Unsupported timestamp format: {ts_str}')

def read_log_file(path: Path) -> List[str]:
    """テキストファイルを UTF-8 で読み込む（エンコーディングエラーは無視）"""
    try:
        with path.open('r', encoding='utf-8', errors='ignore') as f:
            return f.readlines()
    except Exception as e:
        print(f'[WARN] {path} の読み込みに失敗: {e}', file=sys.stderr)
        return []

# ------------------------------------------------------------
# メイン解析ロジック
# ------------------------------------------------------------
def analyze_lines(lines: List[str],
                  since: Optional[datetime] = None,
                  until: Optional[datetime] = None) -> Dict[str, Dict]:
    """
    行リストを走査し、エラーメッセージごとに統計情報を作成する。

    戻り値例:
    {
        "ValueError: invalid literal for int()": {
            "count": 3,
            "first_seen": "2024-08-15 10:12:01",
            "last_seen":  "2024-08-15 12:45:09",
            "samples": ["スタックトレース1...", "スタックトレース2..."]
        },
        ...
    }
    """
    stats: Dict[str, Dict] = defaultdict(lambda: {
        "count": 0,
        "first_seen": None,
        "last_seen": None,
        "samples": []
    })

    current_error: Optional[str] = None
    current_ts: Optional[datetime] = None
    buffer: List[str] = []   # エラー行（スタックトレース）を一時保存

    for raw in lines:
        line = raw.rstrip('\n')
        # 1️⃣ タイムスタンプ取得
        ts_match = TIMESTAMP_REGEX.search(line)
        if ts_match:
            try:
                current_ts = parse_timestamp(ts_match.group('ts'))
            except ValueError:
                current_ts = None

        # 2️⃣ エラー行判定
        if ERROR_REGEX.search(line):
            # 新しいエラーが見つかったらバッファを確定
            if current_error:
                # 期間フィルタリング
                if (since is None or current_ts >= since) and \
                   (until is None or current_ts <= until):
                    entry = stats[current_error]
                    entry["count"] += 1
                    entry["samples"].append('\n'.join(buffer))
                    # 時刻更新
                    if entry["first_seen"] is None or current_ts < entry["first_seen"]:
                        entry["first_seen"] = current_ts
                    if entry["last_seen"] is None or current_ts > entry["last_seen"]:
                        entry["last_seen"] = current_ts
                # バッファリセット
                buffer.clear()

            # エラーメッセージの抽出（例: "ValueError: xxx"）
            # ここはログの実際のフォーマットに合わせて調整してください
            msg_match = re.search(r'(?P<type>\w+Error|Exception):?.*', line)
            current_error = msg_match.group('type') if msg_match else line
            buffer.append(line)
        elif current_error:
            # エラー行の続き（スタックトレース等）をバッファに追加
            buffer.append(line)

    # 最後のバッファを処理
    if current_error and buffer:
        if (since is None or current_ts >= since) and \
           (until is None or current_ts <= until):
            entry = stats[current_error]
            entry["count"] +=