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
)
from src.domain.value_objects.ability import Ability, AbilityName, PowerLevel

# Import in-memory repositories for demo
from src.infrastructure.in_memory_repositories import (
    InMemoryWorldRepository,
    InMemoryCharacterRepository,
    InMemoryStoryRepository,
    InMemoryEventRepository,
    InMemoryPageRepository,
)

# Import persistence layer
from mcp_server.persistence import JSONPersistence

# Initialize repositories (in production, use PostgreSQL repositories)
world_repo = InMemoryWorldRepository()
character_repo = InMemoryCharacterRepository()
story_repo = InMemoryStoryRepository()
event_repo = InMemoryEventRepository()
page_repo = InMemoryPageRepository()

# Initialize JSON persistence
persistence = JSONPersistence()

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
            result[field_name] = field_value.value
        elif isinstance(field_value, (str, int, float, bool)):
            result[field_name] = field_value
        elif isinstance(field_value, datetime):
            result[field_name] = field_value.isoformat()
        elif isinstance(field_value, list):
            result[field_name] = [
                serialize_entity(item) if hasattr(item, '__dict__')
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

        # Persistence operations
        elif name == "save_to_json":
            tenant_id = arguments["tenant_id"]

            counts = persistence.save_all(
                world_repo,
                character_repo,
                story_repo,
                event_repo,
                page_repo,
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
