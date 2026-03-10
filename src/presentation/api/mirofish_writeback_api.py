"""Minimal stdlib JSON API for MiroFish write-back staging."""

from __future__ import annotations

import json
from http import HTTPStatus
from typing import Any
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from src.application.integration.importers import MiroFishResultImporter
from src.infrastructure.mirofish_writeback_store import MiroFishWriteBackStore


class MiroFishWriteBackAPI:
    """Serve safe ingest/review endpoints for staged MiroFish write-back data."""

    base_path = "/api/mirofish/writeback"

    def __init__(self, db_path: str = "lore_system.db"):
        self.store = MiroFishWriteBackStore(db_path)
        self.importer = MiroFishResultImporter(self.store)

    def handle_request(
        self,
        method: str,
        path: str,
        *,
        query_string: str = "",
        body: bytes = b"",
    ) -> tuple[int, dict[str, Any]]:
        if method == "POST" and path == f"{self.base_path}/ingest":
            return self._handle_ingest(body)

        if method == "GET" and path == f"{self.base_path}/candidate-deltas":
            return self._handle_candidate_list(query_string)

        prefix = f"{self.base_path}/runs/"
        if method == "GET" and path.startswith(prefix):
            suffix = path[len(prefix):]
            if suffix.endswith("/evidence"):
                run_id = suffix[:-len("/evidence")].strip("/")
                return self._handle_run_evidence(run_id)
            return self._handle_run_detail(suffix.strip("/"))

        return self._response(HTTPStatus.NOT_FOUND, {"success": False, "error": f"Unknown endpoint: {method} {path}"})

    def _handle_ingest(self, body: bytes) -> tuple[int, dict[str, Any]]:
        try:
            payload = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError as exc:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": f"Invalid JSON body: {exc.msg}"})

        try:
            result = self.importer.import_result_bundle(payload)
        except ValueError as exc:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": str(exc)})
        except Exception as exc:  # pragma: no cover - defensive API guard
            return self._response(HTTPStatus.INTERNAL_SERVER_ERROR, {"success": False, "error": str(exc)})

        return self._response(HTTPStatus.OK, {"success": True, "data": result})

    def _handle_candidate_list(self, query_string: str) -> tuple[int, dict[str, Any]]:
        params = parse_qs(query_string, keep_blank_values=False)
        candidates = self.store.list_candidates(
            world_id=self._first(params, "world_id"),
            status=self._first(params, "status"),
            candidate_type=self._first(params, "candidate_type"),
        )
        items = [
            {
                **item,
                "evidence_count": len(item.get("evidence_ids") or []),
            }
            for item in candidates
        ]
        return self._response(HTTPStatus.OK, {"success": True, "data": {"count": len(items), "candidates": items}})

    def _handle_run_detail(self, run_id: str) -> tuple[int, dict[str, Any]]:
        if not run_id:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": "run_id is required"})
        run = self.store.get_run(run_id)
        if not run:
            return self._response(HTTPStatus.NOT_FOUND, {"success": False, "error": f"Run '{run_id}' not found"})
        return self._response(HTTPStatus.OK, {"success": True, "data": run})

    def _handle_run_evidence(self, run_id: str) -> tuple[int, dict[str, Any]]:
        if not run_id:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": "run_id is required"})
        run = self.store.get_run(run_id)
        if not run:
            return self._response(HTTPStatus.NOT_FOUND, {"success": False, "error": f"Run '{run_id}' not found"})
        evidence = self.store.list_evidence(run_id)
        return self._response(HTTPStatus.OK, {"success": True, "data": {"run_id": run_id, "count": len(evidence), "evidence": evidence}})

    def wsgi_app(self, environ: dict[str, Any], start_response):
        content_length = int(environ.get("CONTENT_LENGTH") or 0)
        body = environ["wsgi.input"].read(content_length) if content_length > 0 else b""
        status_code, payload = self.handle_request(
            environ.get("REQUEST_METHOD", "GET"),
            environ.get("PATH_INFO", "/"),
            query_string=environ.get("QUERY_STRING", ""),
            body=body,
        )
        response_body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        start_response(
            f"{status_code} {HTTPStatus(status_code).phrase}",
            [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(response_body))),
            ],
        )
        return [response_body]

    def _response(self, status: HTTPStatus, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        return int(status), payload

    def _first(self, params: dict[str, list[str]], key: str) -> str | None:
        values = params.get(key) or []
        if not values:
            return None
        value = values[0].strip()
        return value or None


def create_writeback_app(db_path: str = "lore_system.db"):
    """Create a WSGI app exposing MiroFish write-back endpoints."""

    api = MiroFishWriteBackAPI(db_path=db_path)
    return api.wsgi_app


def run_writeback_api_server(host: str = "127.0.0.1", port: int = 8080, db_path: str = "lore_system.db") -> None:
    """Run the write-back API with Python's built-in WSGI server."""

    app = create_writeback_app(db_path=db_path)
    with make_server(host, port, app) as server:
        print(f"MiroFish write-back API listening on http://{host}:{port}")
        server.serve_forever()