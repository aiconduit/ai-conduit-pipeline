# Claude Codeターミナル設定で快適化 - 実践テンプレート

## この動画で学んだこと
Claude Codeのターミナルを快適にするために、`/terminal-setup`コマンドでターミナル設定を最適化し、`/vim`コマンドでVimモードを有効にする方法を学びました。これにより、エディタ操作の効率が大幅に向上します。

## すぐに使えるテンプレート

### 1. Claude Codeを起動してターミナル設定を実行

```bash
# Claude Codeを起動
$ claude

# ターミナル設定を最適化（Claude Code内で実行）
/terminal-setup

# Vimモードを有効化（Claude Code内で実行）
/vim
```

### 2. ターミナル設定のカスタマイズ例

```bash
# ターミナル設定ファイル（~/.claude/settings.json）
{
  "terminal": {
    "theme": "dark",
    "fontSize": 14,
    "lineHeight": 1.5,
    "cursorStyle": "block",
    "scrollback": 10000,
    "wordWrap": true,
    "keybindings": {
      "copy": "Ctrl+Shift+C",
      "paste": "Ctrl+Shift+V",
      "clear": "Ctrl+L"
    }
  },
  "vim": {
    "enabled": true,
    "insertMode": "jj",
    "leader": "space",
    "useSystemClipboard": true
  }
}
```

### 3. Vimモードの便利なキーバインド

```bash
# Vimモードでの主要なキーバインド
# ノーマルモード
# - j/k: 上下移動
# - h/l: 左右移動
# - w/b: 単語移動
# - 0/$: 行頭/行末
# - gg/G: ファイル先頭/末尾
# - dd: 行削除
# - yy: 行コピー
# - p: 貼り付け
# - u: アンドゥ
# - Ctrl+r: リドゥ
# - /: 検索
# - :w: 保存
# - :q: 終了

# インサートモード
# - i: カーソル位置に挿入
# - a: カーソル後ろに挿入
# - o: 新しい行を追加
# - Esc: ノーマルモードに戻る
```

### 4. ターミナル設定の確認とトラブルシューティング

```bash
# 現在の設定を確認
/terminal-setup --status

# 設定をリセット
/terminal-setup --reset

# Vimモードの状態確認
/vim --status

# ヘルプを表示
/help terminal-setup
/help vim
```

## 使い方
1. ターミナルで `$ claude` と入力してClaude Codeを起動します
2. Claude Codeのプロンプトで `/terminal-setup` と入力してターミナル設定を実行します
3. 次に `/vim` と入力してVimモードを有効にします
4. 必要に応じて `~/.claude/settings.json` を編集して設定をカスタマイズします
5. Vimモードのキーバインドを練習して、効率的な操作を身につけます

## よくある質問
Q: Vimモードを無効にするにはどうすればいいですか？
A: `/vim` コマンドをもう一度実行するか、`~/.claude/settings.json` の `"vim": {"enabled": false}` に変更してください。

Q: ターミナル設定を元に戻すには？
A: `/terminal-setup --reset` コマンドを実行すると、デフォルト設定に戻ります。

Q: Vimモードで日本語入力ができない場合は？
A: 日本語入力が必要な場合は、`~/.claude/settings.json` の `"vim": {"useSystemClipboard": true}` を設定し、IMEとの連携を確認してください。

Q: 設定ファイルの場所はどこですか？
A: 設定ファイルは `~/.claude/settings.json` にあります。存在しない場合は、`/terminal-setup` を実行すると自動的に作成されます。

---
AI Conduit: https://www.youtube.com/@AI.Conduit