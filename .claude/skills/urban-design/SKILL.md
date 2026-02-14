---
name: urban-design
description: Extract urban planning entities from narrative text. Use when analyzing city districts, wards, quarters, plazas, markets, slums, noble districts, and port areas.
---
# urban-design

Доменный скилл для Urban Architect. Специфические правила извлечения и экспертиза.

## Domain Expertise

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

1. **Identify urban elements**:
   - Districts or neighborhood names
   - Markets, plazas, public spaces
   - Slums, poor areas mentioned
   - Noble or wealthy districts
   - Port or waterfront areas
   - Ward or quarter divisions

2. **Extract urban details**:
   - District characteristics, population, wealth level
   - Market types, goods traded, operating hours
   - Plaza functions, monuments, gathering places
   - Slum conditions, population density, problems
   - Noble district features, luxury, security

3. **Analyze urban context**:
   - City size and scale
   - Wealth distribution and inequality
   - Infrastructure quality and maintenance
   - Social divisions and segregation

4. **Create schema-compliant entities** with proper JSON structure

## Key Considerations

- **Social inequality**: Slums vs noble districts show wealth gap
- **Infrastructure quality**: Varies dramatically by district
- **Mixed use**: Many areas are residential + commercial
- **Historical layers**: Cities may have old and new sections
- **Zoning**: Some districts specialize (religious, industrial, port)
