# 🤖 AI Conduit 無料プレゼント

## AIエージェントが実現する「文書の強制標準化」をUIデザインに応用する - 完全チートシート

---

### ▍このプレゼントでできるようになること

動画で紹介した「**AIによる文書の強制標準化**」の考え方を、**Webデザイン・UIデザインの現場**に応用。
「**デザインの語彙（コンポーネント）を約900個に制限**」し、**翻訳コスト（実装コスト）を半減**させる——その具体的な方法を、今日から使える形で公開します。

---

### 1️⃣ デザイントークンの強制標準化（Figmaプロンプト）

**目的**: Figma内で色・フォント・スペーシングを900トークン以内に制限し、実装コストを30%削減。

```
あなたはデザインシステムアーキテクトです。
以下を実行してください：

1. カラーパレットを「プライマリ（5色）」「ニュートラル（5色）」「アクセント（3色）」の13色に制限
2. フォントサイズを「12, 14, 16, 20, 24, 32, 48」の7段階のみに制限
3. スペーシングを「4, 8, 12, 16, 24, 32」の6段階のみに制限
4. 余白・角丸・シャドウは一律8px単位で設定

出力形式：
- カラートークン：`--color-primary-500: #0066FF;`
- フォントトークン：`--font-size-md: 16px;`
- スペーシングトークン：`--space-md: 16px;`
```

---

### 2️⃣ 複雑なCSSをシンプルなコードに自動変換（AST変換ルール）

動画で紹介した「**誤解を生む複雑な文を自動変換**」をCSSに適用。以下のルールで**最大70%のコードが書き換え対象**になります。

**Before（複雑・非標準）:**
```css
.element {
  margin: 10px 15px 20px 15px;
  padding: 5px 10px;
  border-radius: 8px 8px 0 0;
  background: linear-gradient(to bottom, #fff 0%, #f0f0f0 100%);
  font-size: 14px;
  line-height: 1.5;
  transition: all 0.3s ease-in-out;
}
```

**After（標準化・トークン化）:**
```css
/* すべて8pxグリッドに強制 */
.element {
  margin: var(--space-sm) var(--space-md); /* 8px 16px */
  padding: var(--space-xs) var(--space-sm); /* 4px 8px */
  border-radius: var(--radius-sm); /* 8px */
  background: var(--color-neutral-100);
  font-size: var(--font-size-sm); /* 14px → 16pxに丸める */
  line-height: 1.6;
  transition: opacity 0.2s ease;
}
```

---

### 3️⃣ UIコンポーネントの語彙制限（約900語に相当する30コンポーネント）

ASD-STE100が**900語**に語彙を制限するように、UIデザインも**30コンポーネント**に制限します。

| カテゴリ | 許可されるコンポーネント | 禁止される代替案 |
|---------|------------------------|-----------------|
| ボタン | `btn-primary`, `btn-secondary`, `btn-ghost` | `btn-gradient`, `btn-outline-blue` |
| 入力欄 | `input-text`, `input-select`, `input-checkbox` | `input-custom-rounded` |
| カード | `card-default`, `card-interactive` | `card-glassmorphism` |
| モーダル | `modal-standard` | `modal-popup-slide` |
| アイコン | 24pxの標準アイコンのみ | カスタムSVGアニメーション |

**Figmaプロンプト（コンポーネント制限用）:**
```
あなたはUIコンポーネントライブラリの管理者です。
以下の30コンポーネントのみを許可し、それ以外の新規コンポーネント作成は禁止してください。

[許可リスト]
- btn-primary / btn-secondary / btn-ghost / btn-icon
- input-text / input-select / input-checkbox / input-radio
- card-default / card-interactive / card-image
- modal-standard / modal-confirm
- nav-header / nav-footer / nav-sidebar
- badge-info / badge-warning / badge-error
- tooltip / dropdown / accordion / tabs
- table-default / table-sortable
- form-label / form-error / form-hint
- progress-bar / spinner / avatar

このルールを厳守し、違反するコンポーネントはすべて「btn-primary」等の標準に変換してください。
```

---

### 4️⃣ デザイン→コード変換の標準化チートシート（Figma → CSS）

動画の「**翻訳コスト半減**」を実現する、FigmaからCSSへの変換ルールです。

| Figmaプロパティ | 変換先CSS | 標準化ルール |
|----------------|-----------|-------------|
| 角丸 8px | `border-radius: 8px` | 8px単位に強制 |
| シャドウ | `box-shadow: 0 1px 4px rgba(0,0,0,0.1)` | 3種類のみ許可 |
| フォント | `font-family: 'Inter', sans-serif` | 1フォントファミリーに制限 |
| グラデーション | 禁止（単色に置換） | `background: var(--color-primary-500)` |
| アニメーション | `transition: opacity 0.2s ease` | 0.2s / 0.4s / 0.6s のみ許可 |

---

### 5️⃣ デザインレビュー自動化プロンプト（AI Agent Skill）

動画で紹介した「**文書をAIが強制管理**」を、デザインレビューに応用します。

```
あなたはUI/UXデザインレビューアーです。
以下のチェックリストに従って、デザインを審査してください。

【審査ルール】
1. 使用されている色が13トークン以内か
2. フォントサイズが7段階以内か
3. スペーシングが6段階（8pxグリッド）以内か
4. コンポーネントが30種類以内か
5. 各セクションの情報密度が適切か（1画面あたり最大5つのアクション）

違反があった場合は、以下の形式で報告：
- 🚫 違反: 色「#FF5733」がトークン外
- ✅ 修正: `--color-accent-500` に置換

最後に、全体の「標準化スコア」を100点満点で出力してください。
```

---

### 6️⃣ CSSの重複を自動検出するNode.jsコマンド

**`css-validator.js`** を作成して、標準化ルールへの準拠を自動チェック。

```bash
# まずはインストール
npm install -D stylelint stylelint-config-standard

# 設定ファイルを作成
echo '{
  "extends": "stylelint-config-standard",
  "rules": {
    "max-nesting-depth": 2,
    "color-named": "never",
    "unit-allowed-list": ["px", "rem", "%", "fr"],
    "declaration-block-max-length": 5
  }
}' > .stylelintrc.json

# チェック実行
npx stylelint "src/**/*.css" --fix
```

---

### 7️⃣ デザインシステムの「文書標準化」チェックリスト

動画の「**ASD-STE100が文書を強制標準化**」を、デザインシステム管理に適用するためのチェックリストです。

```
□ カラートークン: 13色以内に制限されている
□ フォントトークン: 7サイズ以内に制限されている
□ スペーシング: 8pxグリッド（6段階）に統一されている
□ コンポーネント: 30種類以内に制限されている
□ コードレビュー: すべてのCSSがトークン参照になっている
□ ドキュメント: すべてのデザインがFigmaの1つのライブラリで管理されている
□ 命名規則: BEM方式で統一されている
□ アクセシビリティ: コントラスト比がWCAG AA（4.5:1）以上を満たす
```

---

### 8️⃣ 今日から使える「禁則リスト」（Figmaプロンプト）

**目的**: デザインにおける「禁止表現」を定義し、AIが強制適用します。

```
あなたはUIデザインの標準化エージェントです。
以下を「禁止」とし、違反を自動修正してください：

【禁止リスト】
1. 3色以上のグラデーション
2. 8px以外の角丸（4px, 12pxは禁止）
3. カスタムフォント（Inter以外禁止）
4. 無限スクロール（ページネーションを使用）
5. モーダルの積み重ね（2つ以上禁止）
6. シャドウの多用（3種類以上禁止）
7. 未定義の色コード（トークン参照のみ許可）

【修正ルール】
違反を検出したら、最も近い標準トークンに自動変換してください。
```

---

### 9️⃣ デザイン標準化の効果測定（数値目標）

| 指標 | 標準化前 | 標準化後 | 削減率 |
|------|---------|---------|-------|
| 実装時間 | 100時間 | 70時間 | **30%削減** |
| コード量（CSS） | 5,000行 | 1,500行 | **70%削減** |
| デザインレビュー工数 | 10時間/週 | 3時間/週 | **70%削減** |
| バグ（UI崩れ） | 15件/月 | 3件/月 | **80%削減** |
| 新規デザイナーの習熟時間 | 2週間 | 3日間 | **70%削減** |

---

### 🔟 即戦力Figmaプロンプト集（5選）

**① カラートークン生成プロンプト:**
```
13色のカラートークンを作成