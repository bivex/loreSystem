# CAMEL.Bridge Roadmap

Roadmap для **предпочтительного current-generation path** в `loreSystem`.

## Guiding principle

`CAMEL.Bridge` развивается как основной путь для:

- canonical lore generation,
- structured entity write-back,
- SQLite-backed smoke/live verification,
- bridge-owned expansion новых entity slices.

`MiroFish/` остаётся отдельным simulation/report stack и не является основным roadmap target для новой canonical entity generation работы.

## Current completed slices

### Narrative core

- `Rumor`
- `Event`
- `CharacterRelationship`

### Campaign & Story

- `Campaign`, `Story`, `Act`, `Chapter`, `Episode`
- `Prologue`, `Epilogue`
- `Storyline`, `PlotBranch`, `BranchPoint`
- `Choice`, `Consequence`, `MoralChoice`
- `AlternateReality`, `Flashback`, `FlashForward`, `Ending`

### Characters

- `CharacterEvolution`
- `CharacterVariant`
- `CharacterProfileEntry`
- `MotionCapture`
- `VoiceActor`
- `Affinity`
- `Disposition`

### Quests

- `Quest`
- `QuestChain`
- `QuestGiver`
- `QuestNode`
- `QuestObjective`
- `QuestPrerequisite`
- `QuestRewardTier`
- `QuestTracker`
- quest UX text fields:
  - `player_briefing`
  - `journal_summary`
  - `acceptance_text`
  - `completion_text`
  - `failure_text`
  - `reward_summary`
  - `objective_hint`

### Systems already implemented in bridge

- `Item`, `Component`, `Socket`
- `Mastery`, `Skill`, `Perk`, `Trait`, `Attribute`
- `TalentTree`, `Achievement`, `LevelUp`, `Experience`
- `ProgressionState`, `ProgressionEvent`

## Priority roadmap by genre

## P0 — Idle RPG / Raid-first systems

Это главный следующий приоритет, потому что он:

- даёт максимальную production-value,
- хорошо ложится на уже существующий domain model,
- расширяет bridge от narrative-first к systems-first gameplay generation.

### Target entity packs

#### Skills & Progression

- ✅ `Skill`
- ✅ `Perk`
- ✅ `Trait`
- ✅ `Attribute`
- ✅ `Experience`
- ✅ `LevelUp`
- ✅ `TalentTree`
- ✅ `Mastery`
- ✅ `ProgressionState`
- ✅ `ProgressionEvent`

#### Inventory & Crafting

- `Inventory`
- `CraftingRecipe`
- `Material`
- ✅ `Component`
- `Blueprint`
- `Enchantment`
- ✅ `Socket`
- `Rune`
- `Glyph`
- ✅ `Item`

#### Raid / encounter / reward loop

- `Dungeon`
- `Raid`
- `Arena`
- `Instance`
- `OpenWorldZone`
- `LegendaryWeapon`
- `MythicalArmor`
- `DivineItem`
- `CursedItem`
- `ArtifactSet`
- `RelicCollection`
- `WorldEvent`
- `SeasonalEvent`
- `Invasion`
- `War`

#### Live-ops / balance / reward tuning

- ✅ `Achievement`
- `Trophy`
- `Badge`
- `Title`
- `Rank`
- `Leaderboard`
- `PlayerMetric`
- `DropRate`
- `LootTableWeight`
- `DifficultyCurve`

### Why this is first

- best fit for **Idle RPG**
- best fit for **Raid / boss progression loops**
- highest reuse of current domain entities
- minimal need for domain redesign before bridge work starts

## P1 — Gacha pack

### Short version

Gacha важен, но не должен быть первым bridge slice, потому что для него недостаточно только parser/persistence wiring.

### What can be covered with current model

- rarity-flavored item/reward outputs
- drop tables and balance hints
- event / seasonal rotation framing
- progression / duplicate-reward approximations через existing systems

### What likely needs domain expansion

- `Banner`
- `BannerRotation`
- `GachaPool`
- `Pull`
- `PullResult`
- `PityCounter`
- `RateUp`
- `DuplicateReward`
- `SummonCurrency`
- `Shard`
- `AscensionTrack`

### Priority note

`CAMEL.Bridge` should support **gacha-inspired outputs** early, but a real gacha-first production slice should wait until these domain gaps are addressed explicitly.

## P2 — Hyper-casual pack

### Short version

Hyper-casual пригодится как analytics/live-ops extension, но не является первым bridge priority, потому что текущая модель мира больше заточена под lore-heavy и progression-heavy игры.

### Immediate useful entities

- `PlayerMetric`
- `SessionData`
- `Heatmap`
- `ConversionRate`
- `DifficultyCurve`
- `Checkpoint`
- `SavePoint`
- `SpawnPoint`
- `VisualEffect`
- `Particle`
- `Shader`
- `ColorPalette`
- `SoundEffect`

### Likely future domain additions

- `Booster`
- `FTUEStep`
- `LevelSegment`
- `RetryLoop`
- `ObstaclePattern`
- `CosmeticUnlock`
- `AdPlacement`
- `Skin`

## Implementation order

1. **Finish Inventory & Crafting remainder** (`Inventory`, `CraftingRecipe`, `Material`, `Blueprint`, `Enchantment`, `Rune`, `Glyph`)
2. **Finish reward / profile remainder** (`Title`, `Rank`, `Leaderboard`, `Trophy`, `Badge`)
3. **Add analytics / balance slice** (`PlayerMetric`, `DropRate`, `LootTableWeight`, `DifficultyCurve`)
4. **Raid / Dungeon / Legendary Items slice**
5. **Gacha domain-gap review**
6. **Hyper-casual domain-gap review**

## Working rule

If a new gameplay generation feature is requested, default to:

1. checking whether it fits cleanly into `CAMEL.Bridge`,
2. preferring bridge expansion over `MiroFish/` integration work,
3. only falling back to `MiroFish/` when the task is truly simulation/report-specific.