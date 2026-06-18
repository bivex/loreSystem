# Интерактивные графы MythWeave Lore Explorer

Бэклог графовых визуализаций, строящихся на таблицах SQLite (`lore_system.db`).
Все графы строятся **только на структурных полях БД** (FK / id-ссылки), без
keyword-матчинга по тексту — это принцип, принятый после рефакторинга графа
развилок сюжета.

---

## ✅ Реализованные графы (13)

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
| 9 | 📖 Структура повествования | `acts`, `chapters`, `episodes`, `prologues`, `flashbacks`, `flash_forwards`, `alternate_realities` | `/api/graph/narrative` |
| 10 | ⭐ Легендарные предметы и комплекты | `legendary_weapons`, `mythical_armors`, `divine_items`, `cursed_items`, `artifact_sets`, `enchantments`, `runes`, `glyphs`, `sockets`, `traits` | `/api/graph/legendary_items` |
| 11 | 🏆 Достижения и прогресс игрока | `achievements`, `badges`, `masterys`, `titles`, `progression_events`, `progression_states`, `experiences`, `leaderboards`, `player_metrics` | `/api/graph/achievements` |
| 12 | ⚔️ Боевая карта и подземелья | `arenas`, `dungeons`, `instances`, `raids`, `invasions`, `difficulty_curves`, `characters` (bosses), `wars` (factions) | `/api/graph/combat` |
| 13 | 💰 Экономика и лут | `inventories`, `loot_table_weights`, `drop_rates`, `quest_reward_tiers`, `relic_collections`, `characters` (owners), `items`, `quest_nodes` | `/api/graph/economy` |

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

*(пусто — все высокоприоритетные графы реализованы)*

### 🥈 Средний приоритет

#### A. 🎭 Продакшн: озвучка и моушн (Production: Voice & Mocap)
- **Цель**: Карта озвучки персонажей и захвата движений — продакшн-трекинг.
- **Таблицы**: `voice_actors` (7), `motion_captures` (7).
- **Ожидаемые связи**: `voice_actor → character_id/scene_id`; `motion_capture → character_id/scene_id`.
- **Польза**: Продюсерам видна загрузка актёров и покрытие сцен.

### 🥉 Низкий приоритет (sparse / niche)

#### B. 🌍 Открытый мир и события (Open World & Events)
- **Таблицы**: `open_world_zones` (1), `seasonal_events` (1), `quest_givers` (3), `quest_objectives` (4), `quest_trackers` (2).
- **Цель**: Карта зон мира → NPC-квестгиверы → цепочки заданий и трекеры прогресса.
- **Ожидаемые связи**: `open_world_zone → location_id`; `quest_giver → npc_id/quest_id`; `quest_objective → quest_id`; `quest_tracker → quest_id/character_id`.
- **Польза**: Видна география выдачи заданий и покрытие зон контентом.

#### C. 💬 Социальные и моральные выборы (Social & Moral Choices)
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
