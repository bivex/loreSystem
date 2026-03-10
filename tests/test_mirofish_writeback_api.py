import io
import json

from src.presentation.api import create_writeback_app


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
            "rumors": [{"name": "Forged decree rumor", "summary": "Town criers amplify doubts.", "actor_refs": ["org:town_criers"], "confidence": 0.74}],
        },
        "emergent_events": [{"name": "Court issues denial", "description": "The Royal Court publicly denies the forgery.", "participant_ids": ["actor:royal_court", "org:royal_court"], "confidence": 0.81}],
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