# MiroFish ↔ loreSystem Mapping Matrix

## 1. Scope

Этот файл — прикладная шпаргалка по тому, как поля и сущности из MiroFish result bundle сейчас маппятся в staging/write-back слой `loreSystem`.

Покрывает:

- runtime subjects (`actors`, `organizations`)
- runtime evidence
- candidate deltas
- promote в canonical entities
- provenance / run-link слой
- repeat-run semantics в той же SQLite БД

## 2. Result bundle envelope

| MiroFish field | loreSystem DTO / layer | SQLite / runtime target | Notes |
|---|---|---|---|
| `schema_version` | `MiroFishResultBundle.schema_version` | `mirofish_scenario_runs.schema_version` | metadata run-level |
| `world_id` | `MiroFishResultBundle.world_id` | `mirofish_scenario_runs.world_id` | string world ref from MiroFish side |
| `scenario_id` | `MiroFishResultBundle.scenario_id` | `mirofish_scenario_runs.scenario_id` | string scenario ref |
| `run_id` | `MiroFishResultBundle.run_id` | `mirofish_scenario_runs.run_id` | primary run key |
| `generated_at` | `MiroFishResultBundle.generated_at` | `mirofish_scenario_runs.generated_at` | run timestamp |
| `world_version` | `MiroFishResultBundle.world_version` | `mirofish_scenario_runs.world_version` | optional |
| `projection_version` | `MiroFishResultBundle.projection_version` | `mirofish_scenario_runs.projection_version` | optional |
| `source_backend` | `MiroFishResultBundle.source_backend` | `mirofish_scenario_runs.source_backend` | default `mirofish` |
| full raw payload | `MiroFishResultBundle.raw_payload` | `mirofish_scenario_results.bundle_json` | raw archive of original result bundle |

## 3. Runtime subjects

### 3.1 Actors / organizations

| MiroFish field | loreSystem DTO | SQLite target | Notes |
|---|---|---|---|
| `actors[]` | `RunSubjectRecord(subject_kind="actor")` | `mirofish_run_subjects` | normalized runtime actor rows |
| `organizations[]` | `RunSubjectRecord(subject_kind="organization")` | `mirofish_run_subjects` | normalized runtime organization rows |
| `id` | `subject_ref` | `subject_ref` | examples: `actor:royal_court`, `org:town_criers` |
| `name` | `name` | `name` | human-readable subject label |
| `canonical_id` | `canonical_id` | `canonical_id` | upstream canonical pointer if known |
| `canonical_type` | `canonical_type` | `canonical_type` | e.g. `Character`, `Faction` |
| `speaker_mode` | `speaker_mode` | `speaker_mode` | e.g. `individual`, `representative`, `official_account` |
| `represented_entity_id` | `represented_entity_id` | `represented_entity_id` | e.g. actor speaks for org |
| extra keys | `metadata` / `source_payload` | `metadata_json` / `source_payload_json` | preserved for auditability |

### 3.2 What is supported now

Сейчас поддерживаются runtime subject kinds:

- `actor`
- `organization`

Они **staged/queryable**, но **не promote-ятся напрямую** в canonical layer отдельным workflow.

## 4. Runtime evidence

| MiroFish field | loreSystem DTO | SQLite target | Notes |
|---|---|---|---|
| `runtime_evidence[]` | `RuntimeEvidenceRecord` | `mirofish_runtime_evidence` | explicit evidence path |
| derived `prediction_summary.rumors[]` | derived `RuntimeEvidenceRecord` | `mirofish_runtime_evidence` | when explicit evidence missing |
| derived `emergent_events[]` | derived `RuntimeEvidenceRecord` | `mirofish_runtime_evidence` | when explicit evidence missing |
| derived `relationship_changes[]` | derived `RuntimeEvidenceRecord` | `mirofish_runtime_evidence` | when explicit evidence missing |
| `actor_refs[]` | `actor_refs` | `actor_refs_json` | raw refs to runtime subjects |
| `canonical_refs[]` | `canonical_refs` | `canonical_refs_json` | optional canonical object refs |
| `text` / `summary` / `name` | `text` | `text` | normalized evidence text |
| `structured_payload` | `structured_payload` | `structured_payload_json` | original evidence-level payload |
| `source_refs[]` | `source_refs` | `source_refs_json` | supporting references |

### 4.1 Derived read model

При readback через store/API evidence дополнительно получает:

- `linked_subjects`

Mapping:

- `runtime_evidence.actor_refs[*]`
- → match by `mirofish_run_subjects.subject_ref`
- → return normalized subject rows in `linked_subjects`

## 5. Candidate deltas

| MiroFish field | loreSystem DTO | SQLite target | Notes |
|---|---|---|---|
| `candidate_deltas[]` | `CandidateDelta` | `mirofish_candidate_deltas` | explicit candidate path |
| derived event/rumor/relationship outputs | derived `CandidateDelta` | `mirofish_candidate_deltas` | when explicit candidate list missing |
| `candidate_type` | `candidate_type` | `candidate_type` | review / promote routing key |
| `target_canonical_type` | `target_canonical_type` | `target_canonical_type` | set after promote if not already present |
| `target_canonical_id` | `target_canonical_id` | `target_canonical_id` | set after promote |
| `proposed_entity_type` | `proposed_entity_type` | `proposed_entity_type` | optional |
| `name` | `name` | `name` | candidate label |
| `summary` | `summary` | `summary` | candidate text |
| `proposed_change` | `proposed_change` | `proposed_change_json` | canonical mapping payload source |
| `evidence_ids[]` | `evidence_ids` | `evidence_ids_json` | evidence linkage |
| `source_refs[]` | `source_refs` | `source_refs_json` | supporting refs |
| `status` | `status` | `status` | `pending_review` → `approved` / `rejected` / `promoted` |

### 5.1 Candidate types currently supported

Сейчас review/promote flow реально поддерживает:

- `scenario_event`
- `rumor_candidate`
- `relationship_change`

## 6. Canonical promotion mapping

| Candidate type | loreSystem canonical entity | Status |
|---|---|---|
| `scenario_event` | `Event` | supported |
| `rumor_candidate` | `Rumor` | supported |
| `relationship_change` | `CharacterRelationship` | supported |
| `actor` / `organization` runtime subjects | direct promote target | not implemented |

## 7. Provenance mapping

| Source | loreSystem layer | Target |
|---|---|---|
| generic generation run | `GenerationRunRecord` | `LoreData.metadata.generation_runs` |
| generic entity provenance | `EntityProvenanceLink` | `LoreData.metadata.entity_provenance` |
| promoted write-back entity | run-link persistence | `mirofish_entity_run_links` |
| `candidate_id` used for promotion | `source_candidate_id` | `mirofish_canonical_entities.source_candidate_id` |
| promoted entity provenance | `run_id + candidate_id + evidence_ids` | `mirofish_entity_run_links` |

## 8. End-to-end trace that works now

Текущая рабочая цепочка выглядит так:

1. `MiroFish result bundle`
2. `actors[]` / `organizations[]` → `mirofish_run_subjects`
3. `runtime_evidence.actor_refs` → `linked_subjects`
4. `candidate_deltas` → review / approve / reject
5. approved candidate → canonical entity (`Event` / `Rumor` / `CharacterRelationship`)
6. canonical entity → `mirofish_entity_run_links`

## 8.1 Same-DB rerun semantics

При повторном ingest того же logical run в ту же SQLite БД действуют такие правила:

- connection provider store включает `PRAGMA foreign_keys = ON`,
- staging rows для того же `run_id` перезаписываются,
- старые `mirofish_canonical_entities` и `mirofish_entity_run_links`, связанные с предыдущим проходом, удаляются через cascade cleanup,
- итоговые counts после двух проходов остаются стабильными.

Подтверждённый smoke result после фикса:

- `scenario_runs = 1`
- `runtime_evidence = 4`
- `candidate_deltas = 3`
- `run_subjects = 5`
- `canonical_entities = 3`
- `entity_run_links = 3`

Нюанс: `canonical_id` и внутренние row ids могут измениться между проходами из-за SQLite autoincrement. Это нормальная часть текущего design — система идемпотентна по содержимому, а не по числовым surrogate IDs.

## 9. Practical summary

Сейчас система реально умеет хранить и читать назад:

- run metadata
- raw bundle archive
- runtime actors
- runtime organizations
- runtime evidence
- linked evidence subjects
- reviewable candidate deltas
- promoted canonical `Event`
- promoted canonical `Rumor`
- promoted canonical `CharacterRelationship`
- explicit `run -> canonical entity` provenance links