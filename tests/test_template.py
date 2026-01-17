"""
Tests for Template entity with edge cases and comprehensive coverage.
"""
import pytest

from src.domain.entities.template import Template
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    TemplateName,
    Content,
    TemplateType,
)
from src.domain.exceptions import InvariantViolation


def make_basic_template():
    """Factory for basic template."""
    return Template.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name=TemplateName("Basic Template"),
        description="A basic page template",
        template_type=TemplateType.PAGE,
        content=Content("Template structure here."),
    )


def make_template_with_runes():
    """Factory for template with runes."""
    return Template.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name=TemplateName("Complex Template"),
        description="Template with sub-templates",
        template_type=TemplateType.PAGE,
        content=Content("Main template content."),
        rune_ids=[EntityId(20), EntityId(21)],
        parent_template_id=EntityId(10),
    )


def make_rune_template():
    """Factory for rune template."""
    return Template.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name=TemplateName("Header Rune"),
        description="A reusable header section",
        template_type=TemplateType.RUNE,
        content=Content("Header content."),
    )


class TestTemplateCreation:
    """Test template creation scenarios."""

    def test_create_basic_template(self):
        """Test creating a basic template."""
        template = make_basic_template()
        assert template.name.value == "Basic Template"
        assert template.description == "A basic page template"
        assert template.template_type == TemplateType.PAGE
        assert template.rune_ids == []
        assert template.parent_template_id is None
        assert template.version.value == 1

    def test_create_template_with_runes(self):
        """Test creating template with runes."""
        template = make_template_with_runes()
        assert len(template.rune_ids) == 2
        assert template.parent_template_id == EntityId(10)

    def test_create_rune_template(self):
        """Test creating a rune template."""
        template = make_rune_template()
        assert template.template_type == TemplateType.RUNE
        assert template.is_rune()

    def test_create_template_empty_content_fails(self):
        """Test that empty content raises error."""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            Template.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name=TemplateName("Test"),
                description="Test",
                template_type=TemplateType.PAGE,
                content=Content(""),
            )

    def test_create_template_whitespace_content_fails(self):
        """Test that whitespace-only content raises error."""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            Template.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name=TemplateName("Test"),
                description="Test",
                template_type=TemplateType.PAGE,
                content=Content("   \n\t   "),
            )


class TestTemplateOperations:
    """Test template modification operations."""

    def test_update_content(self):
        """Test updating template content."""
        template = make_basic_template()
        old_version = template.version.value

        new_content = Content("Updated template structure.")
        template.update_content(new_content)

        assert template.content == new_content
        assert template.version.value == old_version + 1

    def test_update_content_same_no_change(self):
        """Test updating to same content doesn't increment version."""
        template = make_basic_template()
        old_version = template.version.value

        template.update_content(Content("Template structure here."))

        assert template.version.value == old_version


class TestTemplateRunes:
    """Test rune management operations."""

    def test_add_rune(self):
        """Test adding a rune."""
        template = make_basic_template()
        old_version = template.version.value

        rune_id = EntityId(20)
        template.add_rune(rune_id)

        assert rune_id in template.rune_ids
        assert template.version.value == old_version + 1

    def test_add_duplicate_rune_no_change(self):
        """Test adding duplicate rune doesn't change anything."""
        template = make_template_with_runes()
        old_version = template.version.value
        old_count = len(template.rune_ids)

        template.add_rune(EntityId(20))  # Already exists

        assert len(template.rune_ids) == old_count
        assert template.version.value == old_version

    def test_remove_rune(self):
        """Test removing a rune."""
        template = make_template_with_runes()
        old_version = template.version.value

        rune_id = EntityId(20)
        template.remove_rune(rune_id)

        assert rune_id not in template.rune_ids
        assert template.version.value == old_version + 1

    def test_remove_nonexistent_rune_no_change(self):
        """Test removing non-existent rune doesn't change anything."""
        template = make_basic_template()
        old_version = template.version.value

        template.remove_rune(EntityId(99))

        assert template.version.value == old_version


class TestTemplateTypeMethods:
    """Test template type specific methods."""

    def test_is_rune_method(self):
        """Test is_rune method."""
        page_template = make_basic_template()
        rune_template = make_rune_template()

        assert not page_template.is_rune()
        assert rune_template.is_rune()


class TestTemplateInvariants:
    """Test invariant enforcement."""

    def test_updated_at_not_before_created_at(self):
        """Test that updated_at cannot be before created_at."""
        from datetime import timedelta
        from src.domain.value_objects.common import Timestamp

        template = make_basic_template()
        # Manually set invalid timestamps
        object.__setattr__(template, 'updated_at', Timestamp(template.created_at.value - timedelta(hours=1)))
        # Validation should fail when explicitly called
        with pytest.raises(InvariantViolation, match="Updated timestamp must be >= created timestamp"):
            template._validate_invariants()

    def test_post_init_validates_invariants(self):
        """Test that invariants are checked after construction."""
        from datetime import timedelta
        from src.domain.value_objects.common import Timestamp

        template = make_basic_template()
        # Try to set invalid updated_at
        with pytest.raises(InvariantViolation):
            object.__setattr__(template, 'updated_at', Timestamp(template.created_at.value - timedelta(hours=1)))
            template._validate_invariants()


class TestTemplateStringRepresentations:
    """Test string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        template = make_basic_template()
        assert str(template) == "Template(Basic Template, type=page)"

    def test_rune_str_representation(self):
        """Test __str__ method for rune."""
        template = make_rune_template()
        assert str(template) == "Template(Header Rune, type=rune)"

    def test_repr_representation(self):
        """Test __repr__ method."""
        template = make_basic_template()
        repr_str = repr(template)
        assert "Template(id=None" in repr_str
        assert "name='Basic Template'" in repr_str
        assert "type=page" in repr_str
        assert "version=v1" in repr_str