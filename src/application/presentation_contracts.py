"""Presentation-facing application contracts.

This module exposes application-owned proxy types for domain entities and value
objects. Presentation code imports these application symbols, while the proxy
implementation delegates construction and class-level attribute access to the
real domain types behind the scenes.
"""

from src.domain.entities.banner import Banner as _Banner, BannerType as _BannerType
from src.domain.entities.character import Character as _Character
from src.domain.entities.character_relationship import (
    CharacterRelationship as _CharacterRelationship,
    RelationshipType as _RelationshipType,
)
from src.domain.entities.choice import Choice as _Choice
from src.domain.entities.currency import Currency as _Currency
from src.domain.entities.environment import Environment as _Environment
from src.domain.entities.event import Event as _Event
from src.domain.entities.event_chain import EventChain as _EventChain
from src.domain.entities.faction import (
    Faction as _Faction,
    FactionAlignment as _FactionAlignment,
    FactionType as _FactionType,
)
from src.domain.entities.faction_membership import FactionMembership as _FactionMembership
from src.domain.entities.flowchart import Flowchart as _Flowchart
from src.domain.entities.handout import Handout as _Handout
from src.domain.entities.image import Image as _Image
from src.domain.entities.improvement import Improvement as _Improvement
from src.domain.entities.inspiration import Inspiration as _Inspiration
from src.domain.entities.item import Item as _Item
from src.domain.entities.location import Location as _Location
from src.domain.entities.lore_axioms import (
    AxiomType as _AxiomType,
    LoreAxiom as _LoreAxiom,
    LoreAxioms as _LoreAxioms,
)
from src.domain.entities.map import Map as _Map
from src.domain.entities.model3d import Model3D as _Model3D
from src.domain.entities.music_control import MusicControl as _MusicControl
from src.domain.entities.music_state import MusicState as _MusicState
from src.domain.entities.music_theme import MusicTheme as _MusicTheme
from src.domain.entities.music_track import MusicTrack as _MusicTrack
from src.domain.entities.note import Note as _Note
from src.domain.entities.page import Page as _Page
from src.domain.entities.pity import Pity as _Pity
from src.domain.entities.player_profile import PlayerProfile as _PlayerProfile
from src.domain.entities.progression_event import ProgressionEvent as _ProgressionEvent
from src.domain.entities.progression_state import CharacterState as _CharacterState
from src.domain.entities.pull import Pull as _Pull, PullResult as _PullResult
from src.domain.entities.purchase import Purchase as _Purchase
from src.domain.entities.quest import Quest as _Quest
from src.domain.entities.requirement import Requirement as _Requirement
from src.domain.entities.reward import Reward as _Reward
from src.domain.entities.session import Session as _Session
from src.domain.entities.shop import Shop as _Shop, ShopType as _ShopType
from src.domain.entities.story import Story as _Story
from src.domain.entities.storyline import Storyline as _Storyline
from src.domain.entities.tag import Tag as _Tag
from src.domain.entities.template import Template as _Template
from src.domain.entities.texture import Texture as _Texture
from src.domain.entities.tokenboard import Tokenboard as _Tokenboard
from src.domain.entities.world import World as _World
from src.domain.exceptions import DomainException
from src.domain.value_objects.ability import (
    Ability as _Ability,
    AbilityName as _AbilityName,
    PowerLevel as _PowerLevel,
)
from src.domain.value_objects.common import (
    Backstory as _Backstory,
    CharacterName as _CharacterName,
    CharacterStatus as _CharacterStatus,
    ChoiceType as _ChoiceType,
    Content as _Content,
    DateRange as _DateRange,
    Description as _Description,
    EmotionalTone as _EmotionalTone,
    EntityId as _EntityId,
    EntityType as _EntityType,
    EventOutcome as _EventOutcome,
    FlowchartName as _FlowchartName,
    GitCommitHash as _GitCommitHash,
    HandoutName as _HandoutName,
    ImagePath as _ImagePath,
    ImageType as _ImageType,
    ImprovementStatus as _ImprovementStatus,
    InspirationName as _InspirationName,
    ItemType as _ItemType,
    Lighting as _Lighting,
    LocationType as _LocationType,
    MapName as _MapName,
    MusicSystemType as _MusicSystemType,
    MusicThemeType as _MusicThemeType,
    NarrativePhase as _NarrativePhase,
    NoteTitle as _NoteTitle,
    NoteType as _NoteType,
    PageName as _PageName,
    PlayerContext as _PlayerContext,
    QuestStatus as _QuestStatus,
    Rarity as _Rarity,
    SessionName as _SessionName,
    SessionStatus as _SessionStatus,
    StoryName as _StoryName,
    StoryType as _StoryType,
    StorylineType as _StorylineType,
    TagName as _TagName,
    TagType as _TagType,
    TemplateName as _TemplateName,
    TemplateType as _TemplateType,
    TenantId as _TenantId,
    TimeOfDay as _TimeOfDay,
    Timestamp as _Timestamp,
    TokenboardName as _TokenboardName,
    Version as _Version,
    Weather as _Weather,
    WorldName as _WorldName,
)
from src.domain.value_objects.progression import (
    CharacterClass as _CharacterClass,
    CharacterLevel as _CharacterLevel,
    EventType as _EventType,
    ExperiencePoints as _ExperiencePoints,
    RuleReference as _RuleReference,
    StatType as _StatType,
    StatValue as _StatValue,
)


class _ProxyMeta(type):
    """Metaclass that makes application proxy classes behave like their targets."""

    _target = None

    def __call__(cls, *args, **kwargs):
        return cls._target(*args, **kwargs)

    def __getattr__(cls, item):
        return getattr(cls._target, item)

    def __iter__(cls):
        return iter(cls._target)

    def __instancecheck__(cls, instance):
        return isinstance(instance, cls._target)

    def __subclasscheck__(cls, subclass):
        return issubclass(subclass, cls._target)


def _make_proxy(name, target):
    return _ProxyMeta(name, (), {"_target": target, "__module__": __name__})


_TARGETS = {
    "Ability": _Ability,
    "AbilityName": _AbilityName,
    "AxiomType": _AxiomType,
    "Backstory": _Backstory,
    "Banner": _Banner,
    "BannerType": _BannerType,
    "Character": _Character,
    "CharacterClass": _CharacterClass,
    "CharacterLevel": _CharacterLevel,
    "CharacterName": _CharacterName,
    "CharacterRelationship": _CharacterRelationship,
    "CharacterState": _CharacterState,
    "CharacterStatus": _CharacterStatus,
    "Choice": _Choice,
    "ChoiceType": _ChoiceType,
    "Content": _Content,
    "Currency": _Currency,
    "DateRange": _DateRange,
    "Description": _Description,
    "EmotionalTone": _EmotionalTone,
    "EntityId": _EntityId,
    "EntityType": _EntityType,
    "Environment": _Environment,
    "Event": _Event,
    "EventChain": _EventChain,
    "EventOutcome": _EventOutcome,
    "EventType": _EventType,
    "ExperiencePoints": _ExperiencePoints,
    "Faction": _Faction,
    "FactionAlignment": _FactionAlignment,
    "FactionMembership": _FactionMembership,
    "FactionType": _FactionType,
    "Flowchart": _Flowchart,
    "FlowchartName": _FlowchartName,
    "GitCommitHash": _GitCommitHash,
    "Handout": _Handout,
    "HandoutName": _HandoutName,
    "Image": _Image,
    "ImagePath": _ImagePath,
    "ImageType": _ImageType,
    "Improvement": _Improvement,
    "ImprovementStatus": _ImprovementStatus,
    "Inspiration": _Inspiration,
    "InspirationName": _InspirationName,
    "Item": _Item,
    "ItemType": _ItemType,
    "Lighting": _Lighting,
    "Location": _Location,
    "LocationType": _LocationType,
    "LoreAxiom": _LoreAxiom,
    "LoreAxioms": _LoreAxioms,
    "Map": _Map,
    "MapName": _MapName,
    "Model3D": _Model3D,
    "MusicControl": _MusicControl,
    "MusicSystemType": _MusicSystemType,
    "MusicState": _MusicState,
    "MusicTheme": _MusicTheme,
    "MusicThemeType": _MusicThemeType,
    "MusicTrack": _MusicTrack,
    "NarrativePhase": _NarrativePhase,
    "Note": _Note,
    "NoteTitle": _NoteTitle,
    "NoteType": _NoteType,
    "Page": _Page,
    "PageName": _PageName,
    "Pity": _Pity,
    "PlayerContext": _PlayerContext,
    "PlayerProfile": _PlayerProfile,
    "PowerLevel": _PowerLevel,
    "ProgressionEvent": _ProgressionEvent,
    "Pull": _Pull,
    "PullResult": _PullResult,
    "Purchase": _Purchase,
    "Quest": _Quest,
    "QuestStatus": _QuestStatus,
    "Rarity": _Rarity,
    "RelationshipType": _RelationshipType,
    "Requirement": _Requirement,
    "Reward": _Reward,
    "RuleReference": _RuleReference,
    "Session": _Session,
    "SessionName": _SessionName,
    "SessionStatus": _SessionStatus,
    "Shop": _Shop,
    "ShopType": _ShopType,
    "StatType": _StatType,
    "StatValue": _StatValue,
    "Story": _Story,
    "StoryName": _StoryName,
    "StoryType": _StoryType,
    "Storyline": _Storyline,
    "StorylineType": _StorylineType,
    "Tag": _Tag,
    "TagName": _TagName,
    "TagType": _TagType,
    "Template": _Template,
    "TemplateName": _TemplateName,
    "TemplateType": _TemplateType,
    "TenantId": _TenantId,
    "Texture": _Texture,
    "TimeOfDay": _TimeOfDay,
    "Timestamp": _Timestamp,
    "Tokenboard": _Tokenboard,
    "TokenboardName": _TokenboardName,
    "Version": _Version,
    "Weather": _Weather,
    "World": _World,
    "WorldName": _WorldName,
}

globals().update({name: _make_proxy(name, target) for name, target in _TARGETS.items()})

__all__ = sorted([*list(_TARGETS.keys()), "DomainException"])