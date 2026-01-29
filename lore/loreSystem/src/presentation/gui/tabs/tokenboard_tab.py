"""
TokenboardTab - Tab for managing GM tokenboards
"""
from typing import Optional
import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.entities.tokenboard import Tokenboard
from src.domain.value_objects.common import TenantId, EntityId


class TokenboardTab(QWidget):
    """Tab for managing GM tokenboards."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_tokenboard: Optional[Tokenboard] = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("🎛️ Tokenboards")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Tokenboards table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Name", "Counters", "Notes", "Active", "Updated"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Tokenboard Details")
        form_layout = QFormLayout()

        # World selection
        self.world_combo = QComboBox()
        form_layout.addRow("World:", self.world_combo)

        # Tokenboard name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter tokenboard name...")
        form_layout.addRow("Name:", self.name_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Tokenboard description...")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)

        # Counters (JSON format)
        self.counters_input = QTextEdit()
        self.counters_input.setPlaceholderText('{"initiative": 5, "round": 1}')
        self.counters_input.setMaximumHeight(60)
        form_layout.addRow("Counters (JSON):", self.counters_input)

        # Sticky notes (JSON array)
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText('["Note 1", "Note 2"]')
        self.notes_input.setMaximumHeight(60)
        form_layout.addRow("Notes (JSON):", self.notes_input)

        # Shortcuts (JSON format)
        self.shortcuts_input = QTextEdit()
        self.shortcuts_input.setPlaceholderText('{"F1": "roll_initiative", "F2": "next_turn"}')
        self.shortcuts_input.setMaximumHeight(60)
        form_layout.addRow("Shortcuts (JSON):", self.shortcuts_input)

        # Timers (JSON format)
        self.timers_input = QTextEdit()
        self.timers_input.setPlaceholderText('{"combat": 300, "break": 600}')
        self.timers_input.setMaximumHeight(60)
        form_layout.addRow("Timers (JSON):", self.timers_input)

        # Active checkbox
        self.active_check = QCheckBox("This is the active tokenboard")
        form_layout.addRow("", self.active_check)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Tokenboard")
        self.add_btn.clicked.connect(self._add_tokenboard)

        self.update_btn = QPushButton("Update Tokenboard")
        self.update_btn.clicked.connect(self._update_tokenboard)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Tokenboard")
        self.delete_btn.clicked.connect(self._delete_tokenboard)
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
        """Refresh the tokenboards table and combo boxes."""
        # Update worlds combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(f"{world.name.value}", world.id.value)

        # Update tokenboards table
        self.table.setRowCount(0)
        for tokenboard in self.lore_data.tokenboards:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(tokenboard.id.value) if tokenboard.id else ""))

            # World
            world_name = "Unknown"
            for world in self.lore_data.worlds:
                if world.id == tokenboard.world_id:
                    world_name = world.name.value
                    break
            self.table.setItem(row, 1, QTableWidgetItem(world_name))

            # Name
            self.table.setItem(row, 2, QTableWidgetItem(tokenboard.name))

            # Counters count
            self.table.setItem(row, 3, QTableWidgetItem(str(len(tokenboard.counters))))

            # Notes count
            self.table.setItem(row, 4, QTableWidgetItem(str(len(tokenboard.sticky_notes))))

            # Active
            self.table.setItem(row, 5, QTableWidgetItem("✅" if tokenboard.is_active else ""))

            # Updated
            self.table.setItem(row, 6, QTableWidgetItem(tokenboard.updated_at.value.strftime("%Y-%m-%d %H:%M")))

        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle tokenboard selection changes."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if len(selected_rows) == 1:
            row = list(selected_rows)[0]
            tokenboard_id = int(self.table.item(row, 0).text())
            self.selected_tokenboard = next((t for t in self.lore_data.tokenboards if t.id and t.id.value == tokenboard_id), None)
            if self.selected_tokenboard:
                self._populate_form()
                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
            else:
                self._clear_form()
                self.update_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
        else:
            self.selected_tokenboard = None
            self._clear_form()
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate form with selected tokenboard data."""
        if not self.selected_tokenboard:
            return

        # Set world
        for i in range(self.world_combo.count()):
            if self.world_combo.itemData(i) == self.selected_tokenboard.world_id.value:
                self.world_combo.setCurrentIndex(i)
                break

        # Set fields
        self.name_input.setText(self.selected_tokenboard.name)
        self.description_input.setText(self.selected_tokenboard.description or "")
        self.counters_input.setText(json.dumps(self.selected_tokenboard.counters, indent=2))
        self.notes_input.setText(json.dumps(self.selected_tokenboard.sticky_notes, indent=2))
        self.shortcuts_input.setText(json.dumps(self.selected_tokenboard.shortcuts, indent=2))
        self.timers_input.setText(json.dumps(self.selected_tokenboard.timers, indent=2))
        self.active_check.setChecked(self.selected_tokenboard.is_active)

    def _clear_form(self):
        """Clear all form fields."""
        self.name_input.clear()
        self.description_input.clear()
        self.counters_input.clear()
        self.notes_input.clear()
        self.shortcuts_input.clear()
        self.timers_input.clear()
        self.active_check.setChecked(False)
        if self.world_combo.count() > 0:
            self.world_combo.setCurrentIndex(0)

    def _add_tokenboard(self):
        """Add a new tokenboard."""
        try:
            # Validate inputs
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Tokenboard name cannot be empty.")
                return

            if self.world_combo.currentData() is None:
                QMessageBox.warning(self, "Validation Error", "Please select a world.")
                return

            # Parse JSON fields
            try:
                counters = json.loads(self.counters_input.toPlainText().strip()) if self.counters_input.toPlainText().strip() else {}
                if not isinstance(counters, dict):
                    raise ValueError("Counters must be a dictionary")
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Counters JSON: {str(e)}")
                return

            try:
                sticky_notes = json.loads(self.notes_input.toPlainText().strip()) if self.notes_input.toPlainText().strip() else []
                if not isinstance(sticky_notes, list):
                    raise ValueError("Notes must be a list")
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Notes JSON: {str(e)}")
                return

            try:
                shortcuts = json.loads(self.shortcuts_input.toPlainText().strip()) if self.shortcuts_input.toPlainText().strip() else {}
                if not isinstance(shortcuts, dict):
                    raise ValueError("Shortcuts must be a dictionary")
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Shortcuts JSON: {str(e)}")
                return

            try:
                timers = json.loads(self.timers_input.toPlainText().strip()) if self.timers_input.toPlainText().strip() else {}
                if not isinstance(timers, dict):
                    raise ValueError("Timers must be a dictionary")
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Timers JSON: {str(e)}")
                return

            # Create tokenboard
            tokenboard = Tokenboard.create(
                tenant_id=TenantId(1),
                world_id=EntityId(self.world_combo.currentData()),
                name=self.name_input.text().strip(),
                description=self.description_input.toPlainText().strip() or None,
                counters=counters,
                sticky_notes=sticky_notes,
                shortcuts=shortcuts,
                timers=timers,
                is_active=self.active_check.isChecked()
            )

            self.lore_data.add_tokenboard(tokenboard)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Tokenboard added successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add tokenboard: {str(e)}")

    def _update_tokenboard(self):
        """Update the selected tokenboard."""
        if not self.selected_tokenboard:
            return

        try:
            # Validate inputs
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Tokenboard name cannot be empty.")
                return

            # Parse JSON fields
            try:
                counters = json.loads(self.counters_input.toPlainText().strip()) if self.counters_input.toPlainText().strip() else {}
                if not isinstance(counters, dict):
                    raise ValueError("Counters must be a dictionary")
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Counters JSON: {str(e)}")
                return

            try:
                sticky_notes = json.loads(self.notes_input.toPlainText().strip()) if self.notes_input.toPlainText().strip() else []
                if not isinstance(sticky_notes, list):
                    raise ValueError("Notes must be a list")
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Notes JSON: {str(e)}")
                return

            try:
                shortcuts = json.loads(self.shortcuts_input.toPlainText().strip()) if self.shortcuts_input.toPlainText().strip() else {}
                if not isinstance(shortcuts, dict):
                    raise ValueError("Shortcuts must be a dictionary")
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Shortcuts JSON: {str(e)}")
                return

            try:
                timers = json.loads(self.timers_input.toPlainText().strip()) if self.timers_input.toPlainText().strip() else {}
                if not isinstance(timers, dict):
                    raise ValueError("Timers must be a dictionary")
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Timers JSON: {str(e)}")
                return

            # Update tokenboard
            object.__setattr__(self.selected_tokenboard, 'name', self.name_input.text().strip())
            object.__setattr__(self.selected_tokenboard, 'description', self.description_input.toPlainText().strip() or None)
            object.__setattr__(self.selected_tokenboard, 'counters', counters)
            object.__setattr__(self.selected_tokenboard, 'sticky_notes', sticky_notes)
            object.__setattr__(self.selected_tokenboard, 'shortcuts', shortcuts)
            object.__setattr__(self.selected_tokenboard, 'timers', timers)

            # Update active status
            if self.active_check.isChecked() and not self.selected_tokenboard.is_active:
                self.selected_tokenboard.activate()
            elif not self.active_check.isChecked() and self.selected_tokenboard.is_active:
                self.selected_tokenboard.deactivate()

            # Update metadata
            object.__setattr__(self.selected_tokenboard, 'updated_at', self.selected_tokenboard.updated_at.__class__.now())
            object.__setattr__(self.selected_tokenboard, 'version', self.selected_tokenboard.version.increment())

            self.refresh()
            QMessageBox.information(self, "Success", "Tokenboard updated successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update tokenboard: {str(e)}")

    def _delete_tokenboard(self):
        """Delete the selected tokenboard."""
        if not self.selected_tokenboard:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the tokenboard '{self.selected_tokenboard.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.tokenboards.remove(self.selected_tokenboard)
                self.refresh()
                self._clear_form()
                QMessageBox.information(self, "Success", "Tokenboard deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete tokenboard: {str(e)}")
