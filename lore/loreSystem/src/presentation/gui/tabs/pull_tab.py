"""
PullTab - Tab for managing gacha pulls/draws
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class PullTab(QWidget):
    """Tab for managing gacha pulls/draws."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_pull: Optional[dict] = None
        self.all_pulls: List[dict] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel("🎰 Gacha Pulls")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        splitter = QSplitter(Qt.Orientation.Vertical)

        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Player", "Banner", "Result", "Rarity", "Date"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Pull Details")
        form_layout = QFormLayout()

        self.player_combo = QComboBox()
        form_layout.addRow("Player:", self.player_combo)

        self.banner_combo = QComboBox()
        form_layout.addRow("Banner:", self.banner_combo)

        self.result_input = QLineEdit()
        self.result_input.setPlaceholderText("What was pulled?")
        form_layout.addRow("Result:", self.result_input)

        self.rarity_combo = QComboBox()
        self.rarity_combo.addItems(["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"])
        form_layout.addRow("Rarity:", self.rarity_combo)

        self.pity_count_spin = QSpinBox()
        self.pity_count_spin.setMinimum(1)
        self.pity_count_spin.setMaximum(10000)
        form_layout.addRow("Pity Count:", self.pity_count_spin)

        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("YYYY-MM-DD HH:MM:SS")
        form_layout.addRow("Date:", self.date_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Pull")
        self.add_btn.clicked.connect(self._add_pull)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Pull")
        self.delete_btn.clicked.connect(self._delete_pull)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        try:
            self.all_pulls = getattr(self.lore_data, 'get_pulls', lambda: [])()
            self._populate_combos()
            self._populate_table(self.all_pulls)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load pulls: {str(e)}")

    def _populate_combos(self):
        try:
            profiles = getattr(self.lore_data, 'get_player_profiles', lambda: [])()
            self.player_combo.clear()
            for profile in profiles:
                self.player_combo.addItem(profile.get('username', 'Unknown'), profile.get('id'))

            banners = getattr(self.lore_data, 'get_banners', lambda: [])()
            self.banner_combo.clear()
            for banner in banners:
                self.banner_combo.addItem(getattr(banner, 'name', 'Unknown'), banner.id)
        except Exception:
            pass

    def _populate_table(self, pulls: List[dict]):
        self.table.setRowCount(len(pulls))
        for row, pull in enumerate(pulls):
            self.table.setItem(row, 0, QTableWidgetItem(str(pull.get('id', 'N/A'))))
            self.table.setItem(row, 1, QTableWidgetItem(str(pull.get('player_id', 'N/A'))))
            self.table.setItem(row, 2, QTableWidgetItem(str(pull.get('banner_id', 'N/A'))))
            self.table.setItem(row, 3, QTableWidgetItem(pull.get('result', 'N/A')))
            self.table.setItem(row, 4, QTableWidgetItem(pull.get('rarity', 'N/A')))
            self.table.setItem(row, 5, QTableWidgetItem(pull.get('date', 'N/A')))

    def _on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_pull = self.all_pulls[row]
            self._populate_form()
            self.delete_btn.setEnabled(True)
        else:
            self.selected_pull = None
            self._clear_form()
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        if not self.selected_pull:
            return
        self.result_input.setText(self.selected_pull.get('result', ''))
        self.rarity_combo.setCurrentText(self.selected_pull.get('rarity', 'Uncommon'))
        self.pity_count_spin.setValue(int(self.selected_pull.get('pity_count', 1)))
        self.date_input.setText(self.selected_pull.get('date', ''))

    def _clear_form(self):
        self.player_combo.setCurrentIndex(0)
        self.banner_combo.setCurrentIndex(0)
        self.result_input.clear()
        self.rarity_combo.setCurrentIndex(0)
        self.pity_count_spin.setValue(1)
        self.date_input.clear()

    def _add_pull(self):
        try:
            player_id = self.player_combo.currentData()
            banner_id = self.banner_combo.currentData()

            if not player_id or not banner_id:
                QMessageBox.warning(self, "Warning", "Both player and banner must be selected")
                return

            pull_data = {
                'player_id': player_id,
                'banner_id': banner_id,
                'result': self.result_input.text().strip(),
                'rarity': self.rarity_combo.currentText(),
                'pity_count': self.pity_count_spin.value(),
                'date': self.date_input.text().strip()
            }

            self.lore_data.add_pull(pull_data)
            QMessageBox.information(self, "Success", "Pull added successfully!")
            self._clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add pull: {str(e)}")

    def _delete_pull(self):
        if not self.selected_pull:
            return

        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.delete_pull(self.selected_pull.get('id'))
                QMessageBox.information(self, "Success", "Pull deleted successfully!")
                self._clear_form()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete pull: {str(e)}")
