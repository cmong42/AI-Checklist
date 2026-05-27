import os
import sys

try:
    from llama_cpp import Llama
except (OSError, RuntimeError) as _:
    Llama = None

HF_MODEL_REPO = os.environ.get(
    "HF_MODEL_REPO",
    "amelia-the-fox/FortranCodeGen-3B-SunthData-GGUF",
)
HF_MODEL_FILE = os.environ.get(
    "HF_MODEL_FILE",
    "FortranCodeGen-3B-SynthData.Q4_K_M.gguf",
)

LOCAL_DIR = os.path.join(os.path.dirname(__file__), "models")
VERCEL_MODEL_DIR = "/tmp/models"

MODEL_PATH = os.path.join(LOCAL_DIR, HF_MODEL_FILE)


def _resolve_model_path() -> str:
    if os.path.exists(MODEL_PATH):
        return MODEL_PATH

    vercel_path = os.path.join(VERCEL_MODEL_DIR, HF_MODEL_FILE)
    if os.path.exists(vercel_path):
        return vercel_path

    if os.environ.get("VERCEL") == "1":
        os.makedirs(VERCEL_MODEL_DIR, exist_ok=True)
        return _download_model(VERCEL_MODEL_DIR)
    return MODEL_PATH


def _download_model(download_dir: str) -> str:
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        raise ImportError(
            "Missing huggingface_hub. Install it with: pip install huggingface_hub"
        )

    downloaded_path = hf_hub_download(
        repo_id=HF_MODEL_REPO,
        filename=HF_MODEL_FILE,
        local_dir=download_dir,
        local_dir_use_symlinks=False,
    )
    return downloaded_path


class LowLevelCodingAgent:
    def __init__(self, model_path: str = None):
        if Llama is None:
            self.llm = None
            return
        model_path = model_path or _resolve_model_path()
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                "Upload the GGUF file to Hugging Face and set "
                "HF_MODEL_REPO and HF_MODEL_FILE env vars, "
                "or run download_model.py locally first."
            )
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_threads=4,
            n_gpu_layers=0,
            verbose=False,
        )

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        if self.llm is None:
            return (
                "AI Assistant unavailable: the local LLM could not be loaded "
                "in this environment. Run the backend locally with "
                "'python3 app.py' for AI features."
            )
        output = self.llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.1,
        )
        return output["choices"][0]["message"]["content"].strip()


EXAMPLES = {
    "fortran_hello": "Write a Fortran program that prints 'Hello, World!'",
    "fortran_factorial": "Write a Fortran program to compute factorial of n",
    "fortran_sort": "Write a Fortran subroutine that sorts an array using bubble sort",
    "assembly_sum": "Write x86_64 Assembly code to sum numbers from 1 to 100",
    "assembly_fib": "Write x86 Assembly to compute the nth Fibonacci number",
}


def main():
    agent = LowLevelCodingAgent()

    print("Low-Level Coding Agent (FortranCodeGen 3B)")
    print("=" * 50)
    print("Available examples:")
    for key, desc in EXAMPLES.items():
        print(f"  {key}: {desc}")
    print("Or type your own prompt.")

    while True:
        try:
            choice = input("\nPrompt (or 'quit'): ").strip()
            if not choice or choice == "quit":
                break
            if choice in EXAMPLES:
                prompt = EXAMPLES[choice]
            else:
                prompt = choice
            print(f"\n>>> {prompt}\n")
            result = agent.generate(prompt)
            print(result)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
