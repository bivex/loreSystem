"""
Nation Entity - Political entity with sovereignty
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


class NationType(str, Enum):
    """Types of nations."""
    KINGDOM = "kingdom"
    REPUBLIC = "republic"
    EMPIRE = "empire"
    CITY_STATE = "city_state"
    TRIBAL_CONFEDERACY = "tribal_confederacy"
    THEOCRACY = "theocracy"
    MAGOCRACY = "magocracy"
    FEUDAL_REALM = "feudal_realm"
    DEMOCRACY = "democracy"
    MERITOCRACY = "meritocracy"


class EconomicSystem(str, Enum):
    """Types of economic systems."""
    FEUDALISM = "feudalism"
    CAPITALISM = "capitalism"
    SOCIALISM = "socialism"
    MERCHANT_GUILD = "merchant_guild"
    TRIBAL_ECONOMY = "tribal_economy"
    SLAVE_ECONOMY = "slave_economy"
    MAGICAL_ECONOMY = "magical_economy"


@dataclass
class Nation:
    """
    Nation represents a sovereign political entity.
    
    Invariants:
    - Name cannot be empty
    - Must have at least one territory
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    
    # Basic info
    name: str
    description: Description
    nation_type: NationType
    
    # Geography
    capital_location_id: Optional[EntityId]
    territory_ids: List[EntityId]  # Cities/regions controlled
    borders_ids: List[EntityId]  # Neighboring nations
    
    # Government
    government_type: str  # e.g., "Monarchy", "Council of Elders"
    ruler_character_id: Optional[EntityId]
    government_ids: List[EntityId]  # Government institutions
    
    # Law
    legal_system_id: Optional[EntityId]
    constitution_id: Optional[EntityId]
    
    # Military
    military_strength: Optional[int]  # 1-10 scale
    active_conflicts: List[EntityId]  # Wars/conflicts
    
    # Economy
    economic_system: EconomicSystem
    currency_id: Optional[EntityId]
    main_exports: List[str]
    main_imports: List[str]
    
    # Diplomacy
    allies_ids: List[EntityId]
    enemies_ids: List[EntityId]
    trade_partners_ids: List[EntityId]
    treaties: List[EntityId]
    
    # Population
    population_estimate: Optional[int]
    dominant_culture_id: Optional[EntityId]
    minority_culture_ids: List[EntityId]
    
    # History
    founding_date: Optional[str]  # In-world date
    founding_event_id: Optional[EntityId]
    historical_events: List[EntityId]
    
    # Symbols
    flag_description: Optional[str]
    coat_of_arms: Optional[str]
    motto: Optional[str]
    national_anthem: Optional[str]
    
    # Status
    is_active: bool  # False for fallen nations
    is_vassal: bool
    overlord_nation_id: Optional[EntityId]
    
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
            raise InvariantViolation("Nation name cannot be empty")
        
        if len(self.name) > 200:
            raise InvariantViolation("Nation name must be <= 200 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        nation_type: NationType,
        economic_system: EconomicSystem,
        capital_location_id: Optional[EntityId] = None,
        ruler_character_id: Optional[EntityId] = None,
        is_active: bool = True,
    ) -> 'Nation':
        """
        Factory method for creating a new Nation.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            nation_type=nation_type,
            capital_location_id=capital_location_id,
            territory_ids=[],
            borders_ids=[],
            government_type="",
            ruler_character_id=ruler_character_id,
            government_ids=[],
            legal_system_id=None,
            constitution_id=None,
            military_strength=None,
            active_conflicts=[],
            economic_system=economic_system,
            currency_id=None,
            main_exports=[],
            main_imports=[],
            allies_ids=[],
            enemies_ids=[],
            trade_partners_ids=[],
            treaties=[],
            population_estimate=None,
            dominant_culture_id=None,
            minority_culture_ids=[],
            founding_date=None,
            founding_event_id=None,
            historical_events=[],
            flag_description=None,
            coat_of_arms=None,
            motto=None,
            national_anthem=None,
            is_active=is_active,
            is_vassal=False,
            overlord_nation_id=None,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_territory(self, location_id: EntityId) -> None:
        """Add a territory to the nation."""
        if location_id not in self.territory_ids:
            self.territory_ids.append(location_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def add_ally(self, nation_id: EntityId) -> None:
        """Add an allied nation."""
        if nation_id not in self.allies_ids:
            self.allies_ids.append(nation_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def add_enemy(self, nation_id: EntityId) -> None:
        """Add an enemy nation."""
        if nation_id not in self.enemies_ids:
            self.enemies_ids.append(nation_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
