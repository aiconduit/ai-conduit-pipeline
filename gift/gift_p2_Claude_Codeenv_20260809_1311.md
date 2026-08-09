# Claude Codeのenvで環境変数を一元管理 - 実践テンプレート

## この動画で学んだこと
Claude Codeの`settings.json`の`env`フィールドを使うことで、プロジェクトごとの環境変数を一元管理し、毎回の設定入力を省略できます。

## すぐに使えるテンプレート

### 1. プロジェクト用設定ファイル（`.claude/settings.json`）

```json
{
  "env": {
    // ここに環境変数を追加していく
    "API_KEY": "your-api-key-here",
    "DATABASE_URL": "postgresql://user:password@localhost:5432/mydb",
    "NODE_ENV": "development",
    "LOG_LEVEL": "debug",
    "CUSTOM_VAR": "custom-value"
  }
}
```

### 2. ユーザー全体用設定ファイル（`~/.claude/settings.json`）

```json
{
  "env": {
    // 全プロジェクト共通の環境変数
    "GITHUB_TOKEN": "your-github-token",
    "OPENAI_API_KEY": "your-openai-key",
    "DEFAULT_REGION": "ap-northeast-1"
  }
}
```

### 3. 環境変数を確認するコマンド

```bash
# Claude Code内で環境変数を確認
claude

# 設定が反映されているか確認
echo $API_KEY
echo $DATABASE_URL
```

## 使い方

1. **プロジェクトのルートディレクトリ**に`.claude`フォルダを作成します
   ```bash
   mkdir -p .claude
   ```

2. **`.claude/settings.json`** を作成し、上記のテンプレートをコピー&ペーストします

3. **環境変数を追加**したい場合は、`env`フィールドにキーと値を追加します

4. **Claude Codeを再起動**して、設定を反映させます

5. **動作確認**：`echo $環境変数名` で値が表示されることを確認します

## よくある質問

**Q: プロジェクトごとに異なる環境変数を設定できますか？**
A: はい、`.claude/settings.json`はプロジェクトのルートに置くことで、そのプロジェクト専用の設定として機能します。ユーザー全体の設定は`~/.claude/settings.json`に置くことで、全プロジェクトに適用されます。

**Q: 環境変数が反映されない場合はどうすればいいですか？**
A: Claude Codeを完全に再起動してください。また、JSONの構文エラーがないか確認し、ダブルクォートの閉じ忘れやカンマの付け忘れに注意してください。

**Q: 機密情報を設定ファイルに書いても安全ですか？**
A: `.claude/settings.json`は`.gitignore`に追加して、リポジトリにコミットしないようにしてください。機密情報は環境変数ファイル（`.env`）やシークレット管理ツールの使用を検討してください。

---
AI Conduit: https://www.youtube.com/@AI.Conduit