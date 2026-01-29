"""
TemplatesTab - Tab for managing page templates and runes
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QListWidget, QInputDialog, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.domain.entities.template import Template
from src.domain.value_objects.common import (
    TenantId, EntityId, TemplateName, Content, TemplateType
)


class TemplatesTab(QWidget):
    """Tab for managing templates (page templates and runes)."""

    template_selected = pyqtSignal(EntityId)

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_template: Optional[Template] = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("📐 Templates")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Templates table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Name", "Type", "Runes", "Updated"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Template Details")
        form_layout = QFormLayout()

        # World selection
        self.world_combo = QComboBox()
        form_layout.addRow("World:", self.world_combo)

        # Template name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter template name...")
        form_layout.addRow("Name:", self.name_input)

        # Template type
        self.type_combo = QComboBox()
        self.type_combo.addItem("Page Template", TemplateType.PAGE.value)
        self.type_combo.addItem("Rune (Sub-template)", TemplateType.RUNE.value)
        form_layout.addRow("Type:", self.type_combo)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter template description...")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)

        # Content/Structure editor
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Enter template structure/content...")
        self.content_input.setMinimumHeight(150)
        form_layout.addRow("Template Content:", self.content_input)

        # Parent template selection
        self.parent_template_combo = QComboBox()
        self.parent_template_combo.addItem("None", None)
        form_layout.addRow("Parent Template:", self.parent_template_combo)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Runes section
        runes_group = QGroupBox("Runes (Sub-templates)")
        runes_layout = QVBoxLayout()

        self.runes_list = QListWidget()
        self.runes_list.setMaximumHeight(100)
        runes_layout.addWidget(self.runes_list)

        runes_btn_layout = QHBoxLayout()
        self.add_rune_btn = QPushButton("Add Rune")
        self.add_rune_btn.clicked.connect(self._add_rune)
        self.remove_rune_btn = QPushButton("Remove Rune")
        self.remove_rune_btn.clicked.connect(self._remove_rune)
        runes_btn_layout.addWidget(self.add_rune_btn)
        runes_btn_layout.addWidget(self.remove_rune_btn)
        runes_btn_layout.addStretch()
        runes_layout.addLayout(runes_btn_layout)

        runes_group.setLayout(runes_layout)
        form_main_layout.addWidget(runes_group)

        # Main action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Template")
        self.add_btn.clicked.connect(self._add_template)

        self.update_btn = QPushButton("Update Template")
        self.update_btn.clicked.connect(self._update_template)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Template")
        self.delete_btn.clicked.connect(self._delete_template)
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
        """Refresh the templates table and combo boxes."""
        # Refresh world combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(str(world.name), world.id.value)

        # Refresh parent template combo
        self.parent_template_combo.clear()
        self.parent_template_combo.addItem("None", None)
        if hasattr(self.lore_data, 'templates'):
            for template in self.lore_data.templates:
                if template.template_type == TemplateType.PAGE:
                    if self.selected_template is None or template.id != self.selected_template.id:
                        self.parent_template_combo.addItem(str(template.name), template.id.value)

        # Refresh table
        self.table.setRowCount(0)

        if not hasattr(self.lore_data, 'templates'):
            return

        # Ensure all templates have IDs
        for template in self.lore_data.templates:
            if template.id is None:
                object.__setattr__(template, 'id', self.lore_data.get_next_id())

        for template in self.lore_data.templates:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Get world name
            world = next((w for w in self.lore_data.worlds if w.id == template.world_id), None)
            world_name = str(world.name) if world else f"ID: {template.world_id.value}"

            self.table.setItem(row, 0, QTableWidgetItem(str(template.id.value)))
            self.table.setItem(row, 1, QTableWidgetItem(world_name))
            self.table.setItem(row, 2, QTableWidgetItem(str(template.name)))
            self.table.setItem(row, 3, QTableWidgetItem(template.template_type.value.title()))
            self.table.setItem(row, 4, QTableWidgetItem(str(len(template.rune_ids))))
            self.table.setItem(row, 5, QTableWidgetItem(template.updated_at.value.strftime("%Y-%m-%d %H:%M")))

        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle template selection."""
        selected_items = self.table.selectedItems()
        if selected_items and hasattr(self.lore_data, 'templates'):
            row = selected_items[0].row()
            template_id = EntityId(int(self.table.item(row, 0).text()))
            self.selected_template = next((t for t in self.lore_data.templates if t.id == template_id), None)

            if self.selected_template:
                # Update form fields
                # Find and set world
                for i in range(self.world_combo.count()):
                    if self.world_combo.itemData(i) == self.selected_template.world_id.value:
                        self.world_combo.setCurrentIndex(i)
                        break

                self.name_input.setText(str(self.selected_template.name))
                self.description_input.setPlainText(self.selected_template.description)
                self.content_input.setPlainText(str(self.selected_template.content))

                # Set type
                for i in range(self.type_combo.count()):
                    if self.type_combo.itemData(i) == self.selected_template.template_type.value:
                        self.type_combo.setCurrentIndex(i)
                        break

                # Set parent template
                if self.selected_template.parent_template_id:
                    for i in range(self.parent_template_combo.count()):
                        if self.parent_template_combo.itemData(i) == self.selected_template.parent_template_id.value:
                            self.parent_template_combo.setCurrentIndex(i)
                            break
                else:
                    self.parent_template_combo.setCurrentIndex(0)

                self._refresh_runes_list()

                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.template_selected.emit(template_id)
        else:
            self.selected_template = None
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _refresh_runes_list(self):
        """Refresh runes list widget."""
        self.runes_list.clear()
        if self.selected_template and hasattr(self.lore_data, 'templates'):
            for rune_id in self.selected_template.rune_ids:
                rune = next((t for t in self.lore_data.templates if t.id == rune_id), None)
                name = str(rune.name) if rune else f"Unknown (ID: {rune_id.value})"
                self.runes_list.addItem(name)

    def _add_rune(self):
        """Add a rune to the template."""
        if not self.selected_template:
            QMessageBox.warning(self, "No Template Selected", "Please select a template first.")
            return

        if self.selected_template.template_type == TemplateType.RUNE:
            QMessageBox.warning(self, "Invalid Operation", "Runes cannot contain other runes.")
            return

        if not hasattr(self.lore_data, 'templates'):
            QMessageBox.information(self, "No Templates", "No templates available.")
            return

        # Get available runes
        available_runes = [t for t in self.lore_data.templates
                          if t.template_type == TemplateType.RUNE
                          and t.world_id == self.selected_template.world_id
                          and t.id not in self.selected_template.rune_ids]

        if not available_runes:
            QMessageBox.information(self, "No Runes", "No rune templates available.")
            return

        items = [str(r.name) for r in available_runes]
        item, ok = QInputDialog.getItem(self, "Add Rune", "Select rune:", items, 0, False)

        if ok and item:
            selected_rune = next(r for r in available_runes if str(r.name) == item)
            self.selected_template.add_rune(selected_rune.id)
            self._refresh_runes_list()

    def _remove_rune(self):
        """Remove selected rune."""
        current_row = self.runes_list.currentRow()
        if current_row >= 0 and self.selected_template:
            rune_id = self.selected_template.rune_ids[current_row]
            self.selected_template.remove_rune(rune_id)
            self._refresh_runes_list()

    def _add_template(self):
        """Add a new template."""
        try:
            if self.world_combo.currentData() is None:
                QMessageBox.warning(self, "Error", "Please select a world.")
                return

            world_id = EntityId(self.world_combo.currentData())
            template_type = TemplateType(self.type_combo.currentData())
            parent_template_id = EntityId(self.parent_template_combo.currentData()) if self.parent_template_combo.currentData() else None

            template = Template.create(
                tenant_id=self.lore_data.tenant_id,
                world_id=world_id,
                name=TemplateName(self.name_input.text()),
                description=self.description_input.toPlainText(),
                template_type=template_type,
                content=Content(self.content_input.toPlainText()),
                parent_template_id=parent_template_id
            )

            self.lore_data.add_template(template)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Template created successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create template: {e}")

    def _update_template(self):
        """Update selected template."""
        if not self.selected_template:
            return

        try:
            # Update content
            new_content = Content(self.content_input.toPlainText())
            self.selected_template.update_content(new_content)

            # Note: Updating description, type, and parent requires reconstruction
            # For now, we'll just update content. Full update can be done via delete + add

            self.refresh()
            QMessageBox.information(self, "Success", "Template updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update template: {e}")

    def _delete_template(self):
        """Delete selected template."""
        if not self.selected_template:
            return

        # Check if template is being used
        if hasattr(self.lore_data, 'pages'):
            pages_using_template = [p for p in self.lore_data.pages if p.template_id == self.selected_template.id]
            if pages_using_template:
                QMessageBox.warning(
                    self, "Cannot Delete",
                    f"This template is being used by {len(pages_using_template)} page(s). Remove the template from those pages first."
                )
                return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{self.selected_template.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self.lore_data, 'templates'):
                self.lore_data.templates.remove(self.selected_template)
            self.selected_template = None
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Template deleted successfully!")

    def _clear_form(self):
        """Clear the form fields."""
        self.name_input.clear()
        self.description_input.clear()
        self.content_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.parent_template_combo.setCurrentIndex(0)
        self.runes_list.clear()
        self.selected_template = None
        self.update_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
