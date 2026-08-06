# 🤖 AI Conduit 無料プレゼント

## 🎨 AIエージェントで作る！技術英語対応Webデザイン完全チートシート

**動画で紹介したAIエージェント開発の知見を、Webデザイン・UIデザイン・CSS・Figmaに応用！**  
技術英語の自動修正と同じ「ルールベース×AI」のアプローチで、あなたのデザインを国際水準に引き上げます。

---

### ✅ このチートシートでできること

1. **Figmaで国際規格（ISO 9241）準拠のUIを自動生成するプロンプト**
2. **技術英語対応の多言語UIを実装するCSSスニペット**
3. **AIエージェントを使ったデザイン修正の自動化ワークフロー**
4. **アクセシビリティ（WCAG 2.2）準拠チェックリスト**
5. **Figma→CSSコード変換の効率化プロンプト**

---

### 📋 1. Figma用・国際規格準拠UI生成プロンプト（3選）

#### プロンプト①：ISO 9241準拠ダッシュボード
```
Figmaで技術英語対応のダッシュボードUIをデザインしてください。
要件：
- ISO 9241-11（ユーザビリティ）準拠
- グリッドシステムは8ptベース
- フォントはInter（英語）/ Noto Sans JP（日本語）の併用
- カラーコントラスト比はWCAG AA以上（4.5:1）
- コンポーネント名は英語で命名（例：Button/Primary）
```

#### プロンプト②：多言語対応フォーム
```
技術英語と日本語のバイリンガル対応フォームをFigmaで作成。
- ラベルは英語（例：Email Address）＋日本語（例：メールアドレス）併記
- エラーメッセージは国際規格ISO 9241-110の対話原則に準拠
- 入力フィールドのプレースホルダーは英語のみ
- 送信ボタンは「Submit / 送信」の2言語表示
```

#### プロンプト③：Figma→CSS自動変換用
```
このFigmaデザインをCSSに変換してください。
- 使用しているカラーをCSSカスタムプロパティ（:root）に定義
- ブレークポイントは 375px / 768px / 1024px / 1440px
- アニメーションはprefers-reduced-motion対応
- BEM命名規則（Block__Element--Modifier）でクラス名を生成
```

---

### 🎯 2. 技術英語対応・多言語UIのCSSスニペット（3選）

#### スニペット①：言語切替対応のフォントスタック
```css
:root {
  --font-en: 'Inter', 'Helvetica Neue', Arial, sans-serif;
  --font-ja: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', sans-serif;
  --font-multilingual: var(--font-en), var(--font-ja);
}

/* lang属性で自動切替 */
html[lang="ja"] body {
  font-family: var(--font-ja);
  line-height: 1.8; /* 日本語は行間を広めに */
}

html[lang="en"] body {
  font-family: var(--font-en);
  line-height: 1.6;
}
```

#### スニペット②：WCAG 2.2 AA準拠カラーパレット
```css
:root {
  /* コントラスト比4.5:1以上を保証 */
  --primary-blue: #005A9E;      /* 白文字でAA適合 */
  --primary-blue-dark: #003B62; /* 白文字でAAA適合 */
  --text-primary: #1A1A1A;      /* 白背景でAAA適合 */
  --text-secondary: #4D4D4D;    /* 白背景でAA適合 */
  --bg-light: #F5F5F5;
  --bg-white: #FFFFFF;
  --error-red: #D32F2F;         /* 白背景でAA適合 */
  --success-green: #2E7D32;     /* 白背景でAA適合 */
}

/* アクセシブルなフォーカスリング */
:focus-visible {
  outline: 3px solid var(--primary-blue);
  outline-offset: 2px;
}
```

#### スニペット③：技術英語ラベル用・省略記号クラス
```css
/* 長い技術英語ラベルをスマホで省略表示 */
.tech-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

/* ツールチップで完全表示 */
.tech-label:hover::after {
  content: attr(data-full-text);
  position: absolute;
  background: var(--text-primary);
  color: var(--bg-white);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: normal;
  z-index: 1000;
}
```

---

### 🚀 3. AIエージェントでデザイン修正を自動化するワークフロー

動画で紹介した「300ルール自動適用」の考え方をデザインに応用：

```bash
# 1. Figma APIでデザイントークンを取得
curl -H "X-Figma-Token: YOUR_TOKEN" \
  "https://api.figma.com/v1/files/YOUR_FILE_ID/variables"

# 2. StylelintでCSSのアクセシビリティチェック
npx stylelint "src/**/*.css" \
  --custom-formatter node_modules/stylelint-a11y

# 3. カラーコントラスト検証（Node.js）
npx axe --select ".btn-primary" --show-errors
```

**おすすめツール**：
- **Stylelint + stylelint-a11y** — CSSのアクセシビリティ自動検証
- **Figma REST API** — デザイントークンをJSONで一括エクスポート
- **Pa11y** — 自動アクセシビリティ監査（CIに組み込み可能）

---

### 🔍 4. WCAG 2.2準拠チェックリスト（デザイナー向け）

| 項目 | 基準 | チェック方法 |
|------|------|-------------|
| カラーコントラスト | 4.5:1以上（本文） | WebAIM Contrast Checker |
| フォーカス表示 | 2px以上の可視インジケーター | キーボード操作で確認 |
| タッチターゲット | 24×24px以上（WCAG 2.2新基準） | Figmaでオーバーレイ確認 |
| テキスト拡大 | 200%拡大でレイアウト崩れなし | ブラウザのズーム機能で確認 |
| エラー特定 | アイコン＋テキストの併用 | エラーメッセージを目視確認 |
| 言語指定 | `<html lang="ja">` 等を明示 | ソースコードで確認 |

---

### 💡 5. Figmaで使える便利プロンプト集（2選）

#### プロンプト④：カラートークン自動生成
```
Figmaのカラー変数をCSSカスタムプロパティに変換するコードを生成してください。
- 命名規則：--{semantic}-{variant}（例：--surface-primary）
- ダークモード用の変数も自動生成
- コントラスト比が4.5:1未満の組み合わせは警告コメントを付与
```

#### プロンプト⑤：レスポンシブ対応チェック
```
このFigmaデザインのレスポンシブ問題を検出してください。
- ブレークポイント：375px / 768px / 1024px / 1440px
- 問題箇所には修正案をFigmaコメントとして提案
- 特に技術英語の長い単語（例：Internationalization）の折り返しに注意
```

---

### 📚 保存版！デザイン×技術英語の必須リソース

| ツール名 | 用途 | 料金 |
|---------|------|------|
| **Figma Variables** | デザイントークン管理 | 無料〜 |
| **Stylelint** | CSS自動チェック | 無料（OSS） |
| **WebAIM Contrast Checker** | コントラスト検証 | 無料 |
| **DeepL API** | 技術英語の自動翻訳 | 月5万文字まで無料 |
| **Pa11y** | アクセシビリティ監査 | 無料（OSS） |

---

## 🎁 このプレゼントはAI Conduitからお届けしています

**毎日最新AIニュースを自動配信中！** 動画で紹介したAIエージェントの活用法や、デザイン×AIの最前線情報をいち早くキャッチできます。

- 📺 **YouTube**: https://www.youtube.com/@AI.Conduit
- 📸 **Instagram**: https://www.instagram.com/aiconduit/
- 🐦 **X**: https://x.com/AIconduit777

**この記事を保存＆コメントに「AI」と書いてくれた方に**、次回の限定プレゼントも先行配信します🎁

---

*本チートシートは動画「エージェントが技術英語を自動修正！文書作成が2倍速に」の内容に基づき、Webデザイン・UIデザイン分野に応用して作成しました。AI Conduitは毎日午前7時に最新AI情報を配信中です！*