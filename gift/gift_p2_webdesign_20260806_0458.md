# 🤖 AI Conduit 無料プレゼント

## 【AI時代のWebデザイン完全ガイド】LLM生成コードの安全な活用法 - チートシート

---

### 🎯 なぜ今、このチートシートが必要なのか？

GCCの決定が示す通り、**15行以上**のAI生成コードは法的リスクが発生します。しかし、Webデザイン・UI実装の現場ではLLMの活用が不可欠です。本プレゼントでは、**法的に安全**かつ**実践的**なLLM活用法を完全網羅しました。

---

### 📋 目次（全7項目）

1. 【最重要】15行ルール対応チェックリスト
2. Figma→コード変換プロンプト（安全版）
3. CSS生成セーフプロンプト集
4. テストケース限定LLM活用法
5. AI生成コード検証コマンド集
6. 著作権フリーUIコンポーネント集
7. 保存版：OSSポリシー互換ワークフロー

---

### 1️⃣ 【最重要】15行ルール対応チェックリスト

```
□ 生成コードが15行未満か？（コメント・空行含む）
□ 生成コード内の変数名・関数名を独自命名に変更済みか？
□ コードの動作をブラウザで手動確認済みか？
□ ライセンス表記が必要なライブラリを併用していないか？
□ 生成コードの出典（プロンプト履歴）を記録済みか？
```

**実践テクニック**: 15行以上のコードは**3分割**して生成し、独自のコメントを追加して組み合わせる。

---

### 2️⃣ Figma→コード変換プロンプト（安全版）

```prompt
【安全な変換プロンプト】
あなたはFigmaデザインをCSSに変換するアシスタントです。
以下の制約を必ず守ってください：
1. 一度に生成するコードは14行以内に収めること
2. クラス名はBEM形式で命名すること
3. 色はCSSカスタムプロパティ（:root）で定義すること
4. レスポンシブ対応のメディアクエリは含めない（別途生成）

【対象デザイン】
- カード型UI
- 幅: 320px
- 角丸: 12px
- シャドウ: 0 4px 12px rgba(0,0,0,0.1)
```

**推奨ツール**: Figmaプラグイン「Anima」+ 上記プロンプトの併用で効率2倍

---

### 3️⃣ CSS生成セーフプロンプト集（厳選5選）

```css
/* ① モダンボタン（14行以内） */
.btn-modern {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}
.btn-modern:hover { transform: translateY(-2px); }

/* ② グリッドレイアウト */
.grid-auto {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  padding: 20px;
}

/* ③ スケルトンローディング */
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
}
@keyframes shimmer { to { background-position: -200% 0; } }
```

---

### 4️⃣ テストケース限定LLM活用法

GCCポリシーでは**テストケースに限り**LLM生成を許可。これを最大活用：

```prompt
【テストケース生成プロンプト】
以下のコンポーネントのテストケースを生成してください。
要件：
- 正常系・異常系・境界値の3パターン
- Jest + React Testing Library使用
- 各テストは10行以内に簡潔に

対象コンポーネント：[ここにコンポーネント名]
```

**テスト自動化コマンド**:
```bash
npx jest --coverage --watchAll=false
```

---

### 5️⃣ AI生成コード検証コマンド集

```bash
# 生成コードの行数チェック（15行ルール確認）
wc -l generated.css

# 未使用CSSセレクタの検出
npx purgecss --css generated.css --content index.html --output cleaned.css

# 構文エラーチェック
npx stylelint generated.css --fix

# ライセンスチェック（依存パッケージ）
npx license-checker --summary

# 重複コード検出（生成コードの類似性確認）
npx jscpd generated.css --min-lines 5
```

**おすすめVSCode拡張**:
- 「GitLens」: 生成コードの履歴追跡
- 「ESLint」: 静的解析
- 「Prettier」: 自動フォーマット

---

### 6️⃣ 著作権フリーUIコンポーネント集

**ライセンス完全フリーのリソース**（商用利用OK）：

```css
/* ① フローティングアクションボタン */
.fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #2196f3;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.4);
  cursor: pointer;
}
```

**おすすめサイト**:
- **UIverse.io**: 完全無料UIコンポーネント集
- **Shadcn UI**: MITライセンス
- **Tailwind UI**: 商用ライセンス

---

### 7️⃣ 保存版：OSSポリシー互換ワークフロー

```
① LLMで生成 → ② 14行以下に分割
③ 独自コメント追加 → ④ 手動でリファクタリング
⑤ テストケース自動生成 → ⑥ 検証コマンド実行
⑦ コミット前に差分確認 → ⑧ ドキュメント記録
```

**毎日チェックすべきOSSポリシー更新情報**:
- GCC公式アナウンス: https://gcc.gnu.org
- GNUプロジェクトガイドライン: https://www.gnu.org
- Linux Foundation AIポリシー: https://www.linuxfoundation.org

---

## 📌 保存してすぐ使える！重要ポイントまとめ

| シチュエーション | 対応策 | 重要度 |
|-----------------|--------|--------|
| 15行以上のコード生成 | 3分割して生成 | ⭐⭐⭐⭐⭐ |
| Figma→CSS変換 | Anima + 安全プロンプト | ⭐⭐⭐⭐ |
| テストコード生成 | LLM活用OK | ⭐⭐⭐⭐⭐ |
| 商用利用コード | 手動リファクタ必須 | ⭐⭐⭐⭐⭐ |

---

## 💝 このプレゼントはAI Conduitからお届けしています

毎日最新AIニュースを自動配信中！

- **YouTube**: https://www.youtube.com/@AI.Conduit
- **Instagram**: https://www.instagram.com/aiconduit/
- **X**: https://x.com/AIconduit777

コメントに「**AI**」と書いてくれた方に、このプレゼントをお届けしています🎁

**次回予告**: 「AI生成コードの著作権リスク完全回避マニュアル」を公開予定！

---

*本プレゼントは動画内容と完全連動しています。GCCポリシーの最新情報はコメント欄のリンクから確認できます。*