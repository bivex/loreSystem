"""
PurchaseTab - Tab for managing purchases/transactions
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class PurchaseTab(QWidget):
    """Tab for managing purchases/transactions."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_purchase: Optional[dict] = None
        self.all_purchases: List[dict] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel("💳 Purchases")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        splitter = QSplitter(Qt.Orientation.Vertical)

        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Buyer", "Item", "Price", "Date", "Status"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Purchase Details")
        form_layout = QFormLayout()

        self.buyer_input = QLineEdit()
        form_layout.addRow("Buyer:", self.buyer_input)

        self.item_input = QLineEdit()
        form_layout.addRow("Item:", self.item_input)

        self.price_spin = QDoubleSpinBox()
        self.price_spin.setMinimum(0.0)
        self.price_spin.setMaximum(999999.99)
        form_layout.addRow("Price:", self.price_spin)

        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("YYYY-MM-DD")
        form_layout.addRow("Date:", self.date_input)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Completed", "Pending", "Cancelled", "Refunded"])
        form_layout.addRow("Status:", self.status_combo)

        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        form_layout.addRow("Notes:", self.notes_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Purchase")
        self.add_btn.clicked.connect(self._add_purchase)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Purchase")
        self.delete_btn.clicked.connect(self._delete_purchase)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        try:
            self.all_purchases = getattr(self.lore_data, 'get_purchases', lambda: [])()
            self._populate_table(self.all_purchases)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load purchases: {str(e)}")

    def _populate_table(self, purchases: List[dict]):
        self.table.setRowCount(len(purchases))
        for row, purchase in enumerate(purchases):
            self.table.setItem(row, 0, QTableWidgetItem(str(purchase.get('id', 'N/A'))))
            self.table.setItem(row, 1, QTableWidgetItem(purchase.get('buyer', 'N/A')))
            self.table.setItem(row, 2, QTableWidgetItem(purchase.get('item', 'N/A')))
            self.table.setItem(row, 3, QTableWidgetItem(str(purchase.get('price', 0))))
            self.table.setItem(row, 4, QTableWidgetItem(purchase.get('date', 'N/A')))
            self.table.setItem(row, 5, QTableWidgetItem(purchase.get('status', 'Pending')))

    def _on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_purchase = self.all_purchases[row]
            self._populate_form()
            self.delete_btn.setEnabled(True)
        else:
            self.selected_purchase = None
            self._clear_form()
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        if not self.selected_purchase:
            return
        self.buyer_input.setText(self.selected_purchase.get('buyer', ''))
        self.item_input.setText(self.selected_purchase.get('item', ''))
        self.price_spin.setValue(float(self.selected_purchase.get('price', 0)))
        self.date_input.setText(self.selected_purchase.get('date', ''))
        self.status_combo.setCurrentText(self.selected_purchase.get('status', 'Pending'))
        self.notes_input.setPlainText(self.selected_purchase.get('notes', ''))

    def _clear_form(self):
        self.buyer_input.clear()
        self.item_input.clear()
        self.price_spin.setValue(0.0)
        self.date_input.clear()
        self.status_combo.setCurrentIndex(0)
        self.notes_input.clear()

    def _add_purchase(self):
        try:
            buyer = self.buyer_input.text().strip()
            if not buyer:
                QMessageBox.warning(self, "Warning", "Buyer cannot be empty")
                return

            purchase_data = {
                'buyer': buyer,
                'item': self.item_input.text().strip(),
                'price': self.price_spin.value(),
                'date': self.date_input.text().strip(),
                'status': self.status_combo.currentText(),
                'notes': self.notes_input.toPlainText()
            }

            self.lore_data.add_purchase(purchase_data)
            QMessageBox.information(self, "Success", "Purchase added successfully!")
            self._clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add purchase: {str(e)}")

    def _delete_purchase(self):
        if not self.selected_purchase:
            return

        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.delete_purchase(self.selected_purchase.get('id'))
                QMessageBox.information(self, "Success", "Purchase deleted successfully!")
                self._clear_form()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete purchase: {str(e)}")
