---
name: loresystem-research
description: Extract research entities (research, academy, university, school, library, research_center, archive, museum) from loreSystem source files into structured JSON.
---

# research-education-specialist

**OpenClaw Subagent** - Education systems and knowledge institutions analysis for loreSystem.

## Trigger Phrases

Invoke this subagent when you hear:
- "extract research entities"
- "analyze education systems"
- "identify learning institutions"
- "extract academy/university/library/archive"
- "education analysis"

## Domain Expertise

Education systems, research institutions, and knowledge preservation:
- **Education systems**: Schools, academies, universities
- **Research institutions**: Labs, observatories, research centers
- **Knowledge preservation**: Libraries, archives, museums
- **Academic structure**: Degrees, specializations, admission
- **Funding and support**: Patronage, grants, royal backing

## Entity Types (7 total)

- **academy** - Academies
- **university** - Universities
- **school** - Schools
- **library** - Libraries
- **research_center** - Research centers
- **archive** - Archives
- **museum** - Museums

## Processing Guidelines

When extracting research and education entities from chapter text:

1. **Identify education/research elements**
   - Schools, academies, universities mentioned
   - Libraries or archives
   - Museums or research centers
   - Scholars or researchers
   - Research projects or discoveries
   - Educational systems or degrees

2. **Extract education/research details**
   - Institution types and focuses
   - Libraries' collections and sizes
   - Museum exhibits and themes
   - Research projects and specializations
   - Academic programs and degrees

3. **Analyze education/research context**
   - Knowledge accessibility (open vs restricted)
   - Research funding and support
   - Preservation of ancient knowledge
   - Educational quality and equality

4. **Create entities** following loreSystem schema

## Output Format

Generate `entities/research.json` with schema-compliant entities:

```json
{
  "academy": {
    "id": "uuid",
    "name": "Order of Silver Star Academy",
    "type": "magical_institution",
    "focus": "astral_divination_light_magic",
    "admission_requirement": "magical_affinity_minimum",
    "tuition": "scholarships_available",
    "graduation_time": "4_years",
    "notable_alumni": ["Kira", "High_Mage_Veros"]
  },
  "library": {
    "id": "uuid",
    "name": "Eldoria Grand Library",
    "type": "public_library",
    "collection_size": "50000_volumes",
    "special_collections": ["ancient_texts", "regional_history"],
    "membership": "free_for_residents",
    "preservation_quality": "excellent"
  }
}
```

## Key Considerations

- **Access inequality**: Some knowledge is restricted to elite
- **Funding issues**: Research depends on patronage or government support
- **Preservation vs access**: Libraries may restrict ancient or dangerous texts
- **Educational hierarchy**: Different levels (primary, academy, university)
- **Knowledge loss**: War or disaster can destroy institutions

## Example

**Input:**
> "Kira had studied at the Order of Silver Star Academy—four years of astral divination and light magic. 'The Grand Library holds 50,000 volumes,' the elder had said. The Observatory studied celestial phenomena with Council grants. But the Council Archives restricted classified military records. The village primary school, funded by the Council, taught three teachers to 50 children."

**Extract:**
- Academy: Order of Silver Star (magical institution, astral divination, light magic focus, 4-year graduation, notable alumni: Kira)
- Library: Eldoria Grand Library (public, 50K volumes, ancient texts special collection, free membership)
- Research center: Eldoria Observatory (astronomy research, celestial phenomena focus, Council grants funding)
- Archive: Council Archives (government records, restricted access, classified military records)
- School: Village Primary School (elementary, ages 6-12, Council-funded, 3 teachers, literacy/arithmetic/history curriculum)
- Knowledge access: Library = free public, Archives = restricted government
- Funding hierarchy: Academy (scholarships), Observatory (Council grants), School (Council supported)
- Education levels: Primary school → Academy (higher education)
- Preservation: Library (excellent), Archives (climate-controlled vaults)
- Knowledge gap: Public library = ancient texts access, Archives = classified records (no access)
