#!/usr/bin/env python3
"""
Initialize SQLite database and check all tables
"""

import sqlite3
import re
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("INITIALIZE SQLITE DATABASE AND CHECK TABLES")
print("=" * 80)
print()

db_path = "/root/clawd/lore_system.db"
sql_repos_path = Path("/root/clawd/src/infrastructure/sqlite_repositories.py")

# Read sqlite_repositories.py to extract CREATE TABLE statements
with open(sql_repos_path, 'r') as f:
    content = f.read()

# Extract all CREATE TABLE statements
create_statements = []
table_pattern = r'CREATE TABLE IF NOT EXISTS ([a-z_]+)'
for i, line in enumerate(content.split('\n')):
    if 'CREATE TABLE IF NOT EXISTS' in line:
        match = re.search(table_pattern, line)
        if match:
            create_statements.append((i + 1, line.strip()))

print(f"Found {len(create_statements)} CREATE TABLE statements in code")
print()

# Create database and initialize schema
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # Allow column access by name

print("Creating database and tables...")
print()

for line_num, statement in create_statements:
    print(f"  {line_num}. {statement[:50]}...")
    try:
        conn.execute(statement)
        print(f"     ✅ Success")
    except Exception as e:
        print(f"     ❌ Error: {e}")

conn.commit()
print()

# Check all tables
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"Total tables created: {len(tables)}")
print()
print("Tables in database:")
for i, (table_name,) in enumerate(tables, 1):
    print(f"  {i}. {table_name}")

print()
print("=" * 80)
print(f"✅ DATABASE INITIALIZED: {len(tables)} tables")
print()
print(f"Database file: {db_path}")
print(f"File size: {Path(db_path).stat().st_size} bytes")
print()
print("=" * 80)
print("Next steps:")
print("  1. Check if all 303 entities have tables")
print("  2. Verify foreign key relationships")
print("  3. Test CRUD operations")
print("=" * 80)

conn.close()
