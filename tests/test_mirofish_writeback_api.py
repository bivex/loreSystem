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
        "prediction_summary": {
            "summary": "A forged decree rumor destabilizes trust in the court.",
            "rumors": [{"name": "Forged decree rumor", "summary": "Town criers amplify doubts.", "confidence": 0.74}],
        },
        "emergent_events": [{"name": "Court issues denial", "description": "The Royal Court publicly denies the forgery.", "confidence": 0.81}],
        "relationship_changes": [{"name": "Captain Serik distrusts Nessa", "summary": "Trust drops after the rumor spike.", "confidence": 0.67}],
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
    assert evidence_status == 200
    assert evidence_payload["data"]["run_id"] == "run-123"
    assert evidence_payload["data"]["count"] == 4


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