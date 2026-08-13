# Claude Codeで安全にブラウザ操作 - 実践テンプレート

## この動画で学んだこと
Claude Code の **computer‑use エージェント**をサンドボックスモードで実行し、macOS 仮想マシン（UTM）上で安全にブラウザ操作を自動化できます。

## すぐに使えるテンプレート
以下のファイル・コマンドをそのままコピーして、端末やエディタに貼り付けてください。

### 1️⃣ macOS VM のインストール（UTM）
```bash
# Homebrew がインストールされていない場合は先にインストールしてください
# https://brew.sh/

# UTM（macOS 用仮想マシン）を Homebrew Cask でインストール
brew install --cask utm
```

### 2️⃣ Claude Code エージェント設定ファイル
**パス**: `.claude/agents/computer_use.md`  
**内容**（既存の内容がある場合は追記してください）:

```markdown
# computer_use エージェント設定
# -------------------------------------------------
# 公式ドキュメント: https://docs.anthropic.com/claude/computer-use
# -------------------------------------------------

# エージェントをサンドボックスモードで実行し、ホスト OS への直接アクセスを防止します
sandbox: true

# （任意）エージェントの動作制限やタイムアウト設定
# max_steps: 50          # 1 セッションあたりの最大ステップ数
# timeout_seconds: 300  # タイムアウト（秒）

# ここに他のカスタムプロンプトや設定を書き込めます
```

### 3️⃣ エージェント実行コマンド（VM 内）
UTM で起動した macOS VM にログインし、以下を実行します。

```bash
# 事前に Python と Claude の SDK がインストールされていることを前提とします
# 例: pip install anthropic

# エージェントを起動
python run_agent.py
```

> **※** `run_agent.py` は Claude Code のリポジトリに同梱されているスクリプトです。  
> もしまだ取得していない場合は、リポジトリをクローンしてください。
```bash
git clone https://github.com/anthropic/claude-code.git
cd claude-code
```

## 使い方
1. **UTM のインストール**  
   ターミナルで `brew install --cask utm` を実行し、macOS VM を作成・起動します。

2. **設定ファイルの作成**  
   プロジェクトのルートに `.claude/agents/computer_use.md` を作成し、上記の **sandbox: true** 設定を貼り付けます。

3. **VM 内で Python スクリプトを実行**  
   VM にログインし、`run_agent.py`（または自作スクリプト）を `python` コマンドで起動します。  
   エージェントはサンドボックス内でブラウザを操作し、ホスト OS への影響を最小化します。

4. **結果を確認**  
   エージェントの標準出力やログファイルに、実行された操作や取得したデータが出力されます。必要に応じて結果をローカルにコピーしてください。

## よくある質問

**Q1: sandbox モードを無効にしたい場合はどうすればいいですか？**  
A: `sandbox: true` を `sandbox: false` に変更するか、行自体を削除してください。ただし、サンドボックスを外すとホスト OS への直接アクセスが可能になるため、セキュリティリスクが高まります。

---

**Q2: UTM 以外の仮想化ツールでも動作しますか？**  
A: 基本的には同じ Linux/macOS 環境であれば動作しますが、`run_agent.py` が期待するファイルパスや権限が異なる場合があります。UTM は macOS ユーザー向けに公式で推奨されているので、まずは UTM で試すことをおすすめします。

**Q3: `run_agent.py` が見つからない／エラーになる場合は？**  
A: リポジトリが正しくクローンされているか確認し、Python の仮想環境 (venv) を作成して依存パッケージをインストールしてください。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # 例: requirements.txt がある場合
```

**Q4: サンドボックス内でファイルを永続化したいです。**  
A: VM の共有フォルダ（例: `/Users/Shared`）を利用し、エージェントからそのパスに出力すれば、VM を再起動してもデータが残ります。

---

AI Conduit: https://www.youtube.com/@AI.Conduit