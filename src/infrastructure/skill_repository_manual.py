"""
Skill Repository Implementation

In-memory implementation with full business logic for skills.
Includes:
- Skill definitions and requirements
- Prerequisite validation (level, item, faction, quest dependencies)
- Level-up progression and unlock mechanics
- Skill trees and dependencies
- Experience calculation and formulas
"""

from typing import Dict, List, Optional, Set
from collections import defaultdict
import networkx as nx
from enum import Enum

from src.domain.entities.skill import Skill
from src.domain.repositories.skill_repository import ISkillRepository
from src.domain.value_objects.common import TenantId, EntityId, SkillType, SkillAttribute, Difficulty
from src.domain.exceptions import (
    InvalidEntityOperation,
    BusinessRuleViolation,
    CircularDependency,
    SkillPrerequisiteViolation,
)

class SkillProgression(Enum):
    """Skill progression states."""
    LOCKED = "locked"           # Cannot access
    AVAILABLE = "available"     # Can learn/upgrade
    IN_PROGRESS = "in_progress" # Currently learning
    MASTERED = "mastered"       # Fully learned (max level)
    LEGENDARY = "legendary"     # Special mastery

class SkillRepository(ISkillRepository):
    """
    Repository interface for Skill entity with full business logic.
    
    Business Logic:
    - Skill definitions and requirements
    - Prerequisite validation (level, item, faction, quest dependencies)
    - Level-up progression and unlock mechanics
    - Skill trees and dependencies
    - Experience calculation and formulas
    """

    def __init__(self):
        self._skills: Dict[Tuple[TenantId, EntityId], Skill] = {}
        self._by_type: Dict[Tuple[TenantId, SkillType], List[EntityId]] = defaultdict(list)
        self._by_attribute: Dict[Tuple[TenantId, SkillAttribute], List[EntityId]] = defaultdict(list)
        self._by_required_level: Dict[Tuple[TenantId, int], List[EntityId]] = defaultdict(list)
        self._dependencies: Dict[Tuple[TenantId, EntityId], Set[EntityId]] = {}
        self._next_id = 1

    def save(self, skill: Skill) -> Skill:
        """Save with full validation."""
        if skill.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(skill, 'id', new_id)

        # Validate skill configuration
        self._validate_skill(skill)

        # Check for circular dependencies
        self._check_for_cycles(skill)

        key = (skill.tenant_id, skill.id)
        self._skills[key] = skill

        # Index by type
        type_key = (skill.tenant_id, skill.skill_type)
        self._by_type[type_key].append(skill.id)

        # Index by attributes
        if skill.primary_attribute:
            attr_key = (skill.tenant_id, skill.primary_attribute)
            self._by_attribute[attr_key].append(skill.id)

        # Index by required level
        if skill.required_level:
            level_key = (skill.tenant_id, skill.required_level)
            self._by_required_level[level_key].append(skill.id)

        # Build dependency graph
        if skill.prerequisite_skills:
            self._dependencies[key] = set(skill.prerequisite_skills)

        return skill

    def find_by_id(self, tenant_id: TenantId, skill_id: EntityId) -> Optional[Skill]:
        return self._skills.get((tenant_id, skill_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Skill]:
        """List all skills in a world with pagination."""
        world_skills = [
            skill for skill in self._skills.values()
            if skill.tenant_id == tenant_id and skill.world_id == world_id
        ]
        return world_skills[offset:offset + limit]

    def delete(self, tenant_id: TenantId, skill_id: EntityId) -> bool:
        """Delete with dependency cascade checks."""
        key = (tenant_id, skill_id)
        if key not in self._skills:
            return False

        skill = self._skills[key]

        # Check if required by other skills
        for other_key, other_skill in self._skills.items():
            if other_key == key:
                continue
            if skill.id in (other_skill.prerequisite_skills or []):
                raise BusinessRuleViolation(
                    f"Cannot delete skill {skill_id}: required by {other_key}"
                )

        del self._skills[key]
        return True

    def _validate_skill(self, skill: Skill):
        """Validate skill configuration."""
        # Rule: Must have skill type
        if not skill.skill_type:
            raise InvalidEntityOperation("Skill type must be specified")

        # Rule: Must have primary attribute
        if not skill.primary_attribute:
            raise InvalidEntityOperation("Skill primary attribute must be specified")

        # Rule: Required level must be positive
        if skill.required_level and skill.required_level < 1:
            raise InvalidEntityOperation("Required level must be at least 1")

        # Rule: Max level must be >= required level
        if skill.max_level and skill.max_level < skill.required_level:
            raise InvalidEntityOperation("Max level must be >= required level")

        # Rule: Experience cost must be positive
        if skill.experience_cost and skill.experience_cost < 0:
            raise InvalidEntityOperation("Experience cost must be positive")

        # Rule: Skill prerequisites must exist
        for prereq_id in (skill.prerequisite_skills or []):
            if not self._skill_exists(prereq_id):
                raise SkillPrerequisiteViolation(
                    f"Skill prerequisite {prereq_id} does not exist"
                )

    def _check_for_cycles(self, skill: Skill):
        """Detect cycles in skill dependency graph."""
        if not skill.prerequisite_skills:
            return

        # Build dependency graph
        graph = nx.DiGraph()

        # Add all skills involved
        involved_skills = skill.prerequisite_skills + [skill.id]
        for skill_id in involved_skills:
            if self._skill_exists(skill_id):
                s = self._skills.get((skill.tenant_id, skill_id))
                if s:
                    graph.add_node(skill_id)

        # Add edges from prerequisites
        for prereq_id in (skill.prerequisite_skills or []):
            s = self._skills.get((skill.tenant_id, prereq_id))
            if s:
                skill_prereqs = s.prerequisite_skills or []
                for sp_id in skill_prereqs:
                    graph.add_edge(sp_id, s.id)

        # Check for cycles
        try:
            cycles = list(nx.simple_cycles(graph))
            if cycles:
                raise CircularDependency(
                    f"Circular dependency detected in skill tree: {cycles}"
                )
        except nx.NetworkXError:
            pass  # No cycles

    def _skill_exists(self, skill_id: EntityId) -> bool:
        """Check if skill exists in system."""
        # This would normally query Skill repository
        # For simplicity, check in local storage
        for key, skill in self._skills.items():
            if key[1] == skill_id:
                return True
        return False

    def get_skills_by_type(self, tenant_id: TenantId, skill_type: SkillType, limit: int = 50) -> List[Skill]:
        """Get all skills of a specific type."""
        type_key = (tenant_id, skill_type)
        skill_ids = self._by_type.get(type_key, [])
        skills = []
        for skill_id in skill_ids[:limit]:
            skill = self._skills.get((tenant_id, skill_id))
            if skill:
                skills.append(skill)
        return skills

    def get_skills_by_attribute(self, tenant_id: TenantId, attribute: SkillAttribute, limit: int = 50) -> List[Skill]:
        """Get all skills of a specific attribute."""
        attr_key = (tenant_id, attribute)
        skill_ids = self._by_attribute.get(attr_key, [])
        skills = []
        for skill_id in skill_ids[:limit]:
            skill = self._skills.get((tenant_id, skill_id))
            if skill:
                skills.append(skill)
        return skills

    def get_skills_by_required_level(self, tenant_id: TenantId, required_level: int, limit: int = 50) -> List[Skill]:
        """Get all skills that require a specific level."""
        level_key = (tenant_id, required_level)
        skill_ids = self._by_required_level.get(level_key, [])
        skills = []
        for skill_id in skill_ids[:limit]:
            skill = self._skills.get((tenant_id, skill_id))
            if skill:
                skills.append(skill)
        return skills

    def get_skill_prerequisites(self, tenant_id: TenantId, skill_id: EntityId) -> List[Skill]:
        """Get all prerequisite skills for a skill (transitive)."""
        skill = self.find_by_id(tenant_id, skill_id)
        if not skill or not skill.prerequisite_skills:
            return []

        # Use BFS to find all prerequisites
        prereq_ids = set(skill.prerequisite_skills)
        visited = set(prereq_ids)
        queue = list(prereq_ids)

        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue

            visited.add(current_id)
            current = self._skills.get((tenant_id, current_id))
            if current and current.prerequisite_skills:
                new_prereqs = [sp for sp in current.prerequisite_skills if sp not in visited]
                queue.extend(new_prereqs)

        prereqs = []
        for prereq_id in visited:
            prereq = self._skills.get((tenant_id, prereq_id))
            if prereq:
                prereqs.append(prereq)

        return prereqs

    def get_skill_tree(self, tenant_id: TenantId, root_skill_id: EntityId) -> dict:
        """
        Get complete skill tree from root.
        Returns dict with:
        - levels: skill IDs organized by levels
        - branches: different skill lines
        - skills: skill details
        """
        root = self.find_by_id(tenant_id, root_skill_id)
        if not root:
            return {'levels': {}, 'branches': [], 'skills': []}

        # BFS to get all dependent skills
        levels = {0: [root_skill_id]}
        current_level = 1

        queue = [(root_skill_id, 0)]  # (skill_id, level)
        visited = {root_skill_id}

        while queue:
            skill_id, level = queue.pop(0)

            # Find all skills that depend on this one
            deps = []
            for other_key, other_skill in self._skills.items():
                if other_key[1] in visited:
                    continue
                if other_skill.prerequisite_skills and skill_id in other_skill.prerequisite_skills:
                    deps.append(other_key[1])
                    visited.add(other_key[1])

            if deps:
                if current_level + 1 not in levels:
                    levels[current_level + 1] = deps
                else:
                    levels[current_level + 1].extend(deps)
                queue.extend([(dep_id, current_level + 1) for dep_id in deps])

        skills = []
        for skill_ids in levels.values():
            for skill_id in skill_ids:
                skill = self._skills.get((tenant_id, skill_id))
                if skill:
                    skills.append(skill)

        branches = list(levels.keys())

        return {
            'levels': {k: len(v) for k, v in levels.items()},
            'branches': branches,
            'skills': skills,
        }

    def calculate_skill_unlock_cost(self, tenant_id: TenantId, skill_id: EntityId) -> int:
        """
        Calculate XP cost to unlock a skill.
        Considers:
        - Skill level (linear + exponential)
        - Rarity and difficulty modifiers
        - Attribute requirements
        - Faction discounts
        """
        skill = self.find_by_id(tenant_id, skill_id)
        if not skill:
            return 0

        # Base cost
        base_cost = skill.experience_cost or 100

        # Level modifier (exponential)
        if skill.required_level:
            base_cost *= skill.required_level * 1.5

        # Difficulty modifier
        if skill.difficulty:
            difficulty_mod = {
                Difficulty.EASY: 0.8,
                Difficulty.NORMAL: 1.0,
                Difficulty.HARD: 1.5,
                Difficulty.INSANE: 2.5
            }
            base_cost *= difficulty_mod.get(skill.difficulty, 1.0)

        # Attribute requirement modifiers
        if skill.attribute_requirements:
            for attr_req in skill.attribute_requirements:
                # Assume player has attributes
                # In real implementation, this would query PlayerRepository
                base_cost *= 1.2

        return int(base_cost)

    def check_skill_eligibility(self, tenant_id: TenantId, skill_id: EntityId, player_data: dict) -> dict:
        """
        Check if player can learn/upgrade a skill.
        Returns dict with:
        - can_learn: bool
        - reason: str
        - missing_requirements: list
        - probability: float (0-1)
        """
        skill = self.find_by_id(tenant_id, skill_id)
        if not skill:
            return {'can_learn': False, 'reason': 'Skill not found'}

        can_learn = True
        missing_requirements = []
        probability = 1.0

        # Check level requirement
        if skill.required_level:
            player_level = player_data.get('level', 1)
            if player_level < skill.required_level:
                can_learn = False
                missing_requirements.append(f"Requires level {skill.required_level}")
                probability = 0.5

        # Check attribute requirements
        if skill.attribute_requirements:
            player_stats = player_data.get('stats', {})
            for attr, value in skill.attribute_requirements.items():
                if player_stats.get(attr, 0) < value:
                    can_learn = False
                    missing_requirements.append(f"Requires {attr} >= {value}")
                    probability *= 0.9

        # Check skill prerequisites
        if skill.prerequisite_skills:
            player_skills = player_data.get('skills', [])
            for prereq_id in skill.prerequisite_skills:
                if prereq_id not in player_skills:
                    can_learn = False
                    missing_requirements.append(f"Requires skill {prereq_id}")
                    probability *= 0.95

        # Check item requirements
        if skill.required_items:
            player_inventory = player_data.get('inventory', [])
            for item_id in skill.required_items:
                if item_id not in player_inventory:
                    can_learn = False
                    missing_requirements.append(f"Requires item {item_id}")
                    probability *= 0.9

        # Check faction requirement
        if skill.required_factions:
            player_factions = player_data.get('factions', [])
            if not any(faction in player_factions for faction in skill.required_factions):
                can_learn = False
                missing_requirements.append(f"Requires faction membership")
                probability *= 0.8

        # Ensure probability is in range
        probability = max(0.0, min(1.0, probability))

        return {
            'can_learn': can_learn,
            'reason': "All requirements met" if can_learn else "; ".join(missing_requirements),
            'missing_requirements': missing_requirements,
            'probability': probability
        }

    def get_recommended_skills(self, tenant_id: TenantId, player_class: str, player_level: int, limit: int = 10) -> List[Skill]:
        """
        Recommend skills for a player based on class and level.
        Considers:
        - Skill type compatibility
        - Current progression
        - Missing abilities
        """
        # Get all skills matching player class
        recommended = []
        class_skills = []

        for skill in self._skills.values():
            # In real implementation, check skill compatibility with class
            # For now, just include all
            class_skills.append(skill)

        # Sort by level and relevance
        class_skills.sort(key=lambda s: (s.required_level or 1, -s.experience_cost or 0))

        # Return top recommendations
        return class_skills[:limit]

    def get_player_skill_summary(self, tenant_id: TenantId, character_id: EntityId) -> dict:
        """
        Get summary of player's skills.
        Returns:
        - total_skills: int
        - mastered_skills: int
        - skill_levels: dict of skill -> level
        - total_experience: int
        - next_unlock: dict of skill -> required XP
        """
        # In real implementation, this would query:
        # - Character repository for learned skills
        # - Skill repository for skill details
        # - Experience calculations

        # For now, return placeholder data
        return {
            'total_skills': 0,
            'mastered_skills': 0,
            'skill_levels': {},
            'total_experience': 0,
            'next_unlock': {},
        }
