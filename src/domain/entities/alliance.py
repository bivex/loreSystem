"""
Alliance Entity - Coalition of nations/factions
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


class AllianceType(str, Enum):
    """Types of alliances."""
    MILITARY = "military"
    ECONOMIC = "economic"
    RELIGIOUS = "religious"
    CULTURAL = "cultural"
    DEFENSIVE = "defensive"
    TRADE = "trade"
    MAGICAL = "magical"
    COMPREHENSIVE = "comprehensive"


@dataclass
class Alliance:
    """
    Alliance represents a coalition of nations or factions.
    
    Invariants:
    - Must have at least two members
    - Name cannot be empty
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    
    name: str
    description: Description
    alliance_type: AllianceType
    
    # Members
    member_nation_ids: List[EntityId]
    member_faction_ids: List[EntityId]
    founding_member_ids: List[EntityId]
    
    # Leadership
    leader_nation_id: Optional[EntityId]
    leader_faction_id: Optional[EntityId]
    headquarters_location_id: Optional[EntityId]
    
    # Duration
    founding_date: Optional[str]
    dissolution_date: Optional[str]
    is_active: bool
    
    # Agreements and obligations
    mutual_defense_pact: bool
    free_trade_agreement: bool
    shared_intelligence: bool
    joint_military_operations: bool
    
    # Structure
    governing_council_ids: List[EntityId]  # Character IDs representing members
    voting_system: Optional[str]  # e.g., "Unanimous", "Majority", "Weighted by power"
    
    # Resources
    shared_resources: List[str]
    pooled_fund_id: Optional[EntityId]  # For economic alliances
    
    # Enemies
    enemy_alliance_ids: List[EntityId]
    enemy_nation_ids: List[EntityId]
    
    # History
    formation_event_id: Optional[EntityId]
    key_victories: List[EntityId]  # Battle/event IDs
    key_defeats: List[EntityId]
    
    # Symbols
    alliance_flag: Optional[str]
    alliance_motto: Optional[str]
    
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
            raise InvariantViolation("Alliance name cannot be empty")
        
        total_members = len(self.member_nation_ids) + len(self.member_faction_ids)
        if total_members < 2:
            raise InvariantViolation(
                "Alliance must have at least two members"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        alliance_type: AllianceType = AllianceType.MILITARY,
        mutual_defense_pact: bool = False,
        free_trade_agreement: bool = False,
    ) -> 'Alliance':
        """
        Factory method for creating a new Alliance.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            alliance_type=alliance_type,
            member_nation_ids=[],
            member_faction_ids=[],
            founding_member_ids=[],
            leader_nation_id=None,
            leader_faction_id=None,
            headquarters_location_id=None,
            founding_date=None,
            dissolution_date=None,
            is_active=True,
            mutual_defense_pact=mutual_defense_pact,
            free_trade_agreement=free_trade_agreement,
            shared_intelligence=False,
            joint_military_operations=False,
            governing_council_ids=[],
            voting_system=None,
            shared_resources=[],
            pooled_fund_id=None,
            enemy_alliance_ids=[],
            enemy_nation_ids=[],
            formation_event_id=None,
            key_victories=[],
            key_defeats=[],
            alliance_flag=None,
            alliance_motto=None,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_member_nation(self, nation_id: EntityId, is_founder: bool = False) -> None:
        """Add a nation member."""
        if nation_id not in self.member_nation_ids:
            self.member_nation_ids.append(nation_id)
            if is_founder:
                self.founding_member_ids.append(nation_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def add_member_faction(self, faction_id: EntityId, is_founder: bool = False) -> None:
        """Add a faction member."""
        if faction_id not in self.member_faction_ids:
            self.member_faction_ids.append(faction_id)
            if is_founder:
                self.founding_member_ids.append(faction_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def dissolve(self, dissolution_date: Optional[str] = None) -> None:
        """Dissolve the alliance."""
        object.__setattr__(self, 'is_active', False)
        object.__setattr__(self, 'dissolution_date', dissolution_date)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
