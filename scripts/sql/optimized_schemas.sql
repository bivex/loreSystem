-- Optimized SQL schemas for all 303 entities
-- Fast regex extraction - ONLY unique fields
-- Total: 233 entities
-- Total fields: 959

CREATE TABLE IF NOT EXISTS worlds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    genre TEXT,
    power_level INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(tenant_id, name)
);;

CREATE TABLE IF NOT EXISTS academys (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, faction_id TEXT, location_id TEXT, dean_name TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, id TEXT, icon TEXT, reward_ids TEXT, prerequisites TEXT, version TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS acts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, chapter_ids TEXT, key_events TEXT, estimated_minutes INTEGER, structure TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alliances (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, dissolution_date TEXT, alliance_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alternate_realitys (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, access_method TEXT, parent_world_id TEXT, divergence_point TEXT, entry_points TEXT, exit_points TEXT, id TEXT, version TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ambients (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, file_path TEXT, duration_seconds REAL, loop_crossfade REAL, attenuation_distance REAL, transition_count INTEGER, transition_trigger_tags TEXT, associated_location_id TEXT, associated_biome_id TEXT, crossfade REAL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS archives (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, location_id TEXT, archivist_name TEXT, era_covered TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS armys (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS atmospheres (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attributes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, current_value REAL, maximum_value REAL, temporary_bonus REAL, derivation_formula TEXT, source_attributes TEXT, display_name TEXT, icon_id TEXT, tags TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS autosaves (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, last_triggered_at TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, id TEXT, icon TEXT, achievement_ids TEXT, version TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS balance_entitiess (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, id TEXT, daily_currency_cap INTEGER, total_currency_cap INTEGER, mmr_skill TEXT, version TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS barters (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS battalions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS black_holes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS blueprints (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, requirements INTEGER, required_level INTEGER, required_skill_id TEXT, required_skill_level INTEGER, variant_of_id TEXT, discovery_source_ids TEXT, icon_id TEXT, texture_id TEXT, skill_levels TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS branch_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, condition_expression TEXT, skill_check_difficulty INTEGER, choice_id TEXT, location_id TEXT, branch_point_type INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS calendars (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, calendar_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS camera_paths (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, look_at_target TEXT, metadata TEXT, name TEXT, easing TEXT, loop TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, chapter_ids TEXT, recommended_level INTEGER, estimated_hours INTEGER, start_date TEXT, end_date TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cataclysms (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, trigger_event_id TEXT, affected_locations TEXT, permanent_changes TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS celebrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ceremonys (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, presider_id TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, episode_ids TEXT, act_ids TEXT, required_level INTEGER, estimated_minutes INTEGER, unlocks_at_level INTEGER, chapter_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, abilities TEXT, parent_id TEXT, location_id TEXT, rarity TEXT, element TEXT, role TEXT, base_hp INTEGER, base_atk INTEGER, base_def INTEGER, base_speed INTEGER, energy_cost INTEGER, status TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS character_evolutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, previous_stage TEXT, requirements TEXT, variant_ids TEXT, new_abilities TEXT, evolution_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS character_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, combat_bonus_when_together REAL, first_met_event_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS character_variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, unlock_condition TEXT, model_path TEXT, texture_paths TEXT, animation_overrides TEXT, stat_modifiers TEXT, ability_changes TEXT, season_event_id TEXT, variant_type TEXT, rarity TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, quest_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chekhovs_guns (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, payoff_description TEXT, related_entity_ids TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cinematics (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, scene_id TEXT, camera_path_id TEXT, transitions TEXT, fades TEXT, metadata TEXT, name TEXT, priority INTEGER, is_looping TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS color_palettes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, secondary_color TEXT, accent_colors TEXT, tags TEXT, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS competitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS components (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, required_skill_id TEXT, required_skill_level INTEGER, model_3d_id TEXT, texture_ids TEXT, material_ids TEXT, skill_level INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS concerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS consequences (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, trigger_choice_id TEXT, trigger_action_id TEXT, target_entity_id TEXT, delay_seconds INTEGER, conditions TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS conversion_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, id TEXT, end_point TEXT, version TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS courts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS crafting_recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, success_rate INTEGER, skill_requirement TEXT, skill_level_requirement INTEGER, required_workstation_id TEXT, skill_level INTEGER, difficulty TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS crimes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, victim_id TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS currencys (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, icon_path TEXT, conversion_rate_to_premium REAL, max_hold_amount INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS custom_maps (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, min_players INTEGER, difficulty TEXT, estimated_duration_minutes INTEGER, world_id TEXT, tile_count INTEGER, entity_count INTEGER, checksum TEXT, workshop_entry_id TEXT, status TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cutscenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, trigger_event TEXT, camera_id TEXT, cinematic_id TEXT, metadata TEXT, name TEXT, priority INTEGER, skippable TEXT, auto_start TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS defenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS demands (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, max_price REAL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS deus_ex_machinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, scene_id TEXT, character_ids TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS difficulty_curves (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, id TEXT, version TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS disasters (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS discoverys (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, discovered_entity_id TEXT, discovered_entity_type TEXT, triggers TEXT, hint_text TEXT, reward_item_ids TEXT, reward_achievement_id TEXT, location_id TEXT, area_id TEXT, required_level INTEGER, required_quest_id TEXT, icon_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS districts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS drop_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, id TEXT, conditions TEXT, affected_items TEXT, version TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS dubbings (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, voice_actor TEXT, studio TEXT, quality_score INTEGER, metadata TEXT, dubbed_audio_id TEXT, is_approved TEXT, lip_synced TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS easter_eggs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, location_id TEXT, reference_source TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS eclipses (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, visibility_region TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS enchantments (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, required_item_level INTEGER, required_item_rarity TEXT, mutually_exclusive_ids TEXT, duration_seconds INTEGER, required_material_ids TEXT, required_skill_id TEXT, required_skill_level INTEGER, glow_color TEXT, particle_effect_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS endings (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, conditions TEXT, epilogue_id TEXT, achievement_id TEXT, image_url TEXT, ending_type TEXT, rarity TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS enigmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, location_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS environments (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, temperature TEXT, sounds TEXT, smells TEXT, time_of_day TEXT, weather TEXT, lighting TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS epilogues (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, scene_ids TEXT, character_ids TEXT, required_ending_id TEXT, required_achievement_id TEXT, estimated_minutes INTEGER, trigger_condition TEXT, epilogue_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, scene_ids TEXT, estimated_minutes INTEGER, required_previous_episodes TEXT, episode_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS eras (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, start_date TEXT, end_date TEXT, parent_era_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, end_date TEXT, location_id TEXT, outcome TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS event_chains (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, required_character_ids TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evidences (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evolutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS exhibitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, curator_id TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, largest_gain INTEGER, last_gain_at TEXT, tags TEXT, source TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS extinctions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, affected_regions TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS factions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, leader_character_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS faction_memberships (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, rank TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fades (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, metadata TEXT, name TEXT, fade_type TEXT, duration_ms INTEGER, color TEXT, from_opacity REAL, to_opacity REAL, easing TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS famines (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fast_travel_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, requires_quest_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS festivals (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS flashbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, trigger_event TEXT, flashback_time TEXT, duration_ms INTEGER, characters TEXT, metadata TEXT, name TEXT, is_skippable TEXT, filter_effect TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fleets (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, region_id TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS flowcharts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, story_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS food_chains (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, producers TEXT, consumers TEXT, decomposers TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS foreshadowings (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, hinted_event_id TEXT, character_ids TEXT, location_id TEXT, requires_knowledge TEXT, subtlety TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fortifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS galaxys (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS glyphs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, modifiers TEXT, abilities TEXT, required_socket_type TEXT, synergizes_with_schools TEXT, icon_id TEXT, texture_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS governments (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, nation_id TEXT, region_id TEXT, city_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS handouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, content TEXT, image_ids TEXT, session_id TEXT, reveal_timing TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS heatmaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, id TEXT, version TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hibernations (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hidden_paths (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, alt_text TEXT, description TEXT, dimensions TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS improvements (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, reason TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS inflations (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, region_id TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS inspirations (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, tags TEXT, source TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS internets (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, platform_url TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS invasions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, successful TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS inventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, production_cost_resources TEXT, max_uses INTEGER, inventor_id TEXT, faction_id TEXT, effect_description TEXT, ability_ids TEXT, required_level INTEGER, required_skill_id TEXT, required_skill_level INTEGER, icon_id TEXT, model_id TEXT, skill_levels TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, rarity TEXT, location_id TEXT, level INTEGER, enhancement INTEGER, max_enhancement INTEGER, base_atk INTEGER, base_hp INTEGER, base_def INTEGER, special_stat TEXT, special_stat_value REAL, model_3d_id TEXT, texture_ids TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS judges (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS jurys (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS kingdoms (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, kingdom_tier TEXT, succession_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS laws (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, legal_system_id TEXT, nation_id TEXT, region_id TEXT, repeal_date TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lawyers (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS leaderboards (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, id TEXT, limit INTEGER, version TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS legal_systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, legal_system_type TEXT, trial_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS level_ups (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, reward_ids TEXT, stat_increases TEXT, abilities_unlocked TEXT, choices_made TEXT, selected_rewards TEXT, health_increase INTEGER, mana_increase INTEGER, attack_increase INTEGER, defense_increase INTEGER, occurred_at TEXT, location_id TEXT, quest_id TEXT, notes TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS librarys (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, location_id TEXT, librarian_name TEXT, specialization TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lightings (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, inner_angle REAL, outer_angle REAL, range REAL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS localizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, region_code TEXT, quality_score REAL, review_status TEXT, status TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, parent_location_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS loot_table_weights (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, id TEXT, conditions TEXT, version TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lore_axiomss (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, classes TEXT, stats TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS maps (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, image_ids TEXT, location_ids TEXT, scale TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS market_squares (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, operating_hours TEXT, trade_goods TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS masterys (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, rank_thresholds TEXT, bonuses TEXT, unlocked_bonuses TEXT, active_passive_id TEXT, active_ability_ids TEXT, icon_id TEXT, associated_skill_id TEXT, tags TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, icon_id TEXT, texture_id TEXT, model_3d_id TEXT, durability INTEGER, conductivity INTEGER, hardness INTEGER, magic_affinity TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, trigger_conditions TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS miracles (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, deity_id TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mods (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, file_size_bytes INTEGER, checksum TEXT, dependencies TEXT, workshop_entry_id TEXT, workshop_url TEXT, status TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS model3ds (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, poly_count INTEGER, dimensions TEXT, textures TEXT, animations TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS moons (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS moral_choices (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, campaign_id TEXT, description TEXT, consequence_ids TEXT, time_limit_seconds INTEGER, character_ids TEXT, choice_alignment TEXT, urgency TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS motifs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, file_path TEXT, duration_seconds REAL, key_signature TEXT, tempo_bpm INTEGER, emotional_tone TEXT, parent_theme_id TEXT, character_id TEXT, item_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS motion_captures (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, description TEXT, character_id TEXT, actor_id TEXT, duration_seconds REAL, frame_count INTEGER, transition_from TEXT, transition_to TEXT, animation_type TEXT, status TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mount_equipments (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, compatible_mount_types TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS museums (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, location_id TEXT, curator_name TEXT, admission_fee REAL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS music_controls (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, lore_state TEXT, narrative_phase TEXT, emotional_tone TEXT, player_context TEXT, trigger_conditions TEXT, music_state_id TEXT, music_track_id TEXT, music_theme_id TEXT, fade_in_duration_seconds REAL, fade_out_duration_seconds REAL, allow_interrupt TEXT, can_interrupt_others TEXT, interrupt_priority_threshold INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS music_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, default_track_id TEXT, can_transition_to TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS music_themes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, file_path TEXT, duration_seconds REAL, composer TEXT, character_id TEXT, location_id TEXT, faction_id TEXT, era_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS music_tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, file_path TEXT, duration_seconds REAL, intensity_level INTEGER, loop_start_time REAL, loop_end_time REAL, music_theme_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mysterys (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, location_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nations (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, capital_location_id TEXT, ruler_character_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nebulas (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, composition TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS newspapers (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, faction_id TEXT, publisher_name TEXT, political_bias TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS noble_districts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, tags TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, template_id TEXT, parent_id TEXT, tag_ids TEXT, image_ids TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS particles (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS patents (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, invention_id TEXT, blueprint_id TEXT, jurisdiction_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS perks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, rarity TEXT, stat_type TEXT, stat_modifier REAL, resistance_type TEXT, resistance_value INTEGER, ability_id TEXT, ability_modifier TEXT, stacking_limit INTEGER, icon_id TEXT, source_id TEXT, tags TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS phenomenons (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, repeat_interval_days INTEGER, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS plagues (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS player_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, id TEXT, unit TEXT, session_id TEXT, aggregation_period TEXT, version TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS player_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS plazas (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, features TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS plot_branchs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, consequence_ids TEXT, rejoin_point_id TEXT, difficulty_modifier REAL, branch_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS plot_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, scene_id TEXT, related_entity_ids TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS port_districts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, cargo_facilities TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS progression_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, reasons TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS progression_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, level TEXT, character_class TEXT, experience INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS prologues (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, scene_ids TEXT, character_ids TEXT, estimated_minutes INTEGER, prologue_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS propagandas (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, faction_id TEXT, originator_name TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS prototypes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, base_item_id TEXT, creator_id TEXT, laboratory_id TEXT, build_cost_resources TEXT, parent_prototype_id TEXT, icon_id TEXT, model_id TEXT, notes TEXT, reason TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pulls (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, ten_pull_batch_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS punishments (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, sentence_length_days INTEGER, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, amount_local REAL, purchase_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS puzzles (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, location_id TEXT, completion_time_seconds INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quarters (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, landmarks TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quest_chains (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, required_level INTEGER, cooldown_hours INTEGER, position INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quest_givers (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, character_id TEXT, daily_reset_hour INTEGER, required_reputation INTEGER, greeting_message TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quest_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, prerequisite_ids TEXT, reward_tier_ids TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quest_objectives (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, target_type TEXT, target_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quest_prerequisites (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, required_quest_ids TEXT, required_level INTEGER, required_item_ids TEXT, required_skill_ids TEXT, required_attribute_values TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quest_reward_tiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, min_rating INTEGER, max_rating INTEGER, item_ids TEXT, currency_rewards TEXT, reputation_rewards TEXT, skill_experience TEXT, rating INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS radios (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, faction_id TEXT, frequency TEXT, station_manager TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ranks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, id TEXT, icon TEXT, perks TEXT, version TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reproductions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, breeding_season TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, entity_type TEXT, entity_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS researchs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, prerequisites TEXT, required_level INTEGER, unlocks TEXT, grants_stat_bonus TEXT, cost_resources TEXT, location_id TEXT, researcher_ids TEXT, parent_research_id TEXT, icon_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS research_centers (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, faction_id TEXT, location_id TEXT, director_name TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS revolutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, new_government_id TEXT, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, source_id TEXT, min_player_level INTEGER, max_claims INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS riddles (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, location_id TEXT, hint_text TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rumors (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, location_id TEXT, source_name TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS runes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, bonuses TEXT, effects TEXT, required_socket_type TEXT, combine_result_rank TEXT, icon_id TEXT, texture_id TEXT, glow_color TEXT, particle_effect_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS save_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, requires_quest_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, location_id TEXT, headmaster_name TEXT, student_capacity INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, primary_file_path TEXT, total_duration_seconds REAL, composer TEXT, orchestrator TEXT, act_count INTEGER, movement_count INTEGER, instrument_count INTEGER, emotional_tone TEXT, intensity_peak INTEGER, chapter_id TEXT, quest_id TEXT, scene_id TEXT, stem_count INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS seasonal_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, recurrence_period_days INTEGER, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS secret_areas (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, parent_location_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS session_datas (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, id TEXT, version TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS shaders (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, tags TEXT, description TEXT, errors TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS share_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, content_version TEXT, max_uses INTEGER, expires_at TEXT, status TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS shops (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, items TEXT, player_faction_id TEXT, player_reputation INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS siege_engines (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS silences (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, fade_in_duration REAL, fade_out_duration REAL, minimum_duration REAL, duck_amount REAL, associated_scene_id TEXT, associated_music_id TEXT, associated_event_id TEXT, duration REAL, fade_in_style TEXT, fade_out_style TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, character_id TEXT, rarity TEXT, cooldown_seconds INTEGER, mana_cost INTEGER, prerequisite_skill_ids TEXT, icon_id TEXT, tags TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS slumss (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_medias (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, founder_name TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sockets (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, required_material_ids TEXT, required_level INTEGER, glow_color TEXT, rarity TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS solstices (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sound_effects (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, file_path TEXT, duration_seconds REAL, pitch REAL, variation_count INTEGER, tags TEXT, associated_ability_id TEXT, associated_item_id TEXT, associated_event_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS soundtracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, composer TEXT, file_path TEXT, duration_seconds REAL, bpm INTEGER, key_signature TEXT, fade_in_duration REAL, fade_out_duration REAL, associated_location_id TEXT, associated_event_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS spawn_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, requires_quest_id TEXT, entity_ids TEXT, conditions TEXT, flags TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS star_systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, galaxy_id TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS storys (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, choice_ids TEXT, connected_world_ids TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS subtitles (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, voice_over_id TEXT, character_id TEXT, metadata TEXT, text TEXT, start_time_ms INTEGER, end_time_ms INTEGER, language TEXT, position TEXT, style TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS supplys (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, color TEXT, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS talent_trees (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, character_id TEXT, nodes TEXT, unlocked_node_ids TEXT, icon_id TEXT, tags TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tariffs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS taxs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, region_id TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS televisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, faction_id TEXT, channel_number INTEGER, network_name TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, parent_template_id TEXT, rune_ids TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS textures (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, dimensions TEXT, color_space TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS themes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, emotional_tone TEXT, musical_theme_id TEXT, primary_instrument TEXT, key_signature TEXT, character_id TEXT, faction_id TEXT, location_id TEXT, color_palette TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS time_periods (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, start_date TEXT, end_date TEXT, parent_period_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS timelines (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, scope_entity_id TEXT, start_date TEXT, end_date TEXT, position INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tokenboards (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, sticky_notes TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tournaments (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS traits (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, positive_effects TEXT, negative_effects TEXT, stat_modifiers TEXT, conflicts_with TEXT, synergizes_with TEXT, icon_id TEXT, tags TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, from_scene_id TEXT, to_scene_id TEXT, color TEXT, metadata TEXT, name TEXT, transition_type TEXT, duration_ms INTEGER, easing TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, context TEXT, notes TEXT, confidence_score REAL, max_length INTEGER, status TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS traps (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, location_id TEXT, damage INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS treatys (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, treaty_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trophys (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, id TEXT, icon TEXT, achievement_ids TEXT, version TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS universitys (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, location_id TEXT, motto TEXT, founded_year INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, genre TEXT, starting_location_id TEXT, required_level INTEGER, recommended_level INTEGER, dialogue_line_count INTEGER, choice_count INTEGER, ending_count INTEGER, workshop_entry_id TEXT, status TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS visual_effects (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, tags TEXT, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS voice_actors (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id TEXT, description TEXT, character_ids TEXT, voice_samples TEXT, agency TEXT, contact_info TEXT, hourly_rate REAL, status TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS voice_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, character_id TEXT, voice_actor_id TEXT, file_path TEXT, duration_seconds REAL, pitch REAL, speed REAL, associated_dialogue_id TEXT, associated_scene_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS voice_overs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, audio_asset_id TEXT, duration_ms INTEGER, voice_actor TEXT, metadata TEXT, text TEXT, emotion TEXT, language TEXT, volume REAL, priority INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS wars (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, victor TEXT, created_at TEXT, updated_at TEXT, victor_faction_id TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS wards (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS waypoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, quest_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS weapon_systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS weather_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, affected_regions TEXT, conditions TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS witnesss (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS workshop_entrys (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, description TEXT, content_asset_id TEXT, thumbnail_id TEXT, tags TEXT, metadata TEXT, title TEXT, version TEXT, is_featured TEXT, is_approved TEXT, is_public TEXT, maturity_rating TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS worlds (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, parent_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS world_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, start_date TEXT, duration_days INTEGER, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS wormholes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, created_at TEXT, updated_at TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

