"""
LoreData - In-memory storage for lore entities.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.application.integration.dto.provenance import EntityProvenanceLink, GenerationRunRecord
from src.application.presentation_contracts import *  # noqa: F401,F403



# Serializer bodies extracted to lore_data_serializers.py.
from src.presentation.gui.lore_data_serializers import (  # noqa: F401
    _world_to_dict, _dict_to_world, _character_to_dict, _dict_to_character, _event_to_dict, _dict_to_event,
    _improvement_to_dict, _dict_to_improvement, _item_to_dict, _dict_to_item, _quest_to_dict, _dict_to_quest,
    _storyline_to_dict, _dict_to_storyline, _template_to_dict, _dict_to_template, _page_to_dict, _dict_to_page,
    _story_to_dict, _dict_to_story, _tag_to_dict, _dict_to_tag, _image_to_dict, _dict_to_image,
    _choice_to_dict, _dict_to_choice, _flowchart_to_dict, _dict_to_flowchart, _handout_to_dict, _dict_to_handout,
    _inspiration_to_dict, _location_to_dict, _dict_to_inspiration, _dict_to_location, _environment_to_dict, _dict_to_environment,
    _banner_to_dict, _dict_to_banner, _character_relationship_to_dict, _dict_to_character_relationship, _faction_to_dict, _dict_to_faction,
    _shop_to_dict, _dict_to_shop, _map_to_dict, _dict_to_map, _note_to_dict, _dict_to_note,
    _requirement_to_dict, _dict_to_requirement, _session_to_dict, _dict_to_session, _tokenboard_to_dict, _dict_to_pity,
    _dict_to_pull, _dict_to_player_profile, _dict_to_currency, _dict_to_reward, _dict_to_purchase, _dict_to_event_chain,
    _dict_to_faction_membership, _dict_to_tokenboard, _pity_to_dict, _pull_to_dict, _player_profile_to_dict, _currency_to_dict,
    _reward_to_dict, _purchase_to_dict, _event_chain_to_dict, _faction_membership_to_dict, _lore_axioms_to_dict, _music_control_to_dict,
    _music_state_to_dict, _progression_event_to_dict, _character_state_to_dict, _music_theme_to_dict, _music_track_to_dict, _dict_to_lore_axioms,
    _dict_to_music_control, _dict_to_music_state, _dict_to_progression_event, _dict_to_character_state, _dict_to_music_theme, _dict_to_music_track,
    _texture_to_dict, _dict_to_texture, _model_to_dict, _dict_to_model,
)

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
        self.environments: List[Environment] = []
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
        self.textures: List[Texture] = []
        self.models: List[Model3D] = []
        self.event_chains: List[EventChain] = []
        self.faction_memberships: List[FactionMembership] = []

        # Advanced entities
        self.lore_axioms: List[LoreAxioms] = []
        self.music_controls: List[MusicControl] = []
        self.music_states: List[MusicState] = []
        self.music_themes: List[MusicTheme] = []
        self.music_tracks: List[MusicTrack] = []
        self.progression_events: List[ProgressionEvent] = []
        self.character_states: List[CharacterState] = []

        self.metadata: Dict[str, Any] = self._normalize_metadata()
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
                location_type=LocationType(location_data['type']),
                parent_location_id=None,
                created_at=Timestamp.now(),
                updated_at=Timestamp.now(),
                version=Version(1)
            )
        else:
            # Assume it's already a Location entity
            location = location_data

        if location.id is None:
            object.__setattr__(location, 'id', self.get_next_id())
        self.locations.append(location)
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
                banner_type=BannerType(banner['type']),
                pity_system_id=banner.get('pity_system_id'),
                is_active=banner.get('is_active', True),
                created_at=Timestamp.now(),
                updated_at=Timestamp.now(),
                version=Version(1)
            )
        if banner.id is None:
            object.__setattr__(banner, 'id', self.get_next_id())
        self.banners.append(banner)
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
                relationship_type=RelationshipType(relationship['type']),
                description=Description(relationship['description']),
                strength=relationship.get('strength', 1),
                is_mutual=relationship.get('is_mutual', True),
                created_at=Timestamp.now(),
                updated_at=Timestamp.now(),
                version=Version(1)
            )
        if relationship.id is None:
            object.__setattr__(relationship, 'id', self.get_next_id())
        self.character_relationships.append(relationship)
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
                faction_type=FactionType(faction['type']),
                alignment=faction.get('alignment'),
                reputation=faction.get('reputation', 0),
                is_player_faction=faction.get('is_player_faction', False),
                created_at=Timestamp.now(),
                updated_at=Timestamp.now(),
                version=Version(1)
            )
        if faction.id is None:
            object.__setattr__(faction, 'id', self.get_next_id())
        self.factions.append(faction)
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
                shop_type=ShopType(shop['type']),
                currency_id=shop.get('currency_id'),
                is_open=shop.get('is_open', True),
                created_at=Timestamp.now(),
                updated_at=Timestamp.now(),
                version=Version(1)
            )
        if shop.id is None:
            object.__setattr__(shop, 'id', self.get_next_id())
        self.shops.append(shop)
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

    # Advanced entities methods
    def add_lore_axioms(self, lore_axioms: LoreAxioms) -> LoreAxioms:
        """Add lore axioms with generated ID."""
        if lore_axioms.id is None:
            object.__setattr__(lore_axioms, 'id', self.get_next_id())
        self.lore_axioms.append(lore_axioms)
        return lore_axioms

    def add_music_control(self, music_control: MusicControl) -> MusicControl:
        """Add music control with generated ID."""
        if music_control.id is None:
            object.__setattr__(music_control, 'id', self.get_next_id())
        self.music_controls.append(music_control)
        return music_control

    def add_music_state(self, music_state: MusicState) -> MusicState:
        """Add music state with generated ID."""
        if music_state.id is None:
            object.__setattr__(music_state, 'id', self.get_next_id())
        self.music_states.append(music_state)
        return music_state

    def add_progression_event(self, progression_event: ProgressionEvent) -> ProgressionEvent:
        """Add progression event."""
        self.progression_events.append(progression_event)
        return progression_event

    def add_music_theme(self, music_theme: MusicTheme) -> MusicTheme:
        """Add music theme with generated ID."""
        if music_theme.id is None:
            object.__setattr__(music_theme, 'id', self.get_next_id())
        self.music_themes.append(music_theme)
        return music_theme

    def add_music_track(self, music_track: MusicTrack) -> MusicTrack:
        """Add music track with generated ID."""
        if music_track.id is None:
            object.__setattr__(music_track, 'id', self.get_next_id())
        self.music_tracks.append(music_track)
        return music_track

    def add_character_state(self, character_state: CharacterState) -> CharacterState:
        """Add character state."""
        self.character_states.append(character_state)
        return character_state

    def add_texture(self, texture: Texture) -> Texture:
        """Add texture with generated ID."""
        if texture.id is None:
            object.__setattr__(texture, 'id', self.get_next_id())
        self.textures.append(texture)
        return texture

    def add_model(self, model: Model3D) -> Model3D:
        """Add 3D model with generated ID."""
        if model.id is None:
            object.__setattr__(model, 'id', self.get_next_id())
        self.models.append(model)
        return model

    def get_lore_axioms_by_world_id(self, world_id: EntityId) -> Optional[LoreAxioms]:
        """Get lore axioms for a specific world."""
        return next((la for la in self.lore_axioms if la.world_id == world_id), None)

    def get_character_states(self, character_id: EntityId) -> List[CharacterState]:
        """Get all states for a character."""
        return [cs for cs in self.character_states if cs.character_id == character_id]

    def get_world_by_id(self, world_id: EntityId) -> Optional[World]:
        """Find world by ID."""
        return next((w for w in self.worlds if w.id == world_id), None)

    def get_locations(self) -> List[Location]:
        """Get all locations."""
        return self.locations

    def add_environment(self, environment_data: dict) -> Environment:
        """Add environment from dictionary data."""
        environment = Environment(
            id=None,
            tenant_id=self.tenant_id,
            world_id=EntityId(environment_data['world_id']),
            location_id=EntityId(environment_data['location_id']),
            name=environment_data['name'],
            description=Description(environment_data['description']) if environment_data.get('description') else None,
            time_of_day=TimeOfDay(environment_data['time_of_day']),
            weather=Weather(environment_data['weather']),
            lighting=Lighting(environment_data['lighting']),
            temperature=environment_data.get('temperature'),
            sounds=environment_data.get('sounds'),
            smells=environment_data.get('smells'),
            is_active=environment_data.get('is_active', True),
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
            version=Version(1)
        )
        if environment.id is None:
            object.__setattr__(environment, 'id', self.get_next_id())
        self.environments.append(environment)
        return environment

    def update_environment(self, environment_id: EntityId, environment_data: dict) -> Environment:
        """Update existing environment."""
        for i, existing in enumerate(self.environments):
            if existing.id == environment_id:
                # Update the environment
                updated_environment = Environment(
                    id=existing.id,
                    tenant_id=existing.tenant_id,
                    world_id=EntityId(environment_data['world_id']),
                    location_id=EntityId(environment_data['location_id']),
                    name=environment_data['name'],
                    description=Description(environment_data['description']) if environment_data.get('description') else None,
                    time_of_day=TimeOfDay(environment_data['time_of_day']),
                    weather=Weather(environment_data['weather']),
                    lighting=Lighting(environment_data['lighting']),
                    temperature=environment_data.get('temperature'),
                    sounds=environment_data.get('sounds'),
                    smells=environment_data.get('smells'),
                    is_active=environment_data.get('is_active', True),
                    created_at=existing.created_at,
                    updated_at=Timestamp.now(),
                    version=existing.version.increment()
                )
                self.environments[i] = updated_environment
                return updated_environment
        raise ValueError(f"Environment with id {environment_id} not found")

    def get_environments(self) -> List[Environment]:
        """Get all environments."""
        return self.environments

    def delete_environment(self, environment_id: EntityId) -> None:
        """Delete environment by ID."""
        self.environments = [e for e in self.environments if e.id != environment_id]

    def get_characters_by_world(self, world_id: EntityId) -> List[Character]:
        """Get all characters in a world."""
        return [c for c in self.characters if c.world_id == world_id]

    @staticmethod
    def _normalize_metadata(metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = dict(metadata) if isinstance(metadata, dict) else {}
        payload['generation_runs'] = [
            GenerationRunRecord.from_dict(item).to_dict()
            for item in (payload.get('generation_runs') or [])
            if isinstance(item, dict)
        ]
        payload['entity_provenance'] = [
            EntityProvenanceLink.from_dict(item).to_dict()
            for item in (payload.get('entity_provenance') or [])
            if isinstance(item, dict)
        ]
        return payload

    def add_generation_run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Register a normalized generation run in top-level metadata."""
        record = GenerationRunRecord.from_dict(payload).to_dict()
        self.metadata.setdefault('generation_runs', []).append(record)
        return record

    def add_entity_provenance(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Register a normalized entity provenance link in top-level metadata."""
        record = EntityProvenanceLink.from_dict(payload).to_dict()
        self.metadata.setdefault('entity_provenance', []).append(record)
        return record
    
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
            'environments': [self._environment_to_dict(e) for e in self.environments],
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

            # Advanced entities
            'lore_axioms': [self._lore_axioms_to_dict(la) for la in self.lore_axioms],
            'music_controls': [self._music_control_to_dict(mc) for mc in self.music_controls],
            'music_states': [self._music_state_to_dict(ms) for ms in self.music_states],
            'music_themes': [self._music_theme_to_dict(mt) for mt in self.music_themes],
            'music_tracks': [self._music_track_to_dict(mt) for mt in self.music_tracks],
            'progression_events': [self._progression_event_to_dict(pe) for pe in self.progression_events],
            'character_states': [self._character_state_to_dict(cs) for cs in self.character_states],
            'textures': [self._texture_to_dict(t) for t in self.textures],
            'models': [self._model_to_dict(m) for m in self.models],

            'metadata': self._normalize_metadata(self.metadata),
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
        self.locations = [self._dict_to_location(l) for l in data.get('locations', [])]
        self.environments = [self._dict_to_environment(e) for e in data.get('environments', [])]
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

        # Advanced entities
        self.lore_axioms = [self._dict_to_lore_axioms(la) for la in data.get('lore_axioms', [])]
        self.music_controls = [self._dict_to_music_control(mc) for mc in data.get('music_controls', [])]
        self.music_states = [self._dict_to_music_state(ms) for ms in data.get('music_states', [])]
        self.music_themes = [self._dict_to_music_theme(mt) for mt in data.get('music_themes', [])]
        self.music_tracks = [self._dict_to_music_track(mt) for mt in data.get('music_tracks', [])]
        self.progression_events = [self._dict_to_progression_event(pe) for pe in data.get('progression_events', [])]
        self.character_states = [self._dict_to_character_state(cs) for cs in data.get('character_states', [])]
        self.textures = [self._dict_to_texture(t) for t in data.get('textures', [])]
        self.models = [self._dict_to_model(m) for m in data.get('models', [])]

        self.metadata = self._normalize_metadata(data.get('metadata'))
        self._next_id = data.get('next_id', 1)
    
    @staticmethod
    def _world_to_dict(world: World):
        return _world_to_dict(world)

    @staticmethod
    def _dict_to_world(data: Dict):
        return _dict_to_world(data)

    @staticmethod
    def _character_to_dict(character: Character):
        return _character_to_dict(character)

    @staticmethod
    def _dict_to_character(data: Dict):
        return _dict_to_character(data)

    @staticmethod
    def _event_to_dict(event: Event):
        return _event_to_dict(event)

    @staticmethod
    def _dict_to_event(data: Dict):
        return _dict_to_event(data)

    @staticmethod
    def _improvement_to_dict(improvement: Improvement):
        return _improvement_to_dict(improvement)

    @staticmethod
    def _dict_to_improvement(data: Dict):
        return _dict_to_improvement(data)

    @staticmethod
    def _item_to_dict(item: Item):
        return _item_to_dict(item)

    @staticmethod
    def _dict_to_item(data: Dict):
        return _dict_to_item(data)

    @staticmethod
    def _quest_to_dict(quest: Quest):
        return _quest_to_dict(quest)

    @staticmethod
    def _dict_to_quest(data: Dict):
        return _dict_to_quest(data)

    @staticmethod
    def _storyline_to_dict(storyline: Storyline):
        return _storyline_to_dict(storyline)

    @staticmethod
    def _dict_to_storyline(data: Dict):
        return _dict_to_storyline(data)

    @staticmethod
    def _template_to_dict(template: Template):
        return _template_to_dict(template)

    @staticmethod
    def _dict_to_template(data: Dict):
        return _dict_to_template(data)

    @staticmethod
    def _page_to_dict(page: Page):
        return _page_to_dict(page)

    @staticmethod
    def _dict_to_page(data: Dict):
        return _dict_to_page(data)

    @staticmethod
    def _story_to_dict(story: Story):
        return _story_to_dict(story)

    @staticmethod
    def _dict_to_story(data: Dict):
        return _dict_to_story(data)

    @staticmethod
    def _tag_to_dict(tag: Tag):
        return _tag_to_dict(tag)

    @staticmethod
    def _dict_to_tag(data: Dict):
        return _dict_to_tag(data)

    @staticmethod
    def _image_to_dict(image: Image):
        return _image_to_dict(image)

    @staticmethod
    def _dict_to_image(data: Dict):
        return _dict_to_image(data)

    @staticmethod
    def _choice_to_dict(choice: Choice):
        return _choice_to_dict(choice)

    @staticmethod
    def _dict_to_choice(data: Dict):
        return _dict_to_choice(data)

    @staticmethod
    def _flowchart_to_dict(flowchart: Flowchart):
        return _flowchart_to_dict(flowchart)

    @staticmethod
    def _dict_to_flowchart(data: Dict):
        return _dict_to_flowchart(data)

    @staticmethod
    def _handout_to_dict(handout: Handout):
        return _handout_to_dict(handout)

    @staticmethod
    def _dict_to_handout(data: Dict):
        return _dict_to_handout(data)

    @staticmethod
    def _inspiration_to_dict(inspiration: Inspiration):
        return _inspiration_to_dict(inspiration)

    @staticmethod
    def _location_to_dict(location: Location):
        return _location_to_dict(location)

    @staticmethod
    def _dict_to_inspiration(data: Dict):
        return _dict_to_inspiration(data)

    @staticmethod
    def _dict_to_location(data: Dict):
        return _dict_to_location(data)

    @staticmethod
    def _environment_to_dict(environment: Environment):
        return _environment_to_dict(environment)

    @staticmethod
    def _dict_to_environment(data: Dict):
        return _dict_to_environment(data)

    @staticmethod
    def _banner_to_dict(banner: Banner):
        return _banner_to_dict(banner)

    @staticmethod
    def _dict_to_banner(data: Dict):
        return _dict_to_banner(data)

    @staticmethod
    def _character_relationship_to_dict(relationship: CharacterRelationship):
        return _character_relationship_to_dict(relationship)

    @staticmethod
    def _dict_to_character_relationship(data: Dict):
        return _dict_to_character_relationship(data)

    @staticmethod
    def _faction_to_dict(faction: Faction):
        return _faction_to_dict(faction)

    @staticmethod
    def _dict_to_faction(data: Dict):
        return _dict_to_faction(data)

    @staticmethod
    def _shop_to_dict(shop: Shop):
        return _shop_to_dict(shop)

    @staticmethod
    def _dict_to_shop(data: Dict):
        return _dict_to_shop(data)

    @staticmethod
    def _map_to_dict(map: Map):
        return _map_to_dict(map)

    @staticmethod
    def _dict_to_map(data: Dict):
        return _dict_to_map(data)

    @staticmethod
    def _note_to_dict(note: Note):
        return _note_to_dict(note)

    @staticmethod
    def _dict_to_note(data: Dict):
        return _dict_to_note(data)

    @staticmethod
    def _requirement_to_dict(requirement: Requirement):
        return _requirement_to_dict(requirement)

    @staticmethod
    def _dict_to_requirement(data: Dict):
        return _dict_to_requirement(data)

    @staticmethod
    def _session_to_dict(session: Session):
        return _session_to_dict(session)

    @staticmethod
    def _dict_to_session(data: Dict):
        return _dict_to_session(data)

    @staticmethod
    def _tokenboard_to_dict(tokenboard: Tokenboard):
        return _tokenboard_to_dict(tokenboard)

    @staticmethod
    def _dict_to_pity(data: Dict):
        return _dict_to_pity(data)

    @staticmethod
    def _dict_to_pull(data: Dict):
        return _dict_to_pull(data)

    @staticmethod
    def _dict_to_player_profile(data: Dict):
        return _dict_to_player_profile(data)

    @staticmethod
    def _dict_to_currency(data: Dict):
        return _dict_to_currency(data)

    @staticmethod
    def _dict_to_reward(data: Dict):
        return _dict_to_reward(data)

    @staticmethod
    def _dict_to_purchase(data: Dict):
        return _dict_to_purchase(data)

    @staticmethod
    def _dict_to_event_chain(data: Dict):
        return _dict_to_event_chain(data)

    @staticmethod
    def _dict_to_faction_membership(data: Dict):
        return _dict_to_faction_membership(data)

    @staticmethod
    def _dict_to_tokenboard(data: Dict):
        return _dict_to_tokenboard(data)

    @staticmethod
    def _pity_to_dict(pity: Pity):
        return _pity_to_dict(pity)

    @staticmethod
    def _pull_to_dict(pull: Pull):
        return _pull_to_dict(pull)

    @staticmethod
    def _player_profile_to_dict(profile: PlayerProfile):
        return _player_profile_to_dict(profile)

    @staticmethod
    def _currency_to_dict(currency: Currency):
        return _currency_to_dict(currency)

    @staticmethod
    def _reward_to_dict(reward: Reward):
        return _reward_to_dict(reward)

    @staticmethod
    def _purchase_to_dict(purchase: Purchase):
        return _purchase_to_dict(purchase)

    @staticmethod
    def _event_chain_to_dict(event_chain: EventChain):
        return _event_chain_to_dict(event_chain)

    @staticmethod
    def _faction_membership_to_dict(membership: FactionMembership):
        return _faction_membership_to_dict(membership)

    @staticmethod
    def _lore_axioms_to_dict(lore_axioms: LoreAxioms):
        return _lore_axioms_to_dict(lore_axioms)

    @staticmethod
    def _music_control_to_dict(music_control: MusicControl):
        return _music_control_to_dict(music_control)

    @staticmethod
    def _music_state_to_dict(music_state: MusicState):
        return _music_state_to_dict(music_state)

    @staticmethod
    def _progression_event_to_dict(progression_event: ProgressionEvent):
        return _progression_event_to_dict(progression_event)

    @staticmethod
    def _character_state_to_dict(character_state: CharacterState):
        return _character_state_to_dict(character_state)

    @staticmethod
    def _music_theme_to_dict(music_theme: MusicTheme):
        return _music_theme_to_dict(music_theme)

    @staticmethod
    def _music_track_to_dict(music_track: MusicTrack):
        return _music_track_to_dict(music_track)

    @staticmethod
    def _dict_to_lore_axioms(data: Dict):
        return _dict_to_lore_axioms(data)

    @staticmethod
    def _dict_to_music_control(data: Dict):
        return _dict_to_music_control(data)

    @staticmethod
    def _dict_to_music_state(data: Dict):
        return _dict_to_music_state(data)

    @staticmethod
    def _dict_to_progression_event(data: Dict):
        return _dict_to_progression_event(data)

    @staticmethod
    def _dict_to_character_state(data: Dict):
        return _dict_to_character_state(data)

    @staticmethod
    def _dict_to_music_theme(data: Dict):
        return _dict_to_music_theme(data)

    @staticmethod
    def _dict_to_music_track(data: Dict):
        return _dict_to_music_track(data)

    @staticmethod
    def _texture_to_dict(texture: Texture):
        return _texture_to_dict(texture)

    @staticmethod
    def _dict_to_texture(data: Dict):
        return _dict_to_texture(data)

    @staticmethod
    def _model_to_dict(model: Model3D):
        return _model_to_dict(model)

    @staticmethod
    def _dict_to_model(data: Dict):
        return _dict_to_model(data)

