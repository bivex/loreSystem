"""SQLite-backed storage for MiroFish write-back pipeline artifacts."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.application.integration.dto import CandidateDelta, MiroFishResultBundle, RuntimeEvidenceRecord


class _SQLiteConnectionProvider:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


class MiroFishWriteBackStore:
    def __init__(self, db: str | Path | Any = "lore_system.db"):
        self.db = db if hasattr(db, "get_connection") else _SQLiteConnectionProvider(str(db))
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self.db.get_connection() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS mirofish_scenario_runs (run_id TEXT PRIMARY KEY, world_id TEXT NOT NULL, scenario_id TEXT NOT NULL, schema_version TEXT NOT NULL, world_version TEXT, projection_version TEXT, generated_at TEXT NOT NULL, source_backend TEXT NOT NULL, imported_at TEXT NOT NULL)")
            conn.execute("CREATE TABLE IF NOT EXISTS mirofish_scenario_results (run_id TEXT PRIMARY KEY, bundle_json TEXT NOT NULL, FOREIGN KEY (run_id) REFERENCES mirofish_scenario_runs(run_id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS mirofish_runtime_evidence (evidence_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, world_id TEXT NOT NULL, scenario_id TEXT NOT NULL, evidence_type TEXT NOT NULL, source_type TEXT NOT NULL, actor_refs_json TEXT NOT NULL, canonical_refs_json TEXT NOT NULL, text TEXT, structured_payload_json TEXT NOT NULL, timestamp TEXT NOT NULL, confidence REAL NOT NULL, source_refs_json TEXT NOT NULL, FOREIGN KEY (run_id) REFERENCES mirofish_scenario_runs(run_id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS mirofish_candidate_deltas (candidate_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, world_id TEXT NOT NULL, scenario_id TEXT NOT NULL, candidate_type TEXT NOT NULL, target_canonical_type TEXT, target_canonical_id TEXT, proposed_entity_type TEXT, name TEXT NOT NULL, summary TEXT, proposed_change_json TEXT NOT NULL, evidence_ids_json TEXT NOT NULL, source_refs_json TEXT NOT NULL, confidence REAL NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL, FOREIGN KEY (run_id) REFERENCES mirofish_scenario_runs(run_id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS mirofish_canonical_entities (canonical_id INTEGER PRIMARY KEY AUTOINCREMENT, source_candidate_id TEXT UNIQUE NOT NULL, canonical_type TEXT NOT NULL, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, entity_json TEXT NOT NULL, promoted_at TEXT NOT NULL, FOREIGN KEY (source_candidate_id) REFERENCES mirofish_candidate_deltas(candidate_id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS mirofish_entity_run_links (link_id INTEGER PRIMARY KEY AUTOINCREMENT, canonical_id INTEGER NOT NULL, canonical_type TEXT NOT NULL, run_id TEXT NOT NULL, source_candidate_id TEXT, relation_type TEXT NOT NULL, evidence_ids_json TEXT NOT NULL, metadata_json TEXT NOT NULL, linked_at TEXT NOT NULL, FOREIGN KEY (canonical_id) REFERENCES mirofish_canonical_entities(canonical_id) ON DELETE CASCADE, FOREIGN KEY (run_id) REFERENCES mirofish_scenario_runs(run_id) ON DELETE CASCADE)")

    def save_import(self, bundle: MiroFishResultBundle, evidence: list[RuntimeEvidenceRecord], candidates: list[CandidateDelta]) -> dict[str, Any]:
        with self.db.get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO mirofish_scenario_runs (run_id, world_id, scenario_id, schema_version, world_version, projection_version, generated_at, source_backend, imported_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (bundle.run_id, bundle.world_id, bundle.scenario_id, bundle.schema_version, bundle.world_version, bundle.projection_version, bundle.generated_at, bundle.source_backend, bundle.generated_at),
            )
            conn.execute(
                "INSERT OR REPLACE INTO mirofish_scenario_results (run_id, bundle_json) VALUES (?, ?)",
                (bundle.run_id, json.dumps(bundle.raw_payload, ensure_ascii=False)),
            )
            conn.execute("DELETE FROM mirofish_runtime_evidence WHERE run_id = ?", (bundle.run_id,))
            conn.execute("DELETE FROM mirofish_candidate_deltas WHERE run_id = ?", (bundle.run_id,))
            for item in evidence:
                conn.execute(
                    "INSERT INTO mirofish_runtime_evidence (evidence_id, run_id, world_id, scenario_id, evidence_type, source_type, actor_refs_json, canonical_refs_json, text, structured_payload_json, timestamp, confidence, source_refs_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (item.evidence_id, item.run_id, item.world_id, item.scenario_id, item.evidence_type, item.source_type, json.dumps(item.actor_refs, ensure_ascii=False), json.dumps(item.canonical_refs, ensure_ascii=False), item.text, json.dumps(item.structured_payload, ensure_ascii=False), item.timestamp, item.confidence, json.dumps(item.source_refs, ensure_ascii=False)),
                )
            for item in candidates:
                conn.execute(
                    "INSERT INTO mirofish_candidate_deltas (candidate_id, run_id, world_id, scenario_id, candidate_type, target_canonical_type, target_canonical_id, proposed_entity_type, name, summary, proposed_change_json, evidence_ids_json, source_refs_json, confidence, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (item.candidate_id, item.run_id, item.world_id, item.scenario_id, item.candidate_type, item.target_canonical_type, item.target_canonical_id, item.proposed_entity_type, item.name, item.summary, json.dumps(item.proposed_change, ensure_ascii=False), json.dumps(item.evidence_ids, ensure_ascii=False), json.dumps(item.source_refs, ensure_ascii=False), item.confidence, item.status, item.created_at),
                )
        return {"run_id": bundle.run_id, "world_id": bundle.world_id, "scenario_id": bundle.scenario_id, "runtime_evidence_saved": len(evidence), "candidate_deltas_saved": len(candidates)}

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM mirofish_scenario_runs WHERE run_id = ?", (run_id,)).fetchone()
            result_row = conn.execute("SELECT bundle_json FROM mirofish_scenario_results WHERE run_id = ?", (run_id,)).fetchone()
        if not row:
            return None
        payload = dict(row)
        payload["bundle"] = json.loads(result_row["bundle_json"]) if result_row else None
        return payload

    def list_evidence(self, run_id: str) -> list[dict[str, Any]]:
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM mirofish_runtime_evidence WHERE run_id = ? ORDER BY timestamp, evidence_id", (run_id,)).fetchall()
        return [self._decode_evidence_row(dict(row)) for row in rows]

    def list_candidates(self, *, world_id: str | None = None, status: str | None = None, candidate_type: str | None = None) -> list[dict[str, Any]]:
        clauses = []
        params: list[Any] = []
        if world_id:
            clauses.append("world_id = ?")
            params.append(world_id)
        if status:
            clauses.append("status = ?")
            params.append(status)
        if candidate_type:
            clauses.append("candidate_type = ?")
            params.append(candidate_type)
        query = "SELECT * FROM mirofish_candidate_deltas"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY created_at, candidate_id"
        with self.db.get_connection() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
        return [self._decode_candidate_row(dict(row)) for row in rows]

    def get_candidate(self, candidate_id: str) -> dict[str, Any] | None:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM mirofish_candidate_deltas WHERE candidate_id = ?", (candidate_id,)).fetchone()
        if not row:
            return None
        return self._decode_candidate_row(dict(row))

    def update_candidate_status(self, candidate_id: str, status: str) -> dict[str, Any] | None:
        with self.db.get_connection() as conn:
            updated = conn.execute(
                "UPDATE mirofish_candidate_deltas SET status = ? WHERE candidate_id = ?",
                (status, candidate_id),
            )
            if updated.rowcount == 0:
                return None
            row = conn.execute("SELECT * FROM mirofish_candidate_deltas WHERE candidate_id = ?", (candidate_id,)).fetchone()
        if not row:
            return None
        return self._decode_candidate_row(dict(row))

    def mark_candidate_promoted(self, candidate_id: str, *, canonical_type: str, canonical_id: int) -> dict[str, Any] | None:
        with self.db.get_connection() as conn:
            updated = conn.execute(
                "UPDATE mirofish_candidate_deltas SET status = ?, target_canonical_type = ?, target_canonical_id = ? WHERE candidate_id = ?",
                ("promoted", canonical_type, str(canonical_id), candidate_id),
            )
            if updated.rowcount == 0:
                return None
            row = conn.execute("SELECT * FROM mirofish_candidate_deltas WHERE candidate_id = ?", (candidate_id,)).fetchone()
        if not row:
            return None
        return self._decode_candidate_row(dict(row))

    def save_canonical_entity(
        self,
        *,
        source_candidate_id: str,
        canonical_type: str,
        tenant_id: int,
        world_id: int,
        entity_payload: dict[str, Any],
    ) -> dict[str, Any]:
        promoted_at = datetime.now(timezone.utc).isoformat()
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO mirofish_canonical_entities (source_candidate_id, canonical_type, tenant_id, world_id, entity_json, promoted_at) VALUES (?, ?, ?, ?, ?, ?)",
                (source_candidate_id, canonical_type, tenant_id, world_id, "{}", promoted_at),
            )
            canonical_id = int(cursor.lastrowid)
            entity_payload = {**entity_payload, "id": canonical_id}
            conn.execute(
                "UPDATE mirofish_canonical_entities SET entity_json = ? WHERE canonical_id = ?",
                (json.dumps(entity_payload, ensure_ascii=False), canonical_id),
            )
        return {
            "canonical_id": canonical_id,
            "source_candidate_id": source_candidate_id,
            "canonical_type": canonical_type,
            "tenant_id": tenant_id,
            "world_id": world_id,
            "entity": entity_payload,
            "promoted_at": promoted_at,
        }

    def get_canonical_entity_by_candidate(self, candidate_id: str) -> dict[str, Any] | None:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM mirofish_canonical_entities WHERE source_candidate_id = ?", (candidate_id,)).fetchone()
        if not row:
            return None
        payload = dict(row)
        payload["entity"] = json.loads(payload.pop("entity_json"))
        payload["run_links"] = self.list_entity_run_links(canonical_id=payload["canonical_id"])
        return payload

    def save_entity_run_link(
        self,
        *,
        canonical_id: int,
        canonical_type: str,
        run_id: str,
        source_candidate_id: str | None,
        relation_type: str = "promoted_from",
        evidence_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        linked_at = datetime.now(timezone.utc).isoformat()
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO mirofish_entity_run_links (canonical_id, canonical_type, run_id, source_candidate_id, relation_type, evidence_ids_json, metadata_json, linked_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (canonical_id, canonical_type, run_id, source_candidate_id, relation_type, json.dumps(evidence_ids or [], ensure_ascii=False), json.dumps(metadata or {}, ensure_ascii=False), linked_at),
            )
            link_id = int(cursor.lastrowid)
        return {
            "link_id": link_id,
            "canonical_id": canonical_id,
            "canonical_type": canonical_type,
            "run_id": run_id,
            "source_candidate_id": source_candidate_id,
            "relation_type": relation_type,
            "evidence_ids": list(evidence_ids or []),
            "metadata": dict(metadata or {}),
            "linked_at": linked_at,
        }

    def list_entity_run_links(
        self,
        *,
        canonical_id: int | None = None,
        run_id: str | None = None,
        source_candidate_id: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses = []
        params: list[Any] = []
        if canonical_id is not None:
            clauses.append("canonical_id = ?")
            params.append(canonical_id)
        if run_id is not None:
            clauses.append("run_id = ?")
            params.append(run_id)
        if source_candidate_id is not None:
            clauses.append("source_candidate_id = ?")
            params.append(source_candidate_id)
        query = "SELECT * FROM mirofish_entity_run_links"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY linked_at, link_id"
        with self.db.get_connection() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
        return [self._decode_entity_run_link_row(dict(row)) for row in rows]

    def _decode_evidence_row(self, row: dict[str, Any]) -> dict[str, Any]:
        row["actor_refs"] = json.loads(row.pop("actor_refs_json"))
        row["canonical_refs"] = json.loads(row.pop("canonical_refs_json"))
        row["structured_payload"] = json.loads(row.pop("structured_payload_json"))
        row["source_refs"] = json.loads(row.pop("source_refs_json"))
        return row

    def _decode_candidate_row(self, row: dict[str, Any]) -> dict[str, Any]:
        row["proposed_change"] = json.loads(row.pop("proposed_change_json"))
        row["evidence_ids"] = json.loads(row.pop("evidence_ids_json"))
        row["source_refs"] = json.loads(row.pop("source_refs_json"))
        return row

    def _decode_entity_run_link_row(self, row: dict[str, Any]) -> dict[str, Any]:
        row["evidence_ids"] = json.loads(row.pop("evidence_ids_json"))
        row["metadata"] = json.loads(row.pop("metadata_json"))
        return row