#!/usr/bin/env python3
"""
Add ALL In-Memory repository implementations for 230 new entities
"""

import sys
from pathlib import Path

in_mem_path = Path("/root/clawd/src/infrastructure/in_memory_repositories.py")
repos_dir = Path("/root/clawd/src/domain/repositories")

# Get all new interface files
new_entities = []
for filepath in repos_dir.glob("*_repository.py"):
    if filepath.name.startswith("__"):
        continue
    
    entity_name = filepath.stem.replace("_repository", "")
    
    # Check if already has In-Memory implementation
    with open(in_mem_path, 'r') as f:
        content = f.read()
        if f"InMemory{entity_name[0].upper()}{entity_name[1:]}Repository" in content:
            continue
    
    new_entities.append(entity_name)

print(f"Found {len(new_entities)} entities without In-Memory implementations")
print()

# Read current file
content = in_mem_path.read_text()

# Find end of last repository class
# Simple approach: just append all repositories at the end
implementations = "\n# In-Memory implementations for remaining repositories\n\n"

for entity in new_entities:
    entity_camel = entity[0].upper() + entity[1:]
    implementations += f'''
class InMemory{entity_camel}Repository:
    """In-memory implementation of {entity_camel} repository."""
    def __init__(self):
        self._entities = {{}}
        self._next_id = 1

    def save(self, entity):
        if entity.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(entity, 'id', new_id)
        self._entities[(entity.tenant_id, entity.id)] = entity
        return entity

    def find_by_id(self, tenant_id, entity_id):
        from src.domain.value_objects.common import EntityId
        return self._entities.get((EntityId(tenant_id), EntityId(entity_id)))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        from src.domain.value_objects.common import EntityId
        return [e for e in self._entities.values()
                if e.tenant_id == EntityId(tenant_id)
                and getattr(e, 'world_id', None) == EntityId(world_id)][offset:offset+limit]

    def delete(self, tenant_id, entity_id):
        from src.domain.value_objects.common import EntityId
        key = (EntityId(tenant_id), EntityId(entity_id))
        if key in self._entities:
            del self._entities[key]
            return True
        return False
'''

content += implementations

with open(in_mem_path, 'a') as f:
    f.write(content)

print(f"✅ Added {len(new_entities)} In-Memory implementations")
print()
print(f"Total In-Memory implementations: {len(content.split('class InMemory')) - 29 existing = {len(new_entities)} + 29")
