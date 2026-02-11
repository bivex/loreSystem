"""
Government Entity - Ruling body/institution
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
from ..exceptions import InvariantViolation


class GovernmentType(str, Enum):
    """Types of governments."""
    MONARCHY = "monarchy"
    REPUBLIC = "republic"
    DEMOCRACY = "democracy"
    OLIGARCHY = "oligarchy"
    THEOCRACY = "theocracy"
    MAGOCRACY = "magocracy"
    MILITARY_JUNTA = "military_junta"
    COUNCIL = "council"
    TRIBAL_COUNCIL = "tribal_council"
    FEUDAL = "feudal"
    ANARCHY = "anarchy"


@dataclass
class Government:
    """
    Government represents the ruling body of a nation/region.
    
    Invariants:
    - Must have a governing nation or region
    - Name cannot be empty
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    
    # Jurisdiction
    nation_id: Optional[EntityId]
    region_id: Optional[EntityId]
    city_id: Optional[EntityId]
    
    name: str
    description: Description
    
    # Government type
    government_type: GovernmentType
    
    # Leadership
    head_of_state_id: Optional[EntityId]  # Character ID
    head_of_government_id: Optional[EntityId]  # Character ID
    cabinet_member_ids: List[EntityId]  # Character IDs
    
    # Structure
    branches: List[str]  # e.g., ["Executive", "Legislative", "Judicial"]
    legislative_body_id: Optional[EntityId]
    
    # Authority and legitimacy
    legitimacy_source: Optional[str]  # e.g., "Divine right", "Popular mandate"
    approval_rating: Optional[int]  # 0-100
    corruption_level: Optional[int]  # 0-10 scale
    
    # Policies
    domestic_policy_ids: List[EntityId]
    foreign_policy_ids: List[EntityId]
    economic_policy_ids: List[EntityId]
    
    # Administration
    ministries: List[str]  # e.g., "War", "Finance", "Magic"
    ministry_head_ids: List[EntityId]  # Character IDs
    
    # Military control
    military_control: Optional[str]  # e.g., "Direct", "Through generals"
    
    # Headquarters
    seat_of_government_id: Optional[EntityId]  # Location
    
    # Relationships
    allied_governments: List[EntityId]
    rival_governments: List[EntityId]
    
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
        
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Government name cannot be empty")
        
        # At least one jurisdiction must be set
        if not any([self.nation_id, self.region_id, self.city_id]):
            raise InvariantViolation(
                "Government must have at least one jurisdiction (nation, region, or city)"
            )
        
        if self.approval_rating is not None:
            if self.approval_rating < 0 or self.approval_rating > 100:
                raise InvariantViolation(
                    "Approval rating must be between 0 and 100"
                )
        
        if self.corruption_level is not None:
            if self.corruption_level < 0 or self.corruption_level > 10:
                raise InvariantViolation(
                    "Corruption level must be between 0 and 10"
                )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        government_type: GovernmentType,
        nation_id: Optional[EntityId] = None,
        region_id: Optional[EntityId] = None,
        city_id: Optional[EntityId] = None,
    ) -> 'Government':
        """
        Factory method for creating a new Government.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            nation_id=nation_id,
            region_id=region_id,
            city_id=city_id,
            name=name,
            description=description,
            government_type=government_type,
            head_of_state_id=None,
            head_of_government_id=None,
            cabinet_member_ids=[],
            branches=[],
            legislative_body_id=None,
            legitimacy_source=None,
            approval_rating=None,
            corruption_level=None,
            domestic_policy_ids=[],
            foreign_policy_ids=[],
            economic_policy_ids=[],
            ministries=[],
            ministry_head_ids=[],
            military_control=None,
            seat_of_government_id=None,
            allied_governments=[],
            rival_governments=[],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def set_head_of_state(self, character_id: EntityId) -> None:
        """Set the head of state."""
        object.__setattr__(self, 'head_of_state_id', character_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_cabinet_member(self, character_id: EntityId) -> None:
        """Add a cabinet member."""
        if character_id not in self.cabinet_member_ids:
            self.cabinet_member_ids.append(character_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
