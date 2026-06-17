"""In-memory repositories for faction/politics/religion entities.

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

from src.domain.entities.constitution import Constitution
from src.domain.entities.court import Court
from src.domain.entities.faction_hierarchy import FactionHierarchy
from src.domain.entities.faction_ideology import FactionIdeology
from src.domain.entities.faction_leader import FactionLeader
from src.domain.entities.faction_resource import FactionResource
from src.domain.entities.faction_territory import FactionTerritory
from src.domain.entities.lawyer import Lawyer
from src.domain.entities.miracle import Miracle
from src.domain.entities.social_class import SocialClass
from src.domain.entities.social_media import SocialMedia
from src.domain.entities.social_mobility import SocialMobility
from src.domain.entities.war import War
from src.domain.entities.ward import Ward

class InMemoryAllianceRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for AllianceType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryConstitutionRepository(InMemoryWorldEntityRepository[Constitution]):
    """In-memory repository for Constitution (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryCourtRepository(InMemoryWorldEntityRepository[Court]):
    """In-memory repository for Court (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryDeusExMachinaRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for DeusExMachinaType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryEmpireRepository:
    def __init__(self):
        self._empires = {}
        self._next_id = 1
    def save(self, empire):
        if empire.id is None:
            from src.domain.value_objects.common import EntityId
            empire.id = EntityId(self._next_id)
            self._next_id += 1
        self._empires[(empire.tenant_id, empire.id)] = empire
        return empire
    def find_by_id(self, tenant_id, empire_id):
        return self._empires.get((tenant_id, empire_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [e for e in self._empires.values() if e.tenant_id == tenant_id and e.world_id == world_id][offset:offset+limit]
    def list_by_nation(self, tenant_id, nation_id, limit=50, offset=0):
        return [e for e in self._empires.values() if e.tenant_id == tenant_id and e.nation_id == nation_id][offset:offset+limit]
    def delete(self, tenant_id, empire_id):
        key = (tenant_id, empire_id)
        if key in self._empires:
            del self._empires[key]
            return True
        return False


class InMemoryFactionHierarchyRepository(InMemoryWorldEntityRepository[FactionHierarchy]):
    """In-memory repository for FactionHierarchy (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFactionIdeologyRepository(InMemoryWorldEntityRepository[FactionIdeology]):
    """In-memory repository for FactionIdeology (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFactionLeaderRepository(InMemoryWorldEntityRepository[FactionLeader]):
    """In-memory repository for FactionLeader (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFactionMembershipRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for MembershipRank (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryFactionRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for FactionType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryFactionResourceRepository(InMemoryWorldEntityRepository[FactionResource]):
    """In-memory repository for FactionResource (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFactionTerritoryRepository(InMemoryWorldEntityRepository[FactionTerritory]):
    """In-memory repository for FactionTerritory (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFaction_hierarchyRepository(InMemoryWorldEntityRepository[FactionHierarchy]):
    """In-memory repository for FactionHierarchy (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFaction_ideologyRepository(InMemoryWorldEntityRepository[FactionIdeology]):
    """In-memory repository for FactionIdeology (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFaction_leaderRepository(InMemoryWorldEntityRepository[FactionLeader]):
    """In-memory repository for FactionLeader (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFaction_membershipRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for MembershipRank (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryFaction_resourceRepository(InMemoryWorldEntityRepository[FactionResource]):
    """In-memory repository for FactionResource (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryFaction_territoryRepository(InMemoryWorldEntityRepository[FactionTerritory]):
    """In-memory repository for FactionTerritory (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryGovernmentRepository:
    def __init__(self):
        self._governments = {}
        self._next_id = 1
    def save(self, government):
        if government.id is None:
            from src.domain.value_objects.common import EntityId
            government.id = EntityId(self._next_id)
            self._next_id += 1
        self._governments[(government.tenant_id, government.id)] = government
        return government
    def find_by_id(self, tenant_id, government_id):
        return self._governments.get((tenant_id, government_id))
    def list_by_nation(self, tenant_id, nation_id, limit=50, offset=0):
        return [g for g in self._governments.values() if g.tenant_id == tenant_id and g.nation_id == nation_id][offset:offset+limit]
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [g for g in self._governments.values() if g.tenant_id == tenant_id and g.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, government_id):
        key = (tenant_id, government_id)
        if key in self._governments:
            del self._governments[key]
            return True
        return False


class InMemoryKingdomRepository:
    def __init__(self):
        self._kingdoms = {}
        self._next_id = 1
    def save(self, kingdom):
        if kingdom.id is None:
            from src.domain.value_objects.common import EntityId
            kingdom.id = EntityId(self._next_id)
            self._next_id += 1
        self._kingdoms[(kingdom.tenant_id, kingdom.id)] = kingdom
        return kingdom
    def find_by_id(self, tenant_id, kingdom_id):
        return self._kingdoms.get((tenant_id, kingdom_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [k for k in self._kingdoms.values() if k.tenant_id == tenant_id and k.world_id == world_id][offset:offset+limit]
    def list_by_nation(self, tenant_id, nation_id, limit=50, offset=0):
        return [k for k in self._kingdoms.values() if k.tenant_id == tenant_id and k.nation_id == nation_id][offset:offset+limit]
    def delete(self, tenant_id, kingdom_id):
        key = (tenant_id, kingdom_id)
        if key in self._kingdoms:
            del self._kingdoms[key]
            return True
        return False


class InMemoryLawRepository:
    def __init__(self):
        self._laws = {}
        self._next_id = 1
    def save(self, law):
        if law.id is None:
            from src.domain.value_objects.common import EntityId
            law.id = EntityId(self._next_id)
            self._next_id += 1
        self._laws[(law.tenant_id, law.id)] = law
        return law
    def find_by_id(self, tenant_id, law_id):
        return self._laws.get((tenant_id, law_id))
    def list_by_constitution(self, tenant_id, constitution_id, limit=50, offset=0):
        return [l for l in self._laws.values() if l.tenant_id == tenant_id and l.constitution_id == constitution_id][offset:offset+limit]
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [l for l in self._laws.values() if l.tenant_id == tenant_id and l.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, law_id):
        key = (tenant_id, law_id)
        if key in self._laws:
            del self._laws[key]
            return True
        return False


class InMemoryLawyerRepository(InMemoryWorldEntityRepository[Lawyer]):
    """In-memory repository for Lawyer (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryLegalSystemRepository:
    def __init__(self):
        self._systems = {}
        self._next_id = 1
    def save(self, legal_system):
        if legal_system.id is None:
            from src.domain.value_objects.common import EntityId
            legal_system.id = EntityId(self._next_id)
            self._next_id += 1
        self._systems[(legal_system.tenant_id, legal_system.id)] = legal_system
        return legal_system
    def find_by_id(self, tenant_id, system_id):
        return self._systems.get((tenant_id, system_id))
    def list_by_nation(self, tenant_id, nation_id, limit=50, offset=0):
        return [s for s in self._systems.values() if s.tenant_id == tenant_id and s.nation_id == nation_id][offset:offset+limit]
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [s for s in self._systems.values() if s.tenant_id == tenant_id and s.world_id == world_id][offset:offset+limit]
    def delete(self, tenant_id, system_id):
        key = (tenant_id, system_id)
        if key in self._systems:
            del self._systems[key]
            return True
        return False


class InMemoryLegal_systemRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for LegalSystemType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryMiracleRepository(InMemoryWorldEntityRepository[Miracle]):
    """In-memory repository for Miracle (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryNationRepository:
    def __init__(self):
        self._nations = {}
        self._next_id = 1
    def save(self, nation):
        if nation.id is None:
            from src.domain.value_objects.common import EntityId
            nation.id = EntityId(self._next_id)
            self._next_id += 1
        self._nations[(nation.tenant_id, nation.id)] = nation
        return nation
    def find_by_id(self, tenant_id, nation_id):
        return self._nations.get((tenant_id, nation_id))
    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [n for n in self._nations.values() if n.tenant_id == tenant_id and n.world_id == world_id][offset:offset+limit]
    def list_by_alliance(self, tenant_id, alliance_id, limit=50, offset=0):
        return [n for n in self._nations.values() if n.tenant_id == tenant_id and n.alliance_id == alliance_id][offset:offset+limit]
    def delete(self, tenant_id, nation_id):
        key = (tenant_id, nation_id)
        if key in self._nations:
            del self._nations[key]
            return True
        return False


class InMemorySocialClassRepository(InMemoryWorldEntityRepository[SocialClass]):
    """In-memory repository for SocialClass (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySocialMediaRepository(InMemoryWorldEntityRepository[SocialMedia]):
    """In-memory repository for SocialMedia (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySocialMobilityRepository(InMemoryWorldEntityRepository[SocialMobility]):
    """In-memory repository for SocialMobility (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySocial_classRepository(InMemoryWorldEntityRepository[SocialClass]):
    """In-memory repository for SocialClass (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySocial_mediaRepository(InMemoryWorldEntityRepository[SocialMedia]):
    """In-memory repository for SocialMedia (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemorySocial_mobilityRepository(InMemoryWorldEntityRepository[SocialMobility]):
    """In-memory repository for SocialMobility (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryTreatyRepository(InMemoryWorldEntityRepository[Any]):
    """In-memory repository for TreatyType (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`).

    The entity module is missing or fails to import on this Python
    version; the generic param uses ``Any`` and CRUD works via duck-typing.
    """

    pass


class InMemoryWarRepository(InMemoryWorldEntityRepository[War]):
    """In-memory repository for War (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass


class InMemoryWardRepository(InMemoryWorldEntityRepository[Ward]):
    """In-memory repository for Ward (world-scoped CRUD via :class:`InMemoryWorldEntityRepository`)."""

    pass
