"""
RequirementTab - Tab for managing business requirements
"""
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.entities.requirement import Requirement
from src.domain.value_objects.common import TenantId, EntityId, EntityType


class RequirementTab(QWidget):
    """Tab for managing business requirements."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_requirement: Optional[Requirement] = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("📋 Requirements")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Requirements table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Type", "Entity ID", "Description", "Created"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Requirement Details")
        form_layout = QFormLayout()

        # Entity Type (optional)
        self.type_combo = QComboBox()
        self.type_combo.addItem("Global (all entities)", None)
        for entity_type in EntityType:
            self.type_combo.addItem(entity_type.value.title(), entity_type.value)
        form_layout.addRow("Entity Type:", self.type_combo)

        # Entity ID (optional)
        self.entity_id_input = QLineEdit()
        self.entity_id_input.setPlaceholderText("Entity ID (optional, leave empty for type-wide)")
        form_layout.addRow("Entity ID:", self.entity_id_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter the business rule/requirement...")
        self.description_input.setMaximumHeight(120)
        form_layout.addRow("Description:", self.description_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Info label
        info_label = QLabel(
            "Requirements define business rules that must be preserved.\n"
            "Examples: 'Character X cannot die before Event Y', 'Backstory must be >= 100 chars'"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-style: italic;")
        form_main_layout.addWidget(info_label)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Requirement")
        self.add_btn.clicked.connect(self._add_requirement)

        self.delete_btn = QPushButton("Delete Requirement")
        self.delete_btn.clicked.connect(self._delete_requirement)
        self.delete_btn.setEnabled(False)

        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.clicked.connect(self._clear_form)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        """Refresh the requirements table."""
        # Update requirements table
        self.table.setRowCount(0)
        for requirement in self.lore_data.requirements:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(requirement.id.value) if requirement.id else ""))

            # Type
            type_display = "Global" if requirement.entity_type is None else requirement.entity_type.value.title()
            self.table.setItem(row, 1, QTableWidgetItem(type_display))

            # Entity ID
            entity_id_display = str(requirement.entity_id.value) if requirement.entity_id else "-"
            self.table.setItem(row, 2, QTableWidgetItem(entity_id_display))

            # Description (preview)
            desc_preview = requirement.description[:100] + "..." if len(requirement.description) > 100 else requirement.description
            self.table.setItem(row, 3, QTableWidgetItem(desc_preview))

            # Created
            self.table.setItem(row, 4, QTableWidgetItem(requirement.created_at.value.strftime("%Y-%m-%d %H:%M")))

        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle requirement selection changes."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if len(selected_rows) == 1:
            row = list(selected_rows)[0]
            requirement_id = int(self.table.item(row, 0).text())
            self.selected_requirement = next((r for r in self.lore_data.requirements if r.id and r.id.value == requirement_id), None)
            if self.selected_requirement:
                self._populate_form()
                self.delete_btn.setEnabled(True)
            else:
                self._clear_form()
                self.delete_btn.setEnabled(False)
        else:
            self.selected_requirement = None
            self._clear_form()
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate form with selected requirement data."""
        if not self.selected_requirement:
            return

        # Set type
        if self.selected_requirement.entity_type is None:
            self.type_combo.setCurrentIndex(0)
        else:
            for i in range(1, self.type_combo.count()):
                if self.type_combo.itemData(i) == self.selected_requirement.entity_type.value:
                    self.type_combo.setCurrentIndex(i)
                    break

        # Set entity ID
        if self.selected_requirement.entity_id:
            self.entity_id_input.setText(str(self.selected_requirement.entity_id.value))
        else:
            self.entity_id_input.clear()

        # Set description
        self.description_input.setText(self.selected_requirement.description)

    def _clear_form(self):
        """Clear all form fields."""
        self.type_combo.setCurrentIndex(0)
        self.entity_id_input.clear()
        self.description_input.clear()

    def _add_requirement(self):
        """Add a new requirement."""
        try:
            # Validate inputs
            if not self.description_input.toPlainText().strip():
                QMessageBox.warning(self, "Validation Error", "Requirement description cannot be empty.")
                return

            # Get entity type
            entity_type = None
            if self.type_combo.currentData() is not None:
                entity_type = EntityType(self.type_combo.currentData())

            # Get entity ID
            entity_id = None
            if self.entity_id_input.text().strip():
                try:
                    entity_id = EntityId(int(self.entity_id_input.text().strip()))
                except ValueError:
                    QMessageBox.warning(self, "Validation Error", "Entity ID must be a valid number.")
                    return

            # Validate entity_type and entity_id pairing
            if (entity_type is None) != (entity_id is None):
                QMessageBox.warning(
                    self, "Validation Error",
                    "Entity Type and Entity ID must both be set or both be empty."
                )
                return

            # Create requirement
            requirement = Requirement.create(
                tenant_id=TenantId(1),
                description=self.description_input.toPlainText().strip(),
                entity_type=entity_type,
                entity_id=entity_id
            )

            self.lore_data.add_requirement(requirement)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Requirement added successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add requirement: {str(e)}")

    def _delete_requirement(self):
        """Delete the selected requirement."""
        if not self.selected_requirement:
            return

        desc_preview = self.selected_requirement.description[:50] + "..." if len(self.selected_requirement.description) > 50 else self.selected_requirement.description
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the requirement '{desc_preview}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.requirements.remove(self.selected_requirement)
                self.refresh()
                self._clear_form()
                QMessageBox.information(self, "Success", "Requirement deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete requirement: {str(e)}")
