"""
PagesTab - Tab for managing lore pages with templates and rich content
"""
from typing import Optional, List
from datetime import datetime, timezone

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QListWidget, QInputDialog, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.domain.entities.page import Page
from src.domain.value_objects.common import (
    TenantId, EntityId, PageName, Content, Version, Timestamp
)


class PagesTab(QWidget):
    """Tab for managing pages with template support."""

    page_selected = pyqtSignal(EntityId)

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_page: Optional[Page] = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("📄 Pages")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Pages table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Name", "Template", "Tags", "Images", "Updated"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Page Details")
        form_layout = QFormLayout()

        # World selection
        self.world_combo = QComboBox()
        form_layout.addRow("World:", self.world_combo)

        # Page name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter page name...")
        form_layout.addRow("Name:", self.name_input)

        # Template selection
        self.template_combo = QComboBox()
        self.template_combo.addItem("None", None)
        form_layout.addRow("Template:", self.template_combo)

        # Parent page selection
        self.parent_combo = QComboBox()
        self.parent_combo.addItem("None (Root)", None)
        form_layout.addRow("Parent Page:", self.parent_combo)

        # Content editor
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Enter page content...")
        self.content_input.setMinimumHeight(150)
        form_layout.addRow("Content:", self.content_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Tags section
        tags_group = QGroupBox("Tags")
        tags_layout = QVBoxLayout()

        self.tags_list = QListWidget()
        self.tags_list.setMaximumHeight(80)
        tags_layout.addWidget(self.tags_list)

        tags_btn_layout = QHBoxLayout()
        self.add_tag_btn = QPushButton("Add Tag")
        self.add_tag_btn.clicked.connect(self._add_tag)
        self.remove_tag_btn = QPushButton("Remove Tag")
        self.remove_tag_btn.clicked.connect(self._remove_tag)
        tags_btn_layout.addWidget(self.add_tag_btn)
        tags_btn_layout.addWidget(self.remove_tag_btn)
        tags_btn_layout.addStretch()
        tags_layout.addLayout(tags_btn_layout)

        tags_group.setLayout(tags_layout)
        form_main_layout.addWidget(tags_group)

        # Images section
        images_group = QGroupBox("Images")
        images_layout = QVBoxLayout()

        self.images_list = QListWidget()
        self.images_list.setMaximumHeight(80)
        images_layout.addWidget(self.images_list)

        images_btn_layout = QHBoxLayout()
        self.add_image_btn = QPushButton("Add Image")
        self.add_image_btn.clicked.connect(self._add_image)
        self.remove_image_btn = QPushButton("Remove Image")
        self.remove_image_btn.clicked.connect(self._remove_image)
        images_btn_layout.addWidget(self.add_image_btn)
        images_btn_layout.addWidget(self.remove_image_btn)
        images_btn_layout.addStretch()
        images_layout.addLayout(images_btn_layout)

        images_group.setLayout(images_layout)
        form_main_layout.addWidget(images_group)

        # Main action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Page")
        self.add_btn.clicked.connect(self._add_page)

        self.update_btn = QPushButton("Update Page")
        self.update_btn.clicked.connect(self._update_page)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Page")
        self.delete_btn.clicked.connect(self._delete_page)
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
        """Refresh the pages table and combo boxes."""
        # Refresh world combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(str(world.name), world.id.value)

        # Refresh template combo
        self.template_combo.clear()
        self.template_combo.addItem("None", None)
        if hasattr(self.lore_data, 'templates'):
            for template in self.lore_data.templates:
                self.template_combo.addItem(str(template.name), template.id.value)

        # Refresh parent page combo
        self.parent_combo.clear()
        self.parent_combo.addItem("None (Root)", None)
        if hasattr(self.lore_data, 'pages'):
            for page in self.lore_data.pages:
                if self.selected_page is None or page.id != self.selected_page.id:
                    self.parent_combo.addItem(str(page.name), page.id.value)

        # Refresh table
        self.table.setRowCount(0)

        if not hasattr(self.lore_data, 'pages'):
            return

        for page in self.lore_data.pages:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Get world name
            world = next((w for w in self.lore_data.worlds if w.id == page.world_id), None)
            world_name = str(world.name) if world else f"ID: {page.world_id.value}"

            # Get template name
            template_name = "None"
            if page.template_id and hasattr(self.lore_data, 'templates'):
                template = next((t for t in self.lore_data.templates if t.id == page.template_id), None)
                template_name = str(template.name) if template else f"ID: {page.template_id.value}"

            self.table.setItem(row, 0, QTableWidgetItem(str(page.id.value) if page.id else ""))
            self.table.setItem(row, 1, QTableWidgetItem(world_name))
            self.table.setItem(row, 2, QTableWidgetItem(str(page.name)))
            self.table.setItem(row, 3, QTableWidgetItem(template_name))
            self.table.setItem(row, 4, QTableWidgetItem(str(len(page.tag_ids))))
            self.table.setItem(row, 5, QTableWidgetItem(str(len(page.image_ids))))
            self.table.setItem(row, 6, QTableWidgetItem(page.updated_at.value.strftime("%Y-%m-%d %H:%M")))

        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle page selection."""
        selected_items = self.table.selectedItems()
        if selected_items and hasattr(self.lore_data, 'pages'):
            row = selected_items[0].row()
            page_id = EntityId(int(self.table.item(row, 0).text()))
            self.selected_page = next((p for p in self.lore_data.pages if p.id == page_id), None)

            if self.selected_page:
                # Update form fields
                # Find and set world
                for i in range(self.world_combo.count()):
                    if self.world_combo.itemData(i) == self.selected_page.world_id.value:
                        self.world_combo.setCurrentIndex(i)
                        break

                self.name_input.setText(str(self.selected_page.name))
                self.content_input.setPlainText(str(self.selected_page.content))

                # Set template
                if self.selected_page.template_id:
                    for i in range(self.template_combo.count()):
                        if self.template_combo.itemData(i) == self.selected_page.template_id.value:
                            self.template_combo.setCurrentIndex(i)
                            break
                else:
                    self.template_combo.setCurrentIndex(0)

                # Set parent
                if self.selected_page.parent_id:
                    for i in range(self.parent_combo.count()):
                        if self.parent_combo.itemData(i) == self.selected_page.parent_id.value:
                            self.parent_combo.setCurrentIndex(i)
                            break
                else:
                    self.parent_combo.setCurrentIndex(0)

                self._refresh_tags_list()
                self._refresh_images_list()

                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.page_selected.emit(page_id)
        else:
            self.selected_page = None
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _refresh_tags_list(self):
        """Refresh tags list widget."""
        self.tags_list.clear()
        if self.selected_page and hasattr(self.lore_data, 'tags'):
            for tag_id in self.selected_page.tag_ids:
                tag = next((t for t in self.lore_data.tags if t.id == tag_id), None)
                name = str(tag.name) if tag else f"Unknown (ID: {tag_id.value})"
                self.tags_list.addItem(name)

    def _refresh_images_list(self):
        """Refresh images list widget."""
        self.images_list.clear()
        if self.selected_page and hasattr(self.lore_data, 'images'):
            for image_id in self.selected_page.image_ids:
                image = next((img for img in self.lore_data.images if img.id == image_id), None)
                name = str(image.path) if image else f"Unknown (ID: {image_id.value})"
                self.images_list.addItem(name)

    def _add_tag(self):
        """Add a tag to the page."""
        if not self.selected_page:
            QMessageBox.warning(self, "No Page Selected", "Please select a page first.")
            return

        if not hasattr(self.lore_data, 'tags') or not self.lore_data.tags:
            QMessageBox.information(self, "No Tags", "No tags available. Create tags first.")
            return

        # Get world tags
        world_tags = [t for t in self.lore_data.tags if t.world_id == self.selected_page.world_id]
        if not world_tags:
            QMessageBox.information(self, "No Tags", "No tags available for this world.")
            return

        items = [str(t.name) for t in world_tags]
        item, ok = QInputDialog.getItem(self, "Add Tag", "Select tag:", items, 0, False)

        if ok and item:
            selected_tag = next(t for t in world_tags if str(t.name) == item)
            if selected_tag.id not in self.selected_page.tag_ids:
                self.selected_page.add_tag(selected_tag.id)
                self._refresh_tags_list()

    def _remove_tag(self):
        """Remove selected tag."""
        current_row = self.tags_list.currentRow()
        if current_row >= 0 and self.selected_page:
            tag_id = self.selected_page.tag_ids[current_row]
            self.selected_page.remove_tag(tag_id)
            self._refresh_tags_list()

    def _add_image(self):
        """Add an image to the page."""
        if not self.selected_page:
            QMessageBox.warning(self, "No Page Selected", "Please select a page first.")
            return

        if not hasattr(self.lore_data, 'images') or not self.lore_data.images:
            QMessageBox.information(self, "No Images", "No images available. Upload images first.")
            return

        items = [str(img.path) for img in self.lore_data.images]
        item, ok = QInputDialog.getItem(self, "Add Image", "Select image:", items, 0, False)

        if ok and item:
            selected_image = next(img for img in self.lore_data.images if str(img.path) == item)
            if selected_image.id not in self.selected_page.image_ids:
                self.selected_page.add_image(selected_image.id)
                self._refresh_images_list()

    def _remove_image(self):
        """Remove selected image."""
        current_row = self.images_list.currentRow()
        if current_row >= 0 and self.selected_page:
            image_id = self.selected_page.image_ids[current_row]
            self.selected_page.remove_image(image_id)
            self._refresh_images_list()

    def _add_page(self):
        """Add a new page."""
        try:
            if self.world_combo.currentData() is None:
                QMessageBox.warning(self, "Error", "Please select a world.")
                return

            world_id = EntityId(self.world_combo.currentData())
            template_id = EntityId(self.template_combo.currentData()) if self.template_combo.currentData() else None
            parent_id = EntityId(self.parent_combo.currentData()) if self.parent_combo.currentData() else None

            page = Page.create(
                tenant_id=self.lore_data.tenant_id,
                world_id=world_id,
                name=PageName(self.name_input.text()),
                content=Content(self.content_input.toPlainText()),
                template_id=template_id,
                parent_id=parent_id
            )

            if not hasattr(self.lore_data, 'pages'):
                self.lore_data.pages = []

            self.lore_data.pages.append(page)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Page created successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create page: {e}")

    def _update_page(self):
        """Update selected page."""
        if not self.selected_page:
            return

        try:
            # Update content
            new_content = Content(self.content_input.toPlainText())
            self.selected_page.update_content(new_content)

            # Update template
            template_id = EntityId(self.template_combo.currentData()) if self.template_combo.currentData() else None
            self.selected_page.change_template(template_id)

            # Update parent
            parent_id = EntityId(self.parent_combo.currentData()) if self.parent_combo.currentData() else None
            self.selected_page.move_to_parent(parent_id)

            self.refresh()
            QMessageBox.information(self, "Success", "Page updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update page: {e}")

    def _delete_page(self):
        """Delete selected page."""
        if not self.selected_page:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{self.selected_page.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self.lore_data, 'pages'):
                self.lore_data.pages.remove(self.selected_page)
            self.selected_page = None
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Page deleted successfully!")

    def _clear_form(self):
        """Clear the form fields."""
        self.name_input.clear()
        self.content_input.clear()
        self.template_combo.setCurrentIndex(0)
        self.parent_combo.setCurrentIndex(0)
        self.tags_list.clear()
        self.images_list.clear()
        self.selected_page = None
        self.update_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
