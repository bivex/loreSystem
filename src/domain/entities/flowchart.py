"""
Flowchart Entity

A Flowchart represents a visual diagram of story flow, choices, and branches.
Part of the World aggregate.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class Flowchart:
    """
    Flowchart entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Must have at least one node
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    story_id: Optional[EntityId]  # Associated story
    name: str
    description: Optional[str]
    nodes: List[Dict[str, Any]]  # Flowchart nodes with their data
    connections: List[Dict[str, Any]]  # Connections between nodes
    is_active: bool  # Whether this flowchart is currently displayed
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        if not self.nodes:
            raise InvariantViolation("Flowchart must have at least one node")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        nodes: List[Dict[str, Any]],
        description: Optional[str] = None,
        story_id: Optional[EntityId] = None,
        connections: Optional[List[Dict[str, Any]]] = None,
        is_active: bool = False,
    ) -> 'Flowchart':
        """
        Factory method for creating a new Flowchart.
        """
        if not nodes:
            raise ValueError("Flowchart must have at least one node")
        
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            story_id=story_id,
            name=name,
            description=description,
            nodes=nodes,
            connections=connections or [],
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_node(self, node: Dict[str, Any]) -> None:
        """Add a node to the flowchart."""
        self.nodes.append(node)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_node(self, node_id: str) -> None:
        """Remove a node from the flowchart."""
        self.nodes = [n for n in self.nodes if str(n.get('id')) != node_id]
        # Also remove connections to/from this node
        self.connections = [
            c for c in self.connections 
            if str(c.get('from')) != node_id and str(c.get('to')) != node_id
        ]
        if not self.nodes:
            raise InvariantViolation("Flowchart must have at least one node")
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_connection(self, connection: Dict[str, Any]) -> None:
        """Add a connection between nodes."""
        self.connections.append(connection)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_connection(self, from_node: str, to_node: str) -> None:
        """Remove a connection between nodes."""
        self.connections = [
            c for c in self.connections 
            if not (c.get('from') == from_node and c.get('to') == to_node)
        ]
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def activate(self) -> None:
        """Make this the active flowchart."""
        if self.is_active:
            return
        object.__setattr__(self, 'is_active', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def deactivate(self) -> None:
        """Deactivate this flowchart."""
        if not self.is_active:
            return
        object.__setattr__(self, 'is_active', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Flowchart({self.name}, {len(self.nodes)} nodes)"
    
    def __repr__(self) -> str:
        return (
            f"Flowchart(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', active={self.is_active}, version={self.version})"
        )