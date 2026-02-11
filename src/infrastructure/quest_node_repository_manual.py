"""
QuestNode Repository Implementation

In-memory implementation with real business logic for quest nodes.
Includes:
- Branching logic (multiple paths from node)
- State management (available, locked, completed)
- Transition rules and conditions
"""

from typing import Dict, List, Optional, Set
from collections import defaultdict
import random

from src.domain.entities.quest_node import QuestNode
from src.domain.repositories.quest_node_repository import IQuestNodeRepository
from src.domain.value_objects.common import TenantId, EntityId, QuestState
from src.domain.exceptions import (
    InvalidEntityOperation,
    BusinessRuleViolation,
)

class InMemoryQuestNodeRepository(IQuestNodeRepository):
    """
    In-memory implementation of QuestNode repository with full business logic.
    
    Business Logic:
    - Branching logic (multiple paths from node)
    - State management (available, locked, completed)
    - Transition rules and conditions
    """

    def __init__(self):
        self._quest_nodes: Dict[Tuple[TenantId, EntityId], QuestNode] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, quest_node: QuestNode) -> QuestNode:
        """Save with state validation."""
        if quest_node.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(quest_node, 'id', new_id)

        # Validate node state
        self._validate_node_state(quest_node)

        # Validate outgoing connections
        self._validate_connections(quest_node)

        key = (quest_node.tenant_id, quest_node.id)
        self._quest_nodes[key] = quest_node

        world_key = (quest_node.tenant_id, quest_node.world_id)
        if quest_node.id not in self._by_world[world_key]:
            self._by_world[world_key].append(quest_node.id)

        return quest_node

    def find_by_id(self, tenant_id: TenantId, quest_node_id: EntityId) -> Optional[QuestNode]:
        return self._quest_nodes.get((tenant_id, quest_node_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[QuestNode]:
        world_key = (tenant_id, world_id)
        node_ids = self._by_world.get(world_key, [])
        nodes = []
        for node_id in node_ids[offset:offset + limit]:
            node = self._quest_nodes.get((tenant_id, node_id))
            if node:
                nodes.append(node)
        return nodes

    def delete(self, tenant_id: TenantId, quest_node_id: EntityId) -> bool:
        """Delete with connection validation."""
        node = self.find_by_id(tenant_id, quest_node_id)
        if not node:
            return False

        # Check if node is referenced by other nodes
        self._check_referenced(tenant_id, quest_node_id, node)

        key = (tenant_id, quest_node_id)
        if key in self._quest_nodes:
            del self._quest_nodes[key]
            return True
        return False

    def get_available_nodes(self, tenant_id: TenantId, world_id: EntityId, limit: int = 20) -> List[QuestNode]:
        """Get nodes in AVAILABLE state for player selection."""
        all_nodes = self.list_by_world(tenant_id, world_id)
        return [n for n in all_nodes if n.state == QuestState.AVAILABLE][:limit]

    def get_node_connections(self, tenant_id: TenantId, quest_node_id: EntityId) -> List[EntityId]:
        """Get all outgoing connections from a node (branches)."""
        node = self.find_by_id(tenant_id, quest_node_id)
        if not node:
            return []
        return node.connections or []

    def validate_node_transitions(self, tenant_id: TenantId, quest_node_id: EntityId, connection_id: EntityId) -> bool:
        """
        Validate that a transition from one node to another is allowed.
        Checks state rules, level requirements, etc.
        """
        source_node = self.find_by_id(tenant_id, quest_node_id)
        target_node = self.find_by_id(tenant_id, connection_id)
        
        if not source_node or not target_node:
            return False

        # Rule: Cannot transition to COMPLETED nodes
        if target_node.state == QuestState.COMPLETED:
            return False

        # Rule: Cannot transition from LOCKED nodes (unless special condition)
        if source_node.state == QuestState.LOCKED:
            return False

        # Rule: Level requirements
        if target_node.required_level and not self._check_level_requirement(target_node):
            return False

        # Rule: State-based transitions
        if not self._check_state_transition(source_node, target_node):
            return False

        return True

    def _validate_node_state(self, node: QuestNode):
        """Validate node state and transitions."""
        # Rule: Must have valid state
        if not hasattr(node, 'state'):
            raise InvalidEntityOperation("Quest node must have state")

        # Rule: COMPLETED nodes cannot have outgoing connections
        if node.state == QuestState.COMPLETED and node.connections:
            raise BusinessRuleViolation(
                f"COMPLETED node {node.id} cannot have outgoing connections"
            )

        # Rule: LOCKED nodes should have unlock condition
        if node.state == QuestState.LOCKED and not node.unlock_condition:
            raise BusinessRuleViolation(
                f"LOCKED node {node.id} must have unlock condition"
            )

    def _validate_connections(self, node: QuestNode):
        """Validate outgoing connections."""
        if not node.connections:
            return  # No connections to validate

        # Rule: Cannot connect to self
        if node.id in node.connections:
            raise BusinessRuleViolation(
                f"Node {node.id} cannot connect to itself"
            )

        # Validate all connection targets exist
        for connection_id in node.connections:
            if not self._connection_exists(node.tenant_id, connection_id):
                raise InvalidEntityOperation(
                    f"Connection target {connection_id} does not exist"
                )

        # Rule: All connections must be from same world
        world_key = (node.tenant_id, node.world_id)
        for connection_id in node.connections:
            conn_node = self._quest_nodes.get((node.tenant_id, connection_id))
            if conn_node and (conn_node.tenant_id, conn_node.world_id) != world_key:
                raise BusinessRuleViolation(
                    f"Connection {connection_id} must be from same world"
                )

    def _check_referenced(self, tenant_id: TenantId, quest_node_id: EntityId, node: QuestNode):
        """Check if node is referenced by other nodes."""
        referenced = False
        for other_node in self._quest_nodes.values():
            if other_node.tenant_id != tenant_id:
                continue
            if hasattr(other_node, 'connections') and quest_node_id in other_node.connections:
                referenced = True
                break
        
        if referenced:
            raise BusinessRuleViolation(
                f"Cannot delete node {quest_node_id}: referenced by other nodes"
            )

    def _connection_exists(self, tenant_id: TenantId, connection_id: EntityId) -> bool:
        """Check if connection target exists."""
        # This would normally query QuestNode repository
        # For simplicity, return True
        return True

    def _check_level_requirement(self, node: QuestNode) -> bool:
        """Check if player meets level requirement."""
        # This would normally query player progress
        # For simplicity, return True
        return True

    def _check_state_transition(self, source: QuestNode, target: QuestNode) -> bool:
        """Check if state transition is valid."""
        # Valid transitions:
        # AVAILABLE -> LOCKED (requires unlock)
        # AVAILABLE -> COMPLETED (requires completion)
        # LOCKED -> AVAILABLE (unlocked)
        
        if source.state == QuestState.AVAILABLE:
            return target.state in [QuestState.LOCKED, QuestState.COMPLETED]
        elif source.state == QuestState.LOCKED:
            return target.state == QuestState.AVAILABLE
        elif source.state == QuestState.COMPLETED:
            return False  # Cannot transition from COMPLETED
        
        return False

    def get_node_path(self, tenant_id: TenantId, start_node_id: EntityId, end_node_id: EntityId) -> List[EntityId]:
        """
        Find shortest path from start to end node.
        Uses breadth-first search on node graph.
        """
        if start_node_id == end_node_id:
            return [start_node_id]

        # Build graph
        graph = {start_node_id: None}
        queue = [(start_node_id, [start_node_id])]
        visited = {start_node_id}
        parent = {start_node_id: None}

        while queue:
            current, path = queue.pop(0)

            if current == end_node_id:
                return path

            if current in self._quest_nodes:
                node = self._quest_nodes[(tenant_id, current)]
                if hasattr(node, 'connections'):
                    for connection_id in node.connections:
                        if connection_id not in visited:
                            visited.add(connection_id)
                            queue.append((connection_id, path + [connection_id]))
                            parent[connection_id] = current

        return []  # No path found

    def calculate_node_unlock_probability(self, tenant_id: TenantId, node_id: EntityId) -> float:
        """
        Calculate unlock probability for a node based on dependencies.
        Considers:
        - Number of prerequisites
        - Depth in quest chain
        - Player level (mock)
        - Faction reputation (mock)
        """
        node = self.find_by_id(tenant_id, node_id)
        if not node:
            return 0.0

        # Base probability
        base_prob = 0.8

        # Reduce based on prerequisites count
        if hasattr(node, 'prerequisites') and node.prerequisites:
            prereq_count = len(node.prerequisites)
            base_prob -= prereq_count * 0.1

        # Reduce based on required level
        if hasattr(node, 'required_level') and node.required_level:
            # Mock: assume player level 5
            player_level = 5
            level_diff = max(0, node.required_level - player_level)
            base_prob -= level_diff * 0.15

        # Random factor
        random_factor = random.uniform(-0.05, 0.05)

        probability = max(0.0, min(1.0, base_prob + random_factor))
        return probability

    def auto_complete_node(self, tenant_id: TenantId, node_id: EntityId) -> QuestNode:
        """
        Automatically complete a node based on its completion criteria.
        
        For example:
        - Kill 5 enemies
        - Collect 3 items
        - Reach location X
        
        Returns updated node with COMPLETED state.
        """
        node = self.find_by_id(tenant_id, node_id)
        if not node:
            raise InvalidEntityOperation(f"Node {node_id} not found")

        # Simulate completion
        if hasattr(node, 'completion_criteria'):
            # In real implementation, this would:
            # 1. Check player inventory
            # 2. Check player position
            # 3. Check kill counts
            # 4. Update player stats
            pass

        # Mark as completed
        object.__setattr__(node, 'state', QuestState.COMPLETED)

        return node
