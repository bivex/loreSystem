"""
BannerTab - Tab for managing banners (gacha system)
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.entities.banner import Banner
from src.domain.value_objects.common import EntityId, Description


class BannerTab(QWidget):
    """Tab for managing banners (gacha system)."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_banner: Optional[Banner] = None
        self.all_banners: List[Banner] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("🎁 Banners (Gacha)")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Banners table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Type", "Start Date", "End Date", "Description"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Banner Details")
        form_layout = QFormLayout()

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter banner name...")
        form_layout.addRow("Name:", self.name_input)

        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Character", "Weapon", "Standard", "Event"])
        form_layout.addRow("Type:", self.type_combo)

        # Start Date
        self.start_date_input = QLineEdit()
        self.start_date_input.setPlaceholderText("YYYY-MM-DD")
        form_layout.addRow("Start Date:", self.start_date_input)

        # End Date
        self.end_date_input = QLineEdit()
        self.end_date_input.setPlaceholderText("YYYY-MM-DD")
        form_layout.addRow("End Date:", self.end_date_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter banner description...")
        self.description_input.setMaximumHeight(120)
        form_layout.addRow("Description:", self.description_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Banner")
        self.add_btn.clicked.connect(self._add_banner)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Banner")
        self.delete_btn.clicked.connect(self._delete_banner)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        """Refresh the banners list."""
        try:
            self.all_banners = self.lore_data.get_banners()
            self._populate_table(self.all_banners)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load banners: {str(e)}")

    def _populate_table(self, banners: List[Banner]):
        """Populate the table with banners."""
        self.table.setRowCount(len(banners))
        for row, banner in enumerate(banners):
            self.table.setItem(row, 0, QTableWidgetItem(str(banner.id)))
            self.table.setItem(row, 1, QTableWidgetItem(getattr(banner, 'name', 'N/A')))
            self.table.setItem(row, 2, QTableWidgetItem(getattr(banner, 'type', 'N/A')))
            self.table.setItem(row, 3, QTableWidgetItem(str(getattr(banner, 'start_date', 'N/A'))))
            self.table.setItem(row, 4, QTableWidgetItem(str(getattr(banner, 'end_date', 'N/A'))))
            self.table.setItem(row, 5, QTableWidgetItem(getattr(banner, 'description', '')))

    def _on_selection_changed(self):
        """Handle banner selection change."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_banner = self.all_banners[row]
            self._populate_form()
            self.delete_btn.setEnabled(True)
        else:
            self.selected_banner = None
            self._clear_form()
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate the form with selected banner data."""
        if not self.selected_banner:
            return
        self.name_input.setText(getattr(self.selected_banner, 'name', ''))
        self.type_combo.setCurrentText(getattr(self.selected_banner, 'type', 'Standard'))
        self.start_date_input.setText(str(getattr(self.selected_banner, 'start_date', '')))
        self.end_date_input.setText(str(getattr(self.selected_banner, 'end_date', '')))
        self.description_input.setPlainText(getattr(self.selected_banner, 'description', ''))

    def _clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.start_date_input.clear()
        self.end_date_input.clear()
        self.description_input.clear()

    def _add_banner(self):
        """Add a new banner."""
        try:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Banner name cannot be empty")
                return

            banner_data = {
                'name': name,
                'type': self.type_combo.currentText(),
                'start_date': self.start_date_input.text().strip(),
                'end_date': self.end_date_input.text().strip(),
                'description': self.description_input.toPlainText()
            }

            self.lore_data.add_banner(banner_data)
            QMessageBox.information(self, "Success", "Banner added successfully!")
            self._clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add banner: {str(e)}")

    def _delete_banner(self):
        """Delete the selected banner."""
        if not self.selected_banner:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{getattr(self.selected_banner, 'name', 'Unknown')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.delete_banner(self.selected_banner.id)
                QMessageBox.information(self, "Success", "Banner deleted successfully!")
                self._clear_form()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete banner: {str(e)}")
