"""
StoriesTab - Tab for managing stories with support for non-linear narratives
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QListWidget, QInputDialog, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.domain.entities.story import Story
from src.domain.value_objects.common import (
    TenantId, EntityId, StoryName, Content, StoryType
)


class StoriesTab(QWidget):
    """Tab for managing stories with linear and non-linear narratives."""

    story_selected = pyqtSignal(EntityId)

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_story: Optional[Story] = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("📖 Stories")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Stories table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Name", "Type", "Choices", "Connections", "Active", "Updated"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Story Details")
        form_layout = QFormLayout()

        # World selection
        self.world_combo = QComboBox()
        form_layout.addRow("World:", self.world_combo)

        # Story name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter story name...")
        form_layout.addRow("Name:", self.name_input)

        # Story type
        self.type_combo = QComboBox()
        self.type_combo.addItem("Linear", StoryType.LINEAR.value)
        self.type_combo.addItem("Non-Linear", StoryType.NON_LINEAR.value)
        self.type_combo.addItem("Interactive", StoryType.INTERACTIVE.value)
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        form_layout.addRow("Type:", self.type_combo)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter story description...")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)

        # Content editor
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Enter story content/narrative...")
        self.content_input.setMinimumHeight(150)
        form_layout.addRow("Story Content:", self.content_input)

        # Active status
        self.active_checkbox = QCheckBox("Story is active/playable")
        self.active_checkbox.setChecked(True)
        form_layout.addRow("Status:", self.active_checkbox)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Choices section (for non-linear stories)
        self.choices_group = QGroupBox("Player Choices")
        choices_layout = QVBoxLayout()

        choices_info = QLabel("For non-linear and interactive stories")
        choices_info.setStyleSheet("color: gray; font-style: italic;")
        choices_layout.addWidget(choices_info)

        self.choices_list = QListWidget()
        self.choices_list.setMaximumHeight(100)
        choices_layout.addWidget(self.choices_list)

        choices_btn_layout = QHBoxLayout()
        self.add_choice_btn = QPushButton("Add Choice")
        self.add_choice_btn.clicked.connect(self._add_choice)
        self.remove_choice_btn = QPushButton("Remove Choice")
        self.remove_choice_btn.clicked.connect(self._remove_choice)
        choices_btn_layout.addWidget(self.add_choice_btn)
        choices_btn_layout.addWidget(self.remove_choice_btn)
        choices_btn_layout.addStretch()
        choices_layout.addLayout(choices_btn_layout)

        self.choices_group.setLayout(choices_layout)
        form_main_layout.addWidget(self.choices_group)

        # World connections section
        connections_group = QGroupBox("Connected World Elements")
        connections_layout = QVBoxLayout()

        connections_info = QLabel("Characters, locations, items, etc. involved in this story")
        connections_info.setStyleSheet("color: gray; font-style: italic;")
        connections_layout.addWidget(connections_info)

        self.connections_list = QListWidget()
        self.connections_list.setMaximumHeight(100)
        connections_layout.addWidget(self.connections_list)

        connections_btn_layout = QHBoxLayout()
        self.add_connection_btn = QPushButton("Add Connection")
        self.add_connection_btn.clicked.connect(self._add_connection)
        self.remove_connection_btn = QPushButton("Remove Connection")
        self.remove_connection_btn.clicked.connect(self._remove_connection)
        connections_btn_layout.addWidget(self.add_connection_btn)
        connections_btn_layout.addWidget(self.remove_connection_btn)
        connections_btn_layout.addStretch()
        connections_layout.addLayout(connections_btn_layout)

        connections_group.setLayout(connections_layout)
        form_main_layout.addWidget(connections_group)

        # Main action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Story")
        self.add_btn.clicked.connect(self._add_story)

        self.update_btn = QPushButton("Update Story")
        self.update_btn.clicked.connect(self._update_story)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Story")
        self.delete_btn.clicked.connect(self._delete_story)
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

        # Initially hide choices group for linear stories
        self._on_type_changed()

    def _on_type_changed(self):
        """Handle story type change."""
        story_type = StoryType(self.type_combo.currentData())
        # Show choices group only for non-linear and interactive stories
        self.choices_group.setVisible(story_type in [StoryType.NON_LINEAR, StoryType.INTERACTIVE])

    def refresh(self):
        """Refresh the stories table and combo boxes."""
        # Refresh world combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(str(world.name), world.id.value)

        # Refresh table
        self.table.setRowCount(0)

        if not hasattr(self.lore_data, 'stories'):
            return

        for story in self.lore_data.stories:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Get world name
            world = next((w for w in self.lore_data.worlds if w.id == story.world_id), None)
            world_name = str(world.name) if world else f"ID: {story.world_id.value}"

            self.table.setItem(row, 0, QTableWidgetItem(str(story.id.value) if story.id else ""))
            self.table.setItem(row, 1, QTableWidgetItem(world_name))
            self.table.setItem(row, 2, QTableWidgetItem(str(story.name)))
            self.table.setItem(row, 3, QTableWidgetItem(story.story_type.value.replace("_", " ").title()))
            self.table.setItem(row, 4, QTableWidgetItem(str(len(story.choice_ids))))
            self.table.setItem(row, 5, QTableWidgetItem(str(len(story.connected_world_ids))))
            self.table.setItem(row, 6, QTableWidgetItem("✓" if story.is_active else "✗"))
            self.table.setItem(row, 7, QTableWidgetItem(story.updated_at.value.strftime("%Y-%m-%d %H:%M")))

        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle story selection."""
        selected_items = self.table.selectedItems()
        if selected_items and hasattr(self.lore_data, 'stories'):
            row = selected_items[0].row()
            story_id = EntityId(int(self.table.item(row, 0).text()))
            self.selected_story = next((s for s in self.lore_data.stories if s.id == story_id), None)

            if self.selected_story:
                # Update form fields
                # Find and set world
                for i in range(self.world_combo.count()):
                    if self.world_combo.itemData(i) == self.selected_story.world_id.value:
                        self.world_combo.setCurrentIndex(i)
                        break

                self.name_input.setText(str(self.selected_story.name))
                self.description_input.setPlainText(self.selected_story.description)
                self.content_input.setPlainText(str(self.selected_story.content))
                self.active_checkbox.setChecked(self.selected_story.is_active)

                # Set type
                for i in range(self.type_combo.count()):
                    if self.type_combo.itemData(i) == self.selected_story.story_type.value:
                        self.type_combo.setCurrentIndex(i)
                        break

                self._refresh_choices_list()
                self._refresh_connections_list()

                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.story_selected.emit(story_id)
        else:
            self.selected_story = None
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _refresh_choices_list(self):
        """Refresh choices list widget."""
        self.choices_list.clear()
        if self.selected_story and hasattr(self.lore_data, 'choices'):
            for choice_id in self.selected_story.choice_ids:
                choice = next((c for c in self.lore_data.choices if c.id == choice_id), None)
                name = str(choice.text) if choice else f"Unknown (ID: {choice_id.value})"
                self.choices_list.addItem(name)

    def _refresh_connections_list(self):
        """Refresh world connections list widget."""
        self.connections_list.clear()
        if self.selected_story:
            for element_id in self.selected_story.connected_world_ids:
                # Try to find element in various entity lists
                element_name = self._get_element_name(element_id)
                self.connections_list.addItem(element_name)

    def _get_element_name(self, element_id: EntityId) -> str:
        """Get the name of a world element by ID."""
        # Check characters
        if hasattr(self.lore_data, 'characters'):
            char = next((c for c in self.lore_data.characters if c.id == element_id), None)
            if char:
                return f"Character: {char.name}"

        # Check items
        if hasattr(self.lore_data, 'items'):
            item = next((i for i in self.lore_data.items if i.id == element_id), None)
            if item:
                return f"Item: {item.name}"

        # Check events
        if hasattr(self.lore_data, 'events'):
            event = next((e for e in self.lore_data.events if e.id == element_id), None)
            if event:
                return f"Event: {event.name}"

        return f"Unknown (ID: {element_id.value})"

    def _add_choice(self):
        """Add a choice to the story."""
        if not self.selected_story:
            QMessageBox.warning(self, "No Story Selected", "Please select a story first.")
            return

        if self.selected_story.story_type == StoryType.LINEAR:
            QMessageBox.warning(self, "Invalid Operation", "Linear stories do not have player choices.")
            return

        if not hasattr(self.lore_data, 'choices') or not self.lore_data.choices:
            QMessageBox.information(self, "No Choices", "No choices available. Create choices first.")
            return

        # Get available choices for this world
        world_choices = [c for c in self.lore_data.choices
                        if c.world_id == self.selected_story.world_id
                        and c.id not in self.selected_story.choice_ids]

        if not world_choices:
            QMessageBox.information(self, "No Choices", "No choices available for this world.")
            return

        items = [str(c.text)[:50] for c in world_choices]
        item, ok = QInputDialog.getItem(self, "Add Choice", "Select choice:", items, 0, False)

        if ok and item:
            selected_choice = world_choices[items.index(item)]
            self.selected_story.add_choice(selected_choice.id)
            self._refresh_choices_list()

    def _remove_choice(self):
        """Remove selected choice."""
        current_row = self.choices_list.currentRow()
        if current_row >= 0 and self.selected_story:
            choice_id = self.selected_story.choice_ids[current_row]
            self.selected_story.remove_choice(choice_id)
            self._refresh_choices_list()

    def _add_connection(self):
        """Add a world element connection to the story."""
        if not self.selected_story:
            QMessageBox.warning(self, "No Story Selected", "Please select a story first.")
            return

        # Build list of available entities
        available_entities = []

        # Add characters
        if hasattr(self.lore_data, 'characters'):
            for char in self.lore_data.characters:
                if char.world_id == self.selected_story.world_id and char.id not in self.selected_story.connected_world_ids:
                    available_entities.append(("Character", char.name, char.id))

        # Add items
        if hasattr(self.lore_data, 'items'):
            for item in self.lore_data.items:
                if item.world_id == self.selected_story.world_id and item.id not in self.selected_story.connected_world_ids:
                    available_entities.append(("Item", item.name, item.id))

        # Add events
        if hasattr(self.lore_data, 'events'):
            for event in self.lore_data.events:
                if event.world_id == self.selected_story.world_id and event.id not in self.selected_story.connected_world_ids:
                    available_entities.append(("Event", event.name, event.id))

        if not available_entities:
            QMessageBox.information(self, "No Entities", "No world elements available to connect.")
            return

        items = [f"{entity_type}: {name}" for entity_type, name, _ in available_entities]
        item, ok = QInputDialog.getItem(self, "Add Connection", "Select entity:", items, 0, False)

        if ok and item:
            _, _, entity_id = available_entities[items.index(item)]
            self.selected_story.connect_world_element(entity_id)
            self._refresh_connections_list()

    def _remove_connection(self):
        """Remove selected connection."""
        current_row = self.connections_list.currentRow()
        if current_row >= 0 and self.selected_story:
            element_id = self.selected_story.connected_world_ids[current_row]
            self.selected_story.disconnect_world_element(element_id)
            self._refresh_connections_list()

    def _add_story(self):
        """Add a new story."""
        try:
            if self.world_combo.currentData() is None:
                QMessageBox.warning(self, "Error", "Please select a world.")
                return

            world_id = EntityId(self.world_combo.currentData())
            story_type = StoryType(self.type_combo.currentData())

            story = Story.create(
                tenant_id=self.lore_data.tenant_id,
                world_id=world_id,
                name=StoryName(self.name_input.text()),
                description=self.description_input.toPlainText(),
                story_type=story_type,
                content=Content(self.content_input.toPlainText()),
                is_active=self.active_checkbox.isChecked()
            )

            if not hasattr(self.lore_data, 'stories'):
                self.lore_data.stories = []

            self.lore_data.stories.append(story)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Story created successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create story: {e}")

    def _update_story(self):
        """Update selected story."""
        if not self.selected_story:
            return

        try:
            # Update content
            new_content = Content(self.content_input.toPlainText())
            self.selected_story.update_content(new_content)

            # Update active status
            if self.active_checkbox.isChecked() and not self.selected_story.is_active:
                self.selected_story.activate()
            elif not self.active_checkbox.isChecked() and self.selected_story.is_active:
                self.selected_story.deactivate()

            self.refresh()
            QMessageBox.information(self, "Success", "Story updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update story: {e}")

    def _delete_story(self):
        """Delete selected story."""
        if not self.selected_story:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{self.selected_story.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self.lore_data, 'stories'):
                self.lore_data.stories.remove(self.selected_story)
            self.selected_story = None
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Story deleted successfully!")

    def _clear_form(self):
        """Clear the form fields."""
        self.name_input.clear()
        self.description_input.clear()
        self.content_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.active_checkbox.setChecked(True)
        self.choices_list.clear()
        self.connections_list.clear()
        self.selected_story = None
        self.update_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
