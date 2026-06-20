"""CLI runner for the CAMEL rumor bridge."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runner_args import build_parser
from runner_output import print_chain_result
from runner_service import build_service
from src.application.integration.camel_bridge import RumorGenerationRequest, load_env_file


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    args = build_parser().parse_args()
    loaded_env = load_env_file(args.env_file)
    service, memory_service = build_service(args.db_path, with_memory=args.with_memory)
    if loaded_env:
        print(f"Loaded env from {loaded_env}")
    print(
        "Using CAMEL backend "
        f"platform={service.backend.model_platform} model={service.backend.model_type} "
        f"memory={'on' if memory_service else 'off'}"
    )
    result = service.generate_story_chain(
        RumorGenerationRequest(
            tenant_id=args.tenant_id,
            world_id=args.world_id,
            theme=args.theme,
            context=args.context,
            output_language=args.output_language,
            count=args.count,
            location_id=args.location_id,
            character_names=tuple(args.character),
        ),
        include_narrative_structure=args.with_campaign_story,
        include_systems_slice=args.with_systems,
    )
    print_chain_result(result, include_narrative=args.with_campaign_story, include_systems=args.with_systems)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
