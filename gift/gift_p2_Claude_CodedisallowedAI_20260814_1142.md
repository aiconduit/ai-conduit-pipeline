# Claude Code AIレビュー用サブエージェント - 実践テンプレート

## この動画で学んだこと
Claude Code の **disallowed ツール** をサブエージェントのフロントマターで指定することで、AIレビューを「読み取り専用」状態にし、コードの変更や実行系コマンドをブロックできます。

## すぐに使えるテンプレート
以下の内容を **`review_agent.toml`**（または任意の名前）というファイルに保存してください。  
※拡張子は **`.toml`** が推奨ですが、Claude Code が認識できる形式であれば `.yaml` でも可です。

```toml
# ------------------------------------------------------------
# review_agent.toml
# Claude Code 用サブエージェント設定
# AIレビューを「読み取り専用」にし、以下のツールを無効化します
# ------------------------------------------------------------

# エージェント全体のメタ情報
[agent]
name = "review-only-agent"
description = """
このエージェントはコードレビュー専用です。
コードの実行、ファイル書き込み、ネットワークアクセス等はすべて禁止します。
"""

# 禁止したいツール（disallowed）を列挙
# ここに書かれたツールは Claude が呼び出せません
[disallowed_tools]
# 例: `bash`、`python`、`node` など実行系コマンド
bash = true
python = true
node = true
ruby = true
perl = true
# ファイル操作系
write_file = true
delete_file = true
move_file = true
# ネットワーク系
http = true
curl = true
wget = true

# 必要に応じて許可したいツールは `allowed_tools` に列挙
# ここではデフォルトで許可されている `read_file` のみ残す
[allowed_tools]
read_file = true

# エージェントが実行できるプロンプト例（任意）
[prompt]
system = """
あなたはコードレビューアシスタントです。以下のコードを読み取り、改善点・バグ指摘・ベストプラクティスの提案を行ってください。
実行やファイル書き込みは一切行わないでください。
"""
```

## 使い方
1. **ファイル保存**  
   上記テンプレートを `review_agent.toml` としてプロジェクトのルート（または任意のディレクトリ）に保存します。

2. **Claude Code にサブエージェントを登録**  
   ```bash
   # Claude CLI (例) でサブエージェントをロード
   claude agents add --file review_agent.toml
   ```
   *CLI が無い場合は、Claude Code の UI から「サブエージェント」→「インポート」→`review_agent.toml` を選択してください。

3. **レビューを開始**  
   ```bash
   # 例: 現在のディレクトリのコード全体をレビュー
   claude review --agent review-only-agent .
   ```
   もしくは UI で「エージェントを選択」→`review-only-agent` を選び、対象ファイルをドラッグ＆ドロップします。

4. **結果を確認**  
   Claude がコードの読み取りとコメントだけを行い、実行系コマンドはエラーになることを確認してください。

## よくある質問

**Q1. すべてのツールを禁止したい場合はどうすればいいですか？**  
A: `disallowed_tools` にすべての項目を `true` に設定し、`allowed_tools` を空にすれば実質的に「読み取り専用」になります。例:
```toml
[disallowed_tools]
* = true   # すべてのツールを禁止（Claude がサポートしている全ツールが対象）

[allowed_tools]   # 何も書かない＝全禁止
```

**Q2. 特定のツールだけ許可したいときは？**  
A: `allowed_tools` に許可したいツール名と `true` を記述し、`disallowed_tools` からは削除してください。例:
```toml
[allowed_tools]
read_file = true
search = true   # 例: 文字列検索ツールだけ許可
```

**Q3. サブエージェントが正しく読み込まれない場合は？**  
A:  
1. ファイルの拡張子が `.toml`（または Claude が認識できる形式）か確認。  
2. YAML/TOML の構文エラーがないか `toml-cli validate review_agent.toml` などで検証。  
3. CLI/UI のバージョンが最新か確認（古いバージョンでは `disallowed_tools` がサポートされていないことがあります）。

**Q4. 既存のエージェント設定にこのテンプレートをマージしたい**  
A: 既存の `[agent]` セクションはそのまま残し、`[disallowed_tools]` と `[allowed_tools]` のブロックだけを追記すれば OK です。重複したキーがある場合は後に書いた方が優先されます。

**Q5. 何か注意点はありますか？**  
A:  
- `write_file` 系のツールを禁止しても、Claude が「コメント」や「提案」だけを出力するので、実際のファイルは手動で編集してください。  
- ネットワーク系ツール (`http`, `curl`, `wget`) を禁止すると、外部 API への問い合わせやコード検索ができなくなるので、必要に応じて個別に許可してください。

---

**AI Conduit**: https://www.youtube.com/@AI.Conduit  
このテンプレートは、動画「Claude CodeのdisallowedツールでAIレビューが読み取り専用になった」で紹介された手順をそのまま再現しています。ぜひコピー&ペーストして、すぐに安全なコードレビュー環