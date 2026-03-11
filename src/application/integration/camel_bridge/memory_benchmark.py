"""Curated recall benchmark helpers for CAMEL bridge memory embedders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


class _EmbedderLike(Protocol):
    dimension: int

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


@dataclass(frozen=True)
class BenchmarkDocument:
    scenario: str
    entity_type: str
    summary_text: str


@dataclass(frozen=True)
class BenchmarkQuery:
    label: str
    query_text: str
    expected_scenario: str
    expected_entity_type: str


@dataclass(frozen=True)
class BenchmarkQueryResult:
    label: str
    expected_scenario: str
    expected_entity_type: str
    first_relevant_rank: int | None
    top_results: tuple[str, ...]


@dataclass(frozen=True)
class EmbeddingBenchmarkResult:
    backend_name: str
    hits_at_1: int
    hits_at_3: int
    mean_reciprocal_rank: float
    query_results: tuple[BenchmarkQueryResult, ...]


CURATED_BENCHMARK_DOCUMENTS: tuple[BenchmarkDocument, ...] = (
    BenchmarkDocument("harbor", "rumor", "Rumor: Bellfog Route — Dockworkers whisper that smugglers vanish moments after the iron harbor bells toll through the fog."),
    BenchmarkDocument("harbor", "event", "Event: Quay Sweep — Lantern wardens search the waterfront warehouses after another bell-marked disappearance."),
    BenchmarkDocument("harbor", "relationship", "Relationship: Mara Voss → Iven Hale — The quay disappearances force them into an uneasy alliance over smuggling debts."),
    BenchmarkDocument("harbor", "character", "Character: Mara Voss — A dockside broker who memorizes ship manifests and fears the bell-marked vanishings."),
    BenchmarkDocument("orchard", "rumor", "Rumor: Lantern Cider Waltz — Fruit sellers swear the orchard square erupts into dancing whenever contraband cider is opened under silk lanterns."),
    BenchmarkDocument("orchard", "event", "Event: Cider Market Clash — Lantern ropes snap above the orchard bazaar as masked dancers and merchants riot around spilled barrels."),
    BenchmarkDocument("orchard", "relationship", "Relationship: Sel Ardan → Toma Vale — They become inseparable after surviving the lantern-market cider riot."),
    BenchmarkDocument("orchard", "character", "Character: Toma Vale — A young vendor who smuggles rare apples and follows the lantern dancers through the market."),
    BenchmarkDocument("archive", "rumor", "Rumor: Stolen Ledgers — Apprentices insist forbidden ledgers vanished from the tower stacks before the copyists rebelled."),
    BenchmarkDocument("archive", "event", "Event: Archive Uprising — Scribes barricade the spiral library after censored account books disappear from the upper scriptorium."),
    BenchmarkDocument("archive", "relationship", "Relationship: Nera Quill → Dain Wren — The ledger scandal binds them in a quiet pact against the archivists' council."),
    BenchmarkDocument("archive", "character", "Character: Nera Quill — A tower scholar obsessed with missing account books and the politics of the scriptorium."),
    BenchmarkDocument("shrine", "rumor", "Rumor: Dawn Tithe Fraud — Pilgrims murmur that relic offerings are skimmed from the shrine chest before the sunrise procession."),
    BenchmarkDocument("shrine", "event", "Event: Processional Schism — Novices halt the hilltop rite when the tithe coffer is found half empty at dawn."),
    BenchmarkDocument("shrine", "relationship", "Relationship: Oren Pyre → Lysa Thorn — Their trust fractures while exposing theft among the procession keepers."),
    BenchmarkDocument("shrine", "character", "Character: Oren Pyre — A processional guard who audits every relic coffer before the dawn bells."),
)


CURATED_BENCHMARK_QUERIES: tuple[BenchmarkQuery, ...] = (
    BenchmarkQuery("harbor_rumor", "dock workers whisper after bell tolls before smugglers vanish", "harbor", "rumor"),
    BenchmarkQuery("harbor_character", "ship-manifest broker afraid of bell marked vanishings", "harbor", "character"),
    BenchmarkQuery("orchard_rumor", "fruit vendors dancing under silk lanterns with contraband cider", "orchard", "rumor"),
    BenchmarkQuery("orchard_relationship", "lantern market survivors become inseparable after the cider riot", "orchard", "relationship"),
    BenchmarkQuery("archive_event", "scribes barricade the library after censored account-book disappearances", "archive", "event"),
    BenchmarkQuery("archive_relationship", "quiet pact forged in the ledger scandal against the archivists council", "archive", "relationship"),
    BenchmarkQuery("shrine_rumor", "pilgrims murmur that relic offerings vanish before the sunrise procession", "shrine", "rumor"),
    BenchmarkQuery("shrine_character", "processional guard auditing every relic coffer before dawn bells", "shrine", "character"),
)


def _dot(left: Sequence[float], right: Sequence[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def run_curated_embedding_benchmark(
    embedder: _EmbedderLike,
    *,
    backend_name: str,
    top_k: int = 3,
    documents: Sequence[BenchmarkDocument] = CURATED_BENCHMARK_DOCUMENTS,
    queries: Sequence[BenchmarkQuery] = CURATED_BENCHMARK_QUERIES,
) -> EmbeddingBenchmarkResult:
    doc_vectors = embedder.embed([document.summary_text for document in documents])
    hits_at_1 = 0
    hits_at_3 = 0
    reciprocal_rank_total = 0.0
    query_results: list[BenchmarkQueryResult] = []

    for query in queries:
        query_vector = embedder.embed([query.query_text])[0]
        ranked = sorted(
            zip(documents, doc_vectors, strict=True),
            key=lambda item: _dot(query_vector, item[1]),
            reverse=True,
        )
        top_documents = [document for document, _vector in ranked[:top_k]]
        first_relevant_rank = next(
            (
                index
                for index, document in enumerate(top_documents, start=1)
                if document.scenario == query.expected_scenario and document.entity_type == query.expected_entity_type
            ),
            None,
        )
        if first_relevant_rank == 1:
            hits_at_1 += 1
        if first_relevant_rank is not None:
            hits_at_3 += 1
            reciprocal_rank_total += 1.0 / first_relevant_rank
        query_results.append(
            BenchmarkQueryResult(
                label=query.label,
                expected_scenario=query.expected_scenario,
                expected_entity_type=query.expected_entity_type,
                first_relevant_rank=first_relevant_rank,
                top_results=tuple(f"{document.scenario}/{document.entity_type}" for document in top_documents),
            )
        )

    return EmbeddingBenchmarkResult(
        backend_name=backend_name,
        hits_at_1=hits_at_1,
        hits_at_3=hits_at_3,
        mean_reciprocal_rank=reciprocal_rank_total / len(queries),
        query_results=tuple(query_results),
    )