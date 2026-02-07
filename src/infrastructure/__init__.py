"""Infrastructure layer - concrete repository implementations.

Available repositories:
- InMemoryWorldRepository, InMemoryCharacterRepository, etc. (in_memory_repositories.py)
- SQLiteWorldRepository, SQLiteCharacterRepository, etc. (sqlite_repositories.py)
"""

from .in_memory_repositories import (
    InMemoryWorldRepository,
    InMemoryCharacterRepository,
    InMemoryStoryRepository,
    InMemoryEventRepository,
    InMemoryPageRepository,
    InMemoryItemRepository,
    InMemoryLocationRepository,
    InMemoryEnvironmentRepository,
    InMemoryTextureRepository,
    InMemoryModel3DRepository,
)

from .sqlite_repositories import (
    SQLiteDatabase,
    SQLiteWorldRepository,
    SQLiteCharacterRepository,
    SQLiteStoryRepository,
    SQLiteEventRepository,
    SQLitePageRepository,
    SQLiteItemRepository,
    SQLiteLocationRepository,
    SQLiteEnvironmentRepository,
    SQLiteTextureRepository,
    SQLiteModel3DRepository,
    SQLiteSessionRepository,
    SQLiteTagRepository,
    SQLiteNoteRepository,
    SQLiteTemplateRepository,
    SQLiteChoiceRepository,
    SQLiteFlowchartRepository,
    SQLiteHandoutRepository,
    SQLiteImageRepository,
    SQLiteInspirationRepository,
    SQLiteMapRepository,
    SQLiteTokenboardRepository,
)

__all__ = [
    # In-memory repositories (for testing)
    'InMemoryWorldRepository',
    'InMemoryCharacterRepository',
    'InMemoryStoryRepository',
    'InMemoryEventRepository',
    'InMemoryPageRepository',
    'InMemoryItemRepository',
    'InMemoryLocationRepository',
    'InMemoryEnvironmentRepository',
    'InMemoryTextureRepository',
    'InMemoryModel3DRepository',
    'InMemorySessionRepository',
    'InMemoryTagRepository',
    'InMemoryNoteRepository',
    'InMemoryTemplateRepository',
    'InMemoryChoiceRepository',
    'InMemoryFlowchartRepository',
    'InMemoryHandoutRepository',
    'InMemoryImageRepository',
    'InMemoryInspirationRepository',
    'InMemoryMapRepository',
    'InMemoryTokenboardRepository',

    # SQLite repositoriesfrom src.infrastructure.in_memory_repositories import QuestChain
from src.infrastructure.in_memory_repositories import QuestNode
from src.infrastructure.in_memory_repositories import QuestPrerequisite
from src.infrastructure.in_memory_repositories import QuestObjective
from src.infrastructure.in_memory_repositories import QuestTracker
from src.infrastructure.in_memory_repositories import QuestGiver
from src.infrastructure.in_memory_repositories import QuestReward
from src.infrastructure.in_memory_repositories import QuestRewardTier
from src.infrastructure.sqlite_repositories import SQLiteQuestChain
from src.infrastructure.sqlite_repositories import SQLiteQuestNode
from src.infrastructure.sqlite_repositories import SQLiteQuestPrerequisite
from src.infrastructure.sqlite_repositories import SQLiteQuestObjective
from src.infrastructure.sqlite_repositories import SQLiteQuestTracker
from src.infrastructure.sqlite_repositories import SQLiteQuestGiver
from src.infrastructure.sqlite_repositories import SQLiteQuestReward
from src.infrastructure.sqlite_repositories import SQLiteQuestRewardTier (for production)
    'SQLiteDatabase',
    'SQLiteWorldRepository',
    'SQLiteCharacterRepository',
    'SQLiteStoryRepository',
    'SQLiteEventRepository',
    'SQLitePageRepository',
    'SQLiteItemRepository',
    'SQLiteLocationRepository',
    'SQLiteEnvironmentRepository',
    'SQLiteTextureRepository',
    'SQLiteModel3DRepository',
    'SQLiteSessionRepository',
    'SQLiteTagRepository',
    'SQLiteNoteRepository',
    'SQLiteTemplateRepository',
    'SQLiteChoiceRepository',
    'SQLiteFlowchartRepository',
    'SQLiteHandoutRepository',
    'SQLiteImageRepository',
    'SQLiteInspirationRepository',
    'SQLiteMapRepository',
    'SQLiteTokenboardRepository',
]


# Quest repositories
    'SQLiteQuestChain',
    'SQLiteQuestNode',
    'SQLiteQuestPrerequisite',
    'SQLiteQuestObjective',
    'SQLiteQuestTracker',
    'SQLiteQuestGiver',
    'SQLiteQuestReward',
    'SQLiteQuestRewardTier',


# Quest repositories
    InMemoryQuestChain,
    InMemoryQuestNode,
    InMemoryQuestPrerequisite,
    InMemoryQuestObjective,
    InMemoryQuestTracker,
    InMemoryQuestGiver,
    InMemoryQuestReward,
    InMemoryQuestRewardTier,

    SQLiteQuestChain,
    SQLiteQuestNode,
    SQLiteQuestPrerequisite,
    SQLiteQuestObjective,
    SQLiteQuestTracker,
    SQLiteQuestGiver,
    SQLiteQuestReward,
    SQLiteQuestRewardTier,
