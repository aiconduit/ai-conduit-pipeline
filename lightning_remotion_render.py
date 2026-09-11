#!/usr/bin/env python3
"""
Lightning.ai Studio APIを使ってRemotionドキュメンタリーをレンダリングする
"""
import requests, os, time, json, sys

LIGHTNING_USER_ID = os.environ["LIGHTNING_USER_ID"]
LIGHTNING_API_KEY = os.environ["LIGHTNING_API_KEY"]
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

BASE_URL = "https://lightning.ai/v1"
HEADERS = {
    "Authorization": f"Bearer {LIGHTNING_API_KEY}",
    "Content-Type": "application/json",
}

def create_studio():
    """Lightning Studioを作成"""
    payload = {
        "name": "remotion-render",
        "cluster_id": "default",
        "teamspace_id": LIGHTNING_USER_ID,
        "machine": {
            "name": "cpu-8"  # 8コアCPU
        },
    }
    resp = requests.post(f"{BASE_URL}/studios", headers=HEADERS, json=payload)
    print(f"Studio作成: {resp.status_code}")
    print(resp.text[:500])
    return resp.json()

def run_command(studio_id, command):
    """Studio上でコマンドを実行"""
    payload = {
        "command": command,
        "timeout": 7200,
    }
    resp = requests.post(
        f"{BASE_URL}/studios/{studio_id}/commands",
        headers=HEADERS, json=payload
    )
    print(f"Command: {resp.status_code}")
    return resp.json()

def main():
    # API疎通テスト
    resp = requests.get(f"{BASE_URL}/studios", headers=HEADERS)
    print(f"Studios一覧: {resp.status_code}")
    data = resp.json()
    print(json.dumps(data, indent=2)[:1000])

if __name__ == "__main__":
    main()
