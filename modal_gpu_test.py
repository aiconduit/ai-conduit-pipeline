import modal

app = modal.App("gpu-test")
image = modal.Image.debian_slim().pip_install("torch")

@app.function(gpu="T4", image=image, timeout=60)
def check_gpu():
    import torch
    cuda = torch.cuda.is_available()
    if cuda:
        name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory // 1024**3
        return f"GPU: {name}, VRAM: {vram}GB"
    return "No GPU"

@app.local_entrypoint()
def main():
    with modal.enable_output():
        result = check_gpu.remote()
        print(result)
