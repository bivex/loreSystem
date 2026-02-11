"""
Empire Entity - Multi-ethnic/political expansionist state
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
from ..exceptions import InvariantViolation


class ExpansionType(str):
    """Types of imperial expansion."""
    MILITARY_CONQUEST = "military_conquest"
    DIPLOMATIC_ABSORPTION = "diplomatic_absorption"
    CULTURAL_ASSIMILATION = "cultural_assimilation"
    ECONOMIC_DOMINATION = "economic_domination"
    MAGICAL_SUBJUGATION = "magical_subjugation"


@dataclass
class Empire:
    """
    Empire represents a large multi-territorial state.
    
    Invariants:
    - Must have at least one province/kingdom
    - Must have an emperor or empress
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    nation_id: Optional[EntityId]
    
    name: str
    description: Description
    
    # Imperial leadership
    emperor_title: str  # e.g., "Emperor", "Empress", "Imperator"
    emperor_character_id: Optional[EntityId]
    imperial_council_ids: List[EntityId]  # Members of imperial council
    
    # Provinces and territories
    province_ids: List[EntityId]  # Provinces/kingdoms in the empire
    client_state_ids: List[EntityId]  # Semi-autonomous client states
    colonized_territory_ids: List[EntityId]
    
    # Imperial policy
    capital_province_id: Optional[EntityId]
    expansion_type: str
    expansion_goals: List[str]

    # Administration
    administrative_divisions: List[str]  # e.g., "Prefectures", "Governorates"
    imperial_bureaucracy: Optional[str]  # Description of bureaucracy
    tax_system: Optional[str]
    
    # Military
    imperial_legion_ids: List[EntityId]
    military_garrison_ids: List[EntityId]
    
    # Culture and religion
    official_culture_id: Optional[EntityId]
    official_religion_id: Optional[EntityId]
    cultural_assimilation_policy: Optional[str]
    
    # Symbols and prestige
    imperial_palace_id: Optional[EntityId]
    imperial_seals: List[EntityId]  # Artifact IDs
    founding_date: Optional[str]
    golden_age: Optional[str]  # Period of greatest power
    
    # Decline
    is_declining: bool
    decline_reasons: List[str]
    internal_rebellions: List[EntityId]
    
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
            raise InvariantViolation("Empire name cannot be empty")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        expansion_type: str = ExpansionType.MILITARY_CONQUEST,
        emperor_title: str = "Emperor",
    ) -> 'Empire':
        """
        Factory method for creating a new Empire.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            nation_id=None,
            name=name,
            description=description,
            emperor_title=emperor_title,
            emperor_character_id=None,
            imperial_council_ids=[],
            province_ids=[],
            client_state_ids=[],
            colonized_territory_ids=[],
            capital_province_id=None,
            expansion_type=expansion_type,
            expansion_goals=[],
            administrative_divisions=[],
            imperial_bureaucracy=None,
            tax_system=None,
            imperial_legion_ids=[],
            military_garrison_ids=[],
            official_culture_id=None,
            official_religion_id=None,
            cultural_assimilation_policy=None,
            imperial_palace_id=None,
            imperial_seals=[],
            founding_date=None,
            golden_age=None,
            is_declining=False,
            decline_reasons=[],
            internal_rebellions=[],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_province(self, province_id: EntityId) -> None:
        """Add a province to the empire."""
        if province_id not in self.province_ids:
            self.province_ids.append(province_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def add_client_state(self, state_id: EntityId) -> None:
        """Add a client state to the empire."""
        if state_id not in self.client_state_ids:
            self.client_state_ids.append(state_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def set_emperor(self, character_id: EntityId) -> None:
        """Set the emperor/empress."""
        object.__setattr__(self, 'emperor_character_id', character_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
