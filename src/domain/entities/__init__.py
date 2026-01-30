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

# Legendary Items
from .artifact_set import ArtifactSet
from .cursed_item import CursedItem
from .divine_item import DivineItem
from .legendary_weapon import LegendaryWeapon
from .mythical_armor import MythicalArmor
from .relic_collection import RelicCollection

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

# Economy
from .barter import Barter
from .demand import Demand
from .inflation import Inflation
from .price import Price
from .supply import Supply
from .tariff import Tariff
from .tax import Tax
from .trade import Trade

# Military Systems
from .army import Army
from .battalion import Battalion
from .defense import Defense
from .fleet import Fleet
from .fortification import Fortification
from .siege_engine import SiegeEngine
from .weapon_system import WeaponSystem

# Art & Culture
from .tournament import Tournament

# Weather & Climate
from .weather_pattern import WeatherPattern
from .cataclysm import Cataclysm
from .disaster import Disaster
from .miracle import Miracle
from .phenomenon import Phenomenon

# Legal System
from .witness import Witness
from .court import Court
from .crime import Crime
from .judge import Judge
from .jury import Jury
from .lawyer import Lawyer
from .punishment import Punishment
from .evidence import Evidence

# Art & Culture
from .tournament import Tournament
from .festival import Festival
from .celebration import Celebration
from .ceremony import Ceremony
from .concert import Concert
from .exhibition import Exhibition
from .competition import Competition

# Architecture Detail
from .district import District
from .market_square import MarketSquare
from .noble_district import NobleDistrict
from .plaza import Plaza
from .port_district import PortDistrict
from .quarter import Quarter
from .slums import Slums
from .ward import Ward

# Biology & Ecology
from .evolution import Evolution
from .extinction import Extinction
from .food_chain import FoodChain
from .hibernation import Hibernation
from .migration import Migration
from .reproduction import Reproduction

# Astronomy
from .black_hole import BlackHole
from .eclipse import Eclipse
from .galaxy import Galaxy
from .moon import Moon
from .nebula import Nebula
from .solstice import Solstice
from .star_system import StarSystem
from .wormhole import Wormhole

# Technology
from .atmosphere import Atmosphere
from .discovery import Discovery
from .invention import Invention
from .patent import Patent
from .prototype import Prototype
from .research import Research

# Education
from .academy import Academy
from .archive import Archive
from .library import Library
from .school import School
from .university import University

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

# Music & Audio
from .soundtrack import Soundtrack, SoundtrackType, Mood
from .voice_line import VoiceLine, VoiceLineType, Emotion
from .sound_effect import SoundEffect, SoundEffectType, Priority
from .ambient import Ambient, AmbientType, LayerType
from .silence import Silence, SilencePurpose, FadeStyle
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

# Visual Effects
from .visual_effect import VisualEffect
from .particle import Particle
from .shader import Shader
from .lighting import Lighting
from .color_palette import ColorPalette

# Gameplay Mechanics (Lore)
from .fast_travel_point import FastTravelPoint
from .waypoint import Waypoint
from .save_point import SavePoint
from .checkpoint import Checkpoint
from .autosave import Autosave
from .spawn_point import SpawnPoint

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

    # Legendary Items
    "ArtifactSet",
    "CursedItem",
    "DivineItem",
    "LegendaryWeapon",
    "MythicalArmor",
    "RelicCollection",

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

    # Economy
    "Barter",
    "Demand",
    "Inflation",
    "Price",
    "Supply",
    "Tariff",
    "Tax",
    "Trade",

    # Military Systems
    "Army",
    "Battalion",
    "Defense",
    "Fleet",
    "Fortification",
    "SiegeEngine",
    "WeaponSystem",

    # Art & Culture
    "Tournament",

    # Weather & Climate
    "WeatherPattern",

    # Legal System
    "Witness",

    # Architecture Detail
    "District",
    "MarketSquare",
    "NobleDistrict",
    "Plaza",
    "PortDistrict",
    "Quarter",
    "Slums",
    "Ward",

    # Biology & Ecology
    "Evolution",
    "Extinction",
    "FoodChain",
    "Hibernation",
    "Migration",
    "Reproduction",

    # Astronomy
    "BlackHole",
    "Eclipse",
    "Galaxy",
    "Moon",
    "Nebula",
    "Solstice",
    "StarSystem",
    "Wormhole",

    # Technology
    "Atmosphere",
    "Discovery",
    "Invention",
    "Patent",
    "Prototype",
    "Research",

    # Education
    "Academy",
    "Archive",
    "Library",
    "School",
    "University",

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

    # Music & Audio
    "Soundtrack",
    "SoundtrackType",
    "Mood",
    "VoiceLine",
    "VoiceLineType",
    "Emotion",
    "SoundEffect",
    "SoundEffectType",
    "Priority",
    "Ambient",
    "AmbientType",
    "LayerType",
    "Silence",
    "SilencePurpose",
    "FadeStyle",
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

    # Visual Effects
    "VisualEffect",
    "Particle",
    "Shader",
    "Lighting",
    "ColorPalette",

    # Gameplay Mechanics (Lore)
    "FastTravelPoint",
    "Waypoint",
    "SavePoint",
    "Checkpoint",
    "Autosave",
    "SpawnPoint",
]
