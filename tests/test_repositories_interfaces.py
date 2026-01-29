import pytest

from src.domain.repositories.world_repository import IWorldRepository
from src.domain.repositories.character_repository import ICharacterRepository


def test_world_repository_is_abstract():
    with pytest.raises(TypeError):
        IWorldRepository()


def test_character_repository_is_abstract():
    with pytest.raises(TypeError):
        ICharacterRepository()
