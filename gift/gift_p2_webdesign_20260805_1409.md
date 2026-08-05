# 🤖 AI Conduit 無料プレゼント
## 【保存版】生成AIでWebデザインを10倍速にする！実践プロンプト＆コード集

動画でお伝えした通り、生成AIを活用したデザイン制作は**制作時間78%削減・コスト95%カット**が可能です。ここでは、すぐに使える実践的なプロンプトとコードを厳選してご紹介します。

---

## 🎨 1. Figma用：AIプロンプトチートシート（5選）

### ① ランディングページ生成プロンプト
```
Create a modern landing page design for a [業界] company.
- Style: Minimalist, clean, with lots of white space
- Color palette: #2563EB (primary), #F8FAFC (background), #1E293B (text)
- Include: Hero section with CTA button, 3 feature cards, testimonial section, footer
- Typography: Inter font, large headings (48px+), comfortable line-height
- Make it mobile-responsive with a hamburger menu
```

### ② UIコンポーネント生成プロンプト
```
Design a pricing table component with 3 tiers (Basic $9, Pro $29, Enterprise $99).
- Highlight the "Pro" tier as most popular with a badge
- Include feature lists with checkmark icons
- Toggle for monthly/annual billing (save 20%)
- Style: Rounded corners (12px), subtle shadows, hover effects
```

### ③ カラーパレット抽出プロンプト
```
Extract a complete color palette from this design reference (attached image).
- Generate 5 primary colors with hex codes
- Generate 3 accent colors
- Generate neutral tones for text and backgrounds
- Suggest dark mode equivalents for each color
```

### ④ デザイントークン生成プロンプト
```
Generate CSS design tokens as JSON from this Figma design:
- Spacing scale (4px base): 4, 8, 12, 16, 24, 32, 48, 64px
- Border radius: 4, 8, 12, 16px
- Typography scale: 12, 14, 16, 20, 24, 32, 40, 48px
- Shadow levels: subtle, medium, prominent
Output as a structured CSS custom properties format
```

### ⑤ レスポンシブ対応プロンプト
```
Convert this desktop layout to mobile-responsive:
- Breakpoints: 375px, 768px, 1024px, 1440px
- Stack sections vertically on mobile
- Convert 3-column grid to single column
- Adjust font sizes: desktop 32px → mobile 24px
- Make navigation into hamburger menu
- Ensure touch targets are at least 44x44px
```

---

## 💻 2. 即コピペOK！CSSコードスニペット（3選）

### ① モダングラスモーフィズム効果
```css
.glass-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 16px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  padding: 24px;
}

/* ダークモード対応 */
@media (prefers-color-scheme: dark) {
  .glass-card {
    background: rgba(17, 25, 40, 0.75);
    border-color: rgba(255, 255, 255, 0.125);
  }
}
```

### ② スムーズスクロール＆アニメーション
```css
/* スムーズスクロール */
html {
  scroll-behavior: smooth;
  scroll-padding-top: 80px;
}

/* スクロールフェードイン */
.fade-in {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.fade-in.visible {
  opacity: 1;
  transform: translateY(0);
}

/* ホバーエフェクト */
.btn-primary {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(99, 102, 241, 0.4);
}
```

### ③ モダングリッドレイアウト
```css
.grid-auto-layout {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  padding: 20px;
}

/* コンテナの最大幅を設定 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 12カラムグリッド */
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
    grid-column: span 12;
  }
}
```

---

## 🛠️ 3. AIデザインツール厳選リスト

| ツール名 | 用途 | 料金 | 特徴 |
|---------|------|------|------|
| **Figma AI** | UIデザイン | 無料〜$12/月 | AIによるレイアウト生成、コード変換 |
| **Uizard** | プロトタイプ | 無料〜$12/月 | テキストからUI生成 |
| **Durable** | Webサイト生成 | $12/月 | 30秒でサイト生成 |
| **Galileo AI** | UIデザイン | $22/月 | プロンプトから高品質UI |
| **v0 by Vercel** | コード生成 | 無料〜 | チャットでReact/UI生成 |
| **Midjourney** | ビジュアル素材 | $10/月 | 高品質画像生成 |

**おすすめ組み合わせ：** Figma AI + v0 + Midjourneyで完結するワークフローが最強です。

---

## 🎯 4. 30日でAIデザイナーになる！学習ロードマップ

| 週 | 学習内容 | 目標スキル | 所要時間 |
|----|---------|-----------|---------|
| **Week 1** | Figma基本操作 + AIプラグイン | 既存デザインのAI活用 | 3h×5日 |
| **Week 2** | プロンプトエンジニアリング | 高品質なUI生成 | 3h×5日 |
| **Week 3** | HTML/CSSコード生成 | AI生成コードの編集 | 3h×5日 |
| **Week 4** | 実践プロジェクト | ポートフォリオ作成 | 4h×5日 |

**実践例：**
1. 架空の飲食店のサイトをAIで生成
2. 生成したデザインをFigmaで編集
3. v0でReactコード化
4. ポートフォリオとして公開

---

## 📊 5. AIデザインの収益化戦略

| サービス | 料金設定 | AI活用による原価 | 利益率 |
|---------|---------|----------------|-------|
| LPデザイン | ¥50,000〜 | ¥2,000 | 96% |
| UI/UXデザイン | ¥80,000〜 | ¥3,000 | 96% |
| デザインシステム構築 | ¥300,000〜 | ¥10,000 | 97% |
| 月額デザインパートナー | ¥150,000/月 | ¥10,000/月 | 93% |

**AI活用デザイナーの単価は3倍に跳ね上がる！** 従来のデザイン料金をAIで時短して高単価案件をこなすのが最短ルートです。

---

## 🚀 今日から始める3ステップ

1. **Figma AIプラグインをインストール**
   - プラグイン名: "Automater" または "Design Assistant"
   - Figmaコミュニティから無料で入手

2. **最初のプロンプトを実行**
   - 上記のプロンプトをコピーして使用
   - 自分のプロジェクトに合わせてカスタマイズ

3. **生成結果を学習**
   - AIが出したコードを分析
   - 自分のプロジェクトに統合

---

## このプレゼントはAI Conduitからお届けしています
毎日最新AIニュースを自動配信中！
- YouTube: https://www.youtube.com/@AI.Conduit
- Instagram: https://www.instagram.com/aiconduit/
- X: https://x.com/AIconduit777
コメントに「AI」と書いてくれた方にこのプレゼントをお届けしています🎁

**#AIデザイン #Webデザイン #Figma #UIデザイン #生成AI #デザインツール #AI活用**