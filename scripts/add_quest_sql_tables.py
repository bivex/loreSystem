#!/usr/bin/env python3
"""
Add Quest SQL tables to sqlite_repositories.py initialize_schema
"""

from pathlib import Path

sqlite_path = Path("/root/clawd/src/infrastructure/sqlite_repositories.py")

sql_tables = '''
            # Quest chains table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quest_chains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Quest nodes table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quest_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Quest prerequisites table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quest_prerequisites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Quest objectives table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quest_objectives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Quest trackers table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quest_trackers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Quest givers table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quest_givers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Quest rewards table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quest_rewards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Quest reward tiers table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quest_reward_tiers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)
'''

# Append SQL tables to end of initialize_schema method
content = sqlite_path.read_text()

# Find initialize_schema method and its end
schema_start = content.find('def initialize_schema(self):')
if schema_start == -1:
    print("Error: Could not find initialize_schema method")
    sys.exit(1)

method_end = content.find('\n\n    def', schema_start + len('def initialize_schema(self):'))
if method_end == -1:
    method_end = content.find('\n    def', schema_start + 30)

# Find end of method (last statement before next method or end of class)
method_close = content.find('\n\n    def', method_end + 1)
if method_close == -1:
    method_close = content.find('\n    def', method_end + 1)

# Insert SQL tables before method closes
new_content = content[:method_close] + sql_tables + '\n' + content[method_close:]

sqlite_path.write_text(new_content)

print("✅ Added 8 Quest SQL tables to sqlite_repositories.py initialize_schema method")
