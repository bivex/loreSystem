"""
MusicThemeTab - Tab for managing music themes
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


class MusicThemeTab(QWidget):
    """Tab for managing music themes."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_theme: Optional[dict] = None
        self.all_themes: List[dict] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("🎵 Music Themes")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Music Themes table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Mood", "BPM", "Tracks", "Description"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Music Theme Details")
        form_layout = QFormLayout()

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter theme name...")
        form_layout.addRow("Name:", self.name_input)

        # Mood/Genre
        self.mood_combo = QComboBox()
        self.mood_combo.addItems([
            "Calm", "Peaceful", "Energetic", "Epic", "Dark", "Mysterious", 
            "Romantic", "Tense", "Happy", "Sad", "Neutral", "Action"
        ])
        form_layout.addRow("Mood/Genre:", self.mood_combo)

        # BPM
        self.bpm_spin = QSpinBox()
        self.bpm_spin.setMinimum(0)
        self.bpm_spin.setMaximum(300)
        self.bpm_spin.setValue(120)
        form_layout.addRow("BPM:", self.bpm_spin)

        # Key
        self.key_combo = QComboBox()
        self.key_combo.addItems([
            "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
            "Am", "Cm", "Dm", "Em", "Fm", "Gm", "Other"
        ])
        form_layout.addRow("Key:", self.key_combo)

        # Instruments
        self.instruments_input = QLineEdit()
        self.instruments_input.setPlaceholderText("e.g., Piano, Strings, Drums (comma-separated)")
        form_layout.addRow("Instruments:", self.instruments_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter theme description...")
        self.description_input.setMaximumHeight(120)
        form_layout.addRow("Description:", self.description_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Theme")
        self.add_btn.clicked.connect(self._add_theme)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Theme")
        self.delete_btn.clicked.connect(self._delete_theme)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        """Refresh the music themes list."""
        try:
            self.all_themes = getattr(self.lore_data, 'get_music_themes', lambda: [])()
            self._populate_table(self.all_themes)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load music themes: {str(e)}")

    def _populate_table(self, themes: List[dict]):
        """Populate the table with music themes."""
        self.table.setRowCount(len(themes))
        for row, theme in enumerate(themes):
            self.table.setItem(row, 0, QTableWidgetItem(str(theme.get('id', 'N/A'))))
            self.table.setItem(row, 1, QTableWidgetItem(theme.get('name', 'N/A')))
            self.table.setItem(row, 2, QTableWidgetItem(theme.get('mood', 'N/A')))
            self.table.setItem(row, 3, QTableWidgetItem(str(theme.get('bpm', 120))))
            tracks_count = len(theme.get('tracks', []))
            self.table.setItem(row, 4, QTableWidgetItem(str(tracks_count)))
            self.table.setItem(row, 5, QTableWidgetItem(theme.get('description', '')))

    def _on_selection_changed(self):
        """Handle theme selection change."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_theme = self.all_themes[row]
            self._populate_form()
            self.delete_btn.setEnabled(True)
        else:
            self.selected_theme = None
            self._clear_form()
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate the form with selected theme data."""
        if not self.selected_theme:
            return
        self.name_input.setText(self.selected_theme.get('name', ''))
        self.mood_combo.setCurrentText(self.selected_theme.get('mood', 'Neutral'))
        self.bpm_spin.setValue(int(self.selected_theme.get('bpm', 120)))
        self.key_combo.setCurrentText(self.selected_theme.get('key', 'C'))
        self.instruments_input.setText(', '.join(self.selected_theme.get('instruments', [])))
        self.description_input.setPlainText(self.selected_theme.get('description', ''))

    def _clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.mood_combo.setCurrentIndex(0)
        self.bpm_spin.setValue(120)
        self.key_combo.setCurrentIndex(0)
        self.instruments_input.clear()
        self.description_input.clear()

    def _add_theme(self):
        """Add a new music theme."""
        try:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Theme name cannot be empty")
                return

            theme_data = {
                'name': name,
                'mood': self.mood_combo.currentText(),
                'bpm': self.bpm_spin.value(),
                'key': self.key_combo.currentText(),
                'instruments': [i.strip() for i in self.instruments_input.text().split(',')],
                'description': self.description_input.toPlainText()
            }

            self.lore_data.add_music_theme(theme_data)
            QMessageBox.information(self, "Success", "Music theme added successfully!")
            self._clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add music theme: {str(e)}")

    def _delete_theme(self):
        """Delete the selected theme."""
        if not self.selected_theme:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{self.selected_theme.get('name', 'Unknown')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.delete_music_theme(self.selected_theme.get('id'))
                QMessageBox.information(self, "Success", "Music theme deleted successfully!")
                self._clear_form()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete music theme: {str(e)}")
