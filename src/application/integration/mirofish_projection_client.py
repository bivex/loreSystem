"""HTTP client for importing projection bundles into MiroFish."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def build_projection_import_payload(
    projection_bundle: dict[str, Any],
    *,
    simulation_requirement: str,
    project_name: str = "Projection Bundle Project",
    additional_context: str | None = None,
) -> dict[str, Any]:
    if not simulation_requirement.strip():
        raise ValueError("simulation_requirement is required")
    payload = {
        "project_name": project_name,
        "simulation_requirement": simulation_requirement,
        "projection_bundle": projection_bundle,
    }
    if additional_context:
        payload["additional_context"] = additional_context
    return payload


class MiroFishProjectionClient:
    """Send exported projection bundles to the MiroFish import API."""

    def __init__(self, base_url: str, timeout_seconds: int = 60):
        if not base_url.strip():
            raise ValueError("base_url is required")
        self.base_url = base_url.strip()
        self.timeout_seconds = timeout_seconds

    def import_bundle(
        self,
        projection_bundle: dict[str, Any],
        *,
        simulation_requirement: str,
        project_name: str = "Projection Bundle Project",
        additional_context: str | None = None,
    ) -> dict[str, Any]:
        payload = build_projection_import_payload(
            projection_bundle,
            simulation_requirement=simulation_requirement,
            project_name=project_name,
            additional_context=additional_context,
        )
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = Request(
            self._resolve_endpoint(),
            data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"MiroFish import failed with HTTP {exc.code}: {details}") from exc
        except URLError as exc:
            raise RuntimeError(f"Could not reach MiroFish import API: {exc}") from exc

        result = json.loads(raw)
        if not result.get("success", False):
            raise RuntimeError(f"MiroFish import returned an error: {result}")
        return result

    def _resolve_endpoint(self) -> str:
        base = self.base_url.rstrip("/")
        if base.endswith("/api/graph/projection/import"):
            return base
        if base.endswith("/api/graph"):
            return f"{base}/projection/import"
        return f"{base}/api/graph/projection/import"