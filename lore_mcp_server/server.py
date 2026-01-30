"""
MCP Server for loreSystem

This MCP server provides model context protocol (MCP) functionality
for AAA game development studios using loreSystem domain model.
"""

import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager

# Try to import MCP SDK if available
try:
    from mcp.server import Server, StdioServer
    from mcp.types import Tool, Resource
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    # Create stubs if MCP SDK not available
    class Server:
        def __init__(self, *args, **kwargs):
            pass
        async def serve(self, *args, **kwargs):
            pass
    
    class StdioServer:
        def __init__(self, *args, **kwargs):
            pass
    
    class Tool:
        def __init__(self, *args, **kwargs):
            pass
    
    class Resource:
        def __init__(self, *args, **kwargs):
            pass

# Domain entities (in production, these would be imported from src.domain)
# For this MCP server, we'll define stubs that return JSON data
class Campaign:
    """Campaign stub for MCP server."""
    def __init__(self, id, name, description, campaign_type, difficulty):
        self.id = id
        self.name = name
        self.description = description
        self.campaign_type = campaign_type
        self.difficulty = difficulty

class Quest:
    """Quest stub for MCP server."""
    def __init__(self, id, name, description, quest_type, difficulty):
        self.id = id
        self.name = name
        self.description = description
        self.quest_type = quest_type
        self.difficulty = difficulty

class Faction:
    """Faction stub for MCP server."""
    def __init__(self, id, name, alignment, member_count):
        self.id = id
        self.name = name
        self.alignment = alignment
        self.member_count = member_count

class Location:
    """Location stub for MCP server."""
    def __init__(self, id, name, location_type, is_faction_hq):
        self.id = id
        self.name = name
        self.location_type = location_type
        self.is_faction_hq = is_faction_hq

class Item:
    """Item stub for MCP server."""
    def __init__(self, id, name, item_type, rarity):
        self.id = id
        self.name = name
        self.item_type = item_type
        self.rarity = rarity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MCP Server")

class LoreSystemMCPServer:
    """
    MCP Server for loreSystem domain model.
    
    Provides model context protocol for AAA game dev studios
    with full access to campaigns, quests, factions, items, locations, etc.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000, tenant_id: str = "default"):
        self.host = host
        self.port = port
        self.tenant_id = tenant_id
        
        # Stub repositories (in production, these would be real repository classes)
        self.campaigns = {}
        self.quests = {}
        self.factions = {}
        self.locations = {}
        self.items = {}
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample AAA game data."""
        # Sample campaigns
        self.campaigns["campaign_001"] = Campaign(
            id="campaign_001",
            name="War of Three Kingdoms",
            description="Epic RPG campaign with branching narrative",
            campaign_type="main_story",
            difficulty="medium"
        )
        
        self.campaigns["campaign_002"] = Campaign(
            id="campaign_002",
            name="Ancient Artifact Recovery",
            description="Quest chain for legendary items",
            campaign_type="side_story",
            difficulty="hard"
        )
        
        # Sample quests
        self.quests["quest_001"] = Quest(
            id="quest_001",
            name="Find the Ancient Artifact",
            description="Retrieve legendary artifact from Ruins",
            quest_type="main",
            difficulty="hard"
        )
        
        self.quests["quest_002"] = Quest(
            id="quest_002",
            name="Defend the Ruins",
            description="Protect artifact from bandits",
            quest_type="side",
            difficulty="medium"
        )
        
        # Sample factions
        self.factions["faction_001"] = Faction(
            id="faction_001",
            name="Order of Silver Hand",
            alignment="lawful_good",
            member_count=10000
        )
        
        self.factions["faction_002"] = Faction(
            id="faction_002",
            name="Chaos of Broken Chain",
            alignment="chaotic_neutral",
            member_count=5000
        )
        
        # Sample locations
        self.locations["location_001"] = Location(
            id="location_001",
            name="Capital City",
            location_type="city",
            is_faction_hq=True
        )
        
        self.locations["location_002"] = Location(
            id="location_002",
            name="Ruins of the Kingdom",
            location_type="dungeon",
            is_faction_hq=False
        )
        
        # Sample items
        self.items["item_001"] = Item(
            id="item_001",
            name="Ancient Scarab Amulet",
            item_type="artifact",
            rarity="legendary"
        )
        
        self.items["item_002"] = Item(
            id="item_002",
            name="Enchanted Steel Sword",
            item_type="weapon",
            rarity="epic"
        )
        
        logger.info(f"Initialized sample data for tenant {self.tenant_id}")
        logger.info(f"Campaigns: {len(self.campaigns)}, Quests: {len(self.quests)}, Factions: {len(self.factions)}, Locations: {len(self.locations)}, Items: {len(self.items)}")
    
    def create_tools(self) -> List[Tool]:
        """Create MCP tools for domain entities."""
        tools = []
        
        # Campaign tools
        tools.append(Tool(
            name="list_campaigns",
            description="List all campaigns",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ))
        
        tools.append(Tool(
            name="get_campaign",
            description="Get campaign by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string"}
                },
                "required": ["id"]
            }
        ))
        
        tools.append(Tool(
            name="create_campaign",
            description="Create new campaign",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "campaign_type": {"type": "string"},
                    "difficulty": {"type": "string"}
                },
                "required": ["name", "description"]
            }
        ))
        
        # Quest tools
        tools.append(Tool(
            name="list_quests",
            description="List all quests",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ))
        
        tools.append(Tool(
            name="get_quest",
            description="Get quest by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string"}
                },
                "required": ["id"]
            }
        ))
        
        # Faction tools
        tools.append(Tool(
            name="list_factions",
            description="List all factions",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ))
        
        # Location tools
        tools.append(Tool(
            name="list_locations",
            description="List all locations",
            inputSchema={
                "type": "object",
                "properties": {
                    "location_type": {"type": "string", "enum": ["city", "town", "dungeon", "boss_area"]}
                },
                "required": []
            }
        ))
        
        # Item tools
        tools.append(Tool(
            name="list_items",
            description="List all items",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_type": {"type": "string", "enum": ["weapon", "armor", "artifact", "consumable"]},
                    "rarity": {"type": "string", "enum": ["common", "uncommon", "rare", "epic", "legendary"]}
                },
                "required": []
            }
        ))
        
        # Validation tools
        tools.append(Tool(
            name="validate_campaign",
            description="Validate campaign for export",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"}
                },
                "required": ["campaign_id"]
            }
        ))
        
        tools.append(Tool(
            name="export_campaign_to_unreal",
            description="Export campaign to Unreal Engine JSON",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "format": {"type": "string", "enum": ["json", "xml"]}
                },
                "required": ["campaign_id"]
            }
        ))
        
        # Analytics tools
        tools.append(Tool(
            name="get_campaign_statistics",
            description="Get campaign completion statistics",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"}
                },
                "required": ["campaign_id"]
            }
        ))
        
        tools.append(Tool(
            name="get_player_analytics",
            description="Get player behavior metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "player_id": {"type": "string"},
                    "metrics": {"type": "array", "items": {"type": "string", "enum": ["playtime", "death_count", "completion_rate"]}}
                },
                "required": ["player_id"]
            }
        ))
        
        # Economy tools
        tools.append(Tool(
            name="get_economy_balance",
            description="Get economy balance data",
            inputSchema={
                "type": "object",
                "properties": {
                    "currency": {"type": "string", "enum": ["gold", "silver", "crystal"]},
                    "time_period": {"type": "string", "enum": ["day", "week", "month"]}
                },
                "required": ["currency"]
            }
        ))
        
        logger.info(f"Created {len(tools)} MCP tools")
        return tools
    
    def create_resources(self) -> List[Resource]:
        """Create MCP resources for domain entities."""
        resources = []
        
        # Campaign resources
        resources.append(Resource(
            uri="campaign://list",
            name="All Campaigns",
            description="Access all campaigns in the tenant's world"
        ))
        
        resources.append(Resource(
            uri="campaign://{campaign_id}",
            name="Campaign Details",
            description="Get detailed information about a specific campaign"
        ))
        
        # Quest resources
        resources.append(Resource(
            uri="quest://list",
            name="All Quests",
            description="Access all quests in the tenant's campaigns"
        ))
        
        resources.append(Resource(
            uri="quest://{quest_id}",
            name="Quest Details",
            description="Get detailed information about a specific quest"
        ))
        
        # Faction resources
        resources.append(Resource(
            uri="faction://list",
            name="All Factions",
            description="Access all factions and their relations"
        ))
        
        # Location resources
        resources.append(Resource(
            uri="location://list",
            name="All Locations",
            description="Access all locations in the tenant's world"
        ))
        
        # Item resources
        resources.append(Resource(
            uri="item://list",
            name="All Items",
            description="Access all items in the tenant's inventory"
        ))
        
        # Validation resources
        resources.append(Resource(
            uri="validation://campaign",
            name="Campaign Validation",
            description="Validate campaign for export to game engines"
        ))
        
        # Analytics resources
        resources.append(Resource(
            uri="analytics://campaign_stats",
            name="Campaign Statistics",
            description="Get completion rates and player engagement metrics"
        ))
        
        resources.append(Resource(
            uri="analytics://player_behavior",
            name="Player Analytics",
            description="Get player behavior metrics and heatmaps"
        ))
        
        # Economy resources
        resources.append(Resource(
            uri="economy://balance",
            name="Economy Balance",
            description="Get economy balance, inflation, and trade data"
        ))
        
        logger.info(f"Created {len(resources)} MCP resources")
        return resources
    
    def _handle_list_campaigns(self, arguments: Dict[str, Any]) -> str:
        """Handle list_campaigns tool."""
        campaigns = list(self.campaigns.values())
        
        result = {
            "campaigns": [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "type": c.campaign_type,
                    "difficulty": c.difficulty
                } for c in campaigns
            ],
            "count": len(campaigns)
        }
        
        logger.info(f"Listed {len(campaigns)} campaigns")
        return json.dumps(result, indent=2)
    
    def _handle_get_campaign(self, arguments: Dict[str, Any]) -> str:
        """Handle get_campaign tool."""
        campaign_id = arguments.get("id")
        
        if campaign_id not in self.campaigns:
            return json.dumps({
                "error": "Campaign not found",
                "campaign_id": campaign_id
            }, indent=2)
        
        campaign = self.campaigns[campaign_id]
        
        result = {
            "campaign": {
                "id": campaign.id,
                "name": campaign.name,
                "description": campaign.description,
                "type": campaign.campaign_type,
                "difficulty": campaign.difficulty,
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "tenant_id": self.tenant_id
                }
            },
            "chapters": [],  # Would load from database
            "quests": []  # Would load from database
        }
        
        logger.info(f"Retrieved campaign: {campaign.name}")
        return json.dumps(result, indent=2)
    
    def _handle_create_campaign(self, arguments: Dict[str, Any]) -> str:
        """Handle create_campaign tool."""
        name = arguments.get("name")
        description = arguments.get("description")
        campaign_type = arguments.get("campaign_type", "main_story")
        difficulty = arguments.get("difficulty", "medium")
        
        if not name or not description:
            return json.dumps({
                "error": "Name and description are required"
            }, indent=2)
        
        # Create campaign
        campaign = Campaign(
            id=f"campaign_{datetime.now().timestamp()}",
            name=name,
            description=description,
            campaign_type=campaign_type,
            difficulty=difficulty
        )
        
        self.campaigns[campaign.id] = campaign
        
        logger.info(f"Created campaign: {name} ({campaign.id})")
        return json.dumps({
            "campaign": {
                "id": campaign.id,
                "name": name,
                "description": description,
                "type": campaign_type,
                "difficulty": difficulty
            },
            "status": "created",
            "message": f"Campaign '{name}' created successfully"
        }, indent=2)
    
    def _handle_validate_campaign(self, arguments: Dict[str, Any]) -> str:
        """Handle validate_campaign tool."""
        campaign_id = arguments.get("campaign_id")
        
        if campaign_id not in self.campaigns:
            return json.dumps({
                "error": "Campaign not found",
                "campaign_id": campaign_id
            }, indent=2)
        
        campaign = self.campaigns[campaign_id]
        
        # Stub validation (in production, would use campaign.validate())
        validation_result = {
            "campaign_id": campaign_id,
            "name": campaign.name,
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        logger.info(f"Validated campaign: {campaign.name}")
        return json.dumps(validation_result, indent=2)
    
    def _handle_export_campaign_to_unreal(self, arguments: Dict[str, Any]) -> str:
        """Handle export_campaign_to_unreal tool."""
        campaign_id = arguments.get("campaign_id")
        format_type = arguments.get("format", "json")
        
        if campaign_id not in self.campaigns:
            return json.dumps({
                "error": "Campaign not found",
                "campaign_id": campaign_id
            }, indent=2)
        
        campaign = self.campaigns[campaign_id]
        
        # Stub export (in production, would use real export logic)
        export_data = {
            "campaign": {
                "id": campaign.id,
                "name": campaign.name,
                "description": campaign.description,
                "type": campaign.campaign_type,
                "difficulty": campaign.difficulty
            },
            "format": format_type,
            "unreal_version": "5.3",
            "export_date": datetime.now().isoformat(),
            "metadata": {
                "campaign_id": campaign_id,
                "tenant_id": self.tenant_id
            }
        }
        
        logger.info(f"Exported campaign: {campaign.name} to {format_type}")
        return json.dumps(export_data, indent=2)
    
    async def start(self) -> None:
        """Start the MCP server."""
        tools = self.create_tools()
        resources = self.create_resources()
        
        if MCP_AVAILABLE:
            # Create MCP server
            server = StdioServer("loreSystem", version="1.0.0")
            
            # Register tools
            for tool in tools:
                server.add_tool(tool)
            
            # Register resources
            for resource in resources:
                server.add_resource(resource)
            
            logger.info(f"MCP server starting on {self.host}:{self.port}")
            logger.info(f"Tools: {len(tools)}, Resources: {len(resources)}")
            
            await server.serve()
        else:
            logger.warning("MCP SDK not available, running in stub mode")
            logger.info("MCP server stub started (no actual MCP functionality)")

# Global server instance
mcp_server = LoreSystemMCPServer()

if __name__ == "__main__":
    import sys
    import asyncio
    
    logger.info("Starting loreSystem MCP Server...")
    try:
        asyncio.run(mcp_server.start())
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"MCP server crashed: {e}")
        sys.exit(1)
