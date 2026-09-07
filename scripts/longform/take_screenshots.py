#!/usr/bin/env python3
import json, os, subprocess, sys

video_name = sys.argv[1] if len(sys.argv) > 1 else "anthropic-vs-openai"
script = json.load(open(f"longform/{video_name}/script.json"))
os.makedirs(f"longform/{video_name}/screenshots", exist_ok=True)

sections = [{"id": s["id"], "url": s.get("url", "https://anthropic.com")} for s in script["sections"]]

js_code = f"""
const {{ chromium }} = require('playwright');
const sections = {json.dumps(sections)};
(async () => {{
  const browser = await chromium.launch();
  for (const section of sections) {{
    try {{
      const page = await browser.newPage();
      await page.setViewportSize({{ width: 1280, height: 800 }});
      await page.goto(section.url, {{ waitUntil: 'domcontentloaded', timeout: 15000 }});
      await page.waitForTimeout(2000);
      await page.screenshot({{ path: `longform/{video_name}/screenshots/${{section.id}}.jpg`, type: 'jpeg', quality: 85 }});
      await page.close();
      console.log(`OK: ${{section.id}}`);
    }} catch(e) {{
      console.log(`SKIP: ${{section.id}} - ${{e.message}}`);
    }}
  }}
  await browser.close();
}})();
"""

with open("/tmp/screenshot.js", "w") as f:
    f.write(js_code)

result = subprocess.run(["node", "/tmp/screenshot.js"], capture_output=False)
print("スクリーンショット完了")
