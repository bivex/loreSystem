---
name: religious-lore
description: Extract religious entities from narrative text. Use when analyzing cults, sects, holy sites, scriptures, rituals, oaths, summons, pacts, curses, blessings, and miracles.
---
# religious-lore

Доменный скилл для Religious Scholar. Специфические правила извлечения и экспертиза.

## Domain Expertise

- **Religious systems**: Monotheism, polytheism, animism, cults
- **Sacred places**: Temples, shrines, holy sites
- **Rituals**: Ceremonies, prayers, summoning, blessings
- **Supernatural**: Miracles, curses, pacts, divine intervention
- **Religious conflict**: Heresy, crusades, holy wars

## Entity Types (11 total)

- **cult** - Cults and sects
- **sect** - Religious sects
- **holy_site** - Holy places
- **scripture** - Religious texts
- **ritual** - Rituals and ceremonies
- **oath** - Oaths and vows
- **summon** - Summoning rituals
- **pact** - Pacts and agreements
- **curse** - Curses
- **blessing** - Blessings
- **miracle** - Miracles

## Processing Guidelines

When extracting religious entities from chapter text:

1. **Identify religious elements**:
   - Gods, deities, divine beings mentioned
   - Temples, shrines, holy sites
   - Rituals, ceremonies, prayers
   - Curses, blessings, miracles
   - Cults, sects, religious groups

2. **Extract religious details**:
   - Deity names, domains, powers
   - Sacred places and their significance
   - Ritual procedures and meanings
   - Curse/blessing effects
   - Religious organizations

3. **Analyze religious context**:
   - Faith levels in the world
   - Religious diversity or dominance
   - Supernatural presence and power
   - Religious conflict or tolerance

4. **Create schema-compliant entities** with proper JSON structure

## Key Considerations

- **Multiple faiths**: Worlds often have competing religions
- **Lost religions**: Ancient faiths may have faded
- **Heretical practices**: Cults vs mainstream religion
- **Divine power**: Not all prayers are answered
