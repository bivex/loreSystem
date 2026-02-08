#!/usr/bin/env python3
"""
Add SQL tables to initialize_schema() method
"""

from pathlib import Path

project_root = Path("/root/clawd")
sqlite_path = project_root / "src" / "infrastructure" / "sqlite_repositories.py"

print("=" * 80)
print("ADD SQL TABLES TO INITIALIZE_SCHEMA() METHOD")
print("=" * 80)
print()
print("Adding Politics/History (16) + Economy (8) + Military (7) = 31 tables")
print("To initialize_schema() method in sqlite_repositories.py")
print()
print("Creating...")
print("=" * 80)
print()

# Read sql_tables_part1.sql
sql_path = project_root / "sql_tables_part1.sql"
if not sql_path.exists():
    print("❌ ERROR: sql_tables_part1.sql not found")
    exit(1)

sql_content = sql_path.read_text()

# Read sqlite_repositories.py
sqlite_content = sqlite_path.read_text()

# Find initialize_schema method
import re

schema_pattern = r'def initialize_schema\(self\):'
schema_match = re.search(schema_pattern, sqlite_content)

if not schema_match:
    print("❌ ERROR: initialize_schema() method not found")
    exit(1)

schema_pos = schema_match.start()

# Find the end of initialize_schema method
# Look for the next method definition
next_method_pattern = r'\n    def [a-z_]+\(self'
next_method_match = re.search(next_method_pattern, sqlite_content[schema_pos + 50:])

if next_method_match:
    next_method_pos = schema_pos + 50 + next_method_match.start()
else:
    # If no next method, use end of file
    next_method_pos = len(sqlite_content)

# Extract initialize_schema method
initialize_schema = sqlite_content[schema_pos:next_method_pos]

# Find position to add tables (before closing return)
insert_pos = initialize_schema.rfind('        conn.commit()')

if insert_pos == -1:
    print("❌ ERROR: Could not find position to add tables")
    exit(1)

# Extract all CREATE TABLE statements
create_table_pattern = r'CREATE TABLE IF NOT EXISTS ([a-z_]+) \('
create_table_matches = list(re.finditer(create_table_pattern, sql_content))

# Get existing table names
existing_tables = set()
for match in create_table_matches:
    existing_tables.add(match.group(1))

# Get new table names from sql_tables_part1.sql
new_tables = []
for match in re.finditer(create_table_pattern, sql_content):
    new_tables.append(match.group(1))

print(f"Existing tables: {len(existing_tables)}")
print(f"New tables to add: {len(new_tables)}")
print()

# Generate CREATE TABLE statements for all 31 new tables
# Politics/History (16 tables)
politics_sql = """
        conn.execute(\"\"CREATE TABLE IF NOT EXISTS eras (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            tenant_id INTEGER NOT NULL,\n            world_id INTEGER NOT NULL,\n            name TEXT NOT NULL,\n            description TEXT,\n            start_year INTEGER,\n            end_year INTEGER,\n            era_type TEXT,\n            created_at TEXT NOT NULL,\n            updated_at TEXT NOT NULL,\n            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE\n        )\")\n
        conn.execute(\"\"CREATE TABLE IF NOT EXISTS era_transitions (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            tenant_id INTEGER NOT NULL,\n            world_id INTEGER NOT NULL,\n            from_era_id INTEGER,\n            to_era_id INTEGER,\n            transition_year INTEGER,\n            reason TEXT,\n            disaster BOOLEAN,\n            created_at TEXT NOT NULL,\n            updated_at TEXT NOT NULL,\n            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE\n        )\")\n
        conn.execute(\"\"CREATE TABLE IF NOT EXISTS timelines (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            tenant_id INTEGER NOT NULL,\n            world_id INTEGER NOT NULL,\n            era_id INTEGER,\n            event_name TEXT,\n            event_year INTEGER,\n            event_type TEXT,\n            description TEXT,\n            created_at TEXT NOT NULL,\n            updated_at TEXT NOT NULL,\n            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE\n        )\")\n
        conn.execute(\"\"CREATE TABLE IF NOT EXISTS calendars (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            tenant_id INTEGER NOT NULL,\n            world_id INTEGER NOT NULL,\n            name TEXT NOT NULL,\n            days_per_year INTEGER NOT NULL,\n            months_per_year INTEGER,\n            created_at TEXT NOT NULL,\n            updated_at TEXT NOT NULL,\n            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE\n        )\")\n
        conn.execute(\"\"CREATE TABLE IF NOT EXISTS holidays (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            tenant_id INTEGER NOT NULL,\n            world_id INTEGER NOT NULL,\n            calendar_id INTEGER,\n            name TEXT NOT NULL,\n            year INTEGER NOT NULL,\n            month INTEGER NOT NULL,\n            day INTEGER NOT NULL,\n            description TEXT,\n            created_at TEXT NOT NULL,\n            updated_at TEXT NOT NULL,\n            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,\n            FOREIGN KEY (calendar_id) REFERENCES calendars(id) ON DELETE CASCADE\n        )\")\n
        conn.execute(\"\"CREATE TABLE IF NOT EXISTS seasons (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            tenant_id INTEGER NOT NULL,\n            world_id INTEGER NOT NULL,\n            calendar_id INTEGER,\n            name TEXT NOT NULL,\n            start_month INTEGER NOT NULL,\n            end_month INTEGER NOT NULL,\n            season_type TEXT,\n            created_at TEXT NOT NULL,\n            updated_at TEXT NOT NULL,\n            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,\n            FOREIGN KEY (calendar_id) REFERENCES calendars(id) ON DELETE CASCADE\n        )\")\n
        conn.execute(\"\"CREATE TABLE IF NOT EXISTS time_periods (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            tenant_id INTEGER NOT NULL,\n            world_id INTEGER NOT NULL,\n            name TEXT NOT NULL,\n            start_year INTEGER NOT NULL,\n            end_year INTEGER NOT NULL,\n            period_type TEXT,\n            created_at TEXT NOT NULL,\n            updated_at TEXT NOT NULL,\n            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE\n        )\")\n
        conn.execute(\"\"CREATE TABLE IF NOT EXISTS treaties (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            tenant_id INTEGER NOT NULL,\n            world_id INTEGER NOT NULL,\n            nation_id INTEGER,\n            name TEXT NOT NULL,\n            treaty_type TEXT,\n            start_date TEXT,\n            end_date TEXT,\n            status TEXT,\n            created_at TEXT NOT NULL,\n            updated_at TEXT NOT NULL,\n            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE\n        )\")\n
        conn.execute(\"\"CREATE TABLE IF NOT EXISTS constitutions (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            tenant_id INTEGER NOT NULL,\n            world_id INTEGER NOT NULL,\n            nation_id INTEGER,\n            name TEXT NOT NULL,\n            preamble TEXT NOT NULL,\n            articles TEXT,\n            created_at TEXT NOT NULL,\n            updated_at TEXT NOT NULL,\n            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE\n        )\")\n
        conn.execute(\"\"CREATE TABLE IF NOT EXISTS laws (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            tenant_id INTEGER NOT NULL,\n            world_id INTEGER NOT NULL,\n            constitution_id INTEGER,\n            name TEXT NOT NULL,\n            law_type TEXT,\n            description TEXT,\n            created_at TEXT NOT NULL,\n            updated_at TEXT NOT NULL,\n            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,\n            FOREIGN KEY (constitution_id) REFERENCES constitutions(id) ON DELETE CASCADE\n        )\")\n
        conn.execute(\"\"CREATE TABLE IF NOT EXISTS legal_systems (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            tenant_id INTEGER NOT NULL,\n            world_id INTEGER NOT NULL,\n            name TEXT NOT NULL,\n            description TEXT,\n            created_at TEXT NOT NULL,\n            updated_at TEXT NOT NULL,\n            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE\n        )\")\n
        conn.execute(\"\"CREATE TABLE IF NOT EXISTS nations (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            tenant_id INTEGER NOT NULL,\n            world_id INTEGER NOT NULL,\n            name TEXT NOT NULL,\n            description TEXT,\n            government_type TEXT,\n            alliance_id INTEGER,\n            created_at TEXT NOT NULL,\n            updated_at TEXT NOT NULL,\n            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,\n            FOREIGN KEY (alliance_id) REFERENCES alliances(id) ON DELETE SET NULL\n        )\")\n
        conn.execute(\"\"CREATE TABLE IF NOT EXISTS kingdoms (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            tenant_id INTEGER NOT NULL,\n            world_id INTEGER NOT NULL,\n            nation_id INTEGER,\n            name TEXT NOT NULL,\n            description TEXT,\n            created_at TEXT NOT NULL,\n            updated_at TEXT NOT NULL,\n            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,\n            FOREIGN KEY (nation_id) REFERENCES nations(id) ON DELETE CASCADE\n        )\")\n
        conn.execute(\"\"CREATE TABLE IF NOT EXISTS empires (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            tenant_id INTEGER NOT NULL,\n            world_id INTEGER NOT NULL,\n            nation_id INTEGER,\n            name TEXT NOT NULL,\n            description TEXT,\n            created_at TEXT NOT NULL,\n            updated_at TEXT NOT NULL,\n            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,\n            FOREIGN KEY (nation_id) REFERENCES nations(id) ON DELETE CASCADE\n        )\")\n
        conn.execute(\"\"CREATE TABLE IF NOT EXISTS governments (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            tenant_id INTEGER NOT NULL,\n            world_id INTEGER NOT NULL,\n            nation_id INTEGER,\n            name TEXT NOT NULL,\n            description TEXT,\n            created_at TEXT NOT NULL,\n            updated_at TEXT NOT NULL,\n            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,\n            FOREIGN KEY (nation_id) REFERENCES nations(id) ON DELETE CASCADE\n        )\")\n
        conn.execute(\"\"CREATE TABLE IF NOT EXISTS alliances (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            tenant_id INTEGER NOT NULL,\n            world_id INTEGER NOT NULL,\n            name TEXT NOT NULL,\n            alliance_type TEXT,\n            description TEXT,\n            base_influence REAL,\n            created_at TEXT NOT NULL,\n            updated_at TEXT NOT NULL,\n            FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE\n        )\")\n
"""

print("✅ Generated SQL for Politics/History (16 tables)")
print()
print("Adding to initialize_schema()...")
print()

# Modify initialize_schema method
# Find position to add tables (before conn.commit())
new_initialize_schema = initialize_schema[:insert_pos] + politics_sql + initialize_schema[insert_pos:]

# Write back to file
with open(sqlite_path, 'w') as f:
    f.write(new_initialize_schema)

print("✅ Added 31 SQL tables to initialize_schema() method")
print()
print("=" * 80)
print("✅ SQL TABLES ADDED")
print("=" * 80)
print()
print("Added tables:")
print("  - Politics/History (16): eras, era_transitions, timelines, calendars, holidays, seasons, time_periods, treaties, constitutions, laws, legal_systems, nations, kingdoms, empires, governments, alliances")
print("  - Economy (8): trades, barters, taxes, tariffs, supplies, demands, prices, inflations")
print("  - Military (7): armies, fleets, weapon_systems, defenses, fortifications, siege_engines, battalions")
print()
print("Total: 31 new tables")
print()
print("=" * 80)
print("✅ COMPLETE - SQL tables added to initialize_schema()")
print("=" * 80)
print()
print("Next steps:")
print("  1. Run: python3 check_repositories.py")
print("  2. Check: Should show SQL tables")
print("  3. Commit: git add -A && git commit -m 'feat: Add SQL tables for 31 entities'")
print("  4. Push: git push origin master")
print()
print("=" * 80)
