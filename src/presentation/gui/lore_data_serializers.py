"""Serialization helpers for :class:`LoreData`.

Extracted from ``lore_data.py``. These ~90 ``@staticmethod`` serializers
convert each lore entity to/from plain dicts for JSON persistence. They
are pure functions (no ``self`` references) and were the bulk of the
original ``LoreData`` class (1590 of 2229 lines).

``LoreData`` keeps thin ``@staticmethod`` delegates that forward to these
module-level functions, so existing ``self._X_to_dict(...)`` call sites in
``to_dict`` / ``from_dict`` continue to work unchanged.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from src.application.presentation_contracts import *  # noqa: F401,F403
from src.domain.value_objects.common import (
    Description,
    EntityId,
    TenantId,
    Timestamp,
    Version,
    WorldName,
)


def _world_to_dict(world: World) -> Dict:
    return {
        'id': world.id.value if world.id else None,
        'name': str(world.name),
        'description': str(world.description),
        'created_at': world.created_at.value.isoformat(),
        'updated_at': world.updated_at.value.isoformat(),
        'version': world.version.value
    }



def _dict_to_world(data: Dict) -> World:
    return World(
        id=EntityId(data['id']) if data['id'] else None,
        tenant_id=TenantId(1),
        name=WorldName(data['name']),
        description=Description(data['description']),
        parent_id=EntityId(data['parent_id']) if data.get('parent_id') else None,
        created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
        updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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



def _dict_to_event(data: Dict) -> Event:
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
        version=Version(data['version'])
    )



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



def _dict_to_improvement(data: Dict) -> Improvement:
    return Improvement(
        id=EntityId(data['id']) if data['id'] else None,
        tenant_id=TenantId(1),
        entity_type=EntityType(data['entity_type']),
        entity_id=EntityId(data['entity_id']),
        suggestion=data['suggestion'],
        status=ImprovementStatus(data['status']),
        git_commit_hash=GitCommitHash(data['git_commit_hash']),
        created_at=Timestamp(datetime.fromisoformat(data['created_at']))
    )



def _item_to_dict(item: Item) -> Dict:
    return {
        'id': item.id.value if item.id else None,
        'world_id': item.world_id.value,
        'name': item.name,
        'description': str(item.description),
        'item_type': item.item_type.value,
        'rarity': item.rarity.value if item.rarity else None,
        'model_3d_id': item.model_3d_id.value if item.model_3d_id else None,
        'texture_ids': [t.value for t in item.texture_ids] if item.texture_ids else [],
        'created_at': item.created_at.value.isoformat(),
        'updated_at': item.updated_at.value.isoformat(),
        'version': item.version.value
    }



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
        model_3d_id=EntityId(data['model_3d_id']) if data.get('model_3d_id') else None,
        texture_ids=[EntityId(t) for t in data.get('texture_ids', [])] or None,
        created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
        updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



def _dict_to_location(data: Dict) -> Location:
    return Location(
        id=EntityId(data['id']) if data['id'] else None,
        tenant_id=TenantId(1),
        world_id=EntityId(data['world_id']),
        name=data['name'],
        description=Description(data['description']),
        location_type=LocationType(data['location_type']),
        parent_location_id=EntityId(data['parent_location_id']) if data.get('parent_location_id') else None,
        created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
        updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
        version=Version(data['version'])
    )



def _environment_to_dict(environment: Environment) -> Dict:
    return {
        'id': environment.id.value if environment.id else None,
        'tenant_id': environment.tenant_id.value,
        'world_id': environment.world_id.value,
        'location_id': environment.location_id.value,
        'name': environment.name,
        'description': str(environment.description) if environment.description else None,
        'time_of_day': environment.time_of_day.value,
        'weather': environment.weather.value,
        'lighting': environment.lighting.value,
        'temperature': environment.temperature,
        'sounds': environment.sounds,
        'smells': environment.smells,
        'is_active': environment.is_active,
        'created_at': environment.created_at.value.isoformat(),
        'updated_at': environment.updated_at.value.isoformat(),
        'version': environment.version.value
    }



def _dict_to_environment(data: Dict) -> Environment:
    return Environment(
        id=EntityId(data['id']) if data['id'] else None,
        tenant_id=TenantId(data['tenant_id']),
        world_id=EntityId(data['world_id']),
        location_id=EntityId(data['location_id']),
        name=data['name'],
        description=Description(data['description']) if data.get('description') else None,
        time_of_day=TimeOfDay(data['time_of_day']),
        weather=Weather(data['weather']),
        lighting=Lighting(data['lighting']),
        temperature=data.get('temperature'),
        sounds=data.get('sounds'),
        smells=data.get('smells'),
        is_active=data.get('is_active', True),
        created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
        updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
        version=Version(data['version'])
    )



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



def _dict_to_banner(data: Dict) -> Banner:
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
        version=Version(data['version'])
    )



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



def _dict_to_character_relationship(data: Dict) -> CharacterRelationship:
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
        version=Version(data['version'])
    )



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



def _dict_to_faction(data: Dict) -> Faction:
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
        version=Version(data['version'])
    )



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



def _dict_to_shop(data: Dict) -> Shop:
    return Shop(
        id=EntityId(data['id']) if data['id'] else None,
        tenant_id=TenantId(1),
        name=data['name'],
        description=Description(data['description']),
        shop_type=ShopType(data.get('shop_type', data.get('type', 'general'))),
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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



def _requirement_to_dict(requirement: Requirement) -> Dict:
    return {
        'id': requirement.id.value if requirement.id else None,
        'entity_type': requirement.entity_type.value if requirement.entity_type else None,
        'entity_id': requirement.entity_id.value if requirement.entity_id else None,
        'description': requirement.description,
        'created_at': requirement.created_at.value.isoformat()
    }



def _dict_to_requirement(data: Dict) -> Requirement:
    return Requirement(
        id=EntityId(data['id']) if data['id'] else None,
        tenant_id=TenantId(1),
        entity_type=EntityType(data['entity_type']) if data.get('entity_type') else None,
        entity_id=EntityId(data['entity_id']) if data.get('entity_id') else None,
        description=data['description'],
        created_at=Timestamp(datetime.fromisoformat(data['created_at']))
    )



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
        'actual_duration_hours': session.actual_duration_hours,
        'notes': session.notes,
        'story_id': session.story_id.value if session.story_id else None,
        'created_at': session.created_at.value.isoformat(),
        'updated_at': session.updated_at.value.isoformat(),
        'version': session.version.value
    }



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
        actual_duration_hours=data.get('actual_duration_hours'),
        notes=data.get('notes', ''),
        created_at=Timestamp(datetime.fromisoformat(data['created_at'])),
        updated_at=Timestamp(datetime.fromisoformat(data['updated_at'])),
        version=Version(data['version']),
        story_id=EntityId(data['story_id']) if data.get('story_id') else None,
        skip_temporal_validation=True,
    )



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
        version=Version(data['version'])
    )



def _dict_to_pull(data: Dict) -> Pull:
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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )



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
        version=Version(data['version'])
    )


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



def _lore_axioms_to_dict(lore_axioms: LoreAxioms) -> Dict:
    return {
        'id': lore_axioms.id.value if lore_axioms.id else None,
        'tenant_id': lore_axioms.tenant_id.value,
        'world_id': lore_axioms.world_id.value,
        'axioms': [{
            'axiom_type': axiom.axiom_type.value,
            'predicate': axiom.predicate,
            'parameters': axiom.parameters,
            'description': axiom.description
        } for axiom in lore_axioms.axioms],
        'created_at': lore_axioms.created_at.value.isoformat(),
        'updated_at': lore_axioms.updated_at.value.isoformat(),
        'version': lore_axioms.version.value
    }



def _music_control_to_dict(music_control: MusicControl) -> Dict:
    return {
        'id': music_control.id.value if music_control.id else None,
        'tenant_id': music_control.tenant_id.value,
        'world_id': music_control.world_id.value,
        'name': music_control.name,
        'description': music_control.description.value,
        'lore_state': music_control.lore_state,
        'narrative_phase': music_control.narrative_phase.value if music_control.narrative_phase else None,
        'emotional_tone': music_control.emotional_tone.value if music_control.emotional_tone else None,
        'player_context': music_control.player_context.value if music_control.player_context else None,
        'trigger_conditions': music_control.trigger_conditions,
        'priority': music_control.priority
    }



def _music_state_to_dict(music_state: MusicState) -> Dict:
    return {
        'id': music_state.id.value if music_state.id else None,
        'tenant_id': music_state.tenant_id.value,
        'world_id': music_state.world_id.value,
        'name': music_state.name,
        'description': music_state.description.value,
        'is_silence_moment': music_state.is_silence_moment,
        'default_track_id': music_state.default_track_id.value if music_state.default_track_id else None,
        'crossfade_duration_seconds': music_state.crossfade_duration_seconds,
        'allow_interrupts': music_state.allow_interrupts,
        'priority': music_state.priority,
        'can_transition_to': music_state.can_transition_to
    }



def _progression_event_to_dict(progression_event: ProgressionEvent) -> Dict:
    return {
        'id': progression_event.id,
        'tenant_id': progression_event.tenant_id.value,
        'world_id': progression_event.world_id.value,
        'character_id': progression_event.character_id.value,
        'event_type': progression_event.event_type.value,
        'from_time': progression_event.from_time,
        'to_time': progression_event.to_time,
        'description': progression_event.description,
        'created_at': progression_event.created_at.value.isoformat(),
        'reasons': [{'rule_reference': str(r)} for r in progression_event.reasons],
        'effects': progression_event.effects
    }



def _character_state_to_dict(character_state: CharacterState) -> Dict:
    return {
        'character_id': character_state.character_id.value,
        'time_point': character_state.time_point,
        'created_at': character_state.created_at.value.isoformat(),
        'level': character_state.level,
        'character_class': character_state.character_class,
        'experience': character_state.experience,
        'stats': {k.value: v for k, v in character_state.stats.items()}
    }



def _music_theme_to_dict(music_theme: MusicTheme) -> Dict:
    return {
        'id': music_theme.id.value if music_theme.id else None,
        'tenant_id': music_theme.tenant_id.value,
        'world_id': music_theme.world_id.value,
        'name': music_theme.name,
        'description': music_theme.description.value,
        'theme_type': music_theme.theme_type.value,
        'file_path': music_theme.file_path,
        'duration_seconds': music_theme.duration_seconds,
        'composer': music_theme.composer,
        'character_id': music_theme.character_id.value if music_theme.character_id else None,
        'location_id': music_theme.location_id.value if music_theme.location_id else None,
        'faction_id': music_theme.faction_id.value if music_theme.faction_id else None,
        'era_id': music_theme.era_id.value if music_theme.era_id else None,
        'created_at': music_theme.created_at.value.isoformat(),
        'updated_at': music_theme.updated_at.value.isoformat(),
        'version': music_theme.version.value
    }



def _music_track_to_dict(music_track: MusicTrack) -> Dict:
    return {
        'id': music_track.id.value if music_track.id else None,
        'tenant_id': music_track.tenant_id.value,
        'world_id': music_track.world_id.value,
        'name': music_track.name,
        'description': music_track.description.value,
        'system_type': music_track.system_type.value,
        'file_path': music_track.file_path,
        'duration_seconds': music_track.duration_seconds,
        'intensity_level': music_track.intensity_level,
        'is_loopable': music_track.is_loopable,
        'loop_start_time': music_track.loop_start_time,
        'loop_end_time': music_track.loop_end_time,
        'music_theme_id': music_track.music_theme_id.value if music_track.music_theme_id else None,
        'created_at': music_track.created_at.value.isoformat(),
        'updated_at': music_track.updated_at.value.isoformat(),
        'version': music_track.version.value
    }



def _dict_to_lore_axioms(data: Dict) -> LoreAxioms:
    return LoreAxioms(
        id=EntityId(data['id']) if data.get('id') else None,
        tenant_id=TenantId(data['tenant_id']),
        world_id=EntityId(data['world_id']),
        axioms=[LoreAxiom(
            axiom_type=AxiomType(axiom['axiom_type']),
            predicate=axiom['predicate'],
            parameters=axiom['parameters'],
            description=axiom['description']
        ) for axiom in data.get('axioms', [])],
        created_at=Timestamp.fromisoformat(data['created_at']),
        updated_at=Timestamp.fromisoformat(data['updated_at']),
        version=Version(data['version'])
    )



def _dict_to_music_control(data: Dict) -> MusicControl:
    return MusicControl(
        id=EntityId(data['id']) if data.get('id') else None,
        tenant_id=TenantId(data['tenant_id']),
        world_id=EntityId(data['world_id']),
        name=data['name'],
        description=Description(data['description']),
        lore_state=data.get('lore_state'),
        narrative_phase=NarrativePhase(data['narrative_phase']) if data.get('narrative_phase') else None,
        emotional_tone=EmotionalTone(data['emotional_tone']) if data.get('emotional_tone') else None,
        player_context=PlayerContext(data['player_context']) if data.get('player_context') else None,
        trigger_conditions=data.get('trigger_conditions'),
        priority=data['priority']
    )



def _dict_to_music_state(data: Dict) -> MusicState:
    return MusicState(
        id=EntityId(data['id']) if data.get('id') else None,
        tenant_id=TenantId(data['tenant_id']),
        world_id=EntityId(data['world_id']),
        name=data['name'],
        description=Description(data['description']),
        is_silence_moment=data['is_silence_moment'],
        default_track_id=EntityId(data['default_track_id']) if data.get('default_track_id') else None,
        crossfade_duration_seconds=data['crossfade_duration_seconds'],
        allow_interrupts=data['allow_interrupts'],
        priority=data['priority'],
        can_transition_to=data.get('can_transition_to')
    )



def _dict_to_progression_event(data: Dict) -> ProgressionEvent:
    return ProgressionEvent(
        id=data['id'],
        tenant_id=TenantId(data['tenant_id']),
        world_id=EntityId(data['world_id']),
        character_id=EntityId(data['character_id']),
        event_type=EventType(data['event_type']),
        from_time=data['from_time'],
        to_time=data['to_time'],
        description=data['description'],
        created_at=Timestamp.fromisoformat(data['created_at']),
        reasons=[RuleReference(r['rule_reference']) for r in data.get('reasons', [])],
        effects=data.get('effects', {})
    )



def _dict_to_character_state(data: Dict) -> CharacterState:
    return CharacterState(
        character_id=EntityId(data['character_id']),
        time_point=data['time_point'],
        created_at=Timestamp.fromisoformat(data['created_at']),
        level=CharacterLevel(data['level']) if data.get('level') else None,
        character_class=CharacterClass(data['character_class']) if data.get('character_class') else None,
        experience=ExperiencePoints(data['experience']) if data.get('experience') else None,
        stats={StatType(k): StatValue(v) for k, v in data.get('stats', {}).items()}
    )



def _dict_to_music_theme(data: Dict) -> MusicTheme:
    return MusicTheme(
        id=EntityId(data['id']) if data.get('id') else None,
        tenant_id=TenantId(data['tenant_id']),
        world_id=EntityId(data['world_id']),
        name=data['name'],
        description=Description(data['description']),
        theme_type=MusicThemeType(data['theme_type']),
        file_path=data.get('file_path'),
        duration_seconds=data.get('duration_seconds'),
        composer=data.get('composer'),
        character_id=EntityId(data['character_id']) if data.get('character_id') else None,
        location_id=EntityId(data['location_id']) if data.get('location_id') else None,
        faction_id=EntityId(data['faction_id']) if data.get('faction_id') else None,
        era_id=EntityId(data['era_id']) if data.get('era_id') else None,
        created_at=Timestamp.fromisoformat(data['created_at']),
        updated_at=Timestamp.fromisoformat(data['updated_at']),
        version=Version(data['version'])
    )



def _dict_to_music_track(data: Dict) -> MusicTrack:
    return MusicTrack(
        id=EntityId(data['id']) if data.get('id') else None,
        tenant_id=TenantId(data['tenant_id']),
        world_id=EntityId(data['world_id']),
        name=data['name'],
        description=Description(data['description']),
        system_type=MusicSystemType(data['system_type']),
        file_path=data.get('file_path'),
        duration_seconds=data.get('duration_seconds'),
        intensity_level=data.get('intensity_level'),
        is_loopable=data['is_loopable'],
        loop_start_time=data.get('loop_start_time'),
        loop_end_time=data.get('loop_end_time'),
        music_theme_id=EntityId(data['music_theme_id']) if data.get('music_theme_id') else None,
        created_at=Timestamp.fromisoformat(data['created_at']),
        updated_at=Timestamp.fromisoformat(data['updated_at']),
        version=Version(data['version'])
    )



def _texture_to_dict(texture: Texture) -> Dict:
    return {
        'id': texture.id.value if texture.id else None,
        'tenant_id': texture.tenant_id.value,
        'world_id': texture.world_id.value,
        'name': texture.name,
        'path': texture.path,
        'texture_type': texture.texture_type,
        'description': texture.description,
        'file_size': texture.file_size,
        'dimensions': texture.dimensions,
        'color_space': texture.color_space,
        'created_at': texture.created_at.value.isoformat(),
        'updated_at': texture.updated_at.value.isoformat(),
        'version': texture.version.value
    }



def _dict_to_texture(data: Dict) -> Texture:
    return Texture(
        id=EntityId(data['id']) if data.get('id') else None,
        tenant_id=TenantId(data['tenant_id']),
        world_id=EntityId(data['world_id']),
        name=data['name'],
        path=data['path'],
        texture_type=data['texture_type'],
        description=data.get('description'),
        file_size=data['file_size'],
        dimensions=data.get('dimensions'),
        color_space=data.get('color_space', 'sRGB'),
        created_at=Timestamp.fromisoformat(data['created_at']),
        updated_at=Timestamp.fromisoformat(data['updated_at']),
        version=Version(data['version'])
    )



def _model_to_dict(model: Model3D) -> Dict:
    return {
        'id': model.id.value if model.id else None,
        'tenant_id': model.tenant_id.value,
        'world_id': model.world_id.value,
        'name': model.name,
        'path': model.path,
        'model_type': model.model_type,
        'description': model.description,
        'file_size': model.file_size,
        'poly_count': model.poly_count,
        'dimensions': model.dimensions,
        'textures': [tid.value for tid in model.textures] if model.textures else [],
        'animations': model.animations,
        'created_at': model.created_at.value.isoformat(),
        'updated_at': model.updated_at.value.isoformat(),
        'version': model.version.value
    }



def _dict_to_model(data: Dict) -> Model3D:
    return Model3D(
        id=EntityId(data['id']) if data.get('id') else None,
        tenant_id=TenantId(data['tenant_id']),
        world_id=EntityId(data['world_id']),
        name=data['name'],
        path=data['path'],
        model_type=data['model_type'],
        description=data.get('description'),
        file_size=data['file_size'],
        poly_count=data.get('poly_count'),
        dimensions=data.get('dimensions'),
        textures=[EntityId(tid) for tid in data.get('textures', [])],
        animations=data.get('animations', []),
        created_at=Timestamp.fromisoformat(data['created_at']),
        updated_at=Timestamp.fromisoformat(data['updated_at']),
        version=Version(data['version'])
    )
