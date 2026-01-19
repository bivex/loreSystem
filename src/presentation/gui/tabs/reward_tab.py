"""
RewardTab - Tab for managing rewards
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.value_objects.common import EntityId


class RewardTab(QWidget):
    """Tab for managing rewards."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_reward: Optional[dict] = None
        self.all_rewards: List[dict] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("🎁 Rewards")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Rewards table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Type", "Value", "Rarity", "Description"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Reward Details")
        form_layout = QFormLayout()

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter reward name...")
        form_layout.addRow("Name:", self.name_input)

        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Item", "Currency", "Experience", "Title", "Quest", "Bonus", "Other"])
        form_layout.addRow("Type:", self.type_combo)

        # Value
        self.value_spin = QSpinBox()
        self.value_spin.setMinimum(0)
        self.value_spin.setMaximum(999999)
        form_layout.addRow("Value:", self.value_spin)

        # Rarity
        self.rarity_combo = QComboBox()
        self.rarity_combo.addItems(["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"])
        form_layout.addRow("Rarity:", self.rarity_combo)

        # Condition
        self.condition_input = QLineEdit()
        self.condition_input.setPlaceholderText("When/how is this reward given?")
        form_layout.addRow("Condition:", self.condition_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter reward description...")
        self.description_input.setMaximumHeight(120)
        form_layout.addRow("Description:", self.description_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Reward")
        self.add_btn.clicked.connect(self._add_reward)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Reward")
        self.delete_btn.clicked.connect(self._delete_reward)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        """Refresh the rewards list."""
        try:
            self.all_rewards = getattr(self.lore_data, 'get_rewards', lambda: [])()
            self._populate_table(self.all_rewards)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load rewards: {str(e)}")

    def _populate_table(self, rewards: List[dict]):
        """Populate the table with rewards."""
        self.table.setRowCount(len(rewards))
        for row, reward in enumerate(rewards):
            self.table.setItem(row, 0, QTableWidgetItem(str(reward.get('id', 'N/A'))))
            self.table.setItem(row, 1, QTableWidgetItem(reward.get('name', 'N/A')))
            self.table.setItem(row, 2, QTableWidgetItem(reward.get('type', 'N/A')))
            self.table.setItem(row, 3, QTableWidgetItem(str(reward.get('value', 0))))
            self.table.setItem(row, 4, QTableWidgetItem(reward.get('rarity', 'Common')))
            self.table.setItem(row, 5, QTableWidgetItem(reward.get('description', '')))

    def _on_selection_changed(self):
        """Handle reward selection change."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_reward = self.all_rewards[row]
            self._populate_form()
            self.delete_btn.setEnabled(True)
        else:
            self.selected_reward = None
            self._clear_form()
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate the form with selected reward data."""
        if not self.selected_reward:
            return
        self.name_input.setText(self.selected_reward.get('name', ''))
        self.type_combo.setCurrentText(self.selected_reward.get('type', 'Item'))
        self.value_spin.setValue(int(self.selected_reward.get('value', 0)))
        self.rarity_combo.setCurrentText(self.selected_reward.get('rarity', 'Common'))
        self.condition_input.setText(self.selected_reward.get('condition', ''))
        self.description_input.setPlainText(self.selected_reward.get('description', ''))

    def _clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.value_spin.setValue(0)
        self.rarity_combo.setCurrentIndex(0)
        self.condition_input.clear()
        self.description_input.clear()

    def _add_reward(self):
        """Add a new reward."""
        try:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Reward name cannot be empty")
                return

            reward_data = {
                'name': name,
                'type': self.type_combo.currentText(),
                'value': self.value_spin.value(),
                'rarity': self.rarity_combo.currentText(),
                'condition': self.condition_input.text().strip(),
                'description': self.description_input.toPlainText()
            }

            self.lore_data.add_reward(reward_data)
            QMessageBox.information(self, "Success", "Reward added successfully!")
            self._clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add reward: {str(e)}")

    def _delete_reward(self):
        """Delete the selected reward."""
        if not self.selected_reward:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{self.selected_reward.get('name', 'Unknown')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.delete_reward(self.selected_reward.get('id'))
                QMessageBox.information(self, "Success", "Reward deleted successfully!")
                self._clear_form()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete reward: {str(e)}")
