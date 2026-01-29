"""
CurrencyTab - Tab for managing currencies/resources
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.value_objects.common import EntityId


class CurrencyTab(QWidget):
    """Tab for managing currencies/resources."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_currency: Optional[dict] = None
        self.all_currencies: List[dict] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("💰 Currencies")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Currencies table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Symbol", "Exchange Rate", "Type", "Description"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Currency Details")
        form_layout = QFormLayout()

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter currency name...")
        form_layout.addRow("Name:", self.name_input)

        # Symbol
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("e.g., Gold, Silver, Crystal, etc.")
        form_layout.addRow("Symbol:", self.symbol_input)

        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Currency", "Resource", "Token", "Essence", "Ore", "Gem", "Other"])
        form_layout.addRow("Type:", self.type_combo)

        # Exchange Rate
        self.exchange_rate = QDoubleSpinBox()
        self.exchange_rate.setMinimum(0.0)
        self.exchange_rate.setMaximum(999999.99)
        self.exchange_rate.setValue(1.0)
        form_layout.addRow("Exchange Rate:", self.exchange_rate)

        # Rarity
        self.rarity_combo = QComboBox()
        self.rarity_combo.addItems(["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"])
        form_layout.addRow("Rarity:", self.rarity_combo)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter currency description...")
        self.description_input.setMaximumHeight(120)
        form_layout.addRow("Description:", self.description_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Currency")
        self.add_btn.clicked.connect(self._add_currency)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Currency")
        self.delete_btn.clicked.connect(self._delete_currency)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        """Refresh the currencies list."""
        try:
            # For now, use a mock approach since Currency might not be in LoreData
            self.all_currencies = getattr(self.lore_data, 'get_currencies', lambda: [])()
            self._populate_table(self.all_currencies)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load currencies: {str(e)}")

    def _populate_table(self, currencies: List[dict]):
        """Populate the table with currencies."""
        self.table.setRowCount(len(currencies))
        for row, currency in enumerate(currencies):
            self.table.setItem(row, 0, QTableWidgetItem(str(currency.get('id', 'N/A'))))
            self.table.setItem(row, 1, QTableWidgetItem(currency.get('name', 'N/A')))
            self.table.setItem(row, 2, QTableWidgetItem(currency.get('symbol', 'N/A')))
            self.table.setItem(row, 3, QTableWidgetItem(str(currency.get('exchange_rate', 1.0))))
            self.table.setItem(row, 4, QTableWidgetItem(currency.get('type', 'N/A')))
            self.table.setItem(row, 5, QTableWidgetItem(currency.get('description', '')))

    def _on_selection_changed(self):
        """Handle currency selection change."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_currency = self.all_currencies[row]
            self._populate_form()
            self.delete_btn.setEnabled(True)
        else:
            self.selected_currency = None
            self._clear_form()
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate the form with selected currency data."""
        if not self.selected_currency:
            return
        self.name_input.setText(self.selected_currency.get('name', ''))
        self.symbol_input.setText(self.selected_currency.get('symbol', ''))
        self.type_combo.setCurrentText(self.selected_currency.get('type', 'Currency'))
        self.exchange_rate.setValue(float(self.selected_currency.get('exchange_rate', 1.0)))
        self.rarity_combo.setCurrentText(self.selected_currency.get('rarity', 'Common'))
        self.description_input.setPlainText(self.selected_currency.get('description', ''))

    def _clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.symbol_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.exchange_rate.setValue(1.0)
        self.rarity_combo.setCurrentIndex(0)
        self.description_input.clear()

    def _add_currency(self):
        """Add a new currency."""
        try:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Currency name cannot be empty")
                return

            currency_data = {
                'name': name,
                'symbol': self.symbol_input.text().strip(),
                'type': self.type_combo.currentText(),
                'exchange_rate': self.exchange_rate.value(),
                'rarity': self.rarity_combo.currentText(),
                'description': self.description_input.toPlainText()
            }

            self.lore_data.add_currency(currency_data)
            QMessageBox.information(self, "Success", "Currency added successfully!")
            self._clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add currency: {str(e)}")

    def _delete_currency(self):
        """Delete the selected currency."""
        if not self.selected_currency:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{self.selected_currency.get('name', 'Unknown')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.delete_currency(self.selected_currency.get('id'))
                QMessageBox.information(self, "Success", "Currency deleted successfully!")
                self._clear_form()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete currency: {str(e)}")
