#!/usr/bin/env python3
"""
Gacha/Loot Box Balance Analyzer for loreSystem

Analyzes gacha pull data, calculates drop rates, evaluates system balance,
and recommends adjustments for player satisfaction.
"""

import json
import argparse
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
import math
from statistics import mean, stdev

class BalanceStatus(Enum):
    BALANCED = "balanced"
    OVERWHELMED = "overwhelmed"
    UNDERWHELMED = "underwhelmed"
    EXPENSIVE = "expensive"
    UNFAIR = "unfair"


@dataclass
class RarityMetrics:
    total_pulls: int
    pull_count: int
    drop_count: int
    drop_rate: float
    expected_rate: float
    deviation: float
    status: BalanceStatus


@dataclass
class CostEfficiency:
    total_cost: int
    total_value: int
    cost_efficiency: float
    average_cost_per_rarity: Dict[str, float]
    player_satisfaction: float
    status: BalanceStatus


@dataclass
class PlayerExperience:
    pulls_to_guaranteed: int
    average_pulls: float
    time_to_guaranteed: int
    frustration_score: float
    status: BalanceStatus


@dataclass
class BalanceReport:
    overall_status: BalanceStatus
    cost_efficiency: CostEfficiency
    player_experience: PlayerExperience
    rarity_metrics: Dict[str, RarityMetrics]
    recommendations: List[str]
    summary: str


def load_pull_history(filename: str) -> List[Dict[str, Any]]:
    """Load gacha pull history from JSON file."""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            if 'recent_pulls' in data:
                return data['recent_pulls']
            elif 'pull_history' in data:
                return data['pull_history']
            elif 'pools' in data and 'stats' in data:
                # Full gacha report
                return data['stats']['recent_pulls']
            else:
                print(f"⚠️  Unknown format in {filename}")
                return []
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {filename}: {e}")
        return []


def analyze_rarity_balance(
    pull_data: List[Dict[str, Any]],
    pool_config: Dict[str, Any]
) -> Dict[str, RarityMetrics]:
    """Analyze drop rates by rarity."""
    metrics = {}
    
    # Group pulls by rarity
    rarity_pulls = defaultdict(list)
    for pull in pull_data:
        if pull.get('rarity_pulled'):
            rarity = pull['rarity_pulled']
            rarity_pulls[rarity].append(pull)
    
    # Calculate metrics for each rarity
    for rarity, pulls in rarity_pulls.items():
        total = len(pulls)
        drops = sum(1 for p in pulls if p.get('item_pulled'))
        drop_rate = drops / total if total > 0 else 0.0
        expected_rate = pool_config.get('rarity_distribution', {}).get(rarity, 0.0) * 100
        deviation = abs(drop_rate - expected_rate)
        
        # Determine status
        if drop_rate < expected_rate * 0.8:
            status = BalanceStatus.OVERWHELMED
        elif drop_rate > expected_rate * 1.2:
            status = BalanceStatus.UNDERWHELMED
        else:
            status = BalanceStatus.BALANCED
        
        metrics[rarity] = RarityMetrics(
            total_pulls=total,
            pull_count=total,
            drop_count=drops,
            drop_rate=round(drop_rate * 100, 2),
            expected_rate=round(expected_rate * 100, 2),
            deviation=round(deviation * 100, 2),
            status=status.value
        )
    
    return metrics


def analyze_cost_efficiency(
    pull_data: List[Dict[str, Any]],
    pool_config: Dict[str, Any]
) -> CostEfficiency:
    """Analyze cost efficiency and player satisfaction."""
    total_cost = sum(p.get('cost', 0) for p in pull_data)
    total_value = sum(
        p.get('item_pulled', {}).get('base_stats', {}).get('damage', 0) if p.get('item_pulled') else 0
        for p in pull_data
        if p.get('item_pulled'):
            base = p['item_pulled'].get('base_stats', {})
            total_value += base.get('value_multiplier', 1.0) if 'value_multiplier' in base else base.get('damage', 0)
    )
    
    if total_cost == 0:
        cost_efficiency = 1.0
    else:
        cost_efficiency = total_value / total_cost if total_cost > 0 else 0.0
    
    # Calculate cost per rarity
    cost_per_rarity = defaultdict(float)
    rarity_value = defaultdict(float)
    rarity_count = defaultdict(int)
    
    for pull in pull_data:
        if pull.get('item_pulled'):
            item = pull['item_pulled']
            rarity = item.get('rarity', 'unknown')
            value = item.get('base_stats', {}).get('value', 1.0)
            
            cost_per_rarity[rarity] += pull.get('cost', 0)
            rarity_value[rarity] += value
            rarity_count[rarity] += 1
    
    # Calculate average cost per rarity
    for rarity in cost_per_rarity:
        if rarity_count[rarity] > 0:
            cost_per_rarity[rarity] = cost_per_rarity[rarity] / rarity_count[rarity]
    
    # Player satisfaction (cost per unit value)
    if total_cost > 0 and total_value > 0:
        player_satisfaction = total_value / (total_cost * 10)  # Scaled to 0-100
    else:
        player_satisfaction = 100.0
    
    # Determine status
    if player_satisfaction > 75:
        status = BalanceStatus.BALANCED
    elif player_satisfaction > 50:
        status = BalanceStatus.EXPENSIVE
    else:
        status = BalanceStatus.UNFAIR
    
    return CostEfficiency(
        total_cost=total_cost,
        total_value=total_value,
        cost_efficiency=round(cost_efficiency * 100, 2),
        average_cost_per_rarity=dict(cost_per_rarity),
        player_satisfaction=round(player_satisfaction, 2),
        status=status.value
    )


def analyze_player_experience(
    pull_data: List[Dict[str, Any]],
    pool_config: Dict[str, Any]
) -> PlayerExperience:
    """Analyze player journey to guaranteed drops."""
    guaranteed_rarity = pool_config.get('pity_systems', {}).get('guaranteed_rarity', None)
    pity_thresholds = {}
    
    for pool_type, pity_configs in pool_config.get('pity_systems', {}).items():
        if pity_configs.get('enabled') and pity_configs.get('threshold'):
            pity_thresholds[pool_type] = pity_configs.get('threshold')
    
    # Calculate pulls to guaranteed
    pulls_to_guaranteed = float('inf')
    average_pulls = 0.0
    frustration_score = 0.0
    
    if not guaranteed_rarity:
        return PlayerExperience(
            pulls_to_guaranteed=0,
            average_pulls=0.0,
            time_to_guaranteed=0,
            frustration_score=100.0,
            status=BalanceStatus.UNFAIR
        )
    
    # Find minimum pity threshold
    min_threshold = min(pity_thresholds.values()) if pity_thresholds else 80
    
    guaranteed_pulls = 0
    total_pulls = len(pull_data)
    
    for pull in pull_data:
        if pull.get('was_guaranteed'):
            guaranteed_pulls += 1
            break  # Count only first guaranteed pull
    
    if total_pulls > 0 and guaranteed_pulls > 0:
        pulls_to_guaranteed = guaranteed_pulls / total_pulls
        average_pulls = total_pulls / guaranteed_pulls
        time_to_guaranteed = (total_pulls - guaranteed_pulls) * 100  # Assumed 1 pull per attempt
    else:
        pulls_to_guaranteed = 0.0
        average_pulls = float('inf')
        time_to_guaranteed = float('inf')
    
    # Calculate frustration score (lower is better)
    if guaranteed_pulls > 0:
        # Found guaranteed - good experience
        frustration_score = 0.0
    elif pulls_to_guaranteed < 0.1:  # < 10% of pulls
        frustration_score = 20.0  # Frustrated
    elif pulls_to_guaranteed < 0.3:  # < 30% of pulls
        frustration_score = 50.0  # Very frustrated
    elif pulls_to_guaranteed < 0.5:  # < 50% of pulls
        frustration_score = 70.0  # Extremely frustrated
    else:
        frustration_score = 90.0  # Hopeless
    
    # Determine status
    if frustration_score < 30:
        status = BalanceStatus.BALANCED
    elif frustration_score < 60:
        status = BalanceStatus.OVERWHELMED
    elif frustration_score < 80:
        status = BalanceStatus.EXPENSIVE
    else:
        status = BalanceStatus.UNFAIR
    
    return PlayerExperience(
        pulls_to_guaranteed=round(pulls_to_guaranteed * 100, 1),
        average_pulls=round(average_pulls, 2),
        time_to_guaranteed=round(time_to_guaranteed),
        frustration_score=round(frustration_score, 2),
        status=status.value
    )


def generate_balance_report(
    rarity_metrics: Dict[str, RarityMetrics],
    cost_efficiency: CostEfficiency,
    player_experience: PlayerExperience,
    pool_config: Dict[str, Any]
) -> BalanceReport:
    """Generate comprehensive balance report."""
    
    recommendations = []
    
    # Check rarity drop rates
    overall_status = BalanceStatus.BALANCED
    for rarity, metrics in rarity_metrics.items():
        if metrics.status != BalanceStatus.BALANCED:
            if metrics.status == BalanceStatus.OVERWHELMED:
                recommendations.append(f"{rarity} drop rate ({metrics.drop_rate}%) exceeds expected ({metrics.expected_rate}%) - consider reducing drop rate or increasing expected rate")
                overall_status = BalanceStatus.OVERWHELMED
            elif metrics.status == BalanceStatus.UNDERWHELMED:
                recommendations.append(f"{rarity} drop rate ({metrics.drop_rate}%) is below expected ({metrics.expected_rate}%) - consider increasing drop rate or reducing pool common items")
                if overall_status != BalanceStatus.UNDERWHELMED:
                    overall_status = BalanceStatus.UNDERWHELMED
    
    # Check cost efficiency
    if cost_efficiency.status == BalanceStatus.EXPENSIVE:
        recommendations.append(f"Cost efficiency ({cost_efficiency.cost_efficiency}% value/{currency_cost}) is too low - consider reducing pull cost or increasing drop rates")
        if cost_efficiency.status == BalanceStatus.UNFAIR:
            recommendations.append(f"Cost efficiency ({cost_efficiency.cost_efficiency}% value/{currency_cost}) is unfair - consider adjusting pity thresholds or increasing guaranteed drops")
    
    # Check player experience
    if player_experience.status == BalanceStatus.EXPENSIVE:
        recommendations.append(f"Player experience is too frustrating ({player_experience.frustration_score}/100) - consider lowering pity threshold or increasing guaranteed drop rate")
    elif player_experience.status == BalanceStatus.UNFAIR:
        recommendations.append(f"Player experience is poor ({player_experience.frustration_score}/100) - consider guaranteed system or improving drop rates")
    
    # Generate summary
    if overall_status == BalanceStatus.BALANCED:
        summary = "Overall gacha system is well balanced."
    elif overall_status == BalanceStatus.OVERWHELMED:
        summary = "Overall system is generous to players (drops too frequent)."
    elif overall_status == BalanceStatus.UNDERWHELMED:
        summary = "Overall system is stingy (drops too rare)."
    elif overall_status == BalanceStatus.EXPENSIVE:
        summary = "Overall system is expensive for players."
    else:
        summary = "Overall system is unfair to players."
    
    return BalanceReport(
        overall_status=overall_status.value,
        cost_efficiency=cost_efficiency,
        player_experience=player_experience,
        rarity_metrics=rarity_metrics,
        recommendations=recommendations,
        summary=summary
    )


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Gacha Balance Analyzer for loreSystem")
    parser.add_argument("--input", default="gacha_report.json", help="Gacha pull data file")
    parser.add_argument("--pools", help="Pool configuration file (optional)")
    parser.add_argument("--output", default="balance_report.json", help="Balance report output file")
    parser.add_argument("--threshold", type=float, help="Overwhelmed threshold (default 0.8)")
    parser.add_argument("--underwhelmed", type=float, help="Underwhelmed threshold (default 0.8)")
    
    args = parser.parse_args()
    
    # Load pool config
    pool_config = None
    if args.pools:
        with open(args.pools, 'r') as f:
            pool_config = json.load(f)
    
    # Load pull data
    pull_data = load_pull_history(args.input)
    
    if not pull_data:
        print("❌ No pull data found. Please run gacha_runner first.")
        return
    
    # Check if pools available
    if not pool_config:
        print("❌ No pool configuration found. Please run gacha_generator first.")
        return
    
    # Analyze rarity balance
    rarity_metrics = analyze_rarity_balance(pull_data, pool_config)
    
    # Analyze cost efficiency
    cost_efficiency = analyze_cost_efficiency(pull_data, pool_config)
    
    # Analyze player experience
    player_experience = analyze_player_experience(pull_data, pool_config)
    
    # Generate report
    report = generate_balance_report(
        rarity_metrics=rarity_metrics,
        cost_efficiency=cost_efficiency,
        player_experience=player_experience,
        pool_config=pool_config
    )
    
    # Save report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"✅ Balance analysis complete")
    print(f"📊 Overall status: {report.overall_status}")
    print(f"💰 Cost efficiency: {report.cost_efficiency.cost_efficiency}% ({report.cost_efficiency.status})")
    print(f"😊 Player experience: {report.player_experience.player_satisfaction}% ({report.player_experience.status})")
    print(f"\n📈 Rarity metrics:")
    for rarity, metrics in report.rarity_metrics.items():
        print(f"  {rarity}: {metrics.drop_rate}% drops (expected {metrics.expected_rate}%) - {metrics.status}")
    print(f"\n💡 Recommendations:")
    for rec in report.recommendations:
        print(f"  • {rec}")
    print(f"\n📝 Report saved to: {args.output}")


if __name__ == '__main__':
    main()
