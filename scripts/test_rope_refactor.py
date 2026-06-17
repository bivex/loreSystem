#!/usr/bin/env python3
"""Test Rope refactoring library by renaming serialize_entity to serialize_lore_entity."""

import os
import sys

try:
    from rope.base.project import Project
    from rope.refactor.rename import Rename
except ImportError:
    print("❌ Rope is not installed in this Python environment.")
    sys.exit(1)

def main():
    project_path = "/Volumes/External/Code/loreSystem/lore_mcp_server"
    print(f"📂 Opening project at: {project_path}")
    proj = Project(project_path)
    
    file_path = "mcp_server/server.py"
    print(f"🔍 Finding file: {file_path}")
    resource = proj.get_resource(file_path)
    
    content = resource.read()
    target = "def serialize_entity"
    if target not in content:
        print(f"❌ Target '{target}' not found in {file_path}")
        return 1
        
    offset = content.index("serialize_entity")
    print(f"📍 Found 'serialize_entity' at character offset: {offset}")
    
    print("⚡ Initializing Rope Rename refactoring...")
    rename = Rename(proj, resource, offset)
    
    new_name = "serialize_lore_entity"
    print(f"🔄 Generating refactoring changes (rename to '{new_name}')...")
    changes = rename.get_changes(new_name)
    
    print("\n--- ROPE REFACTORING DIFF DESCRIPTION ---")
    print(changes.get_description())
    print("-----------------------------------------")
    
    proj.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
