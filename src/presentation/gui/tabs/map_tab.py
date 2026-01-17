"""
MapTab - Tab for managing world maps
"""
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.entities.map import Map
from src.domain.value_objects.common import TenantId, EntityId


class MapTab(QWidget):
    """Tab for managing world maps."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_map: Optional[Map] = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("🗺️ Maps")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Maps table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Name", "Images", "Locations", "Interactive", "Updated"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Map Details")
        form_layout = QFormLayout()

        # World selection
        self.world_combo = QComboBox()
        form_layout.addRow("World:", self.world_combo)

        # Map name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter map name...")
        form_layout.addRow("Name:", self.name_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Map description...")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)

        # Image IDs
        self.images_input = QLineEdit()
        self.images_input.setPlaceholderText("image_id1, image_id2 (comma-separated)")
        form_layout.addRow("Image IDs:", self.images_input)

        # Location IDs
        self.locations_input = QLineEdit()
        self.locations_input.setPlaceholderText("location_id1, location_id2 (comma-separated)")
        form_layout.addRow("Location IDs:", self.locations_input)

        # Scale
        self.scale_input = QLineEdit()
        self.scale_input.setPlaceholderText("e.g., '1 inch = 5 miles' (optional)")
        form_layout.addRow("Scale:", self.scale_input)

        # Interactive checkbox
        self.interactive_check = QCheckBox("This map supports interactive elements")
        form_layout.addRow("", self.interactive_check)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Map")
        self.add_btn.clicked.connect(self._add_map)

        self.update_btn = QPushButton("Update Map")
        self.update_btn.clicked.connect(self._update_map)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Map")
        self.delete_btn.clicked.connect(self._delete_map)
        self.delete_btn.setEnabled(False)

        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.clicked.connect(self._clear_form)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        """Refresh the maps table and combo boxes."""
        # Update worlds combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(f"{world.name.value}", world.id.value)

        # Update maps table
        self.table.setRowCount(0)
        for map_obj in self.lore_data.maps:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(map_obj.id.value) if map_obj.id else ""))

            # World
            world_name = "Unknown"
            for world in self.lore_data.worlds:
                if world.id == map_obj.world_id:
                    world_name = world.name.value
                    break
            self.table.setItem(row, 1, QTableWidgetItem(world_name))

            # Name
            self.table.setItem(row, 2, QTableWidgetItem(map_obj.name))

            # Images count
            self.table.setItem(row, 3, QTableWidgetItem(str(len(map_obj.image_ids))))

            # Locations count
            self.table.setItem(row, 4, QTableWidgetItem(str(len(map_obj.location_ids))))

            # Interactive
            self.table.setItem(row, 5, QTableWidgetItem("✅" if map_obj.is_interactive else ""))

            # Updated
            self.table.setItem(row, 6, QTableWidgetItem(map_obj.updated_at.value.strftime("%Y-%m-%d %H:%M")))

        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle map selection changes."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if len(selected_rows) == 1:
            row = list(selected_rows)[0]
            map_id = int(self.table.item(row, 0).text())
            self.selected_map = next((m for m in self.lore_data.maps if m.id and m.id.value == map_id), None)
            if self.selected_map:
                self._populate_form()
                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
            else:
                self._clear_form()
                self.update_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
        else:
            self.selected_map = None
            self._clear_form()
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate form with selected map data."""
        if not self.selected_map:
            return

        # Set world
        for i in range(self.world_combo.count()):
            if self.world_combo.itemData(i) == self.selected_map.world_id.value:
                self.world_combo.setCurrentIndex(i)
                break

        # Set fields
        self.name_input.setText(self.selected_map.name)
        self.description_input.setText(self.selected_map.description or "")
        self.images_input.setText(", ".join(str(img_id.value) for img_id in self.selected_map.image_ids))
        self.locations_input.setText(", ".join(str(loc_id.value) for loc_id in self.selected_map.location_ids))
        self.scale_input.setText(self.selected_map.scale or "")
        self.interactive_check.setChecked(self.selected_map.is_interactive)

    def _clear_form(self):
        """Clear all form fields."""
        self.name_input.clear()
        self.description_input.clear()
        self.images_input.clear()
        self.locations_input.clear()
        self.scale_input.clear()
        self.interactive_check.setChecked(False)
        if self.world_combo.count() > 0:
            self.world_combo.setCurrentIndex(0)

    def _add_map(self):
        """Add a new map."""
        try:
            # Validate inputs
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Map name cannot be empty.")
                return

            if self.world_combo.currentData() is None:
                QMessageBox.warning(self, "Validation Error", "Please select a world.")
                return

            # Parse image IDs
            image_ids = []
            if self.images_input.text().strip():
                for img_str in self.images_input.text().split(","):
                    img_id_str = img_str.strip()
                    if img_id_str:
                        try:
                            image_ids.append(EntityId(int(img_id_str)))
                        except ValueError:
                            QMessageBox.warning(self, "Validation Error", f"Invalid image ID: {img_id_str}")
                            return

            # Parse location IDs
            location_ids = []
            if self.locations_input.text().strip():
                for loc_str in self.locations_input.text().split(","):
                    loc_id_str = loc_str.strip()
                    if loc_id_str:
                        try:
                            location_ids.append(EntityId(int(loc_id_str)))
                        except ValueError:
                            QMessageBox.warning(self, "Validation Error", f"Invalid location ID: {loc_id_str}")
                            return

            # At least one image or description required
            if not image_ids and not self.description_input.toPlainText().strip():
                QMessageBox.warning(self, "Validation Error", "Map must have at least one image or description.")
                return

            # Create map
            map_obj = Map.create(
                tenant_id=TenantId(1),
                world_id=EntityId(self.world_combo.currentData()),
                name=self.name_input.text().strip(),
                description=self.description_input.toPlainText().strip() or None,
                image_ids=image_ids,
                location_ids=location_ids,
                scale=self.scale_input.text().strip() or None,
                is_interactive=self.interactive_check.isChecked()
            )

            self.lore_data.add_map(map_obj)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Map added successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add map: {str(e)}")

    def _update_map(self):
        """Update the selected map."""
        if not self.selected_map:
            return

        try:
            # Validate inputs
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Map name cannot be empty.")
                return

            # Parse image IDs
            image_ids = []
            if self.images_input.text().strip():
                for img_str in self.images_input.text().split(","):
                    img_id_str = img_str.strip()
                    if img_id_str:
                        try:
                            image_ids.append(EntityId(int(img_id_str)))
                        except ValueError:
                            QMessageBox.warning(self, "Validation Error", f"Invalid image ID: {img_id_str}")
                            return

            # Parse location IDs
            location_ids = []
            if self.locations_input.text().strip():
                for loc_str in self.locations_input.text().split(","):
                    loc_id_str = loc_str.strip()
                    if loc_id_str:
                        try:
                            location_ids.append(EntityId(int(loc_id_str)))
                        except ValueError:
                            QMessageBox.warning(self, "Validation Error", f"Invalid location ID: {loc_id_str}")
                            return

            # At least one image or description required
            if not image_ids and not self.description_input.toPlainText().strip():
                QMessageBox.warning(self, "Validation Error", "Map must have at least one image or description.")
                return

            # Update map
            object.__setattr__(self.selected_map, 'name', self.name_input.text().strip())
            self.selected_map.update_description(self.description_input.toPlainText().strip() or None)
            object.__setattr__(self.selected_map, 'image_ids', image_ids)
            object.__setattr__(self.selected_map, 'location_ids', location_ids)
            object.__setattr__(self.selected_map, 'scale', self.scale_input.text().strip() or None)
            object.__setattr__(self.selected_map, 'is_interactive', self.interactive_check.isChecked())

            # Update metadata
            object.__setattr__(self.selected_map, 'updated_at', self.selected_map.updated_at.__class__.now())
            object.__setattr__(self.selected_map, 'version', self.selected_map.version.increment())

            self.refresh()
            QMessageBox.information(self, "Success", "Map updated successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update map: {str(e)}")

    def _delete_map(self):
        """Delete the selected map."""
        if not self.selected_map:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the map '{self.selected_map.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.maps.remove(self.selected_map)
                self.refresh()
                self._clear_form()
                QMessageBox.information(self, "Success", "Map deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete map: {str(e)}")
