#!/usr/bin/env python3
import json, os, sys

video_name = sys.argv[1] if len(sys.argv) > 1 else "anthropic-vs-openai"
script = json.load(open(f"longform/{video_name}/script.json"))

comp_dir = f"longform/{video_name}/compositions"
os.makedirs(comp_dir, exist_ok=True)

for section in script["sections"]:
    sid = section["id"]
    title = section["title"]
    color = section["color"]
    dur = section["duration_sec"]
    cr = int(color[1:3], 16)
    cg = int(color[3:5], 16)
    cb = int(color[5:7], 16)
    url = section.get("url", "https://anthropic.com")
    ss_exists = os.path.exists(f"longform/{video_name}/screenshots/{sid}.jpg")
    
    ss_html = (f'<img id="{sid}-ss-img" src="../screenshots/{sid}.jpg" crossorigin="anonymous" alt="" />'
               if ss_exists else
               '<div style="width:100%;height:420px;background:rgba(255,255,255,0.03);display:flex;align-items:center;justify-content:center;color:rgba(255,255,255,0.2);font-size:14px;font-family:Inter,sans-serif;">Loading...</div>')
    
    html = f'''<template>
<div id="{sid}" data-composition-id="{sid}" data-start="0" data-duration="{dur}"
     data-width="1920" data-height="1080"
     style="position:relative;width:1920px;height:1080px;overflow:hidden;background:#050510;">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;700;800;900&display=block');
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@200;400;700;900&display=block');
#{sid}{{font-family:"Noto Sans JP",Inter,sans-serif;}}
#{sid}-bg{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:brightness(0.22);}}
#{sid}-ov-l{{position:absolute;inset:0;background:linear-gradient(to right,rgba(5,5,16,0.98) 0%,rgba(5,5,16,0.6) 55%,rgba(5,5,16,0.0) 100%);}}
#{sid}-ov-b{{position:absolute;inset:0;background:linear-gradient(to top,rgba(5,5,16,0.8) 0%,rgba(5,5,16,0.0) 40%);}}
#{sid}-accent{{position:absolute;left:0;top:0;bottom:0;width:5px;background:linear-gradient(to bottom,transparent,{color},{color},transparent);}}
#{sid}-tag{{position:absolute;top:52px;left:72px;font-size:12px;letter-spacing:0.4em;color:rgba(255,255,255,0.25);text-transform:uppercase;font-family:Inter,sans-serif;}}
#{sid}-left{{position:absolute;left:72px;top:50%;transform:translateY(-50%);max-width:840px;}}
#{sid}-l1{{font-size:68px;font-weight:900;color:#fff;letter-spacing:-2px;line-height:1.1;will-change:opacity,transform;text-shadow:0 0 60px rgba({cr},{cg},{cb},0.5);}}
#{sid}-divider{{width:0;height:2px;background:linear-gradient(to right,{color},transparent);border-radius:1px;margin:20px 0;will-change:width;}}
#{sid}-prog{{position:absolute;bottom:0;left:0;right:0;height:3px;background:rgba(255,255,255,0.04);}}
#{sid}-prog-bar{{height:100%;background:{color};width:0;}}
#{sid}-ss-wrap{{position:absolute;right:40px;top:50%;transform:translateY(-50%);width:680px;}}
#{sid}-ss-frame{{border-radius:12px;overflow:hidden;box-shadow:0 20px 80px rgba(0,0,0,0.6);border:1px solid rgba({cr},{cg},{cb},0.2);}}
#{sid}-ss-bar{{height:36px;background:rgba(8,10,18,0.9);display:flex;align-items:center;padding:0 16px;gap:8px;border-bottom:1px solid rgba(255,255,255,0.06);}}
#{sid}-ss-url{{font-family:Inter,monospace;font-size:11px;color:rgba(255,255,255,0.3);overflow:hidden;white-space:nowrap;text-overflow:ellipsis;}}
#{sid}-ss-img{{width:100%;height:420px;object-fit:cover;object-position:top;}}
</style>
<img id="{sid}-bg" src="../assets/{sid}.jpg" crossorigin="anonymous" alt="" />
<div id="{sid}-ov-l"></div>
<div id="{sid}-ov-b"></div>
<div id="{sid}-accent"></div>
<div id="{sid}-tag">@AI.Conduit</div>
<div id="{sid}-left">
  <div id="{sid}-l1">{title}</div>
  <div id="{sid}-divider"></div>
</div>
<div id="{sid}-ss-wrap">
  <div id="{sid}-ss-frame">
    <div id="{sid}-ss-bar">
      <div style="display:flex;gap:6px;flex-shrink:0;">
        <div style="width:11px;height:11px;border-radius:50%;background:#ff5f57;"></div>
        <div style="width:11px;height:11px;border-radius:50%;background:#febc2e;"></div>
        <div style="width:11px;height:11px;border-radius:50%;background:#28c840;"></div>
      </div>
      <div id="{sid}-ss-url">{url}</div>
    </div>
    {ss_html}
  </div>
</div>
<div id="{sid}-prog"><div id="{sid}-prog-bar"></div></div>
<script>
(function(){{
  CustomEase.create("hf","M0,0 C0.16,1 0.3,1 1,1");
  CustomEase.create("snap","M0,0 C0.6,0 0.4,1 1,1");
  var tl=gsap.timeline({{paused:true}});
  tl.to("#{sid}-prog-bar",{{width:"100%",duration:{dur},ease:"none"}},0);
  tl.from("#{sid}-tag",{{opacity:0,duration:0.4,ease:"hf"}},0.1);
  tl.from("#{sid}-l1",{{opacity:0,x:-30,duration:0.6,ease:"hf"}},0.2);
  tl.to("#{sid}-divider",{{width:400,duration:0.5,ease:"snap"}},0.4);
  tl.from("#{sid}-ss-wrap",{{opacity:0,x:40,duration:0.7,ease:"hf"}},0.3);
  window.__timelines["{sid}"]=tl;
}})();
</script>
</div>
</template>'''
    
    open(f"{comp_dir}/{sid}.html", "w").write(html)
    print(f"OK: {sid}.html")

# index.html
clips = ""
start = 0
total = 0
for s in script["sections"]:
    sid = s["id"]
    dur = s["duration_sec"]
    idx = script["sections"].index(s) + 1
    clips += f'  <div class="clip" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{start}" data-duration="{dur}" data-track-index="{idx}"></div>\n'
    start += dur
    total += dur

open(f"longform/{video_name}/index.html", "w").write(f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/CustomEase.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1920px;height:1080px;overflow:hidden;background:#050510;}}
#root{{position:relative;width:1920px;height:1080px;}}
.clip{{position:absolute;inset:0;}}
</style>
<script>window.__timelines={{}};</script>
</head>
<body>
<div id="root" data-composition-id="{video_name}" data-start="0" data-width="1920" data-height="1080" data-duration="{total}">
{clips}</div>
</body>
</html>''')
print(f"index.html完成 ({total}秒)")
