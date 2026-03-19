#!/usr/bin/env python3
"""Benchmark LM Studio sequential vs concurrent generation."""

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, "/Volumes/External/Code/loreSystem/src")

os.environ.update({
    "CAMEL_MODEL_PLATFORM": "OPENAI",
    "CAMEL_MODEL_BASE_URL": "http://127.0.0.1:1234",
    "CAMEL_MODEL_TYPE": "l3-8b-stheno-v3.2-mlx",
    "CAMEL_MODEL_TEMPERATURE": "0.8",
})

from src.application.integration.camel_bridge import CamelChatBackend


def benchmark_sequential(backend: CamelChatBackend, prompts: list[tuple[str, str]]) -> float:
    """Benchmark sequential generation."""
    start = time.time()
    for system, user in prompts:
        backend.generate(system, user)
    return time.time() - start


def benchmark_concurrent(backend: CamelChatBackend, prompts: list[tuple[str, str]], workers: int = 4) -> float:
    """Benchmark concurrent generation."""
    start = time.time()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        list(executor.map(lambda p: backend.generate(*p), prompts))
    return time.time() - start


def main():
    print("🚀 LM Studio Benchmark")
    print("=" * 50)
    print()

    # Test prompts (CAMEL Bridge style)
    prompts = [
        ("Ты — мастер слухов dark fantasy.", "Создай слух о древнем проклятии"),
        ("Ты — мастер событий dark fantasy.", "Создай событие в тёмном лесу"),
        ("Ты — мастер персонажей dark fantasy.", "Создай трагичного героя"),
        ("Ты — мастер отношений dark fantasy.", "Создай сложные отношения между героями"),
    ]

    backend = CamelChatBackend()

    # Warmup - ensure model is loaded
    print("🔥 Warming up (loading model)...")
    for _ in range(3):
        try:
            backend.generate("Тест", "Скажи: ОК")
            break
        except Exception as e:
            if "unloaded" in str(e).lower() or "400" in str(e):
                print("   Waiting for model to load...")
                time.sleep(2)
                continue
            raise
    print()

    # Sequential
    print("⏱️  Sequential (4 prompts)...")
    seq_time = benchmark_sequential(backend, prompts)
    print(f"   Time: {seq_time:.1f}s")
    print(f"   Avg per prompt: {seq_time / len(prompts):.1f}s")
    print()

    # Concurrent 2
    print("⏱️  Concurrent (2 workers)...")
    conc2_time = benchmark_concurrent(backend, prompts, workers=2)
    print(f"   Time: {conc2_time:.1f}s")
    print(f"   Speedup: {seq_time / conc2_time:.1f}x")
    print()

    # Concurrent 4
    print("⏱️  Concurrent (4 workers)...")
    conc4_time = benchmark_concurrent(backend, prompts, workers=4)
    print(f"   Time: {conc4_time:.1f}s")
    print(f"   Speedup: {seq_time / conc4_time:.1f}x")
    print()

    print("=" * 50)
    print(f"Sequential:    {seq_time:.1f}s")
    print(f"Concurrent 2:  {conc2_time:.1f}s ({seq_time / conc2_time:.1f}x)")
    print(f"Concurrent 4:  {conc4_time:.1f}s ({seq_time / conc4_time:.1f}x)")
    print()
    print("💡 Recommendation: Set Max Concurrent Predictions in LM Studio to 4-8")


if __name__ == "__main__":
    main()
