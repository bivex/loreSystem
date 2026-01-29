"""
Tests for Page entity with edge cases and comprehensive coverage.
"""
import pytest
from datetime import timedelta

from src.domain.entities.page import Page
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    PageName,
    Content,
    Timestamp,
)
from src.domain.exceptions import InvariantViolation


def make_basic_page():
    """Factory for basic page."""
    return Page.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name=PageName("Test Page"),
        content=Content("Test content for the page."),
        template_id=EntityId(10),
        parent_id=None,
    )


def make_page_with_tags_and_images():
    """Factory for page with tags and images."""
    return Page.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name=PageName("Rich Page"),
        content=Content("Content with media."),
        template_id=EntityId(10),
        tag_ids=[EntityId(20), EntityId(21)],
        image_ids=[EntityId(30)],
    )


class TestPageCreation:
    """Test page creation scenarios."""

    def test_create_basic_page(self):
        """Test creating a basic page."""
        page = make_basic_page()
        assert page.name.value == "Test Page"
        assert page.content.value == "Test content for the page."
        assert page.template_id == EntityId(10)
        assert page.parent_id is None
        assert page.tag_ids == []
        assert page.image_ids == []
        assert page.version.value == 1

    def test_create_page_with_all_fields(self):
        """Test creating page with all optional fields."""
        page = make_page_with_tags_and_images()
        assert len(page.tag_ids) == 2
        assert len(page.image_ids) == 1
        assert page.template_id == EntityId(10)

    def test_create_page_empty_content_fails(self):
        """Test that empty content raises error."""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            Page.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name=PageName("Test"),
                content=Content(""),
            )

    def test_create_page_whitespace_content_fails(self):
        """Test that whitespace-only content raises error."""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            Page.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name=PageName("Test"),
                content=Content("   \n\t   "),
            )


class TestPageOperations:
    """Test page modification operations."""

    def test_update_content(self):
        """Test updating page content."""
        page = make_basic_page()
        old_version = page.version.value

        new_content = Content("Updated content.")
        page.update_content(new_content)

        assert page.content == new_content
        assert page.version.value == old_version + 1
        assert page.updated_at.value > page.created_at.value

    def test_update_content_same_content_no_change(self):
        """Test updating to same content doesn't increment version."""
        page = make_basic_page()
        old_version = page.version.value
        old_updated = page.updated_at

        page.update_content(Content("Test content for the page."))

        assert page.version.value == old_version
        assert page.updated_at == old_updated

    def test_change_template(self):
        """Test changing page template."""
        page = make_basic_page()
        old_version = page.version.value

        new_template = EntityId(15)
        page.change_template(new_template)

        assert page.template_id == new_template
        assert page.version.value == old_version + 1

    def test_change_template_to_none(self):
        """Test changing template to None."""
        page = make_basic_page()
        page.change_template(None)
        assert page.template_id is None

    def test_change_template_same_no_change(self):
        """Test changing to same template doesn't update."""
        page = make_basic_page()
        old_version = page.version.value
        page.change_template(EntityId(10))
        assert page.version.value == old_version


class TestPageTags:
    """Test tag management operations."""

    def test_add_tag(self):
        """Test adding a tag."""
        page = make_basic_page()
        old_version = page.version.value

        tag_id = EntityId(20)
        page.add_tag(tag_id)

        assert tag_id in page.tag_ids
        assert page.version.value == old_version + 1

    def test_add_duplicate_tag_no_change(self):
        """Test adding duplicate tag doesn't change anything."""
        page = make_page_with_tags_and_images()
        old_version = page.version.value
        old_count = len(page.tag_ids)

        page.add_tag(EntityId(20))  # Already exists

        assert len(page.tag_ids) == old_count
        assert page.version.value == old_version

    def test_remove_tag(self):
        """Test removing a tag."""
        page = make_page_with_tags_and_images()
        old_version = page.version.value

        tag_id = EntityId(20)
        page.remove_tag(tag_id)

        assert tag_id not in page.tag_ids
        assert page.version.value == old_version + 1

    def test_remove_nonexistent_tag_no_change(self):
        """Test removing non-existent tag doesn't change anything."""
        page = make_basic_page()
        old_version = page.version.value

        page.remove_tag(EntityId(99))

        assert page.version.value == old_version


class TestPageImages:
    """Test image management operations."""

    def test_add_image(self):
        """Test adding an image."""
        page = make_basic_page()
        old_version = page.version.value

        image_id = EntityId(30)
        page.add_image(image_id)

        assert image_id in page.image_ids
        assert page.version.value == old_version + 1

    def test_add_duplicate_image_no_change(self):
        """Test adding duplicate image doesn't change anything."""
        page = make_page_with_tags_and_images()
        old_version = page.version.value
        old_count = len(page.image_ids)

        page.add_image(EntityId(30))  # Already exists

        assert len(page.image_ids) == old_count
        assert page.version.value == old_version

    def test_remove_image(self):
        """Test removing an image."""
        page = make_page_with_tags_and_images()
        old_version = page.version.value

        image_id = EntityId(30)
        page.remove_image(image_id)

        assert image_id not in page.image_ids
        assert page.version.value == old_version + 1

    def test_remove_nonexistent_image_no_change(self):
        """Test removing non-existent image doesn't change anything."""
        page = make_basic_page()
        old_version = page.version.value

        page.remove_image(EntityId(99))

        assert page.version.value == old_version


class TestPageHierarchy:
    """Test hierarchical operations."""

    def test_move_to_parent(self):
        """Test moving page to new parent."""
        page = make_basic_page()
        old_version = page.version.value

        new_parent = EntityId(5)
        page.move_to_parent(new_parent)

        assert page.parent_id == new_parent
        assert page.version.value == old_version + 1

    def test_move_to_same_parent_no_change(self):
        """Test moving to same parent doesn't update."""
        page = make_basic_page()
        page.move_to_parent(EntityId(5))
        old_version = page.version.value

        page.move_to_parent(EntityId(5))

        assert page.version.value == old_version

    def test_move_to_none_parent(self):
        """Test moving to None parent."""
        page = Page.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name=PageName("Child Page"),
            content=Content("Content"),
            parent_id=EntityId(5),
        )

        page.move_to_parent(None)
        assert page.parent_id is None


class TestPageInvariants:
    """Test invariant enforcement."""

    def test_post_init_validates_invariants(self):
        """Test that invariants are checked after construction."""
        page = make_basic_page()
        # Invariants should have been validated during construction
        assert page.created_at <= page.updated_at


class TestPageStringRepresentations:
    """Test string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        page = make_basic_page()
        assert str(page) == "Page(Test Page)"

    def test_repr_representation(self):
        """Test __repr__ method."""
        page = make_basic_page()
        repr_str = repr(page)
        assert "Page(id=None" in repr_str
        assert "name='Test Page'" in repr_str
        assert "version=v1" in repr_str