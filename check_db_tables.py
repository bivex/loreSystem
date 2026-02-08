#!/usr/bin/env python3
"""
Check tables in lore_system.db
"""

import sqlite3

db_path = "/root/clawd/lore_system.db"

print("=" * 80)
print("CHECK TABLES IN LORE_SYSTEM.DB")
print("=" * 80)
print()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if database has tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"Total tables in database: {len(tables)}")
print()

if len(tables) == 0:
    print("❌ NO TABLES FOUND IN DATABASE!")
    print()
    print("Database file exists but contains no tables.")
    print("SQL schema initialization may have failed.")
    print()
    print("Possible causes:")
    print("  1. Database file exists but was never initialized")
    print("  2. SQLiteDatabase.initialize_schema() was never called")
    print("  3. CREATE TABLE statements were not executed")
    print("  4. SQL statements had syntax errors and were not created")
    print()
    print("Solution:")
    print("  1. Call SQLiteDatabase.initialize_schema() to create all tables")
    print("  2. Verify SQL syntax in sqlite_repositories.py")
    print("  3. Check for errors in CREATE TABLE statements")
else:
    print("Tables found:")
    for i, (table_name,) in enumerate(tables, 1):
        print(f"  {i}. {table_name}")

print()
print("=" * 80)
print(f"Database file: {db_path}")
print(f"File size: {db_path.stat().st_size} bytes")
print()
print("Next steps:")
print("  1. If no tables found: Initialize database with SQLiteDatabase.initialize_schema()")
print("  2. If tables found: Check structure is correct")
print("  3. Verify all 303 entities have tables")
print("  4. Test CRUD operations")
print("=" * 80)

conn.close()
