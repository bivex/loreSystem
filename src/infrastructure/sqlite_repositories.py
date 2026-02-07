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

            # Sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    story_id INTEGER,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE SET NULL
                )
            """)

            # Tags table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    tag_type TEXT NOT NULL,
                    color TEXT,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Notes table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT,
                    is_pinned INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Templates table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    template_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    parent_template_id INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                    FOREIGN KEY (parent_template_id) REFERENCES templates(id) ON DELETE SET NULL
                )
            """)

            # Choices table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS choices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    story_id INTEGER,
                    name TEXT NOT NULL,
                    choice_type TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE SET NULL
                )
            """)

            # Flowcharts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS flowcharts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    story_id INTEGER,
                    name TEXT NOT NULL,
                    is_active INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE SET NULL
                )
            """)

            # Handouts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS handouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    session_id INTEGER,
                    title TEXT NOT NULL,
                    content TEXT,
                    is_revealed INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL
                )
            """)

            # Images table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Inspirations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS inspirations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    category TEXT,
                    content TEXT NOT NULL,
                    is_used INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Maps table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS maps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    is_interactive INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Tokenboards table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tokenboards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    is_active INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
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

            # Progression tables
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS perks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS traits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS attributes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS level_ups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS talent_trees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS masteries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Faction tables
            conn.execute("""
                CREATE TABLE IF NOT EXISTS faction_hierarchys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS faction_ideologys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS faction_leaders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS faction_memberships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS faction_resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS faction_territorys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)


    def __init__(self, db: SQLiteDatabase):
        self.db = db
            # Quest chains table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quest_chains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Quest nodes table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quest_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Quest prerequisites table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quest_prerequisites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Quest objectives table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quest_objectives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Quest trackers table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quest_trackers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Quest givers table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quest_givers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Quest rewards table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quest_rewards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Quest reward tiers table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quest_reward_tiers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)



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



class SQLiteSessionRepository:
    """SQLite implementation of Session repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, session: object) -> object:
        now = datetime.now().isoformat()

        if session.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO sessions (tenant_id, world_id, name, description, story_id, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.tenant_id.value,
                    session.world_id.value,
                    session.name,
                    getattr(session, 'description', None),
                    getattr(session, 'story_id', None),
                    getattr(session, 'is_active', True),
                    now,
                    now
                ))
                session_id = cursor.lastrowid
                object.__setattr__(session, 'id', EntityId(session_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE sessions
                    SET name = ?, description = ?, story_id = ?, is_active = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    session.name,
                    getattr(session, 'description', None),
                    getattr(session, 'story_id', None),
                    getattr(session, 'is_active', True),
                    session.id.value,
                    session.tenant_id.value
                ))

        return session

    def find_by_id(self, tenant_id: TenantId, session_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM sessions WHERE id = ? AND tenant_id = ?
            """, (session_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_session(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM sessions WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_session(row) for row in rows]

    def list_by_story(self, tenant_id: TenantId, story_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM sessions WHERE story_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (story_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_session(row) for row in rows]

    def list_active(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM sessions WHERE world_id = ? AND tenant_id = ? AND is_active = 1 ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_session(row) for row in rows]

    def delete(self, tenant_id: TenantId, session_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM sessions WHERE id = ? AND tenant_id = ?
            """, (session_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_session(self, row: sqlite3.Row) -> object:
        class SimpleSession:
            def __init__(self, id, tenant_id, world_id, name, description, story_id, is_active, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.name = name
                self.description = description
                self.story_id = EntityId(story_id) if story_id else None
                self.is_active = is_active
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleSession(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['name'],
            row['description'],
            row['story_id'],
            row['is_active'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteTagRepository:
    """SQLite implementation of Tag repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, tag: Tag) -> Tag:
        now = datetime.now().isoformat()

        if tag.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO tags (tenant_id, world_id, name, tag_type, color, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tag.tenant_id.value,
                    tag.world_id.value,
                    tag.name.value,
                    tag.tag_type.value,
                    tag.color,
                    tag.description,
                    now,
                    now
                ))
                tag_id = cursor.lastrowid
                object.__setattr__(tag, 'id', EntityId(tag_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE tags
                    SET name = ?, tag_type = ?, color = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    tag.name.value,
                    tag.tag_type.value,
                    tag.color,
                    tag.description,
                    tag.id.value,
                    tag.tenant_id.value
                ))

        return tag

    def find_by_id(self, tenant_id: TenantId, tag_id: EntityId) -> Optional[Tag]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM tags WHERE id = ? AND tenant_id = ?
            """, (tag_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_tag(row)

    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: "TagName") -> Optional[Tag]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM tags WHERE world_id = ? AND tenant_id = ? AND name = ? LIMIT 1
            """, (world_id.value, tenant_id.value, name.value)).fetchone()

            if not row:
                return None
            return self._row_to_tag(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Tag]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tags WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_tag(row) for row in rows]

    def list_by_type(self, tenant_id: TenantId, world_id: EntityId, tag_type: "TagType", limit: int = 50, offset: int = 0) -> List[Tag]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tags WHERE world_id = ? AND tenant_id = ? AND tag_type = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, tag_type.value, limit, offset)).fetchall()
            return [self._row_to_tag(row) for row in rows]

    def delete(self, tenant_id: TenantId, tag_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM tags WHERE id = ? AND tenant_id = ?
            """, (tag_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: "TagName", tag_type: "TagType") -> bool:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT 1 FROM tags WHERE world_id = ? AND tenant_id = ? AND name = ? AND tag_type = ? LIMIT 1
            """, (world_id.value, tenant_id.value, name.value, tag_type.value)).fetchone()
            return row is not None

    def _row_to_tag(self, row: sqlite3.Row) -> Tag:
        return Tag(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=row['name'],
            tag_type=row['tag_type'],
            color=row['color'],
            description=row['description'],
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteNoteRepository:
    """SQLite implementation of Note repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, note: Note) -> Note:
        now = datetime.now().isoformat()

        if note.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO notes (tenant_id, world_id, title, content, tags, is_pinned, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    note.tenant_id.value,
                    note.world_id.value,
                    note.title,
                    note.content,
                    json.dumps(note.tags),
                    note.is_pinned,
                    now,
                    now
                ))
                note_id = cursor.lastrowid
                object.__setattr__(note, 'id', EntityId(note_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE notes
                    SET title = ?, content = ?, tags = ?, is_pinned = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    note.title,
                    note.content,
                    json.dumps(note.tags),
                    note.is_pinned,
                    note.id.value,
                    note.tenant_id.value
                ))

        return note

    def find_by_id(self, tenant_id: TenantId, note_id: EntityId) -> Optional[Note]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM notes WHERE id = ? AND tenant_id = ?
            """, (note_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_note(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Note]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM notes WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_note(row) for row in rows]

    def list_pinned(self, tenant_id: TenantId, world_id: EntityId, limit: int = 20, offset: int = 0) -> List[Note]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM notes WHERE world_id = ? AND tenant_id = ? AND is_pinned = 1 ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_note(row) for row in rows]

    def search_by_content(self, tenant_id: TenantId, search_term: str, limit: int = 20) -> List[Note]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM notes WHERE tenant_id = ? AND (title LIKE ? OR content LIKE ?) LIMIT ?
            """, (tenant_id.value, f'%{search_term}%', f'%{search_term}%', limit)).fetchall()
            return [self._row_to_note(row) for row in rows]

    def delete(self, tenant_id: TenantId, note_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM notes WHERE id = ? AND tenant_id = ?
            """, (note_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_note(self, row: sqlite3.Row) -> Note:
        return Note(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            title=row['title'],
            content=row['content'],
            tags=json.loads(row['tags']),
            is_pinned=row['is_pinned'],
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteTemplateRepository:
    """SQLite implementation of Template repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, template: Template) -> Template:
        now = datetime.now().isoformat()

        if template.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO templates (tenant_id, world_id, name, description, template_type, content, parent_template_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    template.tenant_id.value,
                    template.world_id.value,
                    template.name.value,
                    template.description,
                    template.template_type.value,
                    template.content.value,
                    template.parent_template_id.value if template.parent_template_id else None,
                    now,
                    now
                ))
                template_id = cursor.lastrowid
                object.__setattr__(template, 'id', EntityId(template_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE templates
                    SET name = ?, description = ?, template_type = ?, content = ?, parent_template_id = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    template.name.value,
                    template.description,
                    template.template_type.value,
                    template.content.value,
                    template.parent_template_id.value if template.parent_template_id else None,
                    template.id.value,
                    template.tenant_id.value
                ))

        return template

    def find_by_id(self, tenant_id: TenantId, template_id: EntityId) -> Optional[Template]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM templates WHERE id = ? AND tenant_id = ?
            """, (template_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_template(row)

    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: "TemplateName") -> Optional[Template]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM templates WHERE world_id = ? AND tenant_id = ? AND name = ? LIMIT 1
            """, (world_id.value, tenant_id.value, name.value)).fetchone()

            if not row:
                return None
            return self._row_to_template(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Template]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM templates WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_template(row) for row in rows]

    def list_by_type(self, tenant_id: TenantId, world_id: EntityId, template_type: "TemplateType", limit: int = 50, offset: int = 0) -> List[Template]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM templates WHERE world_id = ? AND tenant_id = ? AND template_type = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, template_type.value, limit, offset)).fetchall()
            return [self._row_to_template(row) for row in rows]

    def list_runes(self, tenant_id: TenantId, parent_template_id: EntityId, limit: int = 50, offset: int = 0) -> List[Template]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM templates WHERE parent_template_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (parent_template_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_template(row) for row in rows]

    def delete(self, tenant_id: TenantId, template_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM templates WHERE id = ? AND tenant_id = ?
            """, (template_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: "TemplateName") -> bool:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT 1 FROM templates WHERE world_id = ? AND tenant_id = ? AND name = ? LIMIT 1
            """, (world_id.value, tenant_id.value, name.value)).fetchone()
            return row is not None

    def _row_to_template(self, row: sqlite3.Row) -> Template:
        return Template(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=row['name'],
            description=row['description'],
            template_type=row['template_type'],
            content=row['content'],
            rune_ids=[],
            parent_template_id=EntityId(row['parent_template_id']) if row['parent_template_id'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteChoiceRepository:
    """SQLite implementation of Choice repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, choice: object) -> object:
        now = datetime.now().isoformat()

        if choice.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO choices (tenant_id, world_id, story_id, name, choice_type, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    choice.tenant_id.value,
                    choice.world_id.value,
                    getattr(choice, 'story_id', None),
                    choice.name,
                    getattr(choice, 'choice_type', None),
                    now,
                    now
                ))
                choice_id = cursor.lastrowid
                object.__setattr__(choice, 'id', EntityId(choice_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE choices
                    SET name = ?, choice_type = ?, story_id = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    choice.name,
                    getattr(choice, 'choice_type', None),
                    getattr(choice, 'story_id', None),
                    choice.id.value,
                    choice.tenant_id.value
                ))

        return choice

    def find_by_id(self, tenant_id: TenantId, choice_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM choices WHERE id = ? AND tenant_id = ?
            """, (choice_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_choice(row)

    def list_by_story(self, tenant_id: TenantId, story_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM choices WHERE story_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (story_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_choice(row) for row in rows]

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM choices WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_choice(row) for row in rows]

    def list_by_type(self, tenant_id: TenantId, world_id: EntityId, choice_type: str, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM choices WHERE world_id = ? AND tenant_id = ? AND choice_type = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, choice_type, limit, offset)).fetchall()
            return [self._row_to_choice(row) for row in rows]

    def delete(self, tenant_id: TenantId, choice_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM choices WHERE id = ? AND tenant_id = ?
            """, (choice_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_choice(self, row: sqlite3.Row) -> object:
        class SimpleChoice:
            def __init__(self, id, tenant_id, world_id, story_id, name, choice_type, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.story_id = EntityId(story_id) if story_id else None
                self.name = name
                self.choice_type = choice_type
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleChoice(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['story_id'],
            row['name'],
            row['choice_type'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteFlowchartRepository:
    """SQLite implementation of Flowchart repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, flowchart: object) -> object:
        now = datetime.now().isoformat()

        if flowchart.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO flowcharts (tenant_id, world_id, story_id, name, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    flowchart.tenant_id.value,
                    flowchart.world_id.value,
                    getattr(flowchart, 'story_id', None),
                    flowchart.name,
                    getattr(flowchart, 'is_active', False),
                    now,
                    now
                ))
                flowchart_id = cursor.lastrowid
                object.__setattr__(flowchart, 'id', EntityId(flowchart_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE flowcharts
                    SET name = ?, is_active = ?, story_id = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    flowchart.name,
                    getattr(flowchart, 'is_active', False),
                    getattr(flowchart, 'story_id', None),
                    flowchart.id.value,
                    flowchart.tenant_id.value
                ))

        return flowchart

    def find_by_id(self, tenant_id: TenantId, flowchart_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM flowcharts WHERE id = ? AND tenant_id = ?
            """, (flowchart_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_flowchart(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM flowcharts WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_flowchart(row) for row in rows]

    def list_by_story(self, tenant_id: TenantId, story_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM flowcharts WHERE story_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (story_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_flowchart(row) for row in rows]

    def find_active(self, tenant_id: TenantId, world_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM flowcharts WHERE world_id = ? AND tenant_id = ? AND is_active = 1 LIMIT 1
            """, (world_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_flowchart(row)

    def delete(self, tenant_id: TenantId, flowchart_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM flowcharts WHERE id = ? AND tenant_id = ?
            """, (flowchart_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_flowchart(self, row: sqlite3.Row) -> object:
        class SimpleFlowchart:
            def __init__(self, id, tenant_id, world_id, story_id, name, is_active, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.story_id = EntityId(story_id) if story_id else None
                self.name = name
                self.is_active = bool(is_active)
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleFlowchart(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['story_id'],
            row['name'],
            row['is_active'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteHandoutRepository:
    """SQLite implementation of Handout repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, handout: object) -> object:
        now = datetime.now().isoformat()

        if handout.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO handouts (tenant_id, world_id, session_id, title, content, is_revealed, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    handout.tenant_id.value,
                    handout.world_id.value,
                    getattr(handout, 'session_id', None),
                    handout.title,
                    getattr(handout, 'content', None),
                    getattr(handout, 'is_revealed', False),
                    now,
                    now
                ))
                handout_id = cursor.lastrowid
                object.__setattr__(handout, 'id', EntityId(handout_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE handouts
                    SET title = ?, content = ?, is_revealed = ?, session_id = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    handout.title,
                    getattr(handout, 'content', None),
                    getattr(handout, 'is_revealed', False),
                    getattr(handout, 'session_id', None),
                    handout.id.value,
                    handout.tenant_id.value
                ))

        return handout

    def find_by_id(self, tenant_id: TenantId, handout_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM handouts WHERE id = ? AND tenant_id = ?
            """, (handout_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_handout(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM handouts WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_handout(row) for row in rows]

    def list_by_session(self, tenant_id: TenantId, session_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM handouts WHERE session_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (session_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_handout(row) for row in rows]

    def list_revealed(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM handouts WHERE world_id = ? AND tenant_id = ? AND is_revealed = 1 ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_handout(row) for row in rows]

    def delete(self, tenant_id: TenantId, handout_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM handouts WHERE id = ? AND tenant_id = ?
            """, (handout_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_handout(self, row: sqlite3.Row) -> object:
        class SimpleHandout:
            def __init__(self, id, tenant_id, world_id, session_id, title, content, is_revealed, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.session_id = EntityId(session_id) if session_id else None
                self.title = title
                self.content = content
                self.is_revealed = bool(is_revealed)
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleHandout(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['session_id'],
            row['title'],
            row['content'],
            row['is_revealed'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteImageRepository:
    """SQLite implementation of Image repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, image: object) -> object:
        now = datetime.now().isoformat()

        if image.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO images (tenant_id, world_id, name, path, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    image.tenant_id.value,
                    image.world_id.value,
                    image.name,
                    image.path,
                    now,
                    now
                ))
                image_id = cursor.lastrowid
                object.__setattr__(image, 'id', EntityId(image_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE images
                    SET name = ?, path = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    image.name,
                    image.path,
                    image.id.value,
                    image.tenant_id.value
                ))

        return image

    def find_by_id(self, tenant_id: TenantId, image_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM images WHERE id = ? AND tenant_id = ?
            """, (image_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_image(row)

    def find_by_path(self, tenant_id: TenantId, world_id: EntityId, path: str) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM images WHERE world_id = ? AND tenant_id = ? AND path = ? LIMIT 1
            """, (world_id.value, tenant_id.value, path)).fetchone()

            if not row:
                return None
            return self._row_to_image(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM images WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_image(row) for row in rows]

    def delete(self, tenant_id: TenantId, image_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM images WHERE id = ? AND tenant_id = ?
            """, (image_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def exists(self, tenant_id: TenantId, world_id: EntityId, path: str) -> bool:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT 1 FROM images WHERE world_id = ? AND tenant_id = ? AND path = ? LIMIT 1
            """, (world_id.value, tenant_id.value, path)).fetchone()
            return row is not None

    def _row_to_image(self, row: sqlite3.Row) -> object:
        class SimpleImage:
            def __init__(self, id, tenant_id, world_id, name, path, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.name = name
                self.path = path
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleImage(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['name'],
            row['path'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteInspirationRepository:
    """SQLite implementation of Inspiration repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, inspiration: object) -> object:
        now = datetime.now().isoformat()

        if inspiration.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO inspirations (tenant_id, world_id, category, content, is_used, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    inspiration.tenant_id.value,
                    inspiration.world_id.value,
                    getattr(inspiration, 'category', None),
                    inspiration.content,
                    getattr(inspiration, 'is_used', False),
                    now,
                    now
                ))
                inspiration_id = cursor.lastrowid
                object.__setattr__(inspiration, 'id', EntityId(inspiration_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE inspirations
                    SET category = ?, content = ?, is_used = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    getattr(inspiration, 'category', None),
                    inspiration.content,
                    getattr(inspiration, 'is_used', False),
                    inspiration.id.value,
                    inspiration.tenant_id.value
                ))

        return inspiration

    def find_by_id(self, tenant_id: TenantId, inspiration_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM inspirations WHERE id = ? AND tenant_id = ?
            """, (inspiration_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_inspiration(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM inspirations WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_inspiration(row) for row in rows]

    def list_by_category(self, tenant_id: TenantId, world_id: EntityId, category: str, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM inspirations WHERE world_id = ? AND tenant_id = ? AND category = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, category, limit, offset)).fetchall()
            return [self._row_to_inspiration(row) for row in rows]

    def list_unused(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM inspirations WHERE world_id = ? AND tenant_id = ? AND is_used = 0 ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_inspiration(row) for row in rows]

    def search_by_content(self, tenant_id: TenantId, search_term: str, limit: int = 20) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM inspirations WHERE tenant_id = ? AND content LIKE ? LIMIT ?
            """, (tenant_id.value, f'%{search_term}%', limit)).fetchall()
            return [self._row_to_inspiration(row) for row in rows]

    def delete(self, tenant_id: TenantId, inspiration_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM inspirations WHERE id = ? AND tenant_id = ?
            """, (inspiration_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_inspiration(self, row: sqlite3.Row) -> object:
        class SimpleInspiration:
            def __init__(self, id, tenant_id, world_id, category, content, is_used, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.category = category
                self.content = content
                self.is_used = bool(is_used)
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleInspiration(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['category'],
            row['content'],
            row['is_used'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteMapRepository:
    """SQLite implementation of Map repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, map_obj: object) -> object:
        now = datetime.now().isoformat()

        if map_obj.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO maps (tenant_id, world_id, name, is_interactive, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    map_obj.tenant_id.value,
                    map_obj.world_id.value,
                    map_obj.name,
                    getattr(map_obj, 'is_interactive', False),
                    now,
                    now
                ))
                map_id = cursor.lastrowid
                object.__setattr__(map_obj, 'id', EntityId(map_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE maps
                    SET name = ?, is_interactive = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    map_obj.name,
                    getattr(map_obj, 'is_interactive', False),
                    map_obj.id.value,
                    map_obj.tenant_id.value
                ))

        return map_obj

    def find_by_id(self, tenant_id: TenantId, map_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM maps WHERE id = ? AND tenant_id = ?
            """, (map_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_map(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM maps WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_map(row) for row in rows]

    def list_interactive(self, tenant_id: TenantId, world_id: EntityId, limit: int = 20, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM maps WHERE world_id = ? AND tenant_id = ? AND is_interactive = 1 ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_map(row) for row in rows]

    def delete(self, tenant_id: TenantId, map_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM maps WHERE id = ? AND tenant_id = ?
            """, (map_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_map(self, row: sqlite3.Row) -> object:
        class SimpleMap:
            def __init__(self, id, tenant_id, world_id, name, is_interactive, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.name = name
                self.is_interactive = bool(is_interactive)
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleMap(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['name'],
            row['is_interactive'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteTokenboardRepository:
    """SQLite implementation of Tokenboard repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, tokenboard: object) -> object:
        now = datetime.now().isoformat()

        if tokenboard.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO tokenboards (tenant_id, world_id, name, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    tokenboard.tenant_id.value,
                    tokenboard.world_id.value,
                    tokenboard.name,
                    getattr(tokenboard, 'is_active', False),
                    now,
                    now
                ))
                tokenboard_id = cursor.lastrowid
                object.__setattr__(tokenboard, 'id', EntityId(tokenboard_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE tokenboards
                    SET name = ?, is_active = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    tokenboard.name,
                    getattr(tokenboard, 'is_active', False),
                    tokenboard.id.value,
                    tokenboard.tenant_id.value
                ))

        return tokenboard

    def find_by_id(self, tenant_id: TenantId, tokenboard_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM tokenboards WHERE id = ? AND tenant_id = ?
            """, (tokenboard_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_tokenboard(row)

    def find_active(self, tenant_id: TenantId, world_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM tokenboards WHERE world_id = ? AND tenant_id = ? AND is_active = 1 LIMIT 1
            """, (world_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_tokenboard(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tokenboards WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_tokenboard(row) for row in rows]

    def delete(self, tenant_id: TenantId, tokenboard_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM tokenboards WHERE id = ? AND tenant_id = ?
            """, (tokenboard_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_tokenboard(self, row: sqlite3.Row) -> object:
        class SimpleTokenboard:
            def __init__(self, id, tenant_id, world_id, name, is_active, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.name = name
                self.is_active = bool(is_active)
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleTokenboard(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['name'],
            row['is_active'],
            row['created_at'],
            row['updated_at']
        )
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

            # Sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    story_id INTEGER,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE SET NULL
                )
            """)

            # Tags table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    tag_type TEXT NOT NULL,
                    color TEXT,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Notes table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT,
                    is_pinned INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Templates table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    template_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    parent_template_id INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                    FOREIGN KEY (parent_template_id) REFERENCES templates(id) ON DELETE SET NULL
                )
            """)

            # Choices table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS choices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    story_id INTEGER,
                    name TEXT NOT NULL,
                    choice_type TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE SET NULL
                )
            """)

            # Flowcharts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS flowcharts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    story_id INTEGER,
                    name TEXT NOT NULL,
                    is_active INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE SET NULL
                )
            """)

            # Handouts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS handouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    session_id INTEGER,
                    title TEXT NOT NULL,
                    content TEXT,
                    is_revealed INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL
                )
            """)

            # Images table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Inspirations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS inspirations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    category TEXT,
                    content TEXT NOT NULL,
                    is_used INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Maps table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS maps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    is_interactive INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Tokenboards table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tokenboards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    is_active INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
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



class SQLiteSessionRepository:
    """SQLite implementation of Session repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, session: object) -> object:
        now = datetime.now().isoformat()

        if session.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO sessions (tenant_id, world_id, name, description, story_id, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.tenant_id.value,
                    session.world_id.value,
                    session.name,
                    getattr(session, 'description', None),
                    getattr(session, 'story_id', None),
                    getattr(session, 'is_active', True),
                    now,
                    now
                ))
                session_id = cursor.lastrowid
                object.__setattr__(session, 'id', EntityId(session_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE sessions
                    SET name = ?, description = ?, story_id = ?, is_active = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    session.name,
                    getattr(session, 'description', None),
                    getattr(session, 'story_id', None),
                    getattr(session, 'is_active', True),
                    session.id.value,
                    session.tenant_id.value
                ))

        return session

    def find_by_id(self, tenant_id: TenantId, session_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM sessions WHERE id = ? AND tenant_id = ?
            """, (session_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_session(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM sessions WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_session(row) for row in rows]

    def list_by_story(self, tenant_id: TenantId, story_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM sessions WHERE story_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (story_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_session(row) for row in rows]

    def list_active(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM sessions WHERE world_id = ? AND tenant_id = ? AND is_active = 1 ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_session(row) for row in rows]

    def delete(self, tenant_id: TenantId, session_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM sessions WHERE id = ? AND tenant_id = ?
            """, (session_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_session(self, row: sqlite3.Row) -> object:
        class SimpleSession:
            def __init__(self, id, tenant_id, world_id, name, description, story_id, is_active, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.name = name
                self.description = description
                self.story_id = EntityId(story_id) if story_id else None
                self.is_active = is_active
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleSession(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['name'],
            row['description'],
            row['story_id'],
            row['is_active'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteTagRepository:
    """SQLite implementation of Tag repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, tag: Tag) -> Tag:
        now = datetime.now().isoformat()

        if tag.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO tags (tenant_id, world_id, name, tag_type, color, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tag.tenant_id.value,
                    tag.world_id.value,
                    tag.name.value,
                    tag.tag_type.value,
                    tag.color,
                    tag.description,
                    now,
                    now
                ))
                tag_id = cursor.lastrowid
                object.__setattr__(tag, 'id', EntityId(tag_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE tags
                    SET name = ?, tag_type = ?, color = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    tag.name.value,
                    tag.tag_type.value,
                    tag.color,
                    tag.description,
                    tag.id.value,
                    tag.tenant_id.value
                ))

        return tag

    def find_by_id(self, tenant_id: TenantId, tag_id: EntityId) -> Optional[Tag]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM tags WHERE id = ? AND tenant_id = ?
            """, (tag_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_tag(row)

    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: "TagName") -> Optional[Tag]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM tags WHERE world_id = ? AND tenant_id = ? AND name = ? LIMIT 1
            """, (world_id.value, tenant_id.value, name.value)).fetchone()

            if not row:
                return None
            return self._row_to_tag(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Tag]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tags WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_tag(row) for row in rows]

    def list_by_type(self, tenant_id: TenantId, world_id: EntityId, tag_type: "TagType", limit: int = 50, offset: int = 0) -> List[Tag]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tags WHERE world_id = ? AND tenant_id = ? AND tag_type = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, tag_type.value, limit, offset)).fetchall()
            return [self._row_to_tag(row) for row in rows]

    def delete(self, tenant_id: TenantId, tag_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM tags WHERE id = ? AND tenant_id = ?
            """, (tag_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: "TagName", tag_type: "TagType") -> bool:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT 1 FROM tags WHERE world_id = ? AND tenant_id = ? AND name = ? AND tag_type = ? LIMIT 1
            """, (world_id.value, tenant_id.value, name.value, tag_type.value)).fetchone()
            return row is not None

    def _row_to_tag(self, row: sqlite3.Row) -> Tag:
        return Tag(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=row['name'],
            tag_type=row['tag_type'],
            color=row['color'],
            description=row['description'],
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteNoteRepository:
    """SQLite implementation of Note repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, note: Note) -> Note:
        now = datetime.now().isoformat()

        if note.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO notes (tenant_id, world_id, title, content, tags, is_pinned, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    note.tenant_id.value,
                    note.world_id.value,
                    note.title,
                    note.content,
                    json.dumps(note.tags),
                    note.is_pinned,
                    now,
                    now
                ))
                note_id = cursor.lastrowid
                object.__setattr__(note, 'id', EntityId(note_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE notes
                    SET title = ?, content = ?, tags = ?, is_pinned = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    note.title,
                    note.content,
                    json.dumps(note.tags),
                    note.is_pinned,
                    note.id.value,
                    note.tenant_id.value
                ))

        return note

    def find_by_id(self, tenant_id: TenantId, note_id: EntityId) -> Optional[Note]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM notes WHERE id = ? AND tenant_id = ?
            """, (note_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_note(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Note]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM notes WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_note(row) for row in rows]

    def list_pinned(self, tenant_id: TenantId, world_id: EntityId, limit: int = 20, offset: int = 0) -> List[Note]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM notes WHERE world_id = ? AND tenant_id = ? AND is_pinned = 1 ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_note(row) for row in rows]

    def search_by_content(self, tenant_id: TenantId, search_term: str, limit: int = 20) -> List[Note]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM notes WHERE tenant_id = ? AND (title LIKE ? OR content LIKE ?) LIMIT ?
            """, (tenant_id.value, f'%{search_term}%', f'%{search_term}%', limit)).fetchall()
            return [self._row_to_note(row) for row in rows]

    def delete(self, tenant_id: TenantId, note_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM notes WHERE id = ? AND tenant_id = ?
            """, (note_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_note(self, row: sqlite3.Row) -> Note:
        return Note(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            title=row['title'],
            content=row['content'],
            tags=json.loads(row['tags']),
            is_pinned=row['is_pinned'],
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteTemplateRepository:
    """SQLite implementation of Template repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, template: Template) -> Template:
        now = datetime.now().isoformat()

        if template.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO templates (tenant_id, world_id, name, description, template_type, content, parent_template_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    template.tenant_id.value,
                    template.world_id.value,
                    template.name.value,
                    template.description,
                    template.template_type.value,
                    template.content.value,
                    template.parent_template_id.value if template.parent_template_id else None,
                    now,
                    now
                ))
                template_id = cursor.lastrowid
                object.__setattr__(template, 'id', EntityId(template_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE templates
                    SET name = ?, description = ?, template_type = ?, content = ?, parent_template_id = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    template.name.value,
                    template.description,
                    template.template_type.value,
                    template.content.value,
                    template.parent_template_id.value if template.parent_template_id else None,
                    template.id.value,
                    template.tenant_id.value
                ))

        return template

    def find_by_id(self, tenant_id: TenantId, template_id: EntityId) -> Optional[Template]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM templates WHERE id = ? AND tenant_id = ?
            """, (template_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_template(row)

    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: "TemplateName") -> Optional[Template]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM templates WHERE world_id = ? AND tenant_id = ? AND name = ? LIMIT 1
            """, (world_id.value, tenant_id.value, name.value)).fetchone()

            if not row:
                return None
            return self._row_to_template(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Template]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM templates WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_template(row) for row in rows]

    def list_by_type(self, tenant_id: TenantId, world_id: EntityId, template_type: "TemplateType", limit: int = 50, offset: int = 0) -> List[Template]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM templates WHERE world_id = ? AND tenant_id = ? AND template_type = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, template_type.value, limit, offset)).fetchall()
            return [self._row_to_template(row) for row in rows]

    def list_runes(self, tenant_id: TenantId, parent_template_id: EntityId, limit: int = 50, offset: int = 0) -> List[Template]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM templates WHERE parent_template_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (parent_template_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_template(row) for row in rows]

    def delete(self, tenant_id: TenantId, template_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM templates WHERE id = ? AND tenant_id = ?
            """, (template_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: "TemplateName") -> bool:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT 1 FROM templates WHERE world_id = ? AND tenant_id = ? AND name = ? LIMIT 1
            """, (world_id.value, tenant_id.value, name.value)).fetchone()
            return row is not None

    def _row_to_template(self, row: sqlite3.Row) -> Template:
        return Template(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=row['name'],
            description=row['description'],
            template_type=row['template_type'],
            content=row['content'],
            rune_ids=[],
            parent_template_id=EntityId(row['parent_template_id']) if row['parent_template_id'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteChoiceRepository:
    """SQLite implementation of Choice repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, choice: object) -> object:
        now = datetime.now().isoformat()

        if choice.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO choices (tenant_id, world_id, story_id, name, choice_type, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    choice.tenant_id.value,
                    choice.world_id.value,
                    getattr(choice, 'story_id', None),
                    choice.name,
                    getattr(choice, 'choice_type', None),
                    now,
                    now
                ))
                choice_id = cursor.lastrowid
                object.__setattr__(choice, 'id', EntityId(choice_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE choices
                    SET name = ?, choice_type = ?, story_id = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    choice.name,
                    getattr(choice, 'choice_type', None),
                    getattr(choice, 'story_id', None),
                    choice.id.value,
                    choice.tenant_id.value
                ))

        return choice

    def find_by_id(self, tenant_id: TenantId, choice_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM choices WHERE id = ? AND tenant_id = ?
            """, (choice_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_choice(row)

    def list_by_story(self, tenant_id: TenantId, story_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM choices WHERE story_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (story_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_choice(row) for row in rows]

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM choices WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_choice(row) for row in rows]

    def list_by_type(self, tenant_id: TenantId, world_id: EntityId, choice_type: str, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM choices WHERE world_id = ? AND tenant_id = ? AND choice_type = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, choice_type, limit, offset)).fetchall()
            return [self._row_to_choice(row) for row in rows]

    def delete(self, tenant_id: TenantId, choice_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM choices WHERE id = ? AND tenant_id = ?
            """, (choice_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_choice(self, row: sqlite3.Row) -> object:
        class SimpleChoice:
            def __init__(self, id, tenant_id, world_id, story_id, name, choice_type, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.story_id = EntityId(story_id) if story_id else None
                self.name = name
                self.choice_type = choice_type
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleChoice(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['story_id'],
            row['name'],
            row['choice_type'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteFlowchartRepository:
    """SQLite implementation of Flowchart repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, flowchart: object) -> object:
        now = datetime.now().isoformat()

        if flowchart.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO flowcharts (tenant_id, world_id, story_id, name, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    flowchart.tenant_id.value,
                    flowchart.world_id.value,
                    getattr(flowchart, 'story_id', None),
                    flowchart.name,
                    getattr(flowchart, 'is_active', False),
                    now,
                    now
                ))
                flowchart_id = cursor.lastrowid
                object.__setattr__(flowchart, 'id', EntityId(flowchart_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE flowcharts
                    SET name = ?, is_active = ?, story_id = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    flowchart.name,
                    getattr(flowchart, 'is_active', False),
                    getattr(flowchart, 'story_id', None),
                    flowchart.id.value,
                    flowchart.tenant_id.value
                ))

        return flowchart

    def find_by_id(self, tenant_id: TenantId, flowchart_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM flowcharts WHERE id = ? AND tenant_id = ?
            """, (flowchart_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_flowchart(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM flowcharts WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_flowchart(row) for row in rows]

    def list_by_story(self, tenant_id: TenantId, story_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM flowcharts WHERE story_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (story_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_flowchart(row) for row in rows]

    def find_active(self, tenant_id: TenantId, world_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM flowcharts WHERE world_id = ? AND tenant_id = ? AND is_active = 1 LIMIT 1
            """, (world_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_flowchart(row)

    def delete(self, tenant_id: TenantId, flowchart_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM flowcharts WHERE id = ? AND tenant_id = ?
            """, (flowchart_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_flowchart(self, row: sqlite3.Row) -> object:
        class SimpleFlowchart:
            def __init__(self, id, tenant_id, world_id, story_id, name, is_active, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.story_id = EntityId(story_id) if story_id else None
                self.name = name
                self.is_active = bool(is_active)
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleFlowchart(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['story_id'],
            row['name'],
            row['is_active'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteHandoutRepository:
    """SQLite implementation of Handout repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, handout: object) -> object:
        now = datetime.now().isoformat()

        if handout.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO handouts (tenant_id, world_id, session_id, title, content, is_revealed, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    handout.tenant_id.value,
                    handout.world_id.value,
                    getattr(handout, 'session_id', None),
                    handout.title,
                    getattr(handout, 'content', None),
                    getattr(handout, 'is_revealed', False),
                    now,
                    now
                ))
                handout_id = cursor.lastrowid
                object.__setattr__(handout, 'id', EntityId(handout_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE handouts
                    SET title = ?, content = ?, is_revealed = ?, session_id = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    handout.title,
                    getattr(handout, 'content', None),
                    getattr(handout, 'is_revealed', False),
                    getattr(handout, 'session_id', None),
                    handout.id.value,
                    handout.tenant_id.value
                ))

        return handout

    def find_by_id(self, tenant_id: TenantId, handout_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM handouts WHERE id = ? AND tenant_id = ?
            """, (handout_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_handout(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM handouts WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_handout(row) for row in rows]

    def list_by_session(self, tenant_id: TenantId, session_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM handouts WHERE session_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (session_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_handout(row) for row in rows]

    def list_revealed(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM handouts WHERE world_id = ? AND tenant_id = ? AND is_revealed = 1 ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_handout(row) for row in rows]

    def delete(self, tenant_id: TenantId, handout_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM handouts WHERE id = ? AND tenant_id = ?
            """, (handout_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_handout(self, row: sqlite3.Row) -> object:
        class SimpleHandout:
            def __init__(self, id, tenant_id, world_id, session_id, title, content, is_revealed, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.session_id = EntityId(session_id) if session_id else None
                self.title = title
                self.content = content
                self.is_revealed = bool(is_revealed)
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleHandout(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['session_id'],
            row['title'],
            row['content'],
            row['is_revealed'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteImageRepository:
    """SQLite implementation of Image repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, image: object) -> object:
        now = datetime.now().isoformat()

        if image.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO images (tenant_id, world_id, name, path, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    image.tenant_id.value,
                    image.world_id.value,
                    image.name,
                    image.path,
                    now,
                    now
                ))
                image_id = cursor.lastrowid
                object.__setattr__(image, 'id', EntityId(image_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE images
                    SET name = ?, path = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    image.name,
                    image.path,
                    image.id.value,
                    image.tenant_id.value
                ))

        return image

    def find_by_id(self, tenant_id: TenantId, image_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM images WHERE id = ? AND tenant_id = ?
            """, (image_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_image(row)

    def find_by_path(self, tenant_id: TenantId, world_id: EntityId, path: str) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM images WHERE world_id = ? AND tenant_id = ? AND path = ? LIMIT 1
            """, (world_id.value, tenant_id.value, path)).fetchone()

            if not row:
                return None
            return self._row_to_image(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM images WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_image(row) for row in rows]

    def delete(self, tenant_id: TenantId, image_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM images WHERE id = ? AND tenant_id = ?
            """, (image_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def exists(self, tenant_id: TenantId, world_id: EntityId, path: str) -> bool:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT 1 FROM images WHERE world_id = ? AND tenant_id = ? AND path = ? LIMIT 1
            """, (world_id.value, tenant_id.value, path)).fetchone()
            return row is not None

    def _row_to_image(self, row: sqlite3.Row) -> object:
        class SimpleImage:
            def __init__(self, id, tenant_id, world_id, name, path, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.name = name
                self.path = path
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleImage(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['name'],
            row['path'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteInspirationRepository:
    """SQLite implementation of Inspiration repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, inspiration: object) -> object:
        now = datetime.now().isoformat()

        if inspiration.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO inspirations (tenant_id, world_id, category, content, is_used, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    inspiration.tenant_id.value,
                    inspiration.world_id.value,
                    getattr(inspiration, 'category', None),
                    inspiration.content,
                    getattr(inspiration, 'is_used', False),
                    now,
                    now
                ))
                inspiration_id = cursor.lastrowid
                object.__setattr__(inspiration, 'id', EntityId(inspiration_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE inspirations
                    SET category = ?, content = ?, is_used = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    getattr(inspiration, 'category', None),
                    inspiration.content,
                    getattr(inspiration, 'is_used', False),
                    inspiration.id.value,
                    inspiration.tenant_id.value
                ))

        return inspiration

    def find_by_id(self, tenant_id: TenantId, inspiration_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM inspirations WHERE id = ? AND tenant_id = ?
            """, (inspiration_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_inspiration(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM inspirations WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_inspiration(row) for row in rows]

    def list_by_category(self, tenant_id: TenantId, world_id: EntityId, category: str, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM inspirations WHERE world_id = ? AND tenant_id = ? AND category = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, category, limit, offset)).fetchall()
            return [self._row_to_inspiration(row) for row in rows]

    def list_unused(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM inspirations WHERE world_id = ? AND tenant_id = ? AND is_used = 0 ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_inspiration(row) for row in rows]

    def search_by_content(self, tenant_id: TenantId, search_term: str, limit: int = 20) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM inspirations WHERE tenant_id = ? AND content LIKE ? LIMIT ?
            """, (tenant_id.value, f'%{search_term}%', limit)).fetchall()
            return [self._row_to_inspiration(row) for row in rows]

    def delete(self, tenant_id: TenantId, inspiration_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM inspirations WHERE id = ? AND tenant_id = ?
            """, (inspiration_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_inspiration(self, row: sqlite3.Row) -> object:
        class SimpleInspiration:
            def __init__(self, id, tenant_id, world_id, category, content, is_used, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.category = category
                self.content = content
                self.is_used = bool(is_used)
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleInspiration(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['category'],
            row['content'],
            row['is_used'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteMapRepository:
    """SQLite implementation of Map repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, map_obj: object) -> object:
        now = datetime.now().isoformat()

        if map_obj.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO maps (tenant_id, world_id, name, is_interactive, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    map_obj.tenant_id.value,
                    map_obj.world_id.value,
                    map_obj.name,
                    getattr(map_obj, 'is_interactive', False),
                    now,
                    now
                ))
                map_id = cursor.lastrowid
                object.__setattr__(map_obj, 'id', EntityId(map_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE maps
                    SET name = ?, is_interactive = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    map_obj.name,
                    getattr(map_obj, 'is_interactive', False),
                    map_obj.id.value,
                    map_obj.tenant_id.value
                ))

        return map_obj

    def find_by_id(self, tenant_id: TenantId, map_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM maps WHERE id = ? AND tenant_id = ?
            """, (map_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_map(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM maps WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_map(row) for row in rows]

    def list_interactive(self, tenant_id: TenantId, world_id: EntityId, limit: int = 20, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM maps WHERE world_id = ? AND tenant_id = ? AND is_interactive = 1 ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_map(row) for row in rows]

    def delete(self, tenant_id: TenantId, map_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM maps WHERE id = ? AND tenant_id = ?
            """, (map_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_map(self, row: sqlite3.Row) -> object:
        class SimpleMap:
            def __init__(self, id, tenant_id, world_id, name, is_interactive, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.name = name
                self.is_interactive = bool(is_interactive)
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleMap(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['name'],
            row['is_interactive'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteTokenboardRepository:
    """SQLite implementation of Tokenboard repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, tokenboard: object) -> object:
        now = datetime.now().isoformat()

        if tokenboard.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO tokenboards (tenant_id, world_id, name, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    tokenboard.tenant_id.value,
                    tokenboard.world_id.value,
                    tokenboard.name,
                    getattr(tokenboard, 'is_active', False),
                    now,
                    now
                ))
                tokenboard_id = cursor.lastrowid
                object.__setattr__(tokenboard, 'id', EntityId(tokenboard_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE tokenboards
                    SET name = ?, is_active = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    tokenboard.name,
                    getattr(tokenboard, 'is_active', False),
                    tokenboard.id.value,
                    tokenboard.tenant_id.value
                ))

        return tokenboard

    def find_by_id(self, tenant_id: TenantId, tokenboard_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM tokenboards WHERE id = ? AND tenant_id = ?
            """, (tokenboard_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_tokenboard(row)

    def find_active(self, tenant_id: TenantId, world_id: EntityId) -> Optional[object]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM tokenboards WHERE world_id = ? AND tenant_id = ? AND is_active = 1 LIMIT 1
            """, (world_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_tokenboard(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tokenboards WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_tokenboard(row) for row in rows]

    def delete(self, tenant_id: TenantId, tokenboard_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM tokenboards WHERE id = ? AND tenant_id = ?
            """, (tokenboard_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_tokenboard(self, row: sqlite3.Row) -> object:
        class SimpleTokenboard:
            def __init__(self, id, tenant_id, world_id, name, is_active, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.name = name
                self.is_active = bool(is_active)
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleTokenboard(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['name'],
            row['is_active'],
            row['created_at'],
            row['updated_at']
        )

class SQLiteQuestChainRepository:
    """SQLite implementation of QuestChain repository."""
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, quest_chain):
        from datetime import datetime
        now = datetime.now().isoformat()
        if quest_chain.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO quest_chains (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    quest_chain.tenant_id.value,
                    quest_chain.world_id.value if hasattr(quest_chain, "world_id") else None,
                    quest_chain.name,
                    getattr(quest_chain, "description", None),
                    now, now
                ))
                object.__setattr__(quest_chain, "id", EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE quest_chains SET name = ?, description = ? WHERE id = ? AND tenant_id = ?
                """, (
                    quest_chain.name,
                    getattr(quest_chain, "description", None),
                    quest_chain.id.value,
                    quest_chain.tenant_id.value
                ))
        return quest_chain

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM quest_chains WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM quest_chains WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM quest_chains WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        from src.domain.entities.quest_chain import QuestChain
        from src.domain.value_objects.common import Description, Timestamp
        return QuestChain(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteQuestNodeRepository:
    """SQLite implementation of QuestNode repository."""
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, quest_node):
        from datetime import datetime
        now = datetime.now().isoformat()
        if quest_node.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO quest_nodes (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    quest_node.tenant_id.value,
                    quest_node.world_id.value if hasattr(quest_node, "world_id") else None,
                    quest_node.name,
                    getattr(quest_node, "description", None),
                    now, now
                ))
                object.__setattr__(quest_node, "id", EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE quest_nodes SET name = ?, description = ? WHERE id = ? AND tenant_id = ?
                """, (
                    quest_node.name,
                    getattr(quest_node, "description", None),
                    quest_node.id.value,
                    quest_node.tenant_id.value
                ))
        return quest_node

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM quest_nodes WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM quest_nodes WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM quest_nodes WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        from src.domain.entities.quest_node import QuestNode
        from src.domain.value_objects.common import Description, Timestamp
        return QuestNode(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteQuestPrerequisiteRepository:
    """SQLite implementation of QuestPrerequisite repository."""
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, prereq):
        from datetime import datetime
        now = datetime.now().isoformat()
        if prereq.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO quest_prerequisites (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    prereq.tenant_id.value,
                    prereq.world_id.value if hasattr(prereq, "world_id") else None,
                    prereq.name,
                    getattr(prereq, "description", None),
                    now, now
                ))
                object.__setattr__(prereq, "id", EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE quest_prerequisites SET name = ?, description = ? WHERE id = ? AND tenant_id = ?
                """, (
                    prereq.name,
                    getattr(prereq, "description", None),
                    prereq.id.value,
                    prereq.tenant_id.value
                ))
        return prereq

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM quest_prerequisites WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM quest_prerequisites WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM quest_prerequisites WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        from src.domain.entities.quest_prerequisite import QuestPrerequisite
        from src.domain.value_objects.common import Description, Timestamp
        return QuestPrerequisite(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteQuestObjectiveRepository:
    """SQLite implementation of QuestObjective repository."""
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, objective):
        from datetime import datetime
        now = datetime.now().isoformat()
        if objective.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO quest_objectives (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    objective.tenant_id.value,
                    objective.world_id.value if hasattr(objective, "world_id") else None,
                    objective.name,
                    getattr(objective, "description", None),
                    now, now
                ))
                object.__setattr__(objective, "id", EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE quest_objectives SET name = ?, description = ? WHERE id = ? AND tenant_id = ?
                """, (
                    objective.name,
                    getattr(objective, "description", None),
                    objective.id.value,
                    objective.tenant_id.value
                ))
        return objective

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM quest_objectives WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM quest_objectives WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM quest_objectives WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        from src.domain.entities.quest_objective import QuestObjective
        from src.domain.value_objects.common import Description, Timestamp
        return QuestObjective(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteQuestTrackerRepository:
    """SQLite implementation of QuestTracker repository."""
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, tracker):
        from datetime import datetime
        now = datetime.now().isoformat()
        if tracker.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO quest_trackers (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    tracker.tenant_id.value,
                    tracker.world_id.value if hasattr(tracker, "world_id") else None,
                    tracker.name,
                    getattr(tracker, "description", None),
                    now, now
                ))
                object.__setattr__(tracker, "id", EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE quest_trackers SET name = ?, description = ? WHERE id = ? AND tenant_id = ?
                """, (
                    tracker.name,
                    getattr(tracker, "description", None),
                    tracker.id.value,
                    tracker.tenant_id.value
                ))
        return tracker

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM quest_trackers WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM quest_trackers WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM quest_trackers WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        from src.domain.entities.quest_tracker import QuestTracker
        from src.domain.value_objects.common import Description, Timestamp
        return QuestTracker(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteQuestGiverRepository:
    """SQLite implementation of QuestGiver repository."""
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, giver):
        from datetime import datetime
        now = datetime.now().isoformat()
        if giver.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO quest_givers (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    giver.tenant_id.value,
                    giver.world_id.value if hasattr(giver, "world_id") else None,
                    giver.name,
                    getattr(giver, "description", None),
                    now, now
                ))
                object.__setattr__(giver, "id", EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE quest_givers SET name = ?, description = ? WHERE id = ? AND tenant_id = ?
                """, (
                    giver.name,
                    getattr(giver, "description", None),
                    giver.id.value,
                    giver.tenant_id.value
                ))
        return giver

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM quest_givers WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM quest_givers WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM quest_givers WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        from src.domain.entities.quest_giver import QuestGiver
        from src.domain.value_objects.common import Description, Timestamp
        return QuestGiver(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteQuestRewardRepository:
    """SQLite implementation of QuestReward repository."""
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, reward):
        from datetime import datetime
        now = datetime.now().isoformat()
        if reward.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO quest_rewards (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    reward.tenant_id.value,
                    reward.world_id.value if hasattr(reward, "world_id") else None,
                    reward.name,
                    getattr(reward, "description", None),
                    now, now
                ))
                object.__setattr__(reward, "id", EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE quest_rewards SET name = ?, description = ? WHERE id = ? AND tenant_id = ?
                """, (
                    reward.name,
                    getattr(reward, "description", None),
                    reward.id.value,
                    reward.tenant_id.value
                ))
        return reward

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM quest_rewards WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM quest_rewards WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM quest_rewards WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        from src.domain.entities.quest_reward import QuestReward
        from src.domain.value_objects.common import Description, Timestamp
        return QuestReward(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteQuestRewardTierRepository:
    """SQLite implementation of QuestRewardTier repository."""
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, tier):
        from datetime import datetime
        now = datetime.now().isoformat()
        if tier.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO quest_reward_tiers (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    tier.tenant_id.value,
                    tier.world_id.value if hasattr(tier, "world_id") else None,
                    tier.name,
                    getattr(tier, "description", None),
                    now, now
                ))
                object.__setattr__(tier, "id", EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE quest_reward_tiers SET name = ?, description = ? WHERE id = ? AND tenant_id = ?
                """, (
                    tier.name,
                    getattr(tier, "description", None),
                    tier.id.value,
                    tier.tenant_id.value
                ))
        return tier

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM quest_reward_tiers WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM quest_reward_tiers WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM quest_reward_tiers WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        from src.domain.entities.quest_reward_tier import QuestRewardTier
        from src.domain.value_objects.common import Description, Timestamp
        return QuestRewardTier(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )

class SQLiteSkillRepository:
    """SQLite implementation of Skill repository."""
    def __init__(self, db: SQLiteDatabase):
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO skills (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entity.tenant_id.value,
                    entity.world_id.value if hasattr(entity, "world_id") else None,
                    entity.name,
                    getattr(entity, "description", None),
                    now, now
                ))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE skills SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    entity.name,
                    getattr(entity, "description", None),
                    entity.id.value,
                    entity.tenant_id.value
                ))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM skills WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM skills WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM skills WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        from src.domain.entities.skill import Skill
        from src.domain.value_objects.common import Description, Timestamp
        return Skill(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )

class SQLitePerkRepository:
    """SQLite implementation of Perk repository."""
    def __init__(self, db: SQLiteDatabase):
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO perks (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entity.tenant_id.value,
                    entity.world_id.value if hasattr(entity, "world_id") else None,
                    entity.name,
                    getattr(entity, "description", None),
                    now, now
                ))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE perks SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    entity.name,
                    getattr(entity, "description", None),
                    entity.id.value,
                    entity.tenant_id.value
                ))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM perks WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM perks WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM perks WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        from src.domain.entities.perk import Perk
        from src.domain.value_objects.common import Description, Timestamp
        return Perk(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )

class SQLiteTraitRepository:
    """SQLite implementation of Trait repository."""
    def __init__(self, db: SQLiteDatabase):
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO traits (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entity.tenant_id.value,
                    entity.world_id.value if hasattr(entity, "world_id") else None,
                    entity.name,
                    getattr(entity, "description", None),
                    now, now
                ))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE traits SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    entity.name,
                    getattr(entity, "description", None),
                    entity.id.value,
                    entity.tenant_id.value
                ))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM traits WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM traits WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM traits WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        from src.domain.entities.trait import Trait
        from src.domain.value_objects.common import Description, Timestamp
        return Trait(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )

class SQLiteAttributeRepository:
    """SQLite implementation of Attribute repository."""
    def __init__(self, db: SQLiteDatabase):
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO attributes (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entity.tenant_id.value,
                    entity.world_id.value if hasattr(entity, "world_id") else None,
                    entity.name,
                    getattr(entity, "description", None),
                    now, now
                ))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE attributes SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    entity.name,
                    getattr(entity, "description", None),
                    entity.id.value,
                    entity.tenant_id.value
                ))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM attributes WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM attributes WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM attributes WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        from src.domain.entities.attribute import Attribute
        from src.domain.value_objects.common import Description, Timestamp
        return Attribute(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )

class SQLiteExperienceRepository:
    """SQLite implementation of Experience repository."""
    def __init__(self, db: SQLiteDatabase):
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO experiences (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entity.tenant_id.value,
                    entity.world_id.value if hasattr(entity, "world_id") else None,
                    entity.name,
                    getattr(entity, "description", None),
                    now, now
                ))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE experiences SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    entity.name,
                    getattr(entity, "description", None),
                    entity.id.value,
                    entity.tenant_id.value
                ))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM experiences WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM experiences WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM experiences WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        from src.domain.entities.experience import Experience
        from src.domain.value_objects.common import Description, Timestamp
        return Experience(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )

class SQLiteLevelUpRepository:
    """SQLite implementation of LevelUp repository."""
    def __init__(self, db: SQLiteDatabase):
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO level_ups (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entity.tenant_id.value,
                    entity.world_id.value if hasattr(entity, "world_id") else None,
                    entity.name,
                    getattr(entity, "description", None),
                    now, now
                ))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE level_ups SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    entity.name,
                    getattr(entity, "description", None),
                    entity.id.value,
                    entity.tenant_id.value
                ))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM level_ups WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM level_ups WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM level_ups WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        from src.domain.entities.level_up import LevelUp
        from src.domain.value_objects.common import Description, Timestamp
        return LevelUp(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )

class SQLiteTalentTreeRepository:
    """SQLite implementation of TalentTree repository."""
    def __init__(self, db: SQLiteDatabase):
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO talent_trees (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entity.tenant_id.value,
                    entity.world_id.value if hasattr(entity, "world_id") else None,
                    entity.name,
                    getattr(entity, "description", None),
                    now, now
                ))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE talent_trees SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    entity.name,
                    getattr(entity, "description", None),
                    entity.id.value,
                    entity.tenant_id.value
                ))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM talent_trees WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM talent_trees WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM talent_trees WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        from src.domain.entities.talent_tree import TalentTree
        from src.domain.value_objects.common import Description, Timestamp
        return TalentTree(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )

class SQLiteMasteryRepository:
    """SQLite implementation of Mastery repository."""
    def __init__(self, db: SQLiteDatabase):
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO masterys (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entity.tenant_id.value,
                    entity.world_id.value if hasattr(entity, "world_id") else None,
                    entity.name,
                    getattr(entity, "description", None),
                    now, now
                ))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE masterys SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    entity.name,
                    getattr(entity, "description", None),
                    entity.id.value,
                    entity.tenant_id.value
                ))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM masterys WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM masterys WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM masterys WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        from src.domain.entities.mastery import Mastery
        from src.domain.value_objects.common import Description, Timestamp
        return Mastery(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )

class SQLiteFactionHierarchyRepository:
    """SQLite implementation of FactionHierarchy repository."""
    def __init__(self, db: SQLiteDatabase):
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO faction_hierarchys (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entity.tenant_id.value,
                    entity.world_id.value if hasattr(entity, "world_id") else None,
                    entity.name,
                    getattr(entity, "description", None),
                    now, now
                ))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE faction_hierarchys SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    entity.name,
                    getattr(entity, "description", None),
                    entity.id.value,
                    entity.tenant_id.value
                ))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM faction_hierarchys WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM faction_hierarchys WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM faction_hierarchys WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        from src.domain.entities.faction_hierarchy import FactionHierarchy
        from src.domain.value_objects.common import Description, Timestamp
        return FactionHierarchy(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )

class SQLiteFactionIdeologyRepository:
    """SQLite implementation of FactionIdeology repository."""
    def __init__(self, db: SQLiteDatabase):
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO faction_ideologys (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entity.tenant_id.value,
                    entity.world_id.value if hasattr(entity, "world_id") else None,
                    entity.name,
                    getattr(entity, "description", None),
                    now, now
                ))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE faction_ideologys SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    entity.name,
                    getattr(entity, "description", None),
                    entity.id.value,
                    entity.tenant_id.value
                ))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM faction_ideologys WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM faction_ideologys WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM faction_ideologys WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        from src.domain.entities.faction_ideology import FactionIdeology
        from src.domain.value_objects.common import Description, Timestamp
        return FactionIdeology(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )

class SQLiteFactionLeaderRepository:
    """SQLite implementation of FactionLeader repository."""
    def __init__(self, db: SQLiteDatabase):
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO faction_leaders (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entity.tenant_id.value,
                    entity.world_id.value if hasattr(entity, "world_id") else None,
                    entity.name,
                    getattr(entity, "description", None),
                    now, now
                ))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE faction_leaders SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    entity.name,
                    getattr(entity, "description", None),
                    entity.id.value,
                    entity.tenant_id.value
                ))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM faction_leaders WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM faction_leaders WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM faction_leaders WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        from src.domain.entities.faction_leader import FactionLeader
        from src.domain.value_objects.common import Description, Timestamp
        return FactionLeader(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )

class SQLiteFactionMembershipRepository:
    """SQLite implementation of FactionMembership repository."""
    def __init__(self, db: SQLiteDatabase):
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO faction_memberships (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entity.tenant_id.value,
                    entity.world_id.value if hasattr(entity, "world_id") else None,
                    entity.name,
                    getattr(entity, "description", None),
                    now, now
                ))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE faction_memberships SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    entity.name,
                    getattr(entity, "description", None),
                    entity.id.value,
                    entity.tenant_id.value
                ))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM faction_memberships WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM faction_memberships WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM faction_memberships WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        from src.domain.entities.faction_membership import FactionMembership
        from src.domain.value_objects.common import Description, Timestamp
        return FactionMembership(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )

class SQLiteFactionResourceRepository:
    """SQLite implementation of FactionResource repository."""
    def __init__(self, db: SQLiteDatabase):
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO faction_resources (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entity.tenant_id.value,
                    entity.world_id.value if hasattr(entity, "world_id") else None,
                    entity.name,
                    getattr(entity, "description", None),
                    now, now
                ))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE faction_resources SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    entity.name,
                    getattr(entity, "description", None),
                    entity.id.value,
                    entity.tenant_id.value
                ))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM faction_resources WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM faction_resources WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM faction_resources WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        from src.domain.entities.faction_resource import FactionResource
        from src.domain.value_objects.common import Description, Timestamp
        return FactionResource(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )

class SQLiteFactionTerritoryRepository:
    """SQLite implementation of FactionTerritory repository."""
    def __init__(self, db: SQLiteDatabase):
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO faction_territorys (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entity.tenant_id.value,
                    entity.world_id.value if hasattr(entity, "world_id") else None,
                    entity.name,
                    getattr(entity, "description", None),
                    now, now
                ))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE faction_territorys SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    entity.name,
                    getattr(entity, "description", None),
                    entity.id.value,
                    entity.tenant_id.value
                ))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM faction_territorys WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM faction_territorys WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM faction_territorys WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        from src.domain.entities.faction_territory import FactionTerritory
        from src.domain.value_objects.common import Description, Timestamp
        return FactionTerritory(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )
