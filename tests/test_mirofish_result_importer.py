import json

from src.application.integration.importers import MiroFishResultImporter
from src.infrastructure.mirofish_writeback_store import MiroFishWriteBackStore


def sample_result_bundle() -> dict:
    return {
        "schema_version": "1.1",
        "world_id": "world-1",
        "scenario_id": "succession-crisis",
        "run_id": "run-123",
        "generated_at": "2026-03-10T12:00:00Z",
        "prediction_summary": {
            "summary": "A forged decree rumor destabilizes trust in the court.",
            "rumors": [
                {"name": "Forged decree rumor", "summary": "Town criers amplify doubts about the royal seal.", "confidence": 0.74}
            ],
        },
        "emergent_events": [
            {"name": "Court issues denial", "description": "The Royal Court publicly denies the forgery.", "participant_ids": ["actor:royal_court"], "confidence": 0.81}
        ],
        "relationship_changes": [
            {"name": "Captain Serik distrusts Nessa", "summary": "Trust drops after the rumor spike.", "confidence": 0.67}
        ],
    }


def test_importer_persists_run_evidence_and_candidates(tmp_path):
    db_path = tmp_path / "mirofish.db"
    importer = MiroFishResultImporter(MiroFishWriteBackStore(db_path))

    result = importer.import_result_bundle(sample_result_bundle())

    assert result["run_id"] == "run-123"
    assert result["derived_runtime_evidence"] is True
    assert result["derived_candidate_deltas"] is True
    assert result["runtime_evidence_saved"] == 4
    assert result["candidate_deltas_saved"] == 3

    store = MiroFishWriteBackStore(db_path)
    saved_run = store.get_run("run-123")
    saved_evidence = store.list_evidence("run-123")
    saved_candidates = store.list_candidates(world_id="world-1")

    assert saved_run is not None
    assert saved_run["scenario_id"] == "succession-crisis"
    assert saved_run["bundle"]["prediction_summary"]["summary"].startswith("A forged decree rumor")
    assert any(item["evidence_type"] == "world_event" for item in saved_evidence)
    assert any(item["evidence_type"] == "relationship_change" for item in saved_evidence)
    assert any(item["candidate_type"] == "scenario_event" for item in saved_candidates)
    assert any(item["candidate_type"] == "relationship_change" for item in saved_candidates)
    assert any(item["candidate_type"] == "rumor_candidate" for item in saved_candidates)


def test_importer_keeps_explicit_runtime_evidence_and_candidate_deltas(tmp_path):
    db_path = tmp_path / "explicit.db"
    importer = MiroFishResultImporter(MiroFishWriteBackStore(db_path))
    payload = sample_result_bundle()
    payload["runtime_evidence"] = [{
        "evidence_id": "ev-1",
        "evidence_type": "post",
        "source_type": "runtime_action",
        "text": "Captain Aria publicly breaks with the Harbor Guild.",
        "timestamp": "2026-03-10T12:05:00Z",
        "confidence": 0.9,
    }]
    payload["candidate_deltas"] = [{
        "candidate_id": "cand-1",
        "candidate_type": "scenario_event",
        "target_canonical_type": "Event",
        "name": "Harbor split",
        "summary": "Aria breaks with the guild.",
        "evidence_ids": ["ev-1"],
        "confidence": 0.88,
    }]

    result = importer.import_result_bundle(payload)
    store = MiroFishWriteBackStore(db_path)
    evidence = store.list_evidence("run-123")
    candidates = store.list_candidates(world_id="world-1")

    assert result["derived_runtime_evidence"] is False
    assert result["derived_candidate_deltas"] is False
    assert len(evidence) == 1
    assert evidence[0]["text"] == "Captain Aria publicly breaks with the Harbor Guild."
    assert len(candidates) == 1
    assert candidates[0]["candidate_id"] == "cand-1"
    assert candidates[0]["evidence_ids"] == ["ev-1"]


def test_import_cli_round_trip(tmp_path):
    input_path = tmp_path / "result_bundle.json"
    db_path = tmp_path / "cli.db"
    input_path.write_text(json.dumps(sample_result_bundle(), ensure_ascii=False), encoding="utf-8")

    from scripts.import_mirofish_results import main

    import sys
    argv_before = sys.argv
    sys.argv = ["import_mirofish_results.py", "--input", str(input_path), "--db", str(db_path)]
    try:
        assert main() == 0
    finally:
        sys.argv = argv_before

    store = MiroFishWriteBackStore(db_path)
    assert store.get_run("run-123") is not None