#!/usr/bin/env python3
"""
Add SQLite implementations for Progression and Faction repositories
"""

from pathlib import Path

sqlite_path = Path("/root/clawd/src/infrastructure/sqlite_repositories.py")

# Progression and Faction entities
ALL_ENTITIES = [
    "skill", "perk", "trait", "attribute", "experience", "level_up", "talent_tree", "mastery",
    "faction_hierarchy", "faction_ideology", "faction_leader", "faction_membership", "faction_resource", "faction_territory",
]

def camel_case(name):
    return ''.join(part.capitalize() for part in name.split('_'))

sqlite_repos = ""
for entity in ALL_ENTITIES:
    entity_camel = camel_case(entity)
    table_name = f"{entity}s"
    
    sqlite_repos += f'''
class SQLite{entity_camel}Repository:
    """SQLite implementation of {entity_camel} repository."""
    def __init__(self, db: SQLiteDatabase):
        import sqlite3
        from datetime import datetime
        self.db = db

    def save(self, entity):
        now = datetime.now().isoformat()
        if entity.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO {table_name} (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entity.tenant_id.value,
                    entity.world_id.value if hasattr(entity, "world_id") else None,
                    entity.name,
                    getattr(entity, "description", None),
                    now, now
                ))
                object.__setattr__(entity, 'id', EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE {table_name} SET name = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    entity.name,
                    getattr(entity, "description", None),
                    entity.id.value,
                    entity.tenant_id.value
                ))
        return entity

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM {table_name} WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM {table_name} WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM {table_name} WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        from src.domain.entities.{entity} import {entity_camel}
        from src.domain.value_objects.common import Description, Timestamp
        return {entity_camel}(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )
'''

with open(sqlite_path, 'a') as f:
    f.write(sqlite_repos)

print(f"✅ Added {len(ALL_ENTITIES)} SQLite repository implementations to sqlite_repositories.py")
