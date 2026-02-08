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
from src.domain.repositories.choice_repository import IChoiceRepository
from src.domain.repositories.flowchart_repository import IFlowchartRepository
from src.domain.repositories.handout_repository import IHandoutRepository
from src.domain.repositories.image_repository import IImageRepository
from src.domain.repositories.inspiration_repository import IInspirationRepository
from src.domain.repositories.map_repository import IMapRepository
from src.domain.repositories.tokenboard_repository import ITokenboardRepository
from src.domain.value_objects.common import (
    TenantId, EntityId, WorldName, CharacterName, TimeOfDay, Weather, Lighting
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


from src.domain.entities.tag import Tag
from src.domain.repositories.tag_repository import ITagRepository
from src.domain.entities.note import Note
from src.domain.repositories.note_repository import INoteRepository
from src.domain.entities.template import Template
from src.domain.repositories.template_repository import ITemplateRepository


class InMemoryTagRepository(ITagRepository):
    """In-memory implementation of Tag repository for testing."""

    def __init__(self):
        self._tags: Dict[Tuple[TenantId, EntityId], Tag] = {}
        self._names: Dict[Tuple[TenantId, EntityId, str, str], EntityId] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, tag: Tag) -> Tag:
        if tag.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(tag, 'id', new_id)

        key = (tag.tenant_id, tag.id)
        name_key = (tag.tenant_id, tag.world_id, tag.name.value, tag.tag_type.value)

        if name_key in self._names and self._names[name_key] != tag.id:
            raise DuplicateEntity(f"Tag with name '{tag.name}' already exists in this world")

        self._tags[key] = tag
        self._names[name_key] = tag.id

        world_key = (tag.tenant_id, tag.world_id)
        if tag.id not in self._by_world[world_key]:
            self._by_world[world_key].append(tag.id)

        return tag

    def find_by_id(self, tenant_id: TenantId, tag_id: EntityId) -> Optional[Tag]:
        return self._tags.get((tenant_id, tag_id))

    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: "TagName") -> Optional[Tag]:
        for key, tag_id in self._names.items():
            if key[0] == tenant_id and key[1] == world_id and key[2] == name.value:
                return self._tags.get((tenant_id, tag_id))
        return None

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Tag]:
        world_key = (tenant_id, world_id)
        tag_ids = self._by_world.get(world_key, [])
        tags = []
        for tag_id in tag_ids[offset:offset + limit]:
            tag = self._tags.get((tenant_id, tag_id))
            if tag:
                tags.append(tag)
        return tags

    def list_by_type(self, tenant_id: TenantId, world_id: EntityId, tag_type: "TagType", limit: int = 50, offset: int = 0) -> List[Tag]:
        all_tags = self.list_by_world(tenant_id, world_id)
        return [t for t in all_tags if t.tag_type.value == tag_type.value][offset:offset + limit]

    def delete(self, tenant_id: TenantId, tag_id: EntityId) -> bool:
        key = (tenant_id, tag_id)
        if key not in self._tags:
            return False

        tag = self._tags[key]
        name_key = (tag.tenant_id, tag.world_id, tag.name.value, tag.tag_type.value)

        if name_key in self._names:
            del self._names[name_key]

        world_key = (tag.tenant_id, tag.world_id)
        if tag_id in self._by_world[world_key]:
            self._by_world[world_key].remove(tag_id)

        del self._tags[key]
        return True

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: "TagName", tag_type: "TagType") -> bool:
        name_key = (tenant_id, world_id, name.value, tag_type.value)
        return name_key in self._names


class InMemoryNoteRepository(INoteRepository):
    """In-memory implementation of Note repository for testing."""

    def __init__(self):
        self._notes: Dict[Tuple[TenantId, EntityId], Note] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, note: Note) -> Note:
        if note.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(note, 'id', new_id)

        key = (note.tenant_id, note.id)
        self._notes[key] = note

        world_key = (note.tenant_id, note.world_id)
        if note.id not in self._by_world[world_key]:
            self._by_world[world_key].append(note.id)

        return note

    def find_by_id(self, tenant_id: TenantId, note_id: EntityId) -> Optional[Note]:
        return self._notes.get((tenant_id, note_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Note]:
        world_key = (tenant_id, world_id)
        note_ids = self._by_world.get(world_key, [])
        notes = []
        for note_id in note_ids[offset:offset + limit]:
            note = self._notes.get((tenant_id, note_id))
            if note:
                notes.append(note)
        return notes

    def list_pinned(self, tenant_id: TenantId, world_id: EntityId, limit: int = 20, offset: int = 0) -> List[Note]:
        all_notes = self.list_by_world(tenant_id, world_id)
        return [n for n in all_notes if n.is_pinned][offset:offset + limit]

    def search_by_content(self, tenant_id: TenantId, search_term: str, limit: int = 20) -> List[Note]:
        results = []
        for note in self._notes.values():
            if note.tenant_id == tenant_id:
                if search_term.lower() in note.content.lower() or search_term.lower() in note.title.lower():
                    results.append(note)
                    if len(results) >= limit:
                        break
        return results

    def delete(self, tenant_id: TenantId, note_id: EntityId) -> bool:
        key = (tenant_id, note_id)
        if key not in self._notes:
            return False

        note = self._notes[key]
        world_key = (note.tenant_id, note.world_id)
        if note_id in self._by_world[world_key]:
            self._by_world[world_key].remove(note_id)

        del self._notes[key]
        return True


class InMemoryTemplateRepository(ITemplateRepository):
    """In-memory implementation of Template repository for testing."""

    def __init__(self):
        self._templates: Dict[Tuple[TenantId, EntityId], Template] = {}
        self._names: Dict[Tuple[TenantId, EntityId, str], EntityId] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, template: Template) -> Template:
        if template.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(template, 'id', new_id)

        key = (template.tenant_id, template.id)
        name_key = (template.tenant_id, template.world_id, template.name.value)

        if name_key in self._names and self._names[name_key] != template.id:
            raise DuplicateEntity(f"Template with name '{template.name}' already exists in this world")

        self._templates[key] = template
        self._names[name_key] = template.id

        world_key = (template.tenant_id, template.world_id)
        if template.id not in self._by_world[world_key]:
            self._by_world[world_key].append(template.id)

        return template

    def find_by_id(self, tenant_id: TenantId, template_id: EntityId) -> Optional[Template]:
        return self._templates.get((tenant_id, template_id))

    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: "TemplateName") -> Optional[Template]:
        template_id = self._names.get((tenant_id, world_id, name.value))
        if template_id:
            return self._templates.get((tenant_id, template_id))
        return None

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Template]:
        world_key = (tenant_id, world_id)
        template_ids = self._by_world.get(world_key, [])
        templates = []
        for template_id in template_ids[offset:offset + limit]:
            template = self._templates.get((tenant_id, template_id))
            if template:
                templates.append(template)
        return templates

    def list_by_type(self, tenant_id: TenantId, world_id: EntityId, template_type: "TemplateType", limit: int = 50, offset: int = 0) -> List[Template]:
        all_templates = self.list_by_world(tenant_id, world_id)
        return [t for t in all_templates if t.template_type.value == template_type.value][offset:offset + limit]

    def list_runes(self, tenant_id: TenantId, parent_template_id: EntityId, limit: int = 50, offset: int = 0) -> List[Template]:
        all_templates = [t for t in self._templates.values() if t.tenant_id == tenant_id]
        return [t for t in all_templates if t.parent_template_id == parent_template_id][offset:offset + limit]

    def delete(self, tenant_id: TenantId, template_id: EntityId) -> bool:
        key = (tenant_id, template_id)
        if key not in self._templates:
            return False

        template = self._templates[key]
        name_key = (template.tenant_id, template.world_id, template.name.value)

        if name_key in self._names:
            del self._names[name_key]

        world_key = (template.tenant_id, template.world_id)
        if template_id in self._by_world[world_key]:
            self._by_world[world_key].remove(template_id)

        del self._templates[key]
        return True

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: "TemplateName") -> bool:
        name_key = (tenant_id, world_id, name.value)
        return name_key in self._names


class InMemoryChoiceRepository(IChoiceRepository):
    """In-memory implementation of Choice repository for testing."""

    def __init__(self):
        from src.domain.repositories.choice_repository import IChoiceRepository
        self._choices: Dict[Tuple[TenantId, EntityId], object] = {}
        self._by_story: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, choice: object) -> object:
        if choice.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(choice, 'id', new_id)

        key = (choice.tenant_id, choice.id)
        self._choices[key] = choice

        story_key = (choice.tenant_id, choice.story_id) if hasattr(choice, 'story_id') else None
        if story_key:
            if choice.id not in self._by_story[story_key]:
                self._by_story[story_key].append(choice.id)

        world_key = (choice.tenant_id, choice.world_id)
        if choice.id not in self._by_world[world_key]:
            self._by_world[world_key].append(choice.id)

        return choice

    def find_by_id(self, tenant_id: TenantId, choice_id: EntityId) -> Optional[object]:
        return self._choices.get((tenant_id, choice_id))

    def list_by_story(self, tenant_id: TenantId, story_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        story_key = (tenant_id, story_id)
        choice_ids = self._by_story.get(story_key, [])
        choices = []
        for choice_id in choice_ids[offset:offset + limit]:
            choice = self._choices.get((tenant_id, choice_id))
            if choice:
                choices.append(choice)
        return choices

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        world_key = (tenant_id, world_id)
        choice_ids = self._by_world.get(world_key, [])
        choices = []
        for choice_id in choice_ids[offset:offset + limit]:
            choice = self._choices.get((tenant_id, choice_id))
            if choice:
                choices.append(choice)
        return choices

    def list_by_type(self, tenant_id: TenantId, world_id: EntityId, choice_type: str, limit: int = 50, offset: int = 0) -> List[object]:
        all_choices = self.list_by_world(tenant_id, world_id)
        return [c for c in all_choices if getattr(c, 'choice_type', None) == choice_type][offset:offset + limit]

    def delete(self, tenant_id: TenantId, choice_id: EntityId) -> bool:
        key = (tenant_id, choice_id)
        if key not in self._choices:
            return False

        choice = self._choices[key]

        story_key = (choice.tenant_id, choice.story_id) if hasattr(choice, 'story_id') else None
        if story_key and choice_id in self._by_story[story_key]:
            self._by_story[story_key].remove(choice_id)

        world_key = (choice.tenant_id, choice.world_id)
        if choice_id in self._by_world[world_key]:
            self._by_world[world_key].remove(choice_id)

        del self._choices[key]
        return True


class InMemoryFlowchartRepository:
    """In-memory implementation of Flowchart repository for testing."""

    def __init__(self):
        self._flowcharts: Dict[Tuple[TenantId, EntityId], object] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._by_story: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, flowchart: object) -> object:
        if flowchart.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(flowchart, 'id', new_id)

        key = (flowchart.tenant_id, flowchart.id)
        self._flowcharts[key] = flowchart

        story_key = (flowchart.tenant_id, flowchart.story_id) if hasattr(flowchart, 'story_id') else None
        if story_key:
            if flowchart.id not in self._by_story[story_key]:
                self._by_story[story_key].append(flowchart.id)

        world_key = (flowchart.tenant_id, flowchart.world_id)
        if flowchart.id not in self._by_world[world_key]:
            self._by_world[world_key].append(flowchart.id)

        return flowchart

    def find_by_id(self, tenant_id: TenantId, flowchart_id: EntityId) -> Optional[object]:
        return self._flowcharts.get((tenant_id, flowchart_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        world_key = (tenant_id, world_id)
        flowchart_ids = self._by_world.get(world_key, [])
        flowcharts = []
        for flowchart_id in flowchart_ids[offset:offset + limit]:
            flowchart = self._flowcharts.get((tenant_id, flowchart_id))
            if flowchart:
                flowcharts.append(flowchart)
        return flowcharts

    def list_by_story(self, tenant_id: TenantId, story_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        story_key = (tenant_id, story_id)
        flowchart_ids = self._by_story.get(story_key, [])
        flowcharts = []
        for flowchart_id in flowchart_ids[offset:offset + limit]:
            flowchart = self._flowcharts.get((tenant_id, flowchart_id))
            if flowchart:
                flowcharts.append(flowchart)
        return flowcharts

    def find_active(self, tenant_id: TenantId, world_id: EntityId) -> Optional[object]:
        all_flowcharts = self.list_by_world(tenant_id, world_id)
        for flowchart in all_flowcharts:
            if getattr(flowchart, 'is_active', False):
                return flowchart
        return None

    def delete(self, tenant_id: TenantId, flowchart_id: EntityId) -> bool:
        key = (tenant_id, flowchart_id)
        if key not in self._flowcharts:
            return False

        flowchart = self._flowcharts[key]

        story_key = (flowchart.tenant_id, flowchart.story_id) if hasattr(flowchart, 'story_id') else None
        if story_key and flowchart_id in self._by_story[story_key]:
            self._by_story[story_key].remove(flowchart_id)

        world_key = (flowchart.tenant_id, flowchart.world_id)
        if flowchart_id in self._by_world[world_key]:
            self._by_world[world_key].remove(flowchart_id)

        del self._flowcharts[key]
        return True


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


class InMemoryImageRepository(IImageRepository):
    """In-memory implementation of Image repository for testing."""

    def __init__(self):
        self._images: Dict[Tuple[TenantId, EntityId], object] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._paths: Dict[Tuple[TenantId, EntityId, str], EntityId] = {}
        self._next_id = 1

    def save(self, image: object) -> object:
        if image.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(image, 'id', new_id)

        key = (image.tenant_id, image.id)
        self._images[key] = image

        path_key = (image.tenant_id, image.world_id, image.path)
        self._paths[path_key] = image.id

        world_key = (image.tenant_id, image.world_id)
        if image.id not in self._by_world[world_key]:
            self._by_world[world_key].append(image.id)

        return image

    def find_by_id(self, tenant_id: TenantId, image_id: EntityId) -> Optional[object]:
        return self._images.get((tenant_id, image_id))

    def find_by_path(self, tenant_id: TenantId, world_id: EntityId, path: str) -> Optional[object]:
        path_key = (tenant_id, world_id, path)
        image_id = self._paths.get(path_key)
        if image_id:
            return self._images.get((tenant_id, image_id))
        return None

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        world_key = (tenant_id, world_id)
        image_ids = self._by_world.get(world_key, [])
        images = []
        for image_id in image_ids[offset:offset + limit]:
            image = self._images.get((tenant_id, image_id))
            if image:
                images.append(image)
        return images

    def delete(self, tenant_id: TenantId, image_id: EntityId) -> bool:
        key = (tenant_id, image_id)
        if key not in self._images:
            return False

        image = self._images[key]
        path_key = (image.tenant_id, image.world_id, image.path)
        if path_key in self._paths:
            del self._paths[path_key]

        world_key = (image.tenant_id, image.world_id)
        if image_id in self._by_world[world_key]:
            self._by_world[world_key].remove(image_id)

        del self._images[key]
        return True

    def exists(self, tenant_id: TenantId, world_id: EntityId, path: str) -> bool:
        path_key = (tenant_id, world_id, path)
        return path_key in self._paths


class InMemoryInspirationRepository:
    """In-memory implementation of Inspiration repository for testing."""

    def __init__(self):
        self._inspirations: Dict[Tuple[TenantId, EntityId], object] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, inspiration: object) -> object:
        if inspiration.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(inspiration, 'id', new_id)

        key = (inspiration.tenant_id, inspiration.id)
        self._inspirations[key] = inspiration

        world_key = (inspiration.tenant_id, inspiration.world_id)
        if inspiration.id not in self._by_world[world_key]:
            self._by_world[world_key].append(inspiration.id)

        return inspiration

    def find_by_id(self, tenant_id: TenantId, inspiration_id: EntityId) -> Optional[object]:
        return self._inspirations.get((tenant_id, inspiration_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        world_key = (tenant_id, world_id)
        inspiration_ids = self._by_world.get(world_key, [])
        inspirations = []
        for inspiration_id in inspiration_ids[offset:offset + limit]:
            inspiration = self._inspirations.get((tenant_id, inspiration_id))
            if inspiration:
                inspirations.append(inspiration)
        return inspirations

    def list_by_category(self, tenant_id: TenantId, world_id: EntityId, category: str, limit: int = 50, offset: int = 0) -> List[object]:
        all_inspirations = self.list_by_world(tenant_id, world_id)
        return [i for i in all_inspirations if getattr(i, 'category', None) == category][offset:offset + limit]

    def list_unused(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        all_inspirations = self.list_by_world(tenant_id, world_id)
        return [i for i in all_inspirations if not getattr(i, 'is_used', False)][offset:offset + limit]

    def search_by_content(self, tenant_id: TenantId, search_term: str, limit: int = 20) -> List[object]:
        results = []
        for inspiration in self._inspirations.values():
            if inspiration.tenant_id == tenant_id:
                content = getattr(inspiration, 'content', '')
                if search_term.lower() in content.lower():
                    results.append(inspiration)
                    if len(results) >= limit:
                        break
        return results

    def delete(self, tenant_id: TenantId, inspiration_id: EntityId) -> bool:
        key = (tenant_id, inspiration_id)
        if key not in self._inspirations:
            return False

        inspiration = self._inspirations[key]
        world_key = (inspiration.tenant_id, inspiration.world_id)
        if inspiration_id in self._by_world[world_key]:
            self._by_world[world_key].remove(inspiration_id)

        del self._inspirations[key]
        return True


class InMemoryMapRepository:
    """In-memory implementation of Map repository for testing."""

    def __init__(self):
        self._maps: Dict[Tuple[TenantId, EntityId], object] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, map_obj: object) -> object:
        if map_obj.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(map_obj, 'id', new_id)

        key = (map_obj.tenant_id, map_obj.id)
        self._maps[key] = map_obj

        world_key = (map_obj.tenant_id, map_obj.world_id)
        if map_obj.id not in self._by_world[world_key]:
            self._by_world[world_key].append(map_obj.id)

        return map_obj

    def find_by_id(self, tenant_id: TenantId, map_id: EntityId) -> Optional[object]:
        return self._maps.get((tenant_id, map_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        world_key = (tenant_id, world_id)
        map_ids = self._by_world.get(world_key, [])
        maps = []
        for map_id in map_ids[offset:offset + limit]:
            map_obj = self._maps.get((tenant_id, map_id))
            if map_obj:
                maps.append(map_obj)
        return maps

    def list_interactive(self, tenant_id: TenantId, world_id: EntityId, limit: int = 20, offset: int = 0) -> List[object]:
        all_maps = self.list_by_world(tenant_id, world_id)
        return [m for m in all_maps if getattr(m, 'is_interactive', False)][offset:offset + limit]

    def delete(self, tenant_id: TenantId, map_id: EntityId) -> bool:
        key = (tenant_id, map_id)
        if key not in self._maps:
            return False

        map_obj = self._maps[key]
        world_key = (map_obj.tenant_id, map_obj.world_id)
        if map_id in self._by_world[world_key]:
            self._by_world[world_key].remove(map_id)

        del self._maps[key]
        return True


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


# Import missing interfaces
from src.domain.repositories.choice_repository import IChoiceRepository
from src.domain.repositories.handout_repository import IHandoutRepository
from src.domain.repositories.image_repository import IImageRepository
from src.domain.repositories.inspiration_repository import IInspirationRepository
from src.domain.repositories.map_repository import IMapRepository
from src.domain.repositories.tokenboard_repository import ITokenboardRepository

class InMemoryQuestChainRepository:
    """In-memory implementation of QuestChain repository."""
    def __init__(self):
        from typing import Dict, Optional, Tuple
        from collections import defaultdict
        from src.domain.value_objects.common import TenantId, EntityId
        
        self._quest_chains: Dict[Tuple[TenantId, EntityId], object] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], list] = defaultdict(list)
        self._next_id = 1

    def save(self, quest_chain):
        if quest_chain.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(quest_chain, 'id', new_id)
        self._quest_chains[(quest_chain.tenant_id, quest_chain.id)] = quest_chain
        world_key = (quest_chain.tenant_id, quest_chain.world_id) if hasattr(quest_chain, 'world_id') else None
        if world_key:
            if quest_chain.id not in self._by_world[world_key]:
                self._by_world[world_key].append(quest_chain.id)
        return quest_chain

    def find_by_id(self, tenant_id, entity_id):
        return self._quest_chains.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        world_key = (tenant_id, world_id)
        return [self._quest_chains[(tenant_id, qid)] for qid in self._by_world.get(world_key, [])[offset:offset+limit]]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._quest_chains:
            qc = self._quest_chains[key]
            world_key = (qc.tenant_id, qc.world_id) if hasattr(qc, 'world_id') else None
            if world_key and entity_id in self._by_world[world_key]:
                self._by_world[world_key].remove(entity_id)
            del self._quest_chains[key]
            return True
        return False


class InMemoryQuestNodeRepository:
    """In-memory implementation of QuestNode repository."""
    def __init__(self):
        self._quest_nodes = {}
        self._next_id = 1

    def save(self, quest_node):
        if quest_node.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(quest_node, 'id', new_id)
        self._quest_nodes[(quest_node.tenant_id, quest_node.id)] = quest_node
        return quest_node

    def find_by_id(self, tenant_id, entity_id):
        return self._quest_nodes.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [qn for qn in self._quest_nodes.values() if qn.tenant_id == tenant_id and qn.world_id == world_id][offset:offset+limit]]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._quest_nodes:
            del self._quest_nodes[key]
            return True
        return False


class InMemoryQuestPrerequisiteRepository:
    """In-memory implementation of QuestPrerequisite repository."""
    def __init__(self):
        self._prerequisites = {}
        self._next_id = 1

    def save(self, prereq):
        if prereq.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(prereq, 'id', new_id)
        self._prerequisites[(prereq.tenant_id, prereq.id)] = prereq
        return prereq

    def find_by_id(self, tenant_id, entity_id):
        return self._prerequisites.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [p for p in self._prerequisites.values() if p.tenant_id == tenant_id and p.world_id == world_id][offset:offset+limit]]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._prerequisites:
            del self._prerequisites[key]
            return True
        return False


class InMemoryQuestObjectiveRepository:
    """In-memory implementation of QuestObjective repository."""
    def __init__(self):
        self._objectives = {}
        self._next_id = 1

    def save(self, objective):
        if objective.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(objective, 'id', new_id)
        self._objectives[(objective.tenant_id, objective.id)] = objective
        return objective

    def find_by_id(self, tenant_id, entity_id):
        return self._objectives.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [o for o in self._objectives.values() if o.tenant_id == tenant_id and o.world_id == world_id][offset:offset+limit]]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._objectives:
            del self._objectives[key]
            return True
        return False


class InMemoryQuestTrackerRepository:
    """In-memory implementation of QuestTracker repository."""
    def __init__(self):
        self._trackers = {}
        self._next_id = 1

    def save(self, tracker):
        if tracker.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(tracker, 'id', new_id)
        self._trackers[(tracker.tenant_id, tracker.id)] = tracker
        return tracker

    def find_by_id(self, tenant_id, entity_id):
        return self._trackers.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._trackers.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._trackers:
            del self._trackers[key]
            return True
        return False


class InMemoryQuestGiverRepository:
    """In-memory implementation of QuestGiver repository."""
    def __init__(self):
        self._givers = {}
        self._next_id = 1

    def save(self, giver):
        if giver.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(giver, 'id', new_id)
        self._givers[(giver.tenant_id, giver.id)] = giver
        return giver

    def find_by_id(self, tenant_id, entity_id):
        return self._givers.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [g for g in self._givers.values() if g.tenant_id == tenant_id and g.world_id == world_id][offset:offset+limit]]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._givers:
            del self._givers[key]
            return True
        return False


class InMemoryQuestRewardRepository:
    """In-memory implementation of QuestReward repository."""
    def __init__(self):
        self._rewards = {}
        self._next_id = 1

    def save(self, reward):
        if reward.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(reward, 'id', new_id)
        self._rewards[(reward.tenant_id, reward.id)] = reward
        return reward

    def find_by_id(self, tenant_id, entity_id):
        return self._rewards.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._rewards.values() if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._rewards:
            del self._rewards[key]
            return True
        return False


class InMemoryQuestRewardTierRepository:
    """In-memory implementation of QuestRewardTier repository."""
    def __init__(self):
        self._tiers = {}
        self._next_id = 1

    def save(self, tier):
        if tier.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(tier, 'id', new_id)
        self._tiers[(tier.tenant_id, tier.id)] = tier
        return tier

    def find_by_id(self, tenant_id, entity_id):
        return self._tiers.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._tiers.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._tiers:
            del self._tiers[key]
            return True
        return False

# Progression repositories
class InMemorySkillRepository:
    def __init__(self):
        self._skills = {}
        self._next_id = 1
    def save(self, skill):
        if skill.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(skill, 'id', new_id)
        self._skills[(skill.tenant_id, skill.id)] = skill
        return skill
    def find_by_id(self, tenant_id, skill_id):
        return self._skills.get((tenant_id, skill_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._skills.values() if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, skill_id):
        if (tenant_id, skill_id) in self._skills:
            del self._skills[(tenant_id, skill_id)]
            return True
        return False

class InMemoryPerkRepository:
    def __init__(self):
        self._perks = {}
        self._next_id = 1
    def save(self, perk):
        if perk.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(perk, 'id', new_id)
        self._perks[(perk.tenant_id, perk.id)] = perk
        return perk
    def find_by_id(self, tenant_id, perk_id):
        return self._perks.get((tenant_id, perk_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [p for p in self._perks.values() if p.tenant_id == tenant_id and p.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, perk_id):
        if (tenant_id, perk_id) in self._perks:
            del self._perks[(tenant_id, perk_id)]
            return True
        return False

class InMemoryTraitRepository:
    def __init__(self):
        self._traits = {}
        self._next_id = 1
    def save(self, trait):
        if trait.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(trait, 'id', new_id)
        self._traits[(trait.tenant_id, trait.id)] = trait
        return trait
    def find_by_id(self, tenant_id, trait_id):
        return self._traits.get((tenant_id, trait_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._traits.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, trait_id):
        if (tenant_id, trait_id) in self._traits:
            del self._traits[(tenant_id, trait_id)]
            return True
        return False

class InMemoryAttributeRepository:
    def __init__(self):
        self._attributes = {}
        self._next_id = 1
    def save(self, attribute):
        if attribute.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(attribute, 'id', new_id)
        self._attributes[(attribute.tenant_id, attribute.id)] = attribute
        return attribute
    def find_by_id(self, tenant_id, attribute_id):
        return self._attributes.get((tenant_id, attribute_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [a for a in self._attributes.values() if a.tenant_id == tenant_id and a.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, attribute_id):
        if (tenant_id, attribute_id) in self._attributes:
            del self._attributes[(tenant_id, attribute_id)]
            return True
        return False

class InMemoryExperienceRepository:
    def __init__(self):
        self._experiences = {}
        self._next_id = 1
    def save(self, experience):
        if experience.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(experience, 'id', new_id)
        self._experiences[(experience.tenant_id, experience.id)] = experience
        return experience
    def find_by_id(self, tenant_id, experience_id):
        return self._experiences.get((tenant_id, experience_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._experiences.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, experience_id):
        if (tenant_id, experience_id) in self._experiences:
            del self._experiences[(tenant_id, experience_id)]
            return True
        return False

class InMemoryLevelUpRepository:
    def __init__(self):
        self._level_ups = {}
        self._next_id = 1
    def save(self, level_up):
        if level_up.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(level_up, 'id', new_id)
        self._level_ups[(level_up.tenant_id, level_up.id)] = level_up
        return level_up
    def find_by_id(self, tenant_id, level_up_id):
        return self._level_ups.get((tenant_id, level_up_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [l for l in self._level_ups.values() if l.tenant_id == tenant_id and l.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, level_up_id):
        if (tenant_id, level_up_id) in self._level_ups:
            del self._level_ups[(tenant_id, level_up_id)]
            return True
        return False

class InMemoryTalentTreeRepository:
    def __init__(self):
        self._talent_trees = {}
        self._next_id = 1
    def save(self, talent_tree):
        if talent_tree.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(talent_tree, 'id', new_id)
        self._talent_trees[(talent_tree.tenant_id, talent_tree.id)] = talent_tree
        return talent_tree
    def find_by_id(self, tenant_id, talent_tree_id):
        return self._talent_trees.get((tenant_id, talent_tree_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._talent_trees.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, talent_tree_id):
        if (tenant_id, talent_tree_id) in self._talent_trees:
            del self._talent_trees[(tenant_id, talent_tree_id)]
            return True
        return False

class InMemoryMasteryRepository:
    def __init__(self):
        self._masteries = {}
        self._next_id = 1
    def save(self, mastery):
        if mastery.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(mastery, 'id', new_id)
        self._masteries[(mastery.tenant_id, mastery.id)] = mastery
        return mastery
    def find_by_id(self, tenant_id, mastery_id):
        return self._masteries.get((tenant_id, mastery_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [m for m in self._masteries.values() if m.tenant_id == tenant_id and m.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, mastery_id):
        if (tenant_id, mastery_id) in self._masteries:
            del self._masteries[(tenant_id, mastery_id)]
            return True
        return False

# Faction repositories
class InMemoryFactionHierarchyRepository:
    def __init__(self):
        self._hierarchies = {}
        self._next_id = 1
    def save(self, hierarchy):
        if hierarchy.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(hierarchy, 'id', new_id)
        self._hierarchies[(hierarchy.tenant_id, hierarchy.id)] = hierarchy
        return hierarchy
    def find_by_id(self, tenant_id, hierarchy_id):
        return self._hierarchies.get((tenant_id, hierarchy_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [h for h in self._hierarchies.values() if h.tenant_id == tenant_id and h.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, hierarchy_id):
        if (tenant_id, hierarchy_id) in self._hierarchies:
            del self._hierarchies[(tenant_id, hierarchy_id)]
            return True
        return False

class InMemoryFactionIdeologyRepository:
    def __init__(self):
        self._ideologies = {}
        self._next_id = 1
    def save(self, ideology):
        if ideology.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(ideology, 'id', new_id)
        self._ideologies[(ideology.tenant_id, ideology.id)] = ideology
        return ideology
    def find_by_id(self, tenant_id, ideology_id):
        return self._ideologies.get((tenant_id, ideology_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [i for i in self._ideologies.values() if i.tenant_id == tenant_id and i.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, ideology_id):
        if (tenant_id, ideology_id) in self._ideologies:
            del self._ideologies[(tenant_id, ideology_id)]
            return True
        return False

class InMemoryFactionLeaderRepository:
    def __init__(self):
        self._leaders = {}
        self._next_id = 1
    def save(self, leader):
        if leader.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(leader, 'id', new_id)
        self._leaders[(leader.tenant_id, leader.id)] = leader
        return leader
    def find_by_id(self, tenant_id, leader_id):
        return self._leaders.get((tenant_id, leader_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [l for l in self._leaders.values() if l.tenant_id == tenant_id and l.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, leader_id):
        if (tenant_id, leader_id) in self._leaders:
            del self._leaders[(tenant_id, leader_id)]
            return True
        return False

class InMemoryFactionMembershipRepository:
    def __init__(self):
        self._memberships = {}
        self._next_id = 1
    def save(self, membership):
        if membership.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(membership, 'id', new_id)
        self._memberships[(membership.tenant_id, membership.id)] = membership
        return membership
    def find_by_id(self, tenant_id, membership_id):
        return self._memberships.get((tenant_id, membership_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [m for m in self._memberships.values() if m.tenant_id == tenant_id and m.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, membership_id):
        if (tenant_id, membership_id) in self._memberships:
            del self._memberships[(tenant_id, membership_id)]
            return True
        return False

class InMemoryFactionResourceRepository:
    def __init__(self):
        self._resources = {}
        self._next_id = 1
    def save(self, resource):
        if resource.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(resource, 'id', new_id)
        self._resources[(resource.tenant_id, resource.id)] = resource
        return resource
    def find_by_id(self, tenant_id, resource_id):
        return self._resources.get((tenant_id, resource_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._resources.values() if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, resource_id):
        if (tenant_id, resource_id) in self._resources:
            del self._resources[(tenant_id, resource_id)]
            return True
        return False

class InMemoryFactionTerritoryRepository:
    def __init__(self):
        self._territories = {}
        self._next_id = 1
    def save(self, territory):
        if territory.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(territory, 'id', new_id)
        self._territories[(territory.tenant_id, territory.id)] = territory
        return territory
    def find_by_id(self, tenant_id, territory_id):
        return self._territories.get((tenant_id, territory_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._territories.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, territory_id):
        if (tenant_id, territory_id) in self._territories:
            del self._territories[(tenant_id, territory_id)]
            return True
        return False

# In-Memory implementations for remaining repositories


class InMemoryMiracleRepository:
    """In-memory implementation of Miracle repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCourtRepository:
    """In-memory implementation of Court repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryVoice_overRepository:
    """In-memory implementation of Voice_over repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryFestivalRepository:
    """In-memory implementation of Festival repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCataclysmRepository:
    """In-memory implementation of Cataclysm repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryProgression_stateRepository:
    """In-memory implementation of Progression_state repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryChapterRepository:
    """In-memory implementation of Chapter repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryNationRepository:
    """In-memory implementation of Nation repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryEvidenceRepository:
    """In-memory implementation of Evidence repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryImprovementRepository:
    """In-memory implementation of Improvement repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryLore_fragmentRepository:
    """In-memory implementation of Lore_fragment repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryFactionRepository:
    """In-memory implementation of Faction repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryConcertRepository:
    """In-memory implementation of Concert repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryAllianceRepository:
    """In-memory implementation of Alliance repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCinematicRepository:
    """In-memory implementation of Cinematic repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryDemandRepository:
    """In-memory implementation of Demand repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryDeus_ex_machinaRepository:
    """In-memory implementation of Deus_ex_machina repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySeasonRepository:
    """In-memory implementation of Season repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryFlash_forwardRepository:
    """In-memory implementation of Flash_forward repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryTalent_treeRepository:
    """In-memory implementation of Talent_tree repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryQuestRepository:
    """In-memory implementation of Quest repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryLegendary_weaponRepository:
    """In-memory implementation of Legendary_weapon repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryGlyphRepository:
    """In-memory implementation of Glyph repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryRelic_collectionRepository:
    """In-memory implementation of Relic_collection repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryArtifact_setRepository:
    """In-memory implementation of Artifact_set repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryDifficulty_curveRepository:
    """In-memory implementation of Difficulty_curve repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryRequirementRepository:
    """In-memory implementation of Requirement repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPlot_deviceRepository:
    """In-memory implementation of Plot_device repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryBannerRepository:
    """In-memory implementation of Banner repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryQuest_rewardRepository:
    """In-memory implementation of Quest_reward repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryJudgeRepository:
    """In-memory implementation of Judge repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryNightmareRepository:
    """In-memory implementation of Nightmare repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySecret_areaRepository:
    """In-memory implementation of Secret_area repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPactRepository:
    """In-memory implementation of Pact repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryWarRepository:
    """In-memory implementation of War repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryUser_scenarioRepository:
    """In-memory implementation of User_scenario repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryVisual_effectRepository:
    """In-memory implementation of Visual_effect repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryMaterialRepository:
    """In-memory implementation of Material repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySave_pointRepository:
    """In-memory implementation of Save_point repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPropagandaRepository:
    """In-memory implementation of Propaganda repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryLeaderboardRepository:
    """In-memory implementation of Leaderboard repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryEclipseRepository:
    """In-memory implementation of Eclipse repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryBalance_entitiesRepository:
    """In-memory implementation of Balance_entities repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPunishmentRepository:
    """In-memory implementation of Punishment repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryUndergroundRepository:
    """In-memory implementation of Underground repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryRadioRepository:
    """In-memory implementation of Radio repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryBestiary_entryRepository:
    """In-memory implementation of Bestiary_entry repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryOpen_world_zoneRepository:
    """In-memory implementation of Open_world_zone repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryRewardRepository:
    """In-memory implementation of Reward repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryDrop_rateRepository:
    """In-memory implementation of Drop_rate repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryMusic_themeRepository:
    """In-memory implementation of Music_theme repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryConstitutionRepository:
    """In-memory implementation of Constitution repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryDefenseRepository:
    """In-memory implementation of Defense repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryInvasionRepository:
    """In-memory implementation of Invasion repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryLoot_table_weightRepository:
    """In-memory implementation of Loot_table_weight repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryDiscoveryRepository:
    """In-memory implementation of Discovery repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryMountRepository:
    """In-memory implementation of Mount repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryWormholeRepository:
    """In-memory implementation of Wormhole repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPocket_dimensionRepository:
    """In-memory implementation of Pocket_dimension repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryEvent_chainRepository:
    """In-memory implementation of Event_chain repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPrologueRepository:
    """In-memory implementation of Prologue repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryFadeRepository:
    """In-memory implementation of Fade repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryAutosaveRepository:
    """In-memory implementation of Autosave repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySocial_mobilityRepository:
    """In-memory implementation of Social_mobility repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCharacter_profile_entryRepository:
    """In-memory implementation of Character_profile_entry repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryModel3dRepository:
    """In-memory implementation of Model3d repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySoundtrackRepository:
    """In-memory implementation of Soundtrack repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryInflationRepository:
    """In-memory implementation of Inflation repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryStar_systemRepository:
    """In-memory implementation of Star_system repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryQuarterRepository:
    """In-memory implementation of Quarter repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPurchaseRepository:
    """In-memory implementation of Purchase repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCharacter_relationshipRepository:
    """In-memory implementation of Character_relationship repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryGovernmentRepository:
    """In-memory implementation of Government repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCampaignRepository:
    """In-memory implementation of Campaign repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPityRepository:
    """In-memory implementation of Pity repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryTranslationRepository:
    """In-memory implementation of Translation repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryColor_paletteRepository:
    """In-memory implementation of Color_palette repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySeasonal_eventRepository:
    """In-memory implementation of Seasonal_event repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryArmyRepository:
    """In-memory implementation of Army repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryModRepository:
    """In-memory implementation of Mod repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryBlueprintRepository:
    """In-memory implementation of Blueprint repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryQuest_trackerRepository:
    """In-memory implementation of Quest_tracker repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryRankRepository:
    """In-memory implementation of Rank repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCelebrationRepository:
    """In-memory implementation of Celebration repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCurseRepository:
    """In-memory implementation of Curse repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryHub_areaRepository:
    """In-memory implementation of Hub_area repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryRevolutionRepository:
    """In-memory implementation of Revolution repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryFaction_resourceRepository:
    """In-memory implementation of Faction_resource repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryTreatyRepository:
    """In-memory implementation of Treaty repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryAirshipRepository:
    """In-memory implementation of Airship repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCultRepository:
    """In-memory implementation of Cult repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryEnchantmentRepository:
    """In-memory implementation of Enchantment repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryInstanceRepository:
    """In-memory implementation of Instance repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryAcademyRepository:
    """In-memory implementation of Academy repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySilenceRepository:
    """In-memory implementation of Silence repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryLore_axiomsRepository:
    """In-memory implementation of Lore_axioms repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySupplyRepository:
    """In-memory implementation of Supply repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryFaction_membershipRepository:
    """In-memory implementation of Faction_membership repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryMusic_stateRepository:
    """In-memory implementation of Music_state repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryBlessingRepository:
    """In-memory implementation of Blessing repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPrototypeRepository:
    """In-memory implementation of Prototype repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryFaction_ideologyRepository:
    """In-memory implementation of Faction_ideology repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryKarmaRepository:
    """In-memory implementation of Karma repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCharacter_variantRepository:
    """In-memory implementation of Character_variant repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryLegal_systemRepository:
    """In-memory implementation of Legal_system repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryQuest_objectiveRepository:
    """In-memory implementation of Quest_objective repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPlot_branchRepository:
    """In-memory implementation of Plot_branch repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryWaypointRepository:
    """In-memory implementation of Waypoint repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryProgression_eventRepository:
    """In-memory implementation of Progression_event repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryNewspaperRepository:
    """In-memory implementation of Newspaper repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryWardRepository:
    """In-memory implementation of Ward repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryMemoryRepository:
    """In-memory implementation of Memory repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPullRepository:
    """In-memory implementation of Pull repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryBranch_pointRepository:
    """In-memory implementation of Branch_point repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryWorld_eventRepository:
    """In-memory implementation of World_event repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySectRepository:
    """In-memory implementation of Sect repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryEmpireRepository:
    """In-memory implementation of Empire repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryQuest_chainRepository:
    """In-memory implementation of Quest_chain repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryRuneRepository:
    """In-memory implementation of Rune repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryHolidayRepository:
    """In-memory implementation of Holiday repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryShaderRepository:
    """In-memory implementation of Shader repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryTitleRepository:
    """In-memory implementation of Title repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPlayer_metricRepository:
    """In-memory implementation of Player_metric repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryEpilogueRepository:
    """In-memory implementation of Epilogue repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryMysteryRepository:
    """In-memory implementation of Mystery repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryWeather_patternRepository:
    """In-memory implementation of Weather_pattern repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryActRepository:
    """In-memory implementation of Act repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryEpisodeRepository:
    """In-memory implementation of Episode repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryTelevisionRepository:
    """In-memory implementation of Television repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySiege_engineRepository:
    """In-memory implementation of Siege_engine repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCustom_mapRepository:
    """In-memory implementation of Custom_map repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryThemeRepository:
    """In-memory implementation of Theme repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCrafting_recipeRepository:
    """In-memory implementation of Crafting_recipe repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySocial_classRepository:
    """In-memory implementation of Social_class repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryFaction_leaderRepository:
    """In-memory implementation of Faction_leader repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryRiddleRepository:
    """In-memory implementation of Riddle repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryFast_travel_pointRepository:
    """In-memory implementation of Fast_travel_point repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryMuseumRepository:
    """In-memory implementation of Museum repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryFamiliarRepository:
    """In-memory implementation of Familiar repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryEra_transitionRepository:
    """In-memory implementation of Era_transition repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryTariffRepository:
    """In-memory implementation of Tariff repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryQuest_nodeRepository:
    """In-memory implementation of Quest_node repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryDreamRepository:
    """In-memory implementation of Dream repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryHoly_siteRepository:
    """In-memory implementation of Holy_site repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryInventoryRepository:
    """In-memory implementation of Inventory repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryAffinityRepository:
    """In-memory implementation of Affinity repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryAlternate_realityRepository:
    """In-memory implementation of Alternate_reality repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryMount_equipmentRepository:
    """In-memory implementation of Mount_equipment repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySound_effectRepository:
    """In-memory implementation of Sound_effect repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryInternetRepository:
    """In-memory implementation of Internet repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryTime_periodRepository:
    """In-memory implementation of Time_period repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPuzzleRepository:
    """In-memory implementation of Puzzle repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryMotion_captureRepository:
    """In-memory implementation of Motion_capture repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryFortificationRepository:
    """In-memory implementation of Fortification repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryVoice_actorRepository:
    """In-memory implementation of Voice_actor repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryDimensionRepository:
    """In-memory implementation of Dimension repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryMusic_controlRepository:
    """In-memory implementation of Music_control repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryDubbingRepository:
    """In-memory implementation of Dubbing repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryHidden_pathRepository:
    """In-memory implementation of Hidden_path repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryFleetRepository:
    """In-memory implementation of Fleet repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySocial_mediaRepository:
    """In-memory implementation of Social_media repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryBarterRepository:
    """In-memory implementation of Barter repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCalendarRepository:
    """In-memory implementation of Calendar repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySolsticeRepository:
    """In-memory implementation of Solstice repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySchoolRepository:
    """In-memory implementation of School repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySlumsRepository:
    """In-memory implementation of Slums repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryDisasterRepository:
    """In-memory implementation of Disaster repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryMotifRepository:
    """In-memory implementation of Motif repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySpawn_pointRepository:
    """In-memory implementation of Spawn_point repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryWorkshop_entryRepository:
    """In-memory implementation of Workshop_entry repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryMoral_choiceRepository:
    """In-memory implementation of Moral_choice repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryVoice_lineRepository:
    """In-memory implementation of Voice_line repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryFamineRepository:
    """In-memory implementation of Famine repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySession_dataRepository:
    """In-memory implementation of Session_data repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPatentRepository:
    """In-memory implementation of Patent repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryArchiveRepository:
    """In-memory implementation of Archive repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryConversion_rateRepository:
    """In-memory implementation of Conversion_rate repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryScriptureRepository:
    """In-memory implementation of Scripture repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySpaceshipRepository:
    """In-memory implementation of Spaceship repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryBattalionRepository:
    """In-memory implementation of Battalion repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPhenomenonRepository:
    """In-memory implementation of Phenomenon repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCompetitionRepository:
    """In-memory implementation of Competition repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPlagueRepository:
    """In-memory implementation of Plague repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryBlack_holeRepository:
    """In-memory implementation of Black_hole repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryWitnessRepository:
    """In-memory implementation of Witness repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCursed_itemRepository:
    """In-memory implementation of Cursed_item repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryTimelineRepository:
    """In-memory implementation of Timeline repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryComponentRepository:
    """In-memory implementation of Component repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCutsceneRepository:
    """In-memory implementation of Cutscene repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryFaction_hierarchyRepository:
    """In-memory implementation of Faction_hierarchy repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryMusic_trackRepository:
    """In-memory implementation of Music_track repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryTrapRepository:
    """In-memory implementation of Trap repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCrimeRepository:
    """In-memory implementation of Crime repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryFood_chainRepository:
    """In-memory implementation of Food_chain repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryReproductionRepository:
    """In-memory implementation of Reproduction repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryRaidRepository:
    """In-memory implementation of Raid repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryScoreRepository:
    """In-memory implementation of Score repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryHonorRepository:
    """In-memory implementation of Honor repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryStorylineRepository:
    """In-memory implementation of Storyline repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryLevel_upRepository:
    """In-memory implementation of Level_up repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryNebulaRepository:
    """In-memory implementation of Nebula repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCodex_entryRepository:
    """In-memory implementation of Codex_entry repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySubtitleRepository:
    """In-memory implementation of Subtitle repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryDistrictRepository:
    """In-memory implementation of District repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryQuest_prerequisiteRepository:
    """In-memory implementation of Quest_prerequisite repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryMythical_armorRepository:
    """In-memory implementation of Mythical_armor repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryRitualRepository:
    """In-memory implementation of Ritual repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryRed_herringRepository:
    """In-memory implementation of Red_herring repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPetRepository:
    """In-memory implementation of Pet repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryAtmosphereRepository:
    """In-memory implementation of Atmosphere repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySocketRepository:
    """In-memory implementation of Socket repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryFlashbackRepository:
    """In-memory implementation of Flashback repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryBadgeRepository:
    """In-memory implementation of Badge repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPlazaRepository:
    """In-memory implementation of Plaza repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryEraRepository:
    """In-memory implementation of Era repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryTournamentRepository:
    """In-memory implementation of Tournament repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryShare_codeRepository:
    """In-memory implementation of Share_code repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryLocalizationRepository:
    """In-memory implementation of Localization repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryMarket_squareRepository:
    """In-memory implementation of Market_square repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryResearch_centerRepository:
    """In-memory implementation of Research_center repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryHeatmapRepository:
    """In-memory implementation of Heatmap repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryResearchRepository:
    """In-memory implementation of Research repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryRumorRepository:
    """In-memory implementation of Rumor repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryInventionRepository:
    """In-memory implementation of Invention repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCamera_pathRepository:
    """In-memory implementation of Camera_path repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryEnigmaRepository:
    """In-memory implementation of Enigma repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryChekhovs_gunRepository:
    """In-memory implementation of Chekhovs_gun repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryReputationRepository:
    """In-memory implementation of Reputation repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryParticleRepository:
    """In-memory implementation of Particle repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryFaction_territoryRepository:
    """In-memory implementation of Faction_territory repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCharacter_evolutionRepository:
    """In-memory implementation of Character_evolution repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryTeleporterRepository:
    """In-memory implementation of Teleporter repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryShopRepository:
    """In-memory implementation of Shop repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryArenaRepository:
    """In-memory implementation of Arena repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCurrencyRepository:
    """In-memory implementation of Currency repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryExhibitionRepository:
    """In-memory implementation of Exhibition repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryMigrationRepository:
    """In-memory implementation of Migration repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryForeshadowingRepository:
    """In-memory implementation of Foreshadowing repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySkyboxRepository:
    """In-memory implementation of Skybox repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryQuest_reward_tierRepository:
    """In-memory implementation of Quest_reward_tier repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryEvolutionRepository:
    """In-memory implementation of Evolution repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryHibernationRepository:
    """In-memory implementation of Hibernation repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryConsequenceRepository:
    """In-memory implementation of Consequence repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryDivine_itemRepository:
    """In-memory implementation of Divine_item repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryEaster_eggRepository:
    """In-memory implementation of Easter_egg repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryVehicleRepository:
    """In-memory implementation of Vehicle repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryWeapon_systemRepository:
    """In-memory implementation of Weapon_system repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPort_districtRepository:
    """In-memory implementation of Port_district repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryLibraryRepository:
    """In-memory implementation of Library repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryLightingRepository:
    """In-memory implementation of Lighting repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCheckpointRepository:
    """In-memory implementation of Checkpoint repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryUniversityRepository:
    """In-memory implementation of University repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryTrophyRepository:
    """In-memory implementation of Trophy repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemorySummonRepository:
    """In-memory implementation of Summon repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryKingdomRepository:
    """In-memory implementation of Kingdom repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryLawRepository:
    """In-memory implementation of Law repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryAchievementRepository:
    """In-memory implementation of Achievement repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryTransitionRepository:
    """In-memory implementation of Transition repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryTaxRepository:
    """In-memory implementation of Tax repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryLawyerRepository:
    """In-memory implementation of Lawyer repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryQuest_giverRepository:
    """In-memory implementation of Quest_giver repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPriceRepository:
    """In-memory implementation of Price repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryEndingRepository:
    """In-memory implementation of Ending repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPortalRepository:
    """In-memory implementation of Portal repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryTradeRepository:
    """In-memory implementation of Trade repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryOathRepository:
    """In-memory implementation of Oath repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryAmbientRepository:
    """In-memory implementation of Ambient repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryMoonRepository:
    """In-memory implementation of Moon repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryExtinctionRepository:
    """In-memory implementation of Extinction repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryDungeonRepository:
    """In-memory implementation of Dungeon repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryJournal_pageRepository:
    """In-memory implementation of Journal_page repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryGalaxyRepository:
    """In-memory implementation of Galaxy repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryPlayer_profileRepository:
    """In-memory implementation of Player_profile repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryNoble_districtRepository:
    """In-memory implementation of Noble_district repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryDispositionRepository:
    """In-memory implementation of Disposition repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryJuryRepository:
    """In-memory implementation of Jury repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

class InMemoryCeremonyRepository:
    """In-memory implementation of Ceremony repository."""
    def __init__(self):
        self._entities = {}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() 
                if hasattr(e, 'tenant_id') and hasattr(e, 'world_id') 
                and e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._entities:
            del self._entities[key]
            return True
        return False

# Simple PerkRepository (stub)
class InMemoryPerkRepository:
    def __init__(self):
        self._perks = {}
        self._next_id = 1
    def save(self, perk):
        if perk.id is None:
            perk.id = self._next_id
            self._next_id += 1
        self._perks[(perk.tenant_id, perk.id)] = perk
        return perk
    def find_by_id(self, tenant_id, entity_id):
        return self._perks.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [p for p in self._perks.values() if p.tenant_id == tenant_id and p.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._perks:
            del self._perks[(tenant_id, entity_id)]
            return True
        return False

# Simple TraitRepository (stub)
class InMemoryTraitRepository:
    def __init__(self):
        self._traits = {}
        self._next_id = 1
    def save(self, trait):
        if trait.id is None:
            trait.id = self._next_id
            self._next_id += 1
        self._traits[(trait.tenant_id, trait.id)] = trait
        return trait
    def find_by_id(self, tenant_id, entity_id):
        return self._traits.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._traits.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._traits:
            del self._traits[(tenant_id, entity_id)]
            return True
        return False

# Simple AttributeRepository (stub)
class InMemoryAttributeRepository:
    def __init__(self):
        self._attributes = {}
        self._next_id = 1
    def save(self, attribute):
        if attribute.id is None:
            attribute.id = self._next_id
            self._next_id += 1
        self._attributes[(attribute.tenant_id, attribute.id)] = attribute
        return attribute
    def find_by_id(self, tenant_id, entity_id):
        return self._attributes.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [a for a in self._attributes.values() if a.tenant_id == tenant_id and a.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._attributes:
            del self._attributes[(tenant_id, entity_id)]
            return True
        return False

# Simple ExperienceRepository (stub)
class InMemoryExperienceRepository:
    def __init__(self):
        self._experience = {}
        self._next_id = 1
    def save(self, experience):
        if experience.id is None:
            experience.id = self._next_id
            self._next_id += 1
        self._experience[(experience.tenant_id, experience.id)] = experience
        return experience
    def find_by_id(self, tenant_id, entity_id):
        return self._experience.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._experience.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._experience:
            del self._experience[(tenant_id, entity_id)]
            return True
        return False

# Simple LevelUpRepository (stub)
class InMemoryLevelUpRepository:
    def __init__(self):
        self._level_ups = {}
        self._next_id = 1
    def save(self, level_up):
        if level_up.id is None:
            level_up.id = self._next_id
            self._next_id += 1
        self._level_ups[(level_up.tenant_id, level_up.id)] = level_up
        return level_up
    def find_by_id(self, tenant_id, entity_id):
        return self._level_ups.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [l for l in self._level_ups.values() if l.tenant_id == tenant_id and l.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._level_ups:
            del self._level_ups[(tenant_id, entity_id)]
            return True
        return False

# Simple TalentTreeRepository (stub)
class InMemoryTalentTreeRepository:
    def __init__(self):
        self._talent_trees = {}
        self._next_id = 1
    def save(self, talent_tree):
        if talent_tree.id is None:
            talent_tree.id = self._next_id
            self._next_id += 1
        self._talent_trees[(talent_tree.tenant_id, talent_tree.id)] = talent_tree
        return talent_tree
    def find_by_id(self, tenant_id, entity_id):
        return self._talent_trees.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._talent_trees.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._talent_trees:
            del self._talent_trees[(tenant_id, entity_id)]
            return True
        return False

# Simple MasteryRepository (stub)
class InMemoryMasteryRepository:
    def __init__(self):
        self._masteries = {}
        self._next_id = 1
    def save(self, mastery):
        if mastery.id is None:
            mastery.id = self._next_id
            self._next_id += 1
        self._masteries[(mastery.tenant_id, mastery.id)] = mastery
        return mastery
    def find_by_id(self, tenant_id, entity_id):
        return self._masteries.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [m for m in self._masteries.values() if m.tenant_id == tenant_id and m.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._masteries:
            del self._masteries[(tenant_id, entity_id)]
            return True
        return False


# Skill Repository
class InMemorySkillRepository:
    def __init__(self):
        self._skills = {}
        self._next_id = 1
    def save(self, skill):
        if skill.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(skill, 'id', new_id)
        self._skills[(skill.tenant_id, skill.id)] = skill
        return skill
    def find_by_id(self, tenant_id, skill_id):
        return self._skills.get((tenant_id, skill_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._skills.values() 
                if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, skill_id):
        if (tenant_id, skill_id) in self._skills:
            del self._skills[(tenant_id, skill_id)]
            return True
        return False

# Perk Repository
class InMemoryPerkRepository:
    def __init__(self):
        self._perks = {}
        self._next_id = 1
    def save(self, perk):
        if perk.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(perk, 'id', new_id)
        self._perks[(perk.tenant_id, perk.id)] = perk
        return perk
    def find_by_id(self, tenant_id, perk_id):
        return self._perks.get((tenant_id, perk_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [p for p in self._perks.values() 
                if p.tenant_id == tenant_id and p.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, perk_id):
        if (tenant_id, perk_id) in self._perks:
            del self._perks[(tenant_id, perk_id)]
            return True
        return False

# Trait Repository
class InMemoryTraitRepository:
    def __init__(self):
        self._traits = {}
        self._next_id = 1
    def save(self, trait):
        if trait.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(trait, 'id', new_id)
        self._traits[(trait.tenant_id, trait.id)] = trait
        return trait
    def find_by_id(self, tenant_id, trait_id):
        return self._traits.get((tenant_id, trait_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._traits.values() 
                if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, trait_id):
        if (tenant_id, trait_id) in self._traits:
            del self._traits[(tenant_id, trait_id)]
            return True
        return False

# Attribute Repository
class InMemoryAttributeRepository:
    def __init__(self):
        self._attributes = {}
        self._next_id = 1
    def save(self, attribute):
        if attribute.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(attribute, 'id', new_id)
        self._attributes[(attribute.tenant_id, attribute.id)] = attribute
        return attribute
    def find_by_id(self, tenant_id, attribute_id):
        return self._attributes.get((tenant_id, attribute_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [a for a in self._attributes.values() 
                if a.tenant_id == tenant_id and a.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, attribute_id):
        if (tenant_id, attribute_id) in self._attributes:
            del self._attributes[(tenant_id, attribute_id)]
            return True
        return False

# Experience Repository
class InMemoryExperienceRepository:
    def __init__(self):
        self._experience = {}
        self._next_id = 1
    def save(self, experience):
        if experience.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(experience, 'id', new_id)
        self._experience[(experience.tenant_id, experience.id)] = experience
        return experience
    def find_by_id(self, tenant_id, experience_id):
        return self._experience.get((tenant_id, experience_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._experience.values() 
                if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, experience_id):
        if (tenant_id, experience_id) in self._experience:
            del self._experience[(tenant_id, experience_id)]
            return True
        return False

# LevelUp Repository
class InMemoryLevelUpRepository:
    def __init__(self):
        self._level_ups = {}
        self._next_id = 1
    def save(self, level_up):
        if level_up.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(level_up, 'id', new_id)
        self._level_ups[(level_up.tenant_id, level_up.id)] = level_up
        return level_up
    def find_by_id(self, tenant_id, level_up_id):
        return self._level_ups.get((tenant_id, level_up_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [l for l in self._level_ups.values() 
                if l.tenant_id == tenant_id and l.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, level_up_id):
        if (tenant_id, level_up_id) in self._level_ups:
            del self._level_ups[(tenant_id, level_up_id)]
            return True
        return False

# TalentTree Repository
class InMemoryTalentTreeRepository:
    def __init__(self):
        self._talent_trees = {}
        self._next_id = 1
    def save(self, talent_tree):
        if talent_tree.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(talent_tree, 'id', new_id)
        self._talent_trees[(talent_tree.tenant_id, talent_tree.id)] = talent_tree
        return talent_tree
    def find_by_id(self, tenant_id, talent_tree_id):
        return self._talent_trees.get((tenant_id, talent_tree_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [tt for tt in self._talent_trees.values() 
                if tt.tenant_id == tenant_id and tt.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, talent_tree_id):
        if (tenant_id, talent_tree_id) in self._talent_trees:
            del self._talent_trees[(tenant_id, talent_tree_id)]
            return True
        return False

# Mastery Repository
class InMemoryMasteryRepository:
    def __init__(self):
        self._masteries = {}
        self._next_id = 1
    def save(self, mastery):
        if mastery.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(mastery, 'id', new_id)
        self._masteries[(mastery.tenant_id, mastery.id)] = mastery
        return mastery
    def find_by_id(self, tenant_id, mastery_id):
        return self._masteries.get((tenant_id, mastery_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [m for m in self._masteries.values() 
                if m.tenant_id == tenant_id and m.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, mastery_id):
        if (tenant_id, mastery_id) in self._masteries:
            del self._masteries[(tenant_id, mastery_id)]
            return True
        return False


# Skill Repository
class InMemorySkillRepository:
    def __init__(self):
        self._skills = {}
        self._next_id = 1
    def save(self, skill):
        if skill.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(skill, 'id', new_id)
        self._skills[(skill.tenant_id, skill.id)] = skill
        return skill
    def find_by_id(self, tenant_id, skill_id):
        return self._skills.get((tenant_id, skill_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._skills.values() 
                if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, skill_id):
        if (tenant_id, skill_id) in self._skills:
            del self._skills[(tenant_id, skill_id)]
            return True
        return False

# Perk Repository
class InMemoryPerkRepository:
    def __init__(self):
        self._perks = {}
        self._next_id = 1
    def save(self, perk):
        if perk.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(perk, 'id', new_id)
        self._perks[(perk.tenant_id, perk.id)] = perk
        return perk
    def find_by_id(self, tenant_id, perk_id):
        return self._perks.get((tenant_id, perk_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [p for p in self._perks.values() 
                if p.tenant_id == tenant_id and p.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, perk_id):
        if (tenant_id, perk_id) in self._perks:
            del self._perks[(tenant_id, perk_id)]
            return True
        return False

# Trait Repository
class InMemoryTraitRepository:
    def __init__(self):
        self._traits = {}
        self._next_id = 1
    def save(self, trait):
        if trait.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(trait, 'id', new_id)
        self._traits[(trait.tenant_id, trait.id)] = trait
        return trait
    def find_by_id(self, tenant_id, trait_id):
        return self._traits.get((tenant_id, trait_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._traits.values() 
                if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, trait_id):
        if (tenant_id, trait_id) in self._traits:
            del self._traits[(tenant_id, trait_id)]
            return True
        return False

# Attribute Repository
class InMemoryAttributeRepository:
    def __init__(self):
        self._attributes = {}
        self._next_id = 1
    def save(self, attribute):
        if attribute.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(attribute, 'id', new_id)
        self._attributes[(attribute.tenant_id, attribute.id)] = attribute
        return attribute
    def find_by_id(self, tenant_id, attribute_id):
        return self._attributes.get((tenant_id, attribute_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [a for a in self._attributes.values() 
                if a.tenant_id == tenant_id and a.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, attribute_id):
        if (tenant_id, attribute_id) in self._attributes:
            del self._attributes[(tenant_id, attribute_id)]
            return True
        return False

# Experience Repository
class InMemoryExperienceRepository:
    def __init__(self):
        self._experience = {}
        self._next_id = 1
    def save(self, experience):
        if experience.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(experience, 'id', new_id)
        self._experience[(experience.tenant_id, experience.id)] = experience
        return experience
    def find_by_id(self, tenant_id, experience_id):
        return self._experience.get((tenant_id, experience_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._experience.values() 
                if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, experience_id):
        if (tenant_id, experience_id) in self._experience:
            del self._experience[(tenant_id, experience_id)]
            return True
        return False

# LevelUp Repository
class InMemoryLevelUpRepository:
    def __init__(self):
        self._level_ups = {}
        self._next_id = 1
    def save(self, level_up):
        if level_up.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(level_up, 'id', new_id)
        self._level_ups[(level_up.tenant_id, level_up.id)] = level_up
        return level_up
    def find_by_id(self, tenant_id, level_up_id):
        return self._level_ups.get((tenant_id, level_up_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [l for l in self._level_ups.values() 
                if l.tenant_id == tenant_id and l.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, level_up_id):
        if (tenant_id, level_up_id) in self._level_ups:
            del self._level_ups[(tenant_id, level_up_id)]
            return True
        return False

# TalentTree Repository
class InMemoryTalentTreeRepository:
    def __init__(self):
        self._talent_trees = {}
        self._next_id = 1
    def save(self, talent_tree):
        if talent_tree.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(talent_tree, 'id', new_id)
        self._talent_trees[(talent_tree.tenant_id, talent_tree.id)] = talent_tree
        return talent_tree
    def find_by_id(self, tenant_id, talent_tree_id):
        return self._talent_trees.get((tenant_id, talent_tree_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [tt for tt in self._talent_trees.values() 
                if tt.tenant_id == tenant_id and tt.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, talent_tree_id):
        if (tenant_id, talent_tree_id) in self._talent_trees:
            del self._talent_trees[(tenant_id, talent_tree_id)]
            return True
        return False

# Mastery Repository
class InMemoryMasteryRepository:
    def __init__(self):
        self._masteries = {}
        self._next_id = 1
    def save(self, mastery):
        if mastery.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(mastery, 'id', new_id)
        self._masteries[(mastery.tenant_id, mastery.id)] = mastery
        return mastery
    def find_by_id(self, tenant_id, mastery_id):
        return self._masteries.get((tenant_id, mastery_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [m for m in self._masteries.values() 
                if m.tenant_id == tenant_id and m.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, mastery_id):
        if (tenant_id, mastery_id) in self._masteries:
            del self._masteries[(tenant_id, mastery_id)]
            return True
        return False


# World History Repositories
class InMemoryEraRepository:
    def __init__(self):
        self._eras = {}
        self._next_id = 1
    def save(self, era):
        if era.id is None:
            from src.domain.value_objects.common import EntityId
            era.id = EntityId(self._next_id)
            self._next_id += 1
        self._eras[(era.tenant_id, era.id)] = era
        return era
    def find_by_id(self, tenant_id, era_id):
        return self._eras.get((tenant_id, era_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._eras.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, era_id):
        key = (tenant_id, era_id)
        if key in self._eras:
            del self._eras[key]
            return True
        return False

class InMemoryEraTransitionRepository:
    def __init__(self):
        self._transitions = {}
        self._next_id = 1
    def save(self, transition):
        if transition.id is None:
            from src.domain.value_objects.common import EntityId
            transition.id = EntityId(self._next_id)
            self._next_id += 1
        self._transitions[(transition.tenant_id, transition.id)] = transition
        return transition
    def find_by_id(self, tenant_id, transition_id):
        return self._transitions.get((tenant_id, transition_id))
    def list_by_era(self, tenant_id, era_id, limit=50, offset=0):
        return [t for t in self._transitions.values() if t.tenant_id == tenant_id and t.from_era == era_id][offset:offset+limit]
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._transitions.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, transition_id):
        key = (tenant_id, transition_id)
        if key in self._transitions:
            del self._transitions[key]
            return True
        return False

class InMemoryTimelineRepository:
    def __init__(self):
        self._events = {}
        self._next_id = 1
    def save(self, event):
        if event.id is None:
            from src.domain.value_objects.common import EntityId
            event.id = EntityId(self._next_id)
            self._next_id += 1
        self._events[(event.tenant_id, event.id)] = event
        return event
    def find_by_id(self, tenant_id, event_id):
        return self._events.get((tenant_id, event_id))
    def list_by_era(self, tenant_id, era_id, limit=50, offset=0):
        return [e for e in self._events.values() if e.tenant_id == tenant_id and e.era_id == era_id][offset:offset+limit]
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._events.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, event_id):
        key = (tenant_id, event_id)
        if key in self._events:
            del self._events[key]
            return True
        return False

class InMemoryCalendarRepository:
    def __init__(self):
        self._calendars = {}
        self._next_id = 1
    def save(self, calendar):
        if calendar.id is None:
            from src.domain.value_objects.common import EntityId
            calendar.id = EntityId(self._next_id)
            self._next_id += 1
        self._calendars[(calendar.tenant_id, calendar.id)] = calendar
        return calendar
    def find_by_id(self, tenant_id, calendar_id):
        return self._calendars.get((tenant_id, calendar_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [c for c in self._calendars.values() if c.tenant_id == tenant_id and c.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, calendar_id):
        key = (tenant_id, calendar_id)
        if key in self._calendars:
            del self._calendars[key]
            return True
        return False

# Time System Repositories
class InMemoryHolidayRepository:
    def __init__(self):
        self._holidays = {}
        self._next_id = 1
    def save(self, holiday):
        if holiday.id is None:
            from src.domain.value_objects.common import EntityId
            holiday.id = EntityId(self._next_id)
            self._next_id += 1
        self._holidays[(holiday.tenant_id, holiday.id)] = holiday
        return holiday
    def find_by_id(self, tenant_id, holiday_id):
        return self._holidays.get((tenant_id, holiday_id))
    def list_by_calendar(self, tenant_id, calendar_id, limit=50, offset=0):
        return [h for h in self._holidays.values() if h.tenant_id == tenant_id and h.calendar_id == calendar_id][offset:offset+limit]
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [h for h in self._holidays.values() if h.tenant_id == tenant_id and h.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, holiday_id):
        key = (tenant_id, holiday_id)
        if key in self._holidays:
            del self._holidays[key]
            return True
        return False

class InMemorySeasonRepository:
    def __init__(self):
        self._seasons = {}
        self._next_id = 1
    def save(self, season):
        if season.id is None:
            from src.domain.value_objects.common import EntityId
            season.id = EntityId(self._next_id)
            self._next_id += 1
        self._seasons[(season.tenant_id, season.id)] = season
        return season
    def find_by_id(self, tenant_id, season_id):
        return self._seasons.get((tenant_id, season_id))
    def list_by_calendar(self, tenant_id, calendar_id, limit=50, offset=0):
        return [s for s in self._seasons.values() if s.tenant_id == tenant_id and s.calendar_id == calendar_id][offset:offset+limit]
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._seasons.values() if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, season_id):
        key = (tenant_id, season_id)
        if key in self._seasons:
            del self._seasons[key]
            return True
        return False

class InMemoryTimePeriodRepository:
    def __init__(self):
        self._periods = {}
        self._next_id = 1
    def save(self, period):
        if period.id is None:
            from src.domain.value_objects.common import EntityId
            period.id = EntityId(self._next_id)
            self._next_id += 1
        self._periods[(period.tenant_id, period.id)] = period
        return period
    def find_by_id(self, tenant_id, period_id):
        return self._periods.get((tenant_id, period_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [p for p in self._periods.values() if p.tenant_id == tenant_id and p.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, period_id):
        key = (tenant_id, period_id)
        if key in self._periods:
            del self._periods[key]
            return True
        return False

# Politics/Law Repositories
class InMemoryTreatyRepository:
    def __init__(self):
        self._treaties = {}
        self._next_id = 1
    def save(self, treaty):
        if treaty.id is None:
            from src.domain.value_objects.common import EntityId
            treaty.id = EntityId(self._next_id)
            self._next_id += 1
        self._treaties[(treaty.tenant_id, treaty.id)] = treaty
        return treaty
    def find_by_id(self, tenant_id, treaty_id):
        return self._treaties.get((tenant_id, treaty_id))
    def list_by_nation(self, tenant_id, nation_id, limit=50, offset=0):
        return [t for t in self._treaties.values() if t.tenant_id == tenant_id and t.nation_id == nation_id][offset:offset+limit]
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._treaties.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, treaty_id):
        key = (tenant_id, treaty_id)
        if key in self._treaties:
            del self._treaties[key]
            return True
        return False

class InMemoryConstitutionRepository:
    def __init__(self):
        self._constitutions = {}
        self._next_id = 1
    def save(self, constitution):
        if constitution.id is None:
            from src.domain.value_objects.common import EntityId
            constitution.id = EntityId(self._next_id)
            self._next_id += 1
        self._constitutions[(constitution.tenant_id, constitution.id)] = constitution
        return constitution
    def find_by_id(self, tenant_id, constitution_id):
        return self._constitutions.get((tenant_id, constitution_id))
    def list_by_nation(self, tenant_id, nation_id, limit=50, offset=0):
        return [c for c in self._constitutions.values() if c.tenant_id == tenant_id and c.nation_id == nation_id][offset:offset+limit]
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [c for c in self._constitutions.values() if c.tenant_id == tenant_id and c.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, constitution_id):
        key = (tenant_id, constitution_id)
        if key in self._constitutions:
            del self._constitutions[key]
            return True
        return False

class InMemoryLawRepository:
    def __init__(self):
        self._laws = {}
        self._next_id = 1
    def save(self, law):
        if law.id is None:
            from src.domain.value_objects.common import EntityId
            law.id = EntityId(self._next_id)
            self._next_id += 1
        self._laws[(law.tenant_id, law.id)] = law
        return law
    def find_by_id(self, tenant_id, law_id):
        return self._laws.get((tenant_id, law_id))
    def list_by_constitution(self, tenant_id, constitution_id, limit=50, offset=0):
        return [l for l in self._laws.values() if l.tenant_id == tenant_id and l.constitution_id == constitution_id][offset:offset+limit]
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [l for l in self._laws.values() if l.tenant_id == tenant_id and l.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, law_id):
        key = (tenant_id, law_id)
        if key in self._laws:
            del self._laws[key]
            return True
        return False

class InMemoryLegalSystemRepository:
    def __init__(self):
        self._systems = {}
        self._next_id = 1
    def save(self, legal_system):
        if legal_system.id is None:
            from src.domain.value_objects.common import EntityId
            legal_system.id = EntityId(self._next_id)
            self._next_id += 1
        self._systems[(legal_system.tenant_id, legal_system.id)] = legal_system
        return legal_system
    def find_by_id(self, tenant_id, system_id):
        return self._systems.get((tenant_id, system_id))
    def list_by_nation(self, tenant_id, nation_id, limit=50, offset=0):
        return [s for s in self._systems.values() if s.tenant_id == tenant_id and s.nation_id == nation_id][offset:offset+limit]
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._systems.values() if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, system_id):
        key = (tenant_id, system_id)
        if key in self._systems:
            del self._systems[key]
            return True
        return False

# Political Entities Repositories
class InMemoryNationRepository:
    def __init__(self):
        self._nations = {}
        self._next_id = 1
    def save(self, nation):
        if nation.id is None:
            from src.domain.value_objects.common import EntityId
            nation.id = EntityId(self._next_id)
            self._next_id += 1
        self._nations[(nation.tenant_id, nation.id)] = nation
        return nation
    def find_by_id(self, tenant_id, nation_id):
        return self._nations.get((tenant_id, nation_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [n for n in self._nations.values() if n.tenant_id == tenant_id and n.world_id == world_id][offset:offset+limit]
    def list_by_alliance(self, tenant_id, alliance_id, limit=50, offset=0):
        return [n for n in self._nations.values() if n.tenant_id == tenant_id and n.alliance_id == alliance_id][offset:offset+limit]
    def delete(self, tenant_id, nation_id):
        key = (tenant_id, nation_id)
        if key in self._nations:
            del self._nations[key]
            return True
        return False

class InMemoryKingdomRepository:
    def __init__(self):
        self._kingdoms = {}
        self._next_id = 1
    def save(self, kingdom):
        if kingdom.id is None:
            from src.domain.value_objects.common import EntityId
            kingdom.id = EntityId(self._next_id)
            self._next_id += 1
        self._kingdoms[(kingdom.tenant_id, kingdom.id)] = kingdom
        return kingdom
    def find_by_id(self, tenant_id, kingdom_id):
        return self._kingdoms.get((tenant_id, kingdom_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [k for k in self._kingdoms.values() if k.tenant_id == tenant_id and k.world_id == world_id][offset:offset+limit]
    def list_by_nation(self, tenant_id, nation_id, limit=50, offset=0):
        return [k for k in self._kingdoms.values() if k.tenant_id == tenant_id and k.nation_id == nation_id][offset:offset+limit]
    def delete(self, tenant_id, kingdom_id):
        key = (tenant_id, kingdom_id)
        if key in self._kingdoms:
            del self._kingdoms[key]
            return True
        return False

class InMemoryEmpireRepository:
    def __init__(self):
        self._empires = {}
        self._next_id = 1
    def save(self, empire):
        if empire.id is None:
            from src.domain.value_objects.common import EntityId
            empire.id = EntityId(self._next_id)
            self._next_id += 1
        self._empires[(empire.tenant_id, empire.id)] = empire
        return empire
    def find_by_id(self, tenant_id, empire_id):
        return self._empires.get((tenant_id, empire_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._empires.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def list_by_nation(self, tenant_id, nation_id, limit=50, offset=0):
        return [e for e in self._empires.values() if e.tenant_id == tenant_id and e.nation_id == nation_id][offset:offset+limit]
    def delete(self, tenant_id, empire_id):
        key = (tenant_id, empire_id)
        if key in self._empires:
            del self._empires[key]
            return True
        return False

class InMemoryGovernmentRepository:
    def __init__(self):
        self._governments = {}
        self._next_id = 1
    def save(self, government):
        if government.id is None:
            from src.domain.value_objects.common import EntityId
            government.id = EntityId(self._next_id)
            self._next_id += 1
        self._governments[(government.tenant_id, government.id)] = government
        return government
    def find_by_id(self, tenant_id, government_id):
        return self._governments.get((tenant_id, government_id))
    def list_by_nation(self, tenant_id, nation_id, limit=50, offset=0):
        return [g for g in self._governments.values() if g.tenant_id == tenant_id and g.nation_id == nation_id][offset:offset+limit]
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [g for g in self._governments.values() if g.tenant_id == tenant_id and g.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, government_id):
        key = (tenant_id, government_id)
        if key in self._governments:
            del self._governments[key]
            return True
        return False

class InMemoryAllianceRepository:
    def __init__(self):
        self._alliances = {}
        self._next_id = 1
    def save(self, alliance):
        if alliance.id is None:
            from src.domain.value_objects.common import EntityId
            alliance.id = EntityId(self._next_id)
            self._next_id += 1
        self._alliances[(alliance.tenant_id, alliance.id)] = alliance
        return alliance
    def find_by_id(self, tenant_id, alliance_id):
        return self._alliances.get((tenant_id, alliance_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [a for a in self._alliances.values() if a.tenant_id == tenant_id and a.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, alliance_id):
        key = (tenant_id, alliance_id)
        if key in self._alliances:
            del self._alliances[key]
            return True
        return False


# ============================================================================
# PARTY 3: SOCIAL/RELIGION + LOCATIONS + INVENTORY/CRAFTING (36 repos)
# ============================================================================

# Social Relations Repositories (7)
class InMemoryReputationRepository:
    def __init__(self):
        self._reputations = {}
        self._next_id = 1
    def save(self, reputation):
        if reputation.id is None:
            from src.domain.value_objects.common import EntityId
            reputation.id = EntityId(self._next_id)
            self._next_id += 1
        self._reputations[(reputation.tenant_id, reputation.id)] = reputation
        return reputation
    def find_by_id(self, tenant_id, entity_id):
        return self._reputations.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._reputations.values() 
                if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._reputations:
            del self._reputations[(tenant_id, entity_id)]
            return True
        return False

class InMemoryAffinityRepository:
    def __init__(self):
        self._affinities = {}
        self._next_id = 1
    def save(self, affinity):
        if affinity.id is None:
            from src.domain.value_objects.common import EntityId
            affinity.id = EntityId(self._next_id)
            self._next_id += 1
        self._affinities[(affinity.tenant_id, affinity.id)] = affinity
        return affinity
    def find_by_id(self, tenant_id, entity_id):
        return self._affinities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [a for a in self._affinities.values() 
                if a.tenant_id == tenant_id and a.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._affinities:
            del self._affinities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDispositionRepository:
    def __init__(self):
        self._dispositions = {}
        self._next_id = 1
    def save(self, disposition):
        if disposition.id is None:
            from src.domain.value_objects.common import EntityId
            disposition.id = EntityId(self._next_id)
            self._next_id += 1
        self._dispositions[(disposition.tenant_id, disposition.id)] = disposition
        return disposition
    def find_by_id(self, tenant_id, entity_id):
        return self._dispositions.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [d for d in self._dispositions.values() 
                if d.tenant_id == tenant_id and d.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._dispositions:
            del self._dispositions[(tenant_id, entity_id)]
            return True
        return False

class InMemoryHonorRepository:
    def __init__(self):
        self._honor = {}
        self._next_id = 1
    def save(self, honor):
        if honor.id is None:
            from src.domain.value_objects.common import EntityId
            honor.id = EntityId(self._next_id)
            self._next_id += 1
        self._honor[(honor.tenant_id, honor.id)] = honor
        return honor
    def find_by_id(self, tenant_id, entity_id):
        return self._honor.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [h for h in self._honor.values() 
                if h.tenant_id == tenant_id and h.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._honor:
            del self._honor[(tenant_id, entity_id)]
            return True
        return False

class InMemoryKarmaRepository:
    def __init__(self):
        self._karmas = {}
        self._next_id = 1
    def save(self, karma):
        if karma.id is None:
            from src.domain.value_objects.common import EntityId
            karma.id = EntityId(self._next_id)
            self._next_id += 1
        self._karmas[(karma.tenant_id, karma.id)] = karma
        return karma
    def find_by_id(self, tenant_id, entity_id):
        return self._karmas.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [k for k in self._karmas.values() 
                if k.tenant_id == tenant_id and k.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._karmas:
            del self._karmas[(tenant_id, entity_id)]
            return True
        return False

class InMemorySocialClassRepository:
    def __init__(self):
        self._social_classes = {}
        self._next_id = 1
    def save(self, social_class):
        if social_class.id is None:
            from src.domain.value_objects.common import EntityId
            social_class.id = EntityId(self._next_id)
            self._next_id += 1
        self._social_classes[(social_class.tenant_id, social_class.id)] = social_class
        return social_class
    def find_by_id(self, tenant_id, entity_id):
        return self._social_classes.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [sc for sc in self._social_classes.values() 
                if sc.tenant_id == tenant_id and sc.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._social_classes:
            del self._social_classes[(tenant_id, entity_id)]
            return True
        return False

class InMemorySocialMobilityRepository:
    def __init__(self):
        self._mobilities = {}
        self._next_id = 1
    def save(self, mobility):
        if mobility.id is None:
            from src.domain.value_objects.common import EntityId
            mobility.id = EntityId(self._next_id)
            self._next_id += 1
        self._mobilities[(mobility.tenant_id, mobility.id)] = mobility
        return mobility
    def find_by_id(self, tenant_id, entity_id):
        return self._mobilities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [m for m in self._mobilities.values() 
                if m.tenant_id == tenant_id and m.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._mobilities:
            del self._mobilities[(tenant_id, entity_id)]
            return True
        return False

# Religion/Mysticism Repositories (10)
class InMemoryCultRepository:
    def __init__(self):
        self._cults = {}
        self._next_id = 1
    def save(self, cult):
        if cult.id is None:
            from src.domain.value_objects.common import EntityId
            cult.id = EntityId(self._next_id)
            self._next_id += 1
        self._cults[(cult.tenant_id, cult.id)] = cult
        return cult
    def find_by_id(self, tenant_id, entity_id):
        return self._cults.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [c for c in self._cults.values() 
                if c.tenant_id == tenant_id and c.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._cults:
            del self._cults[(tenant_id, entity_id)]
            return True
        return False

class InMemorySectRepository:
    def __init__(self):
        self._sects = {}
        self._next_id = 1
    def save(self, sect):
        if sect.id is None:
            from src.domain.value_objects.common import EntityId
            sect.id = EntityId(self._next_id)
            self._next_id += 1
        self._sects[(sect.tenant_id, sect.id)] = sect
        return sect
    def find_by_id(self, tenant_id, entity_id):
        return self._sects.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._sects.values() 
                if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._sects:
            del self._sects[(tenant_id, entity_id)]
            return True
        return False

class InMemoryHolySiteRepository:
    def __init__(self):
        self._holy_sites = {}
        self._next_id = 1
    def save(self, holy_site):
        if holy_site.id is None:
            from src.domain.value_objects.common import EntityId
            holy_site.id = EntityId(self._next_id)
            self._next_id += 1
        self._holy_sites[(holy_site.tenant_id, holy_site.id)] = holy_site
        return holy_site
    def find_by_id(self, tenant_id, entity_id):
        return self._holy_sites.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [hs for hs in self._holy_sites.values() 
                if hs.tenant_id == tenant_id and hs.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._holy_sites:
            del self._holy_sites[(tenant_id, entity_id)]
            return True
        return False

class InMemoryScriptureRepository:
    def __init__(self):
        self._scriptures = {}
        self._next_id = 1
    def save(self, scripture):
        if scripture.id is None:
            from src.domain.value_objects.common import EntityId
            scripture.id = EntityId(self._next_id)
            self._next_id += 1
        self._scriptures[(scripture.tenant_id, scripture.id)] = scripture
        return scripture
    def find_by_id(self, tenant_id, entity_id):
        return self._scriptures.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._scriptures.values() 
                if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._scriptures:
            del self._scriptures[(tenant_id, entity_id)]
            return True
        return False

class InMemoryRitualRepository:
    def __init__(self):
        self._rituals = {}
        self._next_id = 1
    def save(self, ritual):
        if ritual.id is None:
            from src.domain.value_objects.common import EntityId
            ritual.id = EntityId(self._next_id)
            self._next_id += 1
        self._rituals[(ritual.tenant_id, ritual.id)] = ritual
        return ritual
    def find_by_id(self, tenant_id, entity_id):
        return self._rituals.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._rituals.values() 
                if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._rituals:
            del self._rituals[(tenant_id, entity_id)]
            return True
        return False

class InMemoryOathRepository:
    def __init__(self):
        self._oaths = {}
        self._next_id = 1
    def save(self, oath):
        if oath.id is None:
            from src.domain.value_objects.common import EntityId
            oath.id = EntityId(self._next_id)
            self._next_id += 1
        self._oaths[(oath.tenant_id, oath.id)] = oath
        return oath
    def find_by_id(self, tenant_id, entity_id):
        return self._oaths.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [o for o in self._oaths.values() 
                if o.tenant_id == tenant_id and o.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._oaths:
            del self._oaths[(tenant_id, entity_id)]
            return True
        return False

class InMemorySummonRepository:
    def __init__(self):
        self._summons = {}
        self._next_id = 1
    def save(self, summon):
        if summon.id is None:
            from src.domain.value_objects.common import EntityId
            summon.id = EntityId(self._next_id)
            self._next_id += 1
        self._summons[(summon.tenant_id, summon.id)] = summon
        return summon
    def find_by_id(self, tenant_id, entity_id):
        return self._summons.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._summons.values() 
                if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._summons:
            del self._summons[(tenant_id, entity_id)]
            return True
        return False

class InMemoryPactRepository:
    def __init__(self):
        self._pacts = {}
        self._next_id = 1
    def save(self, pact):
        if pact.id is None:
            from src.domain.value_objects.common import EntityId
            pact.id = EntityId(self._next_id)
            self._next_id += 1
        self._pacts[(pact.tenant_id, pact.id)] = pact
        return pact
    def find_by_id(self, tenant_id, entity_id):
        return self._pacts.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [p for p in self._pacts.values() 
                if p.tenant_id == tenant_id and p.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._pacts:
            del self._pacts[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCurseRepository:
    def __init__(self):
        self._curses = {}
        self._next_id = 1
    def save(self, curse):
        if curse.id is None:
            from src.domain.value_objects.common import EntityId
            curse.id = EntityId(self._next_id)
            self._next_id += 1
        self._curses[(curse.tenant_id, curse.id)] = curse
        return curse
    def find_by_id(self, tenant_id, entity_id):
        return self._curses.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [c for c in self._curses.values() 
                if c.tenant_id == tenant_id and c.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._curses:
            del self._curses[(tenant_id, entity_id)]
            return True
        return False

class InMemoryBlessingRepository:
    def __init__(self):
        self._blessings = {}
        self._next_id = 1
    def save(self, blessing):
        if blessing.id is None:
            from src.domain.value_objects.common import EntityId
            blessing.id = EntityId(self._next_id)
            self._next_id += 1
        self._blessings[(blessing.tenant_id, blessing.id)] = blessing
        return blessing
    def find_by_id(self, tenant_id, entity_id):
        return self._blessings.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [b for b in self._blessings.values() 
                if b.tenant_id == tenant_id and b.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._blessings:
            del self._blessings[(tenant_id, entity_id)]
            return True
        return False

# Locations Repositories (10)
class InMemoryHubAreaRepository:
    def __init__(self):
        self._hub_areas = {}
        self._next_id = 1
    def save(self, hub_area):
        if hub_area.id is None:
            from src.domain.value_objects.common import EntityId
            hub_area.id = EntityId(self._next_id)
            self._next_id += 1
        self._hub_areas[(hub_area.tenant_id, hub_area.id)] = hub_area
        return hub_area
    def find_by_id(self, tenant_id, entity_id):
        return self._hub_areas.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [h for h in self._hub_areas.values() 
                if h.tenant_id == tenant_id and h.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._hub_areas:
            del self._hub_areas[(tenant_id, entity_id)]
            return True
        return False

class InMemoryInstanceRepository:
    def __init__(self):
        self._instances = {}
        self._next_id = 1
    def save(self, instance):
        if instance.id is None:
            from src.domain.value_objects.common import EntityId
            instance.id = EntityId(self._next_id)
            self._next_id += 1
        self._instances[(instance.tenant_id, instance.id)] = instance
        return instance
    def find_by_id(self, tenant_id, entity_id):
        return self._instances.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [i for i in self._instances.values() 
                if i.tenant_id == tenant_id and i.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._instances:
            del self._instances[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDungeonRepository:
    def __init__(self):
        self._dungeons = {}
        self._next_id = 1
    def save(self, dungeon):
        if dungeon.id is None:
            from src.domain.value_objects.common import EntityId
            dungeon.id = EntityId(self._next_id)
            self._next_id += 1
        self._dungeons[(dungeon.tenant_id, dungeon.id)] = dungeon
        return dungeon
    def find_by_id(self, tenant_id, entity_id):
        return self._dungeons.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [d for d in self._dungeons.values() 
                if d.tenant_id == tenant_id and d.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._dungeons:
            del self._dungeons[(tenant_id, entity_id)]
            return True
        return False

class InMemoryRaidRepository:
    def __init__(self):
        self._raids = {}
        self._next_id = 1
    def save(self, raid):
        if raid.id is None:
            from src.domain.value_objects.common import EntityId
            raid.id = EntityId(self._next_id)
            self._next_id += 1
        self._raids[(raid.tenant_id, raid.id)] = raid
        return raid
    def find_by_id(self, tenant_id, entity_id):
        return self._raids.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._raids.values() 
                if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._raids:
            del self._raids[(tenant_id, entity_id)]
            return True
        return False

class InMemoryArenaRepository:
    def __init__(self):
        self._arenas = {}
        self._next_id = 1
    def save(self, arena):
        if arena.id is None:
            from src.domain.value_objects.common import EntityId
            arena.id = EntityId(self._next_id)
            self._next_id += 1
        self._arenas[(arena.tenant_id, arena.id)] = arena
        return arena
    def find_by_id(self, tenant_id, entity_id):
        return self._arenas.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [a for a in self._arenas.values() 
                if a.tenant_id == tenant_id and a.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._arenas:
            del self._arenas[(tenant_id, entity_id)]
            return True
        return False

class InMemoryOpenWorldZoneRepository:
    def __init__(self):
        self._open_world_zones = {}
        self._next_id = 1
    def save(self, open_world_zone):
        if open_world_zone.id is None:
            from src.domain.value_objects.common import EntityId
            open_world_zone.id = EntityId(self._next_id)
            self._next_id += 1
        self._open_world_zones[(open_world_zone.tenant_id, open_world_zone.id)] = open_world_zone
        return open_world_zone
    def find_by_id(self, tenant_id, entity_id):
        return self._open_world_zones.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [o for o in self._open_world_zones.values() 
                if o.tenant_id == tenant_id and o.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._open_world_zones:
            del self._open_world_zones[(tenant_id, entity_id)]
            return True
        return False

class InMemoryUndergroundRepository:
    def __init__(self):
        self._undergrounds = {}
        self._next_id = 1
    def save(self, underground):
        if underground.id is None:
            from src.domain.value_objects.common import EntityId
            underground.id = EntityId(self._next_id)
            self._next_id += 1
        self._undergrounds[(underground.tenant_id, underground.id)] = underground
        return underground
    def find_by_id(self, tenant_id, entity_id):
        return self._undergrounds.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [u for u in self._undergrounds.values() 
                if u.tenant_id == tenant_id and u.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._undergrounds:
            del self._undergrounds[(tenant_id, entity_id)]
            return True
        return False

class InMemorySkyboxRepository:
    def __init__(self):
        self._skyboxes = {}
        self._next_id = 1
    def save(self, skybox):
        if skybox.id is None:
            from src.domain.value_objects.common import EntityId
            skybox.id = EntityId(self._next_id)
            self._next_id += 1
        self._skyboxes[(skybox.tenant_id, skybox.id)] = skybox
        return skybox
    def find_by_id(self, tenant_id, entity_id):
        return self._skyboxes.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._skyboxes.values() 
                if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._skyboxes:
            del self._skyboxes[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDimensionRepository:
    def __init__(self):
        self._dimensions = {}
        self._next_id = 1
    def save(self, dimension):
        if dimension.id is None:
            from src.domain.value_objects.common import EntityId
            dimension.id = EntityId(self._next_id)
            self._next_id += 1
        self._dimensions[(dimension.tenant_id, dimension.id)] = dimension
        return dimension
    def find_by_id(self, tenant_id, entity_id):
        return self._dimensions.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [d for d in self._dimensions.values() 
                if d.tenant_id == tenant_id and d.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._dimensions:
            del self._dimensions[(tenant_id, entity_id)]
            return True
        return False

class InMemoryPocketDimensionRepository:
    def __init__(self):
        self._pocket_dimensions = {}
        self._next_id = 1
    def save(self, pocket_dimension):
        if pocket_dimension.id is None:
            from src.domain.value_objects.common import EntityId
            pocket_dimension.id = EntityId(self._next_id)
            self._next_id += 1
        self._pocket_dimensions[(pocket_dimension.tenant_id, pocket_dimension.id)] = pocket_dimension
        return pocket_dimension
    def find_by_id(self, tenant_id, entity_id):
        return self._pocket_dimensions.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [p for p in self._pocket_dimensions.values() 
                if p.tenant_id == tenant_id and p.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._pocket_dimensions:
            del self._pocket_dimensions[(tenant_id, entity_id)]
            return True
        return False

# Inventory/Crafting Repositories (9)
class InMemoryInventoryRepository:
    def __init__(self):
        self._inventories = {}
        self._next_id = 1
    def save(self, inventory):
        if inventory.id is None:
            from src.domain.value_objects.common import EntityId
            inventory.id = EntityId(self._next_id)
            self._next_id += 1
        self._inventories[(inventory.tenant_id, inventory.id)] = inventory
        return inventory
    def find_by_id(self, tenant_id, entity_id):
        return self._inventories.get((tenant_id, entity_id))
    def list_by_character(self, tenant_id, character_id, limit=50, offset=0):
        return [i for i in self._inventories.values() 
                if i.tenant_id == tenant_id and i.character_id == character_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._inventories:
            del self._inventories[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCraftingRecipeRepository:
    def __init__(self):
        self._recipes = {}
        self._next_id = 1
    def save(self, recipe):
        if recipe.id is None:
            from src.domain.value_objects.common import EntityId
            recipe.id = EntityId(self._next_id)
            self._next_id += 1
        self._recipes[(recipe.tenant_id, recipe.id)] = recipe
        return recipe
    def find_by_id(self, tenant_id, entity_id):
        return self._recipes.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._recipes.values() 
                if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._recipes:
            del self._recipes[(tenant_id, entity_id)]
            return True
        return False

class InMemoryMaterialRepository:
    def __init__(self):
        self._materials = {}
        self._next_id = 1
    def save(self, material):
        if material.id is None:
            from src.domain.value_objects.common import EntityId
            material.id = EntityId(self._next_id)
            self._next_id += 1
        self._materials[(material.tenant_id, material.id)] = material
        return material
    def find_by_id(self, tenant_id, entity_id):
        return self._materials.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [m for m in self._materials.values() 
                if m.tenant_id == tenant_id and m.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._materials:
            del self._materials[(tenant_id, entity_id)]
            return True
        return False

class InMemoryComponentRepository:
    def __init__(self):
        self._components = {}
        self._next_id = 1
    def save(self, component):
        if component.id is None:
            from src.domain.value_objects.common import EntityId
            component.id = EntityId(self._next_id)
            self._next_id += 1
        self._components[(component.tenant_id, component.id)] = component
        return component
    def find_by_id(self, tenant_id, entity_id):
        return self._components.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [c for c in self._components.values() 
                if c.tenant_id == tenant_id and c.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._components:
            del self._components[(tenant_id, entity_id)]
            return True
        return False

class InMemoryBlueprintRepository:
    def __init__(self):
        self._blueprints = {}
        self._next_id = 1
    def save(self, blueprint):
        if blueprint.id is None:
            from src.domain.value_objects.common import EntityId
            blueprint.id = EntityId(self._next_id)
            self._next_id += 1
        self._blueprints[(blueprint.tenant_id, blueprint.id)] = blueprint
        return blueprint
    def find_by_id(self, tenant_id, entity_id):
        return self._blueprints.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [b for b in self._blueprints.values() 
                if b.tenant_id == tenant_id and b.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._blueprints:
            del self._blueprints[(tenant_id, entity_id)]
            return True
        return False

class InMemoryEnchantmentRepository:
    def __init__(self):
        self._enchantments = {}
        self._next_id = 1
    def save(self, enchantment):
        if enchantment.id is None:
            from src.domain.value_objects.common import EntityId
            enchantment.id = EntityId(self._next_id)
            self._next_id += 1
        self._enchantments[(enchantment.tenant_id, enchantment.id)] = enchantment
        return enchantment
    def find_by_id(self, tenant_id, entity_id):
        return self._enchantments.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._enchantments.values() 
                if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._enchantments:
            del self._enchantments[(tenant_id, entity_id)]
            return True
        return False

class InMemorySocketRepository:
    def __init__(self):
        self._sockets = {}
        self._next_id = 1
    def save(self, socket):
        if socket.id is None:
            from src.domain.value_objects.common import EntityId
            socket.id = EntityId(self._next_id)
            self._next_id += 1
        self._sockets[(socket.tenant_id, socket.id)] = socket
        return socket
    def find_by_id(self, tenant_id, entity_id):
        return self._sockets.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._sockets.values() 
                if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._sockets:
            del self._sockets[(tenant_id, entity_id)]
            return True
        return False

class InMemoryRuneRepository:
    def __init__(self):
        self._runes = {}
        self._next_id = 1
    def save(self, rune):
        if rune.id is None:
            from src.domain.value_objects.common import EntityId
            rune.id = EntityId(self._next_id)
            self._next_id += 1
        self._runes[(rune.tenant_id, rune.id)] = rune
        return rune
    def find_by_id(self, tenant_id, entity_id):
        return self._runes.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._runes.values() 
                if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._runes:
            del self._runes[(tenant_id, entity_id)]
            return True
        return False

class InMemoryGlyphRepository:
    def __init__(self):
        self._glyphs = {}
        self._next_id = 1
    def save(self, glyph):
        if glyph.id is None:
            from src.domain.value_objects.common import EntityId
            glyph.id = EntityId(self._next_id)
            self._next_id += 1
        self._glyphs[(glyph.tenant_id, glyph.id)] = glyph
        return glyph
    def find_by_id(self, tenant_id, entity_id):
        return self._glyphs.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [g for g in self._glyphs.values() 
                if g.tenant_id == tenant_id and g.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._glyphs:
            del self._glyphs[(tenant_id, entity_id)]
            return True
        return False

# ============================================================================
# PARTY 4: FINAL - ALL REMAINING REPOSITORIES (59 repos)
# ============================================================================

# UGC/Localization/Analytics Repositories (15)
class InMemoryModRepository:
    def __init__(self):
        self._mods = {}
        self._next_id = 1
    def save(self, mod):
        if mod.id is None:
            from src.domain.value_objects.common import EntityId
            mod.id = EntityId(self._next_id)
            self._next_id += 1
        self._mods[(mod.tenant_id, mod.id)] = mod
        return mod
    def find_by_id(self, tenant_id, mod_id):
        return self._mods.get((tenant_id, mod_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [m for m in self._mods.values() if m.tenant_id == tenant_id and m.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, mod_id):
        if (tenant_id, mod_id) in self._mods:
            del self._mods[(tenant_id, mod_id)]
            return True
        return False

class InMemoryCustomMapRepository:
    def __init__(self):
        self._custom_maps = {}
        self._next_id = 1
    def save(self, custom_map):
        if custom_map.id is None:
            from src.domain.value_objects.common import EntityId
            custom_map.id = EntityId(self._next_id)
            self._next_id += 1
        self._custom_maps[(custom_map.tenant_id, custom_map.id)] = custom_map
        return custom_map
    def find_by_id(self, tenant_id, custom_map_id):
        return self._custom_maps.get((tenant_id, custom_map_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [cm for cm in self._custom_maps.values() if cm.tenant_id == tenant_id and cm.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, custom_map_id):
        if (tenant_id, custom_map_id) in self._custom_maps:
            del self._custom_maps[(tenant_id, custom_map_id)]
            return True
        return False

class InMemoryUserScenarioRepository:
    def __init__(self):
        self._scenarios = {}
        self._next_id = 1
    def save(self, scenario):
        if scenario.id is None:
            from src.domain.value_objects.common import EntityId
            scenario.id = EntityId(self._next_id)
            self._next_id += 1
        self._scenarios[(scenario.tenant_id, scenario.id)] = scenario
        return scenario
    def find_by_id(self, tenant_id, scenario_id):
        return self._scenarios.get((tenant_id, scenario_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._scenarios.values() if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, scenario_id):
        if (tenant_id, scenario_id) in self._scenarios:
            del self._scenarios[(tenant_id, scenario_id)]
            return True
        return False

class InMemoryShareCodeRepository:
    def __init__(self):
        self._codes = {}
        self._next_id = 1
    def save(self, code):
        if code.id is None:
            from src.domain.value_objects.common import EntityId
            code.id = EntityId(self._next_id)
            self._next_id += 1
        self._codes[(code.tenant_id, code.id)] = code
        return code
    def find_by_id(self, tenant_id, code_id):
        return self._codes.get((tenant_id, code_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [c for c in self._codes.values() if c.tenant_id == tenant_id and c.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, code_id):
        if (tenant_id, code_id) in self._codes:
            del self._codes[(tenant_id, code_id)]
            return True
        return False

class InMemoryWorkshopEntryRepository:
    def __init__(self):
        self._entries = {}
        self._next_id = 1
    def save(self, entry):
        if entry.id is None:
            from src.domain.value_objects.common import EntityId
            entry.id = EntityId(self._next_id)
            self._next_id += 1
        self._entries[(entry.tenant_id, entry.id)] = entry
        return entry
    def find_by_id(self, tenant_id, entry_id):
        return self._entries.get((tenant_id, entry_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entries.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entry_id):
        if (tenant_id, entry_id) in self._entries:
            del self._entries[(tenant_id, entry_id)]
            return True
        return False

class InMemoryLocalizationRepository:
    def __init__(self):
        self._localizations = {}
        self._next_id = 1
    def save(self, localization):
        if localization.id is None:
            from src.domain.value_objects.common import EntityId
            localization.id = EntityId(self._next_id)
            self._next_id += 1
        self._localizations[(localization.tenant_id, localization.id)] = localization
        return localization
    def find_by_id(self, tenant_id, localization_id):
        return self._localizations.get((tenant_id, localization_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [l for l in self._localizations.values() if l.tenant_id == tenant_id and l.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, localization_id):
        if (tenant_id, localization_id) in self._localizations:
            del self._localizations[(tenant_id, localization_id)]
            return True
        return False

class InMemoryTranslationRepository:
    def __init__(self):
        self._translations = {}
        self._next_id = 1
    def save(self, translation):
        if translation.id is None:
            from src.domain.value_objects.common import EntityId
            translation.id = EntityId(self._next_id)
            self._next_id += 1
        self._translations[(translation.tenant_id, translation.id)] = translation
        return translation
    def find_by_id(self, tenant_id, translation_id):
        return self._translations.get((tenant_id, translation_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._translations.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, translation_id):
        if (tenant_id, translation_id) in self._translations:
            del self._translations[(tenant_id, translation_id)]
            return True
        return False

class InMemoryVoiceOverRepository:
    def __init__(self):
        self._voice_overs = {}
        self._next_id = 1
    def save(self, voice_over):
        if voice_over.id is None:
            from src.domain.value_objects.common import EntityId
            voice_over.id = EntityId(self._next_id)
            self._next_id += 1
        self._voice_overs[(voice_over.tenant_id, voice_over.id)] = voice_over
        return voice_over
    def find_by_id(self, tenant_id, voice_over_id):
        return self._voice_overs.get((tenant_id, voice_over_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [vo for vo in self._voice_overs.values() if vo.tenant_id == tenant_id and vo.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, voice_over_id):
        if (tenant_id, voice_over_id) in self._voice_overs:
            del self._voice_overs[(tenant_id, voice_over_id)]
            return True
        return False

class InMemorySubtitleRepository:
    def __init__(self):
        self._subtitles = {}
        self._next_id = 1
    def save(self, subtitle):
        if subtitle.id is None:
            from src.domain.value_objects.common import EntityId
            subtitle.id = EntityId(self._next_id)
            self._next_id += 1
        self._subtitles[(subtitle.tenant_id, subtitle.id)] = subtitle
        return subtitle
    def find_by_id(self, tenant_id, subtitle_id):
        return self._subtitles.get((tenant_id, subtitle_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._subtitles.values() if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, subtitle_id):
        if (tenant_id, subtitle_id) in self._subtitles:
            del self._subtitles[(tenant_id, subtitle_id)]
            return True
        return False

class InMemoryDubbingRepository:
    def __init__(self):
        self._ dubbings = {}
        self._next_id = 1
    def save(self, dubbing):
        if dubbing.id is None:
            from src.domain.value_objects.common import EntityId
            dubbing.id = EntityId(self._next_id)
            self._next_id += 1
        self._dubbings[(dubbing.tenant_id, dubbing.id)] = dubbing
        return dubbing
    def find_by_id(self, tenant_id, dubbing_id):
        return self._dubbings.get((tenant_id, dubbing_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [d for d in self._dubbings.values() if d.tenant_id == tenant_id and d.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, dubbing_id):
        if (tenant_id, dubbing_id) in self._dubbings:
            del self._dubbings[(tenant_id, dubbing_id)]
            return True
        return False

class InMemoryPlayerMetricRepository:
    def __init__(self):
        self._player_metrics = {}
        self._next_id = 1
    def save(self, player_metric):
        if player_metric.id is None:
            from src.domain.value_objects.common import EntityId
            player_metric.id = EntityId(self._next_id)
            self._next_id += 1
        self._player_metrics[(player_metric.tenant_id, player_metric.id)] = player_metric
        return player_metric
    def find_by_id(self, tenant_id, metric_id):
        return self._player_metrics.get((tenant_id, metric_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [pm for pm in self._player_metrics.values() if pm.tenant_id == tenant_id and pm.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, metric_id):
        if (tenant_id, metric_id) in self._player_metrics:
            del self._player_metrics[(tenant_id, metric_id)]
            return True
        return False

class InMemorySessionDataRepository:
    def __init__(self):
        self._session_data = {}
        self._next_id = 1
    def save(self, session_data):
        if session_data.id is None:
            from src.domain.value_objects.common import EntityId
            session_data.id = EntityId(self._next_id)
            self._next_id += 1
        self._session_data[(session_data.tenant_id, session_data.id)] = session_data
        return session_data
    def find_by_id(self, tenant_id, data_id):
        return self._session_data.get((tenant_id, data_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [sd for sd in self._session_data.values() if sd.tenant_id == tenant_id and sd.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, data_id):
        if (tenant_id, data_id) in self._session_data:
            del self._session_data[(tenant_id, data_id)]
            return True
        return False

class InMemoryHeatmapRepository:
    def __init__(self):
        self._heatmaps = {}
        self._next_id = 1
    def save(self, heatmap):
        if heatmap.id is None:
            from src.domain.value_objects.common import EntityId
            heatmap.id = EntityId(self._next_id)
            self._next_id += 1
        self._heatmaps[(heatmap.tenant_id, heatmap.id)] = heatmap
        return heatmap
    def find_by_id(self, tenant_id, heatmap_id):
        return self._heatmaps.get((tenant_id, heatmap_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [h for h in self._heatmaps.values() if h.tenant_id == tenant_id and h.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, heatmap_id):
        if (tenant_id, heatmap_id) in self._heatmaps:
            del self._heatmaps[(tenant_id, heatmap_id)]
            return True
        return False

class InMemoryDropRateRepository:
    def __init__(self):
        self._drop_rates = {}
        self._next_id = 1
    def save(self, drop_rate):
        if drop_rate.id is None:
            from src.domain.value_objects.common import EntityId
            drop_rate.id = EntityId(self._next_id)
            self._next_id += 1
        self._drop_rates[(drop_rate.tenant_id, drop_rate.id)] = drop_rate
        return drop_rate
    def find_by_id(self, tenant_id, drop_rate_id):
        return self._drop_rates.get((tenant_id, drop_rate_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [dr for dr in self._drop_rates.values() if dr.tenant_id == tenant_id and dr.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, drop_rate_id):
        if (tenant_id, drop_rate_id) in self._drop_rates:
            del self._drop_rates[(tenant_id, drop_rate_id)]
            return True
        return False

class InMemoryConversionRateRepository:
    def __init__(self):
        self._conversion_rates = {}
        self._next_id = 1
    def save(self, conversion_rate):
        if conversion_rate.id is None:
            from src.domain.value_objects.common import EntityId
            conversion_rate.id = EntityId(self._next_id)
            self._next_id += 1
        self._conversion_rates[(conversion_rate.tenant_id, conversion_rate.id)] = conversion_rate
        return conversion_rate
    def find_by_id(self, tenant_id, conversion_rate_id):
        return self._conversion_rates.get((tenant_id, conversion_rate_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [cr for cr in self._conversion_rates.values() if cr.tenant_id == tenant_id and cr.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, conversion_rate_id):
        if (tenant_id, conversion_rate_id) in self._conversion_rates:
            del self._conversion_rates[(tenant_id, conversion_rate_id)]
            return True
        return False

# LegendaryItems Repositories (6)
class InMemoryLegendaryWeaponRepository:
    def __init__(self):
        self._weapons = {}
        self._next_id = 1
    def save(self, weapon):
        if weapon.id is None:
            from src.domain.value_objects.common import EntityId
            weapon.id = EntityId(self._next_id)
            self._next_id += 1
        self._weapons[(weapon.tenant_id, weapon.id)] = weapon
        return weapon
    def find_by_id(self, tenant_id, weapon_id):
        return self._weapons.get((tenant_id, weapon_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [w for w in self._weapons.values() if w.tenant_id == tenant_id and w.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, weapon_id):
        if (tenant_id, weapon_id) in self._weapons:
            del self._weapons[(tenant_id, weapon_id)]
            return True
        return False

class InMemoryMythicalArmorRepository:
    def __init__(self):
        self._armors = {}
        self._next_id = 1
    def save(self, armor):
        if armor.id is None:
            from src.domain.value_objects.common import EntityId
            armor.id = EntityId(self._next_id)
            self._next_id += 1
        self._armors[(armor.tenant_id, armor.id)] = armor
        return armor
    def find_by_id(self, tenant_id, armor_id):
        return self._armors.get((tenant_id, armor_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [a for a in self._armors.values() if a.tenant_id == tenant_id and a.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, armor_id):
        if (tenant_id, armor_id) in self._armors:
            del self._armors[(tenant_id, armor_id)]
            return True
        return False

class InMemoryDivineItemRepository:
    def __init__(self):
        self._divine_items = {}
        self._next_id = 1
    def save(self, divine_item):
        if divine_item.id is None:
            from src.domain.value_objects.common import EntityId
            divine_item.id = EntityId(self._next_id)
            self._next_id += 1
        self._divine_items[(divine_item.tenant_id, divine_item.id)] = divine_item
        return divine_item
    def find_by_id(self, tenant_id, divine_item_id):
        return self._divine_items.get((tenant_id, divine_item_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [di for di in self._divine_items.values() if di.tenant_id == tenant_id and di.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, divine_item_id):
        if (tenant_id, divine_item_id) in self._divine_items:
            del self._divine_items[(tenant_id, divine_item_id)]
            return True
        return False

class InMemoryCursedItemRepository:
    def __init__(self):
        self._cursed_items = {}
        self._next_id = 1
    def save(self, cursed_item):
        if cursed_item.id is None:
            from src.domain.value_objects.common import EntityId
            cursed_item.id = EntityId(self._next_id)
            self._next_id += 1
        self._cursed_items[(cursed_item.tenant_id, cursed_item.id)] = cursed_item
        return cursed_item
    def find_by_id(self, tenant_id, cursed_item_id):
        return self._cursed_items.get((tenant_id, cursed_item_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [ci for ci in self._cursed_items.values() if ci.tenant_id == tenant_id and ci.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, cursed_item_id):
        if (tenant_id, cursed_item_id) in self._cursed_items:
            del self._cursed_items[(tenant_id, cursed_item_id)]
            return True
        return False

class InMemoryArtifactSetRepository:
    def __init__(self):
        self._artifact_sets = {}
        self._next_id = 1
    def save(self, artifact_set):
        if artifact_set.id is None:
            from src.domain.value_objects.common import EntityId
            artifact_set.id = EntityId(self._next_id)
            self._next_id += 1
        self._artifact_sets[(artifact_set.tenant_id, artifact_set.id)] = artifact_set
        return artifact_set
    def find_by_id(self, tenant_id, artifact_set_id):
        return self._artifact_sets.get((tenant_id, artifact_set_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [as_ for as_ in self._artifact_sets.values() if as_.tenant_id == tenant_id and as_.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, artifact_set_id):
        if (tenant_id, artifact_set_id) in self._artifact_sets:
            del self._artifact_sets[(tenant_id, artifact_set_id)]
            return True
        return False

class InMemoryRelicCollectionRepository:
    def __init__(self):
        self._relic_collections = {}
        self._next_id = 1
    def save(self, relic_collection):
        if relic_collection.id is None:
            from src.domain.value_objects.common import EntityId
            relic_collection.id = EntityId(self._next_id)
            self._next_id += 1
        self._relic_collections[(relic_collection.tenant_id, relic_collection.id)] = relic_collection
        return relic_collection
    def find_by_id(self, tenant_id, relic_collection_id):
        return self._relic_collections.get((tenant_id, relic_collection_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [rc for rc in self._relic_collections.values() if rc.tenant_id == tenant_id and rc.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, relic_collection_id):
        if (tenant_id, relic_collection_id) in self._relic_collections:
            del self._relic_collections[(tenant_id, relic_collection_id)]
            return True
        return False

# Companions/Transport Repositories (9)
class InMemoryPetRepository:
    def __init__(self):
        self._pets = {}
        self._next_id = 1
    def save(self, pet):
        if pet.id is None:
            from src.domain.value_objects.common import EntityId
            pet.id = EntityId(self._next_id)
            self._next_id += 1
        self._pets[(pet.tenant_id, pet.id)] = pet
        return pet
    def find_by_id(self, tenant_id, pet_id):
        return self._pets.get((tenant_id, pet_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [p for p in self._pets.values() if p.tenant_id == tenant_id and p.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, pet_id):
        if (tenant_id, pet_id) in self._pets:
            del self._pets[(tenant_id, pet_id)]
            return True
        return False

class InMemoryMountRepository:
    def __init__(self):
        self._mounts = {}
        self._next_id = 1
    def save(self, mount):
        if mount.id is None:
            from src.domain.value_objects.common import EntityId
            mount.id = EntityId(self._next_id)
            self._next_id += 1
        self._mounts[(mount.tenant_id, mount.id)] = mount
        return mount
    def find_by_id(self, tenant_id, mount_id):
        return self._mounts.get((tenant_id, mount_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [m for m in self._mounts.values() if m.tenant_id == tenant_id and m.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, mount_id):
        if (tenant_id, mount_id) in self._mounts:
            del self._mounts[(tenant_id, mount_id)]
            return True
        return False

class InMemoryFamiliarRepository:
    def __init__(self):
        self._familiars = {}
        self._next_id = 1
    def save(self, familiar):
        if familiar.id is None:
            from src.domain.value_objects.common import EntityId
            familiar.id = EntityId(self._next_id)
            self._next_id += 1
        self._familiars[(familiar.tenant_id, familiar.id)] = familiar
        return familiar
    def find_by_id(self, tenant_id, familiar_id):
        return self._familiars.get((tenant_id, familiar_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [f for f in self._familiars.values() if f.tenant_id == tenant_id and f.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, familiar_id):
        if (tenant_id, familiar_id) in self._familiars:
            del self._familiars[(tenant_id, familiar_id)]
            return True
        return False

class InMemoryMountEquipmentRepository:
    def __init__(self):
        self._mount_equipment = {}
        self._next_id = 1
    def save(self, mount_equipment):
        if mount_equipment.id is None:
            from src.domain.value_objects.common import EntityId
            mount_equipment.id = EntityId(self._next_id)
            self._next_id += 1
        self._mount_equipment[(mount_equipment.tenant_id, mount_equipment.id)] = mount_equipment
        return mount_equipment
    def find_by_id(self, tenant_id, mount_equipment_id):
        return self._mount_equipment.get((tenant_id, mount_equipment_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [me for me in self._mount_equipment.values() if me.tenant_id == tenant_id and me.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, mount_equipment_id):
        if (tenant_id, mount_equipment_id) in self._mount_equipment:
            del self._mount_equipment[(tenant_id, mount_equipment_id)]
            return True
        return False

class InMemoryVehicleRepository:
    def __init__(self):
        self._vehicles = {}
        self._next_id = 1
    def save(self, vehicle):
        if vehicle.id is None:
            from src.domain.value_objects.common import EntityId
            vehicle.id = EntityId(self._next_id)
            self._next_id += 1
        self._vehicles[(vehicle.tenant_id, vehicle.id)] = vehicle
        return vehicle
    def find_by_id(self, tenant_id, vehicle_id):
        return self._vehicles.get((tenant_id, vehicle_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [v for v in self._vehicles.values() if v.tenant_id == tenant_id and v.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, vehicle_id):
        if (tenant_id, vehicle_id) in self._vehicles:
            del self._vehicles[(tenant_id, vehicle_id)]
            return True
        return False

class InMemorySpaceshipRepository:
    def __init__(self):
        self._spaceships = {}
        self._next_id = 1
    def save(self, spaceship):
        if spaceship.id is None:
            from src.domain.value_objects.common import EntityId
            spaceship.id = EntityId(self._next_id)
            self._next_id += 1
        self._spaceships[(spaceship.tenant_id, spaceship.id)] = spaceship
        return spaceship
    def find_by_id(self, tenant_id, spaceship_id):
        return self._spaceships.get((tenant_id, spaceship_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._spaceships.values() if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, spaceship_id):
        if (tenant_id, spaceship_id) in self._spaceships:
            del self._spaceships[(tenant_id, spaceship_id)]
            return True
        return False

class InMemoryAirshipRepository:
    def __init__(self):
        self._airships = {}
        self._next_id = 1
    def save(self, airship):
        if airship.id is None:
            from src.domain.value_objects.common import EntityId
            airship.id = EntityId(self._next_id)
            self._next_id += 1
        self._airships[(airship.tenant_id, airship.id)] = airship
        return airship
    def find_by_id(self, tenant_id, airship_id):
        return self._airships.get((tenant_id, airship_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [a for a in self._airships.values() if a.tenant_id == tenant_id and a.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, airship_id):
        if (tenant_id, airship_id) in self._airships:
            del self._airships[(tenant_id, airship_id)]
            return True
        return False

class InMemoryPortalRepository:
    def __init__(self):
        self._portals = {}
        self._next_id = 1
    def save(self, portal):
        if portal.id is None:
            from src.domain.value_objects.common import EntityId
            portal.id = EntityId(self._next_id)
            self._next_id += 1
        self._portals[(portal.tenant_id, portal.id)] = portal
        return portal
    def find_by_id(self, tenant_id, portal_id):
        return self._portals.get((tenant_id, portal_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [p for p in self._portals.values() if p.tenant_id == tenant_id and p.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, portal_id):
        if (tenant_id, portal_id) in self._portals:
            del self._portals[(tenant_id, portal_id)]
            return True
        return False

class InMemoryTeleporterRepository:
    def __init__(self):
        self._teleporters = {}
        self._next_id = 1
    def save(self, teleporter):
        if teleporter.id is None:
            from src.domain.value_objects.common import EntityId
            teleporter.id = EntityId(self._next_id)
            self._next_id += 1
        self._teleporters[(teleporter.tenant_id, teleporter.id)] = teleporter
        return teleporter
    def find_by_id(self, tenant_id, teleporter_id):
        return self._teleporters.get((tenant_id, teleporter_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._teleporters.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, teleporter_id):
        if (tenant_id, teleporter_id) in self._teleporters:
            del self._teleporters[(tenant_id, teleporter_id)]
            return True
        return False

# Institutions Repositories (7)
class InMemoryAcademyRepository:
    def __init__(self):
        self._academies = {}
        self._next_id = 1
    def save(self, academy):
        if academy.id is None:
            from src.domain.value_objects.common import EntityId
            academy.id = EntityId(self._next_id)
            self._next_id += 1
        self._academies[(academy.tenant_id, academy.id)] = academy
        return academy
    def find_by_id(self, tenant_id, academy_id):
        return self._academies.get((tenant_id, academy_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [a for a in self._academies.values() if a.tenant_id == tenant_id and a.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, academy_id):
        if (tenant_id, academy_id) in self._academies:
            del self._academies[(tenant_id, academy_id)]
            return True
        return False

class InMemoryUniversityRepository:
    def __init__(self):
        self._universities = {}
        self._next_id = 1
    def save(self, university):
        if university.id is None:
            from src.domain.value_objects.common import EntityId
            university.id = EntityId(self._next_id)
            self._next_id += 1
        self._universities[(university.tenant_id, university.id)] = university
        return university
    def find_by_id(self, tenant_id, university_id):
        return self._universities.get((tenant_id, university_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [u for u in self._universities.values() if u.tenant_id == tenant_id and u.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, university_id):
        if (tenant_id, university_id) in self._universities:
            del self._universities[(tenant_id, university_id)]
            return True
        return False

class InMemorySchoolRepository:
    def __init__(self):
        self._schools = {}
        self._next_id = 1
    def save(self, school):
        if school.id is None:
            from src.domain.value_objects.common import EntityId
            school.id = EntityId(self._next_id)
            self._next_id += 1
        self._schools[(school.tenant_id, school.id)] = school
        return school
    def find_by_id(self, tenant_id, school_id):
        return self._schools.get((tenant_id, school_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._schools.values() if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, school_id):
        if (tenant_id, school_id) in self._schools:
            del self._schools[(tenant_id, school_id)]
            return True
        return False

class InMemoryLibraryRepository:
    def __init__(self):
        self._libraries = {}
        self._next_id = 1
    def save(self, library):
        if library.id is None:
            from src.domain.value_objects.common import EntityId
            library.id = EntityId(self._next_id)
            self._next_id += 1
        self._libraries[(library.tenant_id, library.id)] = library
        return library
    def find_by_id(self, tenant_id, library_id):
        return self._libraries.get((tenant_id, library_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [l for l in self._libraries.values() if l.tenant_id == tenant_id and l.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, library_id):
        if (tenant_id, library_id) in self._libraries:
            del self._libraries[(tenant_id, library_id)]
            return True
        return False

class InMemoryResearchCenterRepository:
    def __init__(self):
        self._research_centers = {}
        self._next_id = 1
    def save(self, research_center):
        if research_center.id is None:
            from src.domain.value_objects.common import EntityId
            research_center.id = EntityId(self._next_id)
            self._next_id += 1
        self._research_centers[(research_center.tenant_id, research_center.id)] = research_center
        return research_center
    def find_by_id(self, tenant_id, research_center_id):
        return self._research_centers.get((tenant_id, research_center_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [rc for rc in self._research_centers.values() if rc.tenant_id == tenant_id and rc.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, research_center_id):
        if (tenant_id, research_center_id) in self._research_centers:
            del self._research_centers[(tenant_id, research_center_id)]
            return True
        return False

class InMemoryArchiveRepository:
    def __init__(self):
        self._archives = {}
        self._next_id = 1
    def save(self, archive):
        if archive.id is None:
            from src.domain.value_objects.common import EntityId
            archive.id = EntityId(self._next_id)
            self._next_id += 1
        self._archives[(archive.tenant_id, archive.id)] = archive
        return archive
    def find_by_id(self, tenant_id, archive_id):
        return self._archives.get((tenant_id, archive_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [a for a in self._archives.values() if a.tenant_id == tenant_id and a.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, archive_id):
        if (tenant_id, archive_id) in self._archives:
            del self._archives[(tenant_id, archive_id)]
            return True
        return False

class InMemoryMuseumRepository:
    def __init__(self):
        self._museums = {}
        self._next_id = 1
    def save(self, museum):
        if museum.id is None:
            from src.domain.value_objects.common import EntityId
            museum.id = EntityId(self._next_id)
            self._next_id += 1
        self._museums[(museum.tenant_id, museum.id)] = museum
        return museum
    def find_by_id(self, tenant_id, museum_id):
        return self._museums.get((tenant_id, museum_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [m for m in self._museums.values() if m.tenant_id == tenant_id and m.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, museum_id):
        if (tenant_id, museum_id) in self._museums:
            del self._museums[(tenant_id, museum_id)]
            return True
        return False

# Media Repositories (7)
class InMemoryNewspaperRepository:
    def __init__(self):
        self._newspapers = {}
        self._next_id = 1
    def save(self, newspaper):
        if newspaper.id is None:
            from src.domain.value_objects.common import EntityId
            newspaper.id = EntityId(self._next_id)
            self._next_id += 1
        self._newspapers[(newspaper.tenant_id, newspaper.id)] = newspaper
        return newspaper
    def find_by_id(self, tenant_id, newspaper_id):
        return self._newspapers.get((tenant_id, newspaper_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [n for n in self._newspapers.values() if n.tenant_id == tenant_id and n.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, newspaper_id):
        if (tenant_id, newspaper_id) in self._newspapers:
            del self._newspapers[(tenant_id, newspaper_id)]
            return True
        return False

class InMemoryRadioRepository:
    def __init__(self):
        self._radios = {}
        self._next_id = 1
    def save(self, radio):
        if radio.id is None:
            from src.domain.value_objects.common import EntityId
            radio.id = EntityId(self._next_id)
            self._next_id += 1
        self._radios[(radio.tenant_id, radio.id)] = radio
        return radio
    def find_by_id(self, tenant_id, radio_id):
        return self._radios.get((tenant_id, radio_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._radios.values() if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, radio_id):
        if (tenant_id, radio_id) in self._radios:
            del self._radios[(tenant_id, radio_id)]
            return True
        return False

class InMemoryTelevisionRepository:
    def __init__(self):
        self._televisions = {}
        self._next_id = 1
    def save(self, television):
        if television.id is None:
            from src.domain.value_objects.common import EntityId
            television.id = EntityId(self._next_id)
            self._next_id += 1
        self._televisions[(television.tenant_id, television.id)] = television
        return television
    def find_by_id(self, tenant_id, television_id):
        return self._televisions.get((tenant_id, television_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._televisions.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, television_id):
        if (tenant_id, television_id) in self._televisions:
            del self._televisions[(tenant_id, television_id)]
            return True
        return False

class InMemoryInternetRepository:
    def __init__(self):
        self._internets = {}
        self._next_id = 1
    def save(self, internet):
        if internet.id is None:
            from src.domain.value_objects.common import EntityId
            internet.id = EntityId(self._next_id)
            self._next_id += 1
        self._internets[(internet.tenant_id, internet.id)] = internet
        return internet
    def find_by_id(self, tenant_id, internet_id):
        return self._internets.get((tenant_id, internet_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [i for i in self._internets.values() if i.tenant_id == tenant_id and i.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, internet_id):
        if (tenant_id, internet_id) in self._internets:
            del self._internets[(tenant_id, internet_id)]
            return True
        return False

class InMemorySocialMediaRepository:
    def __init__(self):
        self._social_medias = {}
        self._next_id = 1
    def save(self, social_media):
        if social_media.id is None:
            from src.domain.value_objects.common import EntityId
            social_media.id = EntityId(self._next_id)
            self._next_id += 1
        self._social_medias[(social_media.tenant_id, social_media.id)] = social_media
        return social_media
    def find_by_id(self, tenant_id, social_media_id):
        return self._social_medias.get((tenant_id, social_media_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [sm for sm in self._social_medias.values() if sm.tenant_id == tenant_id and sm.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, social_media_id):
        if (tenant_id, social_media_id) in self._social_medias:
            del self._social_medias[(tenant_id, social_media_id)]
            return True
        return False

class InMemoryPropagandaRepository:
    def __init__(self):
        self._propaganda = {}
        self._next_id = 1
    def save(self, propaganda):
        if propaganda.id is None:
            from src.domain.value_objects.common import EntityId
            propaganda.id = EntityId(self._next_id)
            self._next_id += 1
        self._propaganda[(propaganda.tenant_id, propaganda.id)] = propaganda
        return propaganda
    def find_by_id(self, tenant_id, propaganda_id):
        return self._propaganda.get((tenant_id, propaganda_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [p for p in self._propaganda.values() if p.tenant_id == tenant_id and p.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, propaganda_id):
        if (tenant_id, propaganda_id) in self._propaganda:
            del self._propaganda[(tenant_id, propaganda_id)]
            return True
        return False

class InMemoryRumorRepository:
    def __init__(self):
        self._rumors = {}
        self._next_id = 1
    def save(self, rumor):
        if rumor.id is None:
            from src.domain.value_objects.common import EntityId
            rumor.id = EntityId(self._next_id)
            self._next_id += 1
        self._rumors[(rumor.tenant_id, rumor.id)] = rumor
        return rumor
    def find_by_id(self, tenant_id, rumor_id):
        return self._rumors.get((tenant_id, rumor_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._rumors.values() if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, rumor_id):
        if (tenant_id, rumor_id) in self._rumors:
            del self._rumors[(tenant_id, rumor_id)]
            return True
        return False

# Secrets Repositories (8)
class InMemorySecretAreaRepository:
    def __init__(self):
        self._secret_areas = {}
        self._next_id = 1
    def save(self, secret_area):
        if secret_area.id is None:
            from src.domain.value_objects.common import EntityId
            secret_area.id = EntityId(self._next_id)
            self._next_id += 1
        self._secret_areas[(secret_area.tenant_id, secret_area.id)] = secret_area
        return secret_area
    def find_by_id(self, tenant_id, secret_area_id):
        return self._secret_areas.get((tenant_id, secret_area_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [sa for sa in self._secret_areas.values() if sa.tenant_id == tenant_id and sa.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, secret_area_id):
        if (tenant_id, secret_area_id) in self._secret_areas:
            del self._secret_areas[(tenant_id, secret_area_id)]
            return True
        return False

class InMemoryHiddenPathRepository:
    def __init__(self):
        self._hidden_paths = {}
        self._next_id = 1
    def save(self, hidden_path):
        if hidden_path.id is None:
            from src.domain.value_objects.common import EntityId
            hidden_path.id = EntityId(self._next_id)
            self._next_id += 1
        self._hidden_paths[(hidden_path.tenant_id, hidden_path.id)] = hidden_path
        return hidden_path
    def find_by_id(self, tenant_id, hidden_path_id):
        return self._hidden_paths.get((tenant_id, hidden_path_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [hp for hp in self._hidden_paths.values() if hp.tenant_id == tenant_id and hp.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, hidden_path_id):
        if (tenant_id, hidden_path_id) in self._hidden_paths:
            del self._hidden_paths[(tenant_id, hidden_path_id)]
            return True
        return False

class InMemoryEasterEggRepository:
    def __init__(self):
        self._easter_eggs = {}
        self._next_id = 1
    def save(self, easter_egg):
        if easter_egg.id is None:
            from src.domain.value_objects.common import EntityId
            easter_egg.id = EntityId(self._next_id)
            self._next_id += 1
        self._easter_eggs[(easter_egg.tenant_id, easter_egg.id)] = easter_egg
        return easter_egg
    def find_by_id(self, tenant_id, easter_egg_id):
        return self._easter_eggs.get((tenant_id, easter_egg_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [ee for ee in self._easter_eggs.values() if ee.tenant_id == tenant_id and ee.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, easter_egg_id):
        if (tenant_id, easter_egg_id) in self._easter_eggs:
            del self._easter_eggs[(tenant_id, easter_egg_id)]
            return True
        return False

class InMemoryMysteryRepository:
    def __init__(self):
        self._mysteries = {}
        self._next_id = 1
    def save(self, mystery):
        if mystery.id is None:
            from src.domain.value_objects.common import EntityId
            mystery.id = EntityId(self._next_id)
            self._next_id += 1
        self._mysteries[(mystery.tenant_id, mystery.id)] = mystery
        return mystery
    def find_by_id(self, tenant_id, mystery_id):
        return self._mysteries.get((tenant_id, mystery_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [m for m in self._mysteries.values() if m.tenant_id == tenant_id and m.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, mystery_id):
        if (tenant_id, mystery_id) in self._mysteries:
            del self._mysteries[(tenant_id, mystery_id)]
            return True
        return False

class InMemoryEnigmaRepository:
    def __init__(self):
        self._enigmas = {}
        self._next_id = 1
    def save(self, enigma):
        if enigma.id is None:
            from src.domain.value_objects.common import EntityId
            enigma.id = EntityId(self._next_id)
            self._next_id += 1
        self._enigmas[(enigma.tenant_id, enigma.id)] = enigma
        return enigma
    def find_by_id(self, tenant_id, enigma_id):
        return self._enigmas.get((tenant_id, enigma_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._enigmas.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, enigma_id):
        if (tenant_id, enigma_id) in self._enigmas:
            del self._enigmas[(tenant_id, enigma_id)]
            return True
        return False

class InMemoryRiddleRepository:
    def __init__(self):
        self._riddles = {}
        self._next_id = 1
    def save(self, riddle):
        if riddle.id is None:
            from src.domain.value_objects.common import EntityId
            riddle.id = EntityId(self._next_id)
            self._next_id += 1
        self._riddles[(riddle.tenant_id, riddle.id)] = riddle
        return riddle
    def find_by_id(self, tenant_id, riddle_id):
        return self._riddles.get((tenant_id, riddle_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._riddles.values() if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, riddle_id):
        if (tenant_id, riddle_id) in self._riddles:
            del self._riddles[(tenant_id, riddle_id)]
            return True
        return False

class InMemoryPuzzleRepository:
    def __init__(self):
        self._puzzles = {}
        self._next_id = 1
    def save(self, puzzle):
        if puzzle.id is None:
            from src.domain.value_objects.common import EntityId
            puzzle.id = EntityId(self._next_id)
            self._next_id += 1
        self._puzzles[(puzzle.tenant_id, puzzle.id)] = puzzle
        return puzzle
    def find_by_id(self, tenant_id, puzzle_id):
        return self._puzzles.get((tenant_id, puzzle_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [p for p in self._puzzles.values() if p.tenant_id == tenant_id and p.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, puzzle_id):
        if (tenant_id, puzzle_id) in self._puzzles:
            del self._puzzles[(tenant_id, puzzle_id)]
            return True
        return False

class InMemoryTrapRepository:
    def __init__(self):
        self._traps = {}
        self._next_id = 1
    def save(self, trap):
        if trap.id is None:
            from src.domain.value_objects.common import EntityId
            trap.id = EntityId(self._next_id)
            self._next_id += 1
        self._traps[(trap.tenant_id, trap.id)] = trap
        return trap
    def find_by_id(self, tenant_id, trap_id):
        return self._traps.get((tenant_id, trap_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._traps.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, trap_id):
        if (tenant_id, trap_id) in self._traps:
            del self._traps[(tenant_id, trap_id)]
            return True
        return False

# Art Repositories (7)
class InMemoryFestivalRepository:
    def __init__(self):
        self._festivals = {}
        self._next_id = 1
    def save(self, festival):
        if festival.id is None:
            from src.domain.value_objects.common import EntityId
            festival.id = EntityId(self._next_id)
            self._next_id += 1
        self._festivals[(festival.tenant_id, festival.id)] = festival
        return festival
    def find_by_id(self, tenant_id, festival_id):
        return self._festivals.get((tenant_id, festival_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [f for f in self._festivals.values() if f.tenant_id == tenant_id and f.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, festival_id):
        if (tenant_id, festival_id) in self._festivals:
            del self._festivals[(tenant_id, festival_id)]
            return True
        return False

class InMemoryCelebrationRepository:
    def __init__(self):
        self._celebrations = {}
        self._next_id = 1
    def save(self, celebration):
        if celebration.id is None:
            from src.domain.value_objects.common import EntityId
            celebration.id = EntityId(self._next_id)
            self._next_id += 1
        self._celebrations[(celebration.tenant_id, celebration.id)] = celebration
        return celebration
    def find_by_id(self, tenant_id, celebration_id):
        return self._celebrations.get((tenant_id, celebration_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [c for c in self._celebrations.values() if c.tenant_id == tenant_id and c.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, celebration_id):
        if (tenant_id, celebration_id) in self._celebrations:
            del self._celebrations[(tenant_id, celebration_id)]
            return True
        return False

class InMemoryCeremonyRepository:
    def __init__(self):
        self._ceremonies = {}
        self._next_id = 1
    def save(self, ceremony):
        if ceremony.id is None:
            from src.domain.value_objects.common import EntityId
            ceremony.id = EntityId(self._next_id)
            self._next_id += 1
        self._ceremonies[(ceremony.tenant_id, ceremony.id)] = ceremony
        return ceremony
    def find_by_id(self, tenant_id, ceremony_id):
        return self._ceremonies.get((tenant_id, ceremony_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [c for c in self._ceremonies.values() if c.tenant_id == tenant_id and c.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, ceremony_id):
        if (tenant_id, ceremony_id) in self._ceremonies:
            del self._ceremonies[(tenant_id, ceremony_id)]
            return True
        return False

class InMemoryConcertRepository:
    def __init__(self):
        self._concerts = {}
        self._next_id = 1
    def save(self, concert):
        if concert.id is None:
            from src.domain.value_objects.common import EntityId
            concert.id = EntityId(self._next_id)
            self._next_id += 1
        self._concerts[(concert.tenant_id, concert.id)] = concert
        return concert
    def find_by_id(self, tenant_id, concert_id):
        return self._concerts.get((tenant_id, concert_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [c for c in self._concerts.values() if c.tenant_id == tenant_id and c.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, concert_id):
        if (tenant_id, concert_id) in self._concerts:
            del self._concerts[(tenant_id, concert_id)]
            return True
        return False

class InMemoryExhibitionRepository:
    def __init__(self):
        self._exhibitions = {}
        self._next_id = 1
    def save(self, exhibition):
        if exhibition.id is None:
            from src.domain.value_objects.common import EntityId
            exhibition.id = EntityId(self._next_id)
            self._next_id += 1
        self._exhibitions[(exhibition.tenant_id, exhibition.id)] = exhibition
        return exhibition
    def find_by_id(self, tenant_id, exhibition_id):
        return self._exhibitions.get((tenant_id, exhibition_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._exhibitions.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, exhibition_id):
        if (tenant_id, exhibition_id) in self._exhibitions:
            del self._exhibitions[(tenant_id, exhibition_id)]
            return True
        return False

class InMemoryCompetitionRepository:
    def __init__(self):
        self._competitions = {}
        self._next_id = 1
    def save(self, competition):
        if competition.id is None:
            from src.domain.value_objects.common import EntityId
            competition.id = EntityId(self._next_id)
            self._next_id += 1
        self._competitions[(competition.tenant_id, competition.id)] = competition
        return competition
    def find_by_id(self, tenant_id, competition_id):
        return self._competitions.get((tenant_id, competition_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [c for c in self._competitions.values() if c.tenant_id == tenant_id and c.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, competition_id):
        if (tenant_id, competition_id) in self._competitions:
            del self._competitions[(tenant_id, competition_id)]
            return True
        return False

class InMemoryTournamentRepository:
    def __init__(self):
        self._tournaments = {}
        self._next_id = 1
    def save(self, tournament):
        if tournament.id is None:
            from src.domain.value_objects.common import EntityId
            tournament.id = EntityId(self._next_id)
            self._next_id += 1
        self._tournaments[(tournament.tenant_id, tournament.id)] = tournament
        return tournament
    def find_by_id(self, tenant_id, tournament_id):
        return self._tournaments.get((tenant_id, tournament_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._tournaments.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, tournament_id):
        if (tenant_id, tournament_id) in self._tournaments:
            del self._tournaments[(tenant_id, tournament_id)]
            return True
        return False


# MISSING IN-MEMORY IMPLEMENTATIONS (69)

class InMemoryAcademyRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryAchievementRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryActRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryAffinityRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryAirshipRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryAllianceRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryAlternateRealityRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryAmbientRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryArchiveRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryArenaRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryArmyRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryArtifactSetRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryAtmosphereRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryAttributeRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryAutosaveRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryBadgeRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryBalanceEntitiesRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryBannerRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryBarterRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryBattalionRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryBestiaryEntryRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryBlackHoleRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryBlessingRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryBlueprintRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryBranchPointRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCalendarRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCameraPathRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCampaignRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCataclysmRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCelebrationRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCeremonyRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryChapterRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCharacterEvolutionRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCharacterProfileEntryRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCharacterVariantRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCharacterRelationshipRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCheckpointRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryChekhovsGunRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryChoiceRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCinematicRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCodexEntryRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryColorPaletteRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCompetitionRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryComponentRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryConcertRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryConsequenceRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryConstitutionRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryConversionRateRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCourtRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCrimeRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCultRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCurrencyRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCurseRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCursedItemRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCustomMapRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCutsceneRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDefenseRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDemandRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDifficultyCurveRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDimensionRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDisasterRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDiscoveryRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDispositionRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDistrictRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDivineItemRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDropRateRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDungeonRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDubbingRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryEasterEggRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryEclipseRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryEraTransitionRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryEnigmaRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryExhibitionRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryFestivalRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryFlashForwardRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryFoodChainRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryFortificationRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryFactionIdeologyRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryFactionLeaderRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryFactionMembershipRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryFactionResourceRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryFactionTerritoryRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryHubAreaRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryHiddenPathRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryHolySiteRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryInstanceRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryJournalPageRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryKillCountRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryLootTableWeightRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryLoreFragmentRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryMarketSquareRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryModRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryMotionCaptureRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryMountEquipmentRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryMuseumRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryMythicalArmorRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryMysteryRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryMythicalArmorRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryNobleDistrictRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryOpenWorldZoneRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryPactRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryPlotBranchRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryPlotDeviceRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryPocketDimensionRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryPortalRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryPortDistrictRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryPlayerMetricRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryRiddleRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryRuneRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryResearchCenterRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryRumorRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemorySavePointRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryScriptureRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemorySecretAreaRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemorySeasonalEventRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemorySectRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemorySiegeEngineRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemorySocialClassRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemorySocialMediaRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemorySocialMobilityRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemorySocketRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemorySkyboxRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemorySoundEffectRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemorySpawnPointRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryStarSystemRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemorySubtitleRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemorySummonRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemorySwampRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryTeleporterRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryTimePeriodRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryTimelineRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryTournamentRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryTalentTreeRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryTranslationRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryTreasuryRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryTreatyRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryTrophyRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryUndergroundRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryUserScenarioRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryVisualEffectRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryVoiceActorRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryVoiceLineRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryVoiceOverRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryWeatherPatternRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryWeaponSystemRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryWorldEventRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryWorkshopEntryRepository:
    def __init__(self):
        self._entities = {}
        self._next_id = 1
    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            entity.id = EntityId(self._next_id)
            self._next_id += 1
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity
    def find_by_id(self, tenant_id, entity_id):
        return self._entities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._entities.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._entities:
            del self._entities[(tenant_id, entity_id)]
            return True
        return False


# FINAL 3 MISSING IN-MEMORY IMPLEMENTATIONS

class InMemoryDeusExMachinaRepository:
    def __init__(self):
        self._deus_ex_machinas = {}
        self._next_id = 1
    def save(self, dem):
        if dem.id is None:
            from src.domain.value_objects.common import EntityId
            dem.id = EntityId(self._next_id)
            self._next_id += 1
        self._deus_ex_machinas[(dem.tenant_id, dem.id)] = dem
        return dem
    def find_by_id(self, tenant_id, entity_id):
        return self._deus_ex_machinas.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [d for d in self._deus_ex_machinas.values() if d.tenant_id == tenant_id and d.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._deus_ex_machinas:
            del self._deus_ex_machinas[(tenant_id, entity_id)]
            return True
        return False

class InMemoryFastTravelPointRepository:
    def __init__(self):
        self._fast_travel_points = {}
        self._next_id = 1
    def save(self, ftp):
        if ftp.id is None:
            from src.domain.value_objects.common import EntityId
            ftp.id = EntityId(self._next_id)
            self._next_id += 1
        self._fast_travel_points[(ftp.tenant_id, ftp.id)] = ftp
        return ftp
    def find_by_id(self, tenant_id, entity_id):
        return self._fast_travel_points.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [f for f in self._fast_travel_points.values() if f.tenant_id == tenant_id and f.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._fast_travel_points:
            del self._fast_travel_points[(tenant_id, entity_id)]
            return True
        return False

class InMemoryRedHerringRepository:
    def __init__(self):
        self._red_herrings = {}
        self._next_id = 1
    def save(self, rh):
        if rh.id is None:
            from src.domain.value_objects.common import EntityId
            rh.id = EntityId(self._next_id)
            self._next_id += 1
        self._red_herrings[(rh.tenant_id, rh.id)] = rh
        return rh
    def find_by_id(self, tenant_id, entity_id):
        return self._red_herrings.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._red_herrings.values() if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._red_herrings:
            del self._red_herrings[(tenant_id, entity_id)]
            return True
        return False
