"""In-memory repositories for progression/skill/perk/achievement entities.

Extracted from the monolithic ``in_memory_repositories.py``. Standard
repositories inherit world-scoped CRUD from
:class:`InMemoryWorldEntityRepository`; repositories with extra query
methods or interface contracts preserve their original implementations.
"""

from __future__ import annotations

from src.infrastructure.in_memory.base import (
    InMemoryRepository,
    InMemoryWorldEntityRepository,
)

from typing import Any

from src.domain.entities.achievement import Achievement
from src.domain.entities.badge import Badge
from src.domain.entities.leaderboard import Leaderboard
from src.domain.entities.progression_event import ProgressionEvent
from src.domain.entities.rank import Rank
from src.domain.entities.title import Title
from src.domain.entities.trophy import Trophy

class InMemoryAchievementRepository(InMemoryWorldEntityRepository[Achievement]):
    """In-memory repository for Achievement (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryAttributeRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for AttributeType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryBadgeRepository(InMemoryWorldEntityRepository[Badge]):
    """In-memory repository for Badge (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryExperienceRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for ExperienceType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryLeaderboardRepository(InMemoryWorldEntityRepository[Leaderboard]):
    """In-memory repository for Leaderboard (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryLevelUpRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for LevelUpType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryLevel_upRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for LevelUpType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryMasteryRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for MasteryCategory (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryPerkRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for PerkType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryProgression_eventRepository(InMemoryWorldEntityRepository[ProgressionEvent]):
    """In-memory repository for ProgressionEvent (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryProgression_stateRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for CharacterState (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryRankRepository(InMemoryWorldEntityRepository[Rank]):
    """In-memory repository for Rank (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySkillRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for SkillType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryTalentTreeRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for TalentNodeType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryTalent_treeRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for TalentNodeType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryTitleRepository(InMemoryWorldEntityRepository[Title]):
    """In-memory repository for Title (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryTraitRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for TraitCategory (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryTrophyRepository(InMemoryWorldEntityRepository[Trophy]):
    """In-memory repository for Trophy (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass
