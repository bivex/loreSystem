import json

from src.application.integration.importers import MiroFishResultImporter
from src.application.integration.promoters import MiroFishCandidatePromoter
from src.infrastructure.mirofish_writeback_store import MiroFishWriteBackStore


def sample_result_bundle() -> dict:
    return {
        "schema_version": "1.1",
        "world_id": "world-1",
        "scenario_id": "succession-crisis",
        "run_id": "run-123",
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
            "rumors": [
                {"name": "Forged decree rumor", "summary": "Town criers amplify doubts about the royal seal.", "actor_refs": ["org:town_criers"], "confidence": 0.74}
            ],
        },
        "emergent_events": [
            {"name": "Court issues denial", "description": "The Royal Court publicly denies the forgery.", "participant_ids": ["actor:royal_court", "org:royal_court"], "confidence": 0.81}
        ],
        "relationship_changes": [
            {"name": "Captain Serik distrusts Nessa", "summary": "Trust drops after the rumor spike.", "actor_refs": ["actor:captain_serik", "actor:nessa"], "confidence": 0.67}
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
    assert result["actors_saved"] == 3
    assert result["organizations_saved"] == 2
    assert result["subjects_saved"] == 5

    store = MiroFishWriteBackStore(db_path)
    saved_run = store.get_run("run-123")
    saved_evidence = store.list_evidence("run-123")
    saved_candidates = store.list_candidates(world_id="world-1")
    saved_subjects = store.list_run_subjects(run_id="run-123")

    assert saved_run is not None
    assert saved_run["scenario_id"] == "succession-crisis"
    assert saved_run["bundle"]["prediction_summary"]["summary"].startswith("A forged decree rumor")
    assert saved_run["subjects"]["count"] == 5
    assert len(saved_run["subjects"]["actors"]) == 3
    assert len(saved_run["subjects"]["organizations"]) == 2
    assert any(item["subject_ref"] == "org:town_criers" for item in saved_subjects)
    assert any(item["evidence_type"] == "world_event" for item in saved_evidence)
    assert any(item["evidence_type"] == "relationship_change" for item in saved_evidence)
    assert any(any(subject["subject_ref"] == "org:town_criers" for subject in item["linked_subjects"]) for item in saved_evidence)
    assert any(any(subject["subject_ref"] == "actor:captain_serik" for subject in item["linked_subjects"]) for item in saved_evidence)
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
        "actor_refs": ["actor:captain_serik", "org:town_criers"],
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
    assert sorted(item["subject_ref"] for item in evidence[0]["linked_subjects"]) == ["actor:captain_serik", "org:town_criers"]
    assert len(candidates) == 1
    assert candidates[0]["candidate_id"] == "cand-1"
    assert candidates[0]["evidence_ids"] == ["ev-1"]


def test_store_get_run_includes_persisted_entity_run_links_after_promotion(tmp_path):
    db_path = tmp_path / "run-links.db"
    store = MiroFishWriteBackStore(db_path)
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(sample_result_bundle())
    candidate = store.list_candidates(world_id="world-1", candidate_type="scenario_event")[0]
    approved = store.update_candidate_status(candidate["candidate_id"], "approved")

    result = promoter.promote_candidate(
        approved["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201},
            "outcome": "success",
        },
    )

    saved_run = store.get_run("run-123")

    assert saved_run is not None
    assert len(saved_run["entity_run_links"]) == 1
    assert saved_run["entity_run_links"][0]["canonical_id"] == result["canonical_entity"]["canonical_id"]
    assert saved_run["entity_run_links"][0]["run_id"] == "run-123"
    assert saved_run["entity_run_links"][0]["source_candidate_id"] == approved["candidate_id"]
    assert saved_run["entity_run_links"][0]["relation_type"] == "promoted_from"
    assert saved_run["entity_run_links"][0]["evidence_ids"] == approved["evidence_ids"]
    assert saved_run["entity_run_links"][0]["metadata"]["candidate_type"] == "scenario_event"


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