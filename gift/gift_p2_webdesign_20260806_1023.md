# 🤖 AI Conduit 無料プレゼント

## 🎨 Webデザイン・UIデザイン効率化 完全チートシート - コーディング時間を70%削減する実践テクニック集

---

### ✅ このチートシートで得られるもの

動画で紹介したAIを活用した技術文書の標準化テクニックを、**Webデザイン・UIデザイン・CSSコーディング**に応用した実践的なプロンプトとコード集です。コピペですぐ使えます！

---

### 1️⃣ Figmaデザイン → HTML/CSS変換プロンプト（最強版）

**以下のプロンプトをChatGPT/Claudeに貼り付けるだけで、Figmaデザインを高品質なコードに変換できます：**

```
あなたはシニアフロントエンドエンジニアです。
以下のFigmaデザイン仕様をHTML/CSSコードに変換してください。

【デザイン仕様】
- デスクトップファースト（1440px基準）
- カラーパレット: #0F172A（背景）, #3B82F6（プライマリ）, #F59E0B（アクセント）
- フォント: Inter, システムフォントスタック
- コンポーネント: ナビゲーションバー + ヒーローセクション + カードグリッド（3列）

【要件】
- レスポンシブ対応（768px, 480pxブレークポイント）
- BEM命名規則に従う
- CSSはTailwind CSSではなく素のCSSで記述
- アクセシビリティ（ARIAラベル）対応
```

**活用例：** このプロンプトで生成されたコードは、平均して手書きの**1/3の時間**で実装可能です。

---

### 2️⃣ CSSリセット＆モダンベースコード（即戦力テンプレート）

```css
/* Modern CSS Reset + Base */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --primary: #3B82F6;
  --secondary: #6B7280;
  --bg: #0F172A;
  --surface: #1E293B;
  --text: #F1F5F9;
  --radius: 12px;
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

html {
  scroll-behavior: smooth;
  font-size: 16px;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.6;
  color: var(--text);
  background: var(--bg);
  min-height: 100vh;
}

img, picture, video, canvas, svg {
  display: block;
  max-width: 100%;
}

input, button, textarea, select {
  font: inherit;
  color: inherit;
}

@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

**このリセットを導入するだけで、ブラウザ間の表示差異を80%以上解消できます。**

---

### 3️⃣ レスポンシブ対応が自動化されるCSS Gridパターン

```css
/* 自動フィットするカードグリッド */
.grid-auto {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(280px, 100%), 1fr));
  gap: 24px;
  padding: 32px 24px;
}

/* 12カラムのフレキシブルレイアウト */
.grid-12 {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 20px;
}

.col-span-4 { grid-column: span 4; }
.col-span-6 { grid-column: span 6; }
.col-span-8 { grid-column: span 8; }

@media (max-width: 768px) {
  .col-span-4, .col-span-6, .col-span-8 {
    grid-column: 1 / -1;
  }
}
```

**このパターンを使うと、メディアクエリの記述量が約60%削減できます。**

---

### 4️⃣ アニメーション付きUIコンポーネント（コピペ即使用可能）

```html
<!-- ホバーで浮き上がるカード -->
<div class="card-hover">
  <h3>タイトル</h3>
  <p>説明テキスト</p>
  <a href="#" class="btn-primary">詳細を見る</a>
</div>

<style>
.card-hover {
  background: var(--surface);
  border-radius: var(--radius);
  padding: 24px;
  box-shadow: var(--shadow);
  transition: var(--transition);
}

.card-hover:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px -1px rgba(0, 0, 0, 0.2);
}

.btn-primary {
  display: inline-block;
  padding: 10px 24px;
  background: var(--primary);
  color: white;
  border-radius: 8px;
  text-decoration: none;
  transition: var(--transition);
}

.btn-primary:hover {
  background: #2563EB;
  transform: scale(1.05);
}
</style>
```

---

### 5️⃣ Figma用 デザイン生成プロンプト集（5選）

**以下のプロンプトをFigma AIプラグインやChatGPTで使用：**

| 用途 | プロンプト |
|------|------------|
| **ランディングページ** | 「SaaS製品のLP用に、ヒーローセクション+機能紹介3点+CTAボタンのデザインを作成。カラーはブルー系で信頼感を演出。モダンでミニマルなスタイル。」 |
| **ダッシュボード** | 「分析ダッシュボードのUIデザイン。左サイドバー+メインエリア2カラム構成。グラフは折れ線グラフと棒グラフを使用。」 |
| **モバイルアプリ** | 「フィットネスアプリのホーム画面。今日の歩数・消費カロリー・目標達成率をカード型で表示。ダークモード対応。」 |
| **ECサイト** | 「アパレルECサイトの商品一覧ページ。フィルター機能+グリッドレイアウト+クイックビューボタン付き。」 |
| **フォーム** | 「ユーザー登録フォーム。3ステップのプログレスバー付き。入力バリデーションの状態表示を含む。」 |

---

### 6️⃣ アクセシビリティ対応チェックリスト（品質維持の必須項目）

```
□ コントラスト比: テキストは4.5:1以上、大きい文字は3:1以上
□ フォーカス状態: :focus-visibleで視覚的に明確なインジケーター
□ セマンティックHTML: h1→h6の順序、nav, main, section, footerを使用
□ 代替テキスト: 装飾画像にはalt=""、意味のある画像には説明的なalt
□ キーボード操作: Tabで全ての操作が可能
□ フォームラベル: 各inputに<label>を関連付け

/* フォーカスリングの実装例 */
:focus-visible {
  outline: 3px solid var(--primary);
  outline-offset: 2px;
  border-radius: 4px;
}
```

---

### 7️⃣ GitHub Copilot効率化コマンド（コーディング速度2倍）

```
# VS Code内で使用するCopilotチャットプロンプト

# 1. コンポーネント生成
「Reactのカードコンポーネントを作成。props: title, description, imageUrl。Tailwind CSS使用。」

# 2. リファクタリング
「この関数をTypeScriptに変換し、型定義を追加してください。」

# 3. バグ修正
「このコードのエラーを特定して修正。パフォーマンスも最適化して。」

# 4. テスト生成
「このコンポーネントのJestテストを作成。レンダリング、イベント、スナップショットテストを含む。」

# 5. ドキュメント自動生成
「この関数のJSDocコメントを生成。@param, @returns, @throwsを含む」
```

---

### 8️⃣ パフォーマンス最適化スニペット

```javascript
// Lazy Loading画像（読み込み速度30%改善）
document.addEventListener('DOMContentLoaded', () => {
  const images = document.querySelectorAll('img[data-src]');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        observer.unobserve(img);
      }
    });
  });
  images.forEach(img => observer.observe(img));
});

// 使用例: <img data-src="image.jpg" alt="説明" width="600" height="400">
```

```css
/* フォント表示最適化 */
@font-face {
  font-family: 'Inter';
  font-display: swap; /* FOIT防止 */
  src: url('/fonts/Inter.woff2') format('woff2');
}
```

---

### 9️⃣ デザイントークン管理テンプレート（チーム標準化）

```json
{
  "colors": {
    "primary": { "default": "#3B82F6", "hover": "#2563EB", "active": "#1D4ED8" },
    "surface": { "default": "#1E293B", "elevated": "#334155" },
    "text": { "primary": "#F1F5F9", "secondary": "#94A3B8" },
    "status": { "success": "#10B981", "warning": "#F59E0B", "error": "#EF4444" }
  },
  "spacing": { "xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "32px", "xxl": "48px" },
  "typography": {
    "h1": { "size": "2.25rem", "weight": 700, "lineHeight": 1.2 },
    "body": { "size": "1