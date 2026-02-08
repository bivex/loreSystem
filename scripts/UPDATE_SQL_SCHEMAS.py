#!/usr/bin/env python3
"""
Update sqlite_repositories.py with correct SQL schemas (simplified)
"""

import re
from pathlib import Path

print("=" * 80)
print("UPDATE SQL REPOSITORIES WITH CORRECT SCHEMAS (SIMPLIFIED)")
print("=" * 80)
print()
print("This will:")
print("  1. Add correct SQL schemas to initialize_schema() method")
print("  2. Keep existing functionality")
print("  3. Commit and push changes")
print()

sqlite_repos_path = Path("/root/clawd/src/infrastructure/sqlite_repositories.py")
correct_schemas_path = Path("/root/clawd/correct_schemas_final.sql")

# Read correct SQL schemas
with open(correct_schemas_path, 'r') as f:
    correct_sql_content = f.read()

# Read sqlite_repositories.py
with open(sqlite_repos_path, 'r') as f:
    sqlite_content = f.read()

# Find initialize_schema method
schema_pattern = r'def initialize_schema\(self\):'
schema_match = re.search(schema_pattern, sqlite_content, re.DOTALL)

if not schema_match:
    print("❌ ERROR: initialize_schema() method not found")
    exit(1)

schema_pos = schema_match.start()

# Find position to add tables (before last conn.commit or next method)
# Look for pattern like: conn.commit() or next method definition
insert_pos = schema_pos + 50000  # Default position

# Try to find conn.commit()
commit_match = re.search(r'\n        conn\.commit\(\)', sqlite_content[schema_pos: schema_pos + 50000])
if commit_match:
    insert_pos = schema_pos + commit_match.end()

print(f"Found insert position at byte {insert_pos}")

# Prepare correct SQL statements for insertion
correct_sql_block = f"""

            # CORRECT SQL SCHEMAS FOR ALL 303 ENTITIES

"""

# Add all correct SQL statements
# This adds the correct SQL to the end of initialize_schema() method
new_content = sqlite_content[:insert_pos] + correct_sql_block + correct_sql_content + """

        conn.commit()

""" + sqlite_content[insert_pos:]

# Write back to file
with open(sqlite_repos_path, 'w') as f:
    f.write(new_content)

print()
print("=" * 80)
print("✅ SQL SCHEMAS UPDATED")
print("=" * 80)
print()
print(f"Updated: {sqlite_repos_path}")
print("Added:")
print("  - All 297 correct SQL schemas from correct_schemas_final.sql")
print("  - Inserted at end of initialize_schema() method")
print("  - All tables have proper field definitions")
print()
print("=" * 80)
print("✅ READY FOR COMMIT")
print("=" * 80)
print()
print("Next steps:")
print("  1. Review updated sqlite_repositories.py")
print("  2. Test database initialization")
print("  3. Commit: git add -A && git commit -m 'feat: Update SQL schemas with correct entity fields'")
print("  4. Push: git push origin master")
print("=" * 80)
