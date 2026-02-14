---
name: urban-design
description: Extract urban planning entities from narrative text. Use when analyzing city districts, wards, quarters, plazas, markets, slums, noble districts, and port areas.
---
# urban-design

Domain skill for urban planning and city structure extraction.

## Entity Types

| Type | Description |
|------|-------------|
| `district` | Named city district or neighborhood |
| `ward` | Administrative ward or section |
| `quarter` | City quarter (e.g., merchant quarter) |
| `plaza` | Public plaza or gathering space |
| `market_square` | Market area or trade hub |
| `slums` | Impoverished area |
| `noble_district` | Wealthy or aristocratic area |
| `port_district` | Waterfront or harbor area |

## Extraction Rules

1. **Named districts**: Extract with exact name and characteristics
2. **Social geography**: Map wealth distribution across the city
3. **Infrastructure**: Roads, walls, gates, utilities mentioned
4. **Activity zones**: Commercial, residential, religious, industrial areas
5. **Historical layers**: Old vs new city sections

## Output Format

Write to `entities/world.json` (world-team file):

```json
{
  "district": [
    {
      "id": "uuid",
      "name": "Merchant Quarter",
      "description": "Bustling commercial district with shops and warehouses",
      "wealth_level": "middle",
      "population": "high"
    }
  ],
  "slums": [
    {
      "id": "uuid",
      "name": "The Warrens",
      "description": "Overcrowded slum district near the southern wall",
      "conditions": "poor"
    }
  ],
  "cross_references": [
    {
      "source_type": "district",
      "source_id": "uuid",
      "target_type": "location",
      "target_skill": "world-building",
      "target_hint": "Part of Eldoria City"
    }
  ],
  "_metadata": { "source": "...", "skill": "urban-design", "extracted_at": "...", "entity_count": 2 }
}
```

## Key Considerations

- **Social inequality**: Slums vs noble districts show wealth gap
- **Mixed use**: Many areas are residential + commercial
- **Historical layers**: Cities have old and new sections
- **Cross-references**: Parent locations → cross_references to world-building
