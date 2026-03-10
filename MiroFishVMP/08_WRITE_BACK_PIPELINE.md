# Write-back pipeline: MiroFish -> loreSystem

## 1. Зачем нужен отдельный write-back pipeline

Forward path у интеграции уже понятен:

`loreSystem -> canonical world bundle -> social projection bundle -> MiroFish`

Но обратный путь нельзя делать как прямую запись в канон.

`MiroFish` возвращает не "истину мира", а результат вероятностного сценарного прогона. Поэтому между runtime-результатом и canonical lore нужен отдельный write-back pipeline.

Правильная формула:

`MiroFish result bundle -> runtime evidence -> candidate deltas -> review/promotion -> canonical lore`

## 1.1 Что уже реализовано в loreSystem

Статус на текущий момент:

- есть отдельный SQLite store `src/infrastructure/mirofish_writeback_store.py`
- есть importer `src/application/integration/importers/mirofish_result_importer.py`
- есть review/promote API `src/presentation/api/mirofish_writeback_api.py`
- есть promoter `src/application/integration/promoters/mirofish_candidate_promoter.py`
- canonical snapshots пишутся не в legacy repository layer, а в отдельную safe table `mirofish_canonical_entities`
- при ingest actors / organizations нормализуются в отдельную table `mirofish_run_subjects`
- evidence readback обогащается `linked_subjects`, резолвящими `actor_refs` в persisted subject rows
- provenance для обычных lore bundle теперь может храниться в top-level `LoreData.metadata`
- есть generic DTO shape для provenance:
  - `src/application/integration/dto/provenance.py`
  - `GenerationRunRecord`
  - `EntityProvenanceLink`
- после promote создаётся явная связь `run -> canonical entity` в `mirofish_entity_run_links`
- есть CLI:
  - `scripts/import_mirofish_results.py`
  - `scripts/run_mirofish_writeback_api.py`
  - `scripts/smoke_mirofish_writeback_workflow.py`
  - `scripts/autorun_mirofish_live_smoke.py`
- full live smoke уже прогнан против `lore_system.db` и подтвердил запись в БД:
  - `scenario_run`
  - `scenario_result`
  - `runtime_evidence`
  - `candidate_deltas`
  - `canonical_entities`
- `entity_run_links`
- `run_subjects`
- fresh-db и same-db (`--no-reset-db`) smoke сценарии подтверждены отдельно

Практический field-level mapping reference вынесен в `09_MIRO_TO_LORESYSTEM_MAPPING.md`.

## 1.2 Новый provenance layer

Теперь provenance хранится в двух комплементарных слоях.

### A. Generic lore provenance

Для обычных extraction/generation bundle добавлен top-level metadata layer в `src/presentation/gui/lore_data.py`:

- `metadata.generation_runs`
- `metadata.entity_provenance`

Он нужен для roundtrip-safe хранения истории генерации без загрязнения сотен доменных dataclass полями вроде `run_id`.

### B. Write-back promotion provenance

Для reverse path добавлена отдельная relation table `mirofish_entity_run_links`.

Она фиксирует:

- какой `run_id` породил promoted entity,
- из какого `candidate_id` она появилась,
- какие `evidence_ids` её поддерживали,
- какой тип связи используется (`promoted_from`),
- дополнительный metadata payload.

Это лучше, чем хранить provenance только косвенно через `source_candidate_id`, потому что:

- связь становится явной и queryable,
- можно поддержать `one run -> many canonical entities`,
- можно развивать `many runs -> one canonical entity` без изменения доменной модели.

## 1.3 Runtime subject layer

Чтобы key actors / organizations не терялись внутри raw bundle и строковых `actor_refs`, в reverse path добавлен отдельный нормализованный слой `mirofish_run_subjects`.

Он хранит:

- `subject_kind` (`actor` / `organization`)
- `subject_ref`
- `name`
- `canonical_id`
- `canonical_type`
- `speaker_mode`
- `represented_entity_id`
- `metadata`
- `source_payload`

Практически это даёт две вещи:

1. можно queryable-образом посмотреть, какие actors и organizations реально участвовали в конкретном run,
2. `runtime_evidence.actor_refs` теперь можно резолвить в нормализованные subject rows через поле `linked_subjects`.

Итоговая трассировка становится такой:

`scenario_run -> run_subjects -> runtime_evidence -> candidate_delta -> canonical_entity -> entity_run_link`

## 1.4 Repeat-run semantics и FK enforcement

После обнаружения бага на втором прогоне в ту же SQLite БД в connection provider store включён явный SQLite FK enforcement:

- `PRAGMA foreign_keys = ON` на каждом connection

Практический эффект такой:

- повторный ingest того же `run_id` корректно очищает старый run-scoped state,
- cascade cleanup теперь реально удаляет старые `mirofish_canonical_entities` и `mirofish_entity_run_links`,
- двухпроходный smoke на одной и той же БД больше не накапливает дубли.

Следующий слой стабилизации поверх этого фикса:

- derived `runtime_evidence` и `candidate_deltas` больше не получают случайные UUID, а строятся через детерминированный fingerprint от нормализованного payload,
- `mirofish_scenario_runs` / `mirofish_scenario_results` обновляются через upsert, а не через destructive `INSERT OR REPLACE`,
- `runtime_evidence` и `candidate_deltas` синхронизируются через rerun-safe sync/upsert semantics: unchanged rows сохраняются, stale rows удаляются, changed rows обновляются,
- повторный promote того же `candidate_id` переиспользует existing canonical row и existing run-link.

Подтверждённый same-db результат после фикса:

- `scenario_runs = 1`
- `runtime_evidence = 4`
- `candidate_deltas = 3`
- `run_subjects = 5`
- `canonical_entities = 3`
- `entity_run_links = 3`

Важно: текущая система теперь идемпотентна не только по **counts**, но и по identity для неизменившегося candidate-path.

То есть при same-db rerun, если candidate content не изменился:

- `candidate_id` остаётся тем же,
- `canonical_id` остаётся тем же,
- `entity_run_links` не дублируются.

Если же rerun реально меняет candidate/evidence content, fingerprint меняется и система сознательно рассматривает это как новый candidate-path. В этом случае новый `canonical_id` допустим и отражает новую версию результата, а не регрессию cleanup semantics.

## 2. Главный принцип

После первого поста или первого прогона мы **не пишем сразу в canon**.

Сразу сохраняются только:

- `scenario_run`
- `scenario_result`
- `runtime_evidence`
- `candidate_delta`

В canonical layer попадает только то, что:

- подтверждено несколькими evidence items,
- прошло dedupe с текущим каноном,
- прошло review или policy gate,
- может быть безопасно отображено на существующие доменные сущности `loreSystem`.

## 3. Что сохраняем сразу после прогона

### 3.1 Scenario run

Метаданные конкретного запуска:

- `world_id`
- `scenario_id`
- `run_id`
- `world_version`
- `projection_version`
- `generated_at`
- `source_backend = mirofish`

### 3.2 Scenario result

Полный immutable result bundle от `MiroFish`.

Это нужно для:

- повторного анализа,
- пересчёта candidates без нового прогона,
- аудита provenance,
- сравнения нескольких запусков.

### 3.3 Runtime evidence

Атомарные наблюдения из симуляции:

- post / reply / repost / quote,
- interview answer,
- action log,
- report fact,
- conflict summary,
- state summary.

Это слой наблюдений, а не слой канона.

В текущем API/store readback у evidence теперь есть enriched view:

- `actor_refs` — сырой список ссылок из bundle
- `linked_subjects` — нормализованные subject rows из `mirofish_run_subjects`, совпавшие по `subject_ref`

### 3.4 Candidate delta

Нормализованный кандидат на изменение мира:

- `scenario_event`
- `relationship_change`
- `faction_state_change`
- `location_state_change`
- `new_entity_candidate`
- `prediction_report`

### 3.5 Canonical promotion provenance

После successful promote теперь сохраняется не только canonical snapshot, но и отдельная provenance-запись в `mirofish_entity_run_links`.

Минимальные поля этой связи:

- `canonical_id`
- `canonical_type`
- `run_id`
- `source_candidate_id`
- `relation_type`
- `evidence_ids`
- `metadata`
- `linked_at`

Практически это означает, что promote теперь даёт аудит-цепочку:

`scenario_run -> candidate_delta -> canonical_entity -> entity_run_link`

## 4. Какие сущности реально поддерживать в MVP

Текущий реализованный MVP покрывает 3 группы:

- `scenario_event`
- `relationship_change`
- `rumor_candidate`

Это сознательно уже, чем auto-promote scope. `Location`, `Faction`, `Character` не попадают в policy-driven path и остаются только manual-review domain через explicit create/merge.

## 5. Что можно promote в canon в первую очередь

### 5.1 Event

Лучший первый target.

Маппинг:

- `agent_action_summary` -> `Event`
- `conflict_outcome` -> `Event`
- `world_event` -> `Event`

Почему это подходит:

- в текущем домене уже есть `Event.create(...)`,
- модель принимает `name`, `description`, `start_date`, `participant_ids`, optional `location_id`, `outcome`,
- это естественная форма для подтверждённого emergent события.

### 5.2 CharacterRelationship

Второй приоритет.

Маппинг:

- `trust_change` -> `CharacterRelationship`
- `hostility_change` -> `CharacterRelationship`

Почему это подходит:

- в текущем домене уже есть `CharacterRelationship.create(...)`,
- есть `update_relationship_level(delta, event_id)`,
- отношения хорошо выражаются как delta поверх уже существующего канона.

### 5.3 Rumor

Это лучший soft target для low-confidence social outcomes.

Маппинг:

- неустойчивое social propagation,
- single-run claim,
- narrative/social signal без жёсткого подтверждения.

Почему это подходит:

- в домене уже есть `Rumor.create(...)`,
- есть `truth_level`, `spread_speed`, `credibility_score`, `source_name`, `world_id`, `location_id`,
- это позволяет не загрязнять canon ложной определённостью.

Отсюда следует ещё один практический вывод для generation layer: **стартовать со слуха часто лучше всего**. Для лора это даёт естественную трёхактную форму:

- **Act I — Rumor seed**: появляется спорный сигнал, намёк, обвинение, предсказание или тревожный narrative hook
- **Act II — Escalation**: слух начинает менять поведение акторов и порождает observable events
- **Act III — Resolution**: история закрепляется в последствиях — отношениях, репутации, новых или уточнённых canonical entities

Для write-back pipeline это удобно потому, что ранняя стадия истории остаётся soft-canon (`Rumor`), а более жёсткие записи появляются только когда у истории уже есть evidence trail.

## 6. Что promote только после review

### 6.1 Location

Новая location может оказаться:

- alias существующей,
- временным названием,
- под-локацией, которую лучше связать с parent,
- hallucinated place.

Поэтому `Location` — manual review by default.

Минимально реализованный path теперь такой:

- reviewer получает `new_entity_candidate`
- делает `approve`
- либо вызывает existing `POST /candidate-deltas/{id}/promote` с explicit payload
- либо вызывает existing `POST /candidate-deltas/{id}/merge` в уже существующий staged `Location`
- для create обязательный минимум: `tenant_id`, `world_id`, `location_type`

### 6.2 Faction

Новый runtime group может быть:

- реальной новой организацией,
- временной коалицией,
- риторическим блоком,
- просто social cluster без canonical identity.

Поэтому `Faction` — только через candidate + review.

Текущий manual path:

- create идёт через existing `promote` endpoint
- merge идёт через existing `merge` endpoint
- для create обязательный минимум: `tenant_id`, `world_id`, `faction_type`, `alignment`
- optional link к лидеру задаётся через `leader_character_id`

### 6.3 Character

Это самый жёсткий случай.

В текущем домене `Character.create(...)` требует достаточно полноценный canonical profile, включая backstory. Runtime-персона легко может быть:

- alias существующего героя,
- representative account,
- observer persona,
- simulation-only role.

Поэтому новых `Character` на MVP автоматически не создаём.

При этом manual create теперь уже реализован, но только как explicit reviewer action:

- existing `promote` endpoint
- fully explicit payload
- canonical-grade `backstory` обязателен
- optional combat/location fields можно задавать отдельно

## 7. Что нельзя автоматически импортировать в canon

Нельзя без review/policy gate записывать в канон:

- внутренние рассуждения агентов,
- single-run hallucinated details,
- нестабильные локальные колебания,
- краткоживущие social spikes,
- simulation-only representative accounts,
- всё, что не резолвится в canonical IDs.

## 8. Рекомендуемый result bundle от MiroFish

Если `MiroFish` используется именно как generator лора, а не только как runtime simulation, то практический authoring pattern лучше делать таким:

- сценарий стартует со **слуха / disputed claim**
- bundle хранит evidence по трём narrative фазам
- поздние фазы должны давать материал не только для `Rumor`, но и для `Event`, `CharacterRelationship`, а иногда и для manual create/merge новых сущностей

Идеальная практическая трёхактная структура:

- **Act I — Setup / Rumor**
  - `prediction_summary.rumors[]`
  - early `runtime_evidence`
  - цель: задать tension, uncertainty, hook
- **Act II — Confrontation / Escalation**
  - `emergent_events[]`
  - дополнительные `runtime_evidence`
  - цель: превратить rumor в проверяемые действия и столкновения
- **Act III — Resolution / Fallout**
  - `relationship_changes[]`
  - `new_entity_candidate` при необходимости
  - цель: закрепить последствия в мире, factions, locations, characters, social state

Базовый shape:

```json
{
  "schema_version": "1.1",
  "world_id": "world-uuid",
  "scenario_id": "scenario-uuid",
  "run_id": "run-uuid",
  "generated_at": "2026-03-10T12:00:00Z",
  "actors": [],
  "organizations": [],
  "prediction_summary": {},
  "runtime_evidence": [],
  "candidate_deltas": []
}
```

Где:

- `actors` — runtime subjects вида `actor:*`
- `organizations` — runtime subjects вида `org:*`

Даже если evidence/candidates можно вывести эвристически, сами subjects полезно сохранять отдельно, чтобы не терять ключевых действующих лиц прогона.

Если `MiroFish` пока возвращает более простой bundle, importer в `loreSystem` может сам достраивать `runtime_evidence` и `candidate_deltas` из:

- `emergent_events`,
- `state_deltas`,
- `relationship_changes`,
- `timeline_branches`,
- report outputs.

## 9. Формат runtime evidence

Минимальная структура одной записи:

```json
{
  "evidence_id": "ev-uuid",
  "world_id": "world-uuid",
  "scenario_id": "scenario-uuid",
  "run_id": "run-uuid",
  "evidence_type": "post",
  "source_type": "runtime_action",
  "actor_refs": ["actor:1"],
  "canonical_refs": [{"type": "Character", "id": "123"}],
  "text": "Captain Aria publicly breaks with the Harbor Guild.",
  "structured_payload": {},
  "timestamp": "2026-03-10T12:10:00Z",
  "confidence": 0.82,
  "source_refs": []
}
```

При readback из API/store эта запись может дополнительно содержать derived поле:

```json
{
  "linked_subjects": []
}
```

`linked_subjects` не обязан приезжать из исходного result bundle — это enriched read model на стороне `loreSystem`.

Обязательные поля:

- `evidence_id`
- `world_id`
- `scenario_id`
- `run_id`
- `evidence_type`
- `source_type`
- `timestamp`
- `confidence`

## 10. Формат candidate delta

Минимальная структура:

```json
{
  "candidate_id": "cand-uuid",
  "world_id": "world-uuid",
  "scenario_id": "scenario-uuid",
  "run_id": "run-uuid",
  "candidate_type": "relationship_change",
  "target_canonical_type": "CharacterRelationship",
  "target_canonical_id": "456",
  "proposed_entity_type": null,
  "name": "Aria distrusts Boros more strongly",
  "summary": "Trust delta after dock conflict.",
  "proposed_change": {},
  "evidence_ids": ["ev-1", "ev-2"],
  "source_refs": [],
  "confidence": 0.84,
  "status": "pending_review",
  "created_at": "2026-03-10T12:20:00Z"
}
```

Обязательные поля:

- `candidate_id`
- `world_id`
- `scenario_id`
- `run_id`
- `candidate_type`
- `target_canonical_type` или `proposed_entity_type`
- `name`
- `summary`
- `proposed_change`
- `evidence_ids`
- `confidence`
- `status`
- `created_at`

### Статусы candidate

- `pending_review`
- `approved`
- `rejected`
- `promoted`
- `merged`

Дополнительно как future/planned statuses могут появиться:

- `observed`

## 11. Confidence model

Confidence лучше считать не LLM-словами, а детерминированным scoring из нескольких факторов:

- `evidence_count`
- `source_diversity`
- `cross_run_stability`
- `canonical_match_score`
- `contradiction_penalty`

Базовая политика:

- `< 0.35` -> raw evidence only
- `0.35 - 0.79` -> candidate yes, canon no
- `>= 0.80` -> candidate promotable
- `>= 0.90` + explicit policy -> narrow auto-promote допустим для safe slices

На MVP даже `>= 0.80` не должен автоматически писать в canon без review.

Минимально реализованный slice сейчас такой:

- policy `safe_event_only`
- explicit endpoint `POST /api/mirofish/writeback/candidate-deltas/batch/auto-promote`
- только по явно переданным `candidate_id`
- только при явном `mapping` payload для promote
- только для `scenario_event -> Event`
- только при `confidence >= 0.90`
- только при минимум `2 evidence_ids`
- auto-path оставляет audit metadata в `run_link.metadata`

## 12. Promotion rules по типам

### 12.1 Event

Promote, если:

- `confidence >= 0.80`,
- есть хотя бы 2 evidence items,
- participants резолвятся в canonical characters,
- location резолвится или nullable,
- нет явного contradiction с текущим canon.

### 12.2 CharacterRelationship

Promote, если:

- обе стороны резолвятся в canonical characters,
- знак и направление delta стабильны,
- изменение можно привязать к event/evidence cluster,
- delta не выглядит как single noisy fluctuation.

### 12.3 Rumor

Promote, если:

- сигнал narratively/socially важен,
- но evidence недостаточен для hard canon,
- есть source / location / credibility semantics.

### 12.4 Location

Promote, если:

- candidate не дублирует существующую location,
- name и description устойчивы,
- сигнал повторяется across evidence или runs,
- reviewer выбрал create или merge.

Практический manual create contract:

- existing endpoint: `POST /candidate-deltas/{candidate_id}/promote`
- candidate type обычно `new_entity_candidate`
- target canonical type: `Location`
- mapping payload должен содержать как минимум `tenant_id`, `world_id`, `location_type`
- optional: `parent_location_id`, `name`, `description`

### 12.5 Faction

Promote, если:

- это не temporary crowd,
- есть устойчивая identity,
- есть leader / mission / group boundary,
- reviewer явно подтвердил создание.

Практический manual create contract:

- existing endpoint: `POST /candidate-deltas/{candidate_id}/promote`
- candidate type обычно `new_entity_candidate`
- target canonical type: `Faction`
- mapping payload должен содержать как минимум `tenant_id`, `world_id`, `faction_type`, `alignment`
- optional: `leader_character_id`, `is_joinable`, `name`, `description`

### 12.6 Character

Promote только вручную, если:

- это не alias существующего character,
- есть достаточно материала для canonical backstory,
- нет признаков, что это simulation-only persona.

Практический manual create contract:

- existing endpoint: `POST /candidate-deltas/{candidate_id}/promote`
- candidate type обычно `new_entity_candidate`
- target canonical type: `Character`
- mapping payload должен содержать как минимум `tenant_id`, `world_id`, `backstory`
- optional: `status`, `location_id`, `rarity`, `element`, `role`, `base_hp`, `base_atk`, `base_def`, `base_speed`, `energy_cost`

## 13. Где это должно жить в коде

Так как exporter уже живёт в `src/application/integration/`, reverse path логично держать рядом.

Фактическая текущая структура:

- `src/application/integration/dto/mirofish_result_bundle.py`
- `src/application/integration/dto/runtime_evidence_record.py`
- `src/application/integration/dto/candidate_delta.py`
- `src/application/integration/dto/provenance.py`
- `src/application/integration/dto/run_subject_record.py`
- `src/application/integration/importers/mirofish_result_importer.py`
- `src/application/integration/promoters/mirofish_candidate_promoter.py`
- `src/infrastructure/mirofish_writeback_store.py`
- `src/presentation/api/mirofish_writeback_api.py`
- `scripts/import_mirofish_results.py`
- `scripts/run_mirofish_writeback_api.py`
- `scripts/smoke_mirofish_writeback_workflow.py`
- `tests/test_mirofish_result_importer.py`
- `tests/test_mirofish_candidate_promoter.py`
- `tests/test_mirofish_writeback_api.py`
- `tests/test_mirofish_writeback_smoke_script.py`

Важно: adapter layer должен оставаться отдельным от доменной модели. Он переводит simulation outputs в reviewable deltas, а не пишет напрямую в агрегаты при ingest.

## 14. Какие API нужны

### 14.1 Ingest API

Реально реализовано:

- `POST /api/mirofish/writeback/ingest`

Функция:

- принять result bundle,
- сохранить `scenario_run`,
- сохранить `scenario_result`,
- извлечь `runtime_evidence`,
- построить `candidate_deltas`.

### 14.2 Read API

Реально реализовано:

- `GET /api/mirofish/writeback/runs/{run_id}`
- `GET /api/mirofish/writeback/runs/{run_id}/evidence`
- `GET /api/mirofish/writeback/candidate-deltas?world_id=...&status=...&candidate_type=...`
- `GET /api/mirofish/writeback/candidate-deltas/{candidate_id}`

Важно:

- run detail теперь возвращает нормализованные `subjects.actors` и `subjects.organizations`
- evidence readback теперь возвращает `linked_subjects`
- candidate detail теперь возвращает `candidate`, `evidence_count`, `canonical_entity` и `run_links`

### 14.3 Review / merge / promotion API

Реально реализовано:

- `POST /api/mirofish/writeback/candidate-deltas/{candidate_id}/approve`
- `POST /api/mirofish/writeback/candidate-deltas/{candidate_id}/reject`
- `POST /api/mirofish/writeback/candidate-deltas/{candidate_id}/merge`
- `POST /api/mirofish/writeback/candidate-deltas/{candidate_id}/promote`
- `POST /api/mirofish/writeback/candidate-deltas/batch/review`
- `POST /api/mirofish/writeback/candidate-deltas/batch/promote`
- `POST /api/mirofish/writeback/candidate-deltas/batch/auto-promote`

Важно:

- `merge` не создаёт новый canonical snapshot, а привязывает approved candidate к уже существующему `mirofish_canonical_entities.canonical_id`
- provenance для merge пишется в `mirofish_entity_run_links` с `relation_type = merged_into`
- provenance для promote пишется с `relation_type = promoted_from`
- existing `promote` теперь покрывает не только `Event` / `Rumor` / `CharacterRelationship`, но и manual create для `Location` / `Faction` / `Character`
- `data.run_link`
- `data.canonical_entity.run_links`
- batch endpoints работают как per-item wrapper над существующими single-candidate операциями
- batch response возвращает `requested_count`, `success_count`, `failure_count`, `succeeded[]`, `failed[]`
- partial failure в batch допустим и не откатывает успешно обработанные элементы
- auto-promote сейчас не является background automation: это отдельный explicit batch endpoint
- auto-promote policy пока ограничена `safe_event_only` и не распространяется на `Rumor`/`CharacterRelationship`
- прошедший policy gate candidate может быть auto-approved только внутри этого explicit endpoint
- audit metadata для auto-promote пишется в provenance link: `auto_promote_policy`, `auto_promoted`

Пока не реализовано:

- более широкие auto-promotion policies для `Rumor` и `CharacterRelationship`
- background / scheduled auto-promotion

### 14.4 Batch contract

Минимальный batch contract сейчас такой:

- `POST /candidate-deltas/batch/review`
  - payload: `action` + `candidate_ids[]`
- `POST /candidate-deltas/batch/promote`
  - payload: `items[]`, где каждый item содержит `candidate_id` и `mapping`
- `POST /candidate-deltas/batch/auto-promote`
  - payload: `policy` + `items[]`
  - каждый item содержит `candidate_id` и `mapping`
  - текущая допустимая policy: `safe_event_only`

Оба endpoint'а возвращают поэлементный результат, а не all-or-nothing transaction.

Для `safe_event_only` item дополнительно проходит такой gate:

- `candidate_type == scenario_event`
- `target_canonical_type == Event`
- `confidence >= 0.90`
- `len(evidence_ids) >= 2`

## 15. Какие MCP tools нужны

Текущий MCP уже подтверждённо умеет часть обычного CRUD:

- `create_character`
- `update_character`
- `create_event`
- `create_location`
- `update_location`

Но для write-back pipeline пока реализован именно **HTTP/CLI surface**, а не MCP tools.

То есть следующий логичный этап для MCP — завернуть уже существующий ingest/review/promote flow в tools, а не проектировать его с нуля.

Нужны новые tools:

- `ingest_mirofish_result_bundle`
- `list_mirofish_candidates`
- `get_mirofish_candidate`
- `approve_mirofish_candidate`
- `reject_mirofish_candidate`
- `merge_mirofish_candidate`
- `promote_mirofish_candidate`

Также, вероятно, понадобится закрыть обычный CRUD gap для части promote targets:

- `create_faction`
- `update_faction`
- `create_rumor`
- `update_rumor`
- `create_character_relationship`
- `update_character_relationship`

## 16. Какие CLI нужны

Минимальный текущий операционный набор:

- `python scripts/import_mirofish_results.py --input result_bundle.json`
- `python scripts/run_mirofish_writeback_api.py --db lore_system.db --port 8080`
- `python scripts/smoke_mirofish_writeback_workflow.py`

Пока не реализовано как отдельные CLI:

- `list_mirofish_candidates.py`
- `promote_mirofish_candidate.py`
- `promote_mirofish_batch.py`

Опционально позже:

- `python scripts/promote_mirofish_batch.py --world-id <id> --policy safe_event_only`

## 17. Правильный rollout order

### Phase 1 — Evidence Vault

Сделать только:

- ingest result bundle,
- save raw run/result,
- save runtime evidence.

Без canon writes.

Статус: **сделано**.

### Phase 2 — Candidate Extraction

Добавить:

- normalization,
- dedupe,
- candidate storage,
- list/review surface.

Всё ещё без auto-promote.

Статус: **сделано**.

### Phase 3 — Manual Promotion

Разрешить promote только в:

- `Event`
- `CharacterRelationship`
- `Rumor`

Статус: **сделано** через manual promote API + explicit mapping payload.

### Phase 4 — New Entity Promotion

Добавить manual create/merge для:

- `Location`
- `Faction`
- `Character`

Статус: **сделано**.

Реально реализованный slice:

- без новых endpoint'ов
- без изменения SQLite schema
- через existing `promote` / `merge`
- staged-only persistence в `mirofish_canonical_entities`
- explicit mapping payload для каждого create
- targeted tests для promoter/API

### Phase 5 — Policy-driven Auto Promotion

Только после стабилизации:

- selective `Event` promote,
- selective `Relationship` promote,
- safe `Rumor` promote.

Статус: **частично сделано**.

Реально реализован только минимальный slice:

- explicit policy endpoint `batch/auto-promote`
- policy `safe_event_only`
- только `scenario_event -> Event`
- только narrow opt-in gate с audit metadata

Пока не сделано в этой фазе:

- policy-driven auto-promote для `Relationship`
- policy-driven auto-promote для `Rumor`
- cross-run / contradiction-aware policy engine

## 18. MVP recommendation

Если выбирать самый безопасный и полезный MVP, он должен делать ровно это:

1. принять result bundle от `MiroFish`,
2. сохранить его в separate scenario store,
3. построить candidates трёх типов:
   - `scenario_event`
   - `relationship_change`
   - `rumor_candidate`
4. дать человеку review surface,
5. promote only to:
   - `Event`
   - `CharacterRelationship`
   - `Rumor`

Новые `Character` и `Faction` на MVP автоматически не создавать.

Именно этот MVP сейчас и реализован в `loreSystem` для reverse path.

Если смотреть не только на ingestion, но и на **идеальную форму входного lore generation**, то самый удобный сценарий для VMP сейчас такой:

1. начать историю со **слуха**,
2. развернуть её как **трёхактную арку**,
3. в первом акте генерировать в основном `rumor_candidate`,
4. во втором акте генерировать `scenario_event` + более плотный `runtime_evidence`,
5. в третьем акте фиксировать `relationship_change` и при необходимости `new_entity_candidate`,
6. затем уже пропускать это через review/promote/merge слой.

Это хорошо совпадает с уже реализованной safe semantics: система не вынуждена делать hard-canon слишком рано, но при этом narrative progression остаётся структурированной и пригодной для write-back.

## 19. Итоговое правило

`loreSystem` хранит **мир как он признан**.

`MiroFish` возвращает **мир как он может измениться**.

Write-back pipeline нужен именно для того, чтобы между этими двумя состояниями появился управляемый слой:

`observation -> candidate -> decision -> canon`

Без этого канон быстро смешается с гипотезами симуляции.