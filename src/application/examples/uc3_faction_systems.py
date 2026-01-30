"""
Example: Faction & Reputation Systems

This example demonstrates how AAA game dev studios can use
MythWeave's domain model to create and manage complex faction systems
with hierarchies, ideologies, reputation mechanics, and diplomatic relations.
"""

import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# Domain entities (in production, these would be imported from src.domain)
# For this example, we'll define minimal stubs
class Faction:
    """Faction entity stub for example."""
    def __init__(self, tenant_id, name, world_id, ideology_id, alignment, is_player_joinable, relations, territories, is_player_joinable, leaders, member_count, resources, ideology_id, leader_id, relations, territories, leaders, member_count, resources, ideology_id, leader_id, relations, territories, leaders, member_count, resources):
        self.tenant_id = tenant_id
        self.id = None
        self.name = name
        self.world_id = world_id
        self.alignment = alignment
        self.is_player_joinable = is_player_joinable
        self.relations = relations or {}
        self.territories = territories or []
        self.leaders = leaders or []
        self.member_count = member_count
        self.resources = resources
        self.ideology_id = ideology_id
        self.leader_id = leader_id
        self.relations = relations
        self.territories = territories
        self.leaders = leaders
        self.member_count = member_count
        self.resources = resources
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

class FactionHierarchy:
    """Faction hierarchy stub for example."""
    def __init__(self, tenant_id, faction_id, name, hierarchy_type, levels, created_at=None, updated_at=None):
        self.tenant_id = tenant_id
        self.id = None
        self.faction_id = faction_id
        self.name = name
        self.hierarchy_type = hierarchy_type
        self.levels = levels or []
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

class FactionIdeology:
    """Faction ideology stub for example."""
    def __init__(self, tenant_id, name, ideology_type, core_values, is_player_joinable):
        self.tenant_id = tenant_id
        self.id = None
        self.name = name
        self.ideology_type = ideology_type
        self.core_values = core_values
        self.is_player_joinable = is_player_joinable
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

class Reputation:
    """Reputation entity stub for example."""
    def __init__(self, tenant_id, player_id, faction_id, score, tier, created_at=None, updated_at=None):
        self.tenant_id = tenant_id
        self.id = None
        self.player_id = player_id
        self.faction_id = faction_id
        self.score = score
        self.tier = tier
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

def create_order_vs_chaos_factions(tenant_id: str, world_id: str) -> tuple[Faction, Faction]:
    """
    Create two opposing factions "Order vs Chaos" for RPG game.
    """
    
    # 1. Create Order faction
    order_ideology = FactionIdeology(
        tenant_id=tenant_id,
        name="Lawful Order",
        ideology_type="lawful_good",
        core_values=["order", "law", "justice"],
        is_player_joinable=True
    )
    
    order_faction = Faction(
        tenant_id=tenant_id,
        world_id=world_id,
        name="Order of Silver Hand",
        ideology_id=order_ideology.id,
        alignment="lawful_good",
        is_player_joinable=True,
        relations={"chaos": "hostile", "neutral": "neutral"},
        territories=[f"{world_id}:location_silver_capital"],
        member_count=10000,
        resources=[f"{world_id}:currency_gold"],
        ideology_id=order_ideology.id,
        leader_id=None,
        leaders=[],
        relations={"chaos": "hostile", "neutral": "neutral"},
        territories=[f"{world_id}:location_silver_capital"],
        leaders=[],
        member_count=10000,
        resources=[f"{world_id}:currency_gold"]
    )
    
    # 2. Create Order hierarchy
    order_leader = {
        "name": "Grand Commander Aethelgard",
        "title": "Grand Commander",
        "level": 4
    }
    
    order_levels = [
        {"level": 1, "title": "Recruit", "count": 10000},
        {"level": 2, "title": "Soldier", "count": 5000},
        {"level": 3, "title": "Captain", "count": 500},
        {"level": 4, "title": "Commander", "count": 50}
    ]
    
    order_hierarchy = FactionHierarchy(
        tenant_id=tenant_id,
        faction_id=order_faction.id,
        name="Order Hierarchy",
        hierarchy_type="military",
        levels=order_levels
    )
    
    # 3. Create Chaos faction
    chaos_ideology = FactionIdeology(
        tenant_id=tenant_id,
        name="Chaotic Liberation",
        ideology_type="chaotic_neutral",
        core_values=["freedom", "anarchy", "selfish_freedom"],
        is_player_joinable=True
    )
    
    chaos_faction = Faction(
        tenant_id=tenant_id,
        world_id=world_id,
        name="Chaos of Broken Chain",
        ideology_id=chaos_ideology.id,
        alignment="chaotic_neutral",
        is_player_joinable=True,
        relations={"order": "hostile", "neutral": "neutral"},
        territories=[f"{world_id}:location_chaos_camp"],
        member_count=5000,
        resources=[f"{world_id}:currency_silver"],
        ideology_id=chaos_ideology.id,
        leader_id=None,
        leaders=[],
        relations={"order": "hostile", "neutral": "neutral"},
        territories=[f"{world_id}:location_chaos_camp"],
        leaders=[],
        member_count=5000,
        resources=[f"{world_id}:currency_silver"]
    )
    
    # 4. Create Chaos hierarchy
    chaos_leader = {
        "name": "Warlord Vex",
        "title": "Warlord",
        "level": 3
    }
    
    chaos_levels = [
        {"level": 1, "title": "Outlaw", "count": 5000},
        {"level": 2, "title": "Bandit", "count": 2000},
        {"level": 3, "title": "Warlord", "count": 200}
    ]
    
    chaos_hierarchy = FactionHierarchy(
        tenant_id=tenant_id,
        faction_id=chaos_faction.id,
        name="Chaos Hierarchy",
        hierarchy_type="tribal",
        levels=chaos_levels
    )
    
    # 5. Create reputation systems
    # Order faction reputation
    order_reputation = Reputation(
        tenant_id=tenant_id,
        player_id=f"{world_id}:player_hero",
        faction_id=order_faction.id,
        score=100,
        tier="revered"
    )
    
    # Chaos faction reputation
    chaos_reputation = Reputation(
        tenant_id=tenant_id,
        player_id=f"{world_id}:player_hero",
        faction_id=chaos_faction.id,
        score=0,  # Neutral starting reputation
        tier="unknown"
    )
    
    # 6. Create diplomatic relations
    treaty = {
        "name": "Temporary Truce",
        "description": "30-day truce between factions",
        "faction_a": order_faction.id,
        "faction_b": chaos_faction.id,
        "type": "peace",
        "duration_days": 30
    }
    
    alliance = {
        "name": "Silver League",
        "description": "Alliance of lawful kingdoms",
        "leader_faction_id": order_faction.id,
        "type": "military"
    }
    
    return order_faction, chaos_faction

# Example usage
if __name__ == "__main__":
    tenant_id = "tenant_001"
    world_id = "world_001"
    
    # Create factions
    order_faction, chaos_faction = create_order_vs_chaos_factions(tenant_id, world_id)
    
    print(f"✅ Faction Order created: {order_faction.name}")
    print(f"✅ Faction Chaos created: {chaos_faction.name}")
    print(f"📊 Member counts: {order_faction.member_count} (Order) vs {chaos_faction.member_count} (Chaos)")
    print(f"🎯 Alignment: {order_faction.alignment}")
    print(f"🏷️ Hierarchies: {len(order_faction.leaders)} (Order) vs {len(chaos_faction.leaders)} (Chaos)")
    print(f"🎬 Diplomatic relations: Truce ({treaty['duration_days']} days), Alliance ({alliance['type']})")
