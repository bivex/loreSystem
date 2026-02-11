#!/usr/bin/env python3
"""
Add final missing implementations directly to files
"""

from pathlib import Path

project_root = Path("/root/clawd")
in_mem_path = project_root / "src" / "infrastructure" / "in_memory_repositories.py"

# Add 3 In-Memory implementations
in_mem_final = """

# FINAL 3 MISSING IN-MEMORY IMPLEMENTATIONS

class InMemoryDeusExMachinaRepository:
    def __init__(self):
        self._deus_ex_machinas = {}
        self._next_id = 1
    def save(self, dem):
        if dem.id is None:
            from src.domain.value_objects.common import EntityId
            dem.id = EntityId(self._next_id)
            self._next_id += 1
        self._deus_ex_machinas[(dem.tenant_id, dem.id)] = dem
        return dem
    def find_by_id(self, tenant_id, entity_id):
        return self._deus_ex_machinas.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [d for d in self._deus_ex_machinas.values() if d.tenant_id == tenant_id and d.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._deus_ex_machinas:
            del self._deus_ex_machinas[(tenant_id, entity_id)]
            return True
        return False

class InMemoryFastTravelPointRepository:
    def __init__(self):
        self._fast_travel_points = {}
        self._next_id = 1
    def save(self, ftp):
        if ftp.id is None:
            from src.domain.value_objects.common import EntityId
            ftp.id = EntityId(self._next_id)
            self._next_id += 1
        self._fast_travel_points[(ftp.tenant_id, ftp.id)] = ftp
        return ftp
    def find_by_id(self, tenant_id, entity_id):
        return self._fast_travel_points.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [f for f in self._fast_travel_points.values() if f.tenant_id == tenant_id and f.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._fast_travel_points:
            del self._fast_travel_points[(tenant_id, entity_id)]
            return True
        return False

class InMemoryRedHerringRepository:
    def __init__(self):
        self._red_herrings = {}
        self._next_id = 1
    def save(self, rh):
        if rh.id is None:
            from src.domain.value_objects.common import EntityId
            rh.id = EntityId(self._next_id)
            self._next_id += 1
        self._red_herrings[(rh.tenant_id, rh.id)] = rh
        return rh
    def find_by_id(self, tenant_id, entity_id):
        return self._red_herrings.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._red_herrings.values() if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._red_herrings:
            del self._red_herrings[(tenant_id, entity_id)]
            return True
        return False
"""

# Append to file
with open(in_mem_path, 'a') as f:
    f.write(in_mem_final)

print("✅ Added 3 missing In-Memory implementations")
print("✅ DeusExMachina, FastTravelPoint, RedHerring added")
print()
print("=" * 80)
print("✅ 100% IMPLEMENTATIONS ACHIEVED!")
print("=" * 80)
