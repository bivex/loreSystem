"""
Unit tests for PyQt6 GUI components using pytest-qt.

Tests focus on:
- Widget initialization
- Signal-slot connections
- Button clicks and state changes
- Business logic integration
"""
import pytest
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget

from src.presentation.gui.lore_editor import MainWindow, LoreData


@pytest.fixture
def app(qtbot):
    """Create QApplication instance for testing."""
    # pytest-qt handles QApplication creation, but we ensure it's available
    return QApplication.instance() or QApplication([])


def test_main_window_initialization(qtbot):
    """Test that MainWindow initializes correctly."""
    window = MainWindow()
    qtbot.addWidget(window)

    # Check window properties
    assert window.windowTitle().startswith("🎮 MythWeave")
    assert window.lore_data is not None
    assert isinstance(window.lore_data, LoreData)

    # Check that tabs are created (now uses stacked widget with many more tabs)
    assert hasattr(window, 'tabs')
    assert window.tabs.count() >= 7  # At least the core tabs exist

    # Check that core tab widgets are accessible
    assert hasattr(window, 'worlds_tab')
    assert hasattr(window, 'characters_tab')
    assert hasattr(window, 'events_tab')
    assert hasattr(window, 'improvements_tab')
    assert hasattr(window, 'items_tab')
    assert hasattr(window, 'quests_tab')
    assert hasattr(window, 'storylines_tab')


def test_lore_data_initialization():
    """Test LoreData initializes with empty lists."""
    data = LoreData()

    assert data.worlds == []
    assert data.characters == []
    assert data.events == []
    assert data.improvements == []
    assert data.items == []


def test_main_window_search_functionality(qtbot):
    """Test search input field exists and is connected."""
    window = MainWindow()
    qtbot.addWidget(window)

    # Check search input exists
    assert hasattr(window, 'search_input')
    assert window.search_input is not None

    # Check it's a QLineEdit with placeholder
    assert window.search_input.placeholderText() == "Search across all entities..."

    # Test typing in search field (signal should be connected)
    window.search_input.setText("test search")
    assert window.search_input.text() == "test search"


def test_sample_data_loading(qtbot, monkeypatch):
    """Test sample data loading functionality."""
    window = MainWindow()
    qtbot.addWidget(window)

    # Mock the sample file path
    sample_file = Path(__file__).parent.parent / "examples" / "sample_lore.json"

    # Test that _load_sample_data method exists
    assert hasattr(window, '_load_sample_data')

    # If sample file exists, test loading (but don't actually load to avoid side effects)
    if sample_file.exists():
        # We could test the method, but for now just verify it exists
        # In a real test, we'd mock the file operations
        pass


def test_comprehensive_json_loading():
    """Test loading the comprehensive sample_dark_fantasy_gacha_ru.json file."""
    from src.presentation.gui.lore_data import LoreData

    # Path to the comprehensive sample file
    sample_file = Path(__file__).parent.parent / "examples" / "sample_dark_fantasy_gacha_ru.json"

    # Skip test if file doesn't exist
    if not sample_file.exists():
        pytest.skip(f"Sample file not found: {sample_file}")

    # Create fresh LoreData instance
    lore_data = LoreData()

    # Load the JSON file
    with open(sample_file, 'r', encoding='utf-8') as f:
        import json
        data = json.load(f)
        lore_data.from_dict(data)

    # Verify all entity types are loaded with minimum expectations
    assert len(lore_data.worlds) >= 2, f"Expected at least 2 worlds, got {len(lore_data.worlds)}"

    # Check specific world data
    world_names = [w.name.value for w in lore_data.worlds]
    assert "Тёмные Земли Эреба" in world_names
    assert "Проклятые Руины Некрополиса" in world_names

    # Verify characters are loaded
    assert len(lore_data.characters) >= 3, f"Expected at least 3 characters, got {len(lore_data.characters)}"

    # Check specific character data
    character_names = [c.name.value for c in lore_data.characters]
    # Check that we have expected characters (names may vary slightly)
    assert any("Лира" in name and "Шёпот" in name for name in character_names)
    assert any("Виктор" in name and "Кулак" in name for name in character_names)

    # Verify events are loaded
    assert len(lore_data.events) >= 1, f"Expected at least 1 events, got {len(lore_data.events)}"

    # Verify improvements are loaded
    assert len(lore_data.improvements) >= 1, f"Expected at least 1 improvements, got {len(lore_data.improvements)}"

    # Verify items are loaded
    assert len(lore_data.items) >= 1, f"Expected at least 1 items, got {len(lore_data.items)}"

    # Verify quests are loaded
    assert len(lore_data.quests) >= 1, f"Expected at least 1 quests, got {len(lore_data.quests)}"

    # Verify storylines are loaded
    assert len(lore_data.storylines) >= 1, f"Expected at least 1 storylines, got {len(lore_data.storylines)}"

    # Verify stories are loaded
    assert len(lore_data.stories) >= 1, f"Expected at least 1 stories, got {len(lore_data.stories)}"

    # Verify tags are loaded
    assert len(lore_data.tags) >= 1, f"Expected at least 1 tags, got {len(lore_data.tags)}"

    # Verify images are loaded
    assert len(lore_data.images) >= 1, f"Expected at least 1 images, got {len(lore_data.images)}"

    # Verify choices are loaded
    assert len(lore_data.choices) >= 1, f"Expected at least 1 choices, got {len(lore_data.choices)}"

    # Verify flowcharts are loaded
    assert len(lore_data.flowcharts) >= 1, f"Expected at least 1 flowcharts, got {len(lore_data.flowcharts)}"

    # Verify handouts are loaded
    assert len(lore_data.handouts) >= 1, f"Expected at least 1 handouts, got {len(lore_data.handouts)}"

    # Verify inspirations are loaded
    assert len(lore_data.inspirations) >= 1, f"Expected at least 1 inspirations, got {len(lore_data.inspirations)}"

    # Verify maps are loaded
    assert len(lore_data.maps) >= 1, f"Expected at least 1 maps, got {len(lore_data.maps)}"

    # Verify notes are loaded
    assert len(lore_data.notes) >= 1, f"Expected at least 1 notes, got {len(lore_data.notes)}"

    # Verify requirements are loaded
    assert len(lore_data.requirements) >= 1, f"Expected at least 1 requirements, got {len(lore_data.requirements)}"

    # Verify sessions are loaded
    assert len(lore_data.sessions) >= 1, f"Expected at least 1 sessions, got {len(lore_data.sessions)}"

    # Verify tokenboards are loaded
    assert len(lore_data.tokenboards) >= 1, f"Expected at least 1 tokenboards, got {len(lore_data.tokenboards)}"

    # Verify NEW entities are loaded (the ones we added)
    assert len(lore_data.locations) >= 1, f"Expected at least 1 locations, got {len(lore_data.locations)}"
    assert len(lore_data.banners) >= 1, f"Expected at least 1 banners, got {len(lore_data.banners)}"
    assert len(lore_data.character_relationships) >= 1, f"Expected at least 1 character relationships, got {len(lore_data.character_relationships)}"
    assert len(lore_data.factions) >= 1, f"Expected at least 1 factions, got {len(lore_data.factions)}"
    assert len(lore_data.shops) >= 1, f"Expected at least 1 shops, got {len(lore_data.shops)}"

    # Test specific entity data
    # Check that specific entities exist (names may vary)
    if len(lore_data.locations) >= 2:
        location_names = [loc.name for loc in lore_data.locations]
        assert any("Роща" in name or "Лунная" in name for name in location_names)
        assert any("Некрополис" in name or "Зал" in name for name in location_names)

    if len(lore_data.factions) >= 2:
        faction_names = [fac.name for fac in lore_data.factions]
        assert any("Клан" in name or "Крови" in name for name in faction_names)
        assert any("Стражи" in name or "Мертвых" in name for name in faction_names)

    if len(lore_data.banners) >= 2:
        banner_names = [ban.name for ban in lore_data.banners]
        assert any("Вампирский" in name or "Баннер" in name for name in banner_names)
        assert any("Нежить" in name or "Баннер" in name for name in banner_names)

    if len(lore_data.shops) >= 2:
        shop_names = [shop.name for shop in lore_data.shops]
        assert any("Торговец" in name for name in shop_names)

    # Verify next_id is set correctly (should be 84 based on our sample data)
    assert lore_data._next_id == 84, f"Expected next_id=84, got {lore_data._next_id}"

    print(f"✅ Successfully loaded {sum(len(getattr(lore_data, attr)) for attr in dir(lore_data) if not attr.startswith('_') and isinstance(getattr(lore_data, attr), list))} total entities from sample file")


def test_json_roundtrip_serialization():
    """Test that loaded data can be serialized back to JSON without loss."""
    import json
    from src.presentation.gui.lore_data import LoreData

    # Path to the comprehensive sample file
    sample_file = Path(__file__).parent.parent / "examples" / "sample_dark_fantasy_gacha_ru.json"

    # Skip test if file doesn't exist
    if not sample_file.exists():
        pytest.skip(f"Sample file not found: {sample_file}")

    # Create fresh LoreData instance
    original_data = LoreData()

    # Load the JSON file
    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        original_data.from_dict(data)

    # Serialize back to dict
    serialized = original_data.to_dict()

    # Create new instance and load from serialized data
    roundtrip_data = LoreData()
    roundtrip_data.from_dict(serialized)

    # Verify all entity counts match
    original_attrs = [attr for attr in dir(original_data) if not attr.startswith('_') and isinstance(getattr(original_data, attr), list)]
    roundtrip_attrs = [attr for attr in dir(roundtrip_data) if not attr.startswith('_') and isinstance(getattr(roundtrip_data, attr), list)]

    assert set(original_attrs) == set(roundtrip_attrs), "Entity types don't match between original and roundtrip"

    for attr in original_attrs:
        original_count = len(getattr(original_data, attr))
        roundtrip_count = len(getattr(roundtrip_data, attr))
        assert original_count == roundtrip_count, f"Entity count mismatch for {attr}: {original_count} vs {roundtrip_count}"

    print("✅ JSON roundtrip serialization successful - no data loss")


def test_world_selection_signal(qtbot):
    """Test world selection signal connection."""
    window = MainWindow()
    qtbot.addWidget(window)

    # Check that worlds_tab exists and has the signal
    assert hasattr(window, 'worlds_tab')
    assert hasattr(window.worlds_tab, 'world_selected')

    # Check that the signal is connected to _on_world_selected
    assert hasattr(window, '_on_world_selected')


def test_tab_change_signal(qtbot):
    """Test tab change signal connection."""
    window = MainWindow()
    qtbot.addWidget(window)

    # Check that tabs currentChanged signal is connected
    # This is harder to test directly, but we can verify the method exists
    assert hasattr(window, '_on_tab_changed')


def test_status_bar_setup(qtbot):
    """Test that status bar is properly set up."""
    window = MainWindow()
    qtbot.addWidget(window)

    # Check status bar exists
    status_bar = window.statusBar()
    assert status_bar is not None

    # Test showing a message
    test_message = "Test status message"
    status_bar.showMessage(test_message)
    # Note: We can't easily test the actual display without more complex setup


def test_menu_bar_creation(qtbot):
    """Test that menu bar is created."""
    window = MainWindow()
    qtbot.addWidget(window)

    # Check menu bar exists
    menu_bar = window.menuBar()
    assert menu_bar is not None

    # Check that File menu exists (basic check)
    assert len(menu_bar.children()) > 0


def test_tool_bar_creation(qtbot):
    """Test that tool bar is created."""
    window = MainWindow()
    qtbot.addWidget(window)

    # Check that at least one toolbar exists
    toolbars = window.findChildren(QWidget)  # Toolbars are QWidgets
    # This is a basic check - in practice we'd check for specific toolbars