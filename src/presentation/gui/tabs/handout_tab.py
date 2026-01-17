"""
HandoutTab - Tab for managing session handouts
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.entities.handout import Handout
from src.domain.value_objects.common import (
    TenantId, EntityId
)


class HandoutTab(QWidget):
    """Tab for managing session handouts."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_handout: Optional[Handout] = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("📄 Handouts")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Handouts table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Title", "Content Preview", "Images", "Session", "Revealed", "Reveal Timing", "Updated"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Handout Details")
        form_layout = QFormLayout()

        # World selection
        self.world_combo = QComboBox()
        form_layout.addRow("World:", self.world_combo)

        # Handout title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter handout title...")
        form_layout.addRow("Title:", self.title_input)

        # Handout content
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Enter handout content...")
        self.content_input.setMaximumHeight(150)
        form_layout.addRow("Content:", self.content_input)

        # Images (comma-separated IDs)
        self.images_input = QLineEdit()
        self.images_input.setPlaceholderText("image_id1, image_id2 (comma-separated)")
        form_layout.addRow("Image IDs:", self.images_input)

        # Session selection
        self.session_combo = QComboBox()
        self.session_combo.addItem("None", None)  # No session selected
        form_layout.addRow("Session:", self.session_combo)

        # Revealed checkbox
        self.revealed_check = QCheckBox("Handout has been revealed to players")
        form_layout.addRow("", self.revealed_check)

        # Reveal timing
        self.reveal_timing_input = QLineEdit()
        self.reveal_timing_input.setPlaceholderText("e.g., 'During combat', 'At session end'...")
        form_layout.addRow("Reveal Timing:", self.reveal_timing_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Main action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Handout")
        self.add_btn.clicked.connect(self._add_handout)

        self.update_btn = QPushButton("Update Handout")
        self.update_btn.clicked.connect(self._update_handout)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Handout")
        self.delete_btn.clicked.connect(self._delete_handout)
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
        """Refresh the handouts table and combo boxes."""
        # Update worlds combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(f"{world.name.value}", world.id.value)

        # Update sessions combo
        self.session_combo.clear()
        self.session_combo.addItem("None", None)
        for session in self.lore_data.sessions:
            self.session_combo.addItem(f"Session {session.id.value if session.id else 'New'}", session.id.value if session.id else None)

        # Update handouts table
        self.table.setRowCount(0)
        for handout in self.lore_data.handouts:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(handout.id.value) if handout.id else ""))

            # World
            world_name = "Unknown"
            for world in self.lore_data.worlds:
                if world.id == handout.world_id:
                    world_name = world.name.value
                    break
            self.table.setItem(row, 1, QTableWidgetItem(world_name))

            # Title
            self.table.setItem(row, 2, QTableWidgetItem(handout.title))

            # Content Preview (first 50 chars)
            preview = handout.content[:50] + "..." if handout.content and len(handout.content) > 50 else (handout.content or "")
            self.table.setItem(row, 3, QTableWidgetItem(preview))

            # Images
            images_str = ", ".join(str(img_id.value) for img_id in handout.image_ids)
            self.table.setItem(row, 4, QTableWidgetItem(images_str))

            # Session
            session_name = "None"
            if handout.session_id:
                for session in self.lore_data.sessions:
                    if session.id == handout.session_id:
                        session_name = f"Session {session.id.value}"
                        break
            self.table.setItem(row, 5, QTableWidgetItem(session_name))

            # Revealed
            self.table.setItem(row, 6, QTableWidgetItem("✅" if handout.is_revealed else "❌"))

            # Reveal Timing
            self.table.setItem(row, 7, QTableWidgetItem(handout.reveal_timing or ""))

            # Updated
            self.table.setItem(row, 8, QTableWidgetItem(handout.updated_at.value.strftime("%Y-%m-%d %H:%M")))

        # Resize columns to content
        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle handout selection changes."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if len(selected_rows) == 1:
            row = list(selected_rows)[0]
            handout_id = int(self.table.item(row, 0).text())
            self.selected_handout = next((h for h in self.lore_data.handouts if h.id and h.id.value == handout_id), None)
            if self.selected_handout:
                self._populate_form()
                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
            else:
                self._clear_form()
                self.update_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
        else:
            self.selected_handout = None
            self._clear_form()
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate form with selected handout data."""
        if not self.selected_handout:
            return

        # Set world
        for i in range(self.world_combo.count()):
            if self.world_combo.itemData(i) == self.selected_handout.world_id.value:
                self.world_combo.setCurrentIndex(i)
                break

        # Set session
        session_index = 0  # Default to "None"
        if self.selected_handout.session_id:
            for i in range(1, self.session_combo.count()):  # Skip "None" at index 0
                if self.session_combo.itemData(i) == self.selected_handout.session_id.value:
                    session_index = i
                    break
        self.session_combo.setCurrentIndex(session_index)

        # Set other fields
        self.title_input.setText(self.selected_handout.title)
        self.content_input.setText(self.selected_handout.content or "")
        self.images_input.setText(", ".join(str(img_id.value) for img_id in self.selected_handout.image_ids))
        self.revealed_check.setChecked(self.selected_handout.is_revealed)
        self.reveal_timing_input.setText(self.selected_handout.reveal_timing or "")

    def _clear_form(self):
        """Clear all form fields."""
        self.title_input.clear()
        self.content_input.clear()
        self.images_input.clear()
        self.reveal_timing_input.clear()
        self.revealed_check.setChecked(False)
        if self.world_combo.count() > 0:
            self.world_combo.setCurrentIndex(0)
        if self.session_combo.count() > 0:
            self.session_combo.setCurrentIndex(0)

    def _add_handout(self):
        """Add a new handout."""
        try:
            # Validate inputs
            if not self.title_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Handout title cannot be empty.")
                return

            content = self.content_input.toPlainText().strip()
            images_str = self.images_input.text().strip()
            if not content and not images_str:
                QMessageBox.warning(self, "Validation Error", "Handout must have content or attached images.")
                return

            if self.world_combo.currentData() is None:
                QMessageBox.warning(self, "Validation Error", "Please select a world.")
                return

            # Parse image IDs
            image_ids = []
            if images_str:
                for img_str in images_str.split(","):
                    img_id_str = img_str.strip()
                    if img_id_str:
                        try:
                            image_ids.append(EntityId(int(img_id_str)))
                        except ValueError:
                            QMessageBox.warning(self, "Validation Error", f"Invalid image ID: {img_id_str}")
                            return

            # Get session ID
            session_id = None
            if self.session_combo.currentData() is not None:
                session_id = EntityId(self.session_combo.currentData())

            # Create handout
            handout = Handout.create(
                tenant_id=TenantId(1),
                world_id=EntityId(self.world_combo.currentData()),
                title=self.title_input.text().strip(),
                content=content if content else None,
                image_ids=image_ids,
                session_id=session_id,
                reveal_timing=self.reveal_timing_input.text().strip() or None,
                is_revealed=self.revealed_check.isChecked()
            )

            self.lore_data.add_handout(handout)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Handout added successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add handout: {str(e)}")

    def _update_handout(self):
        """Update the selected handout."""
        if not self.selected_handout:
            return

        try:
            # Validate inputs
            if not self.title_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Handout title cannot be empty.")
                return

            content = self.content_input.toPlainText().strip()
            images_str = self.images_input.text().strip()
            if not content and not images_str:
                QMessageBox.warning(self, "Validation Error", "Handout must have content or attached images.")
                return

            # Update title (direct attribute modification)
            object.__setattr__(self.selected_handout, 'title', self.title_input.text().strip())

            # Update content
            self.selected_handout.update_content(content if content else None)

            # Update images
            image_ids = []
            if images_str:
                for img_str in images_str.split(","):
                    img_id_str = img_str.strip()
                    if img_id_str:
                        try:
                            image_ids.append(EntityId(int(img_id_str)))
                        except ValueError:
                            QMessageBox.warning(self, "Validation Error", f"Invalid image ID: {img_id_str}")
                            return

            # Update image_ids (direct modification)
            object.__setattr__(self.selected_handout, 'image_ids', image_ids)

            # Update session_id
            session_id = None
            if self.session_combo.currentData() is not None:
                session_id = EntityId(self.session_combo.currentData())
            object.__setattr__(self.selected_handout, 'session_id', session_id)

            # Update revealed status
            if self.revealed_check.isChecked() and not self.selected_handout.is_revealed:
                self.selected_handout.reveal()
            elif not self.revealed_check.isChecked() and self.selected_handout.is_revealed:
                self.selected_handout.unreveal()

            # Update reveal timing
            object.__setattr__(self.selected_handout, 'reveal_timing', self.reveal_timing_input.text().strip() or None)
            object.__setattr__(self.selected_handout, 'updated_at', self.selected_handout.updated_at.__class__.now())
            object.__setattr__(self.selected_handout, 'version', self.selected_handout.version.increment())

            self.refresh()
            QMessageBox.information(self, "Success", "Handout updated successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update handout: {str(e)}")

    def _delete_handout(self):
        """Delete the selected handout."""
        if not self.selected_handout:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the handout '{self.selected_handout.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.handouts.remove(self.selected_handout)
                self.refresh()
                self._clear_form()
                QMessageBox.information(self, "Success", "Handout deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete handout: {str(e)}")