"""
ShopTab - Tab for managing shop/marketplace
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.entities.shop import Shop
from src.domain.value_objects.common import EntityId


class ShopTab(QWidget):
    """Tab for managing shop/marketplace."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_shop: Optional[Shop] = None
        self.all_shops: List[Shop] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("🏪 Shops")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Shops table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Type", "Location", "Owner", "Description"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Shop Details")
        form_layout = QFormLayout()

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter shop name...")
        form_layout.addRow("Name:", self.name_input)

        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["General Store", "Weapon Shop", "Armor Shop", "Potion Shop", "Tavern", "Inn", "Other"])
        form_layout.addRow("Type:", self.type_combo)

        # Location
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Enter location/address...")
        form_layout.addRow("Location:", self.location_input)

        # Owner
        self.owner_input = QLineEdit()
        self.owner_input.setPlaceholderText("Owner name (optional)")
        form_layout.addRow("Owner:", self.owner_input)

        # Inventory Count
        self.inventory_count = QSpinBox()
        self.inventory_count.setMinimum(0)
        self.inventory_count.setValue(0)
        form_layout.addRow("Items in Stock:", self.inventory_count)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter shop description...")
        self.description_input.setMaximumHeight(120)
        form_layout.addRow("Description:", self.description_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Shop")
        self.add_btn.clicked.connect(self._add_shop)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Shop")
        self.delete_btn.clicked.connect(self._delete_shop)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        """Refresh the shops list."""
        try:
            self.all_shops = self.lore_data.get_shops()
            self._populate_table(self.all_shops)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load shops: {str(e)}")

    def _populate_table(self, shops: List[Shop]):
        """Populate the table with shops."""
        self.table.setRowCount(len(shops))
        for row, shop in enumerate(shops):
            self.table.setItem(row, 0, QTableWidgetItem(str(shop.id)))
            self.table.setItem(row, 1, QTableWidgetItem(getattr(shop, 'name', 'N/A')))
            self.table.setItem(row, 2, QTableWidgetItem(getattr(shop, 'type', 'N/A')))
            self.table.setItem(row, 3, QTableWidgetItem(getattr(shop, 'location', 'N/A')))
            self.table.setItem(row, 4, QTableWidgetItem(getattr(shop, 'owner', 'N/A')))
            self.table.setItem(row, 5, QTableWidgetItem(getattr(shop, 'description', '')))

    def _on_selection_changed(self):
        """Handle shop selection change."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_shop = self.all_shops[row]
            self._populate_form()
            self.delete_btn.setEnabled(True)
        else:
            self.selected_shop = None
            self._clear_form()
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate the form with selected shop data."""
        if not self.selected_shop:
            return
        self.name_input.setText(getattr(self.selected_shop, 'name', ''))
        self.type_combo.setCurrentText(getattr(self.selected_shop, 'type', 'General Store'))
        self.location_input.setText(getattr(self.selected_shop, 'location', ''))
        self.owner_input.setText(getattr(self.selected_shop, 'owner', ''))
        self.inventory_count.setValue(len(getattr(self.selected_shop, 'inventory', [])))
        self.description_input.setPlainText(getattr(self.selected_shop, 'description', ''))

    def _clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.location_input.clear()
        self.owner_input.clear()
        self.inventory_count.setValue(0)
        self.description_input.clear()

    def _add_shop(self):
        """Add a new shop."""
        try:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Shop name cannot be empty")
                return

            shop_data = {
                'name': name,
                'type': self.type_combo.currentText(),
                'location': self.location_input.text().strip(),
                'owner': self.owner_input.text().strip(),
                'description': self.description_input.toPlainText()
            }

            self.lore_data.add_shop(shop_data)
            QMessageBox.information(self, "Success", "Shop added successfully!")
            self._clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add shop: {str(e)}")

    def _delete_shop(self):
        """Delete the selected shop."""
        if not self.selected_shop:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{getattr(self.selected_shop, 'name', 'Unknown')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.delete_shop(self.selected_shop.id)
                QMessageBox.information(self, "Success", "Shop deleted successfully!")
                self._clear_form()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete shop: {str(e)}")
