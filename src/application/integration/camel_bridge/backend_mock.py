"""Deterministic (test/offline) backend for the rumor bridge pipeline.

Extracted from ``rumor_agents.py``. ``DeterministicRumorBackend`` is a
no-network backend that replays a queued list of canned LLM responses,
used by the integration test suite and offline runs. It has no
dependency on the rest of the bridge pipeline.
"""

from __future__ import annotations

import json
import signal
import time
from typing import Sequence


# --- Auto-extracted body (lines 351-1362 of original rumor_agents.py) ---
class DeterministicRumorBackend:
    """Test/offline backend with queued responses."""

    def __init__(self, responses: Sequence[str] | None = None):
        self._responses = list(responses or [])

    def generate(self, system_message: str, user_message: str) -> str:
        if self._responses:
            return self._responses.pop(0)
        theme = (
            user_message.split("Theme:", 1)[-1].splitlines()[0].strip()
            or "market unrest"
        )
        if "campaign" in system_message.lower() or "prologue" in system_message.lower():
            return json.dumps(
                {
                    "campaign": {
                        "title": f"{theme.title()} Campaign",
                        "description": f"A full campaign spun out of the {theme} unrest.",
                        "campaign_type": "main_story",
                        "recommended_level": 5,
                        "estimated_hours": 8,
                        "is_replayable": False,
                    },
                    "story": {
                        "name": f"{theme.title()} Chronicle",
                        "description": f"The central story thread behind {theme}.",
                        "content": f"Rumors of {theme} grow into a city-wide reckoning.",
                        "story_type": "linear",
                    },
                    "storylines": [
                        {
                            "name": "Lantern Line",
                            "description": "Tracks how harbor whispers become public raids.",
                            "storyline_type": "main",
                            "events": ["Blue Lantern Raid"],
                        }
                    ],
                    "character_variants": [
                        {
                            "character_name": "Mara Voss",
                            "name": "Bellwarden Disguise",
                            "description": "A covert disguise for moving through curfew lines.",
                            "variant_type": "costume",
                            "rarity": "uncommon",
                        }
                    ],
                    "character_evolutions": [
                        {
                            "character_name": "Mara Voss",
                            "current_stage": "advanced",
                            "previous_stage": "intermediate",
                            "evolution_type": "story_unlocked",
                            "variant_names": ["Bellwarden Disguise"],
                        }
                    ],
                    "character_profile_entries": [
                        {
                            "character_name": "Mara Voss",
                            "field_name": "fear",
                            "field_value": "The harbor bells ringing in an empty street.",
                        }
                    ],
                    "motion_captures": [
                        {
                            "name": "Harbor Warning Gesture",
                            "file_path": "captures/harbor_warning.fbx",
                            "character_name": "Mara Voss",
                            "actor_name": "Talan Reed",
                            "animation_type": "social",
                            "status": "completed",
                        }
                    ],
                    "voice_actors": [
                        {
                            "name": "Talan Reed",
                            "language": "Common",
                            "character_names": ["Mara Voss"],
                            "status": "active",
                        }
                    ],
                    "affinities": [
                        {
                            "source_name": "Mara Voss",
                            "target_name": "Iven Hale",
                            "category": "trust",
                            "value": 0.8,
                        }
                    ],
                    "dispositions": [
                        {
                            "entity_name": "Mara Voss",
                            "target_type": "faction",
                            "target_value": "Harbor Guard",
                            "attitude": "unfriendly",
                            "intensity": 6,
                        }
                    ],
                    "quests": [
                        {
                            "name": "Silence Before the Bell",
                            "description": "Carry the final warning through the harbor before panic erupts.",
                            "player_briefing": "Dockmaster Elra needs a runner who can cross the piers before fear becomes riot.",
                            "journal_summary": "Warn the harbor before the bells turn rumor into stampede.",
                            "acceptance_text": "Take the warning to the dockworkers and light the signal pyre before curfew shuts the waterfront.",
                            "completion_text": "The piers answer in time, and the harbor meets the bells with preparation instead of panic.",
                            "failure_text": "The warning arrives too late; panic spreads faster than the truth.",
                            "reward_summary": "Bellkeeper's Reward: 25 silver and enough goodwill to keep the watch on your side.",
                            "objectives": [
                                "Speak to the dockworkers",
                                "Light the signal pyre",
                            ],
                            "participant_names": ["Mara Voss", "Iven Hale"],
                            "reward_tier_names": ["Bellkeeper's Reward"],
                        }
                    ],
                    "quest_chains": [
                        {
                            "name": "Harbor Reckoning",
                            "description": "A civic mission chain that decides whether the harbor revolts or submits.",
                            "node_names": ["Warn the Docks"],
                            "required_level": 3,
                        }
                    ],
                    "quest_givers": [
                        {
                            "name": "Dockmaster Elra",
                            "description": "A veteran dockmaster who turns rumor into action.",
                            "character_name": "Mara Voss",
                            "quest_chain_names": ["Harbor Reckoning"],
                            "quest_node_names": ["Warn the Docks"],
                        }
                    ],
                    "quest_nodes": [
                        {
                            "quest_chain_name": "Harbor Reckoning",
                            "name": "Warn the Docks",
                            "description": "Warn every district before curfew locks the gates.",
                            "objective_descriptions": ["Speak to the dockworkers"],
                            "prerequisite_descriptions": [
                                "Complete Silence Before the Bell"
                            ],
                            "reward_tier_names": ["Bellkeeper's Reward"],
                        }
                    ],
                    "quest_objectives": [
                        {
                            "quest_node_name": "Warn the Docks",
                            "description": "Speak to the dockworkers",
                            "objective_type": "talk",
                            "target_name": "Iven Hale",
                            "objective_hint": "Start at the eastern piers where Iven Hale is rallying the night shift.",
                        }
                    ],
                    "quest_prerequisites": [
                        {
                            "description": "Complete Silence Before the Bell",
                            "prerequisite_type": "quest",
                            "required_quest_names": ["Silence Before the Bell"],
                            "required_level": 3,
                        }
                    ],
                    "quest_reward_tiers": [
                        {
                            "quest_node_name": "Warn the Docks",
                            "name": "Bellkeeper's Reward",
                            "description": "A practical reward for warning the harbor in time.",
                            "tier_level": 1,
                            "currency_rewards": {"silver": 25},
                            "experience_reward": 120,
                        }
                    ],
                    "quest_trackers": [
                        {
                            "player_character_name": "Mara Voss",
                            "active_chain_names": ["Harbor Reckoning"],
                            "active_node_names": ["Warn the Docks"],
                            "objective_progress": {"Speak to the dockworkers": 1},
                        }
                    ],
                    "items": [
                        {
                            "name": f"{theme.title()} Relic",
                            "description": f"A signature item born from the {theme} unrest.",
                            "item_type": "artifact",
                            "rarity": "rare",
                            "level": 10,
                            "enhancement": 1,
                            "max_enhancement": 5,
                            "special_stat": "crit_rate",
                            "special_stat_value": 0.08,
                        }
                    ],
                    "blueprints": [
                        {
                            "name": f"{theme.title()} Relic Schematic",
                            "description": f"A schematic for rebuilding the {theme} relic.",
                            "blueprint_type": "weapon",
                            "rarity": "rare",
                            "complexity": 6,
                            "estimated_crafting_time": 420,
                            "requirements": [
                                {"requirement_type": "level", "value": "5"}
                            ],
                            "required_level": 5,
                            "result_item_name": f"{theme.title()} Relic",
                            "result_quantity": 1,
                        }
                    ],
                    "enchantments": [
                        {
                            "name": f"{theme.title()} Ward",
                            "description": f"A ward that protects gear from the pressure of {theme}.",
                            "enchantment_type": "general",
                            "rarity": "rare",
                            "effects": [
                                {
                                    "effect": "protection",
                                    "value": 10,
                                    "is_percentage": True,
                                }
                            ],
                            "required_gold": 75,
                        }
                    ],
                    "runes": [
                        {
                            "name": f"{theme.title()} Sigil Rune",
                            "description": f"A rune carved to survive the pressure of {theme}.",
                            "rune_type": "mystical",
                            "rank": "rare",
                            "bonuses": [
                                {
                                    "stat_name": "attack_power",
                                    "value": 8,
                                    "is_percentage": False,
                                }
                            ],
                            "effects": [
                                {
                                    "effect_name": "arc_burst",
                                    "effect_value": 12,
                                    "trigger_chance": 0.25,
                                    "cooldown_seconds": 8,
                                }
                            ],
                            "required_socket_type": "rune",
                            "base_value": 95,
                        }
                    ],
                    "glyphs": [
                        {
                            "name": f"{theme.title()} Harbor Glyph",
                            "description": f"A glyph that channels the omen-patterns of {theme}.",
                            "glyph_school": "arcane",
                            "tier": "advanced",
                            "category": "triggered",
                            "modifiers": [
                                {
                                    "stat_name": "spell_power",
                                    "value": 6,
                                    "operation": "add",
                                    "is_percentage": False,
                                }
                            ],
                            "abilities": [
                                {
                                    "ability_name": "lantern_pulse",
                                    "description": "Pulse a warning light.",
                                    "mana_cost": 8,
                                    "cooldown_seconds": 14,
                                    "duration_seconds": 4,
                                    "power": 1.4,
                                    "requires_target": False,
                                }
                            ],
                            "required_socket_type": "glyph",
                            "synergizes_with_schools": ["divine"],
                            "base_value": 110,
                        }
                    ],
                    "components": [
                        {
                            "name": f"{theme.title()} Core",
                            "description": f"A crafting core used to assemble the {theme} relic.",
                            "category": "core",
                            "rarity": "uncommon",
                            "quality": 65,
                            "durability": 80,
                            "max_durability": 100,
                            "weight": 1.5,
                            "size": "medium",
                            "is_craftable": True,
                        }
                    ],
                    "sockets": [
                        {
                            "item_name": f"{theme.title()} Relic",
                            "socket_type": "rune",
                            "socket_shape": "round",
                            "slot_index": 0,
                            "rarity": "uncommon",
                            "is_unlocked": True,
                            "stat_bonus_multiplier": 1.1,
                        }
                    ],
                    "masteries": [
                        {
                            "character_name": "Mara Voss",
                            "name": f"{theme.title()} Tactics",
                            "description": f"Battlefield instincts refined by surviving the {theme} unrest.",
                            "category": "combat",
                            "level": 28,
                            "max_level": 100,
                            "progress": 45,
                            "total_experience": 2800,
                            "bonuses": [
                                {
                                    "level": 10,
                                    "bonus_type": "damage",
                                    "value": 0.12,
                                    "description": "Stronger strikes under pressure.",
                                }
                            ],
                            "unlocked_bonuses": ["damage"],
                            "tags": ["harbor", "rumor_chain"],
                        }
                    ],
                    "skills": [
                        {
                            "character_name": "Mara Voss",
                            "name": f"{theme.title()} Feint",
                            "description": f"A combat technique refined during the {theme} unrest.",
                            "skill_type": "ability",
                            "category": "battle",
                            "rarity": "rare",
                            "level": 4,
                            "max_level": 12,
                            "experience": 220,
                            "experience_to_next": 300,
                            "power": 1.35,
                            "mastery": 44,
                            "cooldown_seconds": 12,
                            "mana_cost": 18,
                            "minimum_level": 3,
                            "tags": ["harbor", "counterattack"],
                        }
                    ],
                    "perks": [
                        {
                            "character_name": "Iven Hale",
                            "name": f"{theme.title()} Broker's Edge",
                            "description": f"A passive edge gained while navigating the {theme} panic.",
                            "perk_type": "economic",
                            "source": "quest_reward",
                            "rarity": "rare",
                            "stat_type": "bargaining",
                            "stat_modifier": 0.15,
                            "stacking_limit": 1,
                            "is_active": True,
                            "is_hidden": False,
                            "tags": ["harbor", "broker"],
                        }
                    ],
                    "traits": [
                        {
                            "character_name": "Mara Voss",
                            "name": "Bellwatch Resolve",
                            "description": "Mara holds the harbor line even when the bells turn ominous.",
                            "category": "social",
                            "nature": "positive",
                            "impact_value": 22,
                            "positive_effects": [
                                "steady morale",
                                "guardian reputation",
                            ],
                            "negative_effects": ["sleepless vigilance"],
                            "stat_modifiers": {"willpower": 2.0, "vitality": 1.0},
                            "conflicts_with": ["Harbor Cowardice"],
                            "synergizes_with": ["Dockside Discount"],
                            "is_inheritable": False,
                            "tags": ["harbor", "discipline"],
                        }
                    ],
                    "attributes": [
                        {
                            "character_name": "Mara Voss",
                            "name": "Harbor Focus",
                            "description": "Mara sharpens her judgment with each tolling bell.",
                            "attribute_type": "mind",
                            "scale_type": "static",
                            "base_value": 14,
                            "current_value": 16,
                            "maximum_value": 20,
                            "flat_bonus": 1,
                            "percentage_bonus": 7.5,
                            "temporary_bonus": 0.5,
                            "minimum_value": 0,
                            "display_name": "Harbor Focus",
                            "tags": ["harbor", "discipline"],
                        }
                    ],
                    "talent_trees": [
                        {
                            "character_name": "Mara Voss",
                            "name": f"{theme.title()} Doctrine",
                            "description": f"A branching doctrine assembled while surviving the {theme} unrest.",
                            "talent_tree_type": "specialization",
                            "total_points": 10,
                            "points_spent": 1,
                            "required_level": 4,
                            "tags": ["harbor", "doctrine"],
                            "nodes": [
                                {
                                    "id": "watch-step",
                                    "name": "Watch Step",
                                    "description": "A disciplined opening stance.",
                                    "node_type": "active",
                                    "tier": 1,
                                    "column": 1,
                                    "point_cost": 1,
                                    "is_unlocked": True,
                                },
                                {
                                    "id": "eclipse-call",
                                    "name": "Eclipse Call",
                                    "description": "A capstone signal that rallies allies.",
                                    "node_type": "ultimate",
                                    "tier": 2,
                                    "column": 2,
                                    "point_cost": 2,
                                    "prerequisite_node_ids": ["watch-step"],
                                    "is_unlocked": False,
                                },
                            ],
                        }
                    ],
                    "achievements": [
                        {
                            "name": f"{theme.title()} Survivor",
                            "description": f"Endure the {theme} panic without letting the harbor fall silent.",
                            "achievement_type": "challenge",
                            "difficulty": "hard",
                            "is_hidden": False,
                            "is_repeatable": False,
                            "icon": "achievement_harbor_survivor",
                        }
                    ],
                    "level_ups": [
                        {
                            "character_name": "Mara Voss",
                            "level_up_type": "mastery",
                            "old_level": 9,
                            "new_level": 10,
                            "stat_increases": {"attack": 2, "defense": 1},
                            "skill_points_gained": 3,
                            "selected_rewards": ["Bell Ward", "Harbor Sigil"],
                            "health_increase": 12,
                            "mana_increase": 4,
                            "notes": f"The {theme} panic forced Mara into a harsher doctrine.",
                        }
                    ],
                    "experiences": [
                        {
                            "character_name": "Mara Voss",
                            "experience_type": "questing",
                            "total_experience": 1840,
                            "current_level": 10,
                            "current_xp": 140,
                            "xp_to_next_level": 320,
                            "xp_multiplier": 1.15,
                            "total_gains": 6,
                            "largest_gain": 450,
                            "source_breakdown": {
                                "quest": 900,
                                "event": 490,
                                "achievement": 450,
                            },
                            "tags": ["harbor", "eclipse"],
                        }
                    ],
                    "progression_states": [
                        {
                            "time_point": 1,
                            "character_states": [
                                {
                                    "character_name": "Mara Voss",
                                    "level": 10,
                                    "character_class": "knight",
                                    "experience": 1840,
                                    "stats": {
                                        "attack": 18,
                                        "defense": 16,
                                        "agility": 12,
                                    },
                                },
                                {
                                    "character_name": "Iven Hale",
                                    "level": 8,
                                    "character_class": "assassin",
                                    "experience": 1320,
                                    "stats": {
                                        "strength": 11,
                                        "dexterity": 17,
                                        "willpower": 9,
                                    },
                                },
                            ],
                        }
                    ],
                    "progression_events": [
                        {
                            "character_name": "Mara Voss",
                            "event_type": "quest",
                            "from_time": 1,
                            "to_time": 2,
                            "description": f"Mara cashes in the {theme} pact and advances the watch.",
                            "reasons": [
                                {
                                    "rule_id": "harbor_contract",
                                    "description": "The harbor pact rewards those who hold the line.",
                                }
                            ],
                            "effects": {"quest_complete": "bellwatch_reward_applied"},
                        }
                    ],
                    "player_metrics": [
                        {
                            "player_name": "Mara Voss",
                            "metric_type": "combat_kills",
                            "value": 27,
                            "unit": "count",
                            "session_name": f"{theme.lower()}_raid",
                            "description": f"Tracks how many enemies Mara defeated during {theme}.",
                        }
                    ],
                    "drop_rates": [
                        {
                            "name": f"{theme.title()} Relic Chance",
                            "category": "artifact",
                            "drop_rate": 0.18,
                            "conditions": [
                                "complete harbor defense",
                                "ring all warning bells",
                            ],
                            "affected_item_names": [f"{theme.title()} Relic"],
                            "player_level_scaling": {"10": 1.2, "15": 1.35},
                            "is_event_boosted": True,
                            "boost_multiplier": 1.5,
                            "description": f"Boosted artifact drop profile tied to {theme}.",
                        }
                    ],
                    "loot_table_weights": [
                        {
                            "name": f"{theme.title()} Rare Cache",
                            "description": f"Controls rare cache payouts during {theme}.",
                            "loot_table_name": "Harbor Cache",
                            "item_type": "artifact",
                            "rarity": "epic",
                            "weight": 0.22,
                            "min_level": 8,
                            "is_unique": True,
                            "conditions": ["night encounter"],
                        }
                    ],
                    "difficulty_curves": [
                        {
                            "name": f"{theme.title()} Pressure Curve",
                            "description": f"Difficulty pacing model for {theme}.",
                            "curve_type": "sigmoid",
                            "base_level": 1,
                            "max_level": 5,
                            "level_xp_requirement": [100, 220, 380, 610, 900],
                            "scaling_factor": 1.3,
                            "level_time_minutes": [25, 35, 45, 60, 80],
                            "player_count_tiers": {"1": 1, "3": 2, "5": 4},
                            "is_adaptive": True,
                        }
                    ],
                    "dungeons": [
                        {
                            "name": f"{theme.title()} Vault",
                            "description": f"A dungeon tier where the fallout of {theme} is contained.",
                            "difficulty": "hard",
                            "max_players": 5,
                            "min_level": 8,
                            "boss_names": ["Mara Voss"],
                            "has_lockout": True,
                            "lockout_duration": 86400,
                        }
                    ],
                    "raids": [
                        {
                            "name": f"{theme.title()} Siege",
                            "description": f"A raid encounter escalated from the crisis around {theme}.",
                            "difficulty": "heroic",
                            "max_players": 10,
                            "min_players": 5,
                            "min_level": 10,
                            "boss_names": ["Mara Voss", "Iven Hale"],
                            "has_weekly_lockout": True,
                        }
                    ],
                    "world_events": [
                        {
                            "name": f"{theme.title()} Blackout",
                            "description": f"A world event spreading the consequences of {theme} across the region.",
                            "event_type": "crisis",
                            "severity": "high",
                            "duration_days": 3,
                            "affected_location_names": ["Harbor Quarter"],
                            "is_active": True,
                        }
                    ],
                    "arenas": [
                        {
                            "name": f"{theme.title()} Coliseum",
                            "description": f"A competitive arena built around the rising tensions of {theme}.",
                            "match_type": "team_deathmatch",
                            "team_size": 3,
                            "max_teams": 4,
                            "min_level": 6,
                            "has_ranked_mode": True,
                        }
                    ],
                    "instances": [
                        {
                            "name": f"{theme.title()} Watch Instance",
                            "description": f"A private combat scenario spun up from the chaos of {theme}.",
                            "difficulty": "hard",
                            "max_players": 4,
                            "min_level": 7,
                            "recommended_level": 9,
                            "time_limit": 1800,
                        }
                    ],
                    "open_world_zones": [
                        {
                            "name": f"{theme.title()} Frontier",
                            "description": f"An open zone reshaped by the aftermath of {theme}.",
                            "biome": "coast",
                            "min_level": 5,
                            "max_level": 15,
                            "player_cap": 120,
                            "poi_names": ["Harbor Quarter"],
                            "has_dynamic_events": True,
                        }
                    ],
                    "seasonal_events": [
                        {
                            "name": f"{theme.title()} Vigil",
                            "description": f"A recurring seasonal event commemorating the fallout around {theme}.",
                            "season": "winter",
                            "year_number": 12,
                            "duration_days": 7,
                            "reward_item_names": [f"{theme.title()} Relic"],
                            "is_recurring": True,
                            "recurrence_period_days": 365,
                            "is_active": True,
                        }
                    ],
                    "invasions": [
                        {
                            "name": f"{theme.title()} Incursion",
                            "description": f"A hostile push exploiting the chaos created by {theme}.",
                            "invasion_type": "naval",
                            "invader_name": "Night Tide Corsairs",
                            "target_name": "Harbor Quarter",
                            "force_size": 600,
                            "casualties": 120,
                            "conquest_progress": 45,
                            "is_successful": False,
                            "is_active": True,
                        }
                    ],
                    "wars": [
                        {
                            "name": f"War for {theme.title()}",
                            "description": f"A prolonged conflict over the political vacuum left by {theme}.",
                            "war_type": "territorial",
                            "aggressor_name": "Night Tide Corsairs",
                            "defender_name": "Harbor Wardens",
                            "conflict_region_name": "Bellglass Coast",
                            "total_casualties": 900,
                            "battles_fought": 6,
                            "territorial_change_names": ["Breakwater Battery"],
                            "victor_name": "Harbor Wardens",
                            "is_active": False,
                        }
                    ],
                    "legendary_weapons": [
                        {
                            "name": f"{theme.title()} Oathblade",
                            "description": f"A legendary weapon forged from the crisis around {theme}.",
                            "weapon_type": "sword",
                            "damage": 128,
                            "rarity": "legendary",
                            "special_ability": "Releases a warding pulse when the bells ring.",
                        }
                    ],
                    "mythical_armors": [
                        {
                            "name": f"{theme.title()} Aegis",
                            "description": f"A mythical armor set worn by defenders shaped by {theme}.",
                            "armor_type": "plate",
                            "defense": 94,
                            "rarity": "mythic",
                            "special_protection": "Absorbs the first surge of eclipse damage.",
                        }
                    ],
                    "divine_items": [
                        {
                            "name": f"{theme.title()} Reliquary",
                            "description": f"A divine relic preserving the last blessing against {theme}.",
                            "item_type": "relic",
                            "power": 111,
                            "rarity": "divine",
                            "deity_name": "Tidemother",
                            "domain": "storms",
                            "divine_ability": "Calls down a protective tide over allies.",
                        }
                    ],
                    "cursed_items": [
                        {
                            "name": f"{theme.title()} Griefthorn Idol",
                            "description": f"A cursed focus born from the unresolved grief around {theme}.",
                            "item_type": "amulet",
                            "power": 87,
                            "curse_type": "corruption",
                            "rarity": "cursed",
                            "benefit": "Amplifies dusk magic near graves.",
                            "curse_effect": "Slowly drains warmth from nearby allies.",
                            "risk_level": "high",
                        }
                    ],
                    "artifact_sets": [
                        {
                            "name": f"{theme.title()} Harrowglass Regalia",
                            "description": f"A fractured regalia recovered from the aftermath of {theme}.",
                            "set_type": "armor",
                            "total_pieces": 4,
                            "rarity": "mythical",
                            "set_bonus": "When fully restored, the regalia veils allies against curse surges.",
                        }
                    ],
                    "relic_collections": [
                        {
                            "name": f"Archive of {theme.title()}",
                            "description": f"A relic collection assembled to preserve the surviving truths of {theme}.",
                            "collection_type": "historical",
                            "total_relics": 3,
                            "rarity": "legendary",
                            "collection_power": 133,
                            "completion_reward": "Unlocks the Litany of Salt.",
                        }
                    ],
                    "plot_branches": [
                        {
                            "name": "Ledger Rebellion",
                            "description": "The survivors expose the magistrate and spark open revolt.",
                            "story_content": "The harbor crowds seize the evidence and turn whispers into rebellion.",
                            "branch_type": "major",
                            "consequence_descriptions": [
                                "The wardens tighten control over the harbor."
                            ],
                        },
                        {
                            "name": "Silent Harbor",
                            "description": "The survivors bury the truth and preserve uneasy order.",
                            "story_content": "The ledger disappears and the city survives under a harsher peace.",
                            "branch_type": "temporary",
                            "consequence_descriptions": [
                                "The wardens tighten control over the harbor."
                            ],
                            "is_reversible": True,
                        },
                    ],
                    "branch_points": [
                        {
                            "description": "The survivors decide whether truth or order matters more.",
                            "branch_point_type": "choice",
                            "choice_prompt": "Who do the survivors trust when the bells ring?",
                            "branch_names": ["Ledger Rebellion", "Silent Harbor"],
                        }
                    ],
                    "choices": [
                        {
                            "prompt": "Who do the survivors trust when the bells ring?",
                            "choice_type": "decision",
                            "options": [
                                {
                                    "label": "Trust Mara",
                                    "consequence": "Mara reveals the hidden ledger.",
                                    "next_story": "Blue Lantern Chronicle",
                                },
                                {
                                    "label": "Trust Iven",
                                    "consequence": "Iven opens the armory for a last stand.",
                                    "next_story": None,
                                },
                            ],
                        }
                    ],
                    "consequences": [
                        {
                            "description": "The wardens tighten control over the harbor.",
                            "consequence_type": "story",
                            "severity": "major",
                            "trigger_choice_prompt": "Who do the survivors trust when the bells ring?",
                        }
                    ],
                    "moral_choices": [
                        {
                            "prompt": "Will the survivors expose the magistrate or shield the city from panic?",
                            "description": "Truth may save the harbor or break it.",
                            "choice_alignment": "neutral",
                            "urgency": "high",
                            "options": [
                                {
                                    "label": "Expose the magistrate",
                                    "outcome": "The public rises immediately.",
                                    "alignment": "good",
                                },
                                {
                                    "label": "Shield the city",
                                    "outcome": "Order holds, but corruption survives.",
                                    "alignment": "lawful",
                                },
                            ],
                            "consequence_descriptions": [
                                "The wardens tighten control over the harbor."
                            ],
                        }
                    ],
                    "alternate_realities": [
                        {
                            "name": "Bellglass Reflection",
                            "description": "A fractured mirror-reality where the eclipse never ends.",
                            "reality_type": "alternate_possibility",
                            "access_method": "choice",
                            "divergence_point": "The harbor crowd chooses silence instead of revolt.",
                            "entry_points": ["Broken bell tower"],
                            "exit_points": ["Magistrate archive"],
                        }
                    ],
                    "flashbacks": [
                        {
                            "name": "Night of the First Bell",
                            "description": "A remembered omen from the night fear first took root.",
                            "scene_id": "prologue_1",
                            "trigger_event": "Blue Lantern Raid",
                            "characters": ["Mara Voss"],
                            "filter_effect": "sepia",
                        }
                    ],
                    "prologue": {
                        "title": "Before the First Whisper",
                        "description": "A tense introduction to the harbor unrest.",
                        "content": f"Before dawn, the first whispers of {theme} spread through the piers.",
                        "prologue_type": "world_building",
                        "is_skippable": False,
                        "is_required": True,
                        "estimated_minutes": 12,
                    },
                    "acts": [
                        {
                            "title": "Act I - Gathering Tension",
                            "description": "Rumors gather force.",
                            "act_number": 1,
                            "act_type": "setup",
                            "structure": "three_act",
                            "key_events": ["Dockside whispers"],
                            "estimated_minutes": 30,
                        },
                        {
                            "title": "Act II - Harbor Flashpoint",
                            "description": "Conflict reaches the streets.",
                            "act_number": 2,
                            "act_type": "rising_action",
                            "structure": "three_act",
                            "key_events": ["Harbor uprising"],
                            "estimated_minutes": 45,
                        },
                        {
                            "title": "Act III - Night of Oaths",
                            "description": "Alliances harden into consequence.",
                            "act_number": 3,
                            "act_type": "resolution",
                            "structure": "three_act",
                            "key_events": ["Oathbound alliance"],
                            "estimated_minutes": 35,
                        },
                    ],
                    "chapters": [
                        {
                            "title": "Chapter 1 - Tideborne Hints",
                            "description": "The first clues appear.",
                            "sequence_number": 1,
                            "act_numbers": [1],
                            "chapter_type": "introduction",
                            "estimated_minutes": 20,
                        },
                        {
                            "title": "Chapter 2 - Bells at Noon",
                            "description": "The city hears the warning.",
                            "sequence_number": 2,
                            "act_numbers": [2],
                            "chapter_type": "climax",
                            "estimated_minutes": 25,
                        },
                        {
                            "title": "Chapter 3 - Harbor Afterglow",
                            "description": "The fallout reshapes loyalties.",
                            "sequence_number": 3,
                            "act_numbers": [3],
                            "chapter_type": "resolution",
                            "estimated_minutes": 20,
                        },
                    ],
                    "episodes": [
                        {
                            "title": "Episode 1 - Hidden Ledger",
                            "description": "A clue surfaces in the market.",
                            "sequence_number": 1,
                            "chapter_number": 1,
                            "episode_type": "narrative",
                            "estimated_minutes": 12,
                        },
                        {
                            "title": "Episode 2 - Lantern Riot",
                            "description": "Crowds surge along the quay.",
                            "sequence_number": 2,
                            "chapter_number": 2,
                            "episode_type": "narrative",
                            "estimated_minutes": 15,
                        },
                        {
                            "title": "Episode 3 - Oath in the Rain",
                            "description": "Two survivors bind their fates.",
                            "sequence_number": 3,
                            "chapter_number": 3,
                            "episode_type": "narrative",
                            "estimated_minutes": 12,
                        },
                    ],
                    "epilogue": {
                        "title": "After the Rebellion",
                        "description": "The harbor remembers.",
                        "content": f"In the wake of {theme}, the city records new loyalties and old scars.",
                        "epilogue_type": "aftermath",
                        "trigger_condition": "always",
                        "is_skippable": False,
                        "estimated_minutes": 10,
                    },
                    "flash_forwards": [
                        {
                            "name": "Harbor in Ashes",
                            "description": "A prophetic glimpse of what the bells may yet destroy.",
                            "hinted_event": "Blue Lantern Raid",
                            "clarity_level": "vivid",
                            "is_prophetic": True,
                        }
                    ],
                    "endings": [
                        {
                            "title": "Lanterns at Dawn",
                            "description": "The city accepts the cost of truth.",
                            "ending_type": "good",
                            "rarity": "uncommon",
                            "conditions": ["Expose the magistrate"],
                            "ending_number": 1,
                        }
                    ],
                }
            )
        if "relationship" in system_message.lower():
            return json.dumps(
                [
                    {
                        "character_from_name": "Mara Voss",
                        "character_to_name": "Iven Hale",
                        "description": f"{theme.title()} forces them into a wary alliance.",
                        "relationship_type": "ally",
                        "relationship_level": 25,
                        "is_mutual": True,
                    }
                ]
            )
        if "event" in system_message.lower():
            event_name = f"{theme} Разворачивается"
            return json.dumps(
                [
                    {
                        "name": event_name,
                        "description": f"Напряжение вокруг {theme.lower()} выливается в открытый конфликт в районе гавани.",
                        "participant_names": ["Mara Voss", "Iven Hale"],
                        "outcome": "ongoing",
                    }
                ]
            )
        return json.dumps(
            [
                {
                    "name": f"{theme.title()} Whisper",
                    "description": f"A street rumor links {theme} to a hidden patron.",
                    "source_name": "Whisper Broker",
                    "truth_level": "Unverified",
                    "spread_speed": "Rapid",
                    "credibility_score": 5,
                }
            ]
        )
