#!/usr/bin/env python3
import asyncio, edge_tts, subprocess, os, json

VOICE = "ja-JP-KeitaNeural"
RATE = "+10%"

NARRATIONS = {
    "s01_intro": [
        "2026年、AIの世界を制する2つの巨人が存在します。",
        "OpenAI、そしてAnthropicです。",
        "AnthropicのARRは650億ドル、OpenAIは400億ドル。",
        "時価総額はAnthropicが9650億ドルでOpenAIの8520億ドルを上回っています。",
        "わずか数年前には存在しなかった企業が、今や世界最大のテクノロジー企業と肩を並べています。",
        "この動画では、2社の戦略・思想・財務・技術を徹底比較します。",
    ],
    "s02_origin_openai": [
        "OpenAIは2015年12月に設立されました。",
        "Sam Altman、Elon Musk、Greg Brockmanら錚々たる顔ぶれが共同創業しました。",
        "当初は非営利組織として、AIを人類全体の利益のために開発することを掲げました。",
        "2019年にMicrosoftから10億ドルの投資を受け、営利組織へと転換しました。",
        "そして2022年11月、ChatGPTをリリース。わずか5日で100万ユーザーを獲得しました。",
        "2026年現在、ChatGPTは週間9億人のユーザーを抱える世界最大のAIサービスです。",
    ],
    "s03_origin_anthropic": [
        "2020年末、OpenAIの内部で亀裂が生じていました。",
        "研究担当副社長のDario Amodeiは、会社の方向性に疑問を持ち始めます。",
        "2021年1月、Darioは妹のDaniellaを含む8人のOpenAI研究者と共に退社し、Anthropicを設立します。",
        "設立の理念は明確でした。AIを安全に、人類のために開発する。",
        "2026年現在、AnthropicのARRは650億ドルに達し、19ヶ月で65倍という歴史的な成長を遂げました。",
        "企業顧客が収益の80%を占める強固なビジネスモデルを確立しています。",
    ],
    "s04_split": [
        "なぜDarioはOpenAIを去ったのか。その真相を掘り下げます。",
        "Darioは後のインタビューで「AIが非常に強力になりうると確信した」と語っています。",
        "だからこそ安全性に注力すべきだという考えがあったのです。",
        "一方のOpenAIは、MicrosoftとのパートナーシップによりChatGPTを急速に商業展開していきました。",
        "OpenAIは普及を優先、Anthropicは安全性を優先。この哲学の違いが、2社の戦略を根本から分けることになります。",
        "2026年2月、DarioはFBIからClaudeの安全制限を解除するよう要求されましたが、これを拒否しました。",
    ],
    "s05_models": [
        "2026年9月現在、2社の最新フラッグシップモデルを比較します。",
        "コーディング性能：SWE-benchでClaudeが72.7%、GPT-6が67%です。",
        "長文理解でもClaudeが優位です。",
        "一方、マルチモーダルとミニモデルのコスパではGPT-6が上回っています。",
        "Claude Codeは年間収益25億ドルを達成し、開発者市場で急速に普及しています。",
        "多くの企業が両方を本番環境で使用しているのが現実です。",
    ],
    "s06_revenue": [
        "Anthropicの年間収益は19ヶ月で1億ドルから650億ドルへ急成長。",
        "ソフトウェア史上最速の成長率です。",
        "OpenAIも400億ドルと急成長していますが、Anthropicが首位です。",
        "OpenAIは2025年に209億ドルの損失を計上しています。",
        "Anthropicは2026年、初の黒字化を達成しました。",
        "収益構造の効率性でも、Anthropicが大きく上回っています。",
    ],
    "s07_funding": [
        "資金調達でも2社は熾烈な競争を繰り広げています。",
        "Anthropicは2026年5月に9650億ドルの時価総額でIPO申請。2兆ドル以上の上場時価総額を目指し、10月のIPOを予定しています。",
        "OpenAIは3月に8520億ドルで1220億ドルを調達。6月8日に極秘のS-1を申請し、2026年9月の上場を目指しています。",
        "両社合計で1兆8千億ドル近い時価総額が市場に登場することになります。",
        "これはソフトウェア史上最大規模のIPOレースです。",
    ],
    "s08_business": [
        "2社のビジネスモデルは根本的に異なります。",
        "OpenAIはコンシューマー重視。ChatGPTの9億人ユーザーが象徴するように、一般消費者への普及を最優先します。",
        "一方Anthropicはエンタープライズ重視。収益の80%が企業顧客からです。",
        "年間100万ドル以上支払う企業顧客が7倍に増加しました。",
        "この違いは利益率に直結します。エンタープライズAPIはコンシューマー向けより高マージンです。",
        "Anthropicが初の黒字化を達成できた背景にはこのビジネスモデルの優位性があります。",
    ],
    "s09_safety": [
        "2社を最も分けるのは、AI安全性への哲学です。",
        "AnthropicはConstitutional AIを開発。AIに原則を与えて自己評価させる手法です。",
        "有益で、無害で、正直にというHHH原則が全モデルの基盤となっています。",
        "OpenAIもRLHFによる安全対策を実施していますが、商業展開とのバランスが常に問われます。",
        "2026年2月、DarioはFBIからClaudeの安全制限を解除するよう要求されましたが、これを拒否しました。",
        "AIが社会に組み込まれるにつれ、この哲学の違いはより重要になっていきます。",
    ],
    "s10_partners": [
        "両社のパートナー戦略も対照的です。",
        "OpenAIはMicrosoftと深く結びついています。Microsoftは270億ドルの株式を保有し、Azure経由でGPTを全世界に提供します。",
        "AnthropicはAmazonと戦略的パートナーシップを締結。Amazonは80億ドルを投資しています。",
        "またGoogleも数十億ドルを投資しており、Google Cloudでも利用可能です。",
        "この構図を見ると、AI覇権争いはMicrosoft陣営とAmazon・Google連合の代理戦争とも言えます。",
    ],
    "s11_future": [
        "2社が最終的に目指すものは何か。AGI、つまり汎用人工知能です。",
        "OpenAIのGreg Brockmanは、GPT-6のリリース発表を「AGI時代へようこそ」という言葉で締めくくりました。",
        "OpenAIはStargateプロジェクトで5000億ドルのデータセンター建設を進めています。",
        "一方AnthropicのDarioは「AGIは2〜3年以内に来るかもしれない」と発言しています。",
        "しかしその開発は安全性を担保しながら進めるべきだという姿勢を崩しません。",
        "IPOレースも激化しており、Anthropicは10月、OpenAIは9月の上場を目指しています。",
    ],
    "s12_conclusion": [
        "AnthropicとOpenAI。どちらが勝つのか。",
        "答えは「どちらも勝者になり得る」です。",
        "OpenAIは9億人ユーザーとMicrosoftとの連携が強みです。",
        "AnthropicはARR650億ドル、初の黒字化、エンタープライズ首位という実績が武器です。",
        "この競争はテクノロジーの競争であると同時に、AIをどう社会に統合するかという哲学の競争でもあります。",
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
    return float(result.stdout.strip())

async def main():
    os.makedirs("public/audio", exist_ok=True)
    timing = {}
    for scene_id, chunks in NARRATIONS.items():
        print(f"Generating {scene_id}...")
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
        json.dump(timing, f, indent=2)
    print("\n✅ 全ナレーション生成完了")

asyncio.run(main())
