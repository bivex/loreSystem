"""
ItemsTab - Enhanced tab for managing items with improved UX.
"""
from typing import List, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.domain.entities.item import Item
from src.domain.value_objects.common import (
    EntityId, Description, ItemType, Rarity
)
from src.presentation.gui.lore_data import LoreData


class ItemsTab(QWidget):
    """Enhanced tab for managing items with improved UX."""

    item_selected = pyqtSignal(EntityId)

    def __init__(self, lore_data: LoreData):
        super().__init__()
        self.lore_data = lore_data
        self.selected_item: Optional[Item] = None
        self.all_items: List[Item] = []  # Store all items for filtering
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the enhanced user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        # Filter bar
        filter_layout = QHBoxLayout()
        filter_label = QLabel("🔍 Filter:")
        filter_label.setStyleSheet("color: #ddd; font-weight: bold;")
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter items by name, type, or description...")
        self.filter_input.textChanged.connect(self._apply_filter)

        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types", None)
        for item_type in ItemType:
            self.type_filter.addItem(f"{item_type.value}", item_type)
        self.type_filter.currentIndexChanged.connect(self._apply_filter)

        self.rarity_filter = QComboBox()
        self.rarity_filter.addItem("All Rarities", None)
        self.rarity_filter.addItem("No Rarity", "none")
        for rarity in Rarity:
            self.rarity_filter.addItem(f"{rarity.value}", rarity)
        self.rarity_filter.currentIndexChanged.connect(self._apply_filter)

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.type_filter)
        filter_layout.addWidget(QLabel("Rarity:"))
        filter_layout.addWidget(self.rarity_filter)
        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left side - Table and buttons
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_widget.setLayout(left_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Name", "Type", "Rarity", "Description"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.itemSelectionChanged.connect(self._on_item_selected)
        self.table.setStyleSheet("""
            QTableWidget {
                selection-background-color: #4a6cd4;
                alternate-background-color: #2a2a2a;
            }
        """)

        # Buttons with icons and tooltips
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("➕ Add Item")
        self.add_btn.clicked.connect(self._add_item)
        self.add_btn.setToolTip("Create a new item (Ctrl+N)")
        self.add_btn.setShortcut("Ctrl+N")

        self.edit_btn = QPushButton("✏️ Edit Item")
        self.edit_btn.clicked.connect(self._edit_item)
        self.edit_btn.setEnabled(False)
        self.edit_btn.setToolTip("Edit the selected item (Ctrl+E)")
        self.edit_btn.setShortcut("Ctrl+E")

        self.delete_btn = QPushButton("🗑️ Delete Item")
        self.delete_btn.clicked.connect(self._delete_item)
        self.delete_btn.setEnabled(False)
        self.delete_btn.setToolTip("Delete the selected item (Delete)")
        self.delete_btn.setShortcut("Delete")

        self.duplicate_btn = QPushButton("📋 Duplicate")
        self.duplicate_btn.clicked.connect(self._duplicate_item)
        self.duplicate_btn.setEnabled(False)
        self.duplicate_btn.setToolTip("Create a copy of the selected item")

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.duplicate_btn)
        button_layout.addStretch()

        left_layout.addWidget(self.table)
        left_layout.addLayout(button_layout)

        # Right side - Form
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_widget.setLayout(right_layout)

        form_group = QGroupBox("📝 Item Details")
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)

        self.world_combo = QComboBox()
        self.world_combo.addItem("🏠 Select World...", None)
        self.world_combo.setToolTip("Choose which world this item belongs to")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter item name...")
        self.name_input.setToolTip("The name of your item")

        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(120)
        self.description_input.setPlaceholderText("Describe your item in detail...")
        self.description_input.setToolTip("Detailed description of the item")

        self.type_combo = QComboBox()
        self.type_combo.setToolTip("What type of item is this?")
        for item_type in ItemType:
            self.type_combo.addItem(f"{item_type.value}", item_type)

        self.rarity_combo = QComboBox()
        self.rarity_combo.addItem("✨ No Rarity", None)
        self.rarity_combo.setToolTip("How rare is this item?")
        for rarity in Rarity:
            self.rarity_combo.addItem(f"{rarity.value}", rarity)

        form_layout.addRow("🌍 World:", self.world_combo)
        form_layout.addRow("📛 Name:", self.name_input)
        form_layout.addRow("🏷️ Type:", self.type_combo)
        form_layout.addRow("💎 Rarity:", self.rarity_combo)
        form_layout.addRow("📖 Description:", self.description_input)

        form_group.setLayout(form_layout)
        right_layout.addWidget(form_group)

        # Action buttons
        action_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self._save_item)
        self.save_btn.setEnabled(False)
        self.save_btn.setToolTip("Save the item (Ctrl+S)")
        self.save_btn.setShortcut("Ctrl+S")

        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self._cancel_edit)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setToolTip("Cancel editing (Esc)")
        self.cancel_btn.setShortcut("Esc")

        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.cancel_btn)
        action_layout.addStretch()

        right_layout.addLayout(action_layout)
        right_layout.addStretch()

        # Context menu for table
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 400])  # Default split ratio

    def _show_context_menu(self, position):
        """Show context menu for table."""
        if not self.table.itemAt(position):
            return

        menu = QMenu()

        edit_action = menu.addAction("✏️ Edit Item")
        edit_action.triggered.connect(self._edit_item)

        duplicate_action = menu.addAction("📋 Duplicate Item")
        duplicate_action.triggered.connect(self._duplicate_item)

        menu.addSeparator()

        delete_action = menu.addAction("🗑️ Delete Item")
        delete_action.triggered.connect(self._delete_item)

        menu.exec(self.table.mapToGlobal(position))

    def _duplicate_item(self):
        """Duplicate the selected item."""
        if not self.selected_item:
            return

        try:
            # Create duplicate with new name
            duplicate_name = f"{self.selected_item.name} (Copy)"

            # Check if name already exists and add number if needed
            existing_names = [item.name for item in self.lore_data.items]
            counter = 1
            while duplicate_name in existing_names:
                duplicate_name = f"{self.selected_item.name} (Copy {counter})"
                counter += 1

            # Create new item
            duplicate_item = Item.create(
                tenant_id=self.lore_data.tenant_id,
                world_id=self.selected_item.world_id,
                name=duplicate_name,
                description=self.selected_item.description,
                item_type=self.selected_item.item_type,
                rarity=self.selected_item.rarity
            )

            self.lore_data.add_item(duplicate_item)
            self.refresh()

            QMessageBox.information(
                self, "Success",
                f"Item duplicated successfully as '{duplicate_name}'!"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to duplicate item: {e}")

    def refresh(self):
        """Refresh the table with current data."""
        self.all_items = self.lore_data.items.copy()
        self._apply_filter()

        # Update world combo
        self.world_combo.clear()
        self.world_combo.addItem("🏠 Select World...", None)
        for world in self.lore_data.worlds:
            self.world_combo.addItem(f"🌍 {world.name}", world.id)

    def filter_items(self, search_text: str):
        """Filter items based on search text (called from main window)."""
        self.filter_input.setText(search_text)

    def _apply_filter(self):
        """Apply current filters to the table."""
        search_text = self.filter_input.text().lower()
        type_filter = self.type_filter.currentData()
        rarity_filter = self.rarity_filter.currentData()

        filtered_items = []
        for item in self.all_items:
            # Text search
            text_match = (
                search_text in item.name.lower() or
                search_text in str(item.description).lower() or
                search_text in item.item_type.value.lower() or
                (item.rarity and search_text in item.rarity.value.lower())
            ) if search_text else True

            # Type filter
            type_match = (item.item_type == type_filter) if type_filter else True

            # Rarity filter
            if rarity_filter == "none":
                rarity_match = item.rarity is None
            elif rarity_filter:
                rarity_match = item.rarity == rarity_filter
            else:
                rarity_match = True

            if text_match and type_match and rarity_match:
                filtered_items.append(item)

        self._populate_table(filtered_items)

    def _populate_table(self, items: List[Item]):
        """Populate table with filtered items."""
        self.table.setRowCount(0)

        for item in items:
            row = self.table.rowCount()
            self.table.insertRow(row)

            world = self.lore_data.get_world_by_id(item.world_id)
            world_name = f"🌍 {world.name}" if world else "🏠 Unknown"

            # Color code rarity
            rarity_text = ""
            if item.rarity:
                rarity_colors = {
                    Rarity.COMMON: "#8B8B8B",
                    Rarity.UNCOMMON: "#4CAF50",
                    Rarity.RARE: "#2196F3",
                    Rarity.EPIC: "#9C27B0",
                    Rarity.LEGENDARY: "#FF9800",
                    Rarity.MYTHIC: "#F44336"
                }
                color = rarity_colors.get(item.rarity, "#FFFFFF")
                rarity_text = f'<span style="color: {color};">{item.rarity.value}</span>'

            self.table.setItem(row, 0, QTableWidgetItem(str(item.id.value if item.id else "")))
            self.table.setItem(row, 1, QTableWidgetItem(world_name))
            self.table.setItem(row, 2, QTableWidgetItem(item.name))
            self.table.setItem(row, 3, QTableWidgetItem(item.item_type.value))
            self.table.setItem(row, 4, QTableWidgetItem(rarity_text if rarity_text else "No Rarity"))
            self.table.setItem(row, 5, QTableWidgetItem(str(item.description)))

            # Make rarity column rich text
            if rarity_text:
                self.table.item(row, 4).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # Resize columns to content
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

    def _on_item_selected(self):
        """Handle item selection."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if len(selected_rows) == 1:
            row = list(selected_rows)[0]
            item_id_text = self.table.item(row, 0).text()
            if item_id_text:
                item_id = int(item_id_text)
                self.selected_item = next(
                    (i for i in self.all_items if i.id and i.id.value == item_id),
                    None
                )

                if self.selected_item:
                    self._load_item(self.selected_item)
                    self.edit_btn.setEnabled(True)
                    self.delete_btn.setEnabled(True)
                    self.duplicate_btn.setEnabled(True)
                    self.item_selected.emit(self.selected_item.id)
                else:
                    self._clear_form()
            else:
                self._clear_form()
        else:
            self.selected_item = None
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.duplicate_btn.setEnabled(False)

    def _load_item(self, item: Item):
        """Load item data into form."""
        world_index = self.world_combo.findData(item.world_id)
        if world_index >= 0:
            self.world_combo.setCurrentIndex(world_index)

        self.name_input.setText(item.name)
        self.description_input.setPlainText(str(item.description))

        type_index = self.type_combo.findData(item.item_type)
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)

        if item.rarity:
            rarity_index = self.rarity_combo.findData(item.rarity)
            if rarity_index >= 0:
                self.rarity_combo.setCurrentIndex(rarity_index)
        else:
            self.rarity_combo.setCurrentIndex(0)  # No Rarity

    def _clear_form(self):
        """Clear the form and reset state."""
        self.world_combo.setCurrentIndex(0)
        self.name_input.clear()
        self.description_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.rarity_combo.setCurrentIndex(0)

        self.save_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.add_btn.setEnabled(True)
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.duplicate_btn.setEnabled(False)
        self.selected_item = None

        # Clear table selection
        self.table.clearSelection()

    def _validate_form(self) -> List[str]:
        """Validate form data and return list of errors."""
        errors = []

        world_id = self.world_combo.currentData()
        if not world_id:
            errors.append("Please select a world for the item.")

        name = self.name_input.text().strip()
        if not name:
            errors.append("Item name is required.")
        elif len(name) < 2:
            errors.append("Item name must be at least 2 characters long.")
        elif len(name) > 100:
            errors.append("Item name must be less than 100 characters.")

        description = self.description_input.toPlainText().strip()
        if not description:
            errors.append("Item description is required.")
        elif len(description) < 10:
            errors.append("Item description must be at least 10 characters long.")

        return errors

    def _add_item(self):
        """Start adding a new item."""
        self.selected_item = None
        self._clear_form()
        self.save_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.add_btn.setEnabled(False)
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def _edit_item(self):
        """Start editing the selected item."""
        if not self.selected_item:
            return

        self.save_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.add_btn.setEnabled(False)
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def _save_item(self):
        """Save the item with enhanced validation."""
        # Validate form
        errors = self._validate_form()
        if errors:
            error_msg = "Please fix the following issues:\n\n" + "\n".join(f"• {error}" for error in errors)
            QMessageBox.warning(self, "Validation Error", error_msg)
            return

        try:
            world_id = self.world_combo.currentData()
            name = self.name_input.text().strip()
            description = self.description_input.toPlainText().strip()
            item_type = self.type_combo.currentData()
            rarity = self.rarity_combo.currentData() if self.rarity_combo.currentIndex() > 0 else None

            if self.selected_item:
                # Update existing item
                self.selected_item.rename(name)
                self.selected_item.update_description(Description(description))
                self.selected_item.change_type(item_type)
                self.selected_item.set_rarity(rarity)

                operation = "updated"
            else:
                # Create new item
                item = Item.create(
                    tenant_id=self.lore_data.tenant_id,
                    world_id=world_id,
                    name=name,
                    description=Description(description),
                    item_type=item_type,
                    rarity=rarity
                )
                self.lore_data.add_item(item)

                operation = "created"

            self.refresh()
            self._clear_form()

            # Show success message with item details
            rarity_text = f" ({rarity.value})" if rarity else ""
            QMessageBox.information(
                self, "Success",
                f"Item '{name}' {operation} successfully!\n\n"
                f"Type: {item_type.value}{rarity_text}\n"
                f"World: {self.world_combo.currentText()}"
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Save Error",
                f"Failed to save item:\n\n{str(e)}\n\n"
                "Please check your input and try again."
            )

    def _delete_item(self):
        """Delete selected item with confirmation."""
        if not self.selected_item:
            return

        # Show detailed confirmation dialog
        world = self.lore_data.get_world_by_id(self.selected_item.world_id)
        world_name = world.name if world else "Unknown World"

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Confirm Delete")
        msg_box.setText("Are you sure you want to delete this item?")
        msg_box.setInformativeText(
            f"Item: {self.selected_item.name}\n"
            f"Type: {self.selected_item.item_type.value}\n"
            f"World: {world_name}\n\n"
            "This action cannot be undone."
        )
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.items.remove(self.selected_item)
                self.refresh()
                self._clear_form()

                QMessageBox.information(
                    self, "Success",
                    f"Item '{self.selected_item.name}' deleted successfully!"
                )

            except Exception as e:
                QMessageBox.critical(
                    self, "Delete Error",
                    f"Failed to delete item:\n\n{str(e)}"
                )

    def _cancel_edit(self):
        """Cancel editing and clear form."""
        self._clear_form()