---
name: lore-writing
description: Extract lore entities from narrative text. Use when analyzing codex entries, bestiary entries, journal pages, dreams, nightmares, memories, secrets, and worldbuilding fragments.
---
# lore-writing

Доменный скилл для Lore Chronicler. Специфические правила извлечения и экспертиза.

## Domain Expertise

- **Worldbuilding**: History, culture, myths, legends
- **Secrets**: Hidden knowledge, forbidden lore, mysteries
- **Bestiary**: Creatures, monsters, flora, fauna
- **Dreams/visions**: Prophetic dreams, nightmares, visions
- **Journaling**: Character reflections, discoveries, notes

## Entity Types (8 total)

- **lore_fragment** - Pieces of lore
- **codex_entry** - Codex entries
- **journal_page** - Journal pages
- **bestiary_entry** - Creature descriptions
- **memory** - Character memories
- **dream** - Dreams and visions
- **nightmare** - Nightmares
- **secret_area** - Secret locations

## Processing Guidelines

When extracting lore entities from chapter text:

1. **Identify lore elements**:
   - Historical references mentioned in passing
   - Myths, legends, folklore
   - Creature descriptions (beasts, monsters)
   - Dreams, visions, prophetic moments
   - Secrets, mysteries, forbidden knowledge
   - Journals, diaries, notes

2. **Extract lore details**:
   - Historical fragments, cultural notes
   - Creature abilities, behaviors, habitats
   - Dream/vision symbolism and meaning
   - Secret locations and their contents
   - Journal reflections and discoveries

3. **Organize lore connections**:
   - Link fragments to larger stories
   - Connect dreams to predictions/foreshadowing
   - Reference historical contexts
   - Note recurring symbols or themes

4. **Create schema-compliant entities** with proper JSON structure

## Key Considerations

- **Fragmentary nature**: Lore often comes in small pieces
- **Unreliable narrators**: Stories may be biased or inaccurate
- **Symbolic dreams**: Not all dreams are literal
- **Lost knowledge**: Some lore may be incomplete or forgotten
