"""
Plot Device Entity

A PlotDevice is a narrative tool used to advance the story or resolve conflict.
"""
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation, InvalidState


class PlotDeviceType(str, Enum):
    """Types of plot devices."""
    MACGUFFIN = "macguffin"  # Desired object that drives the plot
    TRIGGER_EVENT = "trigger_event"  # Event that starts the conflict
    DEUS_EX_MACHINA = "deus_ex_machina"  # Unexpected resolution
    COINCIDENCE = "coincidence"  # Chance encounter
    TWIST = "twist"  # Unexpected plot turn
    RED_HERRING = "red_herring"  # Misdirection device
    CHEKHOVS_GUN = "chekhovs_gun"  # Setup that must pay off
    FLASHBACK = "flashback"  # Reveals past information
    FLASH_FORWARD = "flash_forward"  # Shows future events
    FORESHADOWING = "foreshadowing"  # Hints at future events
    CLIFFHANGER = "cliffhanger"  # Suspenseful ending
    CALL_TO_ADVENTURE = "call_to_adventure"  # Starts the hero's journey
    THRESHOLD = "threshold"  # Point of no return
    ORDEAL = "ordeal"  # Major confrontation


@dataclass
class PlotDevice:
    """
    PlotDevice entity within a Story.
    
    Invariants:
    - Must have a valid description
    - Must belong to a story or scene
    - Must have a defined device type
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    story_id: EntityId
    scene_id: Optional[EntityId]  # Optional: specific scene where device appears
    device_type: PlotDeviceType
    name: str
    description: Description
    is_active: bool  # Whether device is currently in effect
    is_resolved: bool  # Whether device has paid off/been resolved
    related_entity_ids: List[EntityId]  # Entities connected to this device
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) < 1:
            raise InvariantViolation("PlotDevice must have a valid name")
        
        if len(self.description.value) < 10:
            raise InvariantViolation("PlotDevice description must be at least 10 characters")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("Updated timestamp must be >= created timestamp")
        
        if self.version.value < 1:
            raise InvalidState("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        story_id: EntityId,
        device_type: PlotDeviceType,
        name: str,
        description: Description,
        scene_id: Optional[EntityId] = None,
        related_entity_ids: Optional[List[EntityId]] = None,
    ) -> 'PlotDevice':
        """
        Factory method for creating a new PlotDevice.
        
        Validates that the device has all required attributes.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            story_id=story_id,
            scene_id=scene_id,
            device_type=device_type,
            name=name,
            description=description,
            is_active=True,
            is_resolved=False,
            related_entity_ids=related_entity_ids or [],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def activate(self) -> None:
        """Mark plot device as active."""
        if self.is_active:
            return
        
        object.__setattr__(self, 'is_active', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def deactivate(self) -> None:
        """Mark plot device as inactive."""
        if not self.is_active:
            return
        
        object.__setattr__(self, 'is_active', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def resolve(self) -> None:
        """Mark plot device as resolved (paid off)."""
        if self.is_resolved:
            return
        
        object.__setattr__(self, 'is_resolved', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_related_entity(self, entity_id: EntityId) -> None:
        """Add an entity connected to this plot device."""
        if entity_id in self.related_entity_ids:
            raise InvalidState(f"Entity {entity_id} already related to this plot device")
        
        self.related_entity_ids.append(entity_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_related_entity(self, entity_id: EntityId) -> None:
        """Remove a related entity."""
        original_count = len(self.related_entity_ids)
        self.related_entity_ids = [
            eid for eid in self.related_entity_ids if eid != entity_id
        ]
        
        if len(self.related_entity_ids) == original_count:
            raise InvalidState(f"Entity {entity_id} not found in related entities")
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def assign_to_scene(self, scene_id: EntityId) -> None:
        """Assign plot device to a specific scene."""
        if self.scene_id == scene_id:
            return
        
        object.__setattr__(self, 'scene_id', scene_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_in_effect(self) -> bool:
        """Check if plot device is currently in effect."""
        return self.is_active and not self.is_resolved
    
    def __str__(self) -> str:
        return f"PlotDevice({self.name}, type={self.device_type})"
    
    def __repr__(self) -> str:
        return (
            f"PlotDevice(id={self.id}, story_id={self.story_id}, "
            f"name='{self.name}', type={self.device_type})"
        )
