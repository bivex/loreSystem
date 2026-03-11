#!/usr/bin/env python3
"""Compare CAMEL memory embedders on the curated recall benchmark corpus."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.application.integration.camel_bridge.memory import HashingTextEmbedder, LocalNgramTextEmbedder
from src.application.integration.camel_bridge.memory_benchmark import run_curated_embedding_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark CAMEL memory embedders on the curated recall corpus.")
    parser.add_argument("--top-k", type=int, default=3, help="Top-K cutoff for recall metrics (default: 3)")
    parser.add_argument("--local-dimension", type=int, default=384, help="Vector dimension for the local ngram embedder")
    parser.add_argument("--hash-dimension", type=int, default=96, help="Vector dimension for the legacy hash embedder")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = [
        run_curated_embedding_benchmark(LocalNgramTextEmbedder(dimension=args.local_dimension), backend_name="local", top_k=args.top_k),
        run_curated_embedding_benchmark(HashingTextEmbedder(dimension=args.hash_dimension), backend_name="hash", top_k=args.top_k),
    ]

    print("CAMEL memory embedding benchmark")
    print("=" * 32)
    for result in results:
        print(f"{result.backend_name}: hits@1={result.hits_at_1} hits@{args.top_k}={result.hits_at_3} mrr={result.mean_reciprocal_rank:.3f}")
    print("\nPer-query top results")
    print("-" * 32)
    for query_index in range(len(results[0].query_results)):
        local_query = results[0].query_results[query_index]
        hash_query = results[1].query_results[query_index]
        print(f"{local_query.label}: expected={local_query.expected_scenario}/{local_query.expected_entity_type}")
        print(f"  local rank={local_query.first_relevant_rank} top={', '.join(local_query.top_results)}")
        print(f"  hash  rank={hash_query.first_relevant_rank} top={', '.join(hash_query.top_results)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())