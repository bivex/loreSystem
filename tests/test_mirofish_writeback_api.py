import io
import json

from src.presentation.api import create_writeback_app


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
            "rumors": [{"name": "Forged decree rumor", "summary": "Town criers amplify doubts.", "actor_refs": ["org:town_criers"], "confidence": 0.74}],
        },
        "emergent_events": [{"name": event_name, "description": "The Royal Court publicly denies the forgery.", "participant_ids": ["actor:royal_court", "org:royal_court"], "confidence": 0.81}],
        "relationship_changes": [{"name": "Captain Serik distrusts Nessa", "summary": "Trust drops after the rumor spike.", "actor_refs": ["actor:captain_serik", "actor:nessa"], "confidence": 0.67}],
    }


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
                "text": "Captain Serik and Nessa repeat the same relationship shift.",
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


def call_json(app, method: str, path: str, payload: dict | None = None):
    body = json.dumps(payload).encode("utf-8") if payload is not None else b""
    query_string = ""
    if "?" in path:
        path, query_string = path.split("?", 1)
    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": query_string,
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.input": io.BytesIO(body),
    }
    captured: dict[str, object] = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    response_body = b"".join(app(environ, start_response))
    return int(str(captured["status"]).split()[0]), json.loads(response_body.decode("utf-8"))


def test_ingest_endpoint_imports_result_bundle(tmp_path):
    app = create_writeback_app(str(tmp_path / "api.db"))

    status, payload = call_json(app, "POST", "/api/mirofish/writeback/ingest", sample_result_bundle())

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["run_id"] == "run-123"
    assert payload["data"]["runtime_evidence_saved"] == 4
    assert payload["data"]["candidate_deltas_saved"] == 3
    assert payload["data"]["subjects_saved"] == 5


def test_candidate_review_endpoint_lists_and_filters_candidates(tmp_path):
    app = create_writeback_app(str(tmp_path / "review.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", sample_result_bundle())

    status, payload = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas?world_id=world-1&candidate_type=rumor_candidate")

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["count"] == 1
    assert payload["data"]["candidates"][0]["candidate_type"] == "rumor_candidate"
    assert payload["data"]["candidates"][0]["evidence_count"] >= 0


def test_candidate_detail_endpoint_returns_full_candidate_context(tmp_path):
    app = create_writeback_app(str(tmp_path / "candidate-detail.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", sample_result_bundle())

    list_status, list_payload = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas?candidate_type=rumor_candidate")
    candidate_id = list_payload["data"]["candidates"][0]["candidate_id"]

    status, payload = call_json(app, "GET", f"/api/mirofish/writeback/candidate-deltas/{candidate_id}")

    assert list_status == 200
    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["candidate_id"] == candidate_id
    assert payload["data"]["candidate_type"] == "rumor_candidate"
    assert payload["data"]["evidence_count"] == len(payload["data"]["evidence_ids"])
    assert payload["data"]["canonical_entity"] is None
    assert payload["data"]["run_links"] == []


def test_candidate_detail_endpoint_includes_canonical_context_after_promote(tmp_path):
    app = create_writeback_app(str(tmp_path / "candidate-detail-promoted.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", sample_result_bundle())
    list_status, list_payload = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas?candidate_type=scenario_event")
    candidate_id = list_payload["data"]["candidates"][0]["candidate_id"]

    call_json(app, "POST", f"/api/mirofish/writeback/candidate-deltas/{candidate_id}/approve")
    promote_status, promote_payload = call_json(
        app,
        "POST",
        f"/api/mirofish/writeback/candidate-deltas/{candidate_id}/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201},
            "outcome": "success",
        },
    )

    status, payload = call_json(app, "GET", f"/api/mirofish/writeback/candidate-deltas/{candidate_id}")

    assert list_status == 200
    assert promote_status == 200
    assert status == 200
    assert payload["data"]["candidate_id"] == candidate_id
    assert payload["data"]["status"] == "promoted"
    assert payload["data"]["canonical_entity"]["canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert payload["data"]["canonical_entity"]["canonical_type"] == "Event"
    assert payload["data"]["run_links"][0]["source_candidate_id"] == candidate_id
    assert payload["data"]["run_links"][0]["entity_provenance"]["metadata"]["provenance"]["relation_type"] == "promoted_from"
    assert payload["data"]["canonical_entity"]["entity_provenance"][0]["metadata"]["provenance"]["canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]


def test_candidate_detail_endpoint_includes_canonical_context_after_merge(tmp_path):
    app = create_writeback_app(str(tmp_path / "candidate-detail-merged.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", sample_result_bundle())
    first_candidates = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas?candidate_type=scenario_event")[1]["data"]["candidates"]
    first_candidate_id = first_candidates[0]["candidate_id"]

    call_json(app, "POST", f"/api/mirofish/writeback/candidate-deltas/{first_candidate_id}/approve")
    promote_payload = call_json(
        app,
        "POST",
        f"/api/mirofish/writeback/candidate-deltas/{first_candidate_id}/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201},
            "outcome": "success",
        },
    )[1]

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        sample_result_bundle(run_id="run-456", generated_at="2026-03-10T13:00:00Z", event_name="Court repeats denial"),
    )
    second_candidates = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas?candidate_type=scenario_event")[1]["data"]["candidates"]
    second_candidate_id = [item for item in second_candidates if item["run_id"] == "run-456"][0]["candidate_id"]
    call_json(app, "POST", f"/api/mirofish/writeback/candidate-deltas/{second_candidate_id}/approve")
    call_json(
        app,
        "POST",
        f"/api/mirofish/writeback/candidate-deltas/{second_candidate_id}/merge",
        {
            "canonical_id": promote_payload["data"]["canonical_entity"]["canonical_id"],
            "metadata": {"reason": "same event"},
        },
    )

    status, payload = call_json(app, "GET", f"/api/mirofish/writeback/candidate-deltas/{second_candidate_id}")

    assert status == 200
    assert payload["data"]["candidate_id"] == second_candidate_id
    assert payload["data"]["status"] == "merged"
    assert payload["data"]["canonical_entity"]["canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert payload["data"]["run_links"][0]["relation_type"] == "merged_into"


def test_candidate_detail_endpoint_returns_404_for_missing_candidate(tmp_path):
    app = create_writeback_app(str(tmp_path / "candidate-detail-missing.db"))

    status, payload = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-missing")

    assert status == 404
    assert payload["success"] is False


def test_run_detail_and_evidence_endpoints_return_review_context(tmp_path):
    app = create_writeback_app(str(tmp_path / "context.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", sample_result_bundle())

    run_status, run_payload = call_json(app, "GET", "/api/mirofish/writeback/runs/run-123")
    evidence_status, evidence_payload = call_json(app, "GET", "/api/mirofish/writeback/runs/run-123/evidence")

    assert run_status == 200
    assert run_payload["data"]["scenario_id"] == "succession-crisis"
    assert run_payload["data"]["subjects"]["count"] == 5
    assert len(run_payload["data"]["subjects"]["actors"]) == 3
    assert len(run_payload["data"]["subjects"]["organizations"]) == 2
    assert evidence_status == 200
    assert evidence_payload["data"]["run_id"] == "run-123"
    assert evidence_payload["data"]["count"] == 4
    assert any(any(subject["subject_ref"] == "org:town_criers" for subject in item["linked_subjects"]) for item in evidence_payload["data"]["evidence"])
    assert run_payload["data"]["entity_run_links"] == []


def test_run_detail_endpoint_exposes_persisted_entity_run_links_after_promote_and_merge(tmp_path):
    app = create_writeback_app(str(tmp_path / "context-links.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", sample_result_bundle())
    first_candidates = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas?candidate_type=scenario_event")[1]["data"]["candidates"]
    first_candidate_id = first_candidates[0]["candidate_id"]

    call_json(app, "POST", f"/api/mirofish/writeback/candidate-deltas/{first_candidate_id}/approve")
    promote_payload = call_json(
        app,
        "POST",
        f"/api/mirofish/writeback/candidate-deltas/{first_candidate_id}/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201},
            "outcome": "success",
        },
    )[1]

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        sample_result_bundle(run_id="run-456", generated_at="2026-03-10T13:00:00Z", event_name="Court repeats denial"),
    )
    second_candidates = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas?candidate_type=scenario_event")[1]["data"]["candidates"]
    second_candidate_id = [item for item in second_candidates if item["run_id"] == "run-456"][0]["candidate_id"]
    call_json(app, "POST", f"/api/mirofish/writeback/candidate-deltas/{second_candidate_id}/approve")
    call_json(
        app,
        "POST",
        f"/api/mirofish/writeback/candidate-deltas/{second_candidate_id}/merge",
        {
            "canonical_id": promote_payload["data"]["canonical_entity"]["canonical_id"],
            "metadata": {"reason": "same event"},
        },
    )

    first_run_payload = call_json(app, "GET", "/api/mirofish/writeback/runs/run-123")[1]
    second_run_payload = call_json(app, "GET", "/api/mirofish/writeback/runs/run-456")[1]

    assert len(first_run_payload["data"]["entity_run_links"]) == 1
    assert first_run_payload["data"]["entity_run_links"][0]["canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert first_run_payload["data"]["entity_run_links"][0]["source_candidate_id"] == first_candidate_id
    assert first_run_payload["data"]["entity_run_links"][0]["relation_type"] == "promoted_from"
    assert first_run_payload["data"]["entity_run_links"][0]["metadata"]["candidate_type"] == "scenario_event"
    assert first_run_payload["data"]["entity_run_links"][0]["metadata"]["provenance"]["source_backend"] == "mirofish"
    assert first_run_payload["data"]["entity_run_links"][0]["entity_provenance"]["metadata"]["provenance"]["canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert first_run_payload["data"]["generation_run"]["run_kind"] == "mirofish_writeback"
    assert first_run_payload["data"]["entity_provenance"][0]["metadata"]["provenance"]["relation_type"] == "promoted_from"
    assert len(second_run_payload["data"]["entity_run_links"]) == 1
    assert second_run_payload["data"]["entity_run_links"][0]["canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert second_run_payload["data"]["entity_run_links"][0]["source_candidate_id"] == second_candidate_id
    assert second_run_payload["data"]["entity_run_links"][0]["relation_type"] == "merged_into"
    assert second_run_payload["data"]["entity_run_links"][0]["metadata"]["reason"] == "same event"
    assert second_run_payload["data"]["entity_run_links"][0]["evidence_ids"] != []
    assert second_run_payload["data"]["entity_provenance"][0]["metadata"]["provenance"]["relation_type"] == "merged_into"


def test_review_action_endpoints_approve_and_reject_candidates(tmp_path):
    app = create_writeback_app(str(tmp_path / "actions.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", sample_result_bundle())

    list_status, list_payload = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas?candidate_type=rumor_candidate")
    candidate_id = list_payload["data"]["candidates"][0]["candidate_id"]

    approve_status, approve_payload = call_json(app, "POST", f"/api/mirofish/writeback/candidate-deltas/{candidate_id}/approve")
    approved_list_status, approved_list_payload = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas?status=approved")
    reject_status, reject_payload = call_json(app, "POST", f"/api/mirofish/writeback/candidate-deltas/{candidate_id}/reject")

    assert list_status == 200
    assert approve_status == 200
    assert approve_payload["data"]["action"] == "approve"
    assert approve_payload["data"]["candidate"]["status"] == "approved"
    assert approved_list_status == 200
    assert approved_list_payload["data"]["count"] == 1
    assert reject_status == 200
    assert reject_payload["data"]["action"] == "reject"
    assert reject_payload["data"]["candidate"]["status"] == "rejected"


def test_batch_review_endpoint_processes_multiple_candidates_with_partial_failures(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-review.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", sample_result_bundle())

    candidates = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas")[1]["data"]["candidates"]
    candidate_ids = [item["candidate_id"] for item in candidates[:2]]

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/review",
        {"action": "approve", "candidate_ids": [candidate_ids[0], "cand-missing", candidate_ids[1]]},
    )

    approved_candidates = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas?status=approved")[1]["data"]["candidates"]
    approved_ids = {item["candidate_id"] for item in approved_candidates}

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["action"] == "approve"
    assert payload["data"]["requested_count"] == 3
    assert payload["data"]["success_count"] == 2
    assert payload["data"]["failure_count"] == 1
    assert {item["candidate"]["candidate_id"] for item in payload["data"]["succeeded"]} == set(candidate_ids)
    assert payload["data"]["failed"][0]["candidate_id"] == "cand-missing"
    assert set(candidate_ids).issubset(approved_ids)


def test_batch_review_endpoint_rejects_invalid_payload(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-review-bad.db"))

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/review",
        {"action": "archive", "candidate_ids": []},
    )

    assert status == 400
    assert payload["success"] is False


def test_review_action_endpoint_returns_404_for_missing_candidate(tmp_path):
    app = create_writeback_app(str(tmp_path / "missing.db"))

    status, payload = call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-missing/approve")

    assert status == 404
    assert payload["success"] is False


def test_promote_endpoint_maps_approved_candidate_to_canonical_entity(tmp_path):
    app = create_writeback_app(str(tmp_path / "promote.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", sample_result_bundle())
    list_status, list_payload = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas?candidate_type=scenario_event")
    candidate_id = list_payload["data"]["candidates"][0]["candidate_id"]

    call_json(app, "POST", f"/api/mirofish/writeback/candidate-deltas/{candidate_id}/approve")
    status, payload = call_json(
        app,
        "POST",
        f"/api/mirofish/writeback/candidate-deltas/{candidate_id}/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201},
            "outcome": "success",
        },
    )

    assert list_status == 200
    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["canonical_entity"]["canonical_type"] == "Event"
    assert payload["data"]["canonical_entity"]["entity"]["participant_ids"] == [201]
    assert payload["data"]["run_link"]["run_id"] == "run-123"
    assert payload["data"]["canonical_entity"]["run_links"][0]["relation_type"] == "promoted_from"
    assert payload["data"]["candidate"]["status"] == "promoted"


def test_promote_endpoint_requires_approved_candidate(tmp_path):
    app = create_writeback_app(str(tmp_path / "promote-gate.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", sample_result_bundle())
    list_status, list_payload = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas?candidate_type=scenario_event")
    candidate_id = list_payload["data"]["candidates"][0]["candidate_id"]

    status, payload = call_json(
        app,
        "POST",
        f"/api/mirofish/writeback/candidate-deltas/{candidate_id}/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201},
        },
    )

    assert list_status == 200
    assert status == 400
    assert payload["success"] is False


def test_batch_promote_endpoint_processes_multiple_candidates_with_partial_failures(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-promote.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", sample_result_bundle())
    candidates = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas")[1]["data"]["candidates"]
    event_candidate_id = next(item["candidate_id"] for item in candidates if item["candidate_type"] == "scenario_event")
    rumor_candidate_id = next(item["candidate_id"] for item in candidates if item["candidate_type"] == "rumor_candidate")

    call_json(app, "POST", f"/api/mirofish/writeback/candidate-deltas/{event_candidate_id}/approve")

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/promote",
        {
            "items": [
                {
                    "candidate_id": event_candidate_id,
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "participant_map": {"actor:royal_court": 201},
                        "outcome": "success",
                    },
                },
                {
                    "candidate_id": rumor_candidate_id,
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                    },
                },
                {
                    "candidate_id": "cand-missing",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                    },
                },
            ]
        },
    )

    event_detail = call_json(app, "GET", f"/api/mirofish/writeback/candidate-deltas/{event_candidate_id}")[1]["data"]
    rumor_detail = call_json(app, "GET", f"/api/mirofish/writeback/candidate-deltas/{rumor_candidate_id}")[1]["data"]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["requested_count"] == 3
    assert payload["data"]["success_count"] == 1
    assert payload["data"]["failure_count"] == 2
    assert payload["data"]["succeeded"][0]["candidate_id"] == event_candidate_id
    assert payload["data"]["succeeded"][0]["candidate"]["status"] == "promoted"
    failed_ids = {item["candidate_id"] for item in payload["data"]["failed"]}
    assert failed_ids == {rumor_candidate_id, "cand-missing"}
    assert event_detail["status"] == "promoted"
    assert rumor_detail["status"] == "pending_review"


def test_batch_promote_endpoint_rejects_invalid_payload(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-promote-bad.db"))

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/promote",
        {"items": []},
    )

    assert status == 400
    assert payload["success"] is False


def test_batch_auto_promote_endpoint_processes_policy_gated_items(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-promote.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", policy_ready_bundle(low_confidence_event=True, include_rumor_candidate=True))

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-promote",
        {
            "policy": "safe_event_only",
            "items": [
                {
                    "candidate_id": "cand-event-safe",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "participant_map": {"actor:royal_court": 201},
                        "outcome": "success",
                    },
                },
                {
                    "candidate_id": "cand-event-low",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "participant_map": {"actor:royal_court": 201},
                    },
                },
                {
                    "candidate_id": "cand-rumor-safe",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "location_id": 301,
                    },
                },
                {
                    "candidate_id": "cand-missing",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                    },
                },
            ],
        },
    )

    safe_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-event-safe")[1]["data"]
    low_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-event-low")[1]["data"]
    rumor_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-rumor-safe")[1]["data"]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_event_only"
    assert payload["data"]["requested_count"] == 4
    assert payload["data"]["success_count"] == 1
    assert payload["data"]["failure_count"] == 3
    assert payload["data"]["succeeded"][0]["candidate_id"] == "cand-event-safe"
    assert payload["data"]["succeeded"][0]["candidate"]["status"] == "promoted"
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["auto_promote_policy"] == "safe_event_only"
    failed_ids = {item["candidate_id"] for item in payload["data"]["failed"]}
    assert failed_ids == {"cand-event-low", "cand-rumor-safe", "cand-missing"}
    assert safe_detail["status"] == "promoted"
    assert low_detail["status"] == "pending_review"
    assert rumor_detail["status"] == "pending_review"


def test_batch_auto_promote_endpoint_supports_safe_rumor_policy(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-promote-rumor.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", policy_ready_bundle(include_rumor_candidate=True))

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-promote",
        {
            "policy": "safe_rumor_only",
            "items": [
                {
                    "candidate_id": "cand-rumor-safe",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "source_name": "Town criers",
                        "credibility_score": 7,
                        "location_id": 301,
                    },
                },
                {
                    "candidate_id": "cand-event-safe",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "participant_map": {"actor:royal_court": 201},
                    },
                },
            ],
        },
    )

    rumor_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-rumor-safe")[1]["data"]
    event_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-event-safe")[1]["data"]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_rumor_only"
    assert payload["data"]["requested_count"] == 2
    assert payload["data"]["success_count"] == 1
    assert payload["data"]["failure_count"] == 1
    assert payload["data"]["succeeded"][0]["candidate_id"] == "cand-rumor-safe"
    assert payload["data"]["succeeded"][0]["candidate"]["status"] == "promoted"
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["auto_promote_policy"] == "safe_rumor_only"
    assert {item["candidate_id"] for item in payload["data"]["failed"]} == {"cand-event-safe"}
    assert rumor_detail["status"] == "promoted"
    assert event_detail["status"] == "pending_review"


def test_batch_auto_promote_endpoint_supports_safe_relationship_policy(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-promote-relationship.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", policy_ready_bundle(include_relationship_candidate=True))

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-promote",
        {
            "policy": "safe_relationship_only",
            "items": [
                {
                    "candidate_id": "cand-relationship-safe",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "character_from_id": 201,
                        "character_to_id": 202,
                        "relationship_level": -42,
                        "is_mutual": False,
                    },
                },
                {
                    "candidate_id": "cand-event-safe",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "participant_map": {"actor:royal_court": 201},
                    },
                },
            ],
        },
    )

    relationship_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-relationship-safe")[1]["data"]
    event_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-event-safe")[1]["data"]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_relationship_only"
    assert payload["data"]["requested_count"] == 2
    assert payload["data"]["success_count"] == 1
    assert payload["data"]["failure_count"] == 1
    assert payload["data"]["succeeded"][0]["candidate_id"] == "cand-relationship-safe"
    assert payload["data"]["succeeded"][0]["candidate"]["status"] == "promoted"
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["auto_promote_policy"] == "safe_relationship_only"
    assert {item["candidate_id"] for item in payload["data"]["failed"]} == {"cand-event-safe"}
    assert relationship_detail["status"] == "promoted"
    assert event_detail["status"] == "pending_review"


def test_batch_auto_promote_endpoint_supports_cross_run_relationship_policy(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-promote-cross-run-relationship.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", cross_run_relationship_bundle(run_id="run-rel-primary", candidate_id="cand-relationship-primary", relationship_level=-42))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", cross_run_relationship_bundle(run_id="run-rel-support", candidate_id="cand-relationship-support", relationship_level=-55))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", cross_run_relationship_bundle(run_id="run-rel-solo", candidate_id="cand-relationship-solo", relationship_level=44))

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-promote",
        {
            "policy": "safe_cross_run_relationship_only",
            "items": [
                {
                    "candidate_id": "cand-relationship-primary",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "character_from_id": 201,
                        "character_to_id": 202,
                        "relationship_level": -42,
                        "is_mutual": False,
                    },
                },
                {
                    "candidate_id": "cand-relationship-solo",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "character_from_id": 201,
                        "character_to_id": 202,
                        "relationship_level": 44,
                        "is_mutual": False,
                    },
                },
            ],
        },
    )

    primary_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-relationship-primary")[1]["data"]
    solo_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-relationship-solo")[1]["data"]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_cross_run_relationship_only"
    assert payload["data"]["requested_count"] == 2
    assert payload["data"]["success_count"] == 1
    assert payload["data"]["failure_count"] == 1
    assert payload["data"]["succeeded"][0]["candidate_id"] == "cand-relationship-primary"
    assert payload["data"]["succeeded"][0]["candidate"]["status"] == "promoted"
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["auto_promote_policy"] == "safe_cross_run_relationship_only"
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["cross_run_supporting_run_ids"] == ["run-rel-support"]
    assert {item["candidate_id"] for item in payload["data"]["failed"]} == {"cand-relationship-solo"}
    assert primary_detail["status"] == "promoted"
    assert solo_detail["status"] == "pending_review"


def test_batch_auto_promote_endpoint_supports_cross_run_event_policy(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-promote-cross-run-event.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", cross_run_event_bundle(run_id="run-event-primary", candidate_id="cand-event-primary", outcome="success"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", cross_run_event_bundle(run_id="run-event-support", candidate_id="cand-event-support", outcome="success"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", cross_run_event_bundle(run_id="run-event-solo", candidate_id="cand-event-solo", outcome="failure"))

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-promote",
        {
            "policy": "safe_cross_run_event_only",
            "items": [
                {
                    "candidate_id": "cand-event-primary",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
                        "outcome": "success",
                        "location_id": 301,
                    },
                },
                {
                    "candidate_id": "cand-event-solo",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
                        "outcome": "failure",
                    },
                },
            ],
        },
    )

    primary_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-event-primary")[1]["data"]
    solo_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-event-solo")[1]["data"]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_cross_run_event_only"
    assert payload["data"]["requested_count"] == 2
    assert payload["data"]["success_count"] == 1
    assert payload["data"]["failure_count"] == 1
    assert payload["data"]["succeeded"][0]["candidate_id"] == "cand-event-primary"
    assert payload["data"]["succeeded"][0]["candidate"]["status"] == "promoted"
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["auto_promote_policy"] == "safe_cross_run_event_only"
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["cross_run_supporting_run_ids"] == ["run-event-support"]
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["event_match_outcome"] == "success"
    assert {item["candidate_id"] for item in payload["data"]["failed"]} == {"cand-event-solo"}
    assert primary_detail["status"] == "promoted"
    assert solo_detail["status"] == "pending_review"


def test_batch_auto_promote_endpoint_supports_cross_run_rumor_policy(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-promote-cross-run-rumor.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", cross_run_rumor_bundle(run_id="run-rumor-primary", candidate_id="cand-rumor-primary"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", cross_run_rumor_bundle(run_id="run-rumor-support", candidate_id="cand-rumor-support", name=" forged decree rumor ", source_name=" town criers "))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", cross_run_rumor_bundle(run_id="run-rumor-solo", candidate_id="cand-rumor-solo", name="Harbor poison rumor", source_name="Dockworkers"))

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-promote",
        {
            "policy": "safe_cross_run_rumor_only",
            "items": [
                {
                    "candidate_id": "cand-rumor-primary",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "source_name": "Town criers",
                        "credibility_score": 7,
                        "location_id": 301,
                    },
                },
                {
                    "candidate_id": "cand-rumor-solo",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "source_name": "Dockworkers",
                        "credibility_score": 6,
                        "location_id": 301,
                    },
                },
            ],
        },
    )

    primary_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-rumor-primary")[1]["data"]
    solo_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-rumor-solo")[1]["data"]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_cross_run_rumor_only"
    assert payload["data"]["requested_count"] == 2
    assert payload["data"]["success_count"] == 1
    assert payload["data"]["failure_count"] == 1
    assert payload["data"]["succeeded"][0]["candidate_id"] == "cand-rumor-primary"
    assert payload["data"]["succeeded"][0]["candidate"]["status"] == "promoted"
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["auto_promote_policy"] == "safe_cross_run_rumor_only"
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["cross_run_supporting_run_ids"] == ["run-rumor-support"]
    assert {item["candidate_id"] for item in payload["data"]["failed"]} == {"cand-rumor-solo"}
    assert primary_detail["status"] == "promoted"
    assert solo_detail["status"] == "pending_review"


def test_batch_auto_promote_endpoint_supports_dry_run_preview_without_side_effects(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-promote-dry-run.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", policy_ready_bundle(low_confidence_event=True, include_rumor_candidate=True))

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-promote",
        {
            "policy": "safe_event_only",
            "dry_run": True,
            "items": [
                {
                    "candidate_id": "cand-event-safe",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "participant_map": {"actor:royal_court": 201},
                        "outcome": "success",
                    },
                },
                {
                    "candidate_id": "cand-event-low",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "participant_map": {"actor:royal_court": 201},
                    },
                },
                {
                    "candidate_id": "cand-rumor-safe",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "location_id": 301,
                    },
                },
                {
                    "candidate_id": "cand-event-safe",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                    },
                },
                {
                    "candidate_id": "cand-missing",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                    },
                },
            ],
        },
    )

    safe_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-event-safe")[1]["data"]
    low_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-event-low")[1]["data"]
    rumor_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-rumor-safe")[1]["data"]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_event_only"
    assert payload["data"]["dry_run"] is True
    assert payload["data"]["requested_count"] == 5
    assert payload["data"]["eligible_count"] == 1
    assert payload["data"]["ineligible_count"] == 4
    assert payload["data"]["eligible"][0]["candidate_id"] == "cand-event-safe"
    assert payload["data"]["eligible"][0]["metadata_preview"]["auto_promote_policy"] == "safe_event_only"
    ineligible_by_id = {}
    for item in payload["data"]["ineligible"]:
        ineligible_by_id.setdefault(item["candidate_id"], []).append(item)
    assert ineligible_by_id["cand-event-low"][0]["reasons"] == ["Policy 'safe_event_only' requires confidence >= 0.90"]
    assert ineligible_by_id["cand-rumor-safe"][0]["reasons"] == ["Policy 'safe_event_only' only supports scenario_event candidates"]
    assert ineligible_by_id["cand-event-safe"][0]["reasons"] == ["Event promotion requires participant_ids or participant_map"]
    assert ineligible_by_id["cand-missing"][0]["status"] == 404
    assert safe_detail["status"] == "pending_review"
    assert safe_detail["canonical_entity"] is None
    assert low_detail["status"] == "pending_review"
    assert rumor_detail["status"] == "pending_review"


def test_batch_auto_promote_endpoint_supports_cross_run_event_dry_run_preview(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-promote-cross-run-event-dry-run.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", cross_run_event_bundle(run_id="run-event-primary", candidate_id="cand-event-primary", outcome="success"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", cross_run_event_bundle(run_id="run-event-support", candidate_id="cand-event-support", outcome="success"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", cross_run_event_bundle(run_id="run-event-ongoing", candidate_id="cand-event-ongoing", outcome="ongoing"))

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-promote",
        {
            "policy": "safe_cross_run_event_only",
            "dry_run": True,
            "items": [
                {
                    "candidate_id": "cand-event-primary",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
                        "outcome": "success",
                    },
                },
                {
                    "candidate_id": "cand-event-ongoing",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
                        "outcome": "ongoing",
                    },
                },
            ],
        },
    )

    primary_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-event-primary")[1]["data"]
    ongoing_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-event-ongoing")[1]["data"]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_cross_run_event_only"
    assert payload["data"]["dry_run"] is True
    assert payload["data"]["eligible_count"] == 1
    assert payload["data"]["ineligible_count"] == 1
    assert payload["data"]["eligible"][0]["candidate_id"] == "cand-event-primary"
    assert payload["data"]["eligible"][0]["metadata_preview"]["event_match_outcome"] == "success"
    assert payload["data"]["eligible"][0]["metadata_preview"]["cross_run_supporting_run_ids"] == ["run-event-support"]
    assert payload["data"]["ineligible"][0]["candidate_id"] == "cand-event-ongoing"
    assert payload["data"]["ineligible"][0]["reasons"] == ["Policy 'safe_cross_run_event_only' requires terminal non-ongoing outcome"]
    assert primary_detail["status"] == "pending_review"
    assert primary_detail["canonical_entity"] is None
    assert ongoing_detail["status"] == "pending_review"


def test_batch_auto_promote_endpoint_supports_cross_run_rumor_dry_run_preview(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-promote-cross-run-rumor-dry-run.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", cross_run_rumor_bundle(run_id="run-rumor-primary", candidate_id="cand-rumor-primary"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", cross_run_rumor_bundle(run_id="run-rumor-support", candidate_id="cand-rumor-support"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", cross_run_rumor_bundle(run_id="run-rumor-resolved", candidate_id="cand-rumor-resolved", truth_level="True"))

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-promote",
        {
            "policy": "safe_cross_run_rumor_only",
            "dry_run": True,
            "items": [
                {
                    "candidate_id": "cand-rumor-primary",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "source_name": "Town criers",
                        "credibility_score": 7,
                        "location_id": 301,
                    },
                },
                {
                    "candidate_id": "cand-rumor-resolved",
                    "mapping": {
                        "tenant_id": 1,
                        "world_id": 101,
                        "source_name": "Town criers",
                        "credibility_score": 7,
                        "location_id": 301,
                        "truth_level": "True",
                    },
                },
            ],
        },
    )

    primary_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-rumor-primary")[1]["data"]
    resolved_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-rumor-resolved")[1]["data"]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_cross_run_rumor_only"
    assert payload["data"]["dry_run"] is True
    assert payload["data"]["eligible_count"] == 1
    assert payload["data"]["ineligible_count"] == 1
    assert payload["data"]["eligible"][0]["candidate_id"] == "cand-rumor-primary"
    assert payload["data"]["eligible"][0]["metadata_preview"]["cross_run_supporting_run_ids"] == ["run-rumor-support"]
    assert payload["data"]["ineligible"][0]["candidate_id"] == "cand-rumor-resolved"
    assert payload["data"]["ineligible"][0]["reasons"] == [
        "Policy 'safe_cross_run_rumor_only' only supports unresolved truth levels (Unverified or Partially True)"
    ]
    assert primary_detail["status"] == "pending_review"
    assert primary_detail["canonical_entity"] is None
    assert resolved_detail["status"] == "pending_review"


def test_batch_auto_promote_endpoint_rejects_non_boolean_dry_run(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-promote-dry-run-bad.db"))

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-promote",
        {"policy": "safe_event_only", "dry_run": "yes", "items": [{"candidate_id": "cand-1", "mapping": {}}]},
    )

    assert status == 400
    assert payload["success"] is False
    assert payload["error"] == "dry_run must be a boolean"


def test_batch_auto_promote_endpoint_rejects_invalid_payload(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-promote-bad.db"))

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-promote",
        {"items": []},
    )

    assert status == 400
    assert payload["success"] is False


def test_promote_endpoint_supports_manual_location_faction_and_character_candidates(tmp_path):
    app = create_writeback_app(str(tmp_path / "manual-promote.db"))

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        manual_candidate_bundle(
            candidate_id="cand-location-api",
            target_canonical_type="Location",
            name="Ashen Keep",
            summary="A ruined fortress overlooking the northern pass.",
            run_id="run-location-api",
        ),
    )
    call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-location-api/approve")
    location_status, location_payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/cand-location-api/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "location_type": "castle",
            "parent_location_id": 900,
        },
    )

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        manual_candidate_bundle(
            candidate_id="cand-faction-api",
            target_canonical_type="Faction",
            name="Harbor Guild",
            summary="A disciplined merchant coalition controlling the docks.",
            run_id="run-faction-api",
        ),
    )
    call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-faction-api/approve")
    faction_status, faction_payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/cand-faction-api/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "faction_type": "merchant",
            "alignment": "neutral",
            "leader_character_id": 501,
            "is_joinable": False,
        },
    )

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        manual_candidate_bundle(
            candidate_id="cand-character-api",
            target_canonical_type="Character",
            name="Captain Aria",
            summary="A harbor defender whose public resolve hides years of sacrifice.",
            run_id="run-character-api",
        ),
    )
    call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-character-api/approve")
    character_status, character_payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/cand-character-api/promote",
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

    assert location_status == 200
    assert location_payload["data"]["canonical_entity"]["canonical_type"] == "Location"
    assert location_payload["data"]["canonical_entity"]["entity"]["location_type"] == "castle"
    assert faction_status == 200
    assert faction_payload["data"]["canonical_entity"]["canonical_type"] == "Faction"
    assert faction_payload["data"]["canonical_entity"]["entity"]["alignment"] == "neutral"
    assert character_status == 200
    assert character_payload["data"]["canonical_entity"]["canonical_type"] == "Character"
    assert character_payload["data"]["canonical_entity"]["entity"]["backstory"] == long_backstory()
    assert character_payload["data"]["candidate"]["status"] == "promoted"


def test_merge_endpoint_links_manual_location_candidate_to_existing_location(tmp_path):
    app = create_writeback_app(str(tmp_path / "manual-merge.db"))

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        manual_candidate_bundle(
            candidate_id="cand-location-create",
            target_canonical_type="Location",
            name="Ashen Keep",
            summary="A ruined fortress overlooking the northern pass.",
            run_id="run-location-create",
        ),
    )
    call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-location-create/approve")
    promote_payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/cand-location-create/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "location_type": "castle",
        },
    )[1]

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        manual_candidate_bundle(
            candidate_id="cand-location-merge",
            target_canonical_type="Location",
            name="Ashen Keep Ruins",
            summary="Witnesses use a variant name for the same fortress.",
            run_id="run-location-merge",
        ),
    )
    call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-location-merge/approve")
    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/cand-location-merge/merge",
        {
            "canonical_id": promote_payload["data"]["canonical_entity"]["canonical_id"],
            "metadata": {"reason": "alias of existing location"},
        },
    )

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["canonical_entity"]["canonical_type"] == "Location"
    assert payload["data"]["run_link"]["relation_type"] == "merged_into"
    assert payload["data"]["run_link"]["metadata"]["reason"] == "alias of existing location"
    assert payload["data"]["candidate"]["status"] == "merged"


def test_merge_endpoint_links_approved_candidate_to_existing_canonical_entity(tmp_path):
    app = create_writeback_app(str(tmp_path / "merge.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", sample_result_bundle())
    first_candidate_id = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas?candidate_type=scenario_event")[1]["data"]["candidates"][0]["candidate_id"]
    call_json(app, "POST", f"/api/mirofish/writeback/candidate-deltas/{first_candidate_id}/approve")
    promote_payload = call_json(
        app,
        "POST",
        f"/api/mirofish/writeback/candidate-deltas/{first_candidate_id}/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201},
            "outcome": "success",
        },
    )[1]

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        sample_result_bundle(run_id="run-456", generated_at="2026-03-10T13:00:00Z", event_name="Court repeats denial"),
    )
    candidates = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas?candidate_type=scenario_event")[1]["data"]["candidates"]
    second_candidate_id = [item for item in candidates if item["run_id"] == "run-456"][0]["candidate_id"]
    call_json(app, "POST", f"/api/mirofish/writeback/candidate-deltas/{second_candidate_id}/approve")

    status, payload = call_json(
        app,
        "POST",
        f"/api/mirofish/writeback/candidate-deltas/{second_candidate_id}/merge",
        {
            "canonical_id": promote_payload["data"]["canonical_entity"]["canonical_id"],
            "metadata": {"reason": "same event"},
        },
    )

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["canonical_entity"]["canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert payload["data"]["run_link"]["relation_type"] == "merged_into"
    assert payload["data"]["run_link"]["metadata"]["reason"] == "same event"
    assert payload["data"]["candidate"]["status"] == "merged"


def test_batch_auto_merge_endpoint_merges_exact_duplicate_location_and_reports_failures(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-merge.db"))

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        manual_candidate_bundle(
            candidate_id="cand-location-create",
            target_canonical_type="Location",
            name="Ashen Keep",
            summary="A ruined fortress overlooking the northern pass.",
            run_id="run-location-create",
        ),
    )
    call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-location-create/approve")
    promote_payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/cand-location-create/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "location_type": "castle",
            "parent_location_id": 900,
        },
    )[1]

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_location_duplicate_bundle(
            candidate_id="cand-location-duplicate",
            name="Ashen Keep",
            summary="Another run confirms the same fortress.",
            run_id="run-location-duplicate",
            parent_location_id=900,
        ),
    )
    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_location_duplicate_bundle(
            candidate_id="cand-location-no-match",
            name="Bellwatch Keep",
            summary="A different fortress should stay pending.",
            run_id="run-location-no-match",
            parent_location_id=900,
        ),
    )

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-merge",
        {
            "policy": "safe_existing_location_duplicate_only",
            "items": [
                {"candidate_id": "cand-location-duplicate", "mapping": {"world_id": 101}},
                {"candidate_id": "cand-location-no-match", "mapping": {"world_id": 101}},
            ],
        },
    )

    duplicate_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-location-duplicate")[1]
    no_match_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-location-no-match")[1]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_existing_location_duplicate_only"
    assert payload["data"]["success_count"] == 1
    assert payload["data"]["failure_count"] == 1
    assert payload["data"]["succeeded"][0]["candidate_id"] == "cand-location-duplicate"
    assert payload["data"]["succeeded"][0]["canonical_entity"]["canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["auto_merge_policy"] == "safe_existing_location_duplicate_only"
    assert payload["data"]["failed"][0]["candidate_id"] == "cand-location-no-match"
    assert "exact duplicate match" in payload["data"]["failed"][0]["error"]
    assert duplicate_detail["data"]["status"] == "merged"
    assert no_match_detail["data"]["status"] == "pending_review"


def test_batch_auto_merge_endpoint_supports_dry_run_without_side_effects(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-merge-dry-run.db"))

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        manual_candidate_bundle(
            candidate_id="cand-location-create",
            target_canonical_type="Location",
            name="Ashen Keep",
            summary="A ruined fortress overlooking the northern pass.",
            run_id="run-location-create",
        ),
    )
    call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-location-create/approve")
    promote_payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/cand-location-create/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "location_type": "castle",
            "parent_location_id": 900,
        },
    )[1]

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_location_duplicate_bundle(
            candidate_id="cand-location-duplicate",
            name="  Ashen-Keep  ",
            summary="Another run confirms the same fortress.",
            run_id="run-location-duplicate",
            parent_location_id=900,
        ),
    )
    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_location_duplicate_bundle(
            candidate_id="cand-location-low-confidence",
            name="Ashen Keep",
            summary="Weak evidence for the same fortress.",
            run_id="run-location-low-confidence",
            parent_location_id=900,
            confidence=0.85,
            evidence_count=2,
        ),
    )

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-merge",
        {
            "policy": "safe_existing_location_duplicate_only",
            "dry_run": True,
            "items": [
                {"candidate_id": "cand-location-duplicate", "mapping": {"world_id": 101}},
                {"candidate_id": "cand-location-low-confidence", "mapping": {"world_id": 101}},
            ],
        },
    )

    duplicate_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-location-duplicate")[1]
    low_confidence_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-location-low-confidence")[1]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_existing_location_duplicate_only"
    assert payload["data"]["dry_run"] is True
    assert payload["data"]["eligible_count"] == 1
    assert payload["data"]["ineligible_count"] == 1
    assert payload["data"]["eligible"][0]["candidate_id"] == "cand-location-duplicate"
    assert payload["data"]["eligible"][0]["target_canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert payload["data"]["eligible"][0]["metadata_preview"]["auto_merge_policy"] == "safe_existing_location_duplicate_only"
    assert payload["data"]["ineligible"][0]["candidate_id"] == "cand-location-low-confidence"
    assert payload["data"]["ineligible"][0]["reasons"] == [
        "Policy 'safe_existing_location_duplicate_only' requires confidence >= 0.90"
    ]
    assert duplicate_detail["data"]["status"] == "pending_review"
    assert low_confidence_detail["data"]["status"] == "pending_review"


def test_batch_auto_merge_endpoint_validates_dry_run_type(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-merge-invalid.db"))

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-merge",
        {
            "policy": "safe_existing_location_duplicate_only",
            "dry_run": "yes",
            "items": [{"candidate_id": "cand-location-duplicate", "mapping": {"world_id": 101}}],
        },
    )

    assert status == 400
    assert payload["success"] is False
    assert payload["error"] == "dry_run must be a boolean"


def test_batch_auto_merge_endpoint_merges_exact_duplicate_event_and_reports_failures(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-merge-event.db"))

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_event_duplicate_bundle(
            candidate_id="cand-event-create",
            run_id="run-event-create",
            outcome="success",
        ),
    )
    call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-event-create/approve")
    promote_payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/cand-event-create/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
            "outcome": "success",
            "location_id": 301,
        },
    )[1]

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_event_duplicate_bundle(
            candidate_id="cand-event-duplicate",
            run_id="run-event-duplicate",
            outcome="success",
        ),
    )
    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_event_duplicate_bundle(
            candidate_id="cand-event-no-match",
            run_id="run-event-no-match",
            outcome="failure",
        ),
    )

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-merge",
        {
            "policy": "safe_existing_event_duplicate_only",
            "items": [
                {
                    "candidate_id": "cand-event-duplicate",
                    "mapping": {
                        "world_id": 101,
                        "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
                        "location_id": 301,
                    },
                },
                {
                    "candidate_id": "cand-event-no-match",
                    "mapping": {
                        "world_id": 101,
                        "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
                        "location_id": 301,
                    },
                },
            ],
        },
    )

    duplicate_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-event-duplicate")[1]
    no_match_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-event-no-match")[1]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_existing_event_duplicate_only"
    assert payload["data"]["success_count"] == 1
    assert payload["data"]["failure_count"] == 1
    assert payload["data"]["succeeded"][0]["candidate_id"] == "cand-event-duplicate"
    assert payload["data"]["succeeded"][0]["canonical_entity"]["canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["auto_merge_policy"] == "safe_existing_event_duplicate_only"
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["event_match_outcome"] == "success"
    assert payload["data"]["failed"][0]["candidate_id"] == "cand-event-no-match"
    assert "exact duplicate match" in payload["data"]["failed"][0]["error"]
    assert duplicate_detail["data"]["status"] == "merged"
    assert no_match_detail["data"]["status"] == "pending_review"


def test_batch_auto_merge_endpoint_supports_event_dry_run_without_side_effects(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-merge-event-dry-run.db"))

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_event_duplicate_bundle(
            candidate_id="cand-event-create",
            run_id="run-event-create",
            outcome="success",
        ),
    )
    call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-event-create/approve")
    promote_payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/cand-event-create/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
            "outcome": "success",
            "location_id": 301,
        },
    )[1]

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_event_duplicate_bundle(
            candidate_id="cand-event-duplicate",
            run_id="run-event-duplicate",
            outcome="success",
        ),
    )
    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_event_duplicate_bundle(
            candidate_id="cand-event-ongoing",
            run_id="run-event-ongoing",
            outcome="ongoing",
        ),
    )

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-merge",
        {
            "policy": "safe_existing_event_duplicate_only",
            "dry_run": True,
            "items": [
                {
                    "candidate_id": "cand-event-duplicate",
                    "mapping": {
                        "world_id": 101,
                        "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
                        "location_id": 301,
                    },
                },
                {
                    "candidate_id": "cand-event-ongoing",
                    "mapping": {
                        "world_id": 101,
                        "participant_map": {"actor:royal_court": 201, "org:royal_court": 202},
                        "location_id": 301,
                    },
                },
            ],
        },
    )

    duplicate_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-event-duplicate")[1]
    ongoing_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-event-ongoing")[1]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_existing_event_duplicate_only"
    assert payload["data"]["dry_run"] is True
    assert payload["data"]["eligible_count"] == 1
    assert payload["data"]["ineligible_count"] == 1
    assert payload["data"]["eligible"][0]["candidate_id"] == "cand-event-duplicate"
    assert payload["data"]["eligible"][0]["target_canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert payload["data"]["eligible"][0]["metadata_preview"]["auto_merge_policy"] == "safe_existing_event_duplicate_only"
    assert payload["data"]["eligible"][0]["metadata_preview"]["event_match_outcome"] == "success"
    assert payload["data"]["ineligible"][0]["candidate_id"] == "cand-event-ongoing"
    assert payload["data"]["ineligible"][0]["reasons"] == [
        "Policy 'safe_existing_event_duplicate_only' requires terminal non-ongoing outcome"
    ]
    assert duplicate_detail["data"]["status"] == "pending_review"
    assert ongoing_detail["data"]["status"] == "pending_review"


def test_batch_auto_merge_endpoint_merges_exact_duplicate_relationship_and_reports_failures(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-merge-relationship.db"))

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-create",
            run_id="run-relationship-create",
            relationship_level=-42,
        ),
    )
    call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-relationship-create/approve")
    promote_payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/cand-relationship-create/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "character_from_id": 201,
            "character_to_id": 202,
            "relationship_level": -42,
            "is_mutual": False,
        },
    )[1]

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-duplicate",
            run_id="run-relationship-duplicate",
            relationship_level=-42,
        ),
    )
    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-no-match",
            run_id="run-relationship-no-match",
            relationship_level=-55,
        ),
    )

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-merge",
        {
            "policy": "safe_existing_relationship_duplicate_only",
            "items": [
                {
                    "candidate_id": "cand-relationship-duplicate",
                    "mapping": {
                        "world_id": 101,
                        "character_from_id": 201,
                        "character_to_id": 202,
                        "relationship_level": -42,
                    },
                },
                {
                    "candidate_id": "cand-relationship-no-match",
                    "mapping": {
                        "world_id": 101,
                        "character_from_id": 201,
                        "character_to_id": 202,
                        "relationship_level": -55,
                    },
                },
            ],
        },
    )

    duplicate_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-relationship-duplicate")[1]
    no_match_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-relationship-no-match")[1]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_existing_relationship_duplicate_only"
    assert payload["data"]["success_count"] == 1
    assert payload["data"]["failure_count"] == 1
    assert payload["data"]["succeeded"][0]["candidate_id"] == "cand-relationship-duplicate"
    assert payload["data"]["succeeded"][0]["canonical_entity"]["canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["auto_merge_policy"] == "safe_existing_relationship_duplicate_only"
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["merge_match_relationship_type"] == "enemy"
    assert payload["data"]["failed"][0]["candidate_id"] == "cand-relationship-no-match"
    assert "exact duplicate match" in payload["data"]["failed"][0]["error"]
    assert duplicate_detail["data"]["status"] == "merged"
    assert no_match_detail["data"]["status"] == "pending_review"


def test_batch_auto_merge_endpoint_supports_relationship_dry_run_without_side_effects(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-merge-relationship-dry-run.db"))

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-create",
            run_id="run-relationship-create",
            relationship_level=-42,
        ),
    )
    call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-relationship-create/approve")
    promote_payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/cand-relationship-create/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "character_from_id": 201,
            "character_to_id": 202,
            "relationship_level": -42,
            "is_mutual": False,
        },
    )[1]

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-duplicate",
            run_id="run-relationship-duplicate",
            relationship_level=-42,
        ),
    )
    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_relationship_duplicate_bundle(
            candidate_id="cand-relationship-weak",
            run_id="run-relationship-weak",
            relationship_level=-10,
        ),
    )

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-merge",
        {
            "policy": "safe_existing_relationship_duplicate_only",
            "dry_run": True,
            "items": [
                {
                    "candidate_id": "cand-relationship-duplicate",
                    "mapping": {
                        "world_id": 101,
                        "character_from_id": 201,
                        "character_to_id": 202,
                        "relationship_level": -42,
                    },
                },
                {
                    "candidate_id": "cand-relationship-weak",
                    "mapping": {
                        "world_id": 101,
                        "character_from_id": 201,
                        "character_to_id": 202,
                        "relationship_level": -10,
                    },
                },
            ],
        },
    )

    duplicate_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-relationship-duplicate")[1]
    weak_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-relationship-weak")[1]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_existing_relationship_duplicate_only"
    assert payload["data"]["dry_run"] is True
    assert payload["data"]["eligible_count"] == 1
    assert payload["data"]["ineligible_count"] == 1
    assert payload["data"]["eligible"][0]["candidate_id"] == "cand-relationship-duplicate"
    assert payload["data"]["eligible"][0]["target_canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert payload["data"]["eligible"][0]["metadata_preview"]["auto_merge_policy"] == "safe_existing_relationship_duplicate_only"
    assert payload["data"]["eligible"][0]["metadata_preview"]["merge_match_relationship_type"] == "enemy"
    assert payload["data"]["ineligible"][0]["candidate_id"] == "cand-relationship-weak"
    assert payload["data"]["ineligible"][0]["reasons"] == [
        "Policy 'safe_existing_relationship_duplicate_only' requires abs(relationship_level) >= 30"
    ]
    assert duplicate_detail["data"]["status"] == "pending_review"
    assert weak_detail["data"]["status"] == "pending_review"


def test_batch_auto_merge_endpoint_merges_exact_duplicate_faction_and_reports_failures(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-merge-faction.db"))

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        manual_candidate_bundle(
            candidate_id="cand-faction-create",
            target_canonical_type="Faction",
            name="Harbor Guild",
            summary="A disciplined merchant coalition controlling the docks.",
            run_id="run-faction-create",
        ),
    )
    call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-faction-create/approve")
    promote_payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/cand-faction-create/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "faction_type": "merchant",
            "alignment": "neutral",
            "leader_character_id": 501,
            "is_joinable": False,
        },
    )[1]

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_faction_duplicate_bundle(
            candidate_id="cand-faction-duplicate",
            name="Harbor Guild",
            summary="Another run confirms the same merchant coalition.",
            run_id="run-faction-duplicate",
        ),
    )
    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_faction_duplicate_bundle(
            candidate_id="cand-faction-no-match",
            name="Harbor Guild",
            summary="A different faction variant should stay pending.",
            run_id="run-faction-no-match",
            is_joinable=True,
        ),
    )

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-merge",
        {
            "policy": "safe_existing_faction_duplicate_only",
            "items": [
                {"candidate_id": "cand-faction-duplicate", "mapping": {"world_id": 101}},
                {"candidate_id": "cand-faction-no-match", "mapping": {"world_id": 101}},
            ],
        },
    )

    duplicate_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-faction-duplicate")[1]
    no_match_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-faction-no-match")[1]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_existing_faction_duplicate_only"
    assert payload["data"]["success_count"] == 1
    assert payload["data"]["failure_count"] == 1
    assert payload["data"]["succeeded"][0]["candidate_id"] == "cand-faction-duplicate"
    assert payload["data"]["succeeded"][0]["canonical_entity"]["canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["auto_merge_policy"] == "safe_existing_faction_duplicate_only"
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["merge_match_faction_type"] == "merchant"
    assert payload["data"]["failed"][0]["candidate_id"] == "cand-faction-no-match"
    assert "exact duplicate match" in payload["data"]["failed"][0]["error"]
    assert duplicate_detail["data"]["status"] == "merged"
    assert no_match_detail["data"]["status"] == "pending_review"


def test_batch_auto_merge_endpoint_supports_faction_dry_run_without_side_effects(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-merge-faction-dry-run.db"))

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        manual_candidate_bundle(
            candidate_id="cand-faction-create",
            target_canonical_type="Faction",
            name="Harbor Guild",
            summary="A disciplined merchant coalition controlling the docks.",
            run_id="run-faction-create",
        ),
    )
    call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-faction-create/approve")
    promote_payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/cand-faction-create/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "faction_type": "merchant",
            "alignment": "neutral",
            "leader_character_id": 501,
            "is_joinable": False,
        },
    )[1]

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_faction_duplicate_bundle(
            candidate_id="cand-faction-duplicate",
            name="  Harbor-Guild  ",
            summary="Another run confirms the same merchant coalition.",
            run_id="run-faction-duplicate",
        ),
    )
    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_faction_duplicate_bundle(
            candidate_id="cand-faction-low-confidence",
            name="Harbor Guild",
            summary="Weak evidence for the same merchant coalition.",
            run_id="run-faction-low-confidence",
            confidence=0.85,
            evidence_count=2,
        ),
    )

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-merge",
        {
            "policy": "safe_existing_faction_duplicate_only",
            "dry_run": True,
            "items": [
                {"candidate_id": "cand-faction-duplicate", "mapping": {"world_id": 101}},
                {"candidate_id": "cand-faction-low-confidence", "mapping": {"world_id": 101}},
            ],
        },
    )

    duplicate_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-faction-duplicate")[1]
    low_confidence_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-faction-low-confidence")[1]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_existing_faction_duplicate_only"
    assert payload["data"]["dry_run"] is True
    assert payload["data"]["eligible_count"] == 1
    assert payload["data"]["ineligible_count"] == 1
    assert payload["data"]["eligible"][0]["candidate_id"] == "cand-faction-duplicate"
    assert payload["data"]["eligible"][0]["target_canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert payload["data"]["eligible"][0]["metadata_preview"]["auto_merge_policy"] == "safe_existing_faction_duplicate_only"
    assert payload["data"]["eligible"][0]["metadata_preview"]["merge_match_name"] == "harbor guild"
    assert payload["data"]["ineligible"][0]["candidate_id"] == "cand-faction-low-confidence"
    assert payload["data"]["ineligible"][0]["reasons"] == [
        "Policy 'safe_existing_faction_duplicate_only' requires confidence >= 0.90"
    ]
    assert duplicate_detail["data"]["status"] == "pending_review"
    assert low_confidence_detail["data"]["status"] == "pending_review"


def test_batch_auto_merge_endpoint_merges_exact_duplicate_character_and_reports_failures(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-merge-character.db"))

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        manual_candidate_bundle(
            candidate_id="cand-character-create",
            target_canonical_type="Character",
            name="Captain Aria",
            summary="A harbor defender whose public resolve hides years of sacrifice.",
            run_id="run-character-create",
        ),
    )
    call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-character-create/approve")
    promote_payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/cand-character-create/promote",
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
    )[1]

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_character_duplicate_bundle(
            candidate_id="cand-character-duplicate",
            name="  Captain-Aria  ",
            summary="Another run confirms the same character snapshot.",
            run_id="run-character-duplicate",
        ),
    )
    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_character_duplicate_bundle(
            candidate_id="cand-character-no-match",
            name="Captain Aria",
            summary="A different combat role snapshot should stay pending.",
            run_id="run-character-no-match",
            role="dps",
        ),
    )

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-merge",
        {
            "policy": "safe_existing_character_duplicate_only",
            "items": [
                {"candidate_id": "cand-character-duplicate", "mapping": {"world_id": 101}},
                {"candidate_id": "cand-character-no-match", "mapping": {"world_id": 101}},
            ],
        },
    )

    duplicate_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-character-duplicate")[1]
    no_match_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-character-no-match")[1]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_existing_character_duplicate_only"
    assert payload["data"]["success_count"] == 1
    assert payload["data"]["failure_count"] == 1
    assert payload["data"]["succeeded"][0]["candidate_id"] == "cand-character-duplicate"
    assert payload["data"]["succeeded"][0]["canonical_entity"]["canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["auto_merge_policy"] == "safe_existing_character_duplicate_only"
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["merge_match_role"] == "support"
    assert payload["data"]["failed"][0]["candidate_id"] == "cand-character-no-match"
    assert "exact duplicate match" in payload["data"]["failed"][0]["error"]
    assert duplicate_detail["data"]["status"] == "merged"
    assert no_match_detail["data"]["status"] == "pending_review"


def test_batch_auto_merge_endpoint_supports_character_dry_run_without_side_effects(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-merge-character-dry-run.db"))

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        manual_candidate_bundle(
            candidate_id="cand-character-create",
            target_canonical_type="Character",
            name="Captain Aria",
            summary="A harbor defender whose public resolve hides years of sacrifice.",
            run_id="run-character-create",
        ),
    )
    call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-character-create/approve")
    promote_payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/cand-character-create/promote",
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
    )[1]

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_character_duplicate_bundle(
            candidate_id="cand-character-duplicate",
            name="Captain Aria",
            summary="Another run confirms the same character snapshot.",
            run_id="run-character-duplicate",
        ),
    )
    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_character_duplicate_bundle(
            candidate_id="cand-character-low-confidence",
            name="Captain Aria",
            summary="Weak evidence repeats the same character snapshot.",
            run_id="run-character-low-confidence",
            confidence=0.85,
            evidence_count=2,
        ),
    )

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-merge",
        {
            "policy": "safe_existing_character_duplicate_only",
            "dry_run": True,
            "items": [
                {"candidate_id": "cand-character-duplicate", "mapping": {"world_id": 101}},
                {"candidate_id": "cand-character-low-confidence", "mapping": {"world_id": 101}},
            ],
        },
    )

    duplicate_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-character-duplicate")[1]
    low_confidence_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-character-low-confidence")[1]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_existing_character_duplicate_only"
    assert payload["data"]["dry_run"] is True
    assert payload["data"]["eligible_count"] == 1
    assert payload["data"]["ineligible_count"] == 1
    assert payload["data"]["eligible"][0]["candidate_id"] == "cand-character-duplicate"
    assert payload["data"]["eligible"][0]["target_canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert payload["data"]["eligible"][0]["metadata_preview"]["auto_merge_policy"] == "safe_existing_character_duplicate_only"
    assert payload["data"]["eligible"][0]["metadata_preview"]["merge_match_name"] == "captain aria"
    assert payload["data"]["ineligible"][0]["candidate_id"] == "cand-character-low-confidence"
    assert payload["data"]["ineligible"][0]["reasons"] == [
        "Policy 'safe_existing_character_duplicate_only' requires confidence >= 0.90"
    ]
    assert duplicate_detail["data"]["status"] == "pending_review"
    assert low_confidence_detail["data"]["status"] == "pending_review"


def test_batch_auto_merge_endpoint_merges_exact_duplicate_rumor_and_reports_failures(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-merge-rumor.db"))

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_rumor_duplicate_bundle(
            candidate_id="cand-rumor-create",
            name="Bellfire Coup",
            summary="Whispers describe a coup brewing in Bellfire.",
            run_id="run-rumor-create",
        ),
    )
    call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-rumor-create/approve")
    promote_payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/cand-rumor-create/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "location_id": 301,
        },
    )[1]

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_rumor_duplicate_bundle(
            candidate_id="cand-rumor-duplicate",
            name="Bellfire Coup",
            summary="Another run confirms the same rumor signature.",
            run_id="run-rumor-duplicate",
        ),
    )
    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_rumor_duplicate_bundle(
            candidate_id="cand-rumor-no-match",
            name="Harbor Fire",
            summary="A different rumor should stay pending.",
            run_id="run-rumor-no-match",
        ),
    )

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-merge",
        {
            "policy": "safe_existing_rumor_duplicate_only",
            "items": [
                {"candidate_id": "cand-rumor-duplicate", "mapping": {"world_id": 101}},
                {"candidate_id": "cand-rumor-no-match", "mapping": {"world_id": 101}},
            ],
        },
    )

    duplicate_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-rumor-duplicate")[1]
    no_match_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-rumor-no-match")[1]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_existing_rumor_duplicate_only"
    assert payload["data"]["success_count"] == 1
    assert payload["data"]["failure_count"] == 1
    assert payload["data"]["succeeded"][0]["candidate_id"] == "cand-rumor-duplicate"
    assert payload["data"]["succeeded"][0]["canonical_entity"]["canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert payload["data"]["succeeded"][0]["run_link"]["metadata"]["auto_merge_policy"] == "safe_existing_rumor_duplicate_only"
    assert payload["data"]["failed"][0]["candidate_id"] == "cand-rumor-no-match"
    assert "exact duplicate match" in payload["data"]["failed"][0]["error"]
    assert duplicate_detail["data"]["status"] == "merged"
    assert no_match_detail["data"]["status"] == "pending_review"


def test_batch_auto_merge_endpoint_supports_rumor_dry_run_without_side_effects(tmp_path):
    app = create_writeback_app(str(tmp_path / "batch-auto-merge-rumor-dry-run.db"))

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_rumor_duplicate_bundle(
            candidate_id="cand-rumor-create",
            name="Bellfire Coup",
            summary="Whispers describe a coup brewing in Bellfire.",
            run_id="run-rumor-create",
            truth_level="partially_true",
        ),
    )
    call_json(app, "POST", "/api/mirofish/writeback/candidate-deltas/cand-rumor-create/approve")
    promote_payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/cand-rumor-create/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "location_id": 301,
            "truth_level": "partially_true",
        },
    )[1]

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_rumor_duplicate_bundle(
            candidate_id="cand-rumor-duplicate",
            name="  Bellfire-Coup  ",
            summary="Another run confirms the same rumor signature.",
            run_id="run-rumor-duplicate",
            truth_level="partially_true",
        ),
    )
    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        exact_rumor_duplicate_bundle(
            candidate_id="cand-rumor-resolved",
            name="Bellfire Coup",
            summary="The rumor is already treated as true.",
            run_id="run-rumor-resolved",
            truth_level="true",
        ),
    )

    status, payload = call_json(
        app,
        "POST",
        "/api/mirofish/writeback/candidate-deltas/batch/auto-merge",
        {
            "policy": "safe_existing_rumor_duplicate_only",
            "dry_run": True,
            "items": [
                {"candidate_id": "cand-rumor-duplicate", "mapping": {"world_id": 101}},
                {"candidate_id": "cand-rumor-resolved", "mapping": {"world_id": 101}},
            ],
        },
    )

    duplicate_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-rumor-duplicate")[1]
    resolved_detail = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas/cand-rumor-resolved")[1]

    assert status == 200
    assert payload["success"] is True
    assert payload["data"]["policy"] == "safe_existing_rumor_duplicate_only"
    assert payload["data"]["dry_run"] is True
    assert payload["data"]["eligible_count"] == 1
    assert payload["data"]["ineligible_count"] == 1
    assert payload["data"]["eligible"][0]["candidate_id"] == "cand-rumor-duplicate"
    assert payload["data"]["eligible"][0]["target_canonical_id"] == promote_payload["data"]["canonical_entity"]["canonical_id"]
    assert payload["data"]["eligible"][0]["metadata_preview"]["auto_merge_policy"] == "safe_existing_rumor_duplicate_only"
    assert payload["data"]["eligible"][0]["metadata_preview"]["rumor_truth_bucket"] == "Partially True"
    assert payload["data"]["ineligible"][0]["candidate_id"] == "cand-rumor-resolved"
    assert payload["data"]["ineligible"][0]["reasons"] == [
        "Policy 'safe_existing_rumor_duplicate_only' only supports unresolved truth levels (Unverified or Partially True)"
    ]
    assert duplicate_detail["data"]["status"] == "pending_review"
    assert resolved_detail["data"]["status"] == "pending_review"


def test_merge_endpoint_requires_approved_candidate(tmp_path):
    app = create_writeback_app(str(tmp_path / "merge-gate.db"))
    call_json(app, "POST", "/api/mirofish/writeback/ingest", sample_result_bundle())
    first_candidate_id = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas?candidate_type=scenario_event")[1]["data"]["candidates"][0]["candidate_id"]
    call_json(app, "POST", f"/api/mirofish/writeback/candidate-deltas/{first_candidate_id}/approve")
    promote_payload = call_json(
        app,
        "POST",
        f"/api/mirofish/writeback/candidate-deltas/{first_candidate_id}/promote",
        {
            "tenant_id": 1,
            "world_id": 101,
            "participant_map": {"actor:royal_court": 201},
            "outcome": "success",
        },
    )[1]

    call_json(
        app,
        "POST",
        "/api/mirofish/writeback/ingest",
        sample_result_bundle(run_id="run-456", generated_at="2026-03-10T13:00:00Z", event_name="Court repeats denial"),
    )
    candidates = call_json(app, "GET", "/api/mirofish/writeback/candidate-deltas?candidate_type=scenario_event")[1]["data"]["candidates"]
    second_candidate_id = [item for item in candidates if item["run_id"] == "run-456"][0]["candidate_id"]

    status, payload = call_json(
        app,
        "POST",
        f"/api/mirofish/writeback/candidate-deltas/{second_candidate_id}/merge",
        {
            "canonical_id": promote_payload["data"]["canonical_entity"]["canonical_id"],
        },
    )

    assert status == 400
    assert payload["success"] is False


def test_ingest_endpoint_rejects_invalid_json(tmp_path):
    app = create_writeback_app(str(tmp_path / "bad.db"))
    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/api/mirofish/writeback/ingest",
        "QUERY_STRING": "",
        "CONTENT_LENGTH": "1",
        "wsgi.input": io.BytesIO(b"{"),
    }
    captured: dict[str, object] = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    body = b"".join(app(environ, start_response))
    payload = json.loads(body.decode("utf-8"))

    assert int(str(captured["status"]).split()[0]) == 400
    assert payload["success"] is False