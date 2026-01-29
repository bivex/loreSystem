#!/usr/bin/env python3
"""
LoreSystem CLI - Command-line interface for lore management

A production-ready CLI tool for managing worlds, characters, events, and stories
in the LoreSystem. Supports CRUD operations, JSON import/export, and statistics.

Usage:
    lore-cli --help
    lore-cli world list
    lore-cli world create --name "My World" --description "A fantasy world"
    lore-cli character create --world-id 1 --name "Hero" --backstory "Once upon a time..."
    lore-cli export --output lore_data.json
    lore-cli import --input lore_data.json
    lore-cli stats
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import traceback

# Color output
try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Fallback class
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
        BRIGHT_RED = BRIGHT_GREEN = BRIGHT_YELLOW = ""
    class Style:
        BRIGHT = DIM = RESET_ALL = NORMAL = ""
    class Back:
        RESET = ""

# Progress bar
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


# Domain imports
from src.domain.entities.world import World
from src.domain.entities.character import Character
from src.domain.entities.event import Event
from src.domain.entities.story import Story
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    WorldName,
    CharacterName,
    Description,
    Backstory,
    Content,
    StoryName,
    Timestamp,
    Version,
    CharacterStatus,
    StoryType,
    EventOutcome,
)
from src.domain.exceptions import (
    DuplicateEntity,
    EntityNotFound,
    InvariantViolation,
    InvalidState,
)

# Repository imports
from src.infrastructure.in_memory_repositories import (
    InMemoryWorldRepository,
    InMemoryCharacterRepository,
    InMemoryEventRepository,
    InMemoryStoryRepository,
)


# ============================================================================
# CLI Configuration
# ============================================================================

TENANT_ID = TenantId(1)  # Default tenant for CLI operations


# ============================================================================
# Output Helpers
# ============================================================================

class CLIOutput:
    """Handles colorized CLI output."""

    @staticmethod
    def success(message: str) -> None:
        """Print success message in green."""
        if COLORS_AVAILABLE:
            print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
        else:
            print(f"✓ {message}")

    @staticmethod
    def error(message: str) -> None:
        """Print error message in red."""
        if COLORS_AVAILABLE:
            print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}", file=sys.stderr)
        else:
            print(f"✗ {message}", file=sys.stderr)

    @staticmethod
    def warning(message: str) -> None:
        """Print warning message in yellow."""
        if COLORS_AVAILABLE:
            print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
        else:
            print(f"⚠ {message}")

    @staticmethod
    def info(message: str) -> None:
        """Print info message in blue."""
        if COLORS_AVAILABLE:
            print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")
        else:
            print(f"ℹ {message}")

    @staticmethod
    def header(message: str) -> None:
        """Print section header."""
        if COLORS_AVAILABLE:
            print(f"\n{Fore.BLUE}{Style.BRIGHT}{message}{Style.RESET_ALL}")
        else:
            print(f"\n{message}")

    @staticmethod
    def table_row(row: List[str], widths: List[int]) -> None:
        """Print a table row with formatted columns."""
        formatted = []
        for i, (cell, width) in enumerate(zip(row, widths)):
            cell_str = str(cell)[:width] if len(str(cell)) > width else str(cell)
            if i < len(row) - 1:
                formatted.append(f"{cell_str:<{width}}")
            else:
                formatted.append(cell_str)
        print(" │ ".join(formatted))

    @staticmethod
    def table_separator(widths: List[int]) -> None:
        """Print a table separator line."""
        separator = "─┼─".join("─" * w for w in widths)
        print(separator)


# ============================================================================
# Progress Indicators
# ============================================================================

class ProgressIndicator:
    """Context manager for showing progress."""

    def __init__(self, description: str, total: Optional[int] = None):
        self.description = description
        self.total = total
        self.pbar = None

    def __enter__(self):
        if TQDM_AVAILABLE and self.total:
            self.pbar = tqdm(
                total=self.total,
                desc=self.description,
                unit="item",
                ncols=80,
            )
        else:
            print(f"{self.description}...", end=" ", flush=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.pbar:
            self.pbar.close()
        else:
            print("done")

    def update(self, n: int = 1) -> None:
        """Update progress."""
        if self.pbar:
            self.pbar.update(n)


# ============================================================================
# Formatters
# ============================================================================

class EntityFormatter:
    """Format entities for CLI display."""

    @staticmethod
    def format_world(world: World) -> str:
        """Format world entity."""
        status = f"v{world.version.value}"
        return (
            f"{Fore.CYAN if COLORS_AVAILABLE else ''}ID {world.id}{Style.RESET_ALL}: "
            f"{Fore.GREEN if COLORS_AVAILABLE else ''}{world.name}{Style.RESET_ALL} "
            f"({status})"
        )

    @staticmethod
    def format_world_detail(world: World) -> str:
        """Format world with full details."""
        return f"""
{Fore.CYAN if COLORS_AVAILABLE else ''}{world.name}{Style.RESET_ALL} (ID: {world.id})
{Fore.YELLOW if COLORS_AVAILABLE else ''}Description:{Style.RESET_ALL} {world.description}
{Fore.YELLOW if COLORS_AVAILABLE else ''}Version:{Style.RESET_ALL} {world.version}
{Fore.YELLOW if COLORS_AVAILABLE else ''}Created:{Style.RESET_ALL} {world.created_at.value.strftime('%Y-%m-%d %H:%M')}
{Fore.YELLOW if COLORS_AVAILABLE else ''}Updated:{Style.RESET_ALL} {world.updated_at.value.strftime('%Y-%m-%d %H:%M')}
"""

    @staticmethod
    def format_character(character: Character) -> str:
        """Format character entity."""
        status_color = Fore.GREEN if COLORS_AVAILABLE and character.status == CharacterStatus.ACTIVE else Fore.RED
        return (
            f"{Fore.CYAN if COLORS_AVAILABLE else ''}ID {character.id}{Style.RESET_ALL}: "
            f"{Fore.GREEN if COLORS_AVAILABLE else ''}{character.name}{Style.RESET_ALL} "
            f"[{status_color if COLORS_AVAILABLE else ''}{character.status.value}{Style.RESET_ALL}] "
            f"({len(character.abilities)} abilities)"
        )

    @staticmethod
    def format_character_detail(character: Character) -> str:
        """Format character with full details."""
        rarity_str = f" {character.rarity.value}" if character.rarity else ""
        role_str = f" - {character.role.value}" if character.role else ""
        element_str = f" [{character.element.value}]" if character.element else ""

        abilities_text = "\n  ".join(
            f"• {ability.name} (Power: {ability.power_level.value})"
            for ability in character.abilities
        ) if character.abilities else "None"

        stats = []
        if character.base_hp is not None:
            stats.append(f"HP: {character.base_hp}")
        if character.base_atk is not None:
            stats.append(f"ATK: {character.base_atk}")
        if character.base_def is not None:
            stats.append(f"DEF: {character.base_def}")
        if character.base_speed is not None:
            stats.append(f"SPD: {character.base_speed}")
        stats_text = ", ".join(stats) if stats else "None"

        return f"""
{Fore.CYAN if COLORS_AVAILABLE else ''}{character.name}{Style.RESET_ALL}{element_str}{rarity_str}{role_str} (ID: {character.id})
{Fore.YELLOW if COLORS_AVAILABLE else ''}Status:{Style.RESET_ALL} {character.status.value}
{Fore.YELLOW if COLORS_AVAILABLE else ''}Backstory:{Style.RESET_ALL} {character.backstory.excerpt(150)}...
{Fore.YELLOW if COLORS_AVAILABLE else ''}Stats:{Style.RESET_ALL} {stats_text}
{Fore.YELLOW if COLORS_AVAILABLE else ''}Abilities:{Style.RESET_ALL}
  {abilities_text}
"""

    @staticmethod
    def format_event(event: Event) -> str:
        """Format event entity."""
        status = "🔥 ONGOING" if event.is_ongoing() else f"✓ {event.outcome.value}"
        status_color = Fore.YELLOW if COLORS_AVAILABLE and event.is_ongoing() else Fore.GREEN
        return (
            f"{Fore.CYAN if COLORS_AVAILABLE else ''}ID {event.id}{Style.RESET_ALL}: "
            f"{Fore.GREEN if COLORS_AVAILABLE else ''}{event.name}{Style.RESET_ALL} "
            f"[{status_color if COLORS_AVAILABLE else ''}{status}{Style.RESET_ALL}] "
            f"({event.participant_count()} participants)"
        )

    @staticmethod
    def format_event_detail(event: Event) -> str:
        """Format event with full details."""
        date_str = event.date_range.start_date.value.strftime('%Y-%m-%d')
        if event.date_range.end_date:
            date_str += f" to {event.date_range.end_date.value.strftime('%Y-%m-%d')}"

        return f"""
{Fore.CYAN if COLORS_AVAILABLE else ''}{event.name}{Style.RESET_ALL} (ID: {event.id})
{Fore.YELLOW if COLORS_AVAILABLE else ''}When:{Style.RESET_ALL} {date_str}
{Fore.YELLOW if COLORS_AVAILABLE else ''}Outcome:{Style.RESET_ALL} {event.outcome.value}
{Fore.YELLOW if COLORS_AVAILABLE else ''}Participants:{Style.RESET_ALL} {event.participant_count()} characters
{Fore.YELLOW if COLORS_AVAILABLE else ''}Description:{Style.RESET_ALL} {event.description.value[:200]}...
"""

    @staticmethod
    def format_story(story: Story) -> str:
        """Format story entity."""
        status = "✓ Active" if story.is_active else "○ Inactive"
        status_color = Fore.GREEN if COLORS_AVAILABLE and story.is_active else Fore.GREY
        return (
            f"{Fore.CYAN if COLORS_AVAILABLE else ''}ID {story.id}{Style.RESET_ALL}: "
            f"{Fore.GREEN if COLORS_AVAILABLE else ''}{story.name}{Style.RESET_ALL} "
            f"[{status_color if COLORS_AVAILABLE else ''}{status}{Style.RESET_ALL}] "
            f"({story.story_type.value})"
        )

    @staticmethod
    def format_story_detail(story: Story) -> str:
        """Format story with full details."""
        return f"""
{Fore.CYAN if COLORS_AVAILABLE else ''}{story.name}{Style.RESET_ALL} (ID: {story.id})
{Fore.YELLOW if COLORS_AVAILABLE else ''}Type:{Style.RESET_ALL} {story.story_type.value}
{Fore.YELLOW if COLORS_AVAILABLE else ''}Status:{Style.RESET_ALL} {'Active' if story.is_active else 'Inactive'}
{Fore.YELLOW if COLORS_AVAILABLE else ''}Description:{Style.RESET_ALL} {story.description[:200]}...
{Fore.YELLOW if COLORS_AVAILABLE else ''}Content:{Style.RESET_ALL} {story.content.excerpt(150)}...
{Fore.YELLOW if COLORS_AVAILABLE else ''}Choices:{Style.RESET_ALL} {len(story.choice_ids)}
{Fore.YELLOW if COLORS_AVAILABLE else ''}Connected Elements:{Style.RESET_ALL} {len(story.connected_world_ids)}
"""


# ============================================================================
# CLI Commands
# ============================================================================

class WorldCommands:
    """Commands for world management."""

    def __init__(self, repo: InMemoryWorldRepository):
        self.repo = repo

    def list(self, args: argparse.Namespace) -> int:
        """List all worlds."""
        try:
            worlds = self.repo.list_by_tenant(TENANT_ID)

            if not worlds:
                CLIOutput.info("No worlds found. Create one with 'world create'")
                return 0

            CLIOutput.header(f"Worlds ({len(worlds)})")
            for world in worlds:
                print(f"  {EntityFormatter.format_world(world)}")

            return 0

        except Exception as e:
            CLIOutput.error(f"Failed to list worlds: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1

    def create(self, args: argparse.Namespace) -> int:
        """Create a new world."""
        try:
            # Validate inputs
            if not args.name:
                CLIOutput.error("World name is required")
                return 1

            if not args.description:
                CLIOutput.error("World description is required")
                return 1

            # Create world
            world = World.create(
                tenant_id=TENANT_ID,
                name=WorldName(args.name),
                description=Description(args.description),
            )

            # Save to repository
            saved_world = self.repo.save(world)

            CLIOutput.success(f"World '{args.name}' created with ID {saved_world.id}")
            CLIOutput.info(f"Version: {saved_world.version}")

            return 0

        except ValueError as e:
            CLIOutput.error(f"Validation error: {e}")
            return 1
        except DuplicateEntity:
            CLIOutput.error(f"World with name '{args.name}' already exists")
            return 1
        except Exception as e:
            CLIOutput.error(f"Failed to create world: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1

    def update(self, args: argparse.Namespace) -> int:
        """Update an existing world."""
        try:
            # Validate inputs
            if not args.world_id:
                CLIOutput.error("World ID is required")
                return 1

            world_id = EntityId(args.world_id)
            world = self.repo.find_by_id(TENANT_ID, world_id)

            if not world:
                CLIOutput.error(f"World with ID {args.world_id} not found")
                return 1

            # Update fields
            if args.name:
                world.rename(WorldName(args.name))
                CLIOutput.info(f"Name updated to '{args.name}'")

            if args.description:
                world.update_description(Description(args.description))
                CLIOutput.info("Description updated")

            # Save changes
            self.repo.save(world)

            CLIOutput.success(f"World updated (version: {world.version})")

            return 0

        except ValueError as e:
            CLIOutput.error(f"Validation error: {e}")
            return 1
        except Exception as e:
            CLIOutput.error(f"Failed to update world: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1

    def delete(self, args: argparse.Namespace) -> int:
        """Delete a world."""
        try:
            if not args.world_id:
                CLIOutput.error("World ID is required")
                return 1

            world_id = EntityId(args.world_id)

            # Confirm deletion
            if not args.force:
                world = self.repo.find_by_id(TENANT_ID, world_id)
                if not world:
                    CLIOutput.error(f"World with ID {args.world_id} not found")
                    return 1

                response = input(f"Delete world '{world.name}'? [y/N] ")
                if response.lower() != 'y':
                    CLIOutput.info("Deletion cancelled")
                    return 0

            # Delete
            if self.repo.delete(TENANT_ID, world_id):
                CLIOutput.success(f"World {args.world_id} deleted")
                return 0
            else:
                CLIOutput.error(f"World with ID {args.world_id} not found")
                return 1

        except Exception as e:
            CLIOutput.error(f"Failed to delete world: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1

    def show(self, args: argparse.Namespace) -> int:
        """Show world details."""
        try:
            if not args.world_id:
                CLIOutput.error("World ID is required")
                return 1

            world = self.repo.find_by_id(TENANT_ID, EntityId(args.world_id))

            if not world:
                CLIOutput.error(f"World with ID {args.world_id} not found")
                return 1

            CLIOutput.header("World Details")
            print(EntityFormatter.format_world_detail(world))

            return 0

        except Exception as e:
            CLIOutput.error(f"Failed to show world: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1


class CharacterCommands:
    """Commands for character management."""

    def __init__(self, repo: InMemoryCharacterRepository, world_repo: InMemoryWorldRepository):
        self.repo = repo
        self.world_repo = world_repo

    def list(self, args: argparse.Namespace) -> int:
        """List characters."""
        try:
            characters = []

            if args.world_id:
                # List characters in a specific world
                world = self.world_repo.find_by_id(TENANT_ID, EntityId(args.world_id))
                if not world:
                    CLIOutput.error(f"World with ID {args.world_id} not found")
                    return 1
                characters = self.repo.list_by_world(TENANT_ID, EntityId(args.world_id))
            else:
                # List all characters
                characters = self.repo.list_by_tenant(TENANT_ID)

            if not characters:
                CLIOutput.info("No characters found. Create one with 'character create'")
                return 0

            CLIOutput.header(f"Characters ({len(characters)})")
            for character in characters:
                print(f"  {EntityFormatter.format_character(character)}")

            return 0

        except Exception as e:
            CLIOutput.error(f"Failed to list characters: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1

    def create(self, args: argparse.Namespace) -> int:
        """Create a new character."""
        try:
            # Validate inputs
            if not args.world_id:
                CLIOutput.error("World ID is required")
                return 1

            if not args.name:
                CLIOutput.error("Character name is required")
                return 1

            if not args.backstory:
                CLIOutput.error("Character backstory is required (min 100 characters)")
                return 1

            # Verify world exists
            world = self.world_repo.find_by_id(TENANT_ID, EntityId(args.world_id))
            if not world:
                CLIOutput.error(f"World with ID {args.world_id} not found")
                return 1

            # Create character
            character = Character.create(
                tenant_id=TENANT_ID,
                world_id=EntityId(args.world_id),
                name=CharacterName(args.name),
                backstory=Backstory(args.backstory),
                status=CharacterStatus.ACTIVE,
            )

            # Save to repository
            saved_character = self.repo.save(character)

            CLIOutput.success(f"Character '{args.name}' created with ID {saved_character.id}")
            CLIOutput.info(f"World: {world.name} | Version: {saved_character.version}")

            return 0

        except ValueError as e:
            CLIOutput.error(f"Validation error: {e}")
            return 1
        except DuplicateEntity:
            CLIOutput.error(f"Character with name '{args.name}' already exists in this world")
            return 1
        except Exception as e:
            CLIOutput.error(f"Failed to create character: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1

    def update(self, args: argparse.Namespace) -> int:
        """Update an existing character."""
        try:
            if not args.character_id:
                CLIOutput.error("Character ID is required")
                return 1

            character_id = EntityId(args.character_id)
            character = self.repo.find_by_id(TENANT_ID, character_id)

            if not character:
                CLIOutput.error(f"Character with ID {args.character_id} not found")
                return 1

            # Update fields
            if args.name:
                character = character.__class__(
                    id=character.id,
                    tenant_id=character.tenant_id,
                    world_id=character.world_id,
                    name=CharacterName(args.name),
                    backstory=character.backstory,
                    status=character.status,
                    abilities=character.abilities,
                    parent_id=character.parent_id,
                    location_id=character.location_id,
                    rarity=character.rarity,
                    element=character.element,
                    role=character.role,
                    base_hp=character.base_hp,
                    base_atk=character.base_atk,
                    base_def=character.base_def,
                    base_speed=character.base_speed,
                    energy_cost=character.energy_cost,
                    created_at=character.created_at,
                    updated_at=character.updated_at,
                    version=character.version,
                )

            if args.backstory:
                character.update_backstory(Backstory(args.backstory))
                CLIOutput.info("Backstory updated")

            if args.status:
                if args.status.lower() == 'active':
                    character.activate()
                elif args.status.lower() == 'inactive':
                    character.deactivate()
                CLIOutput.info(f"Status updated to {args.status}")

            # Save changes
            self.repo.save(character)

            CLIOutput.success(f"Character updated (version: {character.version})")

            return 0

        except ValueError as e:
            CLIOutput.error(f"Validation error: {e}")
            return 1
        except Exception as e:
            CLIOutput.error(f"Failed to update character: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1

    def delete(self, args: argparse.Namespace) -> int:
        """Delete a character."""
        try:
            if not args.character_id:
                CLIOutput.error("Character ID is required")
                return 1

            character_id = EntityId(args.character_id)

            # Confirm deletion
            if not args.force:
                character = self.repo.find_by_id(TENANT_ID, character_id)
                if not character:
                    CLIOutput.error(f"Character with ID {args.character_id} not found")
                    return 1

                response = input(f"Delete character '{character.name}'? [y/N] ")
                if response.lower() != 'y':
                    CLIOutput.info("Deletion cancelled")
                    return 0

            # Delete
            if self.repo.delete(TENANT_ID, character_id):
                CLIOutput.success(f"Character {args.character_id} deleted")
                return 0
            else:
                CLIOutput.error(f"Character with ID {args.character_id} not found")
                return 1

        except Exception as e:
            CLIOutput.error(f"Failed to delete character: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1

    def show(self, args: argparse.Namespace) -> int:
        """Show character details."""
        try:
            if not args.character_id:
                CLIOutput.error("Character ID is required")
                return 1

            character = self.repo.find_by_id(TENANT_ID, EntityId(args.character_id))

            if not character:
                CLIOutput.error(f"Character with ID {args.character_id} not found")
                return 1

            world = self.world_repo.find_by_id(TENANT_ID, character.world_id)
            world_name = world.name if world else "Unknown"

            CLIOutput.header(f"Character Details - {world_name}")
            print(EntityFormatter.format_character_detail(character))

            return 0

        except Exception as e:
            CLIOutput.error(f"Failed to show character: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1


class EventCommands:
    """Commands for event management."""

    def __init__(self, repo: InMemoryEventRepository, world_repo: InMemoryWorldRepository):
        self.repo = repo
        self.world_repo = world_repo

    def list(self, args: argparse.Namespace) -> int:
        """List events."""
        try:
            if not args.world_id:
                CLIOutput.error("World ID is required")
                return 1

            world = self.world_repo.find_by_id(TENANT_ID, EntityId(args.world_id))
            if not world:
                CLIOutput.error(f"World with ID {args.world_id} not found")
                return 1

            events = self.repo.list_by_world(TENANT_ID, EntityId(args.world_id))

            if not events:
                CLIOutput.info(f"No events found in world '{world.name}'")
                return 0

            CLIOutput.header(f"Events in '{world.name}' ({len(events)})")
            for event in events:
                print(f"  {EntityFormatter.format_event(event)}")

            return 0

        except Exception as e:
            CLIOutput.error(f"Failed to list events: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1

    def create(self, args: argparse.Namespace) -> int:
        """Create a new event."""
        try:
            # Validate inputs
            if not args.world_id:
                CLIOutput.error("World ID is required")
                return 1

            if not args.name:
                CLIOutput.error("Event name is required")
                return 1

            if not args.description:
                CLIOutput.error("Event description is required")
                return 1

            if not args.participant_ids:
                CLIOutput.error("At least one participant character ID is required")
                return 1

            # Verify world exists
            world = self.world_repo.find_by_id(TENANT_ID, EntityId(args.world_id))
            if not world:
                CLIOutput.error(f"World with ID {args.world_id} not found")
                return 1

            # Parse participant IDs
            participant_ids = [EntityId(int(pid)) for pid in args.participant_ids.split(',')]

            # Create event
            event = Event.create(
                tenant_id=TENANT_ID,
                world_id=EntityId(args.world_id),
                name=args.name,
                description=Description(args.description),
                start_date=Timestamp.now(),
                participant_ids=participant_ids,
            )

            # Save to repository
            saved_event = self.repo.save(event)

            CLIOutput.success(f"Event '{args.name}' created with ID {saved_event.id}")
            CLIOutput.info(f"World: {world.name} | Participants: {len(participant_ids)}")

            return 0

        except ValueError as e:
            CLIOutput.error(f"Validation error: {e}")
            return 1
        except Exception as e:
            CLIOutput.error(f"Failed to create event: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1

    def show(self, args: argparse.Namespace) -> int:
        """Show event details."""
        try:
            if not args.event_id:
                CLIOutput.error("Event ID is required")
                return 1

            event = self.repo.find_by_id(TENANT_ID, EntityId(args.event_id))

            if not event:
                CLIOutput.error(f"Event with ID {args.event_id} not found")
                return 1

            world = self.world_repo.find_by_id(TENANT_ID, event.world_id)
            world_name = world.name if world else "Unknown"

            CLIOutput.header(f"Event Details - {world_name}")
            print(EntityFormatter.format_event_detail(event))

            return 0

        except Exception as e:
            CLIOutput.error(f"Failed to show event: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1


class StoryCommands:
    """Commands for story management."""

    def __init__(self, repo: InMemoryStoryRepository, world_repo: InMemoryWorldRepository):
        self.repo = repo
        self.world_repo = world_repo

    def list(self, args: argparse.Namespace) -> int:
        """List stories."""
        try:
            if not args.world_id:
                CLIOutput.error("World ID is required")
                return 1

            world = self.world_repo.find_by_id(TENANT_ID, EntityId(args.world_id))
            if not world:
                CLIOutput.error(f"World with ID {args.world_id} not found")
                return 1

            stories = self.repo.list_by_world(TENANT_ID, EntityId(args.world_id))

            if not stories:
                CLIOutput.info(f"No stories found in world '{world.name}'")
                return 0

            CLIOutput.header(f"Stories in '{world.name}' ({len(stories)})")
            for story in stories:
                print(f"  {EntityFormatter.format_story(story)}")

            return 0

        except Exception as e:
            CLIOutput.error(f"Failed to list stories: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1

    def create(self, args: argparse.Namespace) -> int:
        """Create a new story."""
        try:
            # Validate inputs
            if not args.world_id:
                CLIOutput.error("World ID is required")
                return 1

            if not args.name:
                CLIOutput.error("Story name is required")
                return 1

            if not args.content:
                CLIOutput.error("Story content is required")
                return 1

            # Verify world exists
            world = self.world_repo.find_by_id(TENANT_ID, EntityId(args.world_id))
            if not world:
                CLIOutput.error(f"World with ID {args.world_id} not found")
                return 1

            # Determine story type
            story_type = StoryType.LINEAR
            if args.type:
                type_map = {
                    'linear': StoryType.LINEAR,
                    'non_linear': StoryType.NON_LINEAR,
                    'interactive': StoryType.INTERACTIVE,
                }
                story_type = type_map.get(args.type.lower(), StoryType.LINEAR)

            # Create story
            story = Story.create(
                tenant_id=TENANT_ID,
                world_id=EntityId(args.world_id),
                name=StoryName(args.name),
                description=args.description or "",
                story_type=story_type,
                content=Content(args.content),
                is_active=not args.inactive,
            )

            # Save to repository
            saved_story = self.repo.save(story)

            CLIOutput.success(f"Story '{args.name}' created with ID {saved_story.id}")
            CLIOutput.info(f"World: {world.name} | Type: {story_type.value}")

            return 0

        except ValueError as e:
            CLIOutput.error(f"Validation error: {e}")
            return 1
        except Exception as e:
            CLIOutput.error(f"Failed to create story: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1

    def show(self, args: argparse.Namespace) -> int:
        """Show story details."""
        try:
            if not args.story_id:
                CLIOutput.error("Story ID is required")
                return 1

            story = self.repo.find_by_id(TENANT_ID, EntityId(args.story_id))

            if not story:
                CLIOutput.error(f"Story with ID {args.story_id} not found")
                return 1

            world = self.world_repo.find_by_id(TENANT_ID, story.world_id)
            world_name = world.name if world else "Unknown"

            CLIOutput.header(f"Story Details - {world_name}")
            print(EntityFormatter.format_story_detail(story))

            return 0

        except Exception as e:
            CLIOutput.error(f"Failed to show story: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1


class ImportExportCommands:
    """Commands for JSON import/export."""

    def __init__(
        self,
        world_repo: InMemoryWorldRepository,
        character_repo: InMemoryCharacterRepository,
        event_repo: InMemoryEventRepository,
        story_repo: InMemoryStoryRepository,
    ):
        self.world_repo = world_repo
        self.character_repo = character_repo
        self.event_repo = event_repo
        self.story_repo = story_repo

    def export(self, args: argparse.Namespace) -> int:
        """Export all data to JSON file."""
        try:
            output_path = Path(args.output)

            CLIOutput.info(f"Exporting data to {output_path}...")

            # Collect all data
            data = {
                "exported_at": datetime.now().isoformat(),
                "tenant_id": TENANT_ID.value,
                "worlds": [],
                "characters": [],
                "events": [],
                "stories": [],
            }

            # Export worlds
            worlds = self.world_repo.list_by_tenant(TENANT_ID)
            with ProgressIndicator("Exporting worlds", len(worlds)) as pbar:
                for world in worlds:
                    data["worlds"].append(self._serialize_world(world))
                    pbar.update()

            # Export characters
            characters = self.character_repo.list_by_tenant(TENANT_ID)
            with ProgressIndicator("Exporting characters", len(characters)) as pbar:
                for character in characters:
                    data["characters"].append(self._serialize_character(character))
                    pbar.update()

            # Export events
            for world in worlds:
                events = self.event_repo.list_by_world(TENANT_ID, world.id)
                with ProgressIndicator(f"Exporting events for world {world.id}", len(events)) as pbar:
                    for event in events:
                        data["events"].append(self._serialize_event(event))
                        pbar.update()

            # Export stories
            for world in worlds:
                stories = self.story_repo.list_by_world(TENANT_ID, world.id)
                with ProgressIndicator(f"Exporting stories for world {world.id}", len(stories)) as pbar:
                    for story in stories:
                        data["stories"].append(self._serialize_story(story))
                        pbar.update()

            # Write to file
            output_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

            CLIOutput.success(f"Exported {len(worlds)} worlds, {len(characters)} characters, {len(data['events'])} events, {len(data['stories'])} stories")
            CLIOutput.info(f"Output: {output_path.absolute()}")

            return 0

        except Exception as e:
            CLIOutput.error(f"Failed to export data: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1

    def import_data(self, args: argparse.Namespace) -> int:
        """Import data from JSON file."""
        try:
            input_path = Path(args.input)

            if not input_path.exists():
                CLIOutput.error(f"File not found: {input_path}")
                return 1

            CLIOutput.info(f"Importing data from {input_path}...")

            # Read JSON
            content = input_path.read_text(encoding='utf-8')
            data = json.loads(content)

            imported_count = {"worlds": 0, "characters": 0, "events": 0, "stories": 0}

            # Import worlds
            if "worlds" in data:
                with ProgressIndicator("Importing worlds", len(data["worlds"])) as pbar:
                    for world_data in data["worlds"]:
                        try:
                            world = self._deserialize_world(world_data)
                            self.world_repo.save(world)
                            imported_count["worlds"] += 1
                        except Exception as e:
                            CLIOutput.warning(f"Failed to import world: {e}")
                        pbar.update()

            # Import characters
            if "characters" in data:
                with ProgressIndicator("Importing characters", len(data["characters"])) as pbar:
                    for character_data in data["characters"]:
                        try:
                            character = self._deserialize_character(character_data)
                            self.character_repo.save(character)
                            imported_count["characters"] += 1
                        except Exception as e:
                            CLIOutput.warning(f"Failed to import character: {e}")
                        pbar.update()

            # Import events
            if "events" in data:
                with ProgressIndicator("Importing events", len(data["events"])) as pbar:
                    for event_data in data["events"]:
                        try:
                            event = self._deserialize_event(event_data)
                            self.event_repo.save(event)
                            imported_count["events"] += 1
                        except Exception as e:
                            CLIOutput.warning(f"Failed to import event: {e}")
                        pbar.update()

            # Import stories
            if "stories" in data:
                with ProgressIndicator("Importing stories", len(data["stories"])) as pbar:
                    for story_data in data["stories"]:
                        try:
                            story = self._deserialize_story(story_data)
                            self.story_repo.save(story)
                            imported_count["stories"] += 1
                        except Exception as e:
                            CLIOutput.warning(f"Failed to import story: {e}")
                        pbar.update()

            CLIOutput.success(
                f"Imported {imported_count['worlds']} worlds, "
                f"{imported_count['characters']} characters, "
                f"{imported_count['events']} events, "
                f"{imported_count['stories']} stories"
            )

            return 0

        except json.JSONDecodeError as e:
            CLIOutput.error(f"Invalid JSON file: {e}")
            return 1
        except Exception as e:
            CLIOutput.error(f"Failed to import data: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1

    def _serialize_world(self, world: World) -> Dict[str, Any]:
        """Serialize world to dict."""
        return {
            "id": world.id.value if world.id else None,
            "name": world.name.value,
            "description": world.description.value,
            "parent_id": world.parent_id.value if world.parent_id else None,
            "created_at": world.created_at.value.isoformat(),
            "updated_at": world.updated_at.value.isoformat(),
            "version": world.version.value,
        }

    def _deserialize_world(self, data: Dict[str, Any]) -> World:
        """Deserialize dict to world."""
        return World(
            id=EntityId(data["id"]) if data.get("id") else None,
            tenant_id=TENANT_ID,
            name=WorldName(data["name"]),
            description=Description(data["description"]),
            parent_id=EntityId(data["parent_id"]) if data.get("parent_id") else None,
            created_at=Timestamp(datetime.fromisoformat(data["created_at"])),
            updated_at=Timestamp(datetime.fromisoformat(data["updated_at"])),
            version=Version(data["version"]),
        )

    def _serialize_character(self, character: Character) -> Dict[str, Any]:
        """Serialize character to dict."""
        return {
            "id": character.id.value if character.id else None,
            "world_id": character.world_id.value,
            "name": character.name.value,
            "backstory": character.backstory.value,
            "status": character.status.value,
            "parent_id": character.parent_id.value if character.parent_id else None,
            "location_id": character.location_id.value if character.location_id else None,
            "rarity": character.rarity.value if character.rarity else None,
            "element": character.element.value if character.element else None,
            "role": character.role.value if character.role else None,
            "base_hp": character.base_hp,
            "base_atk": character.base_atk,
            "base_def": character.base_def,
            "base_speed": character.base_speed,
            "energy_cost": character.energy_cost,
            "abilities": [
                {
                    "name": ability.name.value,
                    "description": ability.description.value,
                    "power_level": ability.power_level.value,
                }
                for ability in character.abilities
            ],
            "created_at": character.created_at.value.isoformat(),
            "updated_at": character.updated_at.value.isoformat(),
            "version": character.version.value,
        }

    def _deserialize_character(self, data: Dict[str, Any]) -> Character:
        """Deserialize dict to character."""
        from src.domain.value_objects.ability import Ability

        abilities = []
        for ability_data in data.get("abilities", []):
            abilities.append(Ability(
                name=ability_data["name"],
                description=ability_data["description"],
                power_level=ability_data["power_level"],
            ))

        return Character(
            id=EntityId(data["id"]) if data.get("id") else None,
            tenant_id=TENANT_ID,
            world_id=EntityId(data["world_id"]),
            name=CharacterName(data["name"]),
            backstory=Backstory(data["backstory"]),
            status=CharacterStatus(data["status"]),
            abilities=abilities,
            parent_id=EntityId(data["parent_id"]) if data.get("parent_id") else None,
            location_id=EntityId(data["location_id"]) if data.get("location_id") else None,
            rarity=data.get("rarity"),
            element=data.get("element"),
            role=data.get("role"),
            base_hp=data.get("base_hp"),
            base_atk=data.get("base_atk"),
            base_def=data.get("base_def"),
            base_speed=data.get("base_speed"),
            energy_cost=data.get("energy_cost"),
            created_at=Timestamp(datetime.fromisoformat(data["created_at"])),
            updated_at=Timestamp(datetime.fromisoformat(data["updated_at"])),
            version=Version(data["version"]),
        )

    def _serialize_event(self, event: Event) -> Dict[str, Any]:
        """Serialize event to dict."""
        return {
            "id": event.id.value if event.id else None,
            "world_id": event.world_id.value,
            "name": event.name,
            "description": event.description.value,
            "start_date": event.date_range.start_date.value.isoformat(),
            "end_date": event.date_range.end_date.value.isoformat() if event.date_range.end_date else None,
            "outcome": event.outcome.value,
            "participant_ids": [pid.value for pid in event.participant_ids],
            "location_id": event.location_id.value if event.location_id else None,
            "created_at": event.created_at.value.isoformat(),
            "updated_at": event.updated_at.value.isoformat(),
            "version": event.version.value,
        }

    def _deserialize_event(self, data: Dict[str, Any]) -> Event:
        """Deserialize dict to event."""
        from src.domain.value_objects.common import DateRange

        participant_ids = [EntityId(pid) for pid in data["participant_ids"]]
        start_date = Timestamp(datetime.fromisoformat(data["start_date"]))
        end_date = Timestamp(datetime.fromisoformat(data["end_date"])) if data.get("end_date") else None

        return Event(
            id=EntityId(data["id"]) if data.get("id") else None,
            tenant_id=TENANT_ID,
            world_id=EntityId(data["world_id"]),
            name=data["name"],
            description=Description(data["description"]),
            date_range=DateRange(start_date, end_date),
            outcome=EventOutcome(data["outcome"]),
            participant_ids=participant_ids,
            location_id=EntityId(data["location_id"]) if data.get("location_id") else None,
            created_at=Timestamp(datetime.fromisoformat(data["created_at"])),
            updated_at=Timestamp(datetime.fromisoformat(data["updated_at"])),
            version=Version(data["version"]),
        )

    def _serialize_story(self, story: Story) -> Dict[str, Any]:
        """Serialize story to dict."""
        return {
            "id": story.id.value if story.id else None,
            "world_id": story.world_id.value,
            "name": story.name.value,
            "description": story.description,
            "story_type": story.story_type.value,
            "content": story.content.value,
            "choice_ids": [cid.value for cid in story.choice_ids],
            "connected_world_ids": [wid.value for wid in story.connected_world_ids],
            "is_active": story.is_active,
            "created_at": story.created_at.value.isoformat(),
            "updated_at": story.updated_at.value.isoformat(),
            "version": story.version.value,
        }

    def _deserialize_story(self, data: Dict[str, Any]) -> Story:
        """Deserialize dict to story."""
        choice_ids = [EntityId(cid) for cid in data.get("choice_ids", [])]
        connected_ids = [EntityId(wid) for wid in data.get("connected_world_ids", [])]

        return Story(
            id=EntityId(data["id"]) if data.get("id") else None,
            tenant_id=TENANT_ID,
            world_id=EntityId(data["world_id"]),
            name=StoryName(data["name"]),
            description=data["description"],
            story_type=StoryType(data["story_type"]),
            content=Content(data["content"]),
            choice_ids=choice_ids,
            connected_world_ids=connected_ids,
            is_active=data.get("is_active", True),
            created_at=Timestamp(datetime.fromisoformat(data["created_at"])),
            updated_at=Timestamp(datetime.fromisoformat(data["updated_at"])),
            version=Version(data["version"]),
        )


class StatsCommands:
    """Commands for statistics."""

    def __init__(
        self,
        world_repo: InMemoryWorldRepository,
        character_repo: InMemoryCharacterRepository,
        event_repo: InMemoryEventRepository,
        story_repo: InMemoryStoryRepository,
    ):
        self.world_repo = world_repo
        self.character_repo = character_repo
        self.event_repo = event_repo
        self.story_repo = story_repo

    def show(self, args: argparse.Namespace) -> int:
        """Display system statistics."""
        try:
            CLIOutput.header("📊 LoreSystem Statistics")

            # World stats
            worlds = self.world_repo.list_by_tenant(TENANT_ID)
            print(f"\n{Fore.CYAN if COLORS_AVAILABLE else ''}Worlds:{Style.RESET_ALL} {len(worlds)}")

            for world in worlds:
                print(f"  • {world.name}")
                characters = self.character_repo.list_by_world(TENANT_ID, world.id)
                events = self.event_repo.list_by_world(TENANT_ID, world.id)
                stories = self.story_repo.list_by_world(TENANT_ID, world.id)
                print(f"    Characters: {len(characters)} | Events: {len(events)} | Stories: {len(stories)}")

            # Overall stats
            all_characters = self.character_repo.list_by_tenant(TENANT_ID)
            all_events = []
            all_stories = []
            for world in worlds:
                all_events.extend(self.event_repo.list_by_world(TENANT_ID, world.id))
                all_stories.extend(self.story_repo.list_by_world(TENANT_ID, world.id))

            print(f"\n{Fore.CYAN if COLORS_AVAILABLE else ''}Total Characters:{Style.RESET_ALL} {len(all_characters)}")
            active_chars = sum(1 for c in all_characters if c.status == CharacterStatus.ACTIVE)
            print(f"  Active: {active_chars} | Inactive: {len(all_characters) - active_chars}")

            print(f"\n{Fore.CYAN if COLORS_AVAILABLE else ''}Total Events:{Style.RESET_ALL} {len(all_events)}")
            ongoing = sum(1 for e in all_events if e.is_ongoing())
            completed = len(all_events) - ongoing
            print(f"  Ongoing: {ongoing} | Completed: {completed}")

            print(f"\n{Fore.CYAN if COLORS_AVAILABLE else ''}Total Stories:{Style.RESET_ALL} {len(all_stories)}")
            active = sum(1 for s in all_stories if s.is_active)
            print(f"  Active: {active} | Inactive: {len(all_stories) - active}")

            return 0

        except Exception as e:
            CLIOutput.error(f"Failed to show statistics: {e}")
            if args.verbose:
                traceback.print_exc()
            return 1


# ============================================================================
# Argument Parser Setup
# ============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog='lore-cli',
        description='LoreSystem CLI - Manage game lore from the command line',
        epilog="""
Examples:
  %(prog)s world list
  %(prog)s world create --name "My World" --description "A fantasy world"
  %(prog)s character create --world-id 1 --name "Hero" --backstory "Once upon a time..."
  %(prog)s export --output lore_data.json
  %(prog)s import --input lore_data.json
  %(prog)s stats
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global options
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output with error traces',
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # World commands
    world_parser = subparsers.add_parser('world', help='Manage worlds')
    world_subparsers = world_parser.add_subparsers(dest='world_command', help='World operations')

    # world list
    world_list_parser = world_subparsers.add_parser('list', help='List all worlds')
    world_list_parser.set_defaults(func=WorldCommands.list)

    # world create
    world_create_parser = world_subparsers.add_parser('create', help='Create a new world')
    world_create_parser.add_argument('--name', required=True, help='World name')
    world_create_parser.add_argument('--description', required=True, help='World description')
    world_create_parser.set_defaults(func=WorldCommands.create)

    # world update
    world_update_parser = world_subparsers.add_parser('update', help='Update a world')
    world_update_parser.add_argument('--world-id', type=int, required=True, help='World ID')
    world_update_parser.add_argument('--name', help='New world name')
    world_update_parser.add_argument('--description', help='New world description')
    world_update_parser.set_defaults(func=WorldCommands.update)

    # world delete
    world_delete_parser = world_subparsers.add_parser('delete', help='Delete a world')
    world_delete_parser.add_argument('--world-id', type=int, required=True, help='World ID')
    world_delete_parser.add_argument('-f', '--force', action='store_true', help='Skip confirmation')
    world_delete_parser.set_defaults(func=WorldCommands.delete)

    # world show
    world_show_parser = world_subparsers.add_parser('show', help='Show world details')
    world_show_parser.add_argument('--world-id', type=int, required=True, help='World ID')
    world_show_parser.set_defaults(func=WorldCommands.show)

    # Character commands
    character_parser = subparsers.add_parser('character', help='Manage characters')
    character_subparsers = character_parser.add_subparsers(dest='character_command', help='Character operations')

    # character list
    character_list_parser = character_subparsers.add_parser('list', help='List characters')
    character_list_parser.add_argument('--world-id', type=int, help='Filter by world ID')
    character_list_parser.set_defaults(func=CharacterCommands.list)

    # character create
    character_create_parser = character_subparsers.add_parser('create', help='Create a new character')
    character_create_parser.add_argument('--world-id', type=int, required=True, help='World ID')
    character_create_parser.add_argument('--name', required=True, help='Character name')
    character_create_parser.add_argument('--backstory', required=True, help='Character backstory (min 100 chars)')
    character_create_parser.set_defaults(func=CharacterCommands.create)

    # character update
    character_update_parser = character_subparsers.add_parser('update', help='Update a character')
    character_update_parser.add_argument('--character-id', type=int, required=True, help='Character ID')
    character_update_parser.add_argument('--name', help='New character name')
    character_update_parser.add_argument('--backstory', help='New character backstory')
    character_update_parser.add_argument('--status', choices=['active', 'inactive'], help='Character status')
    character_update_parser.set_defaults(func=CharacterCommands.update)

    # character delete
    character_delete_parser = character_subparsers.add_parser('delete', help='Delete a character')
    character_delete_parser.add_argument('--character-id', type=int, required=True, help='Character ID')
    character_delete_parser.add_argument('-f', '--force', action='store_true', help='Skip confirmation')
    character_delete_parser.set_defaults(func=CharacterCommands.delete)

    # character show
    character_show_parser = character_subparsers.add_parser('show', help='Show character details')
    character_show_parser.add_argument('--character-id', type=int, required=True, help='Character ID')
    character_show_parser.set_defaults(func=CharacterCommands.show)

    # Event commands
    event_parser = subparsers.add_parser('event', help='Manage events')
    event_subparsers = event_parser.add_subparsers(dest='event_command', help='Event operations')

    # event list
    event_list_parser = event_subparsers.add_parser('list', help='List events')
    event_list_parser.add_argument('--world-id', type=int, required=True, help='World ID')
    event_list_parser.set_defaults(func=EventCommands.list)

    # event create
    event_create_parser = event_subparsers.add_parser('create', help='Create a new event')
    event_create_parser.add_argument('--world-id', type=int, required=True, help='World ID')
    event_create_parser.add_argument('--name', required=True, help='Event name')
    event_create_parser.add_argument('--description', required=True, help='Event description')
    event_create_parser.add_argument('--participant-ids', required=True, help='Comma-separated character IDs')
    event_create_parser.set_defaults(func=EventCommands.create)

    # event show
    event_show_parser = event_subparsers.add_parser('show', help='Show event details')
    event_show_parser.add_argument('--event-id', type=int, required=True, help='Event ID')
    event_show_parser.set_defaults(func=EventCommands.show)

    # Story commands
    story_parser = subparsers.add_parser('story', help='Manage stories')
    story_subparsers = story_parser.add_subparsers(dest='story_command', help='Story operations')

    # story list
    story_list_parser = story_subparsers.add_parser('list', help='List stories')
    story_list_parser.add_argument('--world-id', type=int, required=True, help='World ID')
    story_list_parser.set_defaults(func=StoryCommands.list)

    # story create
    story_create_parser = story_subparsers.add_parser('create', help='Create a new story')
    story_create_parser.add_argument('--world-id', type=int, required=True, help='World ID')
    story_create_parser.add_argument('--name', required=True, help='Story name')
    story_create_parser.add_argument('--description', help='Story description')
    story_create_parser.add_argument('--content', required=True, help='Story content')
    story_create_parser.add_argument('--type', choices=['linear', 'non_linear', 'interactive'], help='Story type')
    story_create_parser.add_argument('--inactive', action='store_true', help='Create as inactive')
    story_create_parser.set_defaults(func=StoryCommands.create)

    # story show
    story_show_parser = story_subparsers.add_parser('show', help='Show story details')
    story_show_parser.add_argument('--story-id', type=int, required=True, help='Story ID')
    story_show_parser.set_defaults(func=StoryCommands.show)

    # Export command
    export_parser = subparsers.add_parser('export', help='Export data to JSON')
    export_parser.add_argument('--output', '-o', default='lore_export.json', help='Output file path (default: lore_export.json)')
    export_parser.set_defaults(func=ImportExportCommands.export)

    # Import command
    import_parser = subparsers.add_parser('import', help='Import data from JSON')
    import_parser.add_argument('--input', '-i', required=True, help='Input file path')
    import_parser.set_defaults(func=ImportExportCommands.import_data)

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show system statistics')
    stats_parser.set_defaults(func=StatsCommands.show)

    return parser


# ============================================================================
# Main Entry Point
# ============================================================================

def main(args: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    # Initialize repositories
    world_repo = InMemoryWorldRepository()
    character_repo = InMemoryCharacterRepository()
    event_repo = InMemoryEventRepository()
    story_repo = InMemoryStoryRepository()

    # Initialize command handlers
    world_commands = WorldCommands(world_repo)
    character_commands = CharacterCommands(character_repo, world_repo)
    event_commands = EventCommands(event_repo, world_repo)
    story_commands = StoryCommands(story_repo, world_repo)
    import_export_commands = ImportExportCommands(world_repo, character_repo, event_repo, story_repo)
    stats_commands = StatsCommands(world_repo, character_repo, event_repo, story_repo)

    # Parse arguments
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # If no command, show help
    if not parsed_args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    try:
        if parsed_args.command == 'world':
            if parsed_args.world_command == 'list':
                return world_commands.list(parsed_args)
            elif parsed_args.world_command == 'create':
                return world_commands.create(parsed_args)
            elif parsed_args.world_command == 'update':
                return world_commands.update(parsed_args)
            elif parsed_args.world_command == 'delete':
                return world_commands.delete(parsed_args)
            elif parsed_args.world_command == 'show':
                return world_commands.show(parsed_args)

        elif parsed_args.command == 'character':
            if parsed_args.character_command == 'list':
                return character_commands.list(parsed_args)
            elif parsed_args.character_command == 'create':
                return character_commands.create(parsed_args)
            elif parsed_args.character_command == 'update':
                return character_commands.update(parsed_args)
            elif parsed_args.character_command == 'delete':
                return character_commands.delete(parsed_args)
            elif parsed_args.character_command == 'show':
                return character_commands.show(parsed_args)

        elif parsed_args.command == 'event':
            if parsed_args.event_command == 'list':
                return event_commands.list(parsed_args)
            elif parsed_args.event_command == 'create':
                return event_commands.create(parsed_args)
            elif parsed_args.event_command == 'show':
                return event_commands.show(parsed_args)

        elif parsed_args.command == 'story':
            if parsed_args.story_command == 'list':
                return story_commands.list(parsed_args)
            elif parsed_args.story_command == 'create':
                return story_commands.create(parsed_args)
            elif parsed_args.story_command == 'show':
                return story_commands.show(parsed_args)

        elif parsed_args.command == 'export':
            return import_export_commands.export(parsed_args)

        elif parsed_args.command == 'import':
            return import_export_commands.import_data(parsed_args)

        elif parsed_args.command == 'stats':
            return stats_commands.show(parsed_args)

        CLIOutput.error(f"Unknown command or subcommand")
        parser.print_help()
        return 1

    except AttributeError as e:
        if parsed_args.verbose:
            traceback.print_exc()
        CLIOutput.error(f"Invalid command structure")
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
