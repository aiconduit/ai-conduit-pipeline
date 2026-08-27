import os, requests

user = os.environ["KAGGLE_USERNAME"]
key = os.environ["KAGGLE_KEY"]
auth = (user, key)

print(f"User: {user}")

# 認証確認
r = requests.get("https://www.kaggle.com/api/v1/datasets/list",
                params={"search": "test", "pageSize": 1}, auth=auth, timeout=10)
print(f"Auth check: {r.status_code}")

# カーネル一覧確認
r2 = requests.get(f"https://www.kaggle.com/api/v1/kernels",
                 params={"mine": True, "pageSize": 10}, auth=auth, timeout=10)
print(f"Kernels list: {r2.status_code}")
if r2.status_code == 200:
    kernels = r2.json()
    for k in kernels[:5]:
        print(f"  - {k.get('ref', k.get('id', 'unknown'))}")
else:
    print(r2.text[:200])

# hf-screen-recordingを直接確認
r3 = requests.get(f"https://www.kaggle.com/api/v1/kernels/{user}/hf-screen-recording",
                 auth=auth, timeout=10)
print(f"hf-screen-recording: {r3.status_code}")
print(r3.text[:200])
