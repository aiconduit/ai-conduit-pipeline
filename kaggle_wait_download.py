import os, requests, time, subprocess

u = os.environ["KAGGLE_USERNAME"]
k = os.environ["KAGGLE_KEY"]

# GITHUB_ENVから取得したスラッグを使用
slug = os.environ.get("KAGGLE_KERNEL_SLUG", "")
if not slug:
    # フォールバック: ユーザーのカーネル一覧から最新を取得
    r = requests.get("https://www.kaggle.com/api/v1/kernels",
                    params={"mine": True, "pageSize": 5},
                    auth=(u, k), timeout=10)
    print(f"Kernels list: {r.status_code}")
    if r.status_code == 200 and r.json():
        slug = r.json()[0].get("ref", "")
        print(f"Latest kernel: {slug}")

print(f"Waiting for: {slug}")
for i in range(40):
    r = requests.get(f"https://www.kaggle.com/api/v1/kernels/{slug}",
                    auth=(u, k), timeout=10)
    if r.status_code == 200:
        st = r.json().get("currentRunningVersion", {}).get("status", "?")
        print(f"  {i*15}s: {st}")
        if st in ["complete", "error"]:
            print(f"Done: {st}")
            break
    else:
        print(f"  {i*15}s: HTTP{r.status_code} {r.text[:100]}")
    time.sleep(15)

os.environ["KAGGLE_USERNAME"] = u
os.environ["KAGGLE_KEY"] = k
owner, kernel_name = slug.split("/") if "/" in slug else (u, slug)
result = subprocess.run(
    ["kaggle", "kernels", "output", f"{owner}/{kernel_name}", "-p", "/tmp/kout/"],
    capture_output=True, text=True
)
print(result.stdout[:300])
print(result.stderr[:200])

import shutil
if os.path.exists("/tmp/kout/screen_raw.mp4"):
    shutil.copy("/tmp/kout/screen_raw.mp4", "screen_raw.mp4")
    print(f"Downloaded: {os.path.getsize('screen_raw.mp4')//1024}KB")
else:
    files = os.listdir("/tmp/kout/") if os.path.exists("/tmp/kout/") else []
    print(f"No recording. Files: {files}")
