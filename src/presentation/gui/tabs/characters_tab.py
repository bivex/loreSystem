"""
CharactersTab - Tab for managing characters.
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QListWidget, QComboBox, QMessageBox
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from src.domain.entities.character import Character
from src.domain.value_objects.common import (
    TenantId, EntityId, CharacterName, Backstory, CharacterStatus, Timestamp
)
from src.domain.value_objects.ability import Ability
from src.presentation.gui.dialogs.ability_dialog import AbilityDialog


class CharactersTab(QWidget):
    """Tab for managing characters."""
    
    def __init__(self, lore_data):
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