#!/usr/bin/env python3
"""
optimize_title.py
タイトル最適化 - 数字強制・30文字チェック・禁止ワード除去
"""
import re, sys

FORBIDDEN = ["爆速","大幅","劇的","やばい","神","消えた","革命","衝撃","禁断"]

def ensure_number(title):
    if not re.search(r'\d', title):
        title = title + " 5選"
    return title

def remove_forbidden(title):
    for w in FORBIDDEN:
        title = title.replace(w, "")
    return title.strip()

def check_length(title, max_len=50):
    if len(title) > max_len:
        title = title[:max_len-3] + "..."
    return title

def optimize(title, series_num=None):
    title = remove_forbidden(title)
    title = ensure_number(title)
    title = title.replace("#Shorts","").strip()
    if series_num and f"#{series_num}" not in title:
        if len(title) + len(f" #{series_num}") <= 55:
            title = f"{title} #{series_num}"
    return check_length(title)

if __name__ == "__main__":
    title = sys.argv[1] if len(sys.argv) > 1 else "Claude Code Tips"
    num = int(sys.argv[2]) if len(sys.argv) > 2 else None
    print(optimize(title, num))
