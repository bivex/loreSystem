"""
SQLite Repository Implementations

These are SQLite-backed implementations of the repository interfaces
for production use. All data persists to a SQLite database file.
"""
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager
import json
from datetime import datetime

from src.domain.entities.world import World
from src.domain.entities.character import Character
from src.domain.entities.item import Item
from src.domain.entities.location import Location
from src.domain.entities.environment import Environment
from src.domain.entities.texture import Texture
from src.domain.entities.model3d import Model3D
from src.domain.entities.story import Story
from src.domain.entities.event import Event
from src.domain.entities.page import Page

from src.domain.repositories.world_repository import IWorldRepository
from src.domain.repositories.character_repository import ICharacterRepository
from src.domain.repositories.item_repository import IItemRepository
from src.domain.repositories.location_repository import ILocationRepository
from src.domain.repositories.environment_repository import IEnvironmentRepository
from src.domain.value_objects.common import (
    TenantId, EntityId, WorldName, CharacterName, TimeOfDay, Weather, Lighting
)
from src.domain.exceptions import DuplicateEntity, EntityNotFound


class SQLiteDatabase:
    """SQLite database connection manager."""

    def __init__(self, db_path: str = "lore_system.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def get_connection(self):
        """Get a database connection with automatic cleanup."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Allow column access by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize_schema(self):
        """Create all database tables."""
        with self.get_connection() as conn:
            # Worlds table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS worlds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    genre TEXT,
                    power_level INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(tenant_id, name)
                )
            """)

            # Characters table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    backstory TEXT,
                    power_level INTEGER DEFAULT 1,
                    image_url TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Character abilities table (JSON stored as TEXT)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS character_abilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    power_level INTEGER DEFAULT 1,
                    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
                )
            """)

            # Items table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    rarity INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Locations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    environment_type TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Environments table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS environments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    time_of_day TEXT,
                    weather TEXT,
                    lighting TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Textures table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS textures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    texture_type TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # 3D Models table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS models3d (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    model_type TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Stories table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Events table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    timeline_position INTEGER,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Pages table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT,
                    page_number INTEGER,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)


class SQLiteWorldRepository(IWorldRepository):
    """SQLite implementation of World repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, world: World) -> World:
        now = datetime.now().isoformat()

        if world.id is None:
            # Insert new world
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO worlds (tenant_id, name, description, genre, power_level, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    world.tenant_id.value,
                    world.name.value,
                    world.description.value if world.description else None,
                    world.genre.value if world.genre else None,
                    world.power_level.value,
                    now,
                    now
                ))
                world_id = cursor.lastrowid
                object.__setattr__(world, 'id', EntityId(world_id))
        else:
            # Update existing world
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE worlds
                    SET name = ?, description = ?, genre = ?, power_level = ?, updated_at = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    world.name.value,
                    world.description.value if world.description else None,
                    world.genre.value if world.genre else None,
                    world.power_level.value,
                    now,
                    world.id.value,
                    world.tenant_id.value
                ))

        return world

    def find_by_id(self, tenant_id: TenantId, world_id: EntityId) -> Optional[World]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM worlds WHERE id = ? AND tenant_id = ?
            """, (world_id.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_world(row)

    def find_by_name(self, tenant_id: TenantId, name: WorldName) -> Optional[World]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM worlds WHERE name = ? AND tenant_id = ?
            """, (name.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_world(row)

    def list_by_tenant(self, tenant_id: TenantId, limit: int = 100, offset: int = 0) -> List[World]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM worlds WHERE tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (tenant_id.value, limit, offset)).fetchall()

            return [self._row_to_world(row) for row in rows]

    def delete(self, tenant_id: TenantId, world_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM worlds WHERE id = ? AND tenant_id = ?
            """, (world_id.value, tenant_id.value))

            return cursor.rowcount > 0

    def exists(self, tenant_id: TenantId, name: WorldName) -> bool:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT 1 FROM worlds WHERE name = ? AND tenant_id = ? LIMIT 1
            """, (name.value, tenant_id.value)).fetchone()

            return row is not None

    def _row_to_world(self, row: sqlite3.Row) -> World:
        from src.domain.value_objects.common import WorldName, Description, Genre, PowerLevel, Timestamp

        return World(
            tenant_id=TenantId(row['tenant_id']),
            name=WorldName(row['name']),
            description=Description(row['description']) if row['description'] else None,
            genre=Genre(row['genre']) if row['genre'] else None,
            power_level=PowerLevel(row['power_level']),
            id=EntityId(row['id'])
        )


class SQLiteCharacterRepository(ICharacterRepository):
    """SQLite implementation of Character repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, character: Character) -> Character:
        now = datetime.now().isoformat()

        if character.id is None:
            # Insert new character
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO characters (tenant_id, world_id, name, description, backstory, power_level, image_url, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    character.tenant_id.value,
                    character.world_id.value,
                    character.name.value,
                    character.description.value if character.description else None,
                    character.backstory.value if character.backstory else None,
                    character.power_level.value,
                    character.image_url.value if character.image_url else None,
                    now,
                    now
                ))
                char_id = cursor.lastrowid
                object.__setattr__(character, 'id', EntityId(char_id))
        else:
            # Update existing character
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE characters
                    SET name = ?, description = ?, backstory = ?, power_level = ?, image_url = ?, updated_at = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    character.name.value,
                    character.description.value if character.description else None,
                    character.backstory.value if character.backstory else None,
                    character.power_level.value,
                    character.image_url.value if character.image_url else None,
                    now,
                    character.id.value,
                    character.tenant_id.value
                ))

        return character

    def find_by_id(self, tenant_id: TenantId, character_id: EntityId) -> Optional[Character]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM characters WHERE id = ? AND tenant_id = ?
            """, (character_id.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_character(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 100, offset: int = 0) -> List[Character]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM characters WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()

            return [self._row_to_character(row) for row in rows]

    def delete(self, tenant_id: TenantId, character_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM characters WHERE id = ? AND tenant_id = ?
            """, (character_id.value, tenant_id.value))

            return cursor.rowcount > 0

    def _row_to_character(self, row: sqlite3.Row) -> Character:
        from src.domain.value_objects.common import CharacterName, Description, Backstory, PowerLevel

        return Character(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=CharacterName(row['name']),
            description=Description(row['description']) if row['description'] else None,
            backstory=Backstory(row['backstory']) if row['backstory'] else None,
            power_level=PowerLevel(row['power_level']),
            id=EntityId(row['id'])
        )


class SQLiteItemRepository(IItemRepository):
    """SQLite implementation of Item repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, item: Item) -> Item:
        now = datetime.now().isoformat()

        if item.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO items (tenant_id, world_id, name, description, rarity, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    item.tenant_id.value,
                    item.world_id.value,
                    item.name.value,
                    item.description.value if item.description else None,
                    item.rarity.value,
                    now
                ))
                item_id = cursor.lastrowid
                object.__setattr__(item, 'id', EntityId(item_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE items
                    SET name = ?, description = ?, rarity = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    item.name.value,
                    item.description.value if item.description else None,
                    item.rarity.value,
                    item.id.value,
                    item.tenant_id.value
                ))

        return item

    def find_by_id(self, tenant_id: TenantId, item_id: EntityId) -> Optional[Item]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM items WHERE id = ? AND tenant_id = ?
            """, (item_id.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_item(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 100, offset: int = 0) -> List[Item]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM items WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()

            return [self._row_to_item(row) for row in rows]

    def delete(self, tenant_id: TenantId, item_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM items WHERE id = ? AND tenant_id = ?
            """, (item_id.value, tenant_id.value))

            return cursor.rowcount > 0

    def _row_to_item(self, row: sqlite3.Row) -> Item:
        from src.domain.value_objects.common import ItemName, Description, Rarity

        return Item(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=ItemName(row['name']),
            description=Description(row['description']) if row['description'] else None,
            rarity=Rarity(row['rarity']),
            id=EntityId(row['id'])
        )


class SQLiteLocationRepository(ILocationRepository):
    """SQLite implementation of Location repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, location: Location) -> Location:
        now = datetime.now().isoformat()

        if location.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO locations (tenant_id, world_id, name, description, environment_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    location.tenant_id.value,
                    location.world_id.value,
                    location.name.value,
                    location.description.value if location.description else None,
                    location.environment_type.value if location.environment_type else None,
                    now
                ))
                location_id = cursor.lastrowid
                object.__setattr__(location, 'id', EntityId(location_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE locations
                    SET name = ?, description = ?, environment_type = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    location.name.value,
                    location.description.value if location.description else None,
                    location.environment_type.value if location.environment_type else None,
                    location.id.value,
                    location.tenant_id.value
                ))

        return location

    def find_by_id(self, tenant_id: TenantId, location_id: EntityId) -> Optional[Location]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM locations WHERE id = ? AND tenant_id = ?
            """, (location_id.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_location(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 100, offset: int = 0) -> List[Location]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM locations WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()

            return [self._row_to_location(row) for row in rows]

    def delete(self, tenant_id: TenantId, location_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM locations WHERE id = ? AND tenant_id = ?
            """, (location_id.value, tenant_id.value))

            return cursor.rowcount > 0

    def _row_to_location(self, row: sqlite3.Row) -> Location:
        from src.domain.value_objects.common import LocationName, Description, EnvironmentType

        return Location(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=LocationName(row['name']),
            description=Description(row['description']) if row['description'] else None,
            environment_type=EnvironmentType(row['environment_type']) if row['environment_type'] else None,
            id=EntityId(row['id'])
        )


class SQLiteEnvironmentRepository(IEnvironmentRepository):
    """SQLite implementation of Environment repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, environment: Environment) -> Environment:
        now = datetime.now().isoformat()

        if environment.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO environments (tenant_id, world_id, name, description, time_of_day, weather, lighting, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    environment.tenant_id.value,
                    environment.world_id.value,
                    environment.name.value,
                    environment.description.value if environment.description else None,
                    environment.time_of_day.value if environment.time_of_day else None,
                    environment.weather.value if environment.weather else None,
                    environment.lighting.value if environment.lighting else None,
                    now
                ))
                env_id = cursor.lastrowid
                object.__setattr__(environment, 'id', EntityId(env_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE environments
                    SET name = ?, description = ?, time_of_day = ?, weather = ?, lighting = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    environment.name.value,
                    environment.description.value if environment.description else None,
                    environment.time_of_day.value if environment.time_of_day else None,
                    environment.weather.value if environment.weather else None,
                    environment.lighting.value if environment.lighting else None,
                    environment.id.value,
                    environment.tenant_id.value
                ))

        return environment

    def find_by_id(self, tenant_id: TenantId, environment_id: EntityId) -> Optional[Environment]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM environments WHERE id = ? AND tenant_id = ?
            """, (environment_id.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_environment(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 100, offset: int = 0) -> List[Environment]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM environments WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()

            return [self._row_to_environment(row) for row in rows]

    def delete(self, tenant_id: TenantId, environment_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM environments WHERE id = ? AND tenant_id = ?
            """, (environment_id.value, tenant_id.value))

            return cursor.rowcount > 0

    def _row_to_environment(self, row: sqlite3.Row) -> Environment:
        return Environment(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=row['name'],
            description=row['description'] if row['description'] else None,
            time_of_day=TimeOfDay(row['time_of_day']) if row['time_of_day'] else None,
            weather=Weather(row['weather']) if row['weather'] else None,
            lighting=Lighting(row['lighting']) if row['lighting'] else None,
            id=EntityId(row['id'])
        )


class SQLiteStoryRepository:
    """SQLite implementation of Story repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, story: Story) -> Story:
        now = datetime.now().isoformat()

        if story.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO stories (tenant_id, world_id, name, description, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    story.tenant_id.value,
                    story.world_id.value,
                    story.name.value,
                    story.description.value if story.description else None,
                    now
                ))
                story_id = cursor.lastrowid
                object.__setattr__(story, 'id', EntityId(story_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE stories
                    SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    story.name.value,
                    story.description.value if story.description else None,
                    story.id.value,
                    story.tenant_id.value
                ))

        return story

    def find_by_id(self, tenant_id: TenantId, story_id: EntityId) -> Optional[Story]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM stories WHERE id = ? AND tenant_id = ?
            """, (story_id.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_story(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Story]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM stories WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()

            return [self._row_to_story(row) for row in rows]

    def delete(self, tenant_id: TenantId, story_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM stories WHERE id = ? AND tenant_id = ?
            """, (story_id.value, tenant_id.value))

            return cursor.rowcount > 0

    def _row_to_story(self, row: sqlite3.Row) -> Story:
        from src.domain.value_objects.common import StoryName, Description

        return Story(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=StoryName(row['name']),
            description=Description(row['description']) if row['description'] else None,
            id=EntityId(row['id'])
        )


class SQLiteEventRepository:
    """SQLite implementation of Event repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, event: Event) -> Event:
        now = datetime.now().isoformat()

        if event.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO events (tenant_id, world_id, name, description, timeline_position, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    event.tenant_id.value,
                    event.world_id.value,
                    event.name.value,
                    event.description.value if event.description else None,
                    event.timeline_position.value if event.timeline_position else None,
                    now
                ))
                event_id = cursor.lastrowid
                object.__setattr__(event, 'id', EntityId(event_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE events
                    SET name = ?, description = ?, timeline_position = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    event.name.value,
                    event.description.value if event.description else None,
                    event.timeline_position.value if event.timeline_position else None,
                    event.id.value,
                    event.tenant_id.value
                ))

        return event

    def find_by_id(self, tenant_id: TenantId, event_id: EntityId) -> Optional[Event]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM events WHERE id = ? AND tenant_id = ?
            """, (event_id.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_event(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Event]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM events WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()

            return [self._row_to_event(row) for row in rows]

    def delete(self, tenant_id: TenantId, event_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM events WHERE id = ? AND tenant_id = ?
            """, (event_id.value, tenant_id.value))

            return cursor.rowcount > 0

    def _row_to_event(self, row: sqlite3.Row) -> Event:
        from src.domain.value_objects.common import EventName, Description

        return Event(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=EventName(row['name']),
            description=Description(row['description']) if row['description'] else None,
            timeline_position=row['timeline_position'] if row['timeline_position'] else None,
            id=EntityId(row['id'])
        )


class SQLitePageRepository:
    """SQLite implementation of Page repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, page: Page) -> Page:
        now = datetime.now().isoformat()

        if page.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO pages (tenant_id, world_id, title, content, page_number, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    page.tenant_id.value,
                    page.world_id.value,
                    page.title.value,
                    page.content.value if page.content else None,
                    page.page_number if page.page_number else None,
                    now
                ))
                page_id = cursor.lastrowid
                object.__setattr__(page, 'id', EntityId(page_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE pages
                    SET title = ?, content = ?, page_number = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    page.title.value,
                    page.content.value if page.content else None,
                    page.page_number if page.page_number else None,
                    page.id.value,
                    page.tenant_id.value
                ))

        return page

    def find_by_id(self, tenant_id: TenantId, page_id: EntityId) -> Optional[Page]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM pages WHERE id = ? AND tenant_id = ?
            """, (page_id.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_page(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Page]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM pages WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()

            return [self._row_to_page(row) for row in rows]

    def delete(self, tenant_id: TenantId, page_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM pages WHERE id = ? AND tenant_id = ?
            """, (page_id.value, tenant_id.value))

            return cursor.rowcount > 0

    def _row_to_page(self, row: sqlite3.Row) -> Page:
        from src.domain.value_objects.common import PageName, Content

        return Page(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            title=PageName(row['title']),
            content=Content(row['content']) if row['content'] else None,
            page_number=row['page_number'],
            id=EntityId(row['id'])
        )


class SQLiteTextureRepository:
    """SQLite implementation of Texture repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, texture: Texture) -> Texture:
        now = datetime.now().isoformat()

        if texture.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO textures (tenant_id, world_id, name, path, texture_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    texture.tenant_id.value,
                    texture.world_id.value,
                    texture.name.value,
                    texture.path.value,
                    texture.texture_type.value if texture.texture_type else None,
                    now
                ))
                texture_id = cursor.lastrowid
                object.__setattr__(texture, 'id', EntityId(texture_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE textures
                    SET name = ?, path = ?, texture_type = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    texture.name.value,
                    texture.path.value,
                    texture.texture_type.value if texture.texture_type else None,
                    texture.id.value,
                    texture.tenant_id.value
                ))

        return texture

    def find_by_id(self, tenant_id: TenantId, texture_id: EntityId) -> Optional[Texture]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM textures WHERE id = ? AND tenant_id = ?
            """, (texture_id.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_texture(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 100, offset: int = 0) -> List[Texture]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM textures WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()

            return [self._row_to_texture(row) for row in rows]

    def delete(self, tenant_id: TenantId, texture_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM textures WHERE id = ? AND tenant_id = ?
            """, (texture_id.value, tenant_id.value))

            return cursor.rowcount > 0

    def _row_to_texture(self, row: sqlite3.Row) -> Texture:
        from src.domain.value_objects.common import TextureName, Path

        return Texture(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=TextureName(row['name']),
            path=Path(row['path']),
            texture_type=row['texture_type'],
            id=EntityId(row['id'])
        )


class SQLiteModel3DRepository:
    """SQLite implementation of 3D Model repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, model: Model3D) -> Model3D:
        now = datetime.now().isoformat()

        if model.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO models3d (tenant_id, world_id, name, path, model_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    model.tenant_id.value,
                    model.world_id.value,
                    model.name.value,
                    model.path.value,
                    model.model_type.value if model.model_type else None,
                    now
                ))
                model_id = cursor.lastrowid
                object.__setattr__(model, 'id', EntityId(model_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE models3d
                    SET name = ?, path = ?, model_type = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    model.name.value,
                    model.path.value,
                    model.model_type.value if model.model_type else None,
                    model.id.value,
                    model.tenant_id.value
                ))

        return model

    def find_by_id(self, tenant_id: TenantId, model_id: EntityId) -> Optional[Model3D]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM models3d WHERE id = ? AND tenant_id = ?
            """, (model_id.value, tenant_id.value)).fetchone()

            if not row:
                return None

            return self._row_to_model3d(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 100, offset: int = 0) -> List[Model3D]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM models3d WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()

            return [self._row_to_model3d(row) for row in rows]

    def delete(self, tenant_id: TenantId, model_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM models3d WHERE id = ? AND tenant_id = ?
            """, (model_id.value, tenant_id.value))

            return cursor.rowcount > 0

    def _row_to_model3d(self, row: sqlite3.Row) -> Model3D:
        from src.domain.value_objects.common import Model3DName, Path

        return Model3D(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=Model3DName(row['name']),
            path=Path(row['path']),
            model_type=row['model_type'],
            id=EntityId(row['id'])
        )

