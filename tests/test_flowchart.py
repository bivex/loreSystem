"""
Tests for Flowchart entity with edge cases and comprehensive coverage.
"""
import pytest

from src.domain.entities.flowchart import Flowchart
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
)
from src.domain.exceptions import InvariantViolation


def make_basic_flowchart():
    """Factory for basic flowchart."""
    return Flowchart.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Quest Flow",
        nodes=[
            {
                "id": EntityId(300),
                "label": "Start",
                "type": "start",
                "x": 100,
                "y": 100,
                "content": "Quest begins",
            },
            {
                "id": EntityId(301),
                "label": "Choice Point",
                "type": "decision",
                "x": 200,
                "y": 200,
                "content": "What do you choose?",
            },
            {
                "id": EntityId(302),
                "label": "End",
                "type": "end",
                "x": 300,
                "y": 300,
                "content": "Quest complete",
            }
        ],
        description="Flowchart showing quest progression.",
        story_id=EntityId(100),
        connections=[
            {
                "id": EntityId(400),
                "from": EntityId(300),
                "to": EntityId(301),
                "label": "Begin",
            },
            {
                "id": EntityId(401),
                "from": EntityId(301),
                "to": EntityId(302),
                "label": "Complete",
            }
        ],
        is_active=True,
    )


def make_empty_flowchart():
    """Factory for empty flowchart."""
    return Flowchart.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Empty Flow",
        nodes=[
            {
                "id": EntityId(300),
                "label": "Start",
                "type": "start",
                "x": 100,
                "y": 100,
                "content": "Begin planning",
            }
        ],
        description="Blank flowchart for planning.",
        story_id=None,
        connections=[],
        is_active=False,
    )


class TestFlowchartCreation:
    """Test flowchart creation scenarios."""

    def test_create_basic_flowchart(self):
        """Test creating a basic flowchart."""
        flowchart = make_basic_flowchart()
        assert flowchart.name == "Quest Flow"
        assert flowchart.description == "Flowchart showing quest progression."
        assert len(flowchart.nodes) == 3
        assert len(flowchart.connections) == 2
        assert flowchart.is_active
        assert flowchart.version.value == 1
        assert flowchart.version.value == 1

    def test_create_empty_flowchart(self):
        """Test creating empty flowchart."""
        flowchart = make_empty_flowchart()
        assert len(flowchart.nodes) == 1  # Has at least one node
        assert len(flowchart.connections) == 0
        assert not flowchart.is_active


class TestFlowchartOperations:
    """Test flowchart modification operations."""

    def test_add_node(self):
        """Test adding a node."""
        flowchart = make_basic_flowchart()
        old_version = flowchart.version.value

        new_node = {
            "id": EntityId(303),
            "label": "New Node",
            "type": "process",
            "x": 400,
            "y": 400,
            "content": "New content",
        }
        flowchart.add_node(new_node)

        assert len(flowchart.nodes) == 4
        assert flowchart.nodes[3]["id"] == EntityId(303)
        assert flowchart.version.value == old_version + 1

    def test_remove_node(self):
        """Test removing a node."""
        flowchart = make_basic_flowchart()
        old_version = flowchart.version.value

        node_to_remove = flowchart.nodes[1]["id"]  # Middle node
        flowchart.remove_node(str(node_to_remove))  # Convert to str

        assert len(flowchart.nodes) == 2
        assert all(node["id"] != node_to_remove for node in flowchart.nodes)
        # Connections to/from removed node should be removed too
        assert len(flowchart.connections) == 0  # Both connections involved the removed node
        assert flowchart.version.value == old_version + 1

    def test_add_connection(self):
        """Test adding a connection."""
        flowchart = make_basic_flowchart()
        old_version = flowchart.version.value

        new_connection = {
            "id": EntityId(402),
            "from": str(EntityId(302)),  # End node
            "to": str(EntityId(300)),    # Start node (creating a loop)
            "label": "Loop back",
        }
        flowchart.add_connection(new_connection)

        assert len(flowchart.connections) == 3
        assert flowchart.connections[2]["id"] == EntityId(402)
        assert flowchart.version.value == old_version + 1

    def test_remove_connection(self):
        """Test removing a connection."""
        flowchart = make_basic_flowchart()
        old_version = flowchart.version.value

        # Remove the first connection
        from_node = flowchart.connections[0]["from"]
        to_node = flowchart.connections[0]["to"]
        flowchart.remove_connection(from_node, to_node)

        assert len(flowchart.connections) == 1
        assert flowchart.version.value == old_version + 1

    def test_activate(self):
        """Test activating a flowchart."""
        flowchart = make_basic_flowchart()
        flowchart.is_active = False  # Ensure it's inactive
        old_version = flowchart.version.value

        flowchart.activate()

        assert flowchart.is_active
        assert flowchart.version.value == old_version + 1

    def test_deactivate(self):
        """Test deactivating a flowchart."""
        flowchart = make_basic_flowchart()
        old_version = flowchart.version.value

        flowchart.deactivate()

        assert not flowchart.is_active
        assert flowchart.version.value == old_version + 1


class TestFlowchartInvariants:
    """Test invariant enforcement."""

    def test_at_least_one_node_invariant(self):
        """Test that flowchart must have at least one node."""
        with pytest.raises(InvariantViolation, match="Flowchart must have at least one node"):
            flowchart = make_basic_flowchart()
            # Manually set empty nodes
            object.__setattr__(flowchart, 'nodes', [])
            flowchart._validate_invariants()

    def test_updated_at_not_before_created_at(self):
        """Test that updated_at cannot be before created_at."""
        from datetime import timedelta
        from src.domain.value_objects.common import Timestamp

        with pytest.raises(InvariantViolation, match="Updated timestamp must be >= created timestamp"):
            flowchart = make_basic_flowchart()
            # Manually set invalid timestamps
            object.__setattr__(flowchart, 'updated_at', Timestamp(flowchart.created_at.value - timedelta(hours=1)))
            flowchart._validate_invariants()


class TestFlowchartStringRepresentations:
    """Test string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        flowchart = make_basic_flowchart()
        assert str(flowchart) == "Flowchart(Quest Flow, 3 nodes)"

    def test_str_empty_flowchart(self):
        """Test __str__ method for empty flowchart."""
        flowchart = make_empty_flowchart()
        assert str(flowchart) == "Flowchart(Empty Flow, 1 nodes)"

    def test_repr_representation(self):
        """Test __repr__ method."""
        flowchart = make_basic_flowchart()
        repr_str = repr(flowchart)
        assert "Flowchart(id=None" in repr_str
        assert "world_id=1" in repr_str
        assert "name='Quest Flow'" in repr_str
        assert "active=True" in repr_str
        assert "version=v1" in repr_str