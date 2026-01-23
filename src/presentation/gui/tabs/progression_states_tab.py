"""
ProgressionStatesTab - Tab for viewing character progression states.
"""
from typing import Optional, Dict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLabel, QPushButton, QGroupBox, QMessageBox,
    QTextEdit, QSplitter, QTreeWidget, QTreeWidgetItem, QComboBox
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from src.domain.entities.progression_state import CharacterState
from src.domain.value_objects.common import EntityId
from src.domain.value_objects.progression import CharacterLevel, CharacterClass, ExperiencePoints, StatType, StatValue


class ProgressionStatesTab(QWidget):
    """Tab for viewing character progression states."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Progression States")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Character selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Character:"))

        self.character_combo = QComboBox()
        self.character_combo.currentIndexChanged.connect(self._on_character_changed)
        selector_layout.addWidget(self.character_combo)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        selector_layout.addWidget(self.refresh_btn)

        selector_layout.addStretch()
        layout.addLayout(selector_layout)

        # Splitter for table and details
        splitter = QSplitter()
        layout.addWidget(splitter)

        # Left side - States table
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        # States table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Time Point", "Level", "Class", "Experience", "Stats Count"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        left_layout.addWidget(self.table)

        # Right side - State details
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        # State details
        details_group = QGroupBox("State Details")
        details_layout = QFormLayout()

        self.state_time_label = QLabel()
        self.state_level_label = QLabel()
        self.state_class_label = QLabel()
        self.state_experience_label = QLabel()
        self.state_created_label = QLabel()

        details_layout.addRow("Time Point:", self.state_time_label)
        details_layout.addRow("Level:", self.state_level_label)
        details_layout.addRow("Class:", self.state_class_label)
        details_layout.addRow("Experience:", self.state_experience_label)
        details_layout.addRow("Created At:", self.state_created_label)

        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)

        # Stats display
        stats_group = QGroupBox("Character Stats")
        stats_layout = QVBoxLayout()

        self.stats_tree = QTreeWidget()
        self.stats_tree.setHeaderLabel("Stats")
        stats_layout.addWidget(self.stats_tree)

        stats_group.setLayout(stats_layout)
        right_layout.addWidget(stats_group)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 400])

        self.setLayout(layout)

        self.selected_state: Optional[CharacterState] = None
        self.selected_character_id: Optional[EntityId] = None

    def refresh(self):
        """Refresh the states table and character combo."""
        # Populate character combo
        self.character_combo.clear()
        self.character_combo.addItem("Select Character", None)
        for character in self.lore_data.characters:
            self.character_combo.addItem(str(character.name), character.id)

        # Refresh states table if character is selected
        if self.selected_character_id:
            self._refresh_states_table()

    def _refresh_states_table(self):
        """Refresh the states table for selected character."""
        self.table.setRowCount(0)

        if not self.selected_character_id:
            return

        # Get states for this character
        character_states = []
        if hasattr(self.lore_data, 'get_character_states'):
            character_states = self.lore_data.get_character_states(self.selected_character_id)
        else:
            # Fallback: filter from all states
            character_states = [s for s in getattr(self.lore_data, 'character_states', [])
                              if s.character_id == self.selected_character_id]

        for state in sorted(character_states, key=lambda s: s.time_point, reverse=True):
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(state.time_point)))
            self.table.setItem(row, 1, QTableWidgetItem(str(state.level) if state.level else "N/A"))
            self.table.setItem(row, 2, QTableWidgetItem(str(state.character_class) if state.character_class else "N/A"))
            self.table.setItem(row, 3, QTableWidgetItem(str(state.experience) if state.experience else "N/A"))
            self.table.setItem(row, 4, QTableWidgetItem(str(len(state.stats))))

        self.table.resizeColumnsToContents()

    def _on_character_changed(self):
        """Handle character selection change."""
        self.selected_character_id = self.character_combo.currentData()
        if self.selected_character_id:
            self._refresh_states_table()
        else:
            self.table.setRowCount(0)

    def _on_selection_changed(self):
        """Handle state selection."""
        selected_items = self.table.selectedItems()
        if selected_items and self.selected_character_id:
            row = selected_items[0].row()

            # Get states for this character
            character_states = []
            if hasattr(self.lore_data, 'get_character_states'):
                character_states = self.lore_data.get_character_states(self.selected_character_id)
            else:
                character_states = [s for s in getattr(self.lore_data, 'character_states', [])
                                  if s.character_id == self.selected_character_id]

            sorted_states = sorted(character_states, key=lambda s: s.time_point, reverse=True)
            if row < len(sorted_states):
                self.selected_state = sorted_states[row]

                if self.selected_state:
                    self.state_time_label.setText(str(self.selected_state.time_point))
                    self.state_level_label.setText(str(self.selected_state.level) if self.selected_state.level else "N/A")
                    self.state_class_label.setText(str(self.selected_state.character_class) if self.selected_state.character_class else "N/A")
                    self.state_experience_label.setText(str(self.selected_state.experience) if self.selected_state.experience else "N/A")
                    self.state_created_label.setText(str(self.selected_state.created_at))

                    self._update_stats_tree()
        else:
            self.selected_state = None

    def _update_stats_tree(self):
        """Update the stats tree."""
        self.stats_tree.clear()

        if not self.selected_state:
            return

        # Stats
        if self.selected_state.stats:
            for stat_type, stat_value in sorted(self.selected_state.stats.items()):
                QTreeWidgetItem(self.stats_tree, [f"{stat_type}: {stat_value}"])
        else:
            QTreeWidgetItem(self.stats_tree, ["No stats recorded"])

        self.stats_tree.expandAll()