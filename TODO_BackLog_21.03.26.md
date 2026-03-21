## TODO / Backlog — 21.03.26

### Проверка test tooling

#### Рабочее
- [x] Прямой `pytest` работает: `venv/bin/python -m pytest --version` → `pytest 9.0.2`
- [x] Точечный запуск теста работает: `venv/bin/python -m pytest tests/unit/test_lore_data.py -q` → `9 passed`
- [x] Основной target `make test` работает → `488 passed`, exit code `0`
- [x] Скрипты mutation testing компилируются через `py_compile`:
  - `scripts/mutation_tester.py`
  - `scripts/run_mutation_tests.py`
  - `scripts/.mutmut_config.py`

#### Нерабочее / сломано
- [ ] `make test-unit`
  - текущая команда: `pytest tests/unit/ -v -m unit`
  - результат: `39 deselected / 0 selected`
  - причина: unit-тесты не размечены маркером `@pytest.mark.unit`

- [ ] `make test-integration`
  - результат: `ERROR: file or directory not found: tests/integration/`
  - причина: target есть, но директории сейчас нет

- [ ] `make test-e2e`
  - результат: `ERROR: file or directory not found: tests/e2e/`
  - причина: target есть, но директории сейчас нет

- [ ] `make mutation-test`
  - текущая команда: `python mutation_tester.py`
  - результат: `python: No such file or directory`
  - причины:
    - используется `python`, которого нет в PATH этого окружения
    - неверный путь к скрипту: фактический файл лежит в `scripts/mutation_tester.py`

- [ ] `mutmut`-flow не проверен полноценно в рантайме
  - причина: `mutmut` не установлен (`mutmut_installed = False`)

#### Доп. замечание
- [ ] В make-запусках виден warning: `pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)`
  - это не ломает тесты
  - но конфигурацию pytest стоит унифицировать, чтобы не было путаницы

### Следующие действия
- [ ] Починить `Makefile` для `test-unit`
- [ ] Либо убрать `test-integration` / `test-e2e`, либо создать соответствующие директории и тесты
- [ ] Починить `mutation-test` target: интерпретатор + путь к скрипту
- [ ] Обновить документацию mutation testing под фактическую структуру проекта
- [ ] При необходимости установить `mutmut` отдельным разрешением

### CAMEL.Bridge — актуальный хвост на 21.03.26

#### Подтверждено как уже закрыто
- [x] `P0 core systems tranche` закрыт по `CAMEL.Bridge/README.md` и `CAMEL.Bridge/ROADMAP.md`
- [x] starter encounter/world + live-ops slice закрыт: `Dungeon`, `Raid`, `WorldEvent`, `Arena`, `Instance`, `OpenWorldZone`, `SeasonalEvent`, `Invasion`, `War`
- [x] legendary / relic reward loop закрыт: `LegendaryWeapon`, `MythicalArmor`, `DivineItem`, `CursedItem`, `ArtifactSet`, `RelicCollection`
- [x] memory v1 live base закрыт: `SQLite + Qdrant`, widened recall coverage, live smoke, shaping/resource cleanup
- [x] continuation subset по `Storyline` / `Inventory` уже частично стабилизирован и проходит точечные тесты:
  - `pytest -q tests/test_camel_bridge_rumor_pipeline.py -k 'continuation or storyline or inventory or world_event'`
  - результат: `4 passed`
- [x] локального незакоммиченного WIP в `CAMEL.Bridge`-файлах сейчас нет

#### Открыто / нужно доделать
- [ ] `WorldEvent`: добавить canonical merge path для repeated-run continuation
  - сейчас `world_events` сохраняются напрямую, без merge-ветки
- [ ] `Storyline`: довести continuation merge до noise-free поведения
  - текущий merge уже есть, но документы всё ещё фиксируют шум на повторных прогонах
- [ ] `Inventory`: довести merge-эвристику до полностью стабильного second-run поведения
  - базовый merge уже есть, но roadmap всё ещё держит это как незакрытый хвост
- [ ] Уменьшить side-content duplication в branching / flavor slices на втором прогоне
- [ ] Явно разделить `canonical update` и `genuinely new arc`, чтобы рост мира на втором прогоне был намеренным, а не opportunistic
- [ ] Добавить отдельный two-run live regression harness
  - должен снимать counts + canonical names до/после второго прогона
  - должен отдельно отслеживать `storylines`, `world_events`, `inventories`

#### Текущее тестовое состояние CAMEL.Bridge
- [ ] Полный bridge-пакет пока не зелёный:
  - команда: `pytest -q tests/test_camel_bridge_memory.py tests/test_camel_bridge_rumor_pipeline.py`
  - результат: `93 passed / 3 failed`
- [ ] Починить prompt-scope regression после перехода на batch narrative flow
  - падает `test_narrative_prompt_scope_excludes_systems_when_system_slice_disabled`
- [ ] Привести language instruction block к ожидаемому wording для auto-detected Russian prompts
  - падает `test_prompt_language_block_auto_detects_russian_from_cyrillic_theme`
- [ ] Привести language instruction block к ожидаемому wording для explicit English override
  - падает `test_prompt_language_block_respects_explicit_output_language_override`

#### Рекомендуемый порядок добивания
- [ ] Сначала закрыть 3 красных prompt-layer теста
- [ ] Затем сделать `WorldEvent` canonical merge path
- [ ] Потом прогнать и зафиксировать two-run live regression harness
- [ ] После этого обновить `CAMEL.Bridge/ROADMAP.md` и `CAMEL.Bridge/docs/COLD.md` под фактический статус continuation
