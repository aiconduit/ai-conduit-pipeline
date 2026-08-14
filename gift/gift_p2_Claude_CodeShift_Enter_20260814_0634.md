# Claude Codeターミナル設定でShift+Enter改行 - 実践テンプレート

## この動画で学んだこと
Claude のターミナルで **Shift + Enter** を押すと改行できるようになる設定方法を、たった 1 行のコマンドで自動適用できます。

---

## すぐに使えるテンプレート

```bash
#!/usr/bin/env bash
# -------------------------------------------------
# Claude Code ターミナル設定スクリプト
# -------------------------------------------------
# このスクリプトを実行すると、Claude のターミナルで
# Shift+Enter が改行キーとして機能するように設定されます。
# -------------------------------------------------

# 1️⃣ Claude CLI がインストールされていることを確認
if ! command -v claude &> /dev/null; then
  echo "Error: 'claude' コマンドが見つかりません。Claude CLI をインストールしてください。"
  exit 1
fi

# 2️⃣ ターミナル設定コマンドを実行
echo "Claude ターミナル設定を適用中..."
claude /terminal-setup

# 3️⃣ 設定が反映されたか簡易チェック
if [[ $? -eq 0 ]]; then
  echo "✅ 設定が正常に適用されました。ターミナルで Shift+Enter を押すと改行できます。"
else
  echo "⚠️ 設定に失敗しました。エラーメッセージを確認してください。"
fi

# 4️⃣ 必要に応じてターミナルを再起動
echo "※ 変更を反映させるために、ターミナルを再起動することをおすすめします。"
```

> **使い方**  
> 1. 上記コードを `claude_terminal_setup.sh` という名前で保存  
> 2. ターミナルで `chmod +x claude_terminal_setup.sh` を実行して実行権限を付与  
> 3. `./claude_terminal_setup.sh` を実行すると自動で設定が適用されます  

---

## 使い方

1. **スクリプトを保存**  
   ```bash
   curl -o claude_terminal_setup.sh https://raw.githubusercontent.com/your-repo/claude-terminal-setup/main/claude_terminal_setup.sh
   ```

2. **実行権限を付与**  
   ```bash
   chmod +x claude_terminal_setup.sh
   ```

3. **スクリプトを実行**  
   ```bash
   ./claude_terminal_setup.sh
   ```

4. **ターミナルを再起動**（または新しいタブを開く）して、Shift + Enter が改行として機能することを確認。

---

## よくある質問

**Q1: `claude` コマンドが見つからないと言われます。**  
**A:** Claude CLI がインストールされていません。公式サイト（https://claude.ai/cli）からインストールし、`claude --version` が正常に表示されることを確認してください。

---

**Q2: 設定を適用したのに Shift+Enter が効きません。**  
**A:**  
- ターミナルを一度閉じて再度開く（または `exec $SHELL` でシェルを再起動）  
- 設定が正しく反映されたか `claude /terminal-setup` を再度実行してみる  
- それでも解決しない場合は、Claude のバージョンが最新か確認し、最新版にアップデートしてください。

---

**Q3: スクリプトを毎回手動で実行したくないです。自動化できますか？**  
**A:** `~/.bashrc`（または `~/.zshrc`）に以下の行を追加すると、ターミナル起動時に自動で設定が走ります（ただし起動時間が若干遅くなる点に注意）。  

```bash
# ~/.bashrc 例
if command -v claude &> /dev/null; then
  claude /terminal-setup >/dev/null 2>&1
fi
```

---

**Q4: Windows の PowerShell でも同じ設定は使えますか？**  
**A:** 現在の `claude /terminal-setup` は Unix 系シェル向けに実装されています。Windows の場合は WSL か Git Bash で実行してください。

---

**Q5: 設定を元に戻したい場合は？**  
**A:** 現在のところ `claude /terminal-setup` は上書き設定のみです。元に戻したい場合は、Claude の公式ドキュメントに記載されているデフォルト設定コマンド（例: `claude /reset-terminal`）を実行してください。

---

> **AI Conduit:** https://www.youtube.com/@AI.Conduit  

Enjoy your smoother Claude coding experience! 🚀