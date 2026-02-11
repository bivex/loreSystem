#!/usr/bin/env bash
# Fix Loom blockers before running loom run

set -e

echo "=== Fixing Loom Blockers ==="
echo ""

# Check and install jq
if ! command -v jq &> /dev/null; then
    echo "📦 Installing jq..."
    apt-get update -qq
    apt-get install -y jq
    echo "✓ jq installed"
else
    echo "✓ jq already installed"
fi

# Create entities directory if not exists
if [ ! -d "entities" ]; then
    echo "📁 Creating entities/ directory..."
    mkdir -p entities
    echo "✓ entities/ created"
else
    echo "✓ entities/ exists"
fi

# Create chapter file if not exists
CHAPTER_FILE="chapter_1.txt"
if [ ! -f "$CHAPTER_FILE" ]; then
    echo "📝 Creating sample chapter file..."
    cat > "$CHAPTER_FILE" << 'EOF'
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
    echo "✓ Created $CHAPTER_FILE"
else
    echo "✓ $CHAPTER_FILE already exists"
fi

echo ""
echo "=== All Blockers Fixed ==="
echo ""
echo "Ready to run:"
echo "  loom run --max-parallel 30"
echo ""
echo "Or test parse first:"
echo "  python scripts/parse_chapter.py $CHAPTER_FILE"
