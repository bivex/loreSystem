"""
Example: Economy & Trade System

This example demonstrates how AAA game dev studios can use
MythWeave's domain model to create and manage complex economy
with trade routes, taxes, inflation, and supply/demand systems.
"""

import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict

# Domain entities (in production, these would be imported from src.domain)
# For this example, we'll define minimal stubs
class Currency:
    """Currency stub for example."""
    def __init__(self, id, name, symbol, is_crypto, is_global):
        self.id = id
        self.name = name
        self.symbol = symbol
        self.is_crypto = is_crypto
        self.is_global = is_global

class Location:
    """Location stub for example."""
    def __init__(self, id, name, location_type, is_faction_hq):
        self.id = id
        self.name = name
        self.location_type = location_type
        self.is_faction_hq = is_faction_hq

class Trade:
    """Trade stub for example."""
    def __init__(self, tenant_id, name, from_location_id, to_location_id, profit_margin, estimated_daily_volume, trade_type):
        self.tenant_id = tenant_id
        self.id = None
        self.name = name
        self.from_location_id = from_location_id
        self.to_location_id = to_location_id
        self.profit_margin = profit_margin
        self.estimated_daily_volume = estimated_daily_volume
        self.trade_type = trade_type

class Barter:
    """Barter stub for example."""
    def __init__(self, tenant_id, location_id, name, is_npc_managed, commission_rate):
        self.tenant_id = tenant_id
        self.id = None
        self.name = name
        self.location_id = location_id
        self.is_npc_managed = is_npc_managed
        self.commission_rate = commission_rate

class Tax:
    """Tax stub for example."""
    def __init__(self, tenant_id, name, tax_rate, applies_to, currency_id):
        self.tenant_id = tenant_id
        self.id = None
        self.name = name
        self.tax_rate = tax_rate
        self.applies_to = applies_to
        self.currency_id = currency_id

class Inflation:
    """Inflation stub for example."""
    def __init__(self, tenant_id, rate, period_days, currency_id):
        self.tenant_id = tenant_id
        self.id = None
        self.rate = rate
        self.period_days = period_days
        self.currency_id = currency_id

def create_complex_economy(tenant_id: str, world_id: str) -> dict:
    """
    Create complex economy with trade, barter, taxes and inflation.
    """
    
    # 1. Create currencies
    gold = Currency("curr_001", "Gold Coins", "G", False, True)
    silver = Currency("curr_002", "Silver Coins", "S", False, True)
    crystal = Currency("curr_003", "Magic Crystals", "C", False, True)
    
    currencies = {
        "gold": gold,
        "silver": silver,
        "crystal": crystal
    }
    
    # 2. Create locations
    capital_city = Location("loc_001", "Capital City", "city", True)
    trade_town = Location("loc_002", "Trade Town", "town", False)
    coastal_port = Location("loc_003", "Coastal Port", "port", False)
    
    # 3. Create trade routes
    main_route = Trade(
        tenant_id=tenant_id,
        name="Capital -> Town Main Road",
        from_location_id=capital_city.id,
        to_location_id=trade_town.id,
        profit_margin=0.2,  # 20% profit
        estimated_daily_volume=1000,
        trade_type="regular"
    )
    
    secondary_route = Trade(
        tenant_id=tenant_id,
        name="Capital -> Port Coastal Route",
        from_location_id=capital_city.id,
        to_location_id=coastal_port.id,
        profit_margin=0.15,  # 15% profit
        estimated_daily_volume=500,
        trade_type="regular"
    )
    
    # 4. Create barter market
    barter = Barter(
        tenant_id=tenant_id,
        location_id=capital_city.id,
        name="Grand Barter Square",
        is_npc_managed=True,
        commission_rate=0.05  # 5% commission
    )
    
    # 5. Setup tax system
    income_tax = Tax(
        tenant_id=tenant_id,
        name="Income Tax",
        tax_rate=0.1,  # 10% tax
        applies_to="income",
        currency_id="curr_001"
    )
    
    luxury_tax = Tax(
        tenant_id=tenant_id,
        name="Luxury Tax",
        tax_rate=0.15,  # 15% tax
        applies_to="luxury",
        currency_id="curr_001"
    )
    
    # 6. Configure inflation
    inflation = Inflation(
        tenant_id=tenant_id,
        rate=1.05,  # 5% inflation per month
        period_days=30,
        currency_id="curr_001"
    )
    
    # 7. Trade statistics
    trade_stats = {
        "total_routes": 2,
        "active_routes": 2,
        "avg_profit_margin": (main_route.profit_margin + secondary_route.profit_margin) / 2,
        "daily_transaction_volume": 1500
    }
    
    # 8. Return economic system data
    economy_data = {
        "currencies": {name: {"symbol": curr.symbol, "is_crypto": curr.is_crypto} for name, curr in currencies.items()},
        "trade_routes": {
            "main": {
                "name": main_route.name,
                "from": capital_city.name,
                "to": trade_town.name,
                "profit": f"{main_route.profit_margin * 100}%",
                "volume": main_route.estimated_daily_volume
            },
            "secondary": {
                "name": secondary_route.name,
                "from": capital_city.name,
                "to": coastal_port.name,
                "profit": f"{secondary_route.profit_margin * 100}%",
                "volume": secondary_route.estimated_daily_volume
            }
        },
        "barter_market": {
            "location": capital_city.name,
            "commission": f"{barter.commission_rate * 100}%",
            "is_npc_managed": barter.is_npc_managed
        },
        "taxes": {
            "income": f"{income_tax.tax_rate * 100}%",
            "luxury": f"{luxury_tax.tax_rate * 100}%"
        },
        "inflation": {
            "rate": f"{inflation.rate * 100}%",
            "period_days": inflation.period_days,
            "currency": gold.name
        },
        "statistics": trade_stats
    }
    
    return economy_data

def export_economy_to_json(tenant_id: str, world_id: str, output_path: str) -> None:
    """Export economic system to JSON format."""
    
    economy_data = create_complex_economy(tenant_id, world_id)
    
    export_data = {
        "economy": economy_data,
        "metadata": {
            "tenant_id": tenant_id,
            "world_id": world_id,
            "export_date": datetime.now().isoformat(),
            "export_tool": "MythWeave Chronicles v1.0",
            "author": "AAA Game Development Studio"
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

# Example usage
if __name__ == "__main__":
    tenant_id = "tenant_001"
    world_id = "world_001"
    
    # Create economy system
    economy_data = create_complex_economy(tenant_id, world_id)
    
    print("✅ Economic system created:")
    print(f"💰 Currencies: {len(economy_data['currencies'])}")
    print(f"📊 Trade Routes: {economy_data['statistics']['total_routes']}")
    print(f"💸 Barter Commission: {economy_data['barter_market']['commission']}")
    print(f"📈 Inflation: {economy_data['inflation']['rate']}")
    
    # Export
    output_path = "examples/economy_system.json"
    export_economy_to_json(tenant_id, world_id, output_path)
    print(f"✅ Economy exported to {output_path}")
