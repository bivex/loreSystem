#!/usr/bin/env python3
"""
Add In-Memory implementations for Progression and Faction repositories
"""

import sys
from pathlib import Path

in_mem_path = Path("/root/clawd/src/infrastructure/in_memory_repositories.py")

# All entities (Progression + Factions)
ALL_ENTITIES = [
    "skill", "perk", "trait", "attribute", "experience", "level_up", "talent_tree", "mastery",
    "faction_hierarchy", "faction_ideology", "faction_leader", "faction_membership", "faction_resource", "faction_territory",
]

def camel_case(name):
    return ''.join(part.capitalize() for part in name.split('_'))

in_mem_repos = '''
# Progression repositories
class InMemorySkillRepository:
    def __init__(self):
        self._skills = {}
        self._next_id = 1
    def save(self, skill):
        if skill.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(skill, 'id', new_id)
        self._skills[(skill.tenant_id, skill.id)] = skill
        return skill
    def find_by_id(self, tenant_id, skill_id):
        return self._skills.get((tenant_id, skill_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._skills.values() if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, skill_id):
        if (tenant_id, skill_id) in self._skills:
            del self._skills[(tenant_id, skill_id)]
            return True
        return False

class InMemoryPerkRepository:
    def __init__(self):
        self._perks = {}
        self._next_id = 1
    def save(self, perk):
        if perk.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(perk, 'id', new_id)
        self._perks[(perk.tenant_id, perk.id)] = perk
        return perk
    def find_by_id(self, tenant_id, perk_id):
        return self._perks.get((tenant_id, perk_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [p for p in self._perks.values() if p.tenant_id == tenant_id and p.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, perk_id):
        if (tenant_id, perk_id) in self._perks:
            del self._perks[(tenant_id, perk_id)]
            return True
        return False

class InMemoryTraitRepository:
    def __init__(self):
        self._traits = {}
        self._next_id = 1
    def save(self, trait):
        if trait.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(trait, 'id', new_id)
        self._traits[(trait.tenant_id, trait.id)] = trait
        return trait
    def find_by_id(self, tenant_id, trait_id):
        return self._traits.get((tenant_id, trait_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._traits.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, trait_id):
        if (tenant_id, trait_id) in self._traits:
            del self._traits[(tenant_id, trait_id)]
            return True
        return False

class InMemoryAttributeRepository:
    def __init__(self):
        self._attributes = {}
        self._next_id = 1
    def save(self, attribute):
        if attribute.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(attribute, 'id', new_id)
        self._attributes[(attribute.tenant_id, attribute.id)] = attribute
        return attribute
    def find_by_id(self, tenant_id, attribute_id):
        return self._attributes.get((tenant_id, attribute_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [a for a in self._attributes.values() if a.tenant_id == tenant_id and a.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, attribute_id):
        if (tenant_id, attribute_id) in self._attributes:
            del self._attributes[(tenant_id, attribute_id)]
            return True
        return False

class InMemoryExperienceRepository:
    def __init__(self):
        self._experiences = {}
        self._next_id = 1
    def save(self, experience):
        if experience.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(experience, 'id', new_id)
        self._experiences[(experience.tenant_id, experience.id)] = experience
        return experience
    def find_by_id(self, tenant_id, experience_id):
        return self._experiences.get((tenant_id, experience_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._experiences.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, experience_id):
        if (tenant_id, experience_id) in self._experiences:
            del self._experiences[(tenant_id, experience_id)]
            return True
        return False

class InMemoryLevelUpRepository:
    def __init__(self):
        self._level_ups = {}
        self._next_id = 1
    def save(self, level_up):
        if level_up.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(level_up, 'id', new_id)
        self._level_ups[(level_up.tenant_id, level_up.id)] = level_up
        return level_up
    def find_by_id(self, tenant_id, level_up_id):
        return self._level_ups.get((tenant_id, level_up_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [l for l in self._level_ups.values() if l.tenant_id == tenant_id and l.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, level_up_id):
        if (tenant_id, level_up_id) in self._level_ups:
            del self._level_ups[(tenant_id, level_up_id)]
            return True
        return False

class InMemoryTalentTreeRepository:
    def __init__(self):
        self._talent_trees = {}
        self._next_id = 1
    def save(self, talent_tree):
        if talent_tree.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(talent_tree, 'id', new_id)
        self._talent_trees[(talent_tree.tenant_id, talent_tree.id)] = talent_tree
        return talent_tree
    def find_by_id(self, tenant_id, talent_tree_id):
        return self._talent_trees.get((tenant_id, talent_tree_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._talent_trees.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, talent_tree_id):
        if (tenant_id, talent_tree_id) in self._talent_trees:
            del self._talent_trees[(tenant_id, talent_tree_id)]
            return True
        return False

class InMemoryMasteryRepository:
    def __init__(self):
        self._masteries = {}
        self._next_id = 1
    def save(self, mastery):
        if mastery.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(mastery, 'id', new_id)
        self._masteries[(mastery.tenant_id, mastery.id)] = mastery
        return mastery
    def find_by_id(self, tenant_id, mastery_id):
        return self._masteries.get((tenant_id, mastery_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [m for m in self._masteries.values() if m.tenant_id == tenant_id and m.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, mastery_id):
        if (tenant_id, mastery_id) in self._masteries:
            del self._masteries[(tenant_id, mastery_id)]
            return True
        return False

# Faction repositories
class InMemoryFactionHierarchyRepository:
    def __init__(self):
        self._hierarchies = {}
        self._next_id = 1
    def save(self, hierarchy):
        if hierarchy.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(hierarchy, 'id', new_id)
        self._hierarchies[(hierarchy.tenant_id, hierarchy.id)] = hierarchy
        return hierarchy
    def find_by_id(self, tenant_id, hierarchy_id):
        return self._hierarchies.get((tenant_id, hierarchy_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [h for h in self._hierarchies.values() if h.tenant_id == tenant_id and h.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, hierarchy_id):
        if (tenant_id, hierarchy_id) in self._hierarchies:
            del self._hierarchies[(tenant_id, hierarchy_id)]
            return True
        return False

class InMemoryFactionIdeologyRepository:
    def __init__(self):
        self._ideologies = {}
        self._next_id = 1
    def save(self, ideology):
        if ideology.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(ideology, 'id', new_id)
        self._ideologies[(ideology.tenant_id, ideology.id)] = ideology
        return ideology
    def find_by_id(self, tenant_id, ideology_id):
        return self._ideologies.get((tenant_id, ideology_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [i for i in self._ideologies.values() if i.tenant_id == tenant_id and i.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, ideology_id):
        if (tenant_id, ideology_id) in self._ideologies:
            del self._ideologies[(tenant_id, ideology_id)]
            return True
        return False

class InMemoryFactionLeaderRepository:
    def __init__(self):
        self._leaders = {}
        self._next_id = 1
    def save(self, leader):
        if leader.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(leader, 'id', new_id)
        self._leaders[(leader.tenant_id, leader.id)] = leader
        return leader
    def find_by_id(self, tenant_id, leader_id):
        return self._leaders.get((tenant_id, leader_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [l for l in self._leaders.values() if l.tenant_id == tenant_id and l.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, leader_id):
        if (tenant_id, leader_id) in self._leaders:
            del self._leaders[(tenant_id, leader_id)]
            return True
        return False

class InMemoryFactionMembershipRepository:
    def __init__(self):
        self._memberships = {}
        self._next_id = 1
    def save(self, membership):
        if membership.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(membership, 'id', new_id)
        self._memberships[(membership.tenant_id, membership.id)] = membership
        return membership
    def find_by_id(self, tenant_id, membership_id):
        return self._memberships.get((tenant_id, membership_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [m for m in self._memberships.values() if m.tenant_id == tenant_id and m.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, membership_id):
        if (tenant_id, membership_id) in self._memberships:
            del self._memberships[(tenant_id, membership_id)]
            return True
        return False

class InMemoryFactionResourceRepository:
    def __init__(self):
        self._resources = {}
        self._next_id = 1
    def save(self, resource):
        if resource.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(resource, 'id', new_id)
        self._resources[(resource.tenant_id, resource.id)] = resource
        return resource
    def find_by_id(self, tenant_id, resource_id):
        return self._resources.get((tenant_id, resource_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._resources.values() if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, resource_id):
        if (tenant_id, resource_id) in self._resources:
            del self._resources[(tenant_id, resource_id)]
            return True
        return False

class InMemoryFactionTerritoryRepository:
    def __init__(self):
        self._territories = {}
        self._next_id = 1
    def save(self, territory):
        if territory.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(territory, 'id', new_id)
        self._territories[(territory.tenant_id, territory.id)] = territory
        return territory
    def find_by_id(self, tenant_id, territory_id):
        return self._territories.get((tenant_id, territory_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._territories.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, territory_id):
        if (tenant_id, territory_id) in self._territories:
            del self._territories[(tenant_id, territory_id)]
            return True
        return False
'''

# Append to file
with open(in_mem_path, 'a') as f:
    f.write(in_mem_repos)

print(f"✅ Added {len(ALL_ENTITIES)} Progression and Faction repository implementations to in_memory_repositories.py")
