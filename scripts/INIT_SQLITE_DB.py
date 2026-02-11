#!/usr/bin/env python3
"""
Initialize SQLite database and check all tables
"""

import sys
sys.path.insert(0, '/root/clawd')

from pathlib import Path
from src.infrastructure.sqlite_repositories import SQLiteDatabase

print("=" * 80)
print("INITIALIZE SQLITE DATABASE AND CHECK TABLES")
print("=" * 80)
print()

# Create database instance
db_path = "/root/clawd/lore_system.db"
db = SQLiteDatabase(db_path)

print(f"Database path: {db_path}")
print(f"Database exists: {Path(db_path).exists()}")
print()

# Initialize schema (create all tables)
print("Initializing schema...")
db.initialize_schema()
print("✅ Schema initialized")
print()

# Check all tables
print("Checking all tables...")
with db.get_connection() as conn:
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()

    print(f"Total tables: {len(tables)}")
    print()
    
    # Print all tables
    print("Tables:")
    for i, (table_name,) in enumerate(tables, 1):
        print(f"  {i}. {table_name}")

print()
print("=" * 80)
print(f"✅ DATABASE INITIALIZED: {len(tables)} tables created")
print("=" * 80)
print()
print("Next steps:")
print("  1. Check if all 303 tables are created")
print("  2. Verify foreign key relationships")
print("  3. Test CRUD operations")
print("=" * 80)
