"""
MainWindow - Main application window for MythWeave.
"""
import json
import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QGroupBox, QLabel, QComboBox, QMessageBox, QSplitter,
    QMenu, QFrame, QListWidget, QStackedWidget, QProgressBar, QFileDialog,
    QStatusBar, QMenuBar, QToolBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QAction, QKeySequence

from src.presentation.gui.lore_data import LoreData
from src.presentation.gui.i18n import I18N as I18n
from src.presentation.gui.tabs.worlds_tab import WorldsTab
from src.presentation.gui.tabs.characters_tab import CharactersTab
from src.presentation.gui.tabs.events_tab import EventsTab
from src.presentation.gui.tabs.improvements_tab import ImprovementsTab
from src.presentation.gui.tabs.items_tab import ItemsTab
from src.presentation.gui.tabs.quests_tab import QuestsTab
from src.presentation.gui.tabs.storylines_tab import StorylinesTab
from src.presentation.gui.tabs.pages_tab import PagesTab
from src.presentation.gui.tabs.templates_tab import TemplatesTab
from src.presentation.gui.tabs.stories_tab import StoriesTab
from src.presentation.gui.tabs.tags_tab import TagsTab
from src.presentation.gui.tabs.images_tab import ImagesTab
from src.presentation.gui.tabs.world_map_tab import WorldMapTab
from src.domain.value_objects.common import EntityId


class MainWindow(QMainWindow):
    """Main application window with enhanced UI/UX."""

    def __init__(self):
        super().__init__()
        self.lore_data = LoreData()
        self.current_file: Optional[Path] = None
        self.current_locale = 'en'  # Default to English
        self._setup_style()
        self._setup_ui()
        self.setWindowTitle(I18n.t('app.title', "🎮 MythWeave - Lore Management System"))
        self.setWindowIcon(QIcon())  # We'll add a proper icon later
        self.resize(1400, 900)
        self._setup_shortcuts()

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

        # Header with gradient background
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.NoFrame)
        header_frame.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4a4a4a, stop:0.5 #5a5a5a, stop:1 #4a4a4a);
            border-radius: 10px;
            padding: 10px;
        """)

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(20, 10, 20, 10)

        title_label = QLabel("🎮 MythWeave Chronicles")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #fff; font-weight: bold;")

        subtitle_label = QLabel("Master your world's lore with powerful tools")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #ccc;")

        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_frame.setLayout(header_layout)

        main_layout.addWidget(header_frame)

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Quick Search:")
        search_label.setStyleSheet("color: #ddd; font-weight: bold;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(I18n.t('search.placeholder', "Search across all entities..."))
        self.search_input.textChanged.connect(self._on_search_text_changed)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()

        main_layout.addLayout(search_layout)

        # Tabs with enhanced styling - using list and stacked widget for better readability
        tab_layout = QHBoxLayout()

        self.tab_list = QListWidget()
        self.tab_list.setMaximumWidth(200)
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
        """)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("""
            QStackedWidget {
                border: 2px solid #666;
                background: #2b2b2b;
                border-radius: 8px;
            }
        """)

        self.worlds_tab = WorldsTab(self.lore_data)
        try:
            self.world_map_tab = WorldMapTab(self.lore_data)
        except Exception as e:
            print(f"Error creating WorldMapTab: {e}")
            self.world_map_tab = QWidget()  # Placeholder
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
        try:
            self.world_map_tab = WorldMapTab(self.lore_data)
        except Exception as e:
            print(f"Error creating WorldMapTab: {e}")
            import traceback
            traceback.print_exc()
            self.world_map_tab = QWidget()  # Placeholder

        # Add to stacked widget and list
        tabs = [
            (self.worlds_tab, I18n.t('tab.worlds', "🌍 Worlds")),
            (self.world_map_tab, I18n.t('tab.world_map', "🗺️ World Map")),
            (self.characters_tab, I18n.t('tab.characters', "👥 Characters")),
            (self.events_tab, I18n.t('tab.events', "⚡ Events")),
            (self.improvements_tab, I18n.t('tab.improvements', "⬆️ Improvements")),
            (self.items_tab, I18n.t('tab.items', "⚔️ Items")),
            (self.quests_tab, I18n.t('tab.quests', "🎯 Quests")),
            (self.storylines_tab, I18n.t('tab.storylines', "📖 Storylines")),
            (self.pages_tab, I18n.t('tab.pages', "📄 Pages")),
            (self.templates_tab, I18n.t('tab.templates', "📋 Templates")),
            (self.stories_tab, I18n.t('tab.stories', "📚 Stories")),
            (self.tags_tab, I18n.t('tab.tags', "🏷️ Tags")),
            (self.images_tab, I18n.t('tab.images', "🖼️ Images")),
        ]

        for tab, name in tabs:
            self.stacked_widget.addWidget(tab)
            self.tab_list.addItem(name)

        # Set initial selection
        self.tab_list.setCurrentRow(0)
        self.tab_list.update()
        self.tab_list.repaint()
        self.tab_list.setFocus()

        tab_layout.addWidget(self.tab_list)
        tab_layout.addWidget(self.stacked_widget)

        main_layout.addLayout(tab_layout)

        # Connect list to stacked widget
        self.tab_list.currentRowChanged.connect(self.stacked_widget.setCurrentIndex)
        self.tab_list.currentRowChanged.connect(self._on_tab_changed)

        # Enhanced status bar
        self._setup_status_bar()

        # Connect signals
        self.worlds_tab.world_selected.connect(self._on_world_selected)

        # Check for sample data on startup
        QTimer.singleShot(1000, self._check_for_sample_data)  # Delay to ensure UI is fully loaded

    def _set_locale(self, locale: str):
        """Set application locale and update UI texts."""
        I18n.load(locale)
        self.current_locale = locale
        self._retranslate_ui()

    def _retranslate_ui(self):
        """Update all translatable UI texts."""
        # Window title
        self.setWindowTitle(I18n.t('app.title', "🎮 MythWeave - Lore Management System"))

        # Tabs
        try:
            self.tabs.setTabText(0, I18n.t('tab.worlds', "🌍 Worlds"))
            self.tabs.setTabText(1, I18n.t('tab.characters', "👥 Characters"))
            self.tabs.setTabText(2, I18n.t('tab.events', "⚡ Events"))
            self.tabs.setTabText(3, I18n.t('tab.improvements', "⬆️ Improvements"))
            self.tabs.setTabText(4, I18n.t('tab.items', "⚔️ Items"))
            # quests/storylines may not exist in older layouts
            if self.tabs.count() > 5:
                self.tabs.setTabText(5, I18n.t('tab.quests', "🎯 Quests"))
            if self.tabs.count() > 6:
                self.tabs.setTabText(6, I18n.t('tab.storylines', "📖 Storylines"))
        except Exception:
            pass

        # Search placeholder
        try:
            self.search_input.setPlaceholderText(I18n.t('search.placeholder', "Search across all entities..."))
        except Exception:
            pass

        # File menu (actions)
        try:
            # Update file menu title
            if hasattr(self, 'file_menu'):
                self.file_menu.setTitle(I18n.t('menu.file', 'File'))
            self.new_action.setText(I18n.t('menu.file.new', 'New Project'))
            self.open_action.setText(I18n.t('menu.file.open', 'Open...'))
            self.load_sample_action.setText(I18n.t('menu.file.load_sample', 'Load Sample Data'))
            self.save_action.setText(I18n.t('menu.file.save', 'Save'))
            self.save_as_action.setText(I18n.t('menu.file.save_as', 'Save As...'))
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
                self, I18n.t('sample.welcome.title', "Welcome to MythWeave!"),
                I18n.t('sample.welcome.body', "Would you like to load the sample lore data to explore the features?"),
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
                self.current_file = sample_file
                self._refresh_all()
                self.setWindowTitle(f"🎮 MythWeave - {sample_file.name}")
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
        self.file_menu = menubar.addMenu(I18n.t('menu.file', "File"))

        self.new_action = QAction(I18n.t('menu.file.new', "New Project"), self)
        self.new_action.triggered.connect(self._new_file)
        self.new_action.setStatusTip(I18n.t('menu.file.new', "Create a new lore project"))
        self.file_menu.addAction(self.new_action)

        self.open_action = QAction(I18n.t('menu.file.open', "Open..."), self)
        self.open_action.triggered.connect(self._load_file)
        self.open_action.setStatusTip(I18N.t('menu.file.open', "Open an existing lore file"))
        self.file_menu.addAction(self.open_action)

        self.file_menu.addSeparator()

        self.load_sample_action = QAction(I18n.t('menu.file.load_sample', "Load Sample Data"), self)
        self.load_sample_action.triggered.connect(self._load_sample_data)
        self.load_sample_action.setStatusTip(I18n.t('menu.file.load_sample', "Load sample lore data to explore features"))
        self.file_menu.addAction(self.load_sample_action)

        self.file_menu.addSeparator()

        self.save_action = QAction(I18n.t('menu.file.save', "Save"), self)
        self.save_action.triggered.connect(self._save_file)
        self.save_action.setStatusTip(I18n.t('menu.file.save', "Save current project"))
        self.file_menu.addAction(self.save_action)

        self.save_as_action = QAction(I18n.t('menu.file.save_as', "Save As..."), self)
        self.save_as_action.triggered.connect(self._save_file_as)
        self.save_as_action.setStatusTip(I18n.t('menu.file.save_as', "Save project with a new name"))
        self.file_menu.addAction(self.save_as_action)

        self.file_menu.addSeparator()

        exit_action = QAction(I18n.t('menu.file.exit', "Exit"), self)
        exit_action.triggered.connect(self.close)
        exit_action.setStatusTip(I18n.t('menu.file.exit', "Exit the application"))
        self.file_menu.addAction(exit_action)

        # Language menu
        lang_menu = menubar.addMenu(I18n.t('menu.language', "Language"))
        en_action = QAction(I18n.t('language.english', "🇺🇸 English"), self)
        en_action.setCheckable(True)
        en_action.setChecked(self.current_locale == 'en')
        en_action.triggered.connect(lambda: self._set_locale('en'))
        uk_action = QAction(I18n.t('language.ukrainian', "🇺🇦 Ukrainian"), self)
        uk_action.setCheckable(True)
        uk_action.setChecked(self.current_locale == 'uk')
        uk_action.triggered.connect(lambda: self._set_locale('uk'))
        ru_action = QAction(I18n.t('language.russian', "🇷🇺 Russian"), self)
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
        about_action.setToolTip("About MythWeave")
        help_menu.addAction(about_action)

    def _set_locale(self, locale: str):
        """Set application locale and update UI texts."""
        I18n.load(locale)
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
        self.setWindowTitle(I18n.t('app.title', "🎮 MythWeave - Lore Management System"))

        # Tabs
        try:
            self.tabs.setTabText(0, I18n.t('tab.worlds', "🌍 Worlds"))
            self.tabs.setTabText(1, I18n.t('tab.characters', "👥 Characters"))
            self.tabs.setTabText(2, I18n.t('tab.events', "⚡ Events"))
            self.tabs.setTabText(3, I18n.t('tab.improvements', "⬆️ Improvements"))
            self.tabs.setTabText(4, I18n.t('tab.items', "⚔️ Items"))
            # quests/storylines may not exist in older layouts
            if self.tabs.count() > 5:
                self.tabs.setTabText(5, I18n.t('tab.quests', "🎯 Quests"))
            if self.tabs.count() > 6:
                self.tabs.setTabText(6, I18n.t('tab.storylines', "📖 Storylines"))
        except Exception:
            pass

        # Search placeholder
        try:
            self.search_input.setPlaceholderText(I18n.t('search.placeholder', "Search across all entities..."))
        except Exception:
            pass

        # File menu (actions)
        try:
            # Update file menu title
            if hasattr(self, 'file_menu'):
                self.file_menu.setTitle(I18n.t('menu.file', 'File'))
            self.new_action.setText(I18n.t('menu.file.new', 'New Project'))
            self.open_action.setText(I18n.t('menu.file.open', 'Open...'))
            self.load_sample_action.setText(I18n.t('menu.file.load_sample', 'Load Sample Data'))
            self.save_action.setText(I18n.t('menu.file.save', 'Save'))
            self.save_as_action.setText(I18n.t('menu.file.save_as', 'Save As...'))
        except Exception:
            pass

        # Update language menu checkmarks
        try:
            # Find the language menu and update checkmarks
            menubar = self.menuBar()
            for i in range(menubar.count()):
                menu = menubar.actions()[i].menu()
                if menu and I18n.t('menu.language', 'Language') in menu.title():
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
                self.lang_combo.addItem(I18n.t('language.english', "🇺🇸 English"), "en")
                self.lang_combo.addItem(I18n.t('language.ukrainian', "🇺🇦 Ukrainian"), "uk")
                self.lang_combo.addItem(I18n.t('language.russian', "🇷🇺 Russian"), "ru")
                current_text = I18n.t('language.english', "🇺🇸 English") if self.current_locale == "en" else I18n.t('language.ukrainian', "🇺🇦 Ukrainian") if self.current_locale == "uk" else I18n.t('language.russian', "🇷🇺 Russian")
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
        self.lang_combo.addItem(I18n.t('language.english', "🇺🇸 English"), "en")
        self.lang_combo.addItem(I18n.t('language.ukrainian', "🇺🇦 Ukrainian"), "uk")
        self.lang_combo.addItem(I18n.t('language.russian', "🇷🇺 Russian"), "ru")
        self.lang_combo.setCurrentText(I18n.t('language.english', "🇺🇸 English") if self.current_locale == "en" else I18n.t('language.ukrainian', "🇺🇦 Ukrainian") if self.current_locale == "uk" else I18n.t('language.russian', "🇷🇺 Russian"))
        self.lang_combo.currentIndexChanged.connect(self._on_language_changed)
        self.lang_combo.setToolTip(I18n.t('menu.language', 'Select language'))
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
        self.world_map_tab.refresh()
        self.characters_tab.refresh()
        self.events_tab.refresh()
        self.improvements_tab.refresh()
        self.items_tab.refresh()
        self.quests_tab.refresh()
        self.storylines_tab.refresh()
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
        self.quests_tab.lore_data = self.lore_data
        self.storylines_tab.lore_data = self.lore_data
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