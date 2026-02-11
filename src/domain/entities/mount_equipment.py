"""
MountEquipment Entity

A MountEquipment represents equipment for mounts.
"""
from dataclasses import dataclass
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)


@dataclass
class MountEquipment:
    """
    MountEquipment entity for mount customization.
    
    Invariants:
    - Must have a valid name
    - Must have a valid equipment type
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    equipment_type: str
    description: str
    rarity: str
    stats: dict
    compatible_mount_types: List[str]
    is_equipped: bool
    mount_id: Optional[EntityId]
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("MountEquipment must have a valid name")
        
        if not self.equipment_type or len(self.equipment_type.strip()) == 0:
            raise ValueError("MountEquipment must have a valid equipment type")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        equipment_type: str,
        description: str,
        rarity: str = "common",
        stats: dict = None,
        compatible_mount_types: List[str] = None
    ) -> 'MountEquipment':
        """Factory method to create a new MountEquipment."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            equipment_type=equipment_type,
            description=description,
            rarity=rarity,
            stats=stats or {},
            compatible_mount_types=compatible_mount_types or [],
            is_equipped=False,
            mount_id=None,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def equip(self, mount_id: EntityId) -> 'MountEquipment':
        """Equip the equipment to a mount."""
        return MountEquipment(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            name=self.name,
            equipment_type=self.equipment_type,
            description=self.description,
            rarity=self.rarity,
            stats=self.stats,
            compatible_mount_types=self.compatible_mount_types,
            is_equipped=True,
            mount_id=mount_id,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
