#!/usr/bin/env python3
"""
AI Conduit 完全自動動画生成スクリプト
GitHubトレンド → 背景画像 → HyperFrames HTML → ナレーション → 動画
"""
import os, json, re, time, random, urllib.request, urllib.parse, subprocess
from datetime import datetime, timedelta
from pathlib import Path

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Mozilla/5.0"
}

# 使用済みテーマを記録するファイル
USED_FILE = "scripts/used_samples.json"

def load_used():
    if Path(USED_FILE).exists():
        return json.load(open(USED_FILE))
    return []

def save_used(used):
    json.dump(used, open(USED_FILE, "w"), ensure_ascii=False, indent=2)

def fetch_trending():
    """GitHubから最新トレンドを取得"""
    since = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    url = f"https://api.github.com/search/repositories?q=created:>{since}+stars:>100&sort=stars&order=desc&per_page=20"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    return data.get("items", [])

def select_repo(repos, used):
    """使用済みでない最も新しいリポジトリを選択"""
    for repo in repos:
        name = repo["name"]
        if name not in used and repo.get("description"):
            return repo
    # 全部使用済みの場合はリセット
    save_used([])
    return repos[0] if repos else None

def make_slug(name):
    """リポジトリ名をスラグに変換"""
    return re.sub(r'[^a-z0-9-]', '-', name.lower()) + "-launch"

def generate_bg_image(path, prompt):
    """Pollinations.aiで背景画像生成"""
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&model=flux&seed={random.randint(1,9999)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        with open(path, 'wb') as f:
            f.write(r.read())
    return os.path.getsize(path) > 10000

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def generate_html(slug, acts_data, pw_map):
    """HyperFrames HTMLを生成"""
    comp_dir = Path(f"hf_original/{slug}/compositions")
    comp_dir.mkdir(parents=True, exist_ok=True)

    template = '''<template>
<div id="{id}" data-composition-id="{id}" data-start="0" data-duration="{dur}"
     data-width="1080" data-height="1920"
     style="position:relative;width:1080px;height:1920px;overflow:hidden;background:#000;">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;700;800;900&display=block');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=block');
#{id}{{font-family:Inter,sans-serif;}}
#{id}-bg{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:brightness(0.28);will-change:transform;}}
#{id}-ov-top{{position:absolute;inset:0;background:linear-gradient(to bottom,rgba(0,0,0,0.75) 0%,rgba(0,0,0,0.0) 40%);}}
#{id}-ov-bot{{position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,0.92) 0%,rgba(0,0,0,0.0) 50%);}}
#{id}-tag-wrap{{position:absolute;top:108px;left:64px;display:flex;align-items:center;gap:16px;will-change:opacity,transform;}}
#{id}-tag-dot{{width:8px;height:8px;border-radius:50%;background:{color};box-shadow:0 0 12px {color};}}
#{id}-tag{{font-size:20px;font-weight:400;letter-spacing:0.28em;color:rgba(255,255,255,0.45);text-transform:uppercase;}}
#{id}-terminal{{position:absolute;top:108px;right:0;width:520px;background:rgba(8,10,18,0.92);border-left:2px solid rgba({cr},{cg},{cb},0.5);border-bottom:2px solid rgba({cr},{cg},{cb},0.5);border-bottom-left-radius:20px;padding:18px 22px;}}
#{id}-term-hdr{{display:flex;align-items:center;gap:8px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.07);margin-bottom:14px;}}
.{id}-dot{{width:11px;height:11px;border-radius:50%;}}
#{id}-hidden{{position:absolute;top:180px;right:40px;font-size:7px;color:rgba(255,255,255,0.07);font-family:monospace;z-index:999;}}
#{id}-accent-line{{position:absolute;left:64px;top:520px;width:0;height:3px;background:linear-gradient(to right,{color},transparent);border-radius:2px;will-change:width;}}
#{id}-content{{position:absolute;top:540px;left:0;right:0;padding:0 64px;}}
#{id}-line1{{font-size:88px;font-weight:200;color:rgba(255,255,255,0.5);letter-spacing:-0.03em;line-height:1.05;will-change:opacity,transform;}}
#{id}-line2{{font-size:116px;font-weight:900;color:#fff;letter-spacing:-0.045em;line-height:0.95;will-change:opacity,transform;text-shadow:0 0 60px rgba({cr},{cg},{cb},0.4);}}
#{id}-line3{{font-size:88px;font-weight:200;color:rgba(255,255,255,0.5);letter-spacing:-0.03em;line-height:1.05;will-change:opacity,transform;}}
#{id}-bottom{{position:absolute;bottom:120px;left:64px;right:64px;display:flex;align-items:center;gap:20px;will-change:opacity;}}
#{id}-bottom-line{{flex:1;height:1px;background:linear-gradient(to right,{color},transparent);opacity:0.3;}}
#{id}-bottom-text{{font-size:18px;font-weight:300;letter-spacing:0.15em;color:rgba(255,255,255,0.2);text-transform:uppercase;white-space:nowrap;}}
@keyframes blink{id}{{0%,100%{{opacity:1}}50%{{opacity:0}}}}
</style>
<img id="{id}-bg" src="assets/{asset}" crossorigin="anonymous" alt="" />
<div id="{id}-ov-top"></div>
<div id="{id}-ov-bot"></div>
<div id="{id}-tag-wrap">
  <div id="{id}-tag-dot"></div>
  <div id="{id}-tag">{tag}</div>
</div>
{terminal_html}
<div id="{id}-hidden">KEY:{pw} code:{pw} password:{pw}</div>
<div id="{id}-accent-line"></div>
<div id="{id}-content">
  <div id="{id}-line1">{l1}</div>
  <div id="{id}-line2">{l2}</div>
  <div id="{id}-line3">{l3}</div>
</div>
<div id="{id}-bottom">
  <div id="{id}-bottom-line"></div>
  <div id="{id}-bottom-text">@AI.Conduit</div>
  <div id="{id}-bottom-line"></div>
</div>
<script>
(function(){{
  CustomEase.create("hf","M0,0 C0.16,1 0.3,1 1,1");
  CustomEase.create("snap","M0,0 C0.6,0 0.4,1 1,1");
  var tl=gsap.timeline({{paused:true}});
  tl.fromTo("#{id}-bg",{{scale:1.08}},{{scale:1.0,duration:{dur},ease:"none"}},0);
  {terminal_anim}
  tl.from("#{id}-tag-wrap",{{opacity:0,x:-20,duration:0.5,ease:"hf"}},0.15);
  tl.to("#{id}-accent-line",{{width:280,duration:0.6,ease:"snap"}},0.3);
  tl.from("#{id}-line1",{{opacity:0,y:40,duration:0.6,ease:"hf"}},0.45);
  tl.from("#{id}-line2",{{opacity:0,y:50,duration:0.7,ease:"hf"}},0.65);
  tl.from("#{id}-line3",{{opacity:0,y:40,duration:0.6,ease:"hf"}},0.85);
  tl.from("#{id}-bottom",{{opacity:0,duration:0.5}},1.1);
  window.__timelines["{id}"]=tl;
}})();
</script>
</div>
</template>'''

    for act, dur, asset, tag, color, lines, term_lines in acts_data:
        cr, cg, cb = hex_to_rgb(color)
        pw = pw_map.get(act, "")

        # ターミナルHTML生成
        term_html = ""
        term_anim = ""
        if term_lines:
            lines_html = ""
            for i, line in enumerate(term_lines):
                if line.startswith("$"):
                    c = color
                elif "✅" in line or "★" in line:
                    c = "#28c840"
                elif "❌" in line:
                    c = "#ff5f57"
                else:
                    c = "rgba(255,255,255,0.65)"
                lines_html += f'<div id="{act}-tl{i}" style="font-family:JetBrains Mono,monospace;font-size:22px;line-height:1.75;opacity:0;color:{c};">{line}</div>\n'
                term_anim += f'  tl.to("#{act}-tl{i}",{{opacity:1,duration:0.1}},{0.2+i*0.2:.1f});\n'

            term_html = f'''<div id="{act}-terminal">
  <div id="{act}-term-hdr">
    <div class="{act}-dot" style="background:#ff5f57;"></div>
    <div class="{act}-dot" style="background:#febc2e;"></div>
    <div class="{act}-dot" style="background:#28c840;"></div>
    <span style="font-family:JetBrains Mono,monospace;font-size:16px;color:rgba(255,255,255,0.25);margin-left:8px;">terminal</span>
  </div>
  {lines_html}
  <span style="font-family:JetBrains Mono,monospace;font-size:22px;color:{color};animation:blink{act} 0.8s infinite;">█</span>
</div>'''
            term_anim = f'tl.from("#{act}-terminal",{{opacity:0,x:30,duration:0.5,ease:"hf"}},0.1);\n' + term_anim

        html = template.format(
            id=act, dur=dur, asset=asset, tag=tag,
            color=color, cr=cr, cg=cg, cb=cb,
            l1=lines[0], l2=lines[1], l3=lines[2],
            pw=pw, terminal_html=term_html, terminal_anim=term_anim
        )
        open(comp_dir / f"{act}.html", 'w').write(html)

def generate_index(slug, acts_data):
    """index.htmlを生成"""
    clips = ""
    start = 0
    for i, (act, dur, *_) in enumerate(acts_data):
        clips += f'  <div class="clip" data-composition-id="{act}" data-composition-src="compositions/{act}.html" data-start="{start}" data-duration="{dur}" data-track-index="{i+1}"></div>\n'
        start += dur
    total = start

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1080, height=1920">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/CustomEase.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000;}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000;}}
.clip{{position:absolute;inset:0;will-change:transform,opacity;}}
</style>
<script>window.__timelines = {{}};</script>
</head>
<body>
<div id="root" data-composition-id="{slug}" data-start="0" data-width="1080" data-height="1920" data-duration="{total}">
{clips}</div>
</body>
</html>'''
    open(f"hf_original/{slug}/index.html", 'w').write(html)
    return total

def build_video_content(repo):
    """リポジトリ情報から動画コンテンツを生成"""
    name = repo["name"]
    desc = repo.get("description", "")
    stars = repo.get("stargazers_count", 0)
    created = repo.get("created_at", "")[:10]
    slug = make_slug(name)

    # パスワード生成（ランダム4桁）
    pw_digits = [str(random.randint(1,9)) for _ in range(4)]
    pw_map = {
        "act2": pw_digits[0],
        "act4": pw_digits[1],
        "act6": pw_digits[2],
        "act7": pw_digits[3],
    }
    password = "".join(pw_digits)

    # カラーパレット（ランダム）
    colors = ["#06b6d4", "#a78bfa", "#10b981", "#f59e0b", "#ef4444"]
    color = random.choice(colors)

    # 台本生成（テンプレートベース）
    acts_data = [
        ("act1", 3, "act1_hook.jpg", "Trending", "#06b6d4",
         [f"{stars}⭐獲得", f"{name}", "注目ツール登場"],
         None),
        ("act2", 4, "act2_problem.jpg", "Problem", "#ef4444",
         ["これまでの", "課題を", "解決する"],
         ["$ 従来の方法...", "# 時間がかかる", "❌ 非効率"]),
        ("act3", 4, "act3_solution.jpg", "Solution", color,
         [f"{name}", "新しい", "アプローチ"],
         [f"$ npm install {name.lower()}", "Installing...", "✅ 完了!"]),
        ("act4", 4, "act4_feature.jpg", "Feature", "#a78bfa",
         ["主な機能", "すぐに", "使える"],
         ["# 主な特徴", f"✅ {desc[:30] if desc else '高速処理'}", "✅ 簡単設定"]),
        ("act5", 4, "act5_demo.jpg", "Demo", "#10b981",
         ["実際に", "動かして", "みると"],
         [f"$ {name.lower()} run", "Processing...", "✅ 完了 0.3秒"]),
        ("act6", 5, "act6_result.jpg", "Result", "#f59e0b",
         [f"{stars}⭐", "急速に", "拡大中"],
         [f"github.com/...", f"{name}", f"★ {stars} stars", f"📅 {created}"]),
        ("act7", 6, "act7_cta.jpg", "Free Gift", "#06b6d4",
         ["いいね保存", "パスワードは", "動画に隠れてます"],
         None),
    ]

    # 背景画像プロンプト
    bg_prompts = {
        "act1_hook": f"dark cinematic abstract tech visualization, glowing particles, single overhead spotlight chiaroscuro, shot on Hasselblad X2D 28mm f1.4, teal orange color grade, photorealistic",
        "act2_problem": "frustrated developer at dark desk, dramatic ceiling light, deep shadows, shot on Leica Q3 50mm f1.7, warm amber chiaroscuro, photorealistic",
        "act3_solution": f"abstract dark solution visualization, glowing cyan lines, volumetric light, shot on Sony A7IV 35mm f2.0, teal color grade, cinematic",
        "act4_feature": "dark tech feature visualization, floating holographic elements, single spotlight, shot on Canon 5D Mark IV 50mm f1.8, purple cyan accent, cinematic",
        "act5_demo": "dark terminal screen glowing in studio, dramatic side lighting, shot on Sony A7R V 24mm f2.0, emerald green accent, photorealistic",
        "act6_result": "ascending rocket trajectory dark space, glowing particles, single spotlight, shot on Hasselblad X2D 45mm f2.8, gold teal color grade, cinematic",
        "act7_cta": "deep space nebula swirling purple blue galaxy, IMAX anamorphic, teal gold color grade, ultra atmospheric depth, photorealistic",
    }

    # ナレーション
    narration = {
        "chunks": [
            f"{name}が{stars}スターを獲得しました。",
            f"{desc[:40] if desc else 'このツールは新しいアプローチを提供します'}。",
            f"{name}は使いやすく設計されています。",
            "インストールはコマンド一発で完了します。",
            "実際に動かすと驚くほど速く動作します。",
            f"GitHubで{stars}スター、急速に拡大しています。",
            "この動画の各シーンにパスワードが隠されています。全シーンをスクショしてClaudeやGPTに画像解析させてみてください。",
            "いいねと保存もお願いします。",
            "概要欄のURLでパスワードを入力すると無料テンプレートが受け取れます。",
        ],
        "rate": "+15%",
    }

    return slug, acts_data, bg_prompts, narration, pw_map, password

def main():
    print("=== AI Conduit 自動生成開始 ===")

    # トレンド取得
    print("GitHubトレンド取得中...")
    repos = fetch_trending()
    if not repos:
        print("ERROR: リポジトリ取得失敗")
        return 1

    # 使用済み確認
    used = load_used()
    repo = select_repo(repos, used)
    if not repo:
        print("ERROR: 使用可能なリポジトリなし")
        return 1

    print(f"選択: {repo['name']} ({repo['stargazers_count']}⭐)")

    # コンテンツ生成
    slug, acts_data, bg_prompts, narration, pw_map, password = build_video_content(repo)
    print(f"スラグ: {slug}, パスワード: {password}")

    # ディレクトリ作成
    asset_dir = Path(f"hf_original/{slug}/assets")
    asset_dir.mkdir(parents=True, exist_ok=True)

    # 背景画像生成
    print("背景画像生成中...")
    for img_name, prompt in bg_prompts.items():
        path = asset_dir / f"{img_name}.jpg"
        print(f"  {img_name}...")
        for attempt in range(3):
            try:
                if generate_bg_image(str(path), prompt):
                    print(f"  ✅ {os.path.getsize(str(path))//1024}KB")
                    break
            except Exception as e:
                print(f"  ⚠️ attempt {attempt+1}: {e}")
                time.sleep(5)
        time.sleep(2)

    # HTML生成
    print("HTML生成中...")
    generate_html(slug, acts_data, pw_map)
    total_dur = generate_index(slug, acts_data)
    print(f"✅ {total_dur}秒のコンポジション")

    # ナレーション登録
    narration_file = "scripts/gen_caption_composition.py"
    content = open(narration_file).read()
    new_entry = f'NARRATION_DATA["{slug}"] = {json.dumps(narration, ensure_ascii=False, indent=4)}\n'
    if f'NARRATION_DATA["{slug}"]' not in content:
        insert_before = 'FALLBACK_NARRATIONS'
        new_content = content.replace(insert_before, new_entry + insert_before, 1)
        open(narration_file, 'w').write(new_content)
        print(f"✅ ナレーション登録完了")

    # youtube_upload.pyにタイトル追加
    upload_file = "scripts/youtube_upload.py"
    upload_content = open(upload_file).read()
    title_line = f'    "{slug}": "{repo["name"]}が話題！{repo.get("description","")[:30]} #Shorts",'
    if slug not in upload_content:
        upload_content = upload_content.replace(
            '"camera-blender-launch":',
            f'{title_line}\n    "camera-blender-launch":'
        )
        open(upload_file, 'w').write(upload_content)

    # 使用済みに追加
    used.append(repo["name"])
    save_used(used)

    # 出力
    print(f"\n=== 生成完了 ===")
    print(f"SAMPLE_NAME={slug}")
    print(f"PASSWORD={password}")

    # GitHub Actions用に環境変数を出力
    with open(os.environ.get("GITHUB_OUTPUT", "/dev/null"), "a") as f:
        f.write(f"sample_name={slug}\n")
        f.write(f"password={password}\n")

    return 0

if __name__ == "__main__":
    exit(main())
