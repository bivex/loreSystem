"""
WorldMapTab - Tab for viewing the entire world map from above.
"""
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QSplitter, QListWidget, QTextEdit, QGroupBox, QTabWidget,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.domain.entities.world import World
from src.domain.entities.map import Map
from src.domain.value_objects.common import EntityId


class WorldMapTab(QWidget):
    """Tab for viewing the world map overview."""

    def __init__(self, lore_data):
        super().__init__()
        self.lore_data = lore_data
        self.selected_world: Optional[World] = None
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("🗺️ World Map Overview")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Splitter for worlds and details
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Worlds list
        worlds_widget = QWidget()
        worlds_layout = QVBoxLayout()

        worlds_label = QLabel("Worlds")
        worlds_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        worlds_layout.addWidget(worlds_label)

        self.worlds_list = QListWidget()
        self.worlds_list.itemSelectionChanged.connect(self._on_world_selection_changed)
        worlds_layout.addWidget(self.worlds_list)

        worlds_widget.setLayout(worlds_layout)
        splitter.addWidget(worlds_widget)

        # Right panel: Details tabs
        self.details_tabs = QTabWidget()
        self._setup_details_tabs()
        splitter.addWidget(self.details_tabs)

        splitter.setSizes([300, 700])
        layout.addWidget(splitter)

        self.setLayout(layout)

    def _setup_details_tabs(self):
        """Setup tabs for different entity types."""
        # Overview tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout()

        self.overview_text = QTextEdit()
        self.overview_text.setReadOnly(True)
        overview_layout.addWidget(self.overview_text)

        overview_tab.setLayout(overview_layout)
        self.details_tabs.addTab(overview_tab, "Overview")

        # Characters tab
        characters_tab = QWidget()
        characters_layout = QVBoxLayout()

        self.characters_table = QTableWidget()
        self.characters_table.setColumnCount(4)
        self.characters_table.setHorizontalHeaderLabels(["Name", "Status", "Abilities", "Description"])
        characters_layout.addWidget(self.characters_table)

        characters_tab.setLayout(characters_layout)
        self.details_tabs.addTab(characters_tab, "Characters")

        # Events tab
        events_tab = QWidget()
        events_layout = QVBoxLayout()

        self.events_table = QTableWidget()
        self.events_table.setColumnCount(4)
        self.events_table.setHorizontalHeaderLabels(["Name", "Start", "End", "Outcome"])
        events_layout.addWidget(self.events_table)

        events_tab.setLayout(events_layout)
        self.details_tabs.addTab(events_tab, "Events")

        # Items tab
        items_tab = QWidget()
        items_layout = QVBoxLayout()

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Name", "Type", "Rarity", "Description"])
        items_layout.addWidget(self.items_table)

        items_tab.setLayout(items_layout)
        self.details_tabs.addTab(items_tab, "Items")

        # Quests tab
        quests_tab = QWidget()
        quests_layout = QVBoxLayout()

        self.quests_table = QTableWidget()
        self.quests_table.setColumnCount(4)
        self.quests_table.setHorizontalHeaderLabels(["Name", "Status", "Objectives", "Rewards"])
        quests_layout.addWidget(self.quests_table)

        quests_tab.setLayout(quests_layout)
        self.details_tabs.addTab(quests_tab, "Quests")

        # Storylines tab
        storylines_tab = QWidget()
        storylines_layout = QVBoxLayout()

        self.storylines_table = QTableWidget()
        self.storylines_table.setColumnCount(3)
        self.storylines_table.setHorizontalHeaderLabels(["Name", "Type", "Events/Quests"])
        storylines_layout.addWidget(self.storylines_table)

        storylines_tab.setLayout(storylines_layout)
        self.details_tabs.addTab(storylines_tab, "Storylines")

        # Stories tab
        stories_tab = QWidget()
        stories_layout = QVBoxLayout()

        self.stories_table = QTableWidget()
        self.stories_table.setColumnCount(4)
        self.stories_table.setHorizontalHeaderLabels(["Name", "Type", "Content", "Choices"])
        stories_layout.addWidget(self.stories_table)

        stories_tab.setLayout(stories_layout)
        self.details_tabs.addTab(stories_tab, "Stories")

        # Tags tab
        tags_tab = QWidget()
        tags_layout = QVBoxLayout()

        self.tags_table = QTableWidget()
        self.tags_table.setColumnCount(4)
        self.tags_table.setHorizontalHeaderLabels(["Name", "Type", "Color", "Description"])
        tags_layout.addWidget(self.tags_table)

        tags_tab.setLayout(tags_layout)
        self.details_tabs.addTab(tags_tab, "Tags")

        # Images tab
        images_tab = QWidget()
        images_layout = QVBoxLayout()

        self.images_table = QTableWidget()
        self.images_table.setColumnCount(4)
        self.images_table.setHorizontalHeaderLabels(["Name", "Type", "Path", "Description"])
        images_layout.addWidget(self.images_table)

        images_tab.setLayout(images_layout)
        self.details_tabs.addTab(images_tab, "Images")

        # Maps tab
        maps_tab = QWidget()
        maps_layout = QVBoxLayout()

        self.maps_table = QTableWidget()
        self.maps_table.setColumnCount(4)
        self.maps_table.setHorizontalHeaderLabels(["Name", "Scale", "Interactive", "Description"])
        maps_layout.addWidget(self.maps_table)

        maps_tab.setLayout(maps_layout)
        self.details_tabs.addTab(maps_tab, "Maps")

        # Notes tab
        notes_tab = QWidget()
        notes_layout = QVBoxLayout()

        self.notes_table = QTableWidget()
        self.notes_table.setColumnCount(3)
        self.notes_table.setHorizontalHeaderLabels(["Title", "Content", "Tags"])
        notes_layout.addWidget(self.notes_table)

        notes_tab.setLayout(notes_layout)
        self.details_tabs.addTab(notes_tab, "Notes")

        # Sessions tab
        sessions_tab = QWidget()
        sessions_layout = QVBoxLayout()

        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(5)
        self.sessions_table.setHorizontalHeaderLabels(["Name", "Status", "Start", "Duration", "Players"])
        sessions_layout.addWidget(self.sessions_table)

        sessions_tab.setLayout(sessions_layout)
        self.details_tabs.addTab(sessions_tab, "Sessions")

    def refresh(self):
        """Refresh the worlds list."""
        self.worlds_list.clear()
        for world in self.lore_data.worlds:
            self.worlds_list.addItem(f"{world.name} (ID: {world.id.value})")

    def _on_world_selection_changed(self):
        """Handle world selection change."""
        current_item = self.worlds_list.currentItem()
        if not current_item:
            return

        # Extract world ID from item text
        text = current_item.text()
        world_id_str = text.split("(ID: ")[1].rstrip(")")
        world_id = EntityId(int(world_id_str))

        world = self.lore_data.get_world_by_id(world_id)
        if world:
            self.selected_world = world
            self._update_all_details()

    def _update_all_details(self):
        """Update all details for the selected world."""
        if not self.selected_world:
            return

        # Overview
        self._update_overview()

        # Characters
        self._update_characters()

        # Events
        self._update_events()

        # Items
        self._update_items()

        # Quests
        self._update_quests()

        # Storylines
        self._update_storylines()

        # Stories
        self._update_stories()

        # Tags
        self._update_tags()

        # Images
        self._update_images()

        # Maps
        self._update_maps()

        # Notes
        self._update_notes()

        # Sessions
        self._update_sessions()

    def _update_overview(self):
        """Update overview text."""
        if not self.selected_world:
            self.overview_text.clear()
            return

        info = f"World: {self.selected_world.name}\n"
        info += f"Description: {self.selected_world.description}\n"
        info += f"Version: {self.selected_world.version}\n\n"

        # Counts
        char_count = len([c for c in self.lore_data.characters if c.world_id == self.selected_world.id])
        event_count = len([e for e in self.lore_data.events if e.world_id == self.selected_world.id])
        item_count = len([i for i in self.lore_data.items if i.world_id == self.selected_world.id])
        quest_count = len([q for q in self.lore_data.quests if q.world_id == self.selected_world.id])

        info += f"Entities:\n"
        info += f"- Characters: {char_count}\n"
        info += f"- Events: {event_count}\n"
        info += f"- Items: {item_count}\n"
        info += f"- Quests: {quest_count}\n"

        self.overview_text.setPlainText(info)

    def _update_characters(self):
        """Update characters table."""
        self.characters_table.setRowCount(0)
        if not self.selected_world:
            return

        for char in self.lore_data.characters:
            if char.world_id == self.selected_world.id:
                row = self.characters_table.rowCount()
                self.characters_table.insertRow(row)
                self.characters_table.setItem(row, 0, QTableWidgetItem(str(char.name)))
                self.characters_table.setItem(row, 1, QTableWidgetItem(str(char.status)))
                abilities = ", ".join([str(a.name) for a in char.abilities])
                self.characters_table.setItem(row, 2, QTableWidgetItem(abilities))
                self.characters_table.setItem(row, 3, QTableWidgetItem(str(char.backstory)[:100] + "..." if len(str(char.backstory)) > 100 else str(char.backstory)))

    def _update_events(self):
        """Update events table."""
        self.events_table.setRowCount(0)
        if not self.selected_world:
            return

        for event in self.lore_data.events:
            if event.world_id == self.selected_world.id:
                row = self.events_table.rowCount()
                self.events_table.insertRow(row)
                self.events_table.setItem(row, 0, QTableWidgetItem(str(event.name)))
                self.events_table.setItem(row, 1, QTableWidgetItem(str(event.date_range.start_date)))
                self.events_table.setItem(row, 2, QTableWidgetItem(str(event.date_range.end_date) if event.date_range.end_date else "N/A"))
                self.events_table.setItem(row, 3, QTableWidgetItem(str(event.outcome)))

    def _update_items(self):
        """Update items table."""
        self.items_table.setRowCount(0)
        if not self.selected_world:
            return

        for item in self.lore_data.items:
            if item.world_id == self.selected_world.id:
                row = self.items_table.rowCount()
                self.items_table.insertRow(row)
                self.items_table.setItem(row, 0, QTableWidgetItem(str(item.name)))
                self.items_table.setItem(row, 1, QTableWidgetItem(str(item.item_type)))
                self.items_table.setItem(row, 2, QTableWidgetItem(str(item.rarity) if item.rarity else "N/A"))
                self.items_table.setItem(row, 3, QTableWidgetItem(str(item.description)[:100] + "..." if len(str(item.description)) > 100 else str(item.description)))

    def _update_quests(self):
        """Update quests table."""
        self.quests_table.setRowCount(0)
        if not self.selected_world:
            return

        for quest in self.lore_data.quests:
            if quest.world_id == self.selected_world.id:
                row = self.quests_table.rowCount()
                self.quests_table.insertRow(row)
                self.quests_table.setItem(row, 0, QTableWidgetItem(str(quest.name)))
                self.quests_table.setItem(row, 1, QTableWidgetItem(str(quest.status)))
                objectives = "\n".join(quest.objectives)
                self.quests_table.setItem(row, 2, QTableWidgetItem(objectives[:100] + "..." if len(objectives) > 100 else objectives))
                rewards = ", ".join([str(r) for r in quest.reward_ids])
                self.quests_table.setItem(row, 3, QTableWidgetItem(rewards))

    def _update_storylines(self):
        """Update storylines table."""
        self.storylines_table.setRowCount(0)
        if not self.selected_world:
            return

        for storyline in self.lore_data.storylines:
            if storyline.world_id == self.selected_world.id:
                row = self.storylines_table.rowCount()
                self.storylines_table.insertRow(row)
                self.storylines_table.setItem(row, 0, QTableWidgetItem(str(storyline.name)))
                self.storylines_table.setItem(row, 1, QTableWidgetItem(str(storyline.storyline_type)))
                events_quests = f"Events: {len(storyline.event_ids)}, Quests: {len(storyline.quest_ids)}"
                self.storylines_table.setItem(row, 2, QTableWidgetItem(events_quests))

    def _update_stories(self):
        """Update stories table."""
        self.stories_table.setRowCount(0)
        if not self.selected_world:
            return

        for story in self.lore_data.stories:
            if story.world_id == self.selected_world.id:
                row = self.stories_table.rowCount()
                self.stories_table.insertRow(row)
                self.stories_table.setItem(row, 0, QTableWidgetItem(str(story.name)))
                self.stories_table.setItem(row, 1, QTableWidgetItem(str(story.story_type)))
                self.stories_table.setItem(row, 2, QTableWidgetItem(str(story.content)[:100] + "..." if len(str(story.content)) > 100 else str(story.content)))
                self.stories_table.setItem(row, 3, QTableWidgetItem(str(len(story.choice_ids))))

    def _update_tags(self):
        """Update tags table."""
        self.tags_table.setRowCount(0)
        if not self.selected_world:
            return

        for tag in self.lore_data.tags:
            if tag.world_id == self.selected_world.id:
                row = self.tags_table.rowCount()
                self.tags_table.insertRow(row)
                self.tags_table.setItem(row, 0, QTableWidgetItem(str(tag.name)))
                self.tags_table.setItem(row, 1, QTableWidgetItem(str(tag.tag_type)))
                self.tags_table.setItem(row, 2, QTableWidgetItem(tag.color if tag.color else "N/A"))
                self.tags_table.setItem(row, 3, QTableWidgetItem(tag.description if tag.description else "N/A"))

    def _update_images(self):
        """Update images table."""
        self.images_table.setRowCount(0)
        if not self.selected_world:
            return

        for image in self.lore_data.images:
            if image.world_id == self.selected_world.id:
                row = self.images_table.rowCount()
                self.images_table.insertRow(row)
                self.images_table.setItem(row, 0, QTableWidgetItem(image.name))
                self.images_table.setItem(row, 1, QTableWidgetItem(str(image.image_type)))
                self.images_table.setItem(row, 2, QTableWidgetItem(str(image.path)))
                self.images_table.setItem(row, 3, QTableWidgetItem(image.description if image.description else "N/A"))

    def _update_maps(self):
        """Update maps table."""
        self.maps_table.setRowCount(0)
        if not self.selected_world:
            return

        for map_obj in self.lore_data.maps:
            if map_obj.world_id == self.selected_world.id:
                row = self.maps_table.rowCount()
                self.maps_table.insertRow(row)
                self.maps_table.setItem(row, 0, QTableWidgetItem(map_obj.name))
                self.maps_table.setItem(row, 1, QTableWidgetItem(map_obj.scale if map_obj.scale else "N/A"))
                self.maps_table.setItem(row, 2, QTableWidgetItem("Yes" if map_obj.is_interactive else "No"))
                self.maps_table.setItem(row, 3, QTableWidgetItem(map_obj.description if map_obj.description else "N/A"))

    def _update_notes(self):
        """Update notes table."""
        self.notes_table.setRowCount(0)
        if not self.selected_world:
            return

        for note in self.lore_data.notes:
            if note.world_id == self.selected_world.id:
                row = self.notes_table.rowCount()
                self.notes_table.insertRow(row)
                self.notes_table.setItem(row, 0, QTableWidgetItem(note.title))
                self.notes_table.setItem(row, 1, QTableWidgetItem(note.content[:100] + "..." if len(note.content) > 100 else note.content))
                self.notes_table.setItem(row, 2, QTableWidgetItem(", ".join(note.tags)))

    def _update_sessions(self):
        """Update sessions table."""
        self.sessions_table.setRowCount(0)
        if not self.selected_world:
            return

        for session in self.lore_data.sessions:
            if session.world_id == self.selected_world.id:
                row = self.sessions_table.rowCount()
                self.sessions_table.insertRow(row)
                self.sessions_table.setItem(row, 0, QTableWidgetItem(str(session.name)))
                self.sessions_table.setItem(row, 1, QTableWidgetItem(str(session.status)))
                self.sessions_table.setItem(row, 2, QTableWidgetItem(str(session.scheduled_start)))
                self.sessions_table.setItem(row, 3, QTableWidgetItem(f"{session.estimated_duration_hours}h"))
                self.sessions_table.setItem(row, 4, QTableWidgetItem(str(len(session.player_ids))))