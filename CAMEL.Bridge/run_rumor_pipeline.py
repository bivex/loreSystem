"""CLI runner for the CAMEL rumor bridge."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.application.integration.camel_bridge import CamelChatBackend, RumorBridgeService, RumorGenerationRequest, load_env_file
from src.application.integration.camel_bridge.rumor_agents import _env_flag
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
    parser.add_argument("--env-file", default=None, help="Path to a .env file containing model credentials/config")
    parser.add_argument("--strict-model", action="store_true", help="Disable all fallback generation and fail if the model call or JSON output is invalid")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    loaded_env = load_env_file(args.env_file)
    strict_model = args.strict_model or _env_flag("CAMEL_BRIDGE_STRICT_MODEL", default=False)
    repository = CamelBridgeRumorRepository(args.db_path)
    service = RumorBridgeService(
        repository=repository,
        backend=CamelChatBackend(),
        character_repository=CamelBridgeCharacterRepository(args.db_path),
        event_repository=CamelBridgeEventRepository(args.db_path),
        relationship_repository=CamelBridgeCharacterRelationshipRepository(args.db_path),
        allow_fallback=not strict_model,
    )
    if loaded_env:
        print(f"Loaded env from {loaded_env}")
    print(
        "Using CAMEL backend "
        f"platform={service.backend.model_platform} model={service.backend.model_type} "
        f"strict_model={'on' if strict_model else 'off'}"
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