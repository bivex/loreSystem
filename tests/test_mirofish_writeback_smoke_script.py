import json
import subprocess
import sys

from src.application.integration.importers import MiroFishResultImporter
from src.infrastructure.mirofish_writeback_store import MiroFishWriteBackStore


def sample_result_bundle() -> dict:
    return {
        "schema_version": "1.1",
        "world_id": "world-1",
        "scenario_id": "succession-crisis",
        "run_id": "run-123",
        "generated_at": "2026-03-10T12:00:00Z",
        "prediction_summary": {"summary": "A forged decree rumor destabilizes trust in the court.", "rumors": [{"name": "Forged decree rumor", "summary": "Town criers amplify doubts.", "actor_refs": ["org:town_criers"], "confidence": 0.74}]},
        "emergent_events": [{"name": "Court issues denial", "description": "The Royal Court publicly denies the forgery.", "participant_ids": ["actor:royal_court", "org:royal_court"], "confidence": 0.81}],
        "relationship_changes": [{"name": "Captain Serik distrusts Nessa", "summary": "Trust drops after the rumor spike.", "actor_refs": ["actor:captain_serik", "actor:nessa"], "confidence": 0.67}],
    }


def test_smoke_script_runs_full_review_promote_flow(tmp_path):
    db_path = tmp_path / "smoke.db"
    result = subprocess.run(
        [sys.executable, "scripts/smoke_mirofish_writeback_workflow.py", "--db", str(db_path), "--keep-db"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert payload["candidate_count"] == 3
    assert payload["promoted_count"] == 3
    assert payload["subjects_count"] == 5
    assert sorted(payload["canonical_types"]) == ["CharacterRelationship", "Event", "Rumor"]
    assert len(payload["db_state"]["subject_rows"]) == 5
    assert any(item["subject_ref"] == "org:town_criers" for item in payload["db_state"]["subject_rows"])
    assert sorted(item["status"] for item in payload["promotions"]) == ["promoted", "promoted", "promoted"]


def test_list_candidates_script_lists_and_filters_candidates(tmp_path):
    db_path = tmp_path / "list-candidates.db"
    importer = MiroFishResultImporter(MiroFishWriteBackStore(db_path))
    importer.import_result_bundle(sample_result_bundle())

    result = subprocess.run(
        [sys.executable, "scripts/list_mirofish_candidates.py", "--db", str(db_path), "--candidate-type", "scenario_event"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["count"] == 1
    assert payload["candidates"][0]["candidate_type"] == "scenario_event"
    assert payload["candidates"][0]["run_id"] == "run-123"
    assert payload["candidates"][0]["evidence_count"] == 1