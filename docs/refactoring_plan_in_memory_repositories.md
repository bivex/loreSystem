# План рефакторинга: `src/infrastructure/in_memory_repositories.py`

> ## ✅ Статус: ВЫПОЛНЕН
>
> **Коммит:** `133bb9f` — «Decompose in_memory_repositories.py (16,731 LOC) with generic CRUD base class»
>
> **Результат:**
> - `in_memory_repositories.py`: 16 731 строка → **47 строк** (фасад обратной совместимости).
> - Создан пакет `src/infrastructure/in_memory/` с обобщённым базовым классом `InMemoryRepository[T]` / `InMemoryWorldEntityRepository[T]` (`base.py`, 151 строка) и 7 доменными модулями (narrative, quests, progression, economy, world_building, society, misc).
> - **368 из 394** уникальных репозиториев (94 %) унаследовали CRUD от generic-класса; каждый сократился с ~20 строк до однострочного подкласса.
> - **26 репозиториев** с интерфейсами (`IWorldRepository` и т. д.) или доп. методами сохранены дословно.
> - Обратная совместимость: `from src.infrastructure.in_memory_repositories import InMemoryXxxRepository` работает без изменений.
> - **Тесты:** `702 passed / 14 failed` — идентично baseline. 14 падений — предсуществующая несовместимость Python 3.14 (не связаны с рефакторингом). Все 15 репозитарных тестов зелёные.
> - Сокращение объёма кода: 16 731 → 5 344 строк (−68 %).
>
> **Отклонения от плана документа** (обоснованы анализом кода):
> 1. **Generic-класс точнее, чем в §3.** Предложенная в документе реализация (ключ `str(entity.id.value)`, без проверки `DuplicateEntity`, без индексов) нарушила бы поведение 2 тестируемых репозиториев (World, Character). Реализованный generic точно повторяет композитный ключ `(tenant_id, entity_id)`, автоинкремент `EntityId` через `object.__setattr__`, индекс `_by_world` и пагинацию `list_by_world`.
> 2. **Дедупликация.** В монолите было 604 определения классов, но 210 — дубликаты (артефакты скриптов-генераторов; Python last-def-wins уже затенял их). Фасад экспортирует 394 уникальных имени.
> 3. **Any-fallback для сломанных entity.** 14 доменных entity-модулей не импортируются на Python 3.14 (та же категория багов, что 14 baseline-падений). Для репозиториев с такими entity generic-параметр использует `Any` (CRUD работает через duck-typing).
>
> Подробности — в сообщении коммита `133bb9f`.

---

## 1. Проблема и цели

Файл `in_memory_repositories.py` содержит более 16 000 строк кода. Он содержит:
*   Реализацию InMemory-репозиториев для всех доменных сущностей (более 100 классов репозиториев).
*   Большое количество повторяющегося шаблонного кода (каждый репозиторий хранит словари в оперативной памяти и выполняет схожую логику фильтрации).

### Цели рефакторинга:
1.  **Декомпозиция**: Разбить файл на логические модули по аналогии со структурой SQLite-репозиториев.
2.  **Шаблонизация (Generics)**: Создать базовый обобщенный класс `InMemoryRepository[T]`, содержащий CRUD-операции по умолчанию, чтобы избавиться от 80% дублирующегося кода.
3.  **Обратная совместимость**: Сохранить работоспособность всех импортов через фасад пакета `in_memory/`.

---

## 2. Предлагаемая структура пакета `in_memory/`

Вместо монолита `in_memory_repositories.py` будет создан пакет `src/infrastructure/in_memory/` со следующей структурой:

```text
src/infrastructure/in_memory/
├── __init__.py               # Экспорт всех InMemory репозиториев
├── base.py                   # Базовый обобщенный класс InMemoryRepository[T]
├── narrative.py              # InMemory репозитории для Narrative (World, Character, Story, Event)
├── quests.py                 # InMemory репозитории для Quests & Branching (QuestChain, Choice)
├── progression.py            # InMemory репозитории для Progression (Skill, Perk, Attribute)
├── economy.py                # InMemory репозитории для Economy & Items (Item, Material)
├── world_building.py         # InMemory репозитории для World & Environment (Dungeon, Zone)
└── society.py                # InMemory репозитории для Society & Factions (Faction, Court, Miracle)
```

---

## 3. Внедрение базового обобщенного репозитория (`base.py`)

Поскольку все InMemory-репозитории хранят сущности в словаре `{entity_id: entity}`, можно вынести эту логику в базовый класс:

```python
from typing import Generic, TypeVar, Dict, List, Optional
from src.domain.value_objects.common import EntityId, TenantId

T = TypeVar('T')

class InMemoryRepository(Generic[T]):
    def __init__(self):
        self._storage: Dict[str, T] = {}
        self._next_id = 1

    def save(self, entity: T) -> T:
        if not hasattr(entity, 'id') or entity.id is None:
            entity_id = EntityId(self._next_id)
            object.__setattr__(entity, 'id', entity_id)
            self._next_id += 1
        
        self._storage[str(entity.id.value)] = entity
        return entity

    def find_by_id(self, tenant_id: TenantId, entity_id: EntityId) -> Optional[T]:
        entity = self._storage.get(str(entity_id.value))
        if entity and hasattr(entity, 'tenant_id') and entity.tenant_id == tenant_id:
            return entity
        return None

    def delete(self, tenant_id: TenantId, entity_id: EntityId) -> bool:
        key = str(entity_id.value)
        if key in self._storage:
            entity = self._storage[key]
            if hasattr(entity, 'tenant_id') and entity.tenant_id == tenant_id:
                del self._storage[key]
                return True
        return False
```

Благодаря наследованию от `InMemoryRepository[T]`, код каждого конкретного репозитория сократится с ~150 строк до 5-10 строк (будут описываться только специфичные методы поиска вроде `list_by_world` или `find_by_name`).

---

## 4. Пошаговый план выполнения

1.  **Создание пакета**:
    *   Создать директорию `src/infrastructure/in_memory/`.
    *   Создать `base.py` с обобщенным решением `InMemoryRepository[T]`.
2.  **Поэтапный перенос и сокращение кода**:
    *   Создать модули `narrative.py`, `quests.py`, `progression.py` и т.д.
    *   Переносить репозитории, переводя их на наследование от базового класса и удаляя дублирующийся CRUD-код.
3.  **Сохранение обратной совместимости**:
    *   Настроить `src/infrastructure/in_memory/__init__.py` для реэкспорта всех репозиториев.
    *   В оригинальном `src/infrastructure/in_memory_repositories.py` сделать импорт всех классов из нового пакета `in_memory/` для поддержки совместимости.
4.  **Тестирование**:
    *   Запустить тесты, чтобы убедиться в сохранении корректности работы InMemory-хранилища:
        ```bash
        python -m pytest tests/ -v
        ```
