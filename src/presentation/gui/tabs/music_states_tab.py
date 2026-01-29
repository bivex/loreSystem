"""
MusicStatesTab - Tab for managing music states.
"""
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QMessageBox, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QSplitter
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from src.domain.entities.music_state import MusicState
from src.domain.value_objects.common import TenantId, EntityId, Description


class MusicStatesTab(QWidget):
    """Tab for managing music states."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Music States")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

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
        self.table.setHorizontalHeaderLabels(["Name", "Priority", "Silence", "Crossfade (s)", "Allow Interrupts"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        left_layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add State")
        self.add_btn.clicked.connect(self._add_state)

        self.update_btn = QPushButton("Update State")
        self.update_btn.clicked.connect(self._update_state)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete State")
        self.delete_btn.clicked.connect(self._delete_state)
        self.delete_btn.setEnabled(False)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()

        left_layout.addLayout(button_layout)

        # Right side - State details form
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        # Form
        form_group = QGroupBox("State Details")
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)

        # State configuration
        self.is_silence_check = QCheckBox("Is Silence Moment")

        self.default_track_combo = QComboBox()
        self.default_track_combo.addItem("None", None)
        # Will be populated with available tracks

        self.crossfade_spin = QDoubleSpinBox()
        self.crossfade_spin.setMinimum(0.0)
        self.crossfade_spin.setMaximum(30.0)
        self.crossfade_spin.setSingleStep(0.1)
        self.crossfade_spin.setSuffix(" seconds")

        self.allow_interrupts_check = QCheckBox("Allow Interrupts")

        self.priority_spin = QSpinBox()
        self.priority_spin.setMinimum(0)
        self.priority_spin.setMaximum(100)

        # Transition configuration
        self.transitions_input = QTextEdit()
        self.transitions_input.setMaximumHeight(100)
        self.transitions_input.setPlaceholderText("JSON array of allowed state names")

        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("", self.is_silence_check)
        form_layout.addRow("Default Track:", self.default_track_combo)
        form_layout.addRow("Crossfade Duration:", self.crossfade_spin)
        form_layout.addRow("", self.allow_interrupts_check)
        form_layout.addRow("Priority:", self.priority_spin)
        form_layout.addRow("Allowed Transitions:", self.transitions_input)

        form_group.setLayout(form_layout)
        right_layout.addWidget(form_group)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 400])

        self.setLayout(layout)

        self.selected_state: Optional[MusicState] = None

    def refresh(self):
        """Refresh the states table."""
        self.table.setRowCount(0)

        # Populate default track combo
        self.default_track_combo.clear()
        self.default_track_combo.addItem("None", None)
        for track in self.lore_data.music_tracks:
            self.default_track_combo.addItem(track.name, track.id)

        for state in self.lore_data.music_states:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(state.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(state.priority)))
            self.table.setItem(row, 2, QTableWidgetItem("Yes" if state.is_silence_moment else "No"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{state.crossfade_duration_seconds:.1f}"))
            self.table.setItem(row, 4, QTableWidgetItem("Yes" if state.allow_interrupts else "No"))

        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle state selection."""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            state_name = self.table.item(row, 0).text()
            self.selected_state = next((s for s in self.lore_data.music_states if s.name == state_name), None)

            if self.selected_state:
                self.name_input.setText(self.selected_state.name)
                self.description_input.setPlainText(str(self.selected_state.description))
                self.is_silence_check.setChecked(self.selected_state.is_silence_moment)

                # Set default track combo
                if self.selected_state.default_track_id:
                    index = self.default_track_combo.findData(self.selected_state.default_track_id)
                    if index >= 0:
                        self.default_track_combo.setCurrentIndex(index)
                else:
                    self.default_track_combo.setCurrentIndex(0)

                self.crossfade_spin.setValue(self.selected_state.crossfade_duration_seconds)
                self.allow_interrupts_check.setChecked(self.selected_state.allow_interrupts)
                self.priority_spin.setValue(self.selected_state.priority)
                self.transitions_input.setPlainText(self.selected_state.can_transition_to or "")

                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
        else:
            self.selected_state = None
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _add_state(self):
        """Add a new music state."""
        try:
            state = MusicState.create(
                tenant_id=self.lore_data.tenant_id,
                world_id=self.lore_data.current_world_id,
                name=self.name_input.text(),
                description=Description(self.description_input.toPlainText()),
                is_silence_moment=self.is_silence_check.isChecked(),
                default_track_id=self.default_track_combo.currentData(),
                crossfade_duration_seconds=self.crossfade_spin.value(),
                allow_interrupts=self.allow_interrupts_check.isChecked(),
                priority=self.priority_spin.value(),
                can_transition_to=self.transitions_input.toPlainText() or None
            )
            self.lore_data.add_music_state(state)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Music state created successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create music state: {e}")

    def _update_state(self):
        """Update selected state."""
        if not self.selected_state:
            return

        try:
            self.selected_state.update_details(
                name=self.name_input.text(),
                description=Description(self.description_input.toPlainText()),
                is_silence_moment=self.is_silence_check.isChecked(),
                default_track_id=self.default_track_combo.currentData(),
                crossfade_duration_seconds=self.crossfade_spin.value(),
                allow_interrupts=self.allow_interrupts_check.isChecked(),
                priority=self.priority_spin.value(),
                can_transition_to=self.transitions_input.toPlainText() or None
            )
            self.refresh()
            QMessageBox.information(self, "Success", "Music state updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update music state: {e}")

    def _delete_state(self):
        """Delete selected state."""
        if not self.selected_state:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{self.selected_state.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.lore_data.music_states.remove(self.selected_state)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Music state deleted successfully!")

    def _clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.description_input.clear()
        self.is_silence_check.setChecked(False)
        self.default_track_combo.setCurrentIndex(0)
        self.crossfade_spin.setValue(0.0)
        self.allow_interrupts_check.setChecked(True)
        self.priority_spin.setValue(0)
        self.transitions_input.clear()
        self.selected_state = None