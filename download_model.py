import os
import subprocess
import sys

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
HF_REPO = "amelia-the-fox/FortranCodeGen-3B-SunthData-GGUF"
GGUF_FILE = "FortranCodeGen-3B-SynthData.Q4_K_M.gguf"
GGUF_PATH = os.path.join(MODEL_DIR, GGUF_FILE)

os.makedirs(MODEL_DIR, exist_ok=True)


def download_gguf():
    print(f"Downloading GGUF model from {HF_REPO}...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "huggingface_hub",
    ])
    from huggingface_hub import hf_hub_download
    hf_hub_download(
        repo_id=HF_REPO,
        filename=GGUF_FILE,
        local_dir=MODEL_DIR,
        local_dir_use_symlinks=False,
    )
    print(f"Model ready at {GGUF_PATH}")


if __name__ == "__main__":
    if os.path.exists(GGUF_PATH):
        print(f"Model already exists at {GGUF_PATH}")
        sys.exit(0)

    download_gguf()
