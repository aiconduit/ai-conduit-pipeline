# Claude CodeでPDF解析スキルを即導入する方法 - 実践テンプレート

## この動画で学んだこと
Claude CodeでPDFを解析する際、毎回プロンプトを工夫する必要がなくなります。`TerminalSkills`の`pdf-analyzer`スキルをインストールするだけで、Claude CodeがPDF解析の手順を自動認識して実行してくれます。

## すぐに使えるテンプレート

### 1. PDF解析スキルのインストール

```bash
# ターミナルで以下のコマンドを実行するだけ
npx terminal-skills install pdf-analyzer
```

### 2. インストール確認

```bash
# スキルが正しく保存されたか確認
ls -la .claude/skills/
# 期待される出力: pdf-analyzer.md が存在する

# スキルの内容を確認
cat .claude/skills/pdf-analyzer.md
```

### 3. Claude CodeでのPDF解析プロンプト例

```text
# このスキルを有効にしてPDFを解析してください
@pdf-analyzer 解析したいPDFファイルのパスを指定してください

# または、スキルを明示的に呼び出さずに自然に依頼する
このPDFを解析して、要約と主要なポイントを抽出してください: ./path/to/document.pdf
```

### 4. カスタム設定（必要に応じて）

```bash
# スキルの設定をカスタマイズする場合
# .claude/skills/pdf-analyzer.md を編集して、解析の詳細設定を変更できます

# 例: 解析時の言語設定や出力形式を変更したい場合
# pdf-analyzer.md 内の設定を日本語出力にカスタマイズ
```

## 使い方

1. **ターミナルを開く**: Claude Codeを実行しているプロジェクトディレクトリでターミナルを開きます
2. **スキルをインストール**: `npx terminal-skills install pdf-analyzer` を実行します
3. **確認**: `.claude/skills/pdf-analyzer.md` が作成されたことを確認します
4. **Claude Codeを再起動**: スキルを認識させるため、Claude Codeセッションを再起動します
5. **PDF解析を依頼**: Claude CodeにPDFファイルのパスを指定して解析を依頼します

## よくある質問

**Q: インストール時にエラーが発生する場合は？**
A: Node.jsがインストールされているか確認してください。`node -v` でバージョンが表示されない場合は、Node.jsをインストールしてから再試行してください。

**Q: スキルが認識されない場合は？**
A: Claude Codeを再起動してみてください。また、`.claude/skills/` ディレクトリが正しい場所にあるか確認してください。プロジェクトのルートディレクトリに配置する必要があります。

**Q: 複数のPDFを一括解析できますか？**
A: はい、Claude Codeに複数のファイルパスを指定することで一括解析が可能です。ただし、大量のファイルの場合は処理時間に注意してください。

**Q: スキルをアンインストールする方法は？**
A: `.claude/skills/pdf-analyzer.md` ファイルを削除するだけでアンインストールできます。

---
AI Conduit: https://www.youtube.com/@AI.Conduit