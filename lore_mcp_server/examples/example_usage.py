#!/usr/bin/env python3
"""
Example usage of the Lore System MCP Server

This script demonstrates how to use the MCP tools via the server.
Note: In production, these tools would be called by an MCP client (like Claude Desktop).
"""

import json
import asyncio
from pathlib import Path
import sys

# Add project root to path (loreSystem directory)
# __file__ is lore_mcp_server/examples/example_usage.py
# parent.parent = loreSystem/lore_mcp_server, parent.parent.parent = loreSystem/
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the server
from mcp_server.server import call_tool


async def demo_lore_system():
    """Demonstrate the lore system MCP tools."""

    tenant_id = "demo-tenant"

    print("=" * 80)
    print("LORE SYSTEM MCP SERVER DEMO")
    print("=" * 80)

    # 1. Create a World
    print("\n1. Creating a world...")
    world_result = await call_tool("create_world", {
        "tenant_id": tenant_id,
        "name": "Aetheria",
        "description": "A high-fantasy realm where magic and technology coexist in harmony. Ancient ruins dot the landscape, each containing fragments of a lost civilization's knowledge."
    })
    print(world_result[0].text)
    world_data = json.loads(world_result[0].text)
    world_id = world_data["world"]["id"]

    # 2. Create Characters
    print("\n2. Creating characters...")

    # Character 1: Legendary Mage
    char1_result = await call_tool("create_character", {
        "tenant_id": tenant_id,
        "world_id": world_id,
        "name": "Lyra Starweaver",
        "backstory": "Born under a celestial convergence, Lyra discovered her affinity for star magic at age five. She spent decades studying at the Arcane Nexus, eventually becoming one of the youngest Archmages in history. Her research into dimensional rifts led to groundbreaking discoveries, but also attracted the attention of forces beyond mortal comprehension.",
        "rarity": "LEGENDARY",
        "element": "light",
        "role": "dps",
        "base_hp": 800,
        "base_atk": 320,
        "base_def": 120,
        "base_speed": 180,
        "energy_cost": 120
    })
    print(char1_result[0].text)
    char1_data = json.loads(char1_result[0].text)
    char1_id = char1_data["character"]["id"]

    # Character 2: Tank Warrior
    char2_result = await call_tool("create_character", {
        "tenant_id": tenant_id,
        "world_id": world_id,
        "name": "Gorak Ironheart",
        "backstory": "A mountain dwarf from the Iron Peaks, Gorak earned his surname by surviving a dragon's fire breath that would have killed lesser warriors. His legendary endurance and unwavering loyalty make him the perfect shield for any party. He carries the Aegis of Ancestors, a shield passed down through generations.",
        "rarity": "EPIC",
        "element": "earth",
        "role": "tank",
        "base_hp": 1500,
        "base_atk": 180,
        "base_def": 320,
        "base_speed": 80,
        "energy_cost": 100
    })
    print(char2_result[0].text)

    # 3. Add Abilities
    print("\n3. Adding abilities to Lyra...")

    ability1 = await call_tool("add_ability", {
        "tenant_id": tenant_id,
        "character_id": char1_id,
        "ability_name": "Cosmic Cascade",
        "description": "Summons a rain of starlight that damages all enemies and reveals hidden truths",
        "power_level": 92
    })
    print(ability1[0].text)

    ability2 = await call_tool("add_ability", {
        "tenant_id": tenant_id,
        "character_id": char1_id,
        "ability_name": "Dimensional Shift",
        "description": "Briefly phases into another dimension, avoiding all damage and repositioning",
        "power_level": 75
    })
    print(ability2[0].text)

    # 4. Create a Story
    print("\n4. Creating a story...")
    story_result = await call_tool("create_story", {
        "tenant_id": tenant_id,
        "world_id": world_id,
        "name": "The Rift Awakens",
        "description": "When dimensional rifts begin appearing across Aetheria, Lyra must team up with unlikely allies to prevent reality itself from unraveling.",
        "story_type": "NON_LINEAR",
        "content": "Chapter 1: The First Tremor\n\nThe arcane sensors flickered with impossible readings. Lyra's hands moved across the crystalline interface, her brow furrowed in concentration..."
    })
    print(story_result[0].text)

    # 5. Create an Event
    print("\n5. Creating a timeline event...")
    event_result = await call_tool("create_event", {
        "tenant_id": tenant_id,
        "world_id": world_id,
        "name": "The Battle of Shattered Sky",
        "description": "A massive rift opens above the capital city, unleashing otherworldly horrors",
        "start_date": "3024-06-15T14:30:00",
        "end_date": "3024-06-15T23:45:00",
        "outcome": "success"
    })
    print(event_result[0].text)

    # 6. Create a Lore Page
    print("\n6. Creating a lore page...")
    page_result = await call_tool("create_page", {
        "tenant_id": tenant_id,
        "world_id": world_id,
        "name": "The Arcane Nexus",
        "content": """# The Arcane Nexus

## Overview
The Arcane Nexus is the premier institution for magical study in Aetheria, floating above the Crystal Lake on enchanted platforms.

## History
Founded in the Year 1247 by the Council of Seven, the Nexus has produced generations of skilled mages.

## Notable Features
- **The Eternal Library**: Contains every spell ever documented
- **Dimensional Research Wing**: Where Lyra made her discoveries
- **The Summoning Circles**: Ancient rings of power predating the Nexus itself

## Current Leadership
Archmage Lyra Starweaver serves as Head of Dimensional Studies.
"""
    })
    print(page_result[0].text)

    # 7. List Everything
    print("\n7. Listing all content...")

    print("\n--- All Characters ---")
    chars_result = await call_tool("list_characters", {
        "tenant_id": tenant_id,
        "world_id": world_id
    })
    chars_data = json.loads(chars_result[0].text)
    for char in chars_data["characters"]:
        print(f"  - {char['name']} ({char['rarity']}) - {char['role']} - {len(char['abilities'])} abilities")

    print("\n--- All Stories ---")
    stories_result = await call_tool("list_stories", {
        "tenant_id": tenant_id,
        "world_id": world_id
    })
    stories_data = json.loads(stories_result[0].text)
    for story in stories_data["stories"]:
        print(f"  - {story['name']} ({story['story_type']})")

    print("\n--- All Events ---")
    events_result = await call_tool("list_events", {
        "tenant_id": tenant_id,
        "world_id": world_id
    })
    events_data = json.loads(events_result[0].text)
    for event in events_data["events"]:
        print(f"  - {event['name']} - {event['outcome']}")

    print("\n--- All Pages ---")
    pages_result = await call_tool("list_pages", {
        "tenant_id": tenant_id,
        "world_id": world_id
    })
    pages_data = json.loads(pages_result[0].text)
    for page in pages_data["pages"]:
        print(f"  - {page['name']}")

    # 8. Save everything to JSON
    print("\n8. Saving all data to JSON files...")
    save_result = await call_tool("save_to_json", {
        "tenant_id": tenant_id
    })
    save_data = json.loads(save_result[0].text)
    print(f"\nSaved {save_data['counts']['total_files']} files:")
    print(f"  - Worlds: {save_data['counts']['worlds']}")
    print(f"  - Characters: {save_data['counts']['characters']}")
    print(f"  - Stories: {save_data['counts']['stories']}")
    print(f"  - Events: {save_data['counts']['events']}")
    print(f"  - Pages: {save_data['counts']['pages']}")
    print(f"\nData directory: {save_data['data_directory']}")

    # 9. Export to single file
    print("\n9. Exporting tenant data to single file...")
    export_result = await call_tool("export_tenant", {
        "tenant_id": tenant_id,
        "filename": "aetheria_complete.json"
    })
    export_data = json.loads(export_result[0].text)
    print(f"Exported to: {export_data['filepath']}")
    print(f"File size: {export_data['size_kb']} KB")

    # 10. Get storage statistics
    print("\n10. Storage statistics...")
    stats_result = await call_tool("get_storage_stats", {})
    stats_data = json.loads(stats_result[0].text)
    print(f"Total files: {stats_data['statistics']['total_files']}")
    print(f"Total size: {stats_data['statistics']['total_size_bytes']} bytes")
    for entity_type, type_stats in stats_data['statistics']['by_type'].items():
        print(f"  - {entity_type}: {type_stats['count']} files, {type_stats['size_bytes']} bytes")

    print("\n" + "=" * 80)
    print("DEMO COMPLETE!")
    print("=" * 80)
    print("\n✅ All lore data has been saved to JSON files!")
    print(f"📁 Check the '{save_data['data_directory']}' directory")


if __name__ == "__main__":
    asyncio.run(demo_lore_system())
