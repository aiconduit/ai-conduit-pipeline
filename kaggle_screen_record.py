import os, json, requests, zipfile, tempfile, time

user = os.environ["KAGGLE_USERNAME"]
key = os.environ["KAGGLE_KEY"]
auth = (user, key)
target_url = os.environ.get("TARGET_URL", "https://open-design.ai/html-anything/")

print(f"User: {user}")
r = requests.get("https://www.kaggle.com/api/v1/datasets/list",
                params={"search": "test", "pageSize": 1}, auth=auth, timeout=10)
print(f"Auth: {r.status_code}")

kernel_slug = f"screen-rec-{int(time.time()) % 100000}"
print(f"Kernel slug: {user}/{kernel_slug}")

# GITHUB_ENVに書き込む
github_env = os.environ.get("GITHUB_ENV", "")
if github_env:
    with open(github_env, "a") as f:
        f.write(f"KAGGLE_KERNEL_SLUG={user}/{kernel_slug}\n")
    print(f"GITHUB_ENV written: KAGGLE_KERNEL_SLUG={user}/{kernel_slug}")

kernel_code = """
import subprocess, os, time, asyncio

subprocess.run(["pip", "install", "playwright", "-q"])
subprocess.run(["playwright", "install", "chromium", "--with-deps"])
subprocess.Popen(["Xvfb", ":99", "-screen", "0", "1920x1080x24"])
os.environ["DISPLAY"] = ":99"
time.sleep(2)

ffp = subprocess.Popen(["ffmpeg","-y","-f","x11grab","-framerate","30","-video_size","1920x1080","-i",":99","-t","25","-vcodec","libx264","-profile:v","baseline","-level:v","3.1","-pix_fmt","yuv420p","-movflags","+faststart","-acodec","aac","-ar","44100","-crf","18","-preset","fast","/tmp/screen_raw.mp4"])

from playwright.async_api import async_playwright

TARGET = "TARGET_PLACEHOLDER"

async def browse():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--no-sandbox","--disable-setuid-sandbox","--window-size=1920,1080"])
        ctx = await browser.new_context(viewport={"width":1920,"height":1080})
        page = await ctx.new_page()
        print(f"Go to {TARGET}")
        try:
            await page.goto(TARGET, wait_until="networkidle", timeout=20000)
        except:
            await page.goto(TARGET, timeout=20000)
        await page.wait_for_timeout(3000)
        for y in [400, 900, 1400, 0]:
            await page.evaluate(f"window.scrollTo({{top:{y},behavior:'smooth'}})")
            await page.wait_for_timeout(2500)
        await browser.close()

asyncio.run(browse())
ffp.wait()

import shutil, pathlib
pathlib.Path("/kaggle/working").mkdir(exist_ok=True)
shutil.copy("/tmp/screen_raw.mp4", "/kaggle/working/screen_raw.mp4")
print("Done:", os.path.getsize("/kaggle/working/screen_raw.mp4")//1024, "KB")
""".replace("TARGET_PLACEHOLDER", target_url)

meta = {
    "id": f"{user}/{kernel_slug}",
    "title": f"Screen Recording {kernel_slug}",
    "code_file": "kernel.py",
    "language": "python",
    "kernel_type": "script",
    "is_private": True,
    "enable_gpu": False,
    "enable_internet": True,
    "dataset_sources": [],
    "competition_sources": [],
    "kernel_sources": []
}

with tempfile.TemporaryDirectory() as d:
    open(f"{d}/kernel.py", "w").write(kernel_code)
    json.dump(meta, open(f"{d}/kernel-metadata.json", "w"))
    z = f"{d}/k.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.write(f"{d}/kernel.py", "kernel.py")
        zf.write(f"{d}/kernel-metadata.json", "kernel-metadata.json")
    with open(z, "rb") as f:
        r2 = requests.post("https://www.kaggle.com/api/v1/kernels/push",
                          auth=auth, files={"file":("k.zip",f,"application/zip")}, timeout=30)
    print(f"Push: {r2.status_code}")
    print(r2.text[:300])
