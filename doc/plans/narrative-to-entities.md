# PLAN-0001: Narrative Chapter to Entities Generation (30 Agents)

Loom-based agent orchestration for converting narrative chapters into loreSystem entities using 30 specialized agent professions.

<!-- loom METADATA -->
```yaml
loom:
  version: 1
  sandbox:
    enabled: true
    auto_allow: true
    excluded_commands: ["loom"]
    filesystem:
      deny_read:
        - "~/.ssh/**"
        - "~/.aws/**"
        - "../../**"
      deny_write:
        - "../../**"
        - "agents/skills/**"
      allow_write:
        - "entities/**"
        - "scripts/**"
        - "doc/plans/**"
    network:
      allowed_domains: ["github.com", "crates.io"]
      additional_domains: []
      allow_local_binding: false
      allow_unix_sockets: false
  stages:
    - id: parse-chapter
      name: Parse Chapter Input
      description: Extract entities, relationships, context from chapter text
      working_dir: "."
      stage_type: standard
      dependencies: []
      acceptance:
        - "python scripts/validate_parse_output.py parsed_data.json"
      files:
        - "scripts/parse_chapter.py"
        - "src/domain/story/*.py"
      truths:
        - "jq '.entities | length > 0' parsed_data.json"
        - "jq '.chapter_id != null' parsed_data.json"
      artifacts:
        - "parsed_data.json"
        - "extracted_entities.json"
        - "relationships.json"
      wiring:
        - source: "parsed_data.json"
          pattern: "chapter_id"
          description: Chapter ID reference established
      execution_mode: single

    - id: narrative-specialist
      name: Narrative Specialist (8 entities)
      description: Create Story, Chapter, Act, Episode, Prologue, Epilogue, PlotBranch, BranchPoint
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/narrative-specialist.md"
        - "src/domain/story/*.py"
      truths:
        - "jq '.story | length > 0' entities/narrative.json"
        - "jq '.chapter | length > 0' entities/narrative.json"
      artifacts:
        - "entities/narrative.json"
      wiring:
        - source: "entities/narrative.json"
          pattern: "story_id"
          description: Narrative entities linked to chapter

    - id: character-architect
      name: Character Architect (7 entities)
      description: Create Character, CharacterEvolution, CharacterProfileEntry, CharacterRelationship, CharacterVariant, VoiceActor, MotionCapture
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/character-architect.md"
        - "src/domain/entities/character*.py"
      truths:
        - "jq '.character | length > 0' entities/character.json"
      artifacts:
        - "entities/character.json"
      wiring:
        - source: "entities/character.json"
          pattern: "character_id"
          description: Character entities generated

    - id: quest-designer
      name: Quest Designer (9 entities)
      description: Create Quest, QuestChain, QuestNode, QuestGiver, QuestObjective, QuestPrerequisite, QuestRewardTier, QuestTracker, MoralChoice
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/quest-designer.md"
        - "src/domain/entities/quest*.py"
      truths:
        - "jq '.quest | length > 0' entities/quest.json"
      artifacts:
        - "entities/quest.json"

    - id: progression-engineer
      name: Progression Engineer (10 entities)
      description: Create Skill, Perk, Trait, Attribute, Experience, LevelUp, TalentTree, Mastery, ProgressionEvent, ProgressionState
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/progression-engineer.md"
        - "src/domain/entities/*.py"
      truths:
        - "jq '.skill | length > 0' entities/progression.json"
      artifacts:
        - "entities/progression.json"

    - id: world-geographer
      name: World Geographer (11 entities)
      description: Create Location, HubArea, Instance, Dungeon, Raid, Arena, OpenWorldZone, Underground, Skybox, Dimension, PocketDimension
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/world-geographer.md"
        - "src/domain/entities/location*.py"
        - "src/domain/entities/dungeon*.py"
      truths:
        - "jq '.location | length > 0' entities/world.json"
      artifacts:
        - "entities/world.json"

    - id: environmental-scientist
      name: Environmental Scientist (6 entities)
      description: Create Environment, WeatherPattern, Atmosphere, Lighting, TimePeriod, Disaster
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/environmental-scientist.md"
        - "src/domain/entities/environment*.py"
      truths:
        - "jq '.environment | length > 0' entities/environment.json"
      artifacts:
        - "entities/environment.json"

    - id: historian
      name: Historian (10 entities)
      description: Create Era, EraTransition, Timeline, Calendar, Festival, Celebration, Ceremony, Exhibition, Tournament, Competition
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/historian.md"
        - "src/domain/entities/era*.py"
        - "src/domain/entities/timeline*.py"
      truths:
        - "jq '.era | length > 0' entities/historical.json"
      artifacts:
        - "entities/historical.json"

    - id: political-scientist
      name: Political Scientist (13 entities)
      description: Create Government, Law, LegalSystem, Court, Judge, Jury, Lawyer, Crime, Punishment, Evidence, Witness, Treaty, Constitution
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/political-scientist.md"
        - "src/domain/entities/government*.py"
        - "src/domain/entities/law*.py"
        - "src/domain/entities/court*.py"
        - "src/domain/entities/crime*.py"
      truths:
        - "jq '.government | length > 0' entities/political.json"
      artifacts:
        - "entities/political.json"

    - id: economist
      name: Economist (13 entities)
      description: Create Trade, Barter, Tax, Tariff, Supply, Demand, Price, Inflation, Currency, Shop, Purchase, Reward, LootTableWeight
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/economist.md"
        - "src/domain/entities/trade*.py"
        - "src/domain/entities/currency*.py"
        - "src/domain/entities/shop*.py"
      truths:
        - "jq '.trade | length > 0' entities/economy.json"
      artifacts:
        - "entities/economy.json"

    - id: faction-analyst
      name: Faction Analyst (7 entities)
      description: Create Faction, FactionHierarchy, FactionIdeology, FactionLeader, FactionMembership, FactionResource, FactionTerritory
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/faction-analyst.md"
        - "src/domain/entities/faction*.py"
      truths:
        - "jq '.faction | length > 0' entities/faction.json"
      artifacts:
        - "entities/faction.json"

    - id: military-strategist
      name: Military Strategist (10 entities)
      description: Create Army, Fleet, Battalion, WeaponSystem, Defense, Fortification, SiegeEngine, War, Invasion, Revolution
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/military-strategist.md"
        - "src/domain/entities/army*.py"
        - "src/domain/entities/fleet*.py"
        - "src/domain/entities/defense*.py"
      truths:
        - "jq '.army | length > 0' entities/military.json"
      artifacts:
        - "entities/military.json"

    - id: religious-scholar
      name: Religious Scholar (11 entities)
      description: Create Cult, Sect, HolySite, Scripture, Ritual, Oath, Summon, Pact, Curse, Blessing, Miracle
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/religious-scholar.md"
        - "src/domain/entities/cult*.py"
        - "src/domain/entities/ritual*.py"
        - "src/domain/entities/holy*.py"
      truths:
        - "jq '.cult | length > 0' entities/religious.json"
      artifacts:
        - "entities/religious.json"

    - id: lore-chronicler
      name: Lore Chronicler (8 entities)
      description: Create LoreFragment, CodexEntry, JournalPage, BestiaryEntry, Memory, Dream, Nightmare, SecretArea
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/lore-chronicler.md"
        - "src/domain/entities/lore*.py"
        - "src/domain/entities/codex*.py"
        - "src/domain/entities/journal*.py"
      truths:
        - "jq '.lore_fragment | length > 0' entities/lore.json"
      artifacts:
        - "entities/lore.json"

    - id: content-creator
      name: Content Creator (10 entities)
      description: Create Mod, CustomMap, UserScenario, ShareCode, WorkshopEntry, Localization, Translation, Subtitle, Dubbing, VoiceOver
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/content-creator.md"
        - "src/domain/entities/mod*.py"
        - "src/domain/entities/localization*.py"
      truths:
        - "jq '.mod | length > 0' entities/content.json"
      artifacts:
        - "entities/content.json"

    - id: achievement-specialist
      name: Achievement Specialist (6 entities)
      description: Create Achievement, Trophy, Badge, Title, Rank, Leaderboard
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/achievement-specialist.md"
        - "src/domain/entities/achievement*.py"
      truths:
        - "jq '.achievement | length > 0' entities/achievement.json"
      artifacts:
        - "entities/achievement.json"

    - id: audio-director
      name: Audio Director (9 entities)
      description: Create Ambient, Motif, MusicControl, MusicState, MusicTheme, MusicTrack, Score, SoundEffect, Soundtrack, Silence
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/audio-director.md"
        - "src/domain/entities/*.py"
      truths:
        - "jq '.music_track | length > 0' entities/audio.json"
      artifacts:
        - "entities/audio.json"

    - id: visual-effects-artist
      name: Visual Effects Artist (5 entities)
      description: Create VisualEffect, Particle, Shader, Lighting, ColorPalette
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/visual-effects-artist.md"
        - "src/domain/entities/*.py"
      truths:
        - "jq '.visual_effect | length > 0' entities/visual.json"
      artifacts:
        - "entities/visual.json"

    - id: cinematic-director
      name: Cinematic Director (6 entities)
      description: Create Cutscene, Cinematic, CameraPath, Transition, Fade, Flashback
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/cinematic-director.md"
        - "src/domain/entities/*.py"
      truths:
        - "jq '.cutscene | length > 0' entities/cinematic.json"
      artifacts:
        - "entities/cinematic.json"

    - id: media-analyst
      name: Media Analyst (7 entities)
      description: Create Newspaper, Radio, Television, Internet, SocialMedia, Propaganda, Rumor
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/media-analyst.md"
        - "src/domain/entities/*.py"
      truths:
        - "jq '.newspaper | length > 0' entities/media.json"
      artifacts:
        - "entities/media.json"

    - id: transportation-engineer
      name: Transportation Engineer (9 entities)
      description: Create Mount, Familiar, MountEquipment, Vehicle, Airship, Spaceship, Portal, Teleporter, FastTravelPoint
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/transportation-engineer.md"
        - "src/domain/entities/*.py"
      truths:
        - "jq '.mount | length > 0' entities/transportation.json"
      artifacts:
        - "entities/transportation.json"

    - id: celestial-scientist
      name: Celestial Scientist (9 entities)
      description: Create Galaxy, Nebula, BlackHole, Wormhole, StarSystem, Moon, Eclipse, Solstice, CelestialBody
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/celestial-scientist.md"
        - "src/domain/entities/*.py"
      truths:
        - "jq '.galaxy | length > 0' entities/celestial.json"
      artifacts:
        - "entities/celestial.json"

    - id: biology-specialist
      name: Biology Specialist (6 entities)
      description: Create FoodChain, Migration, Hibernation, Reproduction, Extinction, Evolution
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/biology-specialist.md"
        - "src/domain/entities/*.py"
      truths:
        - "jq '.food_chain | length > 0' entities/biology.json"
      artifacts:
        - "entities/biology.json"

    - id: urban-architect
      name: Urban Architect (8 entities)
      description: Create District, Ward, Quarter, Plaza, MarketSquare, Slums, NobleDistrict, PortDistrict
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/urban-architect.md"
        - "src/domain/entities/*.py"
      truths:
        - "jq '.district | length > 0' entities/urban.json"
      artifacts:
        - "entities/urban.json"

    - id: research-education-specialist
      name: Research & Education Specialist (7 entities)
      description: Create Academy, University, School, Library, ResearchCenter, Archive, Museum
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/research-education-specialist.md"
        - "src/domain/entities/*.py"
      truths:
        - "jq '.academy | length > 0' entities/research.json"
      artifacts:
        - "entities/research.json"

    - id: puzzle-secrets-designer
      name: Puzzle & Secrets Designer (7 entities)
      description: Create HiddenPath, EasterEgg, Mystery, Enigma, Riddle, Puzzle, Trap
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/puzzle-secrets-designer.md"
        - "src/domain/entities/*.py"
      truths:
        - "jq '.puzzle | length > 0' entities/puzzle.json"
      artifacts:
        - "entities/puzzle.json"

    - id: ui-content-specialist
      name: UI/Content Specialist (8 entities)
      description: Create Choice, Flowchart, Handout, Tokenboard, Tag, Template, Inspiration, Note
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/ui-content-specialist.md"
        - "src/domain/entities/*.py"
      truths:
        - "jq '.choice | length > 0' entities/ui_content.json"
      artifacts:
        - "entities/ui_content.json"

    - id: analytics-balance-specialist
      name: Analytics & Balance Specialist (8 entities)
      description: Create PlayerMetric, SessionData, Heatmap, DropRate, ConversionRate, DifficultyCurve, LootTableWeight, BalanceEntities
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/analytics-balance-specialist.md"
        - "src/domain/entities/*.py"
      truths:
        - "jq '.difficulty_curve | length > 0' entities/analytics.json"
      artifacts:
        - "entities/analytics.json"

    - id: legendary-items-specialist
      name: Legendary Items Specialist (10 entities)
      description: Create LegendaryWeapon, MythicalArmor, DivineItem, CursedItem, ArtifactSet, RelicCollection, Glyph, Rune, Socket, Enchantment
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/legendary-items-specialist.md"
        - "src/domain/entities/*.py"
      truths:
        - "jq '.legendary_weapon | length > 0' entities/legendary.json"
      artifacts:
        - "entities/legendary.json"

    - id: social-cultural-specialist
      name: Social & Cultural Specialist (11 entities)
      description: Create Affinity, Disposition, Honor, Karma, SocialClass, SocialMobility, Festival, Celebration, Ceremony, Competition, Tournament
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/social-cultural-specialist.md"
        - "src/domain/entities/*.py"
      truths:
        - "jq '.social_class | length > 0' entities/social_cultural.json"
      artifacts:
        - "entities/social_cultural.json"

    - id: game-mechanics-specialist
      name: Game Mechanics Specialist (13 entities)
      description: Create Event, EventChain, AlternateReality, Consequence, Ending, Patent, Invention, Improvement, Requirement, Pull, Phenomenon, Pity, Theme
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/game-mechanics-specialist.md"
        - "src/domain/entities/*.py"
      truths:
        - "jq '.event | length > 0' entities/mechanics.json"
      artifacts:
        - "entities/mechanics.json"

    - id: validate-entities
      name: Validate All Entities
      description: Validate all generated entity JSON files against loreSystem domain model and schema
      working_dir: "."
      stage_type: integration-verify
      dependencies:
        - "narrative-specialist"
        - "character-architect"
        - "quest-designer"
        - "progression-engineer"
        - "world-geographer"
        - "environmental-scientist"
        - "historian"
        - "political-scientist"
        - "economist"
        - "faction-analyst"
        - "military-strategist"
        - "religious-scholar"
        - "lore-chronicler"
        - "content-creator"
        - "achievement-specialist"
        - "audio-director"
        - "visual-effects-artist"
        - "cinematic-director"
        - "media-analyst"
        - "transportation-engineer"
        - "celestial-scientist"
        - "biology-specialist"
        - "urban-architect"
        - "research-education-specialist"
        - "puzzle-secrets-designer"
        - "ui-content-specialist"
        - "analytics-balance-specialist"
        - "legendary-items-specialist"
        - "social-cultural-specialist"
        - "game-mechanics-specialist"
      acceptance:
        - "python scripts/validate_entities.py entities/ --strict"
      truths:
        - "python scripts/validate_schema.py entities/ --all-files"
      artifacts:
        - "validation_report.json"
        - "validation_summary.json"

    - id: persist-to-sqlite
      name: Persist Entities to SQLite
      description: Insert all validated entities into loreSystem database
      working_dir: "."
      stage_type: standard
      dependencies: ["validate-entities"]
      acceptance:
        - "python scripts/verify_sqlite_inserts.py lore_system.db entities/"
      truths:
        - "sqlite3 lore_system.db 'SELECT COUNT(*) FROM story > 0'"
        - "sqlite3 lore_system.db 'SELECT COUNT(*) FROM character > 0'"
        - "sqlite3 lore_system.db 'SELECT COUNT(*) FROM quest > 0'"
      artifacts:
        - "lore_system.db"
        - "insert_log.json"
        - "insert_summary.json"
```
<!-- END loom METADATA -->

## Entity Coverage

| Agent Profession | Entities Covered | Count |
|------------------|------------------|-------|
| Narrative Specialist | story, chapter, act, episode, prologue, epilogue, plot_branch, branch_point | 8 |
| Character Architect | character, character_evolution, character_profile_entry, character_relationship, character_variant, voice_actor, motion_capture | 7 |
| Quest Designer | quest, quest_chain, quest_node, quest_giver, quest_objective, quest_prerequisite, quest_reward_tier, quest_tracker, moral_choice | 9 |
| Progression Engineer | skill, perk, trait, attribute, experience, level_up, talent_tree, mastery, progression_event, progression_state | 10 |
| World Geographer | location, hub_area, instance, dungeon, raid, arena, open_world_zone, underground, skybox, dimension, pocket_dimension | 11 |
| Environmental Scientist | environment, weather_pattern, atmosphere, lighting, time_period, disaster | 6 |
| Historian | era, era_transition, timeline, calendar, festival, celebration, ceremony, exhibition, tournament, competition | 10 |
| Political Scientist | government, law, legal_system, court, judge, jury, lawyer, crime, punishment, evidence, witness, treaty, constitution | 13 |
| Economist | trade, barter, tax, tariff, supply, demand, price, inflation, currency, shop, purchase, reward, loot_table_weight | 13 |
| Faction Analyst | faction, faction_hierarchy, faction_ideology, faction_leader, faction_membership, faction_resource, faction_territory | 7 |
| Military Strategist | army, fleet, battalion, weapon_system, defense, fortification, siege_engine, war, invasion, revolution | 10 |
| Religious Scholar | cult, sect, holy_site, scripture, ritual, oath, summon, pact, curse, blessing, miracle | 11 |
| Lore Chronicler | lore_fragment, codex_entry, journal_page, bestiary_entry, memory, dream, nightmare, secret_area | 8 |
| Content Creator | mod, custom_map, user_scenario, share_code, workshop_entry, localization, translation, subtitle, dubbing, voice_over | 10 |
| Achievement Specialist | achievement, trophy, badge, title, rank, leaderboard | 6 |
| Audio Director | ambient, motif, music_control, music_state, music_theme, music_track, score, sound_effect, soundtrack, silence | 9 |
| Visual Effects Artist | visual_effect, particle, shader, lighting, color_palette | 5 |
| Cinematic Director | cutscene, cinematic, camera_path, transition, fade, flashback | 6 |
| Media Analyst | newspaper, radio, television, internet, social_media, propaganda, rumor | 7 |
| Transportation Engineer | mount, familiar, mount_equipment, vehicle, airship, spaceship, portal, teleporter, fast_travel_point | 9 |
| Celestial Scientist | galaxy, nebula, black_hole, wormhole, star_system, moon, eclipse, solstice, celestial_body | 9 |
| Biology Specialist | food_chain, migration, hibernation, reproduction, extinction, evolution | 6 |
| Urban Architect | district, ward, quarter, plaza, market_square, slums, noble_district, port_district | 8 |
| Research & Education Specialist | academy, university, school, library, research_center, archive, museum | 7 |
| Puzzle & Secrets Designer | hidden_path, easter_egg, mystery, enigma, riddle, puzzle, trap | 7 |
| UI/Content Specialist | choice, flowchart, handout, tokenboard, tag, template, inspiration, note | 8 |
| Analytics & Balance Specialist | player_metric, session_data, heatmap, drop_rate, conversion_rate, difficulty_curve, loot_table_weight, balance_entities | 8 |
| Legendary Items Specialist | legendary_weapon, mythical_armor, divine_item, cursed_item, artifact_set, relic_collection, glyph, rune, socket, enchantment | 10 |
| Social & Cultural Specialist | affinity, disposition, honor, karma, social_class, social_mobility, festival, celebration, ceremony, competition, tournament | 11 |
| Game Mechanics Specialist | event, event_chain, alternate_reality, consequence, ending, patent, invention, improvement, requirement, pull, phenomenon, pity, theme | 13 |
| **TOTAL** | **All 295 entities** | **295** |

## Usage

```bash
cd /root/clawd
loom init doc/plans/narrative-to-entities.md
loom run --max-parallel 30  # All 30 agents working in parallel
loom status --live
```

## Output Structure

```
entities/
├── narrative.json          # 8 entities
├── character.json          # 7 entities
├── quest.json              # 9 entities
├── progression.json        # 10 entities
├── world.json              # 11 entities
├── environment.json        # 6 entities
├── historical.json         # 10 entities
├── political.json          # 13 entities
├── economy.json            # 13 entities
├── faction.json            # 7 entities
├── military.json           # 10 entities
├── religious.json          # 11 entities
├── lore.json               # 8 entities
├── content.json            # 10 entities
├── achievement.json         # 6 entities
├── audio.json              # 9 entities
├── visual.json             # 5 entities
├── cinematic.json          # 6 entities
├── media.json              # 7 entities
├── transportation.json      # 9 entities
├── celestial.json          # 9 entities
├── biology.json            # 6 entities
├── urban.json              # 8 entities
├── research.json           # 7 entities
├── puzzle.json             # 7 entities
├── ui_content.json         # 8 entities
├── analytics.json          # 8 entities
├── legendary.json          # 10 entities
├── social_cultural.json    # 11 entities
├── mechanics.json           # 13 entities
└── validation_summary.json # Combined validation
```
