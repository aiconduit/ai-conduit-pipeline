# Claude Codeで5つ同時にコード生成 – 実践テンプレート

## この動画で学んだこと
Claude Code の CLI を複数タブで同時起動し、`notify-send` によるデスクトップ通知を設定すれば、5 つのインスタンスを並行してコード生成させることができます。

---

## すぐに使えるテンプレート  

以下のシェルスクリプトを **`run_claude_5.sh`** という名前で保存し、実行権限を付与してください。  
※ Ubuntu / Debian 系 Linux（GNOME デスクトップ）を想定しています。  

```bash
#!/usr/bin/env bash
# ------------------------------------------------------------
# Claude Code を 5 つ同時に起動し、各インスタンスの終了を
# notify-send で通知するテンプレート
# ------------------------------------------------------------

# 1. 使用するモデル（必要に応じて変更）
MODEL="claude-opus-4"

# 2. ターミナルエミュレータ（gnome-terminal を想定）
#    -c オプションでコマンドを実行し、終了後に notify-send で通知
#    -t オプションでタブのタイトルを設定
TERMINAL="gnome-terminal"

# 3. 各タブで実行したいコマンド（ここでは単純に対話モードを起動）
#    必要に応じて `--your-flag` 等を追加してください
CMD="claude --model ${MODEL}"

# 4. 5 つのタブを順に作成
for i in {1..5}; do
    ${TERMINAL} \
        --tab \
        --title="Claude #${i}" \
        -- bash -c "\
            echo '=== Claude #${i} 起動中 ==='; \
            ${CMD}; \
            EXIT_CODE=\$?; \
            if [ \$EXIT_CODE -eq 0 ]; then \
                notify-send 'Claude #${i}' '正常に終了しました' -i dialog-information; \
            else \
                notify-send 'Claude #${i}' \"エラーコード \$EXIT_CODE で終了しました\" -i dialog-error; \
            fi; \
            exec bash"
done
```

### スクリプトのポイント（日本語コメント）

| 行 | 内容 | 説明 |
|---|------|------|
| 5‑7 | `MODEL` 変数 | 使用したい Claude のモデル名（例: `claude-opus-4`） |
| 10‑12 | `TERMINAL` 変数 | ターミナルエミュレータ。GNOME 以外なら `konsole` や `xfce4-terminal` へ置換 |
| 15‑17 | `CMD` 変数 | 実際に起動する Claude CLI コマンド |
| 20‑28 | `for` ループ | 5 回繰り返し、各タブで同じコマンドを実行 |
| 22‑27 | `bash -c "...` | タブ内で実行するシェルスクリプト。終了時に `notify-send` で通知 |
| 24‑26 | `notify-send` | 正常終了 / エラー終了をデスクトップにポップアップで知らせる |

---

## 使い方

1. **スクリプトを保存**  
   ```bash
   curl -o run_claude_5.sh https://example.com/run_claude_5.sh   # 例としてダウンロード
   # もしくは手動でエディタに貼り付けて保存
   ```

2. **実行権限を付与**  
   ```bash
   chmod +x run_claude_5.sh
   ```

3. **スクリプトを実行**  
   ```bash
   ./run_claude_5.sh
   ```

   - 5 つのタブが自動で開き、各タブで `claude --model claude-opus-4` が起動します。  
   - 各インスタンスが終了すると、デスクトップに通知が表示されます。

4. **必要に応じてカスタマイズ**  
   - `MODEL` を別のモデル名に変更  
   - `CMD` に `--max-tokens 1024` などのオプションを追加  
   - `TERMINAL` を自分が使っている端末エミュレータに置き換える  

---

## よくある質問

**Q1. `gnome-terminal` がインストールされていません。**  
**A:** Ubuntu 系なら `sudo apt install gnome-terminal` でインストールできます。`konsole` や `xfce4-terminal` を使う場合は、スクリプト中の `TERMINAL` と `--tab --title` のオプションを書き換えてください。

---

**Q2. `notify-send` が見つからないと言われます。**  
**A:** `notify-send` は `libnotify-bin` パッケージに含まれます。以下でインストールしてください。  
```bash
sudo apt install libnotify-bin
```

---

**Q3. タブが 5 つではなく 1 つしか開きません。**  
**A:** `gnome-terminal` のバージョンが古いと `--tab` オプションが無視されることがあります。最新版にアップデートするか、代わりに `gnome-terminal --window` を 5 回呼び出す形に変更してください。

---

**Q4. 終了通知が表示されないのですが？**  
**A:** デスクトップ環境の通知設定がオフになっている可能性があります。設定 → 「通知」→「アプリケーション」から `notify-send`（または `Terminal`）の通知を有効にしてください。

---

**Q5. 5 つ以上同時に起動したいです。**  
**A:** `for i in {1..5}` の `5` を希望する数に変更すれば OK