"""
UserScenario Entity

A UserScenario represents user-created narrative/story content.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    ScenarioStatus,
    Genre,
)


@dataclass
class UserScenario:
    """
    UserScenario entity representing user-created story scenarios.
    
    Invariants:
    - Must belong to exactly one tenant and author
    - Version increases monotonically
    - Name must be non-empty
    - Chapter count must be non-negative
    - Estimated play time must be positive
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    author_id: EntityId
    name: str
    description: Description
    status: ScenarioStatus
    
    # Story metadata
    genre: Optional[Genre]
    chapter_count: int
    estimated_playtime_minutes: int
    
    # Content details
    starting_location_id: Optional[EntityId]
    required_level: Optional[int]
    recommended_level: Optional[int]
    
    # Stats
    play_count: int
    completion_count: int
    rating: float  # Average rating (0.0-5.0)
    rating_count: int
    
    # Technical details
    dialogue_line_count: Optional[int]
    choice_count: Optional[int]
    ending_count: Optional[int]
    
    # Workshop integration
    workshop_entry_id: Optional[EntityId]
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise ValueError(
                "Updated timestamp must be >= created timestamp"
            )
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Scenario name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Scenario name must be <= 255 characters")
        
        if self.chapter_count < 0:
            raise ValueError("Chapter count cannot be negative")
        
        if self.estimated_playtime_minutes <= 0:
            raise ValueError("Estimated playtime must be positive")
        
        if self.required_level is not None and self.required_level < 1:
            raise ValueError("Required level must be at least 1")
        
        if self.recommended_level is not None and self.recommended_level < 1:
            raise ValueError("Recommended level must be at least 1")
        
        if self.required_level is not None and self.recommended_level is not None:
            if self.required_level > self.recommended_level:
                raise ValueError("Required level cannot exceed recommended level")
        
        if self.play_count < 0:
            raise ValueError("Play count cannot be negative")
        
        if self.completion_count < 0:
            raise ValueError("Completion count cannot be negative")
        
        if self.rating < 0.0 or self.rating > 5.0:
            raise ValueError("Rating must be between 0.0 and 5.0")
        
        if self.rating_count < 0:
            raise ValueError("Rating count cannot be negative")
        
        if self.dialogue_line_count is not None and self.dialogue_line_count < 0:
            raise ValueError("Dialogue line count cannot be negative")
        
        if self.choice_count is not None and self.choice_count < 0:
            raise ValueError("Choice count cannot be negative")
        
        if self.ending_count is not None and self.ending_count < 0:
            raise ValueError("Ending count cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        author_id: EntityId,
        name: str,
        description: Description,
        estimated_playtime_minutes: int,
        status: ScenarioStatus = ScenarioStatus.DRAFT,
        genre: Optional[Genre] = None,
        chapter_count: int = 0,
        starting_location_id: Optional[EntityId] = None,
        required_level: Optional[int] = None,
        recommended_level: Optional[int] = None,
        play_count: int = 0,
        completion_count: int = 0,
        rating: float = 0.0,
        rating_count: int = 0,
        dialogue_line_count: Optional[int] = None,
        choice_count: Optional[int] = None,
        ending_count: Optional[int] = None,
        workshop_entry_id: Optional[EntityId] = None,
    ) -> 'UserScenario':
        """
        Factory method for creating a new UserScenario.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            author_id=author_id,
            name=name,
            description=description,
            status=status,
            genre=genre,
            chapter_count=chapter_count,
            estimated_playtime_minutes=estimated_playtime_minutes,
            starting_location_id=starting_location_id,
            required_level=required_level,
            recommended_level=recommended_level,
            play_count=play_count,
            completion_count=completion_count,
            rating=rating,
            rating_count=rating_count,
            dialogue_line_count=dialogue_line_count,
            choice_count=choice_count,
            ending_count=ending_count,
            workshop_entry_id=workshop_entry_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update scenario description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def change_status(self, new_status: ScenarioStatus) -> None:
        """Change scenario status (e.g., from draft to published)."""
        if self.status == new_status:
            return
        
        object.__setattr__(self, 'status', new_status)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def increment_plays(self) -> None:
        """Increment play count."""
        object.__setattr__(self, 'play_count', self.play_count + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def increment_completions(self) -> None:
        """Increment completion count."""
        object.__setattr__(self, 'completion_count', self.completion_count + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def add_rating(self, rating: float) -> None:
        """
        Add a user rating and recalculate average.
        
        Args:
            rating: Rating value (0.0-5.0)
        """
        if rating < 0.0 or rating > 5.0:
            raise ValueError("Rating must be between 0.0 and 5.0")
        
        total_score = self.rating * self.rating_count + rating
        object.__setattr__(self, 'rating_count', self.rating_count + 1)
        object.__setattr__(self, 'rating', total_score / self.rating_count)
        object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def link_workshop(self, entry_id: EntityId) -> None:
        """Link scenario to workshop entry."""
        object.__setattr__(self, 'workshop_entry_id', entry_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        genre_str = f" [{self.genre.value}]" if self.genre else ""
        return f"UserScenario({self.name}{genre_str}, ~{self.estimated_playtime_minutes}min, ⭐{self.rating:.1f})"
    
    def __repr__(self) -> str:
        return (
            f"UserScenario(id={self.id}, name='{self.name}', "
            f"author_id={self.author_id}, status={self.status})"
        )
