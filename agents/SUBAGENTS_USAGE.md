# loreSystem Subagents for OpenClaw — Quick Start (со скилами)

## Структура скилов

Каждый субагент загружает **три базовых скила** + **один специализированный**:

| Скил | Назначение |
|------|-----------|
| `lore-extraction` | Общие правила извлечения сущностей из loreSystem |
| `json-formatter` | Форматирование вывода строго в JSON |
| `entity-validator` | Валидация типов, полей и связей между сущностями |
| `<domain>-*` | Специфика конкретной предметной области |

Скилы хранятся в папке `skills/` и регистрируются в `SUBAGENTS_CONFIG.json` в секции `skills.registry`.

---

## Запуск субагента

### Вариант 1 — по ключу конфига (рекомендуется)

```bash
openclaw agent spawn --config SUBAGENTS_CONFIG.json --key "character-architect"
```

> Скилы, задача и выходной файл берутся автоматически из конфига.

### Вариант 2 — вручную с явным указанием скилов

```bash
openclaw agent spawn \
  --task "Extract character entities (character, character_evolution, ...)" \
  --label "Character Architect" \
  --skills skills/lore-extraction.md,skills/json-formatter.md,skills/entity-validator.md,skills/character-design.md
```

### Вариант 3 — с переопределением модели/таймаута

```bash
openclaw agent spawn \
  --config SUBAGENTS_CONFIG.json \
  --key "technical-director" \
  --model anthropic/claude-sonnet-4 \
  --thinking high \
  --runTimeoutSeconds 900
```

### Вариант 4 — пакетный запуск группы субагентов параллельно

```bash
openclaw agent spawn --config SUBAGENTS_CONFIG.json --key "narrative-specialist"   &
openclaw agent spawn --config SUBAGENTS_CONFIG.json --key "character-architect"    &
openclaw agent spawn --config SUBAGENTS_CONFIG.json --key "quest-designer"         &
openclaw agent spawn --config SUBAGENTS_CONFIG.json --key "world-geographer"       &
wait
echo "Batch done"
```

### Вариант 5 — запуск всех 30 субагентов одной командой

```bash
for key in \
  narrative-specialist character-architect quest-designer progression-engineer \
  world-geographer environmental-scientist historian political-scientist \
  economist faction-analyst military-strategist religious-scholar \
  lore-chronicler content-creator achievement-specialist audio-director \
  visual-effects-artist cinematic-director media-analyst transportation-engineer \
  celestial-scientist biology-specialist urban-architect research-education-specialist \
  puzzle-secrets-designer ui-content-specialist analytics-balance-specialist \
  legendary-items-specialist social-cultural-specialist technical-director; do
    openclaw agent spawn --config SUBAGENTS_CONFIG.json --key "$key" &
done
wait
echo "All 30 subagents done"
```

---

## Управление субагентами

```bash
openclaw subagent list                        # список активных
openclaw subagent stop <run-id>               # остановить
openclaw subagent log <run-id>                # просмотр лога
openclaw subagent log <run-id> 50             # последние 50 строк
openclaw subagent info <run-id>               # статус и метаданные
openclaw subagent message send <run-id> -m "Уточни поле X"  # отправить сообщение
```

---

## Полный список субагентов

| # | Ключ | Лейбл | Скилы | Сущностей | Файл |
|---|------|-------|-------|-----------|------|
| 1 | `narrative-specialist` | Narrative Specialist | lore-extraction, json-formatter, entity-validator, **narrative-writing** | 8 | `entities/narrative.json` |
| 2 | `character-architect` | Character Architect | lore-extraction, json-formatter, entity-validator, **character-design** | 7 | `entities/character.json` |
| 3 | `quest-designer` | Quest Designer | lore-extraction, json-formatter, entity-validator, **quest-design** | 9 | `entities/quest.json` |
| 4 | `progression-engineer` | Progression Engineer | lore-extraction, json-formatter, entity-validator, **progression-design** | 10 | `entities/progression.json` |
| 5 | `world-geographer` | World Geographer | lore-extraction, json-formatter, entity-validator, **world-building** | 11 | `entities/world.json` |
| 6 | `environmental-scientist` | Environmental Scientist | lore-extraction, json-formatter, entity-validator, **environmental-design** | 6 | `entities/environment.json` |
| 7 | `historian` | Historian | lore-extraction, json-formatter, entity-validator, **historical-research** | 10 | `entities/historical.json` |
| 8 | `political-scientist` | Political Scientist | lore-extraction, json-formatter, entity-validator, **political-analysis** | 13 | `entities/political.json` |
| 9 | `economist` | Economist | lore-extraction, json-formatter, entity-validator, **economic-modeling** | 13 | `entities/economy.json` |
| 10 | `faction-analyst` | Faction Analyst | lore-extraction, json-formatter, entity-validator, **faction-design** | 7 | `entities/faction.json` |
| 11 | `military-strategist` | Military Strategist | lore-extraction, json-formatter, entity-validator, **military-strategy** | 10 | `entities/military.json` |
| 12 | `religious-scholar` | Religious Scholar | lore-extraction, json-formatter, entity-validator, **religious-lore** | 11 | `entities/religious.json` |
| 13 | `lore-chronicler` | Lore Chronicler | lore-extraction, json-formatter, entity-validator, **lore-writing** | 8 | `entities/lore.json` |
| 14 | `content-creator` | Content Creator | lore-extraction, json-formatter, entity-validator, **content-management** | 10 | `entities/content.json` |
| 15 | `achievement-specialist` | Achievement Specialist | lore-extraction, json-formatter, entity-validator, **achievement-design** | 6 | `entities/achievement.json` |
| 16 | `audio-director` | Audio Director | lore-extraction, json-formatter, entity-validator, **audio-direction** | 9 | `entities/audio.json` |
| 17 | `visual-effects-artist` | Visual Effects Artist | lore-extraction, json-formatter, entity-validator, **vfx-design** | 5 | `entities/visual.json` |
| 18 | `cinematic-director` | Cinematic Director | lore-extraction, json-formatter, entity-validator, **cinematic-direction** | 6 | `entities/cinematic.json` |
| 19 | `media-analyst` | Media Analyst | lore-extraction, json-formatter, entity-validator, **media-analysis** | 7 | `entities/media.json` |
| 20 | `transportation-engineer` | Transportation Engineer | lore-extraction, json-formatter, entity-validator, **transport-design** | 9 | `entities/transportation.json` |
| 21 | `celestial-scientist` | Celestial Scientist | lore-extraction, json-formatter, entity-validator, **celestial-science** | 9 | `entities/celestial.json` |
| 22 | `biology-specialist` | Biology Specialist | lore-extraction, json-formatter, entity-validator, **biology-design** | 6 | `entities/biology.json` |
| 23 | `urban-architect` | Urban Architect | lore-extraction, json-formatter, entity-validator, **urban-design** | 8 | `entities/urban.json` |
| 24 | `research-education-specialist` | Research & Education Specialist | lore-extraction, json-formatter, entity-validator, **research-design** | 7 | `entities/research.json` |
| 25 | `puzzle-secrets-designer` | Puzzle & Secrets Designer | lore-extraction, json-formatter, entity-validator, **puzzle-design** | 7 | `entities/puzzle.json` |
| 26 | `ui-content-specialist` | UI/Content Specialist | lore-extraction, json-formatter, entity-validator, **ui-design** | 8 | `entities/ui_content.json` |
| 27 | `analytics-balance-specialist` | Analytics & Balance Specialist | lore-extraction, json-formatter, entity-validator, **analytics-balance** | 8 | `entities/analytics.json` |
| 28 | `legendary-items-specialist` | Legendary Items Specialist | lore-extraction, json-formatter, entity-validator, **legendary-items** | 10 | `entities/legendary.json` |
| 29 | `social-cultural-specialist` | Social & Cultural Specialist | lore-extraction, json-formatter, entity-validator, **social-culture** | 11 | `entities/social_cultural.json` |
| 30 | `technical-director` | Technical Director (catch-all) | lore-extraction, json-formatter, entity-validator, **technical-systems** | 193 | `entities/technical.json` |
| **TOTAL** | | | | **295** | |

---

## Разбивка сущностей

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
Все оставшиеся сущности: achievements, inventory, content, creative tools, interactive systems, audio systems, visual systems, cinematic systems, narrative devices, events, progression, legal, research, media, secrets, art, transport, legendary, biology, celestial, architecture, player systems, balance, game mechanics

---

## Справка по параметрам

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `--config` | Путь к конфиг-файлу | — |
| `--key` | Ключ субагента из конфига | — |
| `--model` | Модель (`anthropic/claude-sonnet-4`, `anthropic/claude-opus-4`, `zai/glm-4.7`) | из конфига |
| `--thinking` | Уровень мышления (`low`, `medium`, `high`) | из конфига |
| `--runTimeoutSeconds` | Таймаут в секундах | 300 |
| `--skills` | Список путей к скилам через запятую | из конфига |
| `--task` | Описание задачи | из конфига |
| `--label` | Человекочитаемый лейбл | из конфига |

### Политики инструментов

Разрешены: `read`, `write`, `edit`, `glob`, `grep`  
Запрещены: `sessions_spawn`, `gateway`, `whatsapp_login`

### Порядок приоритетов модели

1. Флаг `--model` в команде (наивысший)
2. Поле `model` в конфиге субагента
3. `agents.defaults.subagents.model` в конфиге
4. Дефолтная модель OpenClaw (наименьший)

---

## Gateway

```bash
openclaw gateway enable    # включить
openclaw gateway disable   # выключить
openclaw gateway status    # статус
```

Docs: docs.openclaw.ai/cli