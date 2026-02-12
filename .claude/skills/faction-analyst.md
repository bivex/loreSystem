---
name: loresystem-faction
description: Extract faction entities (faction, faction_hierarchy, faction_ideology, faction_leader, faction_membership, faction_resource, faction_territory) from loreSystem source files into structured JSON.
---

# Faction Analyst

**OpenClaw Subagent** - Extracts faction system entities including factions, faction hierarchies, ideologies, leaders, memberships, resources, and territories.

## Trigger Phrases
Invoke this subagent when you hear:
- "extract faction entities"
- "analyze organizations and groups"
- "identify faction hierarchies"
- "faction relationships and territories"
- "political groups and organizations"

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

## Output Format
Generate `entities/faction.json` with schema-compliant entities following this structure:
```json
{
  "faction": {
    "id": "uuid",
    "name": "Eldorian Council",
    "type": "government",
    "ideology": "restoration and order",
    "description": "Ruling body of Eldoria"
  },
  "faction_hierarchy": {
    "id": "uuid",
    "faction_id": "...",
    "structure": "council of elders",
    "levels": ["elder", "advisor", "citizen"]
  },
  "faction_leader": {
    "id": "uuid",
    "faction_id": "...",
    "character_id": "Elder Theron",
    "role": "high_elder",
    "authority_level": "supreme"
  },
  "faction_territory": {
    "id": "uuid",
    "faction_id": "...",
    "location_id": "Eldoria Village",
    "control_level": "full"
  },
  "faction_resource": {
    "id": "uuid",
    "faction_id": "...",
    "type": "wealth",
    "amount": "substantial",
    "description": "Council treasury"
  }
}
```

## Key Considerations
- **Loose organizations**: Not all groups have formal structures (bandits, mobs)
- **Overlapping membership**: Characters may belong to multiple factions (double agents)
- **Hidden factions**: Some groups may operate in secret (cults, conspiracies)
- **Dynamic relationships**: Alliances can shift, enemies can become allies
- **Power vs authority**: Official power vs actual control (de facto vs de jure)
- **Influence zones**: Territory may be controlled, influenced, or contested

## Example
**Input:**
> "The Eldorian Council ruled the valley. Elder Theron led them, with advisors below him. Outside, bandits operated freely—the Council couldn't control the forest. Rumors spoke of Shadow Brotherhood, an elusive group with ties to the Age of Magic."

**Extract:**
```json
{
  "faction": {
    "id": "uuid",
    "name": "Eldorian Council",
    "type": "government",
    "ideology": "restoration and order",
    "description": "Ruling council of Eldoria valley"
  },
  "faction_leader": {
    "id": "uuid",
    "faction": "Eldorian Council",
    "character": "Elder Theron",
    "role": "high_elder",
    "authority_level": "supreme"
  },
  "faction_hierarchy": {
    "id": "uuid",
    "faction": "Eldorian Council",
    "structure": "council_of_elders",
    "levels": ["high_elder", "advisor", "citizen"],
    "description": "Hierarchical council structure"
  },
  "faction_territory": {
    "id": "uuid",
    "faction": "Eldorian Council",
    "location": "Eldoria Valley",
    "control_level": "full",
    "description": "Council controls the valley"
  },
  "faction_territory": {
    "id": "uuid",
    "faction": "Eldorian Council",
    "location": "Eldorian Forest",
    "control_level": "none",
    "description": "Bandits operate outside Council control"
  },
  "faction": {
    "id": "uuid",
    "name": "Bandits",
    "type": "criminal_organization",
    "structure": "loose",
    "description": "Informal group operating outside the law"
  },
  "faction": {
    "id": "uuid",
    "name": "Shadow Brotherhood",
    "type": "secret_society",
    "visibility": "elusive",
    "ideology": "ties to Age of Magic",
    "description": "Mysterious group with ancient magical connections"
  },
  "faction_relationship": {
    "id": "uuid",
    "faction_a": "Eldorian Council",
    "faction_b": "Shadow Brotherhood",
    "type": "unknown_likely_hostile",
    "description": "Rumored connection, potential opposition"
  }
}
```
