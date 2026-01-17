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
from src.domain.entities.choice import Choice
from src.domain.entities.flowchart import Flowchart
from src.domain.entities.handout import Handout
from src.domain.entities.inspiration import Inspiration
from src.domain.entities.map import Map
from src.domain.entities.note import Note
from src.domain.entities.requirement import Requirement
from src.domain.entities.session import Session
from src.domain.entities.tokenboard import Tokenboard
from src.domain.value_objects.common import (
    TenantId, EntityId, WorldName, Description, CharacterName,
    Backstory, Timestamp, EntityType, EventOutcome, CharacterStatus,
    ItemType, Rarity, QuestStatus, StorylineType,
    PageName, Content, TemplateName, TemplateType, StoryName, StoryType,
    TagName, TagType, ImagePath, ImageType, ChoiceType, SessionStatus,
    NoteTitle, MapName, HandoutName, InspirationName, TokenboardName,
    FlowchartName, Version, GitCommitHash, ImprovementStatus, SessionName
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
        self.choices: List[Choice] = []
        self.flowcharts: List[Flowchart] = []
        self.handouts: List[Handout] = []
        self.inspirations: List[Inspiration] = []
        self.maps: List[Map] = []
        self.notes: List[Note] = []
        self.requirements: List[Requirement] = []
        self.sessions: List[Session] = []
        self.tokenboards: List[Tokenboard] = []
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
    
    def add_choice(self, choice: Choice) -> Choice:
        """Add choice with generated ID."""
        if choice.id is None:
            object.__setattr__(choice, 'id', self.get_next_id())
        self.choices.append(choice)
        return choice
    
    def add_flowchart(self, flowchart: Flowchart) -> Flowchart:
        """Add flowchart with generated ID."""
        if flowchart.id is None:
            object.__setattr__(flowchart, 'id', self.get_next_id())
        self.flowcharts.append(flowchart)
        return flowchart
    
    def add_handout(self, handout: Handout) -> Handout:
        """Add handout with generated ID."""
        if handout.id is None:
            object.__setattr__(handout, 'id', self.get_next_id())
        self.handouts.append(handout)
        return handout
    
    def add_inspiration(self, inspiration: Inspiration) -> Inspiration:
        """Add inspiration with generated ID."""
        if inspiration.id is None:
            object.__setattr__(inspiration, 'id', self.get_next_id())
        self.inspirations.append(inspiration)
        return inspiration
    
    def add_map(self, map: Map) -> Map:
        """Add map with generated ID."""
        if map.id is None:
            object.__setattr__(map, 'id', self.get_next_id())
        self.maps.append(map)
        return map
    
    def add_note(self, note: Note) -> Note:
        """Add note with generated ID."""
        if note.id is None:
            object.__setattr__(note, 'id', self.get_next_id())
        self.notes.append(note)
        return note
    
    def add_requirement(self, requirement: Requirement) -> Requirement:
        """Add requirement with generated ID."""
        if requirement.id is None:
            object.__setattr__(requirement, 'id', self.get_next_id())
        self.requirements.append(requirement)
        return requirement
    
    def add_session(self, session: Session) -> Session:
        """Add session with generated ID."""
        if session.id is None:
            object.__setattr__(session, 'id', self.get_next_id())
        self.sessions.append(session)
        return session
    
    def add_tokenboard(self, tokenboard: Tokenboard) -> Tokenboard:
        """Add tokenboard with generated ID."""
        if tokenboard.id is None:
            object.__setattr__(tokenboard, 'id', self.get_next_id())
        self.tokenboards.append(tokenboard)
        return tokenboard
    
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
            'pages': [self._page_to_dict(p) for p in self.pages],
            'stories': [self._story_to_dict(s) for s in self.stories],
            'tags': [self._tag_to_dict(t) for t in self.tags],
            'images': [self._image_to_dict(i) for i in self.images],
            'choices': [self._choice_to_dict(c) for c in self.choices],
            'flowcharts': [self._flowchart_to_dict(f) for f in self.flowcharts],
            'handouts': [self._handout_to_dict(h) for h in self.handouts],
            'inspirations': [self._inspiration_to_dict(i) for i in self.inspirations],
            'maps': [self._map_to_dict(m) for m in self.maps],
            'notes': [self._note_to_dict(n) for n in self.notes],
            'requirements': [self._requirement_to_dict(r) for r in self.requirements],
            'sessions': [self._session_to_dict(s) for s in self.sessions],
            'tokenboards': [self._tokenboard_to_dict(t) for t in self.tokenboards],
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
        self.pages = [self._dict_to_page(p) for p in data.get('pages', [])]
        self.stories = [self._dict_to_story(s) for s in data.get('stories', [])]
        self.tags = [self._dict_to_tag(t) for t in data.get('tags', [])]
        self.images = [self._dict_to_image(i) for i in data.get('images', [])]
        self.choices = [self._dict_to_choice(c) for c in data.get('choices', [])]
        self.flowcharts = [self._dict_to_flowchart(f) for f in data.get('flowcharts', [])]
        self.handouts = [self._dict_to_handout(h) for h in data.get('handouts', [])]
        self.inspirations = [self._dict_to_inspiration(i) for i in data.get('inspirations', [])]
        self.maps = [self._dict_to_map(m) for m in data.get('maps', [])]
        self.notes = [self._dict_to_note(n) for n in data.get('notes', [])]
        self.requirements = [self._dict_to_requirement(r) for r in data.get('requirements', [])]
        self.sessions = [self._dict_to_session(s) for s in data.get('sessions', [])]
        self.tokenboards = [self._dict_to_tokenboard(t) for t in data.get('tokenboards', [])]
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
    
    @staticmethod
    def _page_to_dict(page: Page) -> Dict:
        return {
            'id': page.id.value if page.id else None,
            'world_id': page.world_id.value,
            'name': str(page.name),
            'content': str(page.content),
            'template_id': page.template_id.value if page.template_id else None,
            'parent_id': page.parent_id.value if page.parent_id else None,
            'tag_ids': [t.value for t in page.tag_ids],
            'image_ids': [i.value for i in page.image_ids],
            'created_at': page.created_at.value.isoformat(),
            'updated_at': page.updated_at.value.isoformat(),
            'version': page.version.value
        }
    
    @staticmethod
    def _dict_to_page(data: Dict) -> Page:
        return Page(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=PageName(data['name']),
            content=Content(data['content']),
            template_id=EntityId(data['template_id']) if data.get('template_id') else None,
            parent_id=EntityId(data['parent_id']) if data.get('parent_id') else None,
            tag_ids=[EntityId(t) for t in data.get('tag_ids', [])],
            image_ids=[EntityId(i) for i in data.get('image_ids', [])],
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _story_to_dict(story: Story) -> Dict:
        return {
            'id': story.id.value if story.id else None,
            'world_id': story.world_id.value,
            'name': str(story.name),
            'description': story.description,
            'story_type': str(story.story_type),
            'content': str(story.content),
            'choice_ids': [c.value for c in story.choice_ids],
            'connected_world_ids': [w.value for w in story.connected_world_ids],
            'is_active': story.is_active,
            'created_at': story.created_at.value.isoformat(),
            'updated_at': story.updated_at.value.isoformat(),
            'version': story.version.value
        }
    
    @staticmethod
    def _dict_to_story(data: Dict) -> Story:
        return Story(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=StoryName(data['name']),
            description=data['description'],
            story_type=StoryType(data['story_type']),
            content=Content(data['content']),
            choice_ids=[EntityId(c) for c in data.get('choice_ids', [])],
            connected_world_ids=[EntityId(w) for w in data.get('connected_world_ids', [])],
            is_active=data.get('is_active', True),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _tag_to_dict(tag: Tag) -> Dict:
        return {
            'id': tag.id.value if tag.id else None,
            'world_id': tag.world_id.value,
            'name': str(tag.name),
            'tag_type': str(tag.tag_type),
            'color': tag.color,
            'description': tag.description,
            'created_at': tag.created_at.value.isoformat(),
            'updated_at': tag.updated_at.value.isoformat(),
            'version': tag.version.value
        }
    
    @staticmethod
    def _dict_to_tag(data: Dict) -> Tag:
        return Tag(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=TagName(data['name']),
            tag_type=TagType(data['tag_type']),
            color=data.get('color'),
            description=data.get('description'),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _image_to_dict(image: Image) -> Dict:
        return {
            'id': image.id.value if image.id else None,
            'world_id': image.world_id.value,
            'name': image.name,
            'path': str(image.path),
            'image_type': str(image.image_type),
            'alt_text': image.alt_text,
            'description': image.description,
            'file_size': image.file_size,
            'dimensions': image.dimensions,
            'created_at': image.created_at.value.isoformat(),
            'updated_at': image.updated_at.value.isoformat(),
            'version': image.version.value
        }
    
    @staticmethod
    def _dict_to_image(data: Dict) -> Image:
        return Image(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=data['name'],
            path=ImagePath(data['path']),
            image_type=ImageType(data['image_type']),
            alt_text=data.get('alt_text'),
            description=data.get('description'),
            file_size=data['file_size'],
            dimensions=data.get('dimensions'),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _choice_to_dict(choice: Choice) -> Dict:
        return {
            'id': choice.id.value if choice.id else None,
            'world_id': choice.world_id.value,
            'story_id': choice.story_id.value,
            'prompt': choice.prompt,
            'choice_type': str(choice.choice_type),
            'options': choice.options,
            'consequences': choice.consequences,
            'next_story_ids': [s.value if s else None for s in choice.next_story_ids],
            'is_mandatory': choice.is_mandatory,
            'created_at': choice.created_at.value.isoformat(),
            'updated_at': choice.updated_at.value.isoformat(),
            'version': choice.version.value
        }
    
    @staticmethod
    def _dict_to_choice(data: Dict) -> Choice:
        return Choice(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            story_id=EntityId(data['story_id']),
            prompt=data['prompt'],
            choice_type=ChoiceType(data['choice_type']),
            options=data['options'],
            consequences=data['consequences'],
            next_story_ids=[EntityId(s) if s else None for s in data['next_story_ids']],
            is_mandatory=data['is_mandatory'],
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _flowchart_to_dict(flowchart: Flowchart) -> Dict:
        return {
            'id': flowchart.id.value if flowchart.id else None,
            'world_id': flowchart.world_id.value,
            'story_id': flowchart.story_id.value if flowchart.story_id else None,
            'name': flowchart.name,
            'description': flowchart.description,
            'nodes': flowchart.nodes,
            'connections': flowchart.connections,
            'is_active': flowchart.is_active,
            'created_at': flowchart.created_at.value.isoformat(),
            'updated_at': flowchart.updated_at.value.isoformat(),
            'version': flowchart.version.value
        }
    
    @staticmethod
    def _dict_to_flowchart(data: Dict) -> Flowchart:
        return Flowchart(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            story_id=EntityId(data['story_id']) if data.get('story_id') else None,
            name=data['name'],
            description=data.get('description'),
            nodes=data['nodes'],
            connections=data['connections'],
            is_active=data.get('is_active', True),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _handout_to_dict(handout: Handout) -> Dict:
        return {
            'id': handout.id.value if handout.id else None,
            'world_id': handout.world_id.value,
            'title': handout.title,
            'content': handout.content,
            'image_ids': [i.value for i in handout.image_ids],
            'session_id': handout.session_id.value if handout.session_id else None,
            'is_revealed': handout.is_revealed,
            'reveal_timing': handout.reveal_timing,
            'created_at': handout.created_at.value.isoformat(),
            'updated_at': handout.updated_at.value.isoformat(),
            'version': handout.version.value
        }
    
    @staticmethod
    def _dict_to_handout(data: Dict) -> Handout:
        return Handout(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            title=data['title'],
            content=data.get('content'),
            image_ids=[EntityId(i) for i in data.get('image_ids', [])],
            session_id=EntityId(data['session_id']) if data.get('session_id') else None,
            is_revealed=data.get('is_revealed', False),
            reveal_timing=data.get('reveal_timing'),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _inspiration_to_dict(inspiration: Inspiration) -> Dict:
        return {
            'id': inspiration.id.value if inspiration.id else None,
            'world_id': inspiration.world_id.value,
            'title': inspiration.title,
            'content': inspiration.content,
            'category': inspiration.category,
            'tags': inspiration.tags,
            'source': inspiration.source,
            'is_used': inspiration.is_used,
            'created_at': inspiration.created_at.value.isoformat(),
            'updated_at': inspiration.updated_at.value.isoformat(),
            'version': inspiration.version.value
        }
    
    @staticmethod
    def _dict_to_inspiration(data: Dict) -> Inspiration:
        return Inspiration(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            title=data['title'],
            content=data['content'],
            category=data['category'],
            tags=data.get('tags', []),
            source=data.get('source'),
            is_used=data.get('is_used', False),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _map_to_dict(map: Map) -> Dict:
        return {
            'id': map.id.value if map.id else None,
            'world_id': map.world_id.value,
            'name': map.name,
            'description': map.description,
            'image_ids': [i.value for i in map.image_ids],
            'location_ids': [l.value for l in map.location_ids],
            'scale': map.scale,
            'is_interactive': map.is_interactive,
            'created_at': map.created_at.value.isoformat(),
            'updated_at': map.updated_at.value.isoformat(),
            'version': map.version.value
        }
    
    @staticmethod
    def _dict_to_map(data: Dict) -> Map:
        return Map(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=data['name'],
            description=data.get('description'),
            image_ids=[EntityId(i) for i in data.get('image_ids', [])],
            location_ids=[EntityId(l) for l in data.get('location_ids', [])],
            scale=data.get('scale'),
            is_interactive=data.get('is_interactive', False),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _note_to_dict(note: Note) -> Dict:
        return {
            'id': note.id.value if note.id else None,
            'world_id': note.world_id.value,
            'title': note.title,
            'content': note.content,
            'tags': note.tags,
            'is_pinned': note.is_pinned,
            'created_at': note.created_at.value.isoformat(),
            'updated_at': note.updated_at.value.isoformat(),
            'version': note.version.value
        }
    
    @staticmethod
    def _dict_to_note(data: Dict) -> Note:
        return Note(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            title=data['title'],
            content=data['content'],
            tags=data.get('tags', []),
            is_pinned=data.get('is_pinned', False),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _requirement_to_dict(requirement: Requirement) -> Dict:
        return {
            'id': requirement.id.value if requirement.id else None,
            'entity_type': str(requirement.entity_type) if requirement.entity_type else None,
            'entity_id': requirement.entity_id.value if requirement.entity_id else None,
            'description': requirement.description,
            'created_at': requirement.created_at.value.isoformat()
        }
    
    @staticmethod
    def _dict_to_requirement(data: Dict) -> Requirement:
        return Requirement(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            entity_type=EntityType(data['entity_type']) if data.get('entity_type') else None,
            entity_id=EntityId(data['entity_id']) if data.get('entity_id') else None,
            description=data['description'],
            created_at=Timestamp(datetime.fromisoformat(data['created_at']))
        )
    
    @staticmethod
    def _session_to_dict(session: Session) -> Dict:
        return {
            'id': session.id.value if session.id else None,
            'world_id': session.world_id.value,
            'name': str(session.name),
            'description': session.description,
            'gm_id': session.gm_id.value,
            'status': str(session.status),
            'scheduled_start': session.scheduled_start.value.isoformat(),
            'estimated_duration_hours': session.estimated_duration_hours,
            'player_ids': [p.value for p in session.player_ids],
            'actual_start': session.actual_start.value.isoformat() if session.actual_start else None,
            'actual_end': session.actual_end.value.isoformat() if session.actual_end else None,
            'created_at': session.created_at.value.isoformat(),
            'updated_at': session.updated_at.value.isoformat(),
            'version': session.version.value
        }
    
    @staticmethod
    def _dict_to_session(data: Dict) -> Session:
        return Session(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=SessionName(data['name']),
            description=data['description'],
            gm_id=EntityId(data['gm_id']),
            status=SessionStatus(data['status']),
            scheduled_start=Timestamp(datetime.fromisoformat(data['scheduled_start'])),
            estimated_duration_hours=data['estimated_duration_hours'],
            player_ids=[EntityId(p) for p in data.get('player_ids', [])],
            actual_start=Timestamp(datetime.fromisoformat(data['actual_start'])) if data.get('actual_start') else None,
            actual_end=Timestamp(datetime.fromisoformat(data['actual_end'])) if data.get('actual_end') else None,
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
    @staticmethod
    def _tokenboard_to_dict(tokenboard: Tokenboard) -> Dict:
        return {
            'id': tokenboard.id.value if tokenboard.id else None,
            'world_id': tokenboard.world_id.value,
            'name': tokenboard.name,
            'description': tokenboard.description,
            'counters': tokenboard.counters,
            'sticky_notes': tokenboard.sticky_notes,
            'shortcuts': tokenboard.shortcuts,
            'timers': tokenboard.timers,
            'is_active': tokenboard.is_active,
            'created_at': tokenboard.created_at.value.isoformat(),
            'updated_at': tokenboard.updated_at.value.isoformat(),
            'version': tokenboard.version.value
        }
    
    @staticmethod
    def _dict_to_tokenboard(data: Dict) -> Tokenboard:
        return Tokenboard(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=data['name'],
            description=data.get('description'),
            counters=data.get('counters', {}),
            sticky_notes=data.get('sticky_notes', []),
            shortcuts=data.get('shortcuts', {}),
            timers=data.get('timers', {}),
            is_active=data.get('is_active', False),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )