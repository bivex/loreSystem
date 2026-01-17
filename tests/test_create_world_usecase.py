"""
Tests for Application Use Cases

These tests focus on business logic and orchestration.
Repositories are mocked to isolate the use case behavior.
"""
from unittest.mock import Mock
import pytest

from src.application.use_cases.create_world import CreateWorldUseCase
from src.application.dto import CreateWorldDTO
from src.domain.exceptions import DuplicateEntity
from src.domain.value_objects.common import TenantId, WorldName


def test_create_world_success():
    """Test successful world creation."""
    # Arrange
    mock_repo = Mock()
    mock_repo.exists.return_value = False  # World doesn't exist
    
    # Create a proper mock world
    mock_world = Mock()
    mock_world.id = Mock(value=1)
    mock_world.tenant_id = Mock(value=100)
    mock_world.name = Mock()
    mock_world.name.__str__ = Mock(return_value="Test World")
    mock_world.description = Mock()
    mock_world.description.__str__ = Mock(return_value="Description")
    mock_world.created_at = Mock(value=Mock())
    mock_world.updated_at = Mock(value=Mock())
    mock_world.version = Mock(value=1)
    
    mock_repo.save.return_value = mock_world

    use_case = CreateWorldUseCase(mock_repo)
    request = CreateWorldDTO(
        tenant_id=100,
        name="Test World",
        description="A test world"
    )

    # Act
    result = use_case.execute(request)

    # Assert
    assert result.id == 1
    assert result.tenant_id == 100
    assert result.name == "Test World"
    mock_repo.exists.assert_called_once()
    mock_repo.save.assert_called_once()


def test_create_world_duplicate_name_raises_error():
    """Test that duplicate world names raise errors."""
    # Arrange
    mock_repo = Mock()
    mock_repo.exists.return_value = True  # World already exists

    use_case = CreateWorldUseCase(mock_repo)
    request = CreateWorldDTO(
        tenant_id=100,
        name="Existing World",
        description="Description"
    )

    # Act & Assert
    with pytest.raises(DuplicateEntity, match="World 'Existing World' already exists"):
        use_case.execute(request)

    # Verify repository was checked but not saved
    mock_repo.exists.assert_called_once()
    mock_repo.save.assert_not_called()


def test_create_world_invalid_input():
    """Test validation of input data."""
    mock_repo = Mock()

    use_case = CreateWorldUseCase(mock_repo)

    # Empty name should raise ValueError
    request = CreateWorldDTO(
        tenant_id=100,
        name="",  # Invalid
        description="Description"
    )

    with pytest.raises(ValueError):
        use_case.execute(request)