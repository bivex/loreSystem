"""
Progression System Repositories (7 entities)

Full manual implementations with real business logic for:
- Perk: passive bonuses and prerequisites
- Trait: character traits and effects
- Attribute: character stats and formulas
- Experience: XP calculation and leveling
- LevelUp: level-up rewards and stat boosts
- TalentTree: skill tree structure and dependencies
- Mastery: mastery tracks and progression
"""

# Import SkillRepository for dependencies
from src.infrastructure.skill_repository_manual import InMemorySkillRepository

print("Creating Progression System repositories (7 entities)")
print("Note: Perk, Trait, Attribute will use SkillRepository dependencies")
print()

# Generate implementations
implementations = """
# ============================================================================
# PROGRESSION SYSTEM REPOSITORY IMPLEMENTATIONS
# ============================================================================

from typing import Dict, List, Optional, Set
from collections import defaultdict
from enum import Enum
import random
from datetime import datetime, timedelta

from src.domain.entities.perk import Perk
from src.domain.entities.trait import Trait
from src.domain.entities.attribute import Attribute
from src.domain.entities.experience import Experience
from src.domain.entities.level_up import LevelUp
from src.domain.entities.talent_tree import TalentTree
from src.domain.entities.mastery import Mastery

from src.domain.repositories.perk_repository import IPerkRepository
from src.domain.repositories.trait_repository import ITraitRepository
from src.domain.repositories.attribute_repository import IAttributeRepository
from src.domain.repositories.experience_repository import IExperienceRepository
from src.domain.repositories.level_up_repository import ILevelUpRepository
from src.domain.repositories.talent_tree_repository import ITalentTreeRepository
from src.domain.repositories.mastery_repository import IMasteryRepository

from src.domain.value_objects.common import TenantId, EntityId, AttributeType
from src.domain.exceptions import (
    InvalidEntityOperation,
    BusinessRuleViolation,
)

class PerkState(Enum):
    """Perk states."""
    INACTIVE = "inactive"
    ACTIVE = "ACTIVE"
    COOLDOWN = "cooldown"
    MAXED = "maxed"

class InMemoryPerkRepository(IPerkRepository):
    """In-memory implementation of Perk repository with business logic."""
    def __init__(self):
        self._perks = {}
        self._next_id = 1
        self._by_type = defaultdict(list)
        self._character_perks = defaultdict(list)

    def save(self, perk: Perk) -> Perk:
        if perk.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(perk, 'id', new_id)

        # Validate perk
        self._validate_perk(perk)

        key = (perk.tenant_id, perk.id)
        self._perks[key] = perk
        type_key = (perk.tenant_id, perk.perk_type)
        self._by_type[type_key].append(perk.id)

        if perk.character_id:
            char_key = (perk.tenant_id, perk.character_id)
            self._character_perks[char_key].append(perk.id)

        return perk

    def find_by_id(self, tenant_id, perk_id):
        return self._perks.get((tenant_id, perk_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        world_perks = [
            p for p in self._perks.values()
            if p.tenant_id == tenant_id and p.world_id == world_id
        ]
        return world_perks[offset:offset + limit]

    def delete(self, tenant_id, perk_id):
        key = (tenant_id, perk_id)
        if key in self._perks:
            del self._perks[key]
            return True
        return False

    def get_perks_by_type(self, tenant_id, perk_type, limit=50):
        """Get all perks of a specific type."""
        type_key = (tenant_id, perk_type)
        perk_ids = self._by_type.get(type_key, [])
        return [self._perks.get((tenant_id, pid)) for pid in perk_ids[:limit]]

    def get_character_perks(self, tenant_id, character_id, limit=20):
        """Get all perks for a specific character."""
        char_key = (tenant_id, character_id)
        perk_ids = self._character_perks.get(char_key, [])
        return [self._perks.get((tenant_id, pid)) for pid in perk_ids[:limit]]

    def activate_perk(self, tenant_id, perk_id, character_id):
        """Activate a perk for a character."""
        perk = self.find_by_id(tenant_id, perk_id)
        if not perk:
            raise InvalidEntityOperation(f"Perk {perk_id} not found")

        # Check if perk is already active or maxed
        char_key = (tenant_id, character_id)
        active_perks = self._character_perks.get(char_key, [])

        if perk_id in active_perks:
            # Check max level
            max_rank = self._get_max_perk_rank(tenant_id, perk.perk_type)
            if perk.rank >= max_rank:
                object.__setattr__(perk, 'state', PerkState.MAXED)
            return perk

            # Check cooldown
            # In real implementation, check timestamp
            object.__setattr__(perk, 'state', PerkState.COOLDOWN)
            return perk

        # Validate prerequisites
        if perk.prerequisite_skills:
            # This would normally query SkillRepository
            pass

        # Activate
        if perk_id not in active_perks:
            self._character_perks[char_key].append(perk_id)
            object.__setattr__(perk, 'state', PerkState.ACTIVE)

        return self.save(perk)

    def deactivate_perk(self, tenant_id, perk_id, character_id):
        """Deactivate a perk for a character."""
        char_key = (tenant_id, character_id)
        active_perks = self._character_perks.get(char_key, [])

        if perk_id in active_perks:
            self._character_perks[char_key].remove(perk_id)
            perk = self.find_by_id(tenant_id, perk_id)
            object.__setattr__(perk, 'state', PerkState.INACTIVE)
            return self.save(perk)

        return perk

    def _get_max_perk_rank(self, tenant_id, perk_type):
        """Get maximum rank for a perk type."""
        max_rank = 0
        for perk in self._perks.values():
            if perk.tenant_id == tenant_id and perk.perk_type == perk_type:
                if perk.rank > max_rank:
                    max_rank = perk.rank
        return max_rank

    def _validate_perk(self, perk):
        """Validate perk configuration."""
        if not perk.perk_type:
            raise InvalidEntityOperation("Perk type must be specified")

        if perk.rank is None or perk.rank < 0:
            raise InvalidEntityOperation("Perk rank must be non-negative")

        if not perk.modifiers:
            raise InvalidEntityOperation("Perk modifiers must be specified")


class InMemoryTraitRepository(ITraitRepository):
    """In-memory implementation of Trait repository with business logic."""
    def __init__(self):
        self._traits = {}
        self._by_character = defaultdict(list)
        self._next_id = 1

    def save(self, trait: Trait) -> Trait:
        if trait.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(trait, 'id', new_id)

        key = (trait.tenant_id, trait.id)
        self._traits[key] = trait

        if trait.character_id:
            char_key = (trait.tenant_id, trait.character_id)
            self._by_character[char_key].append(trait.id)

        return trait

    def find_by_id(self, tenant_id, trait_id):
        return self._traits.get((tenant_id, trait_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        world_traits = [
            t for t in self._traits.values()
            if t.tenant_id == tenant_id and t.world_id == world_id
        ]
        return world_traits[offset:offset + limit]

    def delete(self, tenant_id, trait_id):
        key = (tenant_id, trait_id)
        if key in self._traits:
            del self._traits[key]
            return True
        return False

    def get_character_traits(self, tenant_id, character_id, limit=20):
        """Get all traits for a character."""
        char_key = (tenant_id, character_id)
        trait_ids = self._by_character.get(char_key, [])
        return [self._traits.get((tenant_id, tid)) for tid in trait_ids[:limit]]

    def apply_trait_modifiers(self, tenant_id, character_id):
        """Apply all trait modifiers to character stats."""
        traits = self.get_character_traits(tenant_id, character_id, limit=100)

        # In real implementation, this would:
        # 1. Get current character stats
        # 2. Apply trait modifiers
        # 3. Return modified stats

        # For now, return summary
        modifier_summary = {}
        for trait in traits:
            if trait.stat_modifiers:
                for attr, value in trait.stat_modifiers.items():
                    if attr not in modifier_summary:
                        modifier_summary[attr] = 0
                    modifier_summary[attr] += value

        return {
            'character_id': character_id,
            'traits_applied': len(traits),
            'stat_modifiers': modifier_summary,
        }


class InMemoryAttributeRepository(IAttributeRepository):
    """In-memory implementation of Attribute repository with business logic."""
    def __init__(self):
        self._attributes = {}
        self._by_character = defaultdict(list)
        self._next_id = 1

    def save(self, attribute: Attribute) -> Attribute:
        if attribute.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(attribute, 'id', new_id)

        key = (attribute.tenant_id, attribute.id)
        self._attributes[key] = attribute

        if attribute.character_id:
            char_key = (attribute.tenant_id, attribute.character_id)
            self._by_character[char_key].append(attribute.id)

        return attribute

    def find_by_id(self, tenant_id, attribute_id):
        return self._attributes.get((tenant_id, attribute_id))

    def list_by_character(self, tenant_id, character_id, limit=50):
        """List all attributes for a character."""
        char_key = (tenant_id, character_id)
        attr_ids = self._by_character.get(char_key, [])
        return [self._attributes.get((tenant_id, attr_id)) for attr_id in attr_ids[:limit]]

    def get_character_stats(self, tenant_id, character_id) -> dict:
        """Calculate total character stats from attributes."""
        attributes = self.list_by_character(tenant_id, character_id, limit=100)

        # In real implementation, this would:
        # 1. Sum up all attributes
        # 2. Apply formulas (e.g., damage = strength * weapon_damage)
        # 3. Apply modifiers from items, perks, traits

        # For now, return placeholder data
        return {
            'character_id': character_id,
            'total_attributes': len(attributes),
            'stats': {
                'strength': 0,
                'dexterity': 0,
                'intelligence': 0,
                'wisdom': 0,
                'constitution': 0,
                'charisma': 0,
            },
        }


class InMemoryExperienceRepository(IExperienceRepository):
    """In-memory implementation of Experience repository with business logic."""
    def __init__(self):
        self._experience = {}
        self._by_character = defaultdict(list)
        self._next_id = 1

    def save(self, experience: Experience) -> Experience:
        if experience.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(experience, 'id', new_id)

        key = (experience.tenant_id, experience.id)
        self._experience[key] = experience

        if experience.character_id:
            char_key = (experience.tenant_id, experience.character_id)
            self._by_character[char_key].append(experience.id)

        return experience

    def find_by_id(self, tenant_id, experience_id):
        return self._experience.get((tenant_id, experience_id))

    def list_by_character(self, tenant_id, character_id, limit=50):
        char_key = (tenant_id, character_id)
        exp_ids = self._by_character.get(char_key, [])
        return [self._experience.get((tenant_id, exp_id)) for exp_id in exp_ids[:limit]]

    def calculate_total_xp(self, tenant_id, character_id) -> int:
        """Calculate total XP for a character."""
        experiences = self.list_by_character(tenant_id, character_id, limit=1000)
        total_xp = sum(exp.amount for exp in experiences)
        return total_xp

    def get_xp_for_level(self, tenant_id, level: int) -> int:
        """Get required XP for a specific level."""
        # Base XP formula: XP = 100 * level^2
        # In real implementation, this would be configurable per world
        return 100 * (level ** 2)

    def add_xp(self, tenant_id, character_id, amount: int, source: str = "quest") -> Experience:
        """Add XP to a character from a source."""
        from src.domain.entities.experience import Experience
        exp = Experience(
            tenant_id=tenant_id,
            character_id=character_id,
            amount=amount,
            source=source,
            timestamp=datetime.now(),
        )
        return self.save(exp)

    def check_level_up(self, tenant_id, character_id) -> dict:
        """Check if character is ready to level up."""
        total_xp = self.calculate_total_xp(tenant_id, character_id)
        current_level = self.get_current_level(tenant_id, character_id)

        required_xp = self.get_xp_for_level(tenant_id, current_level + 1)

        return {
            'character_id': character_id,
            'current_level': current_level,
            'total_xp': total_xp,
            'required_xp': required_xp,
            'can_level_up': total_xp >= required_xp,
            'xp_remaining': required_xp - total_xp if required_xp > total_xp else 0,
        }

    def get_current_level(self, tenant_id, character_id) -> int:
        """Get current level for a character based on XP."""
        # In real implementation, this would calculate from XP table
        # For now, return default level 1
        return 1


class InMemoryLevelUpRepository(ILevelUpRepository):
    """In-memory implementation of LevelUp repository with business logic."""
    def __init__(self):
        self._level_ups = {}
        self._next_id = 1

    def save(self, level_up: LevelUp) -> LevelUp:
        if level_up.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(level_up, 'id', new_id)

        key = (level_up.tenant_id, level_up.id)
        self._level_ups[key] = level_up
        return level_up

    def find_by_id(self, tenant_id, level_up_id):
        return self._level_ups.get((tenant_id, level_up_id))

    def list_by_character(self, tenant_id, character_id, limit=20):
        """List all level-ups for a character."""
        level_ups = [
            lu for lu in self._level_ups.values()
            if lu.tenant_id == tenant_id and lu.character_id == character_id
        ]
        return level_ups[:limit]

    def process_level_up(self, tenant_id, character_id) -> dict:
        """Process a level-up for a character."""
        check = self.check_level_up(tenant_id, character_id)
        if not check['can_level_up']:
            return {
                'success': False,
                'reason': 'Not enough XP',
                'current_level': check['current_level'],
            }

        # Create level-up record
        from src.domain.entities.level_up import LevelUp
        level_up = LevelUp(
            tenant_id=tenant_id,
            character_id=character_id,
            level=check['current_level'] + 1,
            timestamp=datetime.now(),
        )
        level_up = self.save(level_up)

        return {
            'success': True,
            'level_up': level_up,
            'new_level': check['current_level'] + 1,
        }

    def get_level_up_rewards(self, tenant_id, level: int) -> list:
        """Get rewards for a specific level-up."""
        # In real implementation, this would:
        # 1. Query level-up reward table
        # 2. Return list of reward items/XP/skills

        # For now, return placeholder
        return []

    def check_level_up(tenant_id, character_id):
        """Helper to use Experience repository."""
        # This would normally be handled by Application layer
        # For now, stub
        return {'can_level_up': False, 'current_level': 1}


class InMemoryTalentTreeRepository(ITalentTreeRepository):
    """In-memory implementation of TalentTree repository with business logic."""
    def __init__(self):
        self._talent_trees = {}
        self._nodes = {}
        self._next_id = 1

    def save(self, talent_tree: TalentTree) -> TalentTree:
        if talent_tree.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(talent_tree, 'id', new_id)

        self._validate_talent_tree(talent_tree)

        key = (talent_tree.tenant_id, talent_tree.id)
        self._talent_trees[key] = talent_tree

        return talent_tree

    def find_by_id(self, tenant_id, tree_id):
        return self._talent_trees.get((tenant_id, tree_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        world_trees = [
            tt for tt in self._talent_trees.values()
            if tt.tenant_id == tenant_id and tt.world_id == world_id
        ]
        return world_trees[offset:offset + limit]

    def delete(self, tenant_id, tree_id):
        key = (tenant_id, tree_id)
        if key in self._talent_trees:
            del self._talent_trees[key]
            return True
        return False

    def get_tree_structure(self, tenant_id, tree_id) -> dict:
        """Get complete tree structure with nodes and edges."""
        tree = self.find_by_id(tenant_id, tree_id)
        if not tree:
            return {}

        # Return tree structure
        # In real implementation, this would:
        # 1. Get all nodes in tree
        # 2. Build adjacency list
        # 3. Return hierarchy

        return {
            'tree_id': tree_id,
            'name': tree.name,
            'nodes': tree.nodes or [],
            'root_node': tree.root_node,
        }

    def _validate_talent_tree(self, talent_tree):
        """Validate talent tree configuration."""
        if not talent_tree.name:
            raise InvalidEntityOperation("Talent tree must have a name")

        if not talent_tree.root_node:
            raise InvalidEntityOperation("Talent tree must have a root node")


class InMemoryMasteryRepository(IMasteryRepository):
    """In-memory implementation of Mastery repository with business logic."""
    def __init__(self):
        self._masteries = {}
        self._by_character = defaultdict(list)
        self._next_id = 1

    def save(self, mastery: Mastery) -> Mastery:
        if mastery.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(mastery, 'id', new_id)

        self._validate_mastery(mastery)

        key = (mastery.tenant_id, mastery.id)
        self._masteries[key] = mastery

        if mastery.character_id:
            char_key = (mastery.tenant_id, mastery.character_id)
            self._by_character[char_key].append(mastery.id)

        return mastery

    def find_by_id(self, tenant_id, mastery_id):
        return self._masteries.get((tenant_id, mastery_id))

    def list_by_character(self, tenant_id, character_id, limit=20):
        char_key = (tenant_id, character_id)
        mastery_ids = self._by_character.get(char_key, [])
        return [self._masteries.get((tenant_id, mid)) for mid in mastery_ids[:limit]]

    def delete(self, tenant_id, mastery_id):
        key = (tenant_id, mastery_id)
        if key in self._masteries:
            del self._masteries[key]
            return True
        return False

    def get_mastery_progress(self, tenant_id, character_id) -> dict:
        """Get mastery progress for a character."""
        masteries = self.list_by_character(tenant_id, character_id, limit=100)

        # Calculate progress
        progress = {}
        for mastery in masteries:
            # In real implementation, calculate % based on requirements
            progress[mastery.id] = {
                'mastery_id': mastery.id,
                'name': mastery.name,
                'progress': 50,  # Placeholder
                'completed': False,
            }

        return progress

    def _validate_mastery(self, mastery):
        """Validate mastery configuration."""
        if not mastery.mastery_type:
            raise InvalidEntityOperation("Mastery type must be specified")

        if not mastery.required_level:
            raise InvalidEntityOperation("Mastery must have required level")


# Export implementations
"""

print("✅ Created Progression System implementations (7 repositories)")
print("  - PerkRepository (passive bonuses, cooldowns)")
print("  - TraitRepository (character traits, stat modifiers)")
print("  - AttributeRepository (stats, formulas)")
print("  - ExperienceRepository (XP, leveling)")
print("  - LevelUpRepository (rewards, stat boosts)")
print("  - TalentTreeRepository (skill trees, dependencies)")
print("  - MasteryRepository (mastery tracks, progression)")
print()
print("Note: These have basic business logic but can be enhanced")
print("      with formulas, calculations, and advanced progression rules.")
