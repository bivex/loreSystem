#!/usr/bin/env python3
"""
Update exports and server initialization for Quest repositories
"""

import sys
from pathlib import Path

init_path = Path("/root/clawd/src/infrastructure/__init__.py")
server_path = Path("/root/clawd/lore_mcp_server/mcp_server/server.py")

QUEST_REPO_NAMES = [
    "QuestChain",
    "QuestNode",
    "QuestPrerequisite",
    "QuestObjective",
    "QuestTracker",
    "QuestGiver",
    "QuestReward",
    "QuestRewardTier",
]

def update_exports():
    """Update __init__.py exports"""
    print("=== Updating infrastructure/__init__.py ===")
    
    content = init_path.read_text()
    
    # Build new imports and exports for Quest repositories
    new_imports = "\n".join([f"from src.infrastructure.in_memory_repositories import {name}" for name in QUEST_REPO_NAMES])
    new_imports += "\n" + "\n".join([f"from src.infrastructure.sqlite_repositories import SQLite{name}" for name in QUEST_REPO_NAMES])
    
    new_exports = "# Quest repositories\n" + "\n".join([f"    InMemory{name}," for name in QUEST_REPO_NAMES]) + "\n"
    new_exports += "\n" + "\n".join([f"    SQLite{name}," for name in QUEST_REPO_NAMES]) + "\n"
    
    # Add after existing SQLite repositories section
    sql_marker = "# SQLite repositories"
    if sql_marker in content:
        marker_pos = content.find(sql_marker) + len(sql_marker)
        content = content[:marker_pos] + new_imports + content[marker_pos:]
        
        # Add exports at end
        content = content + "\n" + new_exports
        
        init_path.write_text(content)
        print("  ✓ Updated exports")
        return True
    
    print("  ⚠️  SQLite repositories section not found")
    return False

def update_server():
    """Update server.py to initialize Quest repositories"""
    print("=== Updating server.py ===")
    
    content = server_path.read_text()
    
    # Build new repository initializations
    new_repos = "\n".join([f"    {name.lower()}_repo = InMemory{name}()" for name in QUEST_REPO_NAMES])
    new_repos += "\n"
    new_repos += "\n".join([f"    {name.lower()}_repo = SQLite{name}(sqlite_db)" for name in QUEST_REPO_NAMES])
    
    # Find and update SQLite section
    sqlite_pattern = "if connection_type == \"sqlite\":"
    if sqlite_pattern in content:
        sqlite_pos = content.find(sqlite_pattern)
        next_section = content.find("\n\n", sqlite_pos)
        
        if next_section > sqlite_pos:
            content = content[:next_section] + new_repos + content[next_section:]
            print("  ✓ Updated SQLite initialization")
            return True
    
    # Find and update In-Memory section
    else_pattern = "else:"
    if else_pattern in content:
        else_pos = content.find(else_pattern)
        next_section = content.find("\n\n", else_pos)
        
        if next_section > else_pos:
            content = content[:next_section] + new_repos + content[next_section:]
            print("  ✓ Updated In-Memory initialization")
            return True
    
    print("  ⚠️  Repository initialization sections not found")
    return False

def main():
    print("=" * 80)
    print("QUEST REPOSITORY EXPORT & SERVER UPDATE")
    print("=" * 80)
    print()
    
    success = True
    success = success and update_exports()
    success = success and update_server()
    
    print()
    print("=" * 80)
    if success:
        print("✅ SUCCESS! Quest repositories integrated")
    else:
        print("❌ FAILED! Check errors above")
    print("=" * 80)

if __name__ == "__main__":
    main()
