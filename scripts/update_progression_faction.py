#!/usr/bin/env python3
"""
Update exports and server for Progression and Faction repositories
"""

import sys
from pathlib import Path

init_path = Path("/root/clawd/src/infrastructure/__init__.py")
server_path = Path("/root/clawd/lore_mcp_server/mcp_server/server.py")

# Progression repositories (8)
PROGRESSION_NAMES = [
    "Skill",
    "Perk",
    "Trait",
    "Attribute",
    "Experience",
    "LevelUp",
    "TalentTree",
    "Mastery",
]

# Faction repositories (6)
FACTION_NAMES = [
    "FactionHierarchy",
    "FactionIdeology",
    "FactionLeader",
    "FactionMembership",
    "FactionResource",
    "FactionTerritory",
]

ALL_NAMES = PROGRESSION_NAMES + FACTION_NAMES

def update_exports():
    """Update __init__.py exports"""
    print("=== Updating infrastructure/__init__.py ===")
    
    content = init_path.read_text()
    
    # Build new imports
    in_mem_imports = "\n".join([f"from src.infrastructure.in_memory_repositories import {name}" for name in ALL_NAMES])
    sqlite_imports = "\n".join([f"from src.infrastructure.sqlite_repositories import SQLite{name}" for name in ALL_NAMES])
    
    # Build new exports
    in_mem_exports = "# Progression repositories\n" + "\n".join([f"    {name}," for name in PROGRESSION_NAMES]) + "\n\n"
    in_mem_exports += "# Faction repositories\n" + "\n".join([f"    {name}," for name in FACTION_NAMES]) + "\n"
    
    sqlite_exports = "# Progression repositories\n" + "\n".join([f"    SQLite{name}," for name in PROGRESSION_NAMES]) + "\n\n"
    sqlite_exports += "# Faction repositories\n" + "\n".join([f"    SQLite{name}," for name in FACTION_NAMES]) + "\n"
    
    # Add imports at end
    content += "\n" + in_mem_imports + "\n" + sqlite_imports
    
    # Add exports at end
    content += "\n" + in_mem_exports + sqlite_exports
    
    init_path.write_text(content)
    print("  ✓ Updated exports")
    return True

def update_server():
    """Update server.py to initialize repositories"""
    print("=== Updating server.py ===")
    
    content = server_path.read_text()
    
    # Build new repository initializations
    new_repos = "\n".join([f"    {name.lower()}_repo = {name}()" for name in ALL_NAMES])
    new_repos += "\n"
    new_repos += "\n".join([f"    {name.lower()}_repo = SQLite{name}(sqlite_db)" for name in ALL_NAMES])
    
    # Find SQLite initialization section
    sqlite_pattern = "if connection_type == \"sqlite\":"
    if sqlite_pattern in content:
        sqlite_pos = content.find(sqlite_pattern)
        next_section = content.find("\n\n", sqlite_pos + len(sqlite_pattern))
        
        if next_section > sqlite_pos:
            content = content[:next_section] + new_repos + "\n\n" + content[next_section:]
            print("  ✓ Updated SQLite initialization")
    
    # Find In-Memory initialization section
    else_pattern = "else:"
    if else_pattern in content:
        else_pos = content.find(else_pattern)
        next_section = content.find("\n\n", else_pos + len(else_pattern))
        
        if next_section > else_pos:
            content = content[:next_section] + new_repos + "\n\n" + content[next_section:]
            print("  ✓ Updated In-Memory initialization")
    
    server_path.write_text(content)
    return True

def main():
    print("=" * 80)
    print("PROGRESSION & FACTION INTEGRATION")
    print("=" * 80)
    print()
    
    success = True
    success = success and update_exports()
    success = success and update_server()
    
    print()
    print("=" * 80)
    if success:
        print("✅ SUCCESS! Progression and Faction repositories integrated")
        print()
        print("Summary:")
        print(f"  - Progression: {len(PROGRESSION_NAMES)} repositories")
        print(f"  - Factions: {len(FACTION_NAMES)} repositories")
        print(f"  - Total: {len(ALL_NAMES)} new repositories")
        print()
        print("Check coverage:")
        print("  python3 check_repositories.py")
    else:
        print("❌ FAILED! Check errors above")
    print("=" * 80)

if __name__ == "__main__":
    main()
