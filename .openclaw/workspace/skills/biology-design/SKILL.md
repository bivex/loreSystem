# biology-design

Доменный скилл для Biology Specialist. Специфические правила извлечения и экспертиза.

## Trigger Phrases

Invoke this subagent when you hear:
- "extract biology entities"
- "analyze ecosystems and wildlife"
- "identify evolution and extinction"
- "process biological systems"
- "biology specialist analysis"

## Domain Expertise

- **Ecology**: Ecosystems, food chains, predator-prey relationships
- **Biology**: Life cycles, reproduction, hibernation, migration
- **Evolution**: Species adaptation, natural selection, evolution
- **Extinction**: Mass extinction events, species loss, ecological collapse
- **Biodiversity**: Species variety, ecosystem health, keystone species

## Entity Types (6 total)

- **food_chain** - Food chains and ecosystems
- **migration** - Migrations and seasonal movement
- **hibernation** - Hibernation and dormancy
- **reproduction** - Reproduction and life cycles
- **extinction** - Extinction events
- **evolution** - Evolution and adaptation

## Processing Guidelines

When extracting biological entities from chapter text:

1. **Identify biological elements**:
   - Animals or creatures mentioned
   - Predator-prey relationships
   - Migratory behaviors mentioned
   - Hibernation or dormancy
   - Extinct species mentioned
   - Evolution or adaptation references

2. **Extract biological details**:
   - Species names, diets, habitats
   - Food chain positions and relationships
   - Migration patterns and timing
   - Hibernation cycles and triggers
   - Extinction causes and impacts
   - Evolutionary traits and adaptations

3. **Analyze biological context**:
   - Ecosystem health indicators
   - Human impact on wildlife
   - Climate change effects
   - Keystone species importance

4. **Create schema-compliant entities** with proper JSON structure

## Key Considerations

- **Ecosystem interdependence**: Species affect each other
- **Keystone species**: Some species are critical to ecosystem health
- **Human impact**: Extinction often caused by human activity
- **Climate effects**: Temperature and weather affect biology
- **Evolutionary timespan**: Evolution takes thousands of years
