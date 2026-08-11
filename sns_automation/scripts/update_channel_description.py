#!/usr/bin/env python3
import requests, os

def refresh_token(refresh, client_id, client_secret):
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh,
        "client_id": client_id,
        "client_secret": client_secret,
    }, timeout=10)
    return r.json().get("access_token", "") if r.status_code == 200 else ""

access_token = refresh_token(
    os.environ["YOUTUBE_REFRESH_TOKEN"],
    os.environ["YOUTUBE_CLIENT_ID"],
    os.environ["YOUTUBE_CLIENT_SECRET"]
)

if not access_token:
    print("Token refresh failed")
    exit(1)

print("Auth OK")

description = (
    "AI Conduit | Claude/Claude Code\n"
    "Claude Code Tips\n\n"
    "Twitter: https://x.com/AIconduit777\n"
    "Instagram: https://www.instagram.com/aiconduit/\n"
    "Threads: https://threads.com/@aiconduit\n"
    "note: https://note.com/aiconduit\n"
    "GitHub: https://github.com/aiconduit"
)

headers = {"Authorization": f"Bearer {access_token}"}
r = requests.get("https://www.googleapis.com/youtube/v3/channels",
    headers=headers,
    params={"part": "id,snippet", "mine": True},
    timeout=10)

if r.status_code != 200:
    print(f"Channel fetch failed: {r.status_code} {r.text[:100]}")
    exit(1)

items = r.json().get("items", [])
if not items:
    print("No channel found")
    exit(1)

channel_id = items[0]["id"]
current_title = items[0]["snippet"]["title"]
print(f"Channel: {current_title} ({channel_id})")

r2 = requests.put(
    "https://www.googleapis.com/youtube/v3/channels",
    headers={**headers, "Content-Type": "application/json"},
    params={"part": "snippet"},
    json={
        "id": channel_id,
        "snippet": {
            "title": current_title,
            "description": description,
            "country": "JP",
        }
    },
    timeout=10)

if r2.status_code == 200:
    print("Channel description updated!")
    print(description)
else:
    print(f"Update failed: {r2.status_code} {r2.text[:200]}")
    exit(1)
