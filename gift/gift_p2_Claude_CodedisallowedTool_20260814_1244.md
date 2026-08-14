# Claude Code disallowedTools テンプレート - 実践テンプレート

## この動画で学んだこと
Claude Code のスキル（エージェント）に `disallowedTools` を設定すると、Write・Edit ツールが誤って実行されてもコードが自動で書き換えられることを防げます。

## すぐに使えるテンプレート
以下の内容を **そのままコピー&ペースト** して、指定のパスに保存してください。  

```yaml
# .claude/agents/reviewer.md
---
name: reviewer               # エージェント名（任意の名前）
description: >-
  コードレビュー専用エージェント。Write と Edit ツールの使用を禁止し、
  予期せぬコード変更が起きないようにします。
disallowedTools:            # ← ここで禁止したいツールを列挙
  - Write
  - Edit
# ここに必要に応じて他の設定やプロンプトを追記できます
---

# 目的
- 変更が必要なときは手動で行う
- 自動生成されたコードが意図せず上書きされるリスクを排除

# 使用例
以下は簡単なプロンプト例です。  
```text
You are the reviewer. Please check the following Python file for style issues.
```
```

## 使い方
1. **ディレクトリを作成**  
   ```bash
   mkdir -p .claude/agents
   ```
2. **テンプレートファイルを作成**  
   上記のコードブロックを `reviewer.md` という名前で保存します。  
   ```bash
   cat > .claude/agents/reviewer.md <<'EOF'
   (上記 YAML 全体を貼り付け)
   EOF
   ```
3. **Claude Code を再起動**（または設定をリロード）  
   ```bash
   claude restart   # 例: Claude CLI の場合
   ```
4. **エージェントを呼び出す**  
   ```bash
   claude run reviewer --prompt "Please review my script."
   ```
   これで `Write` と `Edit` ツールは無効化され、コードは自動で書き換えられません。

## よくある質問

**Q1: `disallowedTools` に他のツールも追加できますか？**  
**A:** はい。`disallowedTools` に禁止したいツール名を配列で列挙すれば OK です。例: `- Search`、`- Execute` など。

**Q2: 逆に特定のツールだけ許可したい場合はどうすれば？**  
**A:** 現在の仕様では「許可リスト」ではなく「禁止リスト」方式です。許可したいツール以外をすべて `disallowedTools` に列挙してください。

**Q3: 変更が反映されないときは？**  
**A:**  
1. ファイルの保存場所が正しいか (`.claude/agents/reviewer.md`)  
2. YAML のインデントが正しいか（スペース2つが推奨）  
3. Claude Code のプロセスを再起動したか  

**Q4: `disallowedTools` が効かないバージョンがありますか？**  
**A:** 2024 年中頃以降の Claude Code 1.2.0 以降でサポートされています。古いバージョンを使用している場合はアップデートしてください。

---

AI Conduit: https://www.youtube.com/@AI.Conduit