"""SQLite + Qdrant memory helpers for the CAMEL bridge."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sqlite3
from contextlib import closing
from dataclasses import dataclass, field
from typing import Protocol, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import NAMESPACE_URL, uuid5


def _trim(text: object, limit: int = 240) -> str:
    value = str(text or "").strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def _normalize_name_list(values: Sequence[str] | None) -> tuple[str, ...]:
    if not values:
        return ()
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = str(value or "").strip()
        lowered = item.lower()
        if not item or lowered in seen:
            continue
        seen.add(lowered)
        result.append(item)
    return tuple(result)


@dataclass(frozen=True)
class MemoryDocument:
    point_id: str
    tenant_id: int
    world_id: int
    entity_type: str
    entity_id: str
    summary_text: str
    character_names: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    source: str = "camel_bridge"

    def to_payload(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "world_id": self.world_id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "summary_text": self.summary_text,
            "character_names": list(self.character_names),
            "tags": list(self.tags),
            "source": self.source,
        }


class TextEmbedder(Protocol):
    dimension: int

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


def _tokenize_embedding_text(text: str) -> list[str]:
    return [token for token in re.findall(r"[^\W_]+", text.casefold()) if token]


def _add_hashed_feature(vector: list[float], feature: str, weight: float = 1.0) -> None:
    digest = hashlib.sha256(feature.encode("utf-8")).digest()
    slot = int.from_bytes(digest[:4], "big") % len(vector)
    sign = 1.0 if digest[4] % 2 == 0 else -1.0
    vector[slot] += weight * sign


def _normalize_embedding_vector(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


class HashingTextEmbedder:
    """Dependency-free fallback embedder with deterministic token hashing."""

    def __init__(self, dimension: int = 96):
        self.dimension = dimension

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for token in _tokenize_embedding_text(text):
            _add_hashed_feature(vector, f"tok:{token}")
        return _normalize_embedding_vector(vector)


class LocalNgramTextEmbedder:
    """Dependency-free local embedder using token, bigram, and char-ngram features."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        tokens = _tokenize_embedding_text(text)
        for token in tokens:
            _add_hashed_feature(vector, f"tok:{token}", 1.0)
            for ngram in self._char_ngrams(token):
                _add_hashed_feature(vector, f"chr:{ngram}", 0.35)
        for left, right in zip(tokens, tokens[1:]):
            _add_hashed_feature(vector, f"big:{left}|{right}", 1.25)
        if not tokens:
            normalized_text = " ".join(text.casefold().split())
            if normalized_text:
                _add_hashed_feature(vector, f"txt:{normalized_text}", 1.0)
        return _normalize_embedding_vector(vector)

    @staticmethod
    def _char_ngrams(token: str) -> list[str]:
        if len(token) <= 2:
            return [token]
        ngrams: list[str] = []
        padded = f"^{token}$"
        for size in (3, 4):
            if len(padded) < size:
                continue
            ngrams.extend(padded[index : index + size] for index in range(len(padded) - size + 1))
        return ngrams


class OpenAICompatibleTextEmbedder:
    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout_seconds: int = 30,
        dimension: int = 1536,
    ):
        self.model = model or os.getenv("CAMEL_MEMORY_EMBED_MODEL") or "text-embedding-3-small"
        self.base_url = (base_url or os.getenv("CAMEL_MEMORY_EMBED_BASE_URL") or os.getenv("CAMEL_MODEL_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self.api_key = api_key or os.getenv("CAMEL_MEMORY_EMBED_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.timeout_seconds = timeout_seconds
        self.dimension = dimension
        if not self.api_key:
            raise ValueError("CAMEL memory embedding API key is required for openai embedder")

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        payload = {"input": list(texts), "model": self.model}
        raw = self._request_json("POST", "/embeddings", payload)
        data = raw.get("data") or []
        vectors = [item.get("embedding") or [] for item in data]
        if not vectors:
            raise RuntimeError("Embedding endpoint returned no vectors")
        return [[float(value) for value in vector] for vector in vectors]

    def _request_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {self.api_key}",
            },
            method=method,
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Embedding request failed with HTTP {exc.code}: {details}") from exc
        except URLError as exc:
            raise RuntimeError(f"Could not reach embedding endpoint: {exc}") from exc


class QdrantMemoryIndex:
    def __init__(
        self,
        base_url: str,
        *,
        collection_name: str = "camel_bridge_memory",
        api_key: str | None = None,
        timeout_seconds: int = 15,
        embedder: TextEmbedder | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.collection_name = collection_name
        self.api_key = api_key or os.getenv("CAMEL_MEMORY_QDRANT_API_KEY")
        self.timeout_seconds = timeout_seconds
        self.embedder = embedder or LocalNgramTextEmbedder()
        self._collection_ready = False

    def ensure_collection(self) -> None:
        if self._collection_ready:
            return
        try:
            self._request_json(
                "PUT",
                f"/collections/{self.collection_name}",
                {"vectors": {"size": self.embedder.dimension, "distance": "Cosine"}},
            )
        except RuntimeError as exc:
            details = str(exc)
            if "HTTP 409" not in details or "already exists" not in details:
                raise
        self._collection_ready = True

    def upsert(self, documents: Sequence[MemoryDocument]) -> None:
        if not documents:
            return
        self.ensure_collection()
        vectors = self.embedder.embed([document.summary_text for document in documents])
        points = [
            {"id": document.point_id, "vector": vector, "payload": document.to_payload()}
            for document, vector in zip(documents, vectors)
        ]
        self._request_json("PUT", f"/collections/{self.collection_name}/points", {"points": points})

    def search(self, query_text: str, *, tenant_id: int, world_id: int, limit: int = 5) -> list[MemoryDocument]:
        self.ensure_collection()
        vector = self.embedder.embed([query_text])[0]
        raw = self._request_json(
            "POST",
            f"/collections/{self.collection_name}/points/search",
            {
                "vector": vector,
                "limit": limit,
                "with_payload": True,
                "filter": {
                    "must": [
                        {"key": "tenant_id", "match": {"value": tenant_id}},
                        {"key": "world_id", "match": {"value": world_id}},
                    ]
                },
            },
        )
        result = raw.get("result") or []
        documents: list[MemoryDocument] = []
        for item in result:
            payload = item.get("payload") or {}
            summary = str(payload.get("summary_text") or "").strip()
            if not summary:
                continue
            documents.append(MemoryDocument(
                point_id=str(item.get("id") or payload.get("entity_id") or uuid5(NAMESPACE_URL, summary)),
                tenant_id=int(payload.get("tenant_id") or tenant_id),
                world_id=int(payload.get("world_id") or world_id),
                entity_type=str(payload.get("entity_type") or "memory"),
                entity_id=str(payload.get("entity_id") or payload.get("summary_text") or "memory"),
                summary_text=summary,
                character_names=_normalize_name_list(payload.get("character_names") or ()),
                tags=tuple(str(tag) for tag in payload.get("tags") or [] if str(tag).strip()),
                source=str(payload.get("source") or "camel_bridge"),
            ))
        return documents

    def _request_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
        headers = {"Content-Type": "application/json; charset=utf-8"}
        if self.api_key:
            headers["api-key"] = self.api_key
        request = Request(f"{self.base_url}{path}", data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Qdrant request failed with HTTP {exc.code}: {details}") from exc
        except URLError as exc:
            raise RuntimeError(f"Could not reach Qdrant: {exc}") from exc


class SQLiteLoreMemoryReader:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def load_recent_documents(self, tenant_id: int, world_id: int, *, character_names: Sequence[str] = (), limit_per_type: int = 3) -> list[MemoryDocument]:
        with closing(self._connection()) as conn:
            docs: list[MemoryDocument] = []
            docs.extend(self._character_docs(conn, tenant_id, world_id, character_names, limit_per_type))
            docs.extend(self._simple_docs(conn, tenant_id, world_id, "rumors", "rumor", limit_per_type, "name", "description", extra_fields=("truth_level", "spread_speed")))
            docs.extend(self._simple_docs(conn, tenant_id, world_id, "events", "event", limit_per_type, "name", "description", extra_fields=("outcome",)))
            docs.extend(self._relationship_docs(conn, tenant_id, world_id, limit_per_type))
            docs.extend(self._simple_docs(conn, tenant_id, world_id, "quests", "quest", limit_per_type, "name", "description", extra_fields=("status",)))
            docs.extend(self._character_bound_docs(conn, tenant_id, world_id, "traits", "trait", limit_per_type, character_names, extra_fields=("category", "nature")))
            docs.extend(self._character_bound_docs(conn, tenant_id, world_id, "perks", "perk", limit_per_type, character_names, extra_fields=("perk_type", "source")))
            docs.extend(self._character_bound_docs(conn, tenant_id, world_id, "progression_events", "progression_event", limit_per_type, character_names, extra_fields=("event_type",)))
            return docs

    def load_index_documents(self, tenant_id: int, world_id: int) -> list[MemoryDocument]:
        return self.load_recent_documents(tenant_id, world_id, limit_per_type=12)

    def _connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _table_exists(self, conn: sqlite3.Connection, table_name: str) -> bool:
        row = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?", (table_name,)).fetchone()
        return row is not None

    def _table_columns(self, conn: sqlite3.Connection, table_name: str) -> set[str]:
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        return {str(row[1]) for row in rows}

    def _point_id(self, tenant_id: int, world_id: int, entity_type: str, entity_id: object) -> str:
        return str(uuid5(NAMESPACE_URL, f"{tenant_id}:{world_id}:{entity_type}:{entity_id}"))

    def _character_docs(self, conn: sqlite3.Connection, tenant_id: int, world_id: int, character_names: Sequence[str], limit: int) -> list[MemoryDocument]:
        if not self._table_exists(conn, "characters"):
            return []
        names = _normalize_name_list(character_names)
        if names:
            placeholders = ", ".join("?" for _ in names)
            rows = conn.execute(
                f"SELECT * FROM characters WHERE tenant_id = ? AND world_id = ? AND lower(name) IN ({placeholders}) ORDER BY id DESC LIMIT ?",
                (tenant_id, world_id, *[name.lower() for name in names], limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM characters WHERE tenant_id = ? AND world_id = ? ORDER BY id DESC LIMIT ?",
                (tenant_id, world_id, limit),
            ).fetchall()
        docs: list[MemoryDocument] = []
        for row in rows:
            summary = f"Character: {row['name']} — role={row['role'] or 'unknown'}; backstory: {_trim(row['backstory'], 120)}"
            docs.append(MemoryDocument(
                point_id=self._point_id(tenant_id, world_id, "character", row["id"]),
                tenant_id=tenant_id,
                world_id=world_id,
                entity_type="character",
                entity_id=str(row["id"]),
                summary_text=summary,
                character_names=(str(row["name"]),),
            ))
        return docs

    def _simple_docs(self, conn: sqlite3.Connection, tenant_id: int, world_id: int, table_name: str, entity_type: str, limit: int, title_field: str, body_field: str, *, extra_fields: Sequence[str] = ()) -> list[MemoryDocument]:
        if not self._table_exists(conn, table_name):
            return []
        rows = conn.execute(
            f"SELECT * FROM {table_name} WHERE tenant_id = ? AND world_id = ? ORDER BY id DESC LIMIT ?",
            (tenant_id, world_id, limit),
        ).fetchall()
        docs: list[MemoryDocument] = []
        for row in rows:
            extras = ", ".join(f"{field}={row[field]}" for field in extra_fields if field in row.keys() and row[field] not in (None, ""))
            summary = f"{entity_type.replace('_', ' ').title()}: {row[title_field]} — {_trim(row[body_field], 140)}"
            if extras:
                summary += f" [{extras}]"
            docs.append(MemoryDocument(
                point_id=self._point_id(tenant_id, world_id, entity_type, row["id"]),
                tenant_id=tenant_id,
                world_id=world_id,
                entity_type=entity_type,
                entity_id=str(row["id"]),
                summary_text=summary,
            ))
        return docs

    def _relationship_docs(self, conn: sqlite3.Connection, tenant_id: int, world_id: int, limit: int) -> list[MemoryDocument]:
        if not self._table_exists(conn, "character_relationships") or not self._table_exists(conn, "characters"):
            return []
        rows = conn.execute(
            """
            SELECT cr.*, cf.name AS from_name, ct.name AS to_name
            FROM character_relationships cr
            LEFT JOIN characters cf ON cf.id = cr.character_from_id
            LEFT JOIN characters ct ON ct.id = cr.character_to_id
            WHERE cr.tenant_id = ? AND cr.world_id = ?
            ORDER BY cr.id DESC
            LIMIT ?
            """,
            (tenant_id, world_id, limit),
        ).fetchall()
        return [
            MemoryDocument(
                point_id=self._point_id(tenant_id, world_id, "relationship", row["id"]),
                tenant_id=tenant_id,
                world_id=world_id,
                entity_type="relationship",
                entity_id=str(row["id"]),
                summary_text=f"Relationship: {row['from_name'] or row['character_from_id']} → {row['to_name'] or row['character_to_id']} — {_trim(row['description'], 140)} [type={row['relationship_type']}]",
                character_names=_normalize_name_list((row["from_name"], row["to_name"])),
            )
            for row in rows
        ]

    def _character_bound_docs(self, conn: sqlite3.Connection, tenant_id: int, world_id: int, table_name: str, entity_type: str, limit: int, character_names: Sequence[str], *, extra_fields: Sequence[str] = ()) -> list[MemoryDocument]:
        if not self._table_exists(conn, table_name):
            return []
        names = _normalize_name_list(character_names)
        columns = self._table_columns(conn, table_name)
        if "character_id" not in columns:
            return self._generic_bridge_docs(conn, tenant_id, world_id, table_name, entity_type, limit, names, extra_fields=extra_fields)
        if not self._table_exists(conn, "characters"):
            return []
        base_sql = (
            f"SELECT t.*, c.name AS character_name FROM {table_name} t "
            "LEFT JOIN characters c ON c.id = t.character_id "
            "WHERE t.tenant_id = ? AND t.world_id = ?"
        )
        params: list[object] = [tenant_id, world_id]
        if names:
            placeholders = ", ".join("?" for _ in names)
            base_sql += f" AND lower(c.name) IN ({placeholders})"
            params.extend(name.lower() for name in names)
        base_sql += " ORDER BY t.id DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(base_sql, tuple(params)).fetchall()
        docs: list[MemoryDocument] = []
        for row in rows:
            row_keys = row.keys()
            label = row["name"] if "name" in row_keys else (row["description"] if "description" in row_keys else entity_type.title())
            body = row["description"] if "description" in row.keys() else label
            extras = ", ".join(f"{field}={row[field]}" for field in extra_fields if field in row.keys() and row[field] not in (None, ""))
            summary = f"{entity_type.replace('_', ' ').title()} for {row['character_name'] or row['character_id']}: {label} — {_trim(body, 140)}"
            if extras:
                summary += f" [{extras}]"
            docs.append(MemoryDocument(
                point_id=self._point_id(tenant_id, world_id, entity_type, row["id"]),
                tenant_id=tenant_id,
                world_id=world_id,
                entity_type=entity_type,
                entity_id=str(row["id"]),
                summary_text=summary,
                character_names=_normalize_name_list((row["character_name"],)),
            ))
        return docs

    def _generic_bridge_docs(self, conn: sqlite3.Connection, tenant_id: int, world_id: int, table_name: str, entity_type: str, limit: int, character_names: tuple[str, ...], *, extra_fields: Sequence[str] = ()) -> list[MemoryDocument]:
        rows = conn.execute(
            f"SELECT * FROM {table_name} WHERE tenant_id = ? AND world_id = ? ORDER BY id DESC LIMIT ?",
            (tenant_id, world_id, limit),
        ).fetchall()
        requested = {name.lower() for name in character_names}
        docs: list[MemoryDocument] = []
        for row in rows:
            payload_text = str(row["payload_json"] or "{}").strip()
            try:
                payload = json.loads(payload_text) if payload_text else {}
            except json.JSONDecodeError:
                payload = {}
            related_names = _normalize_name_list(
                tuple(payload.get(key) for key in ("character_name", "character_from_name", "character_to_name") if payload.get(key))
                + tuple(value for value in payload.get("character_names", ()) if value)
                + tuple(value for value in payload.get("participant_names", ()) if value)
            )
            if requested and related_names and not any(name.lower() in requested for name in related_names):
                continue
            label = str(row["label"] or payload.get("name") or payload.get("title") or entity_type.title()).strip()
            body = str(payload.get("description") or label).strip()
            extras = ", ".join(f"{field}={payload.get(field)}" for field in extra_fields if payload.get(field) not in (None, ""))
            subject = ", ".join(related_names) if related_names else "world state"
            summary = f"{entity_type.replace('_', ' ').title()} for {subject}: {label} — {_trim(body, 140)}"
            if extras:
                summary += f" [{extras}]"
            docs.append(MemoryDocument(
                point_id=self._point_id(tenant_id, world_id, entity_type, row["id"]),
                tenant_id=tenant_id,
                world_id=world_id,
                entity_type=entity_type,
                entity_id=str(row["id"]),
                summary_text=summary,
                character_names=related_names,
            ))
        return docs


@dataclass
class LoreMemoryService:
    sqlite_reader: SQLiteLoreMemoryReader
    qdrant_index: QdrantMemoryIndex | None = None
    exact_limit: int = 6
    semantic_limit: int = 4
    indexed_types: tuple[str, ...] = field(default_factory=lambda: ("character", "rumor", "event", "relationship", "quest", "trait", "perk", "progression_event"))

    def build_prompt_context(self, *, tenant_id: int, world_id: int, theme: str, context: str = "", character_names: Sequence[str] = ()) -> str:
        exact_docs = self.sqlite_reader.load_recent_documents(tenant_id, world_id, character_names=character_names)
        exact_docs = [doc for doc in exact_docs if doc.entity_type in self.indexed_types][: self.exact_limit]
        semantic_docs: list[MemoryDocument] = []
        if self.qdrant_index:
            query_text = f"Theme: {theme}\nContext: {context}\nCharacters: {', '.join(character_names)}"
            seen = {(doc.entity_type, doc.entity_id) for doc in exact_docs}
            semantic_docs = [
                doc for doc in self.qdrant_index.search(query_text, tenant_id=tenant_id, world_id=world_id, limit=self.semantic_limit * 2)
                if (doc.entity_type, doc.entity_id) not in seen
            ][: self.semantic_limit]
        if not exact_docs and not semantic_docs:
            return ""
        lines = ["Continuity memory:"]
        if exact_docs:
            lines.append("Known canon from SQLite:")
            lines.extend(f"- {doc.summary_text}" for doc in exact_docs)
        if semantic_docs:
            lines.append("Semantically related recalls from Qdrant:")
            lines.extend(f"- {doc.summary_text}" for doc in semantic_docs)
        lines.append("Use this memory to stay consistent, avoid duplicates, and continue existing lore threads.")
        return "\n".join(lines)

    def index_world_snapshot(self, *, tenant_id: int, world_id: int) -> int:
        if not self.qdrant_index:
            return 0
        docs = [doc for doc in self.sqlite_reader.load_index_documents(tenant_id, world_id) if doc.entity_type in self.indexed_types]
        self.qdrant_index.upsert(docs)
        return len(docs)


def build_memory_service_from_env(db_path: str) -> LoreMemoryService:
    qdrant_url = os.getenv("CAMEL_MEMORY_QDRANT_URL")
    if not qdrant_url:
        raise ValueError("CAMEL_MEMORY_QDRANT_URL is required to enable CAMEL memory")
    backend = (os.getenv("CAMEL_MEMORY_EMBED_BACKEND") or "local").strip().lower()
    if backend == "openai":
        embedder: TextEmbedder = OpenAICompatibleTextEmbedder()
    elif backend == "hash":
        embedder = HashingTextEmbedder(dimension=int(os.getenv("CAMEL_MEMORY_EMBED_DIMENSION", "96")))
    elif backend in {"local", "ngram", "hybrid"}:
        embedder = LocalNgramTextEmbedder(dimension=int(os.getenv("CAMEL_MEMORY_EMBED_DIMENSION", "384")))
    else:
        raise ValueError(f"Unsupported CAMEL_MEMORY_EMBED_BACKEND: {backend}")
    return LoreMemoryService(
        sqlite_reader=SQLiteLoreMemoryReader(db_path),
        qdrant_index=QdrantMemoryIndex(
            qdrant_url,
            collection_name=os.getenv("CAMEL_MEMORY_QDRANT_COLLECTION") or "camel_bridge_memory",
            timeout_seconds=int(os.getenv("CAMEL_MEMORY_QDRANT_TIMEOUT_SECONDS", "15")),
            embedder=embedder,
        ),
    )