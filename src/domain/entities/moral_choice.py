"""MoralChoice Entity

A MoralChoice is a decision point with ethical implications.
Often used in RPGs with morality systems (Mass Effect, Witcher, etc.).
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation, InvalidState


class MoralAlignment(str, Enum):
    """Moral alignments of choices."""
    GOOD = "good"
    EVIL = "evil"
    NEUTRAL = "neutral"
    CHAOTIC = "chaotic"
    LAWFUL = "lawful"
    SELFISH = "selfish"
    ALTRUISTIC = "altruistic"


class ChoiceUrgency(str, Enum):
    """Urgency levels for choices."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    IMMEDIATE = "immediate"


@dataclass
class MoralChoice:
    """
    MoralChoice entity representing an ethical decision.
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    campaign_id: Optional[EntityId]
    prompt: str
    description: Optional[Description]
    choice_alignment: MoralAlignment
    urgency: ChoiceUrgency
    options: List[Dict[str, str]]
    consequence_ids: List[EntityId]
    is_reversible: bool
    time_limit_seconds: Optional[int]
    affects_reputation: bool
    affects_karma: bool
    character_ids: List[EntityId]
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        self._validate_invariants()
    
    def _validate_invariants(self):
        if not self.prompt or len(self.prompt.strip()) == 0:
            raise InvariantViolation("Choice prompt cannot be empty")
        if len(self.options) < 2:
            raise InvariantViolation("Moral choice must have at least 2 options")
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("Updated timestamp must be >= created timestamp")
        if self.time_limit_seconds is not None and self.time_limit_seconds < 1:
            raise InvariantViolation("Time limit must be >= 1 second")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        prompt: str,
        options: List[Dict[str, str]],
        choice_alignment: MoralAlignment = MoralAlignment.NEUTRAL,
        urgency: ChoiceUrgency = ChoiceUrgency.LOW,
        campaign_id: Optional[EntityId] = None,
        description: Optional[Description] = None,
        consequence_ids: Optional[List[EntityId]] = None,
        is_reversible: bool = False,
        time_limit_seconds: Optional[int] = None,
        affects_reputation: bool = True,
        affects_karma: bool = True,
        character_ids: Optional[List[EntityId]] = None,
    ) -> 'MoralChoice':
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            campaign_id=campaign_id,
            prompt=prompt,
            description=description,
            choice_alignment=choice_alignment,
            urgency=urgency,
            options=options,
            consequence_ids=consequence_ids or [],
            is_reversible=is_reversible,
            time_limit_seconds=time_limit_seconds,
            affects_reputation=affects_reputation,
            affects_karma=affects_karma,
            character_ids=character_ids or [],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, description: str) -> None:
        self.description = Description(description)
        self.updated_at = Timestamp.now()
        self.version = self.version.increment()
    
    def add_option(self, option: Dict[str, str]) -> None:
        if 'id' not in option or 'text' not in option:
            raise InvariantViolation("Option must have 'id' and 'text'")
        self.options.append(option)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_urgent(self) -> bool:
        return self.urgency in [ChoiceUrgency.HIGH, ChoiceUrgency.IMMEDIATE]
    
    def has_time_limit(self) -> bool:
        return self.time_limit_seconds is not None
    
    def __str__(self) -> str:
        return f"MoralChoice({self.choice_alignment}, options={len(self.options)})"
    
    def __repr__(self) -> str:
        return f"MoralChoice(id={self.id}, prompt='{self.prompt[:50]}...', alignment={self.choice_alignment})"
