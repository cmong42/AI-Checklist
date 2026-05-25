"""
Low-Level Language Coding Agent (Fortran, Assembly, LLVM-IR)
============================================================
Uses FortranCodeGen-3B-SynthData - a Qwen 2.5 Coder 3B model
fine-tuned for Fortran90 and low-level code generation.
"""

from llama_cpp import Llama
import os
import sys

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "FortranCodeGen-3B-SynthData.Q4_K_M.gguf",
)


class LowLevelCodingAgent:
    def __init__(self, model_path: str = MODEL_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                "Run download_model.py first."
            )
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_threads=4,
            n_gpu_layers=0,
            verbose=False,
        )

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
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
