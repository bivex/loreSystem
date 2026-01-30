"""
VoiceActor Entity

A VoiceActor is a person who provides voice talent for characters.
"""
from dataclasses import dataclass, field
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


class VoiceActorStatus(str, Enum):
    """Voice actor availability status."""
    ACTIVE = "active"
    RETIRED = "retired"
    DECEASED = "deceased"
    UNAVAILABLE = "unavailable"


@dataclass
class VoiceActor:
    """
    VoiceActor entity representing voice talent.
    
    Invariants:
    - Must have a name
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: Optional[EntityId]
    name: str
    description: Optional[Description]
    status: VoiceActorStatus
    language: str  # Primary language
    character_ids: List[EntityId]  # Characters voiced
    voice_samples: List[str]  # URLs to voice samples
    agency: Optional[str]  # Talent agency
    contact_info: Optional[str]
    hourly_rate: Optional[float]
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Voice actor name cannot be empty")
        
        if not self.language or len(self.language.strip()) == 0:
            raise InvariantViolation("Language cannot be empty")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if self.hourly_rate is not None and self.hourly_rate < 0:
            raise InvariantViolation("Hourly rate cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        language: str,
        world_id: Optional[EntityId] = None,
        description: Optional[Description] = None,
        status: VoiceActorStatus = VoiceActorStatus.ACTIVE,
        character_ids: Optional[List[EntityId]] = None,
        voice_samples: Optional[List[str]] = None,
        agency: Optional[str] = None,
        contact_info: Optional[str] = None,
        hourly_rate: Optional[float] = None,
    ) -> 'VoiceActor':
        """Factory method for creating a new VoiceActor."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            status=status,
            language=language,
            character_ids=character_ids or [],
            voice_samples=voice_samples or [],
            agency=agency,
            contact_info=contact_info,
            hourly_rate=hourly_rate,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_character(self, character_id: EntityId) -> None:
        """Add a character to voice actor's portfolio."""
        if character_id in self.character_ids:
            return
        
        self.character_ids.append(character_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"VoiceActor({self.name}, {self.language})"
    
    def __repr__(self) -> str:
        return (
            f"VoiceActor(id={self.id}, name='{self.name}', "
            f"language={self.language}, status={self.status})"
        )
