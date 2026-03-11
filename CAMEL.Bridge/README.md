# CAMEL.Bridge

Предпочтительный текущий AI-bridge для **канонической lore generation / structured write-back** в этом репозитории.

Сейчас `CAMEL.Bridge` — это рекомендуемый путь для новых workflow, где нужно:

- генерировать lore напрямую в SQLite,
- быстро итерировать bridge-owned сущности,
- делать smoke/live тесты вокруг persisted entity payloads,
- развивать canonical generation path без зависимости от `MiroFish/` simulation stack.

`MiroFish/` всё ещё нужен для simulation runtime, report UI и graph exploration, но **не является основным рекомендуемым entrypoint** для новой lore generation работы.

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

## Genre priorities for next bridge slices

### Priority 1 — Idle RPG / Raid systems

Это следующий предпочтительный слой для `CAMEL.Bridge`, потому что он лучше всего ложится на уже существующий domain model и даст максимальную production-пользу.

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
- `CAMEL_MODEL_PLATFORM` (например, `OPENAI`)
- `CAMEL_MODEL_TYPE` (например, `GPT_4O_MINI` или raw model string вроде `openai/gpt-oss-20b`)
- `CAMEL_MODEL_BASE_URL` (например, `https://api.groq.com/openai/v1` для OpenAI-compatible провайдера)
- `CAMEL_MODEL_TEMPERATURE` (например, `0.7`)
- `CAMEL_MODEL_MAX_TOKENS`
- `CAMEL_BRIDGE_STRICT_MODEL=true` — полностью выключает fallback

### Пример `.env`

```bash
OPENAI_API_KEY=sk-...
CAMEL_MODEL_PLATFORM=OPENAI
CAMEL_MODEL_TYPE=openai/gpt-oss-20b
CAMEL_MODEL_BASE_URL=https://api.groq.com/openai/v1
CAMEL_BRIDGE_STRICT_MODEL=true
```

## Что внутри

- `run_rumor_pipeline.py` — CLI-раннер для полной цепочки
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
  --strict-model
```

Если `--strict-model` или `CAMEL_BRIDGE_STRICT_MODEL=true` включены, bridge **не использует fallback** и упадёт, если:

- нет API key,
- CAMEL/model call сломался,
- модель вернула невалидный JSON.

Без strict-mode мост всё ещё умеет создавать fallback-записи.