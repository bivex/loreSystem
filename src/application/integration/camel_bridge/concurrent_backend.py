"""Concurrent wrapper for CAMEL backend to speed up LM Studio generation."""

from __future__ import annotations

import concurrent.futures
from typing import Any
from src.application.integration.camel_bridge.backend import AgentTextBackend, CamelChatBackend


class ConcurrentCamelBackend:
    """Wrapper that executes multiple backend.generate() calls in parallel."""

    def __init__(self, backend: CamelChatBackend, max_workers: int = 4):
        self.backend = backend
        self.max_workers = max_workers

    def generate(self, system_message: str, user_message: str) -> str:
        """Single call wrapper - delegates to underlying backend."""
        return self.backend.generate(system_message, user_message)

    def generate_batch(self, prompts: list[tuple[str, str]]) -> list[str]:
        """
        Generate multiple prompts in parallel.

        Args:
            prompts: List of (system_message, user_message) tuples

        Returns:
            List of generated responses in same order as prompts
        """
        if not prompts:
            return []

        # For single prompt, use direct call
        if len(prompts) == 1:
            return [self.backend.generate(*prompts[0])]

        # Use ThreadPoolExecutor for parallel generation
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.backend.generate, system, user): idx
                for idx, (system, user) in enumerate(prompts)
            }

            results: list[str | None] = [None] * len(prompts)

            for future in concurrent.futures.as_completed(futures):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    print(f"[ERROR] Generation failed for prompt {idx}: {e}")
                    results[idx] = ""

            return [r for r in results if r is not None]

    # Delegate all other attributes to underlying backend
    def __getattr__(self, name: str) -> Any:
        return getattr(self.backend, name)


def make_concurrent(backend: CamelChatBackend | ConcurrentCamelBackend, max_workers: int = 4) -> ConcurrentCamelBackend:
    """Wrap a backend for concurrent execution if not already wrapped."""
    if isinstance(backend, ConcurrentCamelBackend):
        return backend
    return ConcurrentCamelBackend(backend, max_workers=max_workers)
