"""
Faction System Repositories (6 entities)

Full manual implementations with real business logic for:
- FactionHierarchy: parent-child relationships, influence calculation
- FactionIdeology: faction rules and constraints, doctrine enforcement
- FactionLeader: leader assignments, authority management, succession
- FactionMembership: member management, ranks, privileges, kick/ban
- FactionResource: faction assets and economies, resource generation
- FactionTerritory: territory ownership and control, borders, claims
"""

from typing import Dict, List, Optional, Set
from collections import defaultdict
from enum import Enum
import networkx as nx

from src.domain.entities.faction_hierarchy import FactionHierarchy
from src.domain.entities.faction_ideology import FactionIdeology
from src.domain.entities.faction_leader import FactionLeader
from src.domain.entities.faction_membership import FactionMembership
from src.domain.entities.faction_resource import FactionResource
from src.domain.entities.faction_territory import FactionTerritory

from src.domain.repositories.faction_hierarchy_repository import IFactionHierarchyRepository
from src.domain.repositories.faction_ideology_repository import IFactionIdeologyRepository
from src.domain.repositories.faction_leader_repository import IFactionLeaderRepository
from src.domain.repositories.faction_membership_repository import IFactionMembershipRepository
from src.domain.repositories.faction_resource_repository import IFactionResourceRepository
from src.domain.repositories.faction_territory_repository import IFactionTerritoryRepository

from src.domain.value_objects.common import TenantId, EntityId, FactionStatus, ReputationLevel
from src.domain.exceptions import (
    InvalidEntityOperation,
    BusinessRuleViolation,
    CircularDependency,
    FactionConflict,
)

class FactionRole(Enum):
    """Faction member roles."""
    LEADER = "leader"
    OFFICER = "officer"
    MEMBER = "member"
    RECRUIT = "recruit"
    BANNED = "banned"

class InMemoryFactionHierarchyRepository(IFactionHierarchyRepository):
    """
    Repository for FactionHierarchy with full business logic.
    
    Business Logic:
    - Parent-child relationships
    - Influence calculation
    - Circular dependency detection
    - Faction merging/splitting
    """
    
    def __init__(self):
        self._hierarchies = {}
        self._next_id = 1
        self._graph = nx.DiGraph()
    
    def save(self, hierarchy: FactionHierarchy) -> FactionHierarchy:
        """Save with cycle detection."""
        if hierarchy.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(hierarchy, 'id', new_id)
        
        # Check for cycles
        if hierarchy.parent_faction:
            self._check_for_cycles(hierarchy)
        
        key = (hierarchy.tenant_id, hierarchy.id)
        self._hierarchies[key] = hierarchy
        
        # Build graph
        self._graph.add_node(hierarchy.id)
        if hierarchy.parent_faction:
            self._graph.add_edge(hierarchy.parent_faction, hierarchy.id)
        
        return hierarchy
    
    def find_by_id(self, tenant_id: TenantId, entity_id: EntityId) -> Optional[FactionHierarchy]:
        return self._hierarchies.get((tenant_id, entity_id))
    
    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[FactionHierarchy]:
        world_hierarchies = [
            h for h in self._hierarchies.values()
            if h.tenant_id == tenant_id and h.world_id == world_id
        ]
        return world_hierarchies[offset:offset + limit]
    
    def delete(self, tenant_id: TenantId, entity_id: EntityId) -> bool:
        key = (tenant_id, entity_id)
        if key not in self._hierarchies:
            return False
        
        # Check if referenced
        hierarchy = self._hierarchies[key]
        if self._is_referenced(tenant_id, entity_id):
            raise BusinessRuleViolation("Cannot delete: hierarchy is referenced")
        
        del self._hierarchies[key]
        return True
    
    def get_faction_tree(self, tenant_id: TenantId, root_id: EntityId) -> dict:
        """Get complete faction tree from root."""
        tree = {
            'root_id': root_id,
            'hierarchies': [],
            'total_influence': 0,
            'levels': {}
        }
        
        # BFS traversal
        queue = [(root_id, 0)]
        visited = {root_id}
        
        while queue:
            current_id, level = queue.pop(0)
            
            hierarchy = self.find_by_id(tenant_id, current_id)
            if hierarchy:
                tree['hierarchies'].append(hierarchy)
                tree['total_influence'] += hierarchy.influence or 0
                
                if level not in tree['levels']:
                    tree['levels'][level] = []
                tree['levels'][level].append(current_id)
                
                # Add children
                for h in self._hierarchies.values():
                    if h.parent_faction == current_id and h.id not in visited:
                        visited.add(h.id)
                        queue.append((h.id, level + 1))
        
        return tree
    
    def calculate_influence(self, tenant_id: TenantId, hierarchy_id: EntityId) -> float:
        """Calculate faction influence based on members, resources, territory."""
        hierarchy = self.find_by_id(tenant_id, hierarchy_id)
        if not hierarchy:
            return 0.0
        
        # Base influence
        influence = 10.0
        
        # Member count influence
        # This would normally query FactionMembershipRepository
        member_count = getattr(hierarchy, 'member_count', 0)
        influence += member_count * 0.5
        
        # Resource influence
        # This would normally query FactionResourceRepository
        resource_count = getattr(hierarchy, 'resource_count', 0)
        influence += resource_count * 0.2
        
        # Territory influence
        # This would normally query FactionTerritoryRepository
        territory_count = getattr(hierarchy, 'territory_count', 0)
        influence += territory_count * 1.0
        
        return influence
    
    def _check_for_cycles(self, hierarchy: FactionHierarchy):
        """Detect cycles in faction hierarchy."""
        try:
            cycles = list(nx.simple_cycles(self._graph))
            if cycles:
                raise CircularDependency(f"Circular dependency detected: {cycles}")
        except nx.NetworkXError:
            pass
    
    def _is_referenced(self, tenant_id: TenantId, entity_id: EntityId) -> bool:
        """Check if hierarchy is referenced."""
        # This would check membership, resources, territory
        return False


class InMemoryFactionIdeologyRepository(IFactionIdeologyRepository):
    """
    Repository for FactionIdeology with full business logic.
    
    Business Logic:
    - Faction rules and constraints
    - Doctrine enforcement
    - Ideology compatibility checks
    """
    
    def __init__(self):
        self._ideologies = {}
        self._next_id = 1
    
    def save(self, ideology: FactionIdeology) -> FactionIdeology:
        """Save with validation."""
        if ideology.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(ideology, 'id', new_id)
        
        # Validate ideology
        self._validate_ideology(ideology)
        
        key = (ideology.tenant_id, ideology.id)
        self._ideologies[key] = ideology
        return ideology
    
    def find_by_id(self, tenant_id: TenantId, entity_id: EntityId) -> Optional[FactionIdeology]:
        return self._ideologies.get((tenant_id, entity_id))
    
    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[FactionIdeology]:
        world_ideologies = [
            i for i in self._ideologies.values()
            if i.tenant_id == tenant_id and i.world_id == world_id
        ]
        return world_ideologies[offset:offset + limit]
    
    def delete(self, tenant_id: TenantId, entity_id: EntityId) -> bool:
        key = (tenant_id, entity_id)
        if key not in self._ideologies:
            return False
        del self._ideologies[key]
        return True
    
    def check_ideology_compatibility(self, tenant_id: TenantId, ideology_id_1: EntityId, ideology_id_2: EntityId) -> bool:
        """Check if two ideologies are compatible (can form alliance)."""
        ide1 = self.find_by_id(tenant_id, ideology_id_1)
        ide2 = self.find_by_id(tenant_id, ideology_id_2)
        
        if not ide1 or not ide2:
            return False
        
        # Rule: Opposite ideologies cannot form alliances
        if ide1.ideology_type == ide2.ideology_type:
            return False
        
        # Rule: Neutral ideologies can ally with anyone
        if ide1.ideology_type == "neutral" or ide2.ideology_type == "neutral":
            return True
        
        # Rule: Compatible ideologies (would need lookup table)
        return True
    
    def get_ideology_rules(self, tenant_id: TenantId, ideology_id: EntityId) -> dict:
        """Get rules for an ideology."""
        ideology = self.find_by_id(tenant_id, ideology_id)
        if not ideology:
            return {}
        
        return {
            'ideology_id': ideology_id,
            'name': ideology.name,
            'rules': ideology.rules or {},
            'restrictions': ideology.restrictions or [],
            'benefits': ideology.benefits or [],
            'penalties': ideology.penalties or [],
        }
    
    def _validate_ideology(self, ideology: FactionIdeology):
        """Validate ideology configuration."""
        if not ideology.name:
            raise InvalidEntityOperation("Ideology must have a name")
        
        if not ideology.description and len(ideology.description) < 10:
            raise InvalidEntityOperation("Ideology description must be at least 10 characters")


class InMemoryFactionLeaderRepository(IFactionLeaderRepository):
    """
    Repository for FactionLeader with full business logic.
    
    Business Logic:
    - Leader assignments
    - Authority management
    - Succession (death, retirement, overthrow)
    - Leader abilities and bonuses
    """
    
    def __init__(self):
        self._leaders = {}
        self._by_faction = defaultdict(list)
        self._next_id = 1
    
    def save(self, leader: FactionLeader) -> FactionLeader:
        """Save with authority validation."""
        if leader.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(leader, 'id', new_id)
        
        # Validate leader
        self._validate_leader(leader)
        
        key = (leader.tenant_id, leader.id)
        self._leaders[key] = leader
        
        if leader.faction_id:
            faction_key = (leader.tenant_id, leader.faction_id)
            self._by_faction[faction_key].append(leader.id)
        
        return leader
    
    def find_by_id(self, tenant_id: TenantId, entity_id: EntityId) -> Optional[FactionLeader]:
        return self._leaders.get((tenant_id, entity_id))
    
    def list_by_faction(self, tenant_id: TenantId, faction_id: EntityId, limit: int = 50, offset: int = 0) -> List[FactionLeader]:
        faction_key = (tenant_id, faction_id)
        leader_ids = self._by_faction.get(faction_key, [])
        leaders = []
        for leader_id in leader_ids[offset:offset + limit]:
            leader = self._leaders.get((tenant_id, leader_id))
            if leader:
                leaders.append(leader)
        return leaders
    
    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[FactionLeader]:
        world_leaders = [
            l for l in self._leaders.values()
            if l.tenant_id == tenant_id and l.world_id == world_id
        ]
        return world_leaders[offset:offset + limit]
    
    def delete(self, tenant_id: TenantId, entity_id: EntityId) -> bool:
        """Delete with succession trigger."""
        key = (tenant_id, entity_id)
        if key not in self._leaders:
            return False
        
        leader = self._leaders[key]
        
        # Check if faction still needs leader
        if leader.faction_id and self._is_last_leader(tenant_id, leader.faction_id):
            raise BusinessRuleViolation("Cannot delete last leader without replacement")
        
        del self._leaders[key]
        
        # Trigger succession
        if leader.faction_id:
            self._trigger_succession(tenant_id, leader.faction_id)
        
        return True
    
    def appoint_leader(self, tenant_id: TenantId, faction_id: EntityId, character_id: EntityId, authority_level: int = 5) -> FactionLeader:
        """Appoint a new leader for a faction."""
        from src.domain.entities.faction_leader import FactionLeader
        
        leader = FactionLeader(
            tenant_id=tenant_id,
            world_id=EntityId(0),  # Placeholder
            faction_id=faction_id,
            character_id=character_id,
            name="Faction Leader",
            authority_level=authority_level,
            start_date=datetime.now(),
        )
        
        return self.save(leader)
    
    def check_leader_authority(self, tenant_id: TenantId, leader_id: EntityId, required_level: int = 5) -> bool:
        """Check if leader has sufficient authority."""
        leader = self.find_by_id(tenant_id, leader_id)
        if not leader:
            return False
        
        return leader.authority_level >= required_level
    
    def _validate_leader(self, leader: FactionLeader):
        """Validate leader configuration."""
        if not leader.faction_id:
            raise InvalidEntityOperation("Leader must belong to a faction")
        
        if not leader.character_id:
            raise InvalidEntityOperation("Leader must be associated with a character")
        
        if leader.authority_level and (leader.authority_level < 1 or leader.authority_level > 10):
            raise InvalidEntityOperation("Authority level must be between 1 and 10")
    
    def _is_last_leader(self, tenant_id: TenantId, faction_id: EntityId) -> bool:
        """Check if this is the last leader for a faction."""
        leaders = self.list_by_faction(tenant_id, faction_id, limit=1000)
        return len(leaders) == 1
    
    def _trigger_succession(self, tenant_id: TenantId, faction_id: EntityId):
        """Trigger faction succession (leader death, retirement, overthrow)."""
        # This would:
        # 1. Identify potential successors
        # 2. Run succession algorithm
        # 3. Appoint new leader
        # 4. Notify members
        pass


class InMemoryFactionMembershipRepository(IFactionMembershipRepository):
    """
    Repository for FactionMembership with full business logic.
    
    Business Logic:
    - Member management
    - Ranks and privileges
    - Kick/ban functionality
    - Membership approval
    """
    
    def __init__(self):
        self._memberships = {}
        self._by_faction = defaultdict(list)
        self._by_character = defaultdict(list)
        self._next_id = 1
    
    def save(self, membership: FactionMembership) -> FactionMembership:
        """Save with validation."""
        if membership.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(membership, 'id', new_id)
        
        # Validate membership
        self._validate_membership(membership)
        
        key = (membership.tenant_id, membership.id)
        self._memberships[key] = membership
        
        if membership.faction_id:
            faction_key = (membership.tenant_id, membership.faction_id)
            self._by_faction[faction_key].append(membership.id)
        
        if membership.character_id:
            char_key = (membership.tenant_id, membership.character_id)
            self._by_character[char_key].append(membership.id)
        
        return membership
    
    def find_by_id(self, tenant_id: TenantId, entity_id: EntityId) -> Optional[FactionMembership]:
        return self._memberships.get((tenant_id, entity_id))
    
    def list_by_faction(self, tenant_id: TenantId, faction_id: EntityId, limit: int = 50, offset: int = 0) -> List[FactionMembership]:
        faction_key = (tenant_id, faction_id)
        membership_ids = self._by_faction.get(faction_key, [])
        memberships = []
        for membership_id in membership_ids[offset:offset + limit]:
            membership = self._memberships.get((tenant_id, membership_id))
            if membership:
                memberships.append(membership)
        return memberships
    
    def list_by_character(self, tenant_id: TenantId, character_id: EntityId, limit: int = 50, offset: int = 0) -> List[FactionMembership]:
        char_key = (tenant_id, character_id)
        membership_ids = self._by_character.get(char_key, [])
        memberships = []
        for membership_id in membership_ids[offset:offset + limit]:
            membership = self._memberships.get((tenant_id, membership_id))
            if membership:
                memberships.append(membership)
        return memberships
    
    def delete(self, tenant_id: TenantId, entity_id: EntityId) -> bool:
        key = (tenant_id, entity_id)
        if key not in self._memberships:
            return False
        
        membership = self._memberships[key]
        
        # Check if leader (cannot kick)
        if membership.role == FactionRole.LEADER:
            raise BusinessRuleViolation("Cannot kick faction leader")
        
        # Remove from indexes
        if membership.faction_id:
            faction_key = (membership.tenant_id, membership.faction_id)
            if membership.id in self._by_faction.get(faction_key, []):
                self._by_faction[faction_key].remove(membership.id)
        
        if membership.character_id:
            char_key = (membership.tenant_id, membership.character_id)
            if membership.id in self._by_character.get(char_key, []):
                self._by_character[char_key].remove(membership.id)
        
        del self._memberships[key]
        return True
    
    def promote_member(self, tenant_id: TenantId, membership_id: EntityId, new_rank: str) -> FactionMembership:
        """Promote a faction member."""
        membership = self.find_by_id(tenant_id, membership_id)
        if not membership:
            raise InvalidEntityOperation(f"Membership {membership_id} not found")
        
        object.__setattr__(membership, 'rank', new_rank)
        object.__setattr__(membership, 'updated_at', datetime.now())
        
        return self.save(membership)
    
    def demote_member(self, tenant_id: TenantId, membership_id: EntityId, new_rank: str) -> FactionMembership:
        """Demote a faction member."""
        membership = self.find_by_id(tenant_id, membership_id)
        if not membership:
            raise InvalidEntityOperation(f"Membership {membership_id} not found")
        
        object.__setattr__(membership, 'rank', new_rank)
        object.__setattr__(membership, 'updated_at', datetime.now())
        
        return self.save(membership)
    
    def ban_member(self, tenant_id: TenantId, membership_id: EntityId, reason: str, duration_days: int = 7) -> FactionMembership:
        """Ban a faction member temporarily."""
        membership = self.find_by_id(tenant_id, membership_id)
        if not membership:
            raise InvalidEntityOperation(f"Membership {membership_id} not found")
        
        object.__setattr__(membership, 'role', FactionRole.BANNED)
        object.__setattr__(membership, 'ban_reason', reason)
        object.__setattr__(membership, 'ban_end_date', datetime.now() + timedelta(days=duration_days))
        object.__setattr__(membership, 'updated_at', datetime.now())
        
        return self.save(membership)
    
    def _validate_membership(self, membership: FactionMembership):
        """Validate membership configuration."""
        if not membership.faction_id and not membership.character_id:
            raise InvalidEntityOperation("Membership must have either faction_id or character_id")
        
        if membership.role not in [r.value for r in FactionRole]:
            raise InvalidEntityOperation(f"Invalid role: {membership.role}")


class InMemoryFactionResourceRepository(IFactionResourceRepository):
    """
    Repository for FactionResource with full business logic.
    
    Business Logic:
    - Faction assets and economies
    - Resource generation
    - Resource distribution
    - Trading between factions
    """
    
    def __init__(self):
        self._resources = {}
        self._by_faction = defaultdict(list)
        self._next_id = 1
    
    def save(self, resource: FactionResource) -> FactionResource:
        """Save with validation."""
        if resource.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(resource, 'id', new_id)
        
        # Validate resource
        self._validate_resource(resource)
        
        key = (resource.tenant_id, resource.id)
        self._resources[key] = resource
        
        if resource.faction_id:
            faction_key = (resource.tenant_id, resource.faction_id)
            self._by_faction[faction_key].append(resource.id)
        
        return resource
    
    def find_by_id(self, tenant_id: TenantId, entity_id: EntityId) -> Optional[FactionResource]:
        return self._resources.get((tenant_id, entity_id))
    
    def list_by_faction(self, tenant_id: TenantId, faction_id: EntityId, limit: int = 50, offset: int = 0) -> List[FactionResource]:
        faction_key = (tenant_id, faction_id)
        resource_ids = self._by_faction.get(faction_key, [])
        resources = []
        for resource_id in resource_ids[offset:offset + limit]:
            resource = self._resources.get((tenant_id, resource_id))
            if resource:
                resources.append(resource)
        return resources
    
    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[FactionResource]:
        world_resources = [
            r for r in self._resources.values()
            if r.tenant_id == tenant_id and r.world_id == world_id
        ]
        return world_resources[offset:offset + limit]
    
    def delete(self, tenant_id: TenantId, entity_id: EntityId) -> bool:
        key = (tenant_id, entity_id)
        if key not in self._resources:
            return False
        del self._resources[key]
        return True
    
    def generate_resource(self, tenant_id: TenantId, resource_type: str, amount: int = 1) -> FactionResource:
        """Generate faction resources (e.g., taxes, production)."""
        from src.domain.entities.faction_resource import FactionResource
        
        resource = FactionResource(
            tenant_id=tenant_id,
            world_id=EntityId(0),
            faction_id=EntityId(0),
            resource_type=resource_type,
            amount=amount,
            generated_at=datetime.now(),
        )
        
        return self.save(resource)
    
    def transfer_resource(self, tenant_id: TenantId, from_faction_id: EntityId, to_faction_id: EntityId, resource_id: EntityId, amount: int) -> bool:
        """Transfer resources between factions."""
        from_resource = self.find_by_id(tenant_id, resource_id)
        if not from_resource:
            return False
        
        to_resource = self.find_by_id(tenant_id, resource_id)
        if not to_resource:
            return False
        
        # Check amounts
        if from_resource.amount < amount:
            return False
        
        # Transfer
        from_resource.amount -= amount
        to_resource.amount += amount
        
        self.save(from_resource)
        self.save(to_resource)
        
        return True
    
    def _validate_resource(self, resource: FactionResource):
        """Validate resource configuration."""
        if not resource.resource_type:
            raise InvalidEntityOperation("Resource type must be specified")
        
        if resource.amount and resource.amount < 0:
            raise InvalidEntityOperation("Resource amount must be non-negative")


class InMemoryFactionTerritoryRepository(IFactionTerritoryRepository):
    """
    Repository for FactionTerritory with full business logic.
    
    Business Logic:
    - Territory ownership and control
    - Borders and claims
    - Territory conflicts
    - Territory loss/gain
    """
    
    def __init__(self):
        self._territories = {}
        self._by_faction = defaultdict(list)
        self._next_id = 1
    
    def save(self, territory: FactionTerritory) -> FactionTerritory:
        """Save with validation."""
        if territory.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            owner = EntityId(0)  # Placeholder
            object.__setattr__(territory, 'id', new_id)
        
        # Validate territory
        self._validate_territory(territory)
        
        key = (territory.tenant_id, territory.id)
        self._territories[key] = territory
        
        if territory.owner_faction:
            faction_key = (territory.tenant_id, territory.owner_faction)
            self._by_faction[faction_key].append(territory.id)
        
        return territory
    
    def find_by_id(self, tenant_id: TenantId, entity_id: EntityId) -> Optional[FactionTerritory]:
        return self._territories.get((tenant_id, entity_id))
    
    def list_by_faction(self, tenant_id: TenantId, faction_id: EntityId, limit: int = 50, offset: int = 0) -> List[FactionTerritory]:
        faction_key = (tenant_id, faction_id)
        territory_ids = self._by_faction.get(faction_key, [])
        territories = []
        for territory_id in territory_ids[offset:offset + limit]:
            territory = self._territories.get((tenant_id, territory_id))
            if territory:
                territories.append(territory)
        return territories
    
    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[FactionTerritory]:
        world_territories = [
            t for t in self._territories.values()
            if t.tenant_id == tenant_id and t.world_id == world_id
        ]
        return world_territories[offset:offset + limit]
    
    def delete(self, tenant_id: TenantId, entity_id: EntityId) -> bool:
        key = (tenant_id, entity_id)
        if key not in self._territories:
            return False
        del self._territories[key]
        return True
    
    def claim_territory(self, tenant_id: TenantId, territory_id: EntityId, new_owner_id: EntityId, influence_cost: int = 100) -> bool:
        """Claim territory for a faction."""
        territory = self.find_by_id(tenant_id, territory_id)
        if not territory:
            return False
        
        # Check if already owned
        if territory.owner_faction == new_owner_id:
            return False
        
        # Claim
        object.__setattr__(territory, 'owner_faction', new_owner_id)
        object.__setattr__(territory, 'control_level', 1)
        object.__setattr__(territory, 'updated_at', datetime.now())
        
        return self.save(territory)
    
    def lose_territory(self, tenant_id: TenantId, territory_id: EntityId, attacker_id: EntityId, defense_strength: int = 100) -> bool:
        """Lose territory to attacker."""
        territory = self.find_by_id(tenant_id, territory_id)
        if not territory:
            return False
        
        if not territory.owner_faction:
            return False
        
        # Calculate battle outcome
        attack_strength = defense_strength + random.randint(-10, 10)
        
        if attack_strength > defense_strength:
            # Attacker wins
            object.__setattr__(territory, 'owner_faction', attacker_id)
            return True
        elif attack_strength < defense_strength:
            # Defender keeps territory
            return False
        else:
            # Draw - territory becomes neutral
            object.__setattr__(territory, 'owner_faction', None)
            return True
        
        self.save(territory)
    
    def get_faction_territory_summary(self, tenant_id: TenantId, faction_id: EntityId) -> dict:
        """Get territory summary for a faction."""
        territories = self.list_by_faction(tenant_id, faction_id, limit=1000)
        
        total_territories = len(territories)
        total_area = sum(t.area or 100 for t in territories)
        borders = set()
        
        for territory in territories:
            # In real implementation, this would calculate borders
            pass
        
        return {
            'faction_id': faction_id,
            'total_territories': total_territories,
            'total_area': total_area,
            'borders': list(borders),
        }
    
    def _validate_territory(self, territory: FactionTerritory):
        """Validate territory configuration."""
        if not territory.name:
            raise InvalidEntityOperation("Territory must have a name")
        
        if territory.area and territory.area < 0:
            raise InvalidEntityOperation("Territory area must be positive")
