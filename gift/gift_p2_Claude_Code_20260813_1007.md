# Claude Codeで安全自動化 - 実践テンプレート

## この動画で学んだこと
Claude Code の **cowork** 機能を有効化し、サンドボックスモードとユーザー確認を必須にすることで、AI が実行するスクリプトを安全に自動化できます。

## すぐに使えるテンプレート
以下の手順をそのままコピーしてターミナルに貼り付ければ、`cowork` バイナリのインストールから設定ファイルの作成まで完了します。

```bash
# 1️⃣ cowork バイナリを /usr/local/bin にダウンロードして実行権限を付与
curl -L https://claude.ai/downloads/cowork -o /usr/local/bin/cowork && chmod +x /usr/local/bin/cowork

# 2️⃣ 設定ディレクトリを作成（まだ無い場合）
mkdir -p ~/.claude

# 3️⃣ cowork の設定ファイルを作成
cat > ~/.claude/cowork.yaml <<'EOF'
# -------------------------------------------------
# Claude Code cowork 設定ファイル
# -------------------------------------------------
# サンドボックスモードを有効化 → AI が実行できるコマンドは安全なものだけに制限されます
sandbox: true

# 各実行前にユーザーの確認を必須にします
# → 予期せぬ操作やデータ削除を防止できます
user_in_loop: true
EOF

# 4️⃣ 動作確認（バージョン表示）※インストールが成功したか確認できます
cowork --version
```

> **ポイント**  
> - `~/.claude/cowork.yaml` のパスは **.claude** ディレクトリ直下です。  
> - `sandbox: true` にすると、AI が実行できるコマンドは `git`, `ls`, `cat` など安全と判断されたものに限定されます。  
> - `user_in_loop: true` にすると、AI が生成したコマンドは実行前に標準入力で確認を求められます。

## 使い方
1. **インストール**  
   上記のテンプレートをそのままターミナルに貼り付け、Enter キーを押すだけで `cowork` がインストールされます。

2. **設定の確認**  
   `cat ~/.claude/cowork.yaml` で内容が正しく書き込まれているか確認します。

3. **AI に指示**  
   Claude Code のチャット画面で `cowork` を有効にした状態で指示を出すと、AI が生成したシェルコマンドが **サンドボックス** と **ユーザー確認** の2段階で安全に実行されます。

4. **実行**  
   AI が提示したコマンドを確認後、`y` と入力すれば実行されます。`n` と入力すればキャンセルできます。

## よくある質問

**Q1: `sandbox: true` だと実行できないコマンドがあります。**  
**A:** サンドボックスは安全性を最優先した設定です。`apt-get install` や `docker run` などシステムに大きな影響を与えるコマンドはブロックされます。必要に応じて一時的に `sandbox: false` に変更し、実行後は必ず元に戻すことを推奨します。

---

**Q2: `user_in_loop: true` をオフにしたいです。**  
**A:** 自動化したいシナリオがある場合は `user_in_loop: false` に変更できますが、**必ず**実行前にスクリプト内容を目視で確認してください。誤操作やデータ損失のリスクが高まります。

---

**Q3: `cowork` コマンドが見つからないと言われます。**  
**A:**  
1. `/usr/local/bin` が `PATH` に含まれているか確認：`echo $PATH`  
2. もし含まれていなければ、`export PATH=$PATH:/usr/local/bin` を `.bashrc` などに追記してください。  
3. 再度 `cowork --version` を実行してみてください。

---

**Q4: 設定ファイルの場所を変えたいです。**  
**A:** デフォルトは `~/.claude/cowork.yaml` ですが、環境変数 `CLAUDE_COWORK_CONFIG` に別パスを指定すればカスタマイズできます。例：`export CLAUDE_COWORK_CONFIG=$HOME/my_cowork.yaml`。

---

**Q5: Windows でも使えますか？**  
**A:** 現在 `cowork` は Linux/macOS のバイナリのみ提供されています。Windows で利用したい場合は WSL2 上で同様の手順を実行してください。

---

AI Conduit: https://www.youtube.com/@AI.Conduit