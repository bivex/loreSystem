"""
QuestPrerequisite Repository Implementation

In-memory implementation with full business logic for quest prerequisites.
Includes:
- Prerequisite validation (level, item, faction, quest, skill requirements)
- Complexity calculation
- Soft prerequisite checking (can attempt without meeting)
"""

from typing import Dict, List, Optional
from collections import defaultdict

from src.domain.entities.quest_prerequisite import QuestPrerequisite
from src.domain.repositories.quest_prerequisite_repository import IQuestPrerequisiteRepository
from src.domain.value_objects.common import TenantId, EntityId, PrerequisiteType, QuestDifficulty
from src.domain.exceptions import (
    InvalidEntityOperation,
    BusinessRuleViolation,
    InconsistentData,
)

class InMemoryQuestPrerequisiteRepository(IQuestPrerequisiteRepository):
    """
    In-memory implementation of QuestPrerequisite repository with full business logic.
    
    Business Logic:
    - Prerequisite validation (level, item, faction, quest, skill requirements)
    - Complexity calculation
    - Soft prerequisite checking (can attempt without meeting)
    """

    def __init__(self):
        self._prerequisites: Dict[Tuple[TenantId, EntityId], QuestPrerequisite] = {}
        self._by_quest: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._by_type: Dict[Tuple[TenantId, PrerequisiteType], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, prerequisite: QuestPrerequisite) -> QuestPrerequisite:
        """Save with validation."""
        if prerequisite.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(prerequisite, 'id', new_id)

        # Validate prerequisite
        self._validate_prerequisite(prerequisite)

        key = (prerequisite.tenant_id, prerequisite.id)
        self._prerequisites[key] = prerequisite
        
        # Index by quest
        if hasattr(prerequisite, 'quest_id') and prerequisite.quest_id:
            quest_key = (prerequisite.tenant_id, prerequisite.quest_id)
            self._by_quest[quest_key].append(prerequisite.id)

        # Index by type
        type_key = (prerequisite.tenant_id, prerequisite.prerequisite_type)
        self._by_type[type_key].append(prerequisite.id)

        return prerequisite

    def find_by_id(self, tenant_id: TenantId, prerequisite_id: EntityId) -> Optional[QuestPrerequisite]:
        return self._prerequisites.get((tenant_id, prerequisite_id))

    def list_by_quest(self, tenant_id: TenantId, quest_id: EntityId, limit: int = 50, offset: int = 0) -> List[QuestPrerequisite]:
        """List all prerequisites for a specific quest."""
        quest_key = (tenant_id, quest_id)
        prerequisite_ids = self._by_quest.get(quest_key, [])
        prerequisites = []
        for prereq_id in prerequisite_ids[offset:offset + limit]:
            prereq = self._prerequisites.get((tenant_id, prereq_id))
            if prereq:
                prerequisites.append(prereq)
        return prerequisites

    def list_by_type(self, tenant_id: TenantId, prereq_type: PrerequisiteType, limit: int = 50, offset: int = 0) -> List[QuestPrerequisite]:
        """List all prerequisites of a specific type."""
        type_key = (tenant_id, prereq_type)
        prerequisite_ids = self._by_type.get(type_key, [])
        prerequisites = []
        for prereq_id in prerequisite_ids[offset:offset + limit]:
            prereq = self._prerequisites.get((tenant_id, prereq_id))
            if prereq:
                prerequisites.append(prereq)
        return prerequisites

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[QuestPrerequisite]:
        """List all prerequisites in a world."""
        world_prerequisites = [
            prereq for prereq in self._prerequisites.values()
            if prereq.tenant_id == tenant_id and prereq.world_id == world_id
        ]
        return world_prerequisites[offset:offset + limit]

    def delete(self, tenant_id: TenantId, prerequisite_id: EntityId) -> bool:
        """Delete with cascade checks."""
        key = (tenant_id, prerequisite_id)
        if key not in self._prerequisites:
            return False

        prerequisite = self._prerequisites[key]

        # Check if used by any quest
        if hasattr(prerequisite, 'quest_id') and prerequisite.quest_id:
            quest_key = (prerequisite.tenant_id, prerequisite.quest_id)
            if prerequisite.id in self._by_quest.get(quest_key, []):
                raise BusinessRuleViolation(
                    f"Cannot delete prerequisite {prerequisite_id}: used by quest {prerequisite.quest_id}"
                )

        del self._prerequisites[key]
        return True

    def _validate_prerequisite(self, prerequisite: QuestPrerequisite):
        """Validate prerequisite configuration."""
        # Rule: Level prerequisites must have target level set
        if prerequisite.prerequisite_type == PrerequisiteType.LEVEL:
            if not hasattr(prerequisite, 'target_level') or prerequisite.target_level is None:
                raise BusinessRuleViolation(
                    f"Level prerequisite must have target_level set"
                )

        # Rule: Item prerequisites must have item_id set
        if prerequisite.prerequisite_type == PrerequisiteType.ITEM:
            if not hasattr(prerequisite, 'item_id') or prerequisite.item_id is None:
                raise BusinessRuleViolation(
                    f"Item prerequisite must have item_id set"
                )

        # Rule: Skill prerequisites must have skill_id and level
        if prerequisite.prerequisite_type == PrerequisiteType.SKILL:
            if not hasattr(prerequisite, 'skill_id') or prerequisite.skill_id is None:
                raise BusinessRuleViolation(
                    f"Skill prerequisite must have skill_id and level set"
                )

        # Rule: Faction prerequisites must have faction_id
        if prerequisite.prerequisite_type == PrerequisiteType.FACTION:
            if not hasattr(prerequisite, 'faction_id') or prerequisite.faction_id is None:
                raise BusinessRuleViolation(
                    f"Faction prerequisite must have faction_id set"
                )

        # Rule: Quest prerequisites must have quest_id
        if prerequisite.prerequisite_type == PrerequisiteType.QUEST:
            if not hasattr(prerequisite, 'quest_id') or prerequisite.quest_id is None:
                raise BusinessRuleViolation(
                    f"Quest prerequisite must have quest_id set"
                )

    def get_prerequisite_complexity(self, tenant_id: TenantId, prerequisite_id: EntityId) -> int:
        """
        Calculate complexity score for a prerequisite.
        Higher complexity = harder to satisfy.
        
        Complexity factors:
        - LEVEL: 1 per level difference
        - ITEM: 3 (requires rare item)
        - SKILL: 2 per skill level
        - FACTION: 4 (requires specific faction)
        - QUEST: 5 (requires completing another quest)
        """
        prerequisite = self.find_by_id(tenant_id, prerequisite_id)
        if not prerequisite:
            return 0

        complexity = 0

        # Base complexity
        if hasattr(prerequisite, 'quest_id') and prerequisite.quest_id:
            complexity += 5  # Quest dependency

        # Type-based complexity
        if prerequisite.prerequisite_type == PrerequisiteType.LEVEL:
            if hasattr(prerequisite, 'target_level') and prerequisite.target_level:
                complexity += abs(prerequisite.target_level - 5) * 1  # Assume level 5 as baseline
        elif prerequisite.prerequisite_type == PrerequisiteType.ITEM:
            complexity += 3  # Requires item
        elif prerequisite.prerequisite_type == PrerequisiteType.SKILL:
            if hasattr(prerequisite, 'skill_level') and prerequisite.skill_level:
                complexity += prerequisite.skill_level * 2
        elif prerequisite.prerequisite_type == PrerequisiteType.FACTION:
            complexity += 4
        else:
            complexity += 1

        return complexity

    def check_soft_prerequisite(self, tenant_id: TenantId, prerequisite_id: EntityId, player_data: dict) -> dict:
        """
        Check if player can SOFTLY attempt a prerequisite without meeting it.
        Returns dict with:
        - can_attempt: bool
        - probability: float (0-1)
        - hint: str
        - alternative_prerequisites: list of alternative IDs
        
        Soft checks:
        - Level: can attempt but very hard (5% chance)
        - Item: can attempt with 50% probability (have item)
        - Skill: can attempt with level difference penalty
        - Faction: can attempt if friendly (80% chance)
        """
        prerequisite = self.find_by_id(tenant_id, prerequisite_id)
        if not prerequisite:
            return {'can_attempt': False, 'probability': 0.0, 'hint': 'Not found', 'alternative_prerequisites': []}

        can_attempt = True
        probability = 1.0
        hint = ""
        alternatives = []

        # Level soft check
        if prerequisite.prerequisite_type == PrerequisiteType.LEVEL:
            player_level = player_data.get('level', 1)
            target_level = getattr(prerequisite, 'target_level', 0)
            
            if player_level < target_level:
                probability = 0.05  # Very hard if too low
                hint = f"Requires level {target_level} (you have {player_level})"
                can_attempt = False
            elif player_level >= target_level + 5:
                probability = 1.0  # Easy if overleveled

        # Item soft check
        if prerequisite.prerequisite_type == PrerequisiteType.ITEM:
            has_item = player_data.get('inventory', {}).get(prerequisite.item_id, False)
            if not has_item:
                probability = 0.5  # 50% chance without item
                hint = f"Requires item"
                can_attempt = True

        # Skill soft check
        if prerequisite.prerequisite_type == PrerequisiteType.SKILL:
            player_skill_level = player_data.get('skills', {}).get(prerequisite.skill_id, 0)
            required_level = getattr(prerequisite, 'skill_level', 0)
            
            if player_skill_level < required_level:
                probability = max(0.2, 1.0 - (required_level - player_skill_level) * 0.1)
                hint = f"Requires skill level {required_level}"
            elif player_skill_level >= required_level + 5:
                probability = 1.0

        # Faction soft check
        if prerequisite.prerequisite_type == PrerequisiteType.FACTION:
            faction_id = getattr(prerequisite, 'faction_id', None)
            player_factions = player_data.get('factions', [])
            
            if faction_id and faction_id not in player_factions:
                probability = 0.2  # Unfriendly = hard
                hint = f"Requires faction membership"
                can_attempt = False
            elif faction_id in player_factions:
                probability = 0.9  # Friendly = easy

        # Quest soft check
        if prerequisite.prerequisite_type == PrerequisiteType.QUEST:
            quest_id = getattr(prerequisite, 'quest_id', None)
            completed_quests = player_data.get('completed_quests', [])
            
            if quest_id and quest_id not in completed_quests:
                probability = 0.1  # Haven't completed required quest
                hint = f"Requires completing quest first"
                can_attempt = False
            elif quest_id in completed_quests:
                probability = 1.0  # Already completed required quest

        # Ensure probability is in range
        probability = max(0.0, min(1.0, probability))

        # Find alternative prerequisites
        # (This would normally query the database)
        alternatives = []

        return {
            'can_attempt': can_attempt,
            'probability': probability,
            'hint': hint,
            'alternative_prerequisites': alternatives
        }
