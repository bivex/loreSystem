#!/usr/bin/env python3
"""
ORGANIZE REPOSITORY FILES - Put everything in correct folders
"""

import shutil
from pathlib import Path

print("=" * 80)
print("ORGANIZE REPOSITORY FILES - CLEAN STRUCTURE")
print("=" * 80)
print()
print("This will:")
print("  1. Create scripts/ folder (if not exists)")
print("  2. Move all *.py scripts to scripts/")
print("  3. Create scripts/sql/ folder (if not exists)")
print("  4. Move all *.sql files to scripts/sql/")
print("  5. Delete all .db files from root (keep only in examples/)")
print("  6. Clean up root directory")
print()

project_root = Path("/root/clawd")
scripts_dir = project_root / "scripts"
sql_dir = scripts_dir / "sql"
examples_dir = project_root / "lore_mcp_server" / "examples"

print(f"Project root: {project_root}")
print(f"Scripts dir: {scripts_dir}")
print(f"SQL dir: {sql_dir}")
print(f"Examples dir: {examples_dir}")
print()

# Create directories if not exist
print("Creating directories...")
print()

if not scripts_dir.exists():
    scripts_dir.mkdir()
    print(f"  ✅ Created: {scripts_dir}")

if not sql_dir.exists():
    sql_dir.mkdir()
    print(f"  ✅ Created: {sql_dir}")

print()

# Move all .py scripts to scripts/ (skip src/, lore_mcp_server/, lore/)
print("Moving .py scripts to scripts/...")
print()

moved_count = 0
for filepath in project_root.glob("*.py"):
    # Skip if file is in a subdirectory (src/, lore_mcp_server/, lore/, scripts/)
    if filepath.parent != project_root:
        continue
    
    # Skip if file is main.py (keep in root)
    if filepath.name == "main.py":
        continue
    
    # Move to scripts/
    target_path = scripts_dir / filepath.name
    shutil.move(str(filepath), str(target_path))
    print(f"  ✅ Moved: {filepath.name}")
    moved_count += 1

print(f"✅ Moved {moved_count} .py scripts to scripts/")
print()

# Move all .sql files to scripts/sql/
print("Moving .sql files to scripts/sql/...")
print()

sql_moved_count = 0
for filepath in project_root.glob("*.sql"):
    # Skip if file is in a subdirectory
    if filepath.parent != project_root:
        continue
    
    # Move to scripts/sql/
    target_path = sql_dir / filepath.name
    shutil.move(str(filepath), str(target_path))
    print(f"  ✅ Moved: {filepath.name}")
    sql_moved_count += 1

print(f"✅ Moved {sql_moved_count} .sql files to scripts/sql/")
print()

# Delete all .db files from root (keep only in examples/)
print("Deleting .db files from root...")
print()

deleted_count = 0
for filepath in project_root.glob("*.db"):
    if filepath.parent == project_root:
        filepath.unlink()
        print(f"  ❌ Deleted: {filepath.name}")
        deleted_count += 1

print(f"✅ Deleted {deleted_count} .db files from root")
print()

# Check remaining files in root
print("Checking remaining files in root...")
print()

remaining_files = []
for filepath in project_root.glob("*"):
    if filepath.is_file():
        # Skip .git files and subdirectories
        if filepath.name.startswith('.'):
            continue
        if filepath.name in ['README.md', 'AGENTS.md', 'CHANGELOG.md', 'BOOTSTRAP.md', '.gitignore', 'main.py', 'requirements.txt', 'setup.py']:
            continue
        remaining_files.append(filepath.name)

if remaining_files:
    print(f"⚠️  Remaining files in root ({len(remaining_files)}):")
    for filename in remaining_files:
        print(f"    - {filename}")
else:
    print("✅ No remaining files in root (clean!)")

print()
print("=" * 80)
print("✅ ORGANIZATION COMPLETE")
print("=" * 80)
print()
print(f"Moved {moved_count} .py scripts to scripts/")
print(f"Moved {sql_moved_count} .sql files to scripts/sql/")
print(f"Deleted {deleted_count} .db files from root")
print()
print("Directory structure:")
print("  root/")
print("    ├── scripts/")
print("    │   ├── *.py (all Python scripts)")
print("    │   └── sql/")
print("    │       └── *.sql (all SQL files)")
print("    ├── src/")
print("    ├── lore_mcp_server/")
print("    │   └── examples/")
print("    │       └── lore_system.db (only DB file)")
print("    ├── README.md")
print("    ├── AGENTS.md")
print("    ├── CHANGELOG.md")
print("    ├── BOOTSTRAP.md")
print("    ├── .gitignore")
print("    └── main.py")
print()
print("=" * 80)
print("✅ READY FOR COMMIT")
print("=" * 80)
print()
print("Next steps:")
print("  1. Review directory structure")
print("  2. Verify all scripts are in scripts/")
print("  3. Verify all SQL files are in scripts/sql/")
print("  4. Verify only lore_system.db remains (in examples/)")
print("  5. Commit: git add -A && git commit -m 'chore: Organize repository files - move scripts to scripts/ and SQL to scripts/sql/'")
print("  6. Push: git push origin master")
print("=" * 80)
