#!/usr/bin/env python3
"""
Validate parsed chapter output JSON.
Ensures chapter_id exists and entities array is present.
"""

import json
import sys

def main():
    try:
        with open('parsed_data.json', 'r') as f:
            data = json.load(f)

        # Check required fields
        if 'chapter_id' not in data:
            print("ERROR: Missing 'chapter_id' in parsed_data.json")
            sys.exit(1)

        if 'entities' not in data:
            print("ERROR: Missing 'entities' array in parsed_data.json")
            sys.exit(1)

        if not isinstance(data['entities'], list):
            print("ERROR: 'entities' must be an array")
            sys.exit(1)

        print(f"✓ Valid parsed_data.json")
        print(f"  Chapter ID: {data['chapter_id']}")
        print(f"  Entities found: {len(data['entities'])}")

        sys.exit(0)

    except FileNotFoundError:
        print("ERROR: parsed_data.json not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in parsed_data.json: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
