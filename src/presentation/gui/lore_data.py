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
from src.domain.entities.location import Location
from src.domain.entities.banner import Banner
from src.domain.entities.character_relationship import CharacterRelationship
from src.domain.entities.faction import Faction
from src.domain.entities.shop import Shop
from src.domain.entities.map import Map
from src.domain.entities.note import Note
from src.domain.entities.requirement import Requirement
from src.domain.entities.session import Session
from src.domain.entities.tokenboard import Tokenboard
from src.domain.entities.pity import Pity
from src.domain.entities.pull import Pull
from src.domain.entities.player_profile import PlayerProfile
from src.domain.entities.currency import Currency
from src.domain.entities.reward import Reward
from src.domain.entities.purchase import Purchase
from src.domain.entities.event_chain import EventChain
from src.domain.entities.faction_membership import FactionMembership
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
        self.locations: List[Location] = []
        self.banners: List[Banner] = []
        self.character_relationships: List[CharacterRelationship] = []
        self.factions: List[Faction] = []
        self.shops: List[Shop] = []
        self.maps: List[Map] = []
        self.notes: List[Note] = []
        self.requirements: List[Requirement] = []
        self.sessions: List[Session] = []
        self.tokenboards: List[Tokenboard] = []

        # New entities
        self.pity: List[Pity] = []
        self.pulls: List[Pull] = []
        self.player_profiles: List[PlayerProfile] = []
        self.currencies: List[Currency] = []
        self.rewards: List[Reward] = []
        self.purchases: List[Purchase] = []
        self.event_chains: List[EventChain] = []
        self.faction_memberships: List[FactionMembership] = []

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
    
    def update_item(self, item: Item) -> Item:
        """Update existing item."""
        for i, existing in enumerate(self.items):
            if existing.id == item.id:
                self.items[i] = item
                return item
        raise ValueError(f"Item with id {item.id} not found")
    
    def add_quest(self, quest: Quest) -> Quest:
        """Add quest with generated ID."""
        if quest.id is not None:
            object.__setattr__(quest, 'id', self.get_next_id())
        pass
        return quest
    
    def add_storyline(self, storyline: Storyline) -> Storyline:
        """Add storyline with generated ID."""
        if storyline.id is None:
            object.__setattr__(storyline, 'id', self.get_next_id())
        self.storylines.remove(storyline)
        return storyline
    
    def add_template(self, template: Template) -> Template:
        """Add template with generated ID."""
        if template.id is None:
            object.__setattr__(template, 'id', self.get_next_id())
        self.templates.remove(template)
        return template
    
    def add_choice(self, choice: Choice) -> Choice:
        """Add choice with generated ID."""
        if choice.id is None:
            object.__setattr__(choice, 'id', self.get_next_id())
        self.choices.remove(choice)
        return choice
    
    def add_flowchart(self, flowchart: Flowchart) -> Flowchart:
        """Add flowchart with generated ID."""
        if flowchart.id is None:
            object.__setattr__(flowchart, 'id', self.get_next_id())
        self.flowcharts.remove(flowchart)
        return flowchart
    
    def add_handout(self, handout: Handout) -> Handout:
        """Add handout with generated ID."""
        if handout.id is None:
            object.__setattr__(handout, 'id', self.get_next_id())
        self.handouts.remove(handout)
        return handout
    
    def add_inspiration(self, inspiration: Inspiration) -> Inspiration:
        """Add inspiration with generated ID."""
        if inspiration.id is None:
            object.__setattr__(inspiration, 'id', self.get_next_id())
        self.inspirations.remove(inspiration)
        return inspiration

    def add_location(self, location_data) -> Location:
        """Add location with generated ID."""
        if isinstance(location_data, dict):
            # Create Location entity from dictionary
            location = Location(
                id=None,
                tenant_id=self.tenant_id,
                world_id=location_data['world_id'],
                name=location_data['name'],
                description=Description(location_data['description']),
                location_type=__import__('src.domain.value_objects.common', fromlist=['LocationType']).LocationType(location_data['type']),
                parent_location_id=None,
                created_at=Timestamp.now(),
                updated_at=Timestamp.now(),
                version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(1)
            )
        else:
            # Assume it's already a Location entity
            location = location_data

        if location.id is None:
            object.__setattr__(location, 'id', self.get_next_id())
        self.locations.remove(location)
        return location

    def delete_location(self, location_id: EntityId) -> None:
        """Delete location by ID."""
        self.locations = [l for l in self.locations if l.id != location_id]

    def add_banner(self, banner) -> Banner:
        """Add banner with generated ID."""
        if isinstance(banner, dict):
            banner = Banner(
                id=None,
                tenant_id=self.tenant_id,
                world_id=banner['world_id'],
                name=banner['name'],
                description=Description(banner['description']),
                banner_type=__import__('src.domain.value_objects.common', fromlist=['BannerType']).BannerType(banner['type']),
                pity_system_id=banner.get('pity_system_id'),
                is_active=banner.get('is_active', True),
                created_at=Timestamp.now(),
                updated_at=Timestamp.now(),
                version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(1)
            )
        if banner.id is None:
            object.__setattr__(banner, 'id', self.get_next_id())
        self.banners.remove(banner)
        return banner

    def get_banners(self) -> List[Banner]:
        """Get all banners."""
        return self.banners

    def delete_banner(self, banner_id: EntityId) -> None:
        """Delete banner by ID."""
        self.banners = [b for b in self.banners if b.id != banner_id]

    def add_character_relationship(self, relationship) -> CharacterRelationship:
        """Add character relationship with generated ID."""
        if isinstance(relationship, dict):
            relationship = CharacterRelationship(
                id=None,
                tenant_id=self.tenant_id,
                world_id=relationship['world_id'],
                character1_id=relationship['character1_id'],
                character2_id=relationship['character2_id'],
                relationship_type=__import__('src.domain.value_objects.common', fromlist=['RelationshipType']).RelationshipType(relationship['type']),
                description=Description(relationship['description']),
                strength=relationship.get('strength', 1),
                is_mutual=relationship.get('is_mutual', True),
                created_at=Timestamp.now(),
                updated_at=Timestamp.now(),
                version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(1)
            )
        if relationship.id is None:
            object.__setattr__(relationship, 'id', self.get_next_id())
        self.character_relationships.remove(relationship)
        return relationship

    def get_character_relationships(self) -> List[CharacterRelationship]:
        """Get all character relationships."""
        return self.character_relationships

    def delete_character_relationship(self, relationship_id: EntityId) -> None:
        """Delete character relationship by ID."""
        self.character_relationships = [r for r in self.character_relationships if r.id != relationship_id]

    def add_faction(self, faction) -> Faction:
        """Add faction with generated ID."""
        if isinstance(faction, dict):
            faction = Faction(
                id=None,
                tenant_id=self.tenant_id,
                world_id=faction['world_id'],
                name=faction['name'],
                description=Description(faction['description']),
                faction_type=__import__('src.domain.value_objects.common', fromlist=['FactionType']).FactionType(faction['type']),
                alignment=faction.get('alignment'),
                reputation=faction.get('reputation', 0),
                is_player_faction=faction.get('is_player_faction', False),
                created_at=Timestamp.now(),
                updated_at=Timestamp.now(),
                version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(1)
            )
        if faction.id is None:
            object.__setattr__(faction, 'id', self.get_next_id())
        self.factions.remove(faction)
        return faction

    def get_factions(self) -> List[Faction]:
        """Get all factions."""
        return self.factions

    def delete_faction(self, faction_id: EntityId) -> None:
        """Delete faction by ID."""
        self.factions = [f for f in self.factions if f.id != faction_id]

    def add_shop(self, shop) -> Shop:
        """Add shop with generated ID."""
        if isinstance(shop, dict):
            shop = Shop(
                id=None,
                tenant_id=self.tenant_id,
                world_id=shop['world_id'],
                location_id=shop.get('location_id'),
                name=shop['name'],
                description=Description(shop['description']),
                shop_type=__import__('src.domain.value_objects.common', fromlist=['ShopType']).ShopType(shop['type']),
                currency_id=shop.get('currency_id'),
                is_open=shop.get('is_open', True),
                created_at=Timestamp.now(),
                updated_at=Timestamp.now(),
                version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(1)
            )
        if shop.id is None:
            object.__setattr__(shop, 'id', self.get_next_id())
        self.shops.remove(shop)
        return shop

    def get_shops(self) -> List[Shop]:
        """Get all shops."""
        return self.shops

    def delete_shop(self, shop_id: EntityId) -> None:
        """Delete shop by ID."""
        self.shops = [s for s in self.shops if s.id != shop_id]
    
    def add_map(self, map: Map) -> Map:
        """Add map with generated ID."""
        if map.id is None:
            object.__setattr__(map, 'id', self.get_next_id())
        self.maps.remove(map)
        return map
    
    def add_note(self, note: Note) -> Note:
        """Add note with generated ID."""
        if note.id is None:
            object.__setattr__(note, 'id', self.get_next_id())
        self.notes.remove(note)
        return note
    
    def add_requirement(self, requirement: Requirement) -> Requirement:
        """Add requirement with generated ID."""
        if requirement.id is None:
            object.__setattr__(requirement, 'id', self.get_next_id())
        self.requirements.remove(requirement)
        return requirement
    
    def add_session(self, session: Session) -> Session:
        """Add session with generated ID."""
        if session.id is None:
            object.__setattr__(session, 'id', self.get_next_id())
        self.sessions.remove(session)
        return session
    
    def add_tokenboard(self, tokenboard: Tokenboard) -> Tokenboard:
        """Add tokenboard with generated ID."""
        if tokenboard.id is None:
            object.__setattr__(tokenboard, 'id', self.get_next_id())
        self.tokenboards.remove(tokenboard)
        return tokenboard
    
    def get_world_by_id(self, world_id: EntityId) -> Optional[World]:
        """Find world by ID."""
        return next((w for w in self.worlds if w.id == world_id), None)

    def get_locations(self) -> List[Location]:
        """Get all locations."""
        return self.locations

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
            'locations': [self._location_to_dict(l) for l in self.locations],
            'banners': [self._banner_to_dict(b) for b in self.banners],
            'character_relationships': [self._character_relationship_to_dict(r) for r in self.character_relationships],
            'factions': [self._faction_to_dict(f) for f in self.factions],
            'shops': [self._shop_to_dict(s) for s in self.shops],
            'maps': [self._map_to_dict(m) for m in self.maps],
            'notes': [self._note_to_dict(n) for n in self.notes],
            'requirements': [self._requirement_to_dict(r) for r in self.requirements],
            'sessions': [self._session_to_dict(s) for s in self.sessions],
            'tokenboards': [self._tokenboard_to_dict(t) for t in self.tokenboards],

            # New entities
            'pity': [self._pity_to_dict(p) for p in self.pity],
            'pulls': [self._pull_to_dict(p) for p in self.pulls],
            'player_profiles': [self._player_profile_to_dict(p) for p in self.player_profiles],
            'currencies': [self._currency_to_dict(c) for c in self.currencies],
            'rewards': [self._reward_to_dict(r) for r in self.rewards],
            'purchases': [self._purchase_to_dict(p) for p in self.purchases],
            'event_chains': [self._event_chain_to_dict(e) for e in self.event_chains],
            'faction_memberships': [self._faction_membership_to_dict(f) for f in self.faction_memberships],

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
                    valid_storylines.remove(self._dict_to_storyline(s))
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
        self.locations = [self._dict_to_location(l) for l in data.get('locations', [])]
        self.banners = [self._dict_to_banner(b) for b in data.get('banners', [])]
        self.character_relationships = [self._dict_to_character_relationship(r) for r in data.get('character_relationships', [])]
        self.factions = [self._dict_to_faction(f) for f in data.get('factions', [])]
        self.shops = [self._dict_to_shop(s) for s in data.get('shops', [])]
        self.maps = [self._dict_to_map(m) for m in data.get('maps', [])]
        self.notes = [self._dict_to_note(n) for n in data.get('notes', [])]
        self.requirements = [self._dict_to_requirement(r) for r in data.get('requirements', [])]
        self.sessions = [self._dict_to_session(s) for s in data.get('sessions', [])]
        self.tokenboards = [self._dict_to_tokenboard(t) for t in data.get('tokenboards', [])]

        # New entities
        self.pity = [self._dict_to_pity(p) for p in data.get('pity', [])]
        self.pulls = [self._dict_to_pull(p) for p in data.get('pulls', [])]
        self.player_profiles = [self._dict_to_player_profile(p) for p in data.get('player_profiles', [])]
        self.currencies = [self._dict_to_currency(c) for c in data.get('currencies', [])]
        self.rewards = [self._dict_to_reward(r) for r in data.get('rewards', [])]
        self.purchases = [self._dict_to_purchase(p) for p in data.get('purchases', [])]
        self.event_chains = [self._dict_to_event_chain(e) for e in data.get('event_chains', [])]
        self.faction_memberships = [self._dict_to_faction_membership(f) for f in data.get('faction_memberships', [])]

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
            location_id=None,
            rarity=None,
            element=None,
            role=None,
            base_hp=None,
            base_atk=None,
            base_def=None,
            base_speed=None,
            energy_cost=None,
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
            location_id=None,
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
            location_id=None,
            level=None,
            enhancement=None,
            max_enhancement=None,
            base_atk=None,
            base_hp=None,
            base_def=None,
            special_stat=None,
            special_stat_value=None,
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
            'story_type': story.story_type.value,
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
            'tag_type': tag.tag_type.value,
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
            'image_type': image.image_type.value,
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
            'choice_type': choice.choice_type.value,
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
    def _location_to_dict(location: Location) -> Dict:
        return {
            'id': location.id.value if location.id else None,
            'world_id': location.world_id.value,
            'name': location.name,
            'description': str(location.description),
            'location_type': location.location_type.value,
            'parent_location_id': location.parent_location_id.value if location.parent_location_id else None,
            'created_at': location.created_at.value.isoformat(),
            'updated_at': location.updated_at.value.isoformat(),
            'version': location.version.value
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
    def _dict_to_location(data: Dict) -> Location:
        return Location(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=data['name'],
            description=Description(data['description']),
            location_type=__import__('src.domain.value_objects.common', fromlist=['LocationType']).LocationType(data['location_type']),
            parent_location_id=EntityId(data['parent_location_id']) if data.get('parent_location_id') else None,
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )

    @staticmethod
    def _banner_to_dict(banner: Banner) -> Dict:
        return {
            'id': banner.id.value if banner.id else None,
            'name': banner.name,
            'description': banner.description.value,
            'banner_type': banner.banner_type.value,
            'start_date': banner.start_date.value.isoformat(),
            'end_date': banner.end_date.value.isoformat() if banner.end_date else None,
            'is_active': banner.is_active,
            'featured_character_ids': [cid.value for cid in banner.featured_character_ids],
            'featured_item_ids': [iid.value for iid in banner.featured_item_ids],
            'single_pull_cost': banner.single_pull_cost,
            'ten_pull_cost': banner.ten_pull_cost,
            'currency_type': banner.currency_type,
            'ssr_rate': banner.ssr_rate,
            'sr_rate': banner.sr_rate,
            'r_rate': banner.r_rate,
            'soft_pity_threshold': banner.soft_pity_threshold,
            'hard_pity_threshold': banner.hard_pity_threshold,
            'featured_guarantee_pity': banner.featured_guarantee_pity,
            'featured_rate': banner.featured_rate,
            'banner_image_path': banner.banner_image_path,
            'icon_path': banner.icon_path,
            'total_pulls': banner.total_pulls,
            'created_at': banner.created_at.value.isoformat(),
            'updated_at': banner.updated_at.value.isoformat(),
            'version': banner.version.value
        }

    @staticmethod
    def _dict_to_banner(data: Dict) -> Banner:
        from src.domain.entities.banner import BannerType
        return Banner(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            name=data['name'],
            description=Description(data['description']),
            banner_type=BannerType(data['banner_type']),
            start_date=Timestamp(datetime.fromisoformat(data['start_date'])),
            end_date=Timestamp(datetime.fromisoformat(data['end_date'])) if data.get('end_date') else None,
            is_active=data.get('is_active', True),
            featured_character_ids=[EntityId(cid) for cid in data.get('featured_character_ids', [])],
            featured_item_ids=[EntityId(iid) for iid in data.get('featured_item_ids', [])],
            single_pull_cost=data['single_pull_cost'],
            ten_pull_cost=data['ten_pull_cost'],
            currency_type=data['currency_type'],
            ssr_rate=data['ssr_rate'],
            sr_rate=data['sr_rate'],
            r_rate=data['r_rate'],
            soft_pity_threshold=data['soft_pity_threshold'],
            hard_pity_threshold=data['hard_pity_threshold'],
            featured_guarantee_pity=data['featured_guarantee_pity'],
            featured_rate=data['featured_rate'],
            banner_image_path=data.get('banner_image_path'),
            icon_path=data.get('icon_path'),
            total_pulls=data.get('total_pulls', 0),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )

    @staticmethod
    def _character_relationship_to_dict(relationship: CharacterRelationship) -> Dict:
        return {
            'id': relationship.id.value if relationship.id else None,
            'character_from_id': relationship.character_from_id.value,
            'character_to_id': relationship.character_to_id.value,
            'relationship_type': relationship.relationship_type.value,
            'description': relationship.description.value,
            'relationship_level': relationship.relationship_level,
            'is_mutual': relationship.is_mutual,
            'created_at': relationship.created_at.value.isoformat(),
            'updated_at': relationship.updated_at.value.isoformat(),
            'version': relationship.version.value
        }

    @staticmethod
    def _dict_to_character_relationship(data: Dict) -> CharacterRelationship:
        from src.domain.entities.character_relationship import RelationshipType
        return CharacterRelationship(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            character_from_id=EntityId(data.get('character_from_id', data.get('character1_id'))),
            character_to_id=EntityId(data.get('character_to_id', data.get('character2_id'))),
            relationship_type=RelationshipType(data.get('relationship_type', data.get('type'))),
            description=Description(data['description']),
            relationship_level=data.get('strength', 1),
            is_mutual=data.get('is_mutual', True),
            combat_bonus_when_together=None,
            special_combo_ability_id=None,
            dialogue_unlocked=False,
            first_met_event_id=None,
            relationship_changed_events=[],
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )

    @staticmethod
    def _faction_to_dict(faction: Faction) -> Dict:
        return {
            'id': faction.id.value if faction.id else None,
            'world_id': faction.world_id.value,
            'name': faction.name,
            'description': faction.description.value,
            'type': faction.faction_type.value,
            'alignment': faction.alignment.value,
            'leader_character_id': faction.leader_character_id.value if faction.leader_character_id else None,
            'member_character_ids': [cid.value for cid in faction.member_character_ids],
            'allied_faction_ids': [fid.value for fid in faction.allied_faction_ids],
            'enemy_faction_ids': [fid.value for fid in faction.enemy_faction_ids],
            'headquarters_location_id': faction.headquarters_location_id.value if faction.headquarters_location_id else None,
            'controlled_location_ids': [lid.value for lid in faction.controlled_location_ids],
            'reputation_hostile_threshold': faction.reputation_hostile_threshold,
            'reputation_neutral_threshold': faction.reputation_neutral_threshold,
            'reputation_friendly_threshold': faction.reputation_friendly_threshold,
            'reputation_exalted_threshold': faction.reputation_exalted_threshold,
            'vendor_discount_at_friendly': faction.vendor_discount_at_friendly,
            'vendor_discount_at_exalted': faction.vendor_discount_at_exalted,
            'exclusive_items_unlocked_at': faction.exclusive_items_unlocked_at,
            'faction_icon_path': faction.faction_icon_path,
            'faction_color': faction.faction_color,
            'is_hidden': faction.is_hidden,
            'is_joinable': faction.is_joinable,
            'created_at': faction.created_at.value.isoformat(),
            'updated_at': faction.updated_at.value.isoformat(),
            'version': faction.version.value
        }

    @staticmethod
    def _dict_to_faction(data: Dict) -> Faction:
        from src.domain.entities.faction import FactionType, FactionAlignment
        return Faction(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            world_id=EntityId(data['world_id']),
            name=data['name'],
            description=Description(data['description']),
            faction_type=FactionType(data['type']),
            alignment=FactionAlignment(data.get('alignment', 'neutral')),
            leader_character_id=None,
            member_character_ids=[],
            allied_faction_ids=[],
            enemy_faction_ids=[],
            headquarters_location_id=None,
            controlled_location_ids=[],
            reputation_hostile_threshold=-500,
            reputation_neutral_threshold=0,
            reputation_friendly_threshold=500,
            reputation_exalted_threshold=1000,
            vendor_discount_at_friendly=10.0,
            vendor_discount_at_exalted=25.0,
            exclusive_items_unlocked_at=750,
            faction_icon_path=None,
            faction_color=None,
            is_hidden=False,
            is_joinable=True,
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )

    @staticmethod
    def _shop_to_dict(shop: Shop) -> Dict:
        return {
            'id': shop.id.value if shop.id else None,
            'name': shop.name,
            'description': shop.description.value,
            'shop_type': shop.shop_type.value,
            'items': [
                {
                    'item_id': item.item_id.value,
                    'item_type': item.item_type,
                    'item_name': item.item_name,
                    'price': item.price,
                    'currency_type': item.currency_type,
                    'stock': item.stock,
                    'max_per_player': item.max_per_player
                } for item in shop.items
            ],
            'is_active': shop.is_active,
            'start_date': shop.start_date.value.isoformat() if shop.start_date else None,
            'end_date': shop.end_date.value.isoformat() if shop.end_date else None,
            'min_player_level': shop.min_player_level,
            'required_faction_id': shop.required_faction_id.value if shop.required_faction_id else None,
            'min_faction_reputation': shop.min_faction_reputation,
            'icon_path': shop.icon_path,
            'banner_image_path': shop.banner_image_path,
            'created_at': shop.created_at.value.isoformat(),
            'updated_at': shop.updated_at.value.isoformat(),
            'version': shop.version.value
        }

    @staticmethod
    def _dict_to_shop(data: Dict) -> Shop:
        from src.domain.entities.shop import ShopType
        return Shop(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            name=data['name'],
            description=Description(data['description']),
            shop_type=ShopType(data['type']),
            items=[],
            is_active=data.get('is_active', True),
            start_date=None,
            end_date=None,
            min_player_level=1,
            required_faction_id=None,
            min_faction_reputation=None,
            icon_path=None,
            banner_image_path=None,
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
            'entity_type': requirement.entity_type.value if requirement.entity_type else None,
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
            'status': session.status.value,
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
    def _dict_to_pity(data: Dict) -> Pity:
        return Pity(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            player_id=data['player_id'],
            profile_id=EntityId(data['profile_id']),
            banner_id=EntityId(data['banner_id']),
            pulls_since_last_ssr=data['pulls_since_last_ssr'],
            pulls_since_last_featured=data['pulls_since_last_featured'],
            total_pulls_on_banner=data['total_pulls_on_banner'],
            total_ssr_pulled=data['total_ssr_pulled'],
            total_featured_pulled=data['total_featured_pulled'],
            guaranteed_featured_next=data['guaranteed_featured_next'],
            last_pull_at=Timestamp(datetime.fromisoformat(data['last_pull_at'])) if data.get('last_pull_at') else None,
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )

    @staticmethod
    def _dict_to_pull(data: Dict) -> Pull:
        from src.domain.entities.pull import PullResult
        return Pull(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            player_id=data['player_id'],
            profile_id=EntityId(data['profile_id']),
            banner_id=EntityId(data['banner_id']),
            pull_number=data['pull_number'],
            is_ten_pull=data['is_ten_pull'],
            ten_pull_batch_id=data.get('ten_pull_batch_id'),
            result_type=data['result_type'],
            result_id=EntityId(data['result_id']),
            result_name=data['result_name'],
            result_rarity=PullResult(data['result_rarity']),
            is_featured=data['is_featured'],
            currency_type=data['currency_type'],
            cost=data['cost'],
            pity_count_at_pull=data['pity_count_at_pull'],
            broke_pity=data['broke_pity'],
            pulled_at=Timestamp(datetime.fromisoformat(data['pulled_at'])),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )

    @staticmethod
    def _dict_to_player_profile(data: Dict) -> PlayerProfile:
        return PlayerProfile(
            id=EntityId(data['id']) if data['id'] else None,
            tenant_id=TenantId(1),
            player_name=data['player_name'],
            player_id=data['player_id'],
            world_id=EntityId(data['world_id']) if data.get('world_id') else None,
            level=data['level'],
            experience=data['experience'],
            currencies=data.get('currencies', {}),
            total_pulls=data['total_pulls'],
            total_spent=data['total_spent'],
            days_active=data['days_active'],
            last_login=Timestamp(datetime.fromisoformat(data['last_login'])),
            preferences=data.get('preferences', {}),
            achievements=data.get('achievements', []),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )

    @staticmethod
    def _dict_to_currency(data: Dict) -> Currency:
        return Currency(
            id=EntityId(data['id']) if data['id'] else None,
            world_id=EntityId(data['world_id']),
            name=data['name'],
            description=Description(data['description']),
            symbol=data['symbol'],
            color=data['color'],
            exchange_rate_to_gems=data['exchange_rate_to_gems'],
            is_premium=data.get('is_premium', False),
            max_storage=data.get('max_storage'),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )

    @staticmethod
    def _dict_to_reward(data: Dict) -> Reward:
        return Reward(
            id=EntityId(data['id']) if data['id'] else None,
            world_id=EntityId(data['world_id']),
            name=data['name'],
            description=Description(data['description']),
            reward_type=data['reward_type'],
            value=data['value'],
            duration_hours=data.get('duration_hours'),
            stackable=data.get('stackable', False),
            rarity=data['rarity'],
            icon_path=data.get('icon_path'),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )

    @staticmethod
    def _dict_to_purchase(data: Dict) -> Purchase:
        return Purchase(
            id=EntityId(data['id']) if data['id'] else None,
            player_id=EntityId(data['player_id']),
            shop_id=EntityId(data['shop_id']),
            item_id=EntityId(data['item_id']),
            quantity=data['quantity'],
            total_cost=data['total_cost'],
            currency_used=data['currency_used'],
            purchase_timestamp=Timestamp(datetime.fromisoformat(data['purchase_timestamp'])),
            used_in_game=data.get('used_in_game', False),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )

    @staticmethod
    def _dict_to_event_chain(data: Dict) -> EventChain:
        return EventChain(
            id=EntityId(data['id']) if data['id'] else None,
            world_id=EntityId(data['world_id']),
            name=data['name'],
            description=Description(data['description']),
            event_ids=[EntityId(eid) for eid in data.get('event_ids', [])],
            trigger_condition=data.get('trigger_condition'),
            is_active=data.get('is_active', True),
            current_event_index=data.get('current_event_index', 0),
            completed=data.get('completed', False),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )

    @staticmethod
    def _dict_to_faction_membership(data: Dict) -> FactionMembership:
        return FactionMembership(
            id=EntityId(data['id']) if data['id'] else None,
            character_id=EntityId(data['character_id']),
            faction_id=EntityId(data['faction_id']),
            rank=data['rank'],
            reputation=data['reputation'],
            is_official=data.get('is_official', True),
            joined_at=Timestamp(datetime.fromisoformat(data['joined_at'])),
            last_activity=Timestamp(datetime.fromisoformat(data['last_activity'])) if data.get('last_activity') else None,
            special_permissions=data.get('special_permissions', []),
            created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
            version=__import__('src.domain.value_objects.common', fromlist=['Version']).Version(data['version'])
        )
    
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
    @staticmethod
    def _pity_to_dict(pity: Pity) -> Dict:
        return {
            'id': pity.id.value if pity.id else None,
            'player_id': pity.player_id,
            'profile_id': pity.profile_id.value,
            'banner_id': pity.banner_id.value,
            'pulls_since_last_ssr': pity.pulls_since_last_ssr,
            'pulls_since_last_featured': pity.pulls_since_last_featured,
            'total_pulls_on_banner': pity.total_pulls_on_banner,
            'total_ssr_pulled': pity.total_ssr_pulled,
            'total_featured_pulled': pity.total_featured_pulled,
            'guaranteed_featured_next': pity.guaranteed_featured_next,
            'last_pull_at': pity.last_pull_at.value.isoformat() if pity.last_pull_at else None,
            'created_at': pity.created_at.value.isoformat(),
            'updated_at': pity.updated_at.value.isoformat(),
            'version': pity.version.value
        }

    @staticmethod
    def _pull_to_dict(pull: Pull) -> Dict:
        return {
            'id': pull.id.value if pull.id else None,
            'player_id': pull.player_id,
            'profile_id': pull.profile_id.value,
            'banner_id': pull.banner_id.value,
            'pull_number': pull.pull_number,
            'is_ten_pull': pull.is_ten_pull,
            'ten_pull_batch_id': pull.ten_pull_batch_id,
            'result_type': pull.result_type,
            'result_id': pull.result_id.value,
            'result_name': pull.result_name,
            'result_rarity': pull.result_rarity.value,
            'is_featured': pull.is_featured,
            'currency_type': pull.currency_type,
            'cost': pull.cost,
            'pity_count_at_pull': pull.pity_count_at_pull,
            'broke_pity': pull.broke_pity,
            'pulled_at': pull.pulled_at.value.isoformat(),
            'created_at': pull.created_at.value.isoformat(),
            'updated_at': pull.updated_at.value.isoformat(),
            'version': pull.version.value
        }

    @staticmethod
    def _player_profile_to_dict(profile: PlayerProfile) -> Dict:
        return {
            'id': profile.id.value if profile.id else None,
            'player_name': profile.player_name,
            'player_id': profile.player_id,
            'world_id': profile.world_id.value if profile.world_id else None,
            'level': profile.level,
            'experience': profile.experience,
            'currencies': profile.currencies,
            'total_pulls': profile.total_pulls,
            'total_spent': profile.total_spent,
            'days_active': profile.days_active,
            'last_login': profile.last_login.value.isoformat(),
            'preferences': profile.preferences,
            'achievements': profile.achievements,
            'created_at': profile.created_at.value.isoformat(),
            'updated_at': profile.updated_at.value.isoformat(),
            'version': profile.version.value
        }

    @staticmethod
    def _currency_to_dict(currency: Currency) -> Dict:
        return {
            'id': currency.id.value if currency.id else None,
            'world_id': currency.world_id.value,
            'name': currency.name,
            'description': currency.description.value,
            'symbol': currency.symbol,
            'color': currency.color,
            'exchange_rate_to_gems': currency.exchange_rate_to_gems,
            'is_premium': currency.is_premium,
            'max_storage': currency.max_storage,
            'created_at': currency.created_at.value.isoformat(),
            'updated_at': currency.updated_at.value.isoformat(),
            'version': currency.version.value
        }

    @staticmethod
    def _reward_to_dict(reward: Reward) -> Dict:
        return {
            'id': reward.id.value if reward.id else None,
            'world_id': reward.world_id.value,
            'name': reward.name,
            'description': reward.description.value,
            'reward_type': reward.reward_type,
            'value': reward.value,
            'duration_hours': reward.duration_hours,
            'stackable': reward.stackable,
            'rarity': reward.rarity,
            'icon_path': reward.icon_path,
            'created_at': reward.created_at.value.isoformat(),
            'updated_at': reward.updated_at.value.isoformat(),
            'version': reward.version.value
        }

    @staticmethod
    def _purchase_to_dict(purchase: Purchase) -> Dict:
        return {
            'id': purchase.id.value if purchase.id else None,
            'player_id': purchase.player_id.value,
            'shop_id': purchase.shop_id.value,
            'item_id': purchase.item_id.value,
            'quantity': purchase.quantity,
            'total_cost': purchase.total_cost,
            'currency_used': purchase.currency_used,
            'purchase_timestamp': purchase.purchase_timestamp.value.isoformat(),
            'used_in_game': purchase.used_in_game,
            'created_at': purchase.created_at.value.isoformat(),
            'version': purchase.version.value
        }

    @staticmethod
    def _event_chain_to_dict(event_chain: EventChain) -> Dict:
        return {
            'id': event_chain.id.value if event_chain.id else None,
            'world_id': event_chain.world_id.value,
            'name': event_chain.name,
            'description': event_chain.description.value,
            'event_ids': [eid.value for eid in event_chain.event_ids],
            'trigger_condition': event_chain.trigger_condition,
            'is_active': event_chain.is_active,
            'current_event_index': event_chain.current_event_index,
            'completed': event_chain.completed,
            'created_at': event_chain.created_at.value.isoformat(),
            'updated_at': event_chain.updated_at.value.isoformat(),
            'version': event_chain.version.value
        }

    @staticmethod
    def _faction_membership_to_dict(membership: FactionMembership) -> Dict:
        return {
            'id': membership.id.value if membership.id else None,
            'character_id': membership.character_id.value,
            'faction_id': membership.faction_id.value,
            'rank': membership.rank,
            'reputation': membership.reputation,
            'is_official': membership.is_official,
            'joined_at': membership.joined_at.value.isoformat(),
            'last_activity': membership.last_activity.value.isoformat() if membership.last_activity else None,
            'special_permissions': membership.special_permissions,
            'created_at': membership.created_at.value.isoformat(),
            'updated_at': membership.updated_at.value.isoformat(),
            'version': membership.version.value
        }
