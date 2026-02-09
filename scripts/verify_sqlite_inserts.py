#!/usr/bin/env python3
"""
Verify that entities were inserted into SQLite database.
Checks that tables exist and have records.
"""

import sqlite3
import json
import sys
from pathlib import Path

def main():
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'lore_system.db'
    entities_dir = sys.argv[2] if len(sys.argv) > 2 else 'entities/'

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print(f"✓ Connected to database: {db_path}")

        # Check if tables exist and have records
        tables_to_check = [
            'story', 'chapter', 'character', 'quest', 'location',
            'item', 'achievement', 'environment', 'world'
        ]

        results = {}
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                results[table] = count
                print(f"  {table}: {count} records")
            except sqlite3.OperationalError:
                print(f"  {table}: Table not found")
                results[table] = 0

        conn.close()

        # Generate summary
        total_records = sum(results.values())
        tables_with_data = sum(1 for count in results.values() if count > 0)

        summary = {
            'total_tables': len(tables_to_check),
            'tables_with_data': tables_with_data,
            'total_records': total_records,
            'table_counts': results
        }

        with open('insert_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        with open('insert_log.json', 'w') as f:
            json.dump({
                'timestamp': 'completed',
                'database': db_path,
                'verification': 'passed' if total_records > 0 else 'no_data'
            }, f, indent=2)

        print(f"\n✓ Database verification complete")
        print(f"  Tables with data: {tables_with_data}/{len(tables_to_check)}")
        print(f"  Total records: {total_records}")

        # Exit with success if we have at least some data
        sys.exit(0 if total_records > 0 else 1)

    except sqlite3.Error as e:
        print(f"ERROR: Database error - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
