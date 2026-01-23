"""
MusicControlsTab - Tab for managing music controls.
"""
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QMessageBox, QComboBox, QSpinBox, QSplitter
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from src.domain.entities.music_control import MusicControl
from src.domain.value_objects.common import TenantId, EntityId, Description, NarrativePhase, EmotionalTone, PlayerContext


class MusicControlsTab(QWidget):
    """Tab for managing music controls."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Music Controls")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and details
        splitter = QSplitter()
        layout.addWidget(splitter)

        # Left side - Controls table
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        # Controls table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Priority", "Lore State", "Narrative Phase", "Emotional Tone"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        left_layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Control")
        self.add_btn.clicked.connect(self._add_control)

        self.update_btn = QPushButton("Update Control")
        self.update_btn.clicked.connect(self._update_control)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Control")
        self.delete_btn.clicked.connect(self._delete_control)
        self.delete_btn.setEnabled(False)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()

        left_layout.addLayout(button_layout)

        # Right side - Control details form
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        # Form
        form_group = QGroupBox("Control Details")
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)

        # Context settings
        self.lore_state_input = QLineEdit()
        self.lore_state_input.setPlaceholderText("Custom lore state identifier")

        self.narrative_phase_combo = QComboBox()
        self.narrative_phase_combo.addItem("", None)
        for phase in NarrativePhase:
            self.narrative_phase_combo.addItem(phase.value, phase)

        self.emotional_tone_combo = QComboBox()
        self.emotional_tone_combo.addItem("", None)
        for tone in EmotionalTone:
            self.emotional_tone_combo.addItem(tone.value, tone)

        self.player_context_combo = QComboBox()
        self.player_context_combo.addItem("", None)
        for context in PlayerContext:
            self.player_context_combo.addItem(context.value, context)

        # Trigger settings
        self.trigger_conditions_input = QTextEdit()
        self.trigger_conditions_input.setMaximumHeight(100)
        self.trigger_conditions_input.setPlaceholderText("JSON trigger conditions")

        self.priority_spin = QSpinBox()
        self.priority_spin.setMinimum(0)
        self.priority_spin.setMaximum(100)

        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Lore State:", self.lore_state_input)
        form_layout.addRow("Narrative Phase:", self.narrative_phase_combo)
        form_layout.addRow("Emotional Tone:", self.emotional_tone_combo)
        form_layout.addRow("Player Context:", self.player_context_combo)
        form_layout.addRow("Trigger Conditions:", self.trigger_conditions_input)
        form_layout.addRow("Priority:", self.priority_spin)

        form_group.setLayout(form_layout)
        right_layout.addWidget(form_group)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 400])

        self.setLayout(layout)

        self.selected_control: Optional[MusicControl] = None

    def refresh(self):
        """Refresh the controls table."""
        self.table.setRowCount(0)

        for control in self.lore_data.music_controls:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(control.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(control.priority)))
            self.table.setItem(row, 2, QTableWidgetItem(control.lore_state or ""))
            self.table.setItem(row, 3, QTableWidgetItem(control.narrative_phase.value if control.narrative_phase else ""))
            self.table.setItem(row, 4, QTableWidgetItem(control.emotional_tone.value if control.emotional_tone else ""))

        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle control selection."""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            control_name = self.table.item(row, 0).text()
            self.selected_control = next((c for c in self.lore_data.music_controls if c.name == control_name), None)

            if self.selected_control:
                self.name_input.setText(self.selected_control.name)
                self.description_input.setPlainText(str(self.selected_control.description))
                self.lore_state_input.setText(self.selected_control.lore_state or "")
                self.narrative_phase_combo.setCurrentText(self.selected_control.narrative_phase.value if self.selected_control.narrative_phase else "")
                self.emotional_tone_combo.setCurrentText(self.selected_control.emotional_tone.value if self.selected_control.emotional_tone else "")
                self.player_context_combo.setCurrentText(self.selected_control.player_context.value if self.selected_control.player_context else "")
                self.trigger_conditions_input.setPlainText(self.selected_control.trigger_conditions or "")
                self.priority_spin.setValue(self.selected_control.priority)

                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
        else:
            self.selected_control = None
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _add_control(self):
        """Add a new music control."""
        try:
            control = MusicControl.create(
                tenant_id=self.lore_data.tenant_id,
                world_id=self.lore_data.current_world_id,
                name=self.name_input.text(),
                description=Description(self.description_input.toPlainText()),
                lore_state=self.lore_state_input.text() or None,
                narrative_phase=self.narrative_phase_combo.currentData(),
                emotional_tone=self.emotional_tone_combo.currentData(),
                player_context=self.player_context_combo.currentData(),
                trigger_conditions=self.trigger_conditions_input.toPlainText() or None,
                priority=self.priority_spin.value()
            )
            self.lore_data.add_music_control(control)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Music control created successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create music control: {e}")

    def _update_control(self):
        """Update selected control."""
        if not self.selected_control:
            return

        try:
            self.selected_control.update_details(
                name=self.name_input.text(),
                description=Description(self.description_input.toPlainText()),
                lore_state=self.lore_state_input.text() or None,
                narrative_phase=self.narrative_phase_combo.currentData(),
                emotional_tone=self.emotional_tone_combo.currentData(),
                player_context=self.player_context_combo.currentData(),
                trigger_conditions=self.trigger_conditions_input.toPlainText() or None,
                priority=self.priority_spin.value()
            )
            self.refresh()
            QMessageBox.information(self, "Success", "Music control updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update music control: {e}")

    def _delete_control(self):
        """Delete selected control."""
        if not self.selected_control:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{self.selected_control.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.lore_data.music_controls.remove(self.selected_control)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Music control deleted successfully!")

    def _clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.description_input.clear()
        self.lore_state_input.clear()
        self.narrative_phase_combo.setCurrentIndex(0)
        self.emotional_tone_combo.setCurrentIndex(0)
        self.player_context_combo.setCurrentIndex(0)
        self.trigger_conditions_input.clear()
        self.priority_spin.setValue(0)
        self.selected_control = None