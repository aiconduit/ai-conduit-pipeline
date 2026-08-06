# 🤖 AI Conduit 無料プレゼント

## 【GCC 15行ルール完全対策】AI生成コードを安全に使うためのWebデザイン・CSSチートシート

---

### 🔥 このチートシートでわかること

GCCの「15行以上のAI生成コード拒否」方針を受けて、**Webデザイン・UIデザインの現場でAIを安全に活用する方法**を完全まとめました。著作権リスクを回避しながら、CSSコードとFigmaプロンプトを最大限活用するための実践テクニックを厳選公開！

---

### 📋 目次

1. 【15行ルール対応】AI生成コードの安全な活用法（3ステップ）
2. 【即コピペ】CSSコード分割テンプレート（15行以内に最適化）
3. 【爆速】Figmaプロンプト完全テンプレート集
4. 【必須】AI利用宣言テンプレート（OSS開発者向け）
5. 【上級者向け】AI生成コードの著作権リスク回避チェックリスト

---

### 1️⃣ 【15行ルール対応】AI生成コードの安全な活用法（3ステップ）

**ステップ1: 生成コードを15行単位に分割**

```bash
# 例: CSSファイルを15行ごとに分割するコマンド
split -l 15 style.css segment_
```

**ステップ2: AI生成部分を明示的にコメント**

```css
/* ============================================
   AI生成コード（ChatGPT-4, 2024年6月） 
   プロンプト: "flexboxでカードレイアウトを作成"
   生成日: 2024-06-15
   手動修正: ブレークポイントを追加
   ============================================ */
```

**ステップ3: 人間によるレビュー＆修正を必ず実施**

- 生成コードの意図を理解する
- 変数名・クラス名を自分好みにリネーム
- 不要なコードを削除して最適化

---

### 2️⃣ 【即コピペ】CSSコード分割テンプレート（15行以内に最適化）

#### ✅ テンプレートA: レスポンシブ対応の基本セット（12行）

```css
/* モバイルファースト基本設定 */
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

@media (min-width: 768px) {
  .container {
    padding: 0 40px;
  }
}
```

#### ✅ テンプレートB: フレックスボックスレイアウト（10行）

```css
.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.flex-item {
  flex: 1 1 250px;
  min-width: 200px;
}
```

#### ✅ テンプレートC: CSS Gridでカードレイアウト（14行）

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.card {
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.card:hover {
  transform: translateY(-4px);
}
```

#### ✅ テンプレートD: アニメーション付きボタン（13行）

```css
.btn-animated {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  transition: all 0.3s ease;
}

.btn-animated:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #764ba2, #667eea);
}
```

---

### 3️⃣ 【爆速】Figmaプロンプト完全テンプレート集

#### 🎨 プロンプトテンプレート1: モダンなランディングページ

```
Create a modern landing page design for a [プロダクト名] with:
- Hero section with headline, subheadline, and CTA button
- Features section with 4 cards (icon + title + description)
- Color palette: primary #667eea, secondary #764ba2, background #f8f9fa
- Typography: Inter font, headings 48px, body 16px
- Rounded corners (12px), soft shadows, minimal design
- Mobile responsive layout (375px width)
```

#### 🎨 プロンプトテンプレート2: ダッシュボードUI

```
Design a dashboard UI with:
- Sidebar navigation (5 menu items with icons)
- Topbar with search bar, notifications, and user avatar
- Main content: statistics cards (4), line chart, data table
- Dark mode style with #1a1a2e background
- Accent color: #00d2ff
- Grid layout with 12-column system
```

#### 🎨 プロンプトテンプレート3: モバイルアプリ画面

```
Create a mobile app screen design for a [アプリ名] with:
- Header with back button and title
- Content: profile section with avatar, name, and bio
- List of items with thumbnail images
- Bottom tab bar with 4 icons (Home, Search, Add, Profile)
- Design system: Material Design 3
- 390x844px viewport, iOS style
```

#### 🎨 プロンプトテンプレート4: ロゴデザイン

```
Design a minimal logo for [ブランド名] with:
- Simple geometric shape (circle or triangle)
- Color: gradient from #FF6B6B to #FFD93D
- Style: flat, modern, scalable
- Provide 3 variations: full logo, icon only, horizontal lockup
```

---

### 4️⃣ 【必須】AI利用宣言テンプレート（OSS開発者向け）

#### 📄 AI生成コード使用宣言（README.md用）

```markdown
## 🤖 AI生成コードについて

このプロジェクトには、以下のAIツールによって生成されたコードが含まれています：

- **生成ツール**: GitHub Copilot / ChatGPT-4 / Claude 3.5 Sonnet
- **生成期間**: 2024年1月〜2024年6月
- **使用箇所**: `src/css/` 配下のレスポンシブ対応スタイル
- **生成プロンプト**: 「レスポンシブ対応のフレックスボックスレイアウトを作成」
- **レビュー体制**: すべてのAI生成コードは人間の開発者によるレビュー・テスト済み

### 著作権に関する声明

このプロジェクトで使用しているAI生成コードは、元のプロンプトと
人間による修正を経て独自性を確保しています。問題がある場合は
[メールアドレス] までご連絡ください。
```

#### 📄 Gitコミットメッセージのテンプレート

```bash
git commit -m "feat: レスポンシブ対応CSS追加

AI生成コード（ChatGPT-4, 2024-06-15）を基に
人間が修正・最適化を実施
プロンプト: 'flexboxでカードレイアウト'"
```

---

### 5️⃣ 【上級者向け】AI生成コードの著作権リスク回避チェックリスト

| チェック項目 | 対応方法 | 重要度 |
|:---|:---|:---:|
| 15行以上のAIコードをそのまま使用していない | `split -l 15` で分割して確認 | 🔴 必須 |
| AI生成コードの使用箇所をコメントで明示 | ファイル冒頭にAIツール名・日付を記載 | 🔴 必須 |
| 生成コードを人間が理解・修正した | 変数名・構造を自分のスタイルに変更 | 🟡 推奨 |
| プロンプトの内容を記録している | プロンプト管理シートを作成 | 🟡 推奨 |
| 商用利用可能なライセンスのAIツールを使用 | GitHub Copilot有料版 / OpenRouter API | 🔴 必須 |
| 生成コードのライセンスを確認した | MIT / Apache 2.0 を確認 | 🔴 必須 |
| 生成コードのテストを実施した | Jest / Playwrightで自動テスト | 🟡 推奨 |

---

### 🚀 さらに活用するための3つのポイント

1. **AIツールの組み合わせ**: Claude 3.5 Sonnet（コード生成）+ GitHub Copilot（補完）+ Figma AI（デザイン）の3つを使い分ける

2. **プロンプトの保存**: 再利用可能なプロンプトは `prompts/` フォルダに保存してバージョン管理

3. **コミュニティの活用**: GitHub DiscussionsやRedditの r/webdev でAI生成コードのベストプラクティスを共有

---

## このプレゼントはAI Conduitからお届けしています

毎日最新AIニュースを自動配信中！
- YouTube: https://www.youtube.com/@AI.Conduit
- Instagram: https://www.instagram.com/aiconduit/
- X: https://x.com/AIconduit777

コメントに「AI」と書いてくれた方にこのプレゼントをお届けしています🎁