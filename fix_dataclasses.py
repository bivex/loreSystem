#!/usr/bin/env python3
"""
Fix dataclass field ordering issues.

Move all non-optional fields (without defaults) before optional ones.
"""

import re
from pathlib import Path

entities_dir = Path("/root/clawd/src/domain/entities")

for filepath in entities_dir.glob("*.py"):
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Find @dataclass blocks
        pattern = r'(@dataclass\n(?:.*?\n)*?class \w+:[^:]*\n(?:.*?\n)*?)(?=\n    def |\n@|\Z)'
        matches = list(re.finditer(pattern, content, re.DOTALL))

        modified = False
        new_content = content

        for match in matches:
            block = match.group(1)

            # Check if this has the problematic pattern
            if 'id: Optional[EntityId] = None' not in block:
                continue

            lines = block.split('\n')
            # Skip first 2 lines (@dataclass and class definition)
            field_lines = [l for l in lines[2:] if l.strip() and not l.strip().startswith('#') and ':' in l]

            required_fields = []
            optional_fields = []

            for line in field_lines:
                stripped = line.strip()
                if '=' in stripped and not stripped.startswith('id: Optional[EntityId]'):
                    # Has default value, skip from required
                    if 'id: Optional[EntityId] = None' in stripped:
                        # This is id, add to optional
                        optional_fields.append(line)
                    else:
                        optional_fields.append(line)
                elif '=' not in stripped and ':' in stripped and 'Optional' not in stripped:
                    # No default value, required field
                    required_fields.append(line)
                else:
                    optional_fields.append(line)

            # If id appears before some required fields, we need to reorder
            id_line_idx = -1
            for i, line in enumerate(field_lines):
                if 'id: Optional[EntityId] = None' in line:
                    id_line_idx = i
                    break

            if id_line_idx > 0 and required_fields:
                # There are required fields after id, need to reorder
                # Rebuild the dataclass block
                new_field_lines = required_fields + [l for l in field_lines if 'id: Optional[EntityId] = None' not in l]

                # Now find where to insert id
                # Insert it after all required fields
                id_line = next(l for l in field_lines if 'id: Optional[EntityId] = None' in l)
                new_field_lines.insert(len(required_fields), id_line)

                # Reconstruct block
                new_block = lines[0] + '\n' + lines[1] + '\n' + '\n'.join(new_field_lines) + '\n'

                # Replace in content
                new_content = new_content.replace(block, new_block, 1)
                modified = True

        if modified:
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"Fixed: {filepath.name}")

    except Exception as e:
        print(f"Error processing {filepath.name}: {e}")

print("Done!")
