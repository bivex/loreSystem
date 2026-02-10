#!/usr/bin/env python3
"""
Repository Generator

Automatically generates repository interfaces and implementations for domain entities
that don't have repositories yet.
"""

import os
import sys
from pathlib import Path
from typing import Set, List, Dict
import re

# Add paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Paths
entities_dir = project_root / "src" / "domain" / "entities"
repositories_dir = project_root / "src" / "domain" / "repositories"
infrastructure_dir = project_root / "src" / "infrastructure"


class RepositoryGenerator:
    """Generate repository interfaces and implementations for domain entities."""

    def __init__(self):
        self.existing_interfaces = self._find_existing_interfaces()
        self.existing_entities = self._find_existing_entities()

    def _find_existing_interfaces(self) -> Set[str]:
        """Find all existing repository interfaces."""
        interfaces = set()
        for filepath in repositories_dir.glob("*_repository.py"):
            if not filepath.name.startswith("__"):
                with open(filepath, 'r') as f:
                    content = f.read()
                    # Find interface definitions
                    matches = re.findall(r'class\s+(I\w+Repository)\s*\([^)]*\):', content)
                    for match in matches:
                        # Extract entity name: IQuestChainRepository -> QuestChain
                        class_name = match
                        if class_name.startswith('I') and 'Repository' in class_name:
                            entity_name = class_name[1:]  # Remove I
                            entity_name = entity_name.replace('Repository', '')
                            if entity_name:  # Skip empty matches
                                interfaces.add(entity_name.lower())
        return interfaces

    def _find_existing_entities(self) -> Set[str]:
        """Find all entities with repositories."""
        entities = set()
        for filepath in repositories_dir.glob("*_repository.py"):
            if not filepath.name.startswith("__"):
                with open(filepath, 'r') as f:
                    content = f.read()
                    # Find imports
                    matches = re.findall(r'from \.\.entities\.(\w+) import', content)
                    for match in matches:
                        entities.add(match.lower())
        return entities

    def find_entities_without_repositories(self) -> List[Path]:
        """Find entities that don't have repositories."""
        entities_without = []

        for filepath in entities_dir.glob("*.py"):
            if filepath.name.startswith("__") or filepath.name == "entity.py":
                continue

            entity_name = filepath.stem.lower()
            if entity_name in self.existing_entities:
                continue

            entities_without.append(filepath)

        return sorted(entities_without, key=lambda p: p.stem)

    def generate_interface(self, entity_path: Path) -> str:
        """Generate repository interface for an entity."""
        entity_name = entity_path.stem
        entity_class = entity_name[0].upper() + entity_name[1:]  # Capitalize

        methods = [
            '    @abstractmethod\n    def save(self, entity: ' + entity_class + ') -> ' + entity_class + ':',
            '        """',
            '        Save an entity (insert or update).',
            '        ',
            '        Returns:',
            '            Saved entity with ID populated',
            '        """',
            '        pass',
            '',
            '    @abstractmethod\n    def find_by_id(',
            '        self,',
            '        tenant_id: TenantId,',
            '        entity_id: EntityId,',
            '    ) -> Optional[' + entity_class + ']:',
            '        """Find entity by ID."""',
            '        pass',
            '',
            '    @abstractmethod\n    def list_by_world(',
            '        self,',
            '        tenant_id: TenantId,',
            '        world_id: EntityId,',
            '        limit: int = 50,',
            '        offset: int = 0,',
            '    ) -> List[' + entity_class + ']:',
            '        """List all entities in a world with pagination."""',
            '        pass',
            '',
            '    @abstractmethod\n    def delete(',
            '        self,',
            '        tenant_id: TenantId,',
            '        entity_id: EntityId,',
            '    ) -> bool:',
            '        """',
            '        Delete an entity.',
            '        ',
            '        Returns:',
            '            True if deleted, False if not found',
            '        """',
            '        pass',
        ]

        interface_code = f'''"""
{entity_class} Repository Interface

Port for persisting and retrieving {entity_class} entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.{entity_name} import {entity_class}
from ..value_objects.common import TenantId, EntityId


class I{entity_class}Repository(ABC):
    """
    Repository interface for {entity_class} entity.
    
    {entity_class}s belong to Worlds (aggregate boundary).
    """
    
{chr(10).join(methods)}
'''

        return interface_code.strip()

    def generate_in_memory_repository(self, entity_path: Path) -> str:
        """Generate in-memory repository implementation."""
        entity_name = entity_path.stem
        entity_class = entity_name[0].upper() + entity_name[1:]
        interface_name = f'I{entity_class}Repository'

        methods = [
            '    def __init__(self):',
            '        self._entities: Dict[Tuple[TenantId, EntityId], {entity_class}] = {{}}',
            '        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)',
            '        self._next_id = 1',
            '',
            '    def save(self, entity: {entity_class}) -> {entity_class}:',
            '        if entity.id is None:',
            '            new_id = EntityId(self._next_id)',
            '            self._next_id += 1',
            '            object.__setattr__(entity, \'id\', new_id)',
            '',
            '        key = (entity.tenant_id, entity.id)',
            '        self._entities[key] = entity',
            '',
            '        world_key = (entity.tenant_id, entity.world_id) if hasattr(entity, \'world_id\') else None',
            '        if world_key and entity.id not in self._by_world[world_key]:',
            '            self._by_world[world_key].append(entity.id)',
            '',
            '        return entity',
            '',
            '    def find_by_id(self, tenant_id: TenantId, entity_id: EntityId) -> Optional[{entity_class}]:',
            '        return self._entities.get((tenant_id, entity_id))',
            '',
            '    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[{entity_class}]:',
            '        world_key = (tenant_id, world_id)',
            '        entity_ids = self._by_world.get(world_key, [])',
            '        entities = []',
            '        for entity_id in entity_ids[offset:offset + limit]:',
            '            entity = self._entities.get((tenant_id, entity_id))',
            '            if entity:',
            '                entities.append(entity)',
            '        return entities',
            '',
            '    def delete(self, tenant_id: TenantId, entity_id: EntityId) -> bool:',
            '        key = (tenant_id, entity_id)',
            '        if key not in self._entities:',
            '            return False',
            '',
            '        entity = self._entities[key]',
            '        world_key = (entity.tenant_id, entity.world_id) if hasattr(entity, \'world_id\') else None',
            '        if world_key and entity_id in self._by_world[world_key]:',
            '            self._by_world[world_key].remove(entity_id)',
            '',
            '        del self._entities[key]',
            '        return True',
        ]

        repository_code = f'''"""
In-Memory {entity_class} Repository Implementation

In-memory implementation of {interface_name} for testing purposes.
"""
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from src.domain.entities.{entity_name} import {entity_class}
from src.domain.repositories.{entity_name}_repository import {interface_name}
from src.domain.value_objects.common import TenantId, EntityId
from src.domain.exceptions import DuplicateEntity


class InMemory{entity_class}Repository({interface_name}):
    """
    In-memory implementation of {entity_class} repository for testing.
    
    Stores {entity_name}s in memory using dictionaries for fast access.
    """

{chr(10).join(methods)}
'''

        return repository_code.strip()

    def generate_sqlite_repository(self, entity_path: Path) -> str:
        """Generate SQLite repository implementation."""
        entity_name = entity_path.stem
        entity_class = entity_name[0].upper() + entity_name[1:]
        interface_name = f'I{entity_class}Repository'
        table_name = f"{entity_name.lower()}s"

        methods = [
            '    def __init__(self, db: SQLiteDatabase):',
            '        self.db = db',
            '',
            '    def save(self, entity: {entity_class}) -> {entity_class}:',
            '        now = datetime.now().isoformat()',
            '',
            '        if entity.id is None:',
            '            with self.db.get_connection() as conn:',
            '                cursor = conn.execute("""',
            f'                    INSERT INTO {table_name} (tenant_id, world_id, name, description, created_at, updated_at)',
            '                    VALUES (?, ?, ?, ?, ?, ?)',
            '                """, (',
            '                    entity.tenant_id.value,',
            '                    entity.world_id.value if hasattr(entity, "world_id") else None,',
            '                    entity.name,',
            '                    getattr(entity, "description", None),',
            '                    now,',
            '                    now',
            '                ))',
            '                entity_id = cursor.lastrowid',
            '                object.__setattr__(entity, \'id\', EntityId(entity_id))',
            '        else:',
            '            with self.db.get_connection() as conn:',
            '                conn.execute("""',
            f'                    UPDATE {table_name}',
            '                    SET name = ?, description = ?',
            '                    WHERE id = ? AND tenant_id = ?',
            '                """, (',
            '                    entity.name,',
            '                    getattr(entity, "description", None),',
            '                    entity.id.value,',
            '                    entity.tenant_id.value,',
            '                ))',
            '',
            '        return entity',
            '',
            '    def find_by_id(self, tenant_id: TenantId, entity_id: EntityId) -> Optional[{entity_class}]:',
            '        with self.db.get_connection() as conn:',
            '            row = conn.execute("""',
            f'                    SELECT * FROM {table_name} WHERE id = ? AND tenant_id = ?',
            '                """, (entity_id.value, tenant_id.value)).fetchone()',
            '',
            '            if not row:',
            '                return None',
            '            return self._row_to_entity(row)',
            '',
            '    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[{entity_class}]:',
            '        with self.db.get_connection() as conn:',
            '            rows = conn.execute("""',
            f'                    SELECT * FROM {table_name} WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?',
            '                """, (world_id.value, tenant_id.value, limit, offset)).fetchall()',
            '            return [self._row_to_entity(row) for row in rows]',
            '',
            '    def delete(self, tenant_id: TenantId, entity_id: EntityId) -> bool:',
            '        with self.db.get_connection() as conn:',
            '            cursor = conn.execute("""',
            f'                    DELETE FROM {table_name} WHERE id = ? AND tenant_id = ?',
            '                """, (entity_id.value, tenant_id.value))',
            '            return cursor.rowcount > 0',
            '',
            f'    def _row_to_entity(self, row: sqlite3.Row) -> {entity_class}:',
            '        from src.domain.value_objects.common import Description',
            '',
            f'        return {entity_class}(',
            '            tenant_id=TenantId(row[\'tenant_id\']),',
            '            world_id=EntityId(row[\'world_id\']) if row[\'world_id\'] else None,',
            '            name=row[\'name\'],',
            '            description=Description(row[\'description\']) if row[\'description\'] else None,',
            '            created_at=Timestamp(datetime.fromisoformat(row[\'created_at\'])),',
            '            updated_at=Timestamp(datetime.fromisoformat(row[\'updated_at\'])),',
            '            id=EntityId(row[\'id\'])',
            '        )',
        ]

        repository_code = f'''"""
SQLite {entity_class} Repository Implementation

SQLite implementation of {interface_name} for production use.
"""
import sqlite3
from datetime import datetime
from typing import Optional, List

from src.domain.entities.{entity_name} import {entity_class}
from src.domain.repositories.{entity_name}_repository import {interface_name}
from src.domain.value_objects.common import TenantId, EntityId, Timestamp
from src.infrastructure.sqlite_repositories import SQLiteDatabase


class SQLite{entity_class}Repository({interface_name}):
    """
    SQLite implementation of {entity_class} repository for production use.
    """

{chr(10).join(methods)}
'''

        return repository_code.strip()

    def generate_sql_table_schema(self, entity_path: Path) -> str:
        """Generate SQL CREATE TABLE statement for an entity."""
        entity_name = entity_path.stem
        table_name = f"{entity_name.lower()}s"

        schema = f'''            # {entity_name} table
            conn.execute("""
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
            """)'''

        return schema.strip()

    def generate_all(self):
        """Generate repositories for all entities without repos."""
        entities_without = self.find_entities_without_repositories()

        print(f"\nFound {len(entities_without)} entities without repositories:")
        for entity_path in entities_without:
            print(f"  - {entity_path.stem}")

        if not entities_without:
            print("\nNo entities found without repositories. All set!")
            return

        output = {
            'interfaces': {},
            'in_memory': {},
            'sqlite': {},
            'schema_tables': {},
        }

        # Generate for each entity
        for entity_path in entities_without:
            entity_name = entity_path.stem

            # Generate interface
            interface_code = self.generate_interface(entity_path)
            interface_path = repositories_dir / f"{entity_name}_repository.py"
            interface_path.write_text(interface_code)
            output['interfaces'][entity_name] = f"{entity_name}_repository"

            # Generate in-memory repo
            in_memory_code = self.generate_in_memory_repository(entity_path)
            output['in_memory'][entity_name] = f"InMemory{entity_name}Repository"

            # Generate SQLite repo
            sqlite_code = self.generate_sqlite_repository(entity_path)
            output['sqlite'][entity_name] = f"SQLite{entity_name}Repository"

            # Generate schema
            schema_code = self.generate_sql_table_schema(entity_path)
            output['schema_tables'][entity_name] = schema_code

        # Generate updates for existing files
        self._generate_imports_update(output)
        self._generate_sqlite_schema_update(output)
        self._generate_server_update(output)

        print(f"\nGenerated repositories for {len(entities_without)} entities")
        print("Files created:")
        print(f"  - {len(output['interfaces'])} interface files")
        print(f"  - Need to add to in_memory_repositories.py")
        print(f"  - Need to add to sqlite_repositories.py")
        print(f"  - Need to add to server.py")

    def _generate_imports_update(self, output: Dict):
        """Generate code to add to in_memory_repositories.py imports."""
        import_lines = []
        for entity_name, class_name in sorted(output['interfaces'].items()):
            import_lines.append(f"from src.domain.repositories.{entity_name}_repository import I{entity_name}Repository")

        code = f"""
# Auto-generated imports for new repositories
{chr(10).join(import_lines)}
"""
        print(f"\n=== Add to in_memory_repositories.py imports ===\n{code}")

    def _generate_sqlite_schema_update(self, output: Dict):
        """Generate code to add to SQLite schema."""
        schema_code = f"""
# Auto-generated SQL table schemas
{chr(10).join(sorted(output['schema_tables'].values()))}
"""
        print(f"\n=== Add to sqlite_repositories.py in initialize_schema() ===\n{schema_code}")

    def _generate_server_update(self, output: Dict):
        """Generate code to add to server.py."""
        import_lines = []
        class_names = sorted(output['sqlite'].items())
        for entity_name, class_name in class_names:
            import_lines.append(f"    {class_name},")
            import_lines.append(f"    InMemory{entity_name}Repository,")

        code = f"""
# Auto-generated repository instances
# Add to imports:
from src.infrastructure.sqlite_repositories import (
{chr(10).join([f"    {class_name}," for class_name in class_names])}
from src.infrastructure.in_memory_repositories import (
{chr(10).join([f"    InMemory{entity_name}Repository," for entity_name in class_names])}
)

# Add to repository initialization (for SQLite section):
{chr(10).join([f"    {entity_name}_repo = SQLite{entity_name}Repository(sqlite_db)" for entity_name in output['interfaces'].keys()])}

# Add to repository initialization (for in-memory section):
{chr(10).join([f"    {entity_name}_repo = InMemory{entity_name}Repository()" for entity_name in output['interfaces'].keys()])}
"""
        print(f"\n=== Add to server.py repository initialization ===\n{code}")


def main():
    """Run the repository generator."""
    print("=" * 80)
    print("REPOSITORY GENERATOR")
    print("=" * 80)
    print()

    generator = RepositoryGenerator()
    generator.generate_all()

    print("\n" + "=" * 80)
    print("Done! Follow the instructions above to integrate generated code.")
    print("=" * 80)


if __name__ == "__main__":
    main()
