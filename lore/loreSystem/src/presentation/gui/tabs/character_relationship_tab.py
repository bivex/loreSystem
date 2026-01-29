"""
CharacterRelationshipTab - Tab for managing character relationships
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.entities.character_relationship import CharacterRelationship
from src.domain.value_objects.common import EntityId


class CharacterRelationshipTab(QWidget):
    """Tab for managing character relationships."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_relationship: Optional[CharacterRelationship] = None
        self.all_relationships: List[CharacterRelationship] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("💑 Character Relationships")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Relationships table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Character 1", "Character 2", "Type", "Strength"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Relationship Details")
        form_layout = QFormLayout()

        # Character 1
        self.char1_combo = QComboBox()
        form_layout.addRow("Character 1:", self.char1_combo)

        # Character 2
        self.char2_combo = QComboBox()
        form_layout.addRow("Character 2:", self.char2_combo)

        # Relationship Type
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Friend", "Enemy", "Family", "Lover", "Ally", "Rival", "Mentor", 
            "Apprentice", "Colleague", "Stranger", "Neutral", "Other"
        ])
        form_layout.addRow("Type:", self.type_combo)

        # Strength/Intensity (1-10)
        self.strength_spin = QSpinBox()
        self.strength_spin.setMinimum(1)
        self.strength_spin.setMaximum(10)
        self.strength_spin.setValue(5)
        form_layout.addRow("Strength (1-10):", self.strength_spin)

        # Bidirectional
        self.bidirectional_combo = QComboBox()
        self.bidirectional_combo.addItems(["Yes", "No"])
        form_layout.addRow("Bidirectional:", self.bidirectional_combo)

        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Enter relationship notes/history...")
        self.notes_input.setMaximumHeight(120)
        form_layout.addRow("Notes:", self.notes_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Relationship")
        self.add_btn.clicked.connect(self._add_relationship)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Relationship")
        self.delete_btn.clicked.connect(self._delete_relationship)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        """Refresh the relationships list."""
        try:
            self.all_relationships = self.lore_data.get_character_relationships()
            self._populate_character_combos()
            self._populate_table(self.all_relationships)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load relationships: {str(e)}")

    def _populate_character_combos(self):
        """Populate character combo boxes."""
        try:
            characters = self.lore_data.get_characters()
            for combo in [self.char1_combo, self.char2_combo]:
                combo.clear()
                for char in characters:
                    combo.addItem(getattr(char, 'name', 'Unknown'), char.id)
        except Exception:
            pass

    def _populate_table(self, relationships: List[CharacterRelationship]):
        """Populate the table with relationships."""
        self.table.setRowCount(len(relationships))
        for row, rel in enumerate(relationships):
            self.table.setItem(row, 0, QTableWidgetItem(str(rel.id)))
            char1_id = getattr(rel, 'character_id_1', 'N/A')
            char2_id = getattr(rel, 'character_id_2', 'N/A')
            self.table.setItem(row, 1, QTableWidgetItem(str(char1_id)))
            self.table.setItem(row, 2, QTableWidgetItem(str(char2_id)))
            self.table.setItem(row, 3, QTableWidgetItem(getattr(rel, 'type', 'N/A')))
            self.table.setItem(row, 4, QTableWidgetItem(str(getattr(rel, 'strength', 5))))

    def _on_selection_changed(self):
        """Handle relationship selection change."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_relationship = self.all_relationships[row]
            self._populate_form()
            self.delete_btn.setEnabled(True)
        else:
            self.selected_relationship = None
            self._clear_form()
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate the form with selected relationship data."""
        if not self.selected_relationship:
            return
        char1_id = getattr(self.selected_relationship, 'character_id_1', None)
        char2_id = getattr(self.selected_relationship, 'character_id_2', None)
        
        for i, combo in enumerate([self.char1_combo, self.char2_combo]):
            char_id = char1_id if i == 0 else char2_id
            for j in range(combo.count()):
                if combo.itemData(j) == char_id:
                    combo.setCurrentIndex(j)
                    break

        self.type_combo.setCurrentText(getattr(self.selected_relationship, 'type', 'Friend'))
        self.strength_spin.setValue(getattr(self.selected_relationship, 'strength', 5))
        bidirectional = getattr(self.selected_relationship, 'bidirectional', True)
        self.bidirectional_combo.setCurrentText("Yes" if bidirectional else "No")
        self.notes_input.setPlainText(getattr(self.selected_relationship, 'notes', ''))

    def _clear_form(self):
        """Clear the form."""
        self.char1_combo.setCurrentIndex(0)
        self.char2_combo.setCurrentIndex(0)
        self.type_combo.setCurrentIndex(0)
        self.strength_spin.setValue(5)
        self.bidirectional_combo.setCurrentIndex(0)
        self.notes_input.clear()

    def _add_relationship(self):
        """Add a new relationship."""
        try:
            char1_id = self.char1_combo.currentData()
            char2_id = self.char2_combo.currentData()

            if not char1_id or not char2_id:
                QMessageBox.warning(self, "Warning", "Both characters must be selected")
                return

            if char1_id == char2_id:
                QMessageBox.warning(self, "Warning", "Cannot create relationship between the same character")
                return

            relationship_data = {
                'character_id_1': char1_id,
                'character_id_2': char2_id,
                'type': self.type_combo.currentText(),
                'strength': self.strength_spin.value(),
                'bidirectional': self.bidirectional_combo.currentText() == "Yes",
                'notes': self.notes_input.toPlainText()
            }

            self.lore_data.add_character_relationship(relationship_data)
            QMessageBox.information(self, "Success", "Relationship added successfully!")
            self._clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add relationship: {str(e)}")

    def _delete_relationship(self):
        """Delete the selected relationship."""
        if not self.selected_relationship:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this relationship?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.delete_character_relationship(self.selected_relationship.id)
                QMessageBox.information(self, "Success", "Relationship deleted successfully!")
                self._clear_form()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete relationship: {str(e)}")
