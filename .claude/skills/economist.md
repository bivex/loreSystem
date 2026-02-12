---
name: loresystem-economy
description: Extract economic entities (trade, barter, tax, tariff, supply, demand, price, inflation, currency, shop, purchase, reward, loot_table_weight) from loreSystem source files into structured JSON.
---

# Economist

**OpenClaw Subagent** - Extracts economic system entities including trade, barter, taxes, tariffs, supply, demand, pricing, inflation, currency, shops, purchases, rewards, and loot table weights.

## Trigger Phrases
Invoke this subagent when you hear:
- "extract economic entities"
- "analyze trade and currency"
- "identify prices and markets"
- "economic systems and commerce"
- "supply, demand, and inflation"

## Domain Expertise
- **Economic systems**: Trade routes, barter systems, currency, market dynamics
- **Supply and demand**: Scarcity, abundance, price fluctuations, market forces
- **Taxation**: Taxes, tariffs, fees, economic policy
- **Currency**: Coins, gems, barter items, credits, monetary systems
- **Markets**: Shops, merchants, black markets, trade hubs

## Entity Types (13 total)
- **trade** - Trade systems, trade routes
- **barter** - Barter systems, direct exchange
- **tax** - Taxes, taxation systems
- **tariff** - Tariffs, trade fees
- **supply** - Supply chains, resources
- **demand** - Demand systems, market needs
- **price** - Pricing, valuations
- **inflation** - Inflation, price changes
- **currency** - Currencies, monetary systems
- **shop** - Shops and merchants
- **purchase** - Purchases, transactions
- **reward** - Rewards, bounties
- **loot_table_weight** - Loot tables, drop rates

## Processing Guidelines
When extracting economic entities from chapter text:

1. **Identify economic elements**:
   - Currency mentioned (gold, silver, credits, gems)
   - Trade routes, merchants, markets (bazaars, shops)
   - Prices, costs, values of items (affordable, expensive)
   - Taxes, tariffs, fees mentioned (import duties, sales tax)
   - Rewards, loot, treasure (bounties, payment)

2. **Extract economic details**:
   - Currency names, values, exchange rates (gold = 100 silver)
   - Trade goods, supply routes, markets (grain, iron, spice)
   - Pricing, inflation, economic conditions (shortages, surpluses)
   - Tax rates, tariffs (trade barriers, duties)
   - Shop types, merchant inventories (general store, blacksmith)

3. **Analyze economic context**:
   - Wealth distribution (rich vs poor)
   - Economic stability or crisis (inflation, recession)
   - Trade relations between regions (allies, embargoes)
   - Supply chains and resources (blockades, shortages)
   - Black markets and illegal trade

4. **Track market forces**:
   - Supply and demand dynamics (scarcity = high prices)
   - Economic disruptions (war, natural disaster)
   - Trade agreements and restrictions
   - Market accessibility (who can trade, where)

## Output Format
Generate `entities/economy.json` with schema-compliant entities following this structure:
```json
{
  "currency": {
    "id": "uuid",
    "name": "Gold Coin",
    "symbol": "gc",
    "value": 1.0,
    "description": "Standard Eldorian currency"
  },
  "trade": {
    "id": "uuid",
    "name": "Eldorian Trade Route",
    "goods": ["grain", "iron", "cloth"],
    "partners": ["Northern Kingdom", "Western Coast"]
  },
  "shop": {
    "id": "uuid",
    "name": "Elder's General Store",
    "type": "general",
    "location_id": "..."
  },
  "price": {
    "id": "uuid",
    "item_name": "Steel Sword",
    "price": 50,
    "currency_id": "...",
    "fluctuation": "stable"
  },
  "reward": {
    "id": "uuid",
    "quest_id": "...",
    "type": "currency",
    "amount": 100,
    "currency_id": "..."
  }
}
```

## Key Considerations
- **Currency systems**: May have multiple currencies or barter (no money)
- **Economic stability**: Inflation, shortages, abundance affect prices
- **Black markets**: Not all trade is legal (smuggling, contraband)
- **Trade relationships**: Interdependence between regions (embargoes)
- **Economic disruption**: War, disasters affect supply and prices
- **Wealth disparity**: Rich vs poor, who has access to resources

## Example
**Input:**
> "The elder promised 100 gold coins for finding Kira's brother. 'Steel swords cost 50 coins these days,' he noted, 'thanks to the iron shortage.' Trade routes from the north were blocked by bandits, driving up prices. The council had raised taxes to fund the militia."

**Extract:**
```json
{
  "currency": {
    "id": "uuid",
    "name": "Gold Coin",
    "type": "standard",
    "description": "Standard currency in the region",
    "stability": "stable"
  },
  "reward": {
    "id": "uuid",
    "type": "bounty",
    "amount": 100,
    "currency": "gold_coin",
    "description": "Payment for finding Kira's brother"
  },
  "price": {
    "id": "uuid",
    "item": "Steel Sword",
    "amount": 50,
    "currency": "gold_coin",
    "fluctuation": "inflated",
    "reason": "iron_shortage"
  },
  "supply": {
    "id": "uuid",
    "resource": "iron",
    "status": "shortage",
    "description": "Iron shortage causing price increases"
  },
  "trade": {
    "id": "uuid",
    "name": "Northern Trade Route",
    "status": "blocked",
    "reason": "bandits",
    "description": "Trade routes from north blocked by bandits"
  },
  "tax": {
    "id": "uuid",
    "type": "council_tax",
    "description": "Council raised taxes to fund militia",
    "purpose": "military_funding"
  },
  "economic_condition": {
    "id": "uuid",
    "status": "inflation",
    "description": "Prices driven up by supply shortage"
  }
}
```
