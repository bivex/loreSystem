#!/usr/bin/env python3
"""
Simple test of the progression simulator components.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from domain.value_objects.progression import CharacterLevel, StatValue, TimePoint
    print("✅ Value objects imported successfully")
    
    # Test value objects
    level = CharacterLevel(5)
    stat = StatValue(10)
    time = TimePoint(1)
    print(f"✅ Created level: {level}, stat: {stat}, time: {time}")
    
    print("✅ Basic progression system components working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()