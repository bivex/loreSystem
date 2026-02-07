#!/usr/bin/env python3
"""
Integrate Quest repositories into the codebase

This script automatically:
1. Adds interface imports to in_memory_repositories.py
2. Adds InMemory repository implementations to in_memory_repositories.py
3. Adds SQLite repository implementations to sqlite_repositories.py
4. Adds SQL table schemas to sqlite_repositories.py (initialize_schema)
5. Updates exports in __init__.py
6. Updates server.py initialization
"""

import sys
from pathlib import Path
import re

# Paths
project_root = Path(__file__).parent
in_memory_repos_path = project_root / "src" / "infrastructure" / "in_memory_repositories.py"
sqlite_repos_path = project_root / "src" / "infrastructure" / "sqlite_repositories.py"
init_path = project_root / "src" / "infrastructure" / "__init__.py"
server_path = project_root / "lore_mcp_server" / "mcp_server" / "server.py"

# Quest entities to process
QUEST_ENTITIES = [
    "quest_chain",
    "quest_node",
    "quest_prerequisite",
    "quest_objective",
    "quest_tracker",
    "quest_giver",
    "quest_reward",
    "quest_reward_tier",
]

def capitalize_name(name):
    """Capitalize first letter for class names."""
    return name[0].upper() + name[1:]

def camel_case(name):
    """Convert to camel case (quest_chain -> QuestChain)."""
    parts = name.split('_')
    return ''.join(part.capitalize() for part in parts)

def add_to_in_memory_repositories():
    """Add Quest repository imports and implementations to in_memory_repositories.py"""
    print("\n=== Updating in_memory_repositories.py ===")
    
    content = in_memory_repos_path.read_text()
    
    # Find where to add (after existing repository classes)
    # Look for last class definition in existing file
    pattern = r'class InMemory\w+Repository\('
    matches = list(re.finditer(pattern, content))
    
    if not matches:
        print("Error: Could not find existing repository classes")
        return False
    
    last_match_end = matches[-1].end()
    
    # Build new imports and classes
    new_imports_lines = []
    new_class_lines = []
    
    for entity in QUEST_ENTITIES:
        entity_camel = camel_case(entity)
        interface_name = f"I{entity_camel}Repository"
        
        # Import line
        new_imports_lines.append(f"from src.domain.repositories.{entity}_repository import {interface_name}")
        
        # Class implementation
        class_def = f"""
class InMemory{entity_camel}Repository({interface_name}):
    \"\"\"In-memory implementation of {entity_camel} repository for testing.\"\"\"

    def __init__(self):
        from typing import Dict, List, Optional, Tuple
        from collections import defaultdict
        from src.domain.entities.{entity} import {entity_camel}
        from src.domain.value_objects.common import TenantId, EntityId
        from src.domain.exceptions import DuplicateEntity
        
        self._entities: Dict[Tuple[TenantId, EntityId], {entity_camel}] = {{}}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, entity: {entity_camel}) -> {entity_camel}:
        if entity.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)

        key = (entity.tenant_id, entity.id)
        self._entities[key] = entity
        
        world_key = (entity.tenant_id, entity.world_id) if hasattr(entity, 'world_id') else None
        if world_key:
            if entity.id not in self._by_world[world_key]:
                self._by_world[world_key].append(entity.id)

        return entity

    def find_by_id(self, tenant_id: TenantId, entity_id: EntityId) -> Optional[{entity_camel}]:
        return self._entities.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[{entity_camel}]:
        world_key = (tenant_id, world_id)
        entity_ids = self._by_world.get(world_key, [])
        entities = []
        for entity_id in entity_ids[offset:offset + limit]:
            entity = self._entities.get((tenant_id, entity_id))
            if entity:
                entities.append(entity)
        return entities

    def delete(self, tenant_id: TenantId, entity_id: EntityId) -> bool:
        key = (tenant_id, entity_id)
        if key not in self._entities:
            return False

        entity = self._entities[key]
        
        world_key = (entity.tenant_id, entity.world_id) if hasattr(entity, 'world_id') else None
        if world_key and entity_id in self._by_world[world_key]:
            self._by_world[world_key].remove(entity_id)

        del self._entities[key]
        return True
"""
        new_class_lines.append(class_def)
    
    # Insert new imports after existing imports
    import_pattern = r'(from src\.domain\.repositories\.[^\n]+)'
    matches = list(re.finditer(import_pattern, content))
    
    if matches:
        last_import_end = matches[-1].end()
        new_imports_section = '\n'.join(new_imports_lines) + '\n\n'
        new_content = content[:last_import_end] + new_imports_section + content[last_import_end:]
        
        # Insert new classes
        new_classes_section = '\n'.join(new_class_lines) + '\n\n'
        new_content = new_content + new_classes_section
        
        in_memory_repos_path.write_text(new_content)
        print(f"  ✓ Added {len(QUEST_ENTITIES)} Quest repository implementations")
    
    return True

def add_to_sqlite_repositories():
    """Add SQLite repository implementations to sqlite_repositories.py"""
    print("\n=== Updating sqlite_repositories.py ===")
    
    content = sqlite_repos_path.read_text()
    
    # Find where to add (before last class)
    pattern = r'class SQLite\w+Repository\('
    matches = list(re.finditer(pattern, content))
    
    if not matches:
        print("Error: Could not find SQLite repository classes")
        return False
    
    last_match_end = matches[-1].end()
    
    # Build new SQLite implementations
    new_sqlite_classes = []
    
    for entity in QUEST_ENTITIES:
        entity_camel = camel_case(entity)
        interface_name = f"I{entity_camel}Repository"
        table_name = f"{entity}s"
        
        # SQLite implementation
        class_def = f"""
class SQLite{entity_camel}Repository({interface_name}):
    \"\"\"SQLite implementation of {entity_camel} repository for production use.\"\"\"

    def __init__(self, db: SQLiteDatabase):
        import sqlite3
        from datetime import datetime
        from src.domain.value_objects.common import TenantId, EntityId
        
        self.db = db

    def save(self, entity: {entity_camel}) -> {entity_camel}:
        now = datetime.now().isoformat()

        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(\"\"\"
                    INSERT INTO {table_name} (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                \"\"\", (
                    entity.tenant_id.value,
                    entity.world_id.value if hasattr(entity, "world_id") else None,
                    entity.name,
                    getattr(entity, "description", None),
                    now,
                    now
                ))
                entity_id = cursor.lastrowid
                object.__setattr__(entity, 'id', EntityId(entity_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute(\"\"\"
                    UPDATE {table_name}
                    SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                \"\"\", (
                    entity.name,
                    getattr(entity, "description", None),
                    entity.id.value,
                    entity.tenant_id.value
                ))

        return entity

    def find_by_id(self, tenant_id: TenantId, entity_id: EntityId) -> Optional[{entity_camel}]:
        with self.db.get_connection() as conn:
            row = conn.execute(\"\"\"
                SELECT * FROM {table_name} WHERE id = ? AND tenant_id = ?
            \"\"\", (entity_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[{entity_camel}]:
        with self.db.get_connection() as conn:
            rows = conn.execute(\"\"\"
                SELECT * FROM {table_name} WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            \"\"\", (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id: TenantId, entity_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute(\"\"\"
                DELETE FROM {table_name} WHERE id = ? AND tenant_id = ?
            \"\"\", (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row: sqlite3.Row) -> {entity_camel}:
        return self._entity_from_row(row)
    
    @staticmethod
    def _entity_from_row(row: sqlite3.Row) -> {entity_camel}:
        from src.domain.entities.{entity} import {entity_camel}
        from src.domain.value_objects.common import Description
        
        return {entity_camel}(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )
"""
        new_sqlite_classes.append(class_def)
    
    new_content = content[:last_match_end] + '\n'.join(new_sqlite_classes) + content[last_match_end:]
    
    sqlite_repos_path.write_text(new_content)
    print(f"  ✓ Added {len(QUEST_ENTITIES)} SQLite repository implementations")
    
    return True

def add_sql_tables():
    """Add SQL table schemas to sqlite_repositories.py"""
    print("\n=== Adding SQL tables to sqlite_repositories.py ===")
    
    content = sqlite_repos_path.read_text()
    
    # Find the initialize_schema method
    pattern = r'def initialize_schema\(self\):'
    matches = list(re.finditer(pattern, content))
    
    if not matches:
        print("Error: Could not find initialize_schema method")
        return False
    
    schema_start = matches[-1].start()
    
    # Find where to insert tables (after CREATE TABLE statements)
    # Look for "CREATE TABLE IF NOT EXISTS" in the method
    schema_pattern = r'CREATE TABLE IF NOT EXISTS \w+\('
    schema_matches = list(re.finditer(schema_pattern, content[schema_start:]))
    
    if not schema_matches:
        print("Error: Could not find CREATE TABLE statements")
        return False
    
    last_table_end = schema_matches[-1].end()
    
    # Build new table definitions
    new_table_definitions = []
    for entity in QUEST_ENTITIES:
        table_name = f"{entity}s"
        table_def = f"""
            # {table_name} table
            conn.execute(\"\"\"
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            \"\"\")"""
        new_table_definitions.append(table_def)
    
    new_content = content[:last_table_end] + '\n'.join(new_table_definitions) + '\n' + content[last_table_end:]
    
    sqlite_repos_path.write_text(new_content)
    print(f"  ✓ Added {len(QUEST_ENTITIES)} SQL table definitions")
    
    return True

def update_exports():
    """Update __init__.py exports"""
    print("\n=== Updating infrastructure/__init__.py ===")
    
    content = init_path.read_text()
    
    # Find SQLite exports section
    sql_export_pattern = r"(# SQLite repositories.*?)(from src\.infrastructure\.sqlite_repositories import\[?\n.]+?)"
    
    if not re.search(sql_export_pattern, content):
        print("Warning: Could not find SQLite export section pattern")
        return False
    
    # Build new exports
    new_imports = []
    new_exports = []
    
    for entity in QUEST_ENTITIES:
        entity_camel = camel_case(entity)
        class_name = f"SQLite{entity_camel}Repository"
        new_imports.append(f"    {class_name},")
        new_exports.append(f"    '{class_name}',")
    
    new_imports_section = "from src.infrastructure.sqlite_repositories import (\n" + '\n'.join(new_imports) + "\n)"
    new_exports_section = "# SQLite repositories (for production)\n" + '\n'.join(new_exports) + "\n"
    
    # Replace old exports
    content = re.sub(sql_export_pattern, new_exports_section, content)
    
    init_path.write_text(content)
    print(f"  ✓ Updated exports with {len(QUEST_ENTITIES)} Quest repositories")
    
    return True

def update_server():
    """Update server.py to initialize Quest repositories"""
    print("\n=== Updating server.py ===")
    
    content = server_path.read_text()
    
    # Find repository initialization sections
    sqlite_section_pattern = r'(if connection_type == "sqlite":\n.*?)(\s+world_repo = SQLiteWorldRepository\(sqlite_db\))'
    in_memory_section_pattern = r'(else:.*?)(\s+world_repo = InMemoryWorldRepository\(\))'
    
    # Build new repository initializations
    sqlite_repo_lines = []
    in_memory_repo_lines = []
    
    for entity in QUEST_ENTITIES:
        entity_camel = camel_case(entity)
        repo_class = f"SQLite{entity_camel}Repository"
        repo_var = f"{entity}_repo"
        
        sqlite_repo_lines.append(f"    {repo_var} = {repo_class}(sqlite_db)")
        in_memory_repo_lines.append(f"    {repo_var} = InMemory{entity_camel}Repository()")
    
    # Insert into SQLite section
    content = re.sub(sqlite_section_pattern, r'\1\n' + '\n'.join(sqlite_repo_lines) + r'\2\n', content)
    
    # Insert into In-Memory section
    content = re.sub(in_memory_section_pattern, r'\1\n' + '\n'.join(in_memory_repo_lines) + r'\2\n', content)
    
    server_path.write_text(content)
    print(f"  ✓ Updated server.py with {len(QUEST_ENTITIES)} Quest repositories")
    
    return True

def main():
    """Run all integration steps"""
    print("=" * 80)
    print("QUEST REPOSITORY INTEGRATION")
    print("=" * 80)
    print()
    
    success = True
    
    success = success and add_to_in_memory_repositories()
    success = success and add_to_sqlite_repositories()
    success = success and add_sql_tables()
    success = success and update_exports()
    success = success and update_server()
    
    print()
    print("=" * 80)
    if success:
        print("✅ SUCCESS! All Quest repositories integrated")
        print()
        print("Next steps:")
        print("  1. Run tests: python3 check_repositories.py")
        print("  2. Commit changes: git add -A && git commit -m 'feat: Add Quest repositories'")
        print("  3. Push: git push origin master")
    else:
        print("❌ FAILED! Check errors above")
    print("=" * 80)

if __name__ == "__main__":
    main()
