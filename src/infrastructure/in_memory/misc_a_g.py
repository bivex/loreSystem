"""In-memory repositories for miscellaneous game-system entities.

Extracted from the monolithic ``in_memory_repositories.py``. Standard
repositories inherit world-scoped CRUD from
:class:`InMemoryWorldEntityRepository`; repositories with extra query
methods or interface contracts preserve their original implementations.
"""

from __future__ import annotations

from src.infrastructure.in_memory.base import (
    InMemoryRepository,
    InMemoryWorldEntityRepository,
)

from typing import Any

from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from src.domain.exceptions import DuplicateEntity, EntityNotFound
from src.domain.value_objects.common import (
    CharacterName,
    EntityId,
    Lighting,
    TenantId,
    TimeOfDay,
    Weather,
    WorldName,
)

from src.domain.entities.academy import Academy
from src.domain.entities.affinity import Affinity
from src.domain.entities.airship import Airship
from src.domain.entities.archive import Archive
from src.domain.entities.arena import Arena
from src.domain.entities.army import Army
from src.domain.entities.artifact_set import ArtifactSet
from src.domain.entities.atmosphere import Atmosphere
from src.domain.entities.autosave import Autosave
from src.domain.entities.barter import Barter
from src.domain.entities.battalion import Battalion
from src.domain.entities.bestiary_entry import BestiaryEntry
from src.domain.entities.black_hole import BlackHole
from src.domain.entities.blessing import Blessing
from src.domain.entities.camera_path import CameraPath
from src.domain.entities.cataclysm import Cataclysm
from src.domain.entities.celebration import Celebration
from src.domain.entities.ceremony import Ceremony
from src.domain.entities.checkpoint import Checkpoint
from src.domain.entities.cinematic import Cinematic
from src.domain.entities.codex_entry import CodexEntry
from src.domain.entities.color_palette import ColorPalette
from src.domain.entities.competition import Competition
from src.domain.entities.concert import Concert
from src.domain.entities.crime import Crime
from src.domain.entities.cult import Cult
from src.domain.entities.curse import Curse
from src.domain.entities.cursed_item import CursedItem
from src.domain.entities.cutscene import Cutscene
from src.domain.entities.defense import Defense
from src.domain.entities.demand import Demand
from src.domain.entities.dimension import Dimension
from src.domain.entities.disaster import Disaster
from src.domain.entities.disposition import Disposition
from src.domain.entities.district import District
from src.domain.entities.divine_item import DivineItem
from src.domain.entities.dream import Dream
from src.domain.entities.dubbing import Dubbing
from src.domain.entities.easter_egg import EasterEgg
from src.domain.entities.eclipse import Eclipse
from src.domain.entities.enigma import Enigma
from src.domain.entities.evidence import Evidence
from src.domain.entities.evolution import Evolution
from src.domain.entities.exhibition import Exhibition
from src.domain.entities.extinction import Extinction
from src.domain.entities.fade import Fade
from src.domain.entities.familiar import Familiar
from src.domain.entities.famine import Famine
from src.domain.entities.fast_travel_point import FastTravelPoint
from src.domain.entities.festival import Festival
from src.domain.entities.flash_forward import FlashForward
from src.domain.entities.fleet import Fleet
from src.domain.entities.flowchart import Flowchart
from src.domain.entities.food_chain import FoodChain
from src.domain.entities.fortification import Fortification
from src.domain.entities.galaxy import Galaxy
from src.domain.entities.hibernation import Hibernation
from src.domain.entities.hidden_path import HiddenPath
from src.domain.entities.holy_site import HolySite
from src.domain.entities.honor import Honor
from src.domain.entities.hub_area import HubArea
from src.domain.entities.improvement import Improvement
from src.domain.entities.inflation import Inflation
from src.domain.entities.inspiration import Inspiration
from src.domain.entities.instance import Instance
from src.domain.entities.internet import Internet
from src.domain.entities.invasion import Invasion
from src.domain.entities.journal_page import JournalPage
from src.domain.entities.judge import Judge
from src.domain.entities.jury import Jury
from src.domain.entities.karma import Karma
from src.domain.entities.library import Library
from src.domain.entities.memory import Memory
from src.domain.entities.migration import Migration
from src.domain.entities.motif import Motif
from src.domain.entities.mount import Mount
from src.domain.entities.mount_equipment import MountEquipment
from src.domain.entities.museum import Museum
from src.domain.entities.music_control import MusicControl
from src.domain.entities.music_state import MusicState
from src.domain.entities.music_theme import MusicTheme
from src.domain.entities.music_track import MusicTrack
from src.domain.entities.mystery import Mystery
from src.domain.entities.mythical_armor import MythicalArmor
from src.domain.entities.nebula import Nebula
from src.domain.entities.newspaper import Newspaper
from src.domain.entities.nightmare import Nightmare
from src.domain.entities.noble_district import NobleDistrict
from src.domain.entities.oath import Oath
from src.domain.entities.open_world_zone import OpenWorldZone
from src.domain.entities.pact import Pact
from src.domain.entities.particle import Particle
from src.domain.entities.pet import Pet
from src.domain.entities.phenomenon import Phenomenon
from src.domain.entities.pity import Pity
from src.domain.entities.plague import Plague
from src.domain.entities.player_profile import PlayerProfile
from src.domain.entities.plaza import Plaza
from src.domain.entities.pocket_dimension import PocketDimension
from src.domain.entities.port_district import PortDistrict
from src.domain.entities.portal import Portal
from src.domain.entities.price import Price
from src.domain.entities.propaganda import Propaganda
from src.domain.entities.punishment import Punishment
from src.domain.entities.quarter import Quarter
from src.domain.entities.radio import Radio
from src.domain.entities.raid import Raid
from src.domain.entities.red_herring import RedHerring
from src.domain.entities.reproduction import Reproduction
from src.domain.entities.reputation import Reputation
from src.domain.entities.requirement import Requirement
from src.domain.entities.research_center import ResearchCenter
from src.domain.entities.revolution import Revolution
from src.domain.entities.ritual import Ritual
from src.domain.entities.save_point import SavePoint
from src.domain.entities.school import School
from src.domain.entities.score import Score
from src.domain.entities.scripture import Scripture
from src.domain.entities.secret_area import SecretArea
from src.domain.entities.sect import Sect
from src.domain.entities.shader import Shader
from src.domain.entities.siege_engine import SiegeEngine
from src.domain.entities.skybox import Skybox
from src.domain.entities.slums import Slums
from src.domain.entities.solstice import Solstice
from src.domain.entities.spaceship import Spaceship
from src.domain.entities.spawn_point import SpawnPoint
from src.domain.entities.subtitle import Subtitle
from src.domain.entities.summon import Summon
from src.domain.entities.supply import Supply
from src.domain.entities.tariff import Tariff
from src.domain.entities.tax import Tax
from src.domain.entities.teleporter import Teleporter
from src.domain.entities.television import Television
from src.domain.entities.theme import Theme
from src.domain.entities.tournament import Tournament
from src.domain.entities.transition import Transition
from src.domain.entities.trap import Trap
from src.domain.entities.underground import Underground
from src.domain.entities.university import University
from src.domain.entities.vehicle import Vehicle
from src.domain.entities.visual_effect import VisualEffect
from src.domain.entities.voice_over import VoiceOver
from src.domain.entities.waypoint import Waypoint
from src.domain.entities.weapon_system import WeaponSystem
from src.domain.entities.witness import Witness
from src.domain.entities.workshop_entry import WorkshopEntry
from src.domain.entities.wormhole import Wormhole

from src.domain.repositories.image_repository import IImageRepository
from src.domain.repositories.note_repository import INoteRepository
from src.domain.repositories.tag_repository import ITagRepository
from src.domain.repositories.template_repository import ITemplateRepository


class InMemoryAcademyRepository(InMemoryWorldEntityRepository[Academy]):
    """In-memory repository for Academy (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryAffinityRepository(InMemoryWorldEntityRepository[Affinity]):
    """In-memory repository for Affinity (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryAirshipRepository(InMemoryWorldEntityRepository[Airship]):
    """In-memory repository for Airship (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryAlternateRealityRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for RealityType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryAlternate_realityRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for RealityType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryAmbientRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for AmbientType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryArchiveRepository(InMemoryWorldEntityRepository[Archive]):
    """In-memory repository for Archive (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryArenaRepository(InMemoryWorldEntityRepository[Arena]):
    """In-memory repository for Arena (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryArmyRepository(InMemoryWorldEntityRepository[Army]):
    """In-memory repository for Army (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryArtifact_setRepository(InMemoryWorldEntityRepository[ArtifactSet]):
    """In-memory repository for ArtifactSet (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryAtmosphereRepository(InMemoryWorldEntityRepository[Atmosphere]):
    """In-memory repository for Atmosphere (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryAutosaveRepository(InMemoryWorldEntityRepository[Autosave]):
    """In-memory repository for Autosave (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryBalanceEntitiesRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for EconomyBalance (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryBalance_entitiesRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for EconomyBalance (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryBannerRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for BannerType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryBarterRepository(InMemoryWorldEntityRepository[Barter]):
    """In-memory repository for Barter (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryBattalionRepository(InMemoryWorldEntityRepository[Battalion]):
    """In-memory repository for Battalion (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryBestiaryEntryRepository(InMemoryWorldEntityRepository[BestiaryEntry]):
    """In-memory repository for BestiaryEntry (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryBestiary_entryRepository(InMemoryWorldEntityRepository[BestiaryEntry]):
    """In-memory repository for BestiaryEntry (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryBlackHoleRepository(InMemoryWorldEntityRepository[BlackHole]):
    """In-memory repository for BlackHole (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryBlack_holeRepository(InMemoryWorldEntityRepository[BlackHole]):
    """In-memory repository for BlackHole (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryBlessingRepository(InMemoryWorldEntityRepository[Blessing]):
    """In-memory repository for Blessing (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryCameraPathRepository(InMemoryWorldEntityRepository[CameraPath]):
    """In-memory repository for CameraPath (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryCamera_pathRepository(InMemoryWorldEntityRepository[CameraPath]):
    """In-memory repository for CameraPath (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryCataclysmRepository(InMemoryWorldEntityRepository[Cataclysm]):
    """In-memory repository for Cataclysm (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryCelebrationRepository(InMemoryWorldEntityRepository[Celebration]):
    """In-memory repository for Celebration (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryCeremonyRepository(InMemoryWorldEntityRepository[Ceremony]):
    """In-memory repository for Ceremony (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryCheckpointRepository(InMemoryWorldEntityRepository[Checkpoint]):
    """In-memory repository for Checkpoint (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryChekhovsGunRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for GunType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryChekhovs_gunRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for GunType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryCinematicRepository(InMemoryWorldEntityRepository[Cinematic]):
    """In-memory repository for Cinematic (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryCodexEntryRepository(InMemoryWorldEntityRepository[CodexEntry]):
    """In-memory repository for CodexEntry (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryCodex_entryRepository(InMemoryWorldEntityRepository[CodexEntry]):
    """In-memory repository for CodexEntry (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryColorPaletteRepository(InMemoryWorldEntityRepository[ColorPalette]):
    """In-memory repository for ColorPalette (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryColor_paletteRepository(InMemoryWorldEntityRepository[ColorPalette]):
    """In-memory repository for ColorPalette (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryCompetitionRepository(InMemoryWorldEntityRepository[Competition]):
    """In-memory repository for Competition (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryConcertRepository(InMemoryWorldEntityRepository[Concert]):
    """In-memory repository for Concert (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryConversionRateRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for ConversionRate (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryConversion_rateRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for ConversionRate (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryCrimeRepository(InMemoryWorldEntityRepository[Crime]):
    """In-memory repository for Crime (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryCultRepository(InMemoryWorldEntityRepository[Cult]):
    """In-memory repository for Cult (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryCurseRepository(InMemoryWorldEntityRepository[Curse]):
    """In-memory repository for Curse (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryCursed_itemRepository(InMemoryWorldEntityRepository[CursedItem]):
    """In-memory repository for CursedItem (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryCustom_mapRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for CustomMap (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryCutsceneRepository(InMemoryWorldEntityRepository[Cutscene]):
    """In-memory repository for Cutscene (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryDefenseRepository(InMemoryWorldEntityRepository[Defense]):
    """In-memory repository for Defense (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryDemandRepository(InMemoryWorldEntityRepository[Demand]):
    """In-memory repository for Demand (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryDeus_ex_machinaRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for DeusExMachinaType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryDifficultyCurveRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for DifficultyCurve (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryDifficulty_curveRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for DifficultyCurve (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryDimensionRepository(InMemoryWorldEntityRepository[Dimension]):
    """In-memory repository for Dimension (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryDisasterRepository(InMemoryWorldEntityRepository[Disaster]):
    """In-memory repository for Disaster (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryDiscoveryRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for DiscoveryType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryDispositionRepository(InMemoryWorldEntityRepository[Disposition]):
    """In-memory repository for Disposition (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryDistrictRepository(InMemoryWorldEntityRepository[District]):
    """In-memory repository for District (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryDivine_itemRepository(InMemoryWorldEntityRepository[DivineItem]):
    """In-memory repository for DivineItem (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryDreamRepository(InMemoryWorldEntityRepository[Dream]):
    """In-memory repository for Dream (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryDropRateRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for DropRate (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryDrop_rateRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for DropRate (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryDubbingRepository(InMemoryWorldEntityRepository[Dubbing]):
    """In-memory repository for Dubbing (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryEasterEggRepository(InMemoryWorldEntityRepository[EasterEgg]):
    """In-memory repository for EasterEgg (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryEaster_eggRepository(InMemoryWorldEntityRepository[EasterEgg]):
    """In-memory repository for EasterEgg (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryEclipseRepository(InMemoryWorldEntityRepository[Eclipse]):
    """In-memory repository for Eclipse (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryEnigmaRepository(InMemoryWorldEntityRepository[Enigma]):
    """In-memory repository for Enigma (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryEvidenceRepository(InMemoryWorldEntityRepository[Evidence]):
    """In-memory repository for Evidence (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryEvolutionRepository(InMemoryWorldEntityRepository[Evolution]):
    """In-memory repository for Evolution (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryExhibitionRepository(InMemoryWorldEntityRepository[Exhibition]):
    """In-memory repository for Exhibition (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryExtinctionRepository(InMemoryWorldEntityRepository[Extinction]):
    """In-memory repository for Extinction (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFadeRepository(InMemoryWorldEntityRepository[Fade]):
    """In-memory repository for Fade (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFamiliarRepository(InMemoryWorldEntityRepository[Familiar]):
    """In-memory repository for Familiar (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFamineRepository(InMemoryWorldEntityRepository[Famine]):
    """In-memory repository for Famine (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFastTravelPointRepository(InMemoryWorldEntityRepository[FastTravelPoint]):
    """In-memory repository for FastTravelPoint (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFast_travel_pointRepository(InMemoryWorldEntityRepository[FastTravelPoint]):
    """In-memory repository for FastTravelPoint (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFestivalRepository(InMemoryWorldEntityRepository[Festival]):
    """In-memory repository for Festival (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFlash_forwardRepository(InMemoryWorldEntityRepository[FlashForward]):
    """In-memory repository for FlashForward (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFleetRepository(InMemoryWorldEntityRepository[Fleet]):
    """In-memory repository for Fleet (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFlowchartRepository:
    """In-memory implementation of Flowchart repository for testing."""

    def __init__(self):
        self._flowcharts: Dict[Tuple[TenantId, EntityId], object] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._by_story: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, flowchart: object) -> object:
        if flowchart.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(flowchart, 'id', new_id)

        key = (flowchart.tenant_id, flowchart.id)
        self._flowcharts[key] = flowchart

        story_key = (flowchart.tenant_id, flowchart.story_id) if hasattr(flowchart, 'story_id') else None
        if story_key:
            if flowchart.id not in self._by_story[story_key]:
                self._by_story[story_key].append(flowchart.id)

        world_key = (flowchart.tenant_id, flowchart.world_id)
        if flowchart.id not in self._by_world[world_key]:
            self._by_world[world_key].append(flowchart.id)

        return flowchart

    def find_by_id(self, tenant_id: TenantId, flowchart_id: EntityId) -> Optional[object]:
        return self._flowcharts.get((tenant_id, flowchart_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        world_key = (tenant_id, world_id)
        flowchart_ids = self._by_world.get(world_key, [])
        flowcharts = []
        for flowchart_id in flowchart_ids[offset:offset + limit]:
            flowchart = self._flowcharts.get((tenant_id, flowchart_id))
            if flowchart:
                flowcharts.append(flowchart)
        return flowcharts

    def list_by_story(self, tenant_id: TenantId, story_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        story_key = (tenant_id, story_id)
        flowchart_ids = self._by_story.get(story_key, [])
        flowcharts = []
        for flowchart_id in flowchart_ids[offset:offset + limit]:
            flowchart = self._flowcharts.get((tenant_id, flowchart_id))
            if flowchart:
                flowcharts.append(flowchart)
        return flowcharts

    def find_active(self, tenant_id: TenantId, world_id: EntityId) -> Optional[object]:
        all_flowcharts = self.list_by_world(tenant_id, world_id)
        for flowchart in all_flowcharts:
            if getattr(flowchart, 'is_active', False):
                return flowchart
        return None

    def delete(self, tenant_id: TenantId, flowchart_id: EntityId) -> bool:
        key = (tenant_id, flowchart_id)
        if key not in self._flowcharts:
            return False

        flowchart = self._flowcharts[key]

        story_key = (flowchart.tenant_id, flowchart.story_id) if hasattr(flowchart, 'story_id') else None
        if story_key and flowchart_id in self._by_story[story_key]:
            self._by_story[story_key].remove(flowchart_id)

        world_key = (flowchart.tenant_id, flowchart.world_id)
        if flowchart_id in self._by_world[world_key]:
            self._by_world[world_key].remove(flowchart_id)

        del self._flowcharts[key]
        return True


class InMemoryFoodChainRepository(InMemoryWorldEntityRepository[FoodChain]):
    """In-memory repository for FoodChain (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFood_chainRepository(InMemoryWorldEntityRepository[FoodChain]):
    """In-memory repository for FoodChain (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryForeshadowingRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for ForeshadowingType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryFortificationRepository(InMemoryWorldEntityRepository[Fortification]):
    """In-memory repository for Fortification (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryGalaxyRepository(InMemoryWorldEntityRepository[Galaxy]):
    """In-memory repository for Galaxy (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


