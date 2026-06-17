#!/usr/bin/env python3
"""
MCP Server Tool Schemas Registration
"""

from mcp.types import Tool

def get_tools() -> list[Tool]:
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
