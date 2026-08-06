# 🤖 AI Conduit 無料プレゼント
## AI駆動UIデザイン完全チートシート - Figma・CSS・Webデザイン最速ワークフロー

---

## 🎯 このチートシートでできること

動画で紹介した「AIエージェントによる文書自動生成」の考え方を、**Webデザイン・UIデザイン・CSSコーディング**に応用。  
Figmaでのデザイン生成から、CSSコードの自動出力、AIを使ったUI改善まで、**今日から使える実践テクニック**を厳選しました。

---

## 1️⃣ Figma AIプロンプト集（即コピペOK）

以下はFigmaのAIプラグイン（例: Figma AI, Magician, Wireframe Designer）で使えるプロンプトです。

```
# ランディングページ生成
「SaaS製品のランディングページ。ヒーローセクション、特徴3つ、価格表、FAQ、フッターを含む。モダンでミニマルなデザイン。青と白のカラースキーム」

# ダッシュボードUI生成
「データ可視化ダッシュボード。折れ線グラフ、円グラフ、KPIカード4つ、サイドバーナビゲーション。ダークモード対応」

# モバイルアプリUI生成
「フィットネストラッカーアプリのホーム画面。歩数計、心拍数、カロリー消費、週間チャート。iOSデザインガイドライン準拠」
```

---

## 2️⃣ CSSコード自動生成プロンプト（AIエージェント用）

動画で紹介したように、AIに「規格準拠」のコードを生成させる手法をCSSに応用します。

```
# プロンプト例
「BEM（Block Element Modifier）命名規則に100%準拠したCSSコードを生成してください。
対象: カードコンポーネント
要件: レスポンシブ対応、アクセシビリティ（WCAG 2.1 AA）準拠、CSS変数を使用したテーマ管理」
```

**生成されるコード例:**
```css
:root {
  --card-bg: #ffffff;
  --card-border: #e0e0e0;
  --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  --card-radius: 12px;
}

.card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
  padding: 24px;
  transition: transform 0.2s ease;
}

.card__title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 8px;
}

.card__body {
  font-size: 0.875rem;
  color: #666;
  line-height: 1.6;
}

.card--featured {
  border-top: 4px solid #4f46e5;
}

.card:hover {
  transform: translateY(-4px);
}
```

---

## 3️⃣ UIデザイン標準化チェックリスト（ASD-STE100のWeb版）

動画で紹介した「規格準拠AI」の考え方をUIデザインに適用。  
以下のチェックリストで、デザインの一貫性を自動チェックできます。

| 項目 | チェック内容 | 基準値 |
|------|-------------|--------|
| フォントサイズ | 本文・見出しのスケール | 最小16px / 比率1.25倍 |
| カラーコントラスト | WCAG 2.1 AA基準 | 4.5:1以上 |
| ボタンサイズ | タッチターゲット | 最小44×44px |
| スペーシング | 8pxグリッドシステム | 8/16/24/32px |
| 角丸 | 統一感のある値 | 4px or 8px or 12px |

---

## 4️⃣ AIでFigmaデザインをHTML/CSSに変換するコマンド

**ツール: Anima, Figma to Code, Locofy** などが使えます。

```bash
# Locofyを使った一括変換例
npx locofy-cli export --project "portfolio" --output ./dist --framework react

# Figma APIを使ったデザイントークン抽出（カラー・フォント）
curl -X GET "https://api.figma.com/v1/files/YOUR_FILE_ID/variables" \
  -H "X-Figma-Token: YOUR_PERSONAL_ACCESS_TOKEN"
```

**おすすめツール比較:**

| ツール名 | 変換品質 | フレームワーク | 料金 |
|---------|---------|--------------|------|
| Anima | ★★★★★ | React / Vue / HTML | 無料枠あり |
| Locofy | ★★★★ | React / Next.js | 無料枠あり |
| Figma to Code | ★★★ | HTML / CSS | 無料 |

---

## 5️⃣ CSS設計パターン即戦力テンプレート

**動画の「規格準拠自動生成」をCSS設計に応用した5つのパターン:**

### パターン1: フレックスボックス中央配置
```css
.centered {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}
```

### パターン2: グリッドでレスポンシブカード
```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  padding: 32px;
}
```

### パターン3: ダークモード対応（CSS変数）
```css
:root {
  --bg-primary: #ffffff;
  --text-primary: #111111;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #1a1a1a;
    --text-primary: #f5f5f5;
  }
}

body {
  background: var(--bg-primary);
  color: var(--text-primary);
}
```

### パターン4: アクセシブルなボタン
```css
.btn {
  min-height: 44px;
  padding: 12px 24px;
  border-radius: 8px;
  background: #4f46e5;
  color: #fff;
  font-size: 16px;
  border: none;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn:focus-visible {
  outline: 3px solid #818cf8;
  outline-offset: 2px;
}
```

### パターン5: アニメーション付きヒーローセクション
```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero {
  animation: fadeInUp 0.8s ease-out;
}
```

---

## 6️⃣ UIデザインAIプロンプト黄金パターン

```
# 完璧なUI生成プロンプトの構造

1. 目的を明確に: 「ユーザーが商品を購入しやすいECサイト」
2. ターゲット指定: 「30代女性向け、シンプルで上品なデザイン」
3. 構成要素を列挙: 「ヘッダー、商品一覧、カート、チェックアウト」
4. カラースキーム: 「ベージュ基調、アクセントにテラコッタ」
5. 参考サイト: 「無印良品とApple.comのミックス」
6. 制約条件: 「モバイルファースト、WCAG準拠」
```

---

## 7️⃣ おすすめAIデザインツール5選（2024年最新）

| ツール名 | 用途 | 特徴 | 料金 |
|---------|------|------|------|
| **Figma AI** | UI生成 | 自然言語からデザイン生成 | 無料 |
| **Uizard** | モックアップ | ワイヤーフレーム自動生成 | 無料枠あり |
| **Galileo AI** | UIデザイン | プロンプトから高品質UI | $19/月 |
| **v0.dev** | React UI | Vercel製、コード生成 | 無料枠あり |
| **Durable** | Webサイト | 30秒でサイト生成 | 無料 |

---

## 8️⃣ 実践ワークフロー: 動画のAIエージェントをWebデザインに応用

動画で紹介した「AIエージェントが規格準拠文書を自動生成」のワークフローをUIデザインに応用：

```
1. 要件定義 → AIにプロジェクト概要をインプット
2. デザイン生成 → Figma AIでワイヤーフレーム作成
3. コード変換 → Anima/LocofyでHTML/CSSに変換
4. 規格チェック → Lighthouse + axeで自動検証
5. 最適化 → AIに改善点を提案させる
```

**ワンライナーで実行:**
```bash
npx create-next-app@latest my-app && npm install -D @tailwindcss/typography && npm run dev
```

---

## 💡 今日から使える3つのポイント

1. **Figma AIプラグイン**をインストールして、プロンプトでUI生成を試す
2. **CSS変数**を活用して、テーマ変更に強い設計にする
3. **AnimaやLocofy**でFigma→コード変換を自動化し、コーディング時間を80%削減

---

## 📌 保存しておきたい！このチートシートの使い方

- **ブックマーク**して、作業中に参照
- **Figmaのコミュニティファイル**に貼り付けて共有
- **AIツールのプロンプト**としても活用可能

---

## 🎁 このプレゼントはAI Conduitからお届けしています

毎日最新AIニュースを自動配信中！

- **YouTube**: https://www.youtube.com/@AI.Conduit
- **Instagram**: https://www.instagram.com/aiconduit/
- **X**: https://x.com/AIconduit777

コメントに「AI」と書いてくれた方にこのプレゼントをお届けしています🎁

---

*※ 本チートシートは動画「GitHub星308超え！ASD-STE100準拠の技術文書生成AIエージェント」の内容をWebデザイン・