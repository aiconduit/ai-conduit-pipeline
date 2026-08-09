# Claude CodeでPDF解析スキルを即導入する方法 - 実践テンプレート

## この動画で学んだこと
Claude CodeでPDFを解析する際、毎回プロンプトを工夫する必要がなくなります。**TerminalSkillsのpdf-analyzerスキル**をインストールするだけで、Claude Codeが自動的にPDF解析の手順を理解し、最適な方法で処理してくれます。

## すぐに使えるテンプレート

### 1. PDF解析スキルのインストール

```bash
# ターミナルで以下のコマンドを実行するだけ
npx terminal-skills install pdf-analyzer
```

### 2. インストール確認

```bash
# スキルが正しくインストールされたか確認
ls -la .claude/skills/
# 以下のファイルが存在すれば成功
# pdf-analyzer.md
```

### 3. スキルの内容確認（任意）

```bash
# スキルの内容を確認したい場合
cat .claude/skills/pdf-analyzer.md
```

### 4. Claude CodeでのPDF解析プロンプト例

```
# インストール後、Claude Codeで以下のように指示するだけ
このPDFを解析して要約してください: [ファイルパス]
```

## 使い方

1. **ターミナルを開く**
   - プロジェクトのルートディレクトリでターミナルを開きます

2. **スキルをインストール**
   ```bash
   npx terminal-skills install pdf-analyzer
   ```

3. **Claude Codeを起動**
   ```bash
   claude
   ```

4. **PDF解析を実行**
   - Claude CodeにPDFファイルのパスを指定して解析を依頼するだけ
   - 例: `このPDFを解析して: ./documents/sample.pdf`

5. **スキルの自動認識**
   - Claude Codeが`.claude/skills/pdf-analyzer.md`を自動的に読み込み
   - PDF解析のベストプラクティスに従って処理を実行

## よくある質問

**Q: インストールに失敗する場合は？**
A: Node.jsがインストールされているか確認してください。`node --version`で確認でき、v14以上が必要です。また、プロジェクトディレクトリに`.claude`フォルダが作成されるため、書き込み権限があることを確認してください。

**Q: 他のスキルもインストールできますか？**
A: はい、`npx terminal-skills install [スキル名]`で他のスキルもインストールできます。利用可能なスキル一覧は`npx terminal-skills list`で確認できます。

**Q: スキルをアンインストールするには？**
A: `.claude/skills/pdf-analyzer.md`ファイルを削除するだけです。または`npx terminal-skills uninstall pdf-analyzer`コマンドでも削除できます。

**Q: チームで共有するには？**
A: `.claude/skills/`ディレクトリをGitリポジトリに含めることで、チーム全体で同じスキルを共有できます。

---
AI Conduit: https://www.youtube.com/@AI.Conduit