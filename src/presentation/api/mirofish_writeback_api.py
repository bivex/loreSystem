"""Minimal stdlib JSON API for MiroFish write-back staging."""

from __future__ import annotations

import json
from http import HTTPStatus
from typing import Any
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from src.application.integration.importers import MiroFishResultImporter
from src.application.integration.promoters import MiroFishCandidatePromoter
from src.infrastructure.mirofish_writeback_store import MiroFishWriteBackStore


class MiroFishWriteBackAPI:
    """Serve safe ingest/review endpoints for staged MiroFish write-back data."""

    base_path = "/api/mirofish/writeback"

    def __init__(self, db_path: str = "lore_system.db"):
        self.store = MiroFishWriteBackStore(db_path)
        self.importer = MiroFishResultImporter(self.store)
        self.promoter = MiroFishCandidatePromoter(self.store)

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

        if method == "POST" and path == f"{self.base_path}/candidate-deltas/batch/review":
            return self._handle_candidate_batch_review(body)

        if method == "POST" and path == f"{self.base_path}/candidate-deltas/batch/promote":
            return self._handle_candidate_batch_promote(body)

        if method == "POST" and path == f"{self.base_path}/candidate-deltas/batch/auto-promote":
            return self._handle_candidate_batch_auto_promote(body)

        candidate_prefix = f"{self.base_path}/candidate-deltas/"
        if method == "GET" and path.startswith(candidate_prefix):
            suffix = path[len(candidate_prefix):].strip("/")
            if suffix and "/" not in suffix:
                return self._handle_candidate_detail(suffix)

        if method == "POST" and path.startswith(candidate_prefix):
            suffix = path[len(candidate_prefix):].strip("/")
            parts = [part for part in suffix.split("/") if part]
            if len(parts) == 2 and parts[1] in {"approve", "reject"}:
                return self._handle_candidate_review_action(parts[0], parts[1])
            if len(parts) == 2 and parts[1] == "promote":
                return self._handle_candidate_promote(parts[0], body)
            if len(parts) == 2 and parts[1] == "merge":
                return self._handle_candidate_merge(parts[0], body)

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

    def _handle_candidate_detail(self, candidate_id: str) -> tuple[int, dict[str, Any]]:
        if not candidate_id:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": "candidate_id is required"})
        candidate = self.store.get_candidate(candidate_id)
        if not candidate:
            return self._response(HTTPStatus.NOT_FOUND, {"success": False, "error": f"Candidate '{candidate_id}' not found"})

        canonical_entity = None
        target_canonical_id = str(candidate.get("target_canonical_id") or "").strip()
        if target_canonical_id:
            try:
                canonical_entity = self.store.get_canonical_entity(int(target_canonical_id))
            except ValueError:
                canonical_entity = None
        if canonical_entity is None:
            canonical_entity = self.store.get_canonical_entity_by_candidate(candidate_id)
        payload = {
            **candidate,
            "evidence_count": len(candidate.get("evidence_ids") or []),
        }
        if canonical_entity:
            payload["canonical_entity"] = canonical_entity
            payload["run_links"] = self.store.list_entity_run_links(source_candidate_id=candidate_id)
        else:
            payload["canonical_entity"] = None
            payload["run_links"] = []
        return self._response(HTTPStatus.OK, {"success": True, "data": payload})

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

    def _handle_candidate_review_action(self, candidate_id: str, action: str) -> tuple[int, dict[str, Any]]:
        if not candidate_id:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": "candidate_id is required"})

        status = "approved" if action == "approve" else "rejected"
        candidate = self.store.update_candidate_status(candidate_id, status)
        if not candidate:
            return self._response(HTTPStatus.NOT_FOUND, {"success": False, "error": f"Candidate '{candidate_id}' not found"})

        return self._response(
            HTTPStatus.OK,
            {
                "success": True,
                "data": {
                    "action": action,
                    "candidate": {
                        **candidate,
                        "evidence_count": len(candidate.get("evidence_ids") or []),
                    },
                },
            },
        )

    def _handle_candidate_batch_review(self, body: bytes) -> tuple[int, dict[str, Any]]:
        try:
            payload = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError as exc:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": f"Invalid JSON body: {exc.msg}"})

        action = str(payload.get("action") or "").strip().lower()
        if action not in {"approve", "reject"}:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": "action must be 'approve' or 'reject'"})

        candidate_ids = payload.get("candidate_ids")
        if not isinstance(candidate_ids, list) or not candidate_ids:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": "candidate_ids must be a non-empty list"})

        succeeded: list[dict[str, Any]] = []
        failed: list[dict[str, Any]] = []
        for raw_candidate_id in candidate_ids:
            candidate_id = str(raw_candidate_id or "").strip()
            if not candidate_id:
                failed.append({"candidate_id": candidate_id, "error": "candidate_id is required"})
                continue
            status_code, result = self._handle_candidate_review_action(candidate_id, action)
            if status_code == int(HTTPStatus.OK):
                succeeded.append(result["data"])
            else:
                failed.append({"candidate_id": candidate_id, "error": result.get("error", "Unknown error"), "status": status_code})

        return self._response(
            HTTPStatus.OK,
            {
                "success": True,
                "data": {
                    "action": action,
                    "requested_count": len(candidate_ids),
                    "success_count": len(succeeded),
                    "failure_count": len(failed),
                    "succeeded": succeeded,
                    "failed": failed,
                },
            },
        )

    def _handle_candidate_promote(self, candidate_id: str, body: bytes) -> tuple[int, dict[str, Any]]:
        if not candidate_id:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": "candidate_id is required"})
        try:
            mapping = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError as exc:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": f"Invalid JSON body: {exc.msg}"})
        try:
            result = self.promoter.promote_candidate(candidate_id, mapping)
        except LookupError as exc:
            return self._response(HTTPStatus.NOT_FOUND, {"success": False, "error": str(exc)})
        except ValueError as exc:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": str(exc)})
        return self._response(HTTPStatus.OK, {"success": True, "data": result})

    def _handle_candidate_batch_promote(self, body: bytes) -> tuple[int, dict[str, Any]]:
        try:
            payload = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError as exc:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": f"Invalid JSON body: {exc.msg}"})

        items = payload.get("items")
        if not isinstance(items, list) or not items:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": "items must be a non-empty list"})

        succeeded: list[dict[str, Any]] = []
        failed: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                failed.append({"candidate_id": None, "error": "Each item must be an object"})
                continue
            candidate_id = str(item.get("candidate_id") or "").strip()
            if not candidate_id:
                failed.append({"candidate_id": candidate_id, "error": "candidate_id is required"})
                continue
            mapping = item.get("mapping")
            if mapping is None:
                mapping = {}
            if not isinstance(mapping, dict):
                failed.append({"candidate_id": candidate_id, "error": "mapping must be an object"})
                continue
            status_code, result = self._handle_candidate_promote(candidate_id, json.dumps(mapping).encode("utf-8"))
            if status_code == int(HTTPStatus.OK):
                succeeded.append(result["data"])
            else:
                failed.append({"candidate_id": candidate_id, "error": result.get("error", "Unknown error"), "status": status_code})

        return self._response(
            HTTPStatus.OK,
            {
                "success": True,
                "data": {
                    "requested_count": len(items),
                    "success_count": len(succeeded),
                    "failure_count": len(failed),
                    "succeeded": succeeded,
                    "failed": failed,
                },
            },
        )

    def _handle_candidate_batch_auto_promote(self, body: bytes) -> tuple[int, dict[str, Any]]:
        try:
            payload = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError as exc:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": f"Invalid JSON body: {exc.msg}"})

        policy = str(payload.get("policy") or "").strip()
        if not policy:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": "policy is required"})

        dry_run = payload.get("dry_run", False)
        if not isinstance(dry_run, bool):
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": "dry_run must be a boolean"})

        items = payload.get("items")
        if not isinstance(items, list) or not items:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": "items must be a non-empty list"})

        if dry_run:
            eligible: list[dict[str, Any]] = []
            ineligible: list[dict[str, Any]] = []
            for item in items:
                if not isinstance(item, dict):
                    ineligible.append({
                        "candidate_id": None,
                        "eligible": False,
                        "reasons": ["Each item must be an object"],
                        "status": int(HTTPStatus.BAD_REQUEST),
                    })
                    continue
                candidate_id = str(item.get("candidate_id") or "").strip()
                if not candidate_id:
                    ineligible.append({
                        "candidate_id": candidate_id,
                        "eligible": False,
                        "reasons": ["candidate_id is required"],
                        "status": int(HTTPStatus.BAD_REQUEST),
                    })
                    continue
                mapping = item.get("mapping")
                if mapping is None:
                    mapping = {}
                if not isinstance(mapping, dict):
                    ineligible.append({
                        "candidate_id": candidate_id,
                        "eligible": False,
                        "reasons": ["mapping must be an object"],
                        "status": int(HTTPStatus.BAD_REQUEST),
                    })
                    continue
                try:
                    result = self.promoter.preview_auto_promote_candidate(candidate_id, mapping, policy=policy)
                except LookupError as exc:
                    ineligible.append({
                        "candidate_id": candidate_id,
                        "eligible": False,
                        "reasons": [str(exc)],
                        "status": int(HTTPStatus.NOT_FOUND),
                    })
                else:
                    if result.get("eligible"):
                        eligible.append(result)
                    else:
                        ineligible.append({
                            **result,
                            "status": int(HTTPStatus.BAD_REQUEST),
                        })

            return self._response(
                HTTPStatus.OK,
                {
                    "success": True,
                    "data": {
                        "policy": policy,
                        "dry_run": True,
                        "requested_count": len(items),
                        "eligible_count": len(eligible),
                        "ineligible_count": len(ineligible),
                        "eligible": eligible,
                        "ineligible": ineligible,
                    },
                },
            )

        succeeded: list[dict[str, Any]] = []
        failed: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                failed.append({"candidate_id": None, "error": "Each item must be an object"})
                continue
            candidate_id = str(item.get("candidate_id") or "").strip()
            if not candidate_id:
                failed.append({"candidate_id": candidate_id, "error": "candidate_id is required"})
                continue
            mapping = item.get("mapping")
            if mapping is None:
                mapping = {}
            if not isinstance(mapping, dict):
                failed.append({"candidate_id": candidate_id, "error": "mapping must be an object"})
                continue
            try:
                result = self.promoter.auto_promote_candidate(candidate_id, mapping, policy=policy)
            except LookupError as exc:
                failed.append({"candidate_id": candidate_id, "error": str(exc), "status": int(HTTPStatus.NOT_FOUND)})
            except ValueError as exc:
                failed.append({"candidate_id": candidate_id, "error": str(exc), "status": int(HTTPStatus.BAD_REQUEST)})
            else:
                succeeded.append(result)

        return self._response(
            HTTPStatus.OK,
            {
                "success": True,
                "data": {
                    "policy": policy,
                    "dry_run": False,
                    "requested_count": len(items),
                    "success_count": len(succeeded),
                    "failure_count": len(failed),
                    "succeeded": succeeded,
                    "failed": failed,
                },
            },
        )

    def _handle_candidate_merge(self, candidate_id: str, body: bytes) -> tuple[int, dict[str, Any]]:
        if not candidate_id:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": "candidate_id is required"})
        try:
            mapping = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError as exc:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": f"Invalid JSON body: {exc.msg}"})
        try:
            result = self.promoter.merge_candidate(candidate_id, mapping)
        except LookupError as exc:
            return self._response(HTTPStatus.NOT_FOUND, {"success": False, "error": str(exc)})
        except ValueError as exc:
            return self._response(HTTPStatus.BAD_REQUEST, {"success": False, "error": str(exc)})
        return self._response(HTTPStatus.OK, {"success": True, "data": result})

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