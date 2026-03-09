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
     Integration Adapter Layer
            |
            v
       MiroFish Simulation
            |
            v
   Scenario Events / State Deltas
            |
            v
      loreSystem Scenario Store
```

## 4. Минимальный технический вариант

На старте лучше использовать **loose coupling**:

- `loreSystem` экспортирует JSON bundle
- `MiroFish` читает bundle
- `MiroFish` отдает JSON result bundle
- `loreSystem` импортирует только значимые результаты

Это быстрее и безопаснее, чем сразу строить общий runtime.

## 5. Рекомендуемая структура интеграции

Если делать внутри `loreSystem`, то логично выделить:

- `src/application/integration/`
- `src/application/integration/exporters/`
- `src/application/integration/importers/`
- `src/application/integration/dto/`
- `src/application/integration/mappers/`

Если делать как внешний мост, то отдельный пакет:

- `integration_bridge/`
  - `export_world_bundle.py`
  - `import_simulation_results.py`
  - `schemas/`
  - `mappers/`

## 6. Какие данные идут в симуляцию

В MiroFish должны попадать не все данные loreSystem, а только данные, нужные для динамики:

- актеры мира
- их роли и цели
- групповые принадлежности
- социальные связи
- пространственный контекст
- ресурсы и ограничения
- стартовые события
- правила и запреты мира

## 7. Какие данные возвращаются обратно

Возвращать нужно не весь внутренний лог симуляции, а только артефакты высокого уровня:

- `emergent_events`
- `relationship_changes`
- `faction_state_changes`
- `location_state_changes`
- `alternative_timelines`
- `prediction_summary`

## 8. Что хранить отдельно

Нужно строго разделить:

- **canon** — каноническая модель мира
- **scenario_run** — один запуск симуляции
- **scenario_result** — агрегированный результат запуска
- **world_delta** — изменения, которые решено принять обратно в loreSystem

Иначе канон быстро смешается с гипотезами.

## 9. Верный порядок реализации

1. Сначала общий exchange contract
2. Потом exporter из loreSystem
3. Потом importer в MiroFish
4. Потом result bundle из MiroFish
5. Потом importer результатов обратно в loreSystem
6. Только после этого UI и orchestration

## 10. Ключевой архитектурный принцип

`loreSystem` должен отвечать на вопрос **"что существует в мире"**.

`MiroFish` должен отвечать на вопрос **"что, вероятно, произойдет дальше"**.

Это и есть правильная граница между системами.