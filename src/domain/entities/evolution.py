"""Evolution entity for biological adaptation."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Evolution:
    """Represents evolution and adaptation mechanisms."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        species_id: str,
        evolution_type: str,
        trait_name: str,
        mutation_rate: float,
        selection_pressure: float,
        generation_count: int,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.species_id = species_id
        self.evolution_type = evolution_type
        self.trait_name = trait_name
        self.mutation_rate = mutation_rate
        self.selection_pressure = selection_pressure
        self.generation_count = generation_count
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        species_id: str,
        evolution_type: str,
        trait_name: str,
        mutation_rate: float = 0.01,
        selection_pressure: float = 0.5,
        generation_count: int = 100,
    ) -> "Evolution":
        """Factory method to create evolution mechanics."""
        if not species_id or not species_id.strip():
            raise ValueError("Species ID is required")
        if not trait_name or not trait_name.strip():
            raise ValueError("Trait name is required")
        if not (0 <= mutation_rate <= 1) or not (0 <= selection_pressure <= 1):
            raise ValueError("Rates must be between 0 and 1")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            species_id=species_id.strip(),
            evolution_type=evolution_type,
            trait_name=trait_name.strip(),
            mutation_rate=mutation_rate,
            selection_pressure=selection_pressure,
            generation_count=generation_count,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate evolution data."""
        return (
            isinstance(self.species_id, str) and len(self.species_id) > 0
            and isinstance(self.trait_name, str) and len(self.trait_name) > 0
            and 0 <= self.mutation_rate <= 1
            and 0 <= self.selection_pressure <= 1
        )

    def __repr__(self) -> str:
        return f"<Evolution {self.species_id}: {self.trait_name}, rate {self.mutation_rate}>"
