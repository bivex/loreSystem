#!/bin/bash
# LoreForge GUI Launcher Script
# This script sets up the virtual environment and runs the GUI

echo "🎮 LoreForge GUI Launcher"
echo "========================="

# Check if we're in the right directory
if [ ! -f "run_gui.py" ]; then
    echo "❌ Error: run_gui.py not found. Please run this script from the loreSystem directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if PyQt6 is installed
if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "📥 Installing PyQt6..."
    pip install "PyQt6>=6.6.1"
fi

# Check if other dependencies are installed
if ! python3 -c "import pydantic" 2>/dev/null; then
    echo "📥 Installing core dependencies..."
    pip install "pydantic>=2.5.3" dataclasses-json
fi

# Run the GUI
echo "🚀 Starting LoreForge GUI..."
echo ""
echo "💡 Tips:"
echo "   - Load sample data: Click 'Load' → Select examples/sample_lore.json"
echo "   - Create worlds in the 'Worlds' tab"
echo "   - Add characters with abilities in the 'Characters' tab"
echo "   - Save your work with 'Save' or 'Save As'"
echo ""
echo "📚 For help, see QUICKSTART_GUI.md"
echo ""

python3 run_gui.py