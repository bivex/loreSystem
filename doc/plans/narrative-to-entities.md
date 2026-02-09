# PLAN-0001: Narrative Chapter to Entities Generation

Loom-based agent orchestration for converting narrative chapters into loreSystem entities using 15 specialized agent professions.

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
      name: Character Architect (6 entities)
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
        - "src/domain/entities/instance*.py"
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
      name: Political Scientist (8 entities)
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
      name: Economist (10 entities)
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
      name: Faction Analyst (6 entities)
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
      name: Religious Scholar (10 entities)
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

    - id: technical-director
      name: Technical Director (193 entities)
      description: Create all remaining entities: Achievement, Item, Inventory, CraftingRecipe, Map, Image, Tag, Template, Inspiration, Choice, Flowchart, Handout, Tokenboard, Note, and all technical systems (audio, video, UI, transport, biology, astronomy, architecture)
      working_dir: "."
      stage_type: standard
      dependencies: ["parse-chapter"]
      execution_mode: team
      files:
        - "agents/skills/technical-director.md"
        - "src/domain/entities/*.py"
      truths:
        - "jq '.item | length > 0' entities/technical.json"
        - "jq '.achievement | length > 0' entities/technical.json"
      artifacts:
        - "entities/technical.json"

    - id: validate-entities
      name: Validate All Entities
      description: Validate all generated entities against loreSystem domain model and schema
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
        - "technical-director"
      acceptance:
        - "python scripts/validate_entities.py entities/ --strict"
      truths:
        - "python scripts/validate_schema.py entities/ --all-files"
        - "jq '[.narrative, .character, .quest, .progression, .world, .environment, .historical, .political, .economy, .faction, .military, .religious, .lore, .content, .technical] | map(. != null) | all' validation_summary.json"
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
| Technical Director | All remaining 193 entities (achievement, item, inventory, crafting_recipe, map, image, tag, template, inspiration, choice, flowchart, handout, tokenboard, note, audio, video, UI, transport, biology, astronomy, architecture, etc.) | 193 |
| **TOTAL** | **All 295 entities** | **295** |

## Usage

```bash
cd /root/clawd
loom init doc/plans/narrative-to-entities.md
loom run --max-parallel 15  # All 15 agents working in parallel
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
├── technical.json          # 193 entities
└── validation_summary.json # Combined validation
```
