# Cold Start

## Overview

In `loreSystem/CAMEL.Bridge`, a cold start is the first full pipeline run against a new or empty SQLite database.

During a successful cold start, the pipeline:

- generates the core lore layer: `rumors`, `events`, and `character_relationships`
- expands the narrative layer: `campaign`, `story`, `acts`, `chapters`, `episodes`, `quests`, and related entities
- expands the systems layer: `items`, `materials`, `skills`, `dungeons`, `seasonal_events`, `wars`, `artifact_sets`, `relic_collections`, and other gameplay-facing entities
- reindexes the resulting world snapshot into Qdrant for continuity memory

A cold start is considered successful when:

- generation completes successfully
- narrative generation and persistence complete
- systems generation and persistence complete
- the SQLite database contains newly created narrative and systems entities
- memory reindex completes without error
- Qdrant receives indexed points for the new world snapshot

## Current Reference Setup

The current end-to-end reference run was validated with:

- model: `arcee-ai/trinity-mini:free`
- flags: `--with-campaign-story --with-systems --with-memory`
- memory backend: SQLite + Qdrant

## What Was Fixed

The current cold-start path depends on several fixes made while stabilizing the pipeline:

1. `INFO` logging was enabled in [run_rumor_pipeline.py](/Volumes/External/Code/loreSystem/CAMEL.Bridge/run_rumor_pipeline.py) so the runner prints real execution stages.
2. Stage-level logs and explicit memory reindex error logging were added in [rumor_agents.py](/Volumes/External/Code/loreSystem/src/application/integration/camel_bridge/rumor_agents.py).
3. [memory.py](/Volumes/External/Code/loreSystem/src/application/integration/camel_bridge/memory.py) was fixed so `SQLiteLoreMemoryReader` can read generic `payload_json` tables such as `quests`, even when those tables do not expose flat `name` and `description` columns.
4. A regression test was added in [test_camel_bridge_memory.py](/Volumes/External/Code/loreSystem/tests/test_camel_bridge_memory.py) to keep that memory-indexing path stable.

## Validation

The memory-layer regression suite now passes with:

```bash
python3 -m pytest --no-cov /Volumes/External/Code/loreSystem/tests/test_camel_bridge_memory.py -q
```

Expected result:

```text
21 passed
```

## First Successful Cold Start

The first successful debug cold start produced the following persisted counts in a fresh SQLite database:

- `rumors=2`
- `events=1`
- `campaigns=1`
- `stories=1`
- `acts=3`
- `chapters=4`
- `episodes=4`
- `quests=1`
- `items=4`
- `seasonal_events=1`
- `wars=1`
- `artifact_sets=1`
- `relic_collections=1`

The matching Qdrant collection contained:

- `points_count=25`

This confirms that the pipeline completed generation, persistence, and memory indexing in one pass.

## Expected First-Run Output

On a successful cold start, the runner prints:

1. backend configuration
2. narrative generation and persistence stages
3. systems generation and persistence stages
4. memory indexing result
5. a list of persisted entities

A typical run starts with logs like:

```text
Using CAMEL backend platform=OPENROUTER model=arcee-ai/trinity-mini:free memory=on
... CAMEL bridge narrative generation start ...
... CAMEL bridge narrative persistence completed ...
... CAMEL bridge systems persistence completed ...
... CAMEL bridge memory indexed documents=25 tenant_id=1 world_id=1
... CAMEL bridge memory reindex completed
```

After that, the script prints the created entities. Example output:

```text
[1] The Midnight Tide: Unverified / Moderate
[2] Moonlit Rebellion: Unverified / Moderate
event[1] Moonlit Sacrifice
relationship[1] complicated 1->2
campaign[1] Midnight Tide: Harbor's Shadow
story[1] The Harbor's Shadow
quest[1] Moonlit Sacrifice
item[1] Moonlit Dagger
seasonal_event[1] Moonlit Rebellion season=autumn active=True
war[1] Harbor Uprising War type=territorial active=True
artifact_set[1] Midnight Tide Set pieces=3
relic_collection[1] Moonlit Relics relics=5 power=0
```

The exact names will vary by model output, but the shape of the result should remain the same:

- core lore first
- narrative entities next
- systems entities after that
- memory indexing at the end

## Practical Meaning

Once cold start succeeds, the project no longer operates from an empty world state.

At that point:

- SQLite contains a canonical first-pass world snapshot
- Qdrant contains searchable continuity memory for that world
- later runs can build on established canon instead of starting from zero

## Second-Run Continuity Check

Cold start alone is not enough. The more important validation is whether a second run against the same SQLite database and the same Qdrant collection:

- reuses the existing canonical campaign/story spine
- reuses the existing canonical quest and quest-chain slots
- reuses singleton high-tier systems slots such as `artifact_sets` and `relic_collections`
- adds continuity context instead of starting from zero

The clean reference check was run against:

- SQLite: `/Volumes/External/Code/loreSystem/tmp/camel_live_debug8.db`
- Qdrant collection: `camel_bridge_memory_debug8`
- model: `arcee-ai/trinity-mini:free`
- flags: `--with-campaign-story --with-systems --with-memory`

### Run 1

Persisted counts after the first run:

- `campaigns=1`
- `stories=1`
- `acts=3`
- `chapters=4`
- `episodes=2`
- `quests=1`
- `quest_chains=1`
- `items=3`
- `seasonal_events=1`
- `wars=1`
- `artifact_sets=1`
- `relic_collections=1`
- `storylines=1`
- `world_events=1`

Canonical names after run 1:

- `campaign`: `Moonlit Rebellion`
- `story`: `Moonlit Rebellion`
- `quest`: `Moonlit Rebellion`
- `quest_chain`: `Moonlit Confrontation`
- `artifact_set`: `Dockside Sabotage Set`
- `relic_collection`: `Moonlit Mutiny Relics`

Qdrant after run 1:

- `points_count=25`

### Run 2

The same command was executed a second time against the same database and the same memory collection.

Persisted counts after the second run:

- `campaigns=1`
- `stories=1`
- `acts=3`
- `chapters=4`
- `episodes=4`
- `quests=1`
- `quest_chains=1`
- `items=3`
- `seasonal_events=1`
- `wars=1`
- `artifact_sets=1`
- `relic_collections=1`
- `storylines=3`
- `world_events=2`

Canonical names after run 2:

- `campaign`: `Moonlit Rebellion`
- `story`: `Moonlit Rebellion`
- `quest`: `Moonlit Rebellion`
- `quest_chain`: `Moonlit Confrontation`
- `artifact_set`: `Rebellion Set`
- `relic_collection`: `Rebel Relics`

Qdrant after run 2:

- `points_count=41`

### Interpretation

The second run confirms that continuity memory is active:

- prompt size increased on the second run because continuity context was injected
- Qdrant points increased from `25` to `41`
- core canonical entities did **not** duplicate:
  - `campaign`
  - `story`
  - `quest`
  - `quest_chain`
  - `artifact_set`
  - `relic_collection`

The current behavior is therefore:

- **good**: the pipeline now preserves a single canonical world spine across repeated runs
- **good**: the second run can still add new continuity-facing content such as new `world_events`
- **not fully solved**: some auxiliary slices still create noise or partial duplication, especially `storylines` and other side-content entities that are not yet fully canonicalized

This means the bridge now supports **soft canonical continuation with a stable core spine**, but not yet a perfectly noise-free continuation pass.

## Recommended Command

```bash
python3 /Volumes/External/Code/loreSystem/CAMEL.Bridge/run_rumor_pipeline.py \
  --db-path /Volumes/External/Code/loreSystem/tmp/camel_live_debug2.db \
  --tenant-id 1 \
  --world-id 1 \
  --theme "moonlit rebellion" \
  --context "The harbor is tense after three disappearances." \
  --character "Mara Voss" \
  --character "Iven Hale" \
  --with-campaign-story \
  --with-systems \
  --with-memory
```
