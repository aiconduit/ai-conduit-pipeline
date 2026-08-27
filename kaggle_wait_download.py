import os, requests, time, subprocess

u = os.environ["KAGGLE_USERNAME"]
k = os.environ["KAGGLE_KEY"]
slug = f"{u}/hf-screen-recording"

print("Waiting for Kaggle kernel...")
for i in range(40):
    r = requests.get(f"https://www.kaggle.com/api/v1/kernels/{slug}", auth=(u, k), timeout=10)
    if r.status_code == 200:
        st = r.json().get("currentRunningVersion", {}).get("status", "?")
        print(f"  {i*15}s: {st}")
        if st in ["complete", "error"]:
            print(f"Done: {st}")
            break
    time.sleep(15)

# ダウンロード
os.environ["KAGGLE_USERNAME"] = u
os.environ["KAGGLE_KEY"] = k
result = subprocess.run(
    ["kaggle", "kernels", "output", f"{u}/hf-screen-recording", "-p", "/tmp/kout/"],
    capture_output=True, text=True
)
print(result.stdout)
print(result.stderr[:200])

import shutil, os
if os.path.exists("/tmp/kout/screen_raw.mp4"):
    shutil.copy("/tmp/kout/screen_raw.mp4", "screen_raw.mp4")
    size = os.path.getsize("screen_raw.mp4")
    print(f"Downloaded: {size//1024}KB")
else:
    print("No recording found")
    import os
    files = os.listdir("/tmp/kout/") if os.path.exists("/tmp/kout/") else []
    print(f"Files: {files}")
