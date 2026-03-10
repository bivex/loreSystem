## TODO / Backlog — 9.03.26

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