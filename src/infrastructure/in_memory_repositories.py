"""In-memory repository implementations.

This module is a **backward-compatibility facade**. The monolithic
~16,700-line implementation (604 repository class definitions, of which
~210 were duplicate names) has been split across the
:mod:`src.infrastructure.in_memory` package:

* :mod:`.base`           - generic ``InMemoryRepository[T]`` and
  ``InMemoryWorldEntityRepository[T]`` capturing the shared CRUD shape.
* ``narrative.py``       - world/character/story/event repositories.
* ``quests.py``          - quest/choice/branch repositories.
* ``progression.py``     - skill/perk/achievement repositories.
* ``economy.py``         - item/material/recipe repositories.
* ``world_building.py``  - location/environment/map repositories.
* ``society.py``         - faction/politics/religion repositories.
* ``misc.py``            - remaining game-system repositories.

Every historically importable ``InMemoryXxxRepository`` is re-exported
here so existing ``from src.infrastructure.in_memory_repositories import
X`` sites keep working. See ``docs/refactoring_plan_in_memory_repositories.md``.

Note: the original file defined 604 classes but only 394 unique names
(the rest were duplicates left by generator scripts; Python's
last-definition-wins already shadowed them). This facade re-exports the
394 unique names.
"""

from __future__ import annotations

# Re-export the generic bases and all repository classes.
from src.infrastructure.in_memory.base import (  # noqa: F401
    InMemoryRepository,
    InMemoryWorldEntityRepository,
)
from src.infrastructure.in_memory.economy import *  # noqa: F401,F403
from src.infrastructure.in_memory.misc import *  # noqa: F401,F403
from src.infrastructure.in_memory.narrative import *  # noqa: F401,F403
from src.infrastructure.in_memory.progression import *  # noqa: F401,F403
from src.infrastructure.in_memory.quests import *  # noqa: F401,F403
from src.infrastructure.in_memory.society import *  # noqa: F401,F403
from src.infrastructure.in_memory.world_building import *  # noqa: F401,F403

# Explicit re-export of the most commonly imported classes (clarity).
from src.infrastructure.in_memory.narrative import (  # noqa: F401
    InMemoryCharacterRepository,
    InMemoryWorldRepository,
)
