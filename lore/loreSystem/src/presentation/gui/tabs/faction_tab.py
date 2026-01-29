"""
FactionTab - Tab for managing factions
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.entities.faction import Faction
from src.domain.value_objects.common import EntityId


class FactionTab(QWidget):
    """Tab for managing factions."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_faction: Optional[Faction] = None
        self.all_factions: List[Faction] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("⚔️ Factions")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Factions table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Alignment", "Members", "Description"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Faction Details")
        form_layout = QFormLayout()

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter faction name...")
        form_layout.addRow("Name:", self.name_input)

        # Alignment/Ideology
        self.alignment_input = QLineEdit()
        self.alignment_input.setPlaceholderText("e.g., Good, Evil, Neutral, Chaotic, etc.")
        form_layout.addRow("Alignment:", self.alignment_input)

        # Goals
        self.goals_input = QTextEdit()
        self.goals_input.setPlaceholderText("Enter faction goals...")
        self.goals_input.setMaximumHeight(100)
        form_layout.addRow("Goals:", self.goals_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter faction description...")
        self.description_input.setMaximumHeight(120)
        form_layout.addRow("Description:", self.description_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Faction")
        self.add_btn.clicked.connect(self._add_faction)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Faction")
        self.delete_btn.clicked.connect(self._delete_faction)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        """Refresh the factions list."""
        try:
            self.all_factions = self.lore_data.get_factions()
            self._populate_table(self.all_factions)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load factions: {str(e)}")

    def _populate_table(self, factions: List[Faction]):
        """Populate the table with factions."""
        self.table.setRowCount(len(factions))
        for row, faction in enumerate(factions):
            self.table.setItem(row, 0, QTableWidgetItem(str(faction.id)))
            self.table.setItem(row, 1, QTableWidgetItem(getattr(faction, 'name', 'N/A')))
            self.table.setItem(row, 2, QTableWidgetItem(getattr(faction, 'alignment', 'N/A')))
            member_count = len(getattr(faction, 'members', []))
            self.table.setItem(row, 3, QTableWidgetItem(str(member_count)))
            self.table.setItem(row, 4, QTableWidgetItem(getattr(faction, 'description', '')))

    def _on_selection_changed(self):
        """Handle faction selection change."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_faction = self.all_factions[row]
            self._populate_form()
            self.delete_btn.setEnabled(True)
        else:
            self.selected_faction = None
            self._clear_form()
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate the form with selected faction data."""
        if not self.selected_faction:
            return
        self.name_input.setText(getattr(self.selected_faction, 'name', ''))
        self.alignment_input.setText(getattr(self.selected_faction, 'alignment', ''))
        self.goals_input.setPlainText(getattr(self.selected_faction, 'goals', ''))
        self.description_input.setPlainText(getattr(self.selected_faction, 'description', ''))

    def _clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.alignment_input.clear()
        self.goals_input.clear()
        self.description_input.clear()

    def _add_faction(self):
        """Add a new faction."""
        try:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Faction name cannot be empty")
                return

            faction_data = {
                'name': name,
                'alignment': self.alignment_input.text().strip(),
                'goals': self.goals_input.toPlainText(),
                'description': self.description_input.toPlainText()
            }

            self.lore_data.add_faction(faction_data)
            QMessageBox.information(self, "Success", "Faction added successfully!")
            self._clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add faction: {str(e)}")

    def _delete_faction(self):
        """Delete the selected faction."""
        if not self.selected_faction:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{getattr(self.selected_faction, 'name', 'Unknown')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.delete_faction(self.selected_faction.id)
                QMessageBox.information(self, "Success", "Faction deleted successfully!")
                self._clear_form()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete faction: {str(e)}")
