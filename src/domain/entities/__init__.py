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

# Inventory & Crafting
from .blueprint import Blueprint
from .component import Component
from .crafting_recipe import CraftingRecipe
from .enchantment import Enchantment
from .glyph import Glyph
from .inventory import Inventory
from .material import Material
from .rune import Rune
from .socket import Socket

# History & Time
from .alliance import Alliance
from .calendar import Calendar
from .constitution import Constitution
from .empire import Empire
from .era import Era
from .era_transition import EraTransition
from .government import Government
from .holiday import Holiday
from .kingdom import Kingdom
from .law import Law
from .legal_system import LegalSystem
from .nation import Nation
from .season import Season
from .time_period import TimePeriod
from .timeline import Timeline
from .treaty import Treaty
from .world import World

# Social Systems
from .affinity import Affinity
from .disposition import Disposition
from .honor import Honor
from .karma import Karma
from .reputation import Reputation
from .social_class import SocialClass
from .social_mobility import SocialMobility

# Faction Depth
from .faction_hierarchy import FactionHierarchy
from .faction_ideology import FactionIdeology
from .faction_leader import FactionLeader
from .faction_resource import FactionResource
from .faction_territory import FactionTerritory

# Religion & Mysticism
from .blessing import Blessing
from .cult import Cult
from .curse import Curse
from .holy_site import HolySite
from .oath import Oath
from .pact import Pact
from .ritual import Ritual
from .scripture import Scripture
from .sect import Sect
from .summon import Summon

# Existing entities (alphabetical)
from .banner import Banner
from .choice import Choice
from .currency import Currency
from .dimension import Dimension
from .event import Event
from .event_chain import EventChain
from .faction import Faction
from .faction_membership import FactionMembership
from .flowchart import Flowchart
from .handout import Handout
from .image import Image
from .improvement import Improvement
from .inspiration import Inspiration
from .item import Item
from .map import Map
from .model3d import Model3D
from .music_control import MusicControl
from .music_state import MusicState
from .music_theme import MusicTheme
from .music_track import MusicTrack
from .note import Note
from .page import Page
from .pity import Pity
from .player_profile import PlayerProfile
from .pull import Pull
from .purchase import Purchase
from .quest import Quest
from .requirement import Requirement
from .reward import Reward
from .session import Session
from .shop import Shop
from .story import Story
from .storyline import Storyline
from .tag import Tag
from .template import Template
from .texture import Texture
from .tokenboard import Tokenboard

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

    # Inventory & Crafting
    "Blueprint",
    "Component",
    "CraftingRecipe",
    "Enchantment",
    "Glyph",
    "Inventory",
    "Material",
    "Rune",
    "Socket",

    # History & Time
    "Alliance",
    "Calendar",
    "Constitution",
    "Empire",
    "Era",
    "EraTransition",
    "Government",
    "Holiday",
    "Kingdom",
    "Law",
    "LegalSystem",
    "Nation",
    "TimePeriod",
    "Timeline",
    "Treaty",
    "World",

    # Social Systems
    "Affinity",
    "Disposition",
    "Honor",
    "Karma",
    "Reputation",
    "SocialClass",
    "SocialMobility",

    # Faction Depth
    "FactionHierarchy",
    "FactionIdeology",
    "FactionLeader",
    "FactionResource",
    "FactionTerritory",

    # Religion & Mysticism
    "Blessing",
    "Cult",
    "Curse",
    "HolySite",
    "Oath",
    "Pact",
    "Ritual",
    "Scripture",
    "Sect",
    "Summon",

    # Existing entities
    "Banner",
    "Choice",
    "Currency",
    "Dimension",
    "Event",
    "EventChain",
    "Faction",
    "FactionMembership",
    "Flowchart",
    "Handout",
    "Image",
    "Improvement",
    "Inspiration",
    "Item",
    "Map",
    "Model3D",
    "MusicControl",
    "MusicState",
    "MusicTheme",
    "MusicTrack",
    "Note",
    "Page",
    "Pity",
    "PlayerProfile",
    "Pull",
    "Purchase",
    "Quest",
    "Requirement",
    "Reward",
    "Session",
    "Shop",
    "Story",
    "Storyline",
    "Tag",
    "Template",
    "Texture",
    "Tokenboard",
]
