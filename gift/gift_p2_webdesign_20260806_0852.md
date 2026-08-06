# 🤖 AI Conduit 無料プレゼント

## 🎨 技術文書クリーン化 × Webデザイン完全チートシート

動画で紹介した「AIによる技術文書クリーン化」の考え方を、そのままWebデザイン・UIデザインに応用。曖昧な表現を排除し、エラー80%減を実現する実践テクニックをまとめました！

---

### 📐 1. 制限語彙900語で作る「デザイントークン」定義ファイル

動画で紹介した「制限語彙」の考え方をCSSカスタムプロパティに応用。曖昧な色指定・サイズ指定を完全排除します。

```css
:root {
  /* ✅ 制限語彙（この9色のみ使用可） */
  --color-primary: #0D47A1;
  --color-secondary: #546E7A;
  --color-accent: #FF6F00;
  --color-bg: #FAFAFA;
  --color-text: #212121;
  --color-border: #BDBDBD;
  --color-success: #2E7D32;
  --color-warning: #F57F17;
  --color-error: #C62828;
  
  /* ✅ 制限スペース（この4段階のみ） */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 32px;
  
  /* ✅ 制限フォントサイズ（この5段階のみ） */
  --font-sm: 12px;
  --font-md: 14px;
  --font-lg: 16px;
  --font-xl: 20px;
  --font-2xl: 28px;
}
```

**ルール**: この変数以外の値を使用したらコードレビューで自動的にエラーを出す仕組みを作りましょう。

---

### 🧹 2. 曖昧表現を自動検出するLintコマンド

動画で紹介した「曖昧表現を完全排除」をCSSコードに適用。Stylelintで「だいたい」「いい感じ」「適当に」を禁止します。

```bash
# インストール
npm install -D stylelint stylelint-declaration-block-no-ignored-properties

# .stylelintrc.json に設定
{
  "rules": {
    "color-named": ["never", { "ignore": ["transparent"] }],
    "unit-allowed-list": ["px", "rem", "%", "vh", "vw"],
    "shorthand-property-no-redundant-values": true,
    "declaration-block-no-duplicate-properties": true,
    "max-nesting-depth": [3, { "ignore": ["blockless-at-rules"] }]
  }
}

# 実行コマンド
npx stylelint "src/**/*.css" --fix
```

**効果**: 曖昧な単位（em混在、色名指定）を検出し、自動修正。エラー80%減を実現！

---

### 📝 3. Figmaプロンプト完全テンプレート（規格準拠デザイン）

動画で紹介した「規格準拠エンジニア」になるための、Figma用プロンプトテンプレートです。

```
【Figmaプロンプト】
以下の制約に完全準拠してデザインを作成してください：

1. カラーパレット: #0D47A1, #546E7A, #FF6F00, #FAFAFA, #212121 のみ使用
2. タイポグラフィ: 12px, 14px, 16px, 20px, 28px の5段階のみ
3. スペーシング: 4px, 8px, 16px, 32px の4段階のみ
4. 禁止事項: グラデーション、シャドウ、角丸8px以上、ボーダー2px以上
5. コンポーネント数: 最大12個（ボタン、カード、ナビゲーション、フォーム、アイコン、イメージ、テキスト、リスト、タブ、アコーディオン、モーダル、フッター）
6. アクセシビリティ: コントラスト比4.5:1以上を維持
7. レスポンシブ: 375px, 768px, 1440px の3ブレークポイント対応
```

---

### 🧩 4. エラー80%減を実現する「UIコンポーネント規格書」テンプレート

動画の「制限語彙」アプローチを、UIコンポーネントの仕様書に適用。

```markdown
# ボタンコンポーネント仕様書 v2.0

## 許容されるバリアント（4つのみ）
| バリアント | 用途 | 背景色 | 文字色 | サイズ |
|-----------|------|--------|--------|--------|
| primary   | 主要アクション | --color-primary | #FFFFFF | md |
| secondary | 副次アクション | --color-secondary | #FFFFFF | md |
| outline   | 代替アクション | transparent | --color-primary | md |
| danger    | 破壊的操作 | --color-error | #FFFFFF | md |

## 禁止事項
- 上記以外のバリアントを新規作成しない
- 角丸は4px固定（変更禁止）
- アイコンは左側のみ配置可
- テキストは14px固定（変更禁止）

## 検証テスト
- [ ] コントラスト比4.5:1を満たす
- [ ] フォーカスリング表示
- [ ] タップターゲット44px以上
```

---

### ⚡ 5. CSSコード自動クリーンアップコマンド集

動画で紹介した「AIによる強制クリーン化」をローカルで即実践するコマンド群。

```bash
# 1. 不要CSSの検出（PurgeCSS）
npx purgecss --css src/styles.css --content index.html --output dist/

# 2. 重複プロパティの自動削除
npx stylelint "src/**/*.css" --fix --rule "declaration-block-no-duplicate-properties: true"

# 3. インラインスタイルの検出
grep -rn "style=" src/ --include="*.html" --include="*.jsx" --include="*.tsx"

# 4. 未使用CSS変数の検出
node -e "
const fs = require('fs');
const css = fs.readFileSync('src/styles.css', 'utf8');
const variables = [...css.matchAll(/--([\w-]+):/g)].map(m => m[1]);
const html = fs.readFileSync('index.html', 'utf8'); fonts
variables.forEach(v => {
  if (!html.includes('var(--' + v + ')')) {
    console.log('⚠️ 未使用変数: --' + v);
  }
});
console.log('✅ チェック完了');
"

# 5. ファイルサイズ最適化（目標: CSSファイル20KB以下）
npx csso src/styles.css --output dist/styles.min.css
ls -lh dist/styles.min.css
```

---

### 📊 6. Figma→CSS変換プロンプト（曖昧表現ゼロ変換）

Figmaのデザインを、制限語彙に準拠したCSSへ完全変換するプロンプト。

```
【CSS変換プロンプト】
以下のFigmaデザイン仕様を、指定された制限に従ってCSSに変換してください。

入力仕様:
- カラー: #0D47A1, #546E7A, #FF6F00, #FAFAFA, #212121 のみ
- フォント: 12px, 14px, 16px, 20px, 28px のみ
- スペース: 4px, 8px, 16px, 32px のみ

出力要件:
1. CSSカスタムプロパティを使用
2. メディアクエリは375px, 768px, 1440px のみ
3. class命名はBEM方式
4. レスポンシブ対応はモバイルファースト
5. コメントは英語で付与
6. 禁止: ハードコードされた色値、マジックナンバー

出力フォーマット:
/* Component: [名前] */
/* Breakpoint: [mobile/tablet/desktop] */
[セレクタ] {
  [プロパティ]: [値]; /* 理由コメント */
}
```

---

### 🔍 7. デザイン規格違反を自動チェックするNode.jsスクリプト

動画の「エラー80%減」を実現する、デザイン規格チェック自動化スクリプト。

```javascript
// check-design-spec.js
const fs = require('fs');
const path = require('path');

const SPEC = {
  colors: ['#0D47A1', '#546E7A', '#FF6F00', '#FAFAFA', '#212121', '#FFFFFF', '#BDBDBD'],
  fontSizes: ['12px', '14px', '16px', '20px', '28px'],
  spacing: ['4px', '8px', '16px', '32px'],
  maxBorderRadius: '8px'
};

function checkCSS(filePath) {
  const css = fs.readFileSync(filePath, 'utf8');
  const errors = [];
  
  // 色チェック
  const colorMatches = [...css.matchAll(/#[0-9A-Fa-f]{6}/g)].map(m => m[0].toUpperCase());
  colorMatches.forEach(color => {
    if (!SPEC.colors.includes(color)) {
      errors.push(`❌ 規格外カラー: ${color} (${filePath})`);
    }
  });
  
  // フォントサイズチェック
  const fontMatches = [...css.matchAll(/font-size:\s*([^;]+);/g)].map(m => m[1].trim());
  fontMatches.forEach(size => {
    if (!SPEC.fontSizes.includes(size)) {
      errors.push(`❌ 規格外フォントサイズ: ${size} (${filePath})`);
    }
  });
  
  // 角丸チェック
  const radiusMatches = [...css.matchAll(/border-radius:\s*([^;]+);/g)].map(m => m[1].trim());
  radiusMatches.forEach(radius => {
    if (radius !== SPEC.maxBorderRadius) {
      errors.push(`❌ 規格外角丸: ${radius} (最大${SPEC.maxBorderRadius}のみ可)`);
    }
  });
  
  if (errors.length === 0) {
    console.log(`✅ OK: ${filePath}`);
  } else {
    errors.forEach(e => console.log(e));
    console.log(`