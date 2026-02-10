#!/usr/bin/env python3
"""
Gacha/Loot Box Runner for loreSystem

Executes gacha pulls from pools, manages pity state, and
tracks results. Simulates player pulls and analyzes drop rates.
"""

import json
import random
import argparse
import sys
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
import time

# Import gacha generator
sys.path.append('/root/clawd/scripts/gacha')
from gacha_generator import (
    GachaPool, Item, PoolType, Rarity,
    calculate_weighted_rarity, roll_rarity,
    pull_from_pool, generate_gacha_system_config,
    create_default_weapon_pool, create_default_armor_pool
)

class Rarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    DIVINE = "divine"


@dataclass
class PullResult:
    pull_number: int
    item_pulled: Item | None
    rarity_pulled: str | None
    pity_counter: int
    was_guaranteed: bool = False
    cost: int = 0


@dataclass
class PullStats:
    total_pulls: int
    rarity_breakdown: Dict[str, int]
    pity_resets: int
    guaranteed_pulls: int = 0
    total_cost: int = 0
    drop_rate_per_rarity: Dict[str, float]
    average_cost_per_rarity: Dict[str, float]


class GachaRunner:
    def __init__(self, pools: List[GachaPool], cost_per_pull: int, currency_name: str):
        self.pools = {pool.name: pool for pool in pools}
        self.cost_per_pull = cost_per_pull
        self.currency_name = currency_name
        
        # Pity state: {pool_type: {pool.name}: {current_pity: 0, guaranteed_rarity: None}}
        self.pity_state = defaultdict(lambda: defaultdict(dict))
        for pool in pools:
            pool_type = pool.pool_type
            self.pity_state[pool_type][pool.name] = {
                'current_pity': 0,
                'guaranteed_rarity': None
            }
        
        # Pull history
        self.pull_history: []
        self.stats = PullStats(
            total_pulls=0,
            rarity_breakdown=defaultdict(int),
            pity_resets=0,
            guaranteed_pulls=0,
            total_cost=0,
            drop_rate_per_rarity=defaultdict(float),
            average_cost_per_rarity=defaultdict(float)
        )
    
    def pull(self, pool_name: str, count: int = 1, dry_run: bool = False) -> List[PullResult]:
        """Execute gacha pulls from a pool."""
        pool = self.pools.get(pool_name)
        if not pool:
            raise ValueError(f"Pool {pool_name} not found")
        
        pool_type = pool.pool_type
        pity_config = pool.pity_system
        
        results = []
        
        for i in range(count):
            pull_num = self.stats.total_pulls + i + 1
            
            # Check pity system
            pity_state = self.pity_state[pool_type][pool_name]
            current_pity = pity_state['current_pity']
            
            is_guaranteed = False
            item_pulled = None
            rarity_pulled = None
            
            # Check if pity threshold reached
            if pity_config['enabled'] and current_pity >= pity_config['threshold']:
                # Guaranteed pull
                guaranteed_rarity = pity_config['guaranteed_rarity']
                if 'guaranteed_rarity' in pool.weights:
                    # Filter items by guaranteed rarity
                    guaranteed_items = [item for item in pool.items if item.rarity == guaranteed_rarity]
                    
                    if guaranteed_items:
                        item_pulled = random.choice(guaranteed_items)
                        rarity_pulled = item_pulled.rarity
                        is_guaranteed = True
                        
                        # Reset pity for this pool type
                        pity_state['guaranteed_rarity'] = None
                        pity_state['current_pity'] = 0
                    else:
                        raise ValueError(f"Guaranteed rarity {guaranteed_rarity} not in pool")
            else:
                # Normal pull with rarity weights
                result = pull_from_pool(pool, pity_state)
                item_pulled = result[0]
                rarity_pulled = result[1].rarity if result[1] else None
                
                # Increment pity
                pity_state['current_pity'] += 1
            
            if not dry_run:
                cost = self.cost_per_pull
                self.stats.total_cost += cost
            
            result = PullResult(
                pull_number=pull_num,
                item_pulled=item_pulled,
                rarity_pulled=rarity_pulled,
                pity_counter=current_pity if not is_guaranteed else 0,
                was_guaranteed=is_guaranteed,
                cost=cost if not dry_run else 0
            )
            
            self.pull_history.append(result)
            
            # Update stats
            self.stats.total_pulls += 1
            
            if item_pulled:
                rarity = item_pulled.rarity if item_pulled else None
                self.stats.rarity_breakdown[rarity] += 1
                self.stats.drop_rate_per_rarity[rarity] = self.stats.rarity_breakdown[rarity] / self.stats.total_pulls
            
            if is_guaranteed:
                self.stats.guaranteed_pulls += 1
            
            # Track pity resets
            if is_guaranteed and pity_state['guaranteed_rarity'] is None:
                self.stats.pity_resets += 1
        
        return results
    
    def reset_pity(self, pool_name: str) -> None:
        """Reset pity counter for a specific pool."""
        pool = self.pools.get(pool_name)
        if not pool:
            raise ValueError(f"Pool {pool_name} not found")
        
        pool_type = pool.pool_type
        pity_config = pool.pity_system
        
        if pity_config['enabled']:
            # Reset pity
            self.pity_state[pool_type][pool_name] = {
                'current_pity': 0,
                'guaranteed_rarity': None
            }
            self.stats.pity_resets += 1
    
    def get_stats(self) -> PullStats:
        """Get current pull statistics."""
        return self.stats
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive pull report."""
        report = {
            'pools': list(self.pools.keys()),
            'stats': {
                'total_pulls': self.stats.total_pulls,
                'rarity_breakdown': dict(self.stats.rarity_breakdown),
                'pity_resets': self.stats.pity_resets,
                'guaranteed_pulls': self.stats.guaranteed_pulls,
                'total_cost': self.stats.total_cost,
                'drop_rates': dict(self.stats.drop_rate_per_rarity),
                'average_cost_per_rarity': dict(self.stats.average_cost_per_rarity)
            },
            'cost_per_pull': self.cost_per_pull,
            'currency_name': self.currency_name,
            'recent_pulls': [
                {
                    'pull_number': r.pull_number,
                    'item_name': r.item_pulled.name if r.item_pulled else None,
                    'rarity': r.rarity_pulled,
                    'was_guaranteed': r.was_guaranteed,
                    'pity_counter': r.pity_counter,
                    'cost': r.cost
                }
                for r in self.pull_history[-10:]  # Last 10 pulls
            ],
            'pity_status': {
                pool_type: {
                    pool_name: {
                        'current_pity': self.pity_state[pool_type][pool_name]['current_pity'],
                        'guaranteed_rarity': self.pity_state[pool_type][pool_name]['guaranteed_rarity'],
                        'threshold': self.pools[pool_name].pity_system.get('threshold', 0)
                    }
                    for pool_name, pool in self.pools.items()
                    for pool_type_name, pool_type in self.pity_state.items()
                }
            },
            'efficiency_analysis': self._analyze_efficiency()
        }
        
        return report
    
    def _analyze_efficiency(self) -> Dict[str, Any]:
        """Analyze pull efficiency and drop rates."""
        total_pulls = self.stats.total_pulls
        
        if total_pulls == 0:
            return {
                'status': 'no_pulls_yet',
                'message': 'No pulls to analyze',
                'recommendations': []
            }
        
        analysis = {
            'overall': {},
            'by_rarity': {},
            'recommendations': []
        }
        
        # Overall efficiency
        guaranteed_rate = (self.stats.guaranteed_pulls / total_pulls) * 100 if total_pulls > 0 else 0
        analysis['overall']['guaranteed_rate'] = round(guaranteed_rate, 2)
        analysis['overall']['cost_efficiency'] = 'good' if self.stats.total_cost / total_pulls <= self.cost_per_pull * 1.5 else 'expensive'
        
        # Per-rarity analysis
        for rarity, count in self.stats.rarity_breakdown.items():
            drop_rate = self.stats.drop_rate_per_rarity[rarity] * 100 if total_pulls > 0 else 0
            expected_rate = self.pools[list(self.pools.keys())[0].weights[rarity] * 100 if rarity in self.pools[list(self.pools.keys())[0].weights else 0
            
            analysis['by_rarity'][rarity] = {
                'drop_rate': round(drop_rate, 2),
                'expected_rate': round(expected_rate, 2),
                'deviation': round(drop_rate - expected_rate, 2),
                'status': 'good' if abs(drop_rate - expected_rate) <= 10 else 'adjust_needed'
            }
        
        # Recommendations
        if guaranteed_rate < 15 and total_pulls > 50:
            analysis['recommendations'].append("Consider lowering pity threshold or increasing guaranteed rate for better player experience")
        
        if analysis['overall']['cost_efficiency'] == 'expensive':
            analysis['recommendations'].append("Consider reducing pull cost or increasing drop rates")
        
        return analysis
    
    def save_report(self, report: Dict[str, Any], filename: str = "gacha_report.json") -> None:
        """Save report to JSON file."""
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ Report saved to {filename}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Gacha/Loot Box Runner for loreSystem")
    parser.add_argument("--pools", default="weapon,armor", help="Pool types to load (weapon, armor, accessory)")
    parser.add_argument("--pulls", type=int, default=10, help="Number of pulls to execute")
    parser.add_argument("--pool", type=str, default="Default Weapon Pool", help="Pool name to pull from")
    parser.add_argument("--dry-run", action="store_true", help="Simulate pulls without cost")
    parser.add_argument("--report", default="gacha_report.json", help="Report output file")
    parser.add_argument("--seed", type=int, help="Random seed for reproducible results")
    parser.add_argument("--cost", type=int, default=100, help="Currency cost per pull")
    
    args = parser.parse_args()
    
    if args.seed:
        random.seed(args.seed)
    
    # Load pools
    pools = []
    if "weapon" in args.pools:
        pools.append(create_default_weapon_pool())
    if "armor" in args.pools:
        pools.append(create_default_armor_pool())
    
    # Create runner
    runner = GachaRunner(pools, cost_per_pull=args.cost, currency_name="premium_currency")
    
    # Execute pulls
    print(f"🎰 Executing {args.pulls} pulls from {args.pool}...")
    results = runner.pull(args.pool, count=args.pulls, dry_run=args.dry_run)
    
    # Print results
    print(f"\n📊 Results:")
    for result in results:
        if result.item_pulled:
            print(f"  Pull #{result.pull_number}: {result.item_pulled.name} ({result.rarity_pulled})" + (f" ✨ GUARANTEED" if result.was_guaranteed else f" (Pity: {result.pity_counter})")
            cost_str = f" [${result.cost}]" if not args.dry_run else f" [DRY RUN]"
            print(f"    Stats: {result.item_pulled.base_stats}")
        else:
            print(f"  Pull #{result.pull_number}: No item (Pity: {result.pity_counter})")
    
    # Show stats
    stats = runner.get_stats()
    print(f"\n📈 Statistics:")
    print(f"  Total pulls: {stats.total_pulls}")
    print(f"  Total cost: ${stats.total_cost}")
    print(f"  Rarity breakdown:")
    for rarity, count in sorted(stats.rarity_breakdown.items(), key=lambda x: ['LEGENDARY', 'DIVINE', 'EPIC', 'RARE', 'UNCOMMON', 'COMMON']):
        print(f"  {rarity}: {count} ({stats.drop_rate_per_rarity[rarity] if stats.total_pulls > 0 else 0:.1f}%)")
    
    # Generate and save report
    report = runner.generate_report()
    runner.save_report(report, args.report)
    
    print(f"\n📝 Report saved to {args.report}")


if __name__ == '__main__':
    main()
