"""
NoteTab - Tab for managing notes
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.entities.note import Note
from src.domain.value_objects.common import (
    TenantId, EntityId
)


class NoteTab(QWidget):
    """Tab for managing notes."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_note: Optional[Note] = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("📝 Notes")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Notes table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Title", "Content Preview", "Tags", "Pinned", "Updated"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Note Details")
        form_layout = QFormLayout()

        # World selection
        self.world_combo = QComboBox()
        form_layout.addRow("World:", self.world_combo)

        # Note title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter note title...")
        form_layout.addRow("Title:", self.title_input)

        # Note content
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Enter note content...")
        self.content_input.setMaximumHeight(150)
        form_layout.addRow("Content:", self.content_input)

        # Tags
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("tag1, tag2, tag3 (comma-separated)")
        form_layout.addRow("Tags:", self.tags_input)

        # Pinned checkbox
        self.pinned_check = QCheckBox("Pin this note for quick access")
        form_layout.addRow("", self.pinned_check)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Main action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Note")
        self.add_btn.clicked.connect(self._add_note)

        self.update_btn = QPushButton("Update Note")
        self.update_btn.clicked.connect(self._update_note)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Note")
        self.delete_btn.clicked.connect(self._delete_note)
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
        """Refresh the notes table and combo boxes."""
        # Update worlds combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(f"{world.name.value}", world.id.value)

        # Update notes table
        self.table.setRowCount(0)
        for note in self.lore_data.notes:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(note.id.value) if note.id else ""))

            # World
            world_name = "Unknown"
            for world in self.lore_data.worlds:
                if world.id == note.world_id:
                    world_name = world.name.value
                    break
            self.table.setItem(row, 1, QTableWidgetItem(world_name))

            # Title
            self.table.setItem(row, 2, QTableWidgetItem(note.title))

            # Content Preview (first 50 chars)
            preview = note.content[:50] + "..." if len(note.content) > 50 else note.content
            self.table.setItem(row, 3, QTableWidgetItem(preview))

            # Tags
            self.table.setItem(row, 4, QTableWidgetItem(", ".join(note.tags)))

            # Pinned
            self.table.setItem(row, 5, QTableWidgetItem("📌" if note.is_pinned else ""))

            # Updated
            self.table.setItem(row, 6, QTableWidgetItem(note.updated_at.value.strftime("%Y-%m-%d %H:%M")))

        # Resize columns to content
        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle note selection changes."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if len(selected_rows) == 1:
            row = list(selected_rows)[0]
            note_id = int(self.table.item(row, 0).text())
            self.selected_note = next((n for n in self.lore_data.notes if n.id and n.id.value == note_id), None)
            if self.selected_note:
                self._populate_form()
                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
            else:
                self._clear_form()
                self.update_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
        else:
            self.selected_note = None
            self._clear_form()
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate form with selected note data."""
        if not self.selected_note:
            return

        # Set world
        for i in range(self.world_combo.count()):
            if self.world_combo.itemData(i) == self.selected_note.world_id.value:
                self.world_combo.setCurrentIndex(i)
                break

        # Set other fields
        self.title_input.setText(self.selected_note.title)
        self.content_input.setText(self.selected_note.content)
        self.tags_input.setText(", ".join(self.selected_note.tags))
        self.pinned_check.setChecked(self.selected_note.is_pinned)

    def _clear_form(self):
        """Clear all form fields."""
        self.title_input.clear()
        self.content_input.clear()
        self.tags_input.clear()
        self.pinned_check.setChecked(False)
        if self.world_combo.count() > 0:
            self.world_combo.setCurrentIndex(0)

    def _add_note(self):
        """Add a new note."""
        try:
            # Validate inputs
            if not self.title_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Note title cannot be empty.")
                return

            if not self.content_input.toPlainText().strip():
                QMessageBox.warning(self, "Validation Error", "Note content cannot be empty.")
                return

            if self.world_combo.currentData() is None:
                QMessageBox.warning(self, "Validation Error", "Please select a world.")
                return

            # Parse tags
            tags = [tag.strip() for tag in self.tags_input.text().split(",") if tag.strip()]

            # Create note
            note = Note.create(
                tenant_id=TenantId(1),
                world_id=EntityId(self.world_combo.currentData()),
                title=self.title_input.text().strip(),
                content=self.content_input.toPlainText().strip(),
                tags=tags,
                is_pinned=self.pinned_check.isChecked()
            )

            self.lore_data.add_note(note)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Note added successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add note: {str(e)}")

    def _update_note(self):
        """Update the selected note."""
        if not self.selected_note:
            return

        try:
            # Validate inputs
            if not self.title_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Note title cannot be empty.")
                return

            if not self.content_input.toPlainText().strip():
                QMessageBox.warning(self, "Validation Error", "Note content cannot be empty.")
                return

            # Update note
            self.selected_note.update_title(self.title_input.text().strip())
            self.selected_note.update_content(self.content_input.toPlainText().strip())

            # Update tags (direct attribute modification for simplicity)
            tags = [tag.strip() for tag in self.tags_input.text().split(",") if tag.strip()]
            object.__setattr__(self.selected_note, 'tags', tags)

            # Update pinned status
            object.__setattr__(self.selected_note, 'is_pinned', self.pinned_check.isChecked())
            object.__setattr__(self.selected_note, 'updated_at', self.selected_note.updated_at.__class__.now())
            object.__setattr__(self.selected_note, 'version', self.selected_note.version.increment())

            self.refresh()
            QMessageBox.information(self, "Success", "Note updated successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update note: {str(e)}")

    def _delete_note(self):
        """Delete the selected note."""
        if not self.selected_note:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the note '{self.selected_note.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.notes.remove(self.selected_note)
                self.refresh()
                self._clear_form()
                QMessageBox.information(self, "Success", "Note deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete note: {str(e)}")