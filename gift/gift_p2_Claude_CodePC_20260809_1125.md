# Claude Codeで安全なPC操作を実現 - 実践テンプレート

## この動画で学んだこと
Claude Codeのcomputer-use機能をmacOS仮想マシン上で実行することで、ホストPCに影響を与えずに安全なAIエージェント操作を実現する方法を学びました。

## すぐに使えるテンプレート

### 1. UTMのインストールとmacOS VMの作成

```bash
# UTMのインストール（Homebrewを使用）
brew install --cask utm

# または公式サイトからダウンロード
# https://mac.getutm.app/
```

### 2. macOSゲストVMのセットアップ

```bash
# UTMを起動し、以下の手順でVMを作成
# 1. "Create a New Virtual Machine" をクリック
# 2. "Virtualize" を選択
# 3. "macOS" を選択
# 4. インストールするmacOSのバージョンを選択
# 5. リソースを割り当て（推奨: CPU 4コア以上、RAM 8GB以上）
# 6. ディスクサイズを設定（推奨: 64GB以上）
```

### 3. VM上でのClaude Codeセットアップ

```bash
# VM内のターミナルで実行

# Node.jsのインストール（Claude Codeの前提条件）
brew install node

# Claude Codeのインストール
npm install -g @anthropic-ai/claude-code

# バージョン確認
claude --version

# Claude Codeの起動
claude
```

### 4. computer-useの設定

```bash
# Claude Codeの設定ファイルを作成
mkdir -p ~/.claude
cat > ~/.claude/settings.json << 'EOF'
{
  "permissions": {
    "allow": [
      "ComputerUse",
      "Bash",
      "Read",
      "Write"
    ],
    "deny": [
      "NetworkAccess"
    ]
  },
  "computerUse": {
    "enabled": true,
    "safetyLevel": "strict",
    "screenshotInterval": 1000
  }
}
EOF
```

### 5. エージェント実行スクリプト

```bash
# エージェント実行用スクリプトを作成
cat > run_agent.sh << 'EOF'
#!/bin/bash

# Claude Codeエージェントを安全に実行するスクリプト

echo "=== Claude Code エージェント起動 ==="
echo "作業ディレクトリ: $(pwd)"
echo "実行日時: $(date)"

# Claude Codeを起動し、エージェントモードで実行
claude --dangerously-skip-permissions << 'PROMPT'
あなたは以下のタスクを実行してください：
1. 現在のディレクトリのファイル一覧を確認
2. 指定されたファイルの内容を分析
3. レポートを作成して保存

注意：システムファイルへの変更は行わないでください。
PROMPT

echo "=== エージェント実行完了 ==="
EOF

# 実行権限を付与
chmod +x run_agent.sh
```

### 6. VMスナップショットの自動化

```bash
# スナップショット作成スクリプト
cat > create_snapshot.sh << 'EOF'
#!/bin/bash

# UTM VMのスナップショットを作成するスクリプト
# 使用方法: ./create_snapshot.sh <VM名>

VM_NAME="${1:-macOS-VM}"
SNAPSHOT_NAME="snapshot-$(date +%Y%m%d-%H%M%S)"

echo "VM: $VM_NAME のスナップショットを作成中..."
utmctl snapshot "$VM_NAME" "$SNAPSHOT_NAME"

echo "スナップショット作成完了: $SNAPSHOT_NAME"
echo "復元コマンド: utmctl restore \"$VM_NAME\" \"$SNAPSHOT_NAME\""
EOF

chmod +x create_snapshot.sh
```

## 使い方

1. **UTMのインストール**: HomebrewでUTMをインストールし、macOSゲストVMを作成します
2. **VMのセットアップ**: 十分なリソース（CPU 4コア以上、RAM 8GB以上）を割り当てます
3. **Claude Codeのインストール**: VM内でNode.jsとClaude Codeをインストールします
4. **設定ファイルの配置**: `settings.json`を`~/.claude/`に配置してcomputer-useを有効化します
5. **エージェントの実行**: `run_agent.sh`を実行して安全な環境でエージェントを起動します
6. **スナップショット管理**: 定期的にスナップショットを作成し、問題発生時に復元できるようにします

## よくある質問

**Q: VMのパフォーマンスが遅い場合はどうすればいいですか？**
A: VMの設定でCPUコア数とRAMを増やしてください。また、SSDストレージを使用し、VMのディスクイメージを高速なストレージに配置することをお勧めします。

**Q: computer-useが動作しない場合は？**
A: 以下の点を確認してください：
- Claude Codeが最新版であること（`npm update -g @anthropic-ai/claude-code`）
- `settings.json`のパーミッション設定が正しいこと
- VMの画面解像度が適切に設定されていること

**Q: ホストPCとのファイル共有は可能ですか？**
A: はい、UTMの共有フォルダ機能を使用できます。ただし、セキュリティを考慮して、読み取り専用での共有をお勧めします。

**Q: スナップショットの保存場所はどこですか？**
A: デフォルトでは`~/Library/Containers/com.utmapp.UTM/Data/Images/`に保存されます。定期的にバックアップを取ることをお勧めします。

---
AI Conduit: https://www.youtube.com/@AI.Conduit