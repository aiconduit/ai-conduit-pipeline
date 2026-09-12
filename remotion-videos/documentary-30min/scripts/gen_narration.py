#!/usr/bin/env python3
"""24シーン全ナレーション生成スクリプト（edge-tts）- 各シーンの尺に合わせた長さ"""
import asyncio, edge_tts, subprocess, os, json

VOICE = "ja-JP-KeitaNeural"
RATE = "+10%"

# 各シーンのターゲット秒数（SECTION_DURATIONと一致させる）
NARRATIONS = {
    "s01_hook": [  # 30秒
        "2社のAI企業が世界を変えようとしています。",
        "AnthropicとOpenAI。どちらが本当に勝つのか？",
        "時価総額の合計は1兆8千億ドル。",
        "30分で全てを徹底解説します。",
    ],
    "s02_intro": [  # 60秒
        "これがAnthropicの公式サイトです。",
        "2021年に設立されたAnthropicは、AIの安全性を最優先に掲げています。",
        "シンプルで洗練されたデザインが印象的です。",
        "安全性を前面に打ち出したブランド戦略が伝わります。",
        "エンタープライズ向けのAPIと、一般ユーザー向けのClaude.aiを展開しています。",
        "2026年現在、年間売上は650億ドルに達しています。",
    ],
    "s03_origin_openai": [  # 75秒
        "OpenAIは2015年12月に設立されました。",
        "Sam Altman、Elon Musk、Greg Brockmanら錚々たる顔ぶれが共同創業しました。",
        "当初は非営利組織として、AIを人類全体の利益のために開発することを掲げました。",
        "2019年にMicrosoftから10億ドルの投資を受け、営利組織へと転換しました。",
        "2022年11月、ChatGPTをリリース。わずか5日で100万ユーザーを獲得しました。",
        "2026年現在、ChatGPTは週間9億人のユーザーを抱える世界最大のAIサービスです。",
        "Microsoftからの総投資額は130億ドルを超えています。",
    ],
    "s04_chatgpt": [  # 60秒
        "これが週間9億人のユーザーが使うChatGPTです。",
        "シンプルで直感的なUIが爆発的な普及を支えました。",
        "リリースからわずか2ヶ月で1億ユーザーを達成。史上最速の成長記録です。",
        "Googleは社内でコードレッドを宣言し、緊急対応を迫られました。",
        "誰でも使えるアクセシビリティがOpenAIの最大の強みです。",
        "月額20ドルのChatGPT Plusは今や世界中のプロフェッショナルに使われています。",
    ],
    "s05_anthropic_birth": [  # 75秒
        "2020年末、OpenAIの内部で亀裂が生じていました。",
        "研究担当副社長のDario Amodeiは、会社の方向性に疑問を持ち始めます。",
        "AIの安全性よりも商業展開が優先されていると感じたからです。",
        "2021年1月、DarioはAnthropicを設立します。",
        "妹のDaniellaを含む8人のOpenAI研究者が一緒に退社しました。",
        "設立の理念は明確でした。AIを安全に、人類のために開発する。",
        "2026年現在、AnthropicのARRは650億ドルに達し、19ヶ月で65倍という歴史的な成長を遂げました。",
    ],
    "s06_split_reason": [  # 60秒
        "なぜDarioはOpenAIを去ったのか。その真相を掘り下げます。",
        "Darioは後のインタビューで「AIが非常に強力になりうると確信した」と語っています。",
        "だからこそ安全性に注力すべきだという考えがあったのです。",
        "一方のOpenAIは、MicrosoftとのパートナーシップによりChatGPTを急速に商業展開していきました。",
        "OpenAIは普及を優先、Anthropicは安全性を優先。",
        "この哲学の違いが、2社の戦略を根本から分けることになります。",
    ],
    "s07_safety_vs_growth": [  # 60秒
        "2社の根本的な違いは哲学にあります。",
        "Anthropicは安全性を最優先。Constitutional AIという独自手法を開発しました。",
        "AIに原則を与えて自己評価させる、革新的なアプローチです。",
        "OpenAIは普及速度を優先。より多くの人にAIを届けることを重視します。",
        "この哲学の違いが製品・価格・対象市場の全てに影響しています。",
        "どちらが正しいかは、今も業界全体で議論が続いています。",
    ],
    "s08_models_claude": [  # 60秒
        "こちらはClaudeのインターフェースです。",
        "長文の理解と精密な分析能力が際立っています。",
        "Claude Fable 5.1はコーディングのSWE-benchで72.7%を達成。業界トップです。",
        "Claude Sonnet 5はコストパフォーマンスが最も高く、企業での採用が急増しています。",
        "企業のプロフェッショナルユーザーから特に高い評価を受けています。",
        "Claude Codeは年間収益25億ドルを達成し、開発者市場で急速に普及しています。",
    ],
    "s09_models_gpt": [  # 60秒
        "こちらはOpenAIの公式サイトです。",
        "ChatGPTを前面に押し出したマーケティング戦略が見て取れます。",
        "GPT-6 Astraはマルチモーダル能力が大幅に強化されました。",
        "o3は深い推論に特化し、数学や科学の問題解決に優れています。",
        "GPT-4o miniはコストパフォーマンスが高く、大量処理に最適です。",
        "世界で最も認知されたAIブランドとしての自信が伝わります。",
    ],
    "s10_benchmark": [  # 60秒
        "2026年9月時点の最新ベンチマーク比較です。",
        "コーディング性能：SWE-benchでClaudeが72.7%、GPT-6が67%です。",
        "長文理解でもClaudeが優位で96.4%対93.1%となっています。",
        "一方、数学のMATH-500ではGPT-6が94.5%でClaudeの91.2%を上回ります。",
        "マルチモーダルと深い推論もGPT-6が優位です。",
        "用途によって使い分けるのが最も賢い選択です。",
    ],
    "s11_revenue_anthropic": [  # 75秒
        "Anthropicの年間収益は19ヶ月で1億ドルから650億ドルへ急成長しました。",
        "ソフトウェア史上最速の成長率として記録されています。",
        "2025年1月に10億ドル、2025年7月に30億ドル、2026年7月に650億ドルへと急増しました。",
        "この急成長を支えているのはエンタープライズ戦略です。",
        "収益の80%が企業顧客からです。",
        "高マージンのAPIビジネスが黒字化を実現しました。",
        "2026年、Anthropicはついに初の黒字化を達成しました。",
    ],
    "s12_revenue_openai": [  # 60秒
        "収益面ではAnthropicが大きく上回っています。",
        "ARRはAnthropicの650億ドルがOpenAIの400億ドルを大幅に超えます。",
        "しかしOpenAIは2025年に209億ドルの損失を計上しています。",
        "一方Anthropicは2026年に初の黒字化を達成しました。",
        "ユーザー数ではOpenAIの9億人がAnthropicを圧倒しています。",
        "収益効率ではAnthropicが、規模ではOpenAIが勝っています。",
    ],
    "s13_funding": [  # 60秒
        "資金調達でも2社は熾烈な競争を繰り広げています。",
        "Anthropicは2026年5月に9650億ドルの時価総額でIPO申請しました。",
        "2兆ドル以上の上場時価総額を目指し、10月のIPOを予定しています。",
        "OpenAIは8520億ドルで1220億ドルを調達しています。",
        "6月8日に極秘のS-1を申請し、2026年9月の上場を目指しています。",
        "両社合計で1兆8千億ドル近い時価総額が市場に登場することになります。",
    ],
    "s14_ipo_race": [  # 60秒
        "IPOレースが激化しています。",
        "OpenAIは9月、Anthropicは10月の上場を目指しています。",
        "これはソフトウェア史上最大規模のIPOレースです。",
        "どちらの株が高く評価されるか、投資家の注目が集まっています。",
        "Anthropicの目標時価総額2兆ドルが達成されれば、史上最大のスタートアップIPOとなります。",
        "AIセクター最大の歴史的イベントとなります。",
    ],
    "s15_enterprise": [  # 60秒
        "Anthropicの最大の強みはエンタープライズ戦略です。",
        "収益の80%が企業顧客から来ています。",
        "年間100万ドル以上支払う大企業顧客が7倍に増加しました。",
        "Goldman Sachs、Salesforce、Pfizer等の大手企業がClaudeを採用しています。",
        "高マージンのAPIビジネスがOpenAIより効率的な収益構造を生んでいます。",
        "このモデルが2026年の初黒字化を実現させました。",
    ],
    "s16_consumer": [  # 60秒
        "OpenAIの最大の強みはブランド力とユーザー数です。",
        "ChatGPTは週間9億人のユーザーを抱える世界最大のAIサービスです。",
        "一般消費者への普及率はAI業界で圧倒的No.1です。",
        "月額20ドルのChatGPT Plusは個人ユーザーに広く普及しています。",
        "ChatGPT Enterpriseは企業向けで急速に成長しています。",
        "消費者ブランドとしての認知度は競合を大幅に引き離しています。",
    ],
    "s17_partners_ms": [  # 60秒
        "OpenAIとMicrosoftの連携は業界最大の提携です。",
        "MicrosoftはAzure経由でGPTを全世界に提供しています。",
        "Office・TeamsへのCopilot統合により、数億人のビジネスユーザーに届きます。",
        "Microsoftの株式保有額は270億ドルに達しています。",
        "Azure OpenAI Serviceは企業のAI導入を加速させています。",
        "Windows 11へのCopilot統合でデスクトップユーザーにも普及が進んでいます。",
    ],
    "s18_partners_aws": [  # 60秒
        "AnthropicはAmazonと戦略的パートナーシップを締結しています。",
        "AmazonはAWS Bedrockを通じてClaudeを展開し、80億ドルを投資しています。",
        "GoogleもAnthropicに数十億ドルを投資しており、Google Cloudでも利用可能です。",
        "AWSのエンタープライズ顧客が直接Claudeにアクセスできる環境が整っています。",
        "この構図を見ると、AI覇権争いはMicrosoft陣営とAmazon・Google連合の代理戦争とも言えます。",
        "2社の提携先の違いが、企業向けAI市場の競争をさらに激化させています。",
    ],
    "s19_safety_constitutional": [  # 75秒
        "AnthropicはConstitutional AIを開発しました。",
        "AIに原則を与えて自己評価させるという革新的な手法です。",
        "有益で、無害で、正直にというHHH原則が全てのClaudeモデルの基盤です。",
        "従来のRLHF手法と比べて、より一貫した安全な出力が可能になります。",
        "この手法は業界全体に影響を与え、多くの研究者が注目しています。",
        "Anthropicはこの研究を論文として公開し、AI安全性の向上に貢献しています。",
        "Constitutional AIはAI安全性研究の重要なマイルストーンとなっています。",
    ],
    "s20_safety_rlhf": [  # 60秒
        "OpenAIもRLHF（人間のフィードバックから強化学習）で安全対策を実施しています。",
        "コンテンツモデレーションの専門チームを持ちます。",
        "GPT-4のリリース時には、数千時間の安全テストを実施しました。",
        "しかし商業展開のスピードとのバランスが常に問われています。",
        "安全性と能力のトレードオフは業界全体の課題です。",
        "OpenAIは安全と普及の両立を目指していますが、批判も受けています。",
    ],
    "s21_fbi": [  # 45秒
        "2026年2月、衝撃的な事件が起きました。",
        "FBIがDario CEOに対し、Claudeの安全制限を解除するよう要求したのです。",
        "Darioはこれを即座に拒否しました。",
        "「安全性は交渉の対象ではない」という強い意志を示したのです。",
    ],
    "s22_future_agi": [  # 75秒
        "2社が最終的に目指すものはAGI、汎用人工知能です。",
        "OpenAIのGreg BrockmanはGPT-6発表を「AGI時代へようこそ」と締めくくりました。",
        "OpenAIはStargateプロジェクトで5000億ドルのデータセンター建設を進めています。",
        "一方AnthropicのDarioは「AGIは2〜3年以内に来るかもしれない」と発言しています。",
        "しかしその開発は安全性を担保しながら進めるべきだという姿勢を崩しません。",
        "AGIの到来は人類史上最大の転換点となる可能性があります。",
        "2社のアプローチの違いが、その到来を左右するかもしれません。",
    ],
    "s23_stargate": [  # 60秒
        "OpenAIはStargateプロジェクトを立ち上げました。",
        "Microsoft・SoftBankと共同で5000億ドルを投資します。",
        "米国全土にAIコンピューティング基盤を整備する壮大な計画です。",
        "テキサス州を中心に大規模データセンターの建設が進んでいます。",
        "AnthropicもAmazonと共に独自のコンピュート投資を進めています。",
        "AIインフラへの投資競争は、AIの未来を左右する重要な戦いです。",
    ],
    "s24_conclusion": [  # 90秒
        "AnthropicとOpenAI。どちらが勝つのか。",
        "答えは「どちらも勝者になり得る」です。",
        "OpenAIは9億人ユーザーとMicrosoftとの連携が最大の強みです。",
        "AnthropicはARR650億ドル、初の黒字化、エンタープライズ首位という実績が武器です。",
        "2社は競合しながらも、AI市場全体を拡大させています。",
        "実際、多くの企業が両方のAIを本番環境で使用しています。",
        "この競争はテクノロジーの競争であると同時に、AIをどう社会に統合するかという哲学の競争でもあります。",
        "どちらの哲学が正しいかは、これからの10年が証明するでしょう。",
        "チャンネル登録とベルアイコンで最新情報をお見逃しなく。",
    ],
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
