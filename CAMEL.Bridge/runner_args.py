"""Argument parsing for the CAMEL rumor pipeline runner."""

from __future__ import annotations

import argparse


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
    parser.add_argument("--with-campaign-story", action="store_true", help="Also generate Campaign/Story plus branching, Character, and Quest entities such as Storyline, PlotBranch, CharacterEvolution, VoiceActor, QuestChain, QuestNode, QuestTracker, Flashback, FlashForward, and Ending")
    parser.add_argument("--with-systems", action="store_true", help="Also generate and persist Item, Inventory, Material, Component, Socket, CraftingRecipe, Blueprint, Enchantment, Rune, Glyph, Title, Rank, Leaderboard, Trophy, Badge, Mastery, Skill, Perk, Trait, Attribute, TalentTree, Achievement, LevelUp, Experience, ProgressionState, ProgressionEvent, PlayerMetric, DropRate, LootTableWeight, DifficultyCurve, Dungeon, Raid, WorldEvent, Arena, Instance, OpenWorldZone, SeasonalEvent, Invasion, War, LegendaryWeapon, MythicalArmor, DivineItem, CursedItem, ArtifactSet, and RelicCollection entities")
    parser.add_argument("--with-memory", action="store_true", help="Enable SQLite + Qdrant continuity memory using CAMEL_MEMORY_QDRANT_* env settings")
    return parser
