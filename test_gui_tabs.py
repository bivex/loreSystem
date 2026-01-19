#!/usr/bin/env python3
"""
Simple test to check if GUI tabs are created correctly.
"""
import sys
import os
sys.path.insert(0, '.')

# Set minimal environment to avoid GUI display issues
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def test_tab_creation():
    try:
        from PyQt6.QtWidgets import QApplication
        from src.presentation.gui.lore_editor import MainWindow

        app = QApplication([])

        # Create window
        window = MainWindow()

        # Check tabs
        tab_count = window.tab_list.count()
        selectable_tabs = []

        for i in range(tab_count):
            item = window.tab_list.item(i)
            if item and (item.flags() & window.tab_list.Qt.ItemFlag.ItemIsSelectable):
                selectable_tabs.append(item.text())

        print(f'✅ GUI initialized successfully!')
        print(f'📊 Total tab list items: {tab_count}')
        print(f'📋 Selectable tabs: {len(selectable_tabs)}')

        # Check for new tabs
        new_tab_keywords = ['Pity', 'Gacha', 'Player', 'Currency', 'Reward', 'Purchase', 'Event Chain', 'Faction Membership']
        found_new_tabs = []

        for tab_name in selectable_tabs:
            for keyword in new_tab_keywords:
                if keyword in tab_name:
                    found_new_tabs.append(tab_name)
                    break

        print(f'🎯 New entity tabs found: {len(found_new_tabs)}')
        for tab in found_new_tabs:
            print(f'  ✓ {tab}')

        # Check data loading
        print(f'\n💾 Sample data loaded:')
        print(f'  Pity systems: {len(window.lore_data.pity)}')
        print(f'  Gacha pulls: {len(window.lore_data.pulls)}')
        print(f'  Player profiles: {len(window.lore_data.player_profiles)}')

        app.quit()
        return True

    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_tab_creation()
    sys.exit(0 if success else 1)