# Claude Codeのsettings.jsonで環境変数一元管理 - 実践テンプレート

## この動画で学んだこと
`Claude Code` のプロジェクトルートに **.claude/settings.claude.json** を置くだけで、環境変数をコードから切り離して安全に管理できるようになります。

---

## すぐに使えるテンプレート

### 1. `settings.claude.json`（日本語コメント付き）

```json
{
  // -------------------------------------------------
  // ここにプロジェクト全体で使う環境変数を定義します
  // 例: APIキー、シークレットトークン、データベース接続情報など
  // -------------------------------------------------
  "env": {
    // 例: OpenAI の API キー
    "OPENAI_API_KEY": "your_secret_key_here",

    // 例: 任意の外部サービスのトークン
    "MY_API_TOKEN": "your_token_here"
  }
}
```

> **※** `your_secret_key_here` には実際に取得したキーを貼り付けてください。  
> コメントは JSON の標準では許容されませんが、`Claude Code` はコメント付きの JSON をパースできるので安心して書けます。

### 2. `.gitignore` に追加（機密情報がリポジトリに流出しないように）

```gitignore
# Claude Code の設定ファイル（機密情報が入るため除外）
.claude/settings.claude.json
```

### 3. 環境変数をコードから参照する例（Node.js）

```js
// src/example.js
// -------------------------------------------------
// 環境変数は process.env から取得できます
// -------------------------------------------------
const openaiKey = process.env.OPENAI_API_KEY;
const myToken   = process.env.MY_API_TOKEN;

console.log('OpenAI Key:', openaiKey);
console.log('My API Token:', myToken);
```

> **ポイント**  
> `Claude Code` が起動すると自動的に `settings.claude.json` の `env` が `process.env` に注入されます。  
> したがって、上記のように普通の `process.env` で取得すれば OK です。

---

## 使い方

1. **ファイルを作成**  
   ```bash
   # プロジェクトのルートに .claude ディレクトリを作成し、設定ファイルを配置
   mkdir -p .claude
   touch .claude/settings.claude.json
   ```

2. **テンプレートを貼り付け**  
   上記の **settings.claude.json** の内容をコピーし、`settings.claude.json` に貼り付けて自分のキーに置き換える。

3. **`.gitignore` に除外設定を追加**（まだ無ければ）  
   ```bash
   echo ".claude/settings.claude.json" >> .gitignore
   ```

4. **Claude Code を起動**  
   VS Code の拡張機能「Claude Code」をインストールしたら、エディタ左下の **Claude** アイコンをクリックして起動。  
   起動時に自動で `settings.claude.json` が読み込まれ、`process.env` に注入されます。

5. **コードで環境変数を使用**  
   上記の Node.js 例のように `process.env.YOUR_VAR_NAME` で取得し、ローカルでも CI/CD パイプラインでも同じコードが動作します。

---

## よくある質問

**Q1. JSON にコメントは書けませんが、エラーになりませんか？**  
**A:** `Claude Code` は内部でコメント付き JSON（JSONC）をサポートしています。コメントは無視され、正常にパースされます。

---

**Q2. 複数の環境（dev / prod）で別々のキーを使いたいです。**  
**A:** `settings.claude.json` に環境ごとのオブジェクトを作り、起動時に `--env=dev` などのフラグで切り替えることができます。例:

```json
{
  "env": {
    "dev": {
      "OPENAI_API_KEY": "dev_key"
    },
    "prod": {
      "OPENAI_API_KEY": "prod_key"
    }
  }
}
```

起動時に `Claude Code: Switch Environment` コマンドで `dev` / `prod` を選択してください。

---

**Q3. 既に `.env` ファイルを使っているプロジェクトに統合したいです。**  
**A:** `.env` から `settings.claude.json` へ自動変換するスクリプトを作れます。簡易例:

```bash
#!/usr/bin/env bash
# .env → .claude/settings.claude.json 変換スクリプト
mkdir -p .claude
echo "{" > .claude/settings.claude.json
echo '  "env": {' >> .claude/settings.claude.json
grep -v '^#' .env | while IFS='=' read -r key value; do
  echo "    \"$key\": \"$value\"," >> .claude/settings.claude.json
done
# 末尾のカンマを削除し、閉じ括弧を追加
sed -i '' -e '$s/,$//' .claude/settings.claude.json
echo "  }" >> .claude/settings.claude.json
echo "}" >> .claude/settings.claude.json
```

---

**Q4. Windows 環境でも同じ手順で使えますか？**  
**A:** はい。PowerShell でも同様にディレクトリ作成とファイル作成が可能です。

```powershell
New-Item -ItemType Directory -Path .claude
New-Item -ItemType File -Path .claude/settings.claude.json
```

---

**Q5. 設定ファイルが読み込まれない場合はどうすれば？**  
**A:**  
1. `Claude Code` が最新バージョンか確認