"""
In-Memory Repository Implementations

These are fast, in-memory implementations of the repository interfaces
for testing purposes. They allow us to test the contract behavior
without external dependencies.

In production, you'd replace these with database-backed implementations.
"""
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from src.domain.entities.world import World
from src.domain.entities.character import Character
from src.domain.repositories.world_repository import IWorldRepository
from src.domain.repositories.character_repository import ICharacterRepository
from src.domain.value_objects.common import (
    TenantId, EntityId, WorldName, CharacterName
)
from src.domain.exceptions import DuplicateEntity, EntityNotFound


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


class InMemoryStoryRepository:
    """In-memory implementation of Story repository for testing."""

    def __init__(self):
        self._stories: Dict[Tuple[TenantId, EntityId], "Story"] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, story: "Story") -> "Story":
        from src.domain.entities.story import Story

        if story.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(story, 'id', new_id)

        key = (story.tenant_id, story.id)
        self._stories[key] = story

        world_key = (story.tenant_id, story.world_id)
        if story.id not in self._by_world[world_key]:
            self._by_world[world_key].append(story.id)

        return story

    def find_by_id(self, tenant_id: TenantId, story_id: EntityId) -> Optional["Story"]:
        return self._stories.get((tenant_id, story_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List["Story"]:
        world_key = (tenant_id, world_id)
        story_ids = self._by_world.get(world_key, [])
        stories = []
        for story_id in story_ids[offset:offset + limit]:
            story = self._stories.get((tenant_id, story_id))
            if story:
                stories.append(story)
        return stories

    def delete(self, tenant_id: TenantId, story_id: EntityId) -> bool:
        key = (tenant_id, story_id)
        if key not in self._stories:
            return False

        story = self._stories[key]
        world_key = (tenant_id, story.world_id)
        if story_id in self._by_world[world_key]:
            self._by_world[world_key].remove(story_id)

        del self._stories[key]
        return True


class InMemoryEventRepository:
    """In-memory implementation of Event repository for testing."""

    def __init__(self):
        self._events: Dict[Tuple[TenantId, EntityId], "Event"] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, event: "Event") -> "Event":
        from src.domain.entities.event import Event

        if event.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(event, 'id', new_id)

        key = (event.tenant_id, event.id)
        self._events[key] = event

        world_key = (event.tenant_id, event.world_id)
        if event.id not in self._by_world[world_key]:
            self._by_world[world_key].append(event.id)

        return event

    def find_by_id(self, tenant_id: TenantId, event_id: EntityId) -> Optional["Event"]:
        return self._events.get((tenant_id, event_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List["Event"]:
        world_key = (tenant_id, world_id)
        event_ids = self._by_world.get(world_key, [])
        events = []
        for event_id in event_ids[offset:offset + limit]:
            event = self._events.get((tenant_id, event_id))
            if event:
                events.append(event)
        return events

    def delete(self, tenant_id: TenantId, event_id: EntityId) -> bool:
        key = (tenant_id, event_id)
        if key not in self._events:
            return False

        event = self._events[key]
        world_key = (event.tenant_id, event.world_id)
        if event_id in self._by_world[world_key]:
            self._by_world[world_key].remove(event_id)

        del self._events[key]
        return True


class InMemoryPageRepository:
    """In-memory implementation of Page repository for testing."""

    def __init__(self):
        self._pages: Dict[Tuple[TenantId, EntityId], "Page"] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, page: "Page") -> "Page":
        from src.domain.entities.page import Page

        if page.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(page, 'id', new_id)

        key = (page.tenant_id, page.id)
        self._pages[key] = page

        world_key = (page.tenant_id, page.world_id)
        if page.id not in self._by_world[world_key]:
            self._by_world[world_key].append(page.id)

        return page

    def find_by_id(self, tenant_id: TenantId, page_id: EntityId) -> Optional["Page"]:
        return self._pages.get((tenant_id, page_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List["Page"]:
        world_key = (tenant_id, world_id)
        page_ids = self._by_world.get(world_key, [])
        pages = []
        for page_id in page_ids[offset:offset + limit]:
            page = self._pages.get((tenant_id, page_id))
            if page:
                pages.append(page)
        return pages

    def delete(self, tenant_id: TenantId, page_id: EntityId) -> bool:
        key = (tenant_id, page_id)
        if key not in self._pages:
            return False

        page = self._pages[key]
        world_key = (page.tenant_id, page.world_id)
        if page_id in self._by_world[world_key]:
            self._by_world[world_key].remove(page_id)

        del self._pages[key]
        return True