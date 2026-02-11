"""Atmosphere entity for environmental ambience."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Atmosphere:
    """Represents atmospheric conditions and ambience."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        atmosphere_type: str,
        location_id: UUID,
        temperature_celsius: float,
        humidity_percent: float,
        wind_speed_kmh: float,
        visibility_km: float,
        air_pressure_hpa: float,
        audio_profile: str,
        visual_tint: str,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.atmosphere_type = atmosphere_type
        self.location_id = location_id
        self.temperature_celsius = temperature_celsius
        self.humidity_percent = humidity_percent
        self.wind_speed_kmh = wind_speed_kmh
        self.visibility_km = visibility_km
        self.air_pressure_hpa = air_pressure_hpa
        self.audio_profile = audio_profile
        self.visual_tint = visual_tint
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        atmosphere_type: str,
        location_id: UUID,
        temperature_celsius: float = 20.0,
        humidity_percent: float = 50.0,
        wind_speed_kmh: float = 10.0,
    ) -> "Atmosphere":
        """Factory method to create a new atmosphere."""
        if not name or not name.strip():
            raise ValueError("Atmosphere name is required")
        if not -50.0 <= temperature_celsius <= 60.0:
            raise ValueError("Temperature must be between -50 and 60 Celsius")
        if not 0.0 <= humidity_percent <= 100.0:
            raise ValueError("Humidity must be between 0 and 100 percent")
        if wind_speed_kmh < 0:
            raise ValueError("Wind speed cannot be negative")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            atmosphere_type=atmosphere_type,
            location_id=location_id,
            temperature_celsius=temperature_celsius,
            humidity_percent=humidity_percent,
            wind_speed_kmh=wind_speed_kmh,
            visibility_km=10.0,
            air_pressure_hpa=1013.25,
            audio_profile="default",
            visual_tint="#ffffff",
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate atmosphere data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.temperature_celsius, (int, float)) and -50.0 <= self.temperature_celsius <= 60.0
            and isinstance(self.humidity_percent, (int, float)) and 0.0 <= self.humidity_percent <= 100.0
        )

    def __repr__(self) -> str:
        return f"<Atmosphere {self.name}: {self.temperature_celsius}°C, {self.humidity_percent}% humidity>"
