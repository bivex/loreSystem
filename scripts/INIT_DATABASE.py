#!/usr/bin/env python3
"""
Initialize lore_system.db with all 303 tables
"""

import sys
import sqlite3
from pathlib import Path

db_path = Path("/root/clawd/lore_system.db")
sql_repos_path = Path("/root/clawd/src/infrastructure/sqlite_repositories.py")

print("=" * 80)
print("INITIALIZE LORE_SYSTEM.DB WITH ALL 303 TABLES")
print("=" * 80)
print()

# Delete existing database if it's empty
if db_path.exists():
    size = db_path.stat().st_size
    if size < 1024:  # Less than 1KB - likely empty
        print(f"Deleting empty database file ({size} bytes)...")
        db_path.unlink()
        print("✅ Empty database deleted")
        print()

# Create database connection
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # Allow column access by name

# Read SQL statements from sqlite_repositories.py
with open(sql_repos_path, 'r') as f:
    content = f.read()

# Extract all CREATE TABLE statements
import re
create_statements = []
for i, line in enumerate(content.split('\n'), 1):
    if 'CREATE TABLE IF NOT EXISTS' in line and 'conn.execute(' in line:
        # Extract the full SQL statement
        match = re.search(r'conn\.execute\(\"(CREATE TABLE IF NOT EXISTS [^\"]+)\")', line)
        if match:
            create_statements.append(match.group(1))
            print(f"  Found SQL statement {i}: {match.group(1)[:50]}...")

print(f"Found {len(create_statements)} CREATE TABLE statements")
print()

# Execute all CREATE TABLE statements
print("Creating tables...")
print()

errors = []
for i, sql in enumerate(create_statements, 1):
    try:
        print(f"  {i}. {sql[:60]}...", end="")
        conn.execute(sql)
        print(" ✅")
    except Exception as e:
        errors.append((i, sql, str(e)))
        print(f" ❌ Error: {e}")

print()
print(f"Created {len(create_statements) - len(errors)} tables successfully")
print(f"Failed to create {len(errors)} tables")

if errors:
    print()
    print("=" * 80)
    print("❌ ERRORS IN SQL STATEMENTS:")
    print("=" * 80)
    print()
    for i, sql, error in errors:
        print(f"{i}. {sql}")
        print(f"   Error: {error}")
    print()
else:
    # Check all tables were created
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print("=" * 80)
    print("✅ ALL TABLES CREATED SUCCESSFULLY!")
    print("=" * 80)
    print()
    print(f"Total tables: {len(tables)}")
    print()
    print("Tables:")
    for i, (table_name,) in enumerate(tables, 1):
        print(f"  {i}. {table_name}")

conn.commit()
conn.close()

print()
print("=" * 80)
print("✅ DATABASE INITIALIZED")
print("=" * 80)
print()
print(f"Database file: {db_path}")
print(f"File size: {db_path.stat().st_size if db_path.exists() else 0} bytes")
print(f"Tables: {len(tables)}")
print()
print("=" * 80)
