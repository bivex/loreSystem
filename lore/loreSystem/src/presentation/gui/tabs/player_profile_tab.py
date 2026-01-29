"""
PlayerProfileTab - Tab for managing player profiles
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class PlayerProfileTab(QWidget):
    """Tab for managing player profiles."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_profile: Optional[dict] = None
        self.all_profiles: List[dict] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel("👤 Player Profiles")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        splitter = QSplitter(Qt.Orientation.Vertical)

        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Username", "Level", "Server", "Joined", "Status"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Player Profile Details")
        form_layout = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Player username...")
        form_layout.addRow("Username:", self.username_input)

        self.level_spin = QSpinBox()
        self.level_spin.setMinimum(1)
        self.level_spin.setMaximum(999)
        self.level_spin.setValue(1)
        form_layout.addRow("Level:", self.level_spin)

        self.server_combo = QComboBox()
        self.server_combo.addItems(["NA", "EU", "ASIA", "Global", "Other"])
        form_layout.addRow("Server:", self.server_combo)

        self.joined_date_input = QLineEdit()
        self.joined_date_input.setPlaceholderText("YYYY-MM-DD")
        form_layout.addRow("Joined Date:", self.joined_date_input)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive", "Banned", "Suspended", "On Break"])
        form_layout.addRow("Status:", self.status_combo)

        self.bio_input = QTextEdit()
        self.bio_input.setPlaceholderText("Player bio/notes...")
        self.bio_input.setMaximumHeight(100)
        form_layout.addRow("Bio:", self.bio_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Profile")
        self.add_btn.clicked.connect(self._add_profile)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Profile")
        self.delete_btn.clicked.connect(self._delete_profile)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        try:
            self.all_profiles = getattr(self.lore_data, 'get_player_profiles', lambda: [])()
            self._populate_table(self.all_profiles)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load profiles: {str(e)}")

    def _populate_table(self, profiles: List[dict]):
        self.table.setRowCount(len(profiles))
        for row, profile in enumerate(profiles):
            self.table.setItem(row, 0, QTableWidgetItem(str(profile.get('id', 'N/A'))))
            self.table.setItem(row, 1, QTableWidgetItem(profile.get('username', 'N/A')))
            self.table.setItem(row, 2, QTableWidgetItem(str(profile.get('level', 1))))
            self.table.setItem(row, 3, QTableWidgetItem(profile.get('server', 'N/A')))
            self.table.setItem(row, 4, QTableWidgetItem(profile.get('joined_date', 'N/A')))
            self.table.setItem(row, 5, QTableWidgetItem(profile.get('status', 'Active')))

    def _on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_profile = self.all_profiles[row]
            self._populate_form()
            self.delete_btn.setEnabled(True)
        else:
            self.selected_profile = None
            self._clear_form()
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        if not self.selected_profile:
            return
        self.username_input.setText(self.selected_profile.get('username', ''))
        self.level_spin.setValue(int(self.selected_profile.get('level', 1)))
        self.server_combo.setCurrentText(self.selected_profile.get('server', 'Global'))
        self.joined_date_input.setText(self.selected_profile.get('joined_date', ''))
        self.status_combo.setCurrentText(self.selected_profile.get('status', 'Active'))
        self.bio_input.setPlainText(self.selected_profile.get('bio', ''))

    def _clear_form(self):
        self.username_input.clear()
        self.level_spin.setValue(1)
        self.server_combo.setCurrentIndex(0)
        self.joined_date_input.clear()
        self.status_combo.setCurrentIndex(0)
        self.bio_input.clear()

    def _add_profile(self):
        try:
            username = self.username_input.text().strip()
            if not username:
                QMessageBox.warning(self, "Warning", "Username cannot be empty")
                return

            profile_data = {
                'username': username,
                'level': self.level_spin.value(),
                'server': self.server_combo.currentText(),
                'joined_date': self.joined_date_input.text().strip(),
                'status': self.status_combo.currentText(),
                'bio': self.bio_input.toPlainText()
            }

            self.lore_data.add_player_profile(profile_data)
            QMessageBox.information(self, "Success", "Player profile added successfully!")
            self._clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add profile: {str(e)}")

    def _delete_profile(self):
        if not self.selected_profile:
            return

        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.delete_player_profile(self.selected_profile.get('id'))
                QMessageBox.information(self, "Success", "Player profile deleted successfully!")
                self._clear_form()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete profile: {str(e)}")
