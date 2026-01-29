"""
MusicTrackTab - Tab for managing music tracks
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class MusicTrackTab(QWidget):
    """Tab for managing music tracks."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_track: Optional[dict] = None
        self.all_tracks: List[dict] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel("🎶 Music Tracks")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        splitter = QSplitter(Qt.Orientation.Vertical)

        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Title", "Theme", "Duration", "Artist", "Description"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Track Details")
        form_layout = QFormLayout()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter track title...")
        form_layout.addRow("Title:", self.title_input)

        self.theme_combo = QComboBox()
        form_layout.addRow("Theme:", self.theme_combo)

        self.artist_input = QLineEdit()
        self.artist_input.setPlaceholderText("Artist/Composer")
        form_layout.addRow("Artist:", self.artist_input)

        self.duration_input = QLineEdit()
        self.duration_input.setPlaceholderText("MM:SS")
        form_layout.addRow("Duration:", self.duration_input)

        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("File path or URL")
        form_layout.addRow("File Path:", self.file_path_input)

        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_input)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Track")
        self.add_btn.clicked.connect(self._add_track)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Track")
        self.delete_btn.clicked.connect(self._delete_track)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        try:
            self.all_tracks = getattr(self.lore_data, 'get_music_tracks', lambda: [])()
            self._populate_theme_combo()
            self._populate_table(self.all_tracks)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load tracks: {str(e)}")

    def _populate_theme_combo(self):
        try:
            themes = getattr(self.lore_data, 'get_music_themes', lambda: [])()
            self.theme_combo.clear()
            for theme in themes:
                self.theme_combo.addItem(theme.get('name', 'Unknown'), theme.get('id'))
        except Exception:
            pass

    def _populate_table(self, tracks: List[dict]):
        self.table.setRowCount(len(tracks))
        for row, track in enumerate(tracks):
            self.table.setItem(row, 0, QTableWidgetItem(str(track.get('id', 'N/A'))))
            self.table.setItem(row, 1, QTableWidgetItem(track.get('title', 'N/A')))
            self.table.setItem(row, 2, QTableWidgetItem(str(track.get('theme_id', 'N/A'))))
            self.table.setItem(row, 3, QTableWidgetItem(track.get('duration', 'N/A')))
            self.table.setItem(row, 4, QTableWidgetItem(track.get('artist', 'N/A')))
            self.table.setItem(row, 5, QTableWidgetItem(track.get('description', '')))

    def _on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_track = self.all_tracks[row]
            self._populate_form()
            self.delete_btn.setEnabled(True)
        else:
            self.selected_track = None
            self._clear_form()
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        if not self.selected_track:
            return
        self.title_input.setText(self.selected_track.get('title', ''))
        self.artist_input.setText(self.selected_track.get('artist', ''))
        self.duration_input.setText(self.selected_track.get('duration', ''))
        self.file_path_input.setText(self.selected_track.get('file_path', ''))
        self.description_input.setPlainText(self.selected_track.get('description', ''))

    def _clear_form(self):
        self.title_input.clear()
        self.theme_combo.setCurrentIndex(0)
        self.artist_input.clear()
        self.duration_input.clear()
        self.file_path_input.clear()
        self.description_input.clear()

    def _add_track(self):
        try:
            title = self.title_input.text().strip()
            if not title:
                QMessageBox.warning(self, "Warning", "Track title cannot be empty")
                return

            track_data = {
                'title': title,
                'theme_id': self.theme_combo.currentData(),
                'artist': self.artist_input.text().strip(),
                'duration': self.duration_input.text().strip(),
                'file_path': self.file_path_input.text().strip(),
                'description': self.description_input.toPlainText()
            }

            self.lore_data.add_music_track(track_data)
            QMessageBox.information(self, "Success", "Track added successfully!")
            self._clear_form()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add track: {str(e)}")

    def _delete_track(self):
        if not self.selected_track:
            return

        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.delete_music_track(self.selected_track.get('id'))
                QMessageBox.information(self, "Success", "Track deleted successfully!")
                self._clear_form()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete track: {str(e)}")
