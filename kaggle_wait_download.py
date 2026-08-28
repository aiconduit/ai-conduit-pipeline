import os, requests, time, subprocess, pathlib

u = os.environ["KAGGLE_USERNAME"]
k = os.environ["KAGGLE_KEY"]

# kaggle_screen_record.pyが書いたスラッグを読み込む
slug_file = "/tmp/kernel_slug.txt"
if os.path.exists(slug_file):
    slug = open(slug_file).read().strip()
    print(f"Slug from file: {slug}")
else:
    # フォールバック：ユーザー名のカーネル一覧から最新を取得
    r = requests.get("https://www.kaggle.com/api/v1/kernels",
                    params={"mine": True, "pageSize": 5, "sortBy": "dateRun"},
                    auth=(u, k), timeout=10)
    print(f"Kernels list: {r.status_code}")
    if r.status_code == 200:
        kernels = r.json()
        if kernels:
            slug = kernels[0].get("ref", f"{u}/wan22-gpu-test")
            print(f"Latest kernel: {slug}")
        else:
            slug = f"{u}/wan22-gpu-test"
    else:
        slug = f"{u}/wan22-gpu-test"
        print(r.text[:200])

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

# ダウンロード
os.environ["KAGGLE_USERNAME"] = u
os.environ["KAGGLE_KEY"] = k
kernel_name = slug.split("/")[-1]
owner = slug.split("/")[0]
result = subprocess.run(
    ["kaggle", "kernels", "output", f"{owner}/{kernel_name}", "-p", "/tmp/kout/"],
    capture_output=True, text=True
)
print(result.stdout[:300])
print(result.stderr[:200])

import shutil
if os.path.exists("/tmp/kout/screen_raw.mp4"):
    shutil.copy("/tmp/kout/screen_raw.mp4", "screen_raw.mp4")
    size = os.path.getsize("screen_raw.mp4")
    print(f"Downloaded: {size//1024}KB")
else:
    files = os.listdir("/tmp/kout/") if os.path.exists("/tmp/kout/") else []
    print(f"No recording. Files: {files}")
