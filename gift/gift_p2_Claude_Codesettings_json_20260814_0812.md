# Claude Code の settings.json で環境変数を一元管理 - 実践テンプレート

## この動画で学んだこと
`Claude Code` のプロジェクトルートに **.claude/settings.claude.json** を置くだけで、環境変数をコードから安全に参照できるようになります。  

## すぐに使えるテンプレート
以下の内容をそのままコピーして、プロジェクトのルートに **.claude/settings.claude.json** として保存してください。  

```json
{
  // -------------------------------------------------
  // Claude Code 用設定ファイル
  // -------------------------------------------------
  // env フィールドに記載したキーは、Claude Code が自動的に
  // process.env（Node.js）や getenv（Python）などから取得できるようになります。
  // ここに書いた値は .gitignore に入っているので、リポジトリに漏れません。
  // -------------------------------------------------
  "env": {
    // 例: OpenAI の API キー
    "MY_API_KEY": "your_secret_key_here",

    // 例: データベース接続文字列
    // "DATABASE_URL": "postgres://user:password@host:5432/dbname",

    // 例: カスタムフラグ
    // "ENABLE_FEATURE_X": "true"
  }
}
```

> **⚠️ 注意**  
> - `your_secret_key_here` の部分は必ず自分の実際のシークレットに置き換えてください。  
> - このファイルは **.gitignore** に追加して、リモートリポジトリへプッシュしないようにしてください。

## 使い方
1. **ファイル作成**  
   ```bash
   mkdir -p .claude
   touch .claude/settings.claude.json
   ```
   上記のテンプレート JSON を貼り付け、必要なキーと値を記入します。

2. **.gitignore に追加**（まだ入っていない場合）  
   ```bash
   echo ".claude/" >> .gitignore
   ```

3. **コード側で環境変数を取得**  
   - **Node.js（JavaScript / TypeScript）**  
     ```js
     // env 変数は process.env から取得できます
     const apiKey = process.env.MY_API_KEY;
     console.log('My API Key:', apiKey);
     ```
   - **Python**  
     ```python
     import os

     api_key = os.getenv('MY_API_KEY')
     print('My API Key:', api_key)
     ```

4. **Claude Code で実行**  
   - VS Code のサイドバーにある **Claude Code** アイコンをクリック  
   - 「Run」や「Chat」ウィンドウでコードを実行すると、上記の環境変数が自動的に注入されます。

5. **変更があったら再ロード**  
   設定ファイルを編集したら、Claude Code のウィンドウを一度閉じて再度開くか、`Reload Window` コマンドでリロードしてください。

## よくある質問

**Q1: 既に `.env` ファイルを使っているプロジェクトでも併用できますか？**  
**A:** できますが、重複したキーがある場合は **settings.claude.json** が優先されます。管理が煩雑になるので、どちらか一方に統一することをおすすめします。

---

**Q2: `settings.claude.json` に書いた値がコード側で取得できません。**  
**A:**  
1. ファイルがプロジェクトの **ルート** に正しく配置されているか確認。  
2. `.gitignore` に `.claude/` が入っているか確認（無くても動作はしますが、プッシュ防止のため必須）。  
3. Claude Code のウィンドウを **リロード** して、設定を再読み込みしてください。

---

**Q3: 複数の環境（dev / prod）で異なるキーを使いたいです。**  
**A:** `settings.claude.json` はプロジェクト単位の設定なので、環境ごとに別のブランチやフォルダを作り、そこで別々のファイルを管理するとシンプルです。あるいはキー名に `DEV_` / `PROD_` プレフィックスを付けて切り替えるスクリプトを自作する方法もあります。

---

**Q4: Windows でも同じ設定ファイルで動作しますか？**  
**A:** はい。JSON 形式なので OS に依存せず、Claude Code がインストールされていれば同一の設定で動作します。

---

**Q5: 何か他に注意すべき点はありますか？**  
**A:**  
- **機密情報は必ず** `.gitignore` に入れること。  
- 共有リポジトリで共同作業する場合は、**シークレット管理ツール（例: 1Password, HashiCorp Vault）** と併用すると安全です。  
- 変更後は必ず **Claude Code のウィンドウをリロード** して、最新設定が反映されているかテストしてください。

---

AI Conduit: https://www.youtube.com/@AI.Conduit