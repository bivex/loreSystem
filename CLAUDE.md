# MythWeave Chronicles — Lore System

## Project Overview

Complete lore management system for AAA game development. Extracts, validates, and manages 200+ entity types across 34 categories from narrative text.

**Architecture:** DDD (Domain-Driven Design) — `src/domain/`, `src/application/`, `src/infrastructure/`, `src/presentation/`
**Language:** Python 3.11+
**MCP Server:** `lore_mcp_server/` — standalone MCP server for lore CRUD operations

## Quick Commands

```bash
# Run tests
python -m pytest tests/ -v

# Run MCP server
python lore_mcp_server/server.py

# Run main app
python main.py
```

## Key Directories

- `src/domain/` — Domain model, entities, value objects, repository interfaces
- `src/application/` — Use cases, services
- `src/infrastructure/` — SQLite/InMemory repository implementations
- `src/presentation/` — CLI, API layer
- `lore_mcp_server/` — MCP server (separate package)
- `.claude/skills/` — 33 domain extraction skills
- `entities/` — Extracted entity output (JSON)
- `examples/` — Sample lore JSON files
- `tests/` — Test suite

## Entity Extraction System

This project uses **domain skills** (`.claude/skills/`) to extract entities from narrative text. Each skill is a specialist:

### Skill Categories

**Core Narrative** (work together on story structure):
- `narrative-writing` — Story, chapters, acts, plot branches
- `character-design` — Characters, relationships, evolution
- `quest-design` — Quests, objectives, moral choices
- `lore-writing` — Lore fragments, codex, bestiary, dreams

**World Building** (spatial and environmental):
- `world-building` — Geography, locations, dungeons, dimensions
- `environmental-design` — Climate, weather, atmosphere, lighting
- `urban-design` — City districts, markets, plazas

**Social & Political** (societies and power):
- `faction-design` — Factions, hierarchies, territories
- `political-analysis` — Governments, laws, courts
- `social-culture` — Social class, honor, karma, festivals
- `religious-lore` — Cults, rituals, blessings, curses
- `historical-research` — Eras, timelines, calendars

**Game Systems** (mechanics and progression):
- `progression-design` — Skills, perks, XP, talent trees
- `economic-modeling` — Trade, currency, markets
- `legendary-items` — Artifacts, runes, enchantments
- `achievement-design` — Achievements, trophies, ranks
- `puzzle-design` — Puzzles, riddles, traps, Easter eggs
- `military-strategy` — Armies, weapons, fortifications

**Technical & Media** (production and aesthetics):
- `cinematic-direction` — Cutscenes, camera paths
- `audio-direction` — Music, sound effects, motifs
- `vfx-design` — Particles, shaders, visual effects
- `transport-design` — Mounts, vehicles, portals
- `content-management` — Mods, localization, UGC
- `media-analysis` — Newspapers, propaganda, rumors
- `research-design` — Academies, libraries, archives
- `biology-design` — Ecosystems, evolution, food chains
- `celestial-science` — Galaxies, stars, cosmic events
- `ui-design` — Player choices, flowcharts, tags
- `analytics-balance` — Metrics, difficulty curves, loot tables

**Base Skills** (infrastructure, auto-loaded):
- `lore-extraction` — Base extraction rules for all agents
- `entity-validator` — Validation rules for extracted entities
- `json-formatter` — JSON output formatting rules
- `technical-systems` — Safety net, catches remaining 193 entity types

## Agent Team Workflow

When working as a team on lore extraction:

### Team Roles

1. **Lead (Orchestrator)** — Breaks text into domains, assigns to teammates, merges results, resolves cross-references. Uses delegate mode.
2. **Narrative Team** — `narrative-writing` + `character-design` + `quest-design` + `lore-writing`
3. **World Team** — `world-building` + `environmental-design` + `urban-design`
4. **Society Team** — `faction-design` + `political-analysis` + `social-culture` + `religious-lore` + `historical-research`
5. **Systems Team** — `progression-design` + `economic-modeling` + `legendary-items` + remaining game mechanics
6. **Technical Team** — `cinematic-direction` + `audio-direction` + `vfx-design` + `technical-systems`

### Coordination Rules

- **Each teammate owns a domain** — do NOT edit entities outside your assigned category
- **Cross-references**: When you find an entity that belongs to another domain, note it in your output as `"cross_ref": { "domain": "...", "entity": "...", "note": "..." }` — the lead will route it
- **Output format**: Always produce valid JSON following loreSystem schema. Use UUIDs for IDs.
- **File ownership**: Write output to `entities/<your-domain>.json` — each teammate writes to their own file
- **Deduplication**: The lead merges and deduplicates across domains after all teammates finish

### Task Workflow

1. Lead reads source text and creates tasks per domain
2. Each teammate claims their domain tasks
3. Teammates extract entities using their skills
4. Teammates report findings with cross-references
5. Lead merges, deduplicates, validates final output
6. Lead writes merged result to `entities/`

## Conventions

- All entity IDs are UUIDs
- All output must be valid JSON
- Entity names are human-readable, not slugs
- Relationships reference other entities by ID
- Every entity has at minimum: `id`, `name`, `type`
- Use `snake_case` for field names
- Timestamps in ISO 8601 format
