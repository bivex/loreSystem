"""
FactionMembershipTab - Tab for managing faction memberships
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class FactionMembershipTab(QWidget):
    """Tab for managing faction memberships."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_membership: Optional[dict] = None
        self.all_memberships: List[dict] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel("👥 Faction Memberships")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        splitter = QSplitter(Qt.Orientation.Vertical)

        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Member", "Faction", "Rank", "Joined", "Status"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Faction Membership Details")
        form_layout = QFormLayout()

        self.member_combo = QComboBox()
        form_layout.addRow("Member:", self.member_combo)

        self.faction_combo = QComboBox()
        form_layout.addRow("Faction:", self.faction_combo)

        self.rank_combo = QComboBox()
        self.rank_combo.addItems(["Recruit", "Member", "Officer", "Leader", "Founder"])
        form_layout.addRow("Rank:", self.rank_combo)

        self.joined_date_input = QLineEdit()
        self.joined_date_input.setPlaceholderText("YYYY-MM-DD")
        form_layout.addRow("Joined Date:", self.joined_date_input)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive", "Left", "Expelled"])
        form_layout.addRow("Status:", self.status_combo)

        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        form_layout.addRow("Notes:", self.notes_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Membership")
        self.add_btn.clicked.connect(self._add_membership)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Membership")
        self.delete_btn.clicked.connect(self._delete_membership)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        try:
            self.all_memberships = getattr(self.lore_data, 'get_faction_memberships', lambda: [])()
            self._populate_combos()
            self._populate_table(self.all_memberships)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load memberships: {str(e)}")

    def _populate_combos(self):
        try:
            characters = self.lore_data.get_characters()
            self.member_combo.clear()
            for char in characters:
                self.member_combo.addItem(getattr(char, 'name', 'Unknown'), char.id)

            factions = getattr(self.lore_data, 'get_factions', lambda: [])()
            self.faction_combo.clear()
            for faction in factions:
                self.faction_combo.addItem(faction.get('name', 'Unknown'), faction.get('id'))
        except Exception:
            pass

    def _populate_table(self, memberships: List[dict]):
        self.table.setRowCount(len(memberships))
        for row, membership in enumerate(memberships):
            self.table.setItem(row, 0, QTableWidgetItem(str(membership.get('id', 'N/A'))))
            self.table.setItem(row, 1, QTableWidgetItem(str(membership.get('member_id', 'N/A'))))
            self.table.setItem(row, 2, QTableWidgetItem(str(membership.get('faction_id', 'N/A'))))
            self.table.setItem(row, 3, QTableWidgetItem(membership.get('rank', 'Member')))
            self.table.setItem(row, 4, QTableWidgetItem(membership.get('joined_date', 'N/A')))
            self.table.setItem(row, 5, QTableWidgetItem(membership.get('status', 'Active')))

    def _on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_membership = self.all_memberships[row]
            self._populate_form()
            self.delete_btn.setEnabled(True)
        else:
            self.selected_membership = None
            self._clear_form()
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        if not self.selected_membership:
            return
        for i in range(self.member_combo.count()):
            if self.member_combo.itemData(i) == self.selected_membership.get('member_id'):
                self.member_combo.setCurrentIndex(i)
                break
        self.faction_combo.setCurrentText(str(self.selected_membership.get('faction_id', '')))
        self.rank_combo.setCurrentText(self.selected_membership.get('rank', 'Member'))
        self.joined_date_input.setText(self.selected_membership.get('joined_date', ''))
        self.status_combo.setCurrentText(self.selected_membership.get('status', 'Active'))
        self.notes_input.setPlainText(self.selected_membership.get('notes', ''))

    def _clear_form(self):
        self.member_combo.setCurrentIndex(0)
        self.faction_combo.setCurrentIndex(0)
        self.rank_combo.setCurrentIndex(0)
        self.joined_date_input.clear()
        self.status_combo.setCurrentIndex(0)
        self.notes_input.clear()

    def _add_membership(self):
        try:
            member_id = self.member_combo.currentData()
            faction_id = self.faction_combo.currentData()

            if not member_id or not faction_id:
                QMessageBox.warning(self, "Warning", "Both member and faction must be selected")
                return

            membership_data = {
                'member_id': member_id,
                'faction_id': faction_id,
                'rank': self.rank_combo.currentText(),
                'joined_date': self.joined_date_input.text().strip(),
                'status': self.status_combo.currentText(),
                'notes': self.notes_input.toPlainText()
            }

            self.lore_data.add_faction_membership(membership_data)
            QMessageBox.information(self, "Success", "Membership added successfully!")
            self._clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add membership: {str(e)}")

    def _delete_membership(self):
        if not self.selected_membership:
            return

        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.delete_faction_membership(self.selected_membership.get('id'))
                QMessageBox.information(self, "Success", "Membership deleted successfully!")
                self._clear_form()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete membership: {str(e)}")
