# Архитектура интеграции loreSystem + MiroFish

## 1. Принцип

Интеграция должна строиться не как merge двух кодовых баз, а как связка из трех слоев:

1. **Canonical World Layer** — `loreSystem`
2. **Simulation Runtime Layer** — `MiroFish`
3. **Adapter / Exchange Layer** — отдельный мост между ними

## 2. Правильное разделение ответственности

### loreSystem = Canonical World Layer

Хранит и валидирует:

- персонажей
- фракции
- локации
- квесты
- ресурсы
- исторические события
- социальные/политические/религиозные правила
- отношения между сущностями

Это источник истины для мира.

### MiroFish = Simulation Runtime Layer

Использует канон как вход и отвечает за:

- инстанцирование агентов
- настройку среды
- поведенческую логику
- память агентов
- социальную динамику
- сценарные прогоны
- агрегированный prediction report

Это не источник истины, а машина сценарного прогноза.

После анализа кода `MiroFish` это уточняется так:

- он создает **social-simulation ontology**, а не полный world ontology
- его сущности — это прежде всего **те, кто может говорить/влиять/реагировать**
- итоговые runtime-агенты создаются не напрямую из текста, а через цепочку `ontology -> graph -> profile -> OASIS runtime`
- `ReportAgent` занимается анализом результатов, а не построением мира

### Adapter Layer = Переводчик между мирами

Нужны два независимых направления:

- **Lore -> MiroFish exporter**
- **MiroFish -> Lore importer**

Adapter layer должен жить отдельно от доменных моделей обеих систем.

## 3. Целевая схема взаимодействия

```text
Source Text / Reports / Stories
            |
            v
      loreSystem Extraction
            |
            v
     Canonical World Bundle
            |
            v
      Social Projection Layer
            |
            v
   MiroFish Graph/Profile Prep
            |
            v
        OASIS Simulation
            |
            v
   Scenario Events / State Deltas
            |
            v
      loreSystem Scenario Store
```

## 4. Что реально происходит внутри MiroFish

Внутренний пайплайн `MiroFish` выглядит так:

1. `OntologyGenerator` создает `entity_types` и `edge_types`
2. `GraphBuilderService.set_ontology(...)` динамически создает model classes и регистрирует их в Zep
3. Zep строит экземпляры сущностей и связей по тексту
4. `OasisProfileGenerator` превращает graph entities в `OasisAgentProfile`
5. `SimulationConfigGenerator` генерирует агентную активность и event config
6. `run_twitter_simulation.py` / `run_reddit_simulation.py` создают OASIS runtime agent graph
7. `ReportAgent` и `zep_tools` анализируют результаты

Следствие: интеграция с `loreSystem` должна подавать в `MiroFish` не весь мир, а **проекцию мира в социально-активных акторов**.

## 5. Минимальный технический вариант

На старте лучше использовать **loose coupling**:

- `loreSystem` экспортирует JSON bundle
- adapter строит из него **social projection bundle**
- `MiroFish` читает projection bundle
- `MiroFish` отдает JSON result bundle
- `loreSystem` импортирует только значимые результаты

Это быстрее и безопаснее, чем сразу строить общий runtime.

## 6. Рекомендуемая стратегия интеграции

Для интегрированного режима рекомендуется такой приоритет:

1. `loreSystem` строит канон мира
2. adapter строит **speaker-capable projection**
3. MiroFish получает уже структурированных акторов, связи и события
4. MiroFish генерирует профили, конфиг и runtime-агентов

На MVP не стоит делать ставку на native путь `MiroFish`, где ontology заново выводится из сырого текста. Этот путь хорош для standalone-режима, но в связке с `loreSystem` создает лишнюю недетерминированность.

## 7. Рекомендуемая структура интеграции

Если делать внутри `loreSystem`, то логично выделить:

- `src/application/integration/`
- `src/application/integration/exporters/`
- `src/application/integration/importers/`
- `src/application/integration/dto/`
- `src/application/integration/mappers/`

Если делать как внешний мост, то отдельный пакет:

- `integration_bridge/`
  - `export_world_bundle.py`
  - `build_social_projection.py`
  - `import_simulation_results.py`
  - `schemas/`
  - `mappers/`

## 8. Какие данные идут в симуляцию

В MiroFish должны попадать не все данные loreSystem, а только данные, нужные для динамики и представимые как субъекты или их контекст:

- актеры мира, способные говорить или действовать
- представительские аккаунты организаций/фракций
- их роли, цели и stance seeds
- групповые принадлежности
- социальные связи
- пространственный контекст
- стартовые события
- правила и запреты мира

Не должны напрямую становиться агентами:

- артефакты
- чистые локации
- абстрактные законы без носителя
- lore fragments без связанного актора

## 9. Какие данные возвращаются обратно

Возвращать нужно не весь внутренний лог симуляции, а только артефакты высокого уровня:

- `emergent_events`
- `relationship_changes`
- `faction_state_changes`
- `location_state_changes`
- `alternative_timelines`
- `prediction_summary`

## 10. Что хранить отдельно

Нужно строго разделить:

- **canon** — каноническая модель мира
- **scenario_run** — один запуск симуляции
- **scenario_result** — агрегированный результат запуска
- **world_delta** — изменения, которые решено принять обратно в loreSystem

Иначе канон быстро смешается с гипотезами.

## 11. Верный порядок реализации

1. Сначала общий exchange contract
2. Потом exporter из loreSystem
3. Потом social projection layer
4. Потом importer/adapter в MiroFish
5. Потом result bundle из MiroFish
6. Потом importer результатов обратно в loreSystem
7. Только после этого UI и orchestration

## 12. Ключевой архитектурный принцип

`loreSystem` должен отвечать на вопрос **"что существует в мире"**.

`MiroFish` должен отвечать на вопрос **"что, вероятно, произойдет дальше"**.

Это и есть правильная граница между системами.