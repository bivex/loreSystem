# Интерактивные графы MythWeave Lore Explorer

Бэклог графовых визуализаций, строящихся на таблицах SQLite (`lore_system.db`).
Все графы строятся **только на структурных полях БД** (FK / id-ссылки), без
keyword-матчинга по тексту — это принцип, принятый после рефакторинга графа
развилок сюжета.

---

## ✅ Реализованные графы (16)

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
| 14 | 🌍 Открытый мир и события | `open_world_zones`, `seasonal_events`, `quest_givers`, `quest_objectives`, `quest_trackers`, `locations`, `quest_chains`, `quest_nodes`, `characters` | `/api/graph/open_world` |
| 15 | 🎭 Продакшн: озвучка и моушн | `voice_actors`, `motion_captures` | `/api/graph/production` |
| 16 | 💬 Социальные и моральные выборы | `moral_choices`, `rumors`, `characters`, `campaigns`, `locations` | `/api/graph/social` |

> ⚠️ Графы 6, 8, 15 работают на **производных** связях, т.к. в БД отсутствуют
> соответствующие прямые FK (нет `factions`/`prerequisite_id`/`character_id`
> в voice_actors). Дипломатия выводится из `wars` + `character_relationships`;
> прокачка — через общий `character_id` и level-based требования; продакшн —
> только через общий `world_id`. При появлении недостающих таблиц/полей графы
> нужно будет переключить на прямые FK.

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
5. **Ширина подписей.** Глобально включены `widthConstraint.maximum: 220` и
   `font.multi: 'html'` — длинные лейблы переносятся, не налезая на соседей.
   Для плотных кросс-доменных графов (open_world, social) максимум поднят
   до 280–320.
6. **Широкий layout.** Все 16 графов используют удвоенные расстояния
   (`springLength` 400–800, `nodeSpacing`/`treeSpacing`/`levelSeparation`
   280–640) для читаемости подписей.
