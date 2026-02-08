#!/usr/bin/env python3
"""
MOVE UNNECESSARY .md FILES TO docs/
"""

import shutil
from pathlib import Path

print("=" * 80)
print("MOVE UNNECESSARY .md FILES TO docs/")
print("=" * 80)
print()
print("This will:")
print("  1. Keep only main README files in root")
print("  2. Move documentation files to docs/")
print("  3. Clean up root directory")
print()

project_root = Path("/root/clawd")
docs_dir = project_root / "docs"

print(f"Project root: {project_root}")
print(f"Docs dir: {docs_dir}")
print()

# Define which .md files to KEEP in root (main documentation)
files_to_keep = {
    project_root: [
        'README.md',  # Main README
        'AGENTS.md',  # Agents documentation
        'BOOTSTRAP.md',  # Bootstrap guide
        'CHANGELOG.md',  # Changelog
    ],
}

# Define which .md files to MOVE to docs/
# These are implementation details, quick references, etc.
files_to_move = {
    project_root: [
        'CLI_IMPLEMENTATION.md',
        'CLI_QUICK_REF.md',
        'CLI_COMPLETION_REPORT.md',
        'REPOSITORY_GENERATION.md',
        'SOUL.md',
        'IDENTITY.md',
        'HEARTBEAT.md',
        'TOOLS.md',
        # Add any other .md files here that should be in docs/
    ],
}

# Create docs directory if not exists
if not docs_dir.exists():
    docs_dir.mkdir()
    print(f"✅ Created: {docs_dir}")

print()
print("Moving unnecessary .md files to docs/...")
print()

# Move files to docs/
moved_count = 0
for filepath in project_root.glob("*.md"):
    if filepath.name in files_to_move[project_root]:
        # Move to docs/
        target_path = docs_dir / filepath.name
        shutil.move(str(filepath), str(target_path))
        print(f"  ✅ Moved: {filepath.name}")
        moved_count += 1
    elif filepath.name in files_to_keep[project_root]:
        print(f"  ✅ Keeping: {filepath.name} (main documentation)")

print()
print(f"✅ Moved {moved_count} .md files to docs/")
print()

# Check remaining .md files in root
print("Remaining .md files in root:")
for filepath in project_root.glob("*.md"):
    print(f"  ✅ {filepath.name}")

print()
print("=" * 80)
print("✅ MOVE COMPLETE")
print("=" * 80)
print()
print("Directory structure:")
print("  root/")
print("    ├── README.md")
print("    ├── AGENTS.md")
print("    ├── BOOTSTRAP.md")
print("    ├── CHANGELOG.md")
print("    ├── scripts/")
print("    ├── src/")
print("    ├── lore_mcp_server/")
print("    └── docs/")
print("        ├── CLI_IMPLEMENTATION.md")
print("        ├── CLI_QUICK_REF.md")
print("        ├── CLI_COMPLETION_REPORT.md")
print("        ├── REPOSITORY_GENERATION.md")
print("        ├── SOUL.md")
print("        ├── IDENTITY.md")
print("        ├── HEARTBEAT.md")
print("        └── TOOLS.md")
print()
print("=" * 80)
print("✅ READY FOR COMMIT")
print("=" * 80)
print()
print("Next steps:")
print("  1. Review moved files")
print("  2. Verify root directory is clean")
print("  3. Verify main README files are in root")
print("  4. Commit: git add -A && git commit -m 'chore: Move unnecessary .md files to docs/'")
print("  5. Push: git push origin master")
print("=" * 80)
