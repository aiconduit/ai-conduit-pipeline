# Claude Codeで5つ同時にコード生成 – 実践テンプレート

## この動画で学んだこと
Claude Code の CLI をターミナルで 5 つ同時に起動し、各インスタンスが完了したら `notify-send` でデスクトップ通知を送る方法を、すぐに実行できる形でまとめました。

---

## すぐに使えるテンプレート  

### 1. 前提条件（インストールがまだの場合）  
```bash
# ① Claude CLI（claude）をインストール
#   公式サイトの手順に従って API キーを設定してください
#   例: curl -L https://cli.anthropic.com/install.sh | sh
#   その後、~/.anthropic/config に API キーを書き込み

# ② notify-send が使えるように (Ubuntu/Debian 系)
sudo apt-get update && sudo apt-get install -y libnotify-bin

# ③ (任意) tmux がインストールされていない場合
sudo apt-get install -y tmux
```

### 2. 5 つの Claude インスタンスを同時起動する Bash スクリプト  
> **ファイル名:** `run_claude_5.sh`  
> **実行権限:** `chmod +x run_claude_5.sh`  

```bash
#!/usr/bin/env bash
# ------------------------------------------------------------
# 5 つの Claude Code インスタンスを同時に起動し、完了時に通知
# ------------------------------------------------------------
# 前提: `claude` コマンドが PATH に通っていること
# 前提: `notify-send` が利用可能な環境 (Linux デスクトップ) であること
# ------------------------------------------------------------

# ① ターミナルエミュレータを自動で 5 タブ開く関数
open_new_tab() {
    local cmd="$1"
    # GNOME Terminal の場合
    gnome-terminal -- bash -c "$cmd; exec bash"
}

# ② 各タブで実行するコマンド（バックグラウンドで走らせ、終了時に通知）
make_instance_cmd() {
    local idx=$1
    cat <<EOF
claude --model claude-opus-4 \\
    --system "You are Claude Code instance #${idx}. Generate code as requested." \\
    --output "claude_output_${idx}.txt" \\
    && notify-send "Claude #${idx}" "コード生成が完了しました (出力: claude_output_${idx}.txt)" \\
    || notify-send "Claude #${idx}" "エラーが発生しました"
EOF
}

# ------------------------------------------------------------
# ③ 5 つのタブを順に開く
for i in {1..5}; do
    cmd=$(make_instance_cmd "$i")
    open_new_tab "$cmd"
    # 少し待つとタブが重なりにくい
    sleep 0.5
done

# ------------------------------------------------------------
# ④ スクリプト終了メッセージ（全タブが起動したことを通知）
notify-send "Claude Launcher" "5 つの Claude インスタンスを起動しました"
```

### 3. 1 行で完結するワンライナー（タブを使わずにバックグラウンド実行）  
```bash
for i in {1..5}; do
    claude --model claude-opus-4 \
        --system "You are Claude Code instance #${i}." \
        --output "claude_output_${i}.txt" \
        && notify-send "Claude #${i}" "コード生成完了 (claude_output_${i}.txt)" \
        || notify-send "Claude #${i}" "エラー発生" &
done
```

---

## 使い方

1. **スクリプトを取得**  
   ```bash
   curl -O https://example.com/run_claude_5.sh   # 実際には自分の配布先 URL に置き換えてください
   chmod +x run_claude_5.sh
   ```

2. **API キーが設定されていることを確認**  
   `cat ~/.anthropic/config` に `api_key = "sk-..."` が書かれていれば OK。

3. **スクリプトを実行**  
   ```bash
   ./run_claude_5.sh
   ```
   - GNOME Terminal がインストールされている環境では、5 つの新しいタブが自動で開きます。  
   - 各タブで Claude が起動し、完了するとデスクトップ通知が届きます。

4. **出力結果の確認**  
   - `claude_output_1.txt` ～ `claude_output_5.txt` がカレントディレクトリに作成されます。  
   - 必要に応じて `cat claude_output_*.txt` でまとめて閲覧できます。

---

## よくある質問

**Q1. Windows でも同様に使えますか？**  
A: `notify-send` と GNOME Terminal は Linux 向けです。Windows で同様の通知をしたい場合は `msg` コマンドや PowerShell の `New-BurntToastNotification`、ターミナルは Windows Terminal の `wt` コマンドで置き換えてください。

**Q2. タブが開かない場合はどうすれば？**  
A: スクリプトは `gnome-terminal` を前提にしています。`konsole`、`xfce4-terminal`、`tilix` など別の端末エミュレータを使う場合は `open_new_tab` 関数内のコマンドを書き換えてください。

**Q3. 出力ファイル名を変えたいです。**  
A: `make_instance_cmd` 関数中の `--output "claude_output_${idx}.txt"` 部分を好きなパスに変更すれば OKです。

**Q4. 5 つ以上同時に起動したいです。**  
A: `for i in {1..5}` の範囲を `{1..N}` に変更