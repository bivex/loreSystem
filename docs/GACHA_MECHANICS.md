# Gacha Mechanics in loreSystem

## Overview

LoreSystem implements a **balanced gacha/loot box system** with player engagement metrics and fairness guarantees.

## Core Concepts

### 1. Gacha Pools

**What is a Gacha Pool?**
A collection of items with defined rarity weights and pull probabilities.

**Pool Types:**
- `weapon` - Weapons and melee weapons
- `armor` - Armor and defensive items
- `accessory` - Accessories and trinkets
- `material` - Crafting materials and currencies

### 2. Rarity Tiers

**Rarity Levels (6 tiers):**

| Tier | Name | Drop Rate | Description |
|-------|------|-----------|-------------|
| 1 | **Common** | 45% | Basic items, low stats |
| 2 | **Uncommon** | 30% | Better stats, minor abilities |
| 3 | **Rare** | 15% | Good stats, special abilities |
| 4 | **Epic** | 7% | Excellent stats, unique abilities |
| 5 | **Legendary** | 2.5% | Outstanding stats, divine/legendary powers |
| 6 | **Divine** | 0.5% | God-like powers, unique artifacts |

### 3. Pity System

**What is Pity?**
A guarantee system that prevents bad luck streaks and ensures players receive high-tier rewards.

**How Pity Works:**
1. **Soft Pity** — At 40 pulls, next Epic/Legendary/Divine item is guaranteed
2. **Hard Pity** — At 80 pulls, guaranteed Divine item
3. **Pity Counter** — Increments with each non-guaranteed pull
4. **Pity Reset** — Resets after guaranteed pull

**Pity Example:**
```
Pull #40-50: Soft pity triggers → guaranteed Epic+
Pull #80+: Hard pity triggers → guaranteed Divine
Pull #81: Pity counter resets to 0
```

### 4. Pull Mechanics

**Pull Process:**
1. **Player Cost** — Each pull costs 100 premium currency
2. **Pool Selection** — Player chooses weapon/armor/accessory pool
3. **Rarity Roll** — Random roll against rarity weights
4. **Item Selection** — Random item from selected rarity
5. **Pity Check** — Check if pity thresholds reached
6. **Reward** — Item awarded or guaranteed drop triggered

**Pull Probability:**
```
- Common:      45% chance
- Uncommon:    30% chance (45+30 = 75%)
- Rare:        15% chance (75+15 = 90%)
- Epic:         7% chance (90+7 = 97%)
- Legendary:    2.5% chance (97+2.5 = 99.5%)
- Divine:       0.5% chance (99.5+0.5 = 100%)
```

## Balance Metrics

### Cost Efficiency

**Formula:**
```
Cost Efficiency = (Total Item Value / Total Currency Cost) × 100
```

**Status Thresholds:**
- **> 75%**: Good — Players get good value per cost
- **50-75%**: Fair — Standard value
- **< 50%**: Expensive — Players pay too much

### Player Experience

**Metrics:**
1. **Pulls to Guaranteed** — Average pulls to reach guaranteed rarity
2. **Frustration Score** — Lower is better (0-100 scale)
3. **Time to Guaranteed** — (Total Pulls - Guaranteed Pulls) × 100

**Experience Status:**
- **0-30%**: Balanced
- **30-60%**: Overwhelmed
- **60-80%**: Expensive
- **80-100%**: Unfair

## Drop Rate Analysis

**Expected vs Actual:**
```
Expected Drop Rate (Rare) = 15%
Actual Drop Rate (Rare) = 14.8%
Deviation = |14.8% - 15%| = 0.2%
```

**Status Determination:**
- **Within 10%**: Balanced
- **±10-20%**: Slightly over/underwhelmed
- **Beyond 20%**: Requires adjustment

## Item Generation

### Legendary Items

**Legendary Weapons:**
- **Blade of Astraea** — Divine light, 250 damage, blind effect
- **Sword of Betrayed** — Cursed, 300 damage, life drain
- **Blade of Shadows** — Epic, shadow meld, stealth

**Legendary Armor:**
- **Shadow Weaver's Vestments** — Invisibility, shadow resistance
- **Astraea's Blessing** — Divine armor, +30% all resistances
- **Dragon Scale Armor** — Mythical, fire resistance

**Divine Items:**
- **Astraea's Compass** — Always shows true north, reveals invisible enemies
- **Amulet of Protection** — Permanent divine blessing
- **Crown of Kingship** - Absolute authority (non-refusable commands)

**Cursed Items:**
- **Vampire Fangs** — Drains HP, cannot be unequipped
- **Sword of Greed** - Steals gold, corrupts stats
- **Ring of Betrayal** - Randomly kills allies

### Artifact Sets

**Sets:**
1. **Eldorian Royal Regalia** (Crown, Scepter, Ring)
   - 2 items: +20% charisma
   - 3 items: Absolute authority
   - Full: +50% all stats in Eldoria

2. **Shadow Weaver's Collection** (Cloak, Boots, Gloves)
   - 2 items: +15% shadow damage
   - 3 items: True invisibility (30s)
   - Full: +20% shadow damage

## Integration with Loom Agents

### Game Mechanics Specialist

**Creates:**
- `event` - Gacha events (player pulls, pity triggers)
- `pull` - Individual pull records
- `phenomenon` - Divine events (rare god-tier drops)
- `pity` - Pity system configurations
- `theme` - Narrative themes (e.g., "Astraea's Blessing")

**Workflow:**
1. Player initiates gacha pull
2. Game Mechanics Specialist generates pull event
3. Calculates rarity roll based on weights
4. Applies pity system
5. Awards item or triggers guaranteed drop

### Legendary Items Specialist

**Creates:**
- `legendary_weapon` - Legendary weapons with divine effects
- `mythical_armor` - Mythical armor with unique abilities
- `divine_item` - God-tier items with permanent buffs
- `cursed_item` - Powerful but penalized items
- `artifact_set` - Multi-item sets with combo bonuses

**Workflow:**
1. Receives pull result from Game Mechanics
2. Determines item rarity (Legendary/Divine)
3. Selects item from rarity-specific pool
4. Generates item with lore, stats, and abilities
5. Adds to player inventory/database

### Analytics & Balance Specialist

**Creates:**
- `player_metric` - Tracks pulls, costs, satisfaction
- `drop_rate` - Actual vs expected drop rates
- `conversion_rate` - Premium currency to high-tier items
- `difficulty_curve` - Gacha difficulty over time

**Workflow:**
1. Monitors pull history
2. Analyzes drop rates by rarity
3. Calculates cost efficiency and player experience
4. Generates balance recommendations
5. Adjusts weights/pity thresholds if needed

## Player Journey

### Engagement Curve

```
Early Game (Levels 1-10):
- Pull Cost: 100 currency
- Guaranteed: 80 pulls
- Focus: Common/Uncommon weapons
- Pity: Soft pity (40 pulls) → Epic+

Mid Game (Levels 11-25):
- Pull Cost: 100 currency
- Guaranteed: 80 pulls
- Focus: Rare/Epic items
- Pity: Hard pity (80 pulls) → Divine

Late Game (Levels 26-40):
- Pull Cost: 150 currency
- Guaranteed: 60 pulls (faster)
- Focus: Legendary/Divine items
- Pity: Hard pity (60 pulls) → Divine
```

### Satisfaction Optimization

**Psychological Hooks:**
1. **Progressive Wins** — Frequent low-tier drops maintain engagement
2. **Near Misses** — Pulling wrong rarity fuels "next one!" mentality
3. **Jackpot Moments** — Epic/Legendary/Divine drops create excitement
4. **Fairness Perception** — Visible pity and drop rates build trust

**Anti-Frustration:**
- Pity guarantees prevent "hundreds of pulls, no reward"
- Drop protection limits extreme bad luck
- Visible metrics let players know what to expect

## Fairness & Ethics

### Player Protection

1. **Drop Rates** — Public, verifiable, never below expected
2. **No False Advertising** — Rates exactly as advertised
3. **Pity System** — Hard caps on bad luck streaks
4. **Price Transparency** — Clear cost per pull with expected value

### Monetization Balance

**Recommended:**
- **Daily Quest Currency** — Players can earn ~3-5 pulls/day free
- **Event Rewards** — Special events grant free pulls
- **Achievement Rewards** — Unlock free Legendary boxes
- **Monthly Bonuses** — 5 free pulls monthly for active players

This ensures free-to-play players can still progress without paying, while maintaining monetization.

## Technical Implementation

### Database Schema

**Tables:**
- `gacha_events` - All pull events
- `gacha_items` - Item definitions and pools
- `gacha_pity` - Player pity state
- `gacha_stats` - Player pull statistics

**Entity Integration:**
- Legendary items inserted into `legendary_items` table
- Cursed items inserted into `cursed_items` table
- Pull events linked to `event` table

**Configuration:**
```json
{
  "gacha_pools": {
    "weapon_pool": "weapon",
    "armor_pool": "armor",
    "accessory_pool": "accessory"
  },
  "pity_system": {
    "enabled": true,
    "soft_pity_threshold": 40,
    "hard_pity_threshold": 80,
    "guaranteed_rarity": "divine",
    "pity_reset": "guaranteed_drop"
  },
  "drop_rates": {
    "common": 0.45,
    "uncommon": 0.30,
    "rare": 0.15,
    "epic": 0.07,
    "legendary": 0.025,
    "divine": 0.005
  }
}
```

## Summary

LoreSystem's gacha system is:
- **✅ Balanced** — Fair drop rates with pity guarantees
- **✅ Fair** — Transparent costs and visible metrics
- **✅ Engaging** — Progressive rewards with excitement
- **✅ Ethical** — Player protection and anti-frustration design
- **✅ Monetizable** — Premium pulls balanced with free rewards
- **✅ Integratable** — Works seamlessly with Loom agents and loreSystem entities
