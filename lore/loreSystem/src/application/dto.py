"""
Data Transfer Objects (DTOs)

DTOs are simple data structures for transferring data between layers.
They are separate from domain entities to avoid coupling.
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class CreateWorldDTO:
    """Input for creating a new world."""
    tenant_id: int
    name: str
    description: str


@dataclass
class WorldDTO:
    """Output representing a world."""
    id: int
    tenant_id: int
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    version: int


@dataclass
class CreateCharacterDTO:
    """Input for creating a new character."""
    tenant_id: int
    world_id: int
    name: str
    backstory: str
    abilities: Optional[List['AbilityDTO']] = None


@dataclass
class AbilityDTO:
    """Represents a character ability."""
    name: str
    description: str
    power_level: int


@dataclass
class CharacterDTO:
    """Output representing a character."""
    id: int
    tenant_id: int
    world_id: int
    world_name: str
    name: str
    backstory: str
    status: str
    abilities: List[AbilityDTO]
    ability_count: int
    avg_power_level: float
    created_at: datetime
    updated_at: datetime
    version: int


@dataclass
class CreateEventDTO:
    """Input for creating a new event."""
    tenant_id: int
    world_id: int
    name: str
    description: str
    start_date: datetime
    participant_ids: List[int]
    end_date: Optional[datetime] = None


@dataclass
class EventDTO:
    """Output representing an event."""
    id: int
    tenant_id: int
    world_id: int
    world_name: str
    name: str
    description: str
    start_date: datetime
    end_date: Optional[datetime]
    outcome: str
    participant_ids: List[int]
    participant_names: List[str]
    is_ongoing: bool
    created_at: datetime
    updated_at: datetime
    version: int


@dataclass
class ProposeImprovementDTO:
    """Input for proposing an improvement."""
    tenant_id: int
    entity_type: str  # world, character, event
    entity_id: int
    suggestion: str
    git_commit_hash: str


@dataclass
class ImprovementDTO:
    """Output representing an improvement."""
    id: int
    tenant_id: int
    entity_type: str
    entity_id: int
    entity_name: str
    suggestion: str
    status: str
    git_commit_hash: str
    created_at: datetime


@dataclass
class CreateRequirementDTO:
    """Input for creating a requirement."""
    tenant_id: int
    description: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None


@dataclass
class CreateItemDTO:
    """Input for creating a new item."""
    tenant_id: int
    world_id: int
    name: str
    description: str
    item_type: str
    rarity: Optional[str] = None


@dataclass
class ItemDTO:
    """Output representing an item."""
    id: int
    tenant_id: int
    world_id: int
    world_name: str
    name: str
    description: str
    item_type: str
    rarity: Optional[str]
    created_at: datetime
    updated_at: datetime
    version: int
