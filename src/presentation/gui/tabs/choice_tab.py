"""
ChoiceTab - Tab for managing player choices in stories
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

from src.domain.entities.choice import Choice
from src.domain.value_objects.common import TenantId, EntityId, ChoiceType


class ChoiceTab(QWidget):
    """Tab for managing player choices in stories."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_choice: Optional[Choice] = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("🎯 Choices")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Choices table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Story", "Prompt", "Type", "Options", "Updated"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Choice Details")
        form_layout = QFormLayout()

        # World selection
        self.world_combo = QComboBox()
        form_layout.addRow("World:", self.world_combo)

        # Story selection
        self.story_combo = QComboBox()
        form_layout.addRow("Story:", self.story_combo)

        # Choice prompt
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("What choice does the player face?")
        self.prompt_input.setMaximumHeight(80)
        form_layout.addRow("Prompt:", self.prompt_input)

        # Choice type
        self.type_combo = QComboBox()
        self.type_combo.addItem("Branch", ChoiceType.BRANCH.value)
        self.type_combo.addItem("Consequence", ChoiceType.CONSEQUENCE.value)
        self.type_combo.addItem("Decision", ChoiceType.DECISION.value)
        form_layout.addRow("Type:", self.type_combo)

        # Options (JSON array)
        self.options_input = QTextEdit()
        self.options_input.setPlaceholderText('["Option 1", "Option 2", "Option 3"]')
        self.options_input.setMaximumHeight(60)
        form_layout.addRow("Options (JSON):", self.options_input)

        # Consequences (JSON array)
        self.consequences_input = QTextEdit()
        self.consequences_input.setPlaceholderText('["Consequence 1", "Consequence 2", "Consequence 3"]')
        self.consequences_input.setMaximumHeight(60)
        form_layout.addRow("Consequences (JSON):", self.consequences_input)

        # Next story IDs (JSON array)
        self.next_stories_input = QTextEdit()
        self.next_stories_input.setPlaceholderText('[5, 6, null] (null = ending)')
        self.next_stories_input.setMaximumHeight(60)
        form_layout.addRow("Next Stories (JSON):", self.next_stories_input)

        # Mandatory checkbox
        self.mandatory_check = QCheckBox("Player must make this choice")
        form_layout.addRow("", self.mandatory_check)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Choice")
        self.add_btn.clicked.connect(self._add_choice)

        self.update_btn = QPushButton("Update Choice")
        self.update_btn.clicked.connect(self._update_choice)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Choice")
        self.delete_btn.clicked.connect(self._delete_choice)
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
        """Refresh the choices table and combo boxes."""
        # Update worlds combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(f"{world.name.value}", world.id.value)

        # Update stories combo
        self.story_combo.clear()
        for story in self.lore_data.stories:
            self.story_combo.addItem(f"{story.name.value} (ID: {story.id.value if story.id else 'New'})",
                                     story.id.value if story.id else None)

        # Update choices table
        self.table.setRowCount(0)
        for choice in self.lore_data.choices:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(choice.id.value) if choice.id else ""))

            # World
            world_name = "Unknown"
            for world in self.lore_data.worlds:
                if world.id == choice.world_id:
                    world_name = world.name.value
                    break
            self.table.setItem(row, 1, QTableWidgetItem(world_name))

            # Story
            story_name = "Unknown"
            for story in self.lore_data.stories:
                if story.id == choice.story_id:
                    story_name = story.name.value
                    break
            self.table.setItem(row, 2, QTableWidgetItem(story_name))

            # Prompt (preview)
            prompt_preview = choice.prompt[:50] + "..." if len(choice.prompt) > 50 else choice.prompt
            self.table.setItem(row, 3, QTableWidgetItem(prompt_preview))

            # Type
            self.table.setItem(row, 4, QTableWidgetItem(choice.choice_type.value.title()))

            # Options count
            self.table.setItem(row, 5, QTableWidgetItem(str(len(choice.options))))

            # Updated
            self.table.setItem(row, 6, QTableWidgetItem(choice.updated_at.value.strftime("%Y-%m-%d %H:%M")))

        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle choice selection changes."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if len(selected_rows) == 1:
            row = list(selected_rows)[0]
            choice_id = int(self.table.item(row, 0).text())
            self.selected_choice = next((c for c in self.lore_data.choices if c.id and c.id.value == choice_id), None)
            if self.selected_choice:
                self._populate_form()
                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
            else:
                self._clear_form()
                self.update_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
        else:
            self.selected_choice = None
            self._clear_form()
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate form with selected choice data."""
        if not self.selected_choice:
            return

        # Set world
        for i in range(self.world_combo.count()):
            if self.world_combo.itemData(i) == self.selected_choice.world_id.value:
                self.world_combo.setCurrentIndex(i)
                break

        # Set story
        for i in range(self.story_combo.count()):
            if self.story_combo.itemData(i) == self.selected_choice.story_id.value:
                self.story_combo.setCurrentIndex(i)
                break

        # Set fields
        self.prompt_input.setText(self.selected_choice.prompt)

        # Set type
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == self.selected_choice.choice_type.value:
                self.type_combo.setCurrentIndex(i)
                break

        # Set JSON fields
        self.options_input.setText(json.dumps(self.selected_choice.options, indent=2))
        self.consequences_input.setText(json.dumps(self.selected_choice.consequences, indent=2))

        # Convert next_story_ids to plain values (None becomes null in JSON)
        next_ids = [s.value if s else None for s in self.selected_choice.next_story_ids]
        self.next_stories_input.setText(json.dumps(next_ids, indent=2))

        self.mandatory_check.setChecked(self.selected_choice.is_mandatory)

    def _clear_form(self):
        """Clear all form fields."""
        self.prompt_input.clear()
        self.options_input.clear()
        self.consequences_input.clear()
        self.next_stories_input.clear()
        self.mandatory_check.setChecked(True)
        if self.world_combo.count() > 0:
            self.world_combo.setCurrentIndex(0)
        if self.story_combo.count() > 0:
            self.story_combo.setCurrentIndex(0)
        if self.type_combo.count() > 0:
            self.type_combo.setCurrentIndex(0)

    def _add_choice(self):
        """Add a new choice."""
        try:
            # Validate inputs
            if not self.prompt_input.toPlainText().strip():
                QMessageBox.warning(self, "Validation Error", "Choice prompt cannot be empty.")
                return

            if self.world_combo.currentData() is None:
                QMessageBox.warning(self, "Validation Error", "Please select a world.")
                return

            if self.story_combo.currentData() is None:
                QMessageBox.warning(self, "Validation Error", "Please select a story.")
                return

            # Parse JSON fields
            try:
                options = json.loads(self.options_input.toPlainText().strip())
                if not isinstance(options, list) or len(options) < 2:
                    raise ValueError("Options must be a list with at least 2 items")
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Options JSON: {str(e)}")
                return

            try:
                consequences = json.loads(self.consequences_input.toPlainText().strip())
                if not isinstance(consequences, list):
                    raise ValueError("Consequences must be a list")
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Consequences JSON: {str(e)}")
                return

            try:
                next_ids_raw = json.loads(self.next_stories_input.toPlainText().strip())
                if not isinstance(next_ids_raw, list):
                    raise ValueError("Next Stories must be a list")
                # Convert to EntityId or None
                next_story_ids = [EntityId(n) if n is not None else None for n in next_ids_raw]
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Next Stories JSON: {str(e)}")
                return

            # Validate arrays have same length
            if not (len(options) == len(consequences) == len(next_story_ids)):
                QMessageBox.warning(self, "Validation Error",
                                  "Options, Consequences, and Next Stories must have the same length.")
                return

            # Create choice
            choice = Choice.create(
                tenant_id=TenantId(1),
                world_id=EntityId(self.world_combo.currentData()),
                story_id=EntityId(self.story_combo.currentData()),
                prompt=self.prompt_input.toPlainText().strip(),
                choice_type=ChoiceType(self.type_combo.currentData()),
                options=options,
                consequences=consequences,
                next_story_ids=next_story_ids,
                is_mandatory=self.mandatory_check.isChecked()
            )

            self.lore_data.add_choice(choice)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Choice added successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add choice: {str(e)}")

    def _update_choice(self):
        """Update the selected choice."""
        if not self.selected_choice:
            return

        try:
            # Validate inputs
            if not self.prompt_input.toPlainText().strip():
                QMessageBox.warning(self, "Validation Error", "Choice prompt cannot be empty.")
                return

            # Parse JSON fields
            try:
                options = json.loads(self.options_input.toPlainText().strip())
                if not isinstance(options, list) or len(options) < 2:
                    raise ValueError("Options must be a list with at least 2 items")
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Options JSON: {str(e)}")
                return

            try:
                consequences = json.loads(self.consequences_input.toPlainText().strip())
                if not isinstance(consequences, list):
                    raise ValueError("Consequences must be a list")
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Consequences JSON: {str(e)}")
                return

            try:
                next_ids_raw = json.loads(self.next_stories_input.toPlainText().strip())
                if not isinstance(next_ids_raw, list):
                    raise ValueError("Next Stories must be a list")
                next_story_ids = [EntityId(n) if n is not None else None for n in next_ids_raw]
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"Invalid Next Stories JSON: {str(e)}")
                return

            # Validate arrays have same length
            if not (len(options) == len(consequences) == len(next_story_ids)):
                QMessageBox.warning(self, "Validation Error",
                                  "Options, Consequences, and Next Stories must have the same length.")
                return

            # Update choice
            self.selected_choice.update_prompt(self.prompt_input.toPlainText().strip())
            self.selected_choice.update_options(options, consequences, next_story_ids)

            # Update type and mandatory
            object.__setattr__(self.selected_choice, 'choice_type', ChoiceType(self.type_combo.currentData()))
            object.__setattr__(self.selected_choice, 'is_mandatory', self.mandatory_check.isChecked())

            # Update metadata
            object.__setattr__(self.selected_choice, 'updated_at', self.selected_choice.updated_at.__class__.now())
            object.__setattr__(self.selected_choice, 'version', self.selected_choice.version.increment())

            self.refresh()
            QMessageBox.information(self, "Success", "Choice updated successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update choice: {str(e)}")

    def _delete_choice(self):
        """Delete the selected choice."""
        if not self.selected_choice:
            return

        prompt_preview = self.selected_choice.prompt[:50] + "..." if len(self.selected_choice.prompt) > 50 else self.selected_choice.prompt
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the choice '{prompt_preview}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.choices.remove(self.selected_choice)
                self.refresh()
                self._clear_form()
                QMessageBox.information(self, "Success", "Choice deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete choice: {str(e)}")
