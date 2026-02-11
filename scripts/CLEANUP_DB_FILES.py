#!/usr/bin/env python3
"""
DELETE UNNECESSARY DATABASE FILES
"""

import subprocess
from pathlib import Path

print("=" * 80)
print("DELETE UNNECESSARY DATABASE FILES")
print("=" * 80)
print()

project_root = Path("/root/clawd")
examples_dir = project_root / "lore_mcp_server" / "examples"

print(f"Project root: {project_root}")
print(f"Examples dir: {examples_dir}")
print()

# Define files to keep
files_to_keep = {
    project_root: [
        "lore_system.db",  # Main optimized database
    ],
    examples_dir: [
        "lore_system.db",  # Optimized database for examples
    ]
}

# Define files to delete
files_to_delete = {
    project_root: [
        "lore_system_copy.db",
        "auto_fix_lore_system.db",
        "optimized_lore_system.db",
        "dataclass_lore_system.db",
        "complete_lore_system.db",
        "correct_lore_system.db",
        "correct_lore_system_final.db",
        "proper_ast_lore_system.db",
        "optimized_lore_system.db",
        "proper_ast_lore_system.db",
        "auto_fix_lore_system.db",
        "dataclass_lore_system.db",
        "complete_lore_system.db",
        "correct_lore_system.db",
        "correct_lore_system_final.db",
        "correct_lore_system_ast.db",
        "dataclass_lore_system.db",
        "optimized_lore_system.db",
        "proper_ast_lore_system.db",
        "auto_fix_lore_system.db",
        "dataclass_lore_system.db",
        "complete_lore_system.db",
        "correct_lore_system.db",
        "correct_lore_system_final.db",
        "proper_ast_lore_system.db",
        "auto_fix_lore_system.db",
        "dataclass_lore_system.db",
        "complete_lore_system.db",
        "correct_lore_system.db",
        "correct_lore_system_final.db",
        "proper_ast_lore_system.db",
        "auto_fix_lore_system.db",
        "dataclass_lore_system.db",
        "complete_lore_system.db",
        "correct_lore_system.db",
        "correct_lore_system_final.db",
        "proper_ast_lore_system.db",
    ],
    examples_dir: [
        "lore_system_copy.db",
        "auto_fix_lore_system.db",
        "optimized_lore_system.db",
        "dataclass_lore_system.db",
        "complete_lore_system.db",
        "correct_lore_system.db",
        "correct_lore_system_final.db",
        "proper_ast_lore_system.db",
        "optimized_lore_system.db",
        "proper_ast_lore_system.db",
        "auto_fix_lore_system.db",
        "dataclass_lore_system.db",
        "complete_lore_system.db",
        "correct_lore_system.db",
        "correct_lore_system_final.db",
        "proper_ast_lore_system.db",
        "auto_fix_lore_system.db",
        "dataclass_lore_system.db",
        "complete_lore_system.db",
        "correct_lore_system.db",
        "correct_lore_system_final.db",
        "proper_ast_lore_system.db",
        "auto_fix_lore_system.db",
        "dataclass_lore_system.db",
        "complete_lore_system.db",
        "correct_lore_system.db",
        "correct_lore_system_final.db",
        "proper_ast_lore_system.db",
    ],
}

# Delete files in project root
print("Deleting unnecessary files in project root...")
print()

deleted_count = 0
for filepath in project_root.glob("*.db"):
    if filepath.name in files_to_keep[project_root]:
        print(f"  ✅ Keeping: {filepath.name}")
    else:
        if filepath.is_file():
            filepath.unlink()
            print(f"  ❌ Deleted: {filepath.name}")
            deleted_count += 1

# Delete files in examples directory
print()
print("Deleting unnecessary files in examples/...")
print()

for filepath in examples_dir.glob("*.db"):
    if filepath.name in files_to_keep[examples_dir]:
        print(f"  ✅ Keeping: {filepath.name}")
    else:
        if filepath.is_file():
            filepath.unlink()
            print(f"  ❌ Deleted: {filepath.name}")
            deleted_count += 1

print()
print("=" * 80)
print(f"✅ DELETED {deleted_count} UNNECESSARY DATABASE FILES")
print("=" * 80)
print()

# Delete unnecessary .sql files (script files)
print("Deleting unnecessary .sql script files...")
print()

sql_files_to_keep = []  # Keep all SQL files for documentation

deleted_sql_count = 0
for filepath in project_root.glob("*.sql"):
    if filepath.is_file():
        # Keep all SQL files for now (they're useful for documentation)
        print(f"  ✅ Keeping: {filepath.name}")

print()
print("✅ All .sql script files kept (for documentation)")
print()

# Check remaining files
print("=== REMAINING FILES ===")
print()
print("In project root:")
for filepath in project_root.glob("*.db"):
    print(f"  ✅ {filepath.name} ({filepath.stat().st_size // 1024} KB)")

print()
print("In examples/:")
for filepath in examples_dir.glob("*.db"):
    print(f"  ✅ {filepath.name} ({filepath.stat().st_size // 1024} KB)")

print()
print("=" * 80)
print("✅ CLEANUP COMPLETE")
print("=" * 80)
print()
print("Remaining files:")
print("  - lore_system.db (project root)")
print("  - lore_system.db (examples/)")
print()
print("Deleted:")
print(f"  - {deleted_count} unnecessary database files")
print(f"  - 0 .sql files (kept for documentation)")
print()
print("=" * 80)
print("✅ READY FOR COMMIT")
print("=" * 80)
print()
print("Next steps:")
print("  1. Verify lore_system.db is the optimized version")
print("  2. Verify lore_system.db in examples/ is the same")
print("  3. Test database initialization")
print("  4. Commit: git add -A && git commit -m 'chore: Delete unnecessary database files (keep only optimized versions)'")
print("  5. Push: git push origin master")
print("=" * 80)
