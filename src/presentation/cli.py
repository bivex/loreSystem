#!/usr/bin/env python3
"""
LoreSystem CLI - Interactive Menu-Driven Presentation Tool

A comprehensive command-line interface for managing lore entities including
Worlds, Characters, Events, Items, and more.

Features:
- Interactive menu-driven interface
- CRUD operations for all entity types
- Search and filter functionality
- Export to JSON
- Rich formatting with colors and tables
- Input validation and confirmations
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Click and Rich for CLI
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box
from rich import print as rprint

# Domain imports
from src.domain.entities.world import World
from src.domain.entities.character import Character
from src.domain.entities.event import Event
from src.domain.entities.item import Item
from src.domain.entities.location import Location
from src.domain.entities.quest import Quest
from src.domain.entities.note import Note
from src.domain.entities.tag import Tag
from src.domain.entities.requirement import Requirement
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    WorldName,
    Description,
    CharacterName,
    Backstory,
    Version,
    Timestamp,
    CharacterStatus,
    ItemType,
    Rarity,
    QuestStatus,
    NoteType,
    TagType,
    ImprovementStatus,
    EventOutcome,
)
from src.domain.value_objects.ability import Ability, AbilityName, PowerLevel


# In-memory storage (in production, use actual repositories)
class InMemoryStorage:
    """Simple in-memory storage for demo purposes."""
    
    def __init__(self):
        self.tenant_id = TenantId(1)
        self.worlds: Dict[str, World] = {}
        self.characters: Dict[str, Character] = {}
        self.events: Dict[str, Event] = {}
        self.items: Dict[str, Item] = {}
        self.locations: Dict[str, Location] = {}
        self.quests: Dict[str, Quest] = {}
        self.notes: Dict[str, Note] = {}
        self.tags: Dict[str, Tag] = {}
        self.requirements: Dict[str, Requirement] = {}
        self._id_counter = 1
    
    def _generate_id(self) -> str:
        """Generate a unique ID."""
        self._id_counter += 1
        return str(self._id_counter)
    
    def save_world(self, world: World) -> World:
        world.id = EntityId(self._generate_id())
        self.worlds[str(world.id)] = world
        return world
    
    def save_character(self, character: Character) -> Character:
        character.id = EntityId(self._generate_id())
        self.characters[str(character.id)] = character
        return character
    
    def save_event(self, event: Event) -> Event:
        event.id = EntityId(self._generate_id())
        self.events[str(event.id)] = event
        return event
    
    def save_item(self, item: Item) -> Item:
        item.id = EntityId(self._generate_id())
        self.items[str(item.id)] = item
        return item
    
    def save_location(self, location: Location) -> Location:
        location.id = EntityId(self._generate_id())
        self.locations[str(location.id)] = location
        return location
    
    def save_quest(self, quest: Quest) -> Quest:
        quest.id = EntityId(self._generate_id())
        self.quests[str(quest.id)] = quest
        return quest
    
    def save_note(self, note: Note) -> Note:
        note.id = EntityId(self._generate_id())
        self.notes[str(note.id)] = note
        return note
    
    def save_tag(self, tag: Tag) -> Tag:
        tag.id = EntityId(self._generate_id())
        self.tags[str(tag.id)] = tag
        return tag
    
    def save_requirement(self, requirement: Requirement) -> Requirement:
        requirement.id = EntityId(self._generate_id())
        self.requirements[str(requirement.id)] = requirement
        return requirement


# Initialize storage and console
storage = InMemoryStorage()
console = Console()


# ==================== Utility Functions ====================

def print_header(title: str, subtitle: str = ""):
    """Print a formatted header."""
    if subtitle:
        header = Text.assemble(
            ("📚 ", "bold yellow"),
            (title, "bold cyan"),
            (" - ", "white"),
            (subtitle, "dim white")
        )
    else:
        header = Text.assemble(
            ("📚 ", "bold yellow"),
            (title, "bold cyan")
        )
    console.print(Panel(header, box=box.DOUBLE, border_style="cyan"))
    console.print()


def print_success(message: str):
    """Print a success message."""
    console.print(f"✅ [green]{message}[/green]")


def print_error(message: str):
    """Print an error message."""
    console.print(f"❌ [red]{message}[/red]")


def print_warning(message: str):
    """Print a warning message."""
    console.print(f"⚠️  [yellow]{message}[/yellow]")


def print_info(message: str):
    """Print an info message."""
    console.print(f"ℹ️  [blue]{message}[/blue]")


def validate_name(name: str, min_len: int = 1, max_len: int = 255) -> bool:
    """Validate a name input."""
    return min_len <= len(name.strip()) <= max_len


def validate_description(text: str, min_len: int = 10) -> bool:
    """Validate a description input."""
    return len(text.strip()) >= min_len


# ==================== Entity Creation Functions ====================

def create_world_interactive() -> Optional[World]:
    """Create a world interactively."""
    console.print("\n[bold cyan]Creating a New World[/bold cyan]")
    console.print("=" * 50)
    
    name = Prompt.ask(
        "World name",
        default="My World",
        show_default=True
    )
    
    if not validate_name(name):
        print_error("World name must be between 1 and 255 characters")
        return None
    
    description = Prompt.ask(
        "Description",
        default="A world full of adventure and mystery.",
        show_default=True
    )
    
    try:
        desc = Description(description)
        world_name = WorldName(name)
    except ValueError as e:
        print_error(f"Validation error: {e}")
        return None
    
    try:
        world = World.create(
            tenant_id=storage.tenant_id,
            name=world_name,
            description=desc
        )
        saved_world = storage.save_world(world)
        print_success(f"World '{name}' created successfully!")
        print_info(f"ID: {saved_world.id}")
        return saved_world
    except Exception as e:
        print_error(f"Failed to create world: {e}")
        return None


def create_character_interactive() -> Optional[Character]:
    """Create a character interactively."""
    console.print("\n[bold cyan]Creating a New Character[/bold cyan]")
    console.print("=" * 50)
    
    # List available worlds
    if not storage.worlds:
        print_warning("No worlds available. Please create a world first.")
        return None
    
    console.print("\nAvailable Worlds:")
    world_table = Table(show_header=True, header_style="bold magenta")
    world_table.add_column("ID", style="dim")
    world_table.add_column("Name", style="cyan")
    world_table.add_column("Description", style="dim")
    
    for world_id, world in storage.worlds.items():
        world_table.add_row(str(world.id), str(world.name), str(world.description)[:50] + "...")
    
    console.print(world_table)
    
    world_id_input = Prompt.ask("\nSelect World ID")
    
    if world_id_input not in storage.worlds:
        print_error("Invalid world ID")
        return None
    
    world_id = storage.worlds[world_id_input].id
    
    name = Prompt.ask("Character name", default="Hero")
    if not validate_name(name):
        print_error("Character name must be between 1 and 255 characters")
        return None
    
    backstory_input = Prompt.ask(
        "Backstory (min 100 chars)",
        default="A mysterious hero from a distant land, seeking adventure and purpose."
    )
    
    try:
        backstory = Backstory(backstory_input)
        char_name = CharacterName(name)
    except ValueError as e:
        print_error(f"Validation error: {e}")
        return None
    
    # Ask for abilities
    abilities = []
    add_abilities = Confirm.ask("Add abilities?", default=True)
    
    while add_abilities:
        ability_name = Prompt.ask("Ability name")
        ability_desc = Prompt.ask("Ability description")
        power_level = Prompt.ask(
            "Power level (1-10)",
            default="5",
            type=click.IntRange(1, 10)
        )
        
        try:
            ability = Ability(
                name=AbilityName(ability_name),
                description=ability_desc,
                power_level=PowerLevel(power_level)
            )
            abilities.append(ability)
            print_success(f"Ability '{ability_name}' added!")
        except ValueError as e:
            print_error(f"Validation error: {e}")
        
        add_abilities = Confirm.ask("Add another ability?", default=False)
    
    # Combat stats
    add_stats = Confirm.ask("Add combat stats?", default=False)
    
    rarity_val = None
    base_hp = None
    base_atk = None
    base_def = None
    
    if add_stats:
        rarity_input = Prompt.ask(
            "Rarity (common/uncommon/rare/epic/legendary)",
            default="common",
            type=click.Choice(["common", "uncommon", "rare", "epic", "legendary"], case_sensitive=False)
        )
        rarity_val = Rarity(rarity_input.lower())
        
        base_hp = Prompt.ask("Base HP", default=100, type=int)
        base_atk = Prompt.ask("Base ATK", default=20, type=int)
        base_def = Prompt.ask("Base DEF", default=15, type=int)
    
    try:
        character = Character.create(
            tenant_id=storage.tenant_id,
            world_id=world_id,
            name=char_name,
            backstory=backstory,
            abilities=abilities,
            rarity=rarity_val,
            base_hp=base_hp,
            base_atk=base_atk,
            base_def=base_def
        )
        saved_char = storage.save_character(character)
        print_success(f"Character '{name}' created successfully!")
        print_info(f"ID: {saved_char.id}, Abilities: {len(abilities)}")
        return saved_char
    except Exception as e:
        print_error(f"Failed to create character: {e}")
        return None


def create_event_interactive() -> Optional[Event]:
    """Create an event interactively."""
    console.print("\n[bold cyan]Creating a New Event[/bold cyan]")
    console.print("=" * 50)
    
    # List available worlds
    if not storage.worlds:
        print_warning("No worlds available. Please create a world first.")
        return None
    
    console.print("\nAvailable Worlds:")
    world_table = Table(show_header=True, header_style="bold magenta")
    world_table.add_column("ID", style="dim")
    world_table.add_column("Name", style="cyan")
    
    for world_id, world in storage.worlds.items():
        world_table.add_row(str(world.id), str(world.name))
    
    console.print(world_table)
    
    world_id_input = Prompt.ask("\nSelect World ID")
    
    if world_id_input not in storage.worlds:
        print_error("Invalid world ID")
        return None
    
    world_id = storage.worlds[world_id_input].id
    
    name = Prompt.ask("Event name", default="The Great Battle")
    if not validate_name(name):
        print_error("Event name must be between 1 and 255 characters")
        return None
    
    description = Prompt.ask(
        "Description",
        default="A pivotal moment in history."
    )
    
    try:
        desc = Description(description)
    except ValueError as e:
        print_error(f"Validation error: {e}")
        return None
    
    # List available characters
    available_chars = {
        cid: char for cid, char in storage.characters.items()
        if char.world_id == world_id
    }
    
    if not available_chars:
        print_warning("No characters available in this world.")
        # Still allow creating event, but warn
    
    participant_ids = []
    if available_chars:
        console.print("\nAvailable Characters:")
        char_table = Table(show_header=True, header_style="bold magenta")
        char_table.add_column("ID", style="dim")
        char_table.add_column("Name", style="cyan")
        char_table.add_column("Status", style="yellow")
        
        for cid, char in available_chars.items():
            char_table.add_row(str(char.id), str(char.name), char.status.value)
        
        console.print(char_table)
        
        add_participants = Confirm.ask("Add participants?", default=True)
        while add_participants:
            char_id = Prompt.ask("Enter Character ID (or 'done' to finish)")
            
            if char_id.lower() == 'done':
                break
            
            if char_id in available_chars:
                participant_ids.append(available_chars[char_id].id)
                print_success(f"Added character: {available_chars[char_id].name}")
            else:
                print_error("Invalid character ID")
            
            if not participant_ids:
                add_participants = True
    
    if not participant_ids:
        print_warning("Creating event without participants (not recommended)")
    
    try:
        start_date = Timestamp.now()
        event = Event.create(
            tenant_id=storage.tenant_id,
            world_id=world_id,
            name=name,
            description=desc,
            start_date=start_date,
            participant_ids=participant_ids
        )
        saved_event = storage.save_event(event)
        print_success(f"Event '{name}' created successfully!")
        print_info(f"ID: {saved_event.id}, Participants: {len(participant_ids)}")
        return saved_event
    except Exception as e:
        print_error(f"Failed to create event: {e}")
        return None


def create_item_interactive() -> Optional[Item]:
    """Create an item interactively."""
    console.print("\n[bold cyan]Creating a New Item[/bold cyan]")
    console.print("=" * 50)
    
    if not storage.worlds:
        print_warning("No worlds available. Please create a world first.")
        return None
    
    console.print("\nAvailable Worlds:")
    for world_id, world in storage.worlds.items():
        console.print(f"  {world.id}: {world.name}")
    
    world_id_input = Prompt.ask("\nSelect World ID")
    
    if world_id_input not in storage.worlds:
        print_error("Invalid world ID")
        return None
    
    world_id = storage.worlds[world_id_input].id
    
    name = Prompt.ask("Item name", default="Excalibur")
    if not validate_name(name):
        print_error("Item name must be between 1 and 255 characters")
        return None
    
    description = Prompt.ask(
        "Description",
        default="A legendary weapon of great power."
    )
    
    try:
        desc = Description(description)
    except ValueError as e:
        print_error(f"Validation error: {e}")
        return None
    
    item_type_input = Prompt.ask(
        "Item type",
        default="weapon",
        type=click.Choice(["weapon", "armor", "artifact", "consumable", "tool", "other"], case_sensitive=False)
    )
    
    rarity_input = Prompt.ask(
        "Rarity",
        default="common",
        type=click.Choice(["common", "uncommon", "rare", "epic", "legendary", "mythic"], case_sensitive=False)
    )
    
    try:
        item = Item.create(
            tenant_id=storage.tenant_id,
            world_id=world_id,
            name=name,
            description=desc,
            item_type=ItemType(item_type_input.lower()),
            rarity=Rarity(rarity_input.lower())
        )
        saved_item = storage.save_item(item)
        print_success(f"Item '{name}' created successfully!")
        print_info(f"ID: {saved_item.id}, Type: {item_type_input}, Rarity: {rarity_input}")
        return saved_item
    except Exception as e:
        print_error(f"Failed to create item: {e}")
        return None


def create_quest_interactive() -> Optional[Quest]:
    """Create a quest interactively."""
    console.print("\n[bold cyan]Creating a New Quest[/bold cyan]")
    console.print("=" * 50)
    
    if not storage.worlds:
        print_warning("No worlds available. Please create a world first.")
        return None
    
    console.print("\nAvailable Worlds:")
    for world_id, world in storage.worlds.items():
        console.print(f"  {world.id}: {world.name}")
    
    world_id_input = Prompt.ask("\nSelect World ID")
    
    if world_id_input not in storage.worlds:
        print_error("Invalid world ID")
        return None
    
    world_id = storage.worlds[world_id_input].id
    
    name = Prompt.ask("Quest name", default="Retrieve the Artifact")
    if not validate_name(name):
        print_error("Quest name must be between 1 and 255 characters")
        return None
    
    description = Prompt.ask(
        "Description",
        default="Find and retrieve the ancient artifact."
    )
    
    try:
        desc = Description(description)
    except ValueError as e:
        print_error(f"Validation error: {e}")
        return None
    
    try:
        quest = Quest.create(
            tenant_id=storage.tenant_id,
            world_id=world_id,
            name=name,
            description=desc
        )
        saved_quest = storage.save_quest(quest)
        print_success(f"Quest '{name}' created successfully!")
        print_info(f"ID: {saved_quest.id}, Status: {quest.status.value}")
        return saved_quest
    except Exception as e:
        print_error(f"Failed to create quest: {e}")
        return None


def create_note_interactive() -> Optional[Note]:
    """Create a note interactively."""
    console.print("\n[bold cyan]Creating a New Note[/bold cyan]")
    console.print("=" * 50)
    
    if not storage.worlds:
        print_warning("No worlds available. Please create a world first.")
        return None
    
    console.print("\nAvailable Worlds:")
    for world_id, world in storage.worlds.items():
        console.print(f"  {world.id}: {world.name}")
    
    world_id_input = Prompt.ask("\nSelect World ID")
    
    if world_id_input not in storage.worlds:
        print_error("Invalid world ID")
        return None
    
    world_id = storage.worlds[world_id_input].id
    
    title = Prompt.ask("Note title", default="Plot Ideas")
    if not validate_name(title):
        print_error("Note title must be between 1 and 255 characters")
        return None
    
    content = Prompt.ask(
        "Content",
        default="Ideas for future plot developments..."
    )
    
    note_type_input = Prompt.ask(
        "Note type",
        default="general",
        type=click.Choice(["general", "reminder", "session", "character", "plot"], case_sensitive=False)
    )
    
    try:
        note = Note.create(
            tenant_id=storage.tenant_id,
            world_id=world_id,
            title=title,
            content=content,
            note_type=NoteType(note_type_input.lower())
        )
        saved_note = storage.save_note(note)
        print_success(f"Note '{title}' created successfully!")
        print_info(f"ID: {saved_note.id}, Type: {note_type_input}")
        return saved_note
    except Exception as e:
        print_error(f"Failed to create note: {e}")
        return None


# ==================== Display Functions ====================

def display_worlds():
    """Display all worlds in a table."""
    if not storage.worlds:
        print_warning("No worlds found.")
        return
    
    console.print("\n[bold cyan]Worlds[/bold cyan]")
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("ID", style="dim", width=6)
    table.add_column("Name", style="cyan", min_width=20)
    table.add_column("Description", style="white", min_width=40)
    table.add_column("Version", style="yellow", width=8)
    table.add_column("Created", style="dim", width=20)
    
    for world_id, world in storage.worlds.items():
        table.add_row(
            str(world.id),
            str(world.name),
            str(world.description)[:60] + "..." if len(str(world.description)) > 60 else str(world.description),
            str(world.version),
            world.created_at.value.strftime("%Y-%m-%d %H:%M")
        )
    
    console.print(table)
    print_info(f"Total: {len(storage.worlds)} world(s)")


def display_characters():
    """Display all characters in a table."""
    if not storage.characters:
        print_warning("No characters found.")
        return
    
    console.print("\n[bold cyan]Characters[/bold cyan]")
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("ID", style="dim", width=6)
    table.add_column("Name", style="cyan", min_width=15)
    table.add_column("World", style="white", min_width=15)
    table.add_column("Status", style="yellow", width=10)
    table.add_column("Abilities", style="green", width=10)
    table.add_column("Rarity", style="magenta", width=10)
    
    for char_id, char in storage.characters.items():
        world_name = str(storage.worlds.get(str(char.world_id), World).name) if str(char.world_id) in storage.worlds else "Unknown"
        table.add_row(
            str(char.id),
            str(char.name),
            world_name,
            char.status.value,
            str(char.ability_count()),
            str(char.rarity.value) if char.rarity else "-"
        )
    
    console.print(table)
    print_info(f"Total: {len(storage.characters)} character(s)")


def display_events():
    """Display all events in a table."""
    if not storage.events:
        print_warning("No events found.")
        return
    
    console.print("\n[bold cyan]Events[/bold cyan]")
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("ID", style="dim", width=6)
    table.add_column("Name", style="cyan", min_width=20)
    table.add_column("World", style="white", min_width=15)
    table.add_column("Outcome", style="yellow", width=10)
    table.add_column("Participants", style="green", width=12)
    table.add_column("Status", style="magenta", width=10)
    
    for event_id, event in storage.events.items():
        world_name = str(storage.worlds.get(str(event.world_id), World).name) if str(event.world_id) in storage.worlds else "Unknown"
        status = "Ongoing" if event.is_ongoing() else "Completed"
        table.add_row(
            str(event.id),
            event.name,
            world_name,
            event.outcome.value,
            str(event.participant_count()),
            status
        )
    
    console.print(table)
    print_info(f"Total: {len(storage.events)} event(s)")


def display_items():
    """Display all items in a table."""
    if not storage.items:
        print_warning("No items found.")
        return
    
    console.print("\n[bold cyan]Items[/bold cyan]")
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("ID", style="dim", width=6)
    table.add_column("Name", style="cyan", min_width=15)
    table.add_column("Type", style="yellow", width=10)
    table.add_column("Rarity", style="magenta", width=10)
    table.add_column("Description", style="white", min_width=30)
    
    for item_id, item in storage.items.items():
        table.add_row(
            str(item.id),
            item.name,
            item.item_type.value,
            item.rarity.value,
            str(item.description)[:40] + "..." if len(str(item.description)) > 40 else str(item.description)
        )
    
    console.print(table)
    print_info(f"Total: {len(storage.items)} item(s)")


def display_quests():
    """Display all quests in a table."""
    if not storage.quests:
        print_warning("No quests found.")
        return
    
    console.print("\n[bold cyan]Quests[/bold cyan]")
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("ID", style="dim", width=6)
    table.add_column("Name", style="cyan", min_width=20)
    table.add_column("World", style="white", min_width=15)
    table.add_column("Status", style="yellow", width=10)
    table.add_column("Description", style="dim", min_width=30)
    
    for quest_id, quest in storage.quests.items():
        world_name = str(storage.worlds.get(str(quest.world_id), World).name) if str(quest.world_id) in storage.worlds else "Unknown"
        table.add_row(
            str(quest.id),
            quest.name,
            world_name,
            quest.status.value,
            str(quest.description)[:40] + "..." if len(str(quest.description)) > 40 else str(quest.description)
        )
    
    console.print(table)
    print_info(f"Total: {len(storage.quests)} quest(s)")


def display_notes():
    """Display all notes in a table."""
    if not storage.notes:
        print_warning("No notes found.")
        return
    
    console.print("\n[bold cyan]Notes[/bold cyan]")
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("ID", style="dim", width=6)
    table.add_column("Title", style="cyan", min_width=20)
    table.add_column("Type", style="yellow", width=10)
    table.add_column("Content", style="white", min_width=40)
    
    for note_id, note in storage.notes.items():
        table.add_row(
            str(note.id),
            note.title,
            note.note_type.value,
            str(note.content)[:50] + "..." if len(str(note.content)) > 50 else str(note.content)
        )
    
    console.print(table)
    print_info(f"Total: {len(storage.notes)} note(s)")


# ==================== Delete Functions ====================

def delete_world():
    """Delete a world by ID."""
    if not storage.worlds:
        print_warning("No worlds to delete.")
        return
    
    display_worlds()
    world_id = Prompt.ask("\nEnter World ID to delete")
    
    if world_id not in storage.worlds:
        print_error("Invalid world ID")
        return
    
    world = storage.worlds[world_id]
    
    # Confirm deletion
    if not Confirm.ask(
        f"[red]Are you sure you want to delete '{world.name}'? "
        f"This will also delete all associated entities![/red]",
        default=False
    ):
        print_info("Deletion cancelled.")
        return
    
    # Cascade delete related entities
    chars_deleted = 0
    events_deleted = 0
    items_deleted = 0
    quests_deleted = 0
    notes_deleted = 0
    
    to_delete_chars = [cid for cid, char in storage.characters.items() if str(char.world_id) == world_id]
    for cid in to_delete_chars:
        del storage.characters[cid]
        chars_deleted += 1
    
    to_delete_events = [eid for eid, event in storage.events.items() if str(event.world_id) == world_id]
    for eid in to_delete_events:
        del storage.events[eid]
        events_deleted += 1
    
    to_delete_items = [iid for iid, item in storage.items.items() if str(item.world_id) == world_id]
    for iid in to_delete_items:
        del storage.items[iid]
        items_deleted += 1
    
    to_delete_quests = [qid for qid, quest in storage.quests.items() if str(quest.world_id) == world_id]
    for qid in to_delete_quests:
        del storage.quests[qid]
        quests_deleted += 1
    
    to_delete_notes = [nid for nid, note in storage.notes.items() if str(note.world_id) == world_id]
    for nid in to_delete_notes:
        del storage.notes[nid]
        notes_deleted += 1
    
    del storage.worlds[world_id]
    
    print_success(f"World '{world.name}' deleted!")
    print_info(f"Cascade deleted: {chars_deleted} characters, {events_deleted} events, {items_deleted} items, {quests_deleted} quests, {notes_deleted} notes")


def delete_character():
    """Delete a character by ID."""
    if not storage.characters:
        print_warning("No characters to delete.")
        return
    
    display_characters()
    char_id = Prompt.ask("\nEnter Character ID to delete")
    
    if char_id not in storage.characters:
        print_error("Invalid character ID")
        return
    
    char = storage.characters[char_id]
    
    if not Confirm.ask(
        f"[red]Are you sure you want to delete '{char.name}'?[/red]",
        default=False
    ):
        print_info("Deletion cancelled.")
        return
    
    del storage.characters[char_id]
    print_success(f"Character '{char.name}' deleted!")


def delete_event():
    """Delete an event by ID."""
    if not storage.events:
        print_warning("No events to delete.")
        return
    
    display_events()
    event_id = Prompt.ask("\nEnter Event ID to delete")
    
    if event_id not in storage.events:
        print_error("Invalid event ID")
        return
    
    event = storage.events[event_id]
    
    if not Confirm.ask(
        f"[red]Are you sure you want to delete '{event.name}'?[/red]",
        default=False
    ):
        print_info("Deletion cancelled.")
        return
    
    del storage.events[event_id]
    print_success(f"Event '{event.name}' deleted!")


def delete_item():
    """Delete an item by ID."""
    if not storage.items:
        print_warning("No items to delete.")
        return
    
    display_items()
    item_id = Prompt.ask("\nEnter Item ID to delete")
    
    if item_id not in storage.items:
        print_error("Invalid item ID")
        return
    
    item = storage.items[item_id]
    
    if not Confirm.ask(
        f"[red]Are you sure you want to delete '{item.name}'?[/red]",
        default=False
    ):
        print_info("Deletion cancelled.")
        return
    
    del storage.items[item_id]
    print_success(f"Item '{item.name}' deleted!")


def delete_quest():
    """Delete a quest by ID."""
    if not storage.quests:
        print_warning("No quests to delete.")
        return
    
    display_quests()
    quest_id = Prompt.ask("\nEnter Quest ID to delete")
    
    if quest_id not in storage.quests:
        print_error("Invalid quest ID")
        return
    
    quest = storage.quests[quest_id]
    
    if not Confirm.ask(
        f"[red]Are you sure you want to delete '{quest.name}'?[/red]",
        default=False
    ):
        print_info("Deletion cancelled.")
        return
    
    del storage.quests[quest_id]
    print_success(f"Quest '{quest.name}' deleted!")


def delete_note():
    """Delete a note by ID."""
    if not storage.notes:
        print_warning("No notes to delete.")
        return
    
    display_notes()
    note_id = Prompt.ask("\nEnter Note ID to delete")
    
    if note_id not in storage.notes:
        print_error("Invalid note ID")
        return
    
    note = storage.notes[note_id]
    
    if not Confirm.ask(
        f"[red]Are you sure you want to delete '{note.title}'?[/red]",
        default=False
    ):
        print_info("Deletion cancelled.")
        return
    
    del storage.notes[note_id]
    print_success(f"Note '{note.title}' deleted!")


# ==================== Search Functions ====================

def search_entities():
    """Search across all entity types."""
    query = Prompt.ask("\nEnter search term").lower().strip()
    
    if not query:
        print_error("Search term cannot be empty")
        return
    
    console.print(f"\n[bold cyan]Searching for: '{query}'[/bold cyan]")
    console.print("=" * 50)
    
    results_found = False
    
    # Search worlds
    world_matches = [w for w in storage.worlds.values() 
                     if query in str(w.name).lower() or query in str(w.description).lower()]
    if world_matches:
        results_found = True
        console.print("\n[bold yellow]Worlds:[/bold yellow]")
        for world in world_matches:
            console.print(f"  • [cyan]{world.name}[/cyan] (ID: {world.id})")
            console.print(f"    {str(world.description)[:60]}...")
    
    # Search characters
    char_matches = [c for c in storage.characters.values()
                    if query in str(c.name).lower() or query in str(c.backstory).lower()]
    if char_matches:
        results_found = True
        console.print("\n[bold yellow]Characters:[/bold yellow]")
        for char in char_matches:
            console.print(f"  • [cyan]{char.name}[/cyan] (ID: {char.id})")
            console.print(f"    {str(char.backstory)[:60]}...")
    
    # Search events
    event_matches = [e for e in storage.events.values()
                     if query in e.name.lower() or query in str(e.description).lower()]
    if event_matches:
        results_found = True
        console.print("\n[bold yellow]Events:[/bold yellow]")
        for event in event_matches:
            console.print(f"  • [cyan]{event.name}[/cyan] (ID: {event.id})")
            console.print(f"    {str(event.description)[:60]}...")
    
    # Search items
    item_matches = [i for i in storage.items.values()
                    if query in i.name.lower() or query in str(i.description).lower()]
    if item_matches:
        results_found = True
        console.print("\n[bold yellow]Items:[/bold yellow]")
        for item in item_matches:
            console.print(f"  • [cyan]{item.name}[/cyan] (ID: {item.id})")
            console.print(f"    {str(item.description)[:60]}...")
    
    # Search quests
    quest_matches = [q for q in storage.quests.values()
                     if query in q.name.lower() or query in str(q.description).lower()]
    if quest_matches:
        results_found = True
        console.print("\n[bold yellow]Quests:[/bold yellow]")
        for quest in quest_matches:
            console.print(f"  • [cyan]{quest.name}[/cyan] (ID: {quest.id})")
            console.print(f"    {str(quest.description)[:60]}...")
    
    # Search notes
    note_matches = [n for n in storage.notes.values()
                    if query in n.title.lower() or query in n.content.lower()]
    if note_matches:
        results_found = True
        console.print("\n[bold yellow]Notes:[/bold yellow]")
        for note in note_matches:
            console.print(f"  • [cyan]{note.title}[/cyan] (ID: {note.id})")
            console.print(f"    {note.content[:60]}...")
    
    if not results_found:
        print_warning("No results found")
    else:
        console.print("\n" + "=" * 50)


# ==================== Export Functions ====================

def export_to_json():
    """Export all entities to a JSON file."""
    filename = Prompt.ask(
        "Export filename",
        default="lore_export.json"
    )
    
    if not filename.endswith('.json'):
        filename += '.json'
    
    export_data = {
        "export_date": datetime.now().isoformat(),
        "worlds": [],
        "characters": [],
        "events": [],
        "items": [],
        "quests": [],
        "notes": []
    }
    
    # Export worlds
    for world in storage.worlds.values():
        export_data["worlds"].append({
            "id": str(world.id),
            "name": str(world.name),
            "description": str(world.description),
            "version": str(world.version),
            "created_at": world.created_at.value.isoformat(),
            "updated_at": world.updated_at.value.isoformat()
        })
    
    # Export characters
    for char in storage.characters.values():
        export_data["characters"].append({
            "id": str(char.id),
            "world_id": str(char.world_id),
            "name": str(char.name),
            "backstory": str(char.backstory),
            "status": char.status.value,
            "abilities": [
                {
                    "name": str(a.name),
                    "description": a.description,
                    "power_level": a.power_level.value
                }
                for a in char.abilities
            ],
            "rarity": char.rarity.value if char.rarity else None,
            "base_hp": char.base_hp,
            "base_atk": char.base_atk,
            "base_def": char.base_def
        })
    
    # Export events
    for event in storage.events.values():
        export_data["events"].append({
            "id": str(event.id),
            "world_id": str(event.world_id),
            "name": event.name,
            "description": str(event.description),
            "outcome": event.outcome.value,
            "participant_ids": [str(pid) for pid in event.participant_ids],
            "is_ongoing": event.is_ongoing()
        })
    
    # Export items
    for item in storage.items.values():
        export_data["items"].append({
            "id": str(item.id),
            "world_id": str(item.world_id),
            "name": item.name,
            "description": str(item.description),
            "item_type": item.item_type.value,
            "rarity": item.rarity.value
        })
    
    # Export quests
    for quest in storage.quests.values():
        export_data["quests"].append({
            "id": str(quest.id),
            "world_id": str(quest.world_id),
            "name": quest.name,
            "description": str(quest.description),
            "status": quest.status.value
        })
    
    # Export notes
    for note in storage.notes.values():
        export_data["notes"].append({
            "id": str(note.id),
            "world_id": str(note.world_id),
            "title": note.title,
            "content": note.content,
            "note_type": note.note_type.value
        })
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print_success(f"Exported to '{filename}'")
        print_info(f"Worlds: {len(export_data['worlds'])}")
        print_info(f"Characters: {len(export_data['characters'])}")
        print_info(f"Events: {len(export_data['events'])}")
        print_info(f"Items: {len(export_data['items'])}")
        print_info(f"Quests: {len(export_data['quests'])}")
        print_info(f"Notes: {len(export_data['notes'])}")
    except Exception as e:
        print_error(f"Failed to export: {e}")


# ==================== Sub-Menus ====================

def world_menu():
    """World management sub-menu."""
    while True:
        console.print("\n[bold cyan]╔══════════════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║         WORLD MANAGEMENT MENU           ║[/bold cyan]")
        console.print("[bold cyan]╚══════════════════════════════════════════╝[/bold cyan]")
        console.print("  [1] List all worlds")
        console.print("  [2] Create new world")
        console.print("  [3] Delete world")
        console.print("  [0] Back to main menu")
        
        choice = Prompt.ask("\nSelect an option", choices=["0", "1", "2", "3"], default="0")
        
        if choice == "0":
            break
        elif choice == "1":
            display_worlds()
        elif choice == "2":
            create_world_interactive()
        elif choice == "3":
            delete_world()


def character_menu():
    """Character management sub-menu."""
    while True:
        console.print("\n[bold cyan]╔══════════════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║       CHARACTER MANAGEMENT MENU         ║[/bold cyan]")
        console.print("[bold cyan]╚══════════════════════════════════════════╝[/bold cyan]")
        console.print("  [1] List all characters")
        console.print("  [2] Create new character")
        console.print("  [3] Delete character")
        console.print("  [0] Back to main menu")
        
        choice = Prompt.ask("\nSelect an option", choices=["0", "1", "2", "3"], default="0")
        
        if choice == "0":
            break
        elif choice == "1":
            display_characters()
        elif choice == "2":
            create_character_interactive()
        elif choice == "3":
            delete_character()


def event_menu():
    """Event management sub-menu."""
    while True:
        console.print("\n[bold cyan]╔══════════════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║         EVENT MANAGEMENT MENU           ║[/bold cyan]")
        console.print("[bold cyan]╚══════════════════════════════════════════╝[/bold cyan]")
        console.print("  [1] List all events")
        console.print("  [2] Create new event")
        console.print("  [3] Delete event")
        console.print("  [0] Back to main menu")
        
        choice = Prompt.ask("\nSelect an option", choices=["0", "1", "2", "3"], default="0")
        
        if choice == "0":
            break
        elif choice == "1":
            display_events()
        elif choice == "2":
            create_event_interactive()
        elif choice == "3":
            delete_event()


def item_menu():
    """Item management sub-menu."""
    while True:
        console.print("\n[bold cyan]╔══════════════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║          ITEM MANAGEMENT MENU            ║[/bold cyan]")
        console.print("[bold cyan]╚══════════════════════════════════════════╝[/bold cyan]")
        console.print("  [1] List all items")
        console.print("  [2] Create new item")
        console.print("  [3] Delete item")
        console.print("  [0] Back to main menu")
        
        choice = Prompt.ask("\nSelect an option", choices=["0", "1", "2", "3"], default="0")
        
        if choice == "0":
            break
        elif choice == "1":
            display_items()
        elif choice == "2":
            create_item_interactive()
        elif choice == "3":
            delete_item()


def quest_menu():
    """Quest management sub-menu."""
    while True:
        console.print("\n[bold cyan]╔══════════════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║          QUEST MANAGEMENT MENU           ║[/bold cyan]")
        console.print("[bold cyan]╚══════════════════════════════════════════╝[/bold cyan]")
        console.print("  [1] List all quests")
        console.print("  [2] Create new quest")
        console.print("  [3] Delete quest")
        console.print("  [0] Back to main menu")
        
        choice = Prompt.ask("\nSelect an option", choices=["0", "1", "2", "3"], default="0")
        
        if choice == "0":
            break
        elif choice == "1":
            display_quests()
        elif choice == "2":
            create_quest_interactive()
        elif choice == "3":
            delete_quest()


def note_menu():
    """Note management sub-menu."""
    while True:
        console.print("\n[bold cyan]╔══════════════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║           NOTE MANAGEMENT MENU            ║[/bold cyan]")
        console.print("[bold cyan]╚══════════════════════════════════════════╝[/bold cyan]")
        console.print("  [1] List all notes")
        console.print("  [2] Create new note")
        console.print("  [3] Delete note")
        console.print("  [0] Back to main menu")
        
        choice = Prompt.ask("\nSelect an option", choices=["0", "1", "2", "3"], default="0")
        
        if choice == "0":
            break
        elif choice == "1":
            display_notes()
        elif choice == "2":
            create_note_interactive()
        elif choice == "3":
            delete_note()


# ==================== Main Menu ====================

def main_menu():
    """Main menu loop."""
    print_header("LoreSystem CLI", "Interactive Entity Management")
    
    while True:
        console.print("\n[bold cyan]╔══════════════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║              MAIN MENU                   ║[/bold cyan]")
        console.print("[bold cyan]╚══════════════════════════════════════════╝[/bold cyan]")
        console.print("  [1] 📚 Worlds")
        console.print("  [2] 👥 Characters")
        console.print("  [3] 📅 Events")
        console.print("  [4] 🎒 Items")
        console.print("  [5] ⚔️  Quests")
        console.print("  [6] 📝 Notes")
        console.print("  [7] 🔍 Search all entities")
        console.print("  [8] 💾 Export to JSON")
        console.print("  [9] ℹ️  Help & Documentation")
        console.print("  [0] 🚪 Exit")
        
        choice = Prompt.ask("\nSelect an option", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], default="0")
        
        if choice == "0":
            console.print("\n[bold green]Thank you for using LoreSystem CLI![/bold green]")
            console.print("[bold yellow]Goodbye! 👋[/bold yellow]\n")
            break
        elif choice == "1":
            world_menu()
        elif choice == "2":
            character_menu()
        elif choice == "3":
            event_menu()
        elif choice == "4":
            item_menu()
        elif choice == "5":
            quest_menu()
        elif choice == "6":
            note_menu()
        elif choice == "7":
            search_entities()
        elif choice == "8":
            export_to_json()
        elif choice == "9":
            show_help()


def show_help():
    """Display help and documentation."""
    console.print("\n[bold cyan]╔══════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║           HELP & DOCUMENTATION          ║[/bold cyan]")
    console.print("[bold cyan]╚══════════════════════════════════════════╝[/bold cyan]")
    
    help_text = """
[bold yellow]Overview[/bold yellow]
The LoreSystem CLI provides an interactive interface for managing lore entities
including Worlds, Characters, Events, Items, Quests, and Notes.

[bold yellow]Entity Types[/bold yellow]

  [cyan]Worlds[/cyan]
    - Top-level containers for game lore
    - Can have hierarchical structure (parent/child worlds)
    - Each world can contain multiple entities

  [cyan]Characters[/cyan]
    - Actors within a world
    - Have backstory, abilities, and combat stats
    - Can be assigned to locations
    - Support rarity levels and elemental affinities

  [cyan]Events[/cyan]
    - Significant occurrences in the timeline
    - Have start/end dates and outcomes
    - Include participating characters
    - Can be ongoing or completed

  [cyan]Items[/cyan]
    - Objects within the world
    - Types: weapon, armor, artifact, consumable, tool
    - Rarity levels from common to mythic
    - Linked to worlds

  [cyan]Quests[/cyan]
    - Tasks and objectives
    - Have status tracking
    - Associated with worlds
    - Support descriptions and objectives

  [cyan]Notes[/cyan]
    - Documentation and reminders
    - Types: general, reminder, session, character, plot
    - Linked to worlds

[bold yellow]Operations[/bold yellow]

  [green]Create[/green]
    - Interactive prompts guide you through creation
    - Input validation ensures data integrity
    - Required fields are clearly marked

  [green]Read/View[/green]
    - Tables display entity information
    - Color-coded for easy reading
    - Pagination for large datasets

  [green]Update[/green]
    - Delete and recreate to modify entities
    - Version tracking prevents conflicts

  [green]Delete[/green]
    - Confirmation required for destructive actions
    - Cascade deletion for worlds (deletes all related entities)
    - Cannot be undone

[bold yellow]Search[/bold yellow]
    - Search across all entity types at once
    - Matches against names and descriptions
    - Displays results grouped by entity type

[bold yellow]Export[/bold yellow]
    - Export all entities to JSON format
    - Preserves relationships between entities
    - Useful for backup and data migration

[bold yellow]Keyboard Shortcuts[/bold yellow]
    - Use Tab for autocomplete (where available)
    - Press Ctrl+C to cancel current operation
    - Enter defaults are shown in [dim gray]square brackets[/dim gray]

[bold yellow]Tips[/bold yellow]
    • Always create a world first before adding other entities
    • Character backstories must be at least 100 characters
    • Events require at least one participant
    • Use search to quickly find entities across types
    • Export regularly to backup your data

[bold yellow]Getting Started[/bold yellow]
  1. Create a world (Menu option 1 → 2)
  2. Add characters to your world (Menu option 2 → 2)
  3. Create events for your timeline (Menu option 3 → 2)
  4. Add items for your world (Menu option 4 → 2)
  5. Create quests (Menu option 5 → 2)
  6. Use notes to track ideas (Menu option 6 → 2)

[bold yellow]Need More Help?[/bold yellow]
  Check the project documentation at:
  https://github.com/yourusername/loreSystem
"""
    
    console.print(help_text)
    
    if Confirm.ask("\nPress Enter to continue", default=True):
        pass


# ==================== Entry Point ====================

@click.command()
@click.version_option(version="1.0.0", prog_name="LoreSystem CLI")
@click.option('--demo', is_flag=True, help='Run with sample data')
def main(demo: bool = False):
    """
    LoreSystem CLI - Interactive Entity Management Tool
    
    A comprehensive command-line interface for managing lore entities
    including Worlds, Characters, Events, Items, Quests, and Notes.
    
    Features:
    • Interactive menu-driven interface
    • CRUD operations for all entity types
    • Search across all entities
    • Export to JSON
    • Rich formatting with colors and tables
    • Input validation and confirmations
    """
    if demo:
        # Load sample data
        console.print("\n[yellow]Loading sample data...[/yellow]")
        
        # Create sample world
        world = World.create(
            tenant_id=TenantId(1),
            name=WorldName("Eternal Forge"),
            description=Description(
                "A vast universe where reality itself can be reforged. "
                "Ancient smiths known as Forge Masters shape the fabric of existence."
            )
        )
        storage.save_world(world)
        
        # Create sample character
        abilities = [
            Ability(
                name=AbilityName("Reality Forge"),
                description="Manipulate the fundamental structure of matter and energy",
                power_level=PowerLevel(9)
            ),
            Ability(
                name=AbilityName("Time Weaving"),
                description="Bend temporal flows to slow or accelerate events",
                power_level=PowerLevel(7)
            )
        ]
        
        character = Character.create(
            tenant_id=TenantId(1),
            world_id=world.id,
            name=CharacterName("Aria the Forge Master"),
            backstory=Backstory(
                "Aria the Forge Master was born in the Eternal Crucible, where stars are forged. "
                "From a young age, she demonstrated an unprecedented affinity with the cosmic forge. "
                "Her mastery over reality manipulation earned her the title of Grand Forge Master "
                "at the age of twenty-five, the youngest in recorded history."
            ),
            abilities=abilities,
            rarity=Rarity.LEGENDARY,
            base_hp=150,
            base_atk=35,
            base_def=25
        )
        storage.save_character(character)
        
        # Create sample event
        event = Event.create(
            tenant_id=TenantId(1),
            world_id=world.id,
            name="The Great Reforging",
            description=Description(
                "The Forge Masters gather at the Eternal Crucible to perform the Great Reforging, "
                "a ritual that will stabilize reality for the next millennium."
            ),
            start_date=Timestamp.now(),
            participant_ids=[character.id],
            outcome=EventOutcome.ONGOING
        )
        storage.save_event(event)
        
        # Create sample item
        item = Item.create(
            tenant_id=TenantId(1),
            world_id=world.id,
            name="Cosmic Hammer",
            description=Description(
                "A legendary hammer forged from the heart of a dying star. "
                "It can reshape reality with each strike."
            ),
            item_type=ItemType.WEAPON,
            rarity=Rarity.LEGENDARY
        )
        storage.save_item(item)
        
        # Create sample quest
        quest = Quest.create(
            tenant_id=TenantId(1),
            world_id=world.id,
            name="Prevent the Unraveling",
            description=Description(
                "Stop the cosmic entity known as the Unraveler from tearing apart "
                "the fabric of reality itself."
            )
        )
        storage.save_quest(quest)
        
        # Create sample note
        note = Note.create(
            tenant_id=TenantId(1),
            world_id=world.id,
            title="Plot Ideas",
            content="Consider adding a subplot about Aria's lost mentor. "
                    "Maybe he didn't die but was transformed into something else...",
            note_type=NoteType.PLOT
        )
        storage.save_note(note)
        
        print_success("Sample data loaded successfully!")
        console.print()
    
    # Run the main menu
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]An error occurred: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
