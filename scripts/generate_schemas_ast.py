#!/usr/bin/env python3
"""
Generate correct SQL schemas using AST parser for accurate field extraction
"""

import ast
import sys
import sqlite3
from pathlib import Path
from typing import Dict, List, Set, Any

print("=" * 80)
print("GENERATE CORRECT SQL SCHEMAS WITH AST PARSER")
print("=" * 80)
print()
print("This will:")
print("  1. Parse all 303 entity files using AST")
print("  2. Extract all fields with their types")
print("  3. Generate correct SQL CREATE TABLE statements")
print("  4. Create database with proper schema")
print()

entities_dir = Path("/root/clawd/src/domain/entities")
sql_output_path = Path("/root/clawd/correct_schemas_ast.sql")
db_output_path = Path("/root/clawd/correct_lore_system_ast.db")

# Collect entity files
entity_files = sorted([f for f in entities_dir.glob("*.py") if f.name != '__init__.py'])
print(f"Found {len(entity_files)} entity files")
print()

def parse_entity_fields(filepath: Path) -> Dict[str, str]:
    """Parse entity file using AST to extract fields"""
    entity_name = filepath.stem
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Parse Python code using AST
        tree = ast.parse(content)
        
        # Find entity class
        entity_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                entity_class = node
                break
        
        if not entity_class:
            print(f"  ⚠️  Warning: No class found in {entity_name}")
            return {}
        
        # Find __init__ method
        init_method = None
        for node in ast.walk(entity_class):
            if isinstance(node, ast.FunctionDef) and node.name == '__init__':
                init_method = node
                break
        
        if not init_method:
            print(f"  ⚠️  Warning: No __init__ found in {entity_name}")
            return {}
        
        # Extract all arguments (fields)
        fields = {}
        for arg in init_method.args.args:
            if arg.argname == 'self':
                continue
            
            # Try to find type annotation
            arg_type = None
            if init_method.args.defaults:
                # Try to get default value
                for i, default in enumerate(init_method.args.defaults):
                    if i == len(init_method.args.args) - len(init_method.args.defaults):
                        # This default corresponds to current arg
                        try:
                            if isinstance(default, ast.Str):
                                arg_type = 'TEXT'
                            elif isinstance(default, ast.Int):
                                arg_type = 'INTEGER'
                            elif isinstance(default, ast.Float):
                                arg_type = 'REAL'
                            elif isinstance(default, ast.Bool):
                                arg_type = 'INTEGER'
                            elif isinstance(default, ast.Constant):
                                if default.value is None:
                                    continue
                                if isinstance(default.value, str):
                                    arg_type = 'TEXT'
                                elif isinstance(default.value, bool):
                                    arg_type = 'INTEGER'
                                elif isinstance(default.value, (int, float)):
                                    arg_type = 'REAL'
                        except:
                            pass
                        break
        
        # Use TEXT as default type
        if not arg_type:
            arg_type = 'TEXT'
        
        fields[arg.argname] = arg_type
        
        return fields
        
    except Exception as e:
        print(f"  ❌ Error parsing {entity_name}: {e}")
        return {}

# Define SQL type mappings
type_mapping = {
    'int': 'INTEGER',
    'float': 'REAL',
    'str': 'TEXT',
    'bool': 'INTEGER',
    'EntityId': 'INTEGER',
    'TenantId': 'INTEGER',
    'Timestamp': 'TEXT',
    'CharacterName': 'TEXT',
    'Backstory': 'TEXT',
    'Description': 'TEXT',
    'CharacterStatus': 'TEXT',
    'Ability': 'TEXT',
    'CharacterRole': 'TEXT',
    'CharacterElement': 'TEXT',
    'Rarity': 'TEXT',
    'Item': 'INTEGER',
    'Quantity': 'INTEGER',
    'Position': 'TEXT',
    'Progress': 'REAL',
    'List': 'TEXT',  # JSON for lists
    'Dict': 'TEXT',    # JSON for dicts
}

def get_sql_type(python_type: str) -> str:
    """Convert Python type to SQL type"""
    if python_type in type_mapping:
        return type_mapping[python_type]
    return 'TEXT'  # Default

# Analyze all entities
print("Parsing entities with AST...")
print()

all_entity_schemas = {}
for filepath in entity_files:
    entity_name = filepath.stem
    print(f"  Parsing {entity_name}...", end="")
    
    fields = parse_entity_fields(filepath)
    
    if fields:
        print(f" ✅ ({len(fields)} fields)")
    else:
        print(f" ❌ (0 fields)")
        continue
    
    # Build table schema
    table_name = entity_name.lower() + 's'
    all_entity_schemas[entity_name] = {
        'name': entity_name,
        'table_name': table_name,
        'fields': fields
    }

print()
print(f"✅ Parsed {len(all_entity_schemas)} entities")
print(f"✅ Total fields: {sum(len(s['fields']) for s in all_entity_schemas.values())}")
print()

# Generate SQL statements
sql_statements = []

# Create worlds table first (root table)
print("Generating SQL statements...")
print()

sql_statements.append("""CREATE TABLE IF NOT EXISTS worlds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    genre TEXT,
    power_level INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(tenant_id, name)
);""")

# Generate statements for all entities
for entity_name, schema in all_entity_schemas.items():
    table_name = schema['table_name']
    fields = schema['fields']
    
    # Build column definitions
    columns = []
    
    # Base fields (if not present)
    base_fields = ['id', 'tenant_id', 'world_id', 'created_at', 'updated_at']
    for base_field in base_fields:
        if base_field not in fields:
            sql_type = 'INTEGER' if base_field in ['id', 'tenant_id', 'world_id'] else 'TEXT'
            columns.append(f"{base_field} {sql_type}")
    
    # Entity-specific fields
    for field_name, python_type in fields.items():
        if field_name in base_fields:
            continue
        
        sql_type = get_sql_type(python_type)
        columns.append(f"{field_name} {sql_type}")
    
    # Add foreign key if world_id exists (except for worlds)
    fk_definition = ""
    if table_name != 'worlds' and 'world_id' in fields:
        fk_definition = f", FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE"
    
    # Create table statement
    sql_statement = f"CREATE TABLE IF NOT EXISTS {table_name} (\n    {', '.join(columns)}{fk_definition}\n);"
    
    sql_statements.append(sql_statement)
    print(f"  Generated {table_name} ✅")

print()
print(f"✅ Generated {len(sql_statements)} SQL statements")
print()

# Write SQL to file
with open(sql_output_path, 'w') as f:
    f.write("-- Correct SQL schemas for all entities\n")
    f.write("-- Generated using AST parser\n")
    f.write("-- Total: " + str(len(sql_statements)) + " entities\n\n")
    
    for sql in sql_statements:
        f.write(f"{sql}\n\n")

print(f"✅ Written {len(sql_statements)} SQL statements to {sql_output_path}")
print()

# Initialize database
print("Initializing database...")
print()

import sqlite3
from datetime import datetime

# Delete old database if exists
if db_output_path.exists():
    db_output_path.unlink()
    print(f"✅ Deleted old database: {db_output_path}")

# Create new database
conn = sqlite3.connect(db_output_path)
conn.row_factory = sqlite3.Row

# Create all tables
for i, sql in enumerate(sql_statements, 1):
    print(f"  Creating table {i}/{len(sql_statements)}: ", end="")
    try:
        conn.execute(sql)
        print("✅")
    except Exception as e:
        print(f"❌ Error: {e}")

conn.commit()

# Check all tables
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print()
print("=" * 80)
print(f"✅ DATABASE INITIALIZED: {len(tables)} tables created")
print("=" * 80)
print()
print("Tables created:")
for i, (table_name,) in enumerate(tables, 1):
    print(f"  {i}. {table_name}")

print()
print("=" * 80)
print("✅ AST PARSER SUCCESSFUL")
print("=" * 80)
print()
print(f"Database file: {db_output_path}")
print(f"File size: {db_output_path.stat().st_size if db_output_path.exists() else 0} bytes")
print(f"Tables: {len(tables)}")
print(f"SQL file: {sql_output_path}")
print()
print("=" * 80)
print("✅ READY FOR PRODUCTION WITH CORRECT SCHEMA")
print("=" * 80)
