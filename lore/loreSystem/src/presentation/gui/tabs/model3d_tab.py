"""
Model3DTab - Tab for managing 3D models
"""
from typing import Optional, List
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QFileDialog, QSplitter, QTextEdit, QSpinBox,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont

from src.domain.entities.model3d import Model3D
from src.domain.value_objects.common import (
    TenantId, EntityId
)


class Model3DTab(QWidget):
    """Tab for managing 3D models."""

    model_selected = pyqtSignal(EntityId)

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_model: Optional[Model3D] = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("🎲 3D Models")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Models table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Name", "Type", "Poly Count", "File Size", "Textures", "Created"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("3D Model Details")
        form_layout = QFormLayout()

        # World selection
        self.world_combo = QComboBox()
        form_layout.addRow("World:", self.world_combo)

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter 3D model name...")
        form_layout.addRow("Name:", self.name_input)

        # Model type
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "character", "environment", "prop", "weapon", "armor",
            "vehicle", "building", "terrain", "effect"
        ])
        form_layout.addRow("Type:", self.type_combo)

        # File path input and browse button
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText("Select a 3D model file...")

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_file)

        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        form_layout.addRow("File Path:", path_layout)

        # File size (read-only, auto-calculated)
        self.file_size_input = QLineEdit()
        self.file_size_input.setReadOnly(True)
        form_layout.addRow("File Size (bytes):", self.file_size_input)

        # Polygon count
        self.poly_count_input = QSpinBox()
        self.poly_count_input.setRange(0, 10000000)
        self.poly_count_input.setValue(1000)
        form_layout.addRow("Polygon Count:", self.poly_count_input)

        # Dimensions
        dims_layout = QHBoxLayout()
        self.width_input = QSpinBox()
        self.width_input.setRange(0, 10000)
        self.width_input.setValue(1)
        self.height_input = QSpinBox()
        self.height_input.setRange(0, 10000)
        self.height_input.setValue(1)
        self.depth_input = QSpinBox()
        self.depth_input.setRange(0, 10000)
        self.depth_input.setValue(1)
        dims_layout.addWidget(QLabel("W:"))
        dims_layout.addWidget(self.width_input)
        dims_layout.addWidget(QLabel("H:"))
        dims_layout.addWidget(self.height_input)
        dims_layout.addWidget(QLabel("D:"))
        dims_layout.addWidget(self.depth_input)
        form_layout.addRow("Dimensions (units):", dims_layout)

        # Textures selection
        textures_group = QGroupBox("Associated Textures")
        textures_layout = QVBoxLayout()

        self.textures_list = QListWidget()
        self.textures_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        textures_layout.addWidget(self.textures_list)

        textures_btn_layout = QHBoxLayout()
        self.select_textures_btn = QPushButton("Select Textures")
        self.select_textures_btn.clicked.connect(self._select_textures)
        self.clear_textures_btn = QPushButton("Clear All")
        self.clear_textures_btn.clicked.connect(self._clear_textures)
        textures_btn_layout.addWidget(self.select_textures_btn)
        textures_btn_layout.addWidget(self.clear_textures_btn)
        textures_layout.addLayout(textures_btn_layout)

        textures_group.setLayout(textures_layout)
        form_layout.addRow(textures_group)

        # Animations (comma-separated)
        self.animations_input = QLineEdit()
        self.animations_input.setPlaceholderText("idle, walk, run, attack (optional)")
        form_layout.addRow("Animations:", self.animations_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Add description for this 3D model (optional)...")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Usage statistics
        usage_group = QGroupBox("Model Usage")
        usage_layout = QVBoxLayout()
        self.usage_label = QLabel("Select a model to view usage statistics")
        self.usage_label.setStyleSheet("color: gray; font-style: italic;")
        usage_layout.addWidget(self.usage_label)
        usage_group.setLayout(usage_layout)
        form_main_layout.addWidget(usage_group)

        # Main action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add 3D Model")
        self.add_btn.clicked.connect(self._add_model)

        self.update_btn = QPushButton("Update Model")
        self.update_btn.clicked.connect(self._update_model)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Model")
        self.delete_btn.clicked.connect(self._delete_model)
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
        """Refresh the models table and combo boxes."""
        # Refresh world combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(str(world.name), world.id.value)

        # Refresh textures list
        self._refresh_textures_list()

        # Refresh table
        self.table.setRowCount(0)

        if not hasattr(self.lore_data, 'models'):
            return

        for model in self.lore_data.models:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Get world name
            world = next((w for w in self.lore_data.worlds if w.id == model.world_id), None)
            world_name = str(world.name) if world else f"ID: {model.world_id.value}"

            # Get file name from path
            file_name = Path(str(model.path)).name

            # Count textures
            texture_count = len(model.textures) if model.textures else 0

            self.table.setItem(row, 0, QTableWidgetItem(str(model.id.value) if model.id else ""))
            self.table.setItem(row, 1, QTableWidgetItem(world_name))
            self.table.setItem(row, 2, QTableWidgetItem(model.name))
            self.table.setItem(row, 3, QTableWidgetItem(model.model_type))
            self.table.setItem(row, 4, QTableWidgetItem(f"{model.poly_count:,}" if model.poly_count else "N/A"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{model.file_size:,}" if model.file_size else "N/A"))
            self.table.setItem(row, 6, QTableWidgetItem(str(texture_count)))
            self.table.setItem(row, 7, QTableWidgetItem(model.created_at.value.strftime("%Y-%m-%d %H:%M")))

        self.table.resizeColumnsToContents()

    def _refresh_textures_list(self):
        """Refresh the available textures list."""
        self.textures_list.clear()
        if hasattr(self.lore_data, 'textures'):
            for texture in self.lore_data.textures:
                item = QListWidgetItem(f"{texture.name} ({texture.texture_type})")
                item.setData(Qt.ItemDataRole.UserRole, texture.id.value)
                self.textures_list.addItem(item)

    def _on_selection_changed(self):
        """Handle model selection."""
        selected_items = self.table.selectedItems()
        if selected_items and hasattr(self.lore_data, 'models'):
            row = selected_items[0].row()
            model_id = EntityId(int(self.table.item(row, 0).text()))
            self.selected_model = next((mod for mod in self.lore_data.models if mod.id == model_id), None)

            if self.selected_model:
                # Update form fields
                self._populate_form()
                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.model_selected.emit(model_id)
                self._update_usage_info()
            else:
                self.update_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate form with selected model data."""
        if not self.selected_model:
            return

        # World
        world_index = self.world_combo.findData(self.selected_model.world_id.value)
        if world_index >= 0:
            self.world_combo.setCurrentIndex(world_index)

        # Other fields
        self.name_input.setText(self.selected_model.name)
        self.type_combo.setCurrentText(self.selected_model.model_type)
        self.path_input.setText(str(self.selected_model.path))
        self.file_size_input.setText(str(self.selected_model.file_size or ""))
        self.poly_count_input.setValue(self.selected_model.poly_count or 0)
        if self.selected_model.dimensions:
            self.width_input.setValue(int(self.selected_model.dimensions[0]))
            self.height_input.setValue(int(self.selected_model.dimensions[1]))
            self.depth_input.setValue(int(self.selected_model.dimensions[2]) if len(self.selected_model.dimensions) > 2 else 1)
        self.animations_input.setText(", ".join(self.selected_model.animations) if self.selected_model.animations else "")
        self.description_input.setText(self.selected_model.description or "")

        # Select associated textures
        self._select_associated_textures()

    def _select_associated_textures(self):
        """Select textures associated with the current model."""
        if not self.selected_model or not self.selected_model.textures:
            return

        for i in range(self.textures_list.count()):
            item = self.textures_list.item(i)
            texture_id = item.data(Qt.ItemDataRole.UserRole)
            if texture_id in [t.value for t in self.selected_model.textures]:
                item.setSelected(True)
            else:
                item.setSelected(False)

    def _update_usage_info(self):
        """Update usage statistics for selected model."""
        if not self.selected_model:
            self.usage_label.setText("Select a model to view usage statistics")
            return

        # Count usage in items
        item_count = 0
        if hasattr(self.lore_data, 'items'):
            for item in self.lore_data.items:
                if item.model_3d_id == self.selected_model.id:
                    item_count += 1

        usage_text = f"Used in {item_count} item{'s' if item_count != 1 else ''}"
        self.usage_label.setText(usage_text)

    def _browse_file(self):
        """Browse for 3D model file."""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("3D Model files (*.obj *.fbx *.dae *.gltf *.glb *.blend *.3ds *.ply)")

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

    def _select_textures(self):
        """Select textures from the list."""
        # All selected items are already handled by the QListWidget
        pass

    def _clear_textures(self):
        """Clear all texture selections."""
        self.textures_list.clearSelection()

    def _add_model(self):
        """Add a new 3D model."""
        try:
            # Validate inputs
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Model name is required.")
                return

            if not self.path_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "File path is required.")
                return

            world_id = EntityId(self.world_combo.currentData())
            if not world_id:
                QMessageBox.warning(self, "Validation Error", "Please select a world.")
                return

            # Get selected textures
            selected_textures = []
            for i in range(self.textures_list.count()):
                item = self.textures_list.item(i)
                if item.isSelected():
                    selected_textures.append(EntityId(item.data(Qt.ItemDataRole.UserRole)))

            # Parse animations
            animations = [anim.strip() for anim in self.animations_input.text().split(",") if anim.strip()]

            # Create model
            model = self.lore_data.add_model(
                name=self.name_input.text().strip(),
                path=self.path_input.text().strip(),
                model_type=self.type_combo.currentText(),
                world_id=world_id,
                description=self.description_input.toPlainText().strip() or None,
                file_size=int(self.file_size_input.text() or 0),
                poly_count=self.poly_count_input.value(),
                dimensions=(self.width_input.value(), self.height_input.value(), self.depth_input.value()),
                textures=selected_textures if selected_textures else None,
                animations=animations if animations else None
            )

            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", f"3D Model '{model.name}' added successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add 3D model: {str(e)}")

    def _update_model(self):
        """Update the selected model."""
        if not self.selected_model:
            return

        try:
            # Validate inputs
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Model name is required.")
                return

            if not self.path_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "File path is required.")
                return

            world_id = EntityId(self.world_combo.currentData())
            if not world_id:
                QMessageBox.warning(self, "Validation Error", "Please select a world.")
                return

            # Get selected textures
            selected_textures = []
            for i in range(self.textures_list.count()):
                item = self.textures_list.item(i)
                if item.isSelected():
                    selected_textures.append(EntityId(item.data(Qt.ItemDataRole.UserRole)))

            # Parse animations
            animations = [anim.strip() for anim in self.animations_input.text().split(",") if anim.strip()]

            # Update model (this would require a method in LoreData)
            # For now, we'll recreate it
            updated_model = Model3D(
                id=self.selected_model.id,
                tenant_id=self.selected_model.tenant_id,
                world_id=world_id,
                name=self.name_input.text().strip(),
                path=self.path_input.text().strip(),
                model_type=self.type_combo.currentText(),
                description=self.description_input.toPlainText().strip() or None,
                file_size=int(self.file_size_input.text() or 0),
                poly_count=self.poly_count_input.value(),
                dimensions=(self.width_input.value(), self.height_input.value(), self.depth_input.value()),
                textures=selected_textures if selected_textures else None,
                animations=animations if animations else None,
                created_at=self.selected_model.created_at,
                updated_at=self.lore_data.get_next_timestamp(),
                version=self.lore_data.get_next_version()
            )

            # Replace in list
            index = next((i for i, m in enumerate(self.lore_data.models) if m.id == self.selected_model.id), -1)
            if index >= 0:
                self.lore_data.models[index] = updated_model

            self.refresh()
            QMessageBox.information(self, "Success", f"3D Model '{updated_model.name}' updated successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update model: {str(e)}")

    def _delete_model(self):
        """Delete the selected model."""
        if not self.selected_model:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete 3D model '{self.selected_model.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Remove from list
                self.lore_data.models = [m for m in self.lore_data.models if m.id != self.selected_model.id]
                self.refresh()
                self._clear_form()
                QMessageBox.information(self, "Success", "3D Model deleted successfully!")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete model: {str(e)}")

    def _clear_form(self):
        """Clear the form fields."""
        self.name_input.clear()
        self.path_input.clear()
        self.file_size_input.clear()
        self.poly_count_input.setValue(1000)
        self.width_input.setValue(1)
        self.height_input.setValue(1)
        self.depth_input.setValue(1)
        self.animations_input.clear()
        self.description_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.world_combo.setCurrentIndex(0) if self.world_combo.count() > 0 else None
        self.textures_list.clearSelection()
        self.selected_model = None
        self.update_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.usage_label.setText("Select a model to view usage statistics")