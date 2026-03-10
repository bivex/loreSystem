"""Run a full multi-entity smoke for the MiroFish write-back review/promote workflow."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path

from wsgiref.simple_server import make_server

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.presentation.api import create_writeback_app


def sample_result_bundle() -> dict:
    return {
        "schema_version": "1.1",
        "world_id": "world-1",
        "scenario_id": "succession-crisis",
        "run_id": "run-full-smoke",
        "generated_at": "2026-03-10T12:00:00Z",
        "actors": [
            {"id": "actor:royal_court", "name": "Royal Court Herald", "canonical_id": "char-royal-court-herald", "canonical_type": "Character", "speaker_mode": "representative", "represented_entity_id": "org:royal_court"},
            {"id": "actor:captain_serik", "name": "Captain Serik", "canonical_id": "char-serik", "canonical_type": "Character", "speaker_mode": "individual"},
            {"id": "actor:nessa", "name": "Nessa", "canonical_id": "char-nessa", "canonical_type": "Character", "speaker_mode": "individual"},
        ],
        "organizations": [
            {"id": "org:royal_court", "name": "The Royal Court", "canonical_id": "faction-royal-court", "canonical_type": "Faction", "speaker_mode": "official_account"},
            {"id": "org:town_criers", "name": "Town Criers", "canonical_id": "faction-town-criers", "canonical_type": "Faction", "speaker_mode": "official_account"},
        ],
        "prediction_summary": {
            "summary": "A forged decree rumor destabilizes trust in the court.",
            "rumors": [{"name": "Forged decree rumor", "summary": "Town criers amplify doubts.", "actor_refs": ["org:town_criers"], "confidence": 0.74}],
        },
        "emergent_events": [{"name": "Court issues denial", "description": "The Royal Court publicly denies the forgery.", "participant_ids": ["actor:royal_court", "org:royal_court"], "confidence": 0.81}],
        "relationship_changes": [{"name": "Captain Serik distrusts Nessa", "summary": "Trust drops after the rumor spike.", "actor_refs": ["actor:captain_serik", "actor:nessa"], "confidence": 0.67}],
    }


def request_json(base_url: str, method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {} if payload is None else {"Content-Type": "application/json"}
    req = urllib.request.Request(f"{base_url}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8") or "{}"
        return exc.code, json.loads(body)


def assert_ok(status: int, payload: dict, step: str) -> None:
    if status != 200 or payload.get("success") is not True:
        raise RuntimeError(f"{step} failed: status={status}, payload={json.dumps(payload, ensure_ascii=False)}")


@contextmanager
def local_server(host: str, port: int, db_path: str):
    server = make_server(host, port, create_writeback_app(db_path=db_path))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://{host}:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def wait_until_ready(base_url: str) -> None:
    last_error: Exception | None = None
    for _ in range(20):
        try:
            status, payload = request_json(base_url, "GET", "/api/mirofish/writeback/candidate-deltas")
            if status == 200 and payload.get("success") is True:
                return
        except Exception as exc:  # pragma: no cover - defensive retry
            last_error = exc
        time.sleep(0.25)
    raise RuntimeError(f"Write-back API did not become ready: {last_error}")


def inspect_db(db_path: str) -> dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    canonical_rows = [dict(row) for row in conn.execute("SELECT canonical_id, source_candidate_id, canonical_type, tenant_id, world_id FROM mirofish_canonical_entities ORDER BY canonical_id").fetchall()]
    promoted_rows = [dict(row) for row in conn.execute("SELECT candidate_id, candidate_type, status, target_canonical_type, target_canonical_id FROM mirofish_candidate_deltas WHERE status = 'promoted' ORDER BY candidate_type").fetchall()]
    subject_rows = [dict(row) for row in conn.execute("SELECT subject_row_id, run_id, subject_kind, subject_ref, name, canonical_id, canonical_type, speaker_mode, represented_entity_id FROM mirofish_run_subjects ORDER BY subject_kind, subject_ref").fetchall()]
    conn.close()
    return {"canonical_rows": canonical_rows, "promoted_rows": promoted_rows, "subject_rows": subject_rows}


def summarize_db(db_path: str) -> dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    counts = {
        "scenario_runs": conn.execute("SELECT COUNT(*) FROM mirofish_scenario_runs").fetchone()[0],
        "runtime_evidence": conn.execute("SELECT COUNT(*) FROM mirofish_runtime_evidence").fetchone()[0],
        "candidate_deltas": conn.execute("SELECT COUNT(*) FROM mirofish_candidate_deltas").fetchone()[0],
        "run_subjects": conn.execute("SELECT COUNT(*) FROM mirofish_run_subjects").fetchone()[0],
        "canonical_entities": conn.execute("SELECT COUNT(*) FROM mirofish_canonical_entities").fetchone()[0],
        "entity_run_links": conn.execute("SELECT COUNT(*) FROM mirofish_entity_run_links").fetchone()[0],
    }
    subjects = [
        dict(row)
        for row in conn.execute(
            "SELECT subject_kind, subject_ref, name, canonical_id, canonical_type, speaker_mode, represented_entity_id FROM mirofish_run_subjects ORDER BY subject_kind, subject_ref"
        ).fetchall()
    ]
    run_links = [
        dict(row)
        for row in conn.execute(
            "SELECT run_id, canonical_type, source_candidate_id, relation_type FROM mirofish_entity_run_links ORDER BY link_id"
        ).fetchall()
    ]
    conn.close()
    return {"db_path": db_path, "counts": counts, "subjects": subjects, "run_links": run_links}


def run_smoke(base_url: str, db_path: str) -> dict:
    ingest_status, ingest_payload = request_json(base_url, "POST", "/api/mirofish/writeback/ingest", sample_result_bundle())
    assert_ok(ingest_status, ingest_payload, "ingest")

    run_status, run_payload = request_json(base_url, "GET", f"/api/mirofish/writeback/runs/{ingest_payload['data']['run_id']}")
    assert_ok(run_status, run_payload, "get run detail")
    evidence_status, evidence_payload = request_json(base_url, "GET", f"/api/mirofish/writeback/runs/{ingest_payload['data']['run_id']}/evidence")
    assert_ok(evidence_status, evidence_payload, "get run evidence")

    list_status, list_payload = request_json(base_url, "GET", "/api/mirofish/writeback/candidate-deltas")
    assert_ok(list_status, list_payload, "list candidates")
    candidates = {item["candidate_type"]: item for item in list_payload["data"]["candidates"]}

    mappings = {
        "scenario_event": {"tenant_id": 1, "world_id": 101, "participant_map": {"actor:royal_court": 201}, "outcome": "success", "location_id": 301},
        "rumor_candidate": {"tenant_id": 1, "world_id": 101, "location_id": 301, "source_name": "Town criers", "credibility_score": 7, "spread_speed": "Rapid", "truth_level": "Plausible"},
        "relationship_change": {"tenant_id": 1, "world_id": 101, "character_from_id": 201, "character_to_id": 202, "relationship_level": -35, "is_mutual": False},
    }

    approvals: list[dict] = []
    promotions: list[dict] = []
    for candidate_type, mapping in mappings.items():
        candidate_id = candidates[candidate_type]["candidate_id"]
        approve_status, approve_payload = request_json(base_url, "POST", f"/api/mirofish/writeback/candidate-deltas/{candidate_id}/approve")
        assert_ok(approve_status, approve_payload, f"approve {candidate_type}")
        approvals.append({"candidate_type": candidate_type, "candidate_id": candidate_id, "status": approve_payload["data"]["candidate"]["status"]})

        promote_status, promote_payload = request_json(base_url, "POST", f"/api/mirofish/writeback/candidate-deltas/{candidate_id}/promote", mapping)
        assert_ok(promote_status, promote_payload, f"promote {candidate_type}")
        promotions.append({
            "candidate_type": candidate_type,
            "candidate_id": candidate_id,
            "status": promote_payload["data"]["candidate"]["status"],
            "canonical_type": promote_payload["data"]["canonical_entity"]["canonical_type"],
            "canonical_id": promote_payload["data"]["canonical_entity"]["canonical_id"],
        })

    promoted_status, promoted_payload = request_json(base_url, "GET", "/api/mirofish/writeback/candidate-deltas?status=promoted")
    assert_ok(promoted_status, promoted_payload, "list promoted candidates")
    db_state = inspect_db(db_path)
    if promoted_payload["data"]["count"] != 3 or len(db_state["canonical_rows"]) != 3:
        raise RuntimeError("Expected exactly 3 promoted candidates and 3 canonical rows")
    if len(db_state["subject_rows"]) != 5:
        raise RuntimeError("Expected exactly 5 persisted run subjects")
    if run_payload["data"]["subjects"]["count"] != 5:
        raise RuntimeError("Expected run detail to expose 5 normalized subjects")
    if not any(any(subject["subject_ref"] == "org:town_criers" for subject in item["linked_subjects"]) for item in evidence_payload["data"]["evidence"]):
        raise RuntimeError("Expected evidence to be linked to persisted subject rows")

    return {
        "success": True,
        "base_url": base_url,
        "db_path": db_path,
        "run_id": ingest_payload["data"]["run_id"],
        "candidate_count": list_payload["data"]["count"],
        "promoted_count": promoted_payload["data"]["count"],
        "subjects_count": run_payload["data"]["subjects"]["count"],
        "approvals": approvals,
        "promotions": promotions,
        "canonical_types": [row["canonical_type"] for row in db_state["canonical_rows"]],
        "db_state": db_state,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", help="Use an already running write-back API instead of starting a local server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host for an auto-started local server")
    parser.add_argument("--port", default=0, type=int, help="Bind port for an auto-started local server (0 = ephemeral)")
    parser.add_argument("--db", help="SQLite database path. Auto-created temp DB when omitted in local mode")
    parser.add_argument("--keep-db", action="store_true", help="Keep the auto-created temp DB after the smoke run")
    args = parser.parse_args()

    auto_db = False
    db_path = args.db
    if not db_path:
        if args.base_url:
            parser.error("--db is required when using --base-url")
        fd, db_path = tempfile.mkstemp(prefix="mirofish_writeback_smoke_", suffix=".db")
        os.close(fd)
        auto_db = True

    try:
        if args.base_url:
            wait_until_ready(args.base_url.rstrip("/"))
            result = run_smoke(args.base_url.rstrip("/"), db_path)
        else:
            with local_server(args.host, args.port, db_path) as base_url:
                wait_until_ready(base_url)
                result = run_smoke(base_url, db_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"success": False, "error": str(exc), "db_path": db_path}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    finally:
        if auto_db and not args.keep_db and db_path and os.path.exists(db_path):
            os.remove(db_path)


if __name__ == "__main__":
    raise SystemExit(main())