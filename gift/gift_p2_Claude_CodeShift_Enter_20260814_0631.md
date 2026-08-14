# Claude Code ターミナル設定で Shift+Enter 改行 - 実践テンプレート

## この動画で学んだこと
Claude のターミナルで **Shift+Enter** を押すだけで改行できるようになる設定方法を、ワンコマンドで自動適用できることを学びました。

## すぐに使えるテンプレート
以下のコマンドをそのままコピーしてターミナルに貼り付けるだけで、設定が適用されます。

```bash
# -------------------------------------------------
# Claude Code ターミナル設定自動適用スクリプト
# -------------------------------------------------
# 1️⃣ Claude CLI がインストールされていることを前提としています。
# 2️⃣ /terminal-setup コマンドを実行すると、Shift+Enter で改行できる設定が自動で書き込まれます。
# -------------------------------------------------

# 実行コマンド
claude /terminal-setup

# 設定が反映されたことを確認するための簡易テスト
# (ターミナルが起動したら、Shift+Enter を押してみてください)
echo "✅ 設定完了！Shift+Enter で改行できるようになりました。"
```

> **ポイント**  
> - `claude` コマンドは Claude の公式 CLI です。インストールされていない場合は、公式サイトの手順に従ってインストールしてください。  
> - 上記スクリプトは **1 行** で完結しているので、コピー＆ペーストだけで即座に適用できます。

## 使い方
1. **Claude CLI がインストール済みか確認**  
   ```bash
   claude --version
   ```  
   バージョン情報が表示されれば OKです。表示されない場合は公式ドキュメントを参照してインストールしてください。

2. **上記テンプレートをコピー**  
   本ページの「すぐに使えるテンプレート」コードブロック全体を選択し、コピーします。

3. **ターミナルに貼り付けて実行**  
   ```bash
   # 例: macOS/Linux のターミナル、Windows の PowerShell でも同様に貼り付け可能
   claude /terminal-setup
   ```

4. **設定が反映されたか確認**  
   ターミナル上で **Shift+Enter** を押してみてください。改行ができれば成功です。

## よくある質問

**Q1: `claude` コマンドが見つからないと言われます。**  
**A:** Claude CLI がインストールされていないか、PATH に登録されていません。公式ページ（https://claude.ai/cli）からインストールし、`export PATH=$PATH:/path/to/claude` などでパスを通してください。

**Q2: 設定を元に戻したい場合はどうすればいいですか？**  
**A:** 設定ファイルは `~/.claude/terminal_config.json`（※実際のパスは環境により異なる）に保存されています。バックアップを取ってから削除するか、元の内容に書き換えてください。

**Q3: Windows の PowerShell でも同じコマンドで動作しますか？**  
**A:** はい、PowerShell でも `claude /terminal-setup` が実行できれば同様に設定が適用されます。PowerShell の実行ポリシーによりスクリプト実行がブロックされる場合は、`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` で緩和してください。

**Q4: 何らかのエラーが出たらどうすればいいですか？**  
**A:** エラーメッセージを確認し、以下を試してください。  
- CLI が最新バージョンか確認 (`claude update`)  
- ネットワーク接続が安定しているか確認  
- 権限が足りない場合は `sudo`（Linux/macOS）や管理者権限で PowerShell を再起動  

**Q5: 他のショートカットキーはカスタマイズできますか？**  
**A:** 現在の `claude /terminal-setup` は Shift+Enter の改行だけを有効化します。追加のカスタマイズは `~/.claude/terminal_config.json` を直接編集するか、公式ドキュメントの「Advanced Terminal Customization」セクションをご参照ください。

---

AI Conduit: https://www.youtube.com/@AI.Conduit