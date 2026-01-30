"""
LegalSystem Entity - Framework of laws and legal institutions
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


class LegalSystemType(str, Enum):
    """Types of legal systems."""
    COMMON_LAW = "common_law"
    CIVIL_LAW = "civil_law"
    RELIGIOUS_LAW = "religious_law"
    CUSTOMARY_LAW = "customary_law"
    MIXED = "mixed"
    MAGICAL_LAW = "magical_law"
    FEUDAL_LAW = "feudal_law"


class TrialType(str, Enum):
    """Types of trials."""
    JUDGE_ONLY = "judge_only"
    JURY_TRIAL = "jury_trial"
    TRIAL_BY_COMBAT = "trial_by_combat"
    TRIAL_BY_ORDEAL = "trial_by_ordeal"
    DIVINE_JUDGMENT = "divine_judgment"
    MAGICAL_TEST = "magical_test"


@dataclass
class LegalSystem:
    """
    LegalSystem represents the framework of laws and legal institutions.
    
    Invariants:
    - Must be linked to a nation
    - Name cannot be empty
    - Must specify a trial type
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    
    nation_id: Optional[EntityId]
    
    name: str
    description: Description
    
    legal_system_type: LegalSystemType
    
    # Courts and judiciary
    court_hierarchy: List[str]  # e.g., ["Local", "Regional", "Supreme"]
    court_ids: List[EntityId]  # Location IDs for courts
    supreme_court_id: Optional[EntityId]
    
    # Judges and lawyers
    judge_title: Optional[str]  # e.g., "Judge", "Magistrate", "Justiciar"
    lawyer_title: Optional[str]  # e.g., "Advocate", "Attorney"
    prosecutor_title: Optional[str]
    
    # Trial procedure
    trial_type: TrialType
    trial_procedure: Optional[str]  # Description of how trials work
    jury_system: Optional[str]  # e.g., "12 citizens", "Elders council"
    appeals_process: Optional[str]
    
    # Evidence and testimony
    evidence_rules: Optional[str]
    testimony_rules: Optional[str]
    
    # Punishment
    philosophy_of_punishment: Optional[str]  # e.g., "Retributive", "Rehabilitative"
    imprisonment_systems: List[str]
    capital_punishment: bool
    capital_crimes: List[str]
    
    # Legal professionals
    law_enforcement_agencies: List[str]
    legal_education: Optional[str]  # How lawyers are trained
    
    # Sources of law
    primary_sources: List[str]  # e.g., ["Constitution", "Statutes", "Precedent"]
    secondary_sources: List[str]
    
    # Constitution
    constitution_id: Optional[EntityId]
    
    # History
    founding_date: Optional[str]
    foreign_influences: List[EntityId]  # Legal systems that influenced this one
    
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
            raise InvariantViolation("LegalSystem name cannot be empty")
        
        if not self.nation_id:
            raise InvariantViolation("LegalSystem must be linked to a nation")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        nation_id: EntityId,
        name: str,
        description: Description,
        legal_system_type: LegalSystemType = LegalSystemType.CIVIL_LAW,
        trial_type: TrialType = TrialType.JUDGE_ONLY,
    ) -> 'LegalSystem':
        """
        Factory method for creating a new LegalSystem.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            nation_id=nation_id,
            name=name,
            description=description,
            legal_system_type=legal_system_type,
            court_hierarchy=[],
            court_ids=[],
            supreme_court_id=None,
            judge_title="Judge",
            lawyer_title="Advocate",
            prosecutor_title="Prosecutor",
            trial_type=trial_type,
            trial_procedure=None,
            jury_system=None,
            appeals_process=None,
            evidence_rules=None,
            testimony_rules=None,
            philosophy_of_punishment=None,
            imprisonment_systems=[],
            capital_punishment=False,
            capital_crimes=[],
            law_enforcement_agencies=[],
            legal_education=None,
            primary_sources=[],
            secondary_sources=[],
            constitution_id=None,
            founding_date=None,
            foreign_influences=[],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_capital_crime(self, crime: str) -> None:
        """Add a capital crime."""
        if crime not in self.capital_crimes:
            self.capital_crimes.append(crime)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def set_capital_punishment(self, enabled: bool) -> None:
        """Enable or disable capital punishment."""
        object.__setattr__(self, 'capital_punishment', enabled)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
