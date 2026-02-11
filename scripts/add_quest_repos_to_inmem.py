#!/usr/bin/env python3
"""
Add Quest repositories to in_memory_repositories.py
"""

import sys
from pathlib import Path

in_memory_path = Path("/root/clawd/src/infrastructure/in_memory_repositories.py")

# Quest repository implementations to append
quest_repos = '''
class InMemoryQuestChainRepository:
    """In-memory implementation of QuestChain repository."""
    def __init__(self):
        from typing import Dict, Optional, Tuple
        from collections import defaultdict
        from src.domain.value_objects.common import TenantId, EntityId
        
        self._quest_chains: Dict[Tuple[TenantId, EntityId], object] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], list] = defaultdict(list)
        self._next_id = 1

    def save(self, quest_chain):
        if quest_chain.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(quest_chain, 'id', new_id)
        self._quest_chains[(quest_chain.tenant_id, quest_chain.id)] = quest_chain
        world_key = (quest_chain.tenant_id, quest_chain.world_id) if hasattr(quest_chain, 'world_id') else None
        if world_key:
            if quest_chain.id not in self._by_world[world_key]:
                self._by_world[world_key].append(quest_chain.id)
        return quest_chain

    def find_by_id(self, tenant_id, entity_id):
        return self._quest_chains.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        world_key = (tenant_id, world_id)
        return [self._quest_chains[(tenant_id, qid)] for qid in self._by_world.get(world_key, [])[offset:offset+limit]]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._quest_chains:
            qc = self._quest_chains[key]
            world_key = (qc.tenant_id, qc.world_id) if hasattr(qc, 'world_id') else None
            if world_key and entity_id in self._by_world[world_key]:
                self._by_world[world_key].remove(entity_id)
            del self._quest_chains[key]
            return True
        return False


class InMemoryQuestNodeRepository:
    """In-memory implementation of QuestNode repository."""
    def __init__(self):
        self._quest_nodes = {}
        self._next_id = 1

    def save(self, quest_node):
        if quest_node.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(quest_node, 'id', new_id)
        self._quest_nodes[(quest_node.tenant_id, quest_node.id)] = quest_node
        return quest_node

    def find_by_id(self, tenant_id, entity_id):
        return self._quest_nodes.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [qn for qn in self._quest_nodes.values() if qn.tenant_id == tenant_id and qn.world_id == world_id][offset:offset+limit]]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._quest_nodes:
            del self._quest_nodes[key]
            return True
        return False


class InMemoryQuestPrerequisiteRepository:
    """In-memory implementation of QuestPrerequisite repository."""
    def __init__(self):
        self._prerequisites = {}
        self._next_id = 1

    def save(self, prereq):
        if prereq.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(prereq, 'id', new_id)
        self._prerequisites[(prereq.tenant_id, prereq.id)] = prereq
        return prereq

    def find_by_id(self, tenant_id, entity_id):
        return self._prerequisites.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [p for p in self._prerequisites.values() if p.tenant_id == tenant_id and p.world_id == world_id][offset:offset+limit]]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._prerequisites:
            del self._prerequisites[key]
            return True
        return False


class InMemoryQuestObjectiveRepository:
    """In-memory implementation of QuestObjective repository."""
    def __init__(self):
        self._objectives = {}
        self._next_id = 1

    def save(self, objective):
        if objective.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(objective, 'id', new_id)
        self._objectives[(objective.tenant_id, objective.id)] = objective
        return objective

    def find_by_id(self, tenant_id, entity_id):
        return self._objectives.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [o for o in self._objectives.values() if o.tenant_id == tenant_id and o.world_id == world_id][offset:offset+limit]]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._objectives:
            del self._objectives[key]
            return True
        return False


class InMemoryQuestTrackerRepository:
    """In-memory implementation of QuestTracker repository."""
    def __init__(self):
        self._trackers = {}
        self._next_id = 1

    def save(self, tracker):
        if tracker.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(tracker, 'id', new_id)
        self._trackers[(tracker.tenant_id, tracker.id)] = tracker
        return tracker

    def find_by_id(self, tenant_id, entity_id):
        return self._trackers.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._trackers.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._trackers:
            del self._trackers[key]
            return True
        return False


class InMemoryQuestGiverRepository:
    """In-memory implementation of QuestGiver repository."""
    def __init__(self):
        self._givers = {}
        self._next_id = 1

    def save(self, giver):
        if giver.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(giver, 'id', new_id)
        self._givers[(giver.tenant_id, giver.id)] = giver
        return giver

    def find_by_id(self, tenant_id, entity_id):
        return self._givers.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [g for g in self._givers.values() if g.tenant_id == tenant_id and g.world_id == world_id][offset:offset+limit]]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._givers:
            del self._givers[key]
            return True
        return False


class InMemoryQuestRewardRepository:
    """In-memory implementation of QuestReward repository."""
    def __init__(self):
        self._rewards = {}
        self._next_id = 1

    def save(self, reward):
        if reward.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(reward, 'id', new_id)
        self._rewards[(reward.tenant_id, reward.id)] = reward
        return reward

    def find_by_id(self, tenant_id, entity_id):
        return self._rewards.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [r for r in self._rewards.values() if r.tenant_id == tenant_id and r.world_id == world_id][offset:offset+limit]]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._rewards:
            del self._rewards[key]
            return True
        return False


class InMemoryQuestRewardTierRepository:
    """In-memory implementation of QuestRewardTier repository."""
    def __init__(self):
        self._tiers = {}
        self._next_id = 1

    def save(self, tier):
        if tier.id is None:
            from src.domain.value_objects.common import EntityId
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(tier, 'id', new_id)
        self._tiers[(tier.tenant_id, tier.id)] = tier
        return tier

    def find_by_id(self, tenant_id, entity_id):
        return self._tiers.get((tenant_id, entity_id))

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        return [t for t in self._tiers.values() if t.tenant_id == tenant_id and t.world_id == world_id][offset:offset+limit]]

    def delete(self, tenant_id, entity_id):
        key = (tenant_id, entity_id)
        if key in self._tiers:
            del self._tiers[key]
            return True
        return False
'''

# Append to file
with open(in_memory_path, 'a') as f:
    f.write(quest_repos)

print("✅ Added 8 Quest repository implementations to in_memory_repositories.py")
