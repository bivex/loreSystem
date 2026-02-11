"""
CustomMap Entity

A CustomMap represents user-created playable map/level content.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    MapStatus,
    MapType,
    Difficulty,
)


@dataclass
class CustomMap:
    """
    CustomMap entity representing user-created game maps/levels.
    
    Invariants:
    - Must belong to exactly one tenant and author
    - Version increases monotonically
    - Name must be non-empty
    - Max players must be positive
    - Play count must be non-negative
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    author_id: EntityId
    name: str
    description: Description
    map_type: MapType
    status: MapStatus
    
    # Gameplay settings
    max_players: int
    min_players: Optional[int]
    difficulty: Optional[Difficulty]
    estimated_duration_minutes: Optional[int]
    
    # Stats
    play_count: int
    rating: float  # Average rating (0.0-5.0)
    rating_count: int
    favorite_count: int
    
    # Technical details
    world_id: Optional[EntityId]  # Base world this map extends
    tile_count: Optional[int]
    entity_count: Optional[int]
    checksum: Optional[str]
    
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
            raise ValueError("Map name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Map name must be <= 255 characters")
        
        if self.max_players < 1:
            raise ValueError("Max players must be at least 1")
        
        if self.min_players is not None and self.min_players < 1:
            raise ValueError("Min players must be at least 1")
        
        if self.min_players is not None and self.min_players > self.max_players:
            raise ValueError("Min players cannot exceed max players")
        
        if self.play_count < 0:
            raise ValueError("Play count cannot be negative")
        
        if self.rating < 0.0 or self.rating > 5.0:
            raise ValueError("Rating must be between 0.0 and 5.0")
        
        if self.rating_count < 0:
            raise ValueError("Rating count cannot be negative")
        
        if self.favorite_count < 0:
            raise ValueError("Favorite count cannot be negative")
        
        if self.tile_count is not None and self.tile_count < 0:
            raise ValueError("Tile count cannot be negative")
        
        if self.entity_count is not None and self.entity_count < 0:
            raise ValueError("Entity count cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        author_id: EntityId,
        name: str,
        description: Description,
        map_type: MapType,
        max_players: int,
        status: MapStatus = MapStatus.DRAFT,
        min_players: Optional[int] = None,
        difficulty: Optional[Difficulty] = None,
        estimated_duration_minutes: Optional[int] = None,
        play_count: int = 0,
        rating: float = 0.0,
        rating_count: int = 0,
        favorite_count: int = 0,
        world_id: Optional[EntityId] = None,
        tile_count: Optional[int] = None,
        entity_count: Optional[int] = None,
        checksum: Optional[str] = None,
        workshop_entry_id: Optional[EntityId] = None,
    ) -> 'CustomMap':
        """
        Factory method for creating a new CustomMap.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            author_id=author_id,
            name=name,
            description=description,
            map_type=map_type,
            status=status,
            max_players=max_players,
            min_players=min_players,
            difficulty=difficulty,
            estimated_duration_minutes=estimated_duration_minutes,
            play_count=play_count,
            rating=rating,
            rating_count=rating_count,
            favorite_count=favorite_count,
            world_id=world_id,
            tile_count=tile_count,
            entity_count=entity_count,
            checksum=checksum,
            workshop_entry_id=workshop_entry_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update map description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def change_status(self, new_status: MapStatus) -> None:
        """Change map status (e.g., from draft to published)."""
        if self.status == new_status:
            return
        
        object.__setattr__(self, 'status', new_status)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def increment_plays(self) -> None:
        """Increment play count."""
        object.__setattr__(self, 'play_count', self.play_count + 1)
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
    
    def toggle_favorite(self) -> bool:
        """Toggle favorite status (increment for demo, real implementation needs user tracking)."""
        object.__setattr__(self, 'favorite_count', self.favorite_count + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        return True
    
    def link_workshop(self, entry_id: EntityId) -> None:
        """Link map to workshop entry."""
        object.__setattr__(self, 'workshop_entry_id', entry_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        diff_str = f" [{self.difficulty.value}]" if self.difficulty else ""
        return f"CustomMap({self.name}, {self.map_type.value}, {self.min_players}-{self.max_players}p{diff_str})"
    
    def __repr__(self) -> str:
        return (
            f"CustomMap(id={self.id}, name='{self.name}', "
            f"author_id={self.author_id}, type={self.map_type})"
        )
