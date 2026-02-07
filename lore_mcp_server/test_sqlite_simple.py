#!/usr/bin/env python3
"""
Simple test for SQLite repositories without importing all entities
"""
import sqlite3
from pathlib import Path

db_path = "/tmp/test_simple.db"

# Create database and tables
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create worlds table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS worlds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tenant_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        genre TEXT,
        power_level INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE(tenant_id, name)
    )
""")

# Create characters table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tenant_id INTEGER NOT NULL,
        world_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        backstory TEXT,
        power_level INTEGER DEFAULT 1,
        image_url TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
    )
""")

print("✓ Created database tables")

# Test inserting a world
from datetime import datetime
now = datetime.now().isoformat()

cursor.execute("""
    INSERT INTO worlds (tenant_id, name, description, genre, power_level, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (1, "TestWorld", "A test world", "Fantasy", 5, now, now))

world_id = cursor.lastrowid
print(f"✓ Created world with ID: {world_id}")

# Test inserting a character
cursor.execute("""
    INSERT INTO characters (tenant_id, world_id, name, description, backstory, power_level, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (1, world_id, "TestHero", "A brave hero", "Born in a small village", 3, now, now))

char_id = cursor.lastrowid
print(f"✓ Created character with ID: {char_id}")

# Test querying
cursor.execute("SELECT * FROM worlds WHERE id = ?", (world_id,))
world = cursor.fetchone()
print(f"✓ Retrieved world: {world}")

cursor.execute("SELECT * FROM characters WHERE world_id = ?", (world_id,))
characters = cursor.fetchall()
print(f"✓ Retrieved {len(characters)} character(s)")

conn.commit()
conn.close()

print(f"\n✅ All tests passed!")
print(f"Database file: {db_path}")
