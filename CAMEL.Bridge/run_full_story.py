"""Orchestrator: generate a full multi-chapter story sequentially.

Calls the lore pipeline once per chapter, feeding summaries of all
previously generated chapters into the next iteration's context so the
LLM continues the canon instead of restarting. All chapters fold into a
single campaign via the pipeline's merge logic.

Usage:
    python3 CAMEL.Bridge/run_full_story.py \\
        --tenant-id 1 --world-id 1 \\
        --theme "Тёмное фэнтези: герой просыпается в бочке в пещере орков" \\
        --chapters 15 \\
        --output-language ru \\
        --db-path lore_system.db \\
        --with-memory \\
        [--env-file .env] \\
        [--character "Мара Восс" --character "Ивен Хейл"]
"""

from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runner_service import build_service
from src.application.integration.camel_bridge import RumorGenerationRequest, load_env_file

LOG = logging.getLogger("run_full_story")


class _CountingBackend:
    """Wraps a CAMEL backend and counts every LLM call with a live progress line."""

    def __init__(self, backend, total_chapters: int, calls_per_chapter: int = 7) -> None:
        self._backend = backend
        self._call_count = 0
        self._chapter_call_count = 0
        self._current_chapter = 0
        self._total_chapters = total_chapters
        self._calls_per_chapter = calls_per_chapter
        self._chapter_start: float = 0.0
        self._total_start: float = time.monotonic()

    def set_chapter(self, chapter_num: int) -> None:
        self._current_chapter = chapter_num
        self._chapter_call_count = 0
        self._chapter_start = time.monotonic()

    def generate(self, system_message: str, user_message: str) -> str:
        self._call_count += 1
        self._chapter_call_count += 1
        total_expected = self._total_chapters * self._calls_per_chapter
        elapsed = time.monotonic() - self._total_start
        avg_per_call = elapsed / self._call_count if self._call_count > 1 else 0
        eta = avg_per_call * (total_expected - self._call_count) if avg_per_call else 0
        print(
            f"   🤖 LLM call #{self._call_count:3d}"
            f" | ch {self._current_chapter}/{self._total_chapters}"
            f" call {self._chapter_call_count}/{self._calls_per_chapter}"
            f" | total {self._call_count}/{total_expected}"
            f" | elapsed {elapsed:5.0f}s"
            f" | ETA ~{eta:5.0f}s",
            flush=True,
        )
        return self._backend.generate(system_message, user_message)

    # Proxy all other attributes to the real backend.
    def __getattr__(self, name: str):
        return getattr(self._backend, name)

# Lore tables to clear on reset. Mirrors scripts/run_generation.py but adds
# the extended narrative/systems tables so the slate is truly clean.
LORE_TABLES = [
    'rumors', 'characters', 'events', 'character_relationships',
    'campaigns', 'stories', 'acts', 'chapters', 'episodes', 'storylines',
    'quests', 'quest_chains', 'quest_givers', 'quest_nodes', 'quest_objectives',
    'quest_prerequisites', 'quest_reward_tiers', 'quest_trackers',
    'prologues', 'epilogues', 'plot_branches', 'branch_points', 'choices',
    'consequences', 'moral_choices', 'alternate_realities', 'flashbacks',
    'flash_forwards', 'endings',
    # Extended character meta
    'character_evolutions', 'character_variants', 'character_profile_entries',
    'affinities', 'dispositions',
    # Production
    'voice_actors', 'motion_captures', 'subtitles',
]


def _load_yaml_config(path: str) -> dict:
    """Load story config from a YAML file. Returns a flat dict of field values."""
    import importlib.util
    if importlib.util.find_spec("yaml") is None:
        raise ImportError(
            "PyYAML is required for --config support: pip install pyyaml"
        )
    import yaml  # type: ignore[import]
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML config must be a mapping, got {type(data).__name__}")
    return data


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate a full multi-chapter story sequentially.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "YAML config example (--config story.yaml):\n"
            "  tenant_id: 1\n"
            "  world_id: 1\n"
            "  theme: \"Тёмное фэнтези\"\n"
            "  chapters: 15\n"
            "  characters:\n"
            "    - Мара Восс\n"
            "    - Ивен Хейл\n"
            "  with_memory: true\n"
            "  reset: true\n"
            "  output_language: ru\n"
            "  env_file: .env\n"
            "  db_path: lore_system.db\n"
        ),
    )
    p.add_argument("--config", default=None, help="Path to YAML story config file")
    p.add_argument("--tenant-id", type=int, default=None)
    p.add_argument("--world-id", type=int, default=None)
    p.add_argument("--theme", default=None, help="Base story theme")
    p.add_argument("--chapters", type=int, default=None, help="Number of chapters to generate (default 15)")
    p.add_argument("--output-language", default=None, help="Output language code (ru, en, uk)")
    p.add_argument("--db-path", default=None)
    p.add_argument("--env-file", default=None, help="Path to .env file with model credentials")
    p.add_argument("--with-memory", action="store_true", default=None, help="Enable Qdrant+SQLite continuity memory")
    p.add_argument("--character", action="append", default=None, help="Seed character name (repeatable)")
    p.add_argument("--reset", action="store_true", default=None,
                   help="Clear lore tables before starting (default: on)")
    p.add_argument("--no-reset", dest="reset", action="store_false",
                   help="Do NOT clear; continue from existing data")
    args = p.parse_args()

    # Merge YAML config under CLI flags (CLI wins over YAML, YAML wins over defaults).
    yaml_cfg: dict = {}
    if args.config:
        yaml_cfg = _load_yaml_config(args.config)

    def _yaml(key: str, default):
        return yaml_cfg.get(key, default)

    if args.tenant_id is None:
        args.tenant_id = _yaml("tenant_id", None)
    if args.world_id is None:
        args.world_id = _yaml("world_id", None)
    if args.theme is None:
        args.theme = _yaml("theme", None)
    if args.chapters is None:
        args.chapters = _yaml("chapters", 15)
    if args.output_language is None:
        args.output_language = _yaml("output_language", "ru")
    if args.db_path is None:
        args.db_path = _yaml("db_path", "lore_system.db")
    if args.env_file is None:
        args.env_file = _yaml("env_file", None)
    if not args.with_memory:
        args.with_memory = bool(_yaml("with_memory", False))
    if args.character is None:
        yaml_chars = _yaml("characters", [])
        args.character = list(yaml_chars) if yaml_chars else []
    if args.reset is None:
        args.reset = bool(_yaml("reset", True))

    # Validate required fields.
    missing = [f for f, v in [("--tenant-id / tenant_id", args.tenant_id),
                               ("--world-id / world_id", args.world_id),
                               ("--theme / theme", args.theme)] if v is None]
    if missing:
        p.error("Missing required fields: " + ", ".join(missing))

    return args


def reset_lore_tables(db_path: str, tenant_id: int, world_id: int) -> int:
    """Delete all lore rows for the given tenant/world. Returns rows deleted."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cleared = 0
    for table in LORE_TABLES:
        try:
            cur.execute(
                f"DELETE FROM {table} WHERE tenant_id = ? AND world_id = ?",
                (tenant_id, world_id),
            )
            cleared += cur.rowcount
        except sqlite3.OperationalError as e:
            if "no such table" not in str(e):
                LOG.warning("Failed to clear %s: %s", table, e)
    conn.commit()
    conn.close()
    return cleared


def load_chapter_summaries(db_path: str, tenant_id: int, world_id: int) -> list[dict]:
    """Load (sequence_number, title, description) for all existing chapters.

    Returns a list of dicts sorted by sequence_number ascending. Reads the
    DB directly (bypassing repositories) the same way the pipeline does
    internally via _list_table_rows.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT sequence_number, title, description "
            "FROM chapters WHERE tenant_id = ? AND world_id = ? "
            "ORDER BY sequence_number ASC, id ASC",
            (tenant_id, world_id),
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    return [
        {
            "sequence_number": r["sequence_number"] or 0,
            "title": r["title"] or "",
            "description": (r["description"] or "")[:200],
        }
        for r in rows
    ]


def build_chapter_context(
    chapter_num: int,
    total: int,
    prev_summaries: list[dict],
    theme: str,
) -> str:
    """Build the context string for chapter N, summarising prior chapters.

    The pipeline injects request.context into every LLM prompt, so stuffing
    the previous-chapters canon here makes the model continue the story.
    """
    lines = [
        f"Последовательная генерация сюжета. Сейчас пишется Глава {chapter_num} из {total}.",
        f"Базовая тема: {theme}",
        "",
    ]
    if prev_summaries:
        lines.append("ПРЕДЫДУЩИЕ ГЛАВЫ (канон — НЕ пересказывай, ПРОДОЛЖАЙ с того места):")
        for s in prev_summaries:
            desc = s["description"]
            lines.append(f"  Глава {s['sequence_number']}: «{s['title']}» — {desc}")
        lines.append("")
    lines.append(
        f"Продолжи сюжет. Сгенерируй ОДНУ новую главу (sequence_number={chapter_num}) "
        f"с 1-2 эпизодами, которые логически следуют из последней главы. "
        f"Сохраняй канон персонажей, событий и локаций."
    )
    return "\n".join(lines)


def enforce_chapter_sequence(
    db_path: str, tenant_id: int, world_id: int, chapter_num: int
) -> bool:
    """Ensure the most recently inserted chapter has sequence_number=chapter_num.

    The LLM may restart numbering at 1 on each call. This finds the latest
    chapter row (highest id) for the tenant/world and force-sets its
    sequence_number so chapters don't collide. Returns True if a fix was applied.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        row = cur.execute(
            "SELECT id, sequence_number FROM chapters "
            "WHERE tenant_id = ? AND world_id = ? ORDER BY id DESC LIMIT 1",
            (tenant_id, world_id),
        ).fetchone()
    except sqlite3.OperationalError:
        conn.close()
        return False
    if row is None:
        conn.close()
        return False
    if row["sequence_number"] == chapter_num:
        conn.close()
        return False
    # Check the target sequence_number isn't already taken by another row.
    conflict = cur.execute(
        "SELECT id FROM chapters WHERE tenant_id = ? AND world_id = ? "
        "AND sequence_number = ? AND id != ?",
        (tenant_id, world_id, chapter_num, row["id"]),
    ).fetchone()
    if conflict:
        # Shift the conflicting row to a temp high number, then set ours.
        cur.execute(
            "UPDATE chapters SET sequence_number = sequence_number + 10000 "
            "WHERE id = ?", (conflict["id"],)
        )
    cur.execute(
        "UPDATE chapters SET sequence_number = ? WHERE id = ?",
        (chapter_num, row["id"]),
    )
    conn.commit()
    conn.close()
    LOG.info("Enforced sequence_number=%d on chapter id=%d", chapter_num, row["id"])
    return True


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    args = parse_args()
    loaded_env = load_env_file(args.env_file) if args.env_file else None
    if loaded_env:
        print(f"Loaded env from {loaded_env}")

    # 1. Optional reset.
    if args.reset:
        deleted = reset_lore_tables(args.db_path, args.tenant_id, args.world_id)
        print(f"🗑️  Cleared {deleted} rows from {len(LORE_TABLES)} lore tables")
        # Also wipe Qdrant memory collection so we start fresh semantically.
        if args.with_memory:
            import os
            qdrant_url = os.environ.get("CAMEL_MEMORY_QDRANT_URL", "http://localhost:6333")
            try:
                import urllib.request
                req = urllib.request.Request(
                    f"{qdrant_url}/collections/camel_bridge_memory",
                    method="DELETE",
                )
                urllib.request.urlopen(req, timeout=5)
                print("🗑️  Cleared Qdrant memory collection")
            except Exception as e:
                LOG.warning("Could not clear Qdrant: %s", e)

    # 2. Build the service once (all repos wired).
    service, memory_service = build_service(args.db_path, with_memory=args.with_memory)
    print(
        f"Using CAMEL backend "
        f"platform={service.backend.model_platform} model={service.backend.model_type} "
        f"memory={'on' if memory_service else 'off'}"
    )

    # Wrap backend with call counter for live progress output.
    counting_backend = _CountingBackend(service.backend, total_chapters=args.chapters)
    service.backend = counting_backend

    # 3. Sequential chapter generation loop.
    for chapter_num in range(1, args.chapters + 1):
        print(f"\n{'='*60}")
        print(f"📖 Generating Chapter {chapter_num} of {args.chapters}...")
        print(f"{'='*60}")
        counting_backend.set_chapter(chapter_num)

        # 3a. Load summaries of all previously generated chapters.
        prev_summaries = load_chapter_summaries(
            args.db_path, args.tenant_id, args.world_id
        )
        if prev_summaries:
            print(f"   📚 Loaded {len(prev_summaries)} previous chapter summaries for context")

        # 3b. Build continuation context.
        context = build_chapter_context(
            chapter_num, args.chapters, prev_summaries, args.theme
        )

        # 3c. Build request.
        request = RumorGenerationRequest(
            tenant_id=args.tenant_id,
            world_id=args.world_id,
            theme=f"{args.theme} — Глава {chapter_num}",
            context=context,
            output_language=args.output_language,
            count=1,
            character_names=tuple(args.character),
        )

        # 3d. Generate (narrative only; no systems slice for speed).
        try:
            result = service.generate_story_chain(
                request,
                include_narrative_structure=True,
                include_systems_slice=False,
            )
        except Exception as e:
            LOG.error("Chapter %d generation failed: %s", chapter_num, e)
            print(f"❌ Chapter {chapter_num} failed: {e}")
            continue

        # 3e. Enforce correct sequence_number.
        fixed = enforce_chapter_sequence(
            args.db_path, args.tenant_id, args.world_id, chapter_num
        )
        if fixed:
            print(f"   🔧 Fixed sequence_number to {chapter_num}")

        # 3f. Progress.
        n_rumors = len(result.rumors)
        n_events = len(result.events)
        print(f"   ✅ Chapter {chapter_num}/{args.chapters} done "
              f"({n_rumors} rumors, {n_events} events)")

    print(f"\n{'='*60}")
    print(f"🎉 Full story complete: {args.chapters} chapters generated!")
    print(f"{'='*60}")

    # Final summary: list all chapters in the DB.
    final_summaries = load_chapter_summaries(
        args.db_path, args.tenant_id, args.world_id
    )
    print(f"\n📜 Final chapter list ({len(final_summaries)} chapters):")
    for s in final_summaries:
        print(f"   Глава {s['sequence_number']}: «{s['title']}»")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
