#!/usr/bin/env python3
"""
Lore System MCP Server

Provides MCP tools and resources for managing game lore including:
- Worlds, Characters, Stories, Events, Pages
- CRUD operations with full validation
- Multi-tenant support
"""

# CRITICAL: Import MCP library FIRST before manipulating sys.path
# This ensures we get the pip package, not the local 'mcp' folder
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    ImageContent,
    EmbeddedResource,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)

# NOW we can add loreSystem to path for domain imports
import sys
from pathlib import Path

lore_system_root = str(Path(__file__).parent.parent.parent)
if lore_system_root not in sys.path:
    sys.path.insert(0, lore_system_root)  # Insert at beginning for priority

# Add mcp_server directory to path for local imports
mcp_server_root = str(Path(__file__).parent)
if mcp_server_root not in sys.path:
    sys.path.insert(0, mcp_server_root)

# Import standard libraries
import asyncio
import json
from typing import Any, Optional
from datetime import datetime

# Import domain entities and value objects
from src.domain.entities.world import World
from src.domain.entities.character import Character, CharacterElement, CharacterRole
from src.domain.entities.story import Story, StoryType
from src.domain.entities.event import Event, EventOutcome
from src.domain.entities.page import Page
from src.domain.entities.item import Item
from src.domain.entities.location import Location
from src.domain.entities.environment import Environment
from src.domain.entities.texture import Texture
from src.domain.entities.model3d import Model3D
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    WorldName,
    CharacterName,
    Description,
    Backstory,
    Version,
    Timestamp,
    CharacterStatus,
    Rarity,
    StoryName,
    PageName,
    Content,
    DateRange,
    ItemType,
    LocationType,
    TimeOfDay,
    Weather,
    Lighting,
)
from src.domain.value_objects.ability import Ability, AbilityName, PowerLevel

# Import in-memory repositories for demo
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
)

# Import SQLite repositories for production
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
)

# Import persistence layer
from .persistence import JSONPersistence

# Load configuration
config_path = Path(__file__).parent / "config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

# Initialize repositories based on configuration
connection_type = config.get("repository", {}).get("connection_type", "in_memory")

if connection_type == "sqlite":
    db_path = config.get("repository", {}).get("database_path", "lore_system.db")
    # Use path relative to mcp_server directory
    full_db_path = Path(__file__).parent / db_path
    sqlite_db = SQLiteDatabase(str(full_db_path))
    sqlite_db.initialize_schema()

    # Use SQLite repositories for all entities
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
else:
    # Default to in-memory repositories
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

# Initialize JSON persistence
persistence = JSONPersistence(data_dir=str(Path(__file__).parent / "lore_data"))

# Create MCP server
app = Server("lore-system-server")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def serialize_entity(entity: Any) -> dict:
    """Serialize domain entity to JSON-compatible dict."""
    if entity is None:
        return None

    result = {}
    for field_name, field_value in entity.__dict__.items():
        if field_value is None:
            result[field_name] = None
        elif hasattr(field_value, 'value'):
            # Value object
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
    # TenantId expects an integer
    try:
        return TenantId(int(tenant_id_str))
    except ValueError:
        # If it's not numeric, hash it to create a deterministic integer
        return TenantId(abs(hash(tenant_id_str)) % (10**9))


def parse_entity_id(entity_id_str: str) -> EntityId:
    """Parse entity ID from string."""
    try:
        return EntityId(int(entity_id_str))
    except ValueError:
        # If it's not numeric, hash it
        return EntityId(abs(hash(entity_id_str)) % (10**9))


# ============================================================================
# WORLD CRUD OPERATIONS
# ============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        # World operations
        Tool(
            name="create_world",
            description="Create a new world in the lore system",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string", "description": "Tenant identifier"},
                    "name": {"type": "string", "description": "World name (max 100 chars)"},
                    "description": {"type": "string", "description": "World description (max 1000 chars)"},
                    "parent_id": {"type": "string", "description": "Optional parent world ID for hierarchies"},
                },
                "required": ["tenant_id", "name", "description"],
            },
        ),
        Tool(
            name="get_world",
            description="Get a world by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                },
                "required": ["tenant_id", "world_id"],
            },
        ),
        Tool(
            name="list_worlds",
            description="List all worlds for a tenant",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 100},
                    "offset": {"type": "integer", "default": 0},
                },
                "required": ["tenant_id"],
            },
        ),
        Tool(
            name="update_world",
            description="Update world description or name",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "name": {"type": "string", "description": "New name (optional)"},
                    "description": {"type": "string", "description": "New description (optional)"},
                },
                "required": ["tenant_id", "world_id"],
            },
        ),
        Tool(
            name="delete_world",
            description="Delete a world",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                },
                "required": ["tenant_id", "world_id"],
            },
        ),

        # Character operations
        Tool(
            name="create_character",
            description="Create a new character in a world",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "name": {"type": "string", "description": "Character name (max 100 chars)"},
                    "backstory": {"type": "string", "description": "Character backstory (min 100 chars)"},
                    "rarity": {"type": "string", "enum": ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"]},
                    "element": {"type": "string", "enum": ["physical", "fire", "water", "earth", "wind", "light", "dark"]},
                    "role": {"type": "string", "enum": ["dps", "tank", "support", "specialist"]},
                    "base_hp": {"type": "integer", "description": "Base health points"},
                    "base_atk": {"type": "integer", "description": "Base attack"},
                    "base_def": {"type": "integer", "description": "Base defense"},
                    "base_speed": {"type": "integer", "description": "Base speed"},
                    "energy_cost": {"type": "integer", "description": "Ultimate energy cost"},
                },
                "required": ["tenant_id", "world_id", "name", "backstory"],
            },
        ),
        Tool(
            name="get_character",
            description="Get a character by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "character_id": {"type": "string"},
                },
                "required": ["tenant_id", "character_id"],
            },
        ),
        Tool(
            name="list_characters",
            description="List characters in a world",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 100},
                    "offset": {"type": "integer", "default": 0},
                },
                "required": ["tenant_id", "world_id"],
            },
        ),
        Tool(
            name="update_character",
            description="Update character details",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "character_id": {"type": "string"},
                    "backstory": {"type": "string", "description": "New backstory (min 100 chars)"},
                    "status": {"type": "string", "enum": ["active", "inactive"]},
                },
                "required": ["tenant_id", "character_id"],
            },
        ),
        Tool(
            name="delete_character",
            description="Delete a character",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "character_id": {"type": "string"},
                },
                "required": ["tenant_id", "character_id"],
            },
        ),
        Tool(
            name="add_ability",
            description="Add an ability to a character",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "character_id": {"type": "string"},
                    "ability_name": {"type": "string"},
                    "description": {"type": "string"},
                    "power_level": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Power level 1-10 (1=weak, 10=strongest)"},
                },
                "required": ["tenant_id", "character_id", "ability_name", "description", "power_level"],
            },
        ),

        # Story operations
        Tool(
            name="create_story",
            description="Create a new story in a world",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "story_type": {"type": "string", "enum": ["LINEAR", "NON_LINEAR", "INTERACTIVE"], "default": "LINEAR"},
                    "content": {"type": "string"},
                },
                "required": ["tenant_id", "world_id", "name", "description"],
            },
        ),
        Tool(
            name="get_story",
            description="Get a story by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "story_id": {"type": "string"},
                },
                "required": ["tenant_id", "story_id"],
            },
        ),
        Tool(
            name="list_stories",
            description="List stories in a world",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 100},
                    "offset": {"type": "integer", "default": 0},
                },
                "required": ["tenant_id", "world_id"],
            },
        ),

        # Event operations
        Tool(
            name="create_event",
            description="Create a new event in a world. Note: Events require at least one participant (character_id).",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "start_date": {"type": "string", "description": "ISO date string"},
                    "end_date": {"type": "string", "description": "ISO date string (optional)"},
                    "participant_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of character IDs participating in the event (at least 1 required)"
                    },
                    "outcome": {"type": "string", "enum": ["success", "failure", "ongoing"], "default": "ongoing"},
                },
                "required": ["tenant_id", "world_id", "name", "description", "start_date", "participant_ids"],
            },
        ),
        Tool(
            name="list_events",
            description="List events in a world",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 100},
                    "offset": {"type": "integer", "default": 0},
                },
                "required": ["tenant_id", "world_id"],
            },
        ),

        # Page operations
        Tool(
            name="create_page",
            description="Create a custom lore page",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "name": {"type": "string"},
                    "content": {"type": "string", "description": "Page content/body"},
                },
                "required": ["tenant_id", "world_id", "name", "content"],
            },
        ),
        Tool(
            name="list_pages",
            description="List pages in a world",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 100},
                    "offset": {"type": "integer", "default": 0},
                },
                "required": ["tenant_id", "world_id"],
            },
        ),

        # Item operations
        Tool(
            name="create_item",
            description="Create a new item in a world",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "name": {"type": "string", "description": "Item name"},
                    "description": {"type": "string", "description": "Item description"},
                    "item_type": {"type": "string", "enum": ["weapon", "armor", "artifact", "consumable", "tool", "other"]},
                    "rarity": {"type": "string", "enum": ["common", "uncommon", "rare", "epic", "legendary", "mythic"]},
                    "location_id": {"type": "string", "description": "Location ID where item is found (optional)"},
                    "level": {"type": "integer", "description": "Item level (1-100)", "minimum": 1, "maximum": 100},
                    "enhancement": {"type": "integer", "description": "Enhancement level (0+)", "minimum": 0},
                    "max_enhancement": {"type": "integer", "description": "Maximum enhancement level", "minimum": 0},
                    "base_atk": {"type": "integer", "description": "Base attack bonus", "minimum": 0},
                    "base_hp": {"type": "integer", "description": "Base HP bonus", "minimum": 0},
                    "base_def": {"type": "integer", "description": "Base defense bonus", "minimum": 0},
                    "special_stat": {"type": "string", "description": "Special stat name (e.g., 'crit_rate')"},
                    "special_stat_value": {"type": "number", "description": "Special stat value"},
                },
                "required": ["tenant_id", "world_id", "name", "description", "item_type"],
            },
        ),
        Tool(
            name="get_item",
            description="Get an item by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "item_id": {"type": "string"},
                },
                "required": ["tenant_id", "item_id"],
            },
        ),
        Tool(
            name="list_items",
            description="List items in a world",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 50},
                    "offset": {"type": "integer", "default": 0},
                },
                "required": ["tenant_id", "world_id"],
            },
        ),

        # Texture operations
        Tool(
            name="create_texture",
            description="Create a new texture for 3D models",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "name": {"type": "string", "description": "Texture name"},
                    "path": {"type": "string", "description": "Path to texture file"},
                    "texture_type": {"type": "string", "enum": ["diffuse", "normal", "specular", "emissive", "roughness", "metallic"]},
                    "file_size": {"type": "integer", "description": "File size in bytes"},
                    "dimensions": {"type": "string", "description": "Dimensions (e.g., '1024x1024')"},
                    "color_space": {"type": "string", "description": "Color space (e.g., 'sRGB')"},
                    "description": {"type": "string"},
                },
                "required": ["tenant_id", "world_id", "name", "path", "texture_type", "file_size"],
            },
        ),
        Tool(
            name="get_texture",
            description="Get a texture by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "texture_id": {"type": "string"},
                },
                "required": ["tenant_id", "texture_id"],
            },
        ),
        Tool(
            name="list_textures",
            description="List textures in a world",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 100},
                    "offset": {"type": "integer", "default": 0},
                },
                "required": ["tenant_id", "world_id"],
            },
        ),

        # 3D Model operations
        Tool(
            name="create_3d_model",
            description="Create a new 3D model",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "name": {"type": "string", "description": "3D model name"},
                    "path": {"type": "string", "description": "Path to 3D model file"},
                    "model_type": {"type": "string", "enum": ["item", "location", "character", "environment"]},
                    "file_size": {"type": "integer", "description": "File size in bytes"},
                    "poly_count": {"type": "integer", "description": "Number of polygons"},
                    "dimensions": {"type": "string", "description": "Dimensions (e.g., '1x1x1')"},
                    "textures": {"type": "array", "items": {"type": "string"}, "description": "List of texture IDs"},
                    "animations": {"type": "array", "items": {"type": "string"}, "description": "List of animation names"},
                    "description": {"type": "string"},
                },
                "required": ["tenant_id", "world_id", "name", "path", "model_type", "file_size"],
            },
        ),
        Tool(
            name="get_3d_model",
            description="Get a 3D model by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "model_id": {"type": "string"},
                },
                "required": ["tenant_id", "model_id"],
            },
        ),
        Tool(
            name="list_3d_models",
            description="List 3D models in a world",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 100},
                    "offset": {"type": "integer", "default": 0},
                },
                "required": ["tenant_id", "world_id"],
            },
        ),
        Tool(
            name="search_items",
            description="Search items by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "search_term": {"type": "string", "description": "Term to search for in item names"},
                    "limit": {"type": "integer", "default": 20},
                },
                "required": ["tenant_id", "search_term"],
            },
        ),
        Tool(
            name="update_item",
            description="Update item details",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "item_id": {"type": "string"},
                    "name": {"type": "string", "description": "New item name"},
                    "description": {"type": "string", "description": "New item description"},
                    "rarity": {"type": "string", "enum": ["common", "uncommon", "rare", "epic", "legendary", "mythic"]},
                    "location_id": {"type": "string", "description": "New location ID"},
                    "level": {"type": "integer", "description": "New item level (1-100)", "minimum": 1, "maximum": 100},
                },
                "required": ["tenant_id", "item_id"],
            },
        ),
        Tool(
            name="enhance_item",
            description="Enhance an item (increase enhancement level)",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "item_id": {"type": "string"},
                },
                "required": ["tenant_id", "item_id"],
            },
        ),
        Tool(
            name="delete_item",
            description="Delete an item",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "item_id": {"type": "string"},
                },
                "required": ["tenant_id", "item_id"],
            },
        ),

        # Location operations
        Tool(
            name="create_location",
            description="Create a new location in a world",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "name": {"type": "string", "description": "Location name"},
                    "description": {"type": "string", "description": "Location description"},
                    "location_type": {"type": "string", "enum": ["building", "house", "barn", "temple", "castle", "dungeon", "cave", "forest", "mountain", "city", "village", "shop", "tavern", "ruins", "landmark", "other"]},
                    "parent_location_id": {"type": "string", "description": "Parent location ID for hierarchical locations (optional)"},
                },
                "required": ["tenant_id", "world_id", "name", "description", "location_type"],
            },
        ),
        Tool(
            name="get_location",
            description="Get a location by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "location_id": {"type": "string"},
                },
                "required": ["tenant_id", "location_id"],
            },
        ),
        Tool(
            name="list_locations",
            description="List locations in a world",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 50},
                    "offset": {"type": "integer", "default": 0},
                },
                "required": ["tenant_id", "world_id"],
            },
        ),
        Tool(
            name="search_locations",
            description="Search locations by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "search_term": {"type": "string", "description": "Term to search for in location names"},
                    "limit": {"type": "integer", "default": 20},
                },
                "required": ["tenant_id", "search_term"],
            },
        ),
        Tool(
            name="find_locations_by_type",
            description="Find locations by type in a world",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "location_type": {"type": "string", "description": "Type of location to find"},
                    "limit": {"type": "integer", "default": 50},
                },
                "required": ["tenant_id", "world_id", "location_type"],
            },
        ),
        Tool(
            name="update_location",
            description="Update location details",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "location_id": {"type": "string"},
                    "name": {"type": "string", "description": "New location name"},
                    "description": {"type": "string", "description": "New location description"},
                    "location_type": {"type": "string", "enum": ["building", "house", "barn", "temple", "castle", "dungeon", "cave", "forest", "mountain", "city", "village", "shop", "tavern", "ruins", "landmark", "other"]},
                },
                "required": ["tenant_id", "location_id"],
            },
        ),
        Tool(
            name="delete_location",
            description="Delete a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "location_id": {"type": "string"},
                },
                "required": ["tenant_id", "location_id"],
            },
        ),

        # Environment operations
        Tool(
            name="create_environment",
            description="Create a new environment for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "location_id": {"type": "string"},
                    "name": {"type": "string", "description": "Environment preset name (e.g., 'Stormy Night')"},
                    "description": {"type": "string", "description": "Detailed environment description"},
                    "time_of_day": {"type": "string", "enum": ["day", "night", "dawn", "dusk"], "description": "Time of day"},
                    "weather": {"type": "string", "enum": ["clear", "rainy", "stormy", "foggy"], "description": "Weather conditions"},
                    "lighting": {"type": "string", "enum": ["bright", "dim", "dark", "magical"], "description": "Lighting conditions"},
                    "temperature": {"type": "string", "description": "Temperature description (optional)"},
                    "sounds": {"type": "string", "description": "Ambient sounds (optional)"},
                    "smells": {"type": "string", "description": "Ambient smells (optional)"},
                    "is_active": {"type": "boolean", "description": "Whether this environment is currently active", "default": True},
                },
                "required": ["tenant_id", "world_id", "location_id", "name", "time_of_day", "weather", "lighting"],
            },
        ),
        Tool(
            name="get_environment",
            description="Get an environment by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "environment_id": {"type": "string"},
                },
                "required": ["tenant_id", "environment_id"],
            },
        ),
        Tool(
            name="list_environments",
            description="List environments in a world",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 50},
                    "offset": {"type": "integer", "default": 0},
                },
                "required": ["tenant_id", "world_id"],
            },
        ),
        Tool(
            name="list_environments_by_location",
            description="List all environments for a specific location",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "location_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 20},
                    "offset": {"type": "integer", "default": 0},
                },
                "required": ["tenant_id", "location_id"],
            },
        ),
        Tool(
            name="search_environments",
            description="Search environments by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "search_term": {"type": "string", "description": "Term to search for in environment names"},
                    "limit": {"type": "integer", "default": 20},
                },
                "required": ["tenant_id", "search_term"],
            },
        ),
        Tool(
            name="find_environments_by_conditions",
            description="Find environments by atmospheric conditions",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "world_id": {"type": "string"},
                    "time_of_day": {"type": "string", "enum": ["day", "night", "dawn", "dusk"], "description": "Filter by time of day"},
                    "weather": {"type": "string", "enum": ["clear", "rainy", "stormy", "foggy"], "description": "Filter by weather"},
                    "lighting": {"type": "string", "enum": ["bright", "dim", "dark", "magical"], "description": "Filter by lighting"},
                    "limit": {"type": "integer", "default": 50},
                },
                "required": ["tenant_id", "world_id"],
            },
        ),
        Tool(
            name="get_active_environment",
            description="Get the currently active environment for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "location_id": {"type": "string"},
                },
                "required": ["tenant_id", "location_id"],
            },
        ),
        Tool(
            name="update_environment",
            description="Update environment details",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "environment_id": {"type": "string"},
                    "name": {"type": "string", "description": "New environment name"},
                    "description": {"type": "string", "description": "New environment description"},
                    "time_of_day": {"type": "string", "enum": ["day", "night", "dawn", "dusk"]},
                    "weather": {"type": "string", "enum": ["clear", "rainy", "stormy", "foggy"]},
                    "lighting": {"type": "string", "enum": ["bright", "dim", "dark", "magical"]},
                    "temperature": {"type": "string", "description": "New temperature description"},
                    "sounds": {"type": "string", "description": "New ambient sounds"},
                    "smells": {"type": "string", "description": "New ambient smells"},
                    "is_active": {"type": "boolean", "description": "Whether this environment should be active"},
                },
                "required": ["tenant_id", "environment_id"],
            },
        ),
        Tool(
            name="delete_environment",
            description="Delete an environment",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "environment_id": {"type": "string"},
                },
                "required": ["tenant_id", "environment_id"],
            },
        ),

        # Persistence operations
        Tool(
            name="save_to_json",
            description="Save all lore data to JSON files for a tenant. Creates individual JSON files for each entity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string", "description": "Tenant ID to save data for"},
                },
                "required": ["tenant_id"],
            },
        ),
        Tool(
            name="export_tenant",
            description="Export all tenant data to a single JSON file",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string", "description": "Tenant ID to export"},
                    "filename": {"type": "string", "description": "Output filename (e.g., 'my_world.json')"},
                },
                "required": ["tenant_id", "filename"],
            },
        ),
        Tool(
            name="list_saved_files",
            description="List all saved JSON files, optionally filtered by tenant",
            inputSchema={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string", "description": "Optional tenant ID to filter by"},
                },
            },
        ),
        Tool(
            name="get_storage_stats",
            description="Get statistics about stored JSON data",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""

    try:
        # World operations
        if name == "create_world":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_name = WorldName(arguments["name"])
            description = Description(arguments["description"])
            parent_id = parse_entity_id(arguments["parent_id"]) if arguments.get("parent_id") else None

            world = World.create(tenant_id, world_name, description, parent_id)
            world_repo.save(world)
            persistence.save_world(world, str(arguments["tenant_id"]))

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "world": serialize_entity(world),
                    "message": f"World '{world_name}' created successfully"
                }, indent=2)
            )]

        elif name == "get_world":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])

            world = world_repo.find_by_id(tenant_id, world_id)
            if not world:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "World not found"}))]

            return [TextContent(
                type="text",
                text=json.dumps({"success": True, "world": serialize_entity(world)}, indent=2)
            )]

        elif name == "list_worlds":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            limit = arguments.get("limit", 100)
            offset = arguments.get("offset", 0)

            worlds = world_repo.list_by_tenant(tenant_id, limit, offset)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(worlds),
                    "worlds": [serialize_entity(w) for w in worlds]
                }, indent=2)
            )]

        elif name == "update_world":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])

            world = world_repo.find_by_id(tenant_id, world_id)
            if not world:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "World not found"}))]

            if "name" in arguments:
                world.rename(WorldName(arguments["name"]))

            if "description" in arguments:
                world.update_description(Description(arguments["description"]))

            world_repo.save(world)
            persistence.save_world(world, str(arguments["tenant_id"]))

            return [TextContent(
                type="text",
                text=json.dumps({"success": True, "world": serialize_entity(world)}, indent=2)
            )]

        elif name == "delete_world":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])

            world_repo.delete(tenant_id, world_id)

            return [TextContent(
                type="text",
                text=json.dumps({"success": True, "message": "World deleted"})
            )]

        # Character operations
        elif name == "create_character":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])
            name = CharacterName(arguments["name"])
            backstory = Backstory(arguments["backstory"])

            # Optional fields
            rarity = Rarity[arguments["rarity"]] if arguments.get("rarity") else None
            element = CharacterElement[arguments["element"].upper()] if arguments.get("element") else None
            role = CharacterRole[arguments["role"].upper()] if arguments.get("role") else None

            character = Character.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=name,
                backstory=backstory,
                rarity=rarity,
                element=element,
                role=role,
                base_hp=arguments.get("base_hp"),
                base_atk=arguments.get("base_atk"),
                base_def=arguments.get("base_def"),
                base_speed=arguments.get("base_speed"),
                energy_cost=arguments.get("energy_cost"),
            )

            character_repo.save(character)
            persistence.save_character(character, str(arguments["tenant_id"]))

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "character": serialize_entity(character),
                    "message": f"Character '{name}' created successfully"
                }, indent=2)
            )]

        elif name == "get_character":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            character_id = parse_entity_id(arguments["character_id"])

            character = character_repo.find_by_id(tenant_id, character_id)
            if not character:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Character not found"}))]

            return [TextContent(
                type="text",
                text=json.dumps({"success": True, "character": serialize_entity(character)}, indent=2)
            )]

        elif name == "list_characters":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])
            limit = arguments.get("limit", 100)
            offset = arguments.get("offset", 0)

            characters = character_repo.list_by_world(tenant_id, world_id, limit, offset)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(characters),
                    "characters": [serialize_entity(c) for c in characters]
                }, indent=2)
            )]

        elif name == "update_character":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            character_id = parse_entity_id(arguments["character_id"])

            character = character_repo.find_by_id(tenant_id, character_id)
            if not character:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Character not found"}))]

            if "backstory" in arguments:
                character.update_backstory(Backstory(arguments["backstory"]))

            if "status" in arguments:
                if arguments["status"] == "active":
                    character.activate()
                else:
                    character.deactivate()

            character_repo.save(character)

            return [TextContent(
                type="text",
                text=json.dumps({"success": True, "character": serialize_entity(character)}, indent=2)
            )]

        elif name == "delete_character":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            character_id = parse_entity_id(arguments["character_id"])

            character_repo.delete(tenant_id, character_id)

            return [TextContent(
                type="text",
                text=json.dumps({"success": True, "message": "Character deleted"})
            )]

        elif name == "add_ability":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            character_id = parse_entity_id(arguments["character_id"])

            character = character_repo.find_by_id(tenant_id, character_id)
            if not character:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Character not found"}))]

            ability = Ability(
                name=AbilityName(arguments["ability_name"]),
                description=Description(arguments["description"]),
                power_level=PowerLevel(arguments["power_level"]),
            )

            character.add_ability(ability)
            character_repo.save(character)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "character": serialize_entity(character),
                    "message": f"Ability '{arguments['ability_name']}' added"
                }, indent=2)
            )]

        # Story operations
        elif name == "create_story":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])

            story = Story.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=StoryName(arguments["name"]),
                description=arguments["description"],
                story_type=StoryType[arguments.get("story_type", "LINEAR")],
                content=Content(arguments.get("content", "") or "Story content to be added."),
            )

            story_repo.save(story)
            persistence.save_story(story, str(arguments["tenant_id"]))

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "story": serialize_entity(story),
                    "message": "Story created successfully"
                }, indent=2)
            )]

        elif name == "get_story":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            story_id = parse_entity_id(arguments["story_id"])

            story = story_repo.find_by_id(tenant_id, story_id)
            if not story:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Story not found"}))]

            return [TextContent(
                type="text",
                text=json.dumps({"success": True, "story": serialize_entity(story)}, indent=2)
            )]

        elif name == "list_stories":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])
            limit = arguments.get("limit", 100)
            offset = arguments.get("offset", 0)

            stories = story_repo.list_by_world(tenant_id, world_id, limit, offset)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(stories),
                    "stories": [serialize_entity(s) for s in stories]
                }, indent=2)
            )]

        # Event operations
        elif name == "create_event":
            from datetime import datetime
            from dataclasses import dataclass

            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])

            start_datetime = datetime.fromisoformat(arguments["start_date"])
            start_timestamp = Timestamp(start_datetime)

            end_timestamp = None
            if arguments.get("end_date"):
                end_datetime = datetime.fromisoformat(arguments["end_date"])
                end_timestamp = Timestamp(end_datetime)

            # Parse participant IDs
            participant_ids = [parse_entity_id(pid) for pid in arguments.get("participant_ids", [])]

            event = Event.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=arguments["name"],
                description=Description(arguments["description"]),
                start_date=start_timestamp,
                end_date=end_timestamp,
                participant_ids=participant_ids,
                outcome=EventOutcome[arguments.get("outcome", "ongoing").upper()],
            )

            event_repo.save(event)
            persistence.save_event(event, str(arguments["tenant_id"]))

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "event": serialize_entity(event),
                    "message": "Event created successfully"
                }, indent=2)
            )]

        elif name == "list_events":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])
            limit = arguments.get("limit", 100)
            offset = arguments.get("offset", 0)

            events = event_repo.list_by_world(tenant_id, world_id, limit, offset)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(events),
                    "events": [serialize_entity(e) for e in events]
                }, indent=2)
            )]

        # Page operations
        elif name == "create_page":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])

            page = Page.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=PageName(arguments["name"]),
                content=Content(arguments["content"]),
            )

            page_repo.save(page)
            persistence.save_page(page, str(arguments["tenant_id"]))

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "page": serialize_entity(page),
                    "message": "Page created successfully"
                }, indent=2)
            )]

        elif name == "list_pages":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])
            limit = arguments.get("limit", 100)
            offset = arguments.get("offset", 0)

            pages = page_repo.list_by_world(tenant_id, world_id, limit, offset)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(pages),
                    "pages": [serialize_entity(p) for p in pages]
                }, indent=2)
            )]

        # Item operations
        elif name == "create_item":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])

            item = Item.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=arguments["name"],
                description=Description(arguments["description"]),
                item_type=ItemType[arguments["item_type"].upper()],
                rarity=Rarity[arguments["rarity"].upper()] if arguments.get("rarity") else None,
                location_id=parse_entity_id(arguments["location_id"]) if arguments.get("location_id") else None,
                level=arguments.get("level"),
                enhancement=arguments.get("enhancement"),
                max_enhancement=arguments.get("max_enhancement"),
                base_atk=arguments.get("base_atk"),
                base_hp=arguments.get("base_hp"),
                base_def=arguments.get("base_def"),
                special_stat=arguments.get("special_stat"),
                special_stat_value=arguments.get("special_stat_value"),
            )

            item_repo.save(item)
            persistence.save_item(item, str(arguments["tenant_id"]))

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "item": serialize_entity(item),
                    "message": "Item created successfully"
                }, indent=2)
            )]

        elif name == "get_item":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            item_id = parse_entity_id(arguments["item_id"])

            item = item_repo.find_by_id(tenant_id, item_id)
            if not item:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Item not found"}))]

            return [TextContent(
                type="text",
                text=json.dumps({"success": True, "item": serialize_entity(item)}, indent=2)
            )]

        elif name == "list_items":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])
            limit = arguments.get("limit", 50)
            offset = arguments.get("offset", 0)

            items = item_repo.list_by_world(tenant_id, world_id, limit, offset)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(items),
                    "items": [serialize_entity(i) for i in items]
                }, indent=2)
            )]

        elif name == "search_items":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            search_term = arguments["search_term"]
            limit = arguments.get("limit", 20)

            items = item_repo.search_by_name(tenant_id, search_term, limit)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(items),
                    "search_term": search_term,
                    "items": [serialize_entity(i) for i in items]
                }, indent=2)
            )]

        elif name == "update_item":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            item_id = parse_entity_id(arguments["item_id"])

            item = item_repo.find_by_id(tenant_id, item_id)
            if not item:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Item not found"}))]

            # Update fields
            if "name" in arguments:
                item.rename(arguments["name"])
            if "description" in arguments:
                item.update_description(Description(arguments["description"]))
            if "rarity" in arguments:
                item.set_rarity(Rarity[arguments["rarity"].upper()] if arguments["rarity"] else None)
            if "location_id" in arguments:
                item.move_to_location(parse_entity_id(arguments["location_id"]) if arguments["location_id"] else None)
            if "level" in arguments:
                item.set_level(arguments["level"])

            item_repo.save(item)
            persistence.save_item(item, str(arguments["tenant_id"]))

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "item": serialize_entity(item),
                    "message": "Item updated successfully"
                }, indent=2)
            )]

        elif name == "enhance_item":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            item_id = parse_entity_id(arguments["item_id"])

            item = item_repo.find_by_id(tenant_id, item_id)
            if not item:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Item not found"}))]

            try:
                item.enhance()
                item_repo.save(item)
                persistence.save_item(item, str(arguments["tenant_id"]))

                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "item": serialize_entity(item),
                        "message": "Item enhanced successfully"
                    }, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e)
                    }, indent=2)
                )]

        elif name == "delete_item":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            item_id = parse_entity_id(arguments["item_id"])

            item = item_repo.find_by_id(tenant_id, item_id)
            if not item:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Item not found"}))]

            deleted = item_repo.delete(tenant_id, item_id)
            if deleted:
                persistence.delete_item(str(arguments["tenant_id"]), str(item_id))

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": deleted,
                    "message": "Item deleted successfully" if deleted else "Item not found"
                }, indent=2)
            )]

        # Texture operations
        elif name == "create_texture":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])

            texture = Texture.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=arguments["name"],
                path=arguments["path"],
                texture_type=arguments["texture_type"],
                file_size=arguments["file_size"],
                dimensions=arguments.get("dimensions"),
                color_space=arguments.get("color_space", "sRGB"),
                description=arguments.get("description"),
            )

            texture_repo.save(texture)
            persistence.save_texture(texture, str(arguments["tenant_id"]))

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "texture": serialize_entity(texture),
                    "message": "Texture created successfully"
                }, indent=2)
            )]

        elif name == "get_texture":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            texture_id = parse_entity_id(arguments["texture_id"])

            texture = texture_repo.get_by_id(tenant_id, texture_id)
            if not texture:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Texture not found"}))]

            return [TextContent(
                type="text",
                text=json.dumps({"success": True, "texture": serialize_entity(texture)}, indent=2)
            )]

        elif name == "list_textures":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            limit = arguments.get("limit", 100)
            offset = arguments.get("offset", 0)

            textures = texture_repo.list_by_world(tenant_id, limit, offset)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(textures),
                    "textures": [serialize_entity(t) for t in textures]
                }, indent=2)
            )]

        # 3D Model operations
        elif name == "create_3d_model":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])

            model = Model3D.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=arguments["name"],
                path=arguments["path"],
                model_type=arguments["model_type"],
                file_size=arguments["file_size"],
                poly_count=arguments.get("poly_count"),
                dimensions=arguments.get("dimensions"),
                textures=[parse_entity_id(tid) for tid in arguments.get("textures", [])],
                animations=arguments.get("animations", []),
                description=arguments.get("description"),
            )

            model3d_repo.save(model)
            persistence.save_3d_model(model, str(arguments["tenant_id"]))

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "model": serialize_entity(model),
                    "message": "3D Model created successfully"
                }, indent=2)
            )]

        elif name == "get_3d_model":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            model_id = parse_entity_id(arguments["model_id"])

            model = model3d_repo.get_by_id(tenant_id, model_id)
            if not model:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "3D Model not found"}))]

            return [TextContent(
                type="text",
                text=json.dumps({"success": True, "model": serialize_entity(model)}, indent=2)
            )]

        elif name == "list_3d_models":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            limit = arguments.get("limit", 100)
            offset = arguments.get("offset", 0)

            models = model3d_repo.list_by_world(tenant_id, limit, offset)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(models),
                    "models": [serialize_entity(m) for m in models]
                }, indent=2)
            )]

        # Location operations
        elif name == "create_location":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])

            location = Location.create(
                tenant_id=tenant_id,
                world_id=world_id,
                name=arguments["name"],
                description=Description(arguments["description"]),
                location_type=LocationType[arguments["location_type"].upper()],
                parent_location_id=parse_entity_id(arguments["parent_location_id"]) if arguments.get("parent_location_id") else None,
            )

            location_repo.save(location)
            persistence.save_location(location, str(arguments["tenant_id"]))

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "location": serialize_entity(location),
                    "message": "Location created successfully"
                }, indent=2)
            )]

        elif name == "get_location":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            location_id = parse_entity_id(arguments["location_id"])

            location = location_repo.find_by_id(tenant_id, location_id)
            if not location:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Location not found"}))]

            return [TextContent(
                type="text",
                text=json.dumps({"success": True, "location": serialize_entity(location)}, indent=2)
            )]

        elif name == "list_locations":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])
            limit = arguments.get("limit", 50)
            offset = arguments.get("offset", 0)

            locations = location_repo.list_by_world(tenant_id, world_id, limit, offset)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(locations),
                    "locations": [serialize_entity(l) for l in locations]
                }, indent=2)
            )]

        elif name == "search_locations":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            search_term = arguments["search_term"]
            limit = arguments.get("limit", 20)

            locations = location_repo.search_by_name(tenant_id, search_term, limit)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(locations),
                    "search_term": search_term,
                    "locations": [serialize_entity(l) for l in locations]
                }, indent=2)
            )]

        elif name == "find_locations_by_type":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])
            location_type = arguments["location_type"]
            limit = arguments.get("limit", 50)

            locations = location_repo.find_by_type(tenant_id, world_id, location_type, limit)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(locations),
                    "location_type": location_type,
                    "locations": [serialize_entity(l) for l in locations]
                }, indent=2)
            )]

        elif name == "update_location":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            location_id = parse_entity_id(arguments["location_id"])

            location = location_repo.find_by_id(tenant_id, location_id)
            if not location:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Location not found"}))]

            # Update fields
            if "name" in arguments:
                location.rename(arguments["name"])
            if "description" in arguments:
                location.update_description(Description(arguments["description"]))
            if "location_type" in arguments:
                # Note: changing type would require updating indexes, for now just update the field
                object.__setattr__(location, 'location_type', LocationType[arguments["location_type"].upper()])
                object.__setattr__(location, 'updated_at', Timestamp.now())
                object.__setattr__(location, 'version', location.version.increment())

            location_repo.save(location)
            persistence.save_location(location, str(arguments["tenant_id"]))

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "location": serialize_entity(location),
                    "message": "Location updated successfully"
                }, indent=2)
            )]

        elif name == "delete_location":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            location_id = parse_entity_id(arguments["location_id"])

            location = location_repo.find_by_id(tenant_id, location_id)
            if not location:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Location not found"}))]

            deleted = location_repo.delete(tenant_id, location_id)
            if deleted:
                persistence.delete_location(str(arguments["tenant_id"]), str(location_id))

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": deleted,
                    "message": "Location deleted successfully" if deleted else "Location not found"
                }, indent=2)
            )]

        # Environment operations
        elif name == "create_environment":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])
            location_id = parse_entity_id(arguments["location_id"])
            name = arguments["name"]
            time_of_day = TimeOfDay(arguments["time_of_day"])
            weather = Weather(arguments["weather"])
            lighting = Lighting(arguments["lighting"])
            description = arguments.get("description")
            temperature = arguments.get("temperature")
            sounds = arguments.get("sounds")
            smells = arguments.get("smells")
            is_active = arguments.get("is_active", True)

            # Check if world exists
            world = world_repo.find_by_id(tenant_id, world_id)
            if not world:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "World not found"}))]

            # Check if location exists
            location = location_repo.find_by_id(tenant_id, location_id)
            if not location:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Location not found"}))]

            # Check for duplicate name for this location
            if environment_repo.exists(tenant_id, location_id, name):
                return [TextContent(type="text", text=json.dumps({"success": False, "error": f"Environment with name '{name}' already exists for this location"}))]

            environment = Environment.create(
                tenant_id=tenant_id,
                world_id=world_id,
                location_id=location_id,
                name=name,
                time_of_day=time_of_day,
                weather=weather,
                lighting=lighting,
                description=Description(description) if description else None,
                temperature=temperature,
                sounds=sounds,
                smells=smells,
                is_active=is_active,
            )

            saved_environment = environment_repo.save(environment)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "environment": serialize_entity(saved_environment),
                    "message": "Environment created successfully"
                }, indent=2)
            )]

        elif name == "get_environment":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            environment_id = parse_entity_id(arguments["environment_id"])

            environment = environment_repo.find_by_id(tenant_id, environment_id)
            if not environment:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Environment not found"}))]

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "environment": serialize_entity(environment)
                }, indent=2)
            )]

        elif name == "list_environments":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])
            limit = arguments.get("limit", 50)
            offset = arguments.get("offset", 0)

            environments = environment_repo.list_by_world(tenant_id, world_id, limit, offset)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(environments),
                    "environments": [serialize_entity(e) for e in environments]
                }, indent=2)
            )]

        elif name == "list_environments_by_location":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            location_id = parse_entity_id(arguments["location_id"])
            limit = arguments.get("limit", 20)
            offset = arguments.get("offset", 0)

            environments = environment_repo.list_by_location(tenant_id, location_id, limit, offset)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(environments),
                    "environments": [serialize_entity(e) for e in environments]
                }, indent=2)
            )]

        elif name == "search_environments":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            search_term = arguments["search_term"]
            limit = arguments.get("limit", 20)

            environments = environment_repo.search_by_name(tenant_id, search_term, limit)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(environments),
                    "environments": [serialize_entity(e) for e in environments]
                }, indent=2)
            )]

        elif name == "find_environments_by_conditions":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            world_id = parse_entity_id(arguments["world_id"])
            time_of_day = TimeOfDay(arguments["time_of_day"]) if arguments.get("time_of_day") else None
            weather = Weather(arguments["weather"]) if arguments.get("weather") else None
            lighting = Lighting(arguments["lighting"]) if arguments.get("lighting") else None
            limit = arguments.get("limit", 50)

            environments = environment_repo.find_by_conditions(
                tenant_id, world_id, time_of_day, weather, lighting, limit
            )

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "count": len(environments),
                    "environments": [serialize_entity(e) for e in environments]
                }, indent=2)
            )]

        elif name == "get_active_environment":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            location_id = parse_entity_id(arguments["location_id"])

            environment = environment_repo.find_active_by_location(tenant_id, location_id)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "environment": serialize_entity(environment) if environment else None
                }, indent=2)
            )]

        elif name == "update_environment":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            environment_id = parse_entity_id(arguments["environment_id"])

            environment = environment_repo.find_by_id(tenant_id, environment_id)
            if not environment:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Environment not found"}))]

            # Update fields if provided
            if "name" in arguments:
                environment.rename(arguments["name"])
            if "description" in arguments:
                environment.update_description(
                    Description(arguments["description"]) if arguments["description"] else None
                )
            if any(k in arguments for k in ["time_of_day", "weather", "lighting", "temperature", "sounds", "smells"]):
                environment.change_conditions(
                    time_of_day=TimeOfDay(arguments["time_of_day"]) if arguments.get("time_of_day") else None,
                    weather=Weather(arguments["weather"]) if arguments.get("weather") else None,
                    lighting=Lighting(arguments["lighting"]) if arguments.get("lighting") else None,
                    temperature=arguments.get("temperature"),
                    sounds=arguments.get("sounds"),
                    smells=arguments.get("smells"),
                )
            if "is_active" in arguments:
                if arguments["is_active"]:
                    environment.activate()
                else:
                    environment.deactivate()

            saved_environment = environment_repo.save(environment)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "environment": serialize_entity(saved_environment),
                    "message": "Environment updated successfully"
                }, indent=2)
            )]

        elif name == "delete_environment":
            tenant_id = parse_tenant_id(arguments["tenant_id"])
            environment_id = parse_entity_id(arguments["environment_id"])

            environment = environment_repo.find_by_id(tenant_id, environment_id)
            if not environment:
                return [TextContent(type="text", text=json.dumps({"success": False, "error": "Environment not found"}))]

            deleted = environment_repo.delete(tenant_id, environment_id)
            if deleted:
                persistence.delete_environment(str(arguments["tenant_id"]), str(environment_id))

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": deleted,
                    "message": "Environment deleted successfully" if deleted else "Environment not found"
                }, indent=2)
            )]

        # Persistence operations
        elif name == "save_to_json":
            tenant_id = arguments["tenant_id"]

            counts = persistence.save_all(
                world_repo,
                character_repo,
                story_repo,
                event_repo,
                page_repo,
                item_repo,
                location_repo,
                environment_repo,
                texture_repo,
                model3d_repo,
                tenant_id
            )

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "message": "Data saved to JSON files",
                    "tenant_id": tenant_id,
                    "counts": {
                        "worlds": counts["worlds"],
                        "characters": counts["characters"],
                        "stories": counts["stories"],
                        "events": counts["events"],
                        "pages": counts["pages"],
                        "items": counts["items"],
                        "locations": counts["locations"],
                        "environments": counts["environments"],
                        "total_files": len(counts["files"])
                    },
                    "data_directory": str(persistence.data_dir.absolute()),
                    "sample_files": counts["files"][:5] if counts["files"] else []
                }, indent=2)
            )]

        elif name == "export_tenant":
            tenant_id = arguments["tenant_id"]
            filename = arguments["filename"]

            # Ensure filename ends with .json
            if not filename.endswith('.json'):
                filename += '.json'

            filepath = persistence.export_tenant(tenant_id, filename)

            # Get file size
            file_size = Path(filepath).stat().st_size

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "message": f"Tenant data exported successfully",
                    "tenant_id": tenant_id,
                    "filepath": filepath,
                    "size_bytes": file_size,
                    "size_kb": round(file_size / 1024, 2)
                }, indent=2)
            )]

        elif name == "list_saved_files":
            tenant_id = arguments.get("tenant_id")

            files = persistence.list_saved_files(tenant_id)

            total_count = sum(len(file_list) for file_list in files.values())

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "tenant_id": tenant_id if tenant_id else "all",
                    "total_files": total_count,
                    "files": files,
                    "data_directory": str(persistence.data_dir.absolute())
                }, indent=2)
            )]

        elif name == "get_storage_stats":
            stats = persistence.get_storage_stats()

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "statistics": stats
                }, indent=2)
            )]

        else:
            return [TextContent(
                type="text",
                text=json.dumps({"success": False, "error": f"Unknown tool: {name}"})
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e),
                "type": type(e).__name__
            }, indent=2)
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
