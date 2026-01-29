"""
Repository Interfaces (Ports)

These are abstract interfaces defining how the domain interacts with
persistence. Implementations are in the infrastructure layer.

Key principles:
- Repositories work with aggregates, not individual entities
- Methods express domain operations, not database operations
- No infrastructure concerns (SQL, ES) leak into interfaces
"""

from .character_repository import ICharacterRepository
from .choice_repository import IChoiceRepository
from .flowchart_repository import IFlowchartRepository
from .handout_repository import IHandoutRepository
from .image_repository import IImageRepository
from .inspiration_repository import IInspirationRepository
from .map_repository import IMapRepository
from .note_repository import INoteRepository
from .page_repository import IPageRepository
from .session_repository import ISessionRepository
from .story_repository import IStoryRepository
from .tag_repository import ITagRepository
from .template_repository import ITemplateRepository
from .tokenboard_repository import ITokenboardRepository
from .world_repository import IWorldRepository

__all__ = [
    "ICharacterRepository",
    "IChoiceRepository",
    "IFlowchartRepository",
    "IHandoutRepository",
    "IImageRepository",
    "IInspirationRepository",
    "IMapRepository",
    "INoteRepository",
    "IPageRepository",
    "ISessionRepository",
    "IStoryRepository",
    "ITagRepository",
    "ITemplateRepository",
    "ITokenboardRepository",
    "IWorldRepository",
]
