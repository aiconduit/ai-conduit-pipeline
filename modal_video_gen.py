import modal
import os

app = modal.App("wan22-video-gen")

# A10G GPU (24GB VRAM) - Wan2.2 5Bモデルに最適
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch==2.4.0",
        "diffusers>=0.30.0",
        "transformers",
        "accelerate",
        "imageio[ffmpeg]",
        "requests",
    )
)

@app.function(
    gpu="A10G",
    image=image,
    timeout=300,
    secrets=[modal.Secret.from_name("github-token")],
)
def generate_scene_video(prompt: str, scene_name: str) -> bytes:
    """シーン別動画生成"""
    import torch
    from diffusers import AutoPipelineForText2Video
    import io
    
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory // 1024**3}GB")
    print(f"生成中: {scene_name}")
    
    # Wan2.1 (軽量版) でテスト
    pipe = AutoPipelineForText2Video.from_pretrained(
        "ali-vilab/text-to-video-ms-1.7b",
        torch_dtype=torch.float16,
    ).to("cuda")
    
    result = pipe(
        prompt=prompt,
        num_inference_steps=20,
        num_frames=49,  # 約6秒
    )
    
    frames = result.frames[0]
    
    # MP4として書き出し
    import imageio
    buf = io.BytesIO()
    imageio.mimsave(buf, frames, format="mp4", fps=8)
    return buf.getvalue()


@app.local_entrypoint()
def main():
    scenes = [
        ("hook", "frustrated developer staring at dark terminal screen, cinematic"),
        ("step1", "close up hands typing commands on dark mechanical keyboard"),
        ("result", "developer celebrating success at computer, multiple screens"),
    ]
    
    import os
    os.makedirs("assets/modal_videos", exist_ok=True)
    
    for scene_name, prompt in scenes:
        print(f"\n生成: {scene_name}")
        video_bytes = generate_scene_video.remote(prompt, scene_name)
        path = f"assets/modal_videos/{scene_name}.mp4"
        with open(path, "wb") as f:
            f.write(video_bytes)
        print(f"✅ 保存: {path} ({len(video_bytes)//1024}KB)")
