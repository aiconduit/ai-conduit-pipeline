import os, json, requests, zipfile, tempfile

user = os.environ["KAGGLE_USERNAME"]
key = os.environ["KAGGLE_KEY"]
auth = (user, key)
print(f"User: {user}")

# 認証確認
r = requests.get("https://www.kaggle.com/api/v1/datasets/list",
                params={"search": "test", "pageSize": 1}, auth=auth, timeout=10)
print(f"Auth: {r.status_code}")

kernel_code = """
import torch
print(f"CUDA: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory // 1024**3}GB")
print("OK")
"""

meta = {
    "id": f"{user}/wan22-gpu-test",
    "title": "Wan2.2 GPU Test",
    "code_file": "kernel.py",
    "language": "python",
    "kernel_type": "script",
    "is_private": True,
    "enable_gpu": True,
    "enable_internet": True,
    "dataset_sources": [],
    "competition_sources": [],
    "kernel_sources": []
}

with tempfile.TemporaryDirectory() as d:
    open(f"{d}/kernel.py","w").write(kernel_code)
    json.dump(meta, open(f"{d}/kernel-metadata.json","w"))
    z = f"{d}/k.zip"
    with zipfile.ZipFile(z,"w") as zf:
        zf.write(f"{d}/kernel.py","kernel.py")
        zf.write(f"{d}/kernel-metadata.json","kernel-metadata.json")
    with open(z,"rb") as f:
        r2 = requests.post("https://www.kaggle.com/api/v1/kernels/push",
                          auth=auth, files={"file":("k.zip",f,"application/zip")}, timeout=30)
    print(f"Push: {r2.status_code}")
    print(r2.text[:300])
