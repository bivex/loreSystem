"""
TagsTab - Tab for managing visual tags for organization
"""
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QColorDialog, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from src.domain.entities.tag import Tag
from src.domain.value_objects.common import (
    TenantId, EntityId, TagName, TagType
)


class TagsTab(QWidget):
    """Tab for managing visual tags for content organization."""

    tag_selected = pyqtSignal(EntityId)

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_tag: Optional[Tag] = None
        self.selected_color: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("🏷️ Tags")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Tags table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Name", "Type", "Color", "Description", "Updated"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Tag Details")
        form_layout = QFormLayout()

        # World selection
        self.world_combo = QComboBox()
        form_layout.addRow("World:", self.world_combo)

        # Tag name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter tag name...")
        form_layout.addRow("Name:", self.name_input)

        # Tag type
        self.type_combo = QComboBox()
        self.type_combo.addItem("Category", TagType.CATEGORY.value)
        self.type_combo.addItem("Theme", TagType.THEME.value)
        self.type_combo.addItem("Status", TagType.STATUS.value)
        self.type_combo.addItem("Custom", TagType.CUSTOM.value)
        form_layout.addRow("Type:", self.type_combo)

        # Color picker
        color_layout = QHBoxLayout()
        self.color_display = QLineEdit()
        self.color_display.setReadOnly(True)
        self.color_display.setPlaceholderText("No color selected")
        self.color_display.setMaximumWidth(200)

        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self._choose_color)
        self.clear_color_btn = QPushButton("Clear Color")
        self.clear_color_btn.clicked.connect(self._clear_color)

        color_layout.addWidget(self.color_display)
        color_layout.addWidget(self.color_btn)
        color_layout.addWidget(self.clear_color_btn)
        color_layout.addStretch()
        form_layout.addRow("Color:", color_layout)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter tag description (optional)...")
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Usage statistics (read-only info)
        stats_group = QGroupBox("Tag Usage")
        stats_layout = QVBoxLayout()
        self.usage_label = QLabel("Select a tag to view usage statistics")
        self.usage_label.setStyleSheet("color: gray; font-style: italic;")
        stats_layout.addWidget(self.usage_label)
        stats_group.setLayout(stats_layout)
        form_main_layout.addWidget(stats_group)

        # Main action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Tag")
        self.add_btn.clicked.connect(self._add_tag)

        self.update_btn = QPushButton("Update Tag")
        self.update_btn.clicked.connect(self._update_tag)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Tag")
        self.delete_btn.clicked.connect(self._delete_tag)
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
        """Refresh the tags table and combo boxes."""
        # Refresh world combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(str(world.name), world.id.value)

        # Refresh table
        self.table.setRowCount(0)

        if not hasattr(self.lore_data, 'tags'):
            return

        for tag in self.lore_data.tags:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Get world name
            world = next((w for w in self.lore_data.worlds if w.id == tag.world_id), None)
            world_name = str(world.name) if world else f"ID: {tag.world_id.value}"

            # Create color item with background
            color_item = QTableWidgetItem(tag.color if tag.color else "None")
            if tag.color:
                color_item.setBackground(QColor(tag.color))
                # Set text color to white or black depending on background brightness
                bg_color = QColor(tag.color)
                brightness = (bg_color.red() * 299 + bg_color.green() * 587 + bg_color.blue() * 114) / 1000
                text_color = QColor("white") if brightness < 128 else QColor("black")
                color_item.setForeground(text_color)

            self.table.setItem(row, 0, QTableWidgetItem(str(tag.id.value) if tag.id else ""))
            self.table.setItem(row, 1, QTableWidgetItem(world_name))
            self.table.setItem(row, 2, QTableWidgetItem(str(tag.name)))
            self.table.setItem(row, 3, QTableWidgetItem(tag.tag_type.value.title()))
            self.table.setItem(row, 4, color_item)
            self.table.setItem(row, 5, QTableWidgetItem((tag.description or "")[:50]))
            self.table.setItem(row, 6, QTableWidgetItem(tag.updated_at.value.strftime("%Y-%m-%d %H:%M")))

        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle tag selection."""
        selected_items = self.table.selectedItems()
        if selected_items and hasattr(self.lore_data, 'tags'):
            row = selected_items[0].row()
            tag_id = EntityId(int(self.table.item(row, 0).text()))
            self.selected_tag = next((t for t in self.lore_data.tags if t.id == tag_id), None)

            if self.selected_tag:
                # Update form fields
                # Find and set world
                for i in range(self.world_combo.count()):
                    if self.world_combo.itemData(i) == self.selected_tag.world_id.value:
                        self.world_combo.setCurrentIndex(i)
                        break

                self.name_input.setText(str(self.selected_tag.name))
                self.description_input.setPlainText(self.selected_tag.description or "")

                # Set type
                for i in range(self.type_combo.count()):
                    if self.type_combo.itemData(i) == self.selected_tag.tag_type.value:
                        self.type_combo.setCurrentIndex(i)
                        break

                # Set color
                self.selected_color = self.selected_tag.color
                if self.selected_color:
                    self.color_display.setText(self.selected_color)
                    self.color_display.setStyleSheet(f"background-color: {self.selected_color};")
                else:
                    self.color_display.clear()
                    self.color_display.setStyleSheet("")

                # Update usage statistics
                self._update_usage_stats()

                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.tag_selected.emit(tag_id)
        else:
            self.selected_tag = None
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _update_usage_stats(self):
        """Update tag usage statistics."""
        if not self.selected_tag:
            self.usage_label.setText("Select a tag to view usage statistics")
            return

        usage_count = 0
        usage_details = []

        # Count pages using this tag
        if hasattr(self.lore_data, 'pages'):
            pages_with_tag = [p for p in self.lore_data.pages if self.selected_tag.id in p.tag_ids]
            if pages_with_tag:
                usage_count += len(pages_with_tag)
                usage_details.append(f"Pages: {len(pages_with_tag)}")

        if usage_count == 0:
            self.usage_label.setText("This tag is not currently used")
        else:
            self.usage_label.setText(f"Used {usage_count} time(s): {', '.join(usage_details)}")

    def _choose_color(self):
        """Open color picker dialog."""
        # Start with current color if available
        initial_color = QColor(self.selected_color) if self.selected_color else QColor("white")

        color = QColorDialog.getColor(initial_color, self, "Choose Tag Color")
        if color.isValid():
            self.selected_color = color.name()
            self.color_display.setText(self.selected_color)
            self.color_display.setStyleSheet(f"background-color: {self.selected_color};")

    def _clear_color(self):
        """Clear the selected color."""
        self.selected_color = None
        self.color_display.clear()
        self.color_display.setStyleSheet("")

    def _add_tag(self):
        """Add a new tag."""
        try:
            if self.world_combo.currentData() is None:
                QMessageBox.warning(self, "Error", "Please select a world.")
                return

            world_id = EntityId(self.world_combo.currentData())
            tag_type = TagType(self.type_combo.currentData())
            description = self.description_input.toPlainText().strip()

            tag = Tag.create(
                tenant_id=self.lore_data.tenant_id,
                world_id=world_id,
                name=TagName(self.name_input.text()),
                tag_type=tag_type,
                color=self.selected_color,
                description=description if description else None
            )

            if not hasattr(self.lore_data, 'tags'):
                self.lore_data.tags = []

            self.lore_data.tags.append(tag)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Tag created successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create tag: {e}")

    def _update_tag(self):
        """Update selected tag."""
        if not self.selected_tag:
            return

        try:
            # Update color
            self.selected_tag.update_color(self.selected_color)

            # Update description
            description = self.description_input.toPlainText().strip()
            self.selected_tag.update_description(description if description else None)

            self.refresh()
            QMessageBox.information(self, "Success", "Tag updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update tag: {e}")

    def _delete_tag(self):
        """Delete selected tag."""
        if not self.selected_tag:
            return

        # Check if tag is being used
        if hasattr(self.lore_data, 'pages'):
            pages_with_tag = [p for p in self.lore_data.pages if self.selected_tag.id in p.tag_ids]
            if pages_with_tag:
                reply = QMessageBox.question(
                    self, "Tag In Use",
                    f"This tag is used by {len(pages_with_tag)} page(s). "
                    f"Deleting it will remove it from those pages. Continue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

                # Remove tag from all pages
                for page in pages_with_tag:
                    page.remove_tag(self.selected_tag.id)

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete tag '{self.selected_tag.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self.lore_data, 'tags'):
                self.lore_data.tags.remove(self.selected_tag)
            self.selected_tag = None
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Tag deleted successfully!")

    def _clear_form(self):
        """Clear the form fields."""
        self.name_input.clear()
        self.description_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.selected_color = None
        self.color_display.clear()
        self.color_display.setStyleSheet("")
        self.usage_label.setText("Select a tag to view usage statistics")
        self.selected_tag = None
        self.update_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
