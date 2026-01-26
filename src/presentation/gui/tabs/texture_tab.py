"""
TextureTab - Tab for managing 3D textures
"""
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QFileDialog, QSplitter, QTextEdit, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont

from src.domain.entities.texture import Texture
from src.domain.value_objects.common import (
    TenantId, EntityId
)


class TextureTab(QWidget):
    """Tab for managing 3D textures."""

    texture_selected = pyqtSignal(EntityId)

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_texture: Optional[Texture] = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("🎨 Textures")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Textures table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Name", "Type", "File Size", "Dimensions", "Color Space", "Created"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Texture Details")
        form_layout = QFormLayout()

        # World selection
        self.world_combo = QComboBox()
        form_layout.addRow("World:", self.world_combo)

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter texture name...")
        form_layout.addRow("Name:", self.name_input)

        # Texture type
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "diffuse", "normal", "specular", "roughness", "metallic",
            "emissive", "ambient_occlusion", "height", "opacity"
        ])
        form_layout.addRow("Type:", self.type_combo)

        # File path input and browse button
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText("Select a texture file...")

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_file)

        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        form_layout.addRow("File Path:", path_layout)

        # File size (read-only, auto-calculated)
        self.file_size_input = QLineEdit()
        self.file_size_input.setReadOnly(True)
        form_layout.addRow("File Size (bytes):", self.file_size_input)

        # Dimensions
        dims_layout = QHBoxLayout()
        self.width_input = QSpinBox()
        self.width_input.setRange(1, 16384)
        self.width_input.setValue(1024)
        self.height_input = QSpinBox()
        self.height_input.setRange(1, 16384)
        self.height_input.setValue(1024)
        dims_layout.addWidget(QLabel("Width:"))
        dims_layout.addWidget(self.width_input)
        dims_layout.addWidget(QLabel("Height:"))
        dims_layout.addWidget(self.height_input)
        form_layout.addRow("Dimensions:", dims_layout)

        # Color space
        self.color_space_combo = QComboBox()
        self.color_space_combo.addItems(["sRGB", "Linear"])
        form_layout.addRow("Color Space:", self.color_space_combo)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Add description for this texture (optional)...")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Usage statistics
        usage_group = QGroupBox("Texture Usage")
        usage_layout = QVBoxLayout()
        self.usage_label = QLabel("Select a texture to view usage statistics")
        self.usage_label.setStyleSheet("color: gray; font-style: italic;")
        usage_layout.addWidget(self.usage_label)
        usage_group.setLayout(usage_layout)
        form_main_layout.addWidget(usage_group)

        # Main action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Texture")
        self.add_btn.clicked.connect(self._add_texture)

        self.update_btn = QPushButton("Update Texture")
        self.update_btn.clicked.connect(self._update_texture)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Texture")
        self.delete_btn.clicked.connect(self._delete_texture)
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

        # Set splitter sizes (table gets more space)
        splitter.setSizes([200, 600])

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        """Refresh the textures table and combo boxes."""
        # Refresh world combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(str(world.name), world.id.value)

        # Refresh table
        self.table.setRowCount(0)

        if not hasattr(self.lore_data, 'textures'):
            return

        for texture in self.lore_data.textures:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Get world name
            world = next((w for w in self.lore_data.worlds if w.id == texture.world_id), None)
            world_name = str(world.name) if world else f"ID: {texture.world_id.value}"

            # Get file name from path
            file_name = Path(str(texture.path)).name

            self.table.setItem(row, 0, QTableWidgetItem(str(texture.id.value) if texture.id else ""))
            self.table.setItem(row, 1, QTableWidgetItem(world_name))
            self.table.setItem(row, 2, QTableWidgetItem(texture.name))
            self.table.setItem(row, 3, QTableWidgetItem(texture.texture_type))
            self.table.setItem(row, 4, QTableWidgetItem(f"{texture.file_size:,}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{texture.dimensions[0]}x{texture.dimensions[1]}" if texture.dimensions else "N/A"))
            self.table.setItem(row, 6, QTableWidgetItem(texture.color_space))
            self.table.setItem(row, 7, QTableWidgetItem(texture.created_at.value.strftime("%Y-%m-%d %H:%M")))

        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle texture selection."""
        selected_items = self.table.selectedItems()
        if selected_items and hasattr(self.lore_data, 'textures'):
            row = selected_items[0].row()
            texture_id = EntityId(int(self.table.item(row, 0).text()))
            self.selected_texture = next((tex for tex in self.lore_data.textures if tex.id == texture_id), None)

            if self.selected_texture:
                # Update form fields
                self._populate_form()
                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.texture_selected.emit(texture_id)
                self._update_usage_info()
            else:
                self.update_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate form with selected texture data."""
        if not self.selected_texture:
            return

        # World
        world_index = self.world_combo.findData(self.selected_texture.world_id.value)
        if world_index >= 0:
            self.world_combo.setCurrentIndex(world_index)

        # Other fields
        self.name_input.setText(self.selected_texture.name)
        self.type_combo.setCurrentText(self.selected_texture.texture_type)
        self.path_input.setText(str(self.selected_texture.path))
        self.file_size_input.setText(str(self.selected_texture.file_size))
        if self.selected_texture.dimensions:
            self.width_input.setValue(self.selected_texture.dimensions[0])
            self.height_input.setValue(self.selected_texture.dimensions[1])
        self.color_space_combo.setCurrentText(self.selected_texture.color_space)
        self.description_input.setText(self.selected_texture.description or "")

    def _update_usage_info(self):
        """Update usage statistics for selected texture."""
        if not self.selected_texture:
            self.usage_label.setText("Select a texture to view usage statistics")
            return

        # Count usage in 3D models
        model_count = 0
        if hasattr(self.lore_data, 'models'):
            for model in self.lore_data.models:
                if model.textures and self.selected_texture.id in [t for t in model.textures]:
                    model_count += 1

        usage_text = f"Used in {model_count} 3D model{'s' if model_count != 1 else ''}"
        self.usage_label.setText(usage_text)

    def _browse_file(self):
        """Browse for texture file."""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Texture files (*.png *.jpg *.jpeg *.tga *.dds *.exr)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                self.path_input.setText(file_path)

                # Auto-calculate file size
                try:
                    file_size = Path(file_path).stat().st_size
                    self.file_size_input.setText(str(file_size))
                except Exception:
                    pass

    def _add_texture(self):
        """Add a new texture."""
        try:
            # Validate inputs
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Texture name is required.")
                return

            if not self.path_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "File path is required.")
                return

            world_id = EntityId(self.world_combo.currentData())
            if not world_id:
                QMessageBox.warning(self, "Validation Error", "Please select a world.")
                return

            # Create texture
            texture = self.lore_data.add_texture(
                name=self.name_input.text().strip(),
                path=self.path_input.text().strip(),
                texture_type=self.type_combo.currentText(),
                world_id=world_id,
                description=self.description_input.toPlainText().strip() or None,
                file_size=int(self.file_size_input.text() or 0),
                dimensions=(self.width_input.value(), self.height_input.value()),
                color_space=self.color_space_combo.currentText()
            )

            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", f"Texture '{texture.name}' added successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add texture: {str(e)}")

    def _update_texture(self):
        """Update the selected texture."""
        if not self.selected_texture:
            return

        try:
            # Validate inputs
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Texture name is required.")
                return

            if not self.path_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "File path is required.")
                return

            world_id = EntityId(self.world_combo.currentData())
            if not world_id:
                QMessageBox.warning(self, "Validation Error", "Please select a world.")
                return

            # Update texture (this would require a method in LoreData)
            # For now, we'll recreate it
            updated_texture = Texture(
                id=self.selected_texture.id,
                tenant_id=self.selected_texture.tenant_id,
                world_id=world_id,
                name=self.name_input.text().strip(),
                path=self.path_input.text().strip(),
                texture_type=self.type_combo.currentText(),
                description=self.description_input.toPlainText().strip() or None,
                file_size=int(self.file_size_input.text() or 0),
                dimensions=(self.width_input.value(), self.height_input.value()),
                color_space=self.color_space_combo.currentText(),
                created_at=self.selected_texture.created_at,
                updated_at=self.lore_data.get_next_timestamp(),
                version=self.lore_data.get_next_version()
            )

            # Replace in list
            index = next((i for i, t in enumerate(self.lore_data.textures) if t.id == self.selected_texture.id), -1)
            if index >= 0:
                self.lore_data.textures[index] = updated_texture

            self.refresh()
            QMessageBox.information(self, "Success", f"Texture '{updated_texture.name}' updated successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update texture: {str(e)}")

    def _delete_texture(self):
        """Delete the selected texture."""
        if not self.selected_texture:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete texture '{self.selected_texture.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Remove from list
                self.lore_data.textures = [t for t in self.lore_data.textures if t.id != self.selected_texture.id]
                self.refresh()
                self._clear_form()
                QMessageBox.information(self, "Success", "Texture deleted successfully!")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete texture: {str(e)}")

    def _clear_form(self):
        """Clear the form fields."""
        self.name_input.clear()
        self.path_input.clear()
        self.file_size_input.clear()
        self.width_input.setValue(1024)
        self.height_input.setValue(1024)
        self.color_space_combo.setCurrentText("sRGB")
        self.description_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.world_combo.setCurrentIndex(0) if self.world_combo.count() > 0 else None
        self.selected_texture = None
        self.update_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.usage_label.setText("Select a texture to view usage statistics")