import modal
import os
import io

app = modal.App("wan22-video-gen")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch==2.4.0",
        "diffusers>=0.32.0",
        "transformers>=4.49.0",
        "accelerate",
        "imageio[ffmpeg]",
        "sentencepiece",
    )
)

@app.function(
    gpu="T4",
    image=image,
    timeout=300,
    memory=16384,
)
def generate_video(prompt: str, scene_name: str) -> bytes:
    import torch
    from diffusers import WanPipeline
    import imageio
    
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"生成中: {scene_name} - {prompt[:50]}")
    
    pipe = WanPipeline.from_pretrained(
        "Wan-AI/Wan2.1-T2V-1.3B-Diffusers",
        torch_dtype=torch.float16,
    )
    pipe.to("cuda")
    pipe.enable_model_cpu_offload()
    
    output = pipe(
        prompt=prompt,
        num_inference_steps=20,
        height=832,
        width=480,
        num_frames=49,
        guidance_scale=5.0,
    )
    
    frames = output.frames[0]
    buf = io.BytesIO()
    imageio.mimsave(buf, frames, format="mp4", fps=8, quality=8)
    video_bytes = buf.getvalue()
    print(f"✅ 生成完了: {len(video_bytes)//1024}KB")
    return video_bytes


@app.local_entrypoint()
def main():
    import json
    
    scenes = [
        ("hook",     "frustrated developer staring at dark terminal screen, close up face, cinematic 4K"),
        ("why",      "developer typing frantically at computer with error messages on screen"),
        ("solution", "developer smiling at computer screen showing successful code, bright terminal"),
        ("step1",    "close up hands typing commands on dark mechanical keyboard, terminal screen"),
        ("step2",    "code editor showing YAML configuration file, syntax highlighting, dark theme"),
        ("result",   "developer celebrating at desk, multiple monitors, successful deployment"),
        ("cta",      "smartphone screen showing download notification, modern app interface"),
    ]
    
    os.makedirs("assets/wan22_videos", exist_ok=True)
    generated = []
    
    for scene_name, prompt in scenes:
        print(f"\n=== {scene_name} ===")
        try:
            video_bytes = generate_video.remote(prompt, scene_name)
            path = f"assets/wan22_videos/{scene_name}.mp4"
            with open(path, "wb") as f:
                f.write(video_bytes)
            size = len(video_bytes) // 1024
            generated.append({"scene": scene_name, "path": path, "size_kb": size})
            print(f"✅ {path} ({size}KB)")
        except Exception as e:
            print(f"❌ {scene_name}: {e}")
    
    print(f"\n生成完了: {len(generated)}/7シーン")
    with open("assets/wan22_videos/manifest.json", "w") as f:
        json.dump(generated, f, indent=2)
