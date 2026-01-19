"""
LocationTab - Tab for managing locations
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.entities.location import Location
from src.domain.value_objects.common import EntityId


class LocationTab(QWidget):
    """Tab for managing locations."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_location: Optional[Location] = None
        self.all_locations: List[Location] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("📍 Locations")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Locations table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Type", "World", "Description"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Location Details")
        form_layout = QFormLayout()

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter location name...")
        form_layout.addRow("Name:", self.name_input)

        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["City", "Town", "Village", "Dungeon", "Forest", "Mountain", "Ocean", "Other"])
        form_layout.addRow("Type:", self.type_combo)

        # World
        self.world_combo = QComboBox()
        form_layout.addRow("World:", self.world_combo)

        # Coordinates (optional)
        self.coords_input = QLineEdit()
        self.coords_input.setPlaceholderText("X, Y (optional)")
        form_layout.addRow("Coordinates:", self.coords_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter location description...")
        self.description_input.setMaximumHeight(120)
        form_layout.addRow("Description:", self.description_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Location")
        self.add_btn.clicked.connect(self._add_location)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Location")
        self.delete_btn.clicked.connect(self._delete_location)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        """Refresh the locations list."""
        try:
            self.all_locations = self.lore_data.get_locations()
            self._populate_world_combo()
            self._populate_table(self.all_locations)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load locations: {str(e)}")

    def _populate_world_combo(self):
        """Populate the world combo box."""
        try:
            worlds = self.lore_data.get_worlds()
            self.world_combo.clear()
            for world in worlds:
                self.world_combo.addItem(getattr(world, 'name', 'Unknown'), world.id)
        except Exception:
            pass

    def _populate_table(self, locations: List[Location]):
        """Populate the table with locations."""
        self.table.setRowCount(len(locations))
        for row, location in enumerate(locations):
            self.table.setItem(row, 0, QTableWidgetItem(str(location.id)))
            self.table.setItem(row, 1, QTableWidgetItem(getattr(location, 'name', 'N/A')))
            self.table.setItem(row, 2, QTableWidgetItem(getattr(location, 'type', 'N/A')))
            world_id = getattr(location, 'world_id', 'N/A')
            self.table.setItem(row, 3, QTableWidgetItem(str(world_id)))
            self.table.setItem(row, 4, QTableWidgetItem(getattr(location, 'description', '')))

    def _on_selection_changed(self):
        """Handle location selection change."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_location = self.all_locations[row]
            self._populate_form()
            self.delete_btn.setEnabled(True)
        else:
            self.selected_location = None
            self._clear_form()
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate the form with selected location data."""
        if not self.selected_location:
            return
        self.name_input.setText(getattr(self.selected_location, 'name', ''))
        self.type_combo.setCurrentText(getattr(self.selected_location, 'type', 'Other'))
        coords = getattr(self.selected_location, 'coordinates', '')
        if coords:
            self.coords_input.setText(f"{coords.get('x', '')}, {coords.get('y', '')}")
        self.description_input.setPlainText(getattr(self.selected_location, 'description', ''))

    def _clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.coords_input.clear()
        self.description_input.clear()

    def _add_location(self):
        """Add a new location."""
        try:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Location name cannot be empty")
                return

            location_data = {
                'name': name,
                'type': self.type_combo.currentText(),
                'world_id': self.world_combo.currentData(),
                'coordinates': self.coords_input.text().strip(),
                'description': self.description_input.toPlainText()
            }

            self.lore_data.add_location(location_data)
            QMessageBox.information(self, "Success", "Location added successfully!")
            self._clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add location: {str(e)}")

    def _delete_location(self):
        """Delete the selected location."""
        if not self.selected_location:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{getattr(self.selected_location, 'name', 'Unknown')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.delete_location(self.selected_location.id)
                QMessageBox.information(self, "Success", "Location deleted successfully!")
                self._clear_form()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete location: {str(e)}")
