"""
PityTab - Tab for managing pity/guarantee systems
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class PityTab(QWidget):
    """Tab for managing pity/guarantee systems."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_pity: Optional[dict] = None
        self.all_pities: List[dict] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel("🎯 Pity/Guarantee Systems")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        splitter = QSplitter(Qt.Orientation.Vertical)

        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Banner", "Threshold", "Guarantee Type", "Description"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Pity System Details")
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Pity system name...")
        form_layout.addRow("Name:", self.name_input)

        self.banner_combo = QComboBox()
        form_layout.addRow("Banner:", self.banner_combo)

        self.threshold_spin = QSpinBox()
        self.threshold_spin.setMinimum(1)
        self.threshold_spin.setMaximum(10000)
        self.threshold_spin.setValue(90)
        form_layout.addRow("Pity Threshold:", self.threshold_spin)

        self.guarantee_type_combo = QComboBox()
        self.guarantee_type_combo.addItems([
            "5-Star Guarantee", "4-Star Guarantee", "Character Guarantee", 
            "Weapon Guarantee", "50/50 System", "Hard Pity", "Soft Pity", "Other"
        ])
        form_layout.addRow("Guarantee Type:", self.guarantee_type_combo)

        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Pity System")
        self.add_btn.clicked.connect(self._add_pity)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Pity System")
        self.delete_btn.clicked.connect(self._delete_pity)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        try:
            self.all_pities = getattr(self.lore_data, 'get_pities', lambda: [])()
            self._populate_banner_combo()
            self._populate_table(self.all_pities)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load pity systems: {str(e)}")

    def _populate_banner_combo(self):
        try:
            banners = getattr(self.lore_data, 'get_banners', lambda: [])()
            self.banner_combo.clear()
            for banner in banners:
                self.banner_combo.addItem(getattr(banner, 'name', 'Unknown'), banner.id)
        except Exception:
            pass

    def _populate_table(self, pities: List[dict]):
        self.table.setRowCount(len(pities))
        for row, pity in enumerate(pities):
            self.table.setItem(row, 0, QTableWidgetItem(str(pity.get('id', 'N/A'))))
            self.table.setItem(row, 1, QTableWidgetItem(pity.get('name', 'N/A')))
            self.table.setItem(row, 2, QTableWidgetItem(str(pity.get('banner_id', 'N/A'))))
            self.table.setItem(row, 3, QTableWidgetItem(str(pity.get('threshold', 90))))
            self.table.setItem(row, 4, QTableWidgetItem(pity.get('guarantee_type', 'N/A')))
            self.table.setItem(row, 5, QTableWidgetItem(pity.get('description', '')))

    def _on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_pity = self.all_pities[row]
            self._populate_form()
            self.delete_btn.setEnabled(True)
        else:
            self.selected_pity = None
            self._clear_form()
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        if not self.selected_pity:
            return
        self.name_input.setText(self.selected_pity.get('name', ''))
        self.threshold_spin.setValue(int(self.selected_pity.get('threshold', 90)))
        self.guarantee_type_combo.setCurrentText(self.selected_pity.get('guarantee_type', '5-Star Guarantee'))
        self.description_input.setPlainText(self.selected_pity.get('description', ''))

    def _clear_form(self):
        self.name_input.clear()
        self.banner_combo.setCurrentIndex(0)
        self.threshold_spin.setValue(90)
        self.guarantee_type_combo.setCurrentIndex(0)
        self.description_input.clear()

    def _add_pity(self):
        try:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Pity system name cannot be empty")
                return

            pity_data = {
                'name': name,
                'banner_id': self.banner_combo.currentData(),
                'threshold': self.threshold_spin.value(),
                'guarantee_type': self.guarantee_type_combo.currentText(),
                'description': self.description_input.toPlainText()
            }

            self.lore_data.add_pity(pity_data)
            QMessageBox.information(self, "Success", "Pity system added successfully!")
            self._clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add pity system: {str(e)}")

    def _delete_pity(self):
        if not self.selected_pity:
            return

        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.delete_pity(self.selected_pity.get('id'))
                QMessageBox.information(self, "Success", "Pity system deleted successfully!")
                self._clear_form()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete pity system: {str(e)}")
