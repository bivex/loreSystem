#!/usr/bin/env python3
"""
Check which repository interfaces are missing implementations.
"""

from pathlib import Path
import re

project_root = Path("/root/clawd")
repos_dir = project_root / "src" / "domain" / "repositories"
in_mem_path = project_root / "src" / "infrastructure" / "in_memory_repositories.py"
sqlite_path = project_root / "src" / "infrastructure" / "sqlite_repositories.py"

# Get all repository interfaces
interfaces = set()
for filepath in repos_dir.glob("*_repository.py"):
    if filepath.name.startswith("__"):
        continue
    
    # Extract class name from file
    with open(filepath, 'r') as f:
        content = f.read()
        match = re.search(r'class\s+I([A-Z][a-zA-Z]+)Repository', content)
        if match:
            interfaces.add(match.group(1))

print(f"Found {len(interfaces)} repository interfaces")
print()

# Check In-Memory implementations
in_mem_content = in_mem_path.read_text()
in_mem_implementations = set()
for match in re.finditer(r'class\s+InMemory([A-Z][a-zA-Z]+)Repository', in_mem_content):
    in_mem_implementations.add(match.group(1))

print(f"Found {len(in_mem_implementations)} In-Memory implementations")
print()

# Check SQLite implementations
sqlite_content = sqlite_path.read_text()
sqlite_implementations = set()
for match in re.finditer(r'class\s+SQLite([A-Z][a-zA-Z]+)Repository', sqlite_content):
    sqlite_implementations.add(match.group(1))

print(f"Found {len(sqlite_implementations)} SQLite implementations")
print()

# Find missing implementations
missing_inmem = interfaces - in_mem_implementations
missing_sqlite = interfaces - sqlite_implementations

print("=" * 80)
print("MISSING IMPLEMENTATIONS")
print("=" * 80)
print()

if missing_inmem:
    print(f"❌ Missing In-Memory implementations ({len(missing_inmem)}):")
    for interface in sorted(missing_inmem):
        print(f"  - {interface}Repository")
    print()
else:
    print("✅ All interfaces have In-Memory implementations")
    print()

if missing_sqlite:
    print(f"❌ Missing SQLite implementations ({len(missing_sqlite)}):")
    for interface in sorted(missing_sqlite):
        print(f"  - {interface}Repository")
    print()
else:
    print("✅ All interfaces have SQLite implementations")
    print()

if not missing_inmem and not missing_sqlite:
    print("=" * 80)
    print("✅ ALL REPOSITORY IMPLEMENTATIONS COMPLETE!")
    print("=" * 80)
    print()
    print(f"Status:")
    print(f"  - Repository interfaces: {len(interfaces)}")
    print(f"  - In-Memory implementations: {len(in_mem_implementations)}")
    print(f"  - SQLite implementations: {len(sqlite_implementations)}")
    print(f"  - Total implementations: {len(in_mem_implementations) + len(sqlite_implementations)}")
