# План рефакторинга: `src/application/integration/camel_bridge/rumor_agents.py`

## 1. Проблема и цели

Файл `rumor_agents.py` является одним из самых больших в проекте (более 16 000 строк кода, ~700 КБ). Он объединяет в себе слишком много разнородных обязанностей:
*   Декларация моделей данных (более 50 классов-черновиков `Draft`).
*   Формирование системных и пользовательских промптов для ИИ.
*   Парсинг, очистка и декодирование JSON-ответов от LLM.
*   Валидация, приведение типов и «стабилизация» идентификаторов/связей.
*   Резервные копии и локализованная генерация заглушек (Fallbacks).
*   Логика сохранения (персистенции) более 150 доменных сущностей в 20+ репозиториев.
*   Основная оркестрация пайплайна (`RumorBridgeService`).

### Цели рефакторинга:
1.  **Повышение поддерживаемости**: Упростить навигацию по коду генерации.
2.  **Изоляция ответственности**: Выделить парсеры, промпты и персистенцию в отдельные чистые модули.
3.  **Сохранение обратной совместимости**: Внешний API класса `RumorBridgeService` не должен измениться, чтобы не сломать тесты и интеграцию.

---

## 2. Предлагаемая структура модулей

Вместо одного монолита в директории `src/application/integration/camel_bridge/` будет создана модульная структура:

```text
src/application/integration/camel_bridge/
├── __init__.py               # Экспорт RumorBridgeService
├── service.py                # (Новый) Основной оркестратор RumorBridgeService
├── rumor_agents.py           # Совместимый фасад (просто импортирует и экспортирует RumorBridgeService)
├── drafts/                   # Пакет моделей данных (Drafts)
│   ├── __init__.py
│   ├── narrative.py          # Сюжетные сущности (CampaignDraft, StoryDraft, QuestDraft)
│   └── systems.py            # Системные сущности (ItemDraft, SkillDraft, DungeonDraft)
├── prompts.py                # Сборка промптов и контекстов для ИИ
├── parsers.py                # Парсинг сырых ответов от LLM и регулярок
├── stabilizer.py             # Логика валидации и привязки ID (UUID / Integer)
├── fallbacks.py              # Генерация резервных структур при сбоях ИИ
└── persistence.py            # Движки сохранения (CanonicalPersistEngine) и запись в БД
```

### Детализация модулей

### 1. Пакет `drafts/`
Сюда переносится вся сотня классов-наследников `dataclasses` или `Pydantic` (если используются):
*   `drafts/narrative.py`: `RumorDraft`, `EventDraft`, `CharacterRelationshipDraft`, `CampaignDraft`, `StoryDraft`, `StorylineDraft`, `QuestDraft`, `QuestNodeDraft`, `ChoiceDraft` и др.
*   `drafts/systems.py`: `ItemDraft`, `MaterialDraft`, `RecipeIngredientDraft`, `CraftingRecipeDraft`, `BlueprintDraft`, `SkillDraft`, `PerkDraft`, `TraitDraft`, `DungeonDraft`, `RaidDraft` и др.

### 2. Модуль `prompts.py`
Отвечает исключительно за генерацию текста промптов для отправки в LLM:
*   `_build_rumor_prompt()`
*   `_build_event_prompt()`
*   `_build_relationship_prompt()`
*   `_build_narrative_prompt()`
*   `_build_systems_batch_prompt()`
*   `_build_narrative_batch_prompt()`
*   Вспомогательные методы форматирования объектов в списки.

### 3. Модуль `parsers.py`
Содержит регулярные выражения и функции для разбора текстовых блоков и JSON-ответов:
*   `_parse_rumor_drafts(raw)`
*   `_parse_event_drafts(raw)`
*   `_parse_relationship_drafts(raw)`
*   `_parse_narrative_structure(raw)`
*   `_parse_items(raw, key)`
*   Обработка JSONDecodeError и очистка от Markdown-тегов (```json ... ```).

### 4. Модуль `stabilizer.py`
Логика валидации, удаления дубликатов и проверки ссылочной целостности:
*   `_stabilize_narrative_structure_draft()`
*   `_merge_partial_narrative_fields()`
*   `_merge_partial_draft_fields()`
*   Связывание квестовых пререквизитов и валидация персонажей.

### 5. Модуль `fallbacks.py`
Логика создания резервных объектов при тайм-аутах или сбоях ИИ:
*   `_fallback_rumor_draft()`
*   `_fallback_event_drafts()`
*   `_fallback_relationship_drafts()`
*   `_fallback_narrative_structure_draft()`
*   Интеграция с `fallback_i18n.py`.

### 6. Модуль `persistence.py`
Самый массивный функциональный блок. Отвечает за транзакционное сохранение сгенерированных графов лора в БД:
*   Методы `_persist_narrative_structure()` и `_persist_systems_slice()`.
*   Все методы сохранения отдельных коллекций (`_persist_campaign()`, `_persist_stories()`, `_persist_quests()`, `_persist_items()`, `_persist_skills()`, `_persist_dungeons()`).
*   `_build_canonical_persist_registry()` и декларация `CanonicalPersistEngine`.

### 7. Модуль `service.py` (RumorBridgeService)
Точка входа. Сохраняет оригинальный конструктор `RumorBridgeService.__init__` и публичные методы:
*   `generate_story_chain()`
*   `generate_narrative_structure()`
*   `generate_and_persist()`
Использует модули `prompts`, `parsers`, `stabilizer`, `fallbacks` и `persistence` для выполнения шагов.

---

## 3. План шагов рефакторинга

Рефакторинг должен выполняться итеративно, с контролем компиляции и тестов на каждом шаге:

1.  **Шаг 1: Подготовка пакета `drafts/`**
    *   Создать файлы `drafts/narrative.py` и `drafts/systems.py`.
    *   Перенести декларации классов.
    *   Импортировать их обратно в `rumor_agents.py` через `from .drafts.narrative import *`.
    *   Проверить компиляцию и запустить юнит-тесты.
2.  **Шаг 2: Выделение `prompts.py` и `parsers.py`**
    *   Перенести функции форматирования и отправки промптов.
    *   Перенести парсеры регулярных выражений.
    *   Проверить импорты и зависимости.
3.  **Шаг 3: Выделение `fallbacks.py` и `stabilizer.py`**
    *   Изолировать логику заглушек и валидации ссылок.
4.  **Шаг 4: Выделение `persistence.py`**
    *   Перенести гигантские блоки сохранения. Так как сохранение требует доступа ко всем репозиториям, `persistence.py` будет принимать контекст сохранения или ссылки на репозитории от `RumorBridgeService`.
5.  **Шаг 5: Перенос основного класса в `service.py`**
    *   Переместить облегченный класс `RumorBridgeService`.
    *   Сделать `rumor_agents.py` фасадом для сохранения обратной совместимости импортов в тестах и внешнем коде.

---

## 4. План верификации (Verification Plan)

Каждое изменение должно верифицироваться двумя способами:

### Автоматические тесты
Для контроля регрессии используются существующие тесты пайплайна:
```bash
# Тесты семантической памяти и промптов
python -m pytest tests/test_camel_bridge_memory.py -o addopts=""

# Полный сквозной тест генерации квестов и систем
python -m pytest tests/test_camel_bridge_rumor_pipeline.py -o addopts=""
```

*Примечание: Поскольку тесты обращаются к мокам LLM, структура промптов и возвращаемый JSON должны оставаться на 100% идентичными исходным.*

### Проверка компиляции
Быстрая проверка корректности синтаксиса после каждого выделения модуля:
```bash
python -m py_compile src/application/integration/camel_bridge/*.py
```
