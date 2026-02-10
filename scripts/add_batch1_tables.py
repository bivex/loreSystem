#!/usr/bin/env python3
"""
Add SQLite tables for remaining entities (Batch 1: CoreGameSystems, InventoryCrafting, Locations - 33 entities)
"""

from pathlib import Path

sqlite_path = Path("/root/clawd/src/infrastructure/sqlite_repositories.py")

# First batch - 33 entities
entities = [
    "character_evolution", "character_variant", "character_profile_entry", "motion_capture", "voice_actor",
    "act", "chapter", "episode", "prologue", "epilogue", "plot_branch", "consequence", "ending", "alternate_reality",
    "inventory", "crafting_recipe", "material", "component", "blueprint", "enchantment", "socket", "rune", "glyph",
    "hub_area", "instance", "dungeon", "raid", "arena", "open_world_zone", "underground", "skybox", "dimension", "pocket_dimension",
]

print(f"Adding {len(entities)} SQL tables...")

content = sqlite_path.read_text()

# Find initialize_schema method
schema_start = content.find('def initialize_schema(self):')
schema_end = content.find('\n        pass', schema_start + 30)

if schema_end == -1:
    schema_end = content.find('\n        pass', schema_start + 50)

# Generate table definitions
new_tables = ""
for entity in entities:
    table_name = f"{entity}s"
    new_tables += f"\n            # {table_name} table\n"
    new_tables += f'            conn.execute("""\n'
    new_tables += f'                CREATE TABLE IF NOT EXISTS {table_name} (\n'
    new_tables += f'                    id INTEGER PRIMARY KEY AUTOINCREMENT,\n'
    new_tables += f'                    tenant_id INTEGER NOT NULL,\n'
    new_tables += f'                    world_id INTEGER,\n'
    new_tables += f'                    name TEXT NOT NULL,\n'
    new_tables += f'                    description TEXT,\n'
    new_tables += f'                    created_at TEXT NOT NULL,\n'
    new_tables += f'                    updated_at TEXT NOT NULL,\n'
    new_tables += f'                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE\n'
    new_tables += f'                """\n'
    new_tables += f'            """)\n'
    if entity in entities[::10]:
        print(f"  ✓ {table_name}")

# Insert before method ends
new_content = content[:schema_end] + new_tables + content[schema_end:]
sqlite_path.write_text(new_content)

print(f"✅ Added {len(entities)} SQL tables")
