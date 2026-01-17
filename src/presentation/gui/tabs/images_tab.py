"""
ImagesTab - Tab for managing images and media library
"""
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QFileDialog, QSplitter, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPixmap

from src.domain.entities.image import Image
from src.domain.value_objects.common import (
    TenantId, EntityId, ImagePath, ImageType
)


class ImagesTab(QWidget):
    """Tab for managing image media library."""

    image_selected = pyqtSignal(EntityId)

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_image: Optional[Image] = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("🖼️ Images")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Images table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "File Name", "Type", "Path", "Created"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Image Details")
        form_layout = QFormLayout()

        # World selection
        self.world_combo = QComboBox()
        form_layout.addRow("World:", self.world_combo)

        # Image type
        self.type_combo = QComboBox()
        self.type_combo.addItem("PNG", ImageType.PNG.value)
        self.type_combo.addItem("JPG", ImageType.JPG.value)
        self.type_combo.addItem("JPEG", ImageType.JPEG.value)
        self.type_combo.addItem("GIF", ImageType.GIF.value)
        self.type_combo.addItem("SVG", ImageType.SVG.value)
        form_layout.addRow("Type:", self.type_combo)

        # File path input and browse button
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText("Select an image file...")

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_file)

        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        form_layout.addRow("File Path:", path_layout)

        # Description/Notes
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Add notes about this image (optional)...")
        self.notes_input.setMaximumHeight(80)
        form_layout.addRow("Notes:", self.notes_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Image preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()

        self.preview_label = QLabel("No image selected")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(300, 300)
        self.preview_label.setMaximumSize(600, 400)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background-color: #f5f5f5;")
        self.preview_label.setScaledContents(False)
        preview_layout.addWidget(self.preview_label, alignment=Qt.AlignmentFlag.AlignCenter)

        preview_group.setLayout(preview_layout)
        form_main_layout.addWidget(preview_group)

        # Usage statistics
        usage_group = QGroupBox("Image Usage")
        usage_layout = QVBoxLayout()
        self.usage_label = QLabel("Select an image to view usage statistics")
        self.usage_label.setStyleSheet("color: gray; font-style: italic;")
        usage_layout.addWidget(self.usage_label)
        usage_group.setLayout(usage_layout)
        form_main_layout.addWidget(usage_group)

        # Main action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Image")
        self.add_btn.clicked.connect(self._add_image)

        self.update_btn = QPushButton("Update Image")
        self.update_btn.clicked.connect(self._update_image)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Image")
        self.delete_btn.clicked.connect(self._delete_image)
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
        """Refresh the images table and combo boxes."""
        # Refresh world combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(str(world.name), world.id.value)

        # Refresh table
        self.table.setRowCount(0)

        if not hasattr(self.lore_data, 'images'):
            return

        for image in self.lore_data.images:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Get world name
            world = next((w for w in self.lore_data.worlds if w.id == image.world_id), None)
            world_name = str(world.name) if world else f"ID: {image.world_id.value}"

            # Get file name from path
            file_name = Path(str(image.path)).name

            self.table.setItem(row, 0, QTableWidgetItem(str(image.id.value) if image.id else ""))
            self.table.setItem(row, 1, QTableWidgetItem(world_name))
            self.table.setItem(row, 2, QTableWidgetItem(file_name))
            self.table.setItem(row, 3, QTableWidgetItem(image.image_type.value.upper()))
            self.table.setItem(row, 4, QTableWidgetItem(str(image.path)[:50]))
            self.table.setItem(row, 5, QTableWidgetItem(image.created_at.value.strftime("%Y-%m-%d %H:%M")))

        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle image selection."""
        selected_items = self.table.selectedItems()
        if selected_items and hasattr(self.lore_data, 'images'):
            row = selected_items[0].row()
            image_id = EntityId(int(self.table.item(row, 0).text()))
            self.selected_image = next((img for img in self.lore_data.images if img.id == image_id), None)

            if self.selected_image:
                # Update form fields
                # Find and set world
                for i in range(self.world_combo.count()):
                    if self.world_combo.itemData(i) == self.selected_image.world_id.value:
                        self.world_combo.setCurrentIndex(i)
                        break

                # Set type
                for i in range(self.type_combo.count()):
                    if self.type_combo.itemData(i) == self.selected_image.image_type.value:
                        self.type_combo.setCurrentIndex(i)
                        break

                self.path_input.setText(str(self.selected_image.path))

                # Load and display preview
                self._load_preview(str(self.selected_image.path))

                # Update usage statistics
                self._update_usage_stats()

                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.image_selected.emit(image_id)
        else:
            self.selected_image = None
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _load_preview(self, image_path: str):
        """Load and display image preview."""
        try:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                self.preview_label.setText(f"Could not load image:\n{image_path}")
            else:
                # Scale pixmap to fit label while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self.preview_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled_pixmap)
        except Exception as e:
            self.preview_label.setText(f"Error loading preview:\n{e}")

    def _update_usage_stats(self):
        """Update image usage statistics."""
        if not self.selected_image:
            self.usage_label.setText("Select an image to view usage statistics")
            return

        usage_count = 0
        usage_details = []

        # Count pages using this image
        if hasattr(self.lore_data, 'pages'):
            pages_with_image = [p for p in self.lore_data.pages if self.selected_image.id in p.image_ids]
            if pages_with_image:
                usage_count += len(pages_with_image)
                usage_details.append(f"Pages: {len(pages_with_image)}")

        if usage_count == 0:
            self.usage_label.setText("This image is not currently used")
        else:
            self.usage_label.setText(f"Used {usage_count} time(s): {', '.join(usage_details)}")

    def _browse_file(self):
        """Open file browser to select an image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image File",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.svg);;All Files (*)"
        )

        if file_path:
            self.path_input.setText(file_path)

            # Detect image type from extension
            extension = Path(file_path).suffix.lower()
            type_map = {
                '.png': ImageType.PNG.value,
                '.jpg': ImageType.JPG.value,
                '.jpeg': ImageType.JPEG.value,
                '.gif': ImageType.GIF.value,
                '.svg': ImageType.SVG.value
            }

            if extension in type_map:
                for i in range(self.type_combo.count()):
                    if self.type_combo.itemData(i) == type_map[extension]:
                        self.type_combo.setCurrentIndex(i)
                        break

            # Load preview
            self._load_preview(file_path)

    def _add_image(self):
        """Add a new image."""
        try:
            if self.world_combo.currentData() is None:
                QMessageBox.warning(self, "Error", "Please select a world.")
                return

            if not self.path_input.text():
                QMessageBox.warning(self, "Error", "Please select an image file.")
                return

            # Validate file exists
            file_path = Path(self.path_input.text())
            if not file_path.exists():
                QMessageBox.warning(self, "Error", "Selected file does not exist.")
                return

            world_id = EntityId(self.world_combo.currentData())
            image_type = ImageType(self.type_combo.currentData())

            image = Image.create(
                tenant_id=self.lore_data.tenant_id,
                world_id=world_id,
                path=ImagePath(str(file_path)),
                image_type=image_type
            )

            if not hasattr(self.lore_data, 'images'):
                self.lore_data.images = []

            self.lore_data.images.append(image)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Image added successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add image: {e}")

    def _update_image(self):
        """Update selected image."""
        if not self.selected_image:
            return

        try:
            # For images, we can't easily update the path or type
            # This could be enhanced to allow metadata updates
            QMessageBox.information(
                self, "Update Image",
                "Image updates are limited. To change the image, delete and re-add it."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update image: {e}")

    def _delete_image(self):
        """Delete selected image."""
        if not self.selected_image:
            return

        # Check if image is being used
        if hasattr(self.lore_data, 'pages'):
            pages_with_image = [p for p in self.lore_data.pages if self.selected_image.id in p.image_ids]
            if pages_with_image:
                reply = QMessageBox.question(
                    self, "Image In Use",
                    f"This image is used by {len(pages_with_image)} page(s). "
                    f"Deleting it will remove it from those pages. Continue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

                # Remove image from all pages
                for page in pages_with_image:
                    page.remove_image(self.selected_image.id)

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete this image?\n{self.selected_image.path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self.lore_data, 'images'):
                self.lore_data.images.remove(self.selected_image)
            self.selected_image = None
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Image deleted successfully!")

    def _clear_form(self):
        """Clear the form fields."""
        self.path_input.clear()
        self.notes_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.preview_label.clear()
        self.preview_label.setText("No image selected")
        self.usage_label.setText("Select an image to view usage statistics")
        self.selected_image = None
        self.update_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
