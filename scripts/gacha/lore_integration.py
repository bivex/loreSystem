#!/usr/bin/env python3
"""
LoreSystem Gacha Integration for loreSystem

Integrates gacha/loot boxes with loreSystem entities.
Allows gacha drops to create legendary items, artifacts, and equipment
with full lore support and database persistence.
"""

import json
import sqlite3
import argparse
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import random
import hashlib

# Import loreSystem entity classes
sys.path.append('/root/clawd/src/domain/entities')
sys.path.append('/root/clawd/src/domain')

try:
    from item import Item
    from legendary_weapon import LegendaryWeapon
    from mythical_armor import MythicalArmor
    from divine_item import DivineItem
    from cursed_item import CursedItem
    from artifact_set import ArtifactSet
    from relic_collection import RelicCollection
    from glyph import Glyph
    from rune import Rune
    from socket import Socket
    from enchantment import Enchantment
except ImportError as e:
    print(f"❌ Failed to import loreSystem entities: {e}")
    print("This script requires loreSystem entity classes to function properly.")
    sys.exit(1)


class Rarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    DIVINE = "divine"


@dataclass
class GachaLootResult:
    pull_id: str
    item_pulled: Dict[str, Any] | None
    lore_entity: Dict[str, Any] | None
    rarity: str
    was_guaranteed: bool
    pity_counter: int
    cost: int
    timestamp: str


def generate_uuid() -> str:
    """Generate a unique ID for gacha pulls."""
    return hashlib.md5(f"pull_{random.randint(0, 999999999999)}{random.time()}").hexdigest()


def insert_lore_entity(
    db: sqlite3.Connection,
    entity_type: str,
    entity_id: str,
    entity_data: Dict[str, Any]
) -> None:
    """
    Insert a gacha pull into loreSystem database.
    """
    try:
        cursor = db.cursor()
        
        # Determine table name
        table_name = entity_type.lower() + 's'
        
        # Check if table exists, create if needed
        cursor.execute(f"""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='{table_name}'
        """)
        
        if not cursor.fetchone():
            print(f"⚠️  Table {table_name} does not exist. Creating...")
            # Simplified table creation (adjust schema as needed)
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id TEXT PRIMARY KEY,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        # Insert entity
        cursor.execute(f"""
            INSERT INTO {table_name} (id, data, created_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (entity_id, json.dumps(entity_data),))
        
        db.commit()
        print(f"✅ Inserted {entity_type}: {entity_id}")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        raise


def process_gacha_pull(
    pool_config: Dict[str, Any],
    pity_state: Dict[str, Dict[str, int]],
    pull_number: int,
    db: sqlite3.Connection
) -> GachaLootResult:
    """
    Process a single gacha pull and integrate with loreSystem.
    """
    # Extract item from pull
    item_data = pull_number.get('item', {})
    
    # Determine entity type based on item
    item_type = item_data.get('type', 'unknown').lower()
    
    # Create lore entity
    lore_entity_id = generate_uuid()
    lore_entity = {
        'gacha_pull_id': pull_number.get('pull_id', 'unknown'),
        'gacha_timestamp': pull_number.get('timestamp', ''),
        'source_pool': item_data.get('source_pool', 'unknown'),
        'rarity': item_data.get('rarity', 'unknown')
    }
    
    # Add lore based on item type
    if item_type in ['weapon', 'legendary_weapon', 'divine_weapon']:
        lore_entity.update({
            'entity_type': 'legendary_weapon' if item_type == 'legendary_weapon' else 'weapon',
            'name': item_data.get('name', 'Unknown Weapon'),
            'description': item_data.get('lore', ''),
            'base_stats': item_data.get('base_stats', {}),
            'special_abilities': item_data.get('special_effects', []),
            'visual_style': item_data.get('sprite', ''),
            'historical_significance': item_data.get('history', ''),
            'acquisition_method': f"gacha pull #{pull_number}",
            'gacha_pool': item_data.get('source_pool', 'unknown')
        })
        entity_type = 'legendary_weapon' if item_type == 'legendary_weapon' else 'weapon'
    
    elif item_type in ['armor', 'mythical_armor', 'divine_armor']:
        lore_entity.update({
            'entity_type': 'mythical_armor' if item_type == 'mythical_armor' else 'armor',
            'name': item_data.get('name', 'Unknown Armor'),
            'description': item_data.get('lore', ''),
            'defense_stats': item_data.get('base_stats', {}),
            'special_effects': item_data.get('special_effects', []),
            'visual_style': item_data.get('sprite', ''),
            'historical_significance': item_data.get('history', ''),
            'acquisition_method': f"gacha pull #{pull_number}",
            'gacha_pool': item_data.get('source_pool', 'unknown')
        })
        entity_type = 'mythical_armor' if item_type == 'mythical_armor' else 'armor'
    
    elif item_type in ['divine_item']:
        lore_entity.update({
            'entity_type': 'divine_item',
            'name': item_data.get('name', 'Unknown Divine Item'),
            'description': item_data.get('lore', ''),
            'effects': item_data.get('base_stats', {}),  # Divine effects
            'blessing_power': item_data.get('special_effects', []),
            'historical_significance': item_data.get('history', ''),
            'acquisition_method': f"gacha pull #{pull_number}",
            'gacha_pool': item_data.get('source_pool', 'unknown')
        })
        entity_type = 'divine_item'
    
    elif item_type in ['cursed_item']:
        lore_entity.update({
            'entity_type': 'cursed_item',
            'name': item_data.get('name', 'Unknown Cursed Item'),
            'description': item_data.get('lore', ''),
            'base_stats': item_data.get('base_stats', {}),
            'curse_effects': item_data.get('special_effects', []),
            'curse_drawbacks': item_data.get(' drawbacks', []),
            'historical_significance': item_data.get('history', ''),
            'acquisition_method': f"gacha pull #{pull_number}",
            'gacha_pool': item_data.get('source_pool', 'unknown')
        })
        entity_type = 'cursed_item'
    
    elif item_type in ['artifact_set']:
        lore_entity.update({
            'entity_type': 'artifact_set',
            'name': item_data.get('name', 'Unknown Artifact Set'),
            'description': item_data.get('lore', ''),
            'items_in_set': item_data.get('set_items', []),
            'set_bonus': item_data.get('set_bonus', {}),
            'historical_significance': item_data.get('history', ''),
            'acquisition_method': f"gacha pull #{pull_number}",
            'gacha_pool': item_data.get('source_pool', 'unknown')
        })
        entity_type = 'artifact_set'
    
    elif item_type in ['relic_collection']:
        lore_entity.update({
            'entity_type': 'relic_collection',
            'name': item_data.get('name', 'Unknown Relic Collection'),
            'description': item_data.get('lore', ''),
            'relics': item_data.get('relics', []),
            'collection_progress': f"{item_data.get('collected', 0)}/{item_data.get('total', 1)}",
            'historical_significance': item_data.get('history', ''),
            'acquisition_method': f"gacha pull #{pull_number}",
            'gacha_pool': item_data.get('source_pool', 'unknown')
        })
        entity_type = 'relic_collection'
    
    elif item_type in ['glyph', 'rune', 'socket', 'enchantment']:
        lore_entity.update({
            'entity_type': 'enhancement',
            'name': item_data.get('name', 'Unknown Enhancement'),
            'description': item_data.get('lore', ''),
            'enhancement_type': item_type,
            'enhancement_power': item_data.get('power', 1),
            'rarity': item_data.get('rarity', 'common'),
            'compatibility': item_data.get('compatible_with', []),
            'historical_significance': item_data.get('history', ''),
            'acquisition_method': f"gacha pull #{pull_number}",
            'gacha_pool': item_data.get('source_pool', 'unknown')
        })
        entity_type = 'enhancement'
    
    else:
        # Unknown item type - store generic data
        lore_entity.update({
            'entity_type': 'unknown',
            'name': item_data.get('name', 'Unknown Item'),
            'description': item_data.get('lore', ''),
            'item_data': item_data,
            'rarity': item_data.get('rarity', 'common'),
            'acquisition_method': f"gacha pull #{pull_number}",
            'gacha_pool': item_data.get('source_pool', 'unknown')
        })
        entity_type = 'unknown'
    
    # Insert into database
    try:
        insert_lore_entity(db, entity_type, lore_entity_id, lore_entity)
    except Exception as e:
        print(f"❌ Failed to insert entity: {e}")
        lore_entity = None
    
    # Create result
    result = GachaLootResult(
        pull_id=str(pull_number.get('pull_id', 'unknown')),
        item_pulled=item_data.get('name', None),
        lore_entity=lore_entity_id,
        rarity=item_data.get('rarity', 'unknown'),
        was_guaranteed=pull_number.get('was_guaranteed', False),
        pity_counter=pull_number.get('pity_counter', 0),
        cost=pull_number.get('cost', 0),
        timestamp=pull_number.get('timestamp', '')
    )
    
    return result


def load_gacha_config(config_file: str) -> Dict[str, Any]:
    """Load gacha configuration from JSON file."""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            if 'pools' in config:
                return config
            else:
                print(f"⚠️  No pools found in {config_file}")
                return {}
    except FileNotFoundError:
        print(f"❌ Gacha config not found: {config_file}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {config_file}: {e}")
        return {}


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="LoreSystem Gacha Integration")
    parser.add_argument("--config", default="gacha_pools.json", help="Gacha configuration file")
    parser.add_argument("--history", default="gacha_report.json", help="Gacha pull history file")
    parser.add_argument("--output", default="gacha_integration.json", help="Integration output file")
    parser.add_argument("--db", default="lore_system.db", help="LoreSystem database file")
    parser.add_argument("--simulate", type=int, default=10, help="Number of pulls to simulate")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_gacha_config(args.config)
    if not config.get('pools'):
        print("❌ No valid gacha pools found. Exiting.")
        return
    
    # Connect to database
    db = sqlite3.connect(args.db)
    
    # Simulate pulls
    results = []
    
    print(f"🎰 Simulating {args.simulate} gacha pulls...")
    for i in range(args.simulate):
        pull_number = i + 1
        
        # Select random pool
        pool_names = list(config['pools'].keys())
        pool_name = random.choice(pool_names)
        pool = config['pools'][pool_name]
        pool_items = pool.get('items', [])
        
        if not pool_items:
            print(f"⚠️  No items in pool {pool_name}. Skipping.")
            continue
        
        # Simulate pull (simplified - in real usage, use gacha_runner)
        # Random item selection based on rarity weights
        item = random.choice(pool_items)
        
        # Check pity system
        pity_system = pool.get('pity_system', {})
        pity_state = {}
        
        pool_type = pool.get('pool_type', 'unknown')
        if pool_type in pity_system:
            pity_state = pity_system[pool_type]
        
        # Check if pity threshold reached
        is_guaranteed = False
        pity_counter = pity_state.get('current_pity', 0) + 1
        
        if pity_system.get('enabled', False) and pity_counter >= pity_system.get('threshold', 80):
            guaranteed_rarity = pity_system.get('guaranteed_rarity', None)
            if guaranteed_rarity:
                # Filter items by guaranteed rarity
                guaranteed_items = [it for it in pool_items if it.get('rarity') == guaranteed_rarity]
                if guaranteed_items:
                    item = random.choice(guaranteed_items)
                    is_guaranteed = True
                    pity_counter = 0  # Reset pity
        else:
            is_guaranteed = False
        
        # Generate pull result
        result = process_gacha_pull(
            pool_config=pool,
            pity_state={pool_type: {'current_pity': pity_counter, 'guaranteed_rarity': pity_system.get('guaranteed_rarity', None)} if pool_type in pity_system else {}},
            pull_number={
                'pull_id': str(pull_number),
                'timestamp': f"{random.time()}",
                'item': item,
                'rarity': item.get('rarity', 'unknown'),
                'was_guaranteed': is_guaranteed,
                'pity_counter': pity_counter,
                'cost': 100  # Default cost
            },
            db=db
        )
        
        results.append(result)
    
    # Save results
    integration_data = {
        'simulation': {
            'pulls_simulated': len(results),
            'pools_used': list(set([r.get('source_pool', 'unknown') for r in results])),
            'timestamp': f"{random.time()}"
        },
        'results': [r.__dict__ for r in results],
        'config_used': args.config,
        'database': args.db
    }
    
    with open(args.output, 'w') as f:
        json.dump(integration_data, f, indent=2)
    
    print(f"✅ Integration complete: {len(results)} pulls processed")
    print(f"📊 Output: {args.output}")
    
    db.close()


if __name__ == '__main__':
    main()
