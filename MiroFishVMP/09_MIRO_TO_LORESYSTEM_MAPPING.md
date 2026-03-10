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

### 4.1 Deterministic evidence identity

Для derived evidence path действует правило:

- если исходный bundle уже прислал `evidence_id`, он сохраняется как есть,
- если evidence собирается/importer'ом из runtime payload, `RuntimeEvidenceRecord` строит детерминированный fingerprint-based `evidence_id` из нормализованного payload.

Практический смысл:

- одинаковый evidence на same-db rerun получает тот же `evidence_id`,
- rerun-safe sync может обновить existing row вместо delete/recreate churn.

### 4.2 Derived read model

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
| `candidate_type` | `candidate_type` | `candidate_type` | review / merge / promote routing key |
| `target_canonical_type` | `target_canonical_type` | `target_canonical_type` | set after merge/promote if not already present |
| `target_canonical_id` | `target_canonical_id` | `target_canonical_id` | set after merge/promote |
| `proposed_entity_type` | `proposed_entity_type` | `proposed_entity_type` | optional |
| `name` | `name` | `name` | candidate label |
| `summary` | `summary` | `summary` | candidate text |
| `proposed_change` | `proposed_change` | `proposed_change_json` | canonical mapping payload source |
| `evidence_ids[]` | `evidence_ids` | `evidence_ids_json` | evidence linkage |
| `source_refs[]` | `source_refs` | `source_refs_json` | supporting refs |
| `status` | `status` | `status` | `pending_review` → `approved` / `rejected` / `promoted` / `merged` |

### 5.1 Deterministic candidate identity

Для candidate layer действует аналогичное правило:

- explicit `candidate_id` из bundle сохраняется как есть,
- derived candidate получает детерминированный fingerprint-based `candidate_id` из нормализованного candidate payload.

Это делает safe два ключевых сценария:

- same-db rerun может переиспользовать уже существующий promoted candidate-path,
- canonical entity может оставаться привязанной к тому же `source_candidate_id`.

### 5.2 Candidate types currently supported

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

## 6.1 Recommended lore-generation arc

Если `MiroFish` используется как generator narrative/lore, то самый удобный mapping сейчас такой:

- **Act I — Rumor seed**
  - основной выход: `prediction_summary.rumors[]`
  - candidate path: `rumor_candidate`
  - canonical target: `Rumor`
- **Act II — Escalation**
  - основной выход: `emergent_events[]` + дополнительный `runtime_evidence`
  - candidate path: `scenario_event`
  - canonical target: `Event`
- **Act III — Resolution / Fallout**
  - основной выход: `relationship_changes[]` и при необходимости explicit `new_entity_candidate`
  - candidate path: `relationship_change` / `new_entity_candidate`
  - canonical target: `CharacterRelationship` или manual create/merge для `Location` / `Faction` / `Character`

Такой порядок хорош тем, что генерация начинает с soft claim, а hard-canon появляется только после narrative escalation и evidence accumulation.

## 6.2 Merge semantics

Текущий `merge` flow специально ограничен безопасной семантикой:

- merge работает только в уже существующий `mirofish_canonical_entities.canonical_id`,
- новый canonical snapshot при merge не создаётся,
- candidate получает `status = merged` и `target_canonical_*`,
- provenance-связь пишется как `relation_type = merged_into`.

## 7. Provenance mapping

| Source | loreSystem layer | Target |
|---|---|---|
| generic generation run | `GenerationRunRecord` | `LoreData.metadata.generation_runs` |
| generic entity provenance | `EntityProvenanceLink` | `LoreData.metadata.entity_provenance` |
| promoted write-back entity | run-link persistence (`promoted_from`) | `mirofish_entity_run_links` |
| merged write-back candidate | run-link persistence (`merged_into`) | `mirofish_entity_run_links` |
| `candidate_id` used for promotion | `source_candidate_id` | `mirofish_canonical_entities.source_candidate_id` |
| promoted/merged entity provenance | `run_id + candidate_id + evidence_ids` | `mirofish_entity_run_links` |

## 8. End-to-end trace that works now

Текущая рабочая цепочка выглядит так:

1. `MiroFish result bundle`
2. `actors[]` / `organizations[]` → `mirofish_run_subjects`
3. `runtime_evidence.actor_refs` → `linked_subjects`
4. `candidate_deltas` → review / approve / reject
5. single candidate detail доступен через `GET /api/mirofish/writeback/candidate-deltas/{candidate_id}`
6. batch review / batch promotion могут вызывать те же операции для нескольких candidate за один запрос
7. explicit `batch/auto-promote` может narrow-gate'ить safe `scenario_event -> Event`, `rumor_candidate -> Rumor` и `relationship_change -> CharacterRelationship` candidates, включая cross-run event/rumor/relationship slices, и вызывать тот же promote path; optional `dry_run: true` даёт preview этого же пути без side effects
8. explicit `batch/auto-merge` может narrow-gate'ить safe exact duplicate merge для `new_entity_candidate -> Location` через policy `safe_existing_location_duplicate_only`, для `scenario_event -> Event` через policy `safe_existing_event_duplicate_only`, для `rumor_candidate -> Rumor` через policy `safe_existing_rumor_duplicate_only` и для `relationship_change -> CharacterRelationship` через policy `safe_existing_relationship_duplicate_only`, после чего вызывает тот же existing merge path; optional `dry_run: true` даёт preview без side effects
9. approved/auto-approved candidate → либо promote в canonical entity, либо merge в existing canonical entity
10. `new_entity_candidate` может вручную создавать staged `Location` / `Faction` / `Character` через тот же `promote` path
11. canonical entity / merge-linkage → `mirofish_entity_run_links`

## 8.1 Same-DB rerun semantics

При повторном ingest того же logical run в ту же SQLite БД действуют такие правила:

- connection provider store включает `PRAGMA foreign_keys = ON`,
- `mirofish_scenario_runs` / `mirofish_scenario_results` обновляются через upsert, а не через destructive replace,
- `runtime_evidence` и `candidate_deltas` синхронизируются через rerun-safe sync/upsert semantics,
- unchanged rows сохраняют прежнюю identity, stale rows удаляются, changed rows обновляются,
- повторный promote того же неизменившегося candidate переиспользует existing canonical row и existing run-link,
- итоговые counts после двух проходов остаются стабильными.

Подтверждённый smoke result после фикса:

- `scenario_runs = 1`
- `runtime_evidence = 4`
- `candidate_deltas = 3`
- `run_subjects = 5`
- `canonical_entities = 3`
- `entity_run_links = 3`

Правило стабильности теперь такое:

- если candidate content не изменился, то сохраняются те же `candidate_id` и `canonical_id`,
- если candidate/evidence content изменился, fingerprint меняется и система рассматривает это как новый candidate-path.

## 9. Practical summary

Сейчас система реально умеет хранить и читать назад:

- run metadata
- raw bundle archive
- runtime actors
- runtime organizations
- runtime evidence
- linked evidence subjects
- reviewable candidate deltas
- single-candidate review detail
- batch review / batch promotion API
- narrow batch auto-promotion API (`safe_event_only`, `safe_cross_run_event_only`, `safe_rumor_only`, `safe_cross_run_rumor_only`, `safe_relationship_only`, `safe_cross_run_relationship_only`)
- narrow batch auto-merge API (`safe_existing_location_duplicate_only`, `safe_existing_event_duplicate_only`, `safe_existing_rumor_duplicate_only`, `safe_existing_relationship_duplicate_only`)
- promoted canonical `Event`
- promoted canonical `Rumor`
- promoted canonical `CharacterRelationship`
- manually created staged `Location`
- manually created staged `Faction`
- manually created staged `Character`
- merged candidate linkage в existing staged canonical entity
- explicit `run -> canonical entity` provenance links

## 9.1 Batch API semantics

Текущая batch-семантика намеренно простая:

- batch review и batch promote являются wrapper'ом над single-candidate endpoint semantics,
- batch auto-promote тоже работает как wrapper над существующим promote path,
- batch auto-promote с `dry_run: true` работает как explain/preview wrapper над тем же promote path,
- batch auto-merge тоже работает как wrapper над существующим merge path,
- batch auto-merge с `dry_run: true` работает как explain/preview wrapper над тем же merge path,
- manual create для `Location` / `Faction` / `Character` тоже использует тот же single-candidate promote path,
- каждый item обрабатывается независимо,
- ответ агрегирует `requested_count`, `success_count`, `failure_count`, `succeeded[]`, `failed[]`,
- частичный успех считается нормальным и не откатывает уже успешные элементы.

Текущий `dry_run` intentionally narrow:

- доступен на existing `batch/auto-promote` и `batch/auto-merge` endpoints
- принимает те же `policy` и `items[]` для соответствующего endpoint
- возвращает `eligible[]` / `ineligible[]` вместо реального promote / merge результата
- даёт per-item `reasons`
- при успешном preview возвращает `metadata_preview`
- не меняет candidate status и не создаёт canonical entity / run-link записи

Текущий auto-promote intentionally narrow:

- policy names:
  - `safe_event_only`
  - `safe_cross_run_event_only`
  - `safe_rumor_only`
  - `safe_cross_run_rumor_only`
  - `safe_relationship_only`
  - `safe_cross_run_relationship_only`
- во всех safe policy только `confidence >= 0.90`
- во всех safe policy только минимум `2 evidence_ids`
- `safe_event_only` → только `scenario_event -> Event`
- `safe_cross_run_event_only` → только `scenario_event -> Event`, сначала проходит все требования `safe_event_only`, затем требует participant set + terminal outcome + UTC date bucket support хотя бы из одного дополнительного run и отклоняет conflicting staged canonical `Event` с тем же participant set / date bucket, но другим terminal outcome
- `safe_rumor_only` → только `rumor_candidate -> Rumor` и требует `source_name` + `credibility_score`
- `safe_cross_run_rumor_only` → только `rumor_candidate -> Rumor`, сначала проходит все требования `safe_rumor_only`, затем требует explicit `location_id`, unresolved truth bucket (`Unverified` / `Partially True`), хотя бы один supporting run с тем же normalized rumor `name` / `source_name` / unresolved truth bucket и отклоняет existing staged canonical `Rumor` с тем же normalized `name` / `source_name` / `location_id`
- `safe_relationship_only` → только `relationship_change -> CharacterRelationship` и требует `character_from_id`, `character_to_id`, `relationship_level`, плюс `abs(relationship_level) >= 30`
- `safe_cross_run_relationship_only` → только `relationship_change -> CharacterRelationship`, сначала проходит все требования `safe_relationship_only`, затем требует хотя бы один supporting run с тем же directed `actor_refs` и той же polarity и отклоняет opposite-polarity staged canonical relationship для той же directed pair
- provenance metadata содержит `auto_promote_policy` и `auto_promoted`; для cross-run event slice ещё пишутся `cross_run_supporting_run_ids`, `cross_run_distinct_run_count`, `event_match_participant_refs`, `event_match_outcome`, `event_match_date_bucket`, `contradiction_check`, для cross-run rumor slice — `cross_run_supporting_run_ids`, `cross_run_distinct_run_count`, `rumor_match_name`, `rumor_match_source_name`, `rumor_truth_bucket`, `duplicate_guard`, а для cross-run relationship slice — `cross_run_supporting_run_ids`, `cross_run_distinct_run_count`, `contradiction_check`

Текущий auto-merge тоже intentionally narrow:

- endpoint: `POST /api/mirofish/writeback/candidate-deltas/batch/auto-merge`
- policy names:
  - `safe_existing_location_duplicate_only`
  - `safe_existing_event_duplicate_only`
  - `safe_existing_rumor_duplicate_only`
  - `safe_existing_relationship_duplicate_only`
- `safe_existing_location_duplicate_only` → только `new_entity_candidate -> Location`
- `safe_existing_event_duplicate_only` → только `scenario_event -> Event`
- `safe_existing_rumor_duplicate_only` → только `rumor_candidate -> Rumor`
- `safe_existing_relationship_duplicate_only` → только `relationship_change -> CharacterRelationship`
- только `confidence >= 0.90`
- только минимум `2 evidence_ids`
- mapping обязан содержать explicit `world_id`
- exact duplicate определяется только по normalized `name` + `location_type` + `parent_location_id` + `world_id`
- event exact duplicate определяется только по canonical participant set + terminal `outcome` + UTC date bucket + optional `location_id` + `world_id`
- rumor exact duplicate определяется только по normalized `name` + normalized `source_name` + unresolved truth bucket + `location_id` + `world_id`
- relationship exact duplicate определяется только по `character_from_id` + `character_to_id` + `relationship_type` + `relationship_level` + `is_mutual` + `world_id`
- event policy дополнительно требует `proposed_change.participant_ids`, `proposed_change.timestamp`, terminal non-ongoing `outcome` и resolve canonical participants через explicit `participant_ids` или `participant_map`
- rumor policy дополнительно требует explicit/resolvable `source_name`, explicit/resolvable `location_id` и unresolved truth bucket (`Unverified` / `Partially True`)
- relationship policy дополнительно требует explicit `character_from_id`, `character_to_id`, `relationship_level`, разные стороны, `abs(relationship_level) >= 30`; `relationship_type` может быть передан явно или выводится из `relationship_level`, `is_mutual` резолвится из mapping
- policy требует ровно один staged canonical `Location` match и reject'ит no-match / ambiguous-match случаи
- event policy тоже требует ровно один staged canonical `Event` match и reject'ит no-match / ambiguous-match случаи
- rumor policy тоже требует ровно один staged canonical `Rumor` match и reject'ит no-match / ambiguous-match случаи
- relationship policy тоже требует ровно один staged canonical `CharacterRelationship` match и reject'ит no-match / ambiguous-match случаи
- provenance metadata содержит `auto_merge_policy`, `auto_merged`; location slice дополнительно пишет `merge_match_name`, `merge_match_location_type`, `merge_match_parent_location_id`, `duplicate_guard`, event slice — `event_match_participant_refs`, `event_match_outcome`, `event_match_date_bucket`, `merge_match_location_id`, `duplicate_guard`, rumor slice — `merge_match_name`, `merge_match_source_name`, `merge_match_location_id`, `rumor_truth_bucket`, `duplicate_guard`, relationship slice — `merge_match_character_from_id`, `merge_match_character_to_id`, `merge_match_relationship_type`, `merge_match_relationship_level`, `merge_match_is_mutual`, `duplicate_guard`

Manual create/merge для новых entity types сейчас intentionally explicit:

- candidate type обычно `new_entity_candidate`
- `Location` требует `location_type`
- `Faction` требует `faction_type` и `alignment`
- `Character` требует canonical-grade `backstory`
- merge для этих типов использует тот же existing `canonical_id`-based path