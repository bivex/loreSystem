# Пошаговый план внедрения

## Фаза 0. Зафиксировать реальную модель MiroFish

Перед кодом нужно принять архитектурный факт:

- `MiroFish` — это social simulation engine
- он работает через цепочку `ontology -> graph -> profile -> runtime`
- он ожидает не весь lore-мир, а набор акторов и их социальный контекст

Итог фазы: команда не пытается интегрировать `loreSystem` как будто `MiroFish` — это универсальный world database.

## Фаза 1. Определить границы MVP

Сначала фиксируем первый сценарий и минимальный scope.

### Что берем в MVP

- персонажи
- фракции
- отношения
- локации
- стартовые события
- цели агентов
- представительские аккаунты фракций или институтов

### Что сознательно откладываем

- полную экономику
- сложную религию и право
- медиа-экосистему
- все 200+ типов сущностей
- real-time orchestration

## Фаза 2. Подготовить экспорт из loreSystem

Нужно реализовать:

1. DTO для `world bundle`
2. mapper из доменных сущностей в exchange schema
3. exporter в JSON
4. валидацию bundle перед передачей

Результат фазы: `loreSystem` умеет стабильно отдавать мир в едином формате.

## Фаза 3. Построить social projection layer

Нужно реализовать:

1. projection rules: кто становится актером, а кто нет
2. преобразование `Faction -> organization/official_account`
3. преобразование `Character -> actor`
4. перенос `relationships`, `event seeds`, `world rules`
5. сохранение `canonical_id -> projection_id`

Результат фазы: из канонического мира получается детерминированный набор social-simulation actors.

## Фаза 4. Подготовить импорт в MiroFish

Нужно реализовать:

1. loader projection bundle
2. преобразование в graph entities / profiles / config
3. инициализацию social graph
4. загрузку memories/goals/rules

Результат фазы: MiroFish умеет запускать симуляцию на данных из `loreSystem`, не переизобретая канон из сырого текста.

### Предпочтительный путь для MVP

Для первой версии предпочтительно подключаться к тем частям `MiroFish`, которые ближе к runtime:

- `OasisProfileGenerator`
- `SimulationConfigGenerator`
- `run_twitter_simulation.py` / `run_reddit_simulation.py`

А native путь `raw text -> OntologyGenerator -> GraphBuilderService` оставить как опциональный режим для standalone-использования.

## Фаза 5. Подготовить формат результатов

Нужно реализовать:

1. `result bundle`
2. нормализацию событий симуляции
3. агрегацию повторяющихся исходов
4. confidence scoring по результатам нескольких прогонов

Результат фазы: симуляция выдает не сырой лог, а структурированный пакет результатов.

## Фаза 6. Импорт результатов обратно в loreSystem

Нужно реализовать:

1. reader `result bundle`
2. классификацию результатов на `events`, `deltas`, `reports`
3. политику принятия изменений
4. сохранение `scenario_run` и `scenario_result`

Результат фазы: результаты симуляции доступны внутри loreSystem и не ломают канон.

### Что уже закрыто в reverse path

В `loreSystem` уже реализован безопасный минимум этой фазы и следующего слоя review/promote:

1. import `result bundle` в отдельный SQLite staging store
2. сохранение `scenario_run`, `scenario_result`, `runtime_evidence`, `candidate_deltas`
3. HTTP review surface для списка candidates и run/evidence readback
4. review actions `approve` / `reject`
5. manual promotion для:
   - `scenario_event -> Event`
   - `rumor_candidate -> Rumor`
   - `relationship_change -> CharacterRelationship`
6. safe canonical persistence в `mirofish_canonical_entities`
7. full smoke script для end-to-end проверки review/promote workflow

То есть reverse path уже не только спроектирован, а доведён до рабочего staging/review/promote MVP.

## Фаза 7. Простой пользовательский поток

Минимальный flow в UI/CLI:

1. выбрать исходный текст или мир
2. нажать `Extract world`
3. выбрать `Simulation mode`
4. задать `what-if` переменные
5. запустить `N runs`
6. получить `prediction report` и `timeline branches`

## Точки интеграции в коде MiroFish

На что ориентироваться при реальной интеграции:

- `backend/app/services/ontology_generator.py` — standalone ontology generation
- `backend/app/services/graph_builder.py` — dynamic model creation для Zep
- `backend/app/services/oasis_profile_generator.py` — entity -> profile
- `backend/app/services/simulation_manager.py` — основной glue-layer
- `backend/app/services/simulation_config_generator.py` — behavior config
- `backend/scripts/run_twitter_simulation.py` — Twitter runtime
- `backend/scripts/run_reddit_simulation.py` — Reddit runtime
- `backend/app/services/report_agent.py` — post-simulation analysis, не ingestion layer

## Распределение работ по направлениям

### Backend / loreSystem

- export DTO
- canonical mapping
- versioning world bundle
- import result bundle
- scenario storage

### Simulation / MiroFish

- projection bundle ingestion
- profile/config generation
- agent instantiation
- run orchestration
- result normalization
- confidence aggregation

### Frontend / UX

- экран выбора мира
- экран настройки сценария
- запуск прогонов
- просмотр итогового отчета
- сравнение веток развития

## Рекомендуемая последовательность по неделям

### Неделя 1

- зафиксировать контракт данных
- сделать exporter из loreSystem
- сделать social projection layer
- сделать importer в MiroFish
- запустить первый end-to-end сценарий

### Неделя 2

- нормализовать результат симуляции
- импортировать результаты обратно
- собрать простой UI/CLI flow
- провести демо на одном сценарии

## Самое важное ограничение

Нельзя считать проект успешным, если он просто гоняет LLM-ответы туда-сюда.

Успех есть только тогда, когда:

- есть четкий canonical world model
- есть воспроизводимый projection/simulation bundle
- есть сравнимые scenario runs
- есть структурированный prediction output

То есть должна появиться инженерная воспроизводимость, а не просто впечатляющий демо-текст.