# Что реально показал разбор кода MiroFish

## 1. Главный вывод

`MiroFish` — это не extraction-team и не универсальный lore-конструктор.

Это **social simulation engine**, который строит и запускает агентов в Twitter/Reddit-подобной среде.

## 2. Какие агенты там реально есть

- runtime-агенты `Twitter`
- runtime-агенты `Reddit`
- `ReportAgent` для анализа результатов

`ReportAgent` не строит канон и не является ядром ingestion pipeline.

## 3. Где рождаются сущности

В `MiroFish` есть несколько уровней сущностей:

1. **Ontology level**
   - `backend/app/services/ontology_generator.py`
   - LLM генерирует `entity_types` и `edge_types`

2. **Model class level**
   - `backend/app/services/graph_builder.py`
   - `set_ontology(...)` динамически создает model classes через `type(...)`

3. **Graph instance level**
   - Zep строит экземпляры сущностей и связей по ontology

4. **Agent profile level**
   - `backend/app/services/oasis_profile_generator.py`
   - graph entity превращается в `OasisAgentProfile`

5. **Runtime agent level**
   - `backend/scripts/run_twitter_simulation.py`
   - `backend/scripts/run_reddit_simulation.py`
   - OASIS создает runtime agent graph

## 4. Реальный пайплайн

`text -> ontology -> graph models -> graph entities -> profiles -> simulation config -> OASIS runtime agents`

Glue-layer:

- `backend/app/services/simulation_manager.py`

Он читает graph entities, генерирует профили, сохраняет `reddit_profiles.json` / `twitter_profiles.csv`, создает `simulation_config.json` и подготавливает запуск.

## 5. Ограничение, критичное для интеграции

`MiroFish` ориентирован на сущности, которые могут:

- говорить
- реагировать
- комментировать
- влиять
- быть представлены как account/actor

Поэтому он плохо совпадает 1:1 с полным каноном `loreSystem`.

## 6. Архитектурное следствие для loreSystem

Нужен не прямой `world -> agents`, а отдельный слой:

`canonical world -> social projection -> MiroFish runtime`

То есть сначала надо выбрать:

- каких персонажей делать агентами
- какие фракции делать organization/official accounts
- какие сущности оставить только контекстом

## 7. Что не надо делать в MVP

- не загружать в `MiroFish` все 200+ типов lore-сущностей
- не считать `ReportAgent` ingestion-механизмом
- не использовать `raw text -> ontology generation` как единственный путь, если уже есть канон от `loreSystem`

## 8. Рекомендуемый путь интеграции

1. `loreSystem` собирает канон
2. adapter строит social projection bundle
3. projection bundle превращается в profiles/config для `MiroFish`
4. запускается OASIS runtime
5. результаты нормализуются и возвращаются в `loreSystem`

## 9. Ключевые файлы для реальной интеграции

- `backend/app/api/graph.py`
- `backend/app/services/ontology_generator.py`
- `backend/app/services/graph_builder.py`
- `backend/app/services/oasis_profile_generator.py`
- `backend/app/services/simulation_manager.py`
- `backend/app/services/simulation_config_generator.py`
- `backend/scripts/run_twitter_simulation.py`
- `backend/scripts/run_reddit_simulation.py`
- `backend/app/services/report_agent.py`

## 10. Где смотреть модели и prompt-layer'ы

Отдельный разбор того,

- какие модели реально вызываются,
- где именно лежат prompt'ы,
- какие prompt-layer'ы надо будет менять при интеграции,

вынесен в `07_MODELS_AND_PROMPTS.md`.

Это важно, потому что `MiroFish` меняется не только на уровне DTO/adapter'ов, но и на уровне:

- ontology prompt
- persona/profile prompt
- simulation behavior prompt
- report prompt
- runtime model routing