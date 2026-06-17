# План рефакторинга: `src/infrastructure/in_memory_repositories.py`

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
