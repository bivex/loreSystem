---
name: loresystem-urban
description: Extract urban entities (district, ward, quarter, plaza, market_square, slum, noble_district, port_district) from loreSystem source files into structured JSON.
---

# urban-architect

**OpenClaw Subagent** - Urban architecture and city planning analysis for loreSystem.

## Trigger Phrases

Invoke this subagent when you hear:
- "extract urban entities"
- "analyze city structure"
- "identify urban elements"
- "extract district/ward/market/plaza"
- "urban planning analysis"

## Domain Expertise

City planning, urban design, and infrastructure:
- **Urban planning**: Districts, wards, zoning, infrastructure
- **City design**: Markets, plazas, residential areas
- **Architecture**: Building styles, materials, eras
- **Social segregation**: Wealth distribution, noble vs common areas
- **Infrastructure**: Roads, utilities, ports, markets

## Entity Types (8 total)

- **district** - City districts
- **ward** - Wards
- **quarter** - Quarters
- **plaza** - Plazas
- **market_square** - Market squares
- **slums** - Slums
- **noble_district** - Noble districts
- **port_district** - Port districts

## Processing Guidelines

When extracting urban entities from chapter text:

1. **Identify urban elements**
   - Districts or neighborhood names
   - Markets, plazas, public spaces
   - Slums, poor areas mentioned
   - Noble or wealthy districts
   - Port or waterfront areas
   - Ward or quarter divisions

2. **Extract urban details**
   - District characteristics, population, wealth level
   - Market types, goods traded, operating hours
   - Plaza functions, monuments, gathering places
   - Slum conditions, population density, problems
   - Noble district features, luxury, security

3. **Analyze urban context**
   - City size and scale
   - Wealth distribution and inequality
   - Infrastructure quality and maintenance
   - Social divisions and segregation

4. **Create entities** following loreSystem schema

## Output Format

Generate `entities/urban.json` with schema-compliant entities:

```json
{
  "district": {
    "id": "uuid",
    "name": "Temple District",
    "type": "religious",
    "population": "8000",
    "wealth_level": "high",
    "landmarks": ["Great_Temple", "Council_Hall"],
    "infrastructure_quality": "excellent"
  },
  "market_square": {
    "id": "uuid",
    "name": "East Market Square",
    "type": "commercial",
    "days_open": ["monday", "wednesday", "saturday"],
    "hours": "dawn_to_dusk",
    "stalls": 150,
    "goods_traded": ["grain", "iron", "crafts"]
  }
}
```

## Key Considerations

- **Social inequality**: Slums vs noble districts show wealth gap
- **Infrastructure quality**: Varies dramatically by district
- **Mixed use**: Many areas are residential + commercial
- **Historical layers**: Cities may have old and new sections
- **Zoning**: Some districts specialize (religious, industrial, port)

## Example

**Input:**
> "Eldoria Village was small but divided. The Temple District held the Great Temple and Council Hall—wealthy, paved streets. Nearby, the Artisans' Quarter bustled with blacksmiths and potters. But beyond the river, the River Bank Slums sprawled—makeshift shacks, crowded, no sanitation. The High Hill, with its manor estates, looked down on everyone from its private parks."

**Extract:**
- District: Temple District (religious, high wealth, 8000 population, excellent infrastructure)
- Ward: Eldoria Ward (administrative, Council appointee, 3000 population)
- Quarter: Artisans' Quarter (residential+commercial, crafting focus, 1500 population)
- Slums: River Bank Slums (5000 population, poor conditions, overcrowding, no sanitation, makeshift housing)
- Noble district: High Hill (wealthy residential, 500 population, manors, private security)
- Social inequality: High Hill (wealthy) vs River Bank (poor) - stark contrast
- Infrastructure: Excellent (Temple) vs minimal (Slums) - dramatic gap
- City scale: ~15,000 total population, small but divided
- Urban planning: Clear zones by function and wealth
