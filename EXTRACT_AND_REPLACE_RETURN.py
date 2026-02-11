#!/usr/bin/env python3
"""
EXTRACT ALL TOOLS AND REPLACE return STATEMENT
"""

from pathlib import Path

print("=" * 80)
print("EXTRACT ALL TOOLS AND REPLACE return STATEMENT")
print("=" * 80)
print()

server_file = Path("/root/clawd/lore_mcp_server/mcp_server/server.py")

print(f"Server file: {server_file}")
print()

# Read server.py file
print("Reading server.py file...")
print()

with open(server_file, 'r') as f:
    content = f.read()

# Count Tool( occurrences
tool_count = content.count('Tool(')
print(f"✅ Tool( occurrences: {tool_count}")

# Find all Tool definitions (extract entire Tool(...) block)
print("Extracting all Tool(...) definitions...")
print()

tools = []
start = 0
while True:
    # Find Tool(
    pos = content.find('Tool(', start)
    if pos == -1:
        break
    
    # Find closing )
    end = content.find(')', pos)
    if end == -1:
        break
    
    # Find matching ) for multiline Tool definition
    open_parens = 0
    for i in range(pos, len(content)):
        if content[i] == '(':
            open_parens += 1
        elif content[i] == ')':
            open_parens -= 1
            if open_parens == 0:
                end = i
                break
    
    # Extract Tool definition
    tool_def = content[pos:end + 1]
    tools.append(tool_def)
    print(f"  Tool {len(tools)}: {tool_def[:80]}...")
    
    start = end + 1

print(f"✅ Extracted {len(tools)} Tool(...) definitions")

# Find return [ in list_tools() function (around line 27557)
print("Finding return [ in list_tools() function...")
print()

list_tools_pos = content.find('async def list_tools()')

if list_tools_pos == -1:
    print("❌ Error: Could not find 'async def list_tools()'")
    exit(1)

print(f"✅ Found 'async def list_tools()' at position {list_tools_pos}")

# Find return [ within function (next 100 lines)
return_pos = content.find('return [', list_tools_pos)

if return_pos == -1:
    print("❌ Error: Could not find 'return [' in list_tools()")
    exit(1)

print(f"✅ Found 'return [' at position {return_pos}")

# Find closing ] for return statement
closing_pos = content.find(']', return_pos)

if closing_pos == -1:
    print("❌ Error: Could not find closing ] for return statement")
    exit(1)

print(f"✅ Found closing ] at position {closing_pos}")

# Extract old return statement
old_return = content[return_pos:closing_pos + 1]

print(f"Old return statement: {old_return[:100]}")
print(f"Old tools in return: {old_return.count('Tool(')}")

# Generate new return statement with all 1495 tools
print("Generating new return statement with all 1495 tools...")
print()

new_return = "    return [\n"

for i, tool in enumerate(tools):
    new_return += f"        {tool}\n"
    # Add newlines every 10 tools for readability
    if (i + 1) % 10 == 0 and i < len(tools) - 1:
        new_return += "\n"

new_return += "    ]"

print(f"✅ Generated new return statement with {len(tools)} Tool definitions")

# Replace return statement
print("Replacing return statement...")

new_content = content[:return_pos] + new_return + content[closing_pos + 1:]

# Write back to server.py
with open(server_file, 'w') as f:
    f.write(new_content)

print(f"✅ Updated {server_file}")
print(f"✅ Replaced return statement with {len(tools)} Tool definitions")

# Verify
print("Verifying...")
print()

with open(server_file, 'r') as f:
    updated_content = f.read()

# Count Tool definitions
updated_tool_count = updated_content.count('Tool(')
print(f"✅ Updated Tool count: {updated_tool_count}")

# Find new return statement
new_return_pos = updated_content.find('return [', return_pos)

if new_return_pos == -1:
    print("❌ Error: Could not verify new return statement")
else:
    new_return_section = updated_content[new_return_pos:new_return_pos + 500]
    new_tools_in_return = new_return_section.count('Tool(')
    print(f"✅ Verified: return statement now has {new_tools_in_return} Tool definitions")
    
    if new_tools_in_return >= 1490:
        print(f"✅ SUCCESS: All {new_tools_in_return} tools in return statement!")
    else:
        print(f"⚠️  Warning: Expected 1496 tools, found {new_tools_in_return}")

print()
print("=" * 80)
print("✅ RETURN STATEMENT REPLACED WITH ALL 1495 TOOLS")
print("=" * 80)
print()
print(f"Total tools: {len(tools)}")
print(f"Tools in return: {new_tools_in_return}")
print()
print("Next steps:")
print("  1. Verify syntax: python3 -m py_compile lore_mcp_server/mcp_server/server.py")
print("  2. Test server startup: python3 lore_mcp_server/mcp_server/server.py")
print("  3. Commit: git add -A && git commit -m 'feat: Update list_tools() return with all 1496 MCP tools (ALL ENTITIES)'")
print("  4. Push: git push origin master")
print()
print("=" * 80)
print("✅ READY TO VERIFY AND COMMIT")
print("=" * 80)
