#!/usr/bin/env python3
"""
Add SQLite Quest repositories to sqlite_repositories.py
"""

import sys
from pathlib import Path

sqlite_path = Path("/root/clawd/src/infrastructure/sqlite_repositories.py")

quest_sqlite = '''
class SQLiteQuestChainRepository:
    """SQLite implementation of QuestChain repository."""
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, quest_chain):
        from datetime import datetime
        now = datetime.now().isoformat()
        if quest_chain.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO quest_chains (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    quest_chain.tenant_id.value,
                    quest_chain.world_id.value if hasattr(quest_chain, "world_id") else None,
                    quest_chain.name,
                    getattr(quest_chain, "description", None),
                    now, now
                ))
                object.__setattr__(quest_chain, "id", EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE quest_chains SET name = ?, description = ? WHERE id = ? AND tenant_id = ?
                """, (
                    quest_chain.name,
                    getattr(quest_chain, "description", None),
                    quest_chain.id.value,
                    quest_chain.tenant_id.value
                ))
        return quest_chain

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM quest_chains WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM quest_chains WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM quest_chains WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        from src.domain.entities.quest_chain import QuestChain
        from src.domain.value_objects.common import Description, Timestamp
        return QuestChain(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteQuestNodeRepository:
    """SQLite implementation of QuestNode repository."""
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, quest_node):
        from datetime import datetime
        now = datetime.now().isoformat()
        if quest_node.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO quest_nodes (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    quest_node.tenant_id.value,
                    quest_node.world_id.value if hasattr(quest_node, "world_id") else None,
                    quest_node.name,
                    getattr(quest_node, "description", None),
                    now, now
                ))
                object.__setattr__(quest_node, "id", EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE quest_nodes SET name = ?, description = ? WHERE id = ? AND tenant_id = ?
                """, (
                    quest_node.name,
                    getattr(quest_node, "description", None),
                    quest_node.id.value,
                    quest_node.tenant_id.value
                ))
        return quest_node

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM quest_nodes WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM quest_nodes WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM quest_nodes WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        from src.domain.entities.quest_node import QuestNode
        from src.domain.value_objects.common import Description, Timestamp
        return QuestNode(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteQuestPrerequisiteRepository:
    """SQLite implementation of QuestPrerequisite repository."""
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, prereq):
        from datetime import datetime
        now = datetime.now().isoformat()
        if prereq.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO quest_prerequisites (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    prereq.tenant_id.value,
                    prereq.world_id.value if hasattr(prereq, "world_id") else None,
                    prereq.name,
                    getattr(prereq, "description", None),
                    now, now
                ))
                object.__setattr__(prereq, "id", EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE quest_prerequisites SET name = ?, description = ? WHERE id = ? AND tenant_id = ?
                """, (
                    prereq.name,
                    getattr(prereq, "description", None),
                    prereq.id.value,
                    prereq.tenant_id.value
                ))
        return prereq

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM quest_prerequisites WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM quest_prerequisites WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM quest_prerequisites WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        from src.domain.entities.quest_prerequisite import QuestPrerequisite
        from src.domain.value_objects.common import Description, Timestamp
        return QuestPrerequisite(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteQuestObjectiveRepository:
    """SQLite implementation of QuestObjective repository."""
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, objective):
        from datetime import datetime
        now = datetime.now().isoformat()
        if objective.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO quest_objectives (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    objective.tenant_id.value,
                    objective.world_id.value if hasattr(objective, "world_id") else None,
                    objective.name,
                    getattr(objective, "description", None),
                    now, now
                ))
                object.__setattr__(objective, "id", EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE quest_objectives SET name = ?, description = ? WHERE id = ? AND tenant_id = ?
                """, (
                    objective.name,
                    getattr(objective, "description", None),
                    objective.id.value,
                    objective.tenant_id.value
                ))
        return objective

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM quest_objectives WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM quest_objectives WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM quest_objectives WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        from src.domain.entities.quest_objective import QuestObjective
        from src.domain.value_objects.common import Description, Timestamp
        return QuestObjective(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteQuestTrackerRepository:
    """SQLite implementation of QuestTracker repository."""
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, tracker):
        from datetime import datetime
        now = datetime.now().isoformat()
        if tracker.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO quest_trackers (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    tracker.tenant_id.value,
                    tracker.world_id.value if hasattr(tracker, "world_id") else None,
                    tracker.name,
                    getattr(tracker, "description", None),
                    now, now
                ))
                object.__setattr__(tracker, "id", EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE quest_trackers SET name = ?, description = ? WHERE id = ? AND tenant_id = ?
                """, (
                    tracker.name,
                    getattr(tracker, "description", None),
                    tracker.id.value,
                    tracker.tenant_id.value
                ))
        return tracker

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM quest_trackers WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM quest_trackers WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM quest_trackers WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        from src.domain.entities.quest_tracker import QuestTracker
        from src.domain.value_objects.common import Description, Timestamp
        return QuestTracker(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteQuestGiverRepository:
    """SQLite implementation of QuestGiver repository."""
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, giver):
        from datetime import datetime
        now = datetime.now().isoformat()
        if giver.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO quest_givers (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    giver.tenant_id.value,
                    giver.world_id.value if hasattr(giver, "world_id") else None,
                    giver.name,
                    getattr(giver, "description", None),
                    now, now
                ))
                object.__setattr__(giver, "id", EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE quest_givers SET name = ?, description = ? WHERE id = ? AND tenant_id = ?
                """, (
                    giver.name,
                    getattr(giver, "description", None),
                    giver.id.value,
                    giver.tenant_id.value
                ))
        return giver

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM quest_givers WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM quest_givers WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM quest_givers WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        from src.domain.entities.quest_giver import QuestGiver
        from src.domain.value_objects.common import Description, Timestamp
        return QuestGiver(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteQuestRewardRepository:
    """SQLite implementation of QuestReward repository."""
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, reward):
        from datetime import datetime
        now = datetime.now().isoformat()
        if reward.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO quest_rewards (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    reward.tenant_id.value,
                    reward.world_id.value if hasattr(reward, "world_id") else None,
                    reward.name,
                    getattr(reward, "description", None),
                    now, now
                ))
                object.__setattr__(reward, "id", EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE quest_rewards SET name = ?, description = ? WHERE id = ? AND tenant_id = ?
                """, (
                    reward.name,
                    getattr(reward, "description", None),
                    reward.id.value,
                    reward.tenant_id.value
                ))
        return reward

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM quest_rewards WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM quest_rewards WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM quest_rewards WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        from src.domain.entities.quest_reward import QuestReward
        from src.domain.value_objects.common import Description, Timestamp
        return QuestReward(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteQuestRewardTierRepository:
    """SQLite implementation of QuestRewardTier repository."""
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, tier):
        from datetime import datetime
        now = datetime.now().isoformat()
        if tier.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO quest_reward_tiers (tenant_id, world_id, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    tier.tenant_id.value,
                    tier.world_id.value if hasattr(tier, "world_id") else None,
                    tier.name,
                    getattr(tier, "description", None),
                    now, now
                ))
                object.__setattr__(tier, "id", EntityId(cursor.lastrowid))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE quest_reward_tiers SET name = ?, description = ? WHERE id = ? AND tenant_id = ?
                """, (
                    tier.name,
                    getattr(tier, "description", None),
                    tier.id.value,
                    tier.tenant_id.value
                ))
        return tier

    def find_by_id(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM quest_reward_tiers WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value)).fetchone()
            if not row:
                return None
            return self._row_to_entity(row)

    def list_by_world(self, tenant_id, world_id, limit=50, offset=0):
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM quest_reward_tiers WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def delete(self, tenant_id, entity_id):
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM quest_reward_tiers WHERE id = ? AND tenant_id = ?
            """, (entity_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_entity(self, row):
        return self._entity_from_row(row)

    @staticmethod
    def _entity_from_row(row):
        from src.domain.entities.quest_reward_tier import QuestRewardTier
        from src.domain.value_objects.common import Description, Timestamp
        return QuestRewardTier(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']) if row['world_id'] else None,
            name=row['name'],
            description=Description(row['description']) if row['description'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )
'''

# Find end of file and append
content = sqlite_path.read_text()
with open(sqlite_path, 'a') as f:
    f.write(content)
    f.write(quest_sqlite)

print("✅ Added 8 SQLite Quest repository implementations to sqlite_repositories.py")
