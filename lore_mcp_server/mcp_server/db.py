#!/usr/bin/env python3
"""
MCP Server Database and Repositories Initialization
"""

import sys
import json
from pathlib import Path
from typing import Any
from datetime import datetime

# Setup paths for domain imports
lore_system_root = str(Path(__file__).parent.parent.parent)
if lore_system_root not in sys.path:
    sys.path.insert(0, lore_system_root)

# Import domain entities and value objects
from src.domain.value_objects.common import TenantId, EntityId

# Import in-memory repositories
from src.infrastructure.in_memory_repositories import (
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
    InMemorySessionRepository,
    InMemoryTagRepository,
    InMemoryNoteRepository,
    InMemoryTemplateRepository,
    InMemoryChoiceRepository,
    InMemoryFlowchartRepository,
    InMemoryHandoutRepository,
    InMemoryImageRepository,
    InMemoryInspirationRepository,
    InMemoryMapRepository,
    InMemoryTokenboardRepository,
)

# Import SQLite repositories
from src.infrastructure.sqlite_repositories import (
    SQLiteDatabase,
    SQLiteWorldRepository,
    SQLiteCharacterRepository,
    SQLiteItemRepository,
    SQLiteLocationRepository,
    SQLiteEnvironmentRepository,
    SQLiteStoryRepository,
    SQLiteEventRepository,
    SQLitePageRepository,
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

from .persistence import JSONPersistence

# Load configuration
config_path = Path(__file__).parent / "config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

connection_type = config.get("repository", {}).get("connection_type", "in_memory")

# Global instances initialized based on config
sqlite_db = None
world_repo = None
character_repo = None
story_repo = None
event_repo = None
page_repo = None
item_repo = None
location_repo = None
environment_repo = None
texture_repo = None
model3d_repo = None
session_repo = None
tag_repo = None
note_repo = None
template_repo = None
choice_repo = None
flowchart_repo = None
handout_repo = None
image_repo = None
inspiration_repo = None
map_repo = None
tokenboard_repo = None

if connection_type == "sqlite":
    db_path = config.get("repository", {}).get("database_path", "lore_system.db")
    full_db_path = Path(__file__).parent / db_path
    sqlite_db = SQLiteDatabase(str(full_db_path))
    sqlite_db.initialize_schema()

    world_repo = SQLiteWorldRepository(sqlite_db)
    character_repo = SQLiteCharacterRepository(sqlite_db)
    story_repo = SQLiteStoryRepository(sqlite_db)
    event_repo = SQLiteEventRepository(sqlite_db)
    page_repo = SQLitePageRepository(sqlite_db)
    item_repo = SQLiteItemRepository(sqlite_db)
    location_repo = SQLiteLocationRepository(sqlite_db)
    environment_repo = SQLiteEnvironmentRepository(sqlite_db)
    texture_repo = SQLiteTextureRepository(sqlite_db)
    model3d_repo = SQLiteModel3DRepository(sqlite_db)
    session_repo = SQLiteSessionRepository(sqlite_db)
    tag_repo = SQLiteTagRepository(sqlite_db)
    note_repo = SQLiteNoteRepository(sqlite_db)
    template_repo = SQLiteTemplateRepository(sqlite_db)
    choice_repo = SQLiteChoiceRepository(sqlite_db)
    flowchart_repo = SQLiteFlowchartRepository(sqlite_db)
    handout_repo = SQLiteHandoutRepository(sqlite_db)
    image_repo = SQLiteImageRepository(sqlite_db)
    inspiration_repo = SQLiteInspirationRepository(sqlite_db)
    map_repo = SQLiteMapRepository(sqlite_db)
    tokenboard_repo = SQLiteTokenboardRepository(sqlite_db)
else:
    world_repo = InMemoryWorldRepository()
    character_repo = InMemoryCharacterRepository()
    story_repo = InMemoryStoryRepository()
    event_repo = InMemoryEventRepository()
    page_repo = InMemoryPageRepository()
    item_repo = InMemoryItemRepository()
    location_repo = InMemoryLocationRepository()
    environment_repo = InMemoryEnvironmentRepository()
    texture_repo = InMemoryTextureRepository()
    model3d_repo = InMemoryModel3DRepository()
    session_repo = InMemorySessionRepository()
    tag_repo = InMemoryTagRepository()
    note_repo = InMemoryNoteRepository()
    template_repo = InMemoryTemplateRepository()
    choice_repo = InMemoryChoiceRepository()
    flowchart_repo = InMemoryFlowchartRepository()
    handout_repo = InMemoryHandoutRepository()
    image_repo = InMemoryImageRepository()
    inspiration_repo = InMemoryInspirationRepository()
    map_repo = InMemoryMapRepository()
    tokenboard_repo = InMemoryTokenboardRepository()

# Initialize JSON persistence
persistence = JSONPersistence(data_dir=str(Path(__file__).parent / "lore_data"))

# Helpers
def serialize_entity(entity: Any) -> dict:
    """Serialize domain entity to JSON-compatible dict."""
    if entity is None:
        return None

    result = {}
    for field_name, field_value in entity.__dict__.items():
        if field_value is None:
            result[field_name] = None
        elif hasattr(field_value, 'value'):
            val = field_value.value
            if isinstance(val, datetime):
                result[field_name] = val.isoformat()
            else:
                result[field_name] = val
        elif isinstance(field_value, (str, int, float, bool)):
            result[field_name] = field_value
        elif isinstance(field_value, datetime):
            result[field_name] = field_value.isoformat()
        elif isinstance(field_value, list):
            result[field_name] = [
                serialize_entity(item) if hasattr(item, '__dict__')
                else item.value.isoformat() if hasattr(item, 'value') and isinstance(item.value, datetime)
                else item.value if hasattr(item, 'value')
                else str(item)
                for item in field_value
            ]
        else:
            result[field_name] = str(field_value)

    return result

def parse_tenant_id(tenant_id_str: str) -> TenantId:
    """Parse tenant ID from string."""
    try:
        return TenantId(int(tenant_id_str))
    except ValueError:
        return TenantId(abs(hash(tenant_id_str)) % (10**9))

def parse_entity_id(entity_id_str: str) -> EntityId:
    """Parse entity ID from string."""
    try:
        return EntityId(int(entity_id_str))
    except ValueError:
        return EntityId(abs(hash(entity_id_str)) % (10**9))
