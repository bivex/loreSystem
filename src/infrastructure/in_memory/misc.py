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


class InMemoryHeatmapRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for Heatmap (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryHibernationRepository(InMemoryWorldEntityRepository[Hibernation]):
    """In-memory repository for Hibernation (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryHiddenPathRepository(InMemoryWorldEntityRepository[HiddenPath]):
    """In-memory repository for HiddenPath (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryHidden_pathRepository(InMemoryWorldEntityRepository[HiddenPath]):
    """In-memory repository for HiddenPath (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryHolySiteRepository(InMemoryWorldEntityRepository[HolySite]):
    """In-memory repository for HolySite (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryHoly_siteRepository(InMemoryWorldEntityRepository[HolySite]):
    """In-memory repository for HolySite (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryHonorRepository(InMemoryWorldEntityRepository[Honor]):
    """In-memory repository for Honor (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryHubAreaRepository(InMemoryWorldEntityRepository[HubArea]):
    """In-memory repository for HubArea (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryHub_areaRepository(InMemoryWorldEntityRepository[HubArea]):
    """In-memory repository for HubArea (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryImageRepository(IImageRepository):
    """In-memory implementation of Image repository for testing."""

    def __init__(self):
        self._images: Dict[Tuple[TenantId, EntityId], object] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._paths: Dict[Tuple[TenantId, EntityId, str], EntityId] = {}
        self._next_id = 1

    def save(self, image: object) -> object:
        if image.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(image, 'id', new_id)

        key = (image.tenant_id, image.id)
        self._images[key] = image

        path_key = (image.tenant_id, image.world_id, image.path)
        self._paths[path_key] = image.id

        world_key = (image.tenant_id, image.world_id)
        if image.id not in self._by_world[world_key]:
            self._by_world[world_key].append(image.id)

        return image

    def find_by_id(self, tenant_id: TenantId, image_id: EntityId) -> Optional[object]:
        return self._images.get((tenant_id, image_id))

    def find_by_path(self, tenant_id: TenantId, world_id: EntityId, path: str) -> Optional[object]:
        path_key = (tenant_id, world_id, path)
        image_id = self._paths.get(path_key)
        if image_id:
            return self._images.get((tenant_id, image_id))
        return None

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        world_key = (tenant_id, world_id)
        image_ids = self._by_world.get(world_key, [])
        images = []
        for image_id in image_ids[offset:offset + limit]:
            image = self._images.get((tenant_id, image_id))
            if image:
                images.append(image)
        return images

    def delete(self, tenant_id: TenantId, image_id: EntityId) -> bool:
        key = (tenant_id, image_id)
        if key not in self._images:
            return False

        image = self._images[key]
        path_key = (image.tenant_id, image.world_id, image.path)
        if path_key in self._paths:
            del self._paths[path_key]

        world_key = (image.tenant_id, image.world_id)
        if image_id in self._by_world[world_key]:
            self._by_world[world_key].remove(image_id)

        del self._images[key]
        return True

    def exists(self, tenant_id: TenantId, world_id: EntityId, path: str) -> bool:
        path_key = (tenant_id, world_id, path)
        return path_key in self._paths


class InMemoryImprovementRepository(InMemoryWorldEntityRepository[Improvement]):
    """In-memory repository for Improvement (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryInflationRepository(InMemoryWorldEntityRepository[Inflation]):
    """In-memory repository for Inflation (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryInspirationRepository:
    """In-memory implementation of Inspiration repository for testing."""

    def __init__(self):
        self._inspirations: Dict[Tuple[TenantId, EntityId], object] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, inspiration: object) -> object:
        if inspiration.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(inspiration, 'id', new_id)

        key = (inspiration.tenant_id, inspiration.id)
        self._inspirations[key] = inspiration

        world_key = (inspiration.tenant_id, inspiration.world_id)
        if inspiration.id not in self._by_world[world_key]:
            self._by_world[world_key].append(inspiration.id)

        return inspiration

    def find_by_id(self, tenant_id: TenantId, inspiration_id: EntityId) -> Optional[object]:
        return self._inspirations.get((tenant_id, inspiration_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        world_key = (tenant_id, world_id)
        inspiration_ids = self._by_world.get(world_key, [])
        inspirations = []
        for inspiration_id in inspiration_ids[offset:offset + limit]:
            inspiration = self._inspirations.get((tenant_id, inspiration_id))
            if inspiration:
                inspirations.append(inspiration)
        return inspirations

    def list_by_category(self, tenant_id: TenantId, world_id: EntityId, category: str, limit: int = 50, offset: int = 0) -> List[object]:
        all_inspirations = self.list_by_world(tenant_id, world_id)
        return [i for i in all_inspirations if getattr(i, 'category', None) == category][offset:offset + limit]

    def list_unused(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[object]:
        all_inspirations = self.list_by_world(tenant_id, world_id)
        return [i for i in all_inspirations if not getattr(i, 'is_used', False)][offset:offset + limit]

    def search_by_content(self, tenant_id: TenantId, search_term: str, limit: int = 20) -> List[object]:
        results = []
        for inspiration in self._inspirations.values():
            if inspiration.tenant_id == tenant_id:
                content = getattr(inspiration, 'content', '')
                if search_term.lower() in content.lower():
                    results.append(inspiration)
                    if len(results) >= limit:
                        break
        return results

    def delete(self, tenant_id: TenantId, inspiration_id: EntityId) -> bool:
        key = (tenant_id, inspiration_id)
        if key not in self._inspirations:
            return False

        inspiration = self._inspirations[key]
        world_key = (inspiration.tenant_id, inspiration.world_id)
        if inspiration_id in self._by_world[world_key]:
            self._by_world[world_key].remove(inspiration_id)

        del self._inspirations[key]
        return True


class InMemoryInstanceRepository(InMemoryWorldEntityRepository[Instance]):
    """In-memory repository for Instance (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryInternetRepository(InMemoryWorldEntityRepository[Internet]):
    """In-memory repository for Internet (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryInvasionRepository(InMemoryWorldEntityRepository[Invasion]):
    """In-memory repository for Invasion (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryInventionRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for InventionCategory (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryJournal_pageRepository(InMemoryWorldEntityRepository[JournalPage]):
    """In-memory repository for JournalPage (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryJudgeRepository(InMemoryWorldEntityRepository[Judge]):
    """In-memory repository for Judge (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryJuryRepository(InMemoryWorldEntityRepository[Jury]):
    """In-memory repository for Jury (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryKarmaRepository(InMemoryWorldEntityRepository[Karma]):
    """In-memory repository for Karma (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryKillCountRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for KillCount (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryLibraryRepository(InMemoryWorldEntityRepository[Library]):
    """In-memory repository for Library (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryLocalizationRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for Localization (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryMemoryRepository(InMemoryWorldEntityRepository[Memory]):
    """In-memory repository for Memory (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryMigrationRepository(InMemoryWorldEntityRepository[Migration]):
    """In-memory repository for Migration (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryModRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for Mod (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryMotifRepository(InMemoryWorldEntityRepository[Motif]):
    """In-memory repository for Motif (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryMotionCaptureRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for AnimationType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryMotion_captureRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for AnimationType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryMountEquipmentRepository(InMemoryWorldEntityRepository[MountEquipment]):
    """In-memory repository for MountEquipment (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryMountRepository(InMemoryWorldEntityRepository[Mount]):
    """In-memory repository for Mount (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryMount_equipmentRepository(InMemoryWorldEntityRepository[MountEquipment]):
    """In-memory repository for MountEquipment (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryMuseumRepository(InMemoryWorldEntityRepository[Museum]):
    """In-memory repository for Museum (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryMusic_controlRepository(InMemoryWorldEntityRepository[MusicControl]):
    """In-memory repository for MusicControl (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryMusic_stateRepository(InMemoryWorldEntityRepository[MusicState]):
    """In-memory repository for MusicState (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryMusic_themeRepository(InMemoryWorldEntityRepository[MusicTheme]):
    """In-memory repository for MusicTheme (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryMusic_trackRepository(InMemoryWorldEntityRepository[MusicTrack]):
    """In-memory repository for MusicTrack (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryMysteryRepository(InMemoryWorldEntityRepository[Mystery]):
    """In-memory repository for Mystery (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryMythicalArmorRepository(InMemoryWorldEntityRepository[MythicalArmor]):
    """In-memory repository for MythicalArmor (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryMythical_armorRepository(InMemoryWorldEntityRepository[MythicalArmor]):
    """In-memory repository for MythicalArmor (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryNebulaRepository(InMemoryWorldEntityRepository[Nebula]):
    """In-memory repository for Nebula (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryNewspaperRepository(InMemoryWorldEntityRepository[Newspaper]):
    """In-memory repository for Newspaper (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryNightmareRepository(InMemoryWorldEntityRepository[Nightmare]):
    """In-memory repository for Nightmare (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryNobleDistrictRepository(InMemoryWorldEntityRepository[NobleDistrict]):
    """In-memory repository for NobleDistrict (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryNoble_districtRepository(InMemoryWorldEntityRepository[NobleDistrict]):
    """In-memory repository for NobleDistrict (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryNoteRepository(INoteRepository):
    """In-memory implementation of Note repository for testing."""

    def __init__(self):
        self._notes: Dict[Tuple[TenantId, EntityId], Note] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, note: Note) -> Note:
        if note.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(note, 'id', new_id)

        key = (note.tenant_id, note.id)
        self._notes[key] = note

        world_key = (note.tenant_id, note.world_id)
        if note.id not in self._by_world[world_key]:
            self._by_world[world_key].append(note.id)

        return note

    def find_by_id(self, tenant_id: TenantId, note_id: EntityId) -> Optional[Note]:
        return self._notes.get((tenant_id, note_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Note]:
        world_key = (tenant_id, world_id)
        note_ids = self._by_world.get(world_key, [])
        notes = []
        for note_id in note_ids[offset:offset + limit]:
            note = self._notes.get((tenant_id, note_id))
            if note:
                notes.append(note)
        return notes

    def list_pinned(self, tenant_id: TenantId, world_id: EntityId, limit: int = 20, offset: int = 0) -> List[Note]:
        all_notes = self.list_by_world(tenant_id, world_id)
        return [n for n in all_notes if n.is_pinned][offset:offset + limit]

    def search_by_content(self, tenant_id: TenantId, search_term: str, limit: int = 20) -> List[Note]:
        results = []
        for note in self._notes.values():
            if note.tenant_id == tenant_id:
                if search_term.lower() in note.content.lower() or search_term.lower() in note.title.lower():
                    results.append(note)
                    if len(results) >= limit:
                        break
        return results

    def delete(self, tenant_id: TenantId, note_id: EntityId) -> bool:
        key = (tenant_id, note_id)
        if key not in self._notes:
            return False

        note = self._notes[key]
        world_key = (note.tenant_id, note.world_id)
        if note_id in self._by_world[world_key]:
            self._by_world[world_key].remove(note_id)

        del self._notes[key]
        return True


class InMemoryOathRepository(InMemoryWorldEntityRepository[Oath]):
    """In-memory repository for Oath (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryOpen_world_zoneRepository(InMemoryWorldEntityRepository[OpenWorldZone]):
    """In-memory repository for OpenWorldZone (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPactRepository(InMemoryWorldEntityRepository[Pact]):
    """In-memory repository for Pact (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryParticleRepository(InMemoryWorldEntityRepository[Particle]):
    """In-memory repository for Particle (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPatentRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for PatentStatus (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryPetRepository(InMemoryWorldEntityRepository[Pet]):
    """In-memory repository for Pet (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPhenomenonRepository(InMemoryWorldEntityRepository[Phenomenon]):
    """In-memory repository for Phenomenon (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPityRepository(InMemoryWorldEntityRepository[Pity]):
    """In-memory repository for Pity (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPlagueRepository(InMemoryWorldEntityRepository[Plague]):
    """In-memory repository for Plague (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPlayerMetricRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for PlayerMetric (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryPlayer_metricRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for PlayerMetric (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryPlayer_profileRepository(InMemoryWorldEntityRepository[PlayerProfile]):
    """In-memory repository for PlayerProfile (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPlazaRepository(InMemoryWorldEntityRepository[Plaza]):
    """In-memory repository for Plaza (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPocketDimensionRepository(InMemoryWorldEntityRepository[PocketDimension]):
    """In-memory repository for PocketDimension (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPocket_dimensionRepository(InMemoryWorldEntityRepository[PocketDimension]):
    """In-memory repository for PocketDimension (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPortDistrictRepository(InMemoryWorldEntityRepository[PortDistrict]):
    """In-memory repository for PortDistrict (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPort_districtRepository(InMemoryWorldEntityRepository[PortDistrict]):
    """In-memory repository for PortDistrict (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPortalRepository(InMemoryWorldEntityRepository[Portal]):
    """In-memory repository for Portal (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPriceRepository(InMemoryWorldEntityRepository[Price]):
    """In-memory repository for Price (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPropagandaRepository(InMemoryWorldEntityRepository[Propaganda]):
    """In-memory repository for Propaganda (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPrototypeRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for PrototypeStatus (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryPullRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for PullResult (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryPunishmentRepository(InMemoryWorldEntityRepository[Punishment]):
    """In-memory repository for Punishment (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryPurchaseRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for PurchaseStatus (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryQuarterRepository(InMemoryWorldEntityRepository[Quarter]):
    """In-memory repository for Quarter (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryRadioRepository(InMemoryWorldEntityRepository[Radio]):
    """In-memory repository for Radio (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryRaidRepository(InMemoryWorldEntityRepository[Raid]):
    """In-memory repository for Raid (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryRedHerringRepository(InMemoryWorldEntityRepository[RedHerring]):
    """In-memory repository for RedHerring (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryRed_herringRepository(InMemoryWorldEntityRepository[RedHerring]):
    """In-memory repository for RedHerring (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryReproductionRepository(InMemoryWorldEntityRepository[Reproduction]):
    """In-memory repository for Reproduction (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryReputationRepository(InMemoryWorldEntityRepository[Reputation]):
    """In-memory repository for Reputation (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryRequirementRepository(InMemoryWorldEntityRepository[Requirement]):
    """In-memory repository for Requirement (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryResearchCenterRepository(InMemoryWorldEntityRepository[ResearchCenter]):
    """In-memory repository for ResearchCenter (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryResearchRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for ResearchStatus (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryResearch_centerRepository(InMemoryWorldEntityRepository[ResearchCenter]):
    """In-memory repository for ResearchCenter (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryRevolutionRepository(InMemoryWorldEntityRepository[Revolution]):
    """In-memory repository for Revolution (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryRitualRepository(InMemoryWorldEntityRepository[Ritual]):
    """In-memory repository for Ritual (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySavePointRepository(InMemoryWorldEntityRepository[SavePoint]):
    """In-memory repository for SavePoint (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySave_pointRepository(InMemoryWorldEntityRepository[SavePoint]):
    """In-memory repository for SavePoint (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySchoolRepository(InMemoryWorldEntityRepository[School]):
    """In-memory repository for School (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryScoreRepository(InMemoryWorldEntityRepository[Score]):
    """In-memory repository for Score (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryScriptureRepository(InMemoryWorldEntityRepository[Scripture]):
    """In-memory repository for Scripture (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySecretAreaRepository(InMemoryWorldEntityRepository[SecretArea]):
    """In-memory repository for SecretArea (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySecret_areaRepository(InMemoryWorldEntityRepository[SecretArea]):
    """In-memory repository for SecretArea (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySectRepository(InMemoryWorldEntityRepository[Sect]):
    """In-memory repository for Sect (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryShaderRepository(InMemoryWorldEntityRepository[Shader]):
    """In-memory repository for Shader (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryShareCodeRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for ShareCode (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryShare_codeRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for ShareCode (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemorySiegeEngineRepository(InMemoryWorldEntityRepository[SiegeEngine]):
    """In-memory repository for SiegeEngine (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySiege_engineRepository(InMemoryWorldEntityRepository[SiegeEngine]):
    """In-memory repository for SiegeEngine (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySilenceRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for SilencePurpose (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemorySkyboxRepository(InMemoryWorldEntityRepository[Skybox]):
    """In-memory repository for Skybox (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySlumsRepository(InMemoryWorldEntityRepository[Slums]):
    """In-memory repository for Slums (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySolsticeRepository(InMemoryWorldEntityRepository[Solstice]):
    """In-memory repository for Solstice (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySoundEffectRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for SoundEffectType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemorySound_effectRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for SoundEffectType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemorySoundtrackRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for SoundtrackType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemorySpaceshipRepository(InMemoryWorldEntityRepository[Spaceship]):
    """In-memory repository for Spaceship (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySpawnPointRepository(InMemoryWorldEntityRepository[SpawnPoint]):
    """In-memory repository for SpawnPoint (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySpawn_pointRepository(InMemoryWorldEntityRepository[SpawnPoint]):
    """In-memory repository for SpawnPoint (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySubtitleRepository(InMemoryWorldEntityRepository[Subtitle]):
    """In-memory repository for Subtitle (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySummonRepository(InMemoryWorldEntityRepository[Summon]):
    """In-memory repository for Summon (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySupplyRepository(InMemoryWorldEntityRepository[Supply]):
    """In-memory repository for Supply (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySwampRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for Swamp (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryTagRepository(ITagRepository):
    """In-memory implementation of Tag repository for testing."""

    def __init__(self):
        self._tags: Dict[Tuple[TenantId, EntityId], Tag] = {}
        self._names: Dict[Tuple[TenantId, EntityId, str, str], EntityId] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, tag: Tag) -> Tag:
        if tag.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(tag, 'id', new_id)

        key = (tag.tenant_id, tag.id)
        name_key = (tag.tenant_id, tag.world_id, tag.name.value, tag.tag_type.value)

        if name_key in self._names and self._names[name_key] != tag.id:
            raise DuplicateEntity(f"Tag with name '{tag.name}' already exists in this world")

        self._tags[key] = tag
        self._names[name_key] = tag.id

        world_key = (tag.tenant_id, tag.world_id)
        if tag.id not in self._by_world[world_key]:
            self._by_world[world_key].append(tag.id)

        return tag

    def find_by_id(self, tenant_id: TenantId, tag_id: EntityId) -> Optional[Tag]:
        return self._tags.get((tenant_id, tag_id))

    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: "TagName") -> Optional[Tag]:
        for key, tag_id in self._names.items():
            if key[0] == tenant_id and key[1] == world_id and key[2] == name.value:
                return self._tags.get((tenant_id, tag_id))
        return None

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Tag]:
        world_key = (tenant_id, world_id)
        tag_ids = self._by_world.get(world_key, [])
        tags = []
        for tag_id in tag_ids[offset:offset + limit]:
            tag = self._tags.get((tenant_id, tag_id))
            if tag:
                tags.append(tag)
        return tags

    def list_by_type(self, tenant_id: TenantId, world_id: EntityId, tag_type: "TagType", limit: int = 50, offset: int = 0) -> List[Tag]:
        all_tags = self.list_by_world(tenant_id, world_id)
        return [t for t in all_tags if t.tag_type.value == tag_type.value][offset:offset + limit]

    def delete(self, tenant_id: TenantId, tag_id: EntityId) -> bool:
        key = (tenant_id, tag_id)
        if key not in self._tags:
            return False

        tag = self._tags[key]
        name_key = (tag.tenant_id, tag.world_id, tag.name.value, tag.tag_type.value)

        if name_key in self._names:
            del self._names[name_key]

        world_key = (tag.tenant_id, tag.world_id)
        if tag_id in self._by_world[world_key]:
            self._by_world[world_key].remove(tag_id)

        del self._tags[key]
        return True

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: "TagName", tag_type: "TagType") -> bool:
        name_key = (tenant_id, world_id, name.value, tag_type.value)
        return name_key in self._names


class InMemoryTariffRepository(InMemoryWorldEntityRepository[Tariff]):
    """In-memory repository for Tariff (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryTaxRepository(InMemoryWorldEntityRepository[Tax]):
    """In-memory repository for Tax (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryTeleporterRepository(InMemoryWorldEntityRepository[Teleporter]):
    """In-memory repository for Teleporter (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryTelevisionRepository(InMemoryWorldEntityRepository[Television]):
    """In-memory repository for Television (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryTemplateRepository(ITemplateRepository):
    """In-memory implementation of Template repository for testing."""

    def __init__(self):
        self._templates: Dict[Tuple[TenantId, EntityId], Template] = {}
        self._names: Dict[Tuple[TenantId, EntityId, str], EntityId] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, template: Template) -> Template:
        if template.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(template, 'id', new_id)

        key = (template.tenant_id, template.id)
        name_key = (template.tenant_id, template.world_id, template.name.value)

        if name_key in self._names and self._names[name_key] != template.id:
            raise DuplicateEntity(f"Template with name '{template.name}' already exists in this world")

        self._templates[key] = template
        self._names[name_key] = template.id

        world_key = (template.tenant_id, template.world_id)
        if template.id not in self._by_world[world_key]:
            self._by_world[world_key].append(template.id)

        return template

    def find_by_id(self, tenant_id: TenantId, template_id: EntityId) -> Optional[Template]:
        return self._templates.get((tenant_id, template_id))

    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: "TemplateName") -> Optional[Template]:
        template_id = self._names.get((tenant_id, world_id, name.value))
        if template_id:
            return self._templates.get((tenant_id, template_id))
        return None

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Template]:
        world_key = (tenant_id, world_id)
        template_ids = self._by_world.get(world_key, [])
        templates = []
        for template_id in template_ids[offset:offset + limit]:
            template = self._templates.get((tenant_id, template_id))
            if template:
                templates.append(template)
        return templates

    def list_by_type(self, tenant_id: TenantId, world_id: EntityId, template_type: "TemplateType", limit: int = 50, offset: int = 0) -> List[Template]:
        all_templates = self.list_by_world(tenant_id, world_id)
        return [t for t in all_templates if t.template_type.value == template_type.value][offset:offset + limit]

    def list_runes(self, tenant_id: TenantId, parent_template_id: EntityId, limit: int = 50, offset: int = 0) -> List[Template]:
        all_templates = [t for t in self._templates.values() if t.tenant_id == tenant_id]
        return [t for t in all_templates if t.parent_template_id == parent_template_id][offset:offset + limit]

    def delete(self, tenant_id: TenantId, template_id: EntityId) -> bool:
        key = (tenant_id, template_id)
        if key not in self._templates:
            return False

        template = self._templates[key]
        name_key = (template.tenant_id, template.world_id, template.name.value)

        if name_key in self._names:
            del self._names[name_key]

        world_key = (template.tenant_id, template.world_id)
        if template_id in self._by_world[world_key]:
            self._by_world[world_key].remove(template_id)

        del self._templates[key]
        return True

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: "TemplateName") -> bool:
        name_key = (tenant_id, world_id, name.value)
        return name_key in self._names


class InMemoryThemeRepository(InMemoryWorldEntityRepository[Theme]):
    """In-memory repository for Theme (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryTimePeriodRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for PeriodType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryTime_periodRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for PeriodType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryTournamentRepository(InMemoryWorldEntityRepository[Tournament]):
    """In-memory repository for Tournament (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryTransitionRepository(InMemoryWorldEntityRepository[Transition]):
    """In-memory repository for Transition (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryTranslationRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for Translation (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryTrapRepository(InMemoryWorldEntityRepository[Trap]):
    """In-memory repository for Trap (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryTreasuryRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for Treasury (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryUndergroundRepository(InMemoryWorldEntityRepository[Underground]):
    """In-memory repository for Underground (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryUniversityRepository(InMemoryWorldEntityRepository[University]):
    """In-memory repository for University (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryUserScenarioRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for UserScenario (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryUser_scenarioRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for UserScenario (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryVehicleRepository(InMemoryWorldEntityRepository[Vehicle]):
    """In-memory repository for Vehicle (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryVisualEffectRepository(InMemoryWorldEntityRepository[VisualEffect]):
    """In-memory repository for VisualEffect (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryVisual_effectRepository(InMemoryWorldEntityRepository[VisualEffect]):
    """In-memory repository for VisualEffect (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryVoiceLineRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for VoiceLineType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryVoiceOverRepository(InMemoryWorldEntityRepository[VoiceOver]):
    """In-memory repository for VoiceOver (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryVoice_actorRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for VoiceActorStatus (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryVoice_lineRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for VoiceLineType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryVoice_overRepository(InMemoryWorldEntityRepository[VoiceOver]):
    """In-memory repository for VoiceOver (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryWaypointRepository(InMemoryWorldEntityRepository[Waypoint]):
    """In-memory repository for Waypoint (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryWeaponSystemRepository(InMemoryWorldEntityRepository[WeaponSystem]):
    """In-memory repository for WeaponSystem (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryWeapon_systemRepository(InMemoryWorldEntityRepository[WeaponSystem]):
    """In-memory repository for WeaponSystem (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryWitnessRepository(InMemoryWorldEntityRepository[Witness]):
    """In-memory repository for Witness (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryWorkshopEntryRepository(InMemoryWorldEntityRepository[WorkshopEntry]):
    """In-memory repository for WorkshopEntry (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryWorkshop_entryRepository(InMemoryWorldEntityRepository[WorkshopEntry]):
    """In-memory repository for WorkshopEntry (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryWormholeRepository(InMemoryWorldEntityRepository[Wormhole]):
    """In-memory repository for Wormhole (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass
