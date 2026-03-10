# Контракт данных между loreSystem и MiroFish

## 1. Зачем нужен единый контракт

Без общего формата интеграция быстро превратится в набор случайных маппингов. Поэтому первым делом нужен один exchange schema.

## 2. Минимальный набор сущностей для MVP

Для первого релиза достаточно 6 канонических групп:

- `characters`
- `factions`
- `locations`
- `relationships`
- `events`
- `goals`

Все остальные сущности подключаются позже.

Но это еще не значит, что все они напрямую попадут в runtime `MiroFish`.

## 3. Канонический bundle на выходе из loreSystem

Рекомендуемая структура:

```json
{
  "schema_version": "1.0",
  "world": {
    "id": "world-uuid",
    "name": "World Name",
    "time_context": "pre-crisis"
  },
  "characters": [],
  "factions": [],
  "locations": [],
  "relationships": [],
  "events": [],
  "rules": [],
  "simulation_goals": []
}
```

Этот bundle — источник истины. Он не обязан совпадать 1:1 с тем, что будет загружено в `MiroFish`.

## 4. Projection bundle для MiroFish

После анализа `MiroFish` рекомендуется промежуточный формат: не просто `world bundle`, а **social projection bundle**.

Рекомендуемая структура:

```json
{
  "schema_version": "1.0",
  "world_id": "world-uuid",
  "world_version": "v1",
  "scenario_id": "scenario-uuid",
  "actors": [],
  "organizations": [],
  "social_edges": [],
  "context_locations": [],
  "event_seeds": [],
  "world_rules": []
}
```

Идея простая: сначала мы проецируем канон в набор **говорящих акторов и их контекст**, а уже потом этот набор попадает в `MiroFish`.

## 5. Обязательные поля у сущностей

Минимальный обязательный набор:

- `id`
- `name`
- `type`

Дополнительно для интеграции стоит ввести:

- `tags`
- `source_refs`
- `confidence`
- `status`

Для projection-слоя дополнительно обязательны:

- `canonical_id`
- `canonical_type`
- `speaker_mode` — `individual | representative | official_account | observer`
- `represented_entity_id` — если агент говорит от имени фракции/организации

## 6. Правила проекции и маппинг сущностей

### Из loreSystem в MiroFish

- `Character` -> `actor`, если это действующий и говорящий субъект
- `Faction` -> `organization` или `official_account`, а не обязательно отдельный персонаж
- `Faction Leader / Spokesperson` -> `representative actor`
- `Location` -> `context_location`, но не агент
- `Relationship` -> `social_edge`
- `Quest/Event` -> `event_seed` или `trigger`
- `Law/Culture/Religion` -> `world_rule`, если влияет на поведение агентов
- `LoreFragment/Memory` -> `memory_seed`, только если привязано к актеру

### Что не должно напрямую становиться агентом

- `Artifact`
- `Dungeon`
- `PureLocation`
- `Calendar/Era`
- `AbstractBelief` без носителя

### Как это соотносится с нативной моделью MiroFish

Внутри `MiroFish` дальше могут появляться:

- `entity_types` / `edge_types` на уровне ontology
- graph entities в Zep
- `OasisAgentProfile`
- runtime agents в OASIS

Но canonical truth по-прежнему остается на стороне `loreSystem`.

### Из MiroFish обратно в loreSystem

- `agent_action_summary` -> `scenario_event`
- `group_shift` -> `faction_state_change`
- `trust_change` -> `relationship_change`
- `conflict_outcome` -> `world_event`
- `trajectory_summary` -> `prediction_report`

## 7. Правила идентификаторов

- canonical IDs всегда генерирует `loreSystem`
- MiroFish обязан хранить ссылку на исходный canonical ID
- simulation-only сущности получают отдельный `simulation_id`
- нельзя подменять canonical ID временными идентификаторами симуляции

Дополнительно:

- каждый runtime agent должен быть трассируем до `canonical_id`
- если создается представительский аккаунт, нужен отдельный `projection_id`, но ссылка на представляемую сущность обязательна

## 8. Правила версии данных

В каждом bundle нужны:

- `schema_version`
- `world_version`
- `scenario_id`
- `run_id`
- `generated_at`

Это позволит сравнивать результаты разных прогонов и не терять совместимость.

## 9. Result bundle от MiroFish

Рекомендуемая структура:

```json
{
  "schema_version": "1.0",
  "world_id": "world-uuid",
  "scenario_id": "scenario-uuid",
  "run_id": "run-uuid",
  "actors": [],
  "organizations": [],
  "prediction_summary": {},
  "emergent_events": [],
  "state_deltas": [],
  "relationship_changes": [],
  "timeline_branches": []
}
```

Для текущего reverse write-back MVP это важно не только для MiroFish-side semantics, но и для staging внутри `loreSystem`:

- `actors` сохраняются как runtime subjects вида `actor:*`
- `organizations` сохраняются как runtime subjects вида `org:*`
- затем evidence может ссылаться на них через `actor_refs`

Внутри staging SQLite это нормализуется в `mirofish_run_subjects`.

### 9.1 Runtime subject shape

Минимально полезные поля одного subject:

- `id`
- `name`
- `canonical_id`
- `canonical_type`
- `speaker_mode`
- `represented_entity_id`

Это покрывает как индивидуальных actors, так и representative / official-account cases.

### 9.2 Evidence linkage

Когда result bundle уже импортирован в `loreSystem`, evidence readback может быть enriched-derived полем:

- `linked_subjects`

Оно не обязано приходить из исходного `MiroFish` payload. Это read model, которая резолвит `actor_refs` в нормализованные строки из `mirofish_run_subjects`.

Желательно также хранить:

- `platform_runs` — twitter/reddit/parallel
- `agent_trace_refs` — связь runtime agent -> projection -> canonical entity

## 10. Что нельзя импортировать обратно автоматически

Без ручного подтверждения или отдельной политики нельзя сразу превращать в канон:

- галлюцинированные детали
- внутренние рассуждения агентов
- нестабильные локальные колебания
- низкоуверенные события из одного прогона

В канон должны попадать только:

- подтвержденные сценарные выводы
- агрегированные устойчивые изменения
- явно принятые пользователем дельты

## 11. Золотое правило контракта

`loreSystem` хранит **мир как есть**.

`MiroFish` возвращает **мир как он может развиться**.

Контракт должен фиксировать эту разницу на уровне схемы.