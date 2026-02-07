#!/usr/bin/env python3
"""
Quick script to append SQLite tables only
"""

from pathlib import Path

sqlite_path = Path("/root/clawd/src/infrastructure/sqlite_repositories.py")

entities = ["character_evolution", "character_variant", "character_profile_entry", "motion_capture", "voice_actor",
    "act", "chapter", "episode", "prologue", "epilogue", "plot_branch", "consequence", "ending", "alternate_reality",
    "inventory", "crafting_recipe", "material", "component", "blueprint", "enchantment", "socket", "rune", "glyph",
    "hub_area", "instance", "dungeon", "raid", "arena", "open_world_zone", "underground", "skybox", "dimension", "pocket_dimension",
    "era", "era_transition", "timeline", "calendar", "holiday", "season", "time_period", "treaty", "constitution", "law", "legal_system", "nation", "kingdom", "empire", "government", "alliance",
    "trade", "barter", "tax", "tariff", "supply", "demand", "price", "inflation",
    "army", "fleet", "weapon_system", "defense", "fortification", "siege_engine", "battalion",
    "reputation", "affinity", "disposition", "honor", "karma", "social_class", "social_mobility",
    "cult", "sect", "holy_site", "scripture", "ritual", "oath", "summon", "pact", "curse", "blessing",
    "lore_fragment", "codex_entry", "journal_page", "bestiary_entry", "memory", "dream", "nightmare",
    "theme", "motif", "score", "soundtrack", "voice_line", "sound_effect", "ambient", "silence",
    "visual_effect", "particle", "shader", "lighting", "color_palette",
    "cutscene", "cinematic", "camera_path", "transition", "fade", "flashback",
    "district", "ward", "quarter", "plaza", "market_square", "slums", "noble_district", "port_district",
    "food_chain", "migration", "hibernation", "reproduction", "extinction", "evolution",
    "galaxy", "nebula", "black_hole", "wormhole", "star_system", "moon", "eclipse", "solstice", "atmosphere",
    "weather_pattern", "cataclysm", "disaster", "miracle", "phenomenon",
    "plot_device", "deus_ex_machina", "chekhovs_gun", "foreshadowing", "flash_forward", "red_herring",
    "world_event", "seasonal_event", "invasion", "plague", "famine", "war", "revolution",
    "fast_travel_point", "waypoint", "save_point", "checkpoint", "autosave", "spawn_point",
    "court", "crime", "judge", "jury", "lawyer", "punishment", "evidence", "witness",
    "achievement", "trophy", "badge", "title", "rank", "leaderboard",
    "mod", "custom_map", "user_scenario", "share_code", "workshop_entry",
    "localization", "translation", "voice_over", "subtitle", "dubbing",
    "player_metric", "session_data", "heatmap", "drop_rate", "conversion_rate",
    "difficulty_curve", "loot_table_weight", "balance_entities",
    "legendary_weapon", "mythical_armor", "divine_item", "cursed_item", "artifact_set", "relic_collection",
    "pet", "mount", "familiar", "mount_equipment", "vehicle", "spaceship", "airship", "portal", "teleporter",
    "academy", "university", "school", "library", "research_center", "archive", "museum",
    "newspaper", "radio", "television", "internet", "social_media", "propaganda", "rumor",
    "secret_area", "hidden_path", "easter_egg", "mystery", "enigma", "riddle", "puzzle", "trap",
    "festival", "celebration", "ceremony", "concert", "exhibition", "competition", "tournament"]

print(f"Adding {len(entities)} SQL tables...")

content = sqlite_path.read_text()
schema_end = content.find('\n        pass', content.find('def initialize_schema'))

if schema_end != -1:
    new_tables = ""
    for entity in entities:
        table_name = f"{entity}s"
        table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        table_sql += "    id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        table_sql += "    tenant_id INTEGER NOT NULL,\n"
        table_sql += "    world_id INTEGER,\n"
        table_sql += "    name TEXT NOT NULL,\n"
        table_sql += "    description TEXT,\n"
        table_sql += "    created_at TEXT NOT NULL,\n"
        table_sql += "    updated_at TEXT NOT NULL,\n"
        table_sql += "    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE\n"
        table_sql += ")\n"
        
        new_tables += f"            # {table_name} table\n            conn.execute(\"{table_sql}\")\n"
        if entity in entities[::10]:
            print(f"  ✓ {table_name}")
    
    content = content[:schema_end] + new_tables + content[schema_end:]
    sqlite_path.write_text(content)
    print(f"✅ Added {len(entities)} SQL tables to sqlite_repositories.py")
else:
    print("❌ Could not find initialize_schema method")
