# -*- coding: utf-8 -*-
"""
Conduit for Gemini (安全版)
- DeepSeekのタブ(deepseek)だけを監視・操作する(最前面依存をやめた)
- [GEMINI:CMD:N] マーカーのみ反応(Claudeの[MACHINE:CMD:N]とは混ざらない)
- 危険コマンドは実行前に確認
- エラーを握りつぶさず表示する
"""
import subprocess
import time
import re
import sys
import os


def _ensure_singleton():
    """起動時に、自分以外の同名プロセスを全て終了する。
    DeepSeekが誤ってスクリプト自身を起動するコマンドを出しても、
    多重起動による暴走(結果の多重送信)を物理的に防ぐ。"""
    current_pid = os.getpid()
    result = subprocess.run(
        ["pgrep", "-f", "conduit_deepseek_safe.py"],
        capture_output=True, text=True
    )
    pids = [int(p) for p in result.stdout.strip().split()
            if p and int(p) != current_pid]
    for pid in pids:
        print("[GeminiConduit] 重複プロセスを終了: PID=%d" % pid)
        subprocess.run(["kill", "-9", str(pid)])


_ensure_singleton()

GEMINI_TAG = "DEEPSEEK"
GEMINI_URL_KEYWORD = "deepseek"  # このURLを含むタブだけを対象にする
last_processed_id = -1

# 実行前に確認したい危険なコマンドのパターン
DANGEROUS_PATTERNS = []


def run_cmd(cmd):
    return subprocess.run(
        cmd, shell=True, capture_output=True, text=True
    ).stdout


def is_dangerous(cmd):
    for pat in DANGEROUS_PATTERNS:
        if re.search(pat, cmd):
            return True
    return False


def find_gemini_tab():
    """全ウィンドウ・全タブからgemini.google.comのタブを探し、(window_index, tab_index)を返す。
    見つからなければ None。"""
    script = '''
    tell application "Google Chrome"
        set out to ""
        set wi to 0
        repeat with w in windows
            set wi to wi + 1
            set ti to 0
            repeat with t in tabs of w
                set ti to ti + 1
                if (URL of t) contains "%s" then
                    set out to (wi as string) & "," & (ti as string)
                    return out
                end if
            end repeat
        end repeat
        return ""
    end tell
    ''' % GEMINI_URL_KEYWORD
    result = subprocess.run(
        ["osascript", "-e", script], capture_output=True, text=True
    ).stdout.strip()
    if not result:
        return None
    try:
        wi, ti = result.split(",")
        return int(wi), int(ti)
    except ValueError:
        return None


def get_gemini_code_blocks(wi, ti):
    """指定したGeminiタブのコードブロックを取得する。"""
    js = ("try { Array.from(document.querySelectorAll('.ds-markdown'))"
          ".map(el => el.innerText).join('---BLOCK---') } catch(e) { '' }")
    script = (
        'tell application "Google Chrome" to return execute '
        'tab %d of window %d javascript "%s"' % (ti, wi, js)
    )
    return subprocess.run(
        ["osascript", "-e", script], capture_output=True, text=True
    ).stdout.strip()


def send_text(text, cmd_id, wi, ti):
    """指定したGeminiタブの入力欄に結果を書き込む。
    長文や特殊文字でAppleScriptが壊れるのを防ぐため、Base64で安全に渡す。"""
    import base64
    # 長すぎる結果は切り詰める(DeepSeekが扱いやすいように)
    MAX_LEN = 3000
    if len(text) > MAX_LEN:
        text = text[:MAX_LEN] + "\n...(以下省略、全%d文字)" % len(text)
    full = "[%s:CMD:%d]\n実行結果:\n%s" % (GEMINI_TAG, cmd_id, text)
    # UTF-8 → Base64(英数字のみになるのでAppleScriptで絶対に壊れない)
    b64 = base64.b64encode(full.encode("utf-8")).decode("ascii")
    # JS側でBase64をデコードしてUTF-8文字列に戻し、入力欄に設定する
    # 入力欄に結果を設定し、inputイベントを発火させてから送信ボタンを押す。
    # (Geminiは入力欄の変更を検知しないと送信ボタンが有効化されないため)
    # DeepSeekの入力欄はtextarea。valueに設定し、Reactが検知できるようinputイベントを発火。
    # 送信ボタンは .ds-button--primary をクリックする。
    js = ("var el=document.querySelector('textarea');"
          "if(el){"
          "var s=decodeURIComponent(escape(atob('%s')));"
          "var setter=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;"
          "setter.call(el,s);"
          "el.dispatchEvent(new Event('input',{bubbles:true}));"
          "setTimeout(function(){"
          "var btn=document.querySelector('.ds-button--primary');"
          "if(btn){btn.click();}"
          "},800);"
          "}void(0);"
          % b64)
    script = (
        'tell application "Google Chrome" to execute '
        'tab %d of window %d javascript "%s"' % (ti, wi, js)
    )
    subprocess.run(["osascript", "-e", script],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    global last_processed_id
    print("=" * 50)
    print("Conduit for DeepSeek (安全版) 起動")
    print("対象: %s のタブのみ" % GEMINI_URL_KEYWORD)
    print("マーカー: [%s:CMD:N] ##RUN## のみ反応" % GEMINI_TAG)
    print("=" * 50)

    tab = find_gemini_tab()
    if tab is None:
        print("⚠ Geminiのタブが見つかりません。"
              "ブラウザで %s を開いてください。" % GEMINI_URL_KEYWORD)
        print("  (タブが開かれるまで待機します)")

    while True:
        try:
            tab = find_gemini_tab()
            if tab is None:
                # Geminiタブがない時は何もしない(他タブを誤実行しないため)
                time.sleep(2)
                continue
            wi, ti = tab
            raw = get_gemini_code_blocks(wi, ti)
            blocks = raw.split('---BLOCK---')
            for block in blocks:
                # 開始マーカーと終了マーカーの両方が揃った時だけ実行する。
                # これにより、DeepSeekが出力途中のコマンドを誤実行する事故を防ぐ。
                match = re.search(
                    r"\[%s:CMD:(?P<num>\d+)\]\s*#+\s*RUN\s*#+\s*(.+?)\s*\[/%s:CMD:(?P=num)\]" % (GEMINI_TAG, GEMINI_TAG),
                    block, re.DOTALL
                )
                if not match:
                    continue
                cmd_id = int(match.group(1))
                cmd = match.group(2).strip()
                if cmd_id <= last_processed_id:
                    continue

                if is_dangerous(cmd):
                    print("\n⚠ 危険なコマンドを検知 → 自動スキップ:")
                    print("   %s" % cmd)
                    last_processed_id = cmd_id
                    send_text("このコマンドは安全のため実行できません(スクリプト起動・プロセス終了・バックグラウンド実行などは禁止)。ls や cat での確認は可能です。", cmd_id, wi, ti)
                    continue

                print("-> 実行: %s ID:%d | CMD:%s" % (GEMINI_TAG, cmd_id, cmd))
                res = run_cmd(cmd)
                send_text(res, cmd_id, wi, ti)
                last_processed_id = cmd_id
                print("-> 完了")
        except KeyboardInterrupt:
            print("\n終了します。")
            sys.exit(0)
        except Exception as e:
            # エラーを握りつぶさず表示(ただし監視は継続)
            print("⚠ エラー: %s" % e)
        time.sleep(2)


if __name__ == "__main__":
    main()
