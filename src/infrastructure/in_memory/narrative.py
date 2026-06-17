"""In-memory repositories for narrative/story/world/character entities.

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

from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from src.domain.exceptions import DuplicateEntity, EntityNotFound
from src.domain.value_objects.common import (
    CharacterName,
    EntityId,
    Lighting,
    TenantId,
    TimeOfDay,
    Weather,
    WorldName,
)

from src.domain.entities.character_profile_entry import CharacterProfileEntry
from src.domain.entities.era import Era
from src.domain.entities.event import Event
from src.domain.entities.flash_forward import FlashForward
from src.domain.entities.flashback import Flashback
from src.domain.entities.journal_page import JournalPage
from src.domain.entities.lore_fragment import LoreFragment
from src.domain.entities.open_world_zone import OpenWorldZone
from src.domain.entities.page import Page
from src.domain.entities.rumor import Rumor
from src.domain.entities.seasonal_event import SeasonalEvent
from src.domain.entities.session import Session
from src.domain.entities.story import Story
from src.domain.entities.storyline import Storyline
from src.domain.entities.world_event import WorldEvent

from src.domain.repositories.character_repository import ICharacterRepository
from src.domain.repositories.handout_repository import IHandoutRepository
from src.domain.repositories.tokenboard_repository import ITokenboardRepository
from src.domain.repositories.world_repository import IWorldRepository

class InMemoryActRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for ActStructure (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryCampaignRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for CampaignType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryChapterRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for ChapterType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryCharacterEvolutionRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for EvolutionStage (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryCharacterProfileEntryRepository(InMemoryWorldEntityRepository[CharacterProfileEntry]):
    """In-memory repository for CharacterProfileEntry (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryCharacterRelationshipRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for RelationshipType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryCharacterRepository(ICharacterRepository):
    """
    In-memory implementation of Character repository for testing.

    Stores characters in memory with proper indexing for fast access.
    """

    def __init__(self):
        # Storage: (tenant_id, character_id) -> Character
        self._characters: Dict[Tuple[TenantId, EntityId], Character] = {}
        # Index: (tenant_id, world_id, character_name) -> character_id
        self._names: Dict[Tuple[TenantId, EntityId, CharacterName], EntityId] = {}
        # Index: (tenant_id, world_id) -> list of character_ids
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        # Index: tenant_id -> list of character_ids
        self._by_tenant: Dict[TenantId, List[EntityId]] = defaultdict(list)
        # ID counter for generating new IDs
        self._next_id = 1

    def save(self, character: Character) -> Character:
        # Assign ID if this is a new character
        if character.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(character, 'id', new_id)

        key = (character.tenant_id, character.id)
        name_key = (character.tenant_id, character.world_id, character.name)

        # Check for duplicate name in world
        if name_key in self._names and self._names[name_key] != character.id:
            raise DuplicateEntity(f"Character with name '{character.name}' already exists in this world")

        # Store the character
        self._characters[key] = character
        self._names[name_key] = character.id

        # Add to world index if not already there
        world_key = (character.tenant_id, character.world_id)
        if character.id not in self._by_world[world_key]:
            self._by_world[world_key].append(character.id)

        # Add to tenant index if not already there
        if character.id not in self._by_tenant[character.tenant_id]:
            self._by_tenant[character.tenant_id].append(character.id)

        return character

    def find_by_id(self, tenant_id: TenantId, character_id: EntityId) -> Optional[Character]:
        return self._characters.get((tenant_id, character_id))

    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: CharacterName) -> Optional[Character]:
        character_id = self._names.get((tenant_id, world_id, name))
        if character_id:
            return self._characters.get((tenant_id, character_id))
        return None

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Character]:
        world_key = (tenant_id, world_id)
        character_ids = self._by_world.get(world_key, [])
        characters = []
        for character_id in character_ids[offset:offset + limit]:
            character = self._characters.get((tenant_id, character_id))
            if character:
                characters.append(character)
        return characters

    def list_by_tenant(self, tenant_id: TenantId, limit: int = 100, offset: int = 0) -> List[Character]:
        character_ids = self._by_tenant.get(tenant_id, [])
        characters = []
        for character_id in character_ids[offset:offset + limit]:
            character = self._characters.get((tenant_id, character_id))
            if character:
                characters.append(character)
        return characters

    def search_by_backstory(self, tenant_id: TenantId, search_term: str, limit: int = 20) -> List[Character]:
        """Simple substring search in backstories."""
        results = []
        for character in self._characters.values():
            if character.tenant_id == tenant_id and search_term.lower() in character.backstory.value.lower():
                results.append(character)
                if len(results) >= limit:
                    break
        return results

    def delete(self, tenant_id: TenantId, character_id: EntityId) -> bool:
        key = (tenant_id, character_id)
        if key not in self._characters:
            return False

        character = self._characters[key]

        # Remove from all indexes
        name_key = (tenant_id, character.world_id, character.name)
        if name_key in self._names:
            del self._names[name_key]

        world_key = (tenant_id, character.world_id)
        if character_id in self._by_world[world_key]:
            self._by_world[world_key].remove(character_id)

        if character_id in self._by_tenant[tenant_id]:
            self._by_tenant[tenant_id].remove(character_id)

        del self._characters[key]
        return True

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: CharacterName) -> bool:
        return (tenant_id, world_id, name) in self._names


class InMemoryCharacterVariantRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for VariantType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryCharacter_evolutionRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for EvolutionStage (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryCharacter_profile_entryRepository(InMemoryWorldEntityRepository[CharacterProfileEntry]):
    """In-memory repository for CharacterProfileEntry (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryCharacter_relationshipRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for RelationshipType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryCharacter_variantRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for VariantType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryEndingRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for EndingType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryEpilogueRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for EpilogueType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryEpisodeRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for EpisodeType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryEraRepository(InMemoryWorldEntityRepository[Era]):
    """In-memory repository for Era (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryEraTransitionRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for TransitionType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryEra_transitionRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for TransitionType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryEventRepository(InMemoryWorldEntityRepository[Event]):
    """In-memory repository for Event (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryEvent_chainRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for ChainStatus (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryFlashForwardRepository(InMemoryWorldEntityRepository[FlashForward]):
    """In-memory repository for FlashForward (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFlashbackRepository(InMemoryWorldEntityRepository[Flashback]):
    """In-memory repository for Flashback (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryHandoutRepository(IHandoutRepository):
    """In-memory implementation of Handout repository for testing."""

    def __init__(self):
        self._handouts: Dict[Tuple[TenantId, EntityId], object] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._by_session: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, handout: object) -> object:
        if handout.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(handout, 'id', new_id)

        key = (handout.tenant_id, handout.id)
        self._handouts[key] = handout

        session_key = (handout.tenant_id, handout.session_id) if hasattr(handout, 'session_id') else None
        if session_key:
            if handout.id not in self._by_session[session_key]:
                self._by_session[session_key].append(handout.id)

        world_key = (handout.tenant_id, handout.world_id)
        if handout.id not in self._by_world[world_key]:
            self._by_world[world_key].append(handout.id)

        return handout

    def find_by_id(self, tenant_id: TenantId, handout_id: EntityId) -> Optional[object]:
        return self._handouts.get((tenant_id, handout_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        world_key = (tenant_id, world_id)
        handout_ids = self._by_world.get(world_key, [])
        handouts = []
        for handout_id in handout_ids[offset:offset + limit]:
            handout = self._handouts.get((tenant_id, handout_id))
            if handout:
                handouts.append(handout)
        return handouts

    def list_by_session(self, tenant_id: TenantId, session_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        session_key = (tenant_id, session_id)
        handout_ids = self._by_session.get(session_key, [])
        handouts = []
        for handout_id in handout_ids[offset:offset + limit]:
            handout = self._handouts.get((tenant_id, handout_id))
            if handout:
                handouts.append(handout)
        return handouts

    def list_revealed(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        all_handouts = self.list_by_world(tenant_id, world_id)
        return [h for h in all_handouts if getattr(h, 'is_revealed', False)][offset:offset + limit]

    def delete(self, tenant_id: TenantId, handout_id: EntityId) -> bool:
        key = (tenant_id, handout_id)
        if key not in self._handouts:
            return False

        handout = self._handouts[key]

        session_key = (handout.tenant_id, handout.session_id) if hasattr(handout, 'session_id') else None
        if session_key and handout_id in self._by_session[session_key]:
            self._by_session[session_key].remove(handout_id)

        world_key = (handout.tenant_id, handout.world_id)
        if handout_id in self._by_world[world_key]:
            self._by_world[world_key].remove(handout_id)

        del self._handouts[key]
        return True


class InMemoryJournalPageRepository(InMemoryWorldEntityRepository[JournalPage]):
    """In-memory repository for JournalPage (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryLoreFragmentRepository(InMemoryWorldEntityRepository[LoreFragment]):
    """In-memory repository for LoreFragment (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryLore_axiomsRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for AxiomType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryLore_fragmentRepository(InMemoryWorldEntityRepository[LoreFragment]):
    """In-memory repository for LoreFragment (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryOpenWorldZoneRepository(InMemoryWorldEntityRepository[OpenWorldZone]):
    """In-memory repository for OpenWorldZone (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPageRepository(InMemoryWorldEntityRepository[Page]):
    """In-memory repository for Page (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPlotBranchRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for BranchType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryPlotDeviceRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for PlotDeviceType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryPlot_branchRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for BranchType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryPlot_deviceRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for PlotDeviceType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryPrologueRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for PrologueType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryRumorRepository(InMemoryWorldEntityRepository[Rumor]):
    """In-memory repository for Rumor (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySeasonalEventRepository(InMemoryWorldEntityRepository[SeasonalEvent]):
    """In-memory repository for SeasonalEvent (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySessionDataRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for SessionData (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemorySessionRepository:
    """In-memory implementation of Session repository for testing."""

    def __init__(self):
        self._sessions: Dict[Tuple[TenantId, EntityId], object] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._by_story: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, session: object) -> object:
        if session.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(session, 'id', new_id)

        key = (session.tenant_id, session.id)
        self._sessions[key] = session

        world_key = (session.tenant_id, session.world_id)
        if session.id not in self._by_world[world_key]:
            self._by_world[world_key].append(session.id)

        if hasattr(session, 'story_id') and session.story_id:
            story_key = (session.tenant_id, session.story_id)
            if session.id not in self._by_story[story_key]:
                self._by_story[story_key].append(session.id)

        return session

    def find_by_id(self, tenant_id: TenantId, session_id: EntityId) -> Optional[object]:
        return self._sessions.get((tenant_id, session_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        world_key = (tenant_id, world_id)
        session_ids = self._by_world.get(world_key, [])
        sessions = []
        for session_id in session_ids[offset:offset + limit]:
            session = self._sessions.get((tenant_id, session_id))
            if session:
                sessions.append(session)
        return sessions

    def list_by_story(self, tenant_id: TenantId, story_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        story_key = (tenant_id, story_id)
        session_ids = self._by_story.get(story_key, [])
        sessions = []
        for session_id in session_ids[offset:offset + limit]:
            session = self._sessions.get((tenant_id, session_id))
            if session:
                sessions.append(session)
        return sessions

    def list_active(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        all_sessions = self.list_by_world(tenant_id, world_id, limit=limit, offset=offset)
        return [s for s in all_sessions if getattr(s, 'is_active', True)]

    def delete(self, tenant_id: TenantId, session_id: EntityId) -> bool:
        key = (tenant_id, session_id)
        if key not in self._sessions:
            return False

        session = self._sessions[key]

        world_key = (session.tenant_id, session.world_id)
        if session_id in self._by_world[world_key]:
            self._by_world[world_key].remove(session_id)

        if hasattr(session, 'story_id') and session.story_id:
            story_key = (session.tenant_id, session.story_id)
            if session_id in self._by_story[story_key]:
                self._by_story[story_key].remove(session_id)

        del self._sessions[key]
        return True


class InMemorySession_dataRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for SessionData (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryStoryRepository(InMemoryWorldEntityRepository[Story]):
    """In-memory repository for Story (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryStorylineRepository(InMemoryWorldEntityRepository[Storyline]):
    """In-memory repository for Storyline (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryTimelineRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for TimelineType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryTokenboardRepository(ITokenboardRepository):
    """In-memory implementation of Tokenboard repository for testing."""

    def __init__(self):
        self._tokenboards: Dict[Tuple[TenantId, EntityId], object] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, tokenboard: object) -> object:
        if tokenboard.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(tokenboard, 'id', new_id)

        key = (tokenboard.tenant_id, tokenboard.id)
        self._tokenboards[key] = tokenboard

        world_key = (tokenboard.tenant_id, tokenboard.world_id)
        if tokenboard.id not in self._by_world[world_key]:
            self._by_world[world_key].append(tokenboard.id)

        return tokenboard

    def find_by_id(self, tenant_id: TenantId, tokenboard_id: EntityId) -> Optional[object]:
        return self._tokenboards.get((tenant_id, tokenboard_id))

    def find_active(self, tenant_id: TenantId, world_id: EntityId) -> Optional[object]:
        all_tokenboards = self.list_by_world(tenant_id, world_id)
        for tokenboard in all_tokenboards:
            if getattr(tokenboard, 'is_active', False):
                return tokenboard
        return None

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        world_key = (tenant_id, world_id)
        tokenboard_ids = self._by_world.get(world_key, [])
        tokenboards = []
        for tokenboard_id in tokenboard_ids[offset:offset + limit]:
            tokenboard = self._tokenboards.get((tenant_id, tokenboard_id))
            if tokenboard:
                tokenboards.append(tokenboard)
        return tokenboards

    def delete(self, tenant_id: TenantId, tokenboard_id: EntityId) -> bool:
        key = (tenant_id, tokenboard_id)
        if key not in self._tokenboards:
            return False

        tokenboard = self._tokenboards[key]
        world_key = (tokenboard.tenant_id, tokenboard.world_id)
        if tokenboard_id in self._by_world[world_key]:
            self._by_world[world_key].remove(tokenboard_id)

        del self._tokenboards[key]
        return True


class InMemoryVoiceActorRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for VoiceActorStatus (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryWorldEventRepository(InMemoryWorldEntityRepository[WorldEvent]):
    """In-memory repository for WorldEvent (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryWorldRepository(IWorldRepository):
    """
    In-memory implementation of World repository for testing.

    Stores worlds in memory using dictionaries for fast access.
    """

    def __init__(self):
        # Storage: (tenant_id, world_id) -> World
        self._worlds: Dict[Tuple[TenantId, EntityId], World] = {}
        # Index: (tenant_id, world_name) -> world_id
        self._names: Dict[Tuple[TenantId, WorldName], EntityId] = {}
        # Index: tenant_id -> list of world_ids
        self._by_tenant: Dict[TenantId, List[EntityId]] = defaultdict(list)
        # ID counter for generating new IDs
        self._next_id = 1

    def save(self, world: World) -> World:
        # Assign ID if this is a new world
        if world.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(world, 'id', new_id)

        key = (world.tenant_id, world.id)
        name_key = (world.tenant_id, world.name)

        # Check for duplicate name
        if name_key in self._names and self._names[name_key] != world.id:
            raise DuplicateEntity(f"World with name '{world.name}' already exists")

        # Store the world
        self._worlds[key] = world
        self._names[name_key] = world.id

        # Add to tenant index if not already there
        if world.id not in self._by_tenant[world.tenant_id]:
            self._by_tenant[world.tenant_id].append(world.id)

        return world

    def find_by_id(self, tenant_id: TenantId, world_id: EntityId) -> Optional[World]:
        return self._worlds.get((tenant_id, world_id))

    def find_by_name(self, tenant_id: TenantId, name: WorldName) -> Optional[World]:
        world_id = self._names.get((tenant_id, name))
        if world_id:
            return self._worlds.get((tenant_id, world_id))
        return None

    def list_by_tenant(self, tenant_id: TenantId, limit: int = 100, offset: int = 0) -> List[World]:
        world_ids = self._by_tenant.get(tenant_id, [])
        worlds = []
        for world_id in world_ids[offset:offset + limit]:
            world = self._worlds.get((tenant_id, world_id))
            if world:
                worlds.append(world)
        return worlds

    def delete(self, tenant_id: TenantId, world_id: EntityId) -> bool:
        key = (tenant_id, world_id)
        if key not in self._worlds:
            return False

        world = self._worlds[key]

        # Remove from all indexes
        name_key = (tenant_id, world.name)
        if name_key in self._names:
            del self._names[name_key]

        if world_id in self._by_tenant[tenant_id]:
            self._by_tenant[tenant_id].remove(world_id)

        del self._worlds[key]
        return True

    def exists(self, tenant_id: TenantId, name: WorldName) -> bool:
        return (tenant_id, name) in self._names


class InMemoryWorld_eventRepository(InMemoryWorldEntityRepository[WorldEvent]):
    """In-memory repository for WorldEvent (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass
