#!/usr/bin/env python3
"""
Add SQL tables to initialize_schema() method (31 tables)
"""

import re
from pathlib import Path

project_root = Path("/root/clawd")
sqlite_path = project_root / "src" / "infrastructure" / "sqlite_repositories.py"

print("=" * 80)
print("ADD 31 SQL TABLES TO INITIALIZE_SCHEMA() METHOD")
print("=" * 80)
print()
print("Adding tables for Politics/History (16) + Economy (8) + Military (7)")
print("To initialize_schema() method at position 2716")
print()
print("Creating...")
print("=" * 80)
print()

# Read sqlite_repositories.py
with open(sqlite_path, 'r') as f:
    content = f.read()

# SQL tables to add (31 tables)
tables_sql = """
            # Politics/History (16 tables)
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS eras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                start_year INTEGER,
                end_year INTEGER,
                era_type TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS era_transitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                from_era_id INTEGER,
                to_era_id INTEGER,
                transition_year INTEGER,
                reason TEXT,
                disaster BOOLEAN,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS timelines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                era_id INTEGER,
                event_name TEXT,
                event_year INTEGER,
                event_type TEXT,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS calendars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                days_per_year INTEGER NOT NULL,
                months_per_year INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS holidays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                calendar_id INTEGER,
                name TEXT NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                day INTEGER NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (calendar_id) REFERENCES calendars(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS seasons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                calendar_id INTEGER,
                name TEXT NOT NULL,
                start_month INTEGER NOT NULL,
                end_month INTEGER NOT NULL,
                season_type TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (calendar_id) REFERENCES calendars(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS time_periods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                start_year INTEGER NOT NULL,
                end_year INTEGER NOT NULL,
                period_type TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS treaties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                nation_id INTEGER,
                name TEXT NOT NULL,
                treaty_type TEXT,
                start_date TEXT,
                end_date TEXT,
                status TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS constitutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                nation_id INTEGER,
                name TEXT NOT NULL,
                preamble TEXT NOT NULL,
                articles TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS laws (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                constitution_id INTEGER,
                name TEXT NOT NULL,
                law_type TEXT,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (constitution_id) REFERENCES constitutions(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS legal_systems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS nations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                government_type TEXT,
                alliance_id INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (alliance_id) REFERENCES alliances(id) ON DELETE SET NULL
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS kingdoms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                nation_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (nation_id) REFERENCES nations(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS empires (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                nation_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (nation_id) REFERENCES nations(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS governments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                nation_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (nation_id) REFERENCES nations(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS alliances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                alliance_type TEXT,
                description TEXT,
                base_influence REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n

            # Economy (8 tables)
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                from_nation_id INTEGER,
                to_nation_id INTEGER,
                item_id INTEGER,
                quantity INTEGER,
                price REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS barters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                from_character_id INTEGER,
                to_character_id INTEGER,
                from_item_id INTEGER,
                to_item_id INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS taxes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                nation_id INTEGER,
                tax_type TEXT,
                tax_rate REAL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS tariffs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                nation_id INTEGER,
                tariff_type TEXT,
                rate REAL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS supplies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                location_id INTEGER,
                item_id INTEGER,
                quantity INTEGER,
                supply_rate REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS demands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                location_id INTEGER,
                item_id INTEGER,
                quantity INTEGER,
                demand_rate REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                item_id INTEGER,
                price REAL,
                currency TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS inflations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                inflation_rate REAL,
                period TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n

            # Military (7 tables)
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS armies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                nation_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                unit_count INTEGER,
                total_power REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (nation_id) REFERENCES nations(id) ON DELETE SET NULL
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS fleets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                nation_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                ship_count INTEGER,
                total_power REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (nation_id) REFERENCES nations(id) ON DELETE SET NULL
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS weapon_systems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                weapon_type TEXT,
                damage INTEGER,
                range INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS defenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                territory_id INTEGER,
                defense_type TEXT,
                strength REAL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS fortifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                territory_id INTEGER,
                fort_type TEXT,
                level INTEGER,
                strength REAL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS siege_engines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                engine_type TEXT,
                damage INTEGER,
                range INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
            )\")\n
            conn.execute(\"\"CREATE TABLE IF NOT EXISTS battalions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                army_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                unit_count INTEGER,
                unit_type TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                FOREIGN KEY (army_id) REFERENCES armies(id) ON DELETE SET NULL
            )\")\n
"""

# Find the second initialize_schema method (position ~2716)
schema_pattern = r'def initialize_schema\(self\):.*?\n        with self\.get_connection\(\) as conn:'
match = re.search(schema_pattern, content, re.DOTALL)

if match:
    schema_pos = match.start()
    # Find the end of the method (next method definition or end of file)
    next_method = re.search(r'\n\n    def [a-z_]+\(self', content[schema_pos + 10000:])
    
    if next_method:
        insert_pos = schema_pos + 10000 + next_method.start()
    else:
        insert_pos = len(content)
    
    # Insert the new tables at the end of initialize_schema method
    new_content = content[:insert_pos] + tables_sql + content[insert_pos:]
    
    # Write back to file
    with open(sqlite_path, 'w') as f:
        f.write(new_content)
    
    print("✅ Added 31 SQL tables to initialize_schema() method")
    print()
    print("Tables added:")
    print("  - Politics/History (16): eras, era_transitions, timelines, calendars, holidays, seasons, time_periods, treaties, constitutions, laws, legal_systems, nations, kingdoms, empires, governments, alliances")
    print("  - Economy (8): trades, barters, taxes, tariffs, supplies, demands, prices, inflations")
    print("  - Military (7): armies, fleets, weapon_systems, defenses, fortifications, siege_engines, battalions")
    print()
    print("=" * 80)
    print("✅ COMPLETE - 31 SQL tables added")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Run: python3 check_repositories.py")
    print("  2. Check: Should show SQL tables")
    print("  3. Commit: git add -A && git commit -m 'feat: Add 31 SQL tables'")
    print("  4. Push: git push origin master")
    print("=" * 80)
else:
    print("❌ ERROR: Could not find initialize_schema() method")
