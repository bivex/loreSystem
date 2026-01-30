"""Heatmap Entity

A Heatmap represents data visualization showing where players
spend most time or where events occur in game. Critical for
level design and balancing decisions.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime, timedelta

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class Heatmap:
    """Data visualization for player behavior and spatial analysis."""
    
    tenant_id: TenantId
    id: Optional[EntityId] = None
    name: str  # "Combat Heatmap", "Spawn Point Analysis"
    heatmap_type: str  # "player_spawn", "death", "movement", "interaction"
    world_id: EntityId
    location_type: str  # "zone", "dungeon", "safe_area"
    data_points: List[Dict[str, float]] = field(default_factory=list)  # {x, y, z, intensity}
    collection_period: timedelta  # Time period this data represents
    grid_size: int  # Size of spatial grid (e.g., 100x100)
    resolution: int  # Pixel or meter resolution
    created_at: Timestamp
    updated_at: Timestamp
    version: Version = field(default_factory=Version)
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Heatmap name cannot be empty")
        
        if self.grid_size <= 0:
            raise InvariantViolation("Grid size must be positive")
        
        if self.resolution <= 0:
            raise InvariantViolation("Resolution must be positive")
        
        if self.collection_period.total_seconds() < 1:
            raise InvariantViolation("Collection period must be >= 1 second")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        heatmap_type: str,
        world_id: EntityId,
        location_type: str = "zone",
        collection_period: timedelta = timedelta(days=7),
        grid_size: int = 100,
        resolution: int = 1,
        data_points: Optional[List[Dict[str, float]]] = None,
    ) -> "Heatmap":
        """Factory method to create a new Heatmap."""
        now = Timestamp.now()
        
        return cls(
            tenant_id=tenant_id,
            name=name.strip(),
            heatmap_type=heatmap_type,
            world_id=world_id,
            location_type=location_type,
            data_points=data_points or [],
            collection_period=collection_period,
            grid_size=grid_size,
            resolution=resolution,
            created_at=now,
            updated_at=now,
            version=Version(1, 0, 0),
        )
    
    def add_data_point(self, x: float, y: float, z: float, intensity: float) -> "Heatmap":
        """Add a single data point to the heatmap."""
        self.data_points.append({
            "x": x,
            "y": y,
            "z": z,
            "intensity": intensity
        })
        self.updated_at = Timestamp.now()
        return self
    
    def aggregate_hotspots(self) -> List[Dict[str, float]]:
        """Identify hotspots in the heatmap."""
        # Simple clustering algorithm
        if len(self.data_points) < 5:
            return []
        
        # Return top 10% most intense points
        sorted_points = sorted(self.data_points, key=lambda p: p["intensity"], reverse=True)
        hotspot_count = max(1, len(sorted_points) // 10)
        return sorted_points[:hotspot_count]
    
    def get_intensity_at(self, x: float, y: float, z: float = 0.0) -> float:
        """Get estimated intensity at a specific coordinate."""
        # In a real implementation, this would use interpolation
        # For now, return average intensity
        if not self.data_points:
            return 0.0
        
        total_intensity = sum(p["intensity"] for p in self.data_points)
        return total_intensity / len(self.data_points)
    
    def __str__(self) -> str:
        return f"Heatmap({self.name}, type={self.heatmap_type}, {len(self.data_points)} points)"
    
    def __repr__(self) -> str:
        return f"<Heatmap {self.name}: {self.heatmap_type} heatmap>"
