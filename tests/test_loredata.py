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


def test_loredata_metadata_roundtrip_normalizes_generation_runs_and_provenance():
    lore = LoreData()
    run_record = lore.add_generation_run({
        "run_id": "run-001",
        "run_kind": "agent_team",
        "source_system": "loreSystem",
        "world_id": "world-1",
        "status": "completed",
        "input_refs": [{"type": "file", "path": "chapters/ch1.txt"}],
        "metadata": {"agent": "narrative-team"},
    })
    provenance_record = lore.add_entity_provenance({
        "entity_type": "Character",
        "entity_id": "101",
        "run_id": "run-001",
        "relation_type": "created_by",
        "confidence": 0.93,
        "source_refs": [{"type": "fragment", "id": "frag-1"}],
        "metadata": {"skill": "character-design"},
    })
    lore.metadata["bundle_label"] = "chapter-1"

    payload = lore.to_dict()
    restored = LoreData()
    restored.from_dict(payload)

    assert payload["metadata"]["generation_runs"][0]["run_id"] == "run-001"
    assert payload["metadata"]["entity_provenance"][0]["entity_type"] == "Character"
    assert restored.metadata["bundle_label"] == "chapter-1"
    assert restored.metadata["generation_runs"] == [run_record]
    assert restored.metadata["entity_provenance"] == [provenance_record]


def test_loredata_from_dict_without_metadata_defaults_to_empty_provenance_lists():
    lore = LoreData()
    lore.from_dict({"worlds": [], "characters": [], "next_id": 7})

    assert lore.metadata["generation_runs"] == []
    assert lore.metadata["entity_provenance"] == []
    assert lore.to_dict()["metadata"]["generation_runs"] == []
