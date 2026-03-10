from src.application.integration.importers import MiroFishResultImporter
from src.application.integration.promoters import MiroFishCandidatePromoter
from src.infrastructure.mirofish_writeback_store import MiroFishWriteBackStore


def sample_result_bundle(*, run_id: str = "run-123", generated_at: str = "2026-03-10T12:00:00Z", event_name: str = "Court issues denial") -> dict:
    return {
        "schema_version": "1.1",
        "world_id": "world-1",
        "scenario_id": "succession-crisis",
        "run_id": run_id,
        "generated_at": generated_at,
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
            {"name": event_name, "description": "The Royal Court publicly denies the forgery.", "participant_ids": ["actor:royal_court", "org:royal_court"], "confidence": 0.81}
        ],
        "relationship_changes": [
            {"name": "Captain Serik distrusts Nessa", "summary": "Trust drops after the rumor spike.", "actor_refs": ["actor:captain_serik", "actor:nessa"], "confidence": 0.67}
        ],
    }


def _approve_candidate(store: MiroFishWriteBackStore, *, candidate_type: str, run_id: str = "run-123") -> dict:
    candidate = [
        item
        for item in store.list_candidates(world_id="world-1", candidate_type=candidate_type)
        if item["run_id"] == run_id
    ][0]
    return store.update_candidate_status(candidate["candidate_id"], "approved")


def test_promoter_maps_approved_event_candidate(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "event.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(sample_result_bundle())
    approved = _approve_candidate(store, candidate_type="scenario_event")

    result = promoter.promote_candidate(
        approved["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201},
            "outcome": "success",
            "location_id": 301,
        },
    )

    assert result["canonical_entity"]["canonical_type"] == "Event"
    assert result["canonical_entity"]["entity"]["world_id"] == 101
    assert result["canonical_entity"]["entity"]["participant_ids"] == [201]
    assert result["run_link"]["run_id"] == "run-123"
    assert result["canonical_entity"]["run_links"][0]["relation_type"] == "promoted_from"
    assert result["candidate"]["status"] == "promoted"
    persisted = store.get_canonical_entity_by_candidate(approved["candidate_id"])
    assert persisted is not None
    assert persisted["run_links"][0]["run_id"] == "run-123"
    assert persisted["run_links"][0]["source_candidate_id"] == approved["candidate_id"]


def test_promoter_maps_approved_rumor_and_relationship_candidates(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "mixed.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(sample_result_bundle())

    approved_rumor = _approve_candidate(store, candidate_type="rumor_candidate")
    approved_relationship = _approve_candidate(store, candidate_type="relationship_change")

    rumor_result = promoter.promote_candidate(
        approved_rumor["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "location_id": 301,
            "source_name": "Town criers",
            "credibility_score": 7,
            "spread_speed": "Rapid",
        },
    )
    relationship_result = promoter.promote_candidate(
        approved_relationship["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "character_from_id": 201,
            "character_to_id": 202,
            "relationship_level": -35,
            "is_mutual": False,
        },
    )

    assert rumor_result["canonical_entity"]["canonical_type"] == "Rumor"
    assert rumor_result["canonical_entity"]["entity"]["credibility_score"] == 7
    assert rumor_result["canonical_entity"]["entity"]["spread_speed"] == "Rapid"
    assert rumor_result["run_link"]["run_id"] == "run-123"
    assert relationship_result["canonical_entity"]["canonical_type"] == "CharacterRelationship"
    assert relationship_result["canonical_entity"]["entity"]["relationship_type"] == "enemy"
    assert relationship_result["canonical_entity"]["entity"]["relationship_level"] == -35
    assert relationship_result["run_link"]["metadata"]["candidate_type"] == "relationship_change"


def test_promoter_requires_approved_candidate(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "gate.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(sample_result_bundle())
    pending = store.list_candidates(world_id="world-1", candidate_type="rumor_candidate")[0]

    try:
        promoter.promote_candidate(pending["candidate_id"], {"tenant_id": 1, "world_id": 101})
    except ValueError as exc:
        assert "approved candidates" in str(exc)
    else:
        raise AssertionError("Expected ValueError for non-approved candidate")


def test_promoter_reuses_canonical_id_for_identical_candidate_on_rerun(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "rerun.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(sample_result_bundle())
    approved = _approve_candidate(store, candidate_type="scenario_event")
    first = promoter.promote_candidate(
        approved["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201},
            "outcome": "success",
            "location_id": 301,
        },
    )

    importer.import_result_bundle(sample_result_bundle())
    rerun_candidate = store.list_candidates(world_id="world-1", candidate_type="scenario_event")[0]
    second = promoter.promote_candidate(
        rerun_candidate["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201},
            "outcome": "success",
            "location_id": 301,
        },
    )

    assert rerun_candidate["candidate_id"] == approved["candidate_id"]
    assert rerun_candidate["status"] == "promoted"
    assert rerun_candidate["target_canonical_id"] == str(first["canonical_entity"]["canonical_id"])
    assert second["canonical_entity"]["canonical_id"] == first["canonical_entity"]["canonical_id"]
    assert second["run_link"]["link_id"] == first["run_link"]["link_id"]
    assert len(store.list_entity_run_links(run_id="run-123", source_candidate_id=approved["candidate_id"])) == 1


def test_promoter_merges_approved_candidate_into_existing_canonical_entity(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "merge.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(sample_result_bundle())
    approved_first = _approve_candidate(store, candidate_type="scenario_event", run_id="run-123")
    promoted = promoter.promote_candidate(
        approved_first["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201},
            "outcome": "success",
            "location_id": 301,
        },
    )

    importer.import_result_bundle(
        sample_result_bundle(
            run_id="run-456",
            generated_at="2026-03-10T13:00:00Z",
            event_name="Court repeats denial",
        )
    )
    approved_second = _approve_candidate(store, candidate_type="scenario_event", run_id="run-456")

    merged = promoter.merge_candidate(
        approved_second["candidate_id"],
        {
            "canonical_id": promoted["canonical_entity"]["canonical_id"],
            "metadata": {"reason": "duplicate event narrative"},
        },
    )

    assert merged["canonical_entity"]["canonical_id"] == promoted["canonical_entity"]["canonical_id"]
    assert merged["run_link"]["relation_type"] == "merged_into"
    assert merged["run_link"]["metadata"]["reason"] == "duplicate event narrative"
    assert merged["candidate"]["status"] == "merged"
    assert merged["candidate"]["target_canonical_id"] == str(promoted["canonical_entity"]["canonical_id"])
    assert merged["candidate"]["target_canonical_type"] == "Event"
    assert store.get_canonical_entity(promoted["canonical_entity"]["canonical_id"])["source_candidate_id"] == approved_first["candidate_id"]


def test_promoter_reuses_existing_merge_link_for_already_merged_candidate(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "merge-rerun.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(sample_result_bundle())
    approved_first = _approve_candidate(store, candidate_type="scenario_event", run_id="run-123")
    promoted = promoter.promote_candidate(
        approved_first["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201},
            "outcome": "success",
        },
    )

    importer.import_result_bundle(
        sample_result_bundle(
            run_id="run-456",
            generated_at="2026-03-10T13:00:00Z",
            event_name="Court repeats denial",
        )
    )
    approved_second = _approve_candidate(store, candidate_type="scenario_event", run_id="run-456")

    first_merge = promoter.merge_candidate(
        approved_second["candidate_id"],
        {"canonical_id": promoted["canonical_entity"]["canonical_id"]},
    )
    second_merge = promoter.merge_candidate(
        approved_second["candidate_id"],
        {"canonical_id": promoted["canonical_entity"]["canonical_id"]},
    )

    assert second_merge["candidate"]["status"] == "merged"
    assert second_merge["candidate"]["target_canonical_id"] == str(promoted["canonical_entity"]["canonical_id"])
    assert second_merge["run_link"]["link_id"] == first_merge["run_link"]["link_id"]
    assert len(store.list_entity_run_links(run_id="run-456", source_candidate_id=approved_second["candidate_id"])) == 1