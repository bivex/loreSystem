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