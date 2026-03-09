# Контракт данных между loreSystem и MiroFish

## 1. Зачем нужен единый контракт

Без общего формата интеграция быстро превратится в набор случайных маппингов. Поэтому первым делом нужен один exchange schema.

## 2. Минимальный набор сущностей для MVP

Для первого релиза достаточно 6 групп:

- `characters`
- `factions`
- `locations`
- `relationships`
- `events`
- `goals`

Все остальные сущности подключаются позже.

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

## 4. Обязательные поля у сущностей

Минимальный обязательный набор:

- `id`
- `name`
- `type`

Дополнительно для интеграции стоит ввести:

- `tags`
- `source_refs`
- `confidence`
- `status`

## 5. Маппинг сущностей

### Из loreSystem в MiroFish

- `Character` -> `agent`
- `Faction` -> `group`
- `Location` -> `environment_node`
- `Relationship` -> `social_edge`
- `Quest/Event` -> `objective` или `trigger`
- `Law/Culture/Religion` -> `world_rule`
- `LoreFragment/Memory` -> `agent_memory_seed`

### Из MiroFish обратно в loreSystem

- `agent_action_summary` -> `scenario_event`
- `group_shift` -> `faction_state_change`
- `trust_change` -> `relationship_change`
- `conflict_outcome` -> `world_event`
- `trajectory_summary` -> `prediction_report`

## 6. Правила идентификаторов

- canonical IDs всегда генерирует `loreSystem`
- MiroFish обязан хранить ссылку на исходный canonical ID
- simulation-only сущности получают отдельный `simulation_id`
- нельзя подменять canonical ID временными идентификаторами симуляции

## 7. Правила версии данных

В каждом bundle нужны:

- `schema_version`
- `world_version`
- `scenario_id`
- `run_id`
- `generated_at`

Это позволит сравнивать результаты разных прогонов и не терять совместимость.

## 8. Result bundle от MiroFish

Рекомендуемая структура:

```json
{
  "schema_version": "1.0",
  "world_id": "world-uuid",
  "scenario_id": "scenario-uuid",
  "run_id": "run-uuid",
  "prediction_summary": {},
  "emergent_events": [],
  "state_deltas": [],
  "relationship_changes": [],
  "timeline_branches": []
}
```

## 9. Что нельзя импортировать обратно автоматически

Без ручного подтверждения или отдельной политики нельзя сразу превращать в канон:

- галлюцинированные детали
- внутренние рассуждения агентов
- нестабильные локальные колебания
- низкоуверенные события из одного прогона

В канон должны попадать только:

- подтвержденные сценарные выводы
- агрегированные устойчивые изменения
- явно принятые пользователем дельты

## 10. Золотое правило контракта

`loreSystem` хранит **мир как есть**.

`MiroFish` возвращает **мир как он может развиться**.

Контракт должен фиксировать эту разницу на уровне схемы.