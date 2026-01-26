#!/usr/bin/env python3
"""
JSON Persistence Layer for Lore System MCP Server

Provides save/load functionality for all lore entities to/from JSON files.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

# Import domain value objects for proper serialization
from src.domain.value_objects.common import Timestamp, DateRange


class JSONPersistence:
    """Handles JSON serialization and persistence of lore entities."""

    def __init__(self, data_dir: str = "lore_data"):
        """
        Initialize JSON persistence.

        Args:
            data_dir: Directory to store JSON files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Create subdirectories for each entity type
        self.worlds_dir = self.data_dir / "worlds"
        self.characters_dir = self.data_dir / "characters"
        self.stories_dir = self.data_dir / "stories"
        self.events_dir = self.data_dir / "events"
        self.pages_dir = self.data_dir / "pages"
        self.items_dir = self.data_dir / "items"
        self.locations_dir = self.data_dir / "locations"
        self.environments_dir = self.data_dir / "environments"

        for dir_path in [self.worlds_dir, self.characters_dir, self.stories_dir,
                         self.events_dir, self.pages_dir, self.items_dir, self.locations_dir,
                         self.environments_dir]:
            dir_path.mkdir(exist_ok=True)

    def _serialize_entity(self, entity: Any) -> dict:
        """
        Serialize a domain entity to JSON-compatible dict.

        Args:
            entity: Domain entity to serialize

        Returns:
            Dictionary representation
        """
        if entity is None:
            return None

        result = {}
        for field_name, field_value in entity.__dict__.items():
            if field_value is None:
                result[field_name] = None
            elif isinstance(field_value, DateRange):
                # Special handling for DateRange
                result[field_name] = {
                    'start_date': field_value.start_date.value.isoformat(),
                    'end_date': field_value.end_date.value.isoformat() if field_value.end_date else None
                }
            elif isinstance(field_value, Timestamp):
                # Special handling for Timestamp
                result[field_name] = field_value.value.isoformat()
            elif hasattr(field_value, 'value'):
                # Value object - need to serialize the inner value
                inner_value = field_value.value
                if isinstance(inner_value, datetime):
                    result[field_name] = inner_value.isoformat()
                elif isinstance(inner_value, (str, int, float, bool)):
                    result[field_name] = inner_value
                else:
                    result[field_name] = str(inner_value)
            elif isinstance(field_value, (str, int, float, bool)):
                result[field_name] = field_value
            elif isinstance(field_value, datetime):
                result[field_name] = field_value.isoformat()
            elif isinstance(field_value, list):
                result[field_name] = [
                    self._serialize_entity(item) if hasattr(item, '__dict__')
                    else item.value if hasattr(item, 'value')
                    else str(item)
                    for item in field_value
                ]
            else:
                result[field_name] = str(field_value)

        return result

    def save_world(self, world: Any, tenant_id: str) -> str:
        """Save a world to JSON file."""
        world_data = self._serialize_entity(world)
        filename = f"{tenant_id}_world_{world_data['id']}.json"
        filepath = self.worlds_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(world_data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def save_character(self, character: Any, tenant_id: str) -> str:
        """Save a character to JSON file."""
        char_data = self._serialize_entity(character)
        filename = f"{tenant_id}_char_{char_data['id']}.json"
        filepath = self.characters_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(char_data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def save_story(self, story: Any, tenant_id: str) -> str:
        """Save a story to JSON file."""
        story_data = self._serialize_entity(story)
        filename = f"{tenant_id}_story_{story_data['id']}.json"
        filepath = self.stories_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(story_data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def save_event(self, event: Any, tenant_id: str) -> str:
        """Save an event to JSON file."""
        event_data = self._serialize_entity(event)
        filename = f"{tenant_id}_event_{event_data['id']}.json"
        filepath = self.events_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(event_data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def save_page(self, page: Any, tenant_id: str) -> str:
        """Save a page to JSON file."""
        page_data = self._serialize_entity(page)
        filename = f"{tenant_id}_page_{page_data['id']}.json"
        filepath = self.pages_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def save_item(self, item: Any, tenant_id: str) -> str:
        """Save an item to JSON file."""
        item_data = self._serialize_entity(item)
        filename = f"{tenant_id}_item_{item_data['id']}.json"
        filepath = self.items_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(item_data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def delete_item(self, tenant_id: str, item_id: str) -> bool:
        """Delete an item JSON file."""
        filename = f"{tenant_id}_item_{item_id}.json"
        filepath = self.items_dir / filename

        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def save_location(self, location: Any, tenant_id: str) -> str:
        """Save a location to JSON file."""
        location_data = self._serialize_entity(location)
        filename = f"{tenant_id}_location_{location_data['id']}.json"
        filepath = self.locations_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(location_data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def delete_location(self, tenant_id: str, location_id: str) -> bool:
        """Delete a location JSON file."""
        filename = f"{tenant_id}_location_{location_id}.json"
        filepath = self.locations_dir / filename

        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def save_environment(self, environment: Any, tenant_id: str) -> str:
        """Save an environment to JSON file."""
        environment_data = self._serialize_entity(environment)
        filename = f"{tenant_id}_environment_{environment_data['id']}.json"
        filepath = self.environments_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(environment_data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def delete_environment(self, tenant_id: str, environment_id: str) -> bool:
        """Delete an environment JSON file."""
        filename = f"{tenant_id}_environment_{environment_id}.json"
        filepath = self.environments_dir / filename

        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def save_all(self, world_repo, character_repo, story_repo, event_repo, page_repo, item_repo, location_repo,
                 environment_repo, tenant_id: str) -> Dict[str, int]:
        """
        Save all entities from repositories to JSON files.

        Args:
            world_repo: World repository
            character_repo: Character repository
            story_repo: Story repository
            event_repo: Event repository
            page_repo: Page repository
            item_repo: Item repository
            location_repo: Location repository
            environment_repo: Environment repository
            tenant_id: Tenant ID to save data for

        Returns:
            Dictionary with counts of saved entities
        """
        from src.domain.value_objects.common import TenantId

        tid = TenantId(int(tenant_id) if tenant_id.isdigit() else abs(hash(tenant_id)) % (10**9))

        counts = {
            "worlds": 0,
            "characters": 0,
            "stories": 0,
            "events": 0,
            "pages": 0,
            "items": 0,
            "locations": 0,
            "environments": 0,
            "files": []
        }

        # Save worlds
        worlds = world_repo.list_by_tenant(tid, limit=10000)
        for world in worlds:
            filepath = self.save_world(world, tenant_id)
            counts["worlds"] += 1
            counts["files"].append(filepath)

        # Save characters
        characters = character_repo.list_by_tenant(tid, limit=10000)
        for character in characters:
            filepath = self.save_character(character, tenant_id)
            counts["characters"] += 1
            counts["files"].append(filepath)

        # Save stories (need to iterate through worlds)
        for world in worlds:
            stories = story_repo.list_by_world(tid, world.id, limit=10000)
            for story in stories:
                filepath = self.save_story(story, tenant_id)
                counts["stories"] += 1
                counts["files"].append(filepath)

        # Save events
        for world in worlds:
            events = event_repo.list_by_world(tid, world.id, limit=10000)
            for event in events:
                filepath = self.save_event(event, tenant_id)
                counts["events"] += 1
                counts["files"].append(filepath)

        # Save pages
        for world in worlds:
            pages = page_repo.list_by_world(tid, world.id, limit=10000)
            for page in pages:
                filepath = self.save_page(page, tenant_id)
                counts["pages"] += 1
                counts["files"].append(filepath)

        # Save items
        for world in worlds:
            items = item_repo.list_by_world(tid, world.id, limit=10000)
            for item in items:
                filepath = self.save_item(item, tenant_id)
                counts["items"] += 1
                counts["files"].append(filepath)

        # Save locations
        for world in worlds:
            locations = location_repo.list_by_world(tid, world.id, limit=10000)
            for location in locations:
                filepath = self.save_location(location, tenant_id)
                counts["locations"] += 1
                counts["files"].append(filepath)

        # Save environments
        for world in worlds:
            environments = environment_repo.list_by_world(tid, world.id, limit=10000)
            for environment in environments:
                filepath = self.save_environment(environment, tenant_id)
                counts["environments"] += 1
                counts["files"].append(filepath)

        return counts

    def load_world(self, filepath: str) -> dict:
        """Load a world from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_character(self, filepath: str) -> dict:
        """Load a character from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_story(self, filepath: str) -> dict:
        """Load a story from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_event(self, filepath: str) -> dict:
        """Load an event from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_page(self, filepath: str) -> dict:
        """Load a page from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_environment(self, filepath: str) -> dict:
        """Load an environment from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_all(self, tenant_id: str) -> Dict[str, List[dict]]:
        """
        Load all entities for a tenant from JSON files.

        Args:
            tenant_id: Tenant ID to load data for

        Returns:
            Dictionary with lists of entity data
        """
        data = {
            "worlds": [],
            "characters": [],
            "stories": [],
            "events": [],
            "pages": [],
            "environments": []
        }

        # Load worlds
        for filepath in self.worlds_dir.glob(f"{tenant_id}_world_*.json"):
            data["worlds"].append(self.load_world(filepath))

        # Load characters
        for filepath in self.characters_dir.glob(f"{tenant_id}_char_*.json"):
            data["characters"].append(self.load_character(filepath))

        # Load stories
        for filepath in self.stories_dir.glob(f"{tenant_id}_story_*.json"):
            data["stories"].append(self.load_story(filepath))

        # Load events
        for filepath in self.events_dir.glob(f"{tenant_id}_event_*.json"):
            data["events"].append(self.load_event(filepath))

        # Load pages
        for filepath in self.pages_dir.glob(f"{tenant_id}_page_*.json"):
            data["pages"].append(self.load_page(filepath))

        # Load environments
        for filepath in self.environments_dir.glob(f"{tenant_id}_environment_*.json"):
            data["environments"].append(self.load_environment(filepath))

        return data

    def export_tenant(self, tenant_id: str, output_file: str) -> str:
        """
        Export all data for a tenant to a single JSON file.

        Args:
            tenant_id: Tenant ID to export
            output_file: Output filename

        Returns:
            Path to exported file
        """
        data = self.load_all(tenant_id)

        export_data = {
            "metadata": {
                "tenant_id": tenant_id,
                "exported_at": datetime.now().isoformat(),
                "version": "1.0.0"
            },
            "data": data,
            "counts": {
                "worlds": len(data["worlds"]),
                "characters": len(data["characters"]),
                "stories": len(data["stories"]),
                "events": len(data["events"]),
                "pages": len(data["pages"])
            }
        }

        filepath = self.data_dir / output_file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def list_saved_files(self, tenant_id: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List all saved JSON files.

        Args:
            tenant_id: Optional tenant ID to filter by

        Returns:
            Dictionary with lists of file paths
        """
        pattern = f"{tenant_id}_*" if tenant_id else "*"

        return {
            "worlds": [str(f) for f in self.worlds_dir.glob(f"{pattern}.json")],
            "characters": [str(f) for f in self.characters_dir.glob(f"{pattern}.json")],
            "stories": [str(f) for f in self.stories_dir.glob(f"{pattern}.json")],
            "events": [str(f) for f in self.events_dir.glob(f"{pattern}.json")],
            "pages": [str(f) for f in self.pages_dir.glob(f"{pattern}.json")]
        }

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get statistics about stored data."""
        stats = {
            "total_files": 0,
            "by_type": {},
            "total_size_bytes": 0,
            "data_directory": str(self.data_dir.absolute())
        }

        for entity_type, directory in [
            ("worlds", self.worlds_dir),
            ("characters", self.characters_dir),
            ("stories", self.stories_dir),
            ("events", self.events_dir),
            ("pages", self.pages_dir),
            ("items", self.items_dir),
            ("locations", self.locations_dir)
        ]:
            files = list(directory.glob("*.json"))
            file_count = len(files)
            total_size = sum(f.stat().st_size for f in files)

            stats["by_type"][entity_type] = {
                "count": file_count,
                "size_bytes": total_size
            }
            stats["total_files"] += file_count
            stats["total_size_bytes"] += total_size

        return stats
