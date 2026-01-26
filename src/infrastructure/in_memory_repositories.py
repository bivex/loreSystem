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
from src.domain.entities.item import Item
from src.domain.entities.location import Location
from src.domain.entities.environment import Environment
from src.domain.entities.texture import Texture
from src.domain.entities.model3d import Model3D
from src.domain.repositories.world_repository import IWorldRepository
from src.domain.repositories.character_repository import ICharacterRepository
from src.domain.repositories.item_repository import IItemRepository
from src.domain.repositories.location_repository import ILocationRepository
from src.domain.repositories.environment_repository import IEnvironmentRepository
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


class InMemoryItemRepository(IItemRepository):
    """
    In-memory implementation of Item repository for testing.

    Stores items in memory with proper indexing for fast access.
    """

    def __init__(self):
        # Storage: (tenant_id, item_id) -> Item
        self._items: Dict[Tuple[TenantId, EntityId], Item] = {}
        # Index: (tenant_id, world_id, item_name) -> item_id
        self._names: Dict[Tuple[TenantId, EntityId, str], EntityId] = {}
        # Index: (tenant_id, world_id) -> list of item_ids
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        # Index: tenant_id -> list of item_ids
        self._by_tenant: Dict[TenantId, List[EntityId]] = defaultdict(list)
        # ID counter for generating new IDs
        self._next_id = 1

    def save(self, item: Item) -> Item:
        # Assign ID if this is a new item
        if item.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(item, 'id', new_id)

        key = (item.tenant_id, item.id)
        name_key = (item.tenant_id, item.world_id, item.name)

        # Check for duplicate name in world
        if name_key in self._names and self._names[name_key] != item.id:
            raise DuplicateEntity(f"Item with name '{item.name}' already exists in this world")

        # Store the item
        self._items[key] = item
        self._names[name_key] = item.id

        # Add to world index if not already there
        world_key = (item.tenant_id, item.world_id)
        if item.id not in self._by_world[world_key]:
            self._by_world[world_key].append(item.id)

        # Add to tenant index if not already there
        if item.id not in self._by_tenant[item.tenant_id]:
            self._by_tenant[item.tenant_id].append(item.id)

        return item

    def find_by_id(self, tenant_id: TenantId, item_id: EntityId) -> Optional[Item]:
        return self._items.get((tenant_id, item_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Item]:
        world_key = (tenant_id, world_id)
        item_ids = self._by_world.get(world_key, [])
        items = []
        for item_id in item_ids[offset:offset + limit]:
            item = self._items.get((tenant_id, item_id))
            if item:
                items.append(item)
        return items

    def list_by_tenant(self, tenant_id: TenantId, limit: int = 100, offset: int = 0) -> List[Item]:
        item_ids = self._by_tenant.get(tenant_id, [])
        items = []
        for item_id in item_ids[offset:offset + limit]:
            item = self._items.get((tenant_id, item_id))
            if item:
                items.append(item)
        return items

    def search_by_name(self, tenant_id: TenantId, search_term: str, limit: int = 20) -> List[Item]:
        """Simple substring search in item names."""
        results = []
        for item in self._items.values():
            if item.tenant_id == tenant_id and search_term.lower() in item.name.lower():
                results.append(item)
                if len(results) >= limit:
                    break
        return results

    def delete(self, tenant_id: TenantId, item_id: EntityId) -> bool:
        key = (tenant_id, item_id)
        if key not in self._items:
            return False

        item = self._items[key]

        # Remove from all indexes
        name_key = (tenant_id, item.world_id, item.name)
        if name_key in self._names:
            del self._names[name_key]

        world_key = (tenant_id, item.world_id)
        if item_id in self._by_world[world_key]:
            self._by_world[world_key].remove(item_id)

        if item_id in self._by_tenant[tenant_id]:
            self._by_tenant[tenant_id].remove(item_id)

        del self._items[key]
        return True

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: str) -> bool:
        return (tenant_id, world_id, name) in self._names


class InMemoryLocationRepository(ILocationRepository):
    """
    In-memory implementation of Location repository for testing.

    Stores locations in memory with proper indexing for fast access.
    """

    def __init__(self):
        # Storage: (tenant_id, location_id) -> Location
        self._locations: Dict[Tuple[TenantId, EntityId], Location] = {}
        # Index: (tenant_id, world_id, location_name) -> location_id
        self._names: Dict[Tuple[TenantId, EntityId, str], EntityId] = {}
        # Index: (tenant_id, world_id) -> list of location_ids
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        # Index: (tenant_id, world_id, location_type) -> list of location_ids
        self._by_type: Dict[Tuple[TenantId, EntityId, str], List[EntityId]] = defaultdict(list)
        # Index: tenant_id -> list of location_ids
        self._by_tenant: Dict[TenantId, List[EntityId]] = defaultdict(list)
        # ID counter for generating new IDs
        self._next_id = 1

    def save(self, location: Location) -> Location:
        # Assign ID if this is a new location
        if location.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(location, 'id', new_id)

        key = (location.tenant_id, location.id)
        name_key = (location.tenant_id, location.world_id, location.name)

        # Check for duplicate name in world
        if name_key in self._names and self._names[name_key] != location.id:
            raise DuplicateEntity(f"Location with name '{location.name}' already exists in this world")

        # Store the location
        self._locations[key] = location
        self._names[name_key] = location.id

        # Add to world index if not already there
        world_key = (location.tenant_id, location.world_id)
        if location.id not in self._by_world[world_key]:
            self._by_world[world_key].append(location.id)

        # Add to type index
        type_key = (location.tenant_id, location.world_id, location.location_type.value)
        if location.id not in self._by_type[type_key]:
            self._by_type[type_key].append(location.id)

        # Add to tenant index if not already there
        if location.id not in self._by_tenant[location.tenant_id]:
            self._by_tenant[location.tenant_id].append(location.id)

        return location

    def find_by_id(self, tenant_id: TenantId, location_id: EntityId) -> Optional[Location]:
        return self._locations.get((tenant_id, location_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Location]:
        world_key = (tenant_id, world_id)
        location_ids = self._by_world.get(world_key, [])
        locations = []
        for location_id in location_ids[offset:offset + limit]:
            location = self._locations.get((tenant_id, location_id))
            if location:
                locations.append(location)
        return locations

    def list_by_tenant(self, tenant_id: TenantId, limit: int = 100, offset: int = 0) -> List[Location]:
        location_ids = self._by_tenant.get(tenant_id, [])
        locations = []
        for location_id in location_ids[offset:offset + limit]:
            location = self._locations.get((tenant_id, location_id))
            if location:
                locations.append(location)
        return locations

    def search_by_name(self, tenant_id: TenantId, search_term: str, limit: int = 20) -> List[Location]:
        """Simple substring search in location names."""
        results = []
        for location in self._locations.values():
            if location.tenant_id == tenant_id and search_term.lower() in location.name.lower():
                results.append(location)
                if len(results) >= limit:
                    break
        return results

    def find_by_type(self, tenant_id: TenantId, world_id: EntityId, location_type: str, limit: int = 50) -> List[Location]:
        type_key = (tenant_id, world_id, location_type)
        location_ids = self._by_type.get(type_key, [])
        locations = []
        for location_id in location_ids[:limit]:
            location = self._locations.get((tenant_id, location_id))
            if location:
                locations.append(location)
        return locations

    def delete(self, tenant_id: TenantId, location_id: EntityId) -> bool:
        key = (tenant_id, location_id)
        if key not in self._locations:
            return False

        location = self._locations[key]

        # Remove from all indexes
        name_key = (tenant_id, location.world_id, location.name)
        if name_key in self._names:
            del self._names[name_key]

        world_key = (tenant_id, location.world_id)
        if location_id in self._by_world[world_key]:
            self._by_world[world_key].remove(location_id)

        type_key = (tenant_id, location.world_id, location.location_type.value)
        if location_id in self._by_type[type_key]:
            self._by_type[type_key].remove(location_id)

        if location_id in self._by_tenant[tenant_id]:
            self._by_tenant[tenant_id].remove(location_id)

        del self._locations[key]
        return True

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: str) -> bool:
        return (tenant_id, world_id, name) in self._names


class InMemoryEnvironmentRepository(IEnvironmentRepository):
    """
    In-memory implementation of Environment repository for testing.

    Stores environments in memory with proper indexing for fast access.
    """

    def __init__(self):
        # Storage: (tenant_id, environment_id) -> Environment
        self._environments: Dict[Tuple[TenantId, EntityId], Environment] = {}
        # Index: (tenant_id, location_id, environment_name) -> environment_id
        self._names: Dict[Tuple[TenantId, EntityId, str], EntityId] = {}
        # Index: (tenant_id, world_id) -> list of environment_ids
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        # Index: (tenant_id, location_id) -> list of environment_ids
        self._by_location: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        # Index: (tenant_id, world_id, time_of_day, weather, lighting) -> list of environment_ids
        self._by_conditions: Dict[Tuple[TenantId, EntityId, str, str, str], List[EntityId]] = defaultdict(list)
        # Index: (tenant_id, location_id) -> active environment_id
        self._active_by_location: Dict[Tuple[TenantId, EntityId], EntityId] = {}
        # Index: tenant_id -> list of environment_ids
        self._by_tenant: Dict[TenantId, List[EntityId]] = defaultdict(list)
        # ID counter for generating new IDs
        self._next_id = 1

    def save(self, environment: Environment) -> Environment:
        # Assign ID if this is a new environment
        if environment.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(environment, 'id', new_id)

        key = (environment.tenant_id, environment.id)
        name_key = (environment.tenant_id, environment.location_id, environment.name)

        # Check for duplicate name for location
        if name_key in self._names and self._names[name_key] != environment.id:
            raise DuplicateEntity(f"Environment with name '{environment.name}' already exists for this location")

        # Store the environment
        self._environments[key] = environment
        self._names[name_key] = environment.id

        # Add to world index if not already there
        world_key = (environment.tenant_id, environment.world_id)
        if environment.id not in self._by_world[world_key]:
            self._by_world[world_key].append(environment.id)

        # Add to location index if not already there
        location_key = (environment.tenant_id, environment.location_id)
        if environment.id not in self._by_location[location_key]:
            self._by_location[location_key].append(environment.id)

        # Add to conditions index
        conditions_key = (
            environment.tenant_id,
            environment.world_id,
            environment.time_of_day.value,
            environment.weather.value,
            environment.lighting.value
        )
        if environment.id not in self._by_conditions[conditions_key]:
            self._by_conditions[conditions_key].append(environment.id)

        # Handle active environment for location
        if environment.is_active:
            self._active_by_location[location_key] = environment.id
        elif self._active_by_location.get(location_key) == environment.id:
            # If this was active but now inactive, remove from active index
            del self._active_by_location[location_key]

        # Add to tenant index if not already there
        if environment.id not in self._by_tenant[environment.tenant_id]:
            self._by_tenant[environment.tenant_id].append(environment.id)

        return environment

    def find_by_id(self, tenant_id: TenantId, environment_id: EntityId) -> Optional[Environment]:
        return self._environments.get((tenant_id, environment_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Environment]:
        world_key = (tenant_id, world_id)
        environment_ids = self._by_world.get(world_key, [])
        environments = []
        for environment_id in environment_ids[offset:offset + limit]:
            environment = self._environments.get((tenant_id, environment_id))
            if environment:
                environments.append(environment)
        return environments

    def list_by_location(self, tenant_id: TenantId, location_id: EntityId, limit: int = 20, offset: int = 0) -> List[Environment]:
        location_key = (tenant_id, location_id)
        environment_ids = self._by_location.get(location_key, [])
        environments = []
        for environment_id in environment_ids[offset:offset + limit]:
            environment = self._environments.get((tenant_id, environment_id))
            if environment:
                environments.append(environment)
        return environments

    def list_by_tenant(self, tenant_id: TenantId, limit: int = 100, offset: int = 0) -> List[Environment]:
        environment_ids = self._by_tenant.get(tenant_id, [])
        environments = []
        for environment_id in environment_ids[offset:offset + limit]:
            environment = self._environments.get((tenant_id, environment_id))
            if environment:
                environments.append(environment)
        return environments

    def search_by_name(self, tenant_id: TenantId, search_term: str, limit: int = 20) -> List[Environment]:
        """Simple substring search in environment names."""
        results = []
        for environment in self._environments.values():
            if environment.tenant_id == tenant_id and search_term.lower() in environment.name.lower():
                results.append(environment)
                if len(results) >= limit:
                    break
        return results

    def find_by_conditions(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        time_of_day: Optional[TimeOfDay] = None,
        weather: Optional[Weather] = None,
        lighting: Optional[Lighting] = None,
        limit: int = 50,
    ) -> List[Environment]:
        # If no conditions specified, return all environments in world
        if time_of_day is None and weather is None and lighting is None:
            return self.list_by_world(tenant_id, world_id, limit, 0)

        # Build conditions key with wildcards for unspecified conditions
        tod_value = time_of_day.value if time_of_day else "*"
        weather_value = weather.value if weather else "*"
        lighting_value = lighting.value if lighting else "*"

        # Find all matching condition combinations
        results = []
        for conditions_key, environment_ids in self._by_conditions.items():
            key_tenant, key_world, key_tod, key_weather, key_lighting = conditions_key
            if key_tenant != tenant_id or key_world != world_id:
                continue

            # Check if conditions match (using * as wildcard)
            tod_match = tod_value == "*" or key_tod == tod_value
            weather_match = weather_value == "*" or key_weather == weather_value
            lighting_match = lighting_value == "*" or key_lighting == lighting_value

            if tod_match and weather_match and lighting_match:
                for environment_id in environment_ids[:limit - len(results)]:
                    environment = self._environments.get((tenant_id, environment_id))
                    if environment:
                        results.append(environment)
                        if len(results) >= limit:
                            break
                if len(results) >= limit:
                    break

        return results

    def find_active_by_location(self, tenant_id: TenantId, location_id: EntityId) -> Optional[Environment]:
        location_key = (tenant_id, location_id)
        active_id = self._active_by_location.get(location_key)
        if active_id:
            return self._environments.get((tenant_id, active_id))
        return None

    def delete(self, tenant_id: TenantId, environment_id: EntityId) -> bool:
        key = (tenant_id, environment_id)
        if key not in self._environments:
            return False

        environment = self._environments[key]

        # Remove from all indexes
        name_key = (tenant_id, environment.location_id, environment.name)
        if name_key in self._names:
            del self._names[name_key]

        world_key = (tenant_id, environment.world_id)
        if environment_id in self._by_world[world_key]:
            self._by_world[world_key].remove(environment_id)

        location_key = (tenant_id, environment.location_id)
        if environment_id in self._by_location[location_key]:
            self._by_location[location_key].remove(environment_id)

        conditions_key = (
            tenant_id,
            environment.world_id,
            environment.time_of_day.value,
            environment.weather.value,
            environment.lighting.value
        )
        if environment_id in self._by_conditions[conditions_key]:
            self._by_conditions[conditions_key].remove(environment_id)

        # Remove from active index if it was active
        if self._active_by_location.get(location_key) == environment_id:
            del self._active_by_location[location_key]

        if environment_id in self._by_tenant[tenant_id]:
            self._by_tenant[tenant_id].remove(environment_id)

        del self._environments[key]
        return True

    def exists(self, tenant_id: TenantId, location_id: EntityId, name: str) -> bool:
        return (tenant_id, location_id, name) in self._names


class InMemoryTextureRepository:
    """
    In-memory implementation of Texture repository.
    """

    def __init__(self):
        self._textures: Dict[Tuple[TenantId, EntityId], Texture] = {}
        self._names: Dict[Tuple[TenantId, str], EntityId] = {}
        self._by_world: Dict[TenantId, List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, texture: Texture) -> Texture:
        if texture.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            texture = texture.__class__(
                id=new_id,
                tenant_id=texture.tenant_id,
                world_id=texture.world_id,
                name=texture.name,
                path=texture.path,
                texture_type=texture.texture_type,
                description=texture.description,
                file_size=texture.file_size,
                dimensions=texture.dimensions,
                color_space=texture.color_space,
                created_at=texture.created_at,
                updated_at=texture.updated_at,
                version=texture.version,
            )
        
        key = (texture.tenant_id, texture.id)
        name_key = (texture.tenant_id, texture.name)
        
        if name_key in self._names and self._names[name_key] != texture.id:
            raise DuplicateEntity(f"Texture with name '{texture.name}' already exists")
        
        self._textures[key] = texture
        self._names[name_key] = texture.id
        if texture.id not in self._by_world[texture.tenant_id]:
            self._by_world[texture.tenant_id].append(texture.id)
        
        return texture

    def get_by_id(self, tenant_id: TenantId, texture_id: EntityId) -> Optional[Texture]:
        return self._textures.get((tenant_id, texture_id))

    def list_by_world(self, tenant_id: TenantId, limit: int = 100, offset: int = 0) -> List[Texture]:
        texture_ids = self._by_world.get(tenant_id, [])[offset:offset + limit]
        return [self._textures[(tenant_id, tid)] for tid in texture_ids if (tenant_id, tid) in self._textures]

    def delete(self, tenant_id: TenantId, texture_id: EntityId) -> bool:
        key = (tenant_id, texture_id)
        if key not in self._textures:
            return False
        
        texture = self._textures[key]
        name_key = (tenant_id, texture.name)
        
        del self._textures[key]
        if name_key in self._names:
            del self._names[name_key]
        if texture_id in self._by_world[tenant_id]:
            self._by_world[tenant_id].remove(texture_id)
        
        return True


class InMemoryModel3DRepository:
    """
    In-memory implementation of 3D Model repository.
    """

    def __init__(self):
        self._models: Dict[Tuple[TenantId, EntityId], Model3D] = {}
        self._names: Dict[Tuple[TenantId, str], EntityId] = {}
        self._by_world: Dict[TenantId, List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, model: Model3D) -> Model3D:
        if model.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            model = model.__class__(
                id=new_id,
                tenant_id=model.tenant_id,
                world_id=model.world_id,
                name=model.name,
                path=model.path,
                model_type=model.model_type,
                description=model.description,
                file_size=model.file_size,
                poly_count=model.poly_count,
                dimensions=model.dimensions,
                textures=model.textures,
                animations=model.animations,
                created_at=model.created_at,
                updated_at=model.updated_at,
                version=model.version,
            )
        
        key = (model.tenant_id, model.id)
        name_key = (model.tenant_id, model.name)
        
        if name_key in self._names and self._names[name_key] != model.id:
            raise DuplicateEntity(f"3D Model with name '{model.name}' already exists")
        
        self._models[key] = model
        self._names[name_key] = model.id
        if model.id not in self._by_world[model.tenant_id]:
            self._by_world[model.tenant_id].append(model.id)
        
        return model

    def get_by_id(self, tenant_id: TenantId, model_id: EntityId) -> Optional[Model3D]:
        return self._models.get((tenant_id, model_id))

    def list_by_world(self, tenant_id: TenantId, limit: int = 100, offset: int = 0) -> List[Model3D]:
        model_ids = self._by_world.get(tenant_id, [])[offset:offset + limit]
        return [self._models[(tenant_id, mid)] for mid in model_ids if (tenant_id, mid) in self._models]

    def delete(self, tenant_id: TenantId, model_id: EntityId) -> bool:
        key = (tenant_id, model_id)
        if key not in self._models:
            return False
        
        model = self._models[key]
        name_key = (tenant_id, model.name)
        
        del self._models[key]
        if name_key in self._names:
            del self._names[name_key]
        if model_id in self._by_world[tenant_id]:
            self._by_world[tenant_id].remove(model_id)
        
        return True