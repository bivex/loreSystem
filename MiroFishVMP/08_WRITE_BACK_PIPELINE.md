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
- есть CLI:
  - `scripts/import_mirofish_results.py`
  - `scripts/run_mirofish_writeback_api.py`
  - `scripts/smoke_mirofish_writeback_workflow.py`
- full live smoke уже прогнан против `lore_system.db` и подтвердил запись в БД:
  - `scenario_run`
  - `scenario_result`
  - `runtime_evidence`
  - `candidate_deltas`
  - `canonical_entities`

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

### 3.4 Candidate delta

Нормализованный кандидат на изменение мира:

- `scenario_event`
- `relationship_change`
- `faction_state_change`
- `location_state_change`
- `new_entity_candidate`
- `prediction_report`

## 4. Какие сущности реально поддерживать в MVP

Текущий реализованный MVP покрывает 3 группы:

- `scenario_event`
- `relationship_change`
- `rumor_candidate`

Это сознательно уже, чем будущий ingest scope. `Location`, `Faction`, `Character` пока остаются только planned/manual-review domain.

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

## 6. Что promote только после review

### 6.1 Location

Новая location может оказаться:

- alias существующей,
- временным названием,
- под-локацией, которую лучше связать с parent,
- hallucinated place.

Поэтому `Location` — manual review by default.

### 6.2 Faction

Новый runtime group может быть:

- реальной новой организацией,
- временной коалицией,
- риторическим блоком,
- просто social cluster без canonical identity.

Поэтому `Faction` — только через candidate + review.

### 6.3 Character

Это самый жёсткий случай.

В текущем домене `Character.create(...)` требует достаточно полноценный canonical profile, включая backstory. Runtime-персона легко может быть:

- alias существующего героя,
- representative account,
- observer persona,
- simulation-only role.

Поэтому новых `Character` на MVP автоматически не создаём.

## 7. Что нельзя автоматически импортировать в canon

Нельзя без review/policy gate записывать в канон:

- внутренние рассуждения агентов,
- single-run hallucinated details,
- нестабильные локальные колебания,
- краткоживущие social spikes,
- simulation-only representative accounts,
- всё, что не резолвится в canonical IDs.

## 8. Рекомендуемый result bundle от MiroFish

Базовый shape:

```json
{
  "schema_version": "1.1",
  "world_id": "world-uuid",
  "scenario_id": "scenario-uuid",
  "run_id": "run-uuid",
  "generated_at": "2026-03-10T12:00:00Z",
  "prediction_summary": {},
  "runtime_evidence": [],
  "candidate_deltas": []
}
```

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

Дополнительно как future/planned statuses могут появиться:

- `merged`
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
- `>= 0.90` + explicit policy -> future auto-promote for narrow safe cases

На MVP даже `>= 0.80` не должен автоматически писать в canon без review.

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

### 12.5 Faction

Promote, если:

- это не temporary crowd,
- есть устойчивая identity,
- есть leader / mission / group boundary,
- reviewer явно подтвердил создание.

### 12.6 Character

Promote только вручную, если:

- это не alias существующего character,
- есть достаточно материала для canonical backstory,
- нет признаков, что это simulation-only persona.

## 13. Где это должно жить в коде

Так как exporter уже живёт в `src/application/integration/`, reverse path логично держать рядом.

Фактическая текущая структура:

- `src/application/integration/dto/mirofish_result_bundle.py`
- `src/application/integration/dto/runtime_evidence_record.py`
- `src/application/integration/dto/candidate_delta.py`
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

Пока не реализовано:

- `GET /api/mirofish/writeback/candidate-deltas/{candidate_id}`

### 14.3 Review / promotion API

Реально реализовано:

- `POST /api/mirofish/writeback/candidate-deltas/{candidate_id}/approve`
- `POST /api/mirofish/writeback/candidate-deltas/{candidate_id}/reject`
- `POST /api/mirofish/writeback/candidate-deltas/{candidate_id}/promote`

Пока не реализовано:

- `merge`
- batch review / batch promotion

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

Статус: **ещё не сделано**.

### Phase 5 — Policy-driven Auto Promotion

Только после стабилизации:

- selective `Event` promote,
- selective `Relationship` promote,
- safe `Rumor` promote.

Статус: **ещё не делалось**.

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

## 19. Итоговое правило

`loreSystem` хранит **мир как он признан**.

`MiroFish` возвращает **мир как он может измениться**.

Write-back pipeline нужен именно для того, чтобы между этими двумя состояниями появился управляемый слой:

`observation -> candidate -> decision -> canon`

Без этого канон быстро смешается с гипотезами симуляции.