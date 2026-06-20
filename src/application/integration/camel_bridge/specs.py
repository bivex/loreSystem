"""Prompt and batch specs for CAMEL.Bridge generation."""

from __future__ import annotations

DEFAULT_RUMOR_AGENT_PROMPTS = (
    (
        "Whisper Broker",
        "Invent one street-level rumor as compact JSON. Keep it flavorful, uncertain, and socially contagious.",
    ),
    (
        "Town Crier",
        "Invent one public-square rumor as compact JSON. Keep it vivid, dramatic, and suitable for codex seeding.",
    ),
    (
        "Dockside Informant",
        "Invent one dockside rumor as compact JSON. Focus on smuggling, cargo, and waterfront secrets.",
    ),
    (
        "Rooftop Scavenger",
        "Invent one rumor from the cyberpunk heights as compact JSON. Focus on surveillance, hacking, and rooftop life.",
    ),
    (
        "Night Market Vendor",
        "Invent one night market rumor as compact JSON. Focus on street trade, underground tech, and local gossip.",
    ),
    (
        "Cyber-Clinic Healer",
        "Invent one rumor from the underground clinics as compact JSON. Focus on black-market implants, body mods, and medical secrets.",
    ),
)

DEFAULT_EVENT_AGENT_PROMPT = (
    "Chronicle Weaver",
    "Convert the rumors into one consequential event as compact JSON with name, description, participant_names, and outcome.",
)

DEFAULT_RELATIONSHIP_AGENT_PROMPT = (
    "Bond Archivist",
    "Infer one character relationship from the rumors and event as compact JSON with character_from_name, character_to_name, description, relationship_type, relationship_level, is_mutual.",
)

NARRATIVE_STRUCTURE_KEYS = (
    "campaign, story, storylines, character_evolutions, character_variants, character_profile_entries, motion_captures, voice_actors, subtitles, "
    "affinities, dispositions, quests, quest_chains, quest_givers, quest_nodes, quest_objectives, quest_prerequisites, "
    "quest_reward_tiers, quest_trackers, plot_branches, branch_points, choices, consequences, moral_choices, "
    "alternate_realities, flashbacks, prologue, acts, chapters, episodes, flash_forwards, epilogue, endings"
)

SYSTEMS_SLICE_KEYS = (
    "items, inventories, materials, components, sockets, crafting_recipes, blueprints, enchantments, runes, glyphs, titles, "
    "ranks, leaderboards, trophies, badges, masteries, skills, perks, traits, attributes, talent_trees, achievements, level_ups, "
    "experiences, progression_states, progression_events, player_metrics, drop_rates, loot_table_weights, difficulty_curves, "
    "dungeons, raids, world_events, arenas, instances, open_world_zones, seasonal_events, invasions, wars, legendary_weapons, "
    "mythical_armors, divine_items, cursed_items, artifact_sets, relic_collections"
)

DEFAULT_NARRATIVE_AGENT_PROMPT = (
    "Saga Architect",
    f"Convert the rumor/event/relationship chain into one compact JSON object with keys {NARRATIVE_STRUCTURE_KEYS}. Write quest-facing copy as readable in-world journal/game UI text, not dry meta summaries.",
)

DEFAULT_NARRATIVE_SYSTEMS_AGENT_PROMPT = (
    "Saga Architect",
    f"Convert the rumor/event/relationship chain into one compact JSON object with keys {NARRATIVE_STRUCTURE_KEYS}, {SYSTEMS_SLICE_KEYS}. Write quest-facing copy as readable in-world journal/game UI text, not dry meta summaries.",
)

NARRATIVE_BATCH_SPECS = (
    (
        "story_spine",
        (
            "campaign",
            "story",
            "acts",
            "chapters",
            "episodes",
            "prologue",
            "epilogue",
            "storylines",
        ),
        "Focus on the campaign spine, dramatic escalation, and readable story structure grounded in the anchored rumor/event canon. CRITICAL: ALL text must be in output language. Examples for Russian: 'Act I - Setup' → 'Акт I - Завязка', 'Chapter 1' → 'Глава 1', 'Prologue' → 'Пролог'. NEVER use English for narrative structure.",
    ),
    (
        "character_meta",
        (
            "character_evolutions",
            "character_variants",
            "character_profile_entries",
            "motion_captures",
            "voice_actors",
            "subtitles",
            "affinities",
            "dispositions",
        ),
        "Focus on character progression, voice production, subtitles (spoken dialogue lines), and relationship metadata. CRITICAL: ALL text must be in output language. Examples for Russian: 'Mara Voss' → 'Мара Восс', 'Dockmaster' → 'Гаваньмастер', 'Harbor Watch' → 'Гаваньская стража'. NEVER use English for character content. Keep outputs compact and canon-consistent.",
    ),
    (
        "quest_meta",
        (
            "quests",
            "quest_chains",
            "quest_givers",
            "quest_nodes",
            "quest_objectives",
            "quest_prerequisites",
            "quest_reward_tiers",
            "quest_trackers",
        ),
        "Focus on quest structure, objectives, givers, and rewards. CRITICAL: ALL text must be in output language. Examples for Russian: 'Silence Before the Bell' → 'Тишина перед колоколом', 'Speak to the dockworkers' → 'Поговори с докерами', 'Light the signal pyre' → 'Зажги сигнальный костер'. NEVER use English for quest content. Keep outputs compact and canon-consistent.",
    ),
    (
        "narrative_branching",
        (
            "plot_branches",
            "branch_points",
            "choices",
            "consequences",
            "moral_choices",
            "alternate_realities",
            "flashbacks",
            "flash_forwards",
            "endings",
        ),
        "Focus on branching narrative structure, player choices, and consequences. CRITICAL: ALL text must be in output language. Examples for Russian: 'The warning reaches' → 'Предупреждение достигает', 'harbor stands ready' → 'гавань готова'. NEVER use English for narrative content. Keep outputs compact and canon-consistent.",
    ),
)

SYSTEMS_BATCH_SPECS = (
    (
        "economy_items",
        (
            "items",
            "inventories",
            "materials",
            "components",
            "sockets",
            "crafting_recipes",
            "blueprints",
            "enchantments",
            "runes",
            "glyphs",
        ),
        "Focus on loot, crafting, and socketable progression. Keep the set compact and internally consistent.",
    ),
    (
        "progression_meta",
        (
            "titles",
            "ranks",
            "leaderboards",
            "trophies",
            "badges",
            "masteries",
            "skills",
            "perks",
            "traits",
            "attributes",
            "talent_trees",
            "achievements",
            "level_ups",
            "experiences",
            "progression_states",
            "progression_events",
            "player_metrics",
            "drop_rates",
            "loot_table_weights",
            "difficulty_curves",
        ),
        "Focus on character progression, account meta, rewards, and balance telemetry. Prefer minimal but valid structures over exhaustive detail.",
    ),
    (
        "encounters_world",
        (
            "dungeons",
            "raids",
            "world_events",
            "arenas",
            "instances",
            "open_world_zones",
            "seasonal_events",
            "invasions",
            "wars",
        ),
        "Focus on playable world content, conflict escalation, and live-ops events grounded in the current harbor unrest.",
    ),
    (
        "legendary_rewards",
        (
            "legendary_weapons",
            "mythical_armors",
            "divine_items",
            "cursed_items",
            "artifact_sets",
            "relic_collections",
        ),
        "Focus on capstone rewards, relic loops, and high-rarity loot tied directly to the main conflict.",
    ),
)

ALL_SYSTEMS_BATCH_FIELDS = tuple(
    field_name
    for _, field_names, _ in SYSTEMS_BATCH_SPECS
    for field_name in field_names
)

ALL_NARRATIVE_BATCH_FIELDS = tuple(
    field_name
    for _, field_names, _ in NARRATIVE_BATCH_SPECS
    for field_name in field_names
)
