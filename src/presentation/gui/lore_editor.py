"""
PyQt6 GUI Application for MythWeave System

Main window with tabs for managing worlds, characters, and events.
Enhanced UI/UX with modern styling, icons, and improved user experience.
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QSpinBox, QComboBox,
    QLabel, QMessageBox, QFileDialog, QGroupBox, QListWidget, QListWidgetItem,
    QDialog, QDialogButtonBox, QInputDialog, QSplitter, QFrame,
    QStatusBar, QMenuBar, QMenu, QToolBar, QProgressBar,
    QSystemTrayIcon, QHeaderView, QStackedWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QIcon, QAction, QPixmap, QKeySequence,
    QPainter, QBrush, QLinearGradient
)
import json
from pathlib import Path as _Path


# --- Simple i18n support -------------------------------------------------
class I18n:
    def __init__(self, locale: str | None = None):
        self.locale = locale or 'en'
        self._dict: dict = {}
        self.load(self.locale)

    def load(self, locale: str):
        self.locale = locale
        base = _Path(__file__).parent / 'i18n'
        path = base / f"{locale}.json"
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                self._dict = json.load(f)
        else:
            # fallback to en
            fallback = base / 'en.json'
            if fallback.exists():
                with open(fallback, 'r', encoding='utf-8') as f:
                    self._dict = json.load(f)
            else:
                self._dict = {}

    def t(self, key: str, default: str | None = None) -> str:
        return self._dict.get(key, default or key)


# singleton
I18N = I18n()

import traceback


def _exception_hook(exc_type, exc_value, exc_tb):
    """Global exception hook for uncaught exceptions in PyQt slots.

    Prints the traceback and shows a QMessageBox instead of letting
    the process abort inside the Qt/C++ runtime.
    """
    # Print full traceback to stderr / logs
    traceback.print_exception(exc_type, exc_value, exc_tb)
    # Try to show an error dialog if the Qt app is running
    try:
        QMessageBox.critical(None, "Unhandled Exception", f"{exc_type.__name__}: {exc_value}")
    except Exception:
        # If QMessageBox isn't available or another error occurs, ignore
        pass


# Install our global hook so uncaught exceptions don't trigger Qt fatal
import sys
sys.excepthook = _exception_hook

from src.application.presentation_contracts import *  # noqa: F401,F403

# Import new tab modules
from src.presentation.gui.tabs import (
    PagesTab, TemplatesTab, StoriesTab, TagsTab, ImagesTab,
    ChoiceTab, FlowchartTab, HandoutTab, InspirationTab, MapTab,
    NoteTab, RequirementTab, SessionTab, TokenboardTab,
    WorldsTab, CharactersTab, EventsTab, ImprovementsTab, ItemsTab,
    QuestsTab, StorylinesTab
)
from src.presentation.gui.tabs.world_map_tab import WorldMapTab
from src.presentation.gui.tabs.banner_tab import BannerTab
from src.presentation.gui.tabs.location_tab import LocationTab
from src.presentation.gui.tabs.environment_tab import EnvironmentTab
from src.presentation.gui.tabs.faction_tab import FactionTab
from src.presentation.gui.tabs.shop_tab import ShopTab
from src.presentation.gui.tabs.character_relationship_tab import CharacterRelationshipTab
from src.presentation.gui.tabs.currency_tab import CurrencyTab
from src.presentation.gui.tabs.event_chain_tab import EventChainTab
from src.presentation.gui.tabs.reward_tab import RewardTab
from src.presentation.gui.tabs.music_theme_tab import MusicThemeTab
from src.presentation.gui.tabs.music_track_tab import MusicTrackTab
from src.presentation.gui.tabs.purchase_tab import PurchaseTab
from src.presentation.gui.tabs.faction_membership_tab import FactionMembershipTab
from src.presentation.gui.tabs.pity_tab import PityTab
from src.presentation.gui.tabs.player_profile_tab import PlayerProfileTab
from src.presentation.gui.tabs.pull_tab import PullTab
from src.presentation.gui.tabs.progression_simulator_tab import ProgressionSimulatorTab
from src.presentation.gui.tabs.lore_axioms_tab import LoreAxiomsTab
from src.presentation.gui.tabs.music_controls_tab import MusicControlsTab
from src.presentation.gui.tabs.music_states_tab import MusicStatesTab
from src.presentation.gui.tabs.progression_events_tab import ProgressionEventsTab
from src.presentation.gui.tabs.progression_states_tab import ProgressionStatesTab
from src.presentation.gui.tabs.texture_tab import TextureTab
from src.presentation.gui.tabs.model3d_tab import Model3DTab


# Import LoreData from separate module
from src.presentation.gui.lore_data import LoreData


# Import AbilityDialog from separate module
from src.presentation.gui.dialogs.ability_dialog import AbilityDialog


class MainWindow(QMainWindow):
    """Main application window with enhanced UI/UX."""

    def __init__(self):
        super().__init__()
        self.lore_data = LoreData()
        self.current_file: Optional[Path] = None
        self.current_locale = 'en'  # Default to English
        self._setup_style()
        self._setup_ui()
        # Alias for backward compatibility with tests
        self.tabs = self.stacked_widget
        self.setWindowTitle(I18N.t('app.title', "🎮 MythWeave - Lore Management System"))
        self.setWindowIcon(QIcon())  # We'll add a proper icon later
        self.resize(1400, 900)
        self._setup_shortcuts()

        # Auto-load sample data (skip in test environments)
        import sys
        is_testing = 'pytest' in sys.modules or 'PYTEST_CURRENT_TEST' in os.environ
        if not is_testing:
            sample_path = Path(__file__).parent.parent.parent / 'examples' / 'sample_dark_fantasy_gacha_ru.json'
            if sample_path.exists():
                self._load_file_by_path(str(sample_path), show_message=False)

    def _setup_style(self):
        """Setup modern dark theme styling."""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2b2b2b, stop:1 #1a1a1a);
            }

            QMenuBar {
                background: #2b2b2b;
                color: #ddd;
                border-bottom: 1px solid #555;
            }

            QMenuBar::item {
                background: transparent;
                color: #ddd;
                padding: 5px 10px;
            }

            QMenuBar::item:selected {
                background: #3a3a3a;
                color: #fff;
            }

            QMenu {
                background: #2b2b2b;
                color: #ddd;
                border: 1px solid #555;
            }

            QMenu::item {
                background: transparent;
                color: #ddd;
                padding: 5px 20px;
            }

            QMenu::item:selected {
                background: #3a3a3a;
                color: #fff;
            }

            QMenu::item:checked {
                background: #4a4a4a;
                color: #fff;
            }

            QTabWidget::pane {
                border: 1px solid #555;
                background: #2b2b2b;
                border-radius: 5px;
            }

            QTabBar::tab {
                background: #3a3a3a;
                color: #ddd;
                padding: 10px 20px;
                margin-right: 2px;
                border: 1px solid #555;
                border-bottom: none;
                border-radius: 5px 5px 0 0;
            }

            QTabBar::tab:selected {
                background: #4a4a4a;
                color: #fff;
                font-weight: bold;
            }

            QTabBar::tab:hover {
                background: #454545;
                color: #fff;
            }

            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a5a5a, stop:1 #4a4a4a);
                color: #fff;
                border: 1px solid #666;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6a6a6a, stop:1 #5a5a5a);
                border: 1px solid #777;
            }

            QPushButton:pressed {
                background: #3a3a3a;
            }

            QPushButton:disabled {
                background: #333;
                color: #666;
                border: 1px solid #444;
            }

            QTableWidget {
                background: #2b2b2b;
                color: #ddd;
                border: 1px solid #555;
                border-radius: 5px;
                gridline-color: #555;
            }

            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #444;
            }

            QTableWidget::item:selected {
                background: #4a4a4a;
                color: #fff;
            }

            QHeaderView::section {
                background: #3a3a3a;
                color: #ddd;
                padding: 8px;
                border: 1px solid #555;
                font-weight: bold;
            }

            QLineEdit, QTextEdit, QComboBox {
                background: #3a3a3a;
                color: #ddd;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 5px;
            }

            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #888;
                background: #404040;
            }

            QGroupBox {
                font-weight: bold;
                color: #ddd;
                border: 2px solid #666;
                border-radius: 5px;
                margin-top: 1ex;
                background: #333;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #fff;
                font-weight: bold;
            }

            QLabel {
                color: #ddd;
            }

            QStatusBar {
                background: #2a2a2a;
                color: #ddd;
                border-top: 1px solid #555;
            }

            QMenuBar {
                background: #2a2a2a;
                color: #ddd;
                border-bottom: 1px solid #555;
            }

            QMenuBar::item:selected {
                background: #3a3a3a;
            }

            QMenu {
                background: #2a2a2a;
                color: #ddd;
                border: 1px solid #555;
            }

            QMenu::item:selected {
                background: #3a3a3a;
            }
        """)

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # File shortcuts
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)

        # Edit shortcuts
        # Add more shortcuts as needed
    
    def _setup_ui(self):
        """Setup the enhanced user interface."""
        self._create_menu_bar()
        # Ensure menu bar is visible (important on some platforms)
        menubar = self.menuBar()
        menubar.setVisible(True)
        menubar.show()
        self._create_tool_bar()

        # Central widget with modern layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        central_widget.setLayout(main_layout)

        # Optimized header with integrated search and status
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.NoFrame)
        header_frame.setMaximumHeight(80)  # Compact height
        header_frame.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #2a2a2a, stop:0.3 #3a3a3a, stop:0.7 #3a3a3a, stop:1 #2a2a2a);
            border: 1px solid #555;
            border-radius: 8px;
        """)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(15, 8, 15, 8)
        header_layout.setSpacing(15)

        # Left section - Title and subtitle
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        title_label = QLabel("🎮 MythWeave")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #fff; font-weight: bold; margin: 0px;")

        subtitle_label = QLabel("Lore Management System")
        subtitle_label.setFont(QFont("Arial", 9))
        subtitle_label.setStyleSheet("color: #aaa; margin: 0px;")

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        # Removed addStretch() to prevent layout parenting issues

        # Center section - Search bar
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("color: #888; font-size: 12px;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(I18N.t('search.placeholder', "Search entities..."))
        self.search_input.setMaximumWidth(300)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #1a1a1a;
                color: #ddd;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 1px solid #777;
                background: #2a2a2a;
            }
        """)
        self.search_input.textChanged.connect(self._on_search_text_changed)

        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        # Removed addStretch() to prevent layout parenting issues

        # Right section - Status and quick actions
        status_layout = QHBoxLayout()
        status_layout.setSpacing(10)

        # World indicator
        self.world_indicator = QLabel("🌍 No World")
        self.world_indicator.setStyleSheet("color: #888; font-size: 10px; padding: 2px 6px; background: #1a1a1a; border-radius: 3px;")
        self.world_indicator.setMinimumWidth(100)

        # Character count
        self.char_count_label = QLabel("👥 0")
        self.char_count_label.setStyleSheet("color: #888; font-size: 10px; padding: 2px 6px; background: #1a1a1a; border-radius: 3px;")

        # Quick save button
        save_btn = QPushButton("💾")
        save_btn.setToolTip("Quick Save")
        save_btn.setMaximumWidth(30)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #2a4a2a;
                color: #fff;
                border: 1px solid #4a6a4a;
                border-radius: 4px;
                padding: 2px;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #3a5a3a;
            }
        """)
        save_btn.clicked.connect(self._quick_save)

        status_layout.addWidget(self.world_indicator)
        status_layout.addWidget(self.char_count_label)
        status_layout.addWidget(save_btn)

        # Add sections to header
        header_layout.addLayout(title_layout)
        header_layout.addLayout(search_layout, 1)  # Stretch factor 1 for center expansion
        header_layout.addLayout(status_layout)

        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)

        # Tabs with enhanced styling - using list and stacked widget for better readability
        tab_layout = QHBoxLayout()
        
        self.tab_list = QListWidget()
        self.tab_list.setMinimumWidth(180)
        self.tab_list.setMaximumWidth(280)
        self.tab_list.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.tab_list.setStyleSheet("""
            QListWidget {
                background: #2b2b2b;
                border: 2px solid #666;
                border-radius: 8px;
                color: #ddd;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #444;
            }
            QListWidget::item:selected {
                background: #444;
                color: #fff;
            }
            QListWidget::item:disabled {
                background: #1a1a1a;
                color: #888;
                font-weight: bold;
                font-size: 11px;
                padding: 5px 10px;
                border-top: 2px solid #555;
                border-bottom: 2px solid #555;
            }
        """)
        
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.stacked_widget.setStyleSheet("""
            QStackedWidget {
                border: 2px solid #666;
                background: #2b2b2b;
                border-radius: 8px;
            }
        """)

        self.worlds_tab = WorldsTab(self.lore_data)
        self.world_map_tab = WorldMapTab(self.lore_data)
        self.characters_tab = CharactersTab(self.lore_data)
        self.events_tab = EventsTab(self.lore_data)
        self.improvements_tab = ImprovementsTab(self.lore_data)
        self.items_tab = ItemsTab(self.lore_data)
        self.quests_tab = QuestsTab(self.lore_data)
        self.storylines_tab = StorylinesTab(self.lore_data)
        self.pages_tab = PagesTab(self.lore_data)
        self.templates_tab = TemplatesTab(self.lore_data)
        self.stories_tab = StoriesTab(self.lore_data)
        self.tags_tab = TagsTab(self.lore_data)
        self.images_tab = ImagesTab(self.lore_data)
        self.choices_tab = ChoiceTab(self.lore_data)
        self.flowcharts_tab = FlowchartTab(self.lore_data)
        self.handouts_tab = HandoutTab(self.lore_data)
        self.inspirations_tab = InspirationTab(self.lore_data)
        self.maps_tab = MapTab(self.lore_data)
        self.notes_tab = NoteTab(self.lore_data)
        self.requirements_tab = RequirementTab(self.lore_data)
        self.sessions_tab = SessionTab(self.lore_data)
        self.tokenboards_tab = TokenboardTab(self.lore_data)
        
        # New tabs from domain entities
        self.banner_tab = BannerTab(self.lore_data)
        self.location_tab = LocationTab(self.lore_data)
        self.environment_tab = EnvironmentTab(self.lore_data)
        self.faction_tab = FactionTab(self.lore_data)
        self.shop_tab = ShopTab(self.lore_data)
        self.character_relationship_tab = CharacterRelationshipTab(self.lore_data)
        self.currency_tab = CurrencyTab(self.lore_data)
        self.event_chain_tab = EventChainTab(self.lore_data)
        self.reward_tab = RewardTab(self.lore_data)
        self.music_theme_tab = MusicThemeTab(self.lore_data)
        self.music_track_tab = MusicTrackTab(self.lore_data)
        self.purchase_tab = PurchaseTab(self.lore_data)
        self.faction_membership_tab = FactionMembershipTab(self.lore_data)
        self.pity_tab = PityTab(self.lore_data)
        self.player_profile_tab = PlayerProfileTab(self.lore_data)
        self.pull_tab = PullTab(self.lore_data)

        # Progression Simulator
        self.progression_simulator_tab = ProgressionSimulatorTab(self.lore_data)

        # New advanced tabs
        self.lore_axioms_tab = LoreAxiomsTab(self.lore_data)
        self.music_controls_tab = MusicControlsTab(self.lore_data)
        self.music_states_tab = MusicStatesTab(self.lore_data)
        self.progression_events_tab = ProgressionEventsTab(self.lore_data)
        self.progression_states_tab = ProgressionStatesTab(self.lore_data)
        self.texture_tab = TextureTab(self.lore_data)
        self.model3d_tab = Model3DTab(self.lore_data)

        # Add to stacked widget and list with categorical dividers
        # Track mapping between list rows and widget indices (excluding dividers)
        self.tab_row_to_widget_index = {}
        widget_index = 0

        def add_divider(text):
            """Add a category divider to the tab list."""
            divider = QListWidgetItem(f"━━ {text.upper()} ━━")
            divider.setFlags(divider.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEnabled)
            self.tab_list.addItem(divider)

        def add_tab(widget, name):
            """Add a tab to both stacked widget and list."""
            nonlocal widget_index
            self.stacked_widget.addWidget(widget)
            self.tab_list.addItem(name)
            try:
                print(f"Added tab: {name}")  # Debug
            except UnicodeEncodeError:
                # Handle encoding issues on Windows consoles
                print(f"Added tab: {name.encode('ascii', 'ignore').decode('ascii')}")  # Debug
            # Map current row to widget index
            self.tab_row_to_widget_index[self.tab_list.count() - 1] = widget_index
            widget_index += 1

        # World Foundation
        add_divider("World Foundation")
        add_tab(self.worlds_tab, I18N.t('tab.worlds', "🌍 Worlds"))
        add_tab(self.world_map_tab, I18N.t('tab.world_map', "🗺️ World Map"))
        add_tab(self.location_tab, I18N.t('tab.locations', "📍 Locations"))
        add_tab(self.environment_tab, I18N.t('tab.environments', "🌤️ Environments"))
        add_tab(self.maps_tab, I18N.t('tab.maps', "🗺️ Maps"))

        # Entities & Relationships
        add_divider("Entities & Relationships")
        add_tab(self.characters_tab, I18N.t('tab.characters', "👥 Characters"))
        add_tab(self.faction_tab, I18N.t('tab.factions', "⚔️ Factions"))
        add_tab(self.character_relationship_tab, I18N.t('tab.relationships', "💑 Relationships"))
        add_tab(self.faction_membership_tab, I18N.t('tab.memberships', "👥 Memberships"))

        # Items & Economy
        add_divider("Items & Economy")
        add_tab(self.items_tab, I18N.t('tab.items', "⚔️ Items"))
        add_tab(self.currency_tab, I18N.t('tab.currencies', "💰 Currencies"))
        add_tab(self.shop_tab, I18N.t('tab.shops', "🏪 Shops"))
        add_tab(self.banner_tab, I18N.t('tab.banners', "🎁 Banners"))
        add_tab(self.pity_tab, I18N.t('tab.pity', "🎯 Pity Systems"))
        add_tab(self.pull_tab, I18N.t('tab.pulls', "🎰 Gacha Pulls"))
        add_tab(self.purchase_tab, I18N.t('tab.purchases', "💳 Purchases"))
        add_tab(self.reward_tab, I18N.t('tab.rewards', "🎁 Rewards"))

        # Content Creation
        add_divider("Content Creation")
        add_tab(self.events_tab, I18N.t('tab.events', "⚡ Events"))
        add_tab(self.event_chain_tab, I18N.t('tab.event_chains', "⛓️ Event Chains"))
        add_tab(self.improvements_tab, I18N.t('tab.improvements', "⬆️ Improvements"))
        add_tab(self.quests_tab, I18N.t('tab.quests', "🎯 Quests"))
        add_tab(self.storylines_tab, I18N.t('tab.storylines', "📖 Storylines"))
        add_tab(self.stories_tab, I18N.t('tab.stories', "📖 Stories"))
        add_tab(self.choices_tab, I18N.t('tab.choices', "🎯 Choices"))
        add_tab(self.flowcharts_tab, I18N.t('tab.flowcharts', "📊 Flowcharts"))

        # Assets & Templates
        add_divider("Assets & Templates")
        add_tab(self.templates_tab, I18N.t('tab.templates', "📐 Templates"))
        add_tab(self.pages_tab, I18N.t('tab.pages', "📄 Pages"))
        add_tab(self.images_tab, I18N.t('tab.images', "🖼️ Images"))
        add_tab(self.texture_tab, I18N.t('tab.textures', "🎨 Textures"))
        add_tab(self.model3d_tab, I18N.t('tab.models', "🎲 3D Models"))
        add_tab(self.handouts_tab, I18N.t('tab.handouts', "📄 Handouts"))

        # Organization & Tools
        add_divider("Organization & Tools")
        add_tab(self.tags_tab, I18N.t('tab.tags', "🏷️ Tags"))
        add_tab(self.notes_tab, I18N.t('tab.notes', "📝 Notes"))
        add_tab(self.requirements_tab, I18N.t('tab.requirements', "📋 Requirements"))
        add_tab(self.lore_axioms_tab, I18N.t('tab.lore_axioms', "📜 Lore Axioms"))
        add_tab(self.sessions_tab, I18N.t('tab.sessions', "🎲 Sessions"))
        add_tab(self.tokenboards_tab, I18N.t('tab.tokenboards', "🎛️ Tokenboards"))
        add_tab(self.progression_simulator_tab, I18N.t('tab.progression_simulator', "📈 Progression Simulator"))
        add_tab(self.progression_events_tab, I18N.t('tab.progression_events', "📈 Progression Events"))
        add_tab(self.progression_states_tab, I18N.t('tab.progression_states', "📊 Progression States"))

        # Player Management
        add_divider("Player Management")
        add_tab(self.player_profile_tab, I18N.t('tab.players', "👤 Player Profiles"))

        # Audio & Media
        add_divider("Audio & Media")
        add_tab(self.music_theme_tab, I18N.t('tab.themes', "🎵 Music Themes"))
        add_tab(self.music_track_tab, I18N.t('tab.tracks', "🎶 Music Tracks"))
        add_tab(self.music_controls_tab, I18N.t('tab.music_controls', "🎵 Music Controls"))
        add_tab(self.music_states_tab, I18N.t('tab.music_states', "🎼 Music States"))
        add_tab(self.inspirations_tab, I18N.t('tab.inspirations', "💡 Inspiration"))

        # Set initial selection (skip first divider, select Worlds tab)
        self.tab_list.setCurrentRow(1)

        tab_layout.addWidget(self.tab_list, 0)  # No stretch for tab list
        tab_layout.addWidget(self.stacked_widget, 1)  # Stretch factor 1 for stacked widget

        main_layout.addLayout(tab_layout)

        # Connect list to stacked widget with mapping for dividers
        def on_tab_row_changed(row):
            """Handle tab list row change, accounting for dividers."""
            if row in self.tab_row_to_widget_index:
                widget_index = self.tab_row_to_widget_index[row]
                self.stacked_widget.setCurrentIndex(widget_index)
                self._on_tab_changed(row)

        self.tab_list.currentRowChanged.connect(on_tab_row_changed)

        # Enhanced status bar
        self._setup_status_bar()

        # Connect signals
        self.worlds_tab.world_selected.connect(self._on_world_selected)
        
        # Initialize header status
        self._update_header_status()
        
        # Check for sample data on startup (skip in test environments)
        import sys
        is_testing = 'pytest' in sys.modules or 'PYTEST_CURRENT_TEST' in os.environ
        if not is_testing:
            QTimer.singleShot(1000, self._check_for_sample_data)  # Delay to ensure UI is fully loaded

    def _set_locale(self, locale: str):
        """Set application locale and update UI texts."""
        I18N.load(locale)
        self.current_locale = locale
        self._retranslate_ui()

    def _retranslate_ui(self):
        """Update all translatable UI texts."""
        # Window title
        self.setWindowTitle(I18N.t('app.title', "🎮 MythWeave - Lore Management System"))

        # Tabs
        try:
            self.tabs.setTabText(0, I18N.t('tab.worlds', "🌍 Worlds"))
            self.tabs.setTabText(1, I18N.t('tab.characters', "👥 Characters"))
            self.tabs.setTabText(2, I18N.t('tab.events', "⚡ Events"))
            self.tabs.setTabText(3, I18N.t('tab.improvements', "⬆️ Improvements"))
            self.tabs.setTabText(4, I18N.t('tab.items', "⚔️ Items"))
            # quests/storylines may not exist in older layouts
            if self.tabs.count() > 5:
                self.tabs.setTabText(5, I18N.t('tab.quests', "🎯 Quests"))
            if self.tabs.count() > 6:
                self.tabs.setTabText(6, I18N.t('tab.storylines', "📖 Storylines"))
        except Exception:
            pass

        # Search placeholder
        try:
            self.search_input.setPlaceholderText(I18N.t('search.placeholder', "Search across all entities..."))
        except Exception:
            pass

        # File menu (actions)
        try:
            # Update file menu title
            if hasattr(self, 'file_menu'):
                self.file_menu.setTitle(I18N.t('menu.file', 'File'))
            self.new_action.setText(I18N.t('menu.file.new', 'New Project'))
            self.open_action.setText(I18N.t('menu.file.open', 'Open...'))
            self.load_sample_action.setText(I18N.t('menu.file.load_sample', 'Load Sample Data'))
            self.save_action.setText(I18N.t('menu.file.save', 'Save'))
            self.save_as_action.setText(I18N.t('menu.file.save_as', 'Save As...'))
        except Exception:
            pass

    def _on_world_selected(self, world_id: EntityId):
        """Handle world selection."""
        world = self.lore_data.get_world_by_id(world_id)
        if world:
            self.statusBar().showMessage(f"Selected world: {world.name}")
        else:
            self.statusBar().showMessage(f"Selected world ID: {world_id.value}")

    def _check_for_sample_data(self):
        """Check if we should suggest loading sample data."""
        if (len(self.lore_data.worlds) == 0 and 
            len(self.lore_data.characters) == 0 and 
            len(self.lore_data.items) == 0):
            
            reply = QMessageBox.question(
                self, I18N.t('sample.welcome.title', "Welcome to MythWeave!"),
                I18N.t('sample.welcome.body', "Would you like to load the sample lore data to explore the features?"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self._load_sample_data()

    def _load_sample_data(self):
        """Load the sample data file."""
        sample_file = Path(__file__).parent.parent.parent / "examples" / "sample_dark_fantasy_gacha_ru.json"
        
        if sample_file.exists():
            try:
                with open(sample_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.lore_data.from_dict(data)
                # Don't set current_file for sample data to prevent overwriting
                self._refresh_all()
                self.setWindowTitle("🎮 MythWeave - Sample Data")
                self.statusBar().showMessage("Sample data loaded successfully!")
                
            except Exception as e:
                QMessageBox.warning(
                    self, "Sample Data Error",
                    f"Could not load sample data:\n\n{str(e)}"
                )
        else:
            QMessageBox.warning(
                self, "Sample Data Not Found",
                f"Sample data file not found at:\n{sample_file}"
            )

    def _create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()

        # File menu
        self.file_menu = menubar.addMenu(I18N.t('menu.file', "File"))

        self.new_action = QAction(I18N.t('menu.file.new', "New Project"), self)
        self.new_action.triggered.connect(self._new_file)
        self.new_action.setStatusTip(I18N.t('menu.file.new', "Create a new lore project"))
        self.file_menu.addAction(self.new_action)

        self.open_action = QAction(I18N.t('menu.file.open', "Open..."), self)
        self.open_action.triggered.connect(self._load_file)
        self.open_action.setStatusTip(I18N.t('menu.file.open', "Open an existing lore file"))
        self.file_menu.addAction(self.open_action)

        self.file_menu.addSeparator()

        self.load_sample_action = QAction(I18N.t('menu.file.load_sample', "Load Sample Data"), self)
        self.load_sample_action.triggered.connect(self._load_sample_data)
        self.load_sample_action.setStatusTip(I18N.t('menu.file.load_sample', "Load sample lore data to explore features"))
        self.file_menu.addAction(self.load_sample_action)

        self.file_menu.addSeparator()

        self.save_action = QAction(I18N.t('menu.file.save', "Save"), self)
        self.save_action.triggered.connect(self._save_file)
        self.save_action.setStatusTip(I18N.t('menu.file.save', "Save current project"))
        self.file_menu.addAction(self.save_action)

        self.save_as_action = QAction(I18N.t('menu.file.save_as', "Save As..."), self)
        self.save_as_action.triggered.connect(self._save_file_as)
        self.save_as_action.setStatusTip(I18N.t('menu.file.save_as', "Save project with a new name"))
        self.file_menu.addAction(self.save_as_action)

        self.file_menu.addSeparator()

        exit_action = QAction(I18N.t('menu.file.exit', "Exit"), self)
        exit_action.triggered.connect(self.close)
        exit_action.setStatusTip(I18N.t('menu.file.exit', "Exit the application"))
        self.file_menu.addAction(exit_action)

        # Language menu
        lang_menu = menubar.addMenu(I18N.t('menu.language', "Language"))
        en_action = QAction(I18N.t('language.english', "🇺🇸 English"), self)
        en_action.setCheckable(True)
        en_action.setChecked(self.current_locale == 'en')
        en_action.triggered.connect(lambda: self._set_locale('en'))
        uk_action = QAction(I18N.t('language.ukrainian', "🇺🇦 Ukrainian"), self)
        uk_action.setCheckable(True)
        uk_action.setChecked(self.current_locale == 'uk')
        uk_action.triggered.connect(lambda: self._set_locale('uk'))
        ru_action = QAction(I18N.t('language.russian', "🇷🇺 Russian"), self)
        ru_action.setCheckable(True)
        ru_action.setChecked(self.current_locale == 'ru')
        ru_action.triggered.connect(lambda: self._set_locale('ru'))
        lang_menu.addAction(en_action)
        lang_menu.addAction(uk_action)
        lang_menu.addAction(ru_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        # View menu
        view_menu = menubar.addMenu("&View")

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        about_action.setStatusTip("About MythWeave")
        help_menu.addAction(about_action)

    def _set_locale(self, locale: str):
        """Set application locale and update UI texts."""
        I18N.load(locale)
        self.current_locale = locale
        # Update combo box selection
        if hasattr(self, 'lang_combo'):
            self.lang_combo.blockSignals(True)
            self.lang_combo.setCurrentText("🇺🇸 English" if locale == "en" else "🇺🇦 Українська" if locale == "uk" else "🇷🇺 Русский")
            self.lang_combo.blockSignals(False)
        self._retranslate_ui()

    def _on_language_changed(self):
        """Handle language combo box selection change."""
        locale = self.lang_combo.currentData()
        self._set_locale(locale)

    def _retranslate_ui(self):
        """Update all translatable UI texts."""
        # Window title
        self.setWindowTitle(I18N.t('app.title', "🎮 MythWeave - Lore Management System"))

        # Tabs
        try:
            self.tabs.setTabText(0, I18N.t('tab.worlds', "🌍 Worlds"))
            self.tabs.setTabText(1, I18N.t('tab.characters', "👥 Characters"))
            self.tabs.setTabText(2, I18N.t('tab.events', "⚡ Events"))
            self.tabs.setTabText(3, I18N.t('tab.improvements', "⬆️ Improvements"))
            self.tabs.setTabText(4, I18N.t('tab.items', "⚔️ Items"))
            # quests/storylines may not exist in older layouts
            if self.tabs.count() > 5:
                self.tabs.setTabText(5, I18N.t('tab.quests', "🎯 Quests"))
            if self.tabs.count() > 6:
                self.tabs.setTabText(6, I18N.t('tab.storylines', "📖 Storylines"))
        except Exception:
            pass

        # Search placeholder
        try:
            self.search_input.setPlaceholderText(I18N.t('search.placeholder', "Search across all entities..."))
        except Exception:
            pass

        # File menu (actions)
        try:
            # Update file menu title
            if hasattr(self, 'file_menu'):
                self.file_menu.setTitle(I18N.t('menu.file', 'File'))
            self.new_action.setText(I18N.t('menu.file.new', 'New Project'))
            self.open_action.setText(I18N.t('menu.file.open', 'Open...'))
            self.load_sample_action.setText(I18N.t('menu.file.load_sample', 'Load Sample Data'))
            self.save_action.setText(I18N.t('menu.file.save', 'Save'))
            self.save_as_action.setText(I18N.t('menu.file.save_as', 'Save As...'))
        except Exception:
            pass

        # Update language menu checkmarks
        try:
            # Find the language menu and update checkmarks
            menubar = self.menuBar()
            for i in range(menubar.count()):
                menu = menubar.actions()[i].menu()
                if menu and I18N.t('menu.language', 'Language') in menu.title():
                    for action in menu.actions():
                        if 'English' in action.text() or 'Англійська' in action.text() or 'English' in action.text():
                            action.setChecked(self.current_locale == 'en')
                        elif 'Ukrainian' in action.text() or 'Українська' in action.text() or 'Українська' in action.text():
                            action.setChecked(self.current_locale == 'uk')
                        elif 'Russian' in action.text() or 'Русский' in action.text() or 'Російська' in action.text():
                            action.setChecked(self.current_locale == 'ru')
                    break
        except Exception:
            pass

        # Update language combo box
        try:
            if hasattr(self, 'lang_combo'):
                self.lang_combo.blockSignals(True)
                self.lang_combo.clear()
                self.lang_combo.addItem(I18N.t('language.english', "🇺🇸 English"), "en")
                self.lang_combo.addItem(I18N.t('language.ukrainian', "🇺🇦 Ukrainian"), "uk")
                self.lang_combo.addItem(I18N.t('language.russian', "🇷🇺 Russian"), "ru")
                current_text = I18N.t('language.english', "🇺🇸 English") if self.current_locale == "en" else I18N.t('language.ukrainian', "🇺🇦 Ukrainian") if self.current_locale == "uk" else I18N.t('language.russian', "🇷🇺 Russian")
                self.lang_combo.setCurrentText(current_text)
                self.lang_combo.blockSignals(False)
        except Exception:
            pass

    def _create_tool_bar(self):
        """Create application tool bar."""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # File actions
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        
        # Sample data action
        sample_action = QAction("📚 Load Sample", self)
        sample_action.triggered.connect(self._load_sample_data)
        sample_action.setToolTip("Load sample lore data")
        toolbar.addAction(sample_action)
        toolbar.addSeparator()

        # Language selector
        from PyQt6.QtWidgets import QComboBox
        self.lang_combo = QComboBox()
        self.lang_combo.addItem(I18N.t('language.english', "🇺🇸 English"), "en")
        self.lang_combo.addItem(I18N.t('language.ukrainian', "🇺🇦 Ukrainian"), "uk")
        self.lang_combo.addItem(I18N.t('language.russian', "🇷🇺 Russian"), "ru")
        self.lang_combo.setCurrentText(I18N.t('language.english', "🇺🇸 English") if self.current_locale == "en" else I18N.t('language.ukrainian', "🇺🇦 Ukrainian") if self.current_locale == "uk" else I18N.t('language.russian', "🇷🇺 Russian"))
        self.lang_combo.currentIndexChanged.connect(self._on_language_changed)
        self.lang_combo.setToolTip(I18N.t('menu.language', 'Select language'))
        self.lang_combo.setStyleSheet("""
            QComboBox {
                background: #3a3a3a;
                color: #ddd;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 2px 5px;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #ddd;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background: #2b2b2b;
                color: #ddd;
                border: 1px solid #555;
                selection-background-color: #4a4a4a;
            }
        """)
        toolbar.addWidget(self.lang_combo)
        toolbar.addSeparator()

        # Quick stats
        self.stats_label = QLabel("Entities: 0 | Worlds: 0")
        self.stats_label.setStyleSheet("color: #ddd; padding: 5px;")
        toolbar.addWidget(self.stats_label)

    def _setup_status_bar(self):
        """Setup enhanced status bar."""
        self.statusBar()

        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.statusBar().addPermanentWidget(self.progress_bar)

        # Current operation label
        self.operation_label = QLabel("Ready")
        self.statusBar().addWidget(self.operation_label)

    def _on_search_text_changed(self, text: str):
        """Handle search text changes."""
        # Implement search across all tabs
        current_tab = self.tabs.currentWidget()
        if hasattr(current_tab, 'filter_items'):
            current_tab.filter_items(text)

    def _on_tab_changed(self, index: int):
        """Handle tab changes."""
        if index >= 0:
            tab_name = self.tab_list.item(index).text()
            self.statusBar().showMessage(f"Switched to {tab_name} tab")
        else:
            self.statusBar().showMessage("")

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About MythWeave",
            "<h2>MythWeave Chronicles</h2>"
            "<p>A powerful tool for managing fantasy world lore.</p>"
            "<p><b>Version:</b> 1.0.0</p>"
            "<p><b>Built with:</b> Python 3.14, PyQt6</p>"
            "<p>Organize your worlds, characters, events, improvements, and items with ease.</p>"
        )
    
    def _refresh_all(self):
        """Refresh all tabs and update statistics."""
        self.worlds_tab.refresh()
        self.characters_tab.refresh()
        self.events_tab.refresh()
        self.improvements_tab.refresh()
        self.items_tab.refresh()
        self._update_statistics()

    def _update_statistics(self):
        """Update the statistics display."""
        total_entities = (
            len(self.lore_data.worlds) +
            len(self.lore_data.characters) +
            len(self.lore_data.events) +
            len(self.lore_data.improvements) +
            len(self.lore_data.items)
        )

        stats_text = (
            f"Entities: {total_entities} | "
            f"Worlds: {len(self.lore_data.worlds)} | "
            f"Characters: {len(self.lore_data.characters)} | "
            f"Events: {len(self.lore_data.events)} | "
            f"Improvements: {len(self.lore_data.improvements)} | "
            f"Items: {len(self.lore_data.items)}"
        )

        self.stats_label.setText(stats_text)
        self.statusBar().showMessage("Data refreshed")

    def _refresh_all(self):
        """Refresh all tabs and update statistics."""
        self.worlds_tab.refresh()
        self.characters_tab.refresh()
        self.events_tab.refresh()
        self.improvements_tab.refresh()
        self.items_tab.refresh()
        self._update_statistics()

    def _update_statistics(self):
        """Update the statistics display."""
        total_entities = (
            len(self.lore_data.worlds) +
            len(self.lore_data.characters) +
            len(self.lore_data.events) +
            len(self.lore_data.improvements) +
            len(self.lore_data.items)
        )

        stats_text = (
            f"Entities: {total_entities} | "
            f"Worlds: {len(self.lore_data.worlds)} | "
            f"Characters: {len(self.lore_data.characters)} | "
            f"Events: {len(self.lore_data.events)} | "
            f"Improvements: {len(self.lore_data.improvements)} | "
            f"Items: {len(self.lore_data.items)}"
        )

        self.stats_label.setText(stats_text)
        self.statusBar().showMessage("Data refreshed")
    
    def _new_file(self):
        """Create a new lore file."""
        reply = QMessageBox.question(
            self, "New Project",
            "This will clear all current data. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.operation_label.setText("Creating new project...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress

            # Simulate some work
            QTimer.singleShot(100, lambda: self._finish_new_file())

    def _finish_new_file(self):
        """Complete the new file creation."""
        self.lore_data = LoreData()
        self.worlds_tab.lore_data = self.lore_data
        self.characters_tab.lore_data = self.lore_data
        self.events_tab.lore_data = self.lore_data
        self.improvements_tab.lore_data = self.lore_data
        self.items_tab.lore_data = self.lore_data
        self.current_file = None
        self._refresh_all()
        self.progress_bar.setVisible(False)
        self.operation_label.setText("New project created")
        self.setWindowTitle("🎮 MythWeave - Lore Management System (Untitled)")

    def _load_file(self):
        """Load lore from JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Lore Project", "", "Lore Files (*.json);;All Files (*)"
        )

        if file_path:
            self.operation_label.setText("Loading project...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.lore_data.from_dict(data)
                self.current_file = Path(file_path)
                self._refresh_all()
                
                # Ensure GUI updates before showing message
                QApplication.processEvents()
                
                self.progress_bar.setVisible(False)
                self.operation_label.setText(f"Loaded: {Path(file_path).name}")
                self.setWindowTitle(f"🎮 MythWeave - {Path(file_path).name}")
                
                # Get updated stats for the message
                total_entities = (
                    len(self.lore_data.worlds) +
                    len(self.lore_data.characters) +
                    len(self.lore_data.events) +
                    len(self.lore_data.improvements) +
                    len(self.lore_data.items)
                )
                
                QMessageBox.information(
                    self, "Success",
                    f"Project loaded successfully!\n\n"
                    f"Entities: {total_entities} | "
                    f"Worlds: {len(self.lore_data.worlds)} | "
                    f"Characters: {len(self.lore_data.characters)} | "
                    f"Events: {len(self.lore_data.events)} | "
                    f"Improvements: {len(self.lore_data.improvements)} | "
                    f"Items: {len(self.lore_data.items)}"
                )
            except Exception as e:
                self.progress_bar.setVisible(False)
                self.operation_label.setText("Load failed")
                QMessageBox.critical(
                    self, "Load Error",
                    f"Failed to load project:\n\n{str(e)}"
                )

    def _save_file(self):
        """Save lore to current file."""
        if not self.current_file:
            self._save_file_as()
            return

        self._perform_save(self.current_file)

    def _save_file_as(self):
        """Save lore with new filename."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Lore Project", "", "Lore Files (*.json);;All Files (*)"
        )

        if file_path:
            # Ensure .json extension
            if not file_path.endswith('.json'):
                file_path += '.json'
            self._perform_save(Path(file_path))

    def _perform_save(self, file_path: Path):
        """Perform the actual save operation."""
        self.operation_label.setText("Saving project...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        try:
            data = self.lore_data.to_dict()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.current_file = file_path
            self.progress_bar.setVisible(False)
            self.operation_label.setText(f"Saved: {file_path.name}")
            self.setWindowTitle(f"🎮 MythWeave - {file_path.name}")
            QMessageBox.information(self, "Success", "Project saved successfully!")

        except Exception as e:
            self.progress_bar.setVisible(False)
            self.operation_label.setText("Save failed")
            QMessageBox.critical(
                self, "Save Error",
                f"Failed to save project:\n\n{str(e)}"
            )
    
    def _save_file(self):
        """Save lore to current file."""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self._save_file_as()
    
    def _save_file_as(self):
        """Save lore to a new file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Lore File", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.current_file = Path(file_path)
            self._save_to_file(self.current_file)
    
    def _save_to_file(self, file_path: Path):
        """Save lore to specified file."""
        try:
            data = self.lore_data.to_dict()
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.statusBar().showMessage(f"Saved: {file_path}")
            QMessageBox.information(self, "Success", "Lore saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
    
    def _load_file_by_path(self, file_path: str, show_message: bool = True):
        """Load lore from a specific file path.

        Args:
            file_path: Path to the JSON file to load
            show_message: Whether to show success/error message boxes

        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.lore_data.from_dict(data)
            self.current_file = Path(file_path)
            self._refresh_all()

            # Get comprehensive entity counts
            entity_counts = {
                'worlds': len(self.lore_data.worlds),
                'characters': len(self.lore_data.characters),
                'events': len(self.lore_data.events),
                'improvements': len(self.lore_data.improvements),
                'items': len(self.lore_data.items),
                'quests': len(self.lore_data.quests),
                'storylines': len(self.lore_data.storylines),
                'pages': len(self.lore_data.pages),
                'templates': len(self.lore_data.templates),
                'stories': len(self.lore_data.stories),
                'tags': len(self.lore_data.tags),
                'images': len(self.lore_data.images),
                'choices': len(self.lore_data.choices),
                'flowcharts': len(self.lore_data.flowcharts),
                'handouts': len(self.lore_data.handouts),
                'inspirations': len(self.lore_data.inspirations),
                'maps': len(self.lore_data.maps),
                'notes': len(self.lore_data.notes),
                'requirements': len(self.lore_data.requirements),
                'sessions': len(self.lore_data.sessions),
                'tokenboards': len(self.lore_data.tokenboards),
            }

            total_entities = sum(entity_counts.values())

            # Update window title
            self.setWindowTitle(f"🎮 MythWeave - {Path(file_path).name}")

            # Update header status after loading
            self._update_header_status()

            if show_message:
                # Build detailed entity report
                entity_report = '\n'.join([
                    f"{name.title()}: {count}" for name, count in entity_counts.items() if count > 0
                ])

                QMessageBox.information(
                    self, "Success",
                    f"Project loaded successfully!\n\n"
                    f"Total Entities: {total_entities}\n\n"
                    f"{entity_report}"
                )

            return True

        except FileNotFoundError:
            if show_message:
                QMessageBox.warning(
                    self, "File Not Found",
                    f"Sample file not found:\n{file_path}\n\n"
                    f"The application will start with an empty project."
                )
            return False

        except Exception as e:
            if show_message:
                QMessageBox.critical(
                    self, "Load Error",
                    f"Failed to load project:\n\n{str(e)}\n\n"
                    f"The application will start with an empty project."
                )
            return False

    def _refresh_all(self):
        """Refresh all tabs."""
        self.worlds_tab.refresh()
        self.world_map_tab.refresh()
        self.characters_tab.refresh()
        self.events_tab.refresh()
        self.improvements_tab.refresh()
        self.items_tab.refresh()
        self.texture_tab.refresh()
        self.model3d_tab.refresh()
        self.quests_tab.refresh()
        self.storylines_tab.refresh()
        self.pages_tab.refresh()
        self.templates_tab.refresh()
        self.stories_tab.refresh()
        self.tags_tab.refresh()
        self.images_tab.refresh()
        self.choices_tab.refresh()
        self.flowcharts_tab.refresh()
        self.handouts_tab.refresh()
        self.inspirations_tab.refresh()
        self.maps_tab.refresh()
        self.notes_tab.refresh()
        self.requirements_tab.refresh()
        self.sessions_tab.refresh()
        self.tokenboards_tab.refresh()
        self.progression_simulator_tab.refresh()
        self._update_header_status()

    def _update_header_status(self):
        """Update header status indicators."""
        try:
            # Update world indicator
            if self.lore_data.worlds:
                current_world = self.lore_data.worlds[0]  # For now, show first world
                self.world_indicator.setText(f"🌍 {current_world.name.value[:15]}...")
                self.world_indicator.setStyleSheet("color: #4a9eff; font-size: 10px; padding: 2px 6px; background: #1a1a1a; border-radius: 3px;")
            else:
                self.world_indicator.setText("🌍 No World")
                self.world_indicator.setStyleSheet("color: #888; font-size: 10px; padding: 2px 6px; background: #1a1a1a; border-radius: 3px;")

            # Update character count
            char_count = len(self.lore_data.characters)
            self.char_count_label.setText(f"👥 {char_count}")
            if char_count > 0:
                self.char_count_label.setStyleSheet("color: #4ae54a; font-size: 10px; padding: 2px 6px; background: #1a1a1a; border-radius: 3px;")
            else:
                self.char_count_label.setStyleSheet("color: #888; font-size: 10px; padding: 2px 6px; background: #1a1a1a; border-radius: 3px;")

        except Exception as e:
            # Silently handle errors in status updates
            pass

    def _quick_save(self):
        """Perform a quick save operation."""
        try:
            if hasattr(self, 'current_file') and self.current_file:
                self._save_file()
                # Briefly highlight the save button (if available)
                save_btn = self.sender()
                if save_btn and hasattr(save_btn, 'setStyleSheet'):
                    original_style = save_btn.styleSheet()
                    save_btn.setStyleSheet("""
                        QPushButton {
                            background: #4a6a2a;
                            color: #fff;
                            border: 1px solid #6a8a4a;
                            border-radius: 4px;
                            padding: 2px;
                            font-size: 10px;
                        }
                    """)
                    QTimer.singleShot(500, lambda: save_btn.setStyleSheet(original_style))
            else:
                self._save_file_as()
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Failed to save: {e}")

    def _on_world_selected(self, world_id: EntityId):
        """Handle world selection."""
        self._update_header_status()

def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("MythWeave")
    app.setOrganizationName("MythWeave")
    
    window = MainWindow()
    window.show()
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
