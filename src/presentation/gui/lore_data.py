"""
LoreData - In-memory storage for lore entities.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.domain.entities.world import World
from src.domain.entities.character import Character
from src.domain.entities.event import Event
from src.domain.entities.improvement import Improvement
from src.domain.entities.item import Item
from src.domain.entities.quest import Quest
from src.domain.entities.storyline import Storyline
from src.domain.entities.page import Page
from src.domain.entities.template import Template
from src.domain.entities.story import Story
from src.domain.entities.tag import Tag
from src.domain.entities.image import Image
from src.domain.value_objects.common import (
    TenantId, EntityId, WorldName, Description, CharacterName,
    Backstory, Timestamp, EntityType, EventOutcome, CharacterStatus,
    ItemType, Rarity, QuestStatus, StorylineType,
    PageName, Content, TemplateName, TemplateType, StoryName, StoryType,
    TagName, TagType, ImagePath, ImageType
)
from src.domain.value_objects.ability import Ability


class LoreData:
    """In-memory storage for lore entities."""
    
    def __init__(self):
        self.worlds: List[World] = []
        self.characters: List[Character] = []
        self.events: List[Event] = []
        self.improvements: List[Improvement] = []
        self.items: List[Item] = []
        self.quests: List[Quest] = []
        self.storylines: List[Storyline] = []
        self.pages: List[Page] = []
        self.templates: List[Template] = []
        self.stories: List[Story] = []
        self.tags: List[Tag] = []
        self.images: List[Image] = []
        self.tenant_id = TenantId(1)
        self._next_id = 1
    
    def get_next_id(self) -> EntityId:
        """Generate next entity ID."""
        entity_id = EntityId(self._next_id)
        self._next_id += 1
        return entity_id
    
    def add_world(self, world: World) -> World:
        """Add world with generated ID."""
        if world.id is None:
            object.__setattr__(world, 'id', self.get_next_id())
        self.worlds.append(world)
        return world
    
    def add_character(self, character: Character) -> Character:
        """Add character with generated ID."""
        if character.id is None:
            object.__setattr__(character, 'id', self.get_next_id())
        self.characters.append(character)
        return character
    
    def add_event(self, event: Event) -> Event:
        """Add event with generated ID."""
        if event.id is None:
            object.__setattr__(event, 'id', self.get_next_id())
        self.events.append(event)
        return event
    
    def add_improvement(self, improvement: Improvement) -> Improvement:
        """Add improvement with generated ID."""
        if improvement.id is None:
            object.__setattr__(improvement, 'id', self.get_next_id())
        self.improvements.append(improvement)
        return improvement
    
    def add_item(self, item: Item) -> Item:
        """Add item with generated ID."""
        if item.id is None:
            object.__setattr__(item, 'id', self.get_next_id())
        self.items.append(item)
        return item
    
    def add_quest(self, quest: Quest) -> Quest:
        """Add quest with generated ID."""
        if quest.id is None:
            object.__setattr__(quest, 'id', self.get_next_id())
        self.quests.append(quest)
        return quest
    
    def add_storyline(self, storyline: Storyline) -> Storyline:
        """Add storyline with generated ID."""
        if storyline.id is None:
            object.__setattr__(storyline, 'id', self.get_next_id())
        self.storylines.append(storyline)
        return storyline
    
    def add_template(self, template: Template) -> Template:
        """Add template with generated ID."""
        if template.id is None:
            object.__setattr__(template, 'id', self.get_next_id())
        self.templates.append(template)
        return template
    
    def get_world_by_id(self, world_id: EntityId) -> Optional[World]:
        """Find world by ID."""
        return next((w for w in self.worlds if w.id == world_id), None)
    
    def get_characters_by_world(self, world_id: EntityId) -> List[Character]:
        """Get all characters in a world."""
        return [c for c in self.characters if c.world_id == world_id]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON."""
        return {
            'worlds': [self._world_to_dict(w) for w in self.worlds],
            'characters': [self._character_to_dict(c) for c in self.characters],
            'events': [self._event_to_dict(e) for e in self.events],
            'improvements': [self._improvement_to_dict(i) for i in self.improvements],
            'items': [self._item_to_dict(i) for i in self.items],
            'quests': [self._quest_to_dict(q) for q in self.quests],
            'storylines': [self._storyline_to_dict(s) for s in self.storylines],
            'templates': [self._template_to_dict(t) for t in self.templates],
            'next_id': self._next_id
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load from dictionary."""
        self.worlds = [self._dict_to_world(w) for w in data.get('worlds', [])]
        self.characters = [self._dict_to_character(c) for c in data.get('characters', [])]
        self.events = [self._dict_to_event(e) for e in data.get('events', [])]
        self.improvements = [self._dict_to_improvement(i) for i in data.get('improvements', [])]
        self.items = [self._dict_to_item(i) for i in data.get('items', [])]
        self.quests = [self._dict_to_quest(q) for q in data.get('quests', [])]
        
        # Validate storylines before creating them
        valid_storylines = []
        for s in data.get('storylines', []):
            if s.get('event_ids') or s.get('quest_ids'):
                try:
                    valid_storylines.append(self._dict_to_storyline(s))
                except Exception as e:
                    print(f"Warning: Skipping invalid storyline {s.get('id', 'unknown')}: {e}")
            else:
                print(f"Warning: Skipping storyline {s.get('id', 'unknown')} - must have at least one event or quest")
        
        self.storylines = valid_storylines
        self.templates = [self._dict_to_template(t) for t in data.get('templates', [])]
        self._next_id = data.get('next_id', 1)
    
    @staticmethod
    def _world_to_dict(world: World) -> Dict:
        return {
            'id': world.id.value if world.id else None,
            'name': str(world.name),
            'description': str(world.description),
            'created_at': world.created_at.value.isoformat(),
            'updated_at': world.updated_at.value.isoformat(),
            'version': world.version.value
        }
    
    @staticmethod
    def _dict_to_world(data: Dict) -> World:
        return World(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            name=WorldName(data['name']),
            description=Description(data['description']),
            parent_id=EntityId(data['parent_id']) if data.get('parent_id') else None,
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _character_to_dict(character: Character) -> Dict:
        return {
            'id': character.id.value if character.id else None,
            'world_id': character.world_id.value,
            'name': str(character.name),
            'backstory': str(character.backstory),
            'status': character.status.value,
            'abilities': [a.to_dict() for a in character.abilities],
            'created_at': character.created_at.value.isoformat(),
            'updated_at': character.updated_at.value.isoformat(),
            'version': character.version.value
        }
    
    @staticmethod
    def _dict_to_character(data: Dict) -> Character:
        return Character(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=CharacterName(data['name']),
            backstory=Backstory(data['backstory']),
            status=CharacterStatus(data['status']),
            abilities=[Ability.from_dict(a) for a in data['abilities']],
            parent_id=EntityId(data['parent_id']) if data.get('parent_id') else None,
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _event_to_dict(event: Event) -> Dict:
        return {
            'id': event.id.value if event.id else None,
            'world_id': event.world_id.value,
            'name': event.name,
            'description': str(event.description),
            'start_date': event.date_range.start_date.value.isoformat(),
            'end_date': event.date_range.end_date.value.isoformat() if event.date_range.end_date else None,
            'outcome': event.outcome.value,
            'participant_ids': [p.value for p in event.participant_ids],
            'created_at': event.created_at.value.isoformat(),
            'updated_at': event.updated_at.value.isoformat(),
            'version': event.version.value
        }
    
    @staticmethod
    def _dict_to_event(data: Dict) -> Event:
        from src.domain.value_objects.common import DateRange
        return Event(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=data['name'],
            description=Description(data['description']),
            date_range=DateRange(
                Timestamp(datetime.fromisoformat(data['start_date'])),
                Timestamp(datetime.fromisoformat(data['end_date'])) if data['end_date'] else None
            ),
            outcome=EventOutcome(data['outcome']),
            participant_ids=[EntityId(p) for p in data['participant_ids']],
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _improvement_to_dict(improvement: Improvement) -> Dict:
        return {
            'id': improvement.id.value if improvement.id else None,
            'entity_type': improvement.entity_type.value,
            'entity_id': improvement.entity_id.value,
            'suggestion': improvement.suggestion,
            'status': improvement.status.value,
            'git_commit_hash': improvement.git_commit_hash.value,
            'created_at': improvement.created_at.value.isoformat()
        }
    
    @staticmethod
    def _dict_to_improvement(data: Dict) -> Improvement:
        from src.domain.value_objects.common import GitCommitHash
        return Improvement(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            entity_type=EntityType(data['entity_type']),
            entity_id=EntityId(data['entity_id']),
            suggestion=data['suggestion'],
            status=__import__('src.domain.value_objects.common', fromlist=['ImprovementStatus']).ImprovementStatus(data['status']),
            git_commit_hash=GitCommitHash(data['git_commit_hash']),
            created_at=Timestamp(datetime.fromisoformat(data['created_at']))
        )
    
    @staticmethod
    def _item_to_dict(item: Item) -> Dict:
        return {
            'id': item.id.value if item.id else None,
            'world_id': item.world_id.value,
            'name': item.name,
            'description': str(item.description),
            'item_type': item.item_type.value,
            'rarity': item.rarity.value if item.rarity else None,
            'created_at': item.created_at.value.isoformat(),
            'updated_at': item.updated_at.value.isoformat(),
            'version': item.version.value
        }
    
    @staticmethod
    def _dict_to_item(data: Dict) -> Item:
        return Item(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=data['name'],
            description=Description(data['description']),
            item_type=ItemType(data['item_type']),
            rarity=Rarity(data['rarity']) if data['rarity'] else None,
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _quest_to_dict(quest: Quest) -> Dict:
        return {
            'id': quest.id.value if quest.id else None,
            'world_id': quest.world_id.value,
            'name': quest.name,
            'description': str(quest.description),
            'objectives': quest.objectives,
            'status': quest.status.value,
            'participant_ids': [p.value for p in quest.participant_ids],
            'reward_ids': [r.value for r in quest.reward_ids],
            'created_at': quest.created_at.value.isoformat(),
            'updated_at': quest.updated_at.value.isoformat(),
            'version': quest.version.value
        }
    
    @staticmethod
    def _dict_to_quest(data: Dict) -> Quest:
        return Quest(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=data['name'],
            description=Description(data['description']),
            objectives=data['objectives'],
            status=QuestStatus(data['status']),
            participant_ids=[EntityId(p) for p in data['participant_ids']],
            reward_ids=[EntityId(r) for r in data['reward_ids']],
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _storyline_to_dict(storyline: Storyline) -> Dict:
        return {
            'id': storyline.id.value if storyline.id else None,
            'world_id': storyline.world_id.value,
            'name': storyline.name,
            'description': str(storyline.description),
            'storyline_type': storyline.storyline_type.value,
            'event_ids': [e.value for e in storyline.event_ids],
            'quest_ids': [q.value for q in storyline.quest_ids],
            'created_at': storyline.created_at.value.isoformat(),
            'updated_at': storyline.updated_at.value.isoformat(),
            'version': storyline.version.value
        }
    
    @staticmethod
    def _dict_to_storyline(data: Dict) -> Storyline:
        return Storyline(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=data['name'],
            description=Description(data['description']),
            storyline_type=StorylineType(data['storyline_type']),
            event_ids=[EntityId(e) for e in data['event_ids']],
            quest_ids=[EntityId(q) for q in data['quest_ids']],
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _template_to_dict(template: Template) -> Dict:
        return {
            'id': template.id.value if template.id else None,
            'world_id': template.world_id.value,
            'name': str(template.name),
            'description': template.description,
            'template_type': template.template_type.value,
            'content': str(template.content),
            'rune_ids': [r.value for r in template.rune_ids],
            'parent_template_id': template.parent_template_id.value if template.parent_template_id else None,
            'created_at': template.created_at.value.isoformat(),
            'updated_at': template.updated_at.value.isoformat(),
            'version': template.version.value
        }
    
    @staticmethod
    def _dict_to_template(data: Dict) -> Template:
        return Template(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=TemplateName(data['name']),
            description=data['description'],
            template_type=TemplateType(data['template_type']),
            content=Content(data['content']),
            rune_ids=[EntityId(r) for r in data['rune_ids']],
            parent_template_id=EntityId(data['parent_template_id']) if data.get('parent_template_id') else None,
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )