# План рефакторинга: `src/infrastructure/sqlite_repositories.py`

> ## ✅ Статус: ВЫПОЛНЕН
>
> **Результат:**
> - `sqlite_repositories.py`: 28 916 строк → **52 строки** (фасад обратной совместимости).
> - Создан пакет `src/infrastructure/sqlite/` с:
>   - `database.py` (510 строк) — `SQLiteDatabase` (connection manager + schema init).
>   - `base.py` (52 строки) — `SQLiteRepositoryBase` (только shared `db` plumbing + execution helpers; **не** generic-CRUD — см. отклонение ниже).
>   - 7 доменными модулями: narrative (50 классов), quests (26), progression (18), economy (25), world_building (19), society (35), misc (229).
> - **Дедупликация**: оригинал содержал 515 определений классов (включая повторное объявление `SQLiteDatabase` и 110 других дубликатов из branch-merges); фасад экспортирует 403 уникальных имени (402 репозитория + `SQLiteDatabase`).
> - Обратная совместимость: `from src.infrastructure.sqlite_repositories import SQLiteXxxRepository` работает без изменений.
> - **Тесты:** `702 passed / 14 failed` — идентично baseline. 14 падений — предсуществующая несовместимость Python 3.14 (не связаны с рефакторингом).
> - Сокращение: 28 916 → 21 788 строк (−25%); монолит-фасад: 28 916 → 52 строки.
>
> **Отклонения от плана документа** (обоснованы анализом кода):
> 1. **`base.py` без generic-CRUD.** Предложенные в §2/§3 хелперы `find_by_id`/`delete`/`list_by_world` в базовом классе **невозможны без переписывания всех 402 репозиториев**: каждый `save` жёстко кодирует список колонок таблицы (INSERT/UPDATE), каждый `find_by_id` — имя таблицы и т.д. Это потребовало бы ~2000 правок SQL **без тестового покрытия** (тесты используют raw `sqlite3`, не репозитории — см. ниже). Поэтому `base.py` содержит только `_execute`/`_fetchone`/`_fetchall` wrappers; SQL остаётся в каждом репозитории дословно.
> 2. **Last-wins дедупликация** (как в `in_memory`): для каждого из 111 дубликатов имён оставлено последнее определение (то, что Python уже использовал).
> 3. **14 entity-модулей не импортируются на Python 3.14** (та же категория, что 14 baseline-падений). Для репозиториев, ссылающихся на такие entity, импорт entity опущен — SQL duck-typed и не требует типа entity во время выполнения.
>
> **Ключевая находка (риск):** тесты **не импортируют** `sqlite_repositories` напрямую — 32 verification-теста используют raw `sqlite3` и создают свою схему. Репозитории — нетестрированный прод-код, поэтому единственная гарантия корректности — механическое извлечение без правок логики + сохранение всех имён классов + успешная компиляция.

---

## 1. Проблема и цели

Файл `sqlite_repositories.py` является самым большим файлом в проекте (более 28 000 строк кода, ~1.4 МБ). В нем содержатся:
*   Класс `SQLiteDatabase`, отвечающий за инициализацию схем и создание сотен SQL-таблиц.
*   Реализация более чем 100 отдельных классов репозиториев (по 2 на каждую сущность из-за частичного дублирования в процессе слияний).
*   Дублирующийся код и избыточные SQL-запросы, накопившиеся в результате объединения веток.

### Цели рефакторинга:
1.  **Декомпозиция**: Разделить гигантский файл на модули, сгруппированные по доменным областям (согласно DDD).
2.  **Устранение дублирования**: Найти и удалить дублирующиеся объявления классов репозиториев (например, повторные объявления `SQLiteWorldRepository`).
3.  **Обратная совместимость**: Сохранить работоспособность всех импортов во внешних модулях и тестах за счет правильного экспорта в пакете `sqlite/`.

---

## 2. Предлагаемая структура пакета `sqlite/`

Вместо монолита `sqlite_repositories.py` будет создан пакет `src/infrastructure/sqlite/` со следующей структурой:

```text
src/infrastructure/sqlite/
├── __init__.py               # Экспорт всех классов репозиториев и SQLiteDatabase
├── database.py               # Инициализация SQLiteDatabase, создание таблиц и схем
├── base.py                   # Базовый класс репозитория (CRUD-хелперы)
├── narrative.py              # Репозитории домена Narrative (World, Character, Story, Event, Page)
├── quests.py                 # Репозитории доменов Quests & Branching (QuestChain, Choice, PlotBranch)
├── progression.py            # Репозитории домена Progression (Skill, Perk, Attribute, Achievement)
├── economy.py                # Репозитории домена Economy & Items (Item, Material, CraftingRecipe)
├── world_building.py         # Репозитории домена World & Environment (Dungeon, Zone, Texture)
└── society.py                # Репозитории домена Society & Factions (Faction, Court, Miracle)
```

### Распределение репозиториев по файлам

1.  **`database.py`**:
    *   Содержит класс `SQLiteDatabase` и метод `initialize_schema()`, выполняющий создание всех таблиц.
2.  **`base.py`**:
    *   Абстрактные или базовые хелперы для минимизации повторяющегося SQL-кода (например, хелперы для `find_by_id`, `delete`, `list_by_world`).
3.  **`narrative.py`**:
    *   `SQLiteWorldRepository`
    *   `SQLiteCharacterRepository`
    *   `SQLiteStoryRepository`
    *   `SQLiteEventRepository`
    *   `SQLitePageRepository`
4.  **`quests.py`**:
    *   `SQLiteQuestChainRepository`, `SQLiteQuestNodeRepository`, `SQLiteQuestObjectiveRepository`, `SQLiteQuestPrerequisiteRepository`, `SQLiteQuestRewardRepository`
    *   `SQLitePlotBranchRepository`, `SQLiteBranchPointRepository`, `SQLiteChoiceRepository`, `SQLiteConsequenceRepository`
5.  **`progression.py`**:
    *   `SQLiteSkillRepository`, `SQLitePerkRepository`, `SQLiteTraitRepository`, `SQLiteAttributeRepository`
    *   `SQLiteExperienceRepository`, `SQLiteLevelUpRepository`, `SQLiteTalentTreeRepository`, `SQLiteAchievementRepository`
6.  **`economy.py`**:
    *   `SQLiteItemRepository`, `SQLiteInventoryRepository`, `SQLiteMaterialRepository`, `SQLiteCraftingRecipeRepository`, `SQLiteBlueprintRepository`, `SQLiteEnchantmentRepository`
7.  **`world_building.py`**:
    *   `SQLiteLocationRepository`, `SQLiteEnvironmentRepository`, `SQLiteTextureRepository`, `SQLiteModel3DRepository`, `SQLiteMapRepository`, `SQLiteDungeonRepository`, `SQLiteOpenWorldZoneRepository`
8.  **`society.py`**:
    *   `SQLiteFactionRepository`, `SQLiteFactionMembershipRepository`, `SQLiteFactionTerritoryRepository`
    *   `SQLiteMiracleRepository`, `SQLiteCourtRepository`, `SQLiteFestivalRepository`, `SQLiteCataclysmRepository`

---

## 3. Пошаговый план выполнения

1.  **Инициализация пакета**:
    *   Создать директорию `src/infrastructure/sqlite/`.
    *   Создать файл `database.py` и перенести туда класс `SQLiteDatabase`.
    *   Настроить `__init__.py` для экспорта `SQLiteDatabase`.
2.  **Поэтапный перенос**:
    *   Вырезать и переносить репозитории группами (например, сначала `narrative.py`).
    *   При переносе сверять наличие дубликатов (если класс объявлен в файле дважды, оставлять только актуальную чистую версию, сравнивая логику методов).
    *   Импортировать перенесенные классы в `__init__.py`.
3.  **Создание совместимого фасада**:
    *   После переноса всех классов, заменить содержимое оригинального `src/infrastructure/sqlite_repositories.py` на импорты из нового пакета `sqlite`, чтобы сторонние модули (например, GUI-редактор) продолжали импортировать репозитории по старому пути:
        ```python
        from src.infrastructure.sqlite.database import SQLiteDatabase
        from src.infrastructure.sqlite.narrative import SQLiteWorldRepository, SQLiteCharacterRepository
        # и так далее...
        ```
4.  **Проверка тестов**:
    *   Запустить тесты базы данных для проверки работоспособности:
        ```bash
        python -m pytest tests/ -v
        ```
