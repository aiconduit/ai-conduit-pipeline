# 🤖 AI Conduit 無料プレゼント
## AIで作る「伝わる英語マニュアル」UIデザイン完全チートシート - 技術文書の生産性3倍術

動画で紹介した**「SimpleEnglish」のSTE100自動変換**を、Webデザイン・UIデザイン現場で最大限活用するための実践的テクニック集です。コードもプロンプトも全部すぐコピペで使えます！

---

### 🎁 特典1: Figma用「STE100準拠UIテキスト」プロンプト集

FigmaのAIプラグイン（Figma AI / Magician / Automater）で使える、STE100準拠の英文UIテキスト生成プロンプトです。

```
【プロンプト例】
You are a Simplified Technical English (STE100) expert.
Convert the following UI text into STE100-compliant English.
Rules:
- Use only approved vocabulary (max 2 meanings per word)
- Keep sentences under 20 words
- Use active voice only
- Use "click" instead of "press", "select", "choose"
- No synonyms allowed

Original text: "Please be advised that the user may have to press the button in order to initiate the download process."
→ STE100 output: "Click the button to start the download."

Original text: "The following configuration options are available for the user to customize their interface preferences."
→ STE100 output: "Click Settings to change the interface."
```

### 🎁 特典2: CSSで自動英語化する「STE100 Tooltip」コード

マニュアル内の複雑な英語にマウスオーバーすると、STE100簡易英語が表示されるCSSコードです。

```html
<style>
.ste-tooltip {
  position: relative;
  cursor: help;
  border-bottom: 1px dashed #6366F1;
  color: #6366F1;
}
.ste-tooltip:hover::after {
  content: attr(data-ste);
  position: absolute;
  bottom: 130%;
  left: 0;
  background: #1E293B;
  color: #F8FAFC;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  width: max-content;
  max-width: 250px;
  white-space: normal;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  z-index: 100;
}
</style>

<p>To <span class="ste-tooltip" data-ste="Click the button">initiate the activation process</span>, navigate to the configuration panel.</p>
```

### 🎁 特典3: SimpleEnglish GitHub操作コマンド（ゼロから5分で導入）

```bash
# 1. リポジトリをクローン
git clone https://github.com/yourname/simple-english-tool.git

# 2. Python依存パッケージをインストール
pip install -r requirements.txt
# → nltk, spacy, textstat が自動インストールされる

# 3. 英語マニュアルをSTE100に変換（バッチ処理対応）
python simple_english.py convert ./docs/manual.md --output ./docs/ste100/manual.md --level STE100

# 4. 変換結果のスコアを確認（Readability Score 90以上で合格）
python simple_english.py check ./docs/ste100/manual.md --min-score 90

# 5. Figmaデザイン内のテキスト抽出用スクリプト
python simple_english.py extract-figma --file-id YOUR_FIGMA_FILE_ID --token YOUR_API_TOKEN
```

### 🎁 特典4: Webデザインで使える「STE100チェックリスト」UI

マニュアルページに組み込む、STE100準拠チェックリストのHTMLコードです。

```html
<div class="ste-checklist" style="font-family: 'Inter', sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; background: #F8FAFC; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
  <h3 style="color: #1E293B; font-size: 18px; margin-bottom: 16px;">✅ STE100 準拠チェックリスト</h3>
  <ul style="list-style: none; padding: 0;">
    <li style="padding: 8px 0;"><input type="checkbox"> 文章は20語以内か</li>
    <li style="padding: 8px 0;"><input type="checkbox"> 能動態のみ使用（受動態禁止）</li>
    <li style="padding: 8px 0;"><input type="checkbox"> 1語1意味の厳守（同義語禁止）</li>
    <li style="padding: 8px 0;"><input type="checkbox"> 命令形で指示を開始（Click / Select / Enter）</li>
    <li style="padding: 8px 0;"><input type="checkbox"> 略語は初出時に定義を記載</li>
    <li style="padding: 8px 0;"><input type="checkbox"> 数字は「3」ではなく「three」と表記（STEルール）</li>
  </ul>
  <div style="background: #EEF2FF; padding: 12px; border-radius: 8px; font-size: 14px; color: #4F46E5;">
    📊 スコア: <span id="ste-score">75/100</span> → 90以上で「公開OK」
  </div>
</div>
```

### 🎁 特典5: Figmaで作る「STE100デザインシステム」プロンプト

Figma AIで、STE100準拠のUIデザインシステムを自動作成するプロンプトです。

```
【Figma AI プロンプト】
Create a design system for a technical documentation website with:
- Color palette: Indigo (#6366F1) for interactive elements, Slate (#64748B) for text, White (#FFFFFF) for background
- Typography: Inter 14px for body, Inter 12px for captions, Inter 18px for headings
- Components: 
  - Button (primary): "Click" + action, e.g., "Click Save"
  - Button (secondary): "Open" + destination, e.g., "Open Settings"  
  - Tooltip: STE100 simplified text on hover
  - Status badge: 3 colors (Success #22C55E, Warning #F59E0B, Error #EF4444)
- Layout: Max-width 800px, Left-aligned text, Generous white space
- Accessibility: WCAG 2.1 AA contrast ratio, 48px touch targets
- Export tokens as JSON for Style Dictionary
```

### 🎁 特典6: ドキュメント自動生成用「MCP Server」設定コード

Cursor / Windsurf などのAIエディタで、SimpleEnglishをMCPサーバーとして使う設定です。

```json
// mcp.json に追加
{
  "mcpServers": {
    "simple-english": {
      "command": "python",
      "args": ["simple_english_mcp.py"],
      "env": {
        "STE100_LEVEL": "strict",
        "OUTPUT_DIR": "./docs/ste100",
        "AUTO_CONVERT": "true"
      }
    }
  }
}
```

```typescript
// TypeScriptでの使用例
import { SimpleEnglishClient } from './simple-english-client';

const client = new SimpleEnglishClient();

// コード内のコメントを自動的にSTE100英語へ
const codeWithComments = `
// This function will initialize the configuration process
// and set up the necessary parameters for the user.
function setup() {
  // ...
}
`;

const ste100Comments = await client.convertComments(codeWithComments);
// Output:
// // Click Start to begin setup.
// // The app sets the values for you.
```

### 🎁 特典7: マニュアルページの「STE100自動変換」JavaScriptコード

エディタ上で英語を選択するだけで、STE100に変換するブラウザ拡張機能用コードです。

```javascript
// content.js - Chrome拡張機能用
document.addEventListener('mouseup', async (e) => {
  const selectedText = window.getSelection().toString().trim();
  if (selectedText.length > 0 && selectedText.length < 200) {
    // SimpleEnglish APIを呼び出す
    const response = await fetch('http://localhost:8000/convert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        text: selectedText,
        target: 'STE100',
        format: 'plain'
      })
    });
    
    const { result } = await response.json();
    
    // 変換結果をツールチップで表示
    const tooltip = document.createElement('div');
    tooltip.style.cssText = `
      position: fixed; background: #1E293B; color: #F8FAFC;
      padding: 8px 12px; border-radius: 6px; font-size: 12px;
      z-index: 99999; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    `;
    tooltip.textContent = `STE100: ${result}`;
    document.body.appendChild(tooltip);
    
    setTimeout(() => tooltip.remove(), 4000);
  }
});
```

### 🎁 特典8: デザイン納品物に添付する「STE100準拠宣言」テンプレート

クライアントにデザインを納品する際、この宣言書を一緒に提出すると信頼度が上がります。

```markdown
# STE100準拠宣言書

プロジェクト名: [プロジェクト名]
デザイナー: [あなたの名前]
日付: [日付]

## 準拠項目
- [x] すべてのUIテキストがSTE100規格（ASD-STE100）に準拠
- [x] 文章の最大語数: 20語 / 文
- [x] 能動態のみ使用（受動態は0件）
- [x] 使用語彙数: [数字]語（STE100認定語彙のみ）
- [x] Figmaテキストレイヤー名もSTE100準拠

## 品質スコア
- Readability Score: [95/100]
- STE100適合率: [98%]
- 校正回数: [3回]

## ツール
- SimpleEnglish (GitHub) + Figma AI連携
- 最終チェック: [日付]に自動検証済み

---
※このデザインはAI Conduitのワークフローで生成・検証されています。
```

### 🎁 特典9: 毎日使える「STE100 よく使うUI用語変換表」

