"""
WorldMapTab - Tab for viewing the entire world map from above.
"""
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QSplitter, QListWidget, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.entities.world import World
from src.domain.entities.map import Map
from src.domain.value_objects.common import EntityId


class WorldMapTab(QWidget):
    """Tab for viewing the world map overview."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_world: Optional[World] = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("🗺️ World Map Overview")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for worlds and map details
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Worlds list
        worlds_widget = QWidget()
        worlds_layout = QVBoxLayout()

        worlds_label = QLabel("Worlds")
        worlds_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        worlds_layout.addWidget(worlds_label)

        self.worlds_list = QListWidget()
        self.worlds_list.itemSelectionChanged.connect(self._on_world_selection_changed)
        worlds_layout.addWidget(self.worlds_list)

        worlds_widget.setLayout(worlds_layout)
        splitter.addWidget(worlds_widget)

        # Right panel: Map details
        details_widget = QWidget()
        details_layout = QVBoxLayout()

        details_label = QLabel("Map Details")
        details_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        details_layout.addWidget(details_label)

        # Map info
        self.map_info = QTextEdit()
        self.map_info.setReadOnly(True)
        self.map_info.setMaximumHeight(200)
        details_layout.addWidget(self.map_info)

        # Locations table
        locations_label = QLabel("Locations")
        locations_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        details_layout.addWidget(locations_label)

        self.locations_table = QTableWidget()
        self.locations_table.setColumnCount(3)
        self.locations_table.setHorizontalHeaderLabels(["Name", "Type", "Description"])
        details_layout.addWidget(self.locations_table)

        details_widget.setLayout(details_layout)
        splitter.addWidget(details_widget)

        splitter.setSizes([300, 700])
        layout.addWidget(splitter)

        self.setLayout(layout)

    def refresh(self):
        """Refresh the worlds list."""
        self.worlds_list.clear()
        for world in self.lore_data.worlds:
            self.worlds_list.addItem(f"{world.name} (ID: {world.id.value})")

    def _on_world_selection_changed(self):
        """Handle world selection change."""
        current_item = self.worlds_list.currentItem()
        if not current_item:
            return

        # Extract world ID from item text
        text = current_item.text()
        world_id_str = text.split("(ID: ")[1].rstrip(")")
        world_id = EntityId(world_id_str)

        world = self.lore_data.get_world_by_id(world_id)
        if world:
            self.selected_world = world
            self._update_map_details()

    def _update_map_details(self):
        """Update the map details for the selected world."""
        if not self.selected_world:
            self.map_info.clear()
            self.locations_table.setRowCount(0)
            return

        # Map info
        info_text = f"World: {self.selected_world.name}\n"
        info_text += f"Description: {self.selected_world.description}\n"
        info_text += f"Version: {self.selected_world.version}\n"
        self.map_info.setPlainText(info_text)

        # Locations (we'll show characters, events, etc. as locations)
        self.locations_table.setRowCount(0)

        # Add characters as locations
        for char in self.lore_data.characters:
            if char.world_id == self.selected_world.id:
                row = self.locations_table.rowCount()
                self.locations_table.insertRow(row)
                self.locations_table.setItem(row, 0, QTableWidgetItem(char.name))
                self.locations_table.setItem(row, 1, QTableWidgetItem("Character"))
                self.locations_table.setItem(row, 2, QTableWidgetItem(char.description[:50] + "..." if len(char.description) > 50 else char.description))

        # Add events
        for event in self.lore_data.events:
            if event.world_id == self.selected_world.id:
                row = self.locations_table.rowCount()
                self.locations_table.insertRow(row)
                self.locations_table.setItem(row, 0, QTableWidgetItem(event.name))
                self.locations_table.setItem(row, 1, QTableWidgetItem("Event"))
                self.locations_table.setItem(row, 2, QTableWidgetItem(event.description[:50] + "..." if len(event.description) > 50 else event.description))

        # Add items
        for item in self.lore_data.items:
            if item.world_id == self.selected_world.id:
                row = self.locations_table.rowCount()
                self.locations_table.insertRow(row)
                self.locations_table.setItem(row, 0, QTableWidgetItem(item.name))
                self.locations_table.setItem(row, 1, QTableWidgetItem("Item"))
                self.locations_table.setItem(row, 2, QTableWidgetItem(item.description[:50] + "..." if len(item.description) > 50 else item.description))