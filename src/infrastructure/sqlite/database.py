"""SQLite database connection manager and schema initialization.

Extracted from the monolithic ``sqlite_repositories.py``. ``SQLiteDatabase``
holds the database path, provides a ``get_connection`` context manager, and
runs ``initialize_schema`` to create all the bridge/canonical tables used by
the repository layer. All repository classes receive a ``SQLiteDatabase``
instance and call ``db.get_connection()`` to execute SQL.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path


class SQLiteDatabase:
    """SQLite database connection manager."""

    def __init__(self, db_path: str = "lore_system.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def get_connection(self):
        """Get a database connection with automatic cleanup."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Allow column access by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize_schema(self):
        """Create all database tables."""
        with self.get_connection() as conn:
            # Worlds table
            conn.execute("""
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
                )
            """)
            
                        # ALL REMAINING 243 SQL TABLES FOR COMPLETE COVERAGE
            
                        # QuestSystem (8 tables)
            
            conn.execute("CREATE TABLE IF NOT EXISTS quest_chains (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, difficulty TEXT, max_rank INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS quest_nodes (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, node_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS quest_prerequisites (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS quest_objectives (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, objective_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS quest_trackers (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, character_id INTEGER, quest_id INTEGER, progress INTEGER, status TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS quest_givers (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS quest_rewards (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, reward_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS quest_reward_tiers (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, tier_level INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            
                        # Social/Religion (17 tables)
            
            conn.execute("CREATE TABLE IF NOT EXISTS reputations (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS affinities (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS dispositions (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS honors (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS karmas (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS social_classes (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS social_mobilities (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS cults (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS sects (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS holy_sites (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS scriptures (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS rituals (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS oaths (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS summons (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS pacts (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS curses (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS blessings (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            
                        # Locations (10 tables)
            
            conn.execute("CREATE TABLE IF NOT EXISTS hub_areas (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS instances (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS dungeons (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, difficulty TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS raids (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, min_players INTEGER, max_players INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS arenas (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, arena_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS open_world_zones (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, level_range TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS undergrounds (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, depth INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS skyboxes (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, day_cycle TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS dimensions (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, dimension_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS pocket_dimensions (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, max_size INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            
                        # Inventory/Crafting (9 tables)
            
            conn.execute("CREATE TABLE IF NOT EXISTS inventories (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, character_id INTEGER, capacity INTEGER, name TEXT, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS crafting_recipes (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, recipe_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS materials (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, rarity TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS components (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, component_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS blueprints (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, blueprint_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS enchantments (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, enchantment_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS sockets (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, socket_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS runes (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, rune_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS glyphs (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, glyph_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            
                        # UGC/Analytics (15 tables)
            
            conn.execute("CREATE TABLE IF NOT EXISTS mods (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, mod_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS custom_maps (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, map_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS user_scenarios (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS share_codes (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, code TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS workshop_entries (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, entry_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS localizations (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, language TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS translations (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, source_lang TEXT, target_lang TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS voice_overs (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, audio_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS subtitles (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, language TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS dubbings (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, language TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS player_metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, character_id INTEGER, metric_type TEXT, value REAL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS session_datas (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, session_id INTEGER, key TEXT, value TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS heatmaps (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, heatmap_data TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS drop_rates (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, item_id INTEGER, rate REAL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS conversion_rates (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, from_metric TEXT, to_metric TEXT, rate REAL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            
                        # LegendaryItems (6 tables)
            
            conn.execute("CREATE TABLE IF NOT EXISTS legendary_weapons (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, weapon_type TEXT, damage INTEGER, rarity TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS mythical_armors (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, armor_type TEXT, defense INTEGER, rarity TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS divine_items (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, item_type TEXT, power INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS cursed_items (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, curse_type TEXT, curse_strength INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS artifact_sets (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, set_bonus TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS relic_collections (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, collection_power INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            
                        # Companions/Transport (9 tables)
            
            conn.execute("CREATE TABLE IF NOT EXISTS pets (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, pet_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS mounts (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, mount_type TEXT, speed INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS familiars (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, familiar_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS mount_equipments (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, equipment_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS vehicles (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, vehicle_type TEXT, speed INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS spaceships (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, spaceship_type TEXT, max_range INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS airships (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, airship_type TEXT, altitude INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS portals (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, portal_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS teleporters (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, teleporter_type TEXT, cooldown INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            
                        # Institutions (7 tables)
            
            conn.execute("CREATE TABLE IF NOT EXISTS academies (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, institution_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS universities (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, research_level INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS schools (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, school_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS libraries (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, book_count INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS research_centers (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, focus_area TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS archives (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, archive_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS museums (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, exhibit_count INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            
                        # Media (7 tables)
            
            conn.execute("CREATE TABLE IF NOT EXISTS newspapers (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, circulation INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS radios (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, frequency TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS televisions (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, channel_number TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS internets (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, website_url TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS social_medias (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, platform TEXT, followers INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS propagandas (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, message TEXT, influence INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS rumors (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, source_type TEXT, credibility REAL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            
                        # Secrets (8 tables)
            
            conn.execute("CREATE TABLE IF NOT EXISTS secret_areas (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, discovery_condition TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS hidden_paths (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, path_type TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS easter_eggs (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, trigger_condition TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS mysteries (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, mystery_type TEXT, difficulty INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS enigmas (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, puzzle_type TEXT, solution TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS riddles (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, riddle_type TEXT, answer TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS puzzles (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, puzzle_type TEXT, solution TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS traps (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, trap_type TEXT, damage INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            
                        # Art (7 tables)
            
            conn.execute("CREATE TABLE IF NOT EXISTS festivals (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, duration_days INTEGER, participants INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS celebrations (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, celebration_type TEXT, location_id INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS ceremonies (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, ceremony_type TEXT, ritual_level INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS concerts (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, music_type TEXT, attendees INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS exhibitions (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, exhibition_type TEXT, exhibit_count INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS competitions (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, competition_type TEXT, prize_pool INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")
            conn.execute("CREATE TABLE IF NOT EXISTS tournaments (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, world_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, tournament_type TEXT, rounds INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE)")

            # Characters table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    backstory TEXT,
                    power_level INTEGER DEFAULT 1,
                    image_url TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Character abilities table (JSON stored as TEXT)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS character_abilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    power_level INTEGER DEFAULT 1,
                    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
                )
            """)

            # Items table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    rarity INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Locations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    environment_type TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Environments table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS environments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    time_of_day TEXT,
                    weather TEXT,
                    lighting TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Textures table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS textures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    texture_type TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # 3D Models table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS models3d (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    model_type TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    story_id INTEGER,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE SET NULL
                )
            """)

            # Tags table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    tag_type TEXT NOT NULL,
                    color TEXT,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Notes table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT,
                    is_pinned INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Templates table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    template_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    parent_template_id INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                    FOREIGN KEY (parent_template_id) REFERENCES templates(id) ON DELETE SET NULL
                )
            """)

            # Choices table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS choices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    story_id INTEGER,
                    name TEXT NOT NULL,
                    choice_type TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE SET NULL
                )
            """)

            # Flowcharts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS flowcharts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    story_id INTEGER,
                    name TEXT NOT NULL,
                    is_active INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE SET NULL
                )
            """)

            # Handouts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS handouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    session_id INTEGER,
                    title TEXT NOT NULL,
                    content TEXT,
                    is_revealed INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL
                )
            """)

            # Images table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Inspirations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS inspirations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    category TEXT,
                    content TEXT NOT NULL,
                    is_used INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Maps table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS maps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    is_interactive INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Tokenboards table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tokenboards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    is_active INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Stories table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Events table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    timeline_position INTEGER,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)

            # Pages table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT,
                    page_number INTEGER,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
                )
            """)


__all__ = ["SQLiteDatabase"]
