#!/usr/bin/env python3
"""
Progression System Repositories (8 entities) - Fixed version
"""

import sys
from pathlib import Path

project_root = Path("/root/clawd")
prog_dir = project_root / "src" / "infrastructure" / "progression_system"

# Create progression_system directory
prog_dir.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("CREATING PROGRESSION SYSTEM REPOSITORIES (FIXED)")
print("=" * 80)
print()
print("This creates 8 repository implementations with basic business logic:")
print("  - Skill: skill definitions and requirements")
print("  - Perk: passive bonuses and prerequisites")
print("  - Trait: character traits and effects")
print("  - Attribute: character stats and formulas")
print("  - Experience: XP calculation and leveling")
print("  - LevelUp: level-up rewards and stat boosts")
print("  - TalentTree: skill tree structure and dependencies")
print("  - Mastery: mastery tracks and progression")
print()
print("Note: These are basic CRUD implementations.")
print("      Full algorithms will be added in next iteration.")
print("=" * 80)
print()

# Create simple implementations
implementations = """

# Skill Repository
class InMemorySkillRepository:
    def __init__(self):
        self._skills = {}
        self._next_id = 1
    def save(self, skill):
        if skill.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(skill, 'id', new_id)
        self._skills[(skill.tenant_id, skill.id)] = skill
        return skill
    def find_by_id(self, tenant_id, skill_id):
        return self._skills.get((tenant_id, skill_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._skills.values() 
                if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, skill_id):
        if (tenant_id, skill_id) in self._skills:
            del self._skills[(tenant_id, skill_id)]
            return True
        return False

# Perk Repository
class InMemoryPerkRepository:
    def __init__(self):
        self._perks = {}
        self._next_id = 1
    def save(self, perk):
        if perk.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(perk, 'id', new_id)
        self._perks[(perk.tenant_id, perk.id)] = perk
        return perk
    def find_by_id(self, tenant_id, perk_id):
        return self._perks.get((tenant_id, perk_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [p for p in self._perks.values() 
                if p.tenant_id == tenant_id and p.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, perk_id):
        if (tenant_id, perk_id) in self._perks:
            del self._perks[(tenant_id, perk_id)]
            return True
        return False

# Trait Repository
class InMemoryTraitRepository:
    def __init__(self):
        self._traits = {}
        self._next_id = 1
    def save(self, trait):
        if trait.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(trait, 'id', new_id)
        self._traits[(trait.tenant_id, trait.id)] = trait
        return trait
    def find_by_id(self, tenant_id, trait_id):
        return self._traits.get((tenant_id, trait_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._traits.values() 
                if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, trait_id):
        if (tenant_id, trait_id) in self._traits:
            del self._traits[(tenant_id, trait_id)]
            return True
        return False

# Attribute Repository
class InMemoryAttributeRepository:
    def __init__(self):
        self._attributes = {}
        self._next_id = 1
    def save(self, attribute):
        if attribute.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(attribute, 'id', new_id)
        self._attributes[(attribute.tenant_id, attribute.id)] = attribute
        return attribute
    def find_by_id(self, tenant_id, attribute_id):
        return self._attributes.get((tenant_id, attribute_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [a for a in self._attributes.values() 
                if a.tenant_id == tenant_id and a.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, attribute_id):
        if (tenant_id, attribute_id) in self._attributes:
            del self._attributes[(tenant_id, attribute_id)]
            return True
        return False

# Experience Repository
class InMemoryExperienceRepository:
    def __init__(self):
        self._experience = {}
        self._next_id = 1
    def save(self, experience):
        if experience.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(experience, 'id', new_id)
        self._experience[(experience.tenant_id, experience.id)] = experience
        return experience
    def find_by_id(self, tenant_id, experience_id):
        return self._experience.get((tenant_id, experience_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._experience.values() 
                if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, experience_id):
        if (tenant_id, experience_id) in self._experience:
            del self._experience[(tenant_id, experience_id)]
            return True
        return False

# LevelUp Repository
class InMemoryLevelUpRepository:
    def __init__(self):
        self._level_ups = {}
        self._next_id = 1
    def save(self, level_up):
        if level_up.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(level_up, 'id', new_id)
        self._level_ups[(level_up.tenant_id, level_up.id)] = level_up
        return level_up
    def find_by_id(self, tenant_id, level_up_id):
        return self._level_ups.get((tenant_id, level_up_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [l for l in self._level_ups.values() 
                if l.tenant_id == tenant_id and l.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, level_up_id):
        if (tenant_id, level_up_id) in self._level_ups:
            del self._level_ups[(tenant_id, level_up_id)]
            return True
        return False

# TalentTree Repository
class InMemoryTalentTreeRepository:
    def __init__(self):
        self._talent_trees = {}
        self._next_id = 1
    def save(self, talent_tree):
        if talent_tree.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(talent_tree, 'id', new_id)
        self._talent_trees[(talent_tree.tenant_id, talent_tree.id)] = talent_tree
        return talent_tree
    def find_by_id(self, tenant_id, talent_tree_id):
        return self._talent_trees.get((tenant_id, talent_tree_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [tt for tt in self._talent_trees.values() 
                if tt.tenant_id == tenant_id and tt.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, talent_tree_id):
        if (tenant_id, talent_tree_id) in self._talent_trees:
            del self._talent_trees[(tenant_id, talent_tree_id)]
            return True
        return False

# Mastery Repository
class InMemoryMasteryRepository:
    def __init__(self):
        self._masteries = {}
        self._next_id = 1
    def save(self, mastery):
        if mastery.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(mastery, 'id', new_id)
        self._masteries[(mastery.tenant_id, mastery.id)] = mastery
        return mastery
    def find_by_id(self, tenant_id, mastery_id):
        return self._masteries.get((tenant_id, mastery_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [m for m in self._masteries.values() 
                if m.tenant_id == tenant_id and m.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, mastery_id):
        if (tenant_id, mastery_id) in self._masteries:
            del self._masteries[(tenant_id, mastery_id)]
            return True
        return False
"""

# Append to in_memory_repositories.py
in_mem_path = project_root / "src" / "infrastructure" / "in_memory_repositories.py"
with open(in_mem_path, 'a') as f:
    f.write(implementations)

print()
print("✅ Created Progression System repositories (8 implementations)")
print()
print("Summary:")
print("  - Skill: skill definitions and requirements")
print("  - Perk: passive bonuses and prerequisites")
print("  - Trait: character traits and effects")
print("  - Attribute: character stats and formulas")
print("  - Experience: XP calculation and leveling")
print("  - LevelUp: level-up rewards and stat boosts")
print("  - TalentTree: skill tree structure and dependencies")
print("  - Mastery: mastery tracks and progression")
print()
print("=" * 80)
print("PROGRESSION SYSTEM - READY")
print("=" * 80)
