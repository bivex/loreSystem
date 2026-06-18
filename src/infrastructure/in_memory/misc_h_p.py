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


