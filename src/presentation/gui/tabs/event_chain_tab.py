"""
EventChainTab - Tab for managing event chains/sequences
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.value_objects.common import EntityId


class EventChainTab(QWidget):
    """Tab for managing event chains/sequences."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_chain: Optional[dict] = None
        self.all_chains: List[dict] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("⛓️ Event Chains")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Event Chains table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Events Count", "Status", "Description"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Event Chain Details")
        form_layout = QFormLayout()

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter chain name...")
        form_layout.addRow("Name:", self.name_input)

        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive", "Completed", "Pending", "Failed"])
        form_layout.addRow("Status:", self.status_combo)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter event chain description...")
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Events in chain
        events_group = QGroupBox("Events in Chain")
        events_layout = QVBoxLayout()

        self.events_list = QListWidget()
        events_layout.addWidget(self.events_list)

        events_button_layout = QHBoxLayout()
        self.add_event_btn = QPushButton("Add Event to Chain")
        self.remove_event_btn = QPushButton("Remove Event")
        events_button_layout.addWidget(self.add_event_btn)
        events_button_layout.addWidget(self.remove_event_btn)
        events_layout.addLayout(events_button_layout)

        events_group.setLayout(events_layout)
        form_main_layout.addWidget(events_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Chain")
        self.add_btn.clicked.connect(self._add_chain)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Chain")
        self.delete_btn.clicked.connect(self._delete_chain)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        """Refresh the event chains list."""
        try:
            self.all_chains = getattr(self.lore_data, 'get_event_chains', lambda: [])()
            self._populate_table(self.all_chains)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load event chains: {str(e)}")

    def _populate_table(self, chains: List[dict]):
        """Populate the table with event chains."""
        self.table.setRowCount(len(chains))
        for row, chain in enumerate(chains):
            self.table.setItem(row, 0, QTableWidgetItem(str(chain.get('id', 'N/A'))))
            self.table.setItem(row, 1, QTableWidgetItem(chain.get('name', 'N/A')))
            events_count = len(chain.get('events', []))
            self.table.setItem(row, 2, QTableWidgetItem(str(events_count)))
            self.table.setItem(row, 3, QTableWidgetItem(chain.get('status', 'Pending')))
            self.table.setItem(row, 4, QTableWidgetItem(chain.get('description', '')))

    def _on_selection_changed(self):
        """Handle chain selection change."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_chain = self.all_chains[row]
            self._populate_form()
            self.delete_btn.setEnabled(True)
        else:
            self.selected_chain = None
            self._clear_form()
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate the form with selected chain data."""
        if not self.selected_chain:
            return
        self.name_input.setText(self.selected_chain.get('name', ''))
        self.status_combo.setCurrentText(self.selected_chain.get('status', 'Pending'))
        self.description_input.setPlainText(self.selected_chain.get('description', ''))
        
        # Populate events list
        self.events_list.clear()
        for event_id in self.selected_chain.get('events', []):
            self.events_list.addItem(QListWidgetItem(str(event_id)))

    def _clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.status_combo.setCurrentIndex(0)
        self.description_input.clear()
        self.events_list.clear()

    def _add_chain(self):
        """Add a new event chain."""
        try:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Chain name cannot be empty")
                return

            chain_data = {
                'name': name,
                'status': self.status_combo.currentText(),
                'description': self.description_input.toPlainText(),
                'events': []
            }

            self.lore_data.add_event_chain(chain_data)
            QMessageBox.information(self, "Success", "Event chain added successfully!")
            self._clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add event chain: {str(e)}")

    def _delete_chain(self):
        """Delete the selected chain."""
        if not self.selected_chain:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{self.selected_chain.get('name', 'Unknown')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.delete_event_chain(self.selected_chain.get('id'))
                QMessageBox.information(self, "Success", "Event chain deleted successfully!")
                self._clear_form()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete event chain: {str(e)}")
