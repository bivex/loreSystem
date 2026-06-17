"""In-memory repositories for quest/choice/branch entities.

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

from src.domain.entities.choice import Choice
from src.domain.entities.puzzle import Puzzle
from src.domain.entities.quest import Quest
from src.domain.entities.quest_chain import QuestChain
from src.domain.entities.quest_giver import QuestGiver
from src.domain.entities.quest_node import QuestNode
from src.domain.entities.quest_objective import QuestObjective
from src.domain.entities.quest_prerequisite import QuestPrerequisite
from src.domain.entities.quest_reward_tier import QuestRewardTier
from src.domain.entities.quest_tracker import QuestTracker
from src.domain.entities.riddle import Riddle

class InMemoryBranchPointRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for BranchPointType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryBranch_pointRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for BranchPointType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryChoiceRepository(InMemoryWorldEntityRepository[Choice]):
    """In-memory repository for Choice (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryConsequenceRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for ConsequenceType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryMoral_choiceRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for MoralAlignment (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryPuzzleRepository(InMemoryWorldEntityRepository[Puzzle]):
    """In-memory repository for Puzzle (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryQuestChainRepository(InMemoryWorldEntityRepository[QuestChain]):
    """In-memory repository for QuestChain (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryQuestGiverRepository(InMemoryWorldEntityRepository[QuestGiver]):
    """In-memory repository for QuestGiver (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryQuestNodeRepository(InMemoryWorldEntityRepository[QuestNode]):
    """In-memory repository for QuestNode (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryQuestObjectiveRepository(InMemoryWorldEntityRepository[QuestObjective]):
    """In-memory repository for QuestObjective (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryQuestPrerequisiteRepository(InMemoryWorldEntityRepository[QuestPrerequisite]):
    """In-memory repository for QuestPrerequisite (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryQuestRepository(InMemoryWorldEntityRepository[Quest]):
    """In-memory repository for Quest (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryQuestRewardRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for QuestReward (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryQuestRewardTierRepository(InMemoryWorldEntityRepository[QuestRewardTier]):
    """In-memory repository for QuestRewardTier (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryQuestTrackerRepository(InMemoryWorldEntityRepository[QuestTracker]):
    """In-memory repository for QuestTracker (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryQuest_chainRepository(InMemoryWorldEntityRepository[QuestChain]):
    """In-memory repository for QuestChain (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryQuest_giverRepository(InMemoryWorldEntityRepository[QuestGiver]):
    """In-memory repository for QuestGiver (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryQuest_nodeRepository(InMemoryWorldEntityRepository[QuestNode]):
    """In-memory repository for QuestNode (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryQuest_objectiveRepository(InMemoryWorldEntityRepository[QuestObjective]):
    """In-memory repository for QuestObjective (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryQuest_prerequisiteRepository(InMemoryWorldEntityRepository[QuestPrerequisite]):
    """In-memory repository for QuestPrerequisite (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryQuest_rewardRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for Quest_reward (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryQuest_reward_tierRepository(InMemoryWorldEntityRepository[QuestRewardTier]):
    """In-memory repository for QuestRewardTier (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryQuest_trackerRepository(InMemoryWorldEntityRepository[QuestTracker]):
    """In-memory repository for QuestTracker (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryRewardRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for RewardType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryRiddleRepository(InMemoryWorldEntityRepository[Riddle]):
    """In-memory repository for Riddle (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass
