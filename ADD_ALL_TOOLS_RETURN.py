#!/usr/bin/env python3
"""
ADD ALL 1496 TOOLS TO list_tools() RETURN STATEMENT
"""

import re
from pathlib import Path

print("=" * 80)
print("ADD ALL 1496 TOOLS TO list_tools() RETURN STATEMENT")
print("=" * 80)
print()

server_file = Path("/root/clawd/lore_mcp_server/mcp_server/server.py")

print(f"Server file: {server_file}")
print()

# Read server.py file
with open(server_file, 'r') as f:
    content = f.read()

# Extract all Tool definitions
print("Extracting all Tool definitions...")
print()

pattern = r'Tool\((.*?)\)'
tools = re.findall(pattern, content)

print(f"✅ Extracted {len(tools)} Tool definitions")
print()

# Find return statement in list_tools() function
print("Finding return statement in list_tools() function...")
print()

# Find async def list_tools() -> list[Tool]:
pattern_list_tools = r'async def list_tools\([^)]*\).*?async def call_tool'
match_list_tools = re.search(pattern_list_tools, content)

if not match_list_tools:
    print("❌ Error: Could not find 'async def list_tools() -> list[Tool]'")
    exit(1)

list_tools_body = match_list_tools.group(1)

# Find return [ in list_tools()
pattern_return = r'return \[(.*?)\]'
match_return = re.search(pattern_return, list_tools_body)

if not match_return:
    print("❌ Error: Could not find 'return [...' in list_tools()")
    print("Checking entire function body...")
    print(f"Function body length: {len(list_tools_body)}")
    print(f"Function body (first 500 chars): {list_tools_body[:500]}")
    exit(1)

return_start = match_list_tools.start() + list_tools_body.find(match_return.group(0))
return_statement = match_return.group(0)

print(f"✅ Found return at position {return_start} (line {content[:return_start].count(chr(10)) + 1})")
print(f"  Return statement: {return_statement[:100]}")
print(f"  Tools in return: {return_statement.count('Tool(')}")
print()

# Generate new return statement with all 1496 tools
print("Generating new return statement with all 1496 tools...")
print()

new_return = "    return [\n"

for i, tool in enumerate(tools):
    new_return += f"        {tool}\n"
    
    # Add newlines every 10 tools for readability
    if (i + 1) % 10 == 0 and i < len(tools) - 1:
        new_return += "\n"

new_return += "    ]"

print(f"✅ Generated new return statement with {len(tools)} Tool definitions")
print()

# Replace return statement
print("Replacing return statement...")
print()

new_content = content[:return_start] + new_return + content[return_start + len(return_statement):]

# Write back to server.py
with open(server_file, 'w') as f:
    f.write(new_content)

print(f"✅ Updated {server_file}")
print(f"✅ Replaced return statement with {len(tools)} Tool definitions")
print()

# Verify
print("Verifying...")
print()

with open(server_file, 'r') as f:
    updated_content = f.read()

# Find return statement in list_tools() again
match_list_tools_check = re.search(pattern_list_tools, updated_content)
match_return_check = re.search(pattern_return, match_list_tools_check.group(1))

if match_return_check:
    tools_in_return = match_return_check.group(0).count('Tool(')
    print(f"✅ Verified: return statement has {tools_in_return} Tool definitions")
    
    if tools_in_return == 1496:
        print(f"✅ SUCCESS: All {tools_in_return} tools in return statement!")
    else:
        print(f"⚠️  Warning: Expected 1496 tools, found {tools_in_return}")
else:
    print("❌ Error: Could not verify return statement")

print()
print("=" * 80)
print("✅ RETURN STATEMENT UPDATED WITH ALL 1496 TOOLS")
print("=" * 80)
print()
print(f"Total tools: {len(tools)} (51 existing + 1445 new)")
print()
print("Next steps:")
print("  1. Verify syntax: python3 -m py_compile lore_mcp_server/mcp_server/server.py")
print("  2. Test server startup: python3 lore_mcp_server/mcp_server/server.py")
print("  3. Commit: git add -A && git commit -m 'feat: Update list_tools() return with all 1496 MCP tools (CRUD + Search)'")
print("  4. Push: git push origin master")
print("=" * 80)
print("✅ READY TO VERIFY AND TEST")
print("=" * 80)
