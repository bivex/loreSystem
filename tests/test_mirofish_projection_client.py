import json

import pytest

from src.application.integration.mirofish_projection_client import (
    MiroFishProjectionClient,
    build_projection_import_payload,
)


def sample_bundle() -> dict:
    return {
        "schema_version": "1.0",
        "world_id": "1",
        "scenario_id": "demo",
        "actors": [{"id": "actor:1", "name": "Aria"}],
        "organizations": [],
        "social_edges": [],
        "context_locations": [],
        "event_seeds": [],
        "world_rules": [],
    }


def test_build_projection_import_payload_requires_simulation_requirement():
    with pytest.raises(ValueError):
        build_projection_import_payload(sample_bundle(), simulation_requirement="")


def test_client_resolves_projection_import_endpoint_variants():
    assert MiroFishProjectionClient("http://localhost:5001")._resolve_endpoint().endswith("/api/graph/projection/import")
    assert MiroFishProjectionClient("http://localhost:5001/api/graph")._resolve_endpoint() == "http://localhost:5001/api/graph/projection/import"
    assert MiroFishProjectionClient("http://localhost:5001/api/graph/projection/import")._resolve_endpoint() == "http://localhost:5001/api/graph/projection/import"


def test_client_posts_projection_bundle_and_parses_response(monkeypatch):
    captured = {}

    class DummyResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps({"success": True, "data": {"project_id": "proj-1", "project_name": "Demo"}}).encode("utf-8")

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["headers"] = dict(request.header_items())
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return DummyResponse()

    monkeypatch.setattr("src.application.integration.mirofish_projection_client.urlopen", fake_urlopen)

    client = MiroFishProjectionClient("http://localhost:5001", timeout_seconds=12)
    result = client.import_bundle(sample_bundle(), simulation_requirement="Run a harbor crisis simulation", project_name="Harbor Crisis")

    assert captured["url"] == "http://localhost:5001/api/graph/projection/import"
    assert captured["timeout"] == 12
    assert captured["body"]["projection_bundle"]["world_id"] == "1"
    assert captured["body"]["simulation_requirement"] == "Run a harbor crisis simulation"
    assert result["data"]["project_id"] == "proj-1"