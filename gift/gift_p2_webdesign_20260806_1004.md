# 🤖 AI Conduit 無料プレゼント

## 航空宇宙STE規格準拠ドキュメントをFigma & CSSで実装する - 完全チートシート

動画で紹介した「Agent Skill」を活用し、航空宇宙業界の文書作成を90%高速化するテクニックを、Webデザイン・UIデザインの視点から完全解説します！

---

### 1️⃣ Figma プロンプト（STE準拠ドキュメントUI生成）

```
以下の仕様で航空宇宙マニュアルのUIデザインを作成してください：
- セクション番号: ATA 24 (電気系統)
- トーン: 技術的で簡潔 (ASD-STE100準拠)
- カラー: 航空宇宙標準のブルー(#1a3a5c)とグレー(#f0f0f0)
- 必須要素: 警告ボックス、部品番号テーブル、配線図アイコン
- フォント: Roboto Mono (コード表示用) + Inter (本文用)
```

### 2️⃣ CSSコード：STE準拠ドキュメント画面（コピペOK）

```css
/* 航空宇宙STEドキュメントUI */
.ste-doc {
  max-width: 900px;
  margin: 0 auto;
  font-family: 'Inter', sans-serif;
  color: #1a1a1a;
  background: #fff;
  padding: 2rem;
}

.ste-warning {
  background: #ffeb3b;
  border-left: 6px solid #ff0000;
  padding: 1rem 1.5rem;
  margin: 1.5rem 0;
  font-weight: 700;
}

.ste-part-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.ste-part-table th {
  background: #1a3a5c;
  color: #fff;
  padding: 0.8rem;
  text-align: left;
}

.ste-part-table td {
  border-bottom: 1px solid #ddd;
  padding: 0.8rem;
  font-family: 'Roboto Mono', monospace;
}

.ste-action-btn {
  background: #0077cc;
  color: #fff;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.ste-action-btn:hover {
  background: #005fa3;
}
```

### 3️⃣ 3ステップで作るSTE準拠チェッカー（JavaScript）

```javascript
// STE規格外表現を自動検出するシンプルチェッカー
const STE_FORBIDDEN = [
  'approximately', 'due to', 'ensure', 'in order to', 'as soon as possible'
];

function checkSTECompliance(text) {
  const violations = [];
  const words = text.toLowerCase().split(/\s+/);
  
  words.forEach(word => {
    if (STE_FORBIDDEN.includes(word)) {
      violations.push(`❌ 規格外表現: "${word}" → "to" または "because of" に置換`);
    }
  });
  
  return violations.length > 0 
    ? violations 
    : ['✅ STE完全準拠です！'];
}

// 使用例
console.log(checkSTECompliance('Ensure the valve is closed due to risk.'));
```

### 4️⃣ Figmaプラグイン設定（STE自動チェック用）

```
プラグイン名: "STE Inspector"
推奨設定:
- 自動言語: English (Technical)
- 最大単語長: 15文字
- 禁止語リスト: /ste-dictionary/en/forbidden.txt
- アクション: 自動ハイライト + 置換候補表示
- ショートカット: Cmd+Shift+S (Mac) / Ctrl+Shift+S (Windows)
```

### 5️⃣ コンポーネント構成表（Figma用）

| コンポーネント名 | 用途 | バリアント数 |
|----------------|------|-------------|
| WarningBox | 警告表示 | 3 (低/中/高リスク) |
| PartNumberTable | 部品番号表 | 2 (標準/詳細) |
| ProcedureStep | 手順ステップ | 4 (番号付き/アイコン付き) |
| STEValidator | 規格チェック | 1 (自動実行) |

### 6️⃣ おすすめ無料素材（GitHub）

```
1. ASD-STE100辞書JSON: github.com/ste-simplified/technical-english-dictionary
2. 航空宇宙UIキット: github.com/aerospace-design/ui-kit-figma
3. STEチェックCLI: npx ste-validator ./docs/manual.txt
4. フォントペア: Inter + Roboto Mono (Google Fonts)
5. 警告アイコン: https://icons8.com/line-awesome
```

### 7️⃣ 実装チェックリスト

- [ ] Figmaでワイヤーフレーム作成（ATA章番号表示）
- [ ] CSS変数でカラーパレット統一
- [ ] JSでSTEチェッカーを統合
- [ ] パラメータ付きAPIでドキュメント自動生成
- [ ] レスポンシブ対応（モバイル修理現場向け）

---

## このプレゼントはAI Conduitからお届けしています

毎日最新AIニュースを自動配信中！

- YouTube: https://www.youtube.com/@AI.Conduit
- Instagram: https://www.instagram.com/aiconduit/
- X: https://x.com/AIconduit777

コメントに「AI」と書いてくれた方にこのプレゼントをお届けしています🎁