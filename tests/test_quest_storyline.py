# import pytest  # Commented out since pytest not available
from datetime import timedelta

from src.domain.entities.quest import Quest
from src.domain.entities.storyline import Storyline
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Timestamp,
    QuestStatus,
    StorylineType,
    Version,
)
from src.domain.exceptions import InvariantViolation, InvalidState


class TestQuest:
    """Test cases for Quest entity."""

    def test_quest_creation(self):
        """Test basic quest creation."""
        quest = Quest(
            id=EntityId(1),
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Quest",
            description=Description("A test quest"),
            objectives=["Objective 1", "Objective 2"],
            status=QuestStatus.ACTIVE,
            participant_ids=[EntityId(1)],
            reward_ids=[EntityId(2)],
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
            version=Version(1)
        )
        assert quest.name == "Test Quest"
        assert len(quest.objectives) == 2
        assert quest.status == QuestStatus.ACTIVE
        print("✓ test_quest_creation passed")

    def test_quest_invariant_no_objectives(self):
        """Test that quest must have at least one objective."""
        try:
            Quest(
                id=EntityId(1),
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name="Test Quest",
                description=Description("A test quest"),
                objectives=[],  # Empty objectives
                status=QuestStatus.ACTIVE,
                participant_ids=[EntityId(1)],
                reward_ids=[],
                created_at=Timestamp.now(),
                updated_at=Timestamp.now(),
                version=Version(1)
            )
            assert False, "Should have raised InvariantViolation"
        except InvariantViolation as e:
            assert "Quest must have at least one objective" in str(e)
            print("✓ test_quest_invariant_no_objectives passed")

    def test_quest_invariant_no_participants(self):
        """Test that quest must have at least one participant."""
        try:
            Quest(
                id=EntityId(1),
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name="Test Quest",
                description=Description("A test quest"),
                objectives=["Objective 1"],
                status=QuestStatus.ACTIVE,
                participant_ids=[],  # No participants
                reward_ids=[],
                created_at=Timestamp.now(),
                updated_at=Timestamp.now(),
                version=Version(1)
            )
            assert False, "Should have raised InvariantViolation"
        except InvariantViolation as e:
            assert "Quest must have at least one participant" in str(e)
            print("✓ test_quest_invariant_no_participants passed")

    def test_quest_complete_active_quest(self):
        """Test completing an active quest."""
        quest = Quest(
            id=EntityId(1),
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Quest",
            description=Description("A test quest"),
            objectives=["Objective 1"],
            status=QuestStatus.ACTIVE,
            participant_ids=[EntityId(1)],
            reward_ids=[],
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
            version=Version(1)
        )

        completed_quest = quest.complete()
        assert completed_quest.status == QuestStatus.COMPLETED
        assert completed_quest.version.value == 2
        assert completed_quest.updated_at.value > quest.updated_at.value
        print("✓ test_quest_complete_active_quest passed")

    def test_quest_complete_non_active_quest_fails(self):
        """Test that completing a non-active quest fails."""
        quest = Quest(
            id=EntityId(1),
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Quest",
            description=Description("A test quest"),
            objectives=["Objective 1"],
            status=QuestStatus.COMPLETED,
            participant_ids=[EntityId(1)],
            reward_ids=[],
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
            version=Version(1)
        )

        try:
            quest.complete()
            assert False, "Should have raised InvalidState"
        except InvalidState as e:
            assert "Cannot complete quest with status QuestStatus.COMPLETED" in str(e)
            print("✓ test_quest_complete_non_active_quest_fails passed")

    def test_quest_fail_active_quest(self):
        """Test failing an active quest."""
        quest = Quest(
            id=EntityId(1),
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Quest",
            description=Description("A test quest"),
            objectives=["Objective 1"],
            status=QuestStatus.ACTIVE,
            participant_ids=[EntityId(1)],
            reward_ids=[],
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
            version=Version(1)
        )

        failed_quest = quest.fail()
        assert failed_quest.status == QuestStatus.FAILED
        assert failed_quest.version.value == 2
        print("✓ test_quest_fail_active_quest passed")

    def test_quest_fail_non_active_quest_fails(self):
        """Test that failing a non-active quest fails."""
        quest = Quest(
            id=EntityId(1),
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Quest",
            description=Description("A test quest"),
            objectives=["Objective 1"],
            status=QuestStatus.FAILED,
            participant_ids=[EntityId(1)],
            reward_ids=[],
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
            version=Version(1)
        )

        try:
            quest.fail()
            assert False, "Should have raised InvalidState"
        except InvalidState as e:
            assert "Cannot fail quest with status QuestStatus.FAILED" in str(e)
            print("✓ test_quest_fail_non_active_quest_fails passed")


class TestStoryline:
    """Test cases for Storyline entity."""

    def test_storyline_creation(self):
        """Test basic storyline creation."""
        storyline = Storyline(
            id=EntityId(1),
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Storyline",
            description=Description("A test storyline"),
            storyline_type=StorylineType.MAIN,
            event_ids=[EntityId(1)],
            quest_ids=[EntityId(2)],
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
            version=Version(1)
        )
        assert storyline.name == "Test Storyline"
        assert storyline.storyline_type == StorylineType.MAIN
        assert len(storyline.event_ids) == 1
        assert len(storyline.quest_ids) == 1
        print("✓ test_storyline_creation passed")

    def test_storyline_invariant_no_events_or_quests(self):
        """Test that storyline must have at least one event or quest."""
        try:
            Storyline(
                id=EntityId(1),
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name="Test Storyline",
                description=Description("A test storyline"),
                storyline_type=StorylineType.MAIN,
                event_ids=[],  # No events
                quest_ids=[],  # No quests
                created_at=Timestamp.now(),
                updated_at=Timestamp.now(),
                version=Version(1)
            )
            assert False, "Should have raised InvariantViolation"
        except InvariantViolation as e:
            assert "Storyline must have at least one event or quest" in str(e)
            print("✓ test_storyline_invariant_no_events_or_quests passed")

    def test_storyline_add_event(self):
        """Test adding an event to a storyline."""
        storyline = Storyline(
            id=EntityId(1),
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Storyline",
            description=Description("A test storyline"),
            storyline_type=StorylineType.MAIN,
            event_ids=[EntityId(1)],
            quest_ids=[],
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
            version=Version(1)
        )

        updated_storyline = storyline.add_event(EntityId(2))
        assert len(updated_storyline.event_ids) == 2
        assert EntityId(2) in updated_storyline.event_ids
        assert updated_storyline.version.value == 2
        print("✓ test_storyline_add_event passed")

    def test_storyline_add_duplicate_event_fails(self):
        """Test that adding a duplicate event fails."""
        storyline = Storyline(
            id=EntityId(1),
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Storyline",
            description=Description("A test storyline"),
            storyline_type=StorylineType.MAIN,
            event_ids=[EntityId(1)],
            quest_ids=[],
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
            version=Version(1)
        )

        try:
            storyline.add_event(EntityId(1))  # Duplicate
            assert False, "Should have raised InvalidState"
        except InvalidState as e:
            assert "Event already in storyline" in str(e)
            print("✓ test_storyline_add_duplicate_event_fails passed")

    def test_storyline_add_quest(self):
        """Test adding a quest to a storyline."""
        storyline = Storyline(
            id=EntityId(1),
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Storyline",
            description=Description("A test storyline"),
            storyline_type=StorylineType.MAIN,
            event_ids=[],
            quest_ids=[EntityId(1)],
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
            version=Version(1)
        )

        updated_storyline = storyline.add_quest(EntityId(2))
        assert len(updated_storyline.quest_ids) == 2
        assert EntityId(2) in updated_storyline.quest_ids
        assert updated_storyline.version.value == 2
        print("✓ test_storyline_add_quest passed")

    def test_storyline_add_duplicate_quest_fails(self):
        """Test that adding a duplicate quest fails."""
        storyline = Storyline(
            id=EntityId(1),
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Test Storyline",
            description=Description("A test storyline"),
            storyline_type=StorylineType.MAIN,
            event_ids=[],
            quest_ids=[EntityId(1)],
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
            version=Version(1)
        )

        try:
            storyline.add_quest(EntityId(1))  # Duplicate
            assert False, "Should have raised InvalidState"
        except InvalidState as e:
            assert "Quest already in storyline" in str(e)
            print("✓ test_storyline_add_duplicate_quest_fails passed")


if __name__ == "__main__":
    # Run all tests
    print("Running Quest and Storyline tests...")

    quest_tests = TestQuest()
    storyline_tests = TestStoryline()

    print("\nRunning Quest tests...")
    quest_tests.test_quest_creation()
    quest_tests.test_quest_invariant_no_objectives()
    quest_tests.test_quest_invariant_no_participants()
    quest_tests.test_quest_complete_active_quest()
    quest_tests.test_quest_complete_non_active_quest_fails()
    quest_tests.test_quest_fail_active_quest()
    quest_tests.test_quest_fail_non_active_quest_fails()

    print("\nRunning Storyline tests...")
    storyline_tests.test_storyline_creation()
    storyline_tests.test_storyline_invariant_no_events_or_quests()
    storyline_tests.test_storyline_add_event()
    storyline_tests.test_storyline_add_duplicate_event_fails()
    storyline_tests.test_storyline_add_quest()
    storyline_tests.test_storyline_add_duplicate_quest_fails()

    print("\nAll tests passed! ✅")