# Claude Codeで完全仮想マシンから安全な操作を実現 - 実践テンプレート

## この動画で学んだこと
Claude Codeのcomputer-use機能とdisposable macOS VMを組み合わせることで、ホスト環境を汚染せずに安全なAI操作を実現できます。隔離された環境でClaudeに自由に作業させるための完全テンプレートです。

## すぐに使えるテンプレート

### 1. 開発環境の準備（ターミナルで実行）

```bash
# ステップ1: Xcode Command Line Toolsのインストール
# これがないとHomebrewやビルドツールが動作しません
xcode-select --install

# インストール確認（バージョンが表示されればOK）
xcode-select -p
# 出力例: /Library/Developer/CommandLineTools

# ステップ2: Homebrewのインストール（未導入の場合）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# ステップ3: UTM（仮想マシン管理ツール）のインストール
brew install --cask utm

# インストール確認
brew list --cask utm
```

### 2. Claude Codeのセットアップ

```bash
# Claude Codeのインストール（Anthropic公式）
npm install -g @anthropic-ai/claude-code

# バージョン確認
claude --version

# 認証（初回のみ）
claude login
```

### 3. 仮想マシン作成スクリプト

```bash
#!/bin/bash
# ファイル名: setup_vm.sh
# 使い方: chmod +x setup_vm.sh && ./setup_vm.sh

set -e  # エラーで即停止

echo "=== macOS VMセットアップ開始 ==="

# UTMがインストールされているか確認
if ! command -v utmctl &> /dev/null; then
    echo "UTMがインストールされていません。インストールします..."
    brew install --cask utm
fi

# VM名を設定
VM_NAME="Claude-Sandbox"

# 既存のVMをチェック
if utmctl list | grep -q "$VM_NAME"; then
    echo "既存のVMが見つかりました: $VM_NAME"
    echo "起動します..."
    utmctl start "$VM_NAME"
else
    echo "新しいVMを作成します: $VM_NAME"
    echo "※ UTM GUIを開いて、macOS VMを手動で作成してください"
    echo "推奨設定:"
    echo "  - OS: macOS Sonoma"
    echo "  - RAM: 4GB以上"
    echo "  - ディスク: 40GB以上"
    echo "  - CPU: 2コア以上"
    open -a UTM
fi

echo "=== セットアップ完了 ==="
```

### 4. Claude CodeをVM内で実行する設定

```bash
#!/bin/bash
# ファイル名: run_claude_in_vm.sh
# VM内でClaude Codeを安全に実行するスクリプト

set -e

VM_NAME="Claude-Sandbox"

# VMが起動しているか確認
if ! utmctl list | grep -q "$VM_NAME"; then
    echo "VMを起動しています..."
    utmctl start "$VM_NAME"
    sleep 10  # 起動待機
fi

# VMのIPアドレスを取得
VM_IP=$(utmctl ip "$VM_NAME")
echo "VM IP: $VM_IP"

# SSHでVMに接続してClaude Codeを実行
# ※ VM側でSSHサーバーを有効にしておく必要があります
ssh user@"$VM_IP" << 'EOF'
    # VM内で実行されるコマンド
    echo "=== Claude CodeをVM内で起動 ==="
    
    # Claude Codeのインストール確認
    if ! command -v claude &> /dev/null; then
        echo "Claude Codeをインストール中..."
        npm install -g @anthropic-ai/claude-code
    fi
    
    # 作業ディレクトリ作成
    mkdir -p ~/claude-workspace
    cd ~/claude-workspace
    
    # Claude Codeを起動（computer-useモード）
    claude --computer-use
    
    echo "=== Claude Code終了 ==="
EOF

# セッション終了後、VMをシャットダウン（disposable環境）
echo "VMをシャットダウンします..."
utmctl stop "$VM_NAME"
echo "安全にVMを破棄しました"
```

### 5. 自動クリーンアップ設定

```bash
#!/bin/bash
# ファイル名: cleanup_vm.sh
# 使い終わったVMを自動で削除するスクリプト

set -e

VM_NAME="Claude-Sandbox"

echo "=== VMクリーンアップ開始 ==="

# VMをシャットダウン
if utmctl list | grep -q "$VM_NAME"; then
    echo "VMをシャットダウン中..."
    utmctl stop "$VM_NAME"
    sleep 5
fi

# VMを削除（完全に破棄）
echo "VMを削除中..."
utmctl delete "$VM_NAME"

# 関連ファイルの削除
echo "関連ファイルを削除中..."
rm -rf ~/Library/Application\ Support/UTM/"$VM_NAME".utm

echo "=== クリーンアップ完了 ==="
echo "新しいVMを作成するには: ./setup_vm.sh を実行"
```

### 6. ワンライナー実行（すべてを自動化）

```bash
# 完全自動化スクリプト
# ファイル名: auto_sandbox.sh

#!/bin/bash
set -e

echo "=== Claude Code Sandbox環境 自動セットアップ ==="

# 1. 環境チェック
echo "1. 環境チェック..."
if ! command -v brew &> /dev/null; then
    echo "Homebrewをインストール中..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# 2. 必要なツールのインストール
echo "2. 必要なツールをインストール..."
xcode-select --install 2>/dev/null || echo "Xcode CLTは既にインストール済み"
brew install --cask utm 2>/dev/null || echo "UTMは既にインストール