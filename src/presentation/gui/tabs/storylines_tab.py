"""
StorylinesTab - Tab for managing storylines.
"""
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

from src.domain.entities.storyline import Storyline
from src.domain.value_objects.common import (
    EntityId, Description, Timestamp, StorylineType
)
from src.presentation.gui.lore_data import LoreData
from src.presentation.gui.i18n import I18n


class StorylinesTab(QWidget):
    """Tab for managing storylines."""

    storyline_selected = pyqtSignal(EntityId)

    def __init__(self, lore_data: LoreData):
        super().__init__()
        self.lore_data = lore_data
        self.selected_storyline: Optional[Storyline] = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Name", "Type"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_storyline_selected)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Storyline")
        self.add_btn.clicked.connect(self._add_storyline)
        self.edit_btn = QPushButton("Edit Storyline")
        self.edit_btn.clicked.connect(self._edit_storyline)
        self.edit_btn.setEnabled(False)
        self.delete_btn = QPushButton("Delete Storyline")
        self.delete_btn.clicked.connect(self._delete_storyline)
        self.delete_btn.setEnabled(False)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()

        layout.addWidget(self.table)
        layout.addLayout(button_layout)

    def refresh(self):
        """Refresh the table with current storylines."""
        self.table.setRowCount(0)
        for storyline in self.lore_data.storylines:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(storyline.id.value)))
            world = self.lore_data.get_world_by_id(storyline.world_id)
            world_name = str(world.name) if world else "Unknown"
            self.table.setItem(row, 1, QTableWidgetItem(world_name))
            self.table.setItem(row, 2, QTableWidgetItem(storyline.name))
            self.table.setItem(row, 3, QTableWidgetItem(storyline.storyline_type.value))

    def _on_storyline_selected(self):
        """Handle storyline selection."""
        current_row = self.table.currentRow()
        if current_row >= 0:
            storyline_id = int(self.table.item(current_row, 0).text())
            self.selected_storyline = next((s for s in self.lore_data.storylines if s.id.value == storyline_id), None)
            self.edit_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            self.storyline_selected.emit(EntityId(storyline_id))
        else:
            self.selected_storyline = None
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _add_storyline(self):
        """Add a new storyline."""
        if not self.lore_data.worlds:
            QMessageBox.warning(self, I18n.t('app.title_short', "LoreForge"), I18n.t('warning.no_worlds', "Please create a world first."))
            return

        world = self.lore_data.worlds[0]  # Use first world
        # Ensure at least one event or quest exists for the new storyline
        events_in_world = [e for e in self.lore_data.events if e.world_id == world.id]
        quests_in_world = [q for q in self.lore_data.quests if q.world_id == world.id]

        if not events_in_world and not quests_in_world:
            QMessageBox.warning(
                self,
                I18n.t('app.title_short', "LoreForge"),
                I18n.t('warning.no_events_or_quests', "Please create at least one Event or Quest in the selected world before adding a Storyline.")
            )
            return

        # Prefer adding an event if available, otherwise attach a quest
        event_ids = [events_in_world[0].id] if events_in_world else []
        quest_ids = [quests_in_world[0].id] if (not event_ids and quests_in_world) else []

        storyline = Storyline(
            id=None,
            tenant_id=self.lore_data.tenant_id,
            world_id=world.id,
            name="New Storyline",
            description=Description(I18n.t('new.storyline.description', "Storyline description")),
            storyline_type=StorylineType.MAIN,
            event_ids=event_ids,
            quest_ids=quest_ids,
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(1)
        )
        self.lore_data.add_storyline(storyline)
        self.refresh()

    def _edit_storyline(self):
        """Edit selected storyline."""
        if self.selected_storyline:
            QMessageBox.information(self, "Edit", f"Editing storyline: {self.selected_storyline.name}")

    def _delete_storyline(self):
        """Delete selected storyline."""
        if self.selected_storyline:
            self.lore_data.storylines.remove(self.selected_storyline)
            self.refresh()