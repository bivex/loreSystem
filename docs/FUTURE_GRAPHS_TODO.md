# Интерактивные графы MythWeave Lore Explorer

Бэклог графовых визуализаций, строящихся на таблицах SQLite (`lore_system.db`).
Все графы строятся **только на структурных полях БД** (FK / id-ссылки), без
keyword-матчинга по тексту — это принцип, принятый после рефакторинга графа
развилок сюжета.

---

## ✅ Реализованные графы (8)

| # | Граф | Таблицы | Эндпоинт |
|---|------|---------|----------|
| 1 | 🕸️ Отношения героев | `characters`, `character_relationships` | `/api/graph/characters` |
| 2 | ⚔️ Дерево квестов | `quests`, `quest_chains`, `quest_nodes`, `quest_prerequisites` | `/api/graph/quests` |
| 3 | 🗺️ Карта локаций мира | `locations` | `/api/graph/locations` |
| 4 | 🔀 Развилки сюжета и концовок | `stories`, `storylines`, `choices`, `consequences`, `plot_branches`, `endings`, `branch_points`, `epilogues` | `/api/graph/story_branches` |
| 5 | ⏳ Хронология исторических эпох | `events`, `world_events`, `eras`, `era_transitions` | `/api/graph/timeline` |
| 6 | 🤝 Дипломатия фракций и альянсы | `wars`, `character_relationships`, `characters`, `ranks` | `/api/graph/factions` |
| 7 | ⚒️ Схемы крафта и ресурсов | `items`, `materials`, `components`, `crafting_recipes`, `blueprints` | `/api/graph/crafting` |
| 8 | 🌲 Дерево прокачки и талантов | `skills`, `talent_trees`, `perks`, `attributes`, `level_ups` | `/api/graph/progression` |

> ⚠️ Графы 6 и 8 работают на **производных** связях, т.к. в БД отсутствуют
> таблицы `factions`/`faction_memberships` и `prerequisite_id`/`talent_node_id`
> FK. Дипломатия выводится из `wars` + `character_relationships`; прокачка —
> через общий `character_id` и level-based требования. При появлении
> недостающих таблиц/полей графы нужно будет переключить на прямые FK.

---

## 📋 Планируемые графы (кандидаты)

Сгруппированы по реальным неиспользуемым таблицам БД. Порядок — по
приоритету (релевантность + наполненность данных).

### 🥇 Высокий приоритет

#### A. 📖 Структура повествования (Narrative Structure)
- **Цель**: Показать иерархию сюжета — акт → глава → эпизод, прологи/флэшбэки/альтернативные реальности.
- **Таблицы**: `acts` (3), `chapters` (4), `episodes` (4), `prologues` (2), `flashbacks` (2), `flash_forwards` (2), `alternate_realities` (3).
- **Ожидаемые связи** (по payload FK): `act.id → chapter.act_id → episode.chapter_id`; `prologue/flashback/flash_forward → campaign_id/story_id`; `alternate_reality → parent_reality_id`.
- **Польза**: Сценаристам видна полная карта нелинейного повествования и где вставлены ретроспективы.

#### B. ⭐ Легендарные предметы и комплекты (Legendary Items & Sets)
- **Цель**: Карта редких/мифических предметов, их зачарования, руны и комплекты.
- **Таблицы**: `legendary_weapons` (1), `mythical_armors` (1), `divine_items` (1), `cursed_items` (1), `artifact_sets` (1), `enchantments` (2), `runes` (2), `glyphs` (2), `sockets` (2), `traits` (1).
- **Ожидаемые связи**: `item → enchantment_id/rune_id/glyph_id`; `artifact_set → item_ids[]`; `sockets → item_id`.
- **Польза**: Баланс редкости и зависимости сет-бонусов.

#### C. 🏆 Достижения и прогресс игрока (Achievements & Player Progress)
- **Цель**: Визуализировать метапрогресс — ачивки, бейджи, мастерство, титулы.
- **Таблицы**: `achievements` (1), `badges` (1), `masterys` (1), `titles` (1), `progression_events` (1), `progression_states` (1), `experiences` (1), `leaderboards` (1), `player_metrics` (1).
- **Ожидаемые связи**: `achievement → prerequisite_achievement_id`; `progression_event → character_id`; `mastery → skill_id`.
- **Польза**: Геймдизайнерам — дерево условий разблокировки и гринда.

### 🥈 Средний приоритет

#### D. ⚔️ Боевая карта и подземелья (Combat & Encounters)
- **Цель**: Карта боевого контента — арены, данжи, рейды, инвазии, инстансы.
- **Таблицы**: `arenas` (1), `dungeons` (2), `instances` (1), `raids` (1), `invasions` (1), `difficulty_curves` (1).
- **Ожидаемые связи**: `dungeon/arena/raid → world_id/location_id`; `instance → parent_id`; `difficulty_curve → encounter_id`.
- **Польза**: План контента для эндгейма и баланс сложности.

#### E. 💰 Экономика и лут (Economy & Loot)
- **Цель**: Поток добычи — лут-таблицы, дроп-рейты, награды квестов, инвентари.
- **Таблицы**: `inventories` (2), `loot_table_weights` (1), `drop_rates` (1), `quest_reward_tiers` (2), `relic_collections` (1).
- **Ожидаемые связи**: `loot_table → item_id`; `drop_rate → source_id/target_item_id`; `quest_reward_tier → quest_id`.
- **Польза**: Поиск «бутылочных горлышек» в экономике, проверка дроп-чансов.

#### F. 🎭 Продакшн: озвучка и моушн (Production: Voice & Mocap)
- **Цель**: Карта озвучки персонажей и захвата движений — продакшн-трекинг.
- **Таблицы**: `voice_actors` (7), `motion_captures` (7).
- **Ожидаемые связи**: `voice_actor → character_id/scene_id`; `motion_capture → character_id/scene_id`.
- **Польза**: Продюсерам видна загрузка актёров и покрытие сцен.

### 🥉 Низкий приоритет (sparse / niche)

#### G. 🌍 Открытый мир и события (Open World & Events)
- **Таблицы**: `open_world_zones` (1), `seasonal_events` (1), `quest_givers` (3), `quest_objectives` (4), `quest_trackers` (2).
- **Цель**: Карта зон мира → NPC-квестгиверы → цепочки заданий и трекеры прогресса.
- **Ожидаемые связи**: `open_world_zone → location_id`; `quest_giver → npc_id/quest_id`; `quest_objective → quest_id`; `quest_tracker → quest_id/character_id`.
- **Польза**: Видна география выдачи заданий и покрытие зон контентом.

#### H. 💬 Социальные и моральные выборы (Social & Moral Choices)
- **Таблицы**: `moral_choices` (2), `rumors` (2).
- **Цель**: Дополнить граф сюжета моральными дилеммами и сетью слухов/репутации.
- **Ожидаемые связи**: `moral_choice → choice_id/consequence_ids`; `rumor → character_id/faction_id/event_id`.
- **Польза**: Сценаристам — карта моральных развилок и информационных потоков в мире.

---

## 🧭 Принципы реализации

1. **Только структурные связи.** Никакого keyword/stem-matching по описаниям —
   только FK, id-массивы и явные поля-ссылки. Связи из текста (`conditions`,
   `notes`) допустимы лишь как резерв при отсутствии FK, с пометкой в коде.
2. **Dedup рёбер.** Использовать `_new_edge_set()` — одинаковая пара
   `(from, to, label)` не дублируется (важно для `branch_points`-подобных
   мостов).
3. **Защита от пустых данных.** Граф с 0 узлов должен отдавать
   `{nodes:[], edges:[]}`, а не падать с 500 — `try/except` с печатью ошибки.
4. **Легенда и physics.** Каждый новый граф требует: пункт в dropdown,
   цветокодированную легенду (`legends[...]`) и профиль physics
   (`forceAtlas2Based` для кластеров, `hierarchical LR/UD` для потоков/деревьев).
5. **Ширина подписей.** Глобально включены `widthConstraint.maximum: 160` и
   `font.multi: 'html'` — длинные лейблы переносятся, не налезая на соседей.
