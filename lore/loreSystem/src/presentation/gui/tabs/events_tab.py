"""
EventsTab - Tab for managing events.
"""
from typing import Optional
from datetime import datetime, timezone

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QPushButton, QGroupBox, QLabel,
    QListWidget, QComboBox, QMessageBox, QInputDialog
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from src.domain.entities.event import Event
from src.domain.value_objects.common import (
    TenantId, EntityId, Description, Timestamp, EventOutcome, DateRange
)


class EventsTab(QWidget):
    """Tab for managing events."""
    
    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Events")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Events table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "World", "Start Date", "End Date", "Outcome"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.table)
        
        # Form
        form_group = QGroupBox("Event Details")
        form_layout = QFormLayout()
        
        self.world_combo = QComboBox()
        self.name_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.start_date_input = QLineEdit()
        self.start_date_input.setPlaceholderText("YYYY-MM-DD")
        self.end_date_input = QLineEdit()
        self.end_date_input.setPlaceholderText("YYYY-MM-DD (optional)")
        self.outcome_combo = QComboBox()
        self.outcome_combo.addItems(["ongoing", "success", "failure", "cancelled"])
        
        form_layout.addRow("World:", self.world_combo)
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Start Date:", self.start_date_input)
        form_layout.addRow("End Date:", self.end_date_input)
        form_layout.addRow("Outcome:", self.outcome_combo)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Participants section
        participants_group = QGroupBox("Participants")
        participants_layout = QVBoxLayout()
        
        self.participants_list = QListWidget()
        participants_layout.addWidget(self.participants_list)
        
        participant_buttons = QHBoxLayout()
        self.add_participant_btn = QPushButton("Add Participant")
        self.add_participant_btn.clicked.connect(self._add_participant)
        self.remove_participant_btn = QPushButton("Remove Participant")
        self.remove_participant_btn.clicked.connect(self._remove_participant)
        
        participant_buttons.addWidget(self.add_participant_btn)
        participant_buttons.addWidget(self.remove_participant_btn)
        participants_layout.addLayout(participant_buttons)
        
        participants_group.setLayout(participants_layout)
        layout.addWidget(participants_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Event")
        self.add_btn.clicked.connect(self._add_event)
        
        self.update_btn = QPushButton("Update Event")
        self.update_btn.clicked.connect(self._update_event)
        self.update_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("Delete Event")
        self.delete_btn.clicked.connect(self._delete_event)
        self.delete_btn.setEnabled(False)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.selected_event: Optional[Event] = None
    
    def refresh(self):
        """Refresh the events table and world combo."""
        self.table.setRowCount(0)
        
        for event in self.lore_data.events:
            world = self.lore_data.get_world_by_id(event.world_id)
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(event.id.value)))
            self.table.setItem(row, 1, QTableWidgetItem(event.name))
            self.table.setItem(row, 2, QTableWidgetItem(str(world.name) if world else "Unknown"))
            self.table.setItem(row, 3, QTableWidgetItem(event.date_range.start_date.value.strftime("%Y-%m-%d")))
            end_date = event.date_range.end_date.value.strftime("%Y-%m-%d") if event.date_range.end_date else ""
            self.table.setItem(row, 4, QTableWidgetItem(end_date))
            self.table.setItem(row, 5, QTableWidgetItem(event.outcome.value))
        
        self.table.resizeColumnsToContents()
        
        # Update world combo
        self.world_combo.clear()
        for world in self.lore_data.worlds:
            self.world_combo.addItem(str(world.name), world.id.value)
    
    def _on_selection_changed(self):
        """Handle event selection."""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            event_id = EntityId(int(self.table.item(row, 0).text()))
            self.selected_event = next((e for e in self.lore_data.events if e.id == event_id), None)
            
            if self.selected_event:
                # Update form
                world_idx = self.world_combo.findData(self.selected_event.world_id.value)
                if world_idx >= 0:
                    self.world_combo.setCurrentIndex(world_idx)
                
                self.name_input.setText(self.selected_event.name)
                self.description_input.setPlainText(str(self.selected_event.description))
                self.start_date_input.setText(self.selected_event.date_range.start_date.value.strftime("%Y-%m-%d"))
                end_date = self.selected_event.date_range.end_date.value.strftime("%Y-%m-%d") if self.selected_event.date_range.end_date else ""
                self.end_date_input.setText(end_date)
                self.outcome_combo.setCurrentText(self.selected_event.outcome.value)
                
                # Update participants list
                self._refresh_participants_list()
                
                self.update_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
        else:
            self.selected_event = None
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
    
    def _refresh_participants_list(self):
        """Refresh participants list widget."""
        self.participants_list.clear()
        if self.selected_event:
            for participant_id in self.selected_event.participant_ids:
                character = next((c for c in self.lore_data.characters if c.id == participant_id), None)
                name = str(character.name) if character else f"Unknown (ID: {participant_id.value})"
                self.participants_list.addItem(name)
    
    def _add_participant(self):
        """Add a participant to the event."""
        # Get available characters from selected world
        world_id = EntityId(self.world_combo.currentData())
        available_characters = [c for c in self.lore_data.characters if c.world_id == world_id]
        
        if not available_characters:
            QMessageBox.information(self, "No Characters", "No characters available in selected world.")
            return
        
        # Show dialog to select character
        items = [str(c.name) for c in available_characters]
        item, ok = QInputDialog.getItem(self, "Add Participant", "Select character:", items, 0, False)
        
        if ok and item:
            selected_char = next(c for c in available_characters if str(c.name) == item)
            if self.selected_event and selected_char.id not in [p.value for p in self.selected_event.participant_ids]:
                # Add participant to current event
                self.selected_event.participant_ids.append(selected_char.id)
                self._refresh_participants_list()
            elif not self.selected_event:
                QMessageBox.warning(self, "No Event Selected", "Please select an event first.")
    
    def _remove_participant(self):
        """Remove selected participant."""
        current_row = self.participants_list.currentRow()
        if current_row >= 0 and self.selected_event:
            self.selected_event.participant_ids.pop(current_row)
            self._refresh_participants_list()
    
    def _add_event(self):
        """Add a new event."""
        try:
            world_id = EntityId(self.world_combo.currentData())
            
            # Parse dates
            start_date = datetime.fromisoformat(self.start_date_input.text()).replace(tzinfo=timezone.utc)
            end_date_str = self.end_date_input.text().strip()
            end_date = datetime.fromisoformat(end_date_str).replace(tzinfo=timezone.utc) if end_date_str else None
            
            event = Event.create(
                tenant_id=self.lore_data.tenant_id,
                world_id=world_id,
                name=self.name_input.text(),
                description=Description(self.description_input.toPlainText()),
                start_date=Timestamp(start_date),
                end_date=Timestamp(end_date) if end_date else None,
                outcome=EventOutcome(self.outcome_combo.currentText()),
                participant_ids=[]  # Start with no participants
            )
            self.lore_data.add_event(event)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Event created successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create event: {e}")
    
    def _update_event(self):
        """Update selected event."""
        if not self.selected_event:
            return
        
        try:
            # Parse dates
            start_date = datetime.fromisoformat(self.start_date_input.text()).replace(tzinfo=timezone.utc)
            end_date_str = self.end_date_input.text().strip()
            end_date = datetime.fromisoformat(end_date_str).replace(tzinfo=timezone.utc) if end_date_str else None
            
            # Create updated event
            updated_event = Event(
                id=self.selected_event.id,
                tenant_id=self.selected_event.tenant_id,
                world_id=EntityId(self.world_combo.currentData()),
                name=self.name_input.text(),
                description=Description(self.description_input.toPlainText()),
                date_range=DateRange(Timestamp(start_date), Timestamp(end_date) if end_date else None),
                outcome=EventOutcome(self.outcome_combo.currentText()),
                participant_ids=self.selected_event.participant_ids.copy(),
                created_at=self.selected_event.created_at,
                updated_at=Timestamp.now(),
                version=self.selected_event.version.increment()
            )
            
            # Replace in list
            idx = self.lore_data.events.index(self.selected_event)
            self.lore_data.events[idx] = updated_event
            
            self.refresh()
            QMessageBox.information(self, "Success", "Event updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update event: {e}")
    
    def _delete_event(self):
        """Delete selected event."""
        if not self.selected_event:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{self.selected_event.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.lore_data.events.remove(self.selected_event)
            self.refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Event deleted successfully!")
    
    def _clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.description_input.clear()
        self.start_date_input.clear()
        self.end_date_input.clear()
        self.participants_list.clear()
        self.selected_event = None