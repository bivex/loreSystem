# CAMEL.Bridge

Предпочтительный текущий AI-bridge для **канонической lore generation / structured write-back** в этом репозитории.

Сейчас `CAMEL.Bridge` — это рекомендуемый путь для новых workflow, где нужно:

- генерировать lore напрямую в SQLite,
- держать continuity context через SQLite + optional Qdrant memory,
- быстро итерировать bridge-owned сущности,
- делать smoke/live тесты вокруг persisted entity payloads,
- развивать canonical generation path без зависимости от `MiroFish/` simulation stack.

`MiroFish/` всё ещё нужен для simulation runtime, report UI и graph exploration, но **не является основным рекомендуемым entrypoint** для новой lore generation работы.

## Continuity architecture

Ниже — актуальная C4-схема для `CAMEL.Bridge`: как runtime path, canonical SQLite storage, optional Qdrant memory и canon-control связаны между собой.

![CAMEL.Bridge continuity architecture](../camel_c4_continuity_architecture_v2.png)

## Что bridge покрывает уже сейчас

Текущий bridge уже умеет генерировать и сохранять:

- `Rumor`
- `Event`
- `CharacterRelationship`
- Campaign / Story slice:
  - `Campaign`, `Story`, `Act`, `Chapter`, `Episode`, `Prologue`, `Epilogue`
  - `Storyline`, `PlotBranch`, `BranchPoint`, `Choice`, `Consequence`, `MoralChoice`
  - `AlternateReality`, `Flashback`, `FlashForward`, `Ending`
- Character slice:
  - `CharacterEvolution`, `CharacterVariant`, `CharacterProfileEntry`
  - `MotionCapture`, `VoiceActor`, `Affinity`, `Disposition`
- Quest slice:
  - `Quest`, `QuestChain`, `QuestGiver`, `QuestNode`, `QuestObjective`
  - `QuestPrerequisite`, `QuestRewardTier`, `QuestTracker`
  - user-facing quest UX fields like `player_briefing`, `journal_summary`, `acceptance_text`, `completion_text`, `failure_text`, `reward_summary`, `objective_hint`
- Systems slice (`--with-systems`):
  - `Item`, `Inventory`, `Material`, `Component`, `Socket`
  - `CraftingRecipe`, `Blueprint`, `Enchantment`, `Rune`, `Glyph`
  - `Title`, `Rank`, `Leaderboard`, `Trophy`, `Badge`
  - `Mastery`, `Skill`, `Perk`, `Trait`, `Attribute`
  - `TalentTree`, `Achievement`, `LevelUp`, `Experience`
  - `ProgressionState`, `ProgressionEvent`
  - `PlayerMetric`, `DropRate`, `LootTableWeight`, `DifficultyCurve`
  - `Dungeon`, `Raid`, `WorldEvent`, `Arena`, `Instance`, `OpenWorldZone`
  - `SeasonalEvent`, `Invasion`, `War`
  - `LegendaryWeapon`, `MythicalArmor`, `DivineItem`
  - `CursedItem`, `ArtifactSet`, `RelicCollection`
- Optional continuity memory (`--with-memory`):
  - exact recall from SQLite world state
  - semantic recall from Qdrant
  - prompt injection for rumor / event / relationship / narrative generation
  - post-persist reindex of the current world snapshot
  - widened SQLite/index coverage for closed encounter/world/reward bridge tables
  - real Qdrant live smoke verified against a live local collection lifecycle (`create -> upsert -> search -> scroll -> cleanup`)

## Genre priorities for next bridge slices

### Priority 1 — Idle RPG / Raid systems

Этот priority-pack остаётся главным gameplay-направлением для `CAMEL.Bridge`: systems-core, starter encounter/world, live-ops warfare slice и весь legendary/relic reward loop уже закрыты; следующий production-фокус — memory live stabilization.

Уже закрыто в текущем bridge (P0 core systems tranche + starter encounter/world slice):

- `Item`, `Inventory`, `Material`, `Component`, `Socket`
- `CraftingRecipe`, `Blueprint`, `Enchantment`, `Rune`, `Glyph`
- `Title`, `Rank`, `Leaderboard`, `Trophy`, `Badge`
- `Mastery`, `Skill`, `Perk`, `Trait`, `Attribute`
- `TalentTree`, `Achievement`, `LevelUp`, `Experience`
- `ProgressionState`, `ProgressionEvent`
- `PlayerMetric`, `DropRate`, `LootTableWeight`, `DifficultyCurve`
- `Dungeon`, `Raid`, `WorldEvent`, `Arena`, `Instance`, `OpenWorldZone`
- `SeasonalEvent`, `Invasion`, `War`
- `LegendaryWeapon`, `MythicalArmor`, `DivineItem`
- `CursedItem`, `ArtifactSet`, `RelicCollection`

Следующий рекомендуемый фокус внутри этого priority-pack:

- memory v1 live stabilization (`shaping cleanup`, resource cleanup)

Из этого хвоста уже закрыт первый safe sub-slice:

- widened indexing/recall coverage for `Dungeon`, `Raid`, `WorldEvent`, `Arena`, `Instance`, `OpenWorldZone`
- widened indexing/recall coverage for `SeasonalEvent`, `Invasion`, `War`
- widened indexing/recall coverage for `LegendaryWeapon`, `MythicalArmor`, `DivineItem`, `CursedItem`, `ArtifactSet`, `RelicCollection`

Текущий remaining focus внутри memory v1:

- memory document shaping / recall quality cleanup
- live-path cleanup around resource handling

Фокус на сущности:

- `Skill`, `Perk`, `Trait`, `Attribute`, `Experience`, `LevelUp`, `TalentTree`, `Mastery`
- `Inventory`, `CraftingRecipe`, `Material`, `Component`, `Blueprint`, `Enchantment`, `Rune`, `Glyph`
- `Achievement`, `Trophy`, `Badge`, `Title`, `Rank`, `Leaderboard`
- `Dungeon`, `Raid`, `Arena`, `Instance`, `OpenWorldZone`
- `LegendaryWeapon`, `MythicalArmor`, `DivineItem`, `CursedItem`, `ArtifactSet`, `RelicCollection`
- `WorldEvent`, `SeasonalEvent`, `Invasion`, `War`
- `PlayerMetric`, `DropRate`, `LootTableWeight`, `DifficultyCurve`

### Priority 2 — Gacha

Для gacha bridge полезен, но тут уже частично нужен **domain expansion**, а не только новый parsing/persistence слой.

Кратко:

- можно переиспользовать economy / reward / balance / rarity-related сущности,
- но полноценный gacha-first path потребует выделенных сущностей вроде banner/pity/pool/rate-up/summon-currency.

### Priority 3 — Hyper-casual

Для hyper-casual bridge пригодится в первую очередь как analytics/live-ops layer, но для полного genre-fit тоже, вероятно, понадобятся новые domain entities.

Фокус будет на:

- `PlayerMetric`, `SessionData`, `Heatmap`, `ConversionRate`, `DifficultyCurve`
- `Checkpoint`, `SavePoint`, `SpawnPoint`
- `VisualEffect`, `Particle`, `Shader`, `ColorPalette`, `SoundEffect`
- lightweight reward/progression/live-ops сущностях

Подробный roadmap см. в [`ROADMAP.md`](ROADMAP.md).

## ENV support

Bridge автоматически пытается загрузить `.env` из корня workspace.

Поддерживаемые переменные:

- `OPENAI_API_KEY` / другой provider key
- `OPENROUTER_API_KEY` — для OpenRouter / free моделей
- `CAMEL_MODEL_PLATFORM` (например, `OPENAI`)
- `CAMEL_MODEL_TYPE` (например, `arcee-ai/trinity-mini:free` или raw model string вроде `openai/gpt-oss-20b`)
- `CAMEL_MODEL_BASE_URL` (например, `https://api.groq.com/openai/v1` для OpenAI-compatible провайдера)
- `CAMEL_MODEL_TEMPERATURE` (например, `0.7`)
- `CAMEL_MODEL_MAX_TOKENS`
- `CAMEL_MODEL_REASONING_EFFORT` — optional reasoning level для OpenRouter-compatible reasoning models
- `OPENROUTER_HTTP_REFERER` / `OPENROUTER_X_TITLE` — optional OpenRouter leaderboard headers

Для optional memory v1:

- `CAMEL_MEMORY_QDRANT_URL` — обязателен для `--with-memory`
- `CAMEL_MEMORY_QDRANT_COLLECTION` — optional, по умолчанию `camel_bridge_memory`
- `CAMEL_MEMORY_QDRANT_API_KEY` — optional
- `CAMEL_MEMORY_QDRANT_TIMEOUT_SECONDS` — optional
- `CAMEL_MEMORY_EMBED_BACKEND` — `local` (default), `hash` (legacy) или `openai`
- `CAMEL_MEMORY_EMBED_DIMENSION` — размер embeddings: default `384` для `local`, `96` для legacy `hash`
- `CAMEL_MEMORY_EMBED_MODEL` — для `openai` backend
- `CAMEL_MEMORY_EMBED_BASE_URL` — optional OpenAI-compatible embeddings base URL
- `CAMEL_MEMORY_EMBED_API_KEY` — optional отдельный embeddings key

### Пример `.env`

```bash
OPENAI_API_KEY=sk-...
CAMEL_MODEL_PLATFORM=OPENAI
CAMEL_MODEL_TYPE=openai/gpt-oss-20b
CAMEL_MODEL_BASE_URL=https://api.groq.com/openai/v1

# optional memory v1
CAMEL_MEMORY_QDRANT_URL=http://localhost:6333
CAMEL_MEMORY_EMBED_BACKEND=local
```

По умолчанию memory path dependency-free:

- SQLite используется как canonical truth,
- Qdrant вызывается по stdlib HTTP client,
- embeddings по умолчанию идут через dependency-free local token+ngram embedder без внешнего embed API.

Если нужен semantic recall через внешний embeddings endpoint, переключи:

- `CAMEL_MEMORY_EMBED_BACKEND=openai`
- и задай `CAMEL_MEMORY_EMBED_API_KEY` + при необходимости `CAMEL_MEMORY_EMBED_BASE_URL`.

Если нужен прежний максимально простой fallback, можно явно оставить:

- `CAMEL_MEMORY_EMBED_BACKEND=hash`

### Пример `.env` для free OpenRouter generation

```bash
OPENROUTER_API_KEY=sk-or-...
CAMEL_MODEL_PLATFORM=OPENROUTER
CAMEL_MODEL_TYPE=arcee-ai/trinity-mini:free
CAMEL_MODEL_BASE_URL=https://openrouter.ai/api/v1
CAMEL_MODEL_REASONING_EFFORT=low

# optional leaderboard headers
OPENROUTER_HTTP_REFERER=https://your-app.example
OPENROUTER_X_TITLE=MythWeave CAMEL Bridge
```

В текущем bridge `OPENROUTER` идёт через OpenAI-compatible `/chat/completions` path. Это позволяет запускать `arcee-ai/trinity-mini:free` даже если в активном интерпретаторе не установлен `camel-ai`.

## Что внутри

- `run_rumor_pipeline.py` — CLI-раннер для полной цепочки
- `src/application/integration/camel_bridge/memory.py` — SQLite + Qdrant continuity layer
- `Whisper Broker` и `Town Crier` — агентные персоны для слухов
- `Chronicle Weaver` — превращает слухи в событие
- `Bond Archivist` — выводит отношение между персонажами
- `ROADMAP.md` — приоритеты дальнейшего расширения bridge под жанры и системные entity packs

## Пример запуска

```bash
python CAMEL.Bridge/run_rumor_pipeline.py \
  --tenant-id 1 \
  --world-id 1 \
  --theme "moonlit rebellion" \
  --context "The harbor is tense after three disappearances." \
  --character "Mara Voss" \
  --character "Iven Hale" \
  --with-memory
```

По умолчанию мост работает в отказоустойчивом режиме и умеет создавать fallback-записи в случае сбоев или невалидного ответа модели.

Если включён `--with-memory`, bridge перед generation собирает continuity packet из SQLite и optional Qdrant recall, а после persistence переиндексирует текущий world snapshot.

## Многоглавная генерация: run_full_story.py

`run_full_story.py` — оркестратор для последовательной генерации полного сюжета из N глав.

```bash
python3 CAMEL.Bridge/run_full_story.py \
  --tenant-id 1 --world-id 1 \
  --theme "Тёмное фэнтези: герой просыпается в бочке в пещере орков" \
  --chapters 15 \
  --output-language ru \
  --with-memory \
  --env-file .env \
  --character "Мара Восс" --character "Ивен Хейл"
```

### Как это работает

Каждая глава генерируется отдельным LLM-вызовом. После каждой итерации саммари сохраняется в SQLite и передаётся в контекст следующей главы — так LLM продолжает канон вместо того чтобы перезапускать историю.

Алгоритм на каждую главу:

1. Загружает саммари всех предыдущих глав из SQLite
2. Строит строку контекста с каноном и инструкцией "ПРОДОЛЖАЙ с того места"
3. Запускает `generate_story_chain()` — один полный цикл генерации
4. Принудительно выставляет `sequence_number` в БД (LLM может сбросить нумерацию)

### Количество LLM-вызовов на главу

При `--with-memory` и narrative structure (по умолчанию) на каждую главу идёт 7 последовательных вызовов:

| # | Шаг | Агент |
|---|-----|-------|
| 1 | Слухи (rumors) | Whisper Broker / Town Crier / ... |
| 2 | События (events) | Chronicle Weaver |
| 3 | Отношения (relationships) | Bond Archivist |
| 4 | Narrative batch: story_spine | campaign, story, acts, chapters, episodes, prologue, epilogue |
| 5 | Narrative batch: character_meta | evolutions, variants, profile_entries, voice_actors, subtitles |
| 6 | Narrative batch: quest_meta | quests, quest_chains, quest_nodes, objectives, rewards |
| 7 | Narrative batch: narrative_branching | plot_branches, choices, consequences, endings |

Для 15 глав: **105 вызовов** итого. Все вызовы идут строго последовательно — каждый батч видит результат предыдущего в промпте.

### Живой прогресс в stdout

Оркестратор выводит строку прогресса после каждого LLM-вызова:

```
🤖 LLM call # 15 | ch 3/15 call 2/7 | total  15/105 | elapsed   142s | ETA ~  808s
```

ETA пересчитывается после каждого вызова на основе среднего времени.

### Память и контекст между главами

Два слоя памяти (при `--with-memory`):

- **SQLite exact recall** — персонажи, события, отношения, квесты из прошлых глав. До 6 документов каждого типа.
- **Qdrant semantic recall** — векторный поиск по сущностям. До 4 документов. Бюджет контекста ~1400 символов.

По умолчанию используется `LocalNgramTextEmbedder` (384-мерный хэш). Для лучшего семантического поиска по русскому тексту рекомендуется переключить на OpenAI-compatible эмбеддер:

```bash
CAMEL_MEMORY_EMBED_BACKEND=openai
CAMEL_MEMORY_EMBED_API_KEY=sk-...
# опционально, если эндпоинт отличается от CAMEL_MODEL_BASE_URL:
# CAMEL_MEMORY_EMBED_BASE_URL=https://api.openai.com/v1
```

При смене бэкенда нужно пересоздать коллекцию Qdrant — запуск с `--reset` (дефолт) сделает это автоматически.

### Флаги

| Флаг | По умолчанию | Описание |
|------|-------------|----------|
| `--chapters N` | 15 | Количество глав |
| `--output-language` | ru | Язык генерации (ru, en, uk) |
| `--with-memory` | выкл | Включить SQLite + Qdrant continuity |
| `--reset` / `--no-reset` | reset=on | Очистить БД перед стартом |
| `--character NAME` | — | Seed-персонаж (повторяемый) |
| `--env-file PATH` | — | Путь к .env файлу |
