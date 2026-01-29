"""
Tests for In-Memory World Repository

Uses the contract tests to ensure the in-memory implementation
behaves correctly. These tests verify that our repository
implementation follows the expected interface contract.
"""
import pytest

from src.infrastructure.in_memory_repositories import InMemoryWorldRepository
from tests.repositories.contract import WorldRepositoryContract


@pytest.fixture
def repo():
    """Fresh repository for each test."""
    return InMemoryWorldRepository()


class TestInMemoryWorldRepository(WorldRepositoryContract):
    """
    Test the in-memory world repository implementation.

    Inherits all contract tests to ensure compliance with the interface.
    """
    pass