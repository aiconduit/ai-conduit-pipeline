import modal
import os, io, json

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
        "bitsandbytes",
    )
)

@app.function(
    gpu="A10G",  # 24GB・無料枠OK
    image=image,
    timeout=900,
    memory=32768,
)
def generate_hq_video(prompt: str, scene_name: str) -> bytes:
    import torch
    import numpy as np
    from diffusers import WanPipeline
    import imageio
    
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory // 1024**3}GB")
    print(f"生成中: {scene_name}")
    
    # Wan2.1 5B - A10G 24GBで動かすための最適化
    pipe = WanPipeline.from_pretrained(
        "Wan-AI/Wan2.1-T2V-5B-Diffusers",
        torch_dtype=torch.float16,  # bfloat16→float16でメモリ節約
    )
    pipe.enable_model_cpu_offload()
    pipe.vae.enable_slicing()
    pipe.vae.enable_tiling()
    
    # メモリ節約のため解像度を調整
    output = pipe(
        prompt=prompt,
        negative_prompt="blurry, low quality, distorted, watermark, text overlay, bad anatomy, ugly",
        num_inference_steps=40,
        height=720,
        width=480,
        num_frames=49,  # 約6秒
        guidance_scale=7.0,
    )
    
    frames = output.frames[0]
    frames_uint8 = [(np.clip(np.array(f), 0, 1) * 255).astype(np.uint8) for f in frames]
    
    buf = io.BytesIO()
    imageio.mimsave(buf, frames_uint8, format="mp4", fps=16, quality=9)
    video_bytes = buf.getvalue()
    print(f"✅ 生成完了: {len(video_bytes)//1024}KB")
    return video_bytes


def make_video_prompt(scene_title: str, narration: str) -> str:
    style = "cinematic 4K, dark moody lighting, professional, sharp focus, no text no watermark, ultra realistic"
    
    base = {
        "Hook":     f"developer at dark computer setup looking satisfied, terminal screen glowing green, professional coding workspace, {style}",
        "Why":      f"developer frustrated at computer screen showing red error messages, stressed at desk, dark office night, {style}",
        "Solution": f"terminal command line interface close up, green text scrolling on black screen, solution found, {style}",
        "Step1":    f"hands typing on mechanical keyboard extreme close up, green terminal glow, dark background, {style}",
        "Step2":    f"code editor with YAML configuration file syntax highlighting, dark theme VSCode style monitor, {style}",
        "Result":   f"developer smiling at multiple monitors showing successful green output, achievement feeling, {style}",
        "CTA":      f"smartphone held in hand showing notification screen close up, download icon glowing, modern UI, {style}",
    }
    
    # ナレーションからキーワード追加
    extra = []
    if "モバイル" in narration or "スマホ" in narration:
        extra.append("smartphone mobile device")
    if "ループ" in narration or "loop" in narration.lower() or "自動" in narration:
        extra.append("automated loop running")
    if "レビュー" in narration or "review" in narration.lower():
        extra.append("code review screen")
    if "コマンド" in narration or "command" in narration.lower():
        extra.append("command line terminal")
        
    prompt = base.get(scene_title, f"professional developer working, {style}")
    if extra:
        prompt = ", ".join(extra) + ", " + prompt
    return prompt


@app.local_entrypoint()
def main():
    import requests as req
    
    token = os.environ.get("GITHUB_TOKEN", "")
    h = {"Authorization": f"token {token}"}
    
    r = req.get(
        "https://raw.githubusercontent.com/aiconduit/ai-conduit-pipeline/master/sns_automation/news_content_plan.json",
        headers=h, timeout=10)
    plan = r.json()
    
    title = plan.get("selected_title", "Claude Code Tips")
    scenes = plan.get("script", {}).get("scenes", plan.get("scenes", []))
    
    print(f"\n台本: {title}")
    print(f"シーン数: {len(scenes)}")
    
    os.makedirs("assets/wan22_hq", exist_ok=True)
    generated = []
    
    for scene in scenes[:7]:
        scene_title = scene.get("title", "")
        narration = scene.get("narration", "")
        prompt = make_video_prompt(scene_title, narration)
        
        print(f"\n=== {scene_title} ===")
        print(f"ナレーション: {narration[:50]}")
        print(f"映像: {prompt[:80]}")
        
        try:
            video_bytes = generate_hq_video.remote(prompt, scene_title)
            path = f"assets/wan22_hq/{scene_title.lower()}.mp4"
            with open(path, "wb") as f:
                f.write(video_bytes)
            size = len(video_bytes) // 1024
            generated.append({"scene": scene_title, "narration": narration, "prompt": prompt, "path": path, "size_kb": size})
            print(f"✅ {path} ({size}KB)")
        except Exception as e:
            print(f"❌ {scene_title}: {e}")
    
    with open("assets/wan22_hq/manifest.json", "w", encoding="utf-8") as f:
        json.dump(generated, f, indent=2, ensure_ascii=False)
    print(f"\n生成完了: {len(generated)}/7シーン")
