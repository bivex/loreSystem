"""
ProgressionEventsTab - Tab for viewing progression events.
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLabel, QPushButton, QGroupBox, QMessageBox,
    QTextEdit, QSplitter, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from src.domain.entities.progression_event import ProgressionEvent
from src.domain.value_objects.common import EntityId
from src.domain.value_objects.progression import EventType


class ProgressionEventsTab(QWidget):
    """Tab for viewing progression events."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Progression Events")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and details
        splitter = QSplitter()
        layout.addWidget(splitter)

        # Left side - Events table
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        # Events table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Time", "Event Type", "Character", "Description", "Effects Count"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        left_layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)

        self.view_character_btn = QPushButton("View Character Events")
        self.view_character_btn.clicked.connect(self._filter_by_character)
        self.view_character_btn.setEnabled(False)

        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.view_character_btn)
        button_layout.addStretch()

        left_layout.addLayout(button_layout)

        # Right side - Event details
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        # Event details
        details_group = QGroupBox("Event Details")
        details_layout = QFormLayout()

        self.event_id_label = QLabel()
        self.event_type_label = QLabel()
        self.character_id_label = QLabel()
        self.time_range_label = QLabel()
        self.created_at_label = QLabel()

        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMaximumHeight(80)

        details_layout.addRow("Event ID:", self.event_id_label)
        details_layout.addRow("Event Type:", self.event_type_label)
        details_layout.addRow("Character ID:", self.character_id_label)
        details_layout.addRow("Time Range:", self.time_range_label)
        details_layout.addRow("Created At:", self.created_at_label)
        details_layout.addRow("Description:", self.description_text)

        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)

        # Reasons and Effects
        reasons_group = QGroupBox("Reasons & Effects")
        reasons_layout = QVBoxLayout()

        self.reasons_tree = QTreeWidget()
        self.reasons_tree.setHeaderLabel("Reasons & Effects")
        reasons_layout.addWidget(self.reasons_tree)

        reasons_group.setLayout(reasons_layout)
        right_layout.addWidget(reasons_group)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 400])

        self.setLayout(layout)

        self.selected_event: Optional[ProgressionEvent] = None
        self.filtered_character_id: Optional[EntityId] = None

    def refresh(self):
        """Refresh the events table."""
        self.table.setRowCount(0)

        events = self.lore_data.progression_events
        if self.filtered_character_id:
            events = [e for e in events if e.character_id == self.filtered_character_id]

        for event in sorted(events, key=lambda e: e.from_time, reverse=True):
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Get character name
            character_name = "Unknown"
            if hasattr(self.lore_data, 'get_character_by_id'):
                character = self.lore_data.get_character_by_id(event.character_id)
                if character:
                    character_name = str(character.name)

            self.table.setItem(row, 0, QTableWidgetItem(str(event.from_time)))
            self.table.setItem(row, 1, QTableWidgetItem(event.event_type.value))
            self.table.setItem(row, 2, QTableWidgetItem(character_name))
            self.table.setItem(row, 3, QTableWidgetItem(event.description[:50] + "..." if len(event.description) > 50 else event.description))
            self.table.setItem(row, 4, QTableWidgetItem(str(len(event.effects))))

        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle event selection."""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            # Find the event
            events = self.lore_data.progression_events
            if self.filtered_character_id:
                events = [e for e in events if e.character_id == self.filtered_character_id]

            sorted_events = sorted(events, key=lambda e: e.from_time, reverse=True)
            if row < len(sorted_events):
                self.selected_event = sorted_events[row]

                if self.selected_event:
                    self.event_id_label.setText(self.selected_event.id)
                    self.event_type_label.setText(self.selected_event.event_type.value)
                    self.character_id_label.setText(str(self.selected_event.character_id.value))
                    self.time_range_label.setText(f"{self.selected_event.from_time} → {self.selected_event.to_time}")
                    self.created_at_label.setText(str(self.selected_event.created_at))
                    self.description_text.setPlainText(self.selected_event.description)

                    self._update_reasons_tree()
                    self.view_character_btn.setEnabled(True)
        else:
            self.selected_event = None
            self.view_character_btn.setEnabled(False)

    def _update_reasons_tree(self):
        """Update the reasons and effects tree."""
        self.reasons_tree.clear()

        if not self.selected_event:
            return

        # Reasons
        if self.selected_event.reasons:
            reasons_item = QTreeWidgetItem(["Reasons"])
            for reason in self.selected_event.reasons:
                QTreeWidgetItem(reasons_item, [str(reason)])
            self.reasons_tree.addTopLevelItem(reasons_item)

        # Effects
        if self.selected_event.effects:
            effects_item = QTreeWidgetItem(["Effects"])
            for effect_key, effect_value in self.selected_event.effects.items():
                QTreeWidgetItem(effects_item, [f"{effect_key}: {effect_value}"])
            self.reasons_tree.addTopLevelItem(effects_item)

        self.reasons_tree.expandAll()

    def _filter_by_character(self):
        """Filter events by the selected character's ID."""
        if self.selected_event:
            self.filtered_character_id = self.selected_event.character_id
            self.refresh()
            # Update title to show filtering
            self.setWindowTitle(f"Progression Events - Character {self.selected_event.character_id.value}")

    def show_all_events(self):
        """Show all events (clear filter)."""
        self.filtered_character_id = None
        self.refresh()
        self.setWindowTitle("Progression Events")