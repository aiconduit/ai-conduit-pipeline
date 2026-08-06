# 🤖 AI Conduit 無料プレゼント

## 🎨 Webデザイン・UI/UX効率化 完全チートシート — AIでデザイン制作時間を90%削減！

動画で紹介した**AIを活用した技術文書の簡素化**のノウハウを、**Webデザイン・UIデザイン・CSSコード・Figmaプロンプト**に特化して応用した実践チートシートです。コピペですぐ使えます👇

---

### ✅ 1. Figma用プロンプト（AIプラグイン「Figma AI」＋ChatGPT併用）

**デザイン生成プロンプト（コピペOK）:**

```
あなたはシニアUI/UXデザイナーです。以下の条件でランディングページのデザイン仕様書を作成してください。
- カラーパレット: メイン#0F172A、アクセント#3B82F6、背景#F8FAFC
- タイポグラフィ: Inter、見出し32px/太字、本文16px/400
- コンポーネント: ヘッダー/ヒーローセクション/特長3カラム/CTA/フッター
- ブレイクポイント: モバイル375px / タブレット768px / デスクトップ1440px
出力はFigmaのオートレイアウト対応のJSON形式で。
```

**🎯 効果:** 仕様書作成時間を約15分→2分に短縮。

---

### ✅ 2. CSSコード自動生成プロンプト（ChatGPT / Claude用）

**動画で紹介した「英語簡素化AI」と同じ手法で、CSSも自動生成:**

```
以下のHTMLクラスに対して、モダンでアクセシブルなCSSを生成してください。
- .navbar（スティッキー、ガラスモーフィズム）
- .card-grid（レスポンシブ3カラム、grid-template-columns: repeat(auto-fit, minmax(280px, 1fr))）
- .btn-primary（ホバー時に色変化、トランジション0.3s）
- ダークモード対応（prefers-color-scheme: dark）
```

**生成例（プロンプト実行結果）:**
```css
.navbar {
  position: sticky; top: 0;
  background: rgba(255,255,255,0.8);
  backdrop-filter: blur(12px);
  z-index: 100;
}
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}
.btn-primary {
  background: #3B82F6; color: #fff;
  padding: 12px 24px; border-radius: 8px;
  transition: all 0.3s ease;
}
.btn-primary:hover { background: #2563EB; transform: translateY(-2px); }
```

---

### ✅ 3. デザイントークン（CSS変数）チートシート

```css
:root {
  /* カラー */
  --color-primary: #3B82F6;
  --color-secondary: #10B981;
  --color-bg: #F8FAFC;
  --color-text: #0F172A;

  /* スペーシング */
  --space-xs: 4px; --space-sm: 8px;
  --space-md: 16px; --space-lg: 24px; --space-xl: 48px;

  /* フォント */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* 角丸 */
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 16px;
}
```

---

### ✅ 4. Figma AIプラグイン「Magician」用プロンプト

```
Generate a mobile app onboarding screen with:
- 3 steps (welcome, features, CTA)
- Soft gradient background (#6366F1 to #8B5CF6)
- Illustration style: flat design, rounded corners
- Text: "AIでデザインをもっと自由に"
```

---

### ✅ 5. デザインレビュー用チェックリスト（AI Copilot活用）

ChatGPTに貼るだけでOK:

```
このデザイン仕様書をレビューしてください。
【チェック項目】
- WCAG 2.1 AAコントラスト比（テキスト4.5:1以上）
- モバイルファーストのレスポンシブ対応
- 状態（ホバー/フォーカス/アクティブ）のスタイル定義
- フォントサイズの階層（32px/24px/16px/14px）
- インラインSVGアイコン使用（外部画像読み込みなし）
```

---

### ✅ 6. CSS圧縮・最適化コマンド（動画の「自動簡素化」と同じ発想）

```bash
# CSSを自動圧縮（簡素化）
npx cssnano input.css -o output.min.css

# 未使用CSSを自動検出
npx purgecss --css styles.css --content index.html --output cleaned.css

# デザインシステムの自動生成
npx style-dictionary build
```

---

### ✅ 7. AIデザインツール比較表（2025年版）

| ツール名 | 用途 | 無料枠 | 主な強み |
|---------|------|--------|---------|
| **Figma AI** | デザイン生成・編集 | あり | オートレイアウト連携 |
| **Uizard** | ワイヤーフレーム自動生成 | あり | スクショ→デザイン変換 |
| **Galileo AI** | UIデザイン生成 | トライアル | 高品質なUI提案 |
| **v0.dev** | コード生成（React） | あり | プロンプト→UIコード |

---

### ✅ 8. レスポンシブ対応 自動チェックコード

```javascript
// ブラウザコンソールに貼り付けて実行
const checkResponsive = () => {
  const widths = [375, 768, 1024, 1440];
  widths.forEach(w => {
    console.log(`--- ${w}px ---`);
    document.querySelectorAll('*').forEach(el => {
      if (el.scrollWidth > w) {
        console.warn(`⚠️ ${el.tagName}.${el.className} が${w}pxで横はみ出し`);
      }
    });
  });
};
checkResponsive();
```

---

### ✅ 9. Figma→CSS自動書き出しプロンプト

```
以下のFigmaデザインのJSONデータをCSSに変換してください。
【条件】
- ピクセルパーフェクト（1px単位で正確に）
- BEM命名規則でクラス名を付与
- メディアクエリはモバイルファースト
- 共通スタイルはCSS変数で定義
- コメントでセクション名を明記
```

---

### ✅ 10. デザイン英語 簡素化フレーズ集（動画のASD-STE100応用）

| NG（複雑） | OK（簡素化） |
|-----------|------------|
| "The button should be visually enhanced" | "Make the button blue" |
| "Utilize the grid system" | "Use the grid" |
| "The color palette consists of..." | "Colors are: #... and #..." |

---

## 🎁 このチートシートの使い方

1. **保存** → ブラウザのブックマーク or Notionに貼り付け
2. **コピペ** → プロンプトやコードをそのまま使用
3. **応用** → 動画で紹介した「AI簡素化」の考え方をデザインに転用

---

## このプレゼントはAI Conduitからお届けしています

毎日最新AIニュースを自動配信中！
- YouTube: https://www.youtube.com/@AI.Conduit
- Instagram: https://www.instagram.com/aiconduit/
- X: https://x.com/AIconduit777

コメントに「AI」と書いてくれた方にこのプレゼントをお届けしています🎁

**動画で紹介したASD-STE100対応ツールの詳細は、動画概要欄のリンクからチェック！**