"""
PyQt6 GUI Application for MythWeave System

Main window with tabs for managing worlds, characters, and events.
Enhanced UI/UX with modern styling, icons, and improved user experience.
"""
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
    QSystemTrayIcon, QHeaderView, QStackedWidget
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

from src.domain.entities.world import World
from src.domain.entities.character import Character
from src.domain.entities.event import Event
from src.domain.entities.improvement import Improvement
from src.domain.entities.item import Item
from src.domain.entities.quest import Quest
from src.domain.entities.storyline import Storyline
from src.domain.entities.page import Page
from src.domain.entities.template import Template
from src.domain.entities.story import Story
from src.domain.entities.tag import Tag
from src.domain.entities.image import Image
from src.domain.value_objects.common import (
    TenantId, EntityId, WorldName, Description, CharacterName,
    Backstory, Timestamp, EntityType, EventOutcome, CharacterStatus,
    ItemType, Rarity, QuestStatus, StorylineType,
    PageName, Content, TemplateName, TemplateType, StoryName, StoryType,
    TagName, TagType, ImagePath, ImageType
)
from src.domain.value_objects.ability import Ability, AbilityName, PowerLevel
from src.domain.exceptions import DomainException

# Import new tab modules
from src.presentation.gui.tabs import (
    PagesTab, TemplatesTab, StoriesTab, TagsTab, ImagesTab,
    ChoiceTab, FlowchartTab, HandoutTab, InspirationTab, MapTab,
    NoteTab, RequirementTab, SessionTab, TokenboardTab
)
from src.presentation.gui.tabs.world_map_tab import WorldMapTab
from src.presentation.gui.tabs.banner_tab import BannerTab
from src.presentation.gui.tabs.location_tab import LocationTab
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


# Import LoreData from separate module
from src.presentation.gui.lore_data import LoreData


# Import AbilityDialog from separate module
from src.presentation.gui.dialogs.ability_dialog import AbilityDialog


class WorldsTab(QWidget):
    """Tab for managing worlds."""
    
    world_selected = pyqtSignal(EntityId)
    
    def __init__(self, lore_data: LoreData):
        super().__init__()
        self.lore_data = lore_data
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Worlds")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Worlds table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Description", "Version"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.table)
        
        # Form
        form_group = QGroupBox("World Details")
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Description:", self.description_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add World")
        self.add_btn.clicked.connect(self._add_world)
        
        self.update_btn = QPushButton("Update World")
        self.update_btn.clicked.connect(self._update_world)
        self.update_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("Delete World")
        self.delete_btn.clicked.connect(self._delete_world)
        self.delete_btn.setEnabled(False)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.selected_world: Optional[World] = None
    
    def refresh(self):
        """Refresh the worlds table."""
        self.table.setRowCount(0)
        
        for world in self.lore_data.worlds:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(world.id.value)))
            self.table.setItem(row, 1, QTableWidgetItem(str(world.name)))
            self.table.setItem(row, 2, QTableWidgetItem(str(world.description)[:50] + "..."))
            self.table.setItem(row, 3, QTableWidgetItem(str(world.version)))
        
        self.table.resizeColumnsToContents()
    
    def _on_selection_changed(self):
        """Handle world selection."""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            world_id = EntityId(int(self.table.item(row, 0).text()))
            self.selected_world = self.lore_data.get_world_by_id(world_id)
            
            if self.selected_world:
                self.name_input.setText(str(self.selected_world.name))
                self.description_input.setPlainText(str(self.selected_world.description))
                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.world_selected.emit(world_id)
        else:
            self.selected_world = None
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
    
    def _add_world(self):
        """Add a new world."""
        try:
            world = World.create(
                tenant_id=self.lore_data.tenant_id,
                name=WorldName(self.name_input.text()),
                description=Description(self.description_input.toPlainText())
            )
            self.lore_data.add_world(world)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "World created successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create world: {e}")
    
    def _update_world(self):
        """Update selected world."""
        if not self.selected_world:
            return
        
        try:
            self.selected_world.rename(WorldName(self.name_input.text()))
            self.selected_world.update_description(Description(self.description_input.toPlainText()))
            self.refresh()
            QMessageBox.information(self, "Success", "World updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update world: {e}")
    
    def _delete_world(self):
        """Delete selected world."""
        if not self.selected_world:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{self.selected_world.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.lore_data.worlds.remove(self.selected_world)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "World deleted successfully!")
    
    def _clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.description_input.clear()
        self.selected_world = None


class CharactersTab(QWidget):
    """Tab for managing characters."""
    
    def __init__(self, lore_data: LoreData):
        super().__init__()
        self.lore_data = lore_data
        self._setup_ui()
        self.current_abilities: List[Ability] = []
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Characters")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Characters table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "World", "Abilities", "Status"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.table)
        
        # Form
        form_group = QGroupBox("Character Details")
        form_layout = QFormLayout()
        
        self.world_combo = QComboBox()
        self.name_input = QLineEdit()
        self.backstory_input = QTextEdit()
        self.backstory_input.setMaximumHeight(100)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["active", "inactive"])
        
        form_layout.addRow("World:", self.world_combo)
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Backstory (≥100 chars):", self.backstory_input)
        form_layout.addRow("Status:", self.status_combo)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Abilities section
        abilities_group = QGroupBox("Abilities")
        abilities_layout = QVBoxLayout()
        
        self.abilities_list = QListWidget()
        abilities_layout.addWidget(self.abilities_list)
        
        ability_buttons = QHBoxLayout()
        self.add_ability_btn = QPushButton("Add Ability")
        self.add_ability_btn.clicked.connect(self._add_ability)
        self.remove_ability_btn = QPushButton("Remove Ability")
        self.remove_ability_btn.clicked.connect(self._remove_ability)
        
        ability_buttons.addWidget(self.add_ability_btn)
        ability_buttons.addWidget(self.remove_ability_btn)
        abilities_layout.addLayout(ability_buttons)
        
        abilities_group.setLayout(abilities_layout)
        layout.addWidget(abilities_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Character")
        self.add_btn.clicked.connect(self._add_character)
        
        self.update_btn = QPushButton("Update Character")
        self.update_btn.clicked.connect(self._update_character)
        self.update_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("Delete Character")
        self.delete_btn.clicked.connect(self._delete_character)
        self.delete_btn.setEnabled(False)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.selected_character: Optional[Character] = None
    
    def refresh(self):
        """Refresh the characters table and world combo."""
        self.table.setRowCount(0)
        
        for character in self.lore_data.characters:
            world = self.lore_data.get_world_by_id(character.world_id)
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(character.id.value)))
            self.table.setItem(row, 1, QTableWidgetItem(str(character.name)))
            self.table.setItem(row, 2, QTableWidgetItem(str(world.name) if world else "Unknown"))
            self.table.setItem(row, 3, QTableWidgetItem(str(character.ability_count())))
            self.table.setItem(row, 4, QTableWidgetItem(character.status.value))
        
        self.table.resizeColumnsToContents()
        
        # Update world combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(str(world.name), world.id.value)
    
    def _on_selection_changed(self):
        """Handle character selection."""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            character_id = EntityId(int(self.table.item(row, 0).text()))
            self.selected_character = next((c for c in self.lore_data.characters if c.id == character_id), None)
            
            if self.selected_character:
                # Update form
                world_idx = self.world_combo.findData(self.selected_character.world_id.value)
                if world_idx >= 0:
                    self.world_combo.setCurrentIndex(world_idx)
                
                self.name_input.setText(str(self.selected_character.name))
                self.backstory_input.setPlainText(str(self.selected_character.backstory))
                self.status_combo.setCurrentText(self.selected_character.status.value)
                
                # Update abilities list
                self.current_abilities = list(self.selected_character.abilities)
                self._refresh_abilities_list()
                
                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
        else:
            self.selected_character = None
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
    
    def _refresh_abilities_list(self):
        """Refresh abilities list widget."""
        self.abilities_list.clear()
        for ability in self.current_abilities:
            self.abilities_list.addItem(f"{ability.name} (Power: {ability.power_level})")
    
    def _add_ability(self):
        """Add a new ability."""
        dialog = AbilityDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            ability = dialog.get_ability()
            if ability:
                self.current_abilities.append(ability)
                self._refresh_abilities_list()
    
    def _remove_ability(self):
        """Remove selected ability."""
        current_row = self.abilities_list.currentRow()
        if current_row >= 0:
            self.current_abilities.pop(current_row)
            self._refresh_abilities_list()
    
    def _add_character(self):
        """Add a new character."""
        try:
            world_id = EntityId(self.world_combo.currentData())
            
            character = Character.create(
                tenant_id=self.lore_data.tenant_id,
                world_id=world_id,
                name=CharacterName(self.name_input.text()),
                backstory=Backstory(self.backstory_input.toPlainText()),
                abilities=list(self.current_abilities),
                status=CharacterStatus(self.status_combo.currentText())
            )
            self.lore_data.add_character(character)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Character created successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create character: {e}")
    
    def _update_character(self):
        """Update selected character."""
        if not self.selected_character:
            return
        
        try:
            # Create new character with updated values
            world_id = EntityId(self.world_combo.currentData())
            
            updated_character = Character(
                id=self.selected_character.id,
                tenant_id=self.selected_character.tenant_id,
                world_id=world_id,
                name=CharacterName(self.name_input.text()),
                backstory=Backstory(self.backstory_input.toPlainText()),
                status=CharacterStatus(self.status_combo.currentText()),
                abilities=list(self.current_abilities),
                created_at=self.selected_character.created_at,
                updated_at=Timestamp.now(),
                version=self.selected_character.version.increment()
            )
            
            # Replace in list
            idx = self.lore_data.characters.index(self.selected_character)
            self.lore_data.characters[idx] = updated_character
            
            self.refresh()
            QMessageBox.information(self, "Success", "Character updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update character: {e}")
    
    def _delete_character(self):
        """Delete selected character."""
        if not self.selected_character:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{self.selected_character.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.lore_data.characters.remove(self.selected_character)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Character deleted successfully!")
    
    def _clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.backstory_input.clear()
        self.current_abilities.clear()
        self._refresh_abilities_list()
        self.selected_character = None


class EventsTab(QWidget):
    """Tab for managing events."""
    
    def __init__(self, lore_data: LoreData):
        super().__init__()
        self.lore_data = lore_data
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Events")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Events table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "World", "Start Date", "End Date", "Outcome"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.table)
        
        # Form
        form_group = QGroupBox("Event Details")
        form_layout = QFormLayout()
        
        self.world_combo = QComboBox()
        self.name_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.start_date_input = QLineEdit()
        self.start_date_input.setPlaceholderText("YYYY-MM-DD")
        self.end_date_input = QLineEdit()
        self.end_date_input.setPlaceholderText("YYYY-MM-DD (optional)")
        self.outcome_combo = QComboBox()
        self.outcome_combo.addItems(["ongoing", "success", "failure", "cancelled"])
        
        form_layout.addRow("World:", self.world_combo)
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Start Date:", self.start_date_input)
        form_layout.addRow("End Date:", self.end_date_input)
        form_layout.addRow("Outcome:", self.outcome_combo)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Participants section
        participants_group = QGroupBox("Participants")
        participants_layout = QVBoxLayout()
        
        self.participants_list = QListWidget()
        participants_layout.addWidget(self.participants_list)
        
        participant_buttons = QHBoxLayout()
        self.add_participant_btn = QPushButton("Add Participant")
        self.add_participant_btn.clicked.connect(self._add_participant)
        self.remove_participant_btn = QPushButton("Remove Participant")
        self.remove_participant_btn.clicked.connect(self._remove_participant)
        
        participant_buttons.addWidget(self.add_participant_btn)
        participant_buttons.addWidget(self.remove_participant_btn)
        participants_layout.addLayout(participant_buttons)
        
        participants_group.setLayout(participants_layout)
        layout.addWidget(participants_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Event")
        self.add_btn.clicked.connect(self._add_event)
        
        self.update_btn = QPushButton("Update Event")
        self.update_btn.clicked.connect(self._update_event)
        self.update_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("Delete Event")
        self.delete_btn.clicked.connect(self._delete_event)
        self.delete_btn.setEnabled(False)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.selected_event: Optional[Event] = None
    
    def refresh(self):
        """Refresh the events table and world combo."""
        self.table.setRowCount(0)
        
        for event in self.lore_data.events:
            world = self.lore_data.get_world_by_id(event.world_id)
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(event.id.value)))
            self.table.setItem(row, 1, QTableWidgetItem(event.name))
            self.table.setItem(row, 2, QTableWidgetItem(str(world.name) if world else "Unknown"))
            self.table.setItem(row, 3, QTableWidgetItem(event.date_range.start_date.value.strftime("%Y-%m-%d")))
            end_date = event.date_range.end_date.value.strftime("%Y-%m-%d") if event.date_range.end_date else ""
            self.table.setItem(row, 4, QTableWidgetItem(end_date))
            self.table.setItem(row, 5, QTableWidgetItem(event.outcome.value))
        
        self.table.resizeColumnsToContents()
        
        # Update world combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(str(world.name), world.id.value)
    
    def _on_selection_changed(self):
        """Handle event selection."""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            event_id = EntityId(int(self.table.item(row, 0).text()))
            self.selected_event = next((e for e in self.lore_data.events if e.id == event_id), None)
            
            if self.selected_event:
                # Update form
                world_idx = self.world_combo.findData(self.selected_event.world_id.value)
                if world_idx >= 0:
                    self.world_combo.setCurrentIndex(world_idx)
                
                self.name_input.setText(self.selected_event.name)
                self.description_input.setPlainText(str(self.selected_event.description))
                self.start_date_input.setText(self.selected_event.date_range.start_date.value.strftime("%Y-%m-%d"))
                end_date = self.selected_event.date_range.end_date.value.strftime("%Y-%m-%d") if self.selected_event.date_range.end_date else ""
                self.end_date_input.setText(end_date)
                self.outcome_combo.setCurrentText(self.selected_event.outcome.value)
                
                # Update participants list
                self._refresh_participants_list()
                
                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
        else:
            self.selected_event = None
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
    
    def _refresh_participants_list(self):
        """Refresh participants list widget."""
        self.participants_list.clear()
        if self.selected_event:
            for participant_id in self.selected_event.participant_ids:
                character = next((c for c in self.lore_data.characters if c.id == participant_id), None)
                name = str(character.name) if character else f"Unknown (ID: {participant_id.value})"
                self.participants_list.addItem(name)
    
    def _add_participant(self):
        """Add a participant to the event."""
        # Get available characters from selected world
        world_id = EntityId(self.world_combo.currentData())
        available_characters = [c for c in self.lore_data.characters if c.world_id == world_id]
        
        if not available_characters:
            QMessageBox.information(self, "No Characters", "No characters available in selected world.")
            return
        
        # Show dialog to select character
        items = [str(c.name) for c in available_characters]
        item, ok = QInputDialog.getItem(self, "Add Participant", "Select character:", items, 0, False)
        
        if ok and item:
            selected_char = next(c for c in available_characters if str(c.name) == item)
            if self.selected_event and selected_char.id not in [p.value for p in self.selected_event.participant_ids]:
                # Add participant to current event
                self.selected_event.participant_ids.append(selected_char.id)
                self._refresh_participants_list()
            elif not self.selected_event:
                QMessageBox.warning(self, "No Event Selected", "Please select an event first.")
    
    def _remove_participant(self):
        """Remove selected participant."""
        current_row = self.participants_list.currentRow()
        if current_row >= 0 and self.selected_event:
            self.selected_event.participant_ids.pop(current_row)
            self._refresh_participants_list()
    
    def _add_event(self):
        """Add a new event."""
        try:
            world_id = EntityId(self.world_combo.currentData())
            
            # Parse dates
            start_date = datetime.fromisoformat(self.start_date_input.text()).replace(tzinfo=timezone.utc)
            end_date_str = self.end_date_input.text().strip()
            end_date = datetime.fromisoformat(end_date_str).replace(tzinfo=timezone.utc) if end_date_str else None
            
            event = Event.create(
                tenant_id=self.lore_data.tenant_id,
                world_id=world_id,
                name=self.name_input.text(),
                description=Description(self.description_input.toPlainText()),
                start_date=Timestamp(start_date),
                end_date=Timestamp(end_date) if end_date else None,
                outcome=EventOutcome(self.outcome_combo.currentText()),
                participant_ids=[]  # Start with no participants
            )
            self.lore_data.add_event(event)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Event created successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create event: {e}")
    
    def _update_event(self):
        """Update selected event."""
        if not self.selected_event:
            return
        
        try:
            # Parse dates
            start_date = datetime.fromisoformat(self.start_date_input.text()).replace(tzinfo=timezone.utc)
            end_date_str = self.end_date_input.text().strip()
            end_date = datetime.fromisoformat(end_date_str).replace(tzinfo=timezone.utc) if end_date_str else None
            
            # Create updated event
            updated_event = Event(
                id=self.selected_event.id,
                tenant_id=self.selected_event.tenant_id,
                world_id=EntityId(self.world_combo.currentData()),
                name=self.name_input.text(),
                description=Description(self.description_input.toPlainText()),
                date_range=DateRange(Timestamp(start_date), Timestamp(end_date) if end_date else None),
                outcome=EventOutcome(self.outcome_combo.currentText()),
                participant_ids=self.selected_event.participant_ids.copy(),
                created_at=self.selected_event.created_at,
                updated_at=Timestamp.now(),
                version=self.selected_event.version.increment()
            )
            
            # Replace in list
            idx = self.lore_data.events.index(self.selected_event)
            self.lore_data.events[idx] = updated_event
            
            self.refresh()
            QMessageBox.information(self, "Success", "Event updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update event: {e}")
    
    def _delete_event(self):
        """Delete selected event."""
        if not self.selected_event:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{self.selected_event.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.lore_data.events.remove(self.selected_event)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Event deleted successfully!")
    
    def _clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.description_input.clear()
        self.start_date_input.clear()
        self.end_date_input.clear()
        self.participants_list.clear()
        self.selected_event = None


class ImprovementsTab(QWidget):
    """Tab for managing improvements."""
    
    def __init__(self, lore_data: LoreData):
        super().__init__()
        self.lore_data = lore_data
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Improvements")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Improvements table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Entity", "Suggestion", "Status", "Created"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.table)
        
        # Form
        form_group = QGroupBox("Improvement Details")
        form_layout = QFormLayout()
        
        self.entity_type_combo = QComboBox()
        self.entity_type_combo.addItems(["world", "character", "event"])
        self.entity_type_combo.currentTextChanged.connect(self._on_entity_type_changed)
        
        self.entity_combo = QComboBox()
        self.suggestion_input = QTextEdit()
        self.suggestion_input.setMaximumHeight(100)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["proposed", "approved", "applied", "rejected"])
        
        form_layout.addRow("Entity Type:", self.entity_type_combo)
        form_layout.addRow("Entity:", self.entity_combo)
        form_layout.addRow("Suggestion:", self.suggestion_input)
        form_layout.addRow("Status:", self.status_combo)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Propose Improvement")
        self.add_btn.clicked.connect(self._add_improvement)
        
        self.update_btn = QPushButton("Update Status")
        self.update_btn.clicked.connect(self._update_improvement)
        self.update_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("Delete Improvement")
        self.delete_btn.clicked.connect(self._delete_improvement)
        self.delete_btn.setEnabled(False)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.selected_improvement: Optional[Improvement] = None
        self._update_entity_combo()
    
    def _on_entity_type_changed(self):
        """Handle entity type change."""
        self._update_entity_combo()
    
    def _update_entity_combo(self):
        """Update entity combo based on selected type."""
        entity_type = self.entity_type_combo.currentText()
        self.entity_combo.clear()
        
        if entity_type == "world":
            for world in self.lore_data.worlds:
                self.entity_combo.addItem(f"World: {world.name}", (entity_type, world.id.value))
        elif entity_type == "character":
            for character in self.lore_data.characters:
                world = self.lore_data.get_world_by_id(character.world_id)
                world_name = world.name if world else "Unknown"
                self.entity_combo.addItem(f"Character: {character.name} ({world_name})", (entity_type, character.id.value))
        elif entity_type == "event":
            for event in self.lore_data.events:
                world = self.lore_data.get_world_by_id(event.world_id)
                world_name = world.name if world else "Unknown"
                self.entity_combo.addItem(f"Event: {event.name} ({world_name})", (entity_type, event.id.value))
    
    def refresh(self):
        """Refresh the improvements table."""
        self.table.setRowCount(0)
        
        for improvement in self.lore_data.improvements:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Find entity name
            entity_name = self._get_entity_name(improvement.entity_type, improvement.entity_id)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(improvement.id.value)))
            self.table.setItem(row, 1, QTableWidgetItem(entity_name))
            self.table.setItem(row, 2, QTableWidgetItem(improvement.suggestion[:50] + "..."))
            self.table.setItem(row, 3, QTableWidgetItem(improvement.status.value))
            self.table.setItem(row, 4, QTableWidgetItem(improvement.created_at.value.strftime("%Y-%m-%d")))
        
        self.table.resizeColumnsToContents()
    
    def _get_entity_name(self, entity_type: EntityType, entity_id: EntityId) -> str:
        """Get display name for entity."""
        if entity_type.value == "world":
            world = self.lore_data.get_world_by_id(entity_id)
            return f"World: {world.name}" if world else "Unknown World"
        elif entity_type.value == "character":
            character = next((c for c in self.lore_data.characters if c.id == entity_id), None)
            return f"Character: {character.name}" if character else "Unknown Character"
        elif entity_type.value == "event":
            event = next((e for e in self.lore_data.events if e.id == entity_id), None)
            return f"Event: {event.name}" if event else "Unknown Event"
        return "Unknown"
    
    def _on_selection_changed(self):
        """Handle improvement selection."""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            improvement_id = EntityId(int(self.table.item(row, 0).text()))
            self.selected_improvement = next((i for i in self.lore_data.improvements if i.id == improvement_id), None)
            
            if self.selected_improvement:
                # Update form
                entity_type_idx = self.entity_type_combo.findText(self.selected_improvement.entity_type.value)
                if entity_type_idx >= 0:
                    self.entity_type_combo.setCurrentIndex(entity_type_idx)
                    self._update_entity_combo()
                
                # Find entity in combo
                for i in range(self.entity_combo.count()):
                    entity_data = self.entity_combo.itemData(i)
                    if entity_data and entity_data[1] == self.selected_improvement.entity_id.value:
                        self.entity_combo.setCurrentIndex(i)
                        break
                
                self.suggestion_input.setPlainText(self.selected_improvement.suggestion)
                self.status_combo.setCurrentText(self.selected_improvement.status.value)
                
                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
        else:
            self.selected_improvement = None
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
    
    def _add_improvement(self):
        """Add a new improvement."""
        try:
            entity_data = self.entity_combo.currentData()
            if not entity_data:
                QMessageBox.warning(self, "No Entity", "Please select an entity.")
                return
            
            entity_type, entity_id = entity_data
            
            improvement = Improvement.propose(
                tenant_id=self.lore_data.tenant_id,
                entity_type=EntityType(entity_type),
                entity_id=EntityId(entity_id),
                suggestion=self.suggestion_input.toPlainText(),
                git_commit_hash=__import__('src.domain.value_objects.common', fromlist=['GitCommitHash']).GitCommitHash("temp_commit_hash")
            )
            self.lore_data.add_improvement(improvement)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Improvement proposed successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to propose improvement: {e}")
    
    def _update_improvement(self):
        """Update selected improvement."""
        if not self.selected_improvement:
            return
        
        try:
            new_status = __import__('src.domain.value_objects.common', fromlist=['ImprovementStatus']).ImprovementStatus(self.status_combo.currentText())
            
            # Apply status transition
            if new_status.value == "approved" and self.selected_improvement.status.value == "proposed":
                self.selected_improvement.approve()
            elif new_status.value == "applied" and self.selected_improvement.status.value == "approved":
                self.selected_improvement.apply()
            elif new_status.value == "rejected":
                self.selected_improvement.reject()
            
            self.refresh()
            QMessageBox.information(self, "Success", "Improvement updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update improvement: {e}")
    
    def _delete_improvement(self):
        """Delete selected improvement."""
        if not self.selected_improvement:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete this improvement?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.lore_data.improvements.remove(self.selected_improvement)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Improvement deleted successfully!")
    
    def _clear_form(self):
        """Clear the form."""
        self.suggestion_input.clear()
        self.selected_improvement = None


class ItemsTab(QWidget):
    """Enhanced tab for managing items with improved UX."""

    item_selected = pyqtSignal(EntityId)

    def __init__(self, lore_data: LoreData):
        super().__init__()
        self.lore_data = lore_data
        self.selected_item: Optional[Item] = None
        self.all_items: List[Item] = []  # Store all items for filtering
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the enhanced user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        # Filter bar
        filter_layout = QHBoxLayout()
        filter_label = QLabel("🔍 Filter:")
        filter_label.setStyleSheet("color: #ddd; font-weight: bold;")
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter items by name, type, or description...")
        self.filter_input.textChanged.connect(self._apply_filter)

        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types", None)
        for item_type in ItemType:
            self.type_filter.addItem(f"{item_type.value}", item_type)
        self.type_filter.currentIndexChanged.connect(self._apply_filter)

        self.rarity_filter = QComboBox()
        self.rarity_filter.addItem("All Rarities", None)
        self.rarity_filter.addItem("No Rarity", "none")
        for rarity in Rarity:
            self.rarity_filter.addItem(f"{rarity.value}", rarity)
        self.rarity_filter.currentIndexChanged.connect(self._apply_filter)

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.type_filter)
        filter_layout.addWidget(QLabel("Rarity:"))
        filter_layout.addWidget(self.rarity_filter)
        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left side - Table and buttons
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_widget.setLayout(left_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Name", "Type", "Rarity", "Description"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.itemSelectionChanged.connect(self._on_item_selected)
        self.table.setStyleSheet("""
            QTableWidget {
                selection-background-color: #4a6cd4;
                alternate-background-color: #2a2a2a;
            }
        """)

        # Buttons with icons and tooltips
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("➕ Add Item")
        self.add_btn.clicked.connect(self._add_item)
        self.add_btn.setToolTip("Create a new item (Ctrl+N)")
        self.add_btn.setShortcut("Ctrl+N")

        self.edit_btn = QPushButton("✏️ Edit Item")
        self.edit_btn.clicked.connect(self._edit_item)
        self.edit_btn.setEnabled(False)
        self.edit_btn.setToolTip("Edit the selected item (Ctrl+E)")
        self.edit_btn.setShortcut("Ctrl+E")

        self.delete_btn = QPushButton("🗑️ Delete Item")
        self.delete_btn.clicked.connect(self._delete_item)
        self.delete_btn.setEnabled(False)
        self.delete_btn.setToolTip("Delete the selected item (Delete)")
        self.delete_btn.setShortcut("Delete")

        self.duplicate_btn = QPushButton("📋 Duplicate")
        self.duplicate_btn.clicked.connect(self._duplicate_item)
        self.duplicate_btn.setEnabled(False)
        self.duplicate_btn.setToolTip("Create a copy of the selected item")

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.duplicate_btn)
        button_layout.addStretch()

        left_layout.addWidget(self.table)
        left_layout.addLayout(button_layout)

        # Right side - Form
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_widget.setLayout(right_layout)

        form_group = QGroupBox("📝 Item Details")
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)

        self.world_combo = QComboBox()
        self.world_combo.addItem("🏠 Select World...", None)
        self.world_combo.setToolTip("Choose which world this item belongs to")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter item name...")
        self.name_input.setToolTip("The name of your item")

        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(120)
        self.description_input.setPlaceholderText("Describe your item in detail...")
        self.description_input.setToolTip("Detailed description of the item")

        self.type_combo = QComboBox()
        self.type_combo.setToolTip("What type of item is this?")
        for item_type in ItemType:
            self.type_combo.addItem(f"{item_type.value}", item_type)

        self.rarity_combo = QComboBox()
        self.rarity_combo.addItem("✨ No Rarity", None)
        self.rarity_combo.setToolTip("How rare is this item?")
        for rarity in Rarity:
            self.rarity_combo.addItem(f"{rarity.value}", rarity)

        form_layout.addRow("🌍 World:", self.world_combo)
        form_layout.addRow("📛 Name:", self.name_input)
        form_layout.addRow("🏷️ Type:", self.type_combo)
        form_layout.addRow("💎 Rarity:", self.rarity_combo)
        form_layout.addRow("📖 Description:", self.description_input)

        form_group.setLayout(form_layout)
        right_layout.addWidget(form_group)

        # Action buttons
        action_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self._save_item)
        self.save_btn.setEnabled(False)
        self.save_btn.setToolTip("Save the item (Ctrl+S)")
        self.save_btn.setShortcut("Ctrl+S")

        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self._cancel_edit)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setToolTip("Cancel editing (Esc)")
        self.cancel_btn.setShortcut("Esc")

        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.cancel_btn)
        action_layout.addStretch()

        right_layout.addLayout(action_layout)
        right_layout.addStretch()

        # Context menu for table
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        left_layout.addWidget(self.table)
        left_layout.addLayout(button_layout)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 400])  # Default split ratio

        # ... existing code ...

    def _show_context_menu(self, position):
        """Show context menu for table."""
        if not self.table.itemAt(position):
            return

        menu = QMenu()

        edit_action = menu.addAction("✏️ Edit Item")
        edit_action.triggered.connect(self._edit_item)

        duplicate_action = menu.addAction("📋 Duplicate Item")
        duplicate_action.triggered.connect(self._duplicate_item)

        menu.addSeparator()

        delete_action = menu.addAction("🗑️ Delete Item")
        delete_action.triggered.connect(self._delete_item)

        menu.exec(self.table.mapToGlobal(position))

    def _duplicate_item(self):
        """Duplicate the selected item."""
        if not self.selected_item:
            return

        try:
            # Create duplicate with new name
            duplicate_name = f"{self.selected_item.name} (Copy)"

            # Check if name already exists and add number if needed
            existing_names = [item.name for item in self.lore_data.items]
            counter = 1
            while duplicate_name in existing_names:
                duplicate_name = f"{self.selected_item.name} (Copy {counter})"
                counter += 1

            # Create new item
            duplicate_item = Item.create(
                tenant_id=self.lore_data.tenant_id,
                world_id=self.selected_item.world_id,
                name=duplicate_name,
                description=self.selected_item.description,
                item_type=self.selected_item.item_type,
                rarity=self.selected_item.rarity
            )

            self.lore_data.add_item(duplicate_item)
            self.refresh()

            QMessageBox.information(
                self, "Success",
                f"Item duplicated successfully as '{duplicate_name}'!"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to duplicate item: {e}")
    
    def refresh(self):
        """Refresh the table with current data."""
        self.all_items = self.lore_data.items.copy()
        self._apply_filter()

        # Update world combo
        self.world_combo.clear()
        self.world_combo.addItem("🏠 Select World...", None)
        for world in self.lore_data.worlds:
            self.world_combo.addItem(f"🌍 {world.name}", world.id)

    def filter_items(self, search_text: str):
        """Filter items based on search text (called from main window)."""
        self.filter_input.setText(search_text)

    def _apply_filter(self):
        """Apply current filters to the table."""
        search_text = self.filter_input.text().lower()
        type_filter = self.type_filter.currentData()
        rarity_filter = self.rarity_filter.currentData()

        filtered_items = []
        for item in self.all_items:
            # Text search
            text_match = (
                search_text in item.name.lower() or
                search_text in str(item.description).lower() or
                search_text in item.item_type.value.lower() or
                (item.rarity and search_text in item.rarity.value.lower())
            ) if search_text else True

            # Type filter
            type_match = (item.item_type == type_filter) if type_filter else True

            # Rarity filter
            if rarity_filter == "none":
                rarity_match = item.rarity is None
            elif rarity_filter:
                rarity_match = item.rarity == rarity_filter
            else:
                rarity_match = True

            if text_match and type_match and rarity_match:
                filtered_items.append(item)

        self._populate_table(filtered_items)

    def _populate_table(self, items: List[Item]):
        """Populate table with filtered items."""
        self.table.setRowCount(0)

        for item in items:
            row = self.table.rowCount()
            self.table.insertRow(row)

            world = self.lore_data.get_world_by_id(item.world_id)
            world_name = f"🌍 {world.name}" if world else "🏠 Unknown"

            # Color code rarity
            rarity_text = ""
            if item.rarity:
                rarity_colors = {
                    Rarity.COMMON: "#8B8B8B",
                    Rarity.UNCOMMON: "#4CAF50",
                    Rarity.RARE: "#2196F3",
                    Rarity.EPIC: "#9C27B0",
                    Rarity.LEGENDARY: "#FF9800",
                    Rarity.MYTHIC: "#F44336"
                }
                color = rarity_colors.get(item.rarity, "#FFFFFF")
                rarity_text = f'<span style="color: {color};">{item.rarity.value}</span>'

            self.table.setItem(row, 0, QTableWidgetItem(str(item.id.value if item.id else "")))
            self.table.setItem(row, 1, QTableWidgetItem(world_name))
            self.table.setItem(row, 2, QTableWidgetItem(item.name))
            self.table.setItem(row, 3, QTableWidgetItem(item.item_type.value))
            self.table.setItem(row, 4, QTableWidgetItem(rarity_text if rarity_text else "No Rarity"))
            self.table.setItem(row, 5, QTableWidgetItem(str(item.description)))

            # Make rarity column rich text
            if rarity_text:
                self.table.item(row, 4).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # Resize columns to content
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
    
    def _on_item_selected(self):
        """Handle item selection."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if len(selected_rows) == 1:
            row = list(selected_rows)[0]
            item_id_text = self.table.item(row, 0).text()
            if item_id_text:
                item_id = int(item_id_text)
                self.selected_item = next(
                    (i for i in self.all_items if i.id and i.id.value == item_id),
                    None
                )

                if self.selected_item:
                    self._load_item(self.selected_item)
                    self.edit_btn.setEnabled(True)
                    self.delete_btn.setEnabled(True)
                    self.duplicate_btn.setEnabled(True)
                    self.item_selected.emit(self.selected_item.id)
                else:
                    self._clear_form()
            else:
                self._clear_form()
        else:
            self.selected_item = None
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.duplicate_btn.setEnabled(False)

    def _load_item(self, item: Item):
        """Load item data into form."""
        world_index = self.world_combo.findData(item.world_id)
        if world_index >= 0:
            self.world_combo.setCurrentIndex(world_index)

        self.name_input.setText(item.name)
        self.description_input.setPlainText(str(item.description))

        type_index = self.type_combo.findData(item.item_type)
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)

        if item.rarity:
            rarity_index = self.rarity_combo.findData(item.rarity)
            if rarity_index >= 0:
                self.rarity_combo.setCurrentIndex(rarity_index)
        else:
            self.rarity_combo.setCurrentIndex(0)  # No Rarity

    def _clear_form(self):
        """Clear the form and reset state."""
        self.world_combo.setCurrentIndex(0)
        self.name_input.clear()
        self.description_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.rarity_combo.setCurrentIndex(0)

        self.save_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.add_btn.setEnabled(True)
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.duplicate_btn.setEnabled(False)
        self.selected_item = None

        # Clear table selection
        self.table.clearSelection()

    def _validate_form(self) -> List[str]:
        """Validate form data and return list of errors."""
        errors = []

        world_id = self.world_combo.currentData()
        if not world_id:
            errors.append("Please select a world for the item.")

        name = self.name_input.text().strip()
        if not name:
            errors.append("Item name is required.")
        elif len(name) < 2:
            errors.append("Item name must be at least 2 characters long.")
        elif len(name) > 100:
            errors.append("Item name must be less than 100 characters.")

        description = self.description_input.toPlainText().strip()
        if not description:
            errors.append("Item description is required.")
        elif len(description) < 10:
            errors.append("Item description must be at least 10 characters long.")

        return errors
    
    def _load_item(self, item: Item):
        """Load item data into form."""
        world_index = self.world_combo.findData(item.world_id)
        if world_index >= 0:
            self.world_combo.setCurrentIndex(world_index)
        
        self.name_input.setText(item.name)
        self.description_input.setPlainText(str(item.description))
        
        type_index = self.type_combo.findData(item.item_type)
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)
        
        if item.rarity:
            rarity_index = self.rarity_combo.findData(item.rarity)
            if rarity_index >= 0:
                self.rarity_combo.setCurrentIndex(rarity_index)
        else:
            self.rarity_combo.setCurrentIndex(0)  # No Rarity
    
    def _add_item(self):
        """Start adding a new item."""
        self.selected_item = None
        self._clear_form()
        self.save_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.add_btn.setEnabled(False)
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
    
    def _edit_item(self):
        """Start editing the selected item."""
        if not self.selected_item:
            return
        
        self.save_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.add_btn.setEnabled(False)
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
    
    def _save_item(self):
        """Save the item with enhanced validation."""
        # Validate form
        errors = self._validate_form()
        if errors:
            error_msg = "Please fix the following issues:\n\n" + "\n".join(f"• {error}" for error in errors)
            QMessageBox.warning(self, "Validation Error", error_msg)
            return

        try:
            world_id = self.world_combo.currentData()
            name = self.name_input.text().strip()
            description = self.description_input.toPlainText().strip()
            item_type = self.type_combo.currentData()
            rarity = self.rarity_combo.currentData() if self.rarity_combo.currentIndex() > 0 else None

            if self.selected_item:
                # Update existing item
                self.selected_item.rename(name)
                self.selected_item.update_description(Description(description))
                self.selected_item.change_type(item_type)
                self.selected_item.set_rarity(rarity)

                operation = "updated"
            else:
                # Create new item
                item = Item.create(
                    tenant_id=self.lore_data.tenant_id,
                    world_id=world_id,
                    name=name,
                    description=Description(description),
                    item_type=item_type,
                    rarity=rarity
                )
                self.lore_data.add_item(item)

                operation = "created"

            self.refresh()
            self._clear_form()

            # Show success message with item details
            rarity_text = f" ({rarity.value})" if rarity else ""
            QMessageBox.information(
                self, "Success",
                f"Item '{name}' {operation} successfully!\n\n"
                f"Type: {item_type.value}{rarity_text}\n"
                f"World: {self.world_combo.currentText()}"
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Save Error",
                f"Failed to save item:\n\n{str(e)}\n\n"
                "Please check your input and try again."
            )

    def _delete_item(self):
        """Delete selected item with confirmation."""
        if not self.selected_item:
            return

        # Show detailed confirmation dialog
        world = self.lore_data.get_world_by_id(self.selected_item.world_id)
        world_name = world.name if world else "Unknown World"

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Confirm Delete")
        msg_box.setText("Are you sure you want to delete this item?")
        msg_box.setInformativeText(
            f"Item: {self.selected_item.name}\n"
            f"Type: {self.selected_item.item_type.value}\n"
            f"World: {world_name}\n\n"
            "This action cannot be undone."
        )
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.items.remove(self.selected_item)
                self.refresh()
                self._clear_form()

                QMessageBox.information(
                    self, "Success",
                    f"Item '{self.selected_item.name}' deleted successfully!"
                )

            except Exception as e:
                QMessageBox.critical(
                    self, "Delete Error",
                    f"Failed to delete item:\n\n{str(e)}"
                )

    def _cancel_edit(self):
        """Cancel editing and clear form."""
        self._clear_form()


class QuestsTab(QWidget):
    """Tab for managing quests."""

    quest_selected = pyqtSignal(EntityId)

    def __init__(self, lore_data: LoreData):
        super().__init__()
        self.lore_data = lore_data
        self.selected_quest: Optional[Quest] = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Name", "Status", "Objectives"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_quest_selected)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Quest")
        self.add_btn.clicked.connect(self._add_quest)
        self.edit_btn = QPushButton("Edit Quest")
        self.edit_btn.clicked.connect(self._edit_quest)
        self.edit_btn.setEnabled(False)
        self.delete_btn = QPushButton("Delete Quest")
        self.delete_btn.clicked.connect(self._delete_quest)
        self.delete_btn.setEnabled(False)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()

        layout.addWidget(self.table)
        layout.addLayout(button_layout)

    def refresh(self):
        """Refresh the table with current quests."""
        self.table.setRowCount(0)
        for quest in self.lore_data.quests:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(quest.id.value)))
            world = self.lore_data.get_world_by_id(quest.world_id)
            world_name = str(world.name) if world else "Unknown"
            self.table.setItem(row, 1, QTableWidgetItem(world_name))
            self.table.setItem(row, 2, QTableWidgetItem(quest.name))
            self.table.setItem(row, 3, QTableWidgetItem(quest.status.value))
            objectives_text = "; ".join(quest.objectives[:2])  # Show first 2 objectives
            if len(quest.objectives) > 2:
                objectives_text += "..."
            self.table.setItem(row, 4, QTableWidgetItem(objectives_text))

    def _on_quest_selected(self):
        """Handle quest selection."""
        current_row = self.table.currentRow()
        if current_row >= 0:
            quest_id = int(self.table.item(current_row, 0).text())
            self.selected_quest = next((q for q in self.lore_data.quests if q.id.value == quest_id), None)
            self.edit_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            self.quest_selected.emit(EntityId(quest_id))
        else:
            self.selected_quest = None
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _add_quest(self):
        """Add a new quest."""
        # Simplified: just create a basic quest
        if not self.lore_data.worlds:
            QMessageBox.warning(self, I18N.t('app.title_short', "MythWeave"), I18N.t('warning.no_worlds', "Please create a world first."))
            return
        
        world = self.lore_data.worlds[0]  # Use first world
        
        # Check if there are characters in this world
        characters_in_world = [c for c in self.lore_data.characters if c.world_id == world.id]
        if not characters_in_world:
            QMessageBox.warning(
                self, "No Characters", 
                f"No characters exist in world '{world.name}'. Please create characters first before creating quests."
            )
            return
        
        # Use the first character as a participant
        participant_id = characters_in_world[0].id
        
        quest = Quest(
            id=None,
            tenant_id=self.lore_data.tenant_id,
            world_id=world.id,
            name=I18N.t('new.quest.name', "New Quest"),
            description=Description(I18N.t('new.quest.description', "Quest description")),
            objectives=["Complete objective 1"],
            status=QuestStatus.ACTIVE,
            participant_ids=[participant_id],
            reward_ids=[],
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(1)
        )
        self.lore_data.add_quest(quest)
        self.refresh()

    def _edit_quest(self):
        """Edit selected quest."""
        if self.selected_quest:
            # For now, just show a message
            QMessageBox.information(self, "Edit", f"Editing quest: {self.selected_quest.name}")

    def _delete_quest(self):
        """Delete selected quest."""
        if self.selected_quest:
            self.lore_data.quests.remove(self.selected_quest)
            self.refresh()


class StorylinesTab(QWidget):
    """Tab for managing storylines."""

    storyline_selected = pyqtSignal(EntityId)

    def __init__(self, lore_data: LoreData):
        super().__init__()
        self.lore_data = lore_data
        self.selected_storyline: Optional[Storyline] = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Name", "Type"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_storyline_selected)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Storyline")
        self.add_btn.clicked.connect(self._add_storyline)
        self.edit_btn = QPushButton("Edit Storyline")
        self.edit_btn.clicked.connect(self._edit_storyline)
        self.edit_btn.setEnabled(False)
        self.delete_btn = QPushButton("Delete Storyline")
        self.delete_btn.clicked.connect(self._delete_storyline)
        self.delete_btn.setEnabled(False)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()

        layout.addWidget(self.table)
        layout.addLayout(button_layout)

    def refresh(self):
        """Refresh the table with current storylines."""
        self.table.setRowCount(0)
        for storyline in self.lore_data.storylines:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(storyline.id.value)))
            world = self.lore_data.get_world_by_id(storyline.world_id)
            world_name = str(world.name) if world else "Unknown"
            self.table.setItem(row, 1, QTableWidgetItem(world_name))
            self.table.setItem(row, 2, QTableWidgetItem(storyline.name))
            self.table.setItem(row, 3, QTableWidgetItem(storyline.storyline_type.value))

    def _on_storyline_selected(self):
        """Handle storyline selection."""
        current_row = self.table.currentRow()
        if current_row >= 0:
            storyline_id = int(self.table.item(current_row, 0).text())
            self.selected_storyline = next((s for s in self.lore_data.storylines if s.id.value == storyline_id), None)
            self.edit_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            self.storyline_selected.emit(EntityId(storyline_id))
        else:
            self.selected_storyline = None
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _add_storyline(self):
        """Add a new storyline."""
        if not self.lore_data.worlds:
            QMessageBox.warning(self, I18N.t('app.title_short', "MythWeave"), I18N.t('warning.no_worlds', "Please create a world first."))
            return
        
        world = self.lore_data.worlds[0]  # Use first world
        # Ensure at least one event or quest exists for the new storyline
        events_in_world = [e for e in self.lore_data.events if e.world_id == world.id]
        quests_in_world = [q for q in self.lore_data.quests if q.world_id == world.id]

        if not events_in_world and not quests_in_world:
            QMessageBox.warning(
                self,
                I18N.t('app.title_short', "MythWeave"),
                I18N.t('warning.no_events_or_quests', "Please create at least one Event or Quest in the selected world before adding a Storyline.")
            )
            return

        # Prefer adding an event if available, otherwise attach a quest
        event_ids = [events_in_world[0].id] if events_in_world else []
        quest_ids = [quests_in_world[0].id] if (not event_ids and quests_in_world) else []

        storyline = Storyline(
            id=None,
            tenant_id=self.lore_data.tenant_id,
            world_id=world.id,
            name="New Storyline",
            description=Description(I18N.t('new.storyline.description', "Storyline description")),
            storyline_type=StorylineType.MAIN,
            event_ids=event_ids,
            quest_ids=quest_ids,
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(1)
        )
        self.lore_data.add_storyline(storyline)
        self.refresh()

    def _edit_storyline(self):
        """Edit selected storyline."""
        if self.selected_storyline:
            QMessageBox.information(self, "Edit", f"Editing storyline: {self.selected_storyline.name}")

    def _delete_storyline(self):
        """Delete selected storyline."""
        if self.selected_storyline:
            self.lore_data.storylines.remove(self.selected_storyline)
            self.refresh()


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

        # Auto-load sample data
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
        self.search_input.setPlaceholderText(I18N.t('search.placeholder', "Search across all entities..."))
        self.search_input.textChanged.connect(self._on_search_text_changed)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()

        main_layout.addLayout(search_layout)

        # Tabs with enhanced styling - using list and stacked widget for better readability
        tab_layout = QHBoxLayout()
        
        self.tab_list = QListWidget()
        self.tab_list.setMaximumWidth(220)
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

        # Core Entities
        add_divider("Core Entities")
        add_tab(self.worlds_tab, I18N.t('tab.worlds', "🌍 Worlds"))
        add_tab(self.world_map_tab, I18N.t('tab.world_map', "🗺️ World Map"))
        add_tab(self.characters_tab, I18N.t('tab.characters', "👥 Characters"))
        add_tab(self.events_tab, I18N.t('tab.events', "⚡ Events"))
        add_tab(self.improvements_tab, I18N.t('tab.improvements', "⬆️ Improvements"))
        add_tab(self.items_tab, I18N.t('tab.items', "⚔️ Items"))

        # Game Content
        add_divider("Game Content")
        add_tab(self.quests_tab, I18N.t('tab.quests', "🎯 Quests"))
        add_tab(self.storylines_tab, I18N.t('tab.storylines', "📖 Storylines"))

        # Pages & Stories
        add_divider("Pages & Stories")
        add_tab(self.pages_tab, I18N.t('tab.pages', "📄 Pages"))
        add_tab(self.templates_tab, I18N.t('tab.templates', "📐 Templates"))
        add_tab(self.stories_tab, I18N.t('tab.stories', "📖 Stories"))
        add_tab(self.choices_tab, I18N.t('tab.choices', "🎯 Choices"))
        add_tab(self.flowcharts_tab, I18N.t('tab.flowcharts', "📊 Flowcharts"))

        # Media & Organization
        add_divider("Media & Tags")
        add_tab(self.tags_tab, I18N.t('tab.tags', "🏷️ Tags"))
        add_tab(self.images_tab, I18N.t('tab.images', "🖼️ Images"))

        # GM Tools
        add_divider("GM Tools")
        add_tab(self.handouts_tab, I18N.t('tab.handouts', "📄 Handouts"))
        add_tab(self.inspirations_tab, I18N.t('tab.inspirations', "💡 Inspiration"))
        add_tab(self.maps_tab, I18N.t('tab.maps', "🗺️ Maps"))
        add_tab(self.notes_tab, I18N.t('tab.notes', "📝 Notes"))
        add_tab(self.requirements_tab, I18N.t('tab.requirements', "📋 Requirements"))
        add_tab(self.sessions_tab, I18N.t('tab.sessions', "🎲 Sessions"))
        add_tab(self.tokenboards_tab, I18N.t('tab.tokenboards', "🎛️ Tokenboards"))
        add_tab(self.progression_simulator_tab, I18N.t('tab.progression_simulator', "📈 Progression Simulator"))

        # World Elements
        add_divider("World Elements")
        add_tab(self.location_tab, I18N.t('tab.locations', "📍 Locations"))
        add_tab(self.faction_tab, I18N.t('tab.factions', "⚔️ Factions"))
        add_tab(self.character_relationship_tab, I18N.t('tab.relationships', "💑 Relationships"))
        add_tab(self.shop_tab, I18N.t('tab.shops', "🏪 Shops"))

        # Gacha System
        add_divider("Gacha System")
        add_tab(self.banner_tab, I18N.t('tab.banners', "🎁 Banners"))
        add_tab(self.pity_tab, I18N.t('tab.pity', "🎯 Pity Systems"))
        add_tab(self.pull_tab, I18N.t('tab.pulls', "🎰 Gacha Pulls"))
        add_tab(self.player_profile_tab, I18N.t('tab.players', "👤 Player Profiles"))

        # Resources & Rewards
        add_divider("Resources & Rewards")
        add_tab(self.currency_tab, I18N.t('tab.currencies', "💰 Currencies"))
        add_tab(self.reward_tab, I18N.t('tab.rewards', "🎁 Rewards"))
        add_tab(self.purchase_tab, I18N.t('tab.purchases', "💳 Purchases"))

        # Events & Chains
        add_divider("Events & Chains")
        add_tab(self.event_chain_tab, I18N.t('tab.event_chains', "⛓️ Event Chains"))

        # Faction Management
        add_divider("Faction Management")
        add_tab(self.faction_membership_tab, I18N.t('tab.memberships', "👥 Memberships"))

        # Music System
        add_divider("Music System")
        add_tab(self.music_theme_tab, I18N.t('tab.themes', "🎵 Music Themes"))
        add_tab(self.music_track_tab, I18N.t('tab.tracks', "🎶 Music Tracks"))

        # Set initial selection (skip first divider, select Worlds tab)
        self.tab_list.setCurrentRow(1)

        tab_layout.addWidget(self.tab_list)
        tab_layout.addWidget(self.stacked_widget)

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
        
        # Check for sample data on startup
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
