---
name: lore-writing
description: Extract lore and narrative device entities from text. Use when analyzing codex entries, bestiary entries, journals, dreams, nightmares, memories, secrets, foreshadowing, and plot devices.
---
# lore-writing

Domain skill for lore knowledge and narrative device extraction.

## Entity Types

| Type | Description |
|------|-------------|
| `lore_fragment` | Piece of world lore or historical knowledge |
| `codex_entry` | Codex or encyclopedia entry |
| `journal_page` | Journal, diary, or log entry |
| `bestiary_entry` | Creature or monster description |
| `memory` | Character memory or recollection |
| `dream` | Dream or prophetic vision |
| `nightmare` | Nightmare or dark vision |
| `foreshadowing` | Narrative foreshadowing element |
| `chekhovs_gun` | Setup element that must pay off later |
| `red_herring` | Misleading narrative element |
| `deus_ex_machina` | Unexpected resolution device |
| `flash_forward` | Future glimpse or time skip |
| `plot_device` | General narrative mechanism |
| `lore_axioms` | Fundamental world rules or laws |

## Extraction Rules

1. **Lore fragments**: Historical references, myths, legends, folklore mentioned in passing
2. **Bestiary**: Creature abilities, behaviors, habitats, weaknesses
3. **Dreams/visions**: Symbolism, prophetic content, emotional context
4. **Narrative devices**: Foreshadowing setups, Chekhov's guns, red herrings
5. **World rules**: Fundamental axioms that govern the world's logic

## Output Format

Write to `entities/narrative.json` (narrative-team file):

```json
{
  "lore_fragment": [
    {
      "id": "uuid",
      "name": "The Old War Legend",
      "description": "A legend about the ancient war between mages and warriors"
    }
  ],
  "foreshadowing": [
    {
      "id": "uuid",
      "name": "The Cracked Amulet",
      "description": "The amulet shows a crack — hints at its eventual breaking",
      "setup_chapter": "chapter_3",
      "expected_payoff": "amulet breaks in climax"
    }
  ],
  "cross_references": [],
  "_metadata": { "source": "...", "skill": "lore-writing", "extracted_at": "...", "entity_count": 2 }
}
```

## Key Considerations

- **Fragmentary nature**: Lore often comes in small, incomplete pieces
- **Unreliable narrators**: Stories within stories may be biased or inaccurate
- **Symbolic dreams**: Not all dream content is literal
- **Cross-references**: Creatures, locations, characters → cross_references to owning skills
