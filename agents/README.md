# 🎭 loreSystem Subagents for OpenClaw

A suite of 30 specialized subagents for converting narrative chapters into loreSystem entities.

**Built for [OpenClaw](https://github.com/openclaw/openclaw)** - Personal AI Assistant with subagent orchestration.

## Overview

Each subagent specializes in extracting specific entity types from narrative text and converting them to structured loreSystem entities. Invoke the appropriate subagent based on what entities you need to extract.

## The 30 Subagent Professions

| # | Subagent | Entity Types | Count |
|---|------------|--------------|-------|
| 1 | narrative-specialist | Story, Chapter, Act, Episode, etc. | 8 |
| 2 | character-architect | Character, Evolution, Relationships, etc. | 7 |
| 3 | quest-designer | Quest, Chain, Objectives, etc. | 9 |
| 4 | progression-engineer | Skills, Perks, Attributes, etc. | 10 |
| 5 | world-geographer | Locations, Zones, Dungeons, etc. | 11 |
| 6 | environmental-scientist | Weather, Atmosphere, Lighting, etc. | 6 |
| 7 | historian | Eras, Timelines, Festivals, etc. | 10 |
| 8 | political-scientist | Government, Laws, Courts, etc. | 13 |
| 9 | economist | Trade, Currency, Markets, etc. | 13 |
| 10 | faction-analyst | Factions, Ideology, Territory, etc. | 7 |
| 11 | military-strategist | Armies, Weapons, Fortifications, etc. | 10 |
| 12 | religious-scholar | Cults, Rituals, Miracles, etc. | 11 |
| 13 | lore-chronicler | Lore fragments, Bestiary, Secrets, etc. | 8 |
| 14 | content-creator | Mods, Maps, Localization, etc. | 10 |
| 15 | achievement-specialist | Achievements, Trophies, Badges, Titles, Ranks, Leaderboards | 6 |
| 16 | audio-director | Music, Sound Effects, Ambient, Motifs, Scores | 9 |
| 17 | visual-effects-artist | Visual Effects, Particles, Shaders, Lighting, Color Palettes | 5 |
| 18 | cinematic-director | Cutscenes, Cinematics, Camera Paths, Transitions, Fades, Flashbacks | 6 |
| 19 | media-analyst | Newspapers, Radio, TV, Internet, Social Media, Propaganda, Rumors | 7 |
| 20 | transportation-engineer | Mounts, Familiars, Vehicles, Airships, Spaceships, Portals, Teleporters | 9 |
| 21 | celestial-scientist | Galaxies, Nebulae, Black Holes, Wormholes, Star Systems, Moons, Eclipses, Solstices | 9 |
| 22 | biology-specialist | Food Chains, Migrations, Hibernation, Reproduction, Extinction, Evolution | 6 |
| 23 | urban-architect | Districts, Wards, Quarters, Plazas, Market Squares, Slums, Noble Districts, Port Districts | 8 |
| 24 | research-education-specialist | Academies, Universities, Schools, Libraries, Research Centers, Archives, Museums | 7 |
| 25 | puzzle-secrets-designer | Hidden Paths, Easter Eggs, Mysteries, Enigmas, Riddles, Puzzles, Traps | 7 |
| 26 | ui-content-specialist | Choices, Flowcharts, Handouts, Tokenboards, Tags, Templates, Inspiration, Notes | 8 |
| 27 | analytics-balance-specialist | Player Metrics, Session Data, Heatmaps, Drop Rates, Conversion Rates, Difficulty Curves, Loot Table Weights | 8 |
| 28 | legendary-items-specialist | Legendary Weapons, Mythical Armor, Divine Items, Cursed Items, Artifact Sets, Relic Collections, Glyphs, Runes, Sockets, Enchantments | 10 |
| 29 | social-cultural-specialist | Affinity, Disposition, Honor, Karma, Social Classes, Social Mobility, Festivals, Celebrations, Ceremonies, Competitions, Tournaments | 11 |
| 30 | technical-director | All remaining 193 technical entities (achievements, items, audio, visual, cinematic, transport, legendary items, biology, architecture, player systems) | 193 |
| **TOTAL** | **All loreSystem entities** | **295** |

## Usage

### Invoking a Subagent

When you need to extract specific entities from narrative text, invoke the appropriate subagent:

```
> "Extract narrative entities from Chapter 1: [text]"
> "Analyze the political systems in this chapter: [text]"
> "Identify all characters and their relationships: [text]"
```

### Multiple Subagents

For comprehensive extraction, invoke multiple subagents in parallel:

```
> "Extract all entities from this chapter using:
   - narrative-specialist for story structure
   - character-architect for characters
   - world-geographer for locations
   - quest-designer for quests"
```

### Input Format

Provide chapter text to the subagent with context:

```
> "Extract [entity type] entities from this chapter text:

   Chapter 7: The Awakening

   As dawn broke over Eldoria, Kira realized her journey was just beginning.
   Two paths lay before her: the mountain pass to the north, or the
   ancient forest to the east. The elder had promised her a reward
   if she found her brother."
```

### Output Format

Each subagent generates JSON output following the loreSystem schema:

```json
{
  "entity_type": {
    "id": "uuid",
    "name": "Entity Name",
    "field1": "value1",
    "field2": "value2"
  }
}
```

## Entity Coverage by Subagent

| Subagent | Primary Entities | Secondary Entities |
|-----------|-----------------|-------------------|
| narrative-specialist | story, chapter, act, episode, prologue, epilogue, plot_branch, branch_point | - |
| character-architect | character, character_evolution, character_profile_entry, character_relationship, character_variant, voice_actor, motion_capture | - |
| quest-designer | quest, quest_chain, quest_node, quest_giver, quest_objective, quest_prerequisite, quest_reward_tier, quest_tracker, moral_choice | - |
| progression-engineer | skill, perk, attribute, ability_tree, ability, level_requirement, experience_curve, mastery_path, class_progression, specializtion, unlock_criterion | - |
| world-geographer | location, hub_area, instance, dungeon, raid, arena, open_world_zone, underground, skybox, dimension, pocket_dimension | - |
| environmental-scientist | weather_system, atmosphere, lighting_config, time_of_day, season, environmental_hazard | - |
| historian | era, timeline, festival, historical_event, calendar_system, chronicle, monument, artifact, legend, prophecy | - |
| political-scientist | government, law, court, treaty, alliance, election, policy, faction_relation, territory_claim, casus_belli, diplomat, embassy, embassy, witness | - |
| economist | trade_route, currency, market, shop, auction_house, bank, tax, tariff, trade_agreement, resource_node, supply_chain, demand_curve, price_fluctuation, trade_sanction | - |
| faction-analyst | faction, faction_member, faction_territory, faction_ideology, faction_reputation, faction_conflict, faction_alliance | - |
| military-strategist | army, navy, air_force, weapon, fortification, siege_equipment, military_rank, battle_formation, war_plan, veteran | - |
| religious-scholar | religion, cult, ritual, miracle, prophecy, religious_text, temple, shrine, priest, pilgrimage, religious_festival | - |
| lore-chronicler | lore_fragment, bestiary_entry, secret, myth, legend, artifact, ancient_language, prophecy | - |
| content-creator | mod, custom_map, localization, voice_pack, cosmetic_pack, campaign, scenario, character_creator, guild_hall, housing | - |
| achievement-specialist | achievement, trophy, badge, title, rank, leaderboard | - |
| audio-director | music_track, sound_effect, ambient, motif, score, soundtrack, music_theme, voice_line, music_control, music_state | - |
| visual-effects-artist | visual_effect, particle, shader, lighting, color_palette | - |
| cinematic-director | cutscene, cinematic, camera_path, transition, fade, flashback | - |
| media-analyst | newspaper, radio, television, internet, social_media, propaganda, rumor | - |
| transportation-engineer | mount, familiar, mount_equipment, vehicle, airship, spaceship, portal, teleporter, fast_travel_point | - |
| celestial-scientist | galaxy, nebula, black_hole, wormhole, star_system, moon, eclipse, solstice, celestial_body | - |
| biology-specialist | food_chain, migration, hibernation, reproduction, extinction, evolution | - |
| urban-architect | district, ward, quarter, plaza, market_square, slum, noble_district, port_district | - |
| research-education-specialist | academy, university, school, library, research_center, archive, museum | - |
| puzzle-secrets-designer | secret_area, hidden_path, easter_egg, mystery, enigma, riddle, puzzle, trap | - |
| ui-content-specialist | choice, flowchart, handout, tokenboard, tag, template, inspiration, note | - |
| analytics-balance-specialist | player_metric, session_data, heatmap, drop_rate, conversion_rate, difficulty_curve, loot_table_weight, balance_entity | - |
| legendary-items-specialist | legendary_weapon, mythical_armor, divine_item, cursed_item, artifact_set, relic_collection, glyph, rune, socket, enchantment | - |
| social-cultural-specialist | affinity, disposition, honor, karma, social_class, social_mobility, festival, celebration, ceremony, competition, tournament | - |
| technical-director | All remaining 193 entities: achievement systems, inventory & items, content organization, creative tools, interactive systems, audio systems, visual systems, cinematic systems, narrative devices, events & disasters, progression & save systems, legal extras, research & education, media & communication, secrets & puzzles, art & culture, transport & travel, legendary items, biology & ecology, astronomy & space, advanced architecture, player systems, balance systems, game mechanics | - |

## Configuration

### Adding New Subagents

Create a new skill file in `skills/<subagent-name>.md` following the format:

```markdown
# Subagent Name

## Trigger Phrases
- "extract [domain] entities"
- "analyze [domain]"
- "identify [entities]"

## Domain Expertise
- Expertise area 1
- Expertise area 2

## Entity Types
- entity1 - Description
- entity2 - Description

## Processing Guidelines
1. Step 1
2. Step 2
3. Step 3

## Output Format
Generate `entities/<type>.json` with schema-compliant entities.
```

## License

MIT - See LICENSE file in repository root.
