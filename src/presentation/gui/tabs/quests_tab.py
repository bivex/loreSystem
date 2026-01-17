"""
QuestsTab - Tab for managing quests.
"""
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

from src.domain.entities.quest import Quest
from src.domain.value_objects.common import (
    EntityId, Description, Timestamp, QuestStatus
)
from src.presentation.gui.lore_data import LoreData
from src.presentation.gui.i18n import I18n


class QuestsTab(QWidget):
    """Tab for managing quests."""

    quest_selected = pyqtSignal(EntityId)

    def __init__(self, lore_data: LoreData):
        super().__init__()
        self.lore_data = lore_data
        self.selected_quest: Optional[Quest] = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "World", "Name", "Status", "Objectives"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_quest_selected)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Quest")
        self.add_btn.clicked.connect(self._add_quest)
        self.edit_btn = QPushButton("Edit Quest")
        self.edit_btn.clicked.connect(self._edit_quest)
        self.edit_btn.setEnabled(False)
        self.delete_btn = QPushButton("Delete Quest")
        self.delete_btn.clicked.connect(self._delete_quest)
        self.delete_btn.setEnabled(False)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()

        layout.addWidget(self.table)
        layout.addLayout(button_layout)

    def refresh(self):
        """Refresh the table with current quests."""
        self.table.setRowCount(0)
        for quest in self.lore_data.quests:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(quest.id.value)))
            world = self.lore_data.get_world_by_id(quest.world_id)
            world_name = str(world.name) if world else "Unknown"
            self.table.setItem(row, 1, QTableWidgetItem(world_name))
            self.table.setItem(row, 2, QTableWidgetItem(quest.name))
            self.table.setItem(row, 3, QTableWidgetItem(quest.status.value))
            objectives_text = "; ".join(quest.objectives[:2])  # Show first 2 objectives
            if len(quest.objectives) > 2:
                objectives_text += "..."
            self.table.setItem(row, 4, QTableWidgetItem(objectives_text))

    def _on_quest_selected(self):
        """Handle quest selection."""
        current_row = self.table.currentRow()
        if current_row >= 0:
            quest_id = int(self.table.item(current_row, 0).text())
            self.selected_quest = next((q for q in self.lore_data.quests if q.id.value == quest_id), None)
            self.edit_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            self.quest_selected.emit(EntityId(quest_id))
        else:
            self.selected_quest = None
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def _add_quest(self):
        """Add a new quest."""
        # Simplified: just create a basic quest
        if not self.lore_data.worlds:
            QMessageBox.warning(self, I18n.t('app.title_short', "MythWeave"), I18n.t('warning.no_worlds', "Please create a world first."))
            return

        world = self.lore_data.worlds[0]  # Use first world

        # Check if there are characters in this world
        characters_in_world = [c for c in self.lore_data.characters if c.world_id == world.id]
        if not characters_in_world:
            QMessageBox.warning(
                self, "No Characters",
                f"No characters exist in world '{world.name}'. Please create characters first before creating quests."
            )
            return

        # Use the first character as a participant
        participant_id = characters_in_world[0].id

        quest = Quest(
            id=None,
            tenant_id=self.lore_data.tenant_id,
            world_id=world.id,
            name=I18n.t('new.quest.name', "New Quest"),
            description=Description(I18n.t('new.quest.description', "Quest description")),
            objectives=["Complete objective 1"],
            status=QuestStatus.ACTIVE,
            participant_ids=[participant_id],
            reward_ids=[],
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(1)
        )
        self.lore_data.add_quest(quest)
        self.refresh()

    def _edit_quest(self):
        """Edit selected quest."""
        if self.selected_quest:
            # For now, just show a message
            QMessageBox.information(self, "Edit", f"Editing quest: {self.selected_quest.name}")

    def _delete_quest(self):
        """Delete selected quest."""
        if self.selected_quest:
            self.lore_data.quests.remove(self.selected_quest)
            self.refresh()