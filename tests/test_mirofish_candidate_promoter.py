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


def policy_ready_bundle(
    *,
    low_confidence_event: bool = False,
    include_rumor_candidate: bool = False,
    include_relationship_candidate: bool = False,
) -> dict:
    bundle = sample_result_bundle()
    bundle["runtime_evidence"] = [
        {
            "evidence_id": "ev-event-1",
            "evidence_type": "post",
            "source_type": "runtime_action",
            "actor_refs": ["actor:royal_court"],
            "text": "The Royal Court publicly denies the forged decree.",
            "timestamp": "2026-03-10T12:05:00Z",
            "confidence": 0.95,
            "source_refs": [{"collection": "policy_event_cluster", "index": 0}],
        },
        {
            "evidence_id": "ev-event-2",
            "evidence_type": "report",
            "source_type": "runtime_action",
            "actor_refs": ["org:royal_court"],
            "text": "Multiple witnesses confirm the denial spread across the capital.",
            "timestamp": "2026-03-10T12:06:00Z",
            "confidence": 0.94,
            "source_refs": [{"collection": "policy_event_cluster", "index": 0}],
        },
    ]
    candidates = [
        {
            "candidate_id": "cand-event-safe",
            "candidate_type": "scenario_event",
            "target_canonical_type": "Event",
            "name": "Court issues denial",
            "summary": "The court publicly denies the forged decree.",
            "proposed_change": {
                "participant_ids": ["actor:royal_court", "org:royal_court"],
                "timestamp": "2026-03-10T12:05:00Z",
                "outcome": "success",
            },
            "evidence_ids": ["ev-event-1", "ev-event-2"],
            "source_refs": [{"collection": "policy_event_cluster", "index": 0}],
            "confidence": 0.93,
        }
    ]
    if low_confidence_event:
        candidates.append(
            {
                "candidate_id": "cand-event-low",
                "candidate_type": "scenario_event",
                "target_canonical_type": "Event",
                "name": "Court whispers denial",
                "summary": "Signals are still too weak for canon.",
                "proposed_change": {
                    "participant_ids": ["actor:royal_court"],
                    "timestamp": "2026-03-10T12:07:00Z",
                },
                "evidence_ids": ["ev-event-1", "ev-event-2"],
                "source_refs": [{"collection": "policy_event_cluster", "index": 1}],
                "confidence": 0.89,
            }
        )
    if include_rumor_candidate:
        candidates.append(
            {
                "candidate_id": "cand-rumor-safe",
                "candidate_type": "rumor_candidate",
                "target_canonical_type": "Rumor",
                "name": "Forged decree rumor",
                "summary": "Town criers continue amplifying the story.",
                "proposed_change": {"source_name": "Town criers"},
                "evidence_ids": ["ev-event-1", "ev-event-2"],
                "source_refs": [{"collection": "policy_event_cluster", "index": 2}],
                "confidence": 0.95,
            }
        )
    if include_relationship_candidate:
        candidates.append(
            {
                "candidate_id": "cand-relationship-safe",
                "candidate_type": "relationship_change",
                "target_canonical_type": "CharacterRelationship",
                "name": "Captain Serik distrusts Nessa",
                "summary": "The decree fallout pushes their trust sharply downward.",
                "proposed_change": {"relationship_level": -42},
                "evidence_ids": ["ev-event-1", "ev-event-2"],
                "source_refs": [{"collection": "policy_event_cluster", "index": 3}],
                "confidence": 0.94,
            }
        )
    bundle["candidate_deltas"] = candidates
    return bundle


def manual_candidate_bundle(
    *,
    candidate_id: str,
    target_canonical_type: str,
    name: str,
    summary: str,
    run_id: str,
    proposed_change: dict | None = None,
) -> dict:
    return {
        "schema_version": "1.1",
        "world_id": "world-1",
        "scenario_id": "succession-crisis",
        "run_id": run_id,
        "generated_at": "2026-03-10T12:00:00Z",
        "runtime_evidence": [
            {
                "evidence_id": f"ev-{candidate_id}",
                "evidence_type": "runtime_observation",
                "source_type": "manual_candidate",
                "text": summary,
                "timestamp": "2026-03-10T12:05:00Z",
                "confidence": 0.88,
                "source_refs": [{"collection": "manual_candidates", "index": 0}],
            }
        ],
        "candidate_deltas": [
            {
                "candidate_id": candidate_id,
                "candidate_type": "new_entity_candidate",
                "target_canonical_type": target_canonical_type,
                "name": name,
                "summary": summary,
                "proposed_change": proposed_change or {},
                "evidence_ids": [f"ev-{candidate_id}"],
                "source_refs": [{"collection": "manual_candidates", "index": 0}],
                "confidence": 0.88,
            }
        ],
    }


def long_backstory() -> str:
    return (
        "Captain Aria was raised among flood-battered harbor walls, learned diplomacy from smugglers and admirals alike, "
        "and now balances civic duty, battlefield discipline, and private grief after years of defending the coast."
    )


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


def test_auto_promote_policy_promotes_safe_event_candidate(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-policy.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(policy_ready_bundle())

    result = promoter.auto_promote_candidate(
        "cand-event-safe",
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201},
            "outcome": "success",
        },
        policy="safe_event_only",
    )

    assert result["candidate"]["status"] == "promoted"
    assert result["canonical_entity"]["canonical_type"] == "Event"
    assert result["run_link"]["metadata"]["auto_promote_policy"] == "safe_event_only"
    assert result["run_link"]["metadata"]["auto_promoted"] is True


def test_auto_promote_policy_rejects_low_confidence_event(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-policy-gate.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(policy_ready_bundle(low_confidence_event=True))

    try:
        promoter.auto_promote_candidate(
            "cand-event-low",
            {
                "tenant_id": 1,
                "world_id": 101,
                "participant_map": {"actor:royal_court": 201},
            },
            policy="safe_event_only",
        )
    except ValueError as exc:
        assert "confidence >= 0.90" in str(exc)
    else:
        raise AssertionError("Expected ValueError for low-confidence auto-promotion candidate")


def test_auto_promote_policy_promotes_safe_rumor_candidate(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-policy-rumor.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(policy_ready_bundle(include_rumor_candidate=True))

    result = promoter.auto_promote_candidate(
        "cand-rumor-safe",
        {
            "tenant_id": 1,
            "world_id": 101,
            "source_name": "Town criers",
            "credibility_score": 7,
            "location_id": 301,
        },
        policy="safe_rumor_only",
    )

    assert result["candidate"]["status"] == "promoted"
    assert result["canonical_entity"]["canonical_type"] == "Rumor"
    assert result["canonical_entity"]["entity"]["credibility_score"] == 7
    assert result["run_link"]["metadata"]["auto_promote_policy"] == "safe_rumor_only"


def test_auto_promote_policy_promotes_safe_relationship_candidate(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-policy-relationship.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(policy_ready_bundle(include_relationship_candidate=True))

    result = promoter.auto_promote_candidate(
        "cand-relationship-safe",
        {
            "tenant_id": 1,
            "world_id": 101,
            "character_from_id": 201,
            "character_to_id": 202,
            "relationship_level": -42,
            "is_mutual": False,
        },
        policy="safe_relationship_only",
    )

    assert result["candidate"]["status"] == "promoted"
    assert result["canonical_entity"]["canonical_type"] == "CharacterRelationship"
    assert result["canonical_entity"]["entity"]["relationship_level"] == -42
    assert result["run_link"]["metadata"]["auto_promote_policy"] == "safe_relationship_only"


def test_auto_promote_policy_rejects_weak_relationship_delta(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-policy-relationship-gate.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(policy_ready_bundle(include_relationship_candidate=True))

    try:
        promoter.auto_promote_candidate(
            "cand-relationship-safe",
            {
                "tenant_id": 1,
                "world_id": 101,
                "character_from_id": 201,
                "character_to_id": 202,
                "relationship_level": -10,
            },
            policy="safe_relationship_only",
        )
    except ValueError as exc:
        assert "abs(relationship_level) >= 30" in str(exc)
    else:
        raise AssertionError("Expected ValueError for weak relationship delta")

    candidate = store.get_candidate("cand-relationship-safe")
    assert candidate is not None
    assert candidate["status"] == "pending_review"


def test_promoter_maps_manual_location_faction_and_character_candidates(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "manual-create.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        manual_candidate_bundle(
            candidate_id="cand-location-new",
            target_canonical_type="Location",
            name="Ashen Keep",
            summary="A ruined fortress overlooking the northern pass.",
            run_id="run-location",
        )
    )
    approved_location = _approve_candidate(store, candidate_type="new_entity_candidate", run_id="run-location")
    location_result = promoter.promote_candidate(
        approved_location["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "location_type": "castle",
            "parent_location_id": 900,
        },
    )

    importer.import_result_bundle(
        manual_candidate_bundle(
            candidate_id="cand-faction-new",
            target_canonical_type="Faction",
            name="Harbor Guild",
            summary="A disciplined merchant coalition controlling the docks.",
            run_id="run-faction",
        )
    )
    approved_faction = _approve_candidate(store, candidate_type="new_entity_candidate", run_id="run-faction")
    faction_result = promoter.promote_candidate(
        approved_faction["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "faction_type": "merchant",
            "alignment": "neutral",
            "leader_character_id": 501,
            "is_joinable": False,
        },
    )

    importer.import_result_bundle(
        manual_candidate_bundle(
            candidate_id="cand-character-new",
            target_canonical_type="Character",
            name="Captain Aria",
            summary="A harbor defender whose public resolve hides years of sacrifice.",
            run_id="run-character",
        )
    )
    approved_character = _approve_candidate(store, candidate_type="new_entity_candidate", run_id="run-character")
    character_result = promoter.promote_candidate(
        approved_character["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "backstory": long_backstory(),
            "status": "active",
            "location_id": 301,
            "rarity": "legendary",
            "element": "water",
            "role": "support",
            "base_hp": 1400,
            "base_atk": 220,
            "base_def": 180,
            "base_speed": 120,
            "energy_cost": 90,
        },
    )

    assert location_result["canonical_entity"]["canonical_type"] == "Location"
    assert location_result["canonical_entity"]["entity"]["location_type"] == "castle"
    assert location_result["canonical_entity"]["entity"]["parent_location_id"] == 900
    assert faction_result["canonical_entity"]["canonical_type"] == "Faction"
    assert faction_result["canonical_entity"]["entity"]["faction_type"] == "merchant"
    assert faction_result["canonical_entity"]["entity"]["alignment"] == "neutral"
    assert faction_result["canonical_entity"]["entity"]["leader_character_id"] == 501
    assert faction_result["canonical_entity"]["entity"]["is_joinable"] is False
    assert character_result["canonical_entity"]["canonical_type"] == "Character"
    assert character_result["canonical_entity"]["entity"]["name"] == "Captain Aria"
    assert character_result["canonical_entity"]["entity"]["backstory"] == long_backstory()
    assert character_result["canonical_entity"]["entity"]["rarity"] == "legendary"
    assert character_result["canonical_entity"]["entity"]["location_id"] == 301


def test_promoter_rejects_manual_character_without_backstory(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "manual-character-gate.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        manual_candidate_bundle(
            candidate_id="cand-character-incomplete",
            target_canonical_type="Character",
            name="Masked Witness",
            summary="A shadowy observer mentioned once during the disturbance.",
            run_id="run-character-gate",
        )
    )
    approved = _approve_candidate(store, candidate_type="new_entity_candidate", run_id="run-character-gate")

    try:
        promoter.promote_candidate(
            approved["candidate_id"],
            {
                "tenant_id": 1,
                "world_id": 101,
            },
        )
    except ValueError as exc:
        assert "Backstory" in str(exc)
    else:
        raise AssertionError("Expected ValueError for incomplete manual character promotion")


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


def test_promoter_merges_manual_location_candidate_into_existing_location(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "manual-merge.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        manual_candidate_bundle(
            candidate_id="cand-location-create",
            target_canonical_type="Location",
            name="Ashen Keep",
            summary="A ruined fortress overlooking the northern pass.",
            run_id="run-location-create",
        )
    )
    approved_first = _approve_candidate(store, candidate_type="new_entity_candidate", run_id="run-location-create")
    promoted = promoter.promote_candidate(
        approved_first["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "location_type": "castle",
        },
    )

    importer.import_result_bundle(
        manual_candidate_bundle(
            candidate_id="cand-location-merge",
            target_canonical_type="Location",
            name="Ashen Keep Ruins",
            summary="Witnesses use a variant name for the same fortress.",
            run_id="run-location-merge",
        )
    )
    approved_second = _approve_candidate(store, candidate_type="new_entity_candidate", run_id="run-location-merge")
    merged = promoter.merge_candidate(
        approved_second["candidate_id"],
        {
            "canonical_id": promoted["canonical_entity"]["canonical_id"],
            "metadata": {"reason": "alias of existing location"},
        },
    )

    assert merged["canonical_entity"]["canonical_type"] == "Location"
    assert merged["canonical_entity"]["canonical_id"] == promoted["canonical_entity"]["canonical_id"]
    assert merged["run_link"]["relation_type"] == "merged_into"
    assert merged["run_link"]["metadata"]["reason"] == "alias of existing location"
    assert merged["candidate"]["status"] == "merged"