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
        "bitsandbytes",
    )
)

@app.function(
    gpu="A10G",  # T4→A10G(24GB)に変更
    image=image,
    timeout=600,
    memory=32768,
)
def generate_video(prompt: str, scene_name: str) -> bytes:
    import torch
    from diffusers import WanPipeline
    from diffusers.utils import export_to_video
    import imageio, tempfile
    
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory // 1024**3}GB")
    print(f"PyTorch: {torch.__version__}")
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
    buf = io.BytesIO()
    imageio.mimsave(buf, frames, format="mp4", fps=8, quality=7)
    video_bytes = buf.getvalue()
    print(f"✅ 生成完了: {len(video_bytes)//1024}KB")
    return video_bytes


@app.local_entrypoint()
def main():
    os.makedirs("assets/wan22_videos", exist_ok=True)
    
    prompt = "frustrated developer staring at dark terminal screen, cinematic 4K"
    scene_name = "hook"
    
    print(f"=== {scene_name} 生成テスト ===")
    try:
        video_bytes = generate_video.remote(prompt, scene_name)
        path = f"assets/wan22_videos/{scene_name}.mp4"
        with open(path, "wb") as f:
            f.write(video_bytes)
        print(f"✅ 保存: {path} ({len(video_bytes)//1024}KB)")
    except Exception as e:
        print(f"❌ エラー: {e}")
