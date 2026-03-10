"""Unit tests for ArtifactSet entity."""

import pytest

from src.domain.entities.artifact_set import ArtifactSet


class TestArtifactSetEntity:
    def test_create_artifact_set_with_defaults(self):
        artifact_set = ArtifactSet.create(
            tenant_id="tenant-1",
            set_name="Relics of Dawn",
            set_type="armor",
            total_pieces=4,
        )

        assert artifact_set.tenant_id == "tenant-1"
        assert artifact_set.set_name == "Relics of Dawn"
        assert artifact_set.set_type == "armor"
        assert artifact_set.total_pieces == 4
        assert artifact_set.tier == "legendary"
        assert artifact_set.rarity == "legendary"

    def test_create_artifact_set_with_custom_tier_and_rarity(self):
        artifact_set = ArtifactSet.create(
            tenant_id="tenant-1",
            set_name="Relics of Dawn",
            set_type="mixed",
            total_pieces=5,
            tier="mythical",
            rarity="divine",
        )

        assert artifact_set.tier == "mythical"
        assert artifact_set.rarity == "divine"

    def test_create_artifact_set_with_invalid_tier_raises_error(self):
        with pytest.raises(ValueError, match="tier must be one of"):
            ArtifactSet.create(
                tenant_id="tenant-1",
                set_name="Relics of Dawn",
                set_type="armor",
                total_pieces=4,
                tier="common",
            )