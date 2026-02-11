"""
Kingdom Entity - Monarchical nation state
"""
from dataclasses import dataclass
from typing import Optional, List, Tuple
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


class SuccessionType(str, Enum):
    """Types of succession."""
    HEREDITARY_PRIMOGENITURE = "hereditary_primogeniture"
    HEREDITARY_ULTIMOGENITURE = "hereditary_ultimogeniture"
    ELECTIVE = "elective"
    APPOINTED = "appointed"
    DIVINE_RIGHT = "divine_right"
    CONQUEST = "conquest"
    MERIT_BASED = "merit_based"


class KingdomTier(str, Enum):
    """Tiers of kingdom size/importance."""
    COUNTY = "county"
    DUCHY = "duchy"
    PRINCIPALITY = "principality"
    KINGDOM = "kingdom"
    EMPIRE = "empire"


@dataclass
class Kingdom:
    """
    Kingdom represents a monarchical nation.
    
    Invariants:
    - Must have a monarch or heir
    - Succession type must be valid
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    nation_id: Optional[EntityId]  # Link to parent Nation entity
    
    name: str
    description: Description
    
    # Monarchy details
    monarch_title: str  # e.g., "King", "Queen", "Emperor", "Pharaoh"
    monarch_character_id: Optional[EntityId]
    heir_character_id: Optional[EntityId]
    succession_type: SuccessionType
    
    # Royal family
    royal_house_name: Optional[str]
    royal_family_member_ids: List[EntityId]
    
    # Tier and status
    kingdom_tier: KingdomTier
    is_independent: bool
    overlord_kingdom_id: Optional[EntityId]  # For vassals
    vassal_kingdom_ids: List[EntityId]
    
    # Royal authority
    centralization_level: int  # 1-10, 1=feudal, 10=absolute
    crown_lands: List[EntityId]
    
    # Nobility
    noble_house_ids: List[EntityId]
    peerage_system: Optional[str]  # e.g., "Duke > Earl > Baron"
    
    # Symbols and regalia
    crown_jewels: List[EntityId]  # Artifact IDs
    throne_room_id: Optional[EntityId]
    royal_palace_id: Optional[EntityId]
    
    # History
    founding_date: Optional[str]
    founding_monarch_id: Optional[EntityId]
    dynasties: List[Tuple[str, str]]  # (house_name, period)
    
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
            raise InvariantViolation("Kingdom name cannot be empty")
        
        if self.centralization_level < 1 or self.centralization_level > 10:
            raise InvariantViolation(
                "Centralization level must be between 1 and 10"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        kingdom_tier: KingdomTier = KingdomTier.KINGDOM,
        succession_type: SuccessionType = SuccessionType.HEREDITARY_PRIMOGENITURE,
        is_independent: bool = True,
        centralization_level: int = 5,
    ) -> 'Kingdom':
        """
        Factory method for creating a new Kingdom.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            nation_id=None,
            name=name,
            description=description,
            monarch_title="King",
            monarch_character_id=None,
            heir_character_id=None,
            succession_type=succession_type,
            royal_house_name=None,
            royal_family_member_ids=[],
            kingdom_tier=kingdom_tier,
            is_independent=is_independent,
            overlord_kingdom_id=None,
            vassal_kingdom_ids=[],
            centralization_level=centralization_level,
            crown_lands=[],
            noble_house_ids=[],
            peerage_system=None,
            crown_jewels=[],
            throne_room_id=None,
            royal_palace_id=None,
            founding_date=None,
            founding_monarch_id=None,
            dynasties=[],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def set_monarch(self, character_id: EntityId) -> None:
        """Set the monarch."""
        object.__setattr__(self, 'monarch_character_id', character_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_heir(self, character_id: EntityId) -> None:
        """Set the heir."""
        object.__setattr__(self, 'heir_character_id', character_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_crown_jewel(self, artifact_id: EntityId) -> None:
        """Add a crown jewel (artifact)."""
        if artifact_id not in self.crown_jewels:
            self.crown_jewels.append(artifact_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
