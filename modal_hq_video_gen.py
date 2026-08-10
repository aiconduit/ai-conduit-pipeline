import modal
import os, io, json, sys

app = modal.App("wan22-hq-video-gen")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch>=2.5.0",
        "torchvision",
        "diffusers>=0.32.0",
        "transformers>=4.49.0",
        "accelerate",
        "imageio[ffmpeg]",
        "sentencepiece",
        "huggingface_hub",
        "numpy",
    )
)

@app.function(
    gpu="A100",  # 5Bモデルには40GB必要
    image=image,
    timeout=900,
    memory=40960,
)
def generate_hq_video(prompt: str, scene_name: str) -> bytes:
    import torch
    import numpy as np
    from diffusers import WanPipeline
    import imageio
    
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory // 1024**3}GB")
    print(f"生成中: {scene_name}")
    print(f"プロンプト: {prompt[:80]}")
    
    # Wan2.2 5B（高品質版）
    pipe = WanPipeline.from_pretrained(
        "Wan-AI/Wan2.1-T2V-5B-Diffusers",
        torch_dtype=torch.bfloat16,
    )
    pipe.enable_model_cpu_offload()
    pipe.vae.enable_slicing()
    pipe.vae.enable_tiling()
    
    output = pipe(
        prompt=prompt,
        negative_prompt="blurry, low quality, distorted, watermark, text overlay, bad anatomy",
        num_inference_steps=50,  # 高品質
        height=1280,
        width=720,
        num_frames=81,  # 約10秒
        guidance_scale=7.0,
    )
    
    frames = output.frames[0]
    frames_uint8 = [(np.clip(np.array(f), 0, 1) * 255).astype(np.uint8) for f in frames]
    
    buf = io.BytesIO()
    imageio.mimsave(buf, frames_uint8, format="mp4", fps=24, quality=9)
    video_bytes = buf.getvalue()
    print(f"✅ 生成完了: {len(video_bytes)//1024}KB")
    return video_bytes


@app.local_entrypoint()
def main():
    # 台本から映像プロンプトを生成するシステム
    # news_content_plan.jsonから台本を読み込む
    import requests as req
    
    TOKEN = os.environ.get("GITHUB_TOKEN", "")
    h = {"Authorization": f"token {TOKEN}"}
    
    r = req.get("https://raw.githubusercontent.com/aiconduit/ai-conduit-pipeline/master/sns_automation/news_content_plan.json",
                headers=h, timeout=10)
    plan = r.json()
    
    title = plan.get("selected_title", "Claude Code Tips")
    scenes = plan.get("script", {}).get("scenes", plan.get("scenes", []))
    
    print(f"\n台本: {title}")
    print(f"シーン数: {len(scenes)}")
    
    # シーン別映像プロンプト生成ルール
    def make_video_prompt(scene: dict) -> str:
        scene_title = scene.get("title", "")
        narration = scene.get("narration", "")
        
        # 共通スタイル
        style = "cinematic 4K, dark moody lighting, professional photography, sharp focus, no text overlay"
        
        prompts = {
            "Hook": f"developer at computer with satisfied expression, dark terminal screen glowing, professional coding environment, {style}",
            "Why": f"developer frustrated at computer screen showing error messages, stressed expression, dark office at night, {style}",
            "Solution": f"close up of terminal screen showing command line interface, green text on black background, {style}",
            "Step1": f"hands typing on mechanical keyboard, close up, terminal screen visible, dark background, green glow, {style}",
            "Step2": f"code editor screen showing configuration file with syntax highlighting, dark theme, professional, {style}",
            "Result": f"developer with satisfied smile looking at multiple monitors showing successful output, celebratory mood, {style}",
            "CTA": f"smartphone screen with notification, download icon, modern UI, close up, {style}",
        }
        
        # ナレーションからキーワードを抽出して追加
        keywords = []
        if "terminal" in narration or "ターミナル" in narration:
            keywords.append("terminal screen")
        if "review" in narration or "レビュー" in narration:
            keywords.append("code review")
        if "mobile" in narration or "スマホ" in narration or "モバイル" in narration:
            keywords.append("smartphone")
        if "loop" in narration or "自動" in narration:
            keywords.append("automated process")
            
        base_prompt = prompts.get(scene_title, f"professional developer working, {style}")
        if keywords:
            base_prompt = ", ".join(keywords) + ", " + base_prompt
        
        return base_prompt
    
    os.makedirs("assets/wan22_hq", exist_ok=True)
    generated = []
    
    for scene in scenes[:7]:
        scene_title = scene.get("title", "")
        narration = scene.get("narration", "")
        prompt = make_video_prompt(scene)
        
        print(f"\n=== {scene_title} ===")
        print(f"ナレーション: {narration[:50]}")
        print(f"映像プロンプト: {prompt[:80]}")
        
        try:
            video_bytes = generate_hq_video.remote(prompt, scene_title)
            path = f"assets/wan22_hq/{scene_title.lower()}.mp4"
            with open(path, "wb") as f:
                f.write(video_bytes)
            size = len(video_bytes) // 1024
            generated.append({
                "scene": scene_title,
                "narration": narration,
                "prompt": prompt,
                "path": path,
                "size_kb": size
            })
            print(f"✅ {path} ({size}KB)")
        except Exception as e:
            print(f"❌ {scene_title}: {e}")
    
    print(f"\n生成完了: {len(generated)}/{len(scenes[:7])}シーン")
    with open("assets/wan22_hq/manifest.json", "w", encoding="utf-8") as f:
        json.dump(generated, f, indent=2, ensure_ascii=False)
    
    print("\n✅ 全シーン生成完了")
