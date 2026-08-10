import modal
import os, io

app = modal.App("wan22-video-gen")

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
    )
)

@app.function(
    gpu="A10G",
    image=image,
    timeout=600,
    memory=32768,
)
def generate_video(prompt: str, scene_name: str) -> bytes:
    import torch
    import numpy as np
    from diffusers import WanPipeline
    import imageio
    
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"生成中: {scene_name}")
    
    pipe = WanPipeline.from_pretrained(
        "Wan-AI/Wan2.1-T2V-1.3B-Diffusers",
        torch_dtype=torch.bfloat16,
    )
    pipe.enable_model_cpu_offload()
    pipe.vae.enable_slicing()
    pipe.vae.enable_tiling()
    
    output = pipe(
        prompt=prompt,
        num_inference_steps=20,
        height=480,
        width=832,
        num_frames=49,
        guidance_scale=5.0,
    )
    
    frames = output.frames[0]
    # float32→uint8変換
    frames_uint8 = [(np.clip(f, 0, 1) * 255).astype(np.uint8) for f in frames]
    
    buf = io.BytesIO()
    imageio.mimsave(buf, frames_uint8, format="mp4", fps=8, quality=7)
    video_bytes = buf.getvalue()
    print(f"✅ 生成完了: {len(video_bytes)//1024}KB")
    return video_bytes


@app.local_entrypoint()
def main():
    import json
    
    scenes = [
        ("hook",     "frustrated developer staring at dark terminal screen, cinematic 4K"),
        ("why",      "developer typing frantically at computer with error messages on screen, dark office"),
        ("solution", "developer smiling at computer screen showing successful code, bright terminal"),
        ("step1",    "close up hands typing commands on dark mechanical keyboard, terminal screen glow"),
        ("step2",    "code editor showing YAML configuration file, syntax highlighting, dark theme monitor"),
        ("result",   "developer celebrating at desk, multiple monitors, successful deployment green screen"),
        ("cta",      "smartphone screen showing download notification, modern app interface close up"),
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
