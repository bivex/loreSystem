#!/usr/bin/env python3
"""
Generate ALL remaining repository interfaces (258 entities)

This script processes all remaining domain entities that don't have repository interfaces yet.
"""

import sys
from pathlib import Path
from typing import List, Dict

project_root = Path(__file__).parent
entities_dir = project_root / "src" / "domain" / "entities"

# Already implemented interfaces (42)
IMPLEMENTED = [
    "world", "character", "story", "page", "item", "location", "environment",
    "session", "tag", "note", "template", "choice", "flowchart", "handout", "image", "inspiration", "map", "tokenboard",
    "quest_chain", "quest_node", "quest_prerequisite", "quest_objective", "quest_tracker", "quest_giver", "quest_reward", "quest_reward_tier",
    "skill", "perk", "trait", "attribute", "experience", "level_up", "talent_tree", "mastery",
    "faction_hierarchy", "faction_ideology", "faction_leader", "faction_membership", "faction_resource", "faction_territory",
]

# Category groups from README
CATEGORIES: Dict[str, List[str]] = {
    "CoreGameSystems": [
        "character_evolution", "character_variant", "character_profile_entry", "motion_capture", "voice_actor",
        "act", "chapter", "episode", "prologue", "epilogue", "plot_branch", "consequence", "ending", "alternate_reality",
    ],
    "InventoryCrafting": [
        "inventory", "crafting_recipe", "material", "component", "blueprint", "enchantment", "socket", "rune", "glyph",
    ],
    "Locations": [
        "hub_area", "instance", "dungeon", "raid", "arena", "open_world_zone", "underground", "skybox", "dimension", "pocket_dimension",
    ],
    "PoliticsHistory": [
        "era", "era_transition", "timeline", "calendar", "holiday", "season", "time_period", "treaty", "constitution", "law", "legal_system", "nation", "kingdom", "empire", "government", "alliance",
    ],
    "Economy": [
        "trade", "barter", "tax", "tariff", "supply", "demand", "price", "inflation",
    ],
    "Military": [
        "army", "fleet", "weapon_system", "defense", "fortification", "siege_engine", "battalion",
    ],
    "SocialRelations": [
        "reputation", "affinity", "disposition", "honor", "karma", "social_class", "social_mobility",
    ],
    "ReligionMysticism": [
        "cult", "sect", "holy_site", "scripture", "ritual", "oath", "summon", "pact", "curse", "blessing",
    ],
    "LoreSystem": [
        "lore_fragment", "codex_entry", "journal_page", "bestiary_entry", "memory", "dream", "nightmare",
    ],
    "MusicAudio": [
        "theme", "motif", "score", "soundtrack", "voice_line", "sound_effect", "ambient", "silence",
    ],
    "VisualEffects": [
        "visual_effect", "particle", "shader", "lighting", "color_palette",
    ],
    "Cinematography": [
        "cutscene", "cinematic", "camera_path", "transition", "fade", "flashback",
    ],
    "Architecture": [
        "district", "ward", "quarter", "plaza", "market_square", "slums", "noble_district", "port_district",
    ],
    "BiologyEcology": [
        "food_chain", "migration", "hibernation", "reproduction", "extinction", "evolution",
    ],
    "Astronomy": [
        "galaxy", "nebula", "black_hole", "wormhole", "star_system", "moon", "eclipse", "solstice", "atmosphere",
    ],
    "WeatherClimate": [
        "weather_pattern", "cataclysm", "disaster", "miracle", "phenomenon",
    ],
    "NarrativeDevices": [
        "plot_device", "deus_ex_machina", "chekhovs_gun", "foreshadowing", "flash_forward", "red_herring",
    ],
    "GlobalEvents": [
        "world_event", "seasonal_event", "invasion", "plague", "famine", "war", "revolution",
    ],
    "TravelProgression": [
        "fast_travel_point", "waypoint", "save_point", "checkpoint", "autosave", "spawn_point",
    ],
    "LegalSystem": [
        "court", "crime", "judge", "jury", "lawyer", "punishment", "evidence", "witness",
    ],
    "Achievements": [
        "achievement", "trophy", "badge", "title", "rank", "leaderboard",
    ],
    "UGC": [
        "mod", "custom_map", "user_scenario", "share_code", "workshop_entry",
    ],
    "Localization": [
        "localization", "translation", "voice_over", "subtitle", "dubbing",
    ],
    "Analytics": [
        "player_metric", "session_data", "heatmap", "drop_rate", "conversion_rate",
    ],
    "Balance": [
        "difficulty_curve", "loot_table_weight", "balance_entities",
    ],
    "LegendaryItems": [
        "legendary_weapon", "mythical_armor", "divine_item", "cursed_item", "artifact_set", "relic_collection",
    ],
    "CompanionsTransport": [
        "pet", "mount", "familiar", "mount_equipment", "vehicle", "spaceship", "airship", "portal", "teleporter",
    ],
    "Institutions": [
        "academy", "university", "school", "library", "research_center", "archive", "museum",
    ],
    "Media": [
        "newspaper", "radio", "television", "internet", "social_media", "propaganda", "rumor",
    ],
    "Secrets": [
        "secret_area", "hidden_path", "easter_egg", "mystery", "enigma", "riddle", "puzzle", "trap",
    ],
    "ArtCulture": [
        "festival", "celebration", "ceremony", "concert", "exhibition", "competition", "tournament",
    ],
}

def camel_case(name):
    """Convert to camel case (character_evolution -> CharacterEvolution)."""
    parts = name.split('_')
    return ''.join(part.capitalize() for part in parts)

def create_interface(entity: str, category: str) -> bool:
    """Create repository interface for an entity."""
    entity_camel = camel_case(entity)
    interface_name = f"I{entity_camel}Repository"
    
    interface_code = f'''"""
{entity_camel} Repository Interface

Port for persisting and retrieving {entity_camel} entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.{entity} import {entity_camel}
from ..value_objects.common import TenantId, EntityId


class {interface_name}(ABC):
    """
    Repository interface for {entity_camel} entity.
    
    {entity_camel}s belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: {entity_camel}) -> {entity_camel}:
        """
        Save an entity (insert or update).
        
        Args:
            entity: {entity_camel} to save
        
        Returns:
            Saved entity with ID populated
        
        Raises:
            DuplicateEntity: If entity name exists in world
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        entity_id: EntityId,
    ) -> Optional[{entity_camel}]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[{entity_camel}]:
        """List all entities in a world with pagination."""
        pass
    
    def delete(
        self,
        tenant_id: TenantId,
        entity_id: EntityId,
    ) -> bool:
        """
        Delete an entity.
        
        Returns:
            True if deleted, False if not found
        """
        pass
'''
    
    # Write to file
    interface_path = project_root / "src" / "domain" / "repositories" / f"{entity}_repository.py"
    interface_path.write_text(interface_code)
    
    return True

def main():
    print("=" * 80)
    print("GENERATING ALL REMAINING REPOSITORY INTERFACES")
    print("=" * 80)
    print()
    
    total = 0
    by_category = {}
    
    for category, entities in CATEGORIES.items():
        print(f"Category: {category} ({len(entities)} entities)")
        created = 0
        
        for entity in entities:
            if entity in IMPLEMENTED:
                continue
            
            try:
                if create_interface(entity, category):
                    created += 1
                    total += 1
            except Exception as e:
                print(f"  ❌ Error creating {entity}: {e}")
        
        print(f"  ✓ Created {created} interfaces")
        by_category[category] = created
        print()
    
    print("=" * 80)
    print(f"✅ Done! Created {total} repository interfaces across {len(CATEGORIES)} categories")
    print("=" * 80)
    print()
    print("Summary by category:")
    for category, count in by_category.items():
        print(f"  {category}: {count}")
    
    print()
    print("Next steps:")
    print("  1. Run: python3 create_all_implementations.py")
    print("  2. Commit: git add -A && git commit -m 'feat: Add all remaining repository interfaces'")
    print("  3. Push: git push origin master")

if __name__ == "__main__":
    main()
