"""Importer for MiroFish scenario result bundles."""

from __future__ import annotations

from typing import Any

from src.application.integration.dto import CandidateDelta, MiroFishResultBundle, RuntimeEvidenceRecord
from src.infrastructure.mirofish_writeback_store import MiroFishWriteBackStore


class MiroFishResultImporter:
    """Persist MiroFish result bundles into the write-back evidence vault."""

    def __init__(self, store: MiroFishWriteBackStore):
        self.store = store

    def import_result_bundle(self, payload: dict[str, Any]) -> dict[str, Any]:
        bundle = MiroFishResultBundle.from_dict(payload)
        evidence = bundle.runtime_evidence or self._derive_runtime_evidence(bundle)
        candidates = bundle.candidate_deltas or self._derive_candidate_deltas(bundle, evidence)
        saved = self.store.save_import(bundle, evidence, candidates)
        return {
            **saved,
            "derived_runtime_evidence": not bool(bundle.runtime_evidence),
            "derived_candidate_deltas": not bool(bundle.candidate_deltas),
        }

    def _derive_runtime_evidence(self, bundle: MiroFishResultBundle) -> list[RuntimeEvidenceRecord]:
        payload = bundle.raw_payload
        records: list[RuntimeEvidenceRecord] = []
        records.extend(self._records_from_collection(bundle, payload.get("emergent_events") or [], evidence_type="world_event", source_type="emergent_event"))
        records.extend(self._records_from_collection(bundle, payload.get("relationship_changes") or [], evidence_type="relationship_change", source_type="relationship_delta"))
        rumor_items = payload.get("rumor_candidates") or payload.get("rumors") or bundle.prediction_summary.get("rumors") or []
        records.extend(self._records_from_collection(bundle, rumor_items, evidence_type="rumor_signal", source_type="prediction_summary"))
        summary_text = str(bundle.prediction_summary.get("summary") or bundle.prediction_summary.get("conflict_summary") or "").strip()
        if summary_text:
            records.append(RuntimeEvidenceRecord.from_dict({
                "evidence_type": "state_summary",
                "source_type": "prediction_summary",
                "text": summary_text,
                "structured_payload": bundle.prediction_summary,
                "timestamp": bundle.generated_at,
                "confidence": bundle.prediction_summary.get("confidence", 0.55),
                "source_refs": [{"collection": "prediction_summary", "key": "summary"}],
            }, world_id=bundle.world_id, scenario_id=bundle.scenario_id, run_id=bundle.run_id))
        return records

    def _records_from_collection(self, bundle: MiroFishResultBundle, items: list[Any], *, evidence_type: str, source_type: str) -> list[RuntimeEvidenceRecord]:
        records: list[RuntimeEvidenceRecord] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                item = {"text": str(item)}
            text = str(item.get("text") or item.get("summary") or item.get("description") or item.get("name") or "").strip()
            if not text:
                continue
            records.append(RuntimeEvidenceRecord.from_dict({
                "evidence_type": evidence_type,
                "source_type": source_type,
                "text": text,
                "structured_payload": item,
                "actor_refs": item.get("actor_refs") or item.get("participant_ids") or [],
                "timestamp": item.get("timestamp") or bundle.generated_at,
                "confidence": item.get("confidence", 0.6),
                "source_refs": [{"collection": source_type, "index": index}],
            }, world_id=bundle.world_id, scenario_id=bundle.scenario_id, run_id=bundle.run_id))
        return records

    def _derive_candidate_deltas(self, bundle: MiroFishResultBundle, evidence: list[RuntimeEvidenceRecord]) -> list[CandidateDelta]:
        evidence_map = self._index_evidence_ids(evidence)
        payload = bundle.raw_payload
        candidates: list[CandidateDelta] = []
        candidates.extend(self._candidates_from_collection(bundle, payload.get("emergent_events") or [], evidence_map, candidate_type="scenario_event", target_canonical_type="Event", source_collection="emergent_event"))
        candidates.extend(self._candidates_from_collection(bundle, payload.get("relationship_changes") or [], evidence_map, candidate_type="relationship_change", target_canonical_type="CharacterRelationship", source_collection="relationship_delta"))
        rumor_items = payload.get("rumor_candidates") or payload.get("rumors") or bundle.prediction_summary.get("rumors") or []
        candidates.extend(self._candidates_from_collection(bundle, rumor_items, evidence_map, candidate_type="rumor_candidate", target_canonical_type="Rumor", source_collection="prediction_summary"))
        return candidates

    def _candidates_from_collection(
        self,
        bundle: MiroFishResultBundle,
        items: list[Any],
        evidence_map: dict[tuple[str, int], list[str]],
        *,
        candidate_type: str,
        target_canonical_type: str,
        source_collection: str,
    ) -> list[CandidateDelta]:
        candidates: list[CandidateDelta] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                item = {"summary": str(item), "name": str(item)}
            name = str(item.get("name") or item.get("title") or item.get("summary") or target_canonical_type).strip()
            summary = str(item.get("summary") or item.get("description") or name).strip()
            candidates.append(CandidateDelta.from_dict({
                "candidate_type": candidate_type,
                "target_canonical_type": target_canonical_type,
                "name": name,
                "summary": summary,
                "proposed_change": item,
                "evidence_ids": evidence_map.get((source_collection, index), []),
                "source_refs": [{"collection": source_collection, "index": index}],
                "confidence": item.get("confidence", 0.6),
            }, world_id=bundle.world_id, scenario_id=bundle.scenario_id, run_id=bundle.run_id))
        return candidates

    def _index_evidence_ids(self, evidence: list[RuntimeEvidenceRecord]) -> dict[tuple[str, int], list[str]]:
        indexed: dict[tuple[str, int], list[str]] = {}
        for item in evidence:
            for source_ref in item.source_refs:
                collection = source_ref.get("collection")
                index = source_ref.get("index")
                if collection is None or not isinstance(index, int):
                    continue
                indexed.setdefault((str(collection), index), []).append(item.evidence_id)
        return indexed