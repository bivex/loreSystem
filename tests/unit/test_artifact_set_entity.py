"""Unit tests for ArtifactSet entity."""

import pytest

from src.domain.entities.artifact_set import ArtifactSet
from src.domain.exceptions import InvariantViolation
from src.domain.value_objects.common import EntityId, TenantId


class TestArtifactSetEntity:
    def test_create_artifact_set_with_defaults(self):
        artifact_set = ArtifactSet.create(
            tenant_id=TenantId(1),
            world_id=EntityId(10),
            name="Relics of Dawn",
            description="A restored regalia of dawn-era guardians.",
            set_type="armor",
            total_pieces=4,
        )

        assert artifact_set.tenant_id == TenantId(1)
        assert artifact_set.world_id == EntityId(10)
        assert artifact_set.set_name == "Relics of Dawn"
        assert artifact_set.set_type == "armor"
        assert artifact_set.total_pieces == 4
        assert artifact_set.tier == "legendary"
        assert artifact_set.rarity == "legendary"

    def test_create_artifact_set_with_custom_rarity(self):
        artifact_set = ArtifactSet.create(
            tenant_id=TenantId(1),
            world_id=EntityId(10),
            name="Relics of Dawn",
            description="A mixed set assembled from lost vaults.",
            set_type="mixed",
            total_pieces=5,
            rarity="divine",
            set_bonus="Unlocks the final dawn barrier.",
        )

        assert artifact_set.rarity == "divine"
        assert artifact_set.tier == "divine"
        assert artifact_set.set_bonus == "Unlocks the final dawn barrier."

    def test_create_artifact_set_with_invalid_rarity_raises_error(self):
        with pytest.raises(InvariantViolation, match="rarity must be one of"):
            ArtifactSet.create(
                tenant_id=TenantId(1),
                world_id=EntityId(10),
                name="Relics of Dawn",
                description="A broken regalia.",
                set_type="armor",
                total_pieces=4,
                rarity="common",
            )