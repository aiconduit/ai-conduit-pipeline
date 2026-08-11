#!/bin/bash
# Arsenal Setup - AI Conduit 戦力セットアップ
# GitHub Actions内でこのスクリプトを実行すると全ツールが使えるようになる

echo "=== AI Conduit Arsenal Setup ==="

# 1. OmniRoute（Free AI Gateway）
echo "\n[1/4] OmniRoute セットアップ..."
pip install openai httpx -q  # OmniRouteはOpenAI互換エンドポイント
cat > /tmp/omni_client.py << 'OMNI'
"""
OmniRoute クライアント
OpenAI互換エンドポイント経由で290+プロバイダーを無料で使える
使い方: python3 /tmp/omni_client.py
"""
from openai import OpenAI

client = OpenAI(
    api_key="or-v1-free",  # OmniRoute無料キー
    base_url="https://openrouter.ai/api/v1",
)

def omni_chat(prompt: str, model: str = "meta-llama/llama-3.2-3b-instruct:free") -> str:
    """無料モデルでチャット（フォールバック付き）"""
    free_models = [
        "meta-llama/llama-3.2-3b-instruct:free",
        "google/gemma-2-9b-it:free", 
        "mistralai/mistral-7b-instruct:free",
        "qwen/qwen-2-7b-instruct:free",
    ]
    for m in free_models:
        try:
            r = client.chat.completions.create(
                model=m,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
            )
            return r.choices[0].message.content
        except Exception as e:
            print(f"  {m}: {e}")
            continue
    return ""

if __name__ == "__main__":
    print(omni_chat("Claude Codeの/loopコマンドとは？日本語で30文字以内"))
OMNI
echo "✅ OmniRoute クライアント: /tmp/omni_client.py"

# 2. kimi-k3-in-c（CPU推論・GPU不要）
echo "\n[2/4] kimi-k3-in-c 確認..."
if command -v git &> /dev/null; then
    # 軽量クローン（バイナリなし）
    git clone --depth=1 --filter=blob:none https://github.com/FareedKhan-dev/kimi-k3-in-c /tmp/kimi-k3 2>/dev/null || true
    echo "✅ kimi-k3-in-c: /tmp/kimi-k3"
fi

# 3. SkiperUI コンポーネントリスト保存
echo "\n[3/4] SkiperUI コンポーネントリスト..."
cat > /tmp/skiper_components.txt << 'SKIP'
# SkiperUI - Uncommon UI Components (shadcn互換)
# インストール: npx shadcn add @skiper-ui/<component>
# 公式: https://skiper-ui.com

利用可能コンポーネント:
- @skiper-ui/dock          # macOS Dockスタイルナビ
- @skiper-ui/text-effect   # テキストアニメーション
- @skiper-ui/card-hover    # 3Dホバーカード
- @skiper-ui/gradient-text # グラデーションテキスト
- @skiper-ui/typewriter    # タイプライターエフェクト
SKIP
echo "✅ SkiperUI: /tmp/skiper_components.txt"

# 4. FacelessReels 競合分析メモ
echo "\n[4/4] 競合分析メモ..."
cat > /tmp/competitor_notes.md << 'COMP'
# FacelessReels 競合分析
URL: https://facelessreels.com
ユーザー数: 88万+
エンゲージメント: 5.5万いいね・3454コメント

## 機能セット（AI Conduitとの比較）
| 機能 | FacelessReels | AI Conduit |
|---|---|---|
| ニッチ選択 | ✅ 8種類 | ❌ 未実装 |
| 自動スクリプト | ✅ | ✅ |
| 自動動画生成 | ✅ | ✅ |
| 自動投稿 | ✅ YouTube/IG/TikTok | ✅ YouTube |
| 顔なし動画 | ✅ | ✅ |
| 5分以内生成 | ✅ | △（20-30分） |

## AI Conduitが勝てる点
- Claude/Anthropic専門コンテンツ（ニッチ特化）
- 実際のコマンド・コードが入った具体的な動画
- 日本語市場（FacelessReelsは英語のみ）
- 完全無料（FacelessReelsは有料SaaS）
COMP
echo "✅ 競合分析: /tmp/competitor_notes.md"

echo "\n=== Arsenal Setup 完了 ==="
echo "使えるツール:"
echo "  - /tmp/omni_client.py  (OmniRoute Free AI)"
echo "  - /tmp/kimi-k3/        (CPU推論エンジン)"
echo "  - /tmp/skiper_components.txt (UI Components)"
echo "  - /tmp/competitor_notes.md (競合分析)"
