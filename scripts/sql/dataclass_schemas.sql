-- Dataclass Parsed Schemas for all 303 entities
-- Extracted from @dataclass field annotations
-- Total: 299 entities

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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    faction_id INTEGER,
    location_id INTEGER,
    specialization TEXT,
    founded_at TEXT,
    dean_name TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    achievement_type TEXT,
    difficulty TEXT,
    reward_ids TEXT,
    is_hidden INTEGER,
    is_repeatable INTEGER,
    prerequisites TEXT,
    icon TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS acts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    campaign_id INTEGER,
    title TEXT,
    act_type TEXT,
    status TEXT,
    act_number INTEGER,
    structure TEXT,
    chapter_ids TEXT,
    key_events TEXT,
    estimated_minutes INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS affinitys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    source_id TEXT,
    target_id TEXT,
    value REAL,
    category TEXT,
    flags TEXT
);

CREATE TABLE IF NOT EXISTS airships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    owner_id INTEGER,
    airship_type TEXT,
    altitude INTEGER,
    max_altitude INTEGER,
    speed REAL,
    fuel INTEGER,
    max_fuel INTEGER,
    passenger_capacity INTEGER,
    is_docked INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alliances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    alliance_type TEXT,
    member_nation_ids TEXT,
    member_faction_ids TEXT,
    founding_member_ids TEXT,
    leader_nation_id INTEGER,
    leader_faction_id INTEGER,
    headquarters_location_id INTEGER,
    founding_date TEXT,
    dissolution_date TEXT,
    is_active INTEGER,
    mutual_defense_pact INTEGER,
    free_trade_agreement INTEGER,
    shared_intelligence INTEGER,
    joint_military_operations INTEGER,
    governing_council_ids TEXT,
    voting_system TEXT,
    shared_resources TEXT,
    pooled_fund_id INTEGER,
    enemy_alliance_ids TEXT,
    enemy_nation_ids TEXT,
    formation_event_id INTEGER,
    key_victories TEXT,
    key_defeats TEXT,
    alliance_flag TEXT,
    alliance_motto TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alternate_realitys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    reality_type TEXT,
    access_method TEXT,
    parent_world_id INTEGER,
    divergence_point TEXT,
    is_canon INTEGER,
    stability REAL,
    entry_points TEXT,
    exit_points TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS ambients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    ambient_type TEXT,
    layer_type TEXT,
    file_path TEXT,
    duration_seconds REAL,
    volume REAL,
    is_loopable INTEGER,
    loop_crossfade REAL,
    spatial_3d INTEGER,
    attenuation_distance REAL,
    has_transitions INTEGER,
    transition_count INTEGER,
    transition_trigger_tags TEXT,
    associated_location_id INTEGER,
    associated_biome_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS archives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id INTEGER,
    archivist_name TEXT,
    document_count INTEGER,
    era_covered TEXT,
    security_level TEXT,
    is_public INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS arenas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    match_type TEXT,
    team_size INTEGER,
    max_teams INTEGER,
    min_level INTEGER,
    has_ranked_mode INTEGER,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS armys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS artifact_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    set_name TEXT,
    set_type TEXT,
    tier TEXT,
    rarity TEXT,
    total_pieces INTEGER,
    collected_pieces TEXT,
    piece_names TEXT,
    piece_descriptions TEXT,
    set_bonus_2 TEXT,
    set_bonus_3 TEXT,
    set_bonus_4 TEXT,
    set_bonus_5 TEXT,
    set_bonus_full TEXT,
    passive_bonuses TEXT,
    active_abilities TEXT,
    unlock_level INTEGER,
    lore TEXT,
    origin_story TEXT,
    creator TEXT,
    creation_era TEXT,
    set_effects TEXT,
    synergies TEXT,
    hidden_effects TEXT,
    unlock_conditions TEXT
);

CREATE TABLE IF NOT EXISTS atmospheres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS attributes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id INTEGER,
    attribute_type TEXT,
    scale_type TEXT,
    base_value REAL,
    current_value REAL,
    maximum_value REAL,
    flat_bonus REAL,
    percentage_bonus REAL,
    temporary_bonus REAL,
    is_derived INTEGER,
    derivation_formula TEXT,
    source_attributes TEXT,
    minimum_value REAL,
    display_name TEXT,
    icon_id TEXT,
    tags TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS autosaves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id TEXT,
    autosave_type TEXT,
    trigger_condition TEXT,
    is_active INTEGER,
    interval_seconds INTEGER,
    last_triggered_at TEXT,
    max_saves INTEGER,
    overwrite_oldest INTEGER,
    save_on_important_event INTEGER,
    save_on_zone_change INTEGER,
    save_on_combat_end INTEGER,
    save_on_pickup INTEGER,
    priority INTEGER,
    icon_path TEXT,
    flags TEXT
);

CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    badge_type TEXT,
    rarity TEXT,
    icon TEXT,
    achievement_ids TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS balance_entitiess (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    gold_generation_rate REAL,
    item_drop_rate REAL,
    vendor_price_modifier REAL,
    crafting_cost_modifier REAL,
    daily_currency_cap INTEGER,
    total_currency_cap INTEGER,
    is_balanced INTEGER,
    version TEXT
);

CREATE TABLE IF NOT EXISTS banners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    banner_type TEXT,
    start_date TEXT,
    end_date TEXT,
    is_active INTEGER,
    featured_character_ids TEXT,
    featured_item_ids TEXT,
    single_pull_cost INTEGER,
    ten_pull_cost INTEGER,
    currency_type TEXT,
    ssr_rate REAL,
    sr_rate REAL,
    r_rate REAL,
    soft_pity_threshold INTEGER,
    hard_pity_threshold INTEGER,
    featured_guarantee_pity INTEGER,
    featured_rate REAL,
    banner_image_path TEXT,
    icon_path TEXT,
    total_pulls INTEGER,
    version TEXT
);

CREATE TABLE IF NOT EXISTS barters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS battalions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bestiary_entrys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    creature_name TEXT,
    types TEXT,
    weakness TEXT,
    resistance TEXT,
    habitat TEXT,
    is_discovered INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS black_holes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS blessings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id TEXT,
    blessing_name TEXT,
    source_id TEXT,
    blessing_type TEXT,
    power INTEGER,
    effects TEXT,
    duration TEXT,
    conditions TEXT,
    loss_conditions TEXT,
    visible INTEGER
);

CREATE TABLE IF NOT EXISTS blueprints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    requirement_type TEXT,
    value TEXT,
    quantity INTEGER
);

CREATE TABLE IF NOT EXISTS branch_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    campaign_id INTEGER,
    branch_point_type TEXT,
    branch_ids TEXT,
    is_mandatory INTEGER,
    is_skippable INTEGER,
    condition_expression TEXT,
    skill_check_difficulty INTEGER,
    choice_id INTEGER,
    location_id INTEGER,
    can_revisit INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS calendars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    calendar_type TEXT,
    seconds_per_minute INTEGER,
    minutes_per_hour INTEGER,
    hours_per_day INTEGER,
    days_per_week INTEGER,
    weeks_per_month INTEGER,
    months_per_year INTEGER,
    day_names TEXT,
    month_names TEXT,
    season_names TEXT,
    holiday_ids TEXT,
    epoch_start INTEGER,
    epoch_name TEXT,
    moon_phase_names TEXT,
    days_per_lunar_cycle INTEGER,
    is_primary_calendar INTEGER,
    is_used_by TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS camera_paths (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    duration_ms INTEGER,
    keyframes TEXT,
    easing TEXT,
    loop INTEGER,
    look_at_target TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    title TEXT,
    campaign_type TEXT,
    status TEXT,
    chapter_ids TEXT,
    recommended_level INTEGER,
    estimated_hours INTEGER,
    start_date TEXT,
    end_date TEXT,
    is_replayable INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cataclysms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS celebrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ceremonys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    campaign_id INTEGER,
    title TEXT,
    chapter_type TEXT,
    status TEXT,
    sequence_number INTEGER,
    episode_ids TEXT,
    act_ids TEXT,
    required_level INTEGER,
    estimated_minutes INTEGER,
    unlocks_at_level INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    backstory TEXT,
    status TEXT,
    abilities TEXT,
    parent_id INTEGER,
    location_id INTEGER,
    rarity TEXT,
    element TEXT,
    role TEXT,
    base_hp INTEGER,
    base_atk INTEGER,
    base_def INTEGER,
    base_speed INTEGER,
    energy_cost INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS character_evolutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id INTEGER,
    evolution_type TEXT,
    current_stage TEXT,
    previous_stage TEXT,
    requirements TEXT,
    rewards TEXT,
    evolved_at TEXT,
    variant_ids TEXT,
    new_abilities TEXT,
    stat_increases TEXT,
    is_permanent INTEGER,
    can_revert INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS character_profile_entrys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id INTEGER,
    field_name TEXT,
    field_value TEXT,
    is_public INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS character_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_from_id INTEGER,
    character_to_id INTEGER,
    relationship_type TEXT,
    relationship_level INTEGER,
    is_mutual INTEGER,
    combat_bonus_when_together REAL,
    special_combo_ability_id INTEGER,
    dialogue_unlocked INTEGER,
    first_met_event_id INTEGER,
    relationship_changed_events TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS character_variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    base_character_id INTEGER,
    variant_type TEXT,
    rarity TEXT,
    is_unlockable INTEGER,
    unlock_condition TEXT,
    model_path TEXT,
    texture_paths TEXT,
    animation_overrides TEXT,
    stat_modifiers TEXT,
    ability_changes TEXT,
    is_seasonal INTEGER,
    season_event_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id TEXT,
    quest_id TEXT,
    checkpoint_type TEXT,
    trigger_type TEXT,
    trigger_position TEXT,
    trigger_radius REAL,
    is_active INTEGER,
    is_triggered INTEGER,
    one_time_only INTEGER,
    restores_on_trigger INTEGER,
    restore_percentage REAL,
    spawn_on_death INTEGER,
    icon_path TEXT,
    flags TEXT
);

CREATE TABLE IF NOT EXISTS chekhovs_guns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    story_id INTEGER,
    introduction_scene_id INTEGER,
    gun_type TEXT,
    state TEXT,
    payoff_description TEXT,
    payoff_scene_id INTEGER,
    is_obvious INTEGER,
    player_expectation TEXT,
    related_entity_ids TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS choices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    story_id INTEGER,
    prompt TEXT,
    choice_type TEXT,
    options TEXT,
    consequences TEXT,
    next_story_ids TEXT,
    is_mandatory INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cinematics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    duration_ms INTEGER,
    scene_id TEXT,
    camera_path_id TEXT,
    transitions TEXT,
    fades TEXT,
    priority INTEGER,
    is_looping INTEGER,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS codex_entrys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    title TEXT,
    category TEXT,
    content TEXT,
    unlock_condition TEXT,
    is_unlocked INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS color_palettes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    palette_type TEXT,
    colors TEXT,
    primary_color TEXT,
    secondary_color TEXT,
    accent_colors TEXT,
    is_locked INTEGER,
    tags TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS competitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    category TEXT,
    rarity TEXT,
    quality INTEGER,
    durability INTEGER,
    max_durability INTEGER,
    weight REAL,
    size TEXT,
    is_craftable INTEGER,
    required_skill_id INTEGER,
    required_skill_level INTEGER,
    model_3d_id INTEGER,
    texture_ids TEXT,
    material_ids TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS concerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS consequences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    consequence_type TEXT,
    severity TEXT,
    is_permanent INTEGER,
    is_visible_to_player INTEGER,
    trigger_choice_id INTEGER,
    trigger_action_id INTEGER,
    target_entity_id INTEGER,
    effect_data TEXT,
    delay_seconds INTEGER,
    conditions TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS constitutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    nation_id INTEGER,
    preamble TEXT,
    articles TEXT,
    amendments TEXT,
    guaranteed_rights TEXT,
    fundamental_principles TEXT,
    branches_of_government TEXT,
    separation_of_powers TEXT,
    checks_and_balances TEXT,
    amendment_process TEXT,
    amendment_threshold TEXT,
    citizenship_criteria TEXT,
    citizen_rights TEXT,
    citizen_duties TEXT,
    adoption_date TEXT,
    ratification_event_id INTEGER,
    authors TEXT,
    inspirations TEXT,
    original_document_id INTEGER,
    is_active INTEGER,
    suspension_reason TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS conversion_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    action_type TEXT,
    start_point INTEGER,
    end_point INTEGER,
    conversion_rate REAL,
    period_days INTEGER,
    segment TEXT,
    funnels TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS courts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS crafting_recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    item_id INTEGER,
    quantity INTEGER,
    is_consumed INTEGER
);

CREATE TABLE IF NOT EXISTS crimes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cults (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deity_id TEXT,
    leader_id TEXT,
    secret_knowledge TEXT,
    rituals TEXT,
    membership_count INTEGER,
    secrecy_level INTEGER,
    alignment TEXT,
    headquarters_location_id TEXT
);

CREATE TABLE IF NOT EXISTS currencys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    code TEXT,
    currency_type TEXT,
    icon_path TEXT,
    is_purchasable INTEGER,
    is_tradable INTEGER,
    conversion_rate_to_premium REAL,
    max_hold_amount INTEGER,
    version TEXT
);

CREATE TABLE IF NOT EXISTS curses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id TEXT,
    curse_name TEXT,
    source_id TEXT,
    severity INTEGER,
    effects TEXT,
    symptoms TEXT,
    duration TEXT,
    removal_conditions TEXT,
    spread_type TEXT,
    cure_methods TEXT
);

CREATE TABLE IF NOT EXISTS cursed_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id TEXT,
    item_name TEXT,
    item_type TEXT,
    tier TEXT,
    rarity TEXT,
    power INTEGER,
    curse_power INTEGER,
    curse_type TEXT,
    benefit TEXT,
    benefit_description TEXT,
    curse_effect TEXT,
    curse_description TEXT,
    effects TEXT,
    curses TEXT,
    unlock_level INTEGER,
    lore TEXT,
    origin TEXT,
    curse_bearer TEXT,
    breaking_conditions TEXT,
    ritual_required TEXT,
    control_level INTEGER,
    risk_level TEXT,
    soulbound INTEGER,
    possession_chance INTEGER,
    corruption_level INTEGER,
    time_to_curse_takeover TEXT,
    warning_signs TEXT
);

CREATE TABLE IF NOT EXISTS custom_maps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    author_id INTEGER,
    map_type TEXT,
    status TEXT,
    max_players INTEGER,
    min_players INTEGER,
    difficulty TEXT,
    estimated_duration_minutes INTEGER,
    play_count INTEGER,
    rating REAL,
    rating_count INTEGER,
    favorite_count INTEGER,
    tile_count INTEGER,
    entity_count INTEGER,
    checksum TEXT,
    workshop_entry_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cutscenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    duration_ms INTEGER,
    trigger_event TEXT,
    priority INTEGER,
    skippable INTEGER,
    auto_start INTEGER,
    camera_id TEXT,
    cinematic_id TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS defenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS demands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS deus_ex_machinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    story_id INTEGER,
    scene_id INTEGER,
    intervention_type TEXT,
    buildup_level INTEGER,
    is_prepared INTEGER,
    is_triggered INTEGER,
    impact_severity TEXT,
    character_ids TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS difficulty_curves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    curve_type TEXT,
    base_level INTEGER,
    max_level INTEGER,
    level_xp_requirement TEXT,
    scaling_factor REAL,
    level_time_minutes TEXT,
    player_count_tiers TEXT,
    is_adaptive INTEGER,
    version TEXT
);

CREATE TABLE IF NOT EXISTS dimensions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    dimension_type TEXT,
    stability INTEGER,
    access_level TEXT,
    is_corrupted INTEGER,
    time_dilation REAL,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS disasters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS discoverys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    trigger_type TEXT,
    condition TEXT,
    required_item_id INTEGER,
    required_location_id INTEGER,
    required_npc_id INTEGER
);

CREATE TABLE IF NOT EXISTS dispositions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    entity_id TEXT,
    target_type TEXT,
    target_value TEXT,
    attitude TEXT,
    intensity INTEGER
);

CREATE TABLE IF NOT EXISTS districts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS divine_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id TEXT,
    item_name TEXT,
    item_type TEXT,
    deity_id TEXT,
    pantheon TEXT,
    tier TEXT,
    rarity TEXT,
    power INTEGER,
    divine_power INTEGER,
    divine_ability TEXT,
    ability_description TEXT,
    domain TEXT,
    blessing_type TEXT,
    effects TEXT,
    miracles TEXT,
    faith_requirement INTEGER,
    alignment TEXT,
    unlock_level INTEGER,
    lore TEXT,
    history TEXT,
    curses TEXT,
    restrictions TEXT,
    soulbound INTEGER,
    worship_bonus INTEGER,
    prayer_power INTEGER,
    blessing_duration TEXT
);

CREATE TABLE IF NOT EXISTS dreams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id INTEGER,
    title TEXT,
    content TEXT,
    dream_type TEXT,
    lucidity_level INTEGER,
    is_recurring INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS drop_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    category TEXT,
    drop_rate REAL,
    conditions TEXT,
    affected_items TEXT,
    player_level_scaling TEXT,
    is_event_boosted INTEGER,
    boost_multiplier REAL,
    version TEXT
);

CREATE TABLE IF NOT EXISTS dubbings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    original_audio_id TEXT,
    dubbed_audio_id TEXT,
    language TEXT,
    voice_actor TEXT,
    studio TEXT,
    quality_score INTEGER,
    is_approved INTEGER,
    lip_synced INTEGER,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS dungeons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    difficulty TEXT,
    max_players INTEGER,
    min_level INTEGER,
    boss_ids TEXT,
    has_lockout INTEGER,
    lockout_duration INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS easter_eggs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id INTEGER,
    egg_type TEXT,
    rarity TEXT,
    discovery_count INTEGER,
    reference_source TEXT,
    is_discovered INTEGER,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS eclipses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS empires (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    nation_id INTEGER,
    emperor_title TEXT,
    emperor_character_id INTEGER,
    imperial_council_ids TEXT,
    province_ids TEXT,
    client_state_ids TEXT,
    colonized_territory_ids TEXT,
    capital_province_id INTEGER,
    expansion_type TEXT,
    expansion_goals TEXT,
    administrative_divisions TEXT,
    imperial_bureaucracy TEXT,
    tax_system TEXT,
    imperial_legion_ids TEXT,
    military_garrison_ids TEXT,
    official_culture_id INTEGER,
    official_religion_id INTEGER,
    cultural_assimilation_policy TEXT,
    imperial_palace_id INTEGER,
    imperial_seals TEXT,
    founding_date TEXT,
    golden_age TEXT,
    is_declining INTEGER,
    decline_reasons TEXT,
    internal_rebellions TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS enchantments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    effect TEXT,
    value REAL,
    is_percentage INTEGER
);

CREATE TABLE IF NOT EXISTS endings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    campaign_id INTEGER,
    title TEXT,
    ending_type TEXT,
    rarity TEXT,
    conditions TEXT,
    is_unlocked INTEGER,
    unlock_count INTEGER,
    character_endings TEXT,
    epilogue_id INTEGER,
    achievement_id INTEGER,
    image_url TEXT,
    ending_number INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS enigmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id INTEGER,
    enigma_type TEXT,
    difficulty TEXT,
    hint_count INTEGER,
    attempt_count INTEGER,
    is_solved INTEGER,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS environments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id INTEGER,
    time_of_day TEXT,
    weather TEXT,
    lighting TEXT,
    temperature TEXT,
    sounds TEXT,
    smells TEXT,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS epilogues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    campaign_id INTEGER,
    title TEXT,
    epilogue_type TEXT,
    trigger_condition TEXT,
    is_skippable INTEGER,
    content TEXT,
    scene_ids TEXT,
    character_ids TEXT,
    required_ending_id INTEGER,
    required_achievement_id INTEGER,
    estimated_minutes INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    chapter_id INTEGER,
    title TEXT,
    episode_type TEXT,
    status TEXT,
    sequence_number INTEGER,
    scene_ids TEXT,
    estimated_minutes INTEGER,
    required_previous_episodes TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS eras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    parent_era_id INTEGER,
    child_era_ids TEXT,
    major_events TEXT,
    cultural_notes TEXT,
    technological_level TEXT,
    is_ongoing INTEGER,
    color_code TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS era_transitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    from_era_id INTEGER,
    to_era_id INTEGER,
    transition_date TEXT,
    transition_type TEXT,
    trigger_events TEXT,
    key_figures TEXT,
    social_impact TEXT,
    economic_impact TEXT,
    political_impact TEXT,
    magical_impact TEXT,
    stories_and_legends TEXT,
    artifacts TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    date_range TEXT,
    outcome TEXT,
    participant_ids TEXT,
    location_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS event_chains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    event_ids TEXT,
    current_event_index INTEGER,
    status TEXT,
    branching_enabled INTEGER,
    branch_point_indices TEXT,
    required_character_ids TEXT,
    required_faction_id INTEGER,
    min_reputation INTEGER,
    success_reward_id INTEGER,
    failure_consequence TEXT,
    affects_world_state INTEGER,
    started_at TEXT,
    completed_at TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evidences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evolutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS exhibitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id INTEGER,
    experience_type TEXT,
    total_experience INTEGER,
    current_level INTEGER,
    current_xp INTEGER,
    xp_to_next_level INTEGER,
    xp_multiplier REAL,
    total_gains INTEGER,
    largest_gain INTEGER,
    source_breakdown TEXT,
    last_gain_at TEXT,
    tags TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS extinctions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS factions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    faction_type TEXT,
    alignment TEXT,
    leader_character_id INTEGER,
    member_character_ids TEXT,
    allied_faction_ids TEXT,
    enemy_faction_ids TEXT,
    headquarters_location_id INTEGER,
    controlled_location_ids TEXT,
    reputation_hostile_threshold INTEGER,
    reputation_neutral_threshold INTEGER,
    reputation_friendly_threshold INTEGER,
    reputation_exalted_threshold INTEGER,
    vendor_discount_at_friendly REAL,
    vendor_discount_at_exalted REAL,
    exclusive_items_unlocked_at INTEGER,
    faction_icon_path TEXT,
    faction_color TEXT,
    is_hidden INTEGER,
    is_joinable INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS faction_hierarchys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    faction_id TEXT,
    structure_type TEXT,
    ranks TEXT,
    leadership_id TEXT,
    succession_rules TEXT,
    promotion_criteria TEXT
);

CREATE TABLE IF NOT EXISTS faction_ideologys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    faction_id TEXT,
    core_beliefs TEXT,
    values TEXT,
    goals TEXT,
    taboos TEXT,
    alignment TEXT,
    strictness INTEGER
);

CREATE TABLE IF NOT EXISTS faction_leaders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    faction_id TEXT,
    character_id TEXT,
    rank TEXT,
    started_leading TEXT,
    approval_rating INTEGER,
    mandates TEXT,
    challenges INTEGER
);

CREATE TABLE IF NOT EXISTS faction_memberships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id INTEGER,
    faction_id INTEGER,
    rank TEXT,
    reputation INTEGER,
    shop_discount REAL,
    can_access_faction_quests INTEGER,
    can_recruit_members INTEGER,
    joined_at TEXT,
    promoted_at TEXT,
    total_contributions INTEGER,
    version TEXT
);

CREATE TABLE IF NOT EXISTS faction_resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    faction_id TEXT,
    resource_type TEXT,
    amount REAL,
    capacity REAL,
    production_rate REAL,
    consumption_rate REAL,
    trade_allowed INTEGER
);

CREATE TABLE IF NOT EXISTS faction_territorys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    faction_id TEXT,
    territory_type TEXT,
    location_id TEXT,
    level_of_control INTEGER,
    borders_with TEXT,
    resources TEXT,
    importance TEXT
);

CREATE TABLE IF NOT EXISTS fades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    fade_type TEXT,
    duration_ms INTEGER,
    color TEXT,
    from_opacity REAL,
    to_opacity REAL,
    easing TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS familiars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    owner_id INTEGER,
    spirit_type TEXT,
    element TEXT,
    power_level INTEGER,
    abilities TEXT,
    bond_level INTEGER,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS famines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fast_travel_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id TEXT,
    is_unlocked INTEGER,
    is_active INTEGER,
    requires_quest_id TEXT,
    requires_level INTEGER,
    cost_gold INTEGER,
    cost_resource TEXT,
    cost_amount INTEGER,
    cooldown_seconds INTEGER,
    icon_path TEXT,
    marker_position TEXT,
    flags TEXT
);

CREATE TABLE IF NOT EXISTS festivals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS flashbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    scene_id TEXT,
    trigger_event TEXT,
    flashback_time TEXT,
    duration_ms INTEGER,
    characters TEXT,
    is_skippable INTEGER,
    filter_effect TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS fleets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS flowcharts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    story_id INTEGER,
    nodes TEXT,
    connections TEXT,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS food_chains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS foreshadowings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    story_id INTEGER,
    scene_id INTEGER,
    foreshadowing_type TEXT,
    subtlety TEXT,
    hinted_event_id INTEGER,
    is_paid_off INTEGER,
    player_discovery_rate REAL,
    character_ids TEXT,
    location_id INTEGER,
    requires_knowledge TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS fortifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS galaxys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS glyphs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    stat_name TEXT,
    value REAL,
    operation TEXT,
    is_percentage INTEGER
);

CREATE TABLE IF NOT EXISTS governments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    nation_id INTEGER,
    region_id INTEGER,
    city_id INTEGER,
    government_type TEXT,
    head_of_state_id INTEGER,
    head_of_government_id INTEGER,
    cabinet_member_ids TEXT,
    branches TEXT,
    legislative_body_id INTEGER,
    legitimacy_source TEXT,
    approval_rating INTEGER,
    corruption_level INTEGER,
    domestic_policy_ids TEXT,
    foreign_policy_ids TEXT,
    economic_policy_ids TEXT,
    ministries TEXT,
    ministry_head_ids TEXT,
    military_control TEXT,
    seat_of_government_id INTEGER,
    allied_governments TEXT,
    rival_governments TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS handouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    title TEXT,
    content TEXT,
    image_ids TEXT,
    session_id INTEGER,
    is_revealed INTEGER,
    reveal_timing TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS heatmaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    heatmap_type TEXT,
    location_type TEXT,
    data_points TEXT,
    collection_period TEXT,
    grid_size INTEGER,
    resolution INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hibernations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hidden_paths (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    start_location_id INTEGER,
    end_location_id INTEGER,
    reveal_method TEXT,
    path_type TEXT,
    is_one_way INTEGER,
    is_revealed INTEGER,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS holidays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    calendar_id INTEGER,
    holiday_type TEXT,
    month INTEGER,
    day INTEGER,
    duration_days INTEGER,
    occurs_every_year INTEGER,
    specific_years TEXT,
    origin_story TEXT,
    associated_deity_ids TEXT,
    associated_event_ids TEXT,
    traditions TEXT,
    rituals TEXT,
    foods TEXT,
    activities TEXT,
    is_observed_nationwide INTEGER,
    observed_by_ids TEXT,
    is_work_free INTEGER,
    restrictions TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS holy_sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id TEXT,
    religion_id TEXT,
    deity_id TEXT,
    site_type TEXT,
    sanctity_level INTEGER,
    visitors_count INTEGER,
    blessings_offered TEXT,
    rituals_performed TEXT,
    guardian_id TEXT
);

CREATE TABLE IF NOT EXISTS honors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id TEXT,
    points INTEGER,
    rank TEXT,
    stain_count INTEGER,
    reputation TEXT
);

CREATE TABLE IF NOT EXISTS hub_areas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_type TEXT,
    capacity INTEGER,
    available_services TEXT,
    is_public INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    path TEXT,
    image_type TEXT,
    alt_text TEXT,
    file_size INTEGER,
    dimensions TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS improvements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    entity_type TEXT,
    entity_id INTEGER,
    suggestion TEXT,
    status TEXT,
    git_commit_hash TEXT
);

CREATE TABLE IF NOT EXISTS inflations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS inspirations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    title TEXT,
    content TEXT,
    category TEXT,
    tags TEXT,
    source TEXT,
    is_used INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    difficulty TEXT,
    max_players INTEGER,
    min_level INTEGER,
    recommended_level INTEGER,
    time_limit INTEGER,
    player_ids TEXT,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS internets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    network_type TEXT,
    platform_url TEXT,
    user_count INTEGER,
    moderation_level TEXT,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS invasions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS inventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    category TEXT,
    status TEXT,
    rarity TEXT,
    inventor_id INTEGER,
    faction_id INTEGER,
    invented_at TEXT,
    complexity INTEGER,
    durability INTEGER,
    efficiency INTEGER,
    production_cost_gold INTEGER,
    production_cost_resources TEXT,
    production_time INTEGER,
    max_uses INTEGER,
    cooldown_time INTEGER,
    base_invention_id INTEGER,
    variant_names TEXT,
    effect_description TEXT,
    ability_ids TEXT,
    is_tradable INTEGER,
    base_value INTEGER,
    required_level INTEGER,
    required_skill_id INTEGER,
    required_skill_level INTEGER,
    icon_id INTEGER,
    model_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS inventorys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    item_id INTEGER,
    quantity INTEGER,
    slot_index INTEGER
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    item_type TEXT,
    rarity TEXT,
    location_id INTEGER,
    level INTEGER,
    enhancement INTEGER,
    max_enhancement INTEGER,
    base_atk INTEGER,
    base_hp INTEGER,
    base_def INTEGER,
    special_stat TEXT,
    special_stat_value REAL,
    model_3d_id INTEGER,
    texture_ids TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS journal_pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id INTEGER,
    page_number INTEGER,
    title TEXT,
    content TEXT,
    is_editable INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS judges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jurys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS karmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    player_id TEXT,
    score INTEGER,
    alignment TEXT,
    tier INTEGER,
    visible INTEGER
);

CREATE TABLE IF NOT EXISTS kingdoms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    nation_id INTEGER,
    monarch_title TEXT,
    monarch_character_id INTEGER,
    heir_character_id INTEGER,
    succession_type TEXT,
    royal_house_name TEXT,
    royal_family_member_ids TEXT,
    kingdom_tier TEXT,
    is_independent INTEGER,
    overlord_kingdom_id INTEGER,
    vassal_kingdom_ids TEXT,
    centralization_level INTEGER,
    crown_lands TEXT,
    noble_house_ids TEXT,
    peerage_system TEXT,
    crown_jewels TEXT,
    throne_room_id INTEGER,
    royal_palace_id INTEGER,
    founding_date TEXT,
    founding_monarch_id INTEGER,
    dynasties TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS laws (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    legal_system_id INTEGER,
    nation_id INTEGER,
    region_id INTEGER,
    law_type TEXT,
    severity TEXT,
    text TEXT,
    summary TEXT,
    applies_to TEXT,
    exceptions TEXT,
    penalties TEXT,
    minimum_penalty TEXT,
    maximum_penalty TEXT,
    enforcement_agency TEXT,
    statute_of_limitations TEXT,
    enacted_date TEXT,
    repealed_date TEXT,
    is_active INTEGER,
    enacting_body TEXT,
    amendment_ids TEXT,
    related_law_ids TEXT,
    precedent_case_ids TEXT,
    constitution_article_id INTEGER,
    treaty_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lawyers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS leaderboards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    board_type TEXT,
    sort_criterion TEXT,
    size_limit INTEGER,
    entries TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS legal_systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    nation_id INTEGER,
    legal_system_type TEXT,
    court_hierarchy TEXT,
    court_ids TEXT,
    supreme_court_id INTEGER,
    judge_title TEXT,
    lawyer_title TEXT,
    prosecutor_title TEXT,
    trial_type TEXT,
    trial_procedure TEXT,
    jury_system TEXT,
    appeals_process TEXT,
    evidence_rules TEXT,
    testimony_rules TEXT,
    philosophy_of_punishment TEXT,
    imprisonment_systems TEXT,
    capital_punishment INTEGER,
    capital_crimes TEXT,
    law_enforcement_agencies TEXT,
    legal_education TEXT,
    primary_sources TEXT,
    secondary_sources TEXT,
    constitution_id INTEGER,
    founding_date TEXT,
    foreign_influences TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS legendary_weapons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id TEXT,
    weapon_name TEXT,
    weapon_type TEXT,
    tier TEXT,
    rarity TEXT,
    attack_power INTEGER,
    special_ability TEXT,
    ability_description TEXT,
    damage_type TEXT,
    durability INTEGER,
    max_durability INTEGER,
    unlock_level INTEGER,
    required_class TEXT,
    lore TEXT,
    enchantments TEXT,
    passive_effects TEXT,
    unique_abilities TEXT,
    soulbound INTEGER,
    upgrade_level INTEGER,
    max_upgrade_level INTEGER,
    previous_owners TEXT
);

CREATE TABLE IF NOT EXISTS level_ups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id INTEGER,
    level_up_type TEXT,
    old_level INTEGER,
    new_level INTEGER,
    reward_ids TEXT,
    stat_increases TEXT,
    skill_points_gained INTEGER,
    abilities_unlocked TEXT,
    choices_made TEXT,
    selected_rewards TEXT,
    health_increase INTEGER,
    mana_increase INTEGER,
    attack_increase INTEGER,
    defense_increase INTEGER,
    occurred_at TEXT,
    location_id INTEGER,
    quest_id INTEGER,
    notes TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS librarys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id INTEGER,
    librarian_name TEXT,
    book_count INTEGER,
    access_level TEXT,
    specialization TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lightings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    light_type TEXT,
    color TEXT,
    intensity REAL,
    position TEXT,
    direction TEXT,
    inner_angle REAL,
    outer_angle REAL,
    range REAL,
    casts_shadows INTEGER,
    shadow_bias REAL,
    shadow_softness REAL,
    is_dynamic INTEGER,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS localizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    language_code TEXT,
    region_code TEXT,
    locale_code TEXT,
    base_content_id INTEGER,
    status TEXT,
    translation_percentage REAL,
    is_default INTEGER,
    is_rtl INTEGER,
    quality_score REAL,
    review_status TEXT,
    release_version TEXT,
    released_at TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_type TEXT,
    parent_location_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS loot_table_weights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    loot_table_id INTEGER,
    item_type TEXT,
    rarity TEXT,
    weight REAL,
    min_level INTEGER,
    is_unique INTEGER,
    conditions TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS lore_axiomss (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    axiom_type TEXT,
    predicate TEXT,
    parameters TEXT
);

CREATE TABLE IF NOT EXISTS lore_fragments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    title TEXT,
    content TEXT,
    rarity TEXT,
    is_discoverable INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS maps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    image_ids TEXT,
    location_ids TEXT,
    scale TEXT,
    is_interactive INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS market_squares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS masterys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    level INTEGER,
    bonus_type TEXT,
    value REAL
);

CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    material_type TEXT,
    rarity TEXT,
    stack_size INTEGER,
    icon_id INTEGER,
    texture_id INTEGER,
    model_3d_id INTEGER,
    base_value INTEGER,
    is_tradeable INTEGER,
    is_sellable INTEGER,
    durability INTEGER,
    conductivity INTEGER,
    hardness INTEGER,
    magic_affinity TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS memorys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id INTEGER,
    memory_type TEXT,
    emotional_intensity INTEGER,
    is_replayable INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS miracles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    author_id INTEGER,
    category TEXT,
    status TEXT,
    version_number TEXT,
    download_count INTEGER,
    rating REAL,
    rating_count INTEGER,
    view_count INTEGER,
    file_size_bytes INTEGER,
    checksum TEXT,
    dependencies TEXT,
    workshop_entry_id INTEGER,
    workshop_url TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS model3ds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    path TEXT,
    model_type TEXT,
    file_size INTEGER,
    poly_count INTEGER,
    dimensions TEXT,
    textures TEXT,
    animations TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS moons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS moral_choices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    campaign_id INTEGER,
    prompt TEXT,
    choice_alignment TEXT,
    urgency TEXT,
    options TEXT,
    consequence_ids TEXT,
    is_reversible INTEGER,
    time_limit_seconds INTEGER,
    affects_reputation INTEGER,
    affects_karma INTEGER,
    character_ids TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS motifs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    motif_type TEXT,
    file_path TEXT,
    duration_seconds REAL,
    key_signature TEXT,
    tempo_bpm INTEGER,
    emotional_tone TEXT,
    primary_association TEXT,
    has_variants INTEGER,
    is_transformable INTEGER,
    can_be_inverted INTEGER,
    parent_theme_id INTEGER,
    character_id INTEGER,
    item_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS motion_captures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    animation_type TEXT,
    status TEXT,
    file_path TEXT,
    character_id INTEGER,
    actor_id INTEGER,
    duration_seconds REAL,
    frame_count INTEGER,
    is_looping INTEGER,
    transition_from TEXT,
    transition_to TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    owner_id INTEGER,
    mount_type TEXT,
    speed REAL,
    stamina INTEGER,
    max_stamina INTEGER,
    abilities TEXT,
    can_fly INTEGER,
    is_summoned INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mount_equipments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    equipment_type TEXT,
    rarity TEXT,
    stats TEXT,
    compatible_mount_types TEXT,
    is_equipped INTEGER,
    mount_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS museums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id INTEGER,
    curator_name TEXT,
    artifact_count INTEGER,
    museum_type TEXT,
    admission_fee REAL,
    is_open INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS music_controls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    lore_state TEXT,
    narrative_phase TEXT,
    emotional_tone TEXT,
    player_context TEXT,
    trigger_conditions TEXT,
    priority INTEGER,
    fade_in_duration_seconds REAL,
    fade_out_duration_seconds REAL,
    allow_interrupt INTEGER,
    can_interrupt_others INTEGER,
    interrupt_priority_threshold INTEGER,
    music_state_id INTEGER,
    music_track_id INTEGER,
    music_theme_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS music_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    is_silence_moment INTEGER,
    default_track_id INTEGER,
    crossfade_duration_seconds REAL,
    allow_interrupts INTEGER,
    priority INTEGER,
    can_transition_to TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS music_themes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    theme_type TEXT,
    file_path TEXT,
    duration_seconds REAL,
    composer TEXT,
    character_id INTEGER,
    location_id INTEGER,
    faction_id INTEGER,
    era_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS music_tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    system_type TEXT,
    file_path TEXT,
    duration_seconds REAL,
    intensity_level INTEGER,
    is_loopable INTEGER,
    loop_start_time REAL,
    loop_end_time REAL,
    music_theme_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mysterys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id INTEGER,
    mystery_type TEXT,
    difficulty TEXT,
    clue_count INTEGER,
    solver_count INTEGER,
    is_solved INTEGER,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mythical_armors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id TEXT,
    armor_name TEXT,
    armor_type TEXT,
    tier TEXT,
    rarity TEXT,
    defense_power INTEGER,
    special_protection TEXT,
    protection_description TEXT,
    damage_resistance TEXT,
    elemental_immune TEXT,
    durability INTEGER,
    max_durability INTEGER,
    unlock_level INTEGER,
    required_class TEXT,
    lore TEXT,
    enchantments TEXT,
    passive_effects TEXT,
    set_bonus TEXT,
    weight INTEGER,
    mobility_penalty INTEGER,
    magical_defense INTEGER,
    physical_defense INTEGER,
    soulbound INTEGER,
    upgrade_level INTEGER,
    max_upgrade_level INTEGER,
    previous_owners TEXT
);

CREATE TABLE IF NOT EXISTS nations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    nation_type TEXT,
    capital_location_id INTEGER,
    territory_ids TEXT,
    borders_ids TEXT,
    government_type TEXT,
    ruler_character_id INTEGER,
    government_ids TEXT,
    legal_system_id INTEGER,
    constitution_id INTEGER,
    military_strength INTEGER,
    active_conflicts TEXT,
    economic_system TEXT,
    currency_id INTEGER,
    main_exports TEXT,
    main_imports TEXT,
    allies_ids TEXT,
    enemies_ids TEXT,
    trade_partners_ids TEXT,
    treaties TEXT,
    population_estimate INTEGER,
    dominant_culture_id INTEGER,
    minority_culture_ids TEXT,
    founding_date TEXT,
    founding_event_id INTEGER,
    historical_events TEXT,
    flag_description TEXT,
    coat_of_arms TEXT,
    motto TEXT,
    national_anthem TEXT,
    is_active INTEGER,
    is_vassal INTEGER,
    overlord_nation_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nebulas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS newspapers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    faction_id INTEGER,
    publisher_name TEXT,
    circulation INTEGER,
    publication_frequency TEXT,
    political_bias TEXT,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nightmares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id INTEGER,
    title TEXT,
    content TEXT,
    fear_level INTEGER,
    trauma_level INTEGER,
    is_lucid INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS noble_districts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    title TEXT,
    content TEXT,
    tags TEXT,
    is_pinned INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS oaths (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id TEXT,
    oath_name TEXT,
    oath_type TEXT,
    terms TEXT,
    restrictions TEXT,
    benefits TEXT,
    witness_id TEXT,
    broken INTEGER,
    break_penalty TEXT
);

CREATE TABLE IF NOT EXISTS open_world_zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    biome TEXT,
    min_level INTEGER,
    max_level INTEGER,
    player_cap INTEGER,
    poi_ids TEXT,
    has_dynamic_events INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id TEXT,
    entity_id TEXT,
    entity_name TEXT,
    pact_type TEXT,
    terms TEXT,
    benefits TEXT,
    costs TEXT,
    duration TEXT,
    condition TEXT,
    active INTEGER,
    breach_consequence TEXT
);

CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    content TEXT,
    template_id INTEGER,
    parent_id INTEGER,
    tag_ids TEXT,
    image_ids TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS particles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    particle_type TEXT,
    max_particles INTEGER,
    lifetime_ms REAL,
    emission_rate REAL,
    gravity REAL,
    initial_velocity TEXT,
    velocity_variance TEXT,
    color_start TEXT,
    color_end TEXT,
    size_start REAL,
    size_end REAL,
    rotation_speed REAL,
    fade_mode TEXT,
    is_emitting INTEGER,
    loop INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS patents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    status TEXT,
    invention_id INTEGER,
    blueprint_id INTEGER,
    owner_id INTEGER,
    owner_type TEXT,
    filed_date TEXT,
    granted_date TEXT,
    expiration_date TEXT,
    patent_number TEXT,
    jurisdiction_id INTEGER,
    is_exclusive INTEGER,
    license_allowed INTEGER,
    license_fee_percentage REAL,
    transferable INTEGER,
    expiry_years INTEGER,
    claims TEXT,
    prior_art_ids TEXT,
    infringer_ids TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS perks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id INTEGER,
    perk_type TEXT,
    source TEXT,
    rarity TEXT,
    stat_type TEXT,
    stat_modifier REAL,
    resistance_type TEXT,
    resistance_value INTEGER,
    ability_id INTEGER,
    ability_modifier TEXT,
    stacking_limit INTEGER,
    is_active INTEGER,
    is_hidden INTEGER,
    icon_id TEXT,
    source_id INTEGER,
    tags TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    owner_id INTEGER,
    species TEXT,
    level INTEGER,
    experience INTEGER,
    abilities TEXT,
    happiness INTEGER,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS phenomenons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pitys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    player_id TEXT,
    profile_id INTEGER,
    banner_id INTEGER,
    pulls_since_last_ssr INTEGER,
    pulls_since_last_featured INTEGER,
    total_pulls_on_banner INTEGER,
    total_ssr_pulled INTEGER,
    total_featured_pulled INTEGER,
    guaranteed_featured_next INTEGER,
    last_pull_at TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS plagues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS player_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    player_id INTEGER,
    metric_type TEXT,
    value REAL,
    unit TEXT,
    timestamp TEXT,
    session_id INTEGER,
    is_aggregated INTEGER,
    aggregation_period TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS player_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    player_name TEXT,
    player_id TEXT,
    level INTEGER,
    experience INTEGER,
    currencies TEXT,
    total_pulls INTEGER,
    total_spent REAL,
    days_active INTEGER,
    last_login TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS plazas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plot_branchs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    campaign_id INTEGER,
    branch_type TEXT,
    status TEXT,
    origin_branch_point_id INTEGER,
    story_content TEXT,
    consequence_ids TEXT,
    rejoin_point_id INTEGER,
    is_reversible INTEGER,
    difficulty_modifier REAL,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS plot_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    story_id INTEGER,
    scene_id INTEGER,
    device_type TEXT,
    is_active INTEGER,
    is_resolved INTEGER,
    related_entity_ids TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS pocket_dimensions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    owner_id INTEGER,
    size INTEGER,
    is_public INTEGER,
    max_visitors INTEGER,
    theme TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS port_districts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS portals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id INTEGER,
    destination_id INTEGER,
    portal_type TEXT,
    is_active INTEGER,
    is_one_way INTEGER,
    cooldown INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS progression_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id INTEGER,
    event_type TEXT,
    from_time TEXT,
    to_time TEXT,
    reasons TEXT,
    effects TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS progression_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id INTEGER,
    time_point TEXT,
    level TEXT,
    character_class TEXT,
    experience TEXT,
    stats TEXT
);

CREATE TABLE IF NOT EXISTS prologues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    campaign_id INTEGER,
    title TEXT,
    prologue_type TEXT,
    is_skippable INTEGER,
    is_required INTEGER,
    content TEXT,
    scene_ids TEXT,
    character_ids TEXT,
    estimated_minutes INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS propagandas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    faction_id INTEGER,
    originator_name TEXT,
    campaign_type TEXT,
    distribution_medium TEXT,
    target_audience TEXT,
    effectiveness_score INTEGER,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS prototypes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    category TEXT,
    status TEXT,
    rarity TEXT,
    base_item_id INTEGER,
    final_product_name TEXT,
    creator_id INTEGER,
    laboratory_id INTEGER,
    progress REAL,
    build_cost_gold INTEGER,
    build_cost_resources TEXT,
    test_count INTEGER,
    success_count INTEGER,
    failure_count INTEGER,
    damage_modifier REAL,
    durability_modifier REAL,
    efficiency_modifier REAL,
    cost_modifier REAL,
    known_issues TEXT,
    failure_modes TEXT,
    iteration_number INTEGER,
    parent_prototype_id INTEGER,
    new_features TEXT,
    removed_features TEXT,
    reviewer_ids TEXT,
    approval_notes TEXT,
    approved_by_id INTEGER,
    icon_id INTEGER,
    model_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pulls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    player_id TEXT,
    profile_id INTEGER,
    banner_id INTEGER,
    pull_number INTEGER,
    is_ten_pull INTEGER,
    ten_pull_batch_id TEXT,
    result_type TEXT,
    result_id INTEGER,
    result_name TEXT,
    result_rarity TEXT,
    is_featured INTEGER,
    currency_type TEXT,
    cost INTEGER,
    pity_count_at_pull INTEGER,
    broke_pity INTEGER,
    pulled_at TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS punishments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    player_id TEXT,
    profile_id INTEGER,
    transaction_id TEXT,
    purchase_type TEXT,
    status TEXT,
    product_id TEXT,
    product_name TEXT,
    amount_usd REAL,
    currency TEXT,
    amount_local REAL,
    reward_currency_type TEXT,
    reward_amount INTEGER,
    bonus_amount INTEGER,
    platform TEXT,
    payment_provider TEXT,
    refund_reason TEXT,
    initiated_at TEXT,
    completed_at TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS puzzles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id INTEGER,
    puzzle_type TEXT,
    difficulty TEXT,
    completion_time INTEGER,
    attempt_count INTEGER,
    is_solved INTEGER,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quarters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    objectives TEXT,
    status TEXT,
    participant_ids TEXT,
    reward_ids TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quest_chains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    quest_node_ids TEXT,
    status TEXT,
    required_level INTEGER,
    is_repeatable INTEGER,
    cooldown_hours INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quest_givers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id INTEGER,
    location_id INTEGER,
    alternative_location_ids TEXT,
    quest_chain_ids TEXT,
    quest_node_ids TEXT,
    is_active INTEGER,
    has_daily_quests INTEGER,
    daily_reset_hour INTEGER,
    required_reputation INTEGER,
    greeting_message TEXT,
    status TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quest_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    quest_chain_id INTEGER,
    objective_ids TEXT,
    prerequisite_ids TEXT,
    reward_tier_ids TEXT,
    status TEXT,
    is_optional INTEGER,
    auto_complete INTEGER,
    position INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quest_objectives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    quest_node_id INTEGER,
    objective_type TEXT,
    target_type TEXT,
    target_id INTEGER,
    target_quantity INTEGER,
    current_progress INTEGER,
    status TEXT,
    is_optional INTEGER,
    is_hidden INTEGER,
    order_index INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quest_prerequisites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    prerequisite_type TEXT,
    required_quest_ids TEXT,
    required_level INTEGER,
    required_item_ids TEXT,
    required_skill_ids TEXT,
    required_attribute_values TEXT,
    is_flexible INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quest_reward_tiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    quest_node_id INTEGER,
    tier_level INTEGER,
    min_rating INTEGER,
    max_rating INTEGER,
    item_ids TEXT,
    currency_rewards TEXT,
    experience_reward INTEGER,
    reputation_rewards TEXT,
    skill_experience TEXT,
    is_guaranteed INTEGER,
    is_selectable INTEGER,
    selection_count INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quest_trackers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    player_profile_id INTEGER,
    active_quest_chain_ids TEXT,
    completed_quest_chain_ids TEXT,
    active_quest_node_ids TEXT,
    completed_quest_node_ids TEXT,
    failed_quest_node_ids TEXT,
    objective_progress TEXT,
    quest_chain_completions TEXT,
    last_updated TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS radios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    faction_id INTEGER,
    frequency TEXT,
    station_manager TEXT,
    broadcast_range TEXT,
    content_type TEXT,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS raids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    difficulty TEXT,
    max_players INTEGER,
    min_players INTEGER,
    min_level INTEGER,
    boss_ids TEXT,
    has_weekly_lockout INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ranks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    rank_type TEXT,
    tier INTEGER,
    required_level INTEGER,
    required_xp INTEGER,
    perks TEXT,
    is_permanent INTEGER,
    icon TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS relic_collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    collection_name TEXT,
    collection_type TEXT,
    tier TEXT,
    rarity TEXT,
    total_relics INTEGER,
    collected_relic_ids TEXT,
    relic_names TEXT,
    relic_descriptions TEXT,
    relic_origins TEXT,
    relic_eras TEXT,
    collection_power INTEGER,
    lore_power INTEGER,
    historical_significance TEXT,
    main_lore TEXT,
    hidden_lore TEXT,
    bonuses TEXT,
    unlock_level INTEGER,
    unlock_conditions TEXT,
    secrets TEXT,
    prophecies TEXT,
    powers_granted TEXT,
    restrictions TEXT,
    warnings TEXT,
    is_complete INTEGER,
    completion_reward TEXT
);

CREATE TABLE IF NOT EXISTS reproductions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reputations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    target_id TEXT,
    target_type TEXT,
    score INTEGER,
    level TEXT,
    visible INTEGER,
    locked INTEGER
);

CREATE TABLE IF NOT EXISTS requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    entity_type TEXT,
    entity_id INTEGER
);

CREATE TABLE IF NOT EXISTS researchs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    type TEXT,
    value TEXT,
    quantity INTEGER
);

CREATE TABLE IF NOT EXISTS research_centers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    faction_id INTEGER,
    location_id INTEGER,
    director_name TEXT,
    research_field TEXT,
    funding_level TEXT,
    is_classified INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS revolutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    reward_type TEXT,
    item_id INTEGER,
    currency_code TEXT,
    amount INTEGER
);

CREATE TABLE IF NOT EXISTS riddles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id INTEGER,
    riddle_text TEXT,
    answer TEXT,
    difficulty TEXT,
    hint_text TEXT,
    attempt_count INTEGER,
    is_solved INTEGER,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rituals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    religion_id TEXT,
    deity_id TEXT,
    ritual_type TEXT,
    difficulty INTEGER,
    required_components TEXT,
    effects TEXT,
    duration_minutes INTEGER,
    participants_required INTEGER,
    cooldown_hours INTEGER,
    is_secret INTEGER
);

CREATE TABLE IF NOT EXISTS rumors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id INTEGER,
    source_name TEXT,
    origin_date TEXT,
    truth_level TEXT,
    spread_speed TEXT,
    credibility_score INTEGER,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS runes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    stat_name TEXT,
    value REAL,
    is_percentage INTEGER
);

CREATE TABLE IF NOT EXISTS save_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id TEXT,
    is_active INTEGER,
    save_type TEXT,
    uses_remaining INTEGER,
    cooldown_seconds INTEGER,
    requires_quest_id TEXT,
    restores_health INTEGER,
    restores_mana INTEGER,
    restores_resources INTEGER,
    icon_path TEXT,
    marker_position TEXT,
    interaction_radius REAL,
    flags TEXT
);

CREATE TABLE IF NOT EXISTS schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id INTEGER,
    school_type TEXT,
    headmaster_name TEXT,
    student_capacity INTEGER,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    score_type TEXT,
    primary_file_path TEXT,
    total_duration_seconds REAL,
    composer TEXT,
    orchestrator TEXT,
    act_count INTEGER,
    movement_count INTEGER,
    has_intro INTEGER,
    has_outro INTEGER,
    instrument_count INTEGER,
    includes_choir INTEGER,
    includes_orchestra INTEGER,
    includes_synthetics INTEGER,
    emotional_tone TEXT,
    intensity_peak INTEGER,
    chapter_id INTEGER,
    quest_id INTEGER,
    scene_id INTEGER,
    is_adaptive INTEGER,
    stem_count INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scriptures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    title TEXT,
    religion_id TEXT,
    author_id TEXT,
    language TEXT,
    chapters INTEGER,
    verses_count INTEGER,
    key_teachings TEXT,
    prophecies TEXT,
    forbidden_knowledge INTEGER,
    rarity TEXT
);

CREATE TABLE IF NOT EXISTS seasons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    calendar_id INTEGER,
    months TEXT,
    typical_weather TEXT,
    average_temperature TEXT,
    precipitation TEXT,
    activities TEXT,
    festivals TEXT,
    crops_planted TEXT,
    crops_harvested TEXT,
    animal_behaviors TEXT,
    magical_phenomena TEXT,
    color_palette TEXT,
    icon_path TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS seasonal_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS secret_areas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    parent_location_id INTEGER,
    discovery_method TEXT,
    difficulty_level TEXT,
    discovery_count INTEGER,
    is_discovered INTEGER,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    parent_religion_id TEXT,
    founder_id TEXT,
    doctrines TEXT,
    practices TEXT,
    is_heresy INTEGER,
    persecution_level INTEGER,
    member_count INTEGER,
    headquarters TEXT
);

CREATE TABLE IF NOT EXISTS session_datas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    date TEXT,
    total_sessions INTEGER,
    total_playtime_minutes INTEGER,
    peak_concurrent_players INTEGER,
    average_session_duration TEXT,
    unique_players INTEGER,
    new_players INTEGER,
    returning_players INTEGER,
    crash_rate REAL,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS shaders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    shader_type TEXT,
    source_code TEXT,
    language TEXT,
    shader_version TEXT,
    is_compiled INTEGER,
    compilation_errors TEXT,
    uniforms TEXT,
    attributes TEXT,
    tags TEXT,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS share_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    author_id INTEGER,
    code TEXT,
    code_type TEXT,
    status TEXT,
    content_type TEXT,
    content_id INTEGER,
    content_version TEXT,
    usage_count INTEGER,
    max_uses INTEGER,
    expires_at TEXT,
    is_public INTEGER,
    requires_authentication INTEGER,
    version TEXT
);

CREATE TABLE IF NOT EXISTS shops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    item_id INTEGER,
    item_type TEXT,
    item_name TEXT,
    price INTEGER,
    currency_type TEXT,
    stock INTEGER,
    max_per_player INTEGER
);

CREATE TABLE IF NOT EXISTS siege_engines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS silences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    purpose TEXT,
    duration_seconds REAL,
    fade_in INTEGER,
    fade_out INTEGER,
    fade_in_duration REAL,
    fade_out_duration REAL,
    fade_in_style TEXT,
    fade_out_style TEXT,
    is_interruptible INTEGER,
    minimum_duration REAL,
    duck_other_audio INTEGER,
    duck_amount REAL,
    associated_scene_id INTEGER,
    associated_music_id INTEGER,
    associated_event_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id INTEGER,
    skill_type TEXT,
    category TEXT,
    rarity TEXT,
    level INTEGER,
    max_level INTEGER,
    experience INTEGER,
    experience_to_next INTEGER,
    power REAL,
    mastery INTEGER,
    cooldown_seconds INTEGER,
    mana_cost INTEGER,
    prerequisite_skill_ids TEXT,
    minimum_level INTEGER,
    icon_id TEXT,
    tags TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS skyboxs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    texture_path TEXT,
    has_day_night_cycle INTEGER,
    cloud_density REAL,
    weather_type TEXT,
    time_of_day TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS slumss (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS social_classs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id TEXT,
    class_name TEXT,
    tier INTEGER,
    title TEXT,
    benefits TEXT,
    restrictions TEXT,
    hereditary INTEGER
);

CREATE TABLE IF NOT EXISTS social_medias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    platform_type TEXT,
    founder_name TEXT,
    follower_count INTEGER,
    hashtag_count INTEGER,
    monetization_enabled INTEGER,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_mobilitys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id TEXT,
    starting_class TEXT,
    current_class TEXT,
    highest_class TEXT,
    moves_made INTEGER,
    direction TEXT,
    locked INTEGER
);

CREATE TABLE IF NOT EXISTS sockets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    item_id INTEGER,
    socket_type TEXT,
    socket_shape TEXT,
    slot_index INTEGER,
    rarity TEXT,
    is_unlocked INTEGER,
    is_required INTEGER,
    rune_id INTEGER,
    gem_id INTEGER,
    glyph_id INTEGER,
    required_material_ids TEXT,
    required_gold INTEGER,
    required_level INTEGER,
    is_glowing INTEGER,
    glow_color TEXT,
    stat_bonus_multiplier REAL,
    effect_duration_modifier REAL,
    version TEXT
);

CREATE TABLE IF NOT EXISTS solstices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sound_effects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    sound_effect_type TEXT,
    priority TEXT,
    file_path TEXT,
    duration_seconds REAL,
    volume REAL,
    pitch REAL,
    spatial_3d INTEGER,
    loop INTEGER,
    has_variations INTEGER,
    variation_count INTEGER,
    tags TEXT,
    associated_ability_id INTEGER,
    associated_item_id INTEGER,
    associated_event_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS soundtracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    title TEXT,
    soundtrack_type TEXT,
    mood TEXT,
    composer TEXT,
    file_path TEXT,
    duration_seconds REAL,
    bpm INTEGER,
    key_signature TEXT,
    is_loopable INTEGER,
    fade_in_duration REAL,
    fade_out_duration REAL,
    associated_location_id INTEGER,
    associated_event_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS spaceships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    owner_id INTEGER,
    ship_class TEXT,
    hull INTEGER,
    max_hull INTEGER,
    shields INTEGER,
    max_shields INTEGER,
    fuel INTEGER,
    max_fuel INTEGER,
    crew_capacity INTEGER,
    is_docked INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS spawn_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id TEXT,
    entity_type TEXT,
    entity_ids TEXT,
    spawn_position TEXT,
    spawn_rotation TEXT,
    spawn_radius REAL,
    is_active INTEGER,
    max_entities INTEGER,
    current_count INTEGER,
    spawn_type TEXT,
    spawn_interval INTEGER,
    spawn_wave_count INTEGER,
    spawn_wave_delay INTEGER,
    requires_quest_id TEXT,
    requires_level INTEGER,
    respawn_time INTEGER,
    conditions TEXT,
    flags TEXT
);

CREATE TABLE IF NOT EXISTS star_systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS storys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    story_type TEXT,
    content TEXT,
    choice_ids TEXT,
    connected_world_ids TEXT,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS storylines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    storyline_type TEXT,
    event_ids TEXT,
    quest_ids TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS subtitles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    text TEXT,
    start_time_ms INTEGER,
    end_time_ms INTEGER,
    voice_over_id TEXT,
    character_id TEXT,
    language TEXT,
    position TEXT,
    style TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS summons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    summoner_id TEXT,
    creature_id TEXT,
    creature_name TEXT,
    power_level INTEGER,
    summon_type TEXT,
    duration_minutes INTEGER,
    loyalty INTEGER,
    abilities TEXT,
    requirements TEXT,
    cost TEXT
);

CREATE TABLE IF NOT EXISTS supplys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    tag_type TEXT,
    color TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS talent_trees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    node_type TEXT,
    tier INTEGER,
    column INTEGER,
    point_cost INTEGER,
    prerequisite_node_ids TEXT,
    effects TEXT,
    icon_id TEXT,
    is_unlocked INTEGER
);

CREATE TABLE IF NOT EXISTS tariffs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS taxs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS teleporters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id INTEGER,
    destination_id INTEGER,
    teleporter_type TEXT,
    charges INTEGER,
    max_charges INTEGER,
    is_rechargeable INTEGER,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS televisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    faction_id INTEGER,
    channel_number INTEGER,
    network_name TEXT,
    broadcast_format TEXT,
    content_focus TEXT,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    template_type TEXT,
    content TEXT,
    rune_ids TEXT,
    parent_template_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS textures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    path TEXT,
    texture_type TEXT,
    file_size INTEGER,
    dimensions TEXT,
    color_space TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS themes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    theme_category TEXT,
    emotional_tone TEXT,
    musical_theme_id INTEGER,
    primary_instrument TEXT,
    key_signature TEXT,
    character_id INTEGER,
    faction_id INTEGER,
    location_id INTEGER,
    color_palette TEXT,
    is_recurring INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS time_periods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    period_type TEXT,
    start_date TEXT,
    end_date TEXT,
    parent_period_id INTEGER,
    child_period_ids TEXT,
    significance TEXT,
    key_events TEXT,
    tags TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS timelines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    timeline_type TEXT,
    scope_entity_id INTEGER,
    start_date TEXT,
    end_date TEXT,
    era_ids TEXT,
    event_ids TEXT,
    era_transition_ids TEXT,
    is_public INTEGER,
    is_canonical INTEGER,
    color_theme TEXT,
    display_format TEXT,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tokenboards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    counters TEXT,
    sticky_notes TEXT,
    shortcuts TEXT,
    timers TEXT,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tournaments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS traits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id INTEGER,
    category TEXT,
    nature TEXT,
    impact_value INTEGER,
    positive_effects TEXT,
    negative_effects TEXT,
    stat_modifiers TEXT,
    conflicts_with TEXT,
    synergizes_with TEXT,
    is_inheritable INTEGER,
    icon_id TEXT,
    tags TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS transitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    transition_type TEXT,
    duration_ms INTEGER,
    from_scene_id TEXT,
    to_scene_id TEXT,
    color TEXT,
    easing TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    localization_id INTEGER,
    key TEXT,
    context TEXT,
    source_text TEXT,
    translated_text TEXT,
    notes TEXT,
    status TEXT,
    is_approved INTEGER,
    is_machine_translated INTEGER,
    confidence_score REAL,
    character_count INTEGER,
    word_count INTEGER,
    max_length INTEGER,
    exceeds_max_length INTEGER,
    version TEXT
);

CREATE TABLE IF NOT EXISTS traps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id INTEGER,
    trap_type TEXT,
    damage INTEGER,
    difficulty_to_disable TEXT,
    trigger_method TEXT,
    is_armed INTEGER,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS treatys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    treaty_type TEXT,
    status TEXT,
    signatory_nation_ids TEXT,
    signatory_faction_ids TEXT,
    third_party_ids TEXT,
    negotiation_location_id INTEGER,
    mediator_ids TEXT,
    negotiation_event_ids TEXT,
    terms TEXT,
    obligations TEXT,
    prohibitions TEXT,
    rights_granted TEXT,
    signing_date TEXT,
    ratification_date TEXT,
    effective_date TEXT,
    expiration_date TEXT,
    is_indefinite INTEGER,
    territory_transfers TEXT,
    border_adjustments TEXT,
    resource_exchanges TEXT,
    trade_concessions TEXT,
    violation_consequences TEXT,
    dispute_mechanism TEXT,
    related_conflict_id INTEGER,
    predecessor_treaty_id INTEGER,
    successor_treaty_id INTEGER,
    treaty_document_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trophys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    trophy_type TEXT,
    rarity TEXT,
    icon TEXT,
    achievement_ids TEXT,
    is_held INTEGER,
    version TEXT
);

CREATE TABLE IF NOT EXISTS undergrounds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    underground_type TEXT,
    depth INTEGER,
    has_undead INTEGER,
    visibility TEXT,
    min_level INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS universitys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id INTEGER,
    motto TEXT,
    founded_year INTEGER,
    student_count INTEGER,
    is_public INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    author_id INTEGER,
    status TEXT,
    genre TEXT,
    chapter_count INTEGER,
    estimated_playtime_minutes INTEGER,
    starting_location_id INTEGER,
    required_level INTEGER,
    recommended_level INTEGER,
    play_count INTEGER,
    completion_count INTEGER,
    rating REAL,
    rating_count INTEGER,
    dialogue_line_count INTEGER,
    choice_count INTEGER,
    ending_count INTEGER,
    workshop_entry_id INTEGER,
    version TEXT
);

CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    owner_id INTEGER,
    vehicle_type TEXT,
    fuel_type TEXT,
    speed REAL,
    durability INTEGER,
    max_durability INTEGER,
    passenger_capacity INTEGER,
    upgrades TEXT,
    is_operational INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS visual_effects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    effect_type TEXT,
    duration_ms REAL,
    loop INTEGER,
    intensity REAL,
    scale REAL,
    priority INTEGER,
    tags TEXT,
    is_active INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS voice_actors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    status TEXT,
    language TEXT,
    character_ids TEXT,
    voice_samples TEXT,
    agency TEXT,
    contact_info TEXT,
    hourly_rate REAL,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS voice_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    text TEXT,
    voice_line_type TEXT,
    emotion TEXT,
    character_id INTEGER,
    voice_actor_id INTEGER,
    file_path TEXT,
    duration_seconds REAL,
    volume REAL,
    pitch REAL,
    speed REAL,
    language TEXT,
    is_localized INTEGER,
    associated_dialogue_id INTEGER,
    associated_scene_id INTEGER,
    version TEXT, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS voice_overs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    character_id TEXT,
    text TEXT,
    audio_asset_id TEXT,
    duration_ms INTEGER,
    voice_actor TEXT,
    emotion TEXT,
    language TEXT,
    volume REAL,
    priority INTEGER,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS wars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS wards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS waypoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    location_id TEXT,
    is_discovered INTEGER,
    is_active INTEGER,
    is_primary INTEGER,
    quest_id TEXT,
    waypoint_type TEXT,
    priority INTEGER,
    marker_type TEXT,
    marker_color TEXT,
    marker_position TEXT,
    radius REAL,
    show_on_minimap INTEGER,
    show_on_compass INTEGER,
    flags TEXT
);

CREATE TABLE IF NOT EXISTS weapon_systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS weather_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS witnesss (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workshop_entrys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    title TEXT,
    author_id TEXT,
    content_type TEXT,
    content_asset_id TEXT,
    thumbnail_id TEXT,
    version TEXT,
    tags TEXT,
    download_count INTEGER,
    rating REAL,
    rating_count INTEGER,
    is_featured INTEGER,
    is_approved INTEGER,
    is_public INTEGER,
    maturity_rating TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS worlds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    parent_id INTEGER,
    version TEXT
);

CREATE TABLE IF NOT EXISTS world_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS wormholes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    world_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

