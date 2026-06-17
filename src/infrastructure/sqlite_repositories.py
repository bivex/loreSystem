"""SQLite-backed repository implementations.

This module is a **backward-compatibility facade**. The monolithic
~28,900-line implementation (515 repository/database class definitions,
of which 111 names were duplicated from branch merges; Python's
last-definition-wins already shadowed them) has been split across the
:mod:`src.infrastructure.sqlite` package:

* :mod:`.database`        - ``SQLiteDatabase`` (connection manager + schema init).
* :mod:`.base`            - ``SQLiteRepositoryBase`` (shared ``db`` plumbing +
  execution helpers; SQL itself is entity-specific so it cannot be generically
  abstracted without rewriting every repository).
* ``narrative.py``        - world/character/story/event repositories.
* ``quests.py``           - quest/choice/branch repositories.
* ``progression.py``      - skill/perk/achievement repositories.
* ``economy.py``          - item/material/recipe repositories.
* ``world_building.py``   - location/environment/map repositories.
* ``society.py``          - faction/politics/religion repositories.
* ``misc.py``             - remaining game-system repositories.

Every historically importable ``SQLiteXxxRepository`` and ``SQLiteDatabase``
is re-exported here so existing ``from src.infrastructure.sqlite_repositories
import X`` sites keep working. See
``docs/refactoring_plan_sqlite_repositories.md``.

Note: the original file defined 515 classes but only 403 unique names
(the rest were duplicates from branch merges; Python's last-def-wins
already shadowed them). ``SQLiteDatabase`` itself was defined twice. This
facade re-exports the 402 unique repository names plus ``SQLiteDatabase``.
"""

from __future__ import annotations

# Re-export the database manager, plumbing base, and all repository classes.
from src.infrastructure.sqlite.base import SQLiteRepositoryBase  # noqa: F401
from src.infrastructure.sqlite.database import SQLiteDatabase  # noqa: F401
from src.infrastructure.sqlite.economy import *  # noqa: F401,F403
from src.infrastructure.sqlite.misc import *  # noqa: F401,F403
from src.infrastructure.sqlite.narrative import *  # noqa: F401,F403
from src.infrastructure.sqlite.progression import *  # noqa: F401,F403
from src.infrastructure.sqlite.quests import *  # noqa: F401,F403
from src.infrastructure.sqlite.society import *  # noqa: F401,F403
from src.infrastructure.sqlite.world_building import *  # noqa: F401,F403

# Explicit re-export of the most commonly imported symbols (clarity).
from src.infrastructure.sqlite.database import (  # noqa: F401
    SQLiteDatabase,
)
from src.infrastructure.sqlite.narrative import (  # noqa: F401
    SQLiteCharacterRepository,
    SQLiteWorldRepository,
)
