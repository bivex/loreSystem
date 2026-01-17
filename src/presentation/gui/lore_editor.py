"""
PyQt6 GUI Application for LoreForge System

Main window with tabs for managing worlds, characters, and events.
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
    QLabel, QMessageBox, QFileDialog, QGroupBox, QListWidget,
    QDialog, QDialogButtonBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from src.domain.entities.world import World
from src.domain.entities.character import Character
from src.domain.entities.event import Event
from src.domain.entities.improvement import Improvement
from src.domain.entities.item import Item
from src.domain.value_objects.common import (
    TenantId, EntityId, WorldName, Description, CharacterName,
    Backstory, Timestamp, EntityType, EventOutcome, CharacterStatus,
    ItemType, Rarity
)
from src.domain.value_objects.ability import Ability, AbilityName, PowerLevel
from src.domain.exceptions import DomainException


class LoreData:
    """In-memory storage for lore entities."""
    
    def __init__(self):
        self.worlds: List[World] = []
        self.characters: List[Character] = []
        self.events: List[Event] = []
        self.improvements: List[Improvement] = []
        self.items: List[Item] = []
        self.tenant_id = TenantId(1)
        self._next_id = 1
    
    def get_next_id(self) -> EntityId:
        """Generate next entity ID."""
        entity_id = EntityId(self._next_id)
        self._next_id += 1
        return entity_id
    
    def add_world(self, world: World) -> World:
        """Add world with generated ID."""
        if world.id is None:
            object.__setattr__(world, 'id', self.get_next_id())
        self.worlds.append(world)
        return world
    
    def add_character(self, character: Character) -> Character:
        """Add character with generated ID."""
        if character.id is None:
            object.__setattr__(character, 'id', self.get_next_id())
        self.characters.append(character)
        return character
    
    def add_event(self, event: Event) -> Event:
        """Add event with generated ID."""
        if event.id is None:
            object.__setattr__(event, 'id', self.get_next_id())
        self.events.append(event)
        return event
    
    def add_improvement(self, improvement: Improvement) -> Improvement:
        """Add improvement with generated ID."""
        if improvement.id is None:
            object.__setattr__(improvement, 'id', self.get_next_id())
        self.improvements.append(improvement)
        return improvement
    
    def add_item(self, item: Item) -> Item:
        """Add item with generated ID."""
        if item.id is None:
            object.__setattr__(item, 'id', self.get_next_id())
        self.items.append(item)
        return item
    
    def get_world_by_id(self, world_id: EntityId) -> Optional[World]:
        """Find world by ID."""
        return next((w for w in self.worlds if w.id == world_id), None)
    
    def get_characters_by_world(self, world_id: EntityId) -> List[Character]:
        """Get all characters in a world."""
        return [c for c in self.characters if c.world_id == world_id]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON."""
        return {
            'worlds': [self._world_to_dict(w) for w in self.worlds],
            'characters': [self._character_to_dict(c) for c in self.characters],
            'events': [self._event_to_dict(e) for e in self.events],
            'improvements': [self._improvement_to_dict(i) for i in self.improvements],
            'items': [self._item_to_dict(i) for i in self.items],
            'next_id': self._next_id
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load from dictionary."""
        self.worlds = [self._dict_to_world(w) for w in data.get('worlds', [])]
        self.characters = [self._dict_to_character(c) for c in data.get('characters', [])]
        self.events = [self._dict_to_event(e) for e in data.get('events', [])]
        self.improvements = [self._dict_to_improvement(i) for i in data.get('improvements', [])]
        self.items = [self._dict_to_item(i) for i in data.get('items', [])]
        self._next_id = data.get('next_id', 1)
    
    @staticmethod
    def _world_to_dict(world: World) -> Dict:
        return {
            'id': world.id.value if world.id else None,
            'name': str(world.name),
            'description': str(world.description),
            'created_at': world.created_at.value.isoformat(),
            'updated_at': world.updated_at.value.isoformat(),
            'version': world.version.value
        }
    
    @staticmethod
    def _dict_to_world(data: Dict) -> World:
        return World(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            name=WorldName(data['name']),
            description=Description(data['description']),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _character_to_dict(character: Character) -> Dict:
        return {
            'id': character.id.value if character.id else None,
            'world_id': character.world_id.value,
            'name': str(character.name),
            'backstory': str(character.backstory),
            'status': character.status.value,
            'abilities': [a.to_dict() for a in character.abilities],
            'created_at': character.created_at.value.isoformat(),
            'updated_at': character.updated_at.value.isoformat(),
            'version': character.version.value
        }
    
    @staticmethod
    def _dict_to_character(data: Dict) -> Character:
        return Character(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=CharacterName(data['name']),
            backstory=Backstory(data['backstory']),
            status=CharacterStatus(data['status']),
            abilities=[Ability.from_dict(a) for a in data['abilities']],
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _event_to_dict(event: Event) -> Dict:
        return {
            'id': event.id.value if event.id else None,
            'world_id': event.world_id.value,
            'name': event.name,
            'description': str(event.description),
            'start_date': event.date_range.start_date.value.isoformat(),
            'end_date': event.date_range.end_date.value.isoformat() if event.date_range.end_date else None,
            'outcome': event.outcome.value,
            'participant_ids': [p.value for p in event.participant_ids],
            'created_at': event.created_at.value.isoformat(),
            'updated_at': event.updated_at.value.isoformat(),
            'version': event.version.value
        }
    
    @staticmethod
    def _dict_to_event(data: Dict) -> Event:
        from src.domain.value_objects.common import DateRange
        return Event(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=data['name'],
            description=Description(data['description']),
            date_range=DateRange(
                Timestamp(datetime.fromisoformat(data['start_date'])),
                Timestamp(datetime.fromisoformat(data['end_date'])) if data['end_date'] else None
            ),
            outcome=EventOutcome(data['outcome']),
            participant_ids=[EntityId(p) for p in data['participant_ids']],
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _improvement_to_dict(improvement: Improvement) -> Dict:
        return {
            'id': improvement.id.value if improvement.id else None,
            'entity_type': improvement.entity_type.value,
            'entity_id': improvement.entity_id.value,
            'suggestion': improvement.suggestion,
            'status': improvement.status.value,
            'git_commit_hash': improvement.git_commit_hash.value,
            'created_at': improvement.created_at.value.isoformat()
        }
    
    @staticmethod
    def _dict_to_improvement(data: Dict) -> Improvement:
        from src.domain.value_objects.common import GitCommitHash
        return Improvement(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            entity_type=EntityType(data['entity_type']),
            entity_id=EntityId(data['entity_id']),
            suggestion=data['suggestion'],
            status=__import__('src.domain.value_objects.common', fromlist=['ImprovementStatus']).ImprovementStatus(data['status']),
            git_commit_hash=GitCommitHash(data['git_commit_hash']),
            created_at=Timestamp(datetime.fromisoformat(data['created_at']))
        )
    
    @staticmethod
    def _item_to_dict(item: Item) -> Dict:
        return {
            'id': item.id.value if item.id else None,
            'world_id': item.world_id.value,
            'name': item.name,
            'description': str(item.description),
            'item_type': item.item_type.value,
            'rarity': item.rarity.value if item.rarity else None,
            'created_at': item.created_at.value.isoformat(),
            'updated_at': item.updated_at.value.isoformat(),
            'version': item.version.value
        }
    
    @staticmethod
    def _dict_to_item(data: Dict) -> Item:
        return Item(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=data['name'],
            description=Description(data['description']),
            item_type=ItemType(data['item_type']),
            rarity=Rarity(data['rarity']) if data['rarity'] else None,
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )


class AbilityDialog(QDialog):
    """Dialog for adding/editing abilities."""
    
    def __init__(self, parent=None, ability: Optional[Ability] = None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Ability")
        self.setModal(True)
        self.ability = ability
        self._setup_ui()
        
        if ability:
            self._load_ability(ability)
    
    def _setup_ui(self):
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.power_input = QSpinBox()
        self.power_input.setRange(1, 10)
        self.power_input.setValue(5)
        
        layout.addRow("Name:", self.name_input)
        layout.addRow("Description:", self.description_input)
        layout.addRow("Power Level (1-10):", self.power_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttons)
        
        self.setLayout(main_layout)
    
    def _load_ability(self, ability: Ability):
        self.name_input.setText(str(ability.name))
        self.description_input.setPlainText(ability.description)
        self.power_input.setValue(ability.power_level.value)
    
    def get_ability(self) -> Optional[Ability]:
        """Get the ability from form data."""
        try:
            return Ability(
                name=AbilityName(self.name_input.text()),
                description=self.description_input.toPlainText(),
                power_level=PowerLevel(self.power_input.value())
            )
        except Exception as e:
            QMessageBox.critical(self, "Validation Error", str(e))
            return None


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
    """Tab for managing items."""
    
    item_selected = pyqtSignal(EntityId)
    
    def __init__(self, lore_data: LoreData):
        super().__init__()
        self.lore_data = lore_data
        self.selected_item: Optional[Item] = None
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Left side - Table
        left_layout = QVBoxLayout()
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Name", "Type", "Rarity", "Description"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_item_selected)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Item")
        self.add_btn.clicked.connect(self._add_item)
        
        self.edit_btn = QPushButton("Edit Item")
        self.edit_btn.clicked.connect(self._edit_item)
        self.edit_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("Delete Item")
        self.delete_btn.clicked.connect(self._delete_item)
        self.delete_btn.setEnabled(False)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        left_layout.addWidget(self.table)
        left_layout.addLayout(button_layout)
        
        # Right side - Form
        right_layout = QVBoxLayout()
        
        form_group = QGroupBox("Item Details")
        form_layout = QFormLayout()
        
        self.world_combo = QComboBox()
        self.world_combo.addItem("Select World...", None)
        for world in self.lore_data.worlds:
            self.world_combo.addItem(str(world.name), world.id)
        
        self.name_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        
        self.type_combo = QComboBox()
        for item_type in ItemType:
            self.type_combo.addItem(item_type.value, item_type)
        
        self.rarity_combo = QComboBox()
        self.rarity_combo.addItem("No Rarity", None)
        for rarity in Rarity:
            self.rarity_combo.addItem(rarity.value, rarity)
        
        form_layout.addRow("World:", self.world_combo)
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Type:", self.type_combo)
        form_layout.addRow("Rarity:", self.rarity_combo)
        form_layout.addRow("Description:", self.description_input)
        
        form_group.setLayout(form_layout)
        right_layout.addWidget(form_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_item)
        self.save_btn.setEnabled(False)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._cancel_edit)
        self.cancel_btn.setEnabled(False)
        
        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.cancel_btn)
        action_layout.addStretch()
        
        right_layout.addLayout(action_layout)
        right_layout.addStretch()
        
        layout.addLayout(left_layout, 2)
        layout.addLayout(right_layout, 1)
    
    def refresh(self):
        """Refresh the table with current data."""
        self.table.setRowCount(0)
        
        for item in self.lore_data.items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            world = self.lore_data.get_world_by_id(item.world_id)
            world_name = str(world.name) if world else "Unknown"
            
            self.table.setItem(row, 0, QTableWidgetItem(str(item.id.value if item.id else "")))
            self.table.setItem(row, 1, QTableWidgetItem(world_name))
            self.table.setItem(row, 2, QTableWidgetItem(item.name))
            self.table.setItem(row, 3, QTableWidgetItem(item.item_type.value))
            self.table.setItem(row, 4, QTableWidgetItem(item.rarity.value if item.rarity else ""))
            self.table.setItem(row, 5, QTableWidgetItem(str(item.description)))
        
        # Update world combo
        self.world_combo.clear()
        self.world_combo.addItem("Select World...", None)
        for world in self.lore_data.worlds:
            self.world_combo.addItem(str(world.name), world.id)
    
    def _on_item_selected(self):
        """Handle item selection."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if len(selected_rows) == 1:
            row = list(selected_rows)[0]
            item_id = int(self.table.item(row, 0).text())
            self.selected_item = next(
                (i for i in self.lore_data.items if i.id and i.id.value == item_id), 
                None
            )
            
            if self.selected_item:
                self._load_item(self.selected_item)
                self.edit_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.item_selected.emit(self.selected_item.id)
            else:
                self.edit_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
        else:
            self.selected_item = None
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
    
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
        """Save the item."""
        try:
            world_id = self.world_combo.currentData()
            if not world_id:
                QMessageBox.warning(self, "Validation Error", "Please select a world.")
                return
            
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Validation Error", "Item name is required.")
                return
            
            description = self.description_input.toPlainText().strip()
            if not description:
                QMessageBox.warning(self, "Validation Error", "Item description is required.")
                return
            
            item_type = self.type_combo.currentData()
            rarity = self.rarity_combo.currentData() if self.rarity_combo.currentIndex() > 0 else None
            
            if self.selected_item:
                # Update existing item
                self.selected_item.rename(name)
                self.selected_item.update_description(Description(description))
                self.selected_item.change_type(item_type)
                self.selected_item.set_rarity(rarity)
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
            
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Item saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save item: {e}")
    
    def _cancel_edit(self):
        """Cancel editing."""
        self._clear_form()
        self.selected_item = None
    
    def _delete_item(self):
        """Delete selected item."""
        if not self.selected_item:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{self.selected_item.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.lore_data.items.remove(self.selected_item)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Item deleted successfully!")
    
    def _clear_form(self):
        """Clear the form."""
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
        self.selected_item = None


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.lore_data = LoreData()
        self.current_file: Optional[Path] = None
        self._setup_ui()
        self.setWindowTitle("LoreForge - Lore Management System")
        self.resize(1200, 800)
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Header
        header = QLabel("🎮 LoreForge Chronicles")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Tabs
        self.tabs = QTabWidget()
        
        self.worlds_tab = WorldsTab(self.lore_data)
        self.characters_tab = CharactersTab(self.lore_data)
        self.events_tab = EventsTab(self.lore_data)
        self.improvements_tab = ImprovementsTab(self.lore_data)
        self.items_tab = ItemsTab(self.lore_data)
        
        self.tabs.addTab(self.worlds_tab, "Worlds")
        self.tabs.addTab(self.characters_tab, "Characters")
        self.tabs.addTab(self.events_tab, "Events")
        self.tabs.addTab(self.improvements_tab, "Improvements")
        self.tabs.addTab(self.items_tab, "Items")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.new_btn = QPushButton("New")
        self.new_btn.clicked.connect(self._new_file)
        
        self.load_btn = QPushButton("Load")
        self.load_btn.clicked.connect(self._load_file)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_file)
        
        self.save_as_btn = QPushButton("Save As")
        self.save_as_btn.clicked.connect(self._save_file_as)
        
        button_layout.addWidget(self.new_btn)
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.save_as_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Connect signals
        self.worlds_tab.world_selected.connect(self._on_world_selected)
    
    def _on_world_selected(self, world_id: EntityId):
        """Handle world selection."""
        self.statusBar().showMessage(f"Selected world ID: {world_id.value}")
    
    def _new_file(self):
        """Create a new lore file."""
        reply = QMessageBox.question(
            self, "New File",
            "This will clear all current data. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.lore_data = LoreData()
            self.worlds_tab.lore_data = self.lore_data
            self.characters_tab.lore_data = self.lore_data
            self.events_tab.lore_data = self.lore_data
            self.improvements_tab.lore_data = self.lore_data
            self.items_tab.lore_data = self.lore_data
            self.current_file = None
            self._refresh_all()
            self.statusBar().showMessage("New file created")
    
    def _load_file(self):
        """Load lore from JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Lore File", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                self.lore_data.from_dict(data)
                self.current_file = Path(file_path)
                self._refresh_all()
                self.statusBar().showMessage(f"Loaded: {file_path}")
                QMessageBox.information(self, "Success", "Lore loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {e}")
    
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
    
    def _refresh_all(self):
        """Refresh all tabs."""
        self.worlds_tab.refresh()
        self.characters_tab.refresh()
        self.events_tab.refresh()
        self.improvements_tab.refresh()
        self.items_tab.refresh()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("LoreForge")
    app.setOrganizationName("LoreForge")
    
    window = MainWindow()
    window.show()
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
