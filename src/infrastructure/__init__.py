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

from src.infrastructure.in_memory_repositories import Skill
from src.infrastructure.in_memory_repositories import Perk
from src.infrastructure.in_memory_repositories import Trait
from src.infrastructure.in_memory_repositories import Attribute
from src.infrastructure.in_memory_repositories import Experience
from src.infrastructure.in_memory_repositories import LevelUp
from src.infrastructure.in_memory_repositories import TalentTree
from src.infrastructure.in_memory_repositories import Mastery
from src.infrastructure.in_memory_repositories import FactionHierarchy
from src.infrastructure.in_memory_repositories import FactionIdeology
from src.infrastructure.in_memory_repositories import FactionLeader
from src.infrastructure.in_memory_repositories import FactionMembership
from src.infrastructure.in_memory_repositories import FactionResource
from src.infrastructure.in_memory_repositories import FactionTerritory
from src.infrastructure.sqlite_repositories import SQLiteSkill
from src.infrastructure.sqlite_repositories import SQLitePerk
from src.infrastructure.sqlite_repositories import SQLiteTrait
from src.infrastructure.sqlite_repositories import SQLiteAttribute
from src.infrastructure.sqlite_repositories import SQLiteExperience
from src.infrastructure.sqlite_repositories import SQLiteLevelUp
from src.infrastructure.sqlite_repositories import SQLiteTalentTree
from src.infrastructure.sqlite_repositories import SQLiteMastery
from src.infrastructure.sqlite_repositories import SQLiteFactionHierarchy
from src.infrastructure.sqlite_repositories import SQLiteFactionIdeology
from src.infrastructure.sqlite_repositories import SQLiteFactionLeader
from src.infrastructure.sqlite_repositories import SQLiteFactionMembership
from src.infrastructure.sqlite_repositories import SQLiteFactionResource
from src.infrastructure.sqlite_repositories import SQLiteFactionTerritory
# Progression repositories
    Skill,
    Perk,
    Trait,
    Attribute,
    Experience,
    LevelUp,
    TalentTree,
    Mastery,

# Faction repositories
    FactionHierarchy,
    FactionIdeology,
    FactionLeader,
    FactionMembership,
    FactionResource,
    FactionTerritory,
# Progression repositories
    SQLiteSkill,
    SQLitePerk,
    SQLiteTrait,
    SQLiteAttribute,
    SQLiteExperience,
    SQLiteLevelUp,
    SQLiteTalentTree,
    SQLiteMastery,

# Faction repositories
    SQLiteFactionHierarchy,
    SQLiteFactionIdeology,
    SQLiteFactionLeader,
    SQLiteFactionMembership,
    SQLiteFactionResource,
    SQLiteFactionTerritory,
