"""
EnvironmentTab - Tab for managing environments
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.entities.environment import Environment
from src.domain.value_objects.common import EntityId, TimeOfDay, Weather, Lighting


class EnvironmentTab(QWidget):
    """Tab for managing environments."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_environment: Optional[Environment] = None
        self.all_environments: List[Environment] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("🌤️ Environments")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Environments table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Location", "Time", "Weather", "Lighting", "Active"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Environment Details")
        form_layout = QFormLayout()

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter environment name (e.g., 'Stormy Night')...")
        form_layout.addRow("Name:", self.name_input)

        # Location
        self.location_combo = QComboBox()
        form_layout.addRow("Location:", self.location_combo)

        # Time of Day
        self.time_combo = QComboBox()
        self.time_combo.addItems(["day", "night", "dawn", "dusk"])
        form_layout.addRow("Time of Day:", self.time_combo)

        # Weather
        self.weather_combo = QComboBox()
        self.weather_combo.addItems(["clear", "rainy", "stormy", "foggy"])
        form_layout.addRow("Weather:", self.weather_combo)

        # Lighting
        self.lighting_combo = QComboBox()
        self.lighting_combo.addItems(["bright", "dim", "dark", "magical"])
        form_layout.addRow("Lighting:", self.lighting_combo)

        # Active checkbox
        self.active_checkbox = QCheckBox("Active Environment")
        self.active_checkbox.setChecked(True)
        form_layout.addRow("", self.active_checkbox)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter environment description...")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)

        # Temperature
        self.temperature_input = QLineEdit()
        self.temperature_input.setPlaceholderText("Temperature description (e.g., 'chilly', 'sweltering')")
        form_layout.addRow("Temperature:", self.temperature_input)

        # Sounds
        self.sounds_input = QLineEdit()
        self.sounds_input.setPlaceholderText("Ambient sounds (e.g., 'thunder rumbling')")
        form_layout.addRow("Sounds:", self.sounds_input)

        # Smells
        self.smells_input = QLineEdit()
        self.smells_input.setPlaceholderText("Ambient smells (e.g., 'fresh rain')")
        form_layout.addRow("Smells:", self.smells_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Environment")
        self.add_btn.clicked.connect(self._add_environment)
        button_layout.addWidget(self.add_btn)

        self.update_btn = QPushButton("Update Environment")
        self.update_btn.clicked.connect(self._update_environment)
        self.update_btn.setEnabled(False)
        button_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("Delete Environment")
        self.delete_btn.clicked.connect(self._delete_environment)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        """Refresh the environments list."""
        try:
            self.all_environments = self.lore_data.get_environments()
            self._populate_location_combo()
            self._populate_table(self.all_environments)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load environments: {str(e)}")

    def _populate_location_combo(self):
        """Populate the location combo box."""
        try:
            locations = self.lore_data.get_locations()
            self.location_combo.clear()
            for location in locations:
                self.location_combo.addItem(getattr(location, 'name', 'Unknown'), location.id)
        except Exception:
            pass

    def _populate_table(self, environments: List[Environment]):
        """Populate the table with environments."""
        self.table.setRowCount(len(environments))
        for row, environment in enumerate(environments):
            self.table.setItem(row, 0, QTableWidgetItem(str(environment.id)))
            self.table.setItem(row, 1, QTableWidgetItem(getattr(environment, 'name', 'N/A')))
            location_id = getattr(environment, 'location_id', 'N/A')
            self.table.setItem(row, 2, QTableWidgetItem(str(location_id)))
            self.table.setItem(row, 3, QTableWidgetItem(getattr(environment.time_of_day, 'value', 'N/A')))
            self.table.setItem(row, 4, QTableWidgetItem(getattr(environment.weather, 'value', 'N/A')))
            self.table.setItem(row, 5, QTableWidgetItem(getattr(environment.lighting, 'value', 'N/A')))
            active_str = "Yes" if getattr(environment, 'is_active', False) else "No"
            self.table.setItem(row, 6, QTableWidgetItem(active_str))

    def _on_selection_changed(self):
        """Handle environment selection change."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_environment = self.all_environments[row]
            self._populate_form()
            self.update_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
        else:
            self.selected_environment = None
            self._clear_form()
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate the form with selected environment data."""
        if not self.selected_environment:
            return

        self.name_input.setText(getattr(self.selected_environment, 'name', ''))
        self.time_combo.setCurrentText(getattr(self.selected_environment.time_of_day, 'value', 'day'))
        self.weather_combo.setCurrentText(getattr(self.selected_environment.weather, 'value', 'clear'))
        self.lighting_combo.setCurrentText(getattr(self.selected_environment.lighting, 'value', 'bright'))
        self.active_checkbox.setChecked(getattr(self.selected_environment, 'is_active', True))
        self.description_input.setPlainText(getattr(self.selected_environment, 'description', ''))
        self.temperature_input.setText(getattr(self.selected_environment, 'temperature', ''))
        self.sounds_input.setText(getattr(self.selected_environment, 'sounds', ''))
        self.smells_input.setText(getattr(self.selected_environment, 'smells', ''))

        # Set location combo to match the environment's location
        location_id = getattr(self.selected_environment, 'location_id', None)
        if location_id is not None:
            for i in range(self.location_combo.count()):
                if self.location_combo.itemData(i) == location_id:
                    self.location_combo.setCurrentIndex(i)
                    break

    def _clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.time_combo.setCurrentIndex(0)
        self.weather_combo.setCurrentIndex(0)
        self.lighting_combo.setCurrentIndex(0)
        self.active_checkbox.setChecked(True)
        self.description_input.clear()
        self.temperature_input.clear()
        self.sounds_input.clear()
        self.smells_input.clear()

    def _add_environment(self):
        """Add a new environment."""
        try:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Environment name cannot be empty")
                return

            if self.location_combo.currentData() is None:
                QMessageBox.warning(self, "Warning", "Please select a location")
                return

            environment_data = {
                'name': name,
                'location_id': self.location_combo.currentData(),
                'time_of_day': self.time_combo.currentText(),
                'weather': self.weather_combo.currentText(),
                'lighting': self.lighting_combo.currentText(),
                'is_active': self.active_checkbox.isChecked(),
                'description': self.description_input.toPlainText(),
                'temperature': self.temperature_input.text().strip(),
                'sounds': self.sounds_input.text().strip(),
                'smells': self.smells_input.text().strip(),
            }

            self.lore_data.add_environment(environment_data)
            QMessageBox.information(self, "Success", "Environment added successfully!")
            self._clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add environment: {str(e)}")

    def _update_environment(self):
        """Update the selected environment."""
        if not self.selected_environment:
            return

        try:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Environment name cannot be empty")
                return

            if self.location_combo.currentData() is None:
                QMessageBox.warning(self, "Warning", "Please select a location")
                return

            environment_data = {
                'name': name,
                'location_id': self.location_combo.currentData(),
                'time_of_day': self.time_combo.currentText(),
                'weather': self.weather_combo.currentText(),
                'lighting': self.lighting_combo.currentText(),
                'is_active': self.active_checkbox.isChecked(),
                'description': self.description_input.toPlainText(),
                'temperature': self.temperature_input.text().strip(),
                'sounds': self.sounds_input.text().strip(),
                'smells': self.smells_input.text().strip(),
            }

            self.lore_data.update_environment(self.selected_environment.id, environment_data)
            QMessageBox.information(self, "Success", "Environment updated successfully!")
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update environment: {str(e)}")

    def _delete_environment(self):
        """Delete the selected environment."""
        if not self.selected_environment:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{getattr(self.selected_environment, 'name', 'Unknown')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.delete_environment(self.selected_environment.id)
                QMessageBox.information(self, "Success", "Environment deleted successfully!")
                self._clear_form()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete environment: {str(e)}")