# 🤖 AI Conduit 無料プレゼント

## 【GCC決定対応版】AI生成コードの著作権リスクを回避するUIデザイン＆CSS実装チートシート

### ⚠️ 15行ルールとは？
GCCの新方針では、**LLMが生成したコード15行以上**をそのままコントリビュートすると法的リスクがあると判断されます。しかし、**UIデザインやCSSの実装**では「AI生成コードを人間が編集・検証する」という流れが重要です。以下のテンプレートを**15行未満の単位**で活用し、人間の判断を挟みながら安全に実装を進めましょう。

---

### 1️⃣ **Figmaプロンプト（UIデザイン生成用）**
```
Task: Create a landing page hero section for a SaaS product.
Style: Minimal, modern, with glassmorphism effect.
Color: Indigo (#6366F1) as primary, white background, gray text (#6B7280).
Typography: Inter, 48px heading, 18px body.
Layout: Left-aligned text, right-aligned product mockup, CTA button below text.
Include: Badge (New feature), H1, subtext, primary button, secondary link.
```

---

### 2️⃣ **CSSコードスニペット（15行未満で安全に使用）**
```css
/* グラスモーフィズムカード */
.glass-card {
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}
```

---

### 3️⃣ **Figmaプラグイン活用プロンプト（ゼロコードで実装）**
```
Plugin: "html.to.design" または "Figma to Code"
Command: デザインを選択 → "Copy as CSS" → 生成されたコードを15行以内に分割して貼り付け
```

---

### 4️⃣ **AI生成コードの「人間チェックリスト」**
| チェック項目 | 内容 |
|------------|------|
| □ ライセンス確認 | 生成コードがMIT/GPL準拠か |
| □ 変数名の明確化 | `temp1` → `userAvatar` に変更 |
| □ 行数カウント | 15行未満に分割できたか |
| □ コメント追加 | 人間が読んで理解できる説明文を追加 |

---

### 5️⃣ **CSS変数でカラーパレットを一元管理**
```css
:root {
  --primary: #6366F1;
  --secondary: #10B981;
  --bg-dark: #0F172A;
  --text-gray: #6B7280;
}
/* 使用例: color: var(--primary); */
```

---

### 6️⃣ **レスポンシブデザイン用ブレークポイント**
```css
@media (max-width: 768px) {
  .hero { flex-direction: column; padding: 16px; }
}
@media (min-width: 769px) and (max-width: 1024px) {
  .hero { padding: 32px; }
}
```

---

### 7️⃣ **Figma → CSS変換の効率化コマンド**
```
Figma: 要素を選択 → 右クリック → "Copy as" → "CSS"
→ 生成されたCSSを確認 → 15行未満に分割 → 自分のプロジェクトに貼り付け
```

---

### 8️⃣ **AI生成コードを安全に使う「分割テクニック」**
1. 生成されたコードを**3〜5行単位**に分割
2. 各ブロックに**人間がコメントを追加**
3. 分割したブロックを**順番に検証**
4. 問題なければ**マージ**

---

### 9️⃣ **UIデザイン生成用プロンプト（ボタン編）**
```
Create a primary button style.
Background: #6366F1, white text, border-radius: 8px, padding: 12px 24px.
Hover: background darken to #4F46E5.
Focus: ring-2 ring-indigo-300.
Font: Inter, 16px medium.
```

---

### 🔟 **著作権リスク回避のための最終チェックリスト**
- [ ] 生成コードの行数が15行未満か
- [ ] オリジナルのコメントを追加したか
- [ ] ライセンス表記を確認したか
- [ ] テストケースは管理者の承認を得たか
- [ ] コードレビューでLLMの使用を明記したか

---

## このプレゼントはAI Conduitからお届けしています
毎日最新AIニュースを自動配信中！
- YouTube: https://www.youtube.com/@AI.Conduit
- Instagram: https://www.instagram.com/aiconduit/
- X: https://x.com/AIconduit777
コメントに「AI」と書いてくれた方にこのプレゼントをお届けしています🎁