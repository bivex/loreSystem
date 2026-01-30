"""Domain Entities - Objects with identity and lifecycle."""

# Campaign & Story
from .act import Act
from .alternate_reality import AlternateReality
from .branch_point import BranchPoint
from .campaign import Campaign
from .chapter import Chapter
from .consequence import Consequence
from .ending import Ending
from .epilogue import Epilogue
from .episode import Episode
from .moral_choice import MoralChoice
from .plot_branch import PlotBranch
from .prologue import Prologue

# Character Depth
from .character import Character, CharacterElement, CharacterRole
from .character_evolution import CharacterEvolution
from .character_profile_entry import CharacterProfileEntry
from .character_relationship import CharacterRelationship
from .character_variant import CharacterVariant
from .motion_capture import MotionCapture
from .voice_actor import VoiceActor

# Lore System
from .bestiary_entry import BestiaryEntry
from .codex_entry import CodexEntry
from .dream import Dream
from .journal_page import JournalPage
from .lore_fragment import LoreFragment
from .memory import Memory
from .nightmare import Nightmare

# Locations
from .dungeon import Dungeon
from .hub_area import HubArea
from .instance import Instance
from .location import Location
from .open_world_zone import OpenWorldZone
from .pocket_dimension import PocketDimension
from .raid import Raid
from .skybox import Skybox
from .underground import Underground

# Companions & Transport
from .airship import Airship
from .familiar import Familiar
from .mount import Mount
from .mount_equipment import MountEquipment
from .pet import Pet
from .portal import Portal
from .spaceship import Spaceship
from .teleporter import Teleporter
from .vehicle import Vehicle

# Quest Mechanics
from .quest_chain import QuestChain
from .quest_giver import QuestGiver
from .quest_node import QuestNode
from .quest_objective import QuestObjective
from .quest_prerequisite import QuestPrerequisite
from .quest_reward_tier import QuestRewardTier
from .quest_tracker import QuestTracker

# Skills & Development
from .attribute import Attribute
from .experience import Experience
from .level_up import LevelUp
from .mastery import Mastery
from .perk import Perk
from .skill import Skill
from .talent_tree import TalentTree
from .trait import Trait

# Existing entities (alphabetical)
from .alliance import Alliance
from .banner import Banner
from .calendar import Calendar
from .choice import Choice
from .constitution import Constitution
from .currency import Currency
from .dimension import Dimension
from .empire import Empire
from .era import Era
from .era_transition import EraTransition
from .event import Event
from .event_chain import EventChain
from .faction import Faction
from .faction_membership import FactionMembership
from .flowchart import Flowchart
from .government import Government
from .handout import Handout
from .holiday import Holiday
from .image import Image
from .improvement import Improvement
from .inspiration import Inspiration
from .item import Item
from .kingdom import Kingdom
from .law import Law
from .legal_system import LegalSystem
from .map import Map
from .model3d import Model3D
from .music_control import MusicControl
from .music_state import MusicState
from .music_theme import MusicTheme
from .music_track import MusicTrack
from .nation import Nation
from .note import Note
from .page import Page
from .pity import Pity
from .player_profile import PlayerProfile
from .pull import Pull
from .purchase import Purchase
from .quest import Quest
from .requirement import Requirement
from .reward import Reward
from .season import Season
from .session import Session
from .shop import Shop
from .story import Story
from .storyline import Storyline
from .tag import Tag
from .template import Template
from .texture import Texture
from .time_period import TimePeriod
from .timeline import Timeline
from .tokenboard import Tokenboard
from .treaty import Treaty
from .world import World

__all__ = [
    # Campaign & Story
    "Act",
    "AlternateReality",
    "BranchPoint",
    "Campaign",
    "Chapter",
    "Consequence",
    "Ending",
    "Epilogue",
    "Episode",
    "MoralChoice",
    "PlotBranch",
    "Prologue",

    # Character Depth
    "Character",
    "CharacterElement",
    "CharacterEvolution",
    "CharacterProfileEntry",
    "CharacterRelationship",
    "CharacterRole",
    "CharacterVariant",
    "MotionCapture",
    "VoiceActor",

    # Lore System
    "BestiaryEntry",
    "CodexEntry",
    "Dream",
    "JournalPage",
    "LoreFragment",
    "Memory",
    "Nightmare",

    # Locations
    "Dungeon",
    "HubArea",
    "Instance",
    "Location",
    "OpenWorldZone",
    "PocketDimension",
    "Raid",
    "Skybox",
    "Underground",

    # Companions & Transport
    "Airship",
    "Familiar",
    "Mount",
    "MountEquipment",
    "Pet",
    "Portal",
    "Spaceship",
    "Teleporter",
    "Vehicle",

    # Quest Mechanics
    "QuestChain",
    "QuestGiver",
    "QuestNode",
    "QuestObjective",
    "QuestPrerequisite",
    "QuestRewardTier",
    "QuestTracker",

    # Skills & Development
    "Attribute",
    "Experience",
    "LevelUp",
    "Mastery",
    "Perk",
    "Skill",
    "TalentTree",
    "Trait",

    # Existing entities
    "Alliance",
    "Banner",
    "Calendar",
    "Choice",
    "Constitution",
    "Currency",
    "Dimension",
    "Era",
    "EraTransition",
    "Empire",
    "Event",
    "EventChain",
    "Faction",
    "FactionMembership",
    "Flowchart",
    "Government",
    "Handout",
    "Holiday",
    "Image",
    "Improvement",
    "Inspiration",
    "Item",
    "Kingdom",
    "Law",
    "LegalSystem",
    "Map",
    "Model3D",
    "MusicControl",
    "MusicState",
    "MusicTheme",
    "MusicTrack",
    "Nation",
    "Note",
    "Page",
    "Pity",
    "PlayerProfile",
    "Pull",
    "Purchase",
    "Quest",
    "Requirement",
    "Reward",
    "Season",
    "Session",
    "Shop",
    "Story",
    "Storyline",
    "Tag",
    "Template",
    "Texture",
    "TimePeriod",
    "Timeline",
    "Tokenboard",
    "Treaty",
    "World",
]
