import json
import re
from pathlib import Path

from src.application.integration import ProjectionBundleExporter


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_example(path: str) -> dict:
    text = (REPO_ROOT / path).read_text(encoding="utf-8")
    text = re.sub(r':\s*\+(\d+)', r': \1', text)
    return json.loads(text)


def test_exporter_builds_projection_bundle_from_sample_lore():
    exporter = ProjectionBundleExporter()

    bundle = exporter.export(load_example("examples/sample_lore.json"), world_id=1, scenario_id="forge-crisis")

    assert bundle["world_id"] == "1"
    assert bundle["scenario_id"] == "forge-crisis"
    assert {actor["name"] for actor in bundle["actors"]} == {"Aria Flameheart", "Valorian the Eternal"}
    assert bundle["organizations"] == []
    assert any(location["name"] == "The Eternal Forge" for location in bundle["context_locations"])
    assert any(event["name"] == "The Great Reforging" for event in bundle["event_seeds"])
    assert bundle["world_rules"][0]["canonical_type"] == "World"


def test_exporter_builds_social_edges_from_interconnected_lore():
    exporter = ProjectionBundleExporter()

    bundle = exporter.export(load_example("examples/enhanced_interconnected_lore.json"), world_id=1)
    actors = {item["name"]: item["id"] for item in bundle["actors"]}
    orgs = {item["name"]: item["id"] for item in bundle["organizations"]}
    edge_tuples = {(item["source_id"], item["target_id"], item["relation_type"]) for item in bundle["social_edges"]}

    assert (actors["Лира Кровавый Шёпот"], actors["Элиза Забытая Ведьма"], "LOVER") in edge_tuples
    assert (actors["Виктор Железный Кулак"], orgs["Орден Святого Пламени"], "BETRAYED_BY") in edge_tuples
    assert (actors["Лира Кровавый Шёпот"], orgs["Клан Кровавой Луны"], "LEADS") in edge_tuples
    assert (orgs["Клан Кровавой Луны"], orgs["Орден Святого Пламени"], "OPPOSES") in edge_tuples


def test_exporter_can_write_bundle_file(tmp_path):
    exporter = ProjectionBundleExporter()
    output_path = tmp_path / "projection_bundle.json"

    bundle = exporter.export_file(REPO_ROOT / "examples/sample_lore.json", output_path, world_id=2)
    saved_bundle = json.loads(output_path.read_text(encoding="utf-8"))

    assert output_path.exists()
    assert saved_bundle == bundle
    assert saved_bundle["world_id"] == "2"
    assert {actor["name"] for actor in saved_bundle["actors"]} == {"Umbra Nightwhisper"}