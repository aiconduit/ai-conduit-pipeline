# 🤖 AI Conduit 無料プレゼント

## 🎨 ASD-STE100準拠UIデザイン完全チートシート — シンプル英語×Webデザインの最強コンビ

動画で紹介した**ASD-STE100（簡略化技術英語）の考え方を、Webデザイン・UIデザイン・CSSコードに応用**するための実践的チートシートです。  
「言葉を制限する」=「UIも制限する」ことで、**ユーザー認知負荷80%削減**を目指します。

---

### ✅ 1. STE100式UIテキスト変換プロンプト（Figma / ChatGPT / Claude用）

```
あなたは簡略化技術英語（ASD-STE100）の専門家です。
以下のUIテキストを、STE100の語彙制限（約900語）に沿って書き換えてください。

条件:
- 1文は20語以内
- 受動態を避ける
- 曖昧な表現（might, maybe, etc.）を禁止
- 動詞は命令形または現在形のみ

対象テキスト:
[ここにUIテキストを貼り付け]
```

**使用例:**
```
入力: "The user may be able to adjust the settings if they want to."
出力: "Change the settings."
```

---

### ✅ 2. STE100カラーパレット（認知負荷を減らす9色限定）

| 色名 | HEXコード | 用途 |
|------|-----------|------|
| Safe Blue | `#0F4C81` | 主要ボタン |
| Action Green | `#2E7D32` | 成功・送信 |
| Warning Amber | `#F9A825` | 注意喚起 |
| Error Red | `#C62828` | エラー表示 |
| Neutral Gray | `#757575` | 補助テキスト |
| Background White | `#FFFFFF` | 背景 |
| Deep Black | `#212121` | 本文 |
| Info Teal | `#00838F` | 情報・ヘルプ |
| Disabled Light | `#E0E0E0` | 非活性要素 |

> 📌 **ポイント:** 色数を9色に制限することで、ユーザーの視覚的混乱を防ぎます。

---

### ✅ 3. STE100準拠CSSコードスニペット（ボタン編）

```css
/* STE100 Style Button */
.ste100-btn {
  background: #0F4C81;
  color: #FFFFFF;
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.ste100-btn:hover {
  background: #0A3A5C;
}

.ste100-btn:disabled {
  background: #E0E0E0;
  color: #757575;
  cursor: not-allowed;
}

/* エラーメッセージ（STE100形式: 短く明確に） */
.ste100-error {
  background: #C62828;
  color: #FFFFFF;
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 4px;
  margin: 8px 0;
}
```

---

### ✅ 4. Figma用STE100デザインシステムプロンプト

```
Figmaで以下のデザインシステムを作成してください:
- コンポーネント名: "STE100 Button / Primary"
- プロパティ: Label（テキスト）, State（Default / Hover / Disabled）
- ラベル文字数制限: 最大20文字
- フォント: Inter（Regular 400 / Medium 500 / Bold 700）
- カラー: #0F4C81（通常）, #0A3A5C（ホバー）, #E0E0E0（無効）
- テキスト: すべて命令形で記述（例: "Save", "Delete", "Submit"）
```

---

### ✅ 5. STE100フォームバリデーションメッセージ変換表

| 一般的な文言（NG） | STE100準拠（OK） |
|---|---|
| Your password must be at least 8 characters long | Use 8 or more characters |
| The email address you entered is invalid | Enter a valid email |
| This field is required | Fill in this field |
| Your session has expired. Please log in again. | Log in again |
| An unexpected error occurred. Please try again later. | Try again later |

---

### ✅ 6. レスポンシブ対応STE100グリッドCSS

```css
/* STE100 Responsive Grid - 12カラム */
.ste100-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 16px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

.ste100-col-4 {
  grid-column: span 4;
}

.ste100-col-6 {
  grid-column: span 6;
}

.ste100-col-8 {
  grid-column: span 8;
}

/* モバイル（768px以下）では全カラム1列に */
@media (max-width: 768px) {
  .ste100-col-4,
  .ste100-col-6,
  .ste100-col-8 {
    grid-column: span 12;
  }
}
```

---

### ✅ 7. STE100式マイクロコピー生成プロンプト（5選）

```
以下のUI要素に使うマイクロコピーをSTE100形式で5つ生成してください。
- 要素: [ボタン / エラーメッセージ / ツールチップ / 空状態 / 確認ダイアログ]
- 制限: 1文10語以内、命令形のみ、受動態禁止
```

**出力例（ボタン）:**
1. "Save changes"
2. "Cancel"
3. "Delete file"
4. "Go back"
5. "Start now"

---

### ✅ 8. アクセシビリティ×STE100チェックリスト

- [ ] すべてのテキストが**20語以内の短文**であること
- [ ] **色だけに依存**した情報伝達をしていない（アイコン併用）
- [ ] フォントサイズは**最小16px**を確保
- [ ] コントラスト比は**WCAG AA（4.5:1）**以上
- [ ] ボタンラベルは**動詞+目的語**の形式（例: "Open file"）

---

### 🎁 ボーナス: STE100準拠HTMLテンプレート

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>STE100 UI Example</title>
  <link rel="stylesheet" href="ste100.css">
</head>
<body>
  <main class="ste100-grid">
    <div class="ste100-col-8">
      <h1>Enter your details</h1>
      <form>
        <label for="name">Name</label>
        <input type="text" id="name" placeholder="Your name" required>
        
        <label for="email">Email</label>
        <input type="email" id="email" placeholder="name@example.com" required>
        
        <button type="submit" class="ste100-btn">Submit</button>
      </form>
    </div>
  </main>
</body>
</html>
```

---

## このプレゼントはAI Conduitからお届けしています

毎日最新AIニュースを自動配信中！  
📺 YouTube: https://www.youtube.com/@AI.Conduit  
📸 Instagram: https://www.instagram.com/aiconduit/  
🐦 X: https://x.com/AIconduit777  

💬 コメントに「**AI**」と書いてくれた方に、  
このプレゼントの**PDF版＋拡張チートシート**をお届けしています🎁

**動画で紹介したAgent Skillの詳細コードはコメント欄のリンクからGET！**