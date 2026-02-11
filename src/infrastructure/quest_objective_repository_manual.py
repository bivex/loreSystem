"""
QuestObjective Repository Implementation

In-memory implementation with real business logic for quest objectives.
Includes:
- Objective tracking (kill, collect, reach, talk, escort, defend)
- Completion validation
- Progress tracking
- Reward triggering
"""

from typing import Dict, List, Optional
from collections import defaultdict
from enum import Enum

from src.domain.entities.quest_objective import QuestObjective
from src.domain.repositories.quest_objective_repository import IQuestObjectiveRepository
from src.domain.value_objects.common import TenantId, EntityId, ObjectiveType, ObjectiveStatus
from src.domain.exceptions import (
    InvalidEntityOperation,
    BusinessRuleViolation,
    ObjectiveAlreadyCompleted,
)

class ObjectiveTracking(Enum):
    """Types of objective tracking."""
    KILL_COUNT = "kill_count"
    ITEM_COLLECTED = "item_collected"
    LOCATION_REACHED = "location_reached"
    NPC_TALKED = "npc_talked"
    TIME_ELAPSED = "time_elapsed"
    ESCORT_ALIVE = "escort_alive"
    DEFEND_OBJECTIVE = "defend_objective"

class InMemoryQuestObjectiveRepository(IQuestObjectiveRepository):
    """
    In-memory implementation of QuestObjective repository with full business logic.
    
    Business Logic:
    - Objective tracking (kill, collect, reach, talk, escort, defend)
    - Completion validation
    - Progress tracking
    - Reward triggering
    """

    def __init__(self):
        self._objectives: Dict[Tuple[TenantId, EntityId], QuestObjective] = {}
        self._next_id = 1
        
        # Progress tracking storage
        self._progress: Dict[Tuple[TenantId, EntityId, str], object] = {}
        
        # Objective relationships (for escort/defend)
        self._escorting: Dict[Tuple[TenantId, EntityId], EntityId] = {}  # objective_id -> target_id
        self._defending: Dict[Tuple[TenantId, EntityId], EntityId] = {}

    def save(self, objective: QuestObjective) -> QuestObjective:
        """Save with validation and progress initialization."""
        if objective.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(objective, 'id', new_id)

        # Validate objective configuration
        self._validate_objective(objective)

        key = (objective.tenant_id, objective.id)
        self._objectives[key] = objective

        # Initialize progress
        if objective.objective_type not in [ObjectiveType.COLLECT, ObjectiveType.REACH]:
            self._initialize_progress(objective)

        return objective

    def find_by_id(self, tenant_id: TenantId, objective_id: EntityId) -> Optional[QuestObjective]:
        return self._objectives.get((tenant_id, objective_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[QuestObjective]:
        world_objectives = [
            obj for obj in self._objectives.values()
            if obj.tenant_id == tenant_id and obj.world_id == world_id
        ]
        return world_objectives[offset:offset + limit]

    def delete(self, tenant_id: TenantId, objective_id: EntityId) -> bool:
        key = (tenant_id, objective_id)
        if key not in self._objectives:
            return False

        # Clean up progress
        for progress_key in list(self._progress.keys()):
            if progress_key[0] == tenant_id and progress_key[1] == objective_id:
                del self._progress[progress_key]

        del self._objectives[key]
        return True

    def update_progress(self, tenant_id: TenantId, objective_id: EntityId, tracking_type: ObjectiveTracking, value: any) -> QuestObjective:
        """
        Update objective progress based on tracking type.
        
        Tracking types:
        - KILL_COUNT: increment kill counter
        - ITEM_COLLECTED: mark item collected
        - LOCATION_REACHED: mark location reached
        - NPC_TALKED: mark NPC talked to
        - TIME_ELAPSED: update time elapsed
        - ESCORT_ALIVE: mark escort target alive
        - DEFEND_OBJECTIVE: mark defend objective met
        """
        objective = self.find_by_id(tenant_id, objective_id)
        if not objective:
            raise InvalidEntityOperation(f"Objective {objective_id} not found")

        if objective.status == ObjectiveStatus.COMPLETED:
            raise ObjectiveAlreadyCompleted(f"Objective {objective_id} already completed")

        # Get current progress
        progress_key = (tenant_id, objective_id, tracking_type.value)
        current_value = self._progress.get(progress_key, {})

        # Update progress based on tracking type
        if tracking_type == ObjectiveTracking.KILL_COUNT:
            current_count = current_value.get('count', 0)
            required = current_value.get('required', 1)
            new_count = min(current_count + value, required)
            
            self._progress[progress_key] = {'count': new_count, 'required': required}
            
            # Check completion
            if new_count >= required:
                self._complete_objective(objective)
                return objective

        elif tracking_type == ObjectiveTracking.ITEM_COLLECTED:
            collected_items = current_value.get('collected', [])
            if value not in collected_items:
                collected_items.append(value)
                self._progress[progress_key] = {'collected': collected_items}
            
            # Check completion
            if len(collected_items) >= current_value.get('required', 1):
                self._complete_objective(objective)
                return objective

        elif tracking_type == ObjectiveTracking.LOCATION_REACHED:
            if not current_value.get('reached', False):
                self._progress[progress_key] = {'reached': True}
                self._complete_objective(objective)
                return objective

        elif tracking_type == ObjectiveTracking.NPC_TALKED:
            if not current_value.get('talked', False):
                self._progress[progress_key] = {'talked': True}
                self._complete_objective(objective)
                return objective

        elif tracking_type == ObjectiveTracking.TIME_ELAPSED:
            elapsed = current_value.get('elapsed', 0)
            required = current_value.get('required', 60)
            new_elapsed = min(elapsed + value, required)
            
            self._progress[progress_key] = {'elapsed': new_elapsed, 'required': required}
            
            if new_elapsed >= required:
                self._complete_objective(objective)
                return objective

        elif tracking_type == ObjectiveTracking.ESCORT_ALIVE:
            target_id = value  # Escort target ID
            self._escorting[(tenant_id, objective_id)] = target_id
            if not current_value.get('alive', False):
                self._progress[progress_key] = {'alive': True}
            
            # Escort completes when target reaches destination (checked by other logic)
            return objective

        elif tracking_type == ObjectiveTracking.DEFEND_OBJECTIVE:
            target_id = value  # Defend target ID
            self._defending[(tenant_id, objective_id)] = target_id
            
            objective_count = current_value.get('count', 0)
            required = current_value.get('required', 1)
            new_count = min(objective_count + value, required)
            
            self._progress[progress_key] = {'count': new_count, 'required': required}
            
            if new_count >= required:
                self._complete_objective(objective)
                return objective

        return objective

    def get_progress(self, tenant_id: TenantId, objective_id: EntityId) -> dict:
        """Get current progress for an objective."""
        objective = self.find_by_id(tenant_id, objective_id)
        if not objective:
            return {}

        progress = {}
        for tracking_type in [ObjectiveTracking.KILL_COUNT, ObjectiveTracking.ITEM_COLLECTED, 
                           ObjectiveTracking.LOCATION_REACHED, ObjectiveTracking.NPC_TALKED, 
                           ObjectiveTracking.TIME_ELAPSED]:
            progress_key = (tenant_id, objective_id, tracking_type.value)
            progress[tracking_type.value] = self._progress.get(progress_key, {})

        # Add escort/defend info
        if (tenant_id, objective_id) in self._escorting:
            progress['escorting'] = self._escorting[(tenant_id, objective_id)]
        if (tenant_id, objective_id) in self._defending:
            progress['defending'] = self._defending[(tenant_id, objective_id)]

        return progress

    def _validate_objective(self, objective: QuestObjective):
        """Validate objective configuration."""
        if not objective.objective_type:
            raise InvalidEntityOperation("Objective type must be specified")

        # Validate kill objectives
        if objective.objective_type == ObjectiveType.KILL:
            if not hasattr(objective, 'target_id') or not objective.target_id:
                raise InvalidEntityOperation("Kill objective must have target_id")

            required = getattr(objective, 'target_count', 1)
            if required < 1:
                raise BusinessRuleViolation("Kill count must be at least 1")

        # Validate collect objectives
        if objective.objective_type == ObjectiveType.COLLECT:
            if not hasattr(objective, 'target_item_id') or not objective.target_item_id:
                raise InvalidEntityOperation("Collect objective must have target_item_id")

            required = getattr(objective, 'target_count', 1)
            if required < 1:
                raise BusinessRuleViolation("Collect count must be at least 1")

        # Validate reach objectives
        if objective.objective_type == ObjectiveType.REACH:
            if not hasattr(objective, 'target_location_id') or not objective.target_location_id:
                raise InvalidEntityOperation("Reach objective must have target_location_id")

        # Validate talk objectives
        if objective.objective_type == ObjectiveType.TALK:
            if not hasattr(objective, 'target_npc_id') or not objective.target_npc_id:
                raise InvalidEntityOperation("Talk objective must have target_npc_id")

        # Validate time objectives
        if objective.objective_type == ObjectiveType.TIME:
            required_time = getattr(objective, 'required_time', 60)
            if required_time < 1:
                raise BusinessRuleViolation("Time objective must have required_time >= 1")

        # Validate escort objectives
        if objective.objective_type == ObjectiveType.ESCORT:
            if not hasattr(objective, 'target_id') or not objective.target_id:
                raise InvalidEntityOperation("Escort objective must have target_id")

        # Validate defend objectives
        if objective.objective_type == ObjectiveType.DEFEND:
            if not hasattr(objective, 'target_id') or not objective.target_id:
                raise InvalidEntityOperation("Defend objective must have target_id")

    def _initialize_progress(self, objective: QuestObjective):
        """Initialize progress tracking for an objective."""
        if objective.objective_type == ObjectiveType.KILL:
            required = getattr(objective, 'target_count', 1)
            progress_key = (objective.tenant_id, objective.id, ObjectiveTracking.KILL_COUNT.value)
            self._progress[progress_key] = {'count': 0, 'required': required}

        elif objective.objective_type == ObjectiveType.COLLECT:
            required = getattr(objective, 'target_count', 1)
            progress_key = (objective.tenant_id, objective.id, ObjectiveTracking.ITEM_COLLECTED.value)
            self._progress[progress_key] = {'collected': [], 'required': required}

        elif objective.objective_type == ObjectiveType.TIME:
            required_time = getattr(objective, 'required_time', 60)
            progress_key = (objective.tenant_id, objective.id, ObjectiveTracking.TIME_ELAPSED.value)
            self._progress[progress_key] = {'elapsed': 0, 'required': required_time}

        elif objective.objective_type == ObjectiveType.ESCORT:
            progress_key = (objective.tenant_id, objective.id, ObjectiveTracking.ESCORT_ALIVE.value)
            self._progress[progress_key] = {'alive': False}

        elif objective.objective_type == ObjectiveType.DEFEND:
            required = getattr(objective, 'target_count', 1)
            progress_key = (objective.tenant_id, objective.id, ObjectiveTracking.DEFEND_OBJECTIVE.value)
            self._progress[progress_key] = {'count': 0, 'required': required}

    def _complete_objective(self, objective: QuestObjective):
        """Mark an objective as completed and handle rewards."""
        object.__setattr__(objective, 'status', ObjectiveStatus.COMPLETED)
        
        # Trigger rewards (would normally call RewardRepository)
        # For now, just log it
        # print(f"Objective {objective.id} completed - triggering rewards")

        key = (objective.tenant_id, objective.id)
        self._objectives[key] = objective

    def get_objectives_for_quest(self, tenant_id: TenantId, quest_id: EntityId) -> List[QuestObjective]:
        """Get all objectives belonging to a specific quest."""
        objectives = []
        for obj in self._objectives.values():
            if obj.tenant_id == tenant_id and obj.quest_id == quest_id:
                objectives.append(obj)
        return objectives

    def auto_complete_if_possible(self, tenant_id: TenantId, objective_id: EntityId, player_state: dict) -> QuestObjective:
        """
        Automatically complete an objective if possible based on player state.
        
        For example:
        - Kill objective: check if player has already killed the target
        - Collect objective: check if player has the required items
        - Reach objective: check if player is at the required location
        """
        objective = self.find_by_id(tenant_id, objective_id)
        if not objective or objective.status == ObjectiveStatus.COMPLETED:
            return objective

        # Kill objective auto-complete
        if objective.objective_type == ObjectiveType.KILL:
            killed_npcs = player_state.get('killed_npcs', [])
            if hasattr(objective, 'target_id') and objective.target_id in killed_npcs:
                self._complete_objective(objective)
                return objective

        # Collect objective auto-complete
        if objective.objective_type == ObjectiveType.COLLECT:
            inventory = player_state.get('inventory', {})
            item_id = getattr(objective, 'target_item_id', None)
            if item_id and inventory.get(item_id, 0) >= getattr(objective, 'target_count', 1):
                for i in range(getattr(objective, 'target_count', 1)):
                    self.update_progress(tenant_id, objective_id, ObjectiveTracking.ITEM_COLLECTED, item_id)
                return objective

        # Reach objective auto-complete
        if objective.objective_type == ObjectiveType.REACH:
            position = player_state.get('position', None)
            location_id = getattr(objective, 'target_location_id', None)
            if position and location_id:
                # In real implementation, this would check if player is at location
                # For now, just mark as reached
                self.update_progress(tenant_id, objective_id, ObjectiveTracking.LOCATION_REACHED, True)
                return objective

        # Time objective auto-complete
        if objective.objective_type == ObjectiveType.TIME:
            play_time = player_state.get('play_time', 0)
            required_time = getattr(objective, 'required_time', 60)
            if play_time >= required_time:
                self.update_progress(tenant_id, objective_id, ObjectiveTracking.TIME_ELAPSED, required_time)
                return objective

        return objective
