# Чеклист и критерии готовности

## 1. Чеклист архитектуры

- [ ] `loreSystem` и `MiroFish` не слиты в один неразделимый модуль
- [ ] существует отдельный exchange contract
- [ ] существует отдельный social projection layer
- [ ] canon хранится отдельно от simulation outputs
- [ ] у world bundle есть versioning
- [ ] у result bundle есть `scenario_id` и `run_id`
- [ ] для MVP не используется путь `raw text -> MiroFish ontology` как единственный источник истины

## 2. Чеклист данных

- [ ] у всех сущностей есть стабильные canonical IDs
- [ ] описано, какие сущности становятся агентами, а какие остаются контекстом
- [ ] маппинг `Character -> actor` описан явно
- [ ] маппинг `Faction -> organization/official_account` описан явно
- [ ] связи и локации передаются в симуляцию
- [ ] правила мира передаются отдельно, а не теряются в тексте
- [ ] каждый runtime agent трассируется до `canonical_id`

## 3. Чеклист симуляции

- [ ] MiroFish может принять bundle без ручной правки JSON
- [ ] один и тот же bundle можно прогнать несколько раз
- [ ] из bundle можно получить `reddit_profiles.json` и/или `twitter_profiles.csv`
- [ ] из bundle можно получить `simulation_config.json`
- [ ] результаты собираются в нормализованный result bundle
- [ ] есть разделение между сырым логом и агрегированным выводом
- [ ] итог содержит confidence / frequency / summary
- [ ] `ReportAgent` используется как анализатор результатов, а не как источник канона

## 4. Чеклист обратной загрузки

- [ ] результат можно импортировать в loreSystem
- [ ] scenario runs сохраняются отдельно от канона
- [ ] world deltas требуют явного принятия
- [ ] timeline branches не перезаписывают основной мир автоматически

### Что уже фактически закрыто в текущем write-back MVP

- [x] `MiroFish result bundle` импортируется в `loreSystem`
- [x] `scenario_run`, `scenario_result`, `runtime_evidence`, `candidate_deltas` сохраняются отдельно от канона
- [x] review требует явного действия через `approve` / `reject`
- [x] promote требует отдельного explicit mapping payload
- [x] canonical snapshot пишется в отдельную safe table `mirofish_canonical_entities`, а не напрямую в legacy canonical repositories
- [x] после promote создаётся явная provenance-связь `run -> canonical entity` в `mirofish_entity_run_links`
- [x] есть single-candidate detail read surface: `GET /api/mirofish/writeback/candidate-deltas/{candidate_id}`
- [x] approved candidate можно safe-merge'ить в уже существующий staged canonical entity без создания нового canonical snapshot
- [x] есть batch review / batch promotion surface поверх existing single-candidate операций
- [x] у обычного lore bundle появился top-level provenance layer через `LoreData.metadata`
- [x] actors / organizations из result bundle нормализуются в `mirofish_run_subjects`
- [x] runtime evidence readback резолвит `actor_refs` в `linked_subjects`
- [x] live smoke подтверждает запись в SQLite БД
- [x] повторный прогон того же smoke в ту же SQLite БД не плодит stale `canonical_entities` / `entity_run_links`
- [x] неизменившийся candidate при same-db rerun сохраняет тот же `candidate_id` и тот же `canonical_id`
- [x] есть прикладная mapping matrix: `09_MIRO_TO_LORESYSTEM_MAPPING.md`
- [x] есть explicit narrow auto-promotion layer для safe cases: `batch/auto-promote` + `safe_event_only` / `safe_cross_run_event_only` / `safe_rumor_only` / `safe_relationship_only` / `safe_cross_run_relationship_only`
- [x] у `batch/auto-promote` есть `dry_run: true` explain/preview режим без side effects на candidate status / canonical rows / run links
- [x] есть manual create/merge flow для `Location`, `Faction`, `Character` через existing `promote` / `merge` endpoints и staged canonical persistence

### Что ещё остаётся вне текущего MVP

- [ ] более широкий contradiction-aware / cross-run-aware auto-promotion policy engine вне текущих event/relationship-only safe slices
- [ ] background / scheduled auto-promotion

## 5. Definition of Done для первого MVP

MVP считается готовым, если выполняются все условия:

1. Из текста получается world bundle
2. Из world bundle строится social projection bundle
3. Projection bundle без ручной правки превращается в профили/конфиг для MiroFish
4. MiroFish делает минимум 10 прогонов
5. На выходе есть prediction summary и список событий
6. Результаты импортируются обратно в loreSystem
7. Пользователь может сравнить хотя бы 2 ветки исхода

## 6. Частые ошибки, которых нужно избежать

### Ошибка 1. Сразу тащить все сущности

Правильно: начать с узкого домена.

### Ошибка 2. Смешать канон и гипотезы

Правильно: хранить канон отдельно, симуляции отдельно.

### Ошибка 3. Делать только красивый отчет

Правильно: сначала обеспечить воспроизводимый обмен данными.

### Ошибка 4. Зашивать маппинг по месту

Правильно: вынести mapping rules в отдельный слой.

### Ошибка 5. Делать слишком умную первую версию

Правильно: сначала один хороший сценарий, потом расширение.

### Ошибка 6. Считать, что любой lore-object должен стать агентом

Правильно: сначала строить actor projection и выбирать только speakable entities.

### Ошибка 7. Считать, что `ReportAgent` = core simulation

Правильно: `ReportAgent` нужен после прогона, а не вместо ingestion/runtime pipeline.

## 7. Критерии качества результата

Хорошая интеграция должна быть:

- **воспроизводимой** — одинаковый формат, понятные версии
- **расширяемой** — можно добавить новые сущности без слома ядра
- **объяснимой** — видно, откуда взялся прогноз
- **трассируемой** — видно, из какой канонической сущности появился агент
- **аудируемой** — видно, из какого `run_id` и `candidate_id` появился promoted или merged canonical linkage
- **наблюдаемой** — видно, какие key actors / organizations реально участвовали в run и к каким evidence они привязаны
- **идемпотентной на уровне staging-store** — повторный импорт того же run в ту же SQLite БД не оставляет stale canonical/run-link rows
- **стабильной по identity для неизменившегося результата** — rerun не меняет `candidate_id` / `canonical_id`, если candidate content не изменился
- **безопасной для канона** — симуляция не портит базовый мир
- **полезной для пользователя** — дает не лог, а решение и сравнение сценариев

## 8. Финальный тест на здравость

Если можно ответить "да" на все три вопроса, направление верное:

1. Можно ли из текста получить структурированный мир?
2. Можно ли по этому миру прогнать несколько правдоподобных будущих траекторий?
3. Можно ли вернуть результаты обратно, не разрушив канон?

Если хотя бы один ответ "нет", нужно чинить архитектуру, а не наращивать фичи.

На текущем reverse write-back MVP на вопрос №3 уже можно ответить: **да, через staging + review + merge/promote, без direct canon write, с явным provenance/run-link следом, с нормализованным subject/evidence слоем и с подтверждённой repeat-run идемпотентностью на same DB**.