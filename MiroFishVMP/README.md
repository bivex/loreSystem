# MiroFishVMP

Практический комплект документации по интеграции `loreSystem` и `MiroFish`.

> Папка названа `MiroFishVMP` по вашему запросу. По содержанию это план MVP-интеграции.

## Цель

Собрать связку из двух систем:

- `loreSystem` как **world compiler** — извлекает из текста канон мира, сущности и связи
- `MiroFish` как **future engine** — запускает агентную симуляцию и строит вероятные траектории

Итоговый конвейер:

1. Пользователь загружает текст, отчет, новость или сюжет
2. `loreSystem` извлекает структурированный мир
3. Адаптер переводит мир в simulation bundle
4. `MiroFish` прогоняет сценарии
5. Значимые события и изменения возвращаются обратно в lore-слой

## Что лежит в папке

- `01_ARCHITECTURE.md` — правильная целевая архитектура интеграции
- `02_DATA_CONTRACT.md` — единый контракт данных и правила маппинга
- `06_MIROFISH_REVERSE_ENGINEERING.md` — что реально показал разбор кода `MiroFish`
- `07_MODELS_AND_PROMPTS.md` — какие модели и prompt-layer'ы реально используются в `MiroFish`
- `08_WRITE_BACK_PIPELINE.md` — safe reverse path: staging, review, promote, smoke validation
- `09_MIRO_TO_LORESYSTEM_MAPPING.md` — прикладная матрица маппинга полей и сущностей между `MiroFish` и `loreSystem`
- `03_IMPLEMENTATION_PLAN.md` — пошаговый план внедрения
- `04_CHECKLIST_AND_ACCEPTANCE.md` — чеклист, риски и критерии готовности
- `05_FIRST_DEMO_SCENARIO.md` — первый демонстрационный сценарий, с которого стоит начинать

## Рекомендуемый порядок чтения

1. `01_ARCHITECTURE.md`
2. `02_DATA_CONTRACT.md`
3. `06_MIROFISH_REVERSE_ENGINEERING.md`
4. `07_MODELS_AND_PROMPTS.md`
5. `08_WRITE_BACK_PIPELINE.md`
6. `09_MIRO_TO_LORESYSTEM_MAPPING.md`
7. `03_IMPLEMENTATION_PLAN.md`
8. `05_FIRST_DEMO_SCENARIO.md`
9. `04_CHECKLIST_AND_ACCEPTANCE.md`

## Актуальный статус reverse path

На текущий момент в `loreSystem` уже реализован безопасный reverse write-back MVP:

- импорт `MiroFish result bundle` в отдельный SQLite staging store
- сохранение `scenario_run`, `scenario_result`, `runtime_evidence`, `candidate_deltas`
- stdlib HTTP API `POST/GET` для ingest/review/detail/batch
- single-candidate detail read surface: `GET /api/mirofish/writeback/candidate-deltas/{candidate_id}`
- review actions: `approve` / `reject`
- batch review / batch promotion API поверх single-candidate операций
- minimal explicit auto-promotion policy endpoint:
  - `POST /api/mirofish/writeback/candidate-deltas/batch/auto-promote`
  - текущие policies:
    - `safe_event_only`
    - `safe_rumor_only`
    - `safe_relationship_only`
    - `safe_cross_run_relationship_only`
- manual promotion для 3 типов:
  - `scenario_event -> Event`
  - `rumor_candidate -> Rumor`
  - `relationship_change -> CharacterRelationship`
- manual create/merge для 3 новых staged canonical targets:
  - `new_entity_candidate -> Location`
  - `new_entity_candidate -> Faction`
  - `new_entity_candidate -> Character`
  - create использует existing `POST /candidate-deltas/{id}/promote`
  - merge использует existing `POST /candidate-deltas/{id}/merge`
- safe merge flow для approved candidate в уже существующий staged canonical entity через `merged_into`
- safe canonical persistence в отдельную таблицу `mirofish_canonical_entities`
- явная provenance-связь `run -> canonical entity` через отдельную таблицу `mirofish_entity_run_links`
- нормализованный staging layer для runtime actors/organizations через `mirofish_run_subjects`
- enriched evidence readback с `linked_subjects`, резолвящими `actor_refs` в persisted subject rows
- generic provenance foundation для обычного lore bundle:
  - `src/application/integration/dto/provenance.py`
  - `src/presentation/gui/lore_data.py::metadata`
- full smoke script для end-to-end проверки review/promote workflow
- convenience wrapper `scripts/autorun_mirofish_live_smoke.py` для fresh-db и same-db smoke прогонов
- repeat-run idempotency на одной и той же SQLite БД подтверждена после включения `PRAGMA foreign_keys = ON`
- derived `runtime_evidence` и `candidate_deltas` теперь получают детерминированные fingerprint-based IDs, а не случайные UUID
- same-db rerun для неизменившегося candidate теперь сохраняет стабильный `canonical_id` и не плодит новые `entity_run_links`
- auto-promotion пока намеренно узкий и audit-friendly:
  - только explicit opt-in вызов
  - `safe_event_only` → только `scenario_event -> Event`
  - `safe_rumor_only` → только `rumor_candidate -> Rumor`
  - `safe_relationship_only` → только `relationship_change -> CharacterRelationship`
  - `safe_cross_run_relationship_only` → только `relationship_change -> CharacterRelationship`, но уже с cross-run stability gate
  - базовые gate для всех safe policy: `confidence >= 0.90` и минимум `2 evidence_ids`
  - `safe_rumor_only` дополнительно требует explicit `source_name` и `credibility_score`
  - `safe_relationship_only` дополнительно требует explicit `character_from_id`, `character_to_id`, `relationship_level`, и `abs(relationship_level) >= 30`
  - `safe_cross_run_relationship_only` дополнительно требует хотя бы один supporting run с тем же directed `actor_refs` и той же polarity, плюс отклоняет opposite-polarity staged canonical relationship для той же directed pair
  - auto-path пишет `auto_promote_policy` / `auto_promoted`, а cross-run policy ещё и `cross_run_supporting_run_ids`, `cross_run_distinct_run_count`, `contradiction_check` в provenance metadata
- manual create для `Location` / `Faction` / `Character` остаётся review-only и требует fully explicit mapping payload:
  - `Location` требует как минимум `location_type`
  - `Faction` требует как минимум `faction_type` и `alignment`
  - `Character` требует canonical-grade `backstory`

Важно: это **не** direct write в старый canonical repository layer. Между simulation output и canon по-прежнему остаётся явный review/merge/promote слой.

Если нужен практический field-level reference, он вынесен отдельно в `09_MIRO_TO_LORESYSTEM_MAPPING.md`.

Для narrative/lore generation есть ещё одно практическое правило: **лучше стартовать со слуха** и строить сценарий как **трёхактную структуру**:

- **Act I — Rumor seed**: мир получает спорный или неполный social/narrative signal → `rumor_candidate`
- **Act II — Escalation**: слух провоцирует наблюдаемые действия, столкновения, публичные реакции → `scenario_event`
- **Act III — Resolution**: последствия закрепляются в отношениях, ролях и новых стабильных сущностях → `relationship_change` + при необходимости manual create/merge для `Location` / `Faction` / `Character`

Такой flow хорошо совпадает с философией `loreSystem`: сначала soft claim, потом evidence-backed event, и только потом более жёсткая канонизация.

## Главная идея

Не надо сливать проекты в один монолит.

Правильнее сделать:

- отдельный **канонический слой данных**
- отдельный **слой симуляции**
- тонкий **adapter layer** между ними

Формула интеграции:

`Text -> Structured World -> Social Projection Bundle -> MiroFish/OASIS Runs -> Run Subjects + Runtime Evidence -> Candidate Deltas -> Review/Merge/Promote -> Canonical Entity + Run Links`

## Что показал анализ кода MiroFish

После reverse-engineering стало ясно, что `MiroFish` — это не универсальный world-builder и не extraction-team.

На практике он работает как **social simulation engine**:

- сначала LLM генерирует **ontology** для социальной симуляции
- затем `MiroFish` динамически создает **модельные классы** для Zep graph
- из текста строятся **graph entities**
- graph entities превращаются в **agent profiles**
- OASIS создает из профилей **runtime-агентов** для `Twitter`/`Reddit`-подобной среды
- отдельный `ReportAgent` анализирует уже готовую симуляцию, но не строит канон мира

Из этого следует ключевое правило интеграции:

> в `MiroFish` нужно передавать не весь lore-мир, а только **speakable / actor-capable projection** мира.

## Что показал анализ моделей и prompt'ов

После отдельного разбора model/prompt-layer'ов стало ясно еще одно важное правило:

- у `MiroFish` сейчас почти весь pipeline собран вокруг **одного OpenAI-compatible model slot**
- но семантически это не один и тот же слой
- на практике там есть разные режимы LLM-работы:
  - ontology design
  - persona/profile generation
  - simulation config generation
  - report generation
  - runtime-agent execution inside OASIS/CAMEL

Из этого следует, что в интеграции с `loreSystem` нам почти наверняка придется менять не только data contract, но и:

- разносить модели по слоям
- переписывать ontology/profile/config/report prompt'ы под наш домен
- убирать из prompt'ов лишние assumptions про китайский social-media scenario, если они не соответствуют миру симуляции

Отдельно это описано в `07_MODELS_AND_PROMPTS.md`.

## Коротко о границах ответственности

### Что делает loreSystem

- извлекает сущности из текста
- валидирует схему и связи
- хранит каноническое состояние мира
- ведет версии и экспортирует world bundle

### Что делает MiroFish

- создает social-simulation ontology, профили агентов, среду и динамику
- запускает сценарные прогоны
- считает вероятные исходы
- возвращает emergent events и state deltas

Важно: `MiroFish` хорошо работает с теми сущностями, которые могут быть представлены как:

- говорящие персонажи
- официальные аккаунты организаций
- представители групп
- комментаторы, медиа, свидетели, лидеры мнений

## Что НЕ стоит делать на старте

- не покрывать сразу все 200+ типов сущностей
- не смешивать канон и результаты симуляции в одной таблице/схеме
- не делать tight coupling между репозиториями
- не пытаться сразу предсказывать все домены: политика, финансы, медиа, сюжет и экономику одновременно
- не кормить `MiroFish` сырым lore-прозовым текстом в интегрированном режиме, если у нас уже есть структурированный канон

## Рекомендуемый стартовый scope

Для первого рабочего MVP достаточно:

- персонажи
- фракции
- отношения
- локации
- события
- цели агентов

Но в сам runtime `MiroFish` должны попадать только:

- персонажи, способные говорить и действовать
- организации или их представительские аккаунты
- социальные связи
- стартовые триггеры и правила мира

Если это заработает стабильно, дальше можно расширять на экономику, религию, медиа и сложные системные сущности.