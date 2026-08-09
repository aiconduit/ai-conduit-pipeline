# Claude Codeターミナル設定で快適化 - 実践テンプレート

## この動画で学んだこと
Claude Codeのターミナルを快適にするために、`/terminal-setup`コマンドでターミナル設定を最適化し、`/vim`コマンドでVimモードを有効にする方法を学びました。これにより、エディタ操作の効率が大幅に向上します。

## すぐに使えるテンプレート

### 1. Claude Codeを起動してターミナル設定を最適化

```bash
# Claude Codeを起動
$ claude

# ターミナル設定を実行（Claude Code内で入力）
/terminal-setup

# 表示される設定オプションから選択：
# - カラーテーマの選択（ダーク/ライト）
# - フォントサイズの調整
# - キーバインドのカスタマイズ
# - スクロールバック行数の設定
```

### 2. Vimモードを有効化

```bash
# Claude Code内でVimモードを有効化
/vim

# これで以下のVimキーバインドが使用可能に：
# - h, j, k, l : カーソル移動
# - w, b : 単語単位で移動
# - 0, $ : 行頭・行末へ移動
# - gg, G : ファイル先頭・末尾へ移動
# - i : 挿入モードに切り替え
# - Esc : ノーマルモードに戻る
```

### 3. カスタム設定ファイル（~/.claude/settings.json）

```json
{
  "terminal": {
    "theme": "dark",
    "fontSize": 14,
    "scrollbackLines": 10000,
    "vimMode": true,
    "keyBindings": {
      "ctrl+p": "command-palette",
      "ctrl+n": "new-chat",
      "ctrl+s": "save-session"
    }
  },
  "editor": {
    "tabSize": 2,
    "wordWrap": true,
    "lineNumbers": true
  }
}
```

### 4. 便利なVimモードショートカット集

```bash
# ノーマルモードでの操作
# 移動系
h, j, k, l     # 左、下、上、右に移動
w, b           # 次の単語、前の単語へ移動
0, $           # 行頭、行末へ移動
gg, G          # ファイル先頭、末尾へ移動
Ctrl+d, Ctrl+u # 半ページ下、上へスクロール

# 編集系
i, a           # カーソル位置、後ろに挿入
x, dd          # 文字削除、行削除
yy, p          # 行コピー、貼り付け
u, Ctrl+r      # アンドゥ、リドゥ

# 検索系
/pattern       # 前方検索
?pattern       # 後方検索
n, N           # 次の検索結果、前の検索結果
```

## 使い方

1. **ターミナルを開いて** `claude` コマンドを実行し、Claude Codeを起動します
2. **`/terminal-setup` と入力**して、ターミナル設定ウィザードを起動します
3. **好みの設定を選択**（テーマ、フォントサイズ、スクロールバック行数など）
4. **`/vim` と入力**して、Vimモードを有効化します
5. **Vimキーバインドを試す**：`i`で挿入モード、`Esc`でノーマルモードに切り替え
6. **設定を永続化**したい場合は、`~/.claude/settings.json`に設定を保存

## よくある質問

**Q: Vimモードを無効に戻すにはどうすればいいですか？**
A: もう一度 `/vim` と入力すると、Vimモードのオン/オフを切り替えられます。または、`settings.json`の`"vimMode": false`に変更してください。

**Q: ターミナル設定をリセットしたい場合は？**
A: `/terminal-setup` を再度実行し、表示されるオプションから「リセット」または「デフォルトに戻す」を選択してください。

**Q: カスタムキーバインドを追加できますか？**
A: はい、`~/.claude/settings.json`の`keyBindings`セクションに追加できます。例：`"ctrl+e": "edit-file"`のように設定します。

**Q: Vimモードで日本語入力がうまくいかないのですが？**
A: 日本語入力時は、`i`で挿入モードに切り替えてから入力してください。ノーマルモードでは日本語入力が制限される場合があります。

---
AI Conduit: https://www.youtube.com/@AI.Conduit