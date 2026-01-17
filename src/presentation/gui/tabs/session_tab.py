"""
SessionTab - Tab for managing gaming sessions
"""
from typing import Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QComboBox, QMessageBox, QSplitter, QDoubleSpinBox, QDateTimeEdit
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont

from src.domain.entities.session import Session
from src.domain.value_objects.common import (
    TenantId, EntityId, SessionName, SessionStatus, Timestamp
)


class SessionTab(QWidget):
    """Tab for managing gaming sessions."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_session: Optional[Session] = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("🎲 Sessions")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for table and form
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Sessions table
        table_widget = QWidget()
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Name", "Status", "GM", "Players", "Scheduled", "Duration (hrs)", "Updated"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        splitter.addWidget(table_widget)

        # Form section
        form_widget = QWidget()
        form_main_layout = QVBoxLayout()

        form_group = QGroupBox("Session Details")
        form_layout = QFormLayout()

        # World selection
        self.world_combo = QComboBox()
        form_layout.addRow("World:", self.world_combo)

        # Session name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter session name...")
        form_layout.addRow("Name:", self.name_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Session description...")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)

        # GM selection
        self.gm_combo = QComboBox()
        form_layout.addRow("Game Master:", self.gm_combo)

        # Player IDs (comma-separated)
        self.players_input = QLineEdit()
        self.players_input.setPlaceholderText("player_id1, player_id2 (comma-separated)")
        form_layout.addRow("Player IDs:", self.players_input)

        # Scheduled start
        self.scheduled_start_input = QDateTimeEdit()
        self.scheduled_start_input.setDateTime(QDateTime.currentDateTime().addDays(1))
        self.scheduled_start_input.setCalendarPopup(True)
        form_layout.addRow("Scheduled Start:", self.scheduled_start_input)

        # Estimated duration
        self.duration_input = QDoubleSpinBox()
        self.duration_input.setRange(0.5, 24.0)
        self.duration_input.setValue(3.0)
        self.duration_input.setSuffix(" hours")
        form_layout.addRow("Est. Duration:", self.duration_input)

        # Status combo
        self.status_combo = QComboBox()
        self.status_combo.addItem("Scheduled", SessionStatus.SCHEDULED.value)
        self.status_combo.addItem("Active", SessionStatus.ACTIVE.value)
        self.status_combo.addItem("Completed", SessionStatus.COMPLETED.value)
        self.status_combo.addItem("Cancelled", SessionStatus.CANCELLED.value)
        form_layout.addRow("Status:", self.status_combo)

        form_group.setLayout(form_layout)
        form_main_layout.addWidget(form_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Session")
        self.add_btn.clicked.connect(self._add_session)

        self.update_btn = QPushButton("Update Session")
        self.update_btn.clicked.connect(self._update_session)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Session")
        self.delete_btn.clicked.connect(self._delete_session)
        self.delete_btn.setEnabled(False)

        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.clicked.connect(self._clear_form)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()

        form_main_layout.addLayout(button_layout)
        form_widget.setLayout(form_main_layout)
        splitter.addWidget(form_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh(self):
        """Refresh the sessions table and combo boxes."""
        # Update worlds combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(f"{world.name.value}", world.id.value)

        # Update GM combo (using characters as potential GMs)
        self.gm_combo.clear()
        for character in self.lore_data.characters:
            self.gm_combo.addItem(f"{character.name.value} (ID: {character.id.value})", character.id.value)

        # Update sessions table
        self.table.setRowCount(0)
        for session in self.lore_data.sessions:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(session.id.value) if session.id else ""))

            # World
            world_name = "Unknown"
            for world in self.lore_data.worlds:
                if world.id == session.world_id:
                    world_name = world.name.value
                    break
            self.table.setItem(row, 1, QTableWidgetItem(world_name))

            # Name
            self.table.setItem(row, 2, QTableWidgetItem(str(session.name.value)))

            # Status
            status_emoji = {"scheduled": "📅", "active": "▶️", "completed": "✅", "cancelled": "❌"}
            status_display = f"{status_emoji.get(session.status.value, '')} {session.status.value.title()}"
            self.table.setItem(row, 3, QTableWidgetItem(status_display))

            # GM
            self.table.setItem(row, 4, QTableWidgetItem(str(session.gm_id.value)))

            # Players count
            self.table.setItem(row, 5, QTableWidgetItem(str(len(session.player_ids))))

            # Scheduled
            self.table.setItem(row, 6, QTableWidgetItem(session.scheduled_start.value.strftime("%Y-%m-%d %H:%M")))

            # Duration
            self.table.setItem(row, 7, QTableWidgetItem(str(session.estimated_duration_hours)))

            # Updated
            self.table.setItem(row, 8, QTableWidgetItem(session.updated_at.value.strftime("%Y-%m-%d %H:%M")))

        self.table.resizeColumnsToContents()

    def _on_selection_changed(self):
        """Handle session selection changes."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if len(selected_rows) == 1:
            row = list(selected_rows)[0]
            session_id = int(self.table.item(row, 0).text())
            self.selected_session = next((s for s in self.lore_data.sessions if s.id and s.id.value == session_id), None)
            if self.selected_session:
                self._populate_form()
                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
            else:
                self._clear_form()
                self.update_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
        else:
            self.selected_session = None
            self._clear_form()
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _populate_form(self):
        """Populate form with selected session data."""
        if not self.selected_session:
            return

        # Set world
        for i in range(self.world_combo.count()):
            if self.world_combo.itemData(i) == self.selected_session.world_id.value:
                self.world_combo.setCurrentIndex(i)
                break

        # Set GM
        for i in range(self.gm_combo.count()):
            if self.gm_combo.itemData(i) == self.selected_session.gm_id.value:
                self.gm_combo.setCurrentIndex(i)
                break

        # Set fields
        self.name_input.setText(str(self.selected_session.name.value))
        self.description_input.setText(self.selected_session.description)
        self.players_input.setText(", ".join(str(p.value) for p in self.selected_session.player_ids))

        # Set scheduled start
        py_dt = self.selected_session.scheduled_start.value
        qt_dt = QDateTime(py_dt.year, py_dt.month, py_dt.day, py_dt.hour, py_dt.minute, py_dt.second)
        self.scheduled_start_input.setDateTime(qt_dt)

        self.duration_input.setValue(self.selected_session.estimated_duration_hours)

        # Set status
        for i in range(self.status_combo.count()):
            if self.status_combo.itemData(i) == self.selected_session.status.value:
                self.status_combo.setCurrentIndex(i)
                break

    def _clear_form(self):
        """Clear all form fields."""
        self.name_input.clear()
        self.description_input.clear()
        self.players_input.clear()
        self.scheduled_start_input.setDateTime(QDateTime.currentDateTime().addDays(1))
        self.duration_input.setValue(3.0)
        if self.world_combo.count() > 0:
            self.world_combo.setCurrentIndex(0)
        if self.gm_combo.count() > 0:
            self.gm_combo.setCurrentIndex(0)
        if self.status_combo.count() > 0:
            self.status_combo.setCurrentIndex(0)

    def _add_session(self):
        """Add a new session."""
        try:
            # Validate inputs
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Session name cannot be empty.")
                return

            if self.world_combo.currentData() is None:
                QMessageBox.warning(self, "Validation Error", "Please select a world.")
                return

            if self.gm_combo.currentData() is None:
                QMessageBox.warning(self, "Validation Error", "Please select a Game Master.")
                return

            # Parse player IDs
            player_ids = []
            if self.players_input.text().strip():
                for p_str in self.players_input.text().split(","):
                    p_id_str = p_str.strip()
                    if p_id_str:
                        try:
                            player_ids.append(EntityId(int(p_id_str)))
                        except ValueError:
                            QMessageBox.warning(self, "Validation Error", f"Invalid player ID: {p_id_str}")
                            return

            if not player_ids:
                QMessageBox.warning(self, "Validation Error", "Session must have at least one player.")
                return

            # Convert QDateTime to Python datetime
            qt_dt = self.scheduled_start_input.dateTime()
            py_dt = datetime(qt_dt.date().year(), qt_dt.date().month(), qt_dt.date().day(),
                           qt_dt.time().hour(), qt_dt.time().minute(), qt_dt.time().second())

            # Create session
            session = Session.create(
                tenant_id=TenantId(1),
                world_id=EntityId(self.world_combo.currentData()),
                name=SessionName(self.name_input.text().strip()),
                description=self.description_input.toPlainText().strip(),
                player_ids=player_ids,
                gm_id=EntityId(self.gm_combo.currentData()),
                scheduled_start=Timestamp(py_dt),
                estimated_duration_hours=self.duration_input.value()
            )

            self.lore_data.add_session(session)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Session added successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add session: {str(e)}")

    def _update_session(self):
        """Update the selected session."""
        if not self.selected_session:
            return

        try:
            # Validate inputs
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Session name cannot be empty.")
                return

            # Parse player IDs
            player_ids = []
            if self.players_input.text().strip():
                for p_str in self.players_input.text().split(","):
                    p_id_str = p_str.strip()
                    if p_id_str:
                        try:
                            player_ids.append(EntityId(int(p_id_str)))
                        except ValueError:
                            QMessageBox.warning(self, "Validation Error", f"Invalid player ID: {p_id_str}")
                            return

            if not player_ids:
                QMessageBox.warning(self, "Validation Error", "Session must have at least one player.")
                return

            # Update name
            object.__setattr__(self.selected_session, 'name', SessionName(self.name_input.text().strip()))

            # Update description
            self.selected_session.update_description(self.description_input.toPlainText().strip())

            # Update player_ids
            object.__setattr__(self.selected_session, 'player_ids', player_ids)

            # Update scheduled start
            qt_dt = self.scheduled_start_input.dateTime()
            py_dt = datetime(qt_dt.date().year(), qt_dt.date().month(), qt_dt.date().day(),
                           qt_dt.time().hour(), qt_dt.time().minute(), qt_dt.time().second())
            object.__setattr__(self.selected_session, 'scheduled_start', Timestamp(py_dt))

            # Update duration
            object.__setattr__(self.selected_session, 'estimated_duration_hours', self.duration_input.value())

            # Update status
            new_status = SessionStatus(self.status_combo.currentData())
            object.__setattr__(self.selected_session, 'status', new_status)

            # Update metadata
            object.__setattr__(self.selected_session, 'updated_at', Timestamp.now())
            object.__setattr__(self.selected_session, 'version', self.selected_session.version.increment())

            self.refresh()
            QMessageBox.information(self, "Success", "Session updated successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update session: {str(e)}")

    def _delete_session(self):
        """Delete the selected session."""
        if not self.selected_session:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the session '{self.selected_session.name.value}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lore_data.sessions.remove(self.selected_session)
                self.refresh()
                self._clear_form()
                QMessageBox.information(self, "Success", "Session deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete session: {str(e)}")
