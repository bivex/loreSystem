"""CLI runner for the CAMEL rumor bridge."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.application.integration.camel_bridge import CamelChatBackend, RumorBridgeService, RumorGenerationRequest
from src.infrastructure.camel_bridge_rumor_repository import (
    CamelBridgeCharacterRelationshipRepository,
    CamelBridgeCharacterRepository,
    CamelBridgeEventRepository,
    CamelBridgeRumorRepository,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate rumor lore and persist it to SQLite.")
    parser.add_argument("--tenant-id", type=int, required=True)
    parser.add_argument("--world-id", type=int, required=True)
    parser.add_argument("--theme", required=True)
    parser.add_argument("--context", default="")
    parser.add_argument("--count", type=int, default=2)
    parser.add_argument("--location-id", type=int)
    parser.add_argument("--character", action="append", default=[])
    parser.add_argument("--db-path", default="lore_system.db")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repository = CamelBridgeRumorRepository(args.db_path)
    service = RumorBridgeService(
        repository=repository,
        backend=CamelChatBackend(),
        character_repository=CamelBridgeCharacterRepository(args.db_path),
        event_repository=CamelBridgeEventRepository(args.db_path),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(args.db_path),
    )
    result = service.generate_story_chain(RumorGenerationRequest(
        tenant_id=args.tenant_id,
        world_id=args.world_id,
        theme=args.theme,
        context=args.context,
        count=args.count,
        location_id=args.location_id,
        character_names=tuple(args.character),
    ))
    for rumor in result.rumors:
        print(f"[{rumor.id.value}] {rumor.name}: {rumor.truth_level} / {rumor.spread_speed}")
    for event in result.events:
        print(f"event[{event.id.value}] {event.name}")
    for rel in result.relationships:
        print(f"relationship[{rel.id.value}] {rel.relationship_type.value} {rel.character_from_id.value}->{rel.character_to_id.value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())