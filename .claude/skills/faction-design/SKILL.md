---
name: faction-design
description: Extract faction entities from narrative text. Use when analyzing organizations, hierarchies, ideologies, faction territories, resources, leaders, and inter-faction relationships.
---
# faction-design

Доменный скилл для Faction Analyst. Специфические правила извлечения и экспертиза.

## Domain Expertise

- **Faction types**: Governments, guilds, cults, criminal organizations, rebels
- **Group dynamics**: Internal politics, leadership struggles, faction divisions
- **Ideologies**: Beliefs, goals, motivations, worldviews
- **Territory**: Geographical control, influence zones, borders
- **Resources**: Wealth, military power, information, magic, technology

## Entity Types (7 total)

- **faction** - Factions and organizations
- **faction_hierarchy** - Faction hierarchy structures
- **faction_ideology** - Faction beliefs, ideologies
- **faction_leader** - Faction leaders
- **faction_membership** - Faction members
- **faction_resource** - Faction resources, assets
- **faction_territory** - Faction territories, controlled areas

## Processing Guidelines

When extracting faction entities from chapter text:

1. **Identify factions**:
   - Named groups (Eldorian Council, Shadow Brotherhood, Rebellion)
   - Organizations mentioned (guilds, armies, cults, orders)
   - Implied groups (bandits, rebels, authorities, resistance)
   - Informal groups (village elders, merchant alliance)

2. **Extract faction details**:
   - Faction name, type, ideology (what do they believe)
   - Leadership structure (who leads, how is power organized)
   - Members and their roles (leaders, advisors, foot soldiers)
   - Territory controlled (where do they operate)
   - Resources and power (wealth, military, magic, influence)

3. **Analyze faction relationships**:
   - Allies and enemies (who supports or opposes whom)
   - Neutral parties (uninvolved or Switzerland-types)
   - Internal divisions or conflicts (factions within factions)
   - Power dynamics (dominant vs subservient groups)

4. **Contextualize politically**:
   - How factions relate to government (official vs underground)
   - Geographic control and influence (where is power concentrated)
   - Resource competition (what are they fighting over)
   - Historical relationships (old alliances, ancient feuds)

## Key Considerations

- **Loose organizations**: Not all groups have formal structures (bandits, mobs)
- **Overlapping membership**: Characters may belong to multiple factions (double agents)
- **Hidden factions**: Some groups may operate in secret (cults, conspiracies)
- **Dynamic relationships**: Alliances can shift, enemies can become allies
- **Power vs authority**: Official power vs actual control (de facto vs de jure)
- **Influence zones**: Territory may be controlled, influenced, or contested
