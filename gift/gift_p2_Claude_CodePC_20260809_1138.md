# Claude Codeで安全なPC操作を実現 - 実践テンプレート

## この動画で学んだこと
Claude Codeのcomputer-use機能をmacOS仮想マシン上で実行することで、ホストPCに影響を与えずに安全なAIエージェント操作を実現する方法を学びました。

## すぐに使えるテンプレート

### 1. UTMのインストール（Homebrewを使用）

```bash
# Homebrewがインストールされているか確認
brew --version

# UTMをインストール
brew install --cask utm

# インストール確認
utm --version
```

### 2. macOSゲストVMの作成（UTM設定）

```bash
# UTMを起動
open -a UTM

# 以下の設定で新しいVMを作成
# 1. 「+」ボタンをクリック
# 2. 「Virtualize」を選択
# 3. 「macOS」を選択
# 4. インストール用のmacOSイメージを選択
# 5. リソース設定:
#    - CPU: 4コア以上
#    - メモリ: 8GB以上
#    - ストレージ: 64GB以上
```

### 3. ゲストVM内でのClaude Codeセットアップ

```bash
# ゲストVM内でターミナルを開き、Node.jsをインストール
brew install node

# Claude Codeをインストール
npm install -g @anthropic-ai/claude-code

# バージョン確認
claude --version

# Claude Codeを起動
claude
```

### 4. computer-use設定ファイル

```json
// ~/.claude/settings.json
{
  "permissions": {
    "computer_use": {
      "enabled": true,
      "allow_screenshots": true,
      "allow_mouse_control": true,
      "allow_keyboard_control": true,
      "restrict_to_vm": true
    }
  },
  "security": {
    "sandbox_mode": "strict",
    "network_access": "restricted"
  }
}
```

### 5. エージェント実行スクリプト

```bash
#!/bin/bash
# claude-vm-agent.sh - VM内でClaude Codeエージェントを安全に実行

echo "=== Claude Code VMエージェント開始 ==="

# 作業ディレクトリの設定
WORK_DIR="$HOME/claude-workspace"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Claude Codeを対話モードで起動
claude --dangerously-skip-permissions \
  --allowedTools "Bash,Read,Write,ComputerUse" \
  --model claude-sonnet-4-20250514

echo "=== エージェント終了 ==="
```

### 6. ホストPCとのファイル共有設定

```bash
# UTMの共有フォルダ設定
# UTM > VM設定 > 共有 > フォルダ追加
# ホスト側: ~/shared
# ゲスト側: /mnt/shared

# ゲストVM内で共有フォルダをマウント
mkdir -p /mnt/shared
mount -t 9p -o trans=virtio shared /mnt/shared

# 共有フォルダの確認
ls -la /mnt/shared
```

## 使い方

1. **UTMをインストール**: HomebrewでUTMをインストールし、macOSゲストVMを作成します
2. **VMのセットアップ**: ゲストVM内でNode.jsとClaude Codeをインストールします
3. **設定ファイルの配置**: `settings.json`を`~/.claude/`ディレクトリに配置します
4. **エージェントの実行**: `claude-vm-agent.sh`スクリプトを実行して、安全な環境でエージェントを起動します
5. **ファイル共有**: 必要に応じてホストPCとのファイル共有を設定します

## よくある質問

**Q: なぜ仮想マシンを使う必要があるのですか？**
A: Claude Codeのcomputer-use機能はPCを直接操作するため、誤操作や予期しない変更のリスクがあります。仮想マシン内で実行することで、ホストPCへの影響を完全に遮断し、安全にテストや自動化を実行できます。

**Q: パフォーマンスが遅くならないですか？**
A: 多少のオーバーヘッドはありますが、UTMはApple Siliconでネイティブに動作するため、十分なパフォーマンスが得られます。CPUを4コア以上、メモリを8GB以上割り当てることで、実用的な速度で動作します。

**Q: ホストPCのファイルにアクセスするには？**
A: UTMの共有フォルダ機能を使用します。ホスト側のフォルダをゲストVMにマウントすることで、安全にファイルをやり取りできます。ただし、共有フォルダへの書き込みは慎重に行ってください。

**Q: 無料で利用できますか？**
A: はい、UTMはオープンソースで無料です。Claude CodeのAPI利用料金のみが必要です。macOSゲストVMの作成には、Appleの利用規約に従う必要があります。

---
AI Conduit: https://www.youtube.com/@AI.Conduit