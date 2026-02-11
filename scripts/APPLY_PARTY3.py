#!/usr/bin/env python3
"""
Apply Party 3: Social/Religion + Locations + Inventory/Crafting (36 repos)
"""

from pathlib import Path

project_root = Path("/root/clawd")
in_mem_path = project_root / "src" / "infrastructure" / "in_memory_repositories.py"

print("=" * 80)
print("APPLYING PARTY 3 - SOCIAL/RELIGION + LOCATIONS + INVENTORY/CRAFTING (36 repos)")
print("=" * 80)
print()
print("Social/Religion (17):")
print("  - Reputation, Affinity, Disposition, Honor, Karma")
print("  - SocialClass, SocialMobility")
print("  - Cult, Sect, HolySite, Scripture, Ritual, Oath")
print("  - Summon, Pact, Curse, Blessing")
print()
print("Locations (10):")
print("  - HubArea, Instance, Dungeon, Raid, Arena")
print("  - OpenWorldZone, Underground, Skybox, Dimension, PocketDimension")
print()
print("Inventory/Crafting (9):")
print("  - Inventory, CraftingRecipe, Material, Component")
print("  - Blueprint, Enchantment, Socket, Rune, Glyph")
print()
print("Creating 36 repository implementations with basic business logic...")
print("=" * 80)
print()

# Create implementations for all 36 repos
party3_repos = """
# ============================================================================
# PARTY 3: SOCIAL/RELIGION + LOCATIONS + INVENTORY/CRAFTING (36 repos)
# ============================================================================

# Social Relations Repositories (7)
class InMemoryReputationRepository:
    def __init__(self):
        self._reputations = {}
        self._next_id = 1
    def save(self, reputation):
        if reputation.id is None:
            from src.domain.value_objects.common import EntityId
            reputation.id = EntityId(self._next_id)
            self._next_id += 1
        self._reputations[(reputation.tenant_id, reputation.id)] = reputation
        return reputation
    def find_by_id(self, tenant_id, entity_id):
        return self._reputations.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._reputations.values() 
                if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._reputations:
            del self._reputations[(tenant_id, entity_id)]
            return True
        return False

class InMemoryAffinityRepository:
    def __init__(self):
        self._affinities = {}
        self._next_id = 1
    def save(self, affinity):
        if affinity.id is None:
            from src.domain.value_objects.common import EntityId
            affinity.id = EntityId(self._next_id)
            self._next_id += 1
        self._affinities[(affinity.tenant_id, affinity.id)] = affinity
        return affinity
    def find_by_id(self, tenant_id, entity_id):
        return self._affinities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [a for a in self._affinities.values() 
                if a.tenant_id == tenant_id and a.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._affinities:
            del self._affinities[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDispositionRepository:
    def __init__(self):
        self._dispositions = {}
        self._next_id = 1
    def save(self, disposition):
        if disposition.id is None:
            from src.domain.value_objects.common import EntityId
            disposition.id = EntityId(self._next_id)
            self._next_id += 1
        self._dispositions[(disposition.tenant_id, disposition.id)] = disposition
        return disposition
    def find_by_id(self, tenant_id, entity_id):
        return self._dispositions.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [d for d in self._dispositions.values() 
                if d.tenant_id == tenant_id and d.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._dispositions:
            del self._dispositions[(tenant_id, entity_id)]
            return True
        return False

class InMemoryHonorRepository:
    def __init__(self):
        self._honor = {}
        self._next_id = 1
    def save(self, honor):
        if honor.id is None:
            from src.domain.value_objects.common import EntityId
            honor.id = EntityId(self._next_id)
            self._next_id += 1
        self._honor[(honor.tenant_id, honor.id)] = honor
        return honor
    def find_by_id(self, tenant_id, entity_id):
        return self._honor.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [h for h in self._honor.values() 
                if h.tenant_id == tenant_id and h.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._honor:
            del self._honor[(tenant_id, entity_id)]
            return True
        return False

class InMemoryKarmaRepository:
    def __init__(self):
        self._karmas = {}
        self._next_id = 1
    def save(self, karma):
        if karma.id is None:
            from src.domain.value_objects.common import EntityId
            karma.id = EntityId(self._next_id)
            self._next_id += 1
        self._karmas[(karma.tenant_id, karma.id)] = karma
        return karma
    def find_by_id(self, tenant_id, entity_id):
        return self._karmas.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [k for k in self._karmas.values() 
                if k.tenant_id == tenant_id and k.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._karmas:
            del self._karmas[(tenant_id, entity_id)]
            return True
        return False

class InMemorySocialClassRepository:
    def __init__(self):
        self._social_classes = {}
        self._next_id = 1
    def save(self, social_class):
        if social_class.id is None:
            from src.domain.value_objects.common import EntityId
            social_class.id = EntityId(self._next_id)
            self._next_id += 1
        self._social_classes[(social_class.tenant_id, social_class.id)] = social_class
        return social_class
    def find_by_id(self, tenant_id, entity_id):
        return self._social_classes.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [sc for sc in self._social_classes.values() 
                if sc.tenant_id == tenant_id and sc.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._social_classes:
            del self._social_classes[(tenant_id, entity_id)]
            return True
        return False

class InMemorySocialMobilityRepository:
    def __init__(self):
        self._mobilities = {}
        self._next_id = 1
    def save(self, mobility):
        if mobility.id is None:
            from src.domain.value_objects.common import EntityId
            mobility.id = EntityId(self._next_id)
            self._next_id += 1
        self._mobilities[(mobility.tenant_id, mobility.id)] = mobility
        return mobility
    def find_by_id(self, tenant_id, entity_id):
        return self._mobilities.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [m for m in self._mobilities.values() 
                if m.tenant_id == tenant_id and m.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._mobilities:
            del self._mobilities[(tenant_id, entity_id)]
            return True
        return False

# Religion/Mysticism Repositories (10)
class InMemoryCultRepository:
    def __init__(self):
        self._cults = {}
        self._next_id = 1
    def save(self, cult):
        if cult.id is None:
            from src.domain.value_objects.common import EntityId
            cult.id = EntityId(self._next_id)
            self._next_id += 1
        self._cults[(cult.tenant_id, cult.id)] = cult
        return cult
    def find_by_id(self, tenant_id, entity_id):
        return self._cults.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [c for c in self._cults.values() 
                if c.tenant_id == tenant_id and c.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._cults:
            del self._cults[(tenant_id, entity_id)]
            return True
        return False

class InMemorySectRepository:
    def __init__(self):
        self._sects = {}
        self._next_id = 1
    def save(self, sect):
        if sect.id is None:
            from src.domain.value_objects.common import EntityId
            sect.id = EntityId(self._next_id)
            self._next_id += 1
        self._sects[(sect.tenant_id, sect.id)] = sect
        return sect
    def find_by_id(self, tenant_id, entity_id):
        return self._sects.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._sects.values() 
                if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._sects:
            del self._sects[(tenant_id, entity_id)]
            return True
        return False

class InMemoryHolySiteRepository:
    def __init__(self):
        self._holy_sites = {}
        self._next_id = 1
    def save(self, holy_site):
        if holy_site.id is None:
            from src.domain.value_objects.common import EntityId
            holy_site.id = EntityId(self._next_id)
            self._next_id += 1
        self._holy_sites[(holy_site.tenant_id, holy_site.id)] = holy_site
        return holy_site
    def find_by_id(self, tenant_id, entity_id):
        return self._holy_sites.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [hs for hs in self._holy_sites.values() 
                if hs.tenant_id == tenant_id and hs.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._holy_sites:
            del self._holy_sites[(tenant_id, entity_id)]
            return True
        return False

class InMemoryScriptureRepository:
    def __init__(self):
        self._scriptures = {}
        self._next_id = 1
    def save(self, scripture):
        if scripture.id is None:
            from src.domain.value_objects.common import EntityId
            scripture.id = EntityId(self._next_id)
            self._next_id += 1
        self._scriptures[(scripture.tenant_id, scripture.id)] = scripture
        return scripture
    def find_by_id(self, tenant_id, entity_id):
        return self._scriptures.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._scriptures.values() 
                if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._scriptures:
            del self._scriptures[(tenant_id, entity_id)]
            return True
        return False

class InMemoryRitualRepository:
    def __init__(self):
        self._rituals = {}
        self._next_id = 1
    def save(self, ritual):
        if ritual.id is None:
            from src.domain.value_objects.common import EntityId
            ritual.id = EntityId(self._next_id)
            self._next_id += 1
        self._rituals[(ritual.tenant_id, ritual.id)] = ritual
        return ritual
    def find_by_id(self, tenant_id, entity_id):
        return self._rituals.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._rituals.values() 
                if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._rituals:
            del self._rituals[(tenant_id, entity_id)]
            return True
        return False

class InMemoryOathRepository:
    def __init__(self):
        self._oaths = {}
        self._next_id = 1
    def save(self, oath):
        if oath.id is None:
            from src.domain.value_objects.common import EntityId
            oath.id = EntityId(self._next_id)
            self._next_id += 1
        self._oaths[(oath.tenant_id, oath.id)] = oath
        return oath
    def find_by_id(self, tenant_id, entity_id):
        return self._oaths.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [o for o in self._oaths.values() 
                if o.tenant_id == tenant_id and o.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._oaths:
            del self._oaths[(tenant_id, entity_id)]
            return True
        return False

class InMemorySummonRepository:
    def __init__(self):
        self._summons = {}
        self._next_id = 1
    def save(self, summon):
        if summon.id is None:
            from src.domain.value_objects.common import EntityId
            summon.id = EntityId(self._next_id)
            self._next_id += 1
        self._summons[(summon.tenant_id, summon.id)] = summon
        return summon
    def find_by_id(self, tenant_id, entity_id):
        return self._summons.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._summons.values() 
                if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._summons:
            del self._summons[(tenant_id, entity_id)]
            return True
        return False

class InMemoryPactRepository:
    def __init__(self):
        self._pacts = {}
        self._next_id = 1
    def save(self, pact):
        if pact.id is None:
            from src.domain.value_objects.common import EntityId
            pact.id = EntityId(self._next_id)
            self._next_id += 1
        self._pacts[(pact.tenant_id, pact.id)] = pact
        return pact
    def find_by_id(self, tenant_id, entity_id):
        return self._pacts.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [p for p in self._pacts.values() 
                if p.tenant_id == tenant_id and p.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._pacts:
            del self._pacts[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCurseRepository:
    def __init__(self):
        self._curses = {}
        self._next_id = 1
    def save(self, curse):
        if curse.id is None:
            from src.domain.value_objects.common import EntityId
            curse.id = EntityId(self._next_id)
            self._next_id += 1
        self._curses[(curse.tenant_id, curse.id)] = curse
        return curse
    def find_by_id(self, tenant_id, entity_id):
        return self._curses.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [c for c in self._curses.values() 
                if c.tenant_id == tenant_id and c.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._curses:
            del self._curses[(tenant_id, entity_id)]
            return True
        return False

class InMemoryBlessingRepository:
    def __init__(self):
        self._blessings = {}
        self._next_id = 1
    def save(self, blessing):
        if blessing.id is None:
            from src.domain.value_objects.common import EntityId
            blessing.id = EntityId(self._next_id)
            self._next_id += 1
        self._blessings[(blessing.tenant_id, blessing.id)] = blessing
        return blessing
    def find_by_id(self, tenant_id, entity_id):
        return self._blessings.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [b for b in self._blessings.values() 
                if b.tenant_id == tenant_id and b.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._blessings:
            del self._blessings[(tenant_id, entity_id)]
            return True
        return False

# Locations Repositories (10)
class InMemoryHubAreaRepository:
    def __init__(self):
        self._hub_areas = {}
        self._next_id = 1
    def save(self, hub_area):
        if hub_area.id is None:
            from src.domain.value_objects.common import EntityId
            hub_area.id = EntityId(self._next_id)
            self._next_id += 1
        self._hub_areas[(hub_area.tenant_id, hub_area.id)] = hub_area
        return hub_area
    def find_by_id(self, tenant_id, entity_id):
        return self._hub_areas.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [h for h in self._hub_areas.values() 
                if h.tenant_id == tenant_id and h.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._hub_areas:
            del self._hub_areas[(tenant_id, entity_id)]
            return True
        return False

class InMemoryInstanceRepository:
    def __init__(self):
        self._instances = {}
        self._next_id = 1
    def save(self, instance):
        if instance.id is None:
            from src.domain.value_objects.common import EntityId
            instance.id = EntityId(self._next_id)
            self._next_id += 1
        self._instances[(instance.tenant_id, instance.id)] = instance
        return instance
    def find_by_id(self, tenant_id, entity_id):
        return self._instances.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [i for i in self._instances.values() 
                if i.tenant_id == tenant_id and i.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._instances:
            del self._instances[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDungeonRepository:
    def __init__(self):
        self._dungeons = {}
        self._next_id = 1
    def save(self, dungeon):
        if dungeon.id is None:
            from src.domain.value_objects.common import EntityId
            dungeon.id = EntityId(self._next_id)
            self._next_id += 1
        self._dungeons[(dungeon.tenant_id, dungeon.id)] = dungeon
        return dungeon
    def find_by_id(self, tenant_id, entity_id):
        return self._dungeons.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [d for d in self._dungeons.values() 
                if d.tenant_id == tenant_id and d.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._dungeons:
            del self._dungeons[(tenant_id, entity_id)]
            return True
        return False

class InMemoryRaidRepository:
    def __init__(self):
        self._raids = {}
        self._next_id = 1
    def save(self, raid):
        if raid.id is None:
            from src.domain.value_objects.common import EntityId
            raid.id = EntityId(self._next_id)
            self._next_id += 1
        self._raids[(raid.tenant_id, raid.id)] = raid
        return raid
    def find_by_id(self, tenant_id, entity_id):
        return self._raids.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._raids.values() 
                if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._raids:
            del self._raids[(tenant_id, entity_id)]
            return True
        return False

class InMemoryArenaRepository:
    def __init__(self):
        self._arenas = {}
        self._next_id = 1
    def save(self, arena):
        if arena.id is None:
            from src.domain.value_objects.common import EntityId
            arena.id = EntityId(self._next_id)
            self._next_id += 1
        self._arenas[(arena.tenant_id, arena.id)] = arena
        return arena
    def find_by_id(self, tenant_id, entity_id):
        return self._arenas.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [a for a in self._arenas.values() 
                if a.tenant_id == tenant_id and a.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._arenas:
            del self._arenas[(tenant_id, entity_id)]
            return True
        return False

class InMemoryOpenWorldZoneRepository:
    def __init__(self):
        self._open_world_zones = {}
        self._next_id = 1
    def save(self, open_world_zone):
        if open_world_zone.id is None:
            from src.domain.value_objects.common import EntityId
            open_world_zone.id = EntityId(self._next_id)
            self._next_id += 1
        self._open_world_zones[(open_world_zone.tenant_id, open_world_zone.id)] = open_world_zone
        return open_world_zone
    def find_by_id(self, tenant_id, entity_id):
        return self._open_world_zones.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [o for o in self._open_world_zones.values() 
                if o.tenant_id == tenant_id and o.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._open_world_zones:
            del self._open_world_zones[(tenant_id, entity_id)]
            return True
        return False

class InMemoryUndergroundRepository:
    def __init__(self):
        self._undergrounds = {}
        self._next_id = 1
    def save(self, underground):
        if underground.id is None:
            from src.domain.value_objects.common import EntityId
            underground.id = EntityId(self._next_id)
            self._next_id += 1
        self._undergrounds[(underground.tenant_id, underground.id)] = underground
        return underground
    def find_by_id(self, tenant_id, entity_id):
        return self._undergrounds.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [u for u in self._undergrounds.values() 
                if u.tenant_id == tenant_id and u.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._undergrounds:
            del self._undergrounds[(tenant_id, entity_id)]
            return True
        return False

class InMemorySkyboxRepository:
    def __init__(self):
        self._skyboxes = {}
        self._next_id = 1
    def save(self, skybox):
        if skybox.id is None:
            from src.domain.value_objects.common import EntityId
            skybox.id = EntityId(self._next_id)
            self._next_id += 1
        self._skyboxes[(skybox.tenant_id, skybox.id)] = skybox
        return skybox
    def find_by_id(self, tenant_id, entity_id):
        return self._skyboxes.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._skyboxes.values() 
                if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._skyboxes:
            del self._skyboxes[(tenant_id, entity_id)]
            return True
        return False

class InMemoryDimensionRepository:
    def __init__(self):
        self._dimensions = {}
        self._next_id = 1
    def save(self, dimension):
        if dimension.id is None:
            from src.domain.value_objects.common import EntityId
            dimension.id = EntityId(self._next_id)
            self._next_id += 1
        self._dimensions[(dimension.tenant_id, dimension.id)] = dimension
        return dimension
    def find_by_id(self, tenant_id, entity_id):
        return self._dimensions.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [d for d in self._dimensions.values() 
                if d.tenant_id == tenant_id and d.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._dimensions:
            del self._dimensions[(tenant_id, entity_id)]
            return True
        return False

class InMemoryPocketDimensionRepository:
    def __init__(self):
        self._pocket_dimensions = {}
        self._next_id = 1
    def save(self, pocket_dimension):
        if pocket_dimension.id is None:
            from src.domain.value_objects.common import EntityId
            pocket_dimension.id = EntityId(self._next_id)
            self._next_id += 1
        self._pocket_dimensions[(pocket_dimension.tenant_id, pocket_dimension.id)] = pocket_dimension
        return pocket_dimension
    def find_by_id(self, tenant_id, entity_id):
        return self._pocket_dimensions.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [p for p in self._pocket_dimensions.values() 
                if p.tenant_id == tenant_id and p.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._pocket_dimensions:
            del self._pocket_dimensions[(tenant_id, entity_id)]
            return True
        return False

# Inventory/Crafting Repositories (9)
class InMemoryInventoryRepository:
    def __init__(self):
        self._inventories = {}
        self._next_id = 1
    def save(self, inventory):
        if inventory.id is None:
            from src.domain.value_objects.common import EntityId
            inventory.id = EntityId(self._next_id)
            self._next_id += 1
        self._inventories[(inventory.tenant_id, inventory.id)] = inventory
        return inventory
    def find_by_id(self, tenant_id, entity_id):
        return self._inventories.get((tenant_id, entity_id))
    def list_by_character(self, tenant_id, character_id, limit=50, offset=0):
        return [i for i in self._inventories.values() 
                if i.tenant_id == tenant_id and i.character_id == character_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._inventories:
            del self._inventories[(tenant_id, entity_id)]
            return True
        return False

class InMemoryCraftingRecipeRepository:
    def __init__(self):
        self._recipes = {}
        self._next_id = 1
    def save(self, recipe):
        if recipe.id is None:
            from src.domain.value_objects.common import EntityId
            recipe.id = EntityId(self._next_id)
            self._next_id += 1
        self._recipes[(recipe.tenant_id, recipe.id)] = recipe
        return recipe
    def find_by_id(self, tenant_id, entity_id):
        return self._recipes.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._recipes.values() 
                if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._recipes:
            del self._recipes[(tenant_id, entity_id)]
            return True
        return False

class InMemoryMaterialRepository:
    def __init__(self):
        self._materials = {}
        self._next_id = 1
    def save(self, material):
        if material.id is None:
            from src.domain.value_objects.common import EntityId
            material.id = EntityId(self._next_id)
            self._next_id += 1
        self._materials[(material.tenant_id, material.id)] = material
        return material
    def find_by_id(self, tenant_id, entity_id):
        return self._materials.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [m for m in self._materials.values() 
                if m.tenant_id == tenant_id and m.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._materials:
            del self._materials[(tenant_id, entity_id)]
            return True
        return False

class InMemoryComponentRepository:
    def __init__(self):
        self._components = {}
        self._next_id = 1
    def save(self, component):
        if component.id is None:
            from src.domain.value_objects.common import EntityId
            component.id = EntityId(self._next_id)
            self._next_id += 1
        self._components[(component.tenant_id, component.id)] = component
        return component
    def find_by_id(self, tenant_id, entity_id):
        return self._components.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [c for c in self._components.values() 
                if c.tenant_id == tenant_id and c.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._components:
            del self._components[(tenant_id, entity_id)]
            return True
        return False

class InMemoryBlueprintRepository:
    def __init__(self):
        self._blueprints = {}
        self._next_id = 1
    def save(self, blueprint):
        if blueprint.id is None:
            from src.domain.value_objects.common import EntityId
            blueprint.id = EntityId(self._next_id)
            self._next_id += 1
        self._blueprints[(blueprint.tenant_id, blueprint.id)] = blueprint
        return blueprint
    def find_by_id(self, tenant_id, entity_id):
        return self._blueprints.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [b for b in self._blueprints.values() 
                if b.tenant_id == tenant_id and b.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._blueprints:
            del self._blueprints[(tenant_id, entity_id)]
            return True
        return False

class InMemoryEnchantmentRepository:
    def __init__(self):
        self._enchantments = {}
        self._next_id = 1
    def save(self, enchantment):
        if enchantment.id is None:
            from src.domain.value_objects.common import EntityId
            enchantment.id = EntityId(self._next_id)
            self._next_id += 1
        self._enchantments[(enchantment.tenant_id, enchantment.id)] = enchantment
        return enchantment
    def find_by_id(self, tenant_id, entity_id):
        return self._enchantments.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._enchantments.values() 
                if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._enchantments:
            del self._enchantments[(tenant_id, entity_id)]
            return True
        return False

class InMemorySocketRepository:
    def __init__(self):
        self._sockets = {}
        self._next_id = 1
    def save(self, socket):
        if socket.id is None:
            from src.domain.value_objects.common import EntityId
            socket.id = EntityId(self._next_id)
            self._next_id += 1
        self._sockets[(socket.tenant_id, socket.id)] = socket
        return socket
    def find_by_id(self, tenant_id, entity_id):
        return self._sockets.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._sockets.values() 
                if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._sockets:
            del self._sockets[(tenant_id, entity_id)]
            return True
        return False

class InMemoryRuneRepository:
    def __init__(self):
        self._runes = {}
        self._next_id = 1
    def save(self, rune):
        if rune.id is None:
            from src.domain.value_objects.common import EntityId
            rune.id = EntityId(self._next_id)
            self._next_id += 1
        self._runes[(rune.tenant_id, rune.id)] = rune
        return rune
    def find_by_id(self, tenant_id, entity_id):
        return self._runes.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._runes.values() 
                if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._runes:
            del self._runes[(tenant_id, entity_id)]
            return True
        return False

class InMemoryGlyphRepository:
    def __init__(self):
        self._glyphs = {}
        self._next_id = 1
    def save(self, glyph):
        if glyph.id is None:
            from src.domain.value_objects.common import EntityId
            glyph.id = EntityId(self._next_id)
            self._next_id += 1
        self._glyphs[(glyph.tenant_id, glyph.id)] = glyph
        return glyph
    def find_by_id(self, tenant_id, entity_id):
        return self._glyphs.get((tenant_id, entity_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [g for g in self._glyphs.values() 
                if g.tenant_id == tenant_id and g.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, entity_id):
        if (tenant_id, entity_id) in self._glyphs:
            del self._glyphs[(tenant_id, entity_id)]
            return True
        return False
"""

# Append to in_memory_repositories.py
with open(in_mem_path, 'a') as f:
    f.write(party3_repos)

print("✅ Created Party 3 implementations (36 repos)")
print()
print("Summary:")
print("  - Social/Religion: 17 repositories")
print("    Reputation, Affinity, Disposition, Honor, Karma")
print("    SocialClass, SocialMobility")
print("    Cult, Sect, HolySite, Scripture, Ritual, Oath")
print("    Summon, Pact, Curse, Blessing")
print("  - Locations: 10 repositories")
print("    HubArea, Instance, Dungeon, Raid, Arena")
print("    OpenWorldZone, Underground, Skybox, Dimension, PocketDimension")
print("  - Inventory/Crafting: 9 repositories")
print("    Inventory, CraftingRecipe, Material, Component, Blueprint")
print("    Enchantment, Socket, Rune, Glyph")
print()
print("Total: 36 new repositories")
print("Party 3 Complete: 22 + 53 + 36 = 111 repositories")
print()
print("=" * 80)
print("PARTY 3 - READY")
print("=" * 80)
print()
print("Next steps:")
print("  1. Check status: python3 check_repositories.py")
print("  2. Commit: git add -A && git commit -m 'feat: Add Party 3 repos'")
print("  3. Push: git push origin master")
