#!/usr/bin/env python3
"""
Add missing repositories to in_memory_repositories.py and sqlite_repositories.py
"""

import sys
from pathlib import Path

# Define code to add to in_memory_repositories.py
in_memory_additions = '''
class InMemorySessionRepository:
    """In-memory implementation of Session repository for testing."""

    def __init__(self):
        self._sessions: Dict[Tuple[TenantId, EntityId], "Session"] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._by_story: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, session: "Session") -> "Session":
        if session.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(session, 'id', new_id)

        key = (session.tenant_id, session.id)
        self._sessions[key] = session

        world_key = (session.tenant_id, session.world_id)
        if session.id not in self._by_world[world_key]:
            self._by_world[world_key].append(session.id)

        if session.story_id:
            story_key = (session.tenant_id, session.story_id)
            if session.id not in self._by_story[story_key]:
                self._by_story[story_key].append(session.id)

        return session

    def find_by_id(self, tenant_id: TenantId, session_id: EntityId) -> Optional["Session"]:
        return self._sessions.get((tenant_id, session_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List["Session"]:
        world_key = (tenant_id, world_id)
        session_ids = self._by_world.get(world_key, [])
        sessions = []
        for session_id in session_ids[offset:offset + limit]:
            session = self._sessions.get((tenant_id, session_id))
            if session:
                sessions.append(session)
        return sessions

    def list_by_story(self, tenant_id: TenantId, story_id: EntityId, limit: int = 50, offset: int = 0) -> List["Session"]:
        story_key = (tenant_id, story_id)
        session_ids = self._by_story.get(story_key, [])
        sessions = []
        for session_id in session_ids[offset:offset + limit]:
            session = self._sessions.get((tenant_id, session_id))
            if session:
                sessions.append(session)
        return sessions

    def list_active(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List["Session"]:
        all_sessions = self.list_by_world(tenant_id, world_id, limit=limit, offset=offset)
        return [s for s in all_sessions if s.is_active]

    def delete(self, tenant_id: TenantId, session_id: EntityId) -> bool:
        key = (tenant_id, session_id)
        if key not in self._sessions:
            return False

        session = self._sessions[key]

        world_key = (session.tenant_id, session.world_id)
        if session_id in self._by_world[world_key]:
            self._by_world[world_key].remove(session_id)

        if session.story_id:
            story_key = (session.tenant_id, session.story_id)
            if session_id in self._by_story[story_key]:
                self._by_story[story_key].remove(session_id)

        del self._sessions[key]
        return True


class InMemoryTagRepository(ITagRepository):
    """In-memory implementation of Tag repository for testing."""

    def __init__(self):
        self._tags: Dict[Tuple[TenantId, EntityId], Tag] = {}
        self._names: Dict[Tuple[TenantId, EntityId, str, str], EntityId] = defaultdict(dict)  # (tenant, world, name, type)
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, tag: Tag) -> Tag:
        if tag.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(tag, 'id', new_id)

        key = (tag.tenant_id, tag.id)
        name_key = (tag.tenant_id, tag.world_id, tag.name.value, tag.tag_type.value)

        if name_key in self._names and self._names[name_key] != tag.id:
            raise DuplicateEntity(f"Tag with name '{tag.name}' already exists in this world")

        self._tags[key] = tag
        self._names[name_key] = tag.id

        world_key = (tag.tenant_id, tag.world_id)
        if tag.id not in self._by_world[world_key]:
            self._by_world[world_key].append(tag.id)

        return tag

    def find_by_id(self, tenant_id: TenantId, tag_id: EntityId) -> Optional[Tag]:
        return self._tags.get((tenant_id, tag_id))

    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: TagName) -> Optional[Tag]:
        # Find by name (first match)
        for key, tag_id in self._names.items():
            if key[0] == tenant_id and key[1] == world_id and key[2] == name.value:
                return self._tags.get((tenant_id, tag_id))
        return None

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Tag]:
        world_key = (tenant_id, world_id)
        tag_ids = self._by_world.get(world_key, [])
        tags = []
        for tag_id in tag_ids[offset:offset + limit]:
            tag = self._tags.get((tenant_id, tag_id))
            if tag:
                tags.append(tag)
        return tags

    def list_by_type(self, tenant_id: TenantId, world_id: EntityId, tag_type: "TagType", limit: int = 50, offset: int = 0) -> List[Tag]:
        all_tags = self.list_by_world(tenant_id, world_id)
        return [t for t in all_tags if t.tag_type.value == tag_type.value][offset:offset + limit]

    def delete(self, tenant_id: TenantId, tag_id: EntityId) -> bool:
        key = (tenant_id, tag_id)
        if key not in self._tags:
            return False

        tag = self._tags[key]
        name_key = (tag.tenant_id, tag.world_id, tag.name.value, tag.tag_type.value)

        if name_key in self._names:
            del self._names[name_key]

        world_key = (tag.tenant_id, tag.world_id)
        if tag_id in self._by_world[world_key]:
            self._by_world[world_key].remove(tag_id)

        del self._tags[key]
        return True

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: TagName, tag_type: "TagType") -> bool:
        name_key = (tenant_id, world_id, name.value, tag_type.value)
        return name_key in self._names


class InMemoryNoteRepository(INoteRepository):
    """In-memory implementation of Note repository for testing."""

    def __init__(self):
        self._notes: Dict[Tuple[TenantId, EntityId], Note] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, note: Note) -> Note:
        if note.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(note, 'id', new_id)

        key = (note.tenant_id, note.id)
        self._notes[key] = note

        world_key = (note.tenant_id, note.world_id)
        if note.id not in self._by_world[world_key]:
            self._by_world[world_key].append(note.id)

        return note

    def find_by_id(self, tenant_id: TenantId, note_id: EntityId) -> Optional[Note]:
        return self._notes.get((tenant_id, note_id))

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Note]:
        world_key = (tenant_id, world_id)
        note_ids = self._by_world.get(world_key, [])
        notes = []
        for note_id in note_ids[offset:offset + limit]:
            note = self._notes.get((tenant_id, note_id))
            if note:
                notes.append(note)
        return notes

    def list_pinned(self, tenant_id: TenantId, world_id: EntityId, limit: int = 20, offset: int = 0) -> List[Note]:
        all_notes = self.list_by_world(tenant_id, world_id)
        return [n for n in all_notes if n.is_pinned][offset:offset + limit]

    def search_by_content(self, tenant_id: TenantId, search_term: str, limit: int = 20) -> List[Note]:
        results = []
        for note in self._notes.values():
            if note.tenant_id == tenant_id:
                if search_term.lower() in note.content.lower() or search_term.lower() in note.title.lower():
                    results.append(note)
                    if len(results) >= limit:
                        break
        return results

    def delete(self, tenant_id: TenantId, note_id: EntityId) -> bool:
        key = (tenant_id, note_id)
        if key not in self._notes:
            return False

        note = self._notes[key]
        world_key = (note.tenant_id, note.world_id)
        if note_id in self._by_world[world_key]:
            self._by_world[world_key].remove(note_id)

        del self._notes[key]
        return True


class InMemoryTemplateRepository(ITemplateRepository):
    """In-memory implementation of Template repository for testing."""

    def __init__(self):
        self._templates: Dict[Tuple[TenantId, EntityId], Template] = {}
        self._names: Dict[Tuple[TenantId, EntityId, str], EntityId] = {}
        self._by_world: Dict[Tuple[TenantId, EntityId], List[EntityId]] = defaultdict(list)
        self._next_id = 1

    def save(self, template: Template) -> Template:
        if template.id is None:
            new_id = EntityId(self._next_id)
            self._next_id += 1
            object.__setattr__(template, 'id', new_id)

        key = (template.tenant_id, template.id)
        name_key = (template.tenant_id, template.world_id, template.name.value)

        if name_key in self._names and self._names[name_key] != template.id:
            raise DuplicateEntity(f"Template with name '{template.name}' already exists in this world")

        self._templates[key] = template
        self._names[name_key] = template.id

        world_key = (template.tenant_id, template.world_id)
        if template.id not in self._by_world[world_key]:
            self._by_world[world_key].append(template.id)

        return template

    def find_by_id(self, tenant_id: TenantId, template_id: EntityId) -> Optional[Template]:
        return self._templates.get((tenant_id, template_id))

    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: TemplateName) -> Optional[Template]:
        template_id = self._names.get((tenant_id, world_id, name.value))
        if template_id:
            return self._templates.get((tenant_id, template_id))
        return None

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Template]:
        world_key = (tenant_id, world_id)
        template_ids = self._by_world.get(world_key, [])
        templates = []
        for template_id in template_ids[offset:offset + limit]:
            template = self._templates.get((tenant_id, template_id))
            if template:
                templates.append(template)
        return templates

    def list_by_type(self, tenant_id: TenantId, world_id: EntityId, template_type: "TemplateType", limit: int = 50, offset: int = 0) -> List[Template]:
        all_templates = self.list_by_world(tenant_id, world_id)
        return [t for t in all_templates if t.template_type.value == template_type.value][offset:offset + limit]

    def list_runes(self, tenant_id: TenantId, parent_template_id: EntityId, limit: int = 50, offset: int = 0) -> List[Template]:
        all_templates = [t for t in self._templates.values() if t.tenant_id == tenant_id]
        return [t for t in all_templates if t.parent_template_id == parent_template_id][offset:offset + limit]

    def delete(self, tenant_id: TenantId, template_id: EntityId) -> bool:
        key = (tenant_id, template_id)
        if key not in self._templates:
            return False

        template = self._templates[key]
        name_key = (template.tenant_id, template.world_id, template.name.value)

        if name_key in self._names:
            del self._names[name_key]

        world_key = (template.tenant_id, template.world_id)
        if template_id in self._by_world[world_key]:
            self._by_world[world_key].remove(template_id)

        del self._templates[key]
        return True

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: TemplateName) -> bool:
        name_key = (tenant_id, world_id, name.value)
        return name_key in self._names
'''

# Define SQLite additions
sqlite_additions = '''
class SQLiteSessionRepository:
    """SQLite implementation of Session repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, session: "Session") -> "Session":
        now = datetime.now().isoformat()

        if session.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO sessions (tenant_id, world_id, name, description, story_id, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.tenant_id.value,
                    session.world_id.value,
                    session.name,
                    session.description.value if session.description else None,
                    session.story_id.value if session.story_id else None,
                    session.is_active if hasattr(session, 'is_active') else True,
                    now,
                    now
                ))
                session_id = cursor.lastrowid
                object.__setattr__(session, 'id', EntityId(session_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE sessions
                    SET name = ?, description = ?, story_id = ?, is_active = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    session.name,
                    session.description.value if session.description else None,
                    session.story_id.value if session.story_id else None,
                    session.is_active if hasattr(session, 'is_active') else True,
                    session.id.value,
                    session.tenant_id.value
                ))

        return session

    def find_by_id(self, tenant_id: TenantId, session_id: EntityId) -> Optional["Session"]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM sessions WHERE id = ? AND tenant_id = ?
            """, (session_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_session(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List["Session"]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM sessions WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_session(row) for row in rows]

    def list_by_story(self, tenant_id: TenantId, story_id: EntityId, limit: int = 50, offset: int = 0) -> List["Session"]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM sessions WHERE story_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (story_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_session(row) for row in rows]

    def list_active(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List["Session"]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM sessions WHERE world_id = ? AND tenant_id = ? AND is_active = 1 ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_session(row) for row in rows]

    def delete(self, tenant_id: TenantId, session_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM sessions WHERE id = ? AND tenant_id = ?
            """, (session_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_session(self, row: sqlite3.Row) -> "Session":
        from src.domain.value_objects.common import Description
        # Create a minimal session object
        # In production, this should use the actual Session entity
        class SimpleSession:
            def __init__(self, id, tenant_id, world_id, name, description, story_id, is_active, created_at, updated_at):
                self.id = EntityId(id) if id else None
                self.tenant_id = TenantId(tenant_id)
                self.world_id = EntityId(world_id)
                self.name = name
                self.description = Description(description) if description else None
                self.story_id = EntityId(story_id) if story_id else None
                self.is_active = is_active
                self.created_at = Timestamp(datetime.fromisoformat(created_at))
                self.updated_at = Timestamp(datetime.fromisoformat(updated_at))

        return SimpleSession(
            row['id'],
            row['tenant_id'],
            row['world_id'],
            row['name'],
            row['description'],
            row['story_id'],
            row['is_active'],
            row['created_at'],
            row['updated_at']
        )


class SQLiteTagRepository:
    """SQLite implementation of Tag repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, tag: Tag) -> Tag:
        now = datetime.now().isoformat()

        if tag.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO tags (tenant_id, world_id, name, tag_type, color, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tag.tenant_id.value,
                    tag.world_id.value,
                    tag.name.value,
                    tag.tag_type.value,
                    tag.color,
                    tag.description,
                    now,
                    now
                ))
                tag_id = cursor.lastrowid
                object.__setattr__(tag, 'id', EntityId(tag_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE tags
                    SET name = ?, tag_type = ?, color = ?, description = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    tag.name.value,
                    tag.tag_type.value,
                    tag.color,
                    tag.description,
                    tag.id.value,
                    tag.tenant_id.value
                ))

        return tag

    def find_by_id(self, tenant_id: TenantId, tag_id: EntityId) -> Optional[Tag]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM tags WHERE id = ? AND tenant_id = ?
            """, (tag_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_tag(row)

    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: TagName) -> Optional[Tag]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM tags WHERE world_id = ? AND tenant_id = ? AND name = ? LIMIT 1
            """, (world_id.value, tenant_id.value, name.value)).fetchone()

            if not row:
                return None
            return self._row_to_tag(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Tag]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tags WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_tag(row) for row in rows]

    def list_by_type(self, tenant_id: TenantId, world_id: EntityId, tag_type: "TagType", limit: int = 50, offset: int = 0) -> List[Tag]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tags WHERE world_id = ? AND tenant_id = ? AND tag_type = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, tag_type.value, limit, offset)).fetchall()
            return [self._row_to_tag(row) for row in rows]

    def delete(self, tenant_id: TenantId, tag_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM tags WHERE id = ? AND tenant_id = ?
            """, (tag_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: TagName, tag_type: "TagType") -> bool:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT 1 FROM tags WHERE world_id = ? AND tenant_id = ? AND name = ? AND tag_type = ? LIMIT 1
            """, (world_id.value, tenant_id.value, name.value, tag_type.value)).fetchone()
            return row is not None

    def _row_to_tag(self, row: sqlite3.Row) -> Tag:
        return Tag(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=TagName(row['name']),
            tag_type=TagType(row['tag_type']),
            color=row['color'],
            description=row['description'],
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteNoteRepository:
    """SQLite implementation of Note repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, note: Note) -> Note:
        now = datetime.now().isoformat()

        if note.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO notes (tenant_id, world_id, title, content, tags, is_pinned, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    note.tenant_id.value,
                    note.world_id.value,
                    note.title,
                    note.content,
                    json.dumps(note.tags),
                    note.is_pinned,
                    now,
                    now
                ))
                note_id = cursor.lastrowid
                object.__setattr__(note, 'id', EntityId(note_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE notes
                    SET title = ?, content = ?, tags = ?, is_pinned = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    note.title,
                    note.content,
                    json.dumps(note.tags),
                    note.is_pinned,
                    note.id.value,
                    note.tenant_id.value
                ))

        return note

    def find_by_id(self, tenant_id: TenantId, note_id: EntityId) -> Optional[Note]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM notes WHERE id = ? AND tenant_id = ?
            """, (note_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_note(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Note]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM notes WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_note(row) for row in rows]

    def list_pinned(self, tenant_id: TenantId, world_id: EntityId, limit: int = 20, offset: int = 0) -> List[Note]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM notes WHERE world_id = ? AND tenant_id = ? AND is_pinned = 1 ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_note(row) for row in rows]

    def search_by_content(self, tenant_id: TenantId, search_term: str, limit: int = 20) -> List[Note]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM notes WHERE tenant_id = ? AND (title LIKE ? OR content LIKE ?) LIMIT ?
            """, (tenant_id.value, f'%{search_term}%', f'%{search_term}%', limit)).fetchall()
            return [self._row_to_note(row) for row in rows]

    def delete(self, tenant_id: TenantId, note_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM notes WHERE id = ? AND tenant_id = ?
            """, (note_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def _row_to_note(self, row: sqlite3.Row) -> Note:
        return Note(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            title=row['title'],
            content=row['content'],
            tags=json.loads(row['tags']),
            is_pinned=row['is_pinned'],
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )


class SQLiteTemplateRepository:
    """SQLite implementation of Template repository."""

    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def save(self, template: Template) -> Template:
        now = datetime.now().isoformat()

        if template.id is None:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO templates (tenant_id, world_id, name, description, template_type, content, parent_template_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    template.tenant_id.value,
                    template.world_id.value,
                    template.name.value,
                    template.description,
                    template.template_type.value,
                    template.content.value,
                    template.parent_template_id.value if template.parent_template_id else None,
                    now,
                    now
                ))
                template_id = cursor.lastrowid
                object.__setattr__(template, 'id', EntityId(template_id))
        else:
            with self.db.get_connection() as conn:
                conn.execute("""
                    UPDATE templates
                    SET name = ?, description = ?, template_type = ?, content = ?, parent_template_id = ?
                    WHERE id = ? AND tenant_id = ?
                """, (
                    template.name.value,
                    template.description,
                    template.template_type.value,
                    template.content.value,
                    template.parent_template_id.value if template.parent_template_id else None,
                    template.id.value,
                    template.tenant_id.value
                ))

        return template

    def find_by_id(self, tenant_id: TenantId, template_id: EntityId) -> Optional[Template]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM templates WHERE id = ? AND tenant_id = ?
            """, (template_id.value, tenant_id.value)).fetchone()

            if not row:
                return None
            return self._row_to_template(row)

    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: TemplateName) -> Optional[Template]:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM templates WHERE world_id = ? AND tenant_id = ? AND name = ? LIMIT 1
            """, (world_id.value, tenant_id.value, name.value)).fetchone()

            if not row:
                return None
            return self._row_to_template(row)

    def list_by_world(self, tenant_id: TenantId, world_id: EntityId, limit: int = 50, offset: int = 0) -> List[Template]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM templates WHERE world_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_template(row) for row in rows]

    def list_by_type(self, tenant_id: TenantId, world_id: EntityId, template_type: "TemplateType", limit: int = 50, offset: int = 0) -> List[Template]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM templates WHERE world_id = ? AND tenant_id = ? AND template_type = ? ORDER BY id LIMIT ? OFFSET ?
            """, (world_id.value, tenant_id.value, template_type.value, limit, offset)).fetchall()
            return [self._row_to_template(row) for row in rows]

    def list_runes(self, tenant_id: TenantId, parent_template_id: EntityId, limit: int = 50, offset: int = 0) -> List[Template]:
        with self.db.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM templates WHERE parent_template_id = ? AND tenant_id = ? ORDER BY id LIMIT ? OFFSET ?
            """, (parent_template_id.value, tenant_id.value, limit, offset)).fetchall()
            return [self._row_to_template(row) for row in rows]

    def delete(self, tenant_id: TenantId, template_id: EntityId) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM templates WHERE id = ? AND tenant_id = ?
            """, (template_id.value, tenant_id.value))
            return cursor.rowcount > 0

    def exists(self, tenant_id: TenantId, world_id: EntityId, name: TemplateName) -> bool:
        with self.db.get_connection() as conn:
            row = conn.execute("""
                SELECT 1 FROM templates WHERE world_id = ? AND tenant_id = ? AND name = ? LIMIT 1
            """, (world_id.value, tenant_id.value, name.value)).fetchone()
            return row is not None

    def _row_to_template(self, row: sqlite3.Row) -> Template:
        return Template(
            tenant_id=TenantId(row['tenant_id']),
            world_id=EntityId(row['world_id']),
            name=TemplateName(row['name']),
            description=row['description'],
            template_type=TemplateType(row['template_type']),
            content=Content(row['content']),
            rune_ids=[],  # Would need to load separately
            parent_template_id=EntityId(row['parent_template_id']) if row['parent_template_id'] else None,
            created_at=Timestamp(datetime.fromisoformat(row['created_at'])),
            updated_at=Timestamp(datetime.fromisoformat(row['updated_at'])),
            id=EntityId(row['id'])
        )
'''

print("Add the following code to in_memory_repositories.py:")
print("=" * 80)
print(in_memory_additions)
print()

print("Add the following code to sqlite_repositories.py:")
print("=" * 80)
print(sqlite_additions)
