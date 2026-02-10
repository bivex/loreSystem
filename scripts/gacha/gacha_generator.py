#!/usr/bin/env python3
"""
Gacha/Loot Box Generator for loreSystem

Generates balanced gacha pools, calculates drop rates, and creates
pity systems. Ensures fairness and player engagement.
"""

import json
import random
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math

class Rarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    DIVINE = "divine"

class PoolType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    MATERIAL = "material"


@dataclass
class Item:
    id: str
    name: str
    type: str
    rarity: str
    base_stats: Dict[str, Any]
    special_effects: List[str]
    lore: str
    sprite: str = None


@dataclass
class GachaPool:
    name: str
    pool_type: str
    items: List[Item]
    weights: Dict[str, float]
    pity_system: Dict[str, Any] = field(default_factory=dict)


def calculate_weighted_rarity(rarity_distribution: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate cumulative weights for rarity-based random selection.
    Ensures weights sum to 1.0 (100%).
    """
    # Normalize weights to ensure they sum to 1.0
    total = sum(rarity_distribution.values())
    normalized = {r: w/total for r, w in rarity_distribution.items()}
    
    # Calculate cumulative thresholds
    cumulative = {}
    running_total = 0.0
    for rarity, weight in sorted(normalized.items(), key=lambda x: x[1], reverse=True):
        running_total += weight
        cumulative[rarity] = running_total
    
    return {
        'normalized_weights': normalized,
        'cumulative_thresholds': cumulative,
        'total': total
    }


def roll_rarity(cumulative_thresholds: Dict[str, float]) -> str:
    """
    Roll for rarity based on cumulative thresholds.
    """
    roll = random.random() * 100.0
    for rarity, threshold in sorted(cumulative_thresholds.items(), key=lambda x: x[1], reverse=True):
        if roll <= threshold:
            return rarity
    return Rarity.COMMON.value


def generate_gacha_pool(
    pool_name: str,
    pool_type: str,
    items: List[Item],
    rarity_distribution: Dict[str, float]
    pity_config: Dict[str, Any] = None
) -> GachaPool:
    """
    Generate a gacha pool with balanced weights and pity system.
    """
    weights = calculate_weighted_rarity(rarity_distribution)
    
    pool = GachaPool(
        name=pool_name,
        pool_type=pool_type,
        items=items,
        weights=weights['normalized_weights'],
        pity_system=pity_config if pity_config else {
            'enabled': False,
            'threshold': None,
            'guaranteed_rarity': None,
            'pity_reset_on': None
        }
    )
    
    return pool


def pull_from_pool(pool: GachaPool, pity_state: Dict[str, int] = None) -> Tuple[Item, Dict[str, int]]:
    """
    Pull an item from a gacha pool, considering pity system.
    Returns the item and updated pity state.
    """
    # Roll rarity
    rarity = roll_rarity(pool.weights['cumulative_thresholds'])
    
    # Filter items by rarity
    rarity_items = [item for item in pool.items if item.rarity == rarity]
    if not rarity_items:
        raise ValueError(f"No items of rarity {rarity} in pool {pool.name}")
    
    # Check pity system
    pity_state = pity_state or {}
    pity_system = pool.pity_system
    
    if pity_system['enabled']:
        # Accumulate pity for this pool type
        pool_type = pool.pool_type
        if pool_type not in pity_state:
            pity_state[pool_type] = 0
        pity_state[pool_type] += 1
        
        # Check if pity threshold reached
        if pity_state[pool_type] >= pity_system['threshold']:
            # Guarantee specified rarity
            guaranteed_rarity = pity_system['guaranteed_rarity']
            guaranteed_items = [item for item in pool.items if item.rarity == guaranteed_rarity]
            
            if guaranteed_items:
                selected_item = random.choice(guaranteed_items)
                # Reset pity for this pool type
                pity_state[pool_type] = 0
                return selected_item, pity_state
        else:
            # Normal pull with rarity weights
            selected_item = random.choice(rarity_items)
            return selected_item, pity_state
    
    # No pity system - normal weighted pull
    else:
        return random.choice(rarity_items), pity_state


def create_default_weapon_pool() -> GachaPool:
    """Create default weapon gacha pool."""
    items = [
        Item(
            id="weapon_common_01",
            name="Rusty Sword",
            type="weapon",
            rarity=Rarity.COMMON.value,
            base_stats={"damage": 25, "speed": 1.0},
            special_effects=[],
            lore="Basic iron sword, rusted from years of use.",
            sprite="weapon_rusty_sword"
        ),
        Item(
            id="weapon_uncommon_01",
            name="Steel Blade",
            type="weapon",
            rarity=Rarity.UNCOMMON.value,
            base_stats={"damage": 40, "speed": 1.2},
            special_effects=["sharp_edge"],
            lore="Forged by Eldorian blacksmiths, slightly sharper than common swords.",
            sprite="weapon_steel_blade"
        ),
        Item(
            id="weapon_rare_01",
            name="Moonlight Saber",
            type="weapon",
            rarity=Rarity.RARE.value,
            base_stats={"damage": 60, "speed": 1.4},
            special_effects=["moonlight_glow", "night_vision"],
            lore="Forged under full moon, glimmers with pale light.",
            sprite="weapon_moonlight_saber"
        ),
        Item(
            id="weapon_epic_01",
            name="Shadow Strike",
            type="weapon",
            rarity=Rarity.EPIC.value,
            base_stats={"damage": 100, "speed": 1.6},
            special_effects=["shadow_meld", "backstab_bonus"],
            lore="Worn by the legendary assassin Shadow Weaver during Great War.",
            sprite="weapon_shadow_strike"
        ),
        Item(
            id="weapon_legendary_01",
            name="Blade of Astraea",
            type="weapon",
            rarity=Rarity.LEGENDARY.value,
            base_stats={"damage": 250, "speed": 1.8},
            special_effects=["divine_light_strike", "holy_damage"],
            lore="Forged by goddess Astraea during Age of Magic. Only three were ever made.",
            sprite="weapon_blade_astraea"
        ),
        Item(
            id="weapon_divine_01",
            name="Sword of Redemption",
            type="weapon",
            rarity=Rarity.DIVINE.value,
            base_stats={"damage": 350, "speed": 2.0},
            special_effects=["auto_heal", "purify", "holy_fire"],
            lore="Blessed by Astraea herself. Purges all corruption and heals wielder in combat.",
            sprite="weapon_sword_redemption"
        )
    ]
    
    rarity_distribution = {
        Rarity.COMMON.value: 45.0,  # 45%
        Rarity.UNCOMMON.value: 30.0,  # 30%
        Rarity.RARE.value: 15.0,  # 15%
        Rarity.EPIC.value: 7.0,  # 7%
        Rarity.LEGENDARY.value: 2.5,  # 2.5%
        Rarity.DIVINE.value: 0.5  # 0.5%
    }
    
    pity_config = {
        'enabled': True,
        'threshold': 80,
        'guaranteed_rarity': Rarity.LEGENDARY.value,
        'pity_reset_on': 'guaranteed_pull'
    }
    
    return generate_gacha_pool(
        pool_name="Default Weapon Pool",
        pool_type=PoolType.WEAPON.value,
        items=items,
        rarity_distribution=rarity_distribution,
        pity_config=pity_config
    )


def create_default_armor_pool() -> GachaPool:
    """Create default armor gacha pool."""
    items = [
        Item(
            id="armor_common_01",
            name="Leather Vest",
            type="armor",
            rarity=Rarity.COMMON.value,
            base_stats={"defense": 15, "weight": 5.0},
            special_effects=[],
            lore="Basic leather armor, offers minimal protection.",
            sprite="armor_leather_vest"
        ),
        Item(
            id="armor_uncommon_01",
            name="Chainmail Armor",
            type="armor",
            rarity=Rarity.UNCOMMON.value,
            base_stats={"defense": 30, "weight": 15.0},
            special_effects=["noise_reduction"],
            lore="Standard chainmail worn by Eldorian soldiers.",
            sprite="armor_chainmail"
        ),
        Item(
            id="armor_rare_01",
            name="Shadowweave Garb",
            type="armor",
            rarity=Rarity.RARE.value,
            base_stats={"defense": 50, "weight": 12.0},
            special_effects=["stealth_boost", "shadow_resistance"],
            lore="Woven by Shadow Cult weavers. Enhances stealth and resists shadow magic.",
            sprite="armor_shadowweave"
        ),
        Item(
            id="armor_epic_01",
            name="Dragon Scale Armor",
            type="armor",
            rarity=Rarity.EPIC.value,
            base_stats={"defense": 80, "weight": 20.0},
            special_effects=["fire_resistance", "dragon_protection"],
            lore="Forged from dragon scales by ancient smiths. Provides exceptional fire protection.",
            sprite="armor_dragon_scale"
        ),
        Item(
            id="armor_legendary_01",
            name="Mantle of the Oracle",
            type="armor",
            rarity=Rarity.LEGENDARY.value,
            base_stats={"defense": 120, "weight": 18.0},
            special_effects=["prophecy_vision", "resistance_all"],
            lore="Worn by the legendary oracle during Age of Magic. Grants visions of the future.",
            sprite="armor_mantle_oracle"
        ),
        Item(
            id="armor_divine_01",
            name="Astraea's Blessing",
            type="armor",
            rarity=Rarity.DIVINE.value,
            base_stats={"defense": 150, "weight": 22.0},
            special_effects=["divine_protection", "auto_ressurection", "light_aura"],
            lore="Blessed armor created by Astraea. Wearer becomes nearly invincible.",
            sprite="armor_blessing_astraea"
        )
    ]
    
    rarity_distribution = {
        Rarity.COMMON.value: 45.0,
        Rarity.UNCOMMON.value: 30.0,
        Rarity.RARE.value: 15.0,
        Rarity.EPIC.value: 7.0,
        Rarity.LEGENDARY.value: 2.5,
        Rarity.DIVINE.value: 0.5
    }
    
    pity_config = {
        'enabled': True,
        'threshold': 80,
        'guaranteed_rarity': Rarity.LEGENDARY.value,
        'pity_reset_on': 'guaranteed_pull'
    }
    
    return generate_gacha_pool(
        pool_name="Default Armor Pool",
        pool_type=PoolType.ARMOR.value,
        items=items,
        rarity_distribution=rarity_distribution,
        pity_config=pity_config
    )


def create_pity_system_config() -> Dict[str, Dict[str, Any]]:
    """Create default pity system configuration for multiple pool types."""
    return {
        'weapon_pool': {
            'enabled': True,
            'threshold': 80,
            'guaranteed_rarity': Rarity.LEGENDARY.value,
            'pity_reset_on': 'guaranteed_pull',
            'soft_pity_at': 40,
            'soft_pity_rarity': Rarity.EPIC.value
        },
        'armor_pool': {
            'enabled': True,
            'threshold': 80,
            'guaranteed_rarity': Rarity.LEGENDARY.value,
            'pity_reset_on': 'guaranteed_pull',
            'soft_pity_at': 40,
            'soft_pity_rarity': Rarity.EPIC.value
        },
        'accessory_pool': {
            'enabled': True,
            'threshold': 80,
            'guaranteed_rarity': Rarity.LEGENDARY.value,
            'pity_reset_on': 'guaranteed_pull',
            'soft_pity_at': 40,
            'soft_pity_rarity': Rarity.EPIC.value
        }
    }


def generate_gacha_system_config(
    pools: List[GachaPool],
    pity_system_config: Dict[str, Dict[str, Any]],
    cost_per_pull: int = 100,
    currency_name: str = "premium_currency"
) -> Dict[str, Any]:
    """Generate complete gacha system configuration."""
    
    pool_configs = {}
    for pool in pools:
        pool_configs[pool.name] = {
            'pool_type': pool.pool_type,
            'items': [item.id for item in pool.items],
            'rarity_distribution': pool.weights,
            'pity_config': pool.pity_system
        }
    
    return {
        'system_name': 'loreSystem Gacha Engine',
        'version': '1.0',
        'currency': {
            'name': currency_name,
            'cost_per_pull': cost_per_pull
        },
        'pools': pool_configs,
        'pity_systems': pity_system_config,
        'balance_metrics': {
            'tracking_enabled': True,
            'drop_protection_enabled': True,
            'rng_seed': None  # Set to a specific value for reproducible results
        }
    }


def calculate_expected_pulls(pool: GachaPool, target_rarity: str, pity_threshold: int) -> float:
    """Calculate expected number of pulls to get a specific rarity."""
    if target_rarity not in pool.weights:
        raise ValueError(f"Target rarity {target_rarity} not in pool")
    
    target_weight = pool.weights[target_rarity]
    expected_pulls = pity_threshold / target_weight if target_weight > 0 else float('inf')
    
    return expected_pulls


def main():
    """Main entry point for gacha generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate gacha/loot box pools for loreSystem")
    parser.add_argument("--output", default="gacha_pools.json", help="Output file for gacha config")
    parser.add_argument("--pools", nargs="+", default=["weapon", "armor"], help="Pools to generate (weapon, armor, accessory)")
    parser.add_argument("--pity-threshold", type=int, default=80, help="Pity threshold for guaranteed pull")
    parser.add_argument("--seed", type=int, help="Random seed for reproducible results")
    
    args = parser.parse_args()
    
    if args.seed:
        random.seed(args.seed)
    
    # Generate pools
    pools = []
    if "weapon" in args.pools:
        pools.append(create_default_weapon_pool())
    if "armor" in args.pools:
        pools.append(create_default_armor_pool())
    
    # Create pity system config
    pity_config = create_pity_system_config()
    
    # Generate gacha system config
    config = generate_gacha_system_config(pools, pity_config, cost_per_pull=100)
    
    # Save to file
    with open(args.output, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Generated gacha pools: {len(pools)}")
    print(f"✓ Output: {args.output}")
    print(f"✓ Pity threshold: {args.pity_threshold}")
    print(f"\nPool details:")
    for pool in pools:
        print(f"  - {pool.name}: {len(pool.items)} items")
        print(f"    Weights: {pool.weights}")
        if pool.pity_system['enabled']:
            print(f"    Pity: {pool.pity_system['threshold']} pulls → guaranteed {pool.pity_system['guaranteed_rarity']}")
            if 'soft_pity_at' in pool.pity_system:
                print(f"    Soft pity: {pool.pity_system['soft_pity_at']} pulls → {pool.pity_system['soft_pity_rarity']}")


if __name__ == '__main__':
    main()
