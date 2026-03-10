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


def cross_run_relationship_bundle(
    *,
    run_id: str,
    candidate_id: str,
    relationship_level: int,
    actor_refs: list[str] | None = None,
    confidence: float = 0.94,
) -> dict:
    refs = actor_refs or ["actor:captain_serik", "actor:nessa"]
    evidence_ids = [f"{candidate_id}-ev-1", f"{candidate_id}-ev-2"]
    return {
        "schema_version": "1.1",
        "world_id": "world-1",
        "scenario_id": "succession-crisis",
        "run_id": run_id,
        "generated_at": "2026-03-10T12:00:00Z",
        "runtime_evidence": [
            {
                "evidence_id": evidence_ids[0],
                "evidence_type": "relationship_change",
                "source_type": "relationship_delta",
                "actor_refs": refs,
                "text": "Captain Serik publicly breaks trust with Nessa.",
                "timestamp": "2026-03-10T12:05:00Z",
                "confidence": confidence,
                "source_refs": [{"collection": "relationship_delta", "index": 0}],
            },
            {
                "evidence_id": evidence_ids[1],
                "evidence_type": "relationship_change",
                "source_type": "relationship_delta",
                "actor_refs": refs,
                "text": "Observers confirm the fallout persists across the district.",
                "timestamp": "2026-03-10T12:06:00Z",
                "confidence": confidence,
                "source_refs": [{"collection": "relationship_delta", "index": 0}],
            },
        ],
        "candidate_deltas": [
            {
                "candidate_id": candidate_id,
                "candidate_type": "relationship_change",
                "target_canonical_type": "CharacterRelationship",
                "name": "Captain Serik distrusts Nessa",
                "summary": "Repeated signals show the pair sliding into open distrust.",
                "proposed_change": {
                    "actor_refs": refs,
                    "relationship_level": relationship_level,
                },
                "evidence_ids": evidence_ids,
                "source_refs": [{"collection": "relationship_delta", "index": 0}],
                "confidence": confidence,
            }
        ],
    }


def cross_run_event_bundle(
    *,
    run_id: str,
    candidate_id: str,
    outcome: str,
    participant_ids: list[str] | None = None,
    timestamp: str = "2026-03-10T12:05:00Z",
    confidence: float = 0.94,
) -> dict:
    refs = participant_ids or ["actor:royal_court", "org:royal_court"]
    evidence_ids = [f"{candidate_id}-ev-1", f"{candidate_id}-ev-2"]
    return {
        "schema_version": "1.1",
        "world_id": "world-1",
        "scenario_id": "succession-crisis",
        "run_id": run_id,
        "generated_at": "2026-03-10T12:00:00Z",
        "runtime_evidence": [
            {
                "evidence_id": evidence_ids[0],
                "evidence_type": "post",
                "source_type": "runtime_action",
                "actor_refs": refs,
                "text": "The Royal Court publicly denies the forged decree.",
                "timestamp": timestamp,
                "confidence": confidence,
                "source_refs": [{"collection": "emergent_event", "index": 0}],
            },
            {
                "evidence_id": evidence_ids[1],
                "evidence_type": "report",
                "source_type": "runtime_action",
                "actor_refs": refs,
                "text": "Multiple witnesses confirm the denial spread across the capital.",
                "timestamp": timestamp,
                "confidence": confidence,
                "source_refs": [{"collection": "emergent_event", "index": 0}],
            },
        ],
        "candidate_deltas": [
            {
                "candidate_id": candidate_id,
                "candidate_type": "scenario_event",
                "target_canonical_type": "Event",
                "name": "Court issues denial",
                "summary": "The court publicly denies the forged decree.",
                "proposed_change": {
                    "participant_ids": refs,
                    "timestamp": timestamp,
                    "outcome": outcome,
                },
                "evidence_ids": evidence_ids,
                "source_refs": [{"collection": "emergent_event", "index": 0}],
                "confidence": confidence,
            }
        ],
    }


def exact_event_duplicate_bundle(
    *,
    candidate_id: str,
    run_id: str,
    outcome: str,
    participant_ids: list[str] | None = None,
    timestamp: str = "2026-03-10T12:05:00Z",
    location_id: int | None = 301,
    confidence: float = 0.95,
    evidence_count: int = 2,
) -> dict:
    refs = ["actor:royal_court", "org:royal_court"] if participant_ids is None else list(participant_ids)
    evidence_ids = [f"{candidate_id}-ev-{index + 1}" for index in range(evidence_count)]
    proposed_change = {
        "participant_ids": refs,
        "timestamp": timestamp,
        "outcome": outcome,
    }
    if location_id is not None:
        proposed_change["location_id"] = location_id
    return {
        "schema_version": "1.1",
        "world_id": "world-1",
        "scenario_id": "succession-crisis",
        "run_id": run_id,
        "generated_at": "2026-03-10T12:00:00Z",
        "runtime_evidence": [
            {
                "evidence_id": evidence_id,
                "evidence_type": "runtime_action",
                "source_type": "manual_event_candidate",
                "actor_refs": refs,
                "text": "Witnesses describe the same court denial event.",
                "timestamp": timestamp,
                "confidence": confidence,
                "source_refs": [{"collection": "manual_event_candidates", "index": index}],
            }
            for index, evidence_id in enumerate(evidence_ids)
        ],
        "candidate_deltas": [
            {
                "candidate_id": candidate_id,
                "candidate_type": "scenario_event",
                "target_canonical_type": "Event",
                "name": "Court issues denial",
                "summary": "The court publicly denies the forged decree.",
                "proposed_change": proposed_change,
                "evidence_ids": evidence_ids,
                "source_refs": [{"collection": "manual_event_candidates", "index": 0}],
                "confidence": confidence,
            }
        ],
    }


def cross_run_rumor_bundle(
    *,
    run_id: str,
    candidate_id: str,
    name: str = "Forged decree rumor",
    source_name: str = "Town criers",
    truth_level: str = "Unverified",
    confidence: float = 0.95,
) -> dict:
    evidence_ids = [f"{candidate_id}-ev-1", f"{candidate_id}-ev-2"]
    return {
        "schema_version": "1.1",
        "world_id": "world-1",
        "scenario_id": "succession-crisis",
        "run_id": run_id,
        "generated_at": "2026-03-10T12:00:00Z",
        "runtime_evidence": [
            {
                "evidence_id": evidence_ids[0],
                "evidence_type": "rumor_signal",
                "source_type": "prediction_summary",
                "text": "Town criers keep repeating the forged decree story.",
                "timestamp": "2026-03-10T12:05:00Z",
                "confidence": confidence,
                "source_refs": [{"collection": "prediction_summary", "index": 0}],
            },
            {
                "evidence_id": evidence_ids[1],
                "evidence_type": "rumor_signal",
                "source_type": "prediction_summary",
                "text": "A second witness confirms the rumor is still spreading.",
                "timestamp": "2026-03-10T12:06:00Z",
                "confidence": confidence,
                "source_refs": [{"collection": "prediction_summary", "index": 0}],
            },
        ],
        "candidate_deltas": [
            {
                "candidate_id": candidate_id,
                "candidate_type": "rumor_candidate",
                "target_canonical_type": "Rumor",
                "name": name,
                "summary": "Repeated chatter says the decree was forged.",
                "proposed_change": {
                    "source_name": source_name,
                    "truth_level": truth_level,
                },
                "evidence_ids": evidence_ids,
                "source_refs": [{"collection": "prediction_summary", "index": 0}],
                "confidence": confidence,
            }
        ],
    }


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


def exact_location_duplicate_bundle(
    *,
    candidate_id: str,
    name: str,
    summary: str,
    run_id: str,
    location_type: str = "castle",
    parent_location_id: int | None = None,
    confidence: float = 0.95,
    evidence_count: int = 2,
) -> dict:
    evidence_ids = [f"{candidate_id}-ev-{index + 1}" for index in range(evidence_count)]
    proposed_change = {"location_type": location_type}
    if parent_location_id is not None:
        proposed_change["parent_location_id"] = parent_location_id
    return {
        "schema_version": "1.1",
        "world_id": "world-1",
        "scenario_id": "succession-crisis",
        "run_id": run_id,
        "generated_at": "2026-03-10T12:00:00Z",
        "runtime_evidence": [
            {
                "evidence_id": evidence_id,
                "evidence_type": "runtime_observation",
                "source_type": "manual_candidate",
                "text": summary,
                "timestamp": f"2026-03-10T12:0{index + 1}:00Z",
                "confidence": confidence,
                "source_refs": [{"collection": "manual_candidates", "index": index}],
            }
            for index, evidence_id in enumerate(evidence_ids)
        ],
        "candidate_deltas": [
            {
                "candidate_id": candidate_id,
                "candidate_type": "new_entity_candidate",
                "target_canonical_type": "Location",
                "name": name,
                "summary": summary,
                "proposed_change": proposed_change,
                "evidence_ids": evidence_ids,
                "source_refs": [{"collection": "manual_candidates", "index": 0}],
                "confidence": confidence,
            }
        ],
    }


def exact_faction_duplicate_bundle(
    *,
    candidate_id: str,
    name: str,
    summary: str,
    run_id: str,
    faction_type: str = "merchant",
    alignment: str = "neutral",
    leader_character_id: int | None = 501,
    is_joinable: bool = False,
    confidence: float = 0.95,
    evidence_count: int = 2,
) -> dict:
    evidence_ids = [f"{candidate_id}-ev-{index + 1}" for index in range(evidence_count)]
    proposed_change: dict[str, object] = {
        "faction_type": faction_type,
        "alignment": alignment,
        "is_joinable": is_joinable,
    }
    if leader_character_id is not None:
        proposed_change["leader_character_id"] = leader_character_id
    return {
        "schema_version": "1.1",
        "world_id": "world-1",
        "scenario_id": "succession-crisis",
        "run_id": run_id,
        "generated_at": "2026-03-10T12:00:00Z",
        "runtime_evidence": [
            {
                "evidence_id": evidence_id,
                "evidence_type": "runtime_observation",
                "source_type": "manual_candidate",
                "text": summary,
                "timestamp": f"2026-03-10T12:0{index + 1}:00Z",
                "confidence": confidence,
                "source_refs": [{"collection": "manual_candidates", "index": index}],
            }
            for index, evidence_id in enumerate(evidence_ids)
        ],
        "candidate_deltas": [
            {
                "candidate_id": candidate_id,
                "candidate_type": "new_entity_candidate",
                "target_canonical_type": "Faction",
                "name": name,
                "summary": summary,
                "proposed_change": proposed_change,
                "evidence_ids": evidence_ids,
                "source_refs": [{"collection": "manual_candidates", "index": 0}],
                "confidence": confidence,
            }
        ],
    }


def exact_character_duplicate_bundle(
    *,
    candidate_id: str,
    name: str,
    summary: str,
    run_id: str,
    status: str = "active",
    parent_id: int | None = None,
    location_id: int = 301,
    rarity: str = "legendary",
    element: str = "water",
    role: str | None = "support",
    confidence: float = 0.95,
    evidence_count: int = 2,
) -> dict:
    evidence_ids = [f"{candidate_id}-ev-{index + 1}" for index in range(evidence_count)]
    proposed_change: dict[str, object] = {
        "status": status,
        "location_id": location_id,
        "rarity": rarity,
        "element": element,
    }
    if parent_id is not None:
        proposed_change["parent_id"] = parent_id
    if role is not None:
        proposed_change["role"] = role
    return {
        "schema_version": "1.1",
        "world_id": "world-1",
        "scenario_id": "succession-crisis",
        "run_id": run_id,
        "generated_at": "2026-03-10T12:00:00Z",
        "runtime_evidence": [
            {
                "evidence_id": evidence_id,
                "evidence_type": "runtime_observation",
                "source_type": "manual_candidate",
                "text": summary,
                "timestamp": f"2026-03-10T12:0{index + 1}:00Z",
                "confidence": confidence,
                "source_refs": [{"collection": "manual_candidates", "index": index}],
            }
            for index, evidence_id in enumerate(evidence_ids)
        ],
        "candidate_deltas": [
            {
                "candidate_id": candidate_id,
                "candidate_type": "new_entity_candidate",
                "target_canonical_type": "Character",
                "name": name,
                "summary": summary,
                "proposed_change": proposed_change,
                "evidence_ids": evidence_ids,
                "source_refs": [{"collection": "manual_candidates", "index": 0}],
                "confidence": confidence,
            }
        ],
    }


def exact_relationship_duplicate_bundle(
    *,
    candidate_id: str,
    run_id: str,
    relationship_level: int,
    actor_refs: list[str] | None = None,
    confidence: float = 0.95,
    evidence_count: int = 2,
) -> dict:
    refs = actor_refs or ["actor:captain_serik", "actor:nessa"]
    evidence_ids = [f"{candidate_id}-ev-{index + 1}" for index in range(evidence_count)]
    return {
        "schema_version": "1.1",
        "world_id": "world-1",
        "scenario_id": "succession-crisis",
        "run_id": run_id,
        "generated_at": "2026-03-10T12:00:00Z",
        "runtime_evidence": [
            {
                "evidence_id": evidence_id,
                "evidence_type": "relationship_change",
                "source_type": "relationship_delta",
                "actor_refs": refs,
                "text": "Captain Serik and Nessa show the same relationship shift again.",
                "timestamp": "2026-03-10T12:05:00Z",
                "confidence": confidence,
                "source_refs": [{"collection": "relationship_delta", "index": 0}],
            }
            for evidence_id in evidence_ids
        ],
        "candidate_deltas": [
            {
                "candidate_id": candidate_id,
                "candidate_type": "relationship_change",
                "target_canonical_type": "CharacterRelationship",
                "name": "Captain Serik distrusts Nessa",
                "summary": "Repeated signals show the same directed relationship snapshot.",
                "proposed_change": {
                    "actor_refs": refs,
                    "relationship_level": relationship_level,
                },
                "evidence_ids": evidence_ids,
                "source_refs": [{"collection": "relationship_delta", "index": 0}],
                "confidence": confidence,
            }
        ],
    }


def exact_rumor_duplicate_bundle(
    *,
    candidate_id: str,
    name: str,
    summary: str,
    run_id: str,
    source_name: str = "Town criers",
    truth_level: str = "unverified",
    location_id: int = 301,
    confidence: float = 0.95,
    evidence_count: int = 2,
) -> dict:
    evidence_ids = [f"{candidate_id}-ev-{index + 1}" for index in range(evidence_count)]
    return {
        "schema_version": "1.1",
        "world_id": "world-1",
        "scenario_id": "succession-crisis",
        "run_id": run_id,
        "generated_at": "2026-03-10T12:00:00Z",
        "runtime_evidence": [
            {
                "evidence_id": evidence_id,
                "evidence_type": "runtime_observation",
                "source_type": "manual_candidate",
                "text": summary,
                "timestamp": f"2026-03-10T12:0{index + 1}:00Z",
                "confidence": confidence,
                "source_refs": [{"collection": "manual_candidates", "index": index}],
            }
            for index, evidence_id in enumerate(evidence_ids)
        ],
        "candidate_deltas": [
            {
                "candidate_id": candidate_id,
                "candidate_type": "rumor_candidate",
                "target_canonical_type": "Rumor",
                "name": name,
                "summary": summary,
                "proposed_change": {
                    "source_name": source_name,
                    "truth_level": truth_level,
                    "location_id": location_id,
                },
                "evidence_ids": evidence_ids,
                "source_refs": [{"collection": "manual_candidates", "index": 0}],
                "confidence": confidence,
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


def test_preview_auto_promote_candidate_reports_eligibility_without_side_effects(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "preview-auto-policy-relationship.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(policy_ready_bundle(include_relationship_candidate=True))

    preview = promoter.preview_auto_promote_candidate(
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

    candidate = store.get_candidate("cand-relationship-safe")
    canonical_entity = store.get_canonical_entity_by_candidate("cand-relationship-safe")

    assert preview["eligible"] is True
    assert preview["target_canonical_type"] == "CharacterRelationship"
    assert preview["metadata_preview"]["auto_promote_policy"] == "safe_relationship_only"
    assert any("Policy 'safe_relationship_only' gate passed" == item for item in preview["reasons"])
    assert candidate is not None
    assert candidate["status"] == "pending_review"
    assert canonical_entity is None


def test_preview_auto_promote_candidate_reports_mapping_failure_without_side_effects(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "preview-auto-policy-event-mapping.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(policy_ready_bundle())

    preview = promoter.preview_auto_promote_candidate(
        "cand-event-safe",
        {
            "tenant_id": 1,
            "world_id": 101,
        },
        policy="safe_event_only",
    )

    candidate = store.get_candidate("cand-event-safe")
    canonical_entity = store.get_canonical_entity_by_candidate("cand-event-safe")

    assert preview["eligible"] is False
    assert preview["metadata_preview"] is None
    assert preview["reasons"] == ["Event promotion requires participant_ids or participant_map"]
    assert candidate is not None
    assert candidate["status"] == "pending_review"
    assert canonical_entity is None


def test_auto_promote_policy_promotes_cross_run_relationship_candidate(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-policy-cross-run-relationship.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(
        cross_run_relationship_bundle(run_id="run-rel-primary", candidate_id="cand-relationship-primary", relationship_level=-42)
    )
    importer.import_result_bundle(
        cross_run_relationship_bundle(run_id="run-rel-support", candidate_id="cand-relationship-support", relationship_level=-55)
    )

    result = promoter.auto_promote_candidate(
        "cand-relationship-primary",
        {
            "tenant_id": 1,
            "world_id": 101,
            "character_from_id": 201,
            "character_to_id": 202,
            "relationship_level": -42,
            "is_mutual": False,
        },
        policy="safe_cross_run_relationship_only",
    )

    assert result["candidate"]["status"] == "promoted"
    assert result["canonical_entity"]["canonical_type"] == "CharacterRelationship"
    assert result["run_link"]["metadata"]["auto_promote_policy"] == "safe_cross_run_relationship_only"
    assert result["run_link"]["metadata"]["cross_run_supporting_run_ids"] == ["run-rel-support"]
    assert result["run_link"]["metadata"]["cross_run_distinct_run_count"] == 2
    assert result["run_link"]["metadata"]["contradiction_check"] == "passed"


def test_auto_promote_policy_promotes_cross_run_event_candidate(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-policy-cross-run-event.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(cross_run_event_bundle(run_id="run-event-primary", candidate_id="cand-event-primary", outcome="success"))
    importer.import_result_bundle(cross_run_event_bundle(run_id="run-event-support", candidate_id="cand-event-support", outcome="success"))

    result = promoter.auto_promote_candidate(
        "cand-event-primary",
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
            "outcome": "success",
            "location_id": 301,
        },
        policy="safe_cross_run_event_only",
    )

    assert result["candidate"]["status"] == "promoted"
    assert result["canonical_entity"]["canonical_type"] == "Event"
    assert result["run_link"]["metadata"]["auto_promote_policy"] == "safe_cross_run_event_only"
    assert result["run_link"]["metadata"]["cross_run_supporting_run_ids"] == ["run-event-support"]
    assert result["run_link"]["metadata"]["event_match_outcome"] == "success"
    assert result["run_link"]["metadata"]["event_match_date_bucket"] == "2026-03-10"
    assert result["run_link"]["metadata"]["contradiction_check"] == "passed"


def test_auto_promote_policy_promotes_cross_run_rumor_candidate(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-policy-cross-run-rumor.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(cross_run_rumor_bundle(run_id="run-rumor-primary", candidate_id="cand-rumor-primary"))
    importer.import_result_bundle(
        cross_run_rumor_bundle(
            run_id="run-rumor-support",
            candidate_id="cand-rumor-support",
            name="  forged decree rumor  ",
            source_name=" town criers ",
        )
    )

    result = promoter.auto_promote_candidate(
        "cand-rumor-primary",
        {
            "tenant_id": 1,
            "world_id": 101,
            "source_name": "Town criers",
            "credibility_score": 7,
            "location_id": 301,
        },
        policy="safe_cross_run_rumor_only",
    )

    assert result["candidate"]["status"] == "promoted"
    assert result["canonical_entity"]["canonical_type"] == "Rumor"
    assert result["canonical_entity"]["entity"]["credibility_score"] == 7
    assert result["run_link"]["metadata"]["auto_promote_policy"] == "safe_cross_run_rumor_only"
    assert result["run_link"]["metadata"]["cross_run_supporting_run_ids"] == ["run-rumor-support"]
    assert result["run_link"]["metadata"]["rumor_match_name"] == "forged decree rumor"
    assert result["run_link"]["metadata"]["rumor_match_source_name"] == "town criers"
    assert result["run_link"]["metadata"]["rumor_truth_bucket"] == "Unverified"
    assert result["run_link"]["metadata"]["duplicate_guard"] == "passed"


def test_auto_promote_policy_rejects_cross_run_event_without_support(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-policy-cross-run-event-no-support.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(cross_run_event_bundle(run_id="run-event-primary", candidate_id="cand-event-primary", outcome="success"))

    try:
        promoter.auto_promote_candidate(
            "cand-event-primary",
            {
                "tenant_id": 1,
                "world_id": 101,
                "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
                "outcome": "success",
            },
            policy="safe_cross_run_event_only",
        )
    except ValueError as exc:
        assert "at least 1 additional run" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing event cross-run support")

    candidate = store.get_candidate("cand-event-primary")
    assert candidate is not None
    assert candidate["status"] == "pending_review"


def test_auto_promote_policy_rejects_cross_run_event_with_ongoing_outcome(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-policy-cross-run-event-ongoing.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(cross_run_event_bundle(run_id="run-event-primary", candidate_id="cand-event-primary", outcome="ongoing"))
    importer.import_result_bundle(cross_run_event_bundle(run_id="run-event-support", candidate_id="cand-event-support", outcome="ongoing"))

    try:
        promoter.auto_promote_candidate(
            "cand-event-primary",
            {
                "tenant_id": 1,
                "world_id": 101,
                "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
                "outcome": "ongoing",
            },
            policy="safe_cross_run_event_only",
        )
    except ValueError as exc:
        assert "terminal non-ongoing outcome" in str(exc)
    else:
        raise AssertionError("Expected ValueError for ongoing event outcome")


def test_auto_promote_policy_rejects_cross_run_rumor_without_support(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-policy-cross-run-rumor-no-support.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(cross_run_rumor_bundle(run_id="run-rumor-primary", candidate_id="cand-rumor-primary"))

    try:
        promoter.auto_promote_candidate(
            "cand-rumor-primary",
            {
                "tenant_id": 1,
                "world_id": 101,
                "source_name": "Town criers",
                "credibility_score": 7,
                "location_id": 301,
            },
            policy="safe_cross_run_rumor_only",
        )
    except ValueError as exc:
        assert "at least 1 additional run" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing rumor cross-run support")

    candidate = store.get_candidate("cand-rumor-primary")
    assert candidate is not None
    assert candidate["status"] == "pending_review"


def test_auto_promote_policy_rejects_cross_run_rumor_with_resolved_truth(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-policy-cross-run-rumor-resolved.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(
        cross_run_rumor_bundle(
            run_id="run-rumor-primary",
            candidate_id="cand-rumor-primary",
            truth_level="True",
        )
    )
    importer.import_result_bundle(
        cross_run_rumor_bundle(
            run_id="run-rumor-support",
            candidate_id="cand-rumor-support",
            truth_level="True",
        )
    )

    try:
        promoter.auto_promote_candidate(
            "cand-rumor-primary",
            {
                "tenant_id": 1,
                "world_id": 101,
                "source_name": "Town criers",
                "credibility_score": 7,
                "location_id": 301,
                "truth_level": "True",
            },
            policy="safe_cross_run_rumor_only",
        )
    except ValueError as exc:
        assert "only supports unresolved truth levels" in str(exc)
    else:
        raise AssertionError("Expected ValueError for resolved rumor truth level")

    candidate = store.get_candidate("cand-rumor-primary")
    assert candidate is not None
    assert candidate["status"] == "pending_review"


def test_preview_auto_promote_candidate_reports_cross_run_event_eligibility_without_side_effects(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "preview-auto-policy-cross-run-event.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(cross_run_event_bundle(run_id="run-event-primary", candidate_id="cand-event-primary", outcome="success"))
    importer.import_result_bundle(cross_run_event_bundle(run_id="run-event-support", candidate_id="cand-event-support", outcome="success"))

    preview = promoter.preview_auto_promote_candidate(
        "cand-event-primary",
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
            "outcome": "success",
        },
        policy="safe_cross_run_event_only",
    )

    candidate = store.get_candidate("cand-event-primary")
    canonical_entity = store.get_canonical_entity_by_candidate("cand-event-primary")

    assert preview["eligible"] is True
    assert preview["target_canonical_type"] == "Event"
    assert preview["metadata_preview"]["auto_promote_policy"] == "safe_cross_run_event_only"
    assert preview["metadata_preview"]["cross_run_supporting_run_ids"] == ["run-event-support"]
    assert any("Cross-run support found in runs: run-event-support" == item for item in preview["reasons"])
    assert candidate is not None
    assert candidate["status"] == "pending_review"
    assert canonical_entity is None


def test_preview_auto_promote_candidate_reports_cross_run_rumor_eligibility_without_side_effects(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "preview-auto-policy-cross-run-rumor.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(cross_run_rumor_bundle(run_id="run-rumor-primary", candidate_id="cand-rumor-primary"))
    importer.import_result_bundle(cross_run_rumor_bundle(run_id="run-rumor-support", candidate_id="cand-rumor-support"))

    preview = promoter.preview_auto_promote_candidate(
        "cand-rumor-primary",
        {
            "tenant_id": 1,
            "world_id": 101,
            "source_name": "Town criers",
            "credibility_score": 7,
            "location_id": 301,
        },
        policy="safe_cross_run_rumor_only",
    )

    candidate = store.get_candidate("cand-rumor-primary")
    canonical_entity = store.get_canonical_entity_by_candidate("cand-rumor-primary")

    assert preview["eligible"] is True
    assert preview["target_canonical_type"] == "Rumor"
    assert preview["metadata_preview"]["auto_promote_policy"] == "safe_cross_run_rumor_only"
    assert preview["metadata_preview"]["cross_run_supporting_run_ids"] == ["run-rumor-support"]
    assert any("Cross-run support found in runs: run-rumor-support" == item for item in preview["reasons"])
    assert candidate is not None
    assert candidate["status"] == "pending_review"
    assert canonical_entity is None


def test_auto_promote_policy_rejects_cross_run_relationship_without_support(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-policy-cross-run-relationship-no-support.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)
    importer.import_result_bundle(
        cross_run_relationship_bundle(run_id="run-rel-primary", candidate_id="cand-relationship-primary", relationship_level=-42)
    )

    try:
        promoter.auto_promote_candidate(
            "cand-relationship-primary",
            {
                "tenant_id": 1,
                "world_id": 101,
                "character_from_id": 201,
                "character_to_id": 202,
                "relationship_level": -42,
            },
            policy="safe_cross_run_relationship_only",
        )
    except ValueError as exc:
        assert "at least 1 additional run" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing cross-run support")

    candidate = store.get_candidate("cand-relationship-primary")
    assert candidate is not None
    assert candidate["status"] == "pending_review"


def test_auto_promote_policy_rejects_cross_run_relationship_on_canonical_contradiction(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-policy-cross-run-relationship-conflict.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        cross_run_relationship_bundle(run_id="run-existing", candidate_id="cand-relationship-existing", relationship_level=58)
    )
    approved_existing = _approve_candidate(store, candidate_type="relationship_change", run_id="run-existing")
    promoter.promote_candidate(
        approved_existing["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "character_from_id": 201,
            "character_to_id": 202,
            "relationship_level": 58,
            "is_mutual": False,
        },
    )

    importer.import_result_bundle(
        cross_run_relationship_bundle(run_id="run-rel-primary", candidate_id="cand-relationship-primary", relationship_level=-42)
    )
    importer.import_result_bundle(
        cross_run_relationship_bundle(run_id="run-rel-support", candidate_id="cand-relationship-support", relationship_level=-55)
    )

    try:
        promoter.auto_promote_candidate(
            "cand-relationship-primary",
            {
                "tenant_id": 1,
                "world_id": 101,
                "character_from_id": 201,
                "character_to_id": 202,
                "relationship_level": -42,
            },
            policy="safe_cross_run_relationship_only",
        )
    except ValueError as exc:
        assert "opposite-polarity staged canonical relationship" in str(exc)
    else:
        raise AssertionError("Expected ValueError for canonical contradiction")

    candidate = store.get_candidate("cand-relationship-primary")
    assert candidate is not None
    assert candidate["status"] == "pending_review"


def test_auto_promote_policy_rejects_cross_run_event_on_canonical_contradiction(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-policy-cross-run-event-conflict.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(cross_run_event_bundle(run_id="run-event-existing", candidate_id="cand-event-existing", outcome="failure"))
    approved_existing = _approve_candidate(store, candidate_type="scenario_event", run_id="run-event-existing")
    promoter.promote_candidate(
        approved_existing["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
            "outcome": "failure",
            "location_id": 301,
        },
    )

    importer.import_result_bundle(cross_run_event_bundle(run_id="run-event-primary", candidate_id="cand-event-primary", outcome="success"))
    importer.import_result_bundle(cross_run_event_bundle(run_id="run-event-support", candidate_id="cand-event-support", outcome="success"))

    try:
        promoter.auto_promote_candidate(
            "cand-event-primary",
            {
                "tenant_id": 1,
                "world_id": 101,
                "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
                "outcome": "success",
                "location_id": 301,
            },
            policy="safe_cross_run_event_only",
        )
    except ValueError as exc:
        assert "conflicting staged canonical Event outcome" in str(exc)
    else:
        raise AssertionError("Expected ValueError for canonical event contradiction")

    candidate = store.get_candidate("cand-event-primary")
    assert candidate is not None
    assert candidate["status"] == "pending_review"


def test_auto_promote_policy_rejects_cross_run_rumor_on_canonical_duplicate(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-policy-cross-run-rumor-duplicate.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(cross_run_rumor_bundle(run_id="run-rumor-existing", candidate_id="cand-rumor-existing"))
    approved_existing = _approve_candidate(store, candidate_type="rumor_candidate", run_id="run-rumor-existing")
    promoter.promote_candidate(
        approved_existing["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "source_name": "Town criers",
            "credibility_score": 6,
            "location_id": 301,
        },
    )

    importer.import_result_bundle(cross_run_rumor_bundle(run_id="run-rumor-primary", candidate_id="cand-rumor-primary"))
    importer.import_result_bundle(cross_run_rumor_bundle(run_id="run-rumor-support", candidate_id="cand-rumor-support"))

    try:
        promoter.auto_promote_candidate(
            "cand-rumor-primary",
            {
                "tenant_id": 1,
                "world_id": 101,
                "source_name": "Town criers",
                "credibility_score": 7,
                "location_id": 301,
            },
            policy="safe_cross_run_rumor_only",
        )
    except ValueError as exc:
        assert "existing staged canonical Rumor" in str(exc)
    else:
        raise AssertionError("Expected ValueError for canonical rumor duplicate")

    candidate = store.get_candidate("cand-rumor-primary")
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
    assert len(merged["canonical_entity"]["run_links"]) == 2
    assert sorted((item["run_id"], item["relation_type"]) for item in merged["canonical_entity"]["run_links"]) == [
        ("run-123", "promoted_from"),
        ("run-456", "merged_into"),
    ]
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


def test_preview_auto_merge_candidate_finds_exact_duplicate_location_without_side_effects(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-preview.db")
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
    approved_create = _approve_candidate(store, candidate_type="new_entity_candidate", run_id="run-location-create")
    promoted = promoter.promote_candidate(
        approved_create["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "location_type": "castle",
            "parent_location_id": 900,
        },
    )

    importer.import_result_bundle(
        exact_location_duplicate_bundle(
            candidate_id="cand-location-duplicate",
            name="  Ashen-Keep  ",
            summary="Scouts clearly describe the same ruined fortress.",
            run_id="run-location-duplicate",
            parent_location_id=900,
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-location-duplicate",
        {"world_id": 101},
        policy="safe_existing_location_duplicate_only",
    )

    assert preview["eligible"] is True
    assert preview["candidate_status_before"] == "pending_review"
    assert preview["would_auto_approve"] is True
    assert preview["target_canonical_id"] == promoted["canonical_entity"]["canonical_id"]
    assert preview["target_canonical_type"] == "Location"
    assert preview["metadata_preview"]["auto_merge_policy"] == "safe_existing_location_duplicate_only"
    assert preview["metadata_preview"]["merge_match_name"] == "ashen keep"
    assert store.get_candidate("cand-location-duplicate")["status"] == "pending_review"
    assert store.list_entity_run_links(run_id="run-location-duplicate", source_candidate_id="cand-location-duplicate") == []


def test_auto_merge_candidate_merges_exact_duplicate_location_candidate(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-success.db")
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
    approved_create = _approve_candidate(store, candidate_type="new_entity_candidate", run_id="run-location-create")
    promoted = promoter.promote_candidate(
        approved_create["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "location_type": "castle",
            "parent_location_id": 900,
        },
    )

    importer.import_result_bundle(
        exact_location_duplicate_bundle(
            candidate_id="cand-location-duplicate",
            name="Ashen Keep",
            summary="A second run confirms the same ruined fortress.",
            run_id="run-location-duplicate",
            parent_location_id=900,
        )
    )

    merged = promoter.auto_merge_candidate(
        "cand-location-duplicate",
        {"world_id": 101},
        policy="safe_existing_location_duplicate_only",
    )

    assert merged["canonical_entity"]["canonical_id"] == promoted["canonical_entity"]["canonical_id"]
    assert merged["run_link"]["relation_type"] == "merged_into"
    assert merged["run_link"]["metadata"]["auto_merge_policy"] == "safe_existing_location_duplicate_only"
    assert merged["run_link"]["metadata"]["auto_merged"] is True
    assert merged["run_link"]["metadata"]["duplicate_guard"] == "passed"
    assert merged["candidate"]["status"] == "merged"
    assert merged["candidate"]["target_canonical_id"] == str(promoted["canonical_entity"]["canonical_id"])
    assert len(store.list_entity_run_links(run_id="run-location-duplicate", source_candidate_id="cand-location-duplicate")) == 1


def test_preview_auto_merge_candidate_rejects_when_location_signature_does_not_match(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-no-match.db")
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
    approved_create = _approve_candidate(store, candidate_type="new_entity_candidate", run_id="run-location-create")
    promoter.promote_candidate(
        approved_create["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "location_type": "castle",
            "parent_location_id": 900,
        },
    )

    importer.import_result_bundle(
        exact_location_duplicate_bundle(
            candidate_id="cand-location-duplicate",
            name="Ashen Keep",
            summary="This report points to a different sub-site.",
            run_id="run-location-duplicate",
            parent_location_id=901,
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-location-duplicate",
        {"world_id": 101},
        policy="safe_existing_location_duplicate_only",
    )

    assert preview["eligible"] is False
    assert preview["reasons"] == [
        "Policy 'safe_existing_location_duplicate_only' requires exactly 1 staged canonical Location exact duplicate match in the same world"
    ]


def test_preview_auto_merge_candidate_rejects_ambiguous_duplicate_locations(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-ambiguous.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    for candidate_id, run_id in (("cand-location-create-1", "run-location-create-1"), ("cand-location-create-2", "run-location-create-2")):
        importer.import_result_bundle(
            manual_candidate_bundle(
                candidate_id=candidate_id,
                target_canonical_type="Location",
                name="Ashen Keep",
                summary="A ruined fortress overlooking the northern pass.",
                run_id=run_id,
            )
        )
        approved = _approve_candidate(store, candidate_type="new_entity_candidate", run_id=run_id)
        promoter.promote_candidate(
            approved["candidate_id"],
            {
                "tenant_id": 1,
                "world_id": 101,
                "location_type": "castle",
                "parent_location_id": 900,
            },
        )

    importer.import_result_bundle(
        exact_location_duplicate_bundle(
            candidate_id="cand-location-duplicate",
            name="Ashen Keep",
            summary="Another run repeats the same location signature.",
            run_id="run-location-duplicate",
            parent_location_id=900,
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-location-duplicate",
        {"world_id": 101},
        policy="safe_existing_location_duplicate_only",
    )

    assert preview["eligible"] is False
    assert preview["reasons"] == [
        "Policy 'safe_existing_location_duplicate_only' rejected due to ambiguous staged canonical Location duplicate matches"
    ]


def test_preview_auto_merge_candidate_rejects_low_confidence_and_sparse_evidence(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-gates.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        exact_location_duplicate_bundle(
            candidate_id="cand-location-low-confidence",
            name="Ashen Keep",
            summary="Weak evidence for the same fortress.",
            run_id="run-location-low-confidence",
            confidence=0.85,
            evidence_count=2,
        )
    )
    importer.import_result_bundle(
        exact_location_duplicate_bundle(
            candidate_id="cand-location-sparse-evidence",
            name="Ashen Keep",
            summary="Only one witness mentions the same fortress.",
            run_id="run-location-sparse-evidence",
            confidence=0.95,
            evidence_count=1,
        )
    )

    low_confidence_preview = promoter.preview_auto_merge_candidate(
        "cand-location-low-confidence",
        {"world_id": 101},
        policy="safe_existing_location_duplicate_only",
    )
    sparse_evidence_preview = promoter.preview_auto_merge_candidate(
        "cand-location-sparse-evidence",
        {"world_id": 101},
        policy="safe_existing_location_duplicate_only",
    )

    assert low_confidence_preview["eligible"] is False
    assert low_confidence_preview["reasons"] == [
        "Policy 'safe_existing_location_duplicate_only' requires confidence >= 0.90"
    ]
    assert sparse_evidence_preview["eligible"] is False
    assert sparse_evidence_preview["reasons"] == [
        "Policy 'safe_existing_location_duplicate_only' requires at least 2 evidence items"
    ]


def test_preview_auto_merge_candidate_for_exact_duplicate_faction_is_side_effect_free(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-faction-preview.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        manual_candidate_bundle(
            candidate_id="cand-faction-create",
            target_canonical_type="Faction",
            name="Harbor Guild",
            summary="A disciplined merchant coalition controlling the docks.",
            run_id="run-faction-create",
        )
    )
    approved_create = _approve_candidate(store, candidate_type="new_entity_candidate", run_id="run-faction-create")
    promote_result = promoter.promote_candidate(
        approved_create["candidate_id"],
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
        exact_faction_duplicate_bundle(
            candidate_id="cand-faction-duplicate",
            name="  Harbor-Guild  ",
            summary="Scouts describe the same merchant coalition again.",
            run_id="run-faction-duplicate",
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-faction-duplicate",
        {"world_id": 101},
        policy="safe_existing_faction_duplicate_only",
    )

    detail = store.get_candidate("cand-faction-duplicate")

    assert preview["eligible"] is True
    assert preview["target_canonical_id"] == promote_result["canonical_entity"]["canonical_id"]
    assert preview["metadata_preview"]["auto_merge_policy"] == "safe_existing_faction_duplicate_only"
    assert preview["metadata_preview"]["merge_match_name"] == "harbor guild"
    assert preview["metadata_preview"]["merge_match_faction_type"] == "merchant"
    assert preview["metadata_preview"]["merge_match_alignment"] == "neutral"
    assert preview["metadata_preview"]["merge_match_leader_character_id"] == 501
    assert preview["metadata_preview"]["merge_match_is_joinable"] is False
    assert detail["status"] == "pending_review"
    assert detail["target_canonical_id"] is None
    assert store.list_entity_run_links(run_id="run-faction-duplicate", source_candidate_id="cand-faction-duplicate") == []


def test_auto_merge_candidate_merges_exact_duplicate_faction_candidate(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-faction-execute.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        manual_candidate_bundle(
            candidate_id="cand-faction-create",
            target_canonical_type="Faction",
            name="Harbor Guild",
            summary="A disciplined merchant coalition controlling the docks.",
            run_id="run-faction-create",
        )
    )
    approved_create = _approve_candidate(store, candidate_type="new_entity_candidate", run_id="run-faction-create")
    promote_result = promoter.promote_candidate(
        approved_create["candidate_id"],
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
        exact_faction_duplicate_bundle(
            candidate_id="cand-faction-duplicate",
            name="Harbor Guild",
            summary="A second run confirms the same merchant coalition.",
            run_id="run-faction-duplicate",
        )
    )

    result = promoter.auto_merge_candidate(
        "cand-faction-duplicate",
        {"world_id": 101},
        policy="safe_existing_faction_duplicate_only",
    )

    detail = store.get_candidate("cand-faction-duplicate")

    assert result["candidate"]["status"] == "merged"
    assert result["canonical_entity"]["canonical_id"] == promote_result["canonical_entity"]["canonical_id"]
    assert result["run_link"]["metadata"]["auto_merge_policy"] == "safe_existing_faction_duplicate_only"
    assert result["run_link"]["metadata"]["merge_match_faction_type"] == "merchant"
    assert result["run_link"]["metadata"]["merge_match_alignment"] == "neutral"
    assert result["run_link"]["metadata"]["merge_match_leader_character_id"] == 501
    assert result["run_link"]["metadata"]["merge_match_is_joinable"] is False
    assert detail["status"] == "merged"
    assert detail["target_canonical_id"] == str(promote_result["canonical_entity"]["canonical_id"])


def test_preview_auto_merge_candidate_rejects_when_no_exact_duplicate_faction_exists(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-faction-no-match.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        manual_candidate_bundle(
            candidate_id="cand-faction-create",
            target_canonical_type="Faction",
            name="Harbor Guild",
            summary="A disciplined merchant coalition controlling the docks.",
            run_id="run-faction-create",
        )
    )
    approved_create = _approve_candidate(store, candidate_type="new_entity_candidate", run_id="run-faction-create")
    promoter.promote_candidate(
        approved_create["candidate_id"],
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
        exact_faction_duplicate_bundle(
            candidate_id="cand-faction-no-match",
            name="Harbor Guild",
            summary="This report points to a different leadership snapshot.",
            run_id="run-faction-no-match",
            is_joinable=True,
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-faction-no-match",
        {"world_id": 101},
        policy="safe_existing_faction_duplicate_only",
    )

    assert preview["eligible"] is False
    assert preview["reasons"] == [
        "Policy 'safe_existing_faction_duplicate_only' requires exactly 1 staged canonical Faction exact duplicate match in the same world"
    ]


def test_preview_auto_merge_candidate_rejects_ambiguous_duplicate_factions(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-faction-ambiguous.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    for candidate_id, run_id in (("cand-faction-create-a", "run-faction-create-a"), ("cand-faction-create-b", "run-faction-create-b")):
        importer.import_result_bundle(
            manual_candidate_bundle(
                candidate_id=candidate_id,
                target_canonical_type="Faction",
                name="Harbor Guild",
                summary="A disciplined merchant coalition controlling the docks.",
                run_id=run_id,
            )
        )
        approved = _approve_candidate(store, candidate_type="new_entity_candidate", run_id=run_id)
        promoter.promote_candidate(
            approved["candidate_id"],
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
        exact_faction_duplicate_bundle(
            candidate_id="cand-faction-duplicate",
            name="Harbor Guild",
            summary="Another run repeats the same faction signature.",
            run_id="run-faction-duplicate",
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-faction-duplicate",
        {"world_id": 101},
        policy="safe_existing_faction_duplicate_only",
    )

    assert preview["eligible"] is False
    assert preview["reasons"] == [
        "Policy 'safe_existing_faction_duplicate_only' rejected due to ambiguous staged canonical Faction duplicate matches"
    ]


def test_preview_auto_merge_candidate_rejects_faction_duplicate_gates(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-faction-gates.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        exact_faction_duplicate_bundle(
            candidate_id="cand-faction-low-confidence",
            name="Harbor Guild",
            summary="Weak evidence for the same merchant coalition.",
            run_id="run-faction-low-confidence",
            confidence=0.89,
            evidence_count=2,
        )
    )
    importer.import_result_bundle(
        exact_faction_duplicate_bundle(
            candidate_id="cand-faction-sparse-evidence",
            name="Harbor Guild",
            summary="Only one witness mentions the same merchant coalition.",
            run_id="run-faction-sparse-evidence",
            confidence=0.95,
            evidence_count=1,
        )
    )

    low_confidence_preview = promoter.preview_auto_merge_candidate(
        "cand-faction-low-confidence",
        {"world_id": 101},
        policy="safe_existing_faction_duplicate_only",
    )
    sparse_evidence_preview = promoter.preview_auto_merge_candidate(
        "cand-faction-sparse-evidence",
        {"world_id": 101},
        policy="safe_existing_faction_duplicate_only",
    )

    assert low_confidence_preview["eligible"] is False
    assert low_confidence_preview["reasons"] == [
        "Policy 'safe_existing_faction_duplicate_only' requires confidence >= 0.90"
    ]
    assert sparse_evidence_preview["eligible"] is False
    assert sparse_evidence_preview["reasons"] == [
        "Policy 'safe_existing_faction_duplicate_only' requires at least 2 evidence items"
    ]


def test_preview_auto_merge_candidate_for_exact_duplicate_character_is_side_effect_free(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-character-preview.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        manual_candidate_bundle(
            candidate_id="cand-character-create",
            target_canonical_type="Character",
            name="Captain Aria",
            summary="A harbor defender whose public resolve hides years of sacrifice.",
            run_id="run-character-create",
        )
    )
    approved_create = _approve_candidate(store, candidate_type="new_entity_candidate", run_id="run-character-create")
    promote_result = promoter.promote_candidate(
        approved_create["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "backstory": long_backstory(),
            "status": "active",
            "location_id": 301,
            "rarity": "legendary",
            "element": "water",
            "role": "support",
        },
    )

    importer.import_result_bundle(
        exact_character_duplicate_bundle(
            candidate_id="cand-character-duplicate",
            name="  Captain-Aria  ",
            summary="A second run repeats the same character signature.",
            run_id="run-character-duplicate",
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-character-duplicate",
        {"world_id": 101},
        policy="safe_existing_character_duplicate_only",
    )

    detail = store.get_candidate("cand-character-duplicate")

    assert preview["eligible"] is True
    assert preview["target_canonical_id"] == promote_result["canonical_entity"]["canonical_id"]
    assert preview["metadata_preview"]["auto_merge_policy"] == "safe_existing_character_duplicate_only"
    assert preview["metadata_preview"]["merge_match_name"] == "captain aria"
    assert preview["metadata_preview"]["merge_match_status"] == "active"
    assert preview["metadata_preview"]["merge_match_location_id"] == 301
    assert preview["metadata_preview"]["merge_match_rarity"] == "legendary"
    assert preview["metadata_preview"]["merge_match_element"] == "water"
    assert preview["metadata_preview"]["merge_match_role"] == "support"
    assert detail["status"] == "pending_review"
    assert detail["target_canonical_id"] is None
    assert store.list_entity_run_links(run_id="run-character-duplicate", source_candidate_id="cand-character-duplicate") == []


def test_auto_merge_candidate_merges_exact_duplicate_character(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-character-execute.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        manual_candidate_bundle(
            candidate_id="cand-character-create",
            target_canonical_type="Character",
            name="Captain Aria",
            summary="A harbor defender whose public resolve hides years of sacrifice.",
            run_id="run-character-create",
        )
    )
    approved_create = _approve_candidate(store, candidate_type="new_entity_candidate", run_id="run-character-create")
    promote_result = promoter.promote_candidate(
        approved_create["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "backstory": long_backstory(),
            "status": "active",
            "location_id": 301,
            "rarity": "legendary",
            "element": "water",
            "role": "support",
        },
    )

    importer.import_result_bundle(
        exact_character_duplicate_bundle(
            candidate_id="cand-character-duplicate",
            name="Captain Aria",
            summary="A second run confirms the same character snapshot.",
            run_id="run-character-duplicate",
        )
    )

    result = promoter.auto_merge_candidate(
        "cand-character-duplicate",
        {"world_id": 101},
        policy="safe_existing_character_duplicate_only",
    )

    detail = store.get_candidate("cand-character-duplicate")

    assert result["candidate"]["status"] == "merged"
    assert result["canonical_entity"]["canonical_id"] == promote_result["canonical_entity"]["canonical_id"]
    assert result["run_link"]["metadata"]["auto_merge_policy"] == "safe_existing_character_duplicate_only"
    assert result["run_link"]["metadata"]["merge_match_status"] == "active"
    assert result["run_link"]["metadata"]["merge_match_location_id"] == 301
    assert result["run_link"]["metadata"]["merge_match_rarity"] == "legendary"
    assert result["run_link"]["metadata"]["merge_match_element"] == "water"
    assert result["run_link"]["metadata"]["merge_match_role"] == "support"
    assert detail["status"] == "merged"
    assert detail["target_canonical_id"] == str(promote_result["canonical_entity"]["canonical_id"])


def test_preview_auto_merge_candidate_rejects_when_no_exact_duplicate_character_exists(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-character-no-match.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        manual_candidate_bundle(
            candidate_id="cand-character-create",
            target_canonical_type="Character",
            name="Captain Aria",
            summary="A harbor defender whose public resolve hides years of sacrifice.",
            run_id="run-character-create",
        )
    )
    approved_create = _approve_candidate(store, candidate_type="new_entity_candidate", run_id="run-character-create")
    promoter.promote_candidate(
        approved_create["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "backstory": long_backstory(),
            "status": "active",
            "location_id": 301,
            "rarity": "legendary",
            "element": "water",
            "role": "support",
        },
    )

    importer.import_result_bundle(
        exact_character_duplicate_bundle(
            candidate_id="cand-character-no-match",
            name="Captain Aria",
            summary="This report points to a different combat role snapshot.",
            run_id="run-character-no-match",
            role="dps",
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-character-no-match",
        {"world_id": 101},
        policy="safe_existing_character_duplicate_only",
    )

    assert preview["eligible"] is False
    assert preview["reasons"] == [
        "Policy 'safe_existing_character_duplicate_only' requires exactly 1 staged canonical Character exact duplicate match in the same world"
    ]


def test_preview_auto_merge_candidate_rejects_ambiguous_duplicate_characters(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-character-ambiguous.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    for candidate_id, run_id in (("cand-character-create-a", "run-character-create-a"), ("cand-character-create-b", "run-character-create-b")):
        importer.import_result_bundle(
            manual_candidate_bundle(
                candidate_id=candidate_id,
                target_canonical_type="Character",
                name="Captain Aria",
                summary="A harbor defender whose public resolve hides years of sacrifice.",
                run_id=run_id,
            )
        )
        approved = _approve_candidate(store, candidate_type="new_entity_candidate", run_id=run_id)
        promoter.promote_candidate(
            approved["candidate_id"],
            {
                "tenant_id": 1,
                "world_id": 101,
                "backstory": long_backstory(),
                "status": "active",
                "location_id": 301,
                "rarity": "legendary",
                "element": "water",
                "role": "support",
            },
        )

    importer.import_result_bundle(
        exact_character_duplicate_bundle(
            candidate_id="cand-character-duplicate",
            name="Captain Aria",
            summary="Another run repeats the same character signature.",
            run_id="run-character-duplicate",
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-character-duplicate",
        {"world_id": 101},
        policy="safe_existing_character_duplicate_only",
    )

    assert preview["eligible"] is False
    assert preview["reasons"] == [
        "Policy 'safe_existing_character_duplicate_only' rejected due to ambiguous staged canonical Character duplicate matches"
    ]


def test_preview_auto_merge_candidate_rejects_character_duplicate_gates(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-character-gates.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        exact_character_duplicate_bundle(
            candidate_id="cand-character-low-confidence",
            name="Captain Aria",
            summary="Weak evidence repeats the same character snapshot.",
            run_id="run-character-low-confidence",
            confidence=0.89,
        )
    )
    importer.import_result_bundle(
        exact_character_duplicate_bundle(
            candidate_id="cand-character-sparse-evidence",
            name="Captain Aria",
            summary="Only one witness mentions the same character snapshot.",
            run_id="run-character-sparse-evidence",
            evidence_count=1,
        )
    )
    importer.import_result_bundle(
        exact_character_duplicate_bundle(
            candidate_id="cand-character-missing-role",
            name="Captain Aria",
            summary="The report omits a required combat role.",
            run_id="run-character-missing-role",
            role=None,
        )
    )

    low_confidence_preview = promoter.preview_auto_merge_candidate(
        "cand-character-low-confidence",
        {"world_id": 101},
        policy="safe_existing_character_duplicate_only",
    )
    sparse_evidence_preview = promoter.preview_auto_merge_candidate(
        "cand-character-sparse-evidence",
        {"world_id": 101},
        policy="safe_existing_character_duplicate_only",
    )
    missing_role_preview = promoter.preview_auto_merge_candidate(
        "cand-character-missing-role",
        {"world_id": 101},
        policy="safe_existing_character_duplicate_only",
    )

    assert low_confidence_preview["eligible"] is False
    assert low_confidence_preview["reasons"] == [
        "Policy 'safe_existing_character_duplicate_only' requires confidence >= 0.90"
    ]
    assert sparse_evidence_preview["eligible"] is False
    assert sparse_evidence_preview["reasons"] == [
        "Policy 'safe_existing_character_duplicate_only' requires at least 2 evidence items"
    ]
    assert missing_role_preview["eligible"] is False
    assert missing_role_preview["reasons"] == ["role is required"]


def test_preview_auto_merge_candidate_for_exact_duplicate_event_is_side_effect_free(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-event-preview.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        exact_event_duplicate_bundle(
            candidate_id="cand-event-create",
            run_id="run-event-create",
            outcome="success",
        )
    )
    approved_create = _approve_candidate(store, candidate_type="scenario_event", run_id="run-event-create")
    promote_result = promoter.promote_candidate(
        approved_create["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
            "outcome": "success",
            "location_id": 301,
        },
    )

    importer.import_result_bundle(
        exact_event_duplicate_bundle(
            candidate_id="cand-event-duplicate",
            run_id="run-event-duplicate",
            outcome="success",
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-event-duplicate",
        {
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
            "location_id": 301,
        },
        policy="safe_existing_event_duplicate_only",
    )

    detail = store.get_candidate("cand-event-duplicate")

    assert preview["eligible"] is True
    assert preview["target_canonical_id"] == promote_result["canonical_entity"]["canonical_id"]
    assert preview["metadata_preview"]["auto_merge_policy"] == "safe_existing_event_duplicate_only"
    assert preview["metadata_preview"]["event_match_outcome"] == "success"
    assert preview["metadata_preview"]["event_match_date_bucket"] == "2026-03-10"
    assert preview["metadata_preview"]["merge_match_location_id"] == 301
    assert detail["status"] == "pending_review"
    assert detail["target_canonical_id"] is None
    assert store.list_entity_run_links(run_id="run-event-duplicate", source_candidate_id="cand-event-duplicate") == []


def test_auto_merge_candidate_merges_exact_duplicate_event(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-event-execute.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        exact_event_duplicate_bundle(
            candidate_id="cand-event-create",
            run_id="run-event-create",
            outcome="success",
        )
    )
    approved_create = _approve_candidate(store, candidate_type="scenario_event", run_id="run-event-create")
    promote_result = promoter.promote_candidate(
        approved_create["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
            "outcome": "success",
            "location_id": 301,
        },
    )

    importer.import_result_bundle(
        exact_event_duplicate_bundle(
            candidate_id="cand-event-duplicate",
            run_id="run-event-duplicate",
            outcome="success",
        )
    )

    result = promoter.auto_merge_candidate(
        "cand-event-duplicate",
        {
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
            "location_id": 301,
        },
        policy="safe_existing_event_duplicate_only",
    )

    detail = store.get_candidate("cand-event-duplicate")

    assert result["candidate"]["status"] == "merged"
    assert result["canonical_entity"]["canonical_id"] == promote_result["canonical_entity"]["canonical_id"]
    assert result["run_link"]["metadata"]["auto_merge_policy"] == "safe_existing_event_duplicate_only"
    assert result["run_link"]["metadata"]["event_match_outcome"] == "success"
    assert result["run_link"]["metadata"]["event_match_date_bucket"] == "2026-03-10"
    assert result["run_link"]["metadata"]["merge_match_location_id"] == 301
    assert detail["status"] == "merged"
    assert detail["target_canonical_id"] == str(promote_result["canonical_entity"]["canonical_id"])


def test_preview_auto_merge_candidate_rejects_when_no_exact_duplicate_event_exists(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-event-no-match.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        exact_event_duplicate_bundle(
            candidate_id="cand-event-create",
            run_id="run-event-create",
            outcome="success",
        )
    )
    approved_create = _approve_candidate(store, candidate_type="scenario_event", run_id="run-event-create")
    promoter.promote_candidate(
        approved_create["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
            "outcome": "success",
            "location_id": 301,
        },
    )

    importer.import_result_bundle(
        exact_event_duplicate_bundle(
            candidate_id="cand-event-no-match",
            run_id="run-event-no-match",
            outcome="failure",
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-event-no-match",
        {
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
            "location_id": 301,
        },
        policy="safe_existing_event_duplicate_only",
    )

    assert preview["eligible"] is False
    assert preview["reasons"] == [
        "Policy 'safe_existing_event_duplicate_only' requires exactly 1 staged canonical Event exact duplicate match in the same world"
    ]


def test_preview_auto_merge_candidate_rejects_ambiguous_duplicate_events(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-event-ambiguous.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    for candidate_id, run_id in (("cand-event-create-a", "run-event-create-a"), ("cand-event-create-b", "run-event-create-b")):
        importer.import_result_bundle(
            exact_event_duplicate_bundle(
                candidate_id=candidate_id,
                run_id=run_id,
                outcome="success",
            )
        )
        approved = _approve_candidate(store, candidate_type="scenario_event", run_id=run_id)
        promoter.promote_candidate(
            approved["candidate_id"],
            {
                "tenant_id": 1,
                "world_id": 101,
                "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
                "outcome": "success",
                "location_id": 301,
            },
        )

    importer.import_result_bundle(
        exact_event_duplicate_bundle(
            candidate_id="cand-event-duplicate",
            run_id="run-event-duplicate",
            outcome="success",
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-event-duplicate",
        {
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
            "location_id": 301,
        },
        policy="safe_existing_event_duplicate_only",
    )

    assert preview["eligible"] is False
    assert preview["reasons"] == [
        "Policy 'safe_existing_event_duplicate_only' rejected due to ambiguous staged canonical Event duplicate matches"
    ]


def test_preview_auto_merge_candidate_rejects_event_duplicate_gates(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-event-gates.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        exact_event_duplicate_bundle(
            candidate_id="cand-event-ongoing",
            run_id="run-event-ongoing",
            outcome="ongoing",
        )
    )
    importer.import_result_bundle(
        exact_event_duplicate_bundle(
            candidate_id="cand-event-low-confidence",
            run_id="run-event-low-confidence",
            outcome="success",
            confidence=0.89,
        )
    )
    importer.import_result_bundle(
        exact_event_duplicate_bundle(
            candidate_id="cand-event-sparse-evidence",
            run_id="run-event-sparse-evidence",
            outcome="success",
            evidence_count=1,
        )
    )

    ongoing_preview = promoter.preview_auto_merge_candidate(
        "cand-event-ongoing",
        {"world_id": 101, "participant_map": {"actor:royal_court": 201, "org:royal_court": 202}, "location_id": 301},
        policy="safe_existing_event_duplicate_only",
    )
    low_confidence_preview = promoter.preview_auto_merge_candidate(
        "cand-event-low-confidence",
        {"world_id": 101, "participant_map": {"actor:royal_court": 201, "org:royal_court": 202}, "location_id": 301},
        policy="safe_existing_event_duplicate_only",
    )
    sparse_evidence_preview = promoter.preview_auto_merge_candidate(
        "cand-event-sparse-evidence",
        {"world_id": 101, "participant_map": {"actor:royal_court": 201, "org:royal_court": 202}, "location_id": 301},
        policy="safe_existing_event_duplicate_only",
    )

    assert ongoing_preview["eligible"] is False
    assert ongoing_preview["reasons"] == [
        "Policy 'safe_existing_event_duplicate_only' requires terminal non-ongoing outcome"
    ]
    assert low_confidence_preview["eligible"] is False
    assert low_confidence_preview["reasons"] == [
        "Policy 'safe_existing_event_duplicate_only' requires confidence >= 0.90"
    ]
    assert sparse_evidence_preview["eligible"] is False
    assert sparse_evidence_preview["reasons"] == [
        "Policy 'safe_existing_event_duplicate_only' requires at least 2 evidence items"
    ]


def test_preview_auto_merge_candidate_rejects_missing_event_duplicate_fields(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-event-missing-fields.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        exact_event_duplicate_bundle(
            candidate_id="cand-event-missing-participants",
            run_id="run-event-missing-participants",
            outcome="success",
            participant_ids=[],
        )
    )
    importer.import_result_bundle(
        exact_event_duplicate_bundle(
            candidate_id="cand-event-missing-timestamp",
            run_id="run-event-missing-timestamp",
            outcome="success",
            timestamp="",
        )
    )

    missing_participants_preview = promoter.preview_auto_merge_candidate(
        "cand-event-missing-participants",
        {"world_id": 101, "participant_map": {"actor:royal_court": 201, "org:royal_court": 202}, "location_id": 301},
        policy="safe_existing_event_duplicate_only",
    )
    missing_timestamp_preview = promoter.preview_auto_merge_candidate(
        "cand-event-missing-timestamp",
        {"world_id": 101, "participant_map": {"actor:royal_court": 201, "org:royal_court": 202}, "location_id": 301},
        policy="safe_existing_event_duplicate_only",
    )

    assert missing_participants_preview["eligible"] is False
    assert missing_participants_preview["reasons"] == [
        "Policy 'safe_existing_event_duplicate_only' requires proposed_change.participant_ids"
    ]
    assert missing_timestamp_preview["eligible"] is False
    assert missing_timestamp_preview["reasons"] == [
        "Policy 'safe_existing_event_duplicate_only' requires proposed_change.timestamp"
    ]


def test_preview_auto_merge_candidate_for_exact_duplicate_relationship_is_side_effect_free(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-relationship-preview.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-create",
            run_id="run-relationship-create",
            relationship_level=-42,
        )
    )
    approved_create = _approve_candidate(store, candidate_type="relationship_change", run_id="run-relationship-create")
    promote_result = promoter.promote_candidate(
        approved_create["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "character_from_id": 201,
            "character_to_id": 202,
            "relationship_level": -42,
            "is_mutual": False,
        },
    )

    importer.import_result_bundle(
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-duplicate",
            run_id="run-relationship-duplicate",
            relationship_level=-42,
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-relationship-duplicate",
        {
            "world_id": 101,
            "character_from_id": 201,
            "character_to_id": 202,
            "relationship_level": -42,
        },
        policy="safe_existing_relationship_duplicate_only",
    )

    detail = store.get_candidate("cand-relationship-duplicate")

    assert preview["eligible"] is True
    assert preview["target_canonical_id"] == promote_result["canonical_entity"]["canonical_id"]
    assert preview["metadata_preview"]["auto_merge_policy"] == "safe_existing_relationship_duplicate_only"
    assert preview["metadata_preview"]["merge_match_relationship_type"] == "enemy"
    assert preview["metadata_preview"]["merge_match_relationship_level"] == -42
    assert preview["metadata_preview"]["merge_match_is_mutual"] is False
    assert detail["status"] == "pending_review"
    assert detail["target_canonical_id"] is None
    assert store.list_entity_run_links(run_id="run-relationship-duplicate", source_candidate_id="cand-relationship-duplicate") == []


def test_auto_merge_candidate_merges_exact_duplicate_relationship(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-relationship-execute.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-create",
            run_id="run-relationship-create",
            relationship_level=-42,
        )
    )
    approved_create = _approve_candidate(store, candidate_type="relationship_change", run_id="run-relationship-create")
    promote_result = promoter.promote_candidate(
        approved_create["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "character_from_id": 201,
            "character_to_id": 202,
            "relationship_level": -42,
            "is_mutual": False,
        },
    )

    importer.import_result_bundle(
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-duplicate",
            run_id="run-relationship-duplicate",
            relationship_level=-42,
        )
    )

    result = promoter.auto_merge_candidate(
        "cand-relationship-duplicate",
        {
            "world_id": 101,
            "character_from_id": 201,
            "character_to_id": 202,
            "relationship_level": -42,
        },
        policy="safe_existing_relationship_duplicate_only",
    )

    detail = store.get_candidate("cand-relationship-duplicate")

    assert result["candidate"]["status"] == "merged"
    assert result["canonical_entity"]["canonical_id"] == promote_result["canonical_entity"]["canonical_id"]
    assert result["run_link"]["metadata"]["auto_merge_policy"] == "safe_existing_relationship_duplicate_only"
    assert result["run_link"]["metadata"]["merge_match_relationship_type"] == "enemy"
    assert result["run_link"]["metadata"]["merge_match_relationship_level"] == -42
    assert result["run_link"]["metadata"]["merge_match_is_mutual"] is False
    assert detail["status"] == "merged"
    assert detail["target_canonical_id"] == str(promote_result["canonical_entity"]["canonical_id"])


def test_preview_auto_merge_candidate_rejects_when_no_exact_duplicate_relationship_exists(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-relationship-no-match.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-create",
            run_id="run-relationship-create",
            relationship_level=-42,
        )
    )
    approved_create = _approve_candidate(store, candidate_type="relationship_change", run_id="run-relationship-create")
    promoter.promote_candidate(
        approved_create["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "character_from_id": 201,
            "character_to_id": 202,
            "relationship_level": -42,
            "is_mutual": False,
        },
    )

    importer.import_result_bundle(
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-no-match",
            run_id="run-relationship-no-match",
            relationship_level=-55,
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-relationship-no-match",
        {
            "world_id": 101,
            "character_from_id": 201,
            "character_to_id": 202,
            "relationship_level": -55,
        },
        policy="safe_existing_relationship_duplicate_only",
    )

    assert preview["eligible"] is False
    assert preview["reasons"] == [
        "Policy 'safe_existing_relationship_duplicate_only' requires exactly 1 staged canonical CharacterRelationship exact duplicate match in the same world"
    ]


def test_preview_auto_merge_candidate_rejects_ambiguous_duplicate_relationships(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-relationship-ambiguous.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    for candidate_id, run_id in (("cand-relationship-create-a", "run-relationship-create-a"), ("cand-relationship-create-b", "run-relationship-create-b")):
        importer.import_result_bundle(
            exact_relationship_duplicate_bundle(
                candidate_id=candidate_id,
                run_id=run_id,
                relationship_level=-42,
            )
        )
        approved = _approve_candidate(store, candidate_type="relationship_change", run_id=run_id)
        promoter.promote_candidate(
            approved["candidate_id"],
            {
                "tenant_id": 1,
                "world_id": 101,
                "character_from_id": 201,
                "character_to_id": 202,
                "relationship_level": -42,
                "is_mutual": False,
            },
        )

    importer.import_result_bundle(
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-duplicate",
            run_id="run-relationship-duplicate",
            relationship_level=-42,
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-relationship-duplicate",
        {
            "world_id": 101,
            "character_from_id": 201,
            "character_to_id": 202,
            "relationship_level": -42,
        },
        policy="safe_existing_relationship_duplicate_only",
    )

    assert preview["eligible"] is False
    assert preview["reasons"] == [
        "Policy 'safe_existing_relationship_duplicate_only' rejected due to ambiguous staged canonical CharacterRelationship duplicate matches"
    ]


def test_preview_auto_merge_candidate_rejects_relationship_duplicate_gates(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-relationship-gates.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-low-confidence",
            run_id="run-relationship-low-confidence",
            relationship_level=-42,
            confidence=0.89,
        )
    )
    importer.import_result_bundle(
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-sparse-evidence",
            run_id="run-relationship-sparse-evidence",
            relationship_level=-42,
            evidence_count=1,
        )
    )
    importer.import_result_bundle(
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-self",
            run_id="run-relationship-self",
            relationship_level=-42,
        )
    )
    importer.import_result_bundle(
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-weak",
            run_id="run-relationship-weak",
            relationship_level=-10,
        )
    )

    low_confidence_preview = promoter.preview_auto_merge_candidate(
        "cand-relationship-low-confidence",
        {"world_id": 101, "character_from_id": 201, "character_to_id": 202, "relationship_level": -42},
        policy="safe_existing_relationship_duplicate_only",
    )
    sparse_evidence_preview = promoter.preview_auto_merge_candidate(
        "cand-relationship-sparse-evidence",
        {"world_id": 101, "character_from_id": 201, "character_to_id": 202, "relationship_level": -42},
        policy="safe_existing_relationship_duplicate_only",
    )
    self_relationship_preview = promoter.preview_auto_merge_candidate(
        "cand-relationship-self",
        {"world_id": 101, "character_from_id": 201, "character_to_id": 201, "relationship_level": -42},
        policy="safe_existing_relationship_duplicate_only",
    )
    weak_preview = promoter.preview_auto_merge_candidate(
        "cand-relationship-weak",
        {"world_id": 101, "character_from_id": 201, "character_to_id": 202, "relationship_level": -10},
        policy="safe_existing_relationship_duplicate_only",
    )

    assert low_confidence_preview["eligible"] is False
    assert low_confidence_preview["reasons"] == [
        "Policy 'safe_existing_relationship_duplicate_only' requires confidence >= 0.90"
    ]
    assert sparse_evidence_preview["eligible"] is False
    assert sparse_evidence_preview["reasons"] == [
        "Policy 'safe_existing_relationship_duplicate_only' requires at least 2 evidence items"
    ]
    assert self_relationship_preview["eligible"] is False
    assert self_relationship_preview["reasons"] == [
        "Policy 'safe_existing_relationship_duplicate_only' requires two different characters"
    ]
    assert weak_preview["eligible"] is False
    assert weak_preview["reasons"] == [
        "Policy 'safe_existing_relationship_duplicate_only' requires abs(relationship_level) >= 30"
    ]


def test_preview_auto_merge_candidate_rejects_relationship_is_mutual_mismatch(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-relationship-mutual-mismatch.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-create",
            run_id="run-relationship-create",
            relationship_level=48,
        )
    )
    approved_create = _approve_candidate(store, candidate_type="relationship_change", run_id="run-relationship-create")
    promoter.promote_candidate(
        approved_create["candidate_id"],
        {
            "tenant_id": 1,
            "world_id": 101,
            "character_from_id": 201,
            "character_to_id": 202,
            "relationship_level": 48,
            "is_mutual": True,
        },
    )

    importer.import_result_bundle(
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-duplicate",
            run_id="run-relationship-duplicate",
            relationship_level=48,
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-relationship-duplicate",
        {
            "world_id": 101,
            "character_from_id": 201,
            "character_to_id": 202,
            "relationship_level": 48,
            "is_mutual": False,
        },
        policy="safe_existing_relationship_duplicate_only",
    )

    assert preview["eligible"] is False
    assert preview["reasons"] == [
        "Policy 'safe_existing_relationship_duplicate_only' requires exactly 1 staged canonical CharacterRelationship exact duplicate match in the same world"
    ]


def test_preview_auto_merge_candidate_for_exact_duplicate_rumor_is_side_effect_free(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-rumor-preview.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        exact_rumor_duplicate_bundle(
            candidate_id="cand-rumor-create",
            name="Bellfire Coup",
            summary="Whispers describe a coup brewing in Bellfire.",
            run_id="run-rumor-create",
        )
    )
    approved_create = _approve_candidate(store, candidate_type="rumor_candidate", run_id="run-rumor-create")
    promote_result = promoter.promote_candidate(
        approved_create["candidate_id"],
        {"tenant_id": 1, "world_id": 101, "location_id": 301},
    )

    importer.import_result_bundle(
        exact_rumor_duplicate_bundle(
            candidate_id="cand-rumor-duplicate",
            name="  Bellfire Coup  ",
            summary="A second run repeats the same rumor signature.",
            run_id="run-rumor-duplicate",
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-rumor-duplicate",
        {"world_id": 101},
        policy="safe_existing_rumor_duplicate_only",
    )

    detail = store.get_candidate("cand-rumor-duplicate")

    assert preview["eligible"] is True
    assert preview["target_canonical_id"] == promote_result["canonical_entity"]["canonical_id"]
    assert preview["metadata_preview"]["auto_merge_policy"] == "safe_existing_rumor_duplicate_only"
    assert preview["metadata_preview"]["merge_match_name"] == "bellfire coup"
    assert preview["metadata_preview"]["merge_match_source_name"] == "town criers"
    assert preview["metadata_preview"]["merge_match_location_id"] == 301
    assert preview["metadata_preview"]["rumor_truth_bucket"] == "Unverified"
    assert detail["status"] == "pending_review"
    assert detail["target_canonical_id"] is None
    assert store.list_entity_run_links(run_id="run-rumor-duplicate", source_candidate_id="cand-rumor-duplicate") == []


def test_auto_merge_candidate_merges_exact_duplicate_rumor(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-rumor-execute.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        exact_rumor_duplicate_bundle(
            candidate_id="cand-rumor-create",
            name="Bellfire Coup",
            summary="Whispers describe a coup brewing in Bellfire.",
            run_id="run-rumor-create",
            truth_level="partially_true",
        )
    )
    approved_create = _approve_candidate(store, candidate_type="rumor_candidate", run_id="run-rumor-create")
    promote_result = promoter.promote_candidate(
        approved_create["candidate_id"],
        {"tenant_id": 1, "world_id": 101, "location_id": 301},
    )

    importer.import_result_bundle(
        exact_rumor_duplicate_bundle(
            candidate_id="cand-rumor-duplicate",
            name="Bellfire Coup",
            summary="A second run repeats the same rumor signature.",
            run_id="run-rumor-duplicate",
            truth_level="partially_true",
        )
    )

    result = promoter.auto_merge_candidate(
        "cand-rumor-duplicate",
        {"world_id": 101, "truth_level": "partially_true"},
        policy="safe_existing_rumor_duplicate_only",
    )

    detail = store.get_candidate("cand-rumor-duplicate")

    assert result["candidate"]["status"] == "merged"
    assert result["canonical_entity"]["canonical_id"] == promote_result["canonical_entity"]["canonical_id"]
    assert result["run_link"]["metadata"]["auto_merge_policy"] == "safe_existing_rumor_duplicate_only"
    assert result["run_link"]["metadata"]["merge_match_source_name"] == "town criers"
    assert result["run_link"]["metadata"]["merge_match_location_id"] == 301
    assert result["run_link"]["metadata"]["rumor_truth_bucket"] == "Partially True"
    assert detail["status"] == "merged"
    assert detail["target_canonical_id"] == str(promote_result["canonical_entity"]["canonical_id"])


def test_preview_auto_merge_candidate_rejects_when_no_exact_duplicate_rumor_exists(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-rumor-no-match.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        exact_rumor_duplicate_bundle(
            candidate_id="cand-rumor-create",
            name="Bellfire Coup",
            summary="Whispers describe a coup brewing in Bellfire.",
            run_id="run-rumor-create",
        )
    )
    approved_create = _approve_candidate(store, candidate_type="rumor_candidate", run_id="run-rumor-create")
    promoter.promote_candidate(
        approved_create["candidate_id"],
        {"tenant_id": 1, "world_id": 101, "location_id": 301},
    )

    importer.import_result_bundle(
        exact_rumor_duplicate_bundle(
            candidate_id="cand-rumor-no-match",
            name="Harbor Fire",
            summary="A different rumor should stay pending review.",
            run_id="run-rumor-no-match",
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-rumor-no-match",
        {"world_id": 101},
        policy="safe_existing_rumor_duplicate_only",
    )

    assert preview["eligible"] is False
    assert preview["reasons"] == [
        "Policy 'safe_existing_rumor_duplicate_only' requires exactly 1 staged canonical Rumor exact duplicate match in the same world"
    ]


def test_preview_auto_merge_candidate_rejects_ambiguous_duplicate_rumors(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-rumor-ambiguous.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    for candidate_id, run_id, source_name in (
        ("cand-rumor-create-a", "run-rumor-create-a", "Town criers"),
        ("cand-rumor-create-b", "run-rumor-create-b", "  Town-criers  "),
    ):
        importer.import_result_bundle(
            exact_rumor_duplicate_bundle(
                candidate_id=candidate_id,
                name="Bellfire Coup",
                summary="Whispers describe a coup brewing in Bellfire.",
                run_id=run_id,
                source_name=source_name,
            )
        )
        approved = _approve_candidate(store, candidate_type="rumor_candidate", run_id=run_id)
        promoter.promote_candidate(
            approved["candidate_id"],
            {"tenant_id": 1, "world_id": 101, "location_id": 301},
        )

    importer.import_result_bundle(
        exact_rumor_duplicate_bundle(
            candidate_id="cand-rumor-duplicate",
            name="Bellfire Coup",
            summary="A second run repeats the same rumor signature.",
            run_id="run-rumor-duplicate",
        )
    )

    preview = promoter.preview_auto_merge_candidate(
        "cand-rumor-duplicate",
        {"world_id": 101},
        policy="safe_existing_rumor_duplicate_only",
    )

    assert preview["eligible"] is False
    assert preview["reasons"] == [
        "Policy 'safe_existing_rumor_duplicate_only' rejected due to ambiguous staged canonical Rumor duplicate matches"
    ]


def test_preview_auto_merge_candidate_rejects_resolved_truth_low_confidence_and_sparse_rumor_evidence(tmp_path):
    store = MiroFishWriteBackStore(tmp_path / "auto-merge-rumor-gates.db")
    importer = MiroFishResultImporter(store)
    promoter = MiroFishCandidatePromoter(store)

    importer.import_result_bundle(
        exact_rumor_duplicate_bundle(
            candidate_id="cand-rumor-resolved",
            name="Bellfire Coup",
            summary="The rumor is already treated as true.",
            run_id="run-rumor-resolved",
            truth_level="true",
        )
    )
    importer.import_result_bundle(
        exact_rumor_duplicate_bundle(
            candidate_id="cand-rumor-low-confidence",
            name="Bellfire Coup",
            summary="Weak evidence for the same rumor.",
            run_id="run-rumor-low-confidence",
            confidence=0.85,
        )
    )
    importer.import_result_bundle(
        exact_rumor_duplicate_bundle(
            candidate_id="cand-rumor-sparse-evidence",
            name="Bellfire Coup",
            summary="Only one witness mentions the same rumor.",
            run_id="run-rumor-sparse-evidence",
            evidence_count=1,
        )
    )

    resolved_preview = promoter.preview_auto_merge_candidate(
        "cand-rumor-resolved",
        {"world_id": 101},
        policy="safe_existing_rumor_duplicate_only",
    )
    low_confidence_preview = promoter.preview_auto_merge_candidate(
        "cand-rumor-low-confidence",
        {"world_id": 101},
        policy="safe_existing_rumor_duplicate_only",
    )
    sparse_evidence_preview = promoter.preview_auto_merge_candidate(
        "cand-rumor-sparse-evidence",
        {"world_id": 101},
        policy="safe_existing_rumor_duplicate_only",
    )

    assert resolved_preview["eligible"] is False
    assert resolved_preview["reasons"] == [
        "Policy 'safe_existing_rumor_duplicate_only' only supports unresolved truth levels (Unverified or Partially True)"
    ]
    assert low_confidence_preview["eligible"] is False
    assert low_confidence_preview["reasons"] == [
        "Policy 'safe_existing_rumor_duplicate_only' requires confidence >= 0.90"
    ]
    assert sparse_evidence_preview["eligible"] is False
    assert sparse_evidence_preview["reasons"] == [
        "Policy 'safe_existing_rumor_duplicate_only' requires at least 2 evidence items"
    ]