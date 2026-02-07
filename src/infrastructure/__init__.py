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

    # SQLite repositories (for production)
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
]


