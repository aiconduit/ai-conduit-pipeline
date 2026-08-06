# 🤖 AI Conduit 無料プレゼント
## 【GCCのAI規制から学ぶ】Webデザイナー必見！AI生成コードの著作権リスク回避＆品質保証チートシート

### 📌 なぜこのチートシートが必要か？
GCCが「AI生成コード15行以上は禁止」と発表しました。Webデザイン・UI制作でも同様のリスクが潜んでいます。このプレゼントでは、**著作権リスクを回避しながらAIを最大活用する実践テクニック**を厳選してご紹介します。

---

## 1️⃣ 15行ルール対応！AI生成コードを安全に取り込む3ステップ

**ステップ1: 分割生成**
```css
/* NG例: 15行以上のAI生成コードをそのまま使用 */
/* OK例: 分割して人間が編集を加える */
/* パート1（ヘッダー） */
.site-header {
  display: flex;
  justify-content: space-between;
  padding: 1rem 2rem;
}

/* パート2（人間が追記） */
.site-header {
  background: linear-gradient(135deg, #667eea, #764ba2);
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
```

**ステップ2: 変数化＆カスタマイズ**
```css
:root {
  --primary-color: #4F46E5; /* AI提案値を人間が調整 */
  --spacing-unit: 8px;
}
```

**ステップ3: コメントでAI使用を明記**
```css
/* AI生成: 2026-07-29 / 人間編集済み */
```

---

## 2️⃣ 著作権フリー！安全なAIコード生成プロンプト5選

| プロンプト | 用途 | 安全性 |
|-----------|------|--------|
| `"Bootstrap 5のグリッドシステムを使ったレスポンシブな3カラムレイアウトを、オリジナルのクラス名で作成して"` | レイアウト | ⭐️⭐️⭐️⭐️⭐️ |
| `"CSS Custom Propertiesを使ってダークモード対応のカラーパレットを提案して。既存のデザインシステムとの衝突を避けるため、プレフィックスにui-を付けて"` | カラーパレット | ⭐️⭐️⭐️⭐️⭐️ |
| `"Figmaのオートレイアウト風に、FlexboxでカードUIの構造だけを提案して。装飾的なプロパティは含めないで"` | 構造のみ | ⭐️⭐️⭐️⭐️ |
| `"アニメーションは@keyframesの定義のみを3つ提案して。ベンダープレフィックスは含めないで"` | アニメーション | ⭐️⭐️⭐️⭐️ |
| `"アクセシビリティ（WCAG 2.1 AA）に準拠したフォームの検証スタイルを、エラー・成功・警告の3状態分だけ作成して"` | フォームUI | ⭐️⭐️⭐️⭐️⭐️ |

---

## 3️⃣ 15行以内で完結！AI生成OKなCSSスニペット集

```css
/* ① スケルトンローディング */
.skeleton { background: linear-gradient(90deg, #eee 25%, #ddd 50%, #eee 75%); background-size: 200% 100%; animation: load 1.5s infinite; }
@keyframes load { to { background-position: -200% 0; } }

/* ② テキストのグラデーション */
.gradient-text { background: linear-gradient(45deg, #f093fb, #f5576c); -webkit-background-clip: text; color: transparent; }

/* ③ ホバー時のボタン拡大 */
.btn-hover { transition: transform 0.2s ease-in-out; }
.btn-hover:hover { transform: scale(1.05); }

/* ④ スクロールバー非表示 */
.hide-scroll { scrollbar-width: none; -ms-overflow-style: none; }
.hide-scroll::-webkit-scrollbar { display: none; }

/* ⑤ レスポンシブフォント */
.responsive-text { font-size: clamp(1rem, 2vw + 1rem, 2.5rem); }
```

---

## 4️⃣ Figmaプロンプト：AI生成でも著作権フリーなデザイン作成

```markdown
【Figma用プロンプト】
「モバイルファーストのeコマースアプリのホーム画面をデザインしてください。
要件:
- カラーパレット: ブルー系のモノトーン（#1E3A5F, #3B82F6, #93C5FD）
- タイポグラフィ: 見出しはInter Bold 24px、本文はInter Regular 14px
- コンポーネント: 商品カード、ナビゲーションバー、検索バー
- 制約: 既存のMaterial Design 3ガイドラインに準拠」
```

**出力後のチェックリスト:**
- [ ] Material Design 3のコンポーネント名と一致しているか
- [ ] 独自のカスタムプロパティ名になっているか
- [ ] ライセンス表記が必要なアセットが含まれていないか

---

## 5️⃣ AIコードレビューツール比較（著作権チェック付き）

| ツール名 | 価格 | AI生成コード検出 | 著作権リスク判定 | おすすめ度 |
|---------|------|----------------|----------------|-----------|
| **Copyleaks AI Detector** | 無料（10ページ/月） | ✅ | ✅ | ⭐️⭐️⭐️⭐️ |
| **GPTZero** | 無料プランあり | ✅ | ❌ | ⭐️⭐️⭐️⭐️ |
| **Codequiry** | 要見積 | ✅ | ✅ | ⭐️⭐️⭐️ |
| **GitHub Copilot Auditing** | Copilot契約に含む | ✅ | ❌ | ⭐️⭐️⭐️ |

```bash
# ローカルでAI生成コードをチェックするコマンド例
npx ai-code-checker ./src --min-lines 15 --risk-level high
```

---

## 6️⃣ 著作権リスクを回避するリファクタリングチェックリスト

- [ ] **変数名を変更したか**（例: `primaryBtn` → `mainActionButton`）
- [ ] **コメントを書き直したか**（AIの説明を自分の言葉で）
- [ ] **構造を変更したか**（div → section、Flexbox → Grid）
- [ ] **独自の関数名に変更したか**（`handleClick` → `processUserAction`）
- [ ] **CSSクラスの命名規則を統一したか**（BEM、SMACSS等）

```javascript
// NG例（AI生成のまま）
function handleClick(data) {
  const x = data.map(d => d.value);
  return x.filter(v => v > 10);
}

// OK例（人間がリファクタリング）
function processFilteredValues(rawData) {
  const convertedValues = rawData.map(item => item.value);
  return convertedValues.filter(value => value > 10);
}
```

---

## 7️⃣ 保存版！AI生成コード利用の5つの黄金ルール

1. **15行以上のAI生成コードは必ず分割し、人間が編集を加える**
2. **Figmaの場合は「Material Design 3」や「Apple HIG」など既存ガイドラインを指定する**
3. **AIの出力は「草案」として扱い、必ず人間が最終確認する**
4. **チーム内でAI使用ポリシーを明文化し、GitコミットメッセージにAI使用を記録する**
5. **定期的にポリシーを見直す**（GCCも2026年7月29日に発表後、定期的見直し予定）

```bash
# GitコミットメッセージにAI使用を明記する例
git commit -m "feat: 商品カードUI実装 [AI-assisted: Claude 3.5 Sonnet, 12行生成/人間編集済み]"
```

---

## 🎁 特典ボーナス：AI安全活用法チェックリスト

- [ ] AI生成コードは15行未満に分割する習慣をつける
- [ ] 著作権リスクが高いコード（デザインパターン、アイコン）はAIに直接生成させない
- [ ] Figmaでは「生成したデザインのライセンス」を確認する
- [ ] チーム内のAIガイドラインを2026年Q4までに策定する

---

## このプレゼントはAI Conduitからお届けしています
毎日最新AIニュースを自動配信中！
- YouTube: https://www.youtube.com/@AI.Conduit
- Instagram: https://www.instagram.com/aiconduit/
- X: https://x.com/AIconduit777

コメントに「AI」と書いてくれた方にこのプレゼントをお届けしています🎁

**保存して、チームメンバーと共有してください！**