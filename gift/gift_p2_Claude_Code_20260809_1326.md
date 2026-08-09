# Claude Codeで完全仮想マシンから安全な操作を実現 - 実践テンプレート

## この動画で学んだこと
Claude Codeのcomputer-use機能とdisposable macOS VMを組み合わせることで、ホスト環境を汚染せずに安全なAI操作を実現できます。隔離された環境でAIに自由に作業させるための完全なセットアップ手順を紹介します。

## すぐに使えるテンプレート

### 1. 開発環境の準備（ターミナルで実行）

```bash
# 開発ツール（Xcode Command Line Tools）をインストール
# これがないとHomebrewやコンパイラが使えない
xcode-select --install

# インストール確認
xcode-select -p
# 出力例: /Library/Developer/CommandLineTools
```

### 2. UTM（仮想マシン管理ツール）のインストール

```bash
# Homebrewがインストールされているか確認
brew --version

# なければHomebrewをインストール
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# UTMをインストール（macOS用仮想マシンアプリ）
brew install --cask utm

# インストール確認
ls /Applications/ | grep UTM
```

### 3. 仮想マシンの作成（UTM内で設定）

```bash
# UTMを起動
open /Applications/UTM.app

# 以下の操作をGUIで実行:
# 1. "+" ボタンをクリック
# 2. "Virtualize" を選択
# 3. "macOS" を選択
# 4. インストールするmacOSのバージョンを選択
# 5. メモリ: 4GB以上、CPU: 2コア以上を推奨
# 6. ディスク: 40GB以上を推奨
```

### 4. 仮想マシン内でのClaude Codeセットアップ

```bash
# 仮想マシン内のターミナルで実行

# Node.jsをインストール（Claude Codeの前提条件）
brew install node

# Claude Codeをインストール
npm install -g @anthropic-ai/claude-code

# バージョン確認
claude --version

# Claude Codeを起動（初回はログインが必要）
claude
```

### 5. computer-use機能の有効化

```bash
# Claude Code内でcomputer-useを有効化
# Claude Codeの設定ファイルを作成
mkdir -p ~/.claude
cat > ~/.claude/settings.json << 'EOF'
{
  "permissions": {
    "computer_use": true,
    "allow": [
      "Bash",
      "Read",
      "Write",
      "Edit"
    ]
  },
  "model": "claude-3-5-sonnet-20241022"
}
EOF

# 設定確認
cat ~/.claude/settings.json
```

### 6. 安全な操作のためのスクリプト

```bash
# 仮想マシンのスナップショット作成スクリプト
# 作業前に実行して、いつでも元の状態に戻せるようにする

#!/bin/bash
# snapshot.sh - UTM仮想マシンのスナップショットを作成

echo "=== UTM スナップショット作成 ==="

# UTMのCLIツールを使用（UTM 4.0以降）
UTMCTL="/Applications/UTM.app/Contents/MacOS/utmctl"

# 仮想マシンのリストを表示
$UTMCTL list

# スナップショットを作成（仮想マシン名を指定）
echo "スナップショットを作成する仮想マシン名を入力:"
read VM_NAME

$UTMCTL snapshot "$VM_NAME" "before-claude-$(date +%Y%m%d-%H%M%S)"
echo "✅ スナップショットを作成しました"
```

### 7. ワンクリックで安全な環境を起動するスクリプト

```bash
#!/bin/bash
# safe-claude.sh - 安全なClaude Code環境を起動

echo "=== 安全なClaude Code環境を起動します ==="

# 1. UTMを起動
open /Applications/UTM.app

# 2. 仮想マシンを起動（VM名を指定）
UTMCTL="/Applications/UTM.app/Contents/MacOS/utmctl"
$UTMCTL start "Claude-VM"

# 3. 起動待ち
echo "仮想マシンの起動を待っています..."
sleep 30

# 4. SSHで接続（事前にSSH設定が必要）
# ssh user@localhost -p 2222

echo "✅ 仮想マシンが起動しました"
echo "⚠️ 注意: この環境は使い捨てです。重要なデータは保存しないでください。"
```

### 8. 使い捨て環境のリセットスクリプト

```bash
#!/bin/bash
# reset-vm.sh - 仮想マシンを初期状態にリセット

echo "=== 仮想マシンをリセットします ==="

UTMCTL="/Applications/UTM.app/Contents/MacOS/utmctl"

# 仮想マシンを停止
$UTMCTL stop "Claude-VM"

# スナップショットから復元
echo "復元するスナップショットを選択:"
$UTMCTL list snapshots "Claude-VM"

# 最新のスナップショットに復元
$UTMCTL restore "Claude-VM" "before-claude-*"

echo "✅ 仮想マシンを初期状態に戻しました"
```

## 使い方

1. **開発環境の準備**: `xcode-select --install` を実行して開発ツールをインストール
2. **UTMのインストール**: `brew install --cask utm` で仮想マシン管理ツールを導入
3. **仮想マシンの作成**: UTMでmacOS VMを作成（メモリ4GB以上、ディスク40GB以上）
4. **VM内のセットアップ**: 仮想マシン内でNode.jsとClaude Codeをインストール
5. **computer-useの有効化**: 設定ファイルでcomputer-use機能を有効化
6. **ス