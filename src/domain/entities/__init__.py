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

# Art & Culture
from .celebration import Celebration
from .ceremony import Ceremony
from .concert import Concert
from .competition import Competition
from .exhibition import Exhibition
from .festival import Festival
from .tournament import Tournament
from .weather_pattern import WeatherPattern

# Legal System
from .court import Court
from .crime import Crime
from .evidence import Evidence
from .judge import Judge
from .jury import Jury
from .lawyer import Lawyer
from .punishment import Punishment
from .witness import Witness

# Education
from .academy import Academy
from .archive import Archive
from .library import Library
from .museum import Museum
from .research_center import ResearchCenter
from .school import School
from .university import University

# Media
from .internet import Internet
from .newspaper import Newspaper
from .propaganda import Propaganda
from .radio import Radio
from .social_media import SocialMedia
from .rumor import Rumor
from .television import Television

# Secrets
from .easter_egg import EasterEgg
from .enigma import Enigma
from .hidden_path import HiddenPath
from .mystery import Mystery
from .puzzle import Puzzle
from .riddle import Riddle
from .secret_area import SecretArea
from .trap import Trap

# Legendary Items
from .artifact_set import ArtifactSet
from .cursed_item import CursedItem
from .divine_item import DivineItem
from .legendary_weapon import LegendaryWeapon
from .mythical_armor import MythicalArmor
from .relic_collection import RelicCollection

# Music & Audio
from .ambient import Ambient
from .motif import Motif
from .score import Score
from .silence import Silence
from .sound_effect import SoundEffect
from .soundtrack import Soundtrack
from .theme import Theme
from .voice_line import VoiceLine

# Visual Effects
from .color_palette import ColorPalette
from .lighting import Lighting
from .particle import Particle
from .shader import Shader
from .visual_effect import VisualEffect

# Cinematography
from .camera_path import CameraPath
from .cinematic import Cinematic
from .cutscene import Cutscene
from .fade import Fade
from .flashback import Flashback
from .transition import Transition

# Narrative Devices
from .chekhovs_gun import ChekhovsGun
from .deus_ex_machina import DeusExMachina
from .flashforward import FlashForward
from .foreshadowing import Foreshadowing
from .plot_device import PlotDevice
from .redherring import RedHerring

# Global Events
from .famine import Famine
from .invasion import Invasion
from .plague import Plague
from .revolution import Revolution
from .seasonal_event import SeasonalEvent
from .war import War
from .world_event import WorldEvent

# Gameplay Mechanics
from .autosave import Autosave
from .checkpoint import Checkpoint
from .fast_travel_point import FastTravelPoint
from .save_point import SavePoint
from .spawn_point import SpawnPoint
from .waypoint import Waypoint

# Achievements
from .achievement import Achievement
from .badge import Badge
from .leaderboard import Leaderboard
from .rank import Rank
from .trophy import Trophy

# UGC & Localization
from .custom_map import CustomMap
from .dubbing import Dubbing
from .localization import Localization
from .mod import Mod
from .share_code import ShareCode
from .subtitle import Subtitle
from .translation import Translation
from .user_scenario import UserScenario
from .voice_over import VoiceOver
from .workshop_entry import WorkshopEntry

# Analytics & Balance
from .balance_entities import EconomyBalance, PvPBalance, PvEBalance
from .conversion_rate import ConversionRate
from .difficulty_curve import DifficultyCurve
from .drop_rate import DropRate
from .heatmap import Heatmap
from .loot_table_weight import LootTableWeight
from .player_metric import PlayerMetric
from .session_data import SessionData

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
    "Season",
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

    # Art & Culture
    "Celebration",
    "Ceremony",
    "Concert",
    "Competition",
    "Exhibition",
    "Festival",
    "Tournament",
    "WeatherPattern",

    # Legal System
    "Court",
    "Crime",
    "Evidence",
    "Judge",
    "Jury",
    "Lawyer",
    "Punishment",
    "Witness",

    # Education
    "Academy",
    "Archive",
    "Library",
    "Museum",
    "ResearchCenter",
    "School",
    "University",

    # Media
    "Internet",
    "Newspaper",
    "Propaganda",
    "Radio",
    "SocialMedia",
    "Rumor",
    "Television",

    # Secrets
    "EasterEgg",
    "Enigma",
    "HiddenPath",
    "Mystery",
    "Puzzle",
    "Riddle",
    "SecretArea",
    "Trap",

    # Legendary Items
    "ArtifactSet",
    "CursedItem",
    "DivineItem",
    "LegendaryWeapon",
    "MythicalArmor",
    "RelicCollection",

    # Music & Audio
    "Ambient",
    "Motif",
    "Score",
    "Silence",
    "SoundEffect",
    "Soundtrack",
    "Theme",
    "VoiceLine",

    # Visual Effects
    "ColorPalette",
    "Lighting",
    "Particle",
    "Shader",
    "VisualEffect",

    # Cinematography
    "CameraPath",
    "Cinematic",
    "Cutscene",
    "Fade",
    "Flashback",
    "Transition",

    # Narrative Devices
    "ChekhovsGun",
    "DeusExMachina",
    "FlashForward",
    "Foreshadowing",
    "PlotDevice",
    "RedHerring",

    # Global Events
    "Famine",
    "Invasion",
    "Plague",
    "Revolution",
    "SeasonalEvent",
    "War",
    "WorldEvent",

    # Gameplay Mechanics
    "Autosave",
    "Checkpoint",
    "FastTravelPoint",
    "SavePoint",
    "SpawnPoint",
    "Waypoint",

    # Achievements
    "Achievement",
    "Badge",
    "Leaderboard",
    "Rank",
    "Trophy",

    # UGC & Localization
    "CustomMap",
    "Dubbing",
    "Localization",
    "Mod",
    "ShareCode",
    "Subtitle",
    "Translation",
    "UserScenario",
    "VoiceOver",
    "WorkshopEntry",

    # Analytics & Balance
    "BalanceEntities",
    "ConversionRate",
    "DifficultyCurve",
    "DropRate",
    "Heatmap",
    "LootTableWeight",
    "PlayerMetric",
    "SessionData",
]
