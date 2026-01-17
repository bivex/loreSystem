"""
InspirationTab - Tab for managing creative inspiration
"""
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.entities.inspiration import Inspiration
from src.domain.value_objects.common import TenantId, EntityId


class InspirationTab(QWidget):
    """Tab for managing creative inspiration."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_inspiration: Optional[Inspiration] = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("💡 Inspiration")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Inspirations table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Title", "Category", "Tags", "Source", "Used", "Updated"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Inspiration Details")
        form_layout = QFormLayout()

        # World selection
        self.world_combo = QComboBox()
        form_layout.addRow("World:", self.world_combo)

        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter inspiration title...")
        form_layout.addRow("Title:", self.title_input)

        # Content
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("The inspiration content/prompt...")
        self.content_input.setMaximumHeight(120)
        form_layout.addRow("Content:", self.content_input)

        # Category
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Plot, Character, Setting, etc.")
        form_layout.addRow("Category:", self.category_input)

        # Tags
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("tag1, tag2, tag3 (comma-separated)")
        form_layout.addRow("Tags:", self.tags_input)

        # Source
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("Where this inspiration came from (optional)")
        form_layout.addRow("Source:", self.source_input)

        # Used checkbox
        self.used_check = QCheckBox("This inspiration has been used")
        form_layout.addRow("", self.used_check)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Inspiration")
        self.add_btn.clicked.connect(self._add_inspiration)

        self.update_btn = QPushButton("Update Inspiration")
        self.update_btn.clicked.connect(self._update_inspiration)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Inspiration")
        self.delete_btn.clicked.connect(self._delete_inspiration)
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
        """Refresh the inspirations table and combo boxes."""
        # Update worlds combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(f"{world.name.value}", world.id.value)

        # Update inspirations table
        self.table.setRowCount(0)
        for inspiration in self.lore_data.inspirations:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(inspiration.id.value) if inspiration.id else ""))

            # World
            world_name = "Unknown"
            for world in self.lore_data.worlds:
                if world.id == inspiration.world_id:
                    world_name = world.name.value
                    break
            self.table.setItem(row, 1, QTableWidgetItem(world_name))

            # Title
            self.table.setItem(row, 2, QTableWidgetItem(inspiration.title))

            # Category
            self.table.setItem(row, 3, QTableWidgetItem(inspiration.category))

            # Tags
            self.table.setItem(row, 4, QTableWidgetItem(", ".join(inspiration.tags)))

            # Source
            self.table.setItem(row, 5, QTableWidgetItem(inspiration.source or ""))

            # Used
            self.table.setItem(row, 6, QTableWidgetItem("✅" if inspiration.is_used else ""))

            # Updated
            self.table.setItem(row, 7, QTableWidgetItem(inspiration.updated_at.value.strftime("%Y-%m-%d %H:%M")))

        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle inspiration selection changes."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if len(selected_rows) == 1:
            row = list(selected_rows)[0]
            inspiration_id = int(self.table.item(row, 0).text())
            self.selected_inspiration = next((i for i in self.lore_data.inspirations if i.id and i.id.value == inspiration_id), None)
            if self.selected_inspiration:
                self._populate_form()
                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
            else:
                self._clear_form()
                self.update_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
        else:
            self.selected_inspiration = None
            self._clear_form()
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate form with selected inspiration data."""
        if not self.selected_inspiration:
            return

        # Set world
        for i in range(self.world_combo.count()):
            if self.world_combo.itemData(i) == self.selected_inspiration.world_id.value:
                self.world_combo.setCurrentIndex(i)
                break

        # Set fields
        self.title_input.setText(self.selected_inspiration.title)
        self.content_input.setText(self.selected_inspiration.content)
        self.category_input.setText(self.selected_inspiration.category)
        self.tags_input.setText(", ".join(self.selected_inspiration.tags))
        self.source_input.setText(self.selected_inspiration.source or "")
        self.used_check.setChecked(self.selected_inspiration.is_used)

    def _clear_form(self):
        """Clear all form fields."""
        self.title_input.clear()
        self.content_input.clear()
        self.category_input.clear()
        self.tags_input.clear()
        self.source_input.clear()
        self.used_check.setChecked(False)
        if self.world_combo.count() > 0:
            self.world_combo.setCurrentIndex(0)

    def _add_inspiration(self):
        """Add a new inspiration."""
        try:
            # Validate inputs
            if not self.title_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Inspiration title cannot be empty.")
                return

            if not self.content_input.toPlainText().strip():
                QMessageBox.warning(self, "Validation Error", "Inspiration content cannot be empty.")
                return

            if not self.category_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Category cannot be empty.")
                return

            if self.world_combo.currentData() is None:
                QMessageBox.warning(self, "Validation Error", "Please select a world.")
                return

            # Parse tags
            tags = [tag.strip() for tag in self.tags_input.text().split(",") if tag.strip()]

            # Create inspiration
            inspiration = Inspiration.create(
                tenant_id=TenantId(1),
                world_id=EntityId(self.world_combo.currentData()),
                title=self.title_input.text().strip(),
                content=self.content_input.toPlainText().strip(),
                category=self.category_input.text().strip(),
                tags=tags,
                source=self.source_input.text().strip() or None,
                is_used=self.used_check.isChecked()
            )

            self.lore_data.add_inspiration(inspiration)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Inspiration added successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add inspiration: {str(e)}")

    def _update_inspiration(self):
        """Update the selected inspiration."""
        if not self.selected_inspiration:
            return

        try:
            # Validate inputs
            if not self.title_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Inspiration title cannot be empty.")
                return

            if not self.content_input.toPlainText().strip():
                QMessageBox.warning(self, "Validation Error", "Inspiration content cannot be empty.")
                return

            if not self.category_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Category cannot be empty.")
                return

            # Update inspiration
            object.__setattr__(self.selected_inspiration, 'title', self.title_input.text().strip())
            self.selected_inspiration.update_content(self.content_input.toPlainText().strip())
            object.__setattr__(self.selected_inspiration, 'category', self.category_input.text().strip())

            # Parse tags
            tags = [tag.strip() for tag in self.tags_input.text().split(",") if tag.strip()]
            object.__setattr__(self.selected_inspiration, 'tags', tags)

            # Update source
            object.__setattr__(self.selected_inspiration, 'source', self.source_input.text().strip() or None)

            # Update used status
            if self.used_check.isChecked() and not self.selected_inspiration.is_used:
                self.selected_inspiration.mark_used()
            elif not self.used_check.isChecked() and self.selected_inspiration.is_used:
                self.selected_inspiration.mark_unused()

            # Update metadata
            object.__setattr__(self.selected_inspiration, 'updated_at', self.selected_inspiration.updated_at.__class__.now())
            object.__setattr__(self.selected_inspiration, 'version', self.selected_inspiration.version.increment())

            self.refresh()
            QMessageBox.information(self, "Success", "Inspiration updated successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update inspiration: {str(e)}")

    def _delete_inspiration(self):
        """Delete the selected inspiration."""
        if not self.selected_inspiration:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the inspiration '{self.selected_inspiration.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.inspirations.remove(self.selected_inspiration)
                self.refresh()
                self._clear_form()
                QMessageBox.information(self, "Success", "Inspiration deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete inspiration: {str(e)}")
