import json
from pathlib import Path

from src.presentation.gui.lore_editor import LoreData


def test_loredata_load_and_serialize_roundtrip():
    repo_root = Path(__file__).resolve().parent.parent
    sample_file = repo_root / "examples" / "sample_lore.json"
    assert sample_file.exists(), f"sample file missing: {sample_file}"

    data = json.loads(sample_file.read_text())

    lore = LoreData()
    # ensure from_dict works without raising
    lore.from_dict(data)

    # basic sanity checks
    assert isinstance(lore.worlds, list)
    assert isinstance(lore.characters, list)
    assert isinstance(lore.events, list)
    assert isinstance(lore.improvements, list)
    assert isinstance(lore.items, list)

    # serialize back and ensure keys present
    out = lore.to_dict()
    assert "worlds" in out and "characters" in out
    assert "events" in out and "improvements" in out
    assert "items" in out


def test_improvements_api_present():
    lore = LoreData()
    assert hasattr(lore, "improvements")
    assert hasattr(lore, "add_improvement")


def test_items_api_present():
    lore = LoreData()
    assert hasattr(lore, "items")
    assert hasattr(lore, "add_item")
