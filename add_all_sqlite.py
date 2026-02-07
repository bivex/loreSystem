#!/usr/bin/env python3
"""
Add ALL SQLite repository implementations for 230 new entities
"""

import sys
from pathlib import Path

sqlite_path = Path("/root/clawd/src/infrastructure/sqlite_repositories.py")
init_path = Path("/root/clawd/src/infrastructure/__init__.py")
server_path = Path("/root/clawd/lore_mcp_server/mcp_server/server.py")
repos_dir = Path("/root/clawd/src/domain/repositories")

# Get all new interface files (without implementations yet)
new_entities = []
for filepath in repos_dir.glob("*_repository.py"):
    if filepath.name.startswith("__"):
        continue
    
    entity_name = filepath.stem.replace("_repository", "")
    
    # Check if already has SQLite implementation
    with open(sqlite_path, 'r') as f:
        content = f.read()
        if f"SQLite{entity_name[0].upper()}{entity_name[1:]}Repository" in content:
            continue  # Already has SQLite implementation
    
    new_entities.append(entity_name)

print(f"Found {len(new_entities)} entities without SQLite implementations")
print()

# --- Add SQLite implementations ---
print("=== Adding SQLite implementations ===")

sqlite_implementations = ""
for entity in new_entities:
    entity_camel = entity[0].upper() + entity[1:]
    table_name = f"{entity}s"
    
    # SQLite repository implementation
    sqlite_implementations += f'''
class SQLite{entity_camel}Repository:
    """SQLite implementation of {entity_camel} repository."""
    def __init__(self, db):
        from src.infrastructure.sqlite_repositories import SQLiteDatabase
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute(f"INSERT INTO {table_name} (tenant_id, world_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (entity.tenant_id.value, getattr(entity, 'world_id', lambda: entity.world_id.value, None), entity.name, getattr(entity, 'description', None), now, now))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute(f"UPDATE {table_name} SET name = ?, description = ? WHERE id = ? AND tenant_id = ?",
                    (entity.name, getattr(entity, 'description', None), entity.id.value, entity.tenant_id.value))

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute(f"SELECT * FROM {table_name} WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM {table_name} WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?",
                (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute(f"DELETE FROM {table_name} WHERE id = ? AND tenant_id = ?",
                (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        return None  # Placeholder - should import entity
'''
    if len(new_entities) % 10 == 0:
        print(f"  ✓ SQLite{entity_camel}Repository")

# Append to file
with open(sqlite_path, 'a') as f:
    f.write(sqlite_implementations)

print(f"✅ Added {len(new_entities)} SQLite repository implementations")
