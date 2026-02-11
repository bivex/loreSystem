#!/usr/bin/env bash
# Start Loom with 30 agents for narrative-to-entities plan (macOS version)
# This script handles all the setup and initialization for macOS

set -e

# Set terminal emulator for loom (macOS uses default Terminal.app)
export TERMINAL=Terminal

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "=== Loom 30 Agents Launcher (macOS) ==="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Stop any running daemon
echo "🛑 Stopping any running daemon..."
if loom stop 2>/dev/null; then
    echo "  ✓ Daemon stopped"
else
    echo "  ⚠ No daemon was running"
fi

# Step 1b: Kill ALL loom processes (including orphans from deleted binary)
echo "🧹 Killing any orphaned loom processes..."
if pgrep -x loom >/dev/null 2>&1; then
    pkill -9 -x loom 2>/dev/null || true
    sleep 1
    if pgrep -x loom >/dev/null 2>&1; then
        echo -e "${RED}  ✗ Some processes could not be killed${NC}"
        echo "  Running processes:"
        pgrep -fl loom || true
    else
        echo "  ✓ All orphaned processes killed"
    fi
else
    echo "  ✓ No orphaned processes found"
fi

# Step 1c: Check for launchd services
echo "🔍 Checking for launchd services..."
LAUNCHD_SERVICES=$(launchctl list 2>/dev/null | grep -i loom || true)
if [ -n "$LAUNCHD_SERVICES" ]; then
    echo "  ⚠ Found launchd services:"
    echo "$LAUNCHD_SERVICES"
    # Try to unload any loom-related services
    echo "  Attempting to unload services..."
    for service in $(echo "$LAUNCHD_SERVICES" | awk '{print $1}'); do
        if launchctl unload "$service" 2>/dev/null; then
            echo "    ✓ Unloaded: $service"
        fi
    done
else
    echo "  ✓ No launchd services found"
fi

# Step 1d: Verify loom binary is valid
echo "🔍 Verifying loom binary..."
LOOM_PATH=$(which loom 2>/dev/null)
if [ -z "$LOOM_PATH" ]; then
    echo -e "${RED}  ✗ loom binary not found in PATH${NC}"
    exit 1
fi
if [ ! -f "$LOOM_PATH" ]; then
    echo -e "${RED}  ✗ loom binary path doesn't exist: $LOOM_PATH${NC}"
    echo "  This indicates a deleted binary issue. Reinstall loom."
    exit 1
fi
echo "  ✓ loom binary found: $LOOM_PATH"

# Step 1e: Clean orphaned worktrees
echo "🧹 Cleaning orphaned worktrees..."
if [ -d ".worktrees" ]; then
    WORKTREE_COUNT=$(find .worktrees -maxdepth 1 -type d ! -name ".worktrees" | wc -l | tr -d ' ')
    if [ "$WORKTREE_COUNT" -gt 0 ]; then
        echo "  Found $WORKTREE_COUNT worktree(s), cleaning..."
        find .worktrees -maxdepth 1 -type d ! -name ".worktrees" -exec rm -rf {} + 2>/dev/null || true
        echo "  ✓ Worktrees cleaned"
    else
        echo "  ✓ No orphaned worktrees"
    fi
else
    echo "  ✓ No .worktrees directory"
fi

# Step 2: Restore plan from IN_PROGRESS if needed
echo ""
echo "📋 Checking plan file..."
if [ ! -f "doc/plans/narrative-to-entities.md" ]; then
    if [ -f "doc/plans/IN_PROGRESS-narrative-to-entities.md" ]; then
        echo "  📝 Restoring plan from IN_PROGRESS..."
        cp doc/plans/IN_PROGRESS-narrative-to-entities.md doc/plans/narrative-to-entities.md
        echo "  ✓ Plan restored"
    else
        echo -e "${RED}  ✗ ERROR: No plan file found!${NC}"
        exit 1
    fi
else
    echo "  ✓ Plan file exists"
fi

# Step 3: Clean work directory
echo ""
echo "🧹 Cleaning work directory..."
if [ -d ".work" ]; then
    # Remove work directory completely to avoid any state issues
    rm -rf .work
    echo "  ✓ Work directory cleaned"
else
    echo "  ✓ Work directory already clean"
fi

# Also clean handoffs if they exist
if [ -d ".work/handoffs" ]; then
    rm -rf .work/handoffs
fi

# Step 4: Fix any git issues
echo ""
echo "🔧 Checking git status..."
if git status --short | grep -q "D doc/plans/narrative-to-entities.md"; then
    echo "  📝 Restoring deleted plan file..."
    git checkout HEAD -- doc/plans/narrative-to-entities.md 2>/dev/null || \
    cp doc/plans/IN_PROGRESS-narrative-to-entities.md doc/plans/narrative-to-entities.md
fi

# Commit any uncommitted plan changes
if git diff --quiet doc/plans/narrative-to-entities.md 2>/dev/null; then
    echo "  ✓ Plan is committed"
else
    echo "  📝 Committing plan changes..."
    git add doc/plans/narrative-to-entities.md
    git commit -m "chore: update narrative-to-entities plan" 2>/dev/null || echo "  ⚠ Nothing to commit"
fi

# Step 5: Initialize loom
echo ""
echo "🚀 Initializing Loom..."
if ! loom init doc/plans/narrative-to-entities.md; then
    echo -e "${RED}  ✗ Failed to initialize Loom${NC}"
    exit 1
fi
echo "  ✓ Loom initialized"

# Step 6: Fix config if needed (shouldn't be needed after clean init)
CONFIG_FILE=".work/config.toml"
if [ -f "$CONFIG_FILE" ]; then
    if grep -q "IN_PROGRESS-narrative-to-entities.md" "$CONFIG_FILE"; then
        echo ""
        echo "🔧 Fixing config path..."
        sed -i '' 's|IN_PROGRESS-narrative-to-entities.md|narrative-to-entities.md|' "$CONFIG_FILE"
        echo "  ✓ Config fixed"
    fi
fi

# Step 7: Check chapter file exists
echo ""
echo "📖 Checking chapter input..."
if [ ! -f "chapter_1.txt" ]; then
    echo "  ⚠ chapter_1.txt not found, creating sample..."
    cat > chapter_1.txt << 'EOF'
Chapter 1: The Beginning

Kira stood at the edge of Eldoria, watching the sunset paint the sky in hues of orange and purple. The ancient city stretched before her, its towers reaching toward the heavens like fingers of stone.

"Ready?" asked Marcus, adjusting his sword belt.

Kira nodded. "The Council awaits. We must tell them about the artifact."

Marcus frowned. "You think they'll believe us? About the magic returning?"

"They have to," Kira said. "The fate of the entire kingdom depends on it."

As they walked through the city gates, the guards recognized them and waved through. The Grand Council chamber was in the central spire, a hundred floors up. The elevator ride gave them time to review their story.

The artifact had been found in the ruins of Old Valoria, buried beneath thousands of years of dust. It pulsed with an energy that none of the scholars could identify. And when Kira touched it, she saw visions - visions of a past that had been erased from history.

"We need proof," Marcus said as the elevator doors opened.

Kira pulled the small crystal from her pouch. It glowed faintly, responding to the ambient magic in the chamber.

The Council members were already assembled. High Councilor Aris sat at the head of the table, his expression unreadable. Around him sat representatives from each of the six factions - the Merchants Guild, the Warriors Circle, the Mages Collective, the Rangers Corps, the Artisans Alliance, and the Scholars Academy.

"Report," Aris said simply.

Kira stepped forward. "We found something in the Valoria ruins. Something that changes everything."

She placed the crystal on the table. It glowed brighter, casting dancing shadows across the chamber.

The room fell silent. Then, from the Mages Collective seat, Elder Lyra stood up slowly.

"That's impossible," she whispered. "Those crystals were destroyed during the Purge. Every last one of them."

"Apparently not," Kira said. "And this one speaks. It shows visions of the past - of the time before the Purge, when magic was free and the gods walked among mortals."

The room erupted into chaos. Some called it a hoax. Others called for immediate destruction of the artifact. And a few... a few looked at it with something else in their eyes. Hunger.

High Councilor Aris slammed his hand on the table. Silence fell immediately.

"We will investigate this properly," he said. "The artifact will be secured in the Vault. Kira, Marcus - you will be temporarily detained for questioning."

"Detained?" Marcus stepped forward, hand on his sword. "We bring you proof of magic returning, and you imprison us?"

"Standard procedure," Aris said coolly. "For the safety of the Council."

But Kira noticed something. As the crystal was taken away by guards, one of the Scholars representatives - a young man named Valen - slipped something into his pocket. A small device of some kind. And he was watching her with an expression that said: I believe you. Meet me later.

The game was just beginning.
EOF
    echo "  ✓ Sample chapter created"
else
    echo "  ✓ chapter_1.txt exists"
fi

# Step 8: Final pre-flight check
echo ""
echo "🔍 Final pre-flight check..."
FINAL_ISSUES=0

# Check no loom processes running
if pgrep -x loom >/dev/null 2>&1; then
    echo -e "${RED}  ✗ ERROR: loom processes still running!${NC}"
    pgrep -fl loom || true
    FINAL_ISSUES=1
fi

# Check .work is clean
if [ -d ".work" ] && [ "$(ls -A .work 2>/dev/null)" ]; then
    echo "  ⚠ Warning: .work directory not empty"
    echo "  This may cause issues, but continuing..."
fi

# Check plan file exists
if [ ! -f "doc/plans/narrative-to-entities.md" ]; then
    echo -e "${RED}  ✗ ERROR: Plan file not found!${NC}"
    FINAL_ISSUES=1
fi

if [ $FINAL_ISSUES -eq 1 ]; then
    echo ""
    echo -e "${RED}✗ Pre-flight check failed. Please fix issues above.${NC}"
    exit 1
fi
echo -e "${GREEN}  ✓ All checks passed${NC}"

# Step 9: Run loom
echo ""
echo "🎯 Starting Loom with 30 parallel agents..."
echo ""

loom run --max-parallel 30

echo ""
echo "=== Loom Started ==="
echo ""
echo "Monitor with:"
echo "  loom status"
echo "  loom status --live"
echo ""
echo "Stop with:"
echo "  loom stop"
echo ""
