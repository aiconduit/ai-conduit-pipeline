import requests, os, json

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

def score_script(scenes):
    if not GROQ_API_KEY:
        return scenes
    script_text = "\n".join([f"Scene {s['id']}: {s['text']}" for s in scenes])
    prompt = f"""Rate each scene viral potential 1-10 for Japanese tech channel.
Scenes:
{script_text}
Return ONLY JSON: [{{"id":1,"score":8}},...] """
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={"model": "llama-3.3-70b-versatile",
                  "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}, timeout=15)
        text = r.json()["choices"][0]["message"]["content"].strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"): text = text[4:]
        scores = json.loads(text.strip())
        score_map = {s["id"]: s["score"] for s in scores}
        for scene in scenes:
            scene["viral_score"] = score_map.get(scene["id"], 5)
            print(f"   Scene {scene['id']}: {scene['viral_score']}/10")
    except Exception as e:
        print(f"   スコアリング失敗: {e}")
    return scenes

def optimize_hook(scenes):
    hook = scenes[0] if scenes else None
    if hook and hook.get("viral_score", 5) < 6:
        print(f"   ⚠️ フックスコア低({hook.get('viral_score')}): 要改善")
    return scenes
