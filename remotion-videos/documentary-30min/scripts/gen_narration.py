#!/usr/bin/env python3
"""24シーン全ナレーション生成スクリプト（edge-tts）"""
import asyncio, edge_tts, subprocess, os, json

VOICE = "ja-JP-KeitaNeural"
RATE = "+10%"

NARRATIONS = {
    "s01_hook": ["2社のAI企業が世界を変えようとしています。","でも、どちらが本当に勝つのか？","数字が全てを語ります。30分で徹底解説。"],
    "s02_intro": ["これがAnthropicの公式サイトです。","シンプルで洗練されたデザインが印象的です。","安全性を前面に打ち出したブランド戦略が伝わります。"],
    "s03_origin_openai": ["OpenAIは2015年12月に設立されました。","Sam Altman、Elon Musk、Greg Brockmanら錚々たる顔ぶれが共同創業しました。","当初は非営利組織として、AIを人類全体の利益のために開発することを掲げました。","2022年11月、ChatGPTをリリース。わずか5日で100万ユーザーを獲得しました。"],
    "s04_chatgpt": ["これが週間9億人のユーザーが使うChatGPTです。","シンプルで直感的なUIが爆発的な普及を支えました。","誰でも使えるアクセシビリティがOpenAIの強みです。"],
    "s05_anthropic_birth": ["2020年末、OpenAIの内部で亀裂が生じていました。","Dario Amodeiは会社の方向性に疑問を持ち始めます。","2021年1月、DarioはAnthropicを設立します。","2026年現在、ARRは650億ドルに達しました。"],
    "s06_split": ["なぜDarioはOpenAIを去ったのか。","Darioは「AIが非常に強力になりうると確信した」と語っています。","OpenAIは普及を優先、Anthropicは安全性を優先。","2026年2月、DarioはFBIからの制限解除要求を拒否しました。"],
    "s07_safety_vs_growth": ["2社の根本的な違いは哲学にあります。","Anthropicは安全性を最優先。Constitutional AIという独自手法を開発しました。","OpenAIは普及速度を優先します。","この哲学の違いが製品・価格・対象市場の全てに影響しています。"],
    "s08_models_claude": ["こちらはClaudeのインターフェースです。","長文の理解と精密な分析能力が際立っています。","企業のプロフェッショナルユーザーから特に高い評価を受けています。"],
    "s09_models_gpt": ["こちらはOpenAIの公式サイトです。","ChatGPTを前面に押し出したマーケティング戦略が見て取れます。","世界で最も認知されたAIブランドとしての自信が伝わります。"],
    "s10_benchmark": ["2026年9月時点の最新ベンチマーク比較です。","コーディングと長文理解はClaudeが優位。","数学とマルチモーダルはGPT-6が優位。","用途によって使い分けるのが賢い選択です。"],
    "s11_revenue_anthropic": ["Anthropicの年間収益は19ヶ月で1億ドルから650億ドルへ急成長。","ソフトウェア史上最速の成長率です。","2026年、Anthropicは初の黒字化を達成しました。","収益構造の効率性で、Anthropicが大きく上回っています。"],
    "s12_revenue_compare": ["収益面ではAnthropicが大きく上回っています。","ARRはAnthropicの650億ドルがOpenAIを大幅に超えます。","利益面でもAnthropicが2026年に初の黒字化を達成しました。","ただしユーザー数ではOpenAIが圧倒しています。"],
    "s13_funding": ["資金調達でも2社は熾烈な競争を繰り広げています。","Anthropicは時価総額9650億ドルでIPO申請しました。","OpenAIは8520億ドルで1220億ドルを調達しています。","2社合計で約1兆8千億ドルが市場に登場します。"],
    "s14_ipo_race": ["IPOレースが激化しています。","OpenAIは9月、Anthropicは10月の上場を目指しています。","どちらの株が高く評価されるか、投資家の注目が集まっています。","AIセクター最大のIPOイベントとなります。"],
    "s15_enterprise": ["Anthropicの最大の強みはエンタープライズ戦略です。","収益の80%が企業顧客から来ています。","年間100万ドル以上支払う大企業顧客が7倍に増加しました。","このモデルが2026年の初黒字化を実現させました。"],
    "s16_consumer": ["OpenAIの最大の強みはブランド力とユーザー数です。","ChatGPTは週間9億人のユーザーを抱える世界最大のAIサービスです。","一般消費者への普及率はAI業界で圧倒的No.1です。","月額20ドルのChatGPT Plusは個人ユーザーに広く普及しています。"],
    "s17_partners_ms": ["OpenAIとMicrosoftの連携は業界最大の提携です。","MicrosoftはAzure経由でGPTを全世界に提供しています。","Office・TeamsへのCopilot統合により、数億人のビジネスユーザーに届きます。","Microsoftの株式保有額は270億ドルに達しています。"],
    "s18_partners_aws": ["AnthropicはAmazonと戦略的パートナーシップを締結しています。","AmazonはAWS経由でClaudeを展開し、80億ドルを投資しています。","GoogleもAnthropicに数十億ドルを投資しており、Google Cloudでも利用可能です。","AI覇権争いはMicrosoft陣営とAmazon・Google連合の代理戦争とも言えます。"],
    "s19_safety_constitutional": ["AnthropicはConstitutional AIを開発しました。","AIに原則を与えて自己評価させるという革新的な手法です。","有益で、無害で、正直にというHHH原則が全てのClaudeモデルの基盤です。","この手法は業界全体に影響を与えています。"],
    "s20_safety_rlhf": ["OpenAIもRLHFで安全対策を実施しています。","コンテンツモデレーションの専門チームを持ちます。","しかし商業展開のスピードとのバランスが常に問われています。","安全性と能力のトレードオフは業界全体の課題です。"],
    "s21_fbi": ["2026年2月、衝撃的な事件が起きました。","FBIがDario CEOに対し、Claudeの安全制限を解除するよう要求したのです。","Darioはこれを即座に拒否しました。","この決断はAnthropicの安全性への姿勢を世界に示す転換点となりました。"],
    "s22_future_agi": ["2社が最終的に目指すものはAGI、汎用人工知能です。","OpenAIのGreg BrockmanはGPT-6発表を「AGI時代へようこそ」と締めくくりました。","OpenAIはStargateプロジェクトで5000億ドルのデータセンター建設を進めています。","AnthropicのDarioは「AGIは2〜3年以内に来るかもしれない」と発言しています。"],
    "s23_stargate": ["OpenAIはStargateプロジェクトを立ち上げました。","Microsoft・SoftBankと共同で5000億ドルを投資します。","米国全土にAIコンピューティング基盤を整備する壮大な計画です。","AnthropicもAmazonと共に独自のコンピュート投資を進めています。"],
    "s24_conclusion": ["AnthropicとOpenAI。どちらが勝つのか。","答えは「どちらも勝者になり得る」です。","OpenAIは9億人ユーザーとMicrosoftとの連携が強みです。","AnthropicはARR650億ドル、初の黒字化、エンタープライズ首位という実績が武器です。","この競争はテクノロジーの競争であると同時に、哲学の競争でもあります。","チャンネル登録とベルアイコンで最新情報をお見逃しなく。"],
}

async def gen_audio(text, path, voice, rate):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(path)

def get_duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True
    )
    try:
        return float(result.stdout.strip())
    except:
        return 0.0

async def main():
    os.makedirs("public/audio", exist_ok=True)
    timing = {}
    
    for scene_id, chunks in NARRATIONS.items():
        print(f"Generating {scene_id} ({len(chunks)} chunks)...")
        seg_paths = []
        for i, chunk in enumerate(chunks):
            path = f"/tmp/_{scene_id}_{i:02d}.mp3"
            await gen_audio(chunk, path, VOICE, RATE)
            seg_paths.append(path)
        
        concat_txt = f"/tmp/_{scene_id}_concat.txt"
        with open(concat_txt, "w") as f:
            for p in seg_paths:
                f.write(f"file \'{p}\'\n")
        
        out_path = f"public/audio/{scene_id}.mp3"
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_txt, "-c", "copy", out_path
        ], capture_output=True)
        
        dur = get_duration(out_path)
        timing[scene_id] = {"duration": dur, "chunks": len(chunks)}
        print(f"  {scene_id}: {dur:.1f}s")
    
    with open("public/audio/timing.json", "w") as f:
        json.dump(timing, f, indent=2, ensure_ascii=False)
    
    total = sum(v["duration"] for v in timing.values())
    print(f"\n✅ 全24シーンのナレーション生成完了")
    print(f"総ナレーション時間: {total:.0f}秒 ({total/60:.1f}分)")

asyncio.run(main())
