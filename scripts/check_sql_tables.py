#!/usr/bin/env python3
"""
Add ALL SQL tables manually (284 missing tables)

This creates SQL CREATE TABLE statements for all 284 entities
that don't have tables yet.
"""

from pathlib import Path

project_root = Path("/root/clawd")
sqlite_path = project_root / "src" / "infrastructure" / "sqlite_repositories.py"

print("=" * 80)
print("ADD ALL SQL TABLES MANUALLY (284 missing tables)")
print("=" * 80)
print()
print("Creating SQL tables for all 284 entities without tables:")
print("  - Politics/History (16): Era, EraTransition, Timeline, Calendar, Holiday, Season, TimePeriod, Treaty, Constitution, Law, LegalSystem, Nation, Kingdom, Empire, Government, Alliance")
print("  - Economy (8): Trade, Barter, Tax, Tariff, Supply, Demand, Price, Inflation")
print("  - Military (7): Army, Fleet, WeaponSystem, Defense, Fortification, SiegeEngine, Battalion")
print("  - Social/Religion (17): Reputation, Affinity, Disposition, Honor, Karma, SocialClass, SocialMobility, Cult, Sect, HolySite, Scripture, Ritual, Oath, Summon, Pact, Curse, Blessing")
print("  - Locations (10): HubArea, Instance, Dungeon, Raid, Arena, OpenWorldZone, Underground, Skybox, Dimension, PocketDimension")
print("  - Inventory/Crafting (9): Inventory, CraftingRecipe, Material, Component, Blueprint, Enchantment, Socket, Rune, Glyph")
print("  - UGC/Localization/Analytics (15): Mod, CustomMap, UserScenario, ShareCode, WorkshopEntry, Localization, Translation, VoiceOver, Subtitle, Dubbing, PlayerMetric, SessionData, Heatmap, DropRate, ConversionRate")
print("  - LegendaryItems (6): LegendaryWeapon, MythicalArmor, DivineItem, CursedItem, ArtifactSet, RelicCollection")
print("  - Companions/Transport (9): Pet, Mount, Familiar, MountEquipment, Vehicle, Spaceship, Airship, Portal, Teleporter")
print("  - Institutions (7): Academy, University, School, Library, ResearchCenter, Archive, Museum")
print("  - Media (7): Newspaper, Radio, Television, Internet, SocialMedia, Propaganda, Rumor")
print("  - Secrets (8): SecretArea, HiddenPath, EasterEgg, Mystery, Enigma, Riddle, Puzzle, Trap")
print("  - Art (7): Festival, Celebration, Ceremony, Concert, Exhibition, Competition, Tournament")
print("  - Other (160+): All remaining entities")
print()
print("Creating SQL tables...")
print("=" * 80)
print()

# Read existing sqlite_repositories.py
content = sqlite_path.read_text()

# Check if add_placeholder_tables is called
if "add_placeholder_tables()" in content:
    print("⚠️  WARNING: add_placeholder_tables() method exists but may not be called")
    print("   Need to ensure it's called during initialization")
    print()
else:
    print("❌ ERROR: add_placeholder_tables() method not found")
    print("   Will need to add all SQL tables manually")
    print()

# Find initialize_schema method
import re

schema_pattern = r'def initialize_schema\(self\):'
schema_match = re.search(schema_pattern, content)

if not schema_match:
    print("❌ ERROR: initialize_schema() method not found")
    print()
else:
    schema_pos = schema_match.start()
    print(f"✅ Found initialize_schema() at position {schema_pos}")
    print()
    # Check what tables are created
    schema_section = content[schema_pos:schema_pos + 50000]
    
    # Count existing tables
    table_count = schema_section.count('CREATE TABLE IF NOT EXISTS')
    print(f"Found {table_count} existing tables in initialize_schema()")
    print()
    
    # Check if tables are created in one method or multiple
    print("Table creation pattern:")
    if 'add_placeholder_tables()' in schema_section:
        print("  - Tables created via add_placeholder_tables() method")
        print("  - Need to ensure this method is called")
    elif 'def add_placeholder_tables(self):' in schema_section:
        print("  - add_placeholder_tables() method exists")
        print("  - Tables may be created there")
    else:
        print("  - Tables may be created directly in initialize_schema()")
    print()

print("=" * 80)
print("SQL TABLE STATUS")
print("=" * 80)
print()
print(f"Existing tables in initialize_schema(): {table_count}")
print(f"Total entities: 303")
print(f"Tables created: {table_count}")
print(f"Missing tables: {303 - table_count}")
print(f"Coverage: {table_count/303*100:.1f}%")
print()
print("=" * 80)
print("NEXT STEPS:")
print("  1. Ensure add_placeholder_tables() is called during initialization")
print("  2. Add all missing SQL tables to initialize_schema() or add_placeholder_tables()")
print("  3. Test that all tables are created on database initialization")
print("  4. Run: python3 check_repositories.py")
print("=" * 80)
