"""
Tests for In-Memory Character Repository

Uses the contract tests to ensure the in-memory implementation
behaves correctly. These tests verify that our repository
implementation follows the expected interface contract.
"""
import pytest

from src.infrastructure.in_memory_repositories import InMemoryCharacterRepository
from tests.repositories.contract import CharacterRepositoryContract


@pytest.fixture
def repo():
    """Fresh repository for each test."""
    return InMemoryCharacterRepository()


class TestInMemoryCharacterRepository(CharacterRepositoryContract):
    """
    Test the in-memory character repository implementation.

    Inherits all contract tests to ensure compliance with the interface.
    """
    pass