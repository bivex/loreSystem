# loreSystem Subagents for OpenClaw - Quick Start

## Configuration Complete

All 30 subagents are now configured in `SUBAGENTS_CONFIG.json`.

## Quick Start

### Option 1: Spawn Individual Subagent

```bash
openclaw agent spawn "Extract character entities" --label "Character Architect"
```

### Option 2: Spawn Using Config Key

```bash
openclaw agent spawn --config SUBAGENTS_CONFIG.json --key "character-architect"
```

### Option 3: Batch Spawn Multiple Subagents

```bash
# Spawn multiple subagents in parallel
openclaw agent spawn --config SUBAGENTS_CONFIG.json --key "narrative-specialist" &
openclaw agent spawn --config SUBAGENTS_CONFIG.json --key "character-architect" &
openclaw agent spawn --config SUBAGENTS_CONFIG.json --key "quest-designer" &
openclaw agent spawn --config SUBAGENTS_CONFIG.json --key "world-geographer"
```

## List Active Subagents

```bash
/subagents list
```

## Stop a Subagent

```bash
/subagents stop <run-id>
```

## View Subagent Log

```bash
/subagents log <run-id>
```

## Quick Reference - All 30 Subagents

| # | Subagent | Entities | Output File |
|---|------------|----------|-------------|
| 1 | narrative-specialist | 8 narrative | entities/narrative.json |
| 2 | character-architect | 7 character | entities/character.json |
| 3 | quest-designer | 9 quest | entities/quest.json |
| 4 | progression-engineer | 10 progression | entities/progression.json |
| 5 | world-geographer | 11 location | entities/world.json |
| 6 | environmental-scientist | 6 environmental | entities/environment.json |
| 7 | historian | 10 historical | entities/historical.json |
| 8 | political-scientist | 13 political | entities/political.json |
| 9 | economist | 13 economic | entities/economy.json |
| 10 | faction-analyst | 7 faction | entities/faction.json |
| 11 | military-strategist | 10 military | entities/military.json |
| 12 | religious-scholar | 11 religious | entities/religious.json |
| 13 | lore-chronicler | 8 lore | entities/lore.json |
| 14 | content-creator | 10 content | entities/content.json |
| 15 | achievement-specialist | 6 achievement | entities/achievement.json |
| 16 | audio-director | 9 audio | entities/audio.json |
| 17 | visual-effects-artist | 5 visual | entities/visual.json |
| 18 | cinematic-director | 6 cinematic | entities/cinematic.json |
| 19 | media-analyst | 7 media | entities/media.json |
| 20 | transportation-engineer | 9 transport | entities/transportation.json |
| 21 | celestial-scientist | 9 celestial | entities/celestial.json |
| 22 | biology-specialist | 6 biology | entities/biology.json |
| 23 | urban-architect | 8 urban | entities/urban.json |
| 24 | research-education-specialist | 7 research | entities/research.json |
| 25 | puzzle-secrets-designer | 7 puzzle | entities/puzzle.json |
| 26 | ui-content-specialist | 8 UI | entities/ui_content.json |
| 27 | analytics-balance-specialist | 8 analytics | entities/analytics.json |
| 28 | legendary-items-specialist | 10 legendary | entities/legendary.json |
| 29 | social-cultural-specialist | 11 social | entities/social_cultural.json |
| 30 | technical-director | 193 technical | entities/technical.json |
| **TOTAL** | **All loreSystem entities** | **295** |

## Full Entity Count Breakdown

### Narrative (8)
story, chapter, act, episode, prologue, epilogue, plot_branch, branch_point

### Character (7)
character, character_evolution, character_profile_entry, character_relationship, character_variant, voice_actor, motion_capture

### Quest (9)
quest, quest_chain, quest_node, quest_giver, quest_objective, quest_prerequisite, quest_reward_tier, quest_tracker, moral_choice

### Progression (10)
skill, perk, trait, attribute, experience, level_up, talent_tree, mastery, progression_event, progression_state

### World (11)
location, hub_area, instance, dungeon, raid, arena, open_world_zone, underground, skybox, dimension, pocket_dimension

### Environmental (6)
environment, weather_pattern, atmosphere, lighting, time_period, disaster

### Historical (10)
era, era_transition, timeline, calendar, festival, celebration, ceremony, exhibition, tournament, competition

### Political (13)
government, law, legal_system, court, judge, jury, lawyer, crime, punishment, evidence, witness, treaty, constitution

### Economic (13)
trade, barter, tax, tariff, supply, demand, price, inflation, currency, shop, purchase, reward, loot_table_weight

### Faction (7)
faction, faction_hierarchy, faction_ideology, faction_leader, faction_membership, faction_resource, faction_territory

### Military (10)
army, fleet, battalion, weapon_system, defense, fortification, siege_engine, war, invasion, revolution

### Religious (11)
cult, sect, holy_site, scripture, ritual, oath, summon, pact, curse, blessing, miracle

### Lore (8)
lore_fragment, codex_entry, journal_page, bestiary_entry, memory, dream, nightmare, secret_area

### Content (10)
mod, custom_map, user_scenario, share_code, workshop_entry, localization, translation, subtitle, dubbing, voice_over

### Achievement (6)
achievement, trophy, badge, title, rank, leaderboard

### Audio (9)
music_track, music_theme, motif, score, soundtrack, voice_line, sound_effect, ambient, music_control, music_state

### Visual (5)
visual_effect, particle, shader, lighting, color_palette

### Cinematic (6)
cutscene, cinematic, camera_path, transition, fade, flashback

### Media (7)
newspaper, radio, television, internet, social_media, propaganda, rumor

### Transport (9)
mount, familiar, mount_equipment, vehicle, spaceship, airship, portal, teleporter

### Celestial (9)
galaxy, nebula, black_hole, wormhole, star_system, moon, eclipse, solstice, celestial_body

### Biology (6)
food_chain, migration, hibernation, reproduction, extinction, evolution

### Urban (8)
district, ward, quarter, plaza, market_square, slum, noble_district, port_district

### Research (7)
research, academy, university, school, library, research_center, archive, museum

### Puzzle (7)
secret_area, hidden_path, easter_egg, mystery, enigma, riddle, puzzle, trap

### UI (8)
choice, flowchart, handout, tokenboard, tag, template, inspiration, note

### Analytics (8)
player_metric, session_data, heatmap, drop_rate, conversion_rate, difficulty_curve, loot_table_weight, balance_entity

### Legendary (10)
legendary_weapon, mythical_armor, divine_item, cursed_item, artifact_set, relic_collection, glyph, rune, socket, enchantment

### Social (11)
affinity, disposition, honor, karma, social_class, social_mobility, festival, celebration, ceremony, competition, tournament

### Technical (193)
All remaining entities: achievements, inventory, content, creative tools, interactive systems, audio systems, visual systems, cinematic systems, narrative devices, events, progression, legal, research, media, secrets, art, transport, legendary, biology, celestial, architecture, player systems, balance, game mechanics
