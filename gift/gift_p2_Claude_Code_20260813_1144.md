# Claude Codeで安全にブラウザ操作 - 実践テンプレート

## この動画で学んだこと
Claude Code の **computer‑use** エージェントをサンドボックスモードで実行すれば、VM 内で安全にブラウザ操作やファイル操作ができます。macOS VM は **UTM** を Homebrew で簡単にインストールできます。

---

## すぐに使えるテンプレート

### 1️⃣ Homebrew で UTM（macOS VM）をインストール
```bash
# Homebrew がインストールされていない場合は公式サイトの手順でインストールしてください
# UTM を macOS VM 用にインストール
brew install --cask utm
```

### 2️⃣ Claude Code の computer‑use エージェント設定
> **.claude/agents/computer_use.md** を作成（または既存ファイルを編集）し、以下の内容を貼り付けて保存してください。

```markdown
# computer_use エージェント設定
# -------------------------------------------------
# 公式ドキュメント: https://docs.anthropic.com/claude/code/computer-use
# -------------------------------------------------

# エージェントの基本情報
name: computer_use
description: |
  Claude が VM 内でブラウザ操作やファイル操作を行うためのエージェントです。
  サンドボックスモードを有効にすることで、ホストマシンへの影響を防ぎます。

# -------------------------------------------------
# ★ 重要 ★  サンドボックスモードを有効化
# -------------------------------------------------
sandbox: true   # ← ここを true にすると VM 内だけで動作します

# エージェントが利用できるツール（必要に応じて追加）
tools:
  - name: web_browser
    description: "Web ブラウザでページを閲覧・検索します"
  - name: file_system
    description: "VM 内のファイルを読み書きします"

# デフォルトで有効にしたいオプション（任意）
default_options:
  max_steps: 30          # 1 セッションあたりの最大ステップ数
  timeout_seconds: 300  # タイムアウト（秒）

# -------------------------------------------------
# ここから下はカスタマイズ可能です
# -------------------------------------------------
# 例: 特定の環境変数を渡したいとき
# env:
#   DISPLAY: ":0"
```

### 3️⃣ VM 内でエージェントを起動
UTM で macOS VM を起動したら、ターミナルを開き以下を実行します。

```bash
# 事前に Python と Claude の SDK がインストールされていることを前提とします
# 例: pip install anthropic
python run_agent.py --agent computer_use
```

> **ポイント**  
> - `run_agent.py` は Claude Code の公式リポジトリに同梱されているスクリプトです。  
> - `--agent computer_use` で先ほど作成した設定ファイルを指定しています。

---

## 使い方

1. **UTM のインストール**  
   `brew install --cask utm` を実行し、macOS VM を作成・起動します。

2. **エージェント設定ファイルを作成**  
   上記の `computer_use.md` を **.claude/agents/** ディレクトリに保存します。  
   `sandbox: true` が必ず入っていることを確認してください。

3. **VM 内で Python 環境を整える**  
   ```bash
   # 例: Python 3.11 と Claude SDK のインストール
   brew install python
   pip install anthropic
   ```

4. **エージェントを起動**  
   ```bash
   python run_agent.py --agent computer_use
   ```
   起動後、Claude が指示した通りにブラウザやファイル操作が行われます。

5. **結果を確認**  
   エージェントが生成したログやスクリーンショットは VM の `~/claude_output/` に保存されます。必要に応じてホストへコピーしてください。

---

## よくある質問

**Q1: 「sandbox: true」を入れ忘れたらどうなりますか？**  
**A:** サンドボックスが無効になると、Claude がホストマシンのファイルやネットワークに直接アクセスできる可能性があります。セキュリティ上のリスクが高まるため、必ず `sandbox: true` を設定してください。

---

**Q2: macOS VM が起動しないときの対処法は？**  
**A:**  
1. UTM のバージョンが最新か確認（`brew upgrade utm`）。  
2. VM の設定で「CPU コア数」や「メモリ」を増やす。  
3. macOS のインストールイメージ（.iso）を公式サイトから再取得し、再作成。

---

**Q3: `run_agent.py` が見つからない場合は？**  
**A:** Claude Code の公式リポジトリ（https://github.com/anthropic/claude-code）から `run_agent.py` をダウンロードし、プロジェクトのルートに配置してください。

---

**Q4: エージェントが途中で止まってしまうのはなぜ？**  
**A:**  
- `max_steps` が足りない → `default_options.max_steps` を増やす。  
- タイムアウト → `default_options.timeout_seconds` を長く設定。  
- VM のリソース不足 → CPU・メモリを増やす。

---

**Q5: 日本語のコメントが表示されないのはなぜ？**  
**A:** Claude の出力は UTF‑8 でエンコードされます。ターミナルやエディタの文字コード設定が UTF‑8 になっているか確認してください。

---

### 参考リンク
- **AI Conduit（動画チャンネル）**: https://www.youtube.com/@AI.Conduit  
- **Claude Code 公式ドキュメント**: https://docs.anthropic.com/cla