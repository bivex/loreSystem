# -*- coding: utf-8 -*-
"""
Database operations for the MythWeave Lore Explorer.
Extracts tables, stats, and graph representations from the SQLite database.
"""
import sqlite3
import json
import os

DB_PATH = "lore_system.db"

def get_tables():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def get_table_data(table_name):
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    valid_tables = [row[0] for row in cursor.fetchall()]
    
    rows = []
    if table_name in valid_tables:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = [dict(row) for row in cursor.fetchall()]
        
        # Decode binary data
        for r in rows:
            for k, v in r.items():
                if isinstance(v, bytes):
                    r[k] = v.decode('utf-8', errors='ignore')
    conn.close()
    return rows

def get_characters_graph():
    nodes = []
    edges = []
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in cursor.fetchall()}
        
        if 'characters' not in tables:
            return {'nodes': [], 'edges': []}
            
        cursor.execute("SELECT id, name, rarity, element, role, backstory FROM characters")
        characters = [dict(row) for row in cursor.fetchall()]
        
        relationships = []
        if 'character_relationships' in tables:
            cursor.execute("SELECT character_from_id, character_to_id, relationship_type, relationship_level, is_mutual FROM character_relationships")
            relationships = [dict(row) for row in cursor.fetchall()]
            
        conn.close()
        
        elem_colors = {
            'fire': '#ef4444',
            'water': '#3b82f6',
            'earth': '#10b981',
            'wind': '#06b6d4',
            'light': '#f59e0b',
            'dark': '#8b5cf6',
            'physical': '#6b7280'
        }
        
        for char in characters:
            elem = str(char.get('element', '')).lower()
            bg_color = elem_colors.get(elem, '#6366f1')
            
            tooltip = f"<b>Роль:</b> {char.get('role', 'N/A')}<br>" \
                      f"<b>Стихия:</b> {char.get('element', 'N/A')}<br>" \
                      f"<b>Редкость:</b> {char.get('rarity', 'N/A')}<br>" \
                      f"<b>Биография:</b> {char.get('backstory', '')}"
                      
            nodes.append({
                'id': f"char_{char['id']}",
                'label': char['name'],
                'title': tooltip,
                'color': {
                    'background': bg_color,
                    'border': '#1e293b',
                    'highlight': {'background': '#ec4899', 'border': '#fbcfe8'}
                },
                'size': 20,
                'shape': 'dot'
            })
            
        for rel in relationships:
            r_type = str(rel.get('relationship_type', '')).lower()
            level = rel.get('relationship_level')
            is_mut = rel.get('is_mutual')
            
            if r_type in ['ally', 'friend'] or (level is not None and level > 10):
                line_color = '#10b981'
            elif r_type in ['enemy', 'rival'] or (level is not None and level < -10):
                line_color = '#ef4444'
            else:
                line_color = '#9ca3af'
                
            label_str = f"{r_type}"
            if level is not None:
                label_str += f" ({level})"
                
            edge = {
                'from': f"char_{rel['character_from_id']}",
                'to': f"char_{rel['character_to_id']}",
                'label': label_str,
                'color': {'color': line_color, 'highlight': '#ec4899'},
                'font': {'align': 'middle', 'color': '#9ca3af', 'size': 9, 'face': 'Inter'},
                'width': 2
            }
            
            if not is_mut:
                edge['arrows'] = 'to'
                
            edges.append(edge)
            
    except Exception as e:
        print(f"Error building character graph: {e}")
        
    return {'nodes': nodes, 'edges': edges}

def get_locations_graph():
    nodes = []
    edges = []
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in cursor.fetchall()}
        
        # Determine World/Campaign Title
        world_name = "Основной мир"
        world_desc = "Генерируемый игровой мир лора"
        if 'campaigns' in tables:
            cursor.execute("SELECT title, description FROM campaigns LIMIT 1")
            campaign = cursor.fetchone()
            if campaign:
                world_name = campaign['title']
                world_desc = campaign['description'] or world_desc
                
        # Add root World node
        nodes.append({
            'id': 'world_1',
            'label': world_name,
            'title': f"<b>Мир: {world_name}</b><br>{world_desc}",
            'color': {
                'background': '#10b981', # emerald green
                'border': '#065f46'
            },
            'shape': 'box',
            'font': {'color': '#ffffff', 'size': 16, 'bold': True}
        })
        
        # Location tables to scan
        loc_tables = {
            'open_world_zones': {'name': 'Зона', 'color': '#06b6d4', 'border': '#0891b2'},      # Cyan
            'dungeons': {'name': 'Подземелье', 'color': '#f43f5e', 'border': '#be123c'},          # Crimson
            'raids': {'name': 'Рейд', 'color': '#8b5cf6', 'border': '#6d28d9'},                 # Purple
            'arenas': {'name': 'Арена', 'color': '#f59e0b', 'border': '#b45309'},               # Amber
            'instances': {'name': 'Инстанс', 'color': '#3b82f6', 'border': '#1d4ed8'}            # Blue
        }
        
        for t_name, info in loc_tables.items():
            if t_name not in tables:
                continue
                
            cursor.execute(f"SELECT id, label, payload_json FROM {t_name}")
            rows = cursor.fetchall()
            
            for row in rows:
                payload = {}
                if row['payload_json']:
                    try:
                        payload = json.loads(row['payload_json'])
                    except Exception:
                        pass
                
                # Fetch name and description from payload, fallback to label
                name = payload.get('name') or row['label'] or f"{info['name']} #{row['id']}"
                desc = payload.get('description', '')
                
                # Dynamic tooltip based on available payload fields
                tooltip = f"<b>Тип:</b> {info['name']}<br>" \
                          f"<b>Название:</b> {name}<br>"
                
                if desc:
                    tooltip += f"<b>Описание:</b> {desc}<br>"
                    
                if 'difficulty' in payload:
                    tooltip += f"<b>Сложность:</b> {payload['difficulty']}<br>"
                if 'min_level' in payload:
                    tooltip += f"<b>Уровень:</b> {payload['min_level']}"
                    if 'max_level' in payload:
                        tooltip += f"-{payload['max_level']}"
                    tooltip += "<br>"
                if 'max_players' in payload:
                    tooltip += f"<b>Игроков:</b> {payload['max_players']}<br>"
                    
                node_id = f"loc_{t_name}_{row['id']}"
                
                nodes.append({
                    'id': node_id,
                    'label': name,
                    'title': tooltip,
                    'color': {
                        'background': info['color'],
                        'border': info['border']
                    },
                    'shape': 'dot',
                    'size': 15
                })
                
                # Connect to root World node
                edges.append({
                    'from': 'world_1',
                    'to': node_id,
                    'arrows': 'to',
                    'color': info['color'],
                    'width': 2
                })
                
        conn.close()
    except Exception as e:
        print(f"Error building locations graph: {e}")
        
    return {'nodes': nodes, 'edges': edges}

def get_quests_graph():
    nodes = []
    edges = []
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in cursor.fetchall()}
        
        quests = []
        if 'quests' in tables:
            cursor.execute("SELECT id, label, payload_json FROM quests")
            quests = [dict(row) for row in cursor.fetchall()]
            
        quest_chains = []
        if 'quest_chains' in tables:
            cursor.execute("SELECT id, label, payload_json FROM quest_chains")
            quest_chains = [dict(row) for row in cursor.fetchall()]
            
        quest_nodes = []
        if 'quest_nodes' in tables:
            cursor.execute("SELECT id, label, payload_json FROM quest_nodes")
            quest_nodes = [dict(row) for row in cursor.fetchall()]
            
        prereqs = []
        if 'quest_prerequisites' in tables:
            cursor.execute("SELECT id, payload_json FROM quest_prerequisites")
            prereqs = [dict(row) for row in cursor.fetchall()]
            
        conn.close()
        
        quest_map = {}
        for q in quests:
            payload = {}
            if q.get('payload_json'):
                try:
                    payload = json.loads(q['payload_json'])
                except Exception:
                    pass
            q_name = payload.get('name', q['label'])
            status = payload.get('status', 'not_started')
            tooltip = f"<b>Квест: {q_name}</b><br>Статус: {status}"
            
            nodes.append({
                'id': f"quest_{q['id']}",
                'label': q_name,
                'title': tooltip,
                'shape': 'box',
                'color': {
                    'background': '#f59e0b',
                    'border': '#b45309'
                },
                'font': {'color': '#111827', 'size': 14, 'bold': True}
            })
            quest_map[q['id']] = q_name
            
        # Build quest <-> chain linkage.
        # Prefer an explicit `quest_id` in the chain payload, but fall back to
        # matching by id (quest.id == quest_chains.id) since the schema uses
        # shared identifiers and many chains don't carry a quest_id field.
        chain_to_quest = {}
        for qc in quest_chains:
            payload = {}
            if qc.get('payload_json'):
                try:
                    payload = json.loads(qc['payload_json'])
                except Exception:
                    pass
            quest_id = payload.get('quest_id') or qc['id']
            chain_to_quest[qc['id']] = quest_id

        # Map each quest node to its parent quest via quest_chain_id (authoritative,
        # present on every node) -> chain -> quest. Fall back to the chain's
        # quest_node_ids list for nodes that don't carry quest_chain_id.
        node_to_quest_map = {}
        for qn in quest_nodes:
            payload = {}
            if qn.get('payload_json'):
                try:
                    payload = json.loads(qn['payload_json'])
                except Exception:
                    pass
            chain_id = payload.get('quest_chain_id')
            if chain_id is not None and chain_id in chain_to_quest:
                node_to_quest_map[qn['id']] = chain_to_quest[chain_id]
        for qc in quest_chains:
            payload = {}
            if qc.get('payload_json'):
                try:
                    payload = json.loads(qc['payload_json'])
                except Exception:
                    pass
            quest_id = chain_to_quest.get(qc['id'])
            node_ids = payload.get('quest_node_ids', [])
            if quest_id and isinstance(node_ids, list):
                for nid in node_ids:
                    node_to_quest_map.setdefault(nid, quest_id)

        node_id_list = set()
        # Remember each node's chain and position so we can sequence nodes
        # within a chain even when quest_node_ids is incomplete.
        node_chain = {}
        node_position = {}
        for qn in quest_nodes:
            nid = qn['id']
            node_id_list.add(nid)
            payload = {}
            if qn.get('payload_json'):
                try:
                    payload = json.loads(qn['payload_json'])
                except Exception:
                    pass
            obj_ids = payload.get('objective_ids', [])
            tooltip = f"<b>Шаг: {qn['label']}</b><br>ID: {nid}<br>Цели: {obj_ids}"

            nodes.append({
                'id': f"node_{nid}",
                'label': qn['label'],
                'title': tooltip,
                'shape': 'dot',
                'size': 15,
                'color': {
                    'background': '#06b6d4',
                    'border': '#0891b2'
                }
            })

            node_chain[nid] = payload.get('quest_chain_id')
            node_position[nid] = payload.get('position')

            parent_quest_id = node_to_quest_map.get(nid)
            if parent_quest_id:
                edges.append({
                    'from': f"quest_{parent_quest_id}",
                    'to': f"node_{nid}",
                    'arrows': 'to',
                    'color': '#d97706',
                    'dashes': True,
                    'width': 1.5
                })

        # Sequence nodes within a chain. Prefer the explicit quest_node_ids
        # order from the chain payload; otherwise fall back to ordering nodes
        # that share the same quest_chain_id by their id.
        for qc in quest_chains:
            payload = {}
            if qc.get('payload_json'):
                try:
                    payload = json.loads(qc['payload_json'])
                except Exception:
                    pass
            node_ids = payload.get('quest_node_ids', [])
            if not isinstance(node_ids, list) or len(node_ids) < 2:
                # Reconstruct the chain from nodes that reference it directly.
                chain_id = qc['id']
                node_ids = sorted(
                    [nid for nid, cid in node_chain.items() if cid == chain_id and nid in node_id_list]
                )
            if len(node_ids) > 1:
                for i in range(len(node_ids) - 1):
                    n_from = node_ids[i]
                    n_to = node_ids[i+1]
                    if n_from in node_id_list and n_to in node_id_list:
                        edges.append({
                            'from': f"node_{n_from}",
                            'to': f"node_{n_to}",
                            'arrows': 'to',
                            'color': '#06b6d4',
                            'width': 2.5
                        })
                        
        prereqs_map = {}
        for pr in prereqs:
            try:
                payload = json.loads(pr['payload_json'])
                reqs = payload.get('required_quest_ids', [])
                if isinstance(reqs, list):
                    prereqs_map[pr['id']] = reqs
            except Exception:
                pass
                
        for qn in quest_nodes:
            nid = qn['id']
            payload = {}
            if qn.get('payload_json'):
                try:
                    payload = json.loads(qn['payload_json'])
                except Exception:
                    pass
            pr_ids = payload.get('prerequisite_ids', [])
            if isinstance(pr_ids, list):
                for prid in pr_ids:
                    req_quests = prereqs_map.get(prid, [])
                    for req_qid in req_quests:
                        edges.append({
                            'from': f"quest_{req_qid}",
                            'to': f"node_{nid}",
                            'arrows': 'to',
                            'color': '#ef4444',
                            'dashes': [5, 5],
                            'width': 1.5,
                            'label': 'требует'
                        })
                        
    except Exception as e:
        print(f"Error building quest graph: {e}")
        
    return {'nodes': nodes, 'edges': edges}

def get_future_graphs_todo():
    """
    Parses docs/FUTURE_GRAPHS_TODO.md and returns a structured list of
    dictionaries representing the PLANNED (not yet implemented) graph
    visualizations.

    Supports two document layouts:
      - Legacy: top-level `## N. Title` sections.
      - Current: a single `## 📋 Планируемые графы (кандидаты)` section whose
        subsections use `### A. Title` / `### B. Title` headings, optionally
        grouped under `### 🥇/🥈/🥉 Priority` markers.
    The "Реализованные графы" and "Принципы реализации" sections are skipped.
    """
    todo_path = os.path.join("docs", "FUTURE_GRAPHS_TODO.md")
    if not os.path.exists(todo_path):
        return []

    try:
        with open(todo_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {todo_path}: {e}")
        return []

    import re

    # Sections that are NOT planned graphs.
    skip_prefixes = (
        "Реализованные графы",
        "Принципы реализации",
        "Планируемые графы",  # wrapper section; its real items live in ###
    )

    def parse_block(block):
        """Parse a heading + bullet block into a todo item dict."""
        lines = block.strip().split("\n")
        title_line = lines[0].strip()
        # Strip any leading 'A. ' / '1. ' prefix and leading emoji group.
        title_match = re.match(r'^(?:[A-Z\d]+\.|###\s+)?\s*(.*)', title_line)
        title = title_match.group(1).strip() if title_match else title_line
        title = title.lstrip('#').strip()

        goal, tables, benefit = "", "", ""
        connections = []
        in_connections = False

        for line in lines[1:]:
            s = line.strip()
            if not s:
                continue
            if s.startswith("- **Цель**"):
                goal = s.split(":", 1)[1].strip() if ":" in s else s
                in_connections = False
            elif s.startswith("- **Таблицы**"):
                tables = s.split(":", 1)[1].strip() if ":" in s else s
                in_connections = False
            elif s.startswith("- **Связи**"):
                in_connections = True
            elif s.startswith("- **Польза**"):
                benefit = s.split(":", 1)[1].strip() if ":" in s else s
                in_connections = False
            elif in_connections and (s.startswith("-") or s.startswith("*") or line.startswith("  ")):
                connections.append(s.lstrip("-* ").strip())
        return {
            'title': title,
            'goal': goal,
            'tables': tables,
            'connections': connections,
            'benefit': benefit
        }

    todo_items = []

    # Try the current layout first: #### candidate subsections inside the
    # planned section. Priority group markers use ###, candidates use ####.
    planned_match = re.search(
        r'##\s+📋?\s*Планируемые графы.*?(?=\n##\s+|\Z)',
        content, flags=re.S
    )
    if planned_match:
        planned_body = planned_match.group(0)
        # Split on #### headings (the A./B./C... candidates).
        sub_blocks = re.split(r'\n####\s+', planned_body)
        for block in sub_blocks:
            block = block.strip()
            if not block:
                continue
            # A real candidate has a "- **Цель**" or "- **Таблицы**" line.
            if "**Цель**" in block or "**Таблицы**" in block:
                todo_items.append(parse_block(block))

    # Fallback / supplement: legacy top-level ## sections that look like graphs.
    if not todo_items:
        sections = re.split(r'\n##\s+', content)
        for section in sections:
            if not section.strip() or section.startswith("#"):
                continue
            title_line = section.split("\n", 1)[0].strip()
            if any(title_line.startswith(p) for p in skip_prefixes):
                continue
            if "**Цель**" in section or "**Таблицы**" in section:
                todo_items.append(parse_block(section))

    return todo_items

def get_story_branches_graph():
    nodes = []
    edges = []
    
    # Track edge endpoints to avoid duplicates from redundant branch_points
    # and overlapping keyword matches.
    seen_edges = set()
    def add_edge(from_id, to_id, color, width=1.5, label=None, dashes=False):
        key = (from_id, to_id, label)
        if key in seen_edges:
            return
        seen_edges.add(key)
        edge = {
            'from': from_id,
            'to': to_id,
            'arrows': 'to',
            'color': color,
            'width': width
        }
        if dashes:
            edge['dashes'] = True
        if label:
            edge['label'] = label
            edge['font'] = {'align': 'middle', 'color': '#9ca3af', 'size': 9, 'face': 'Inter'}
        edges.append(edge)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in cursor.fetchall()}
        
        stories = []
        if 'stories' in tables:
            cursor.execute("SELECT id, name, description FROM stories")
            stories = [dict(row) for row in cursor.fetchall()]

        storylines = []
        if 'storylines' in tables:
            cursor.execute("SELECT id, label, payload_json FROM storylines")
            storylines = [dict(row) for row in cursor.fetchall()]

        choices = []
        if 'choices' in tables:
            cursor.execute("SELECT id, label, payload_json FROM choices")
            choices = [dict(row) for row in cursor.fetchall()]

        consequences = []
        if 'consequences' in tables:
            cursor.execute("SELECT id, label, payload_json FROM consequences")
            consequences = [dict(row) for row in cursor.fetchall()]

        plot_branches = []
        if 'plot_branches' in tables:
            cursor.execute("SELECT id, label, payload_json FROM plot_branches")
            plot_branches = [dict(row) for row in cursor.fetchall()]

        endings = []
        if 'endings' in tables:
            cursor.execute("SELECT id, label, payload_json FROM endings")
            endings = [dict(row) for row in cursor.fetchall()]

        branch_points = []
        if 'branch_points' in tables:
            cursor.execute("SELECT id, label, payload_json FROM branch_points")
            branch_points = [dict(row) for row in cursor.fetchall()]

        epilogues = []
        if 'epilogues' in tables:
            cursor.execute("SELECT id, title, description, epilogue_type, trigger_condition FROM epilogues")
            epilogues = [dict(row) for row in cursor.fetchall()]

        conn.close()

        # Helper to parse a payload_json blob.
        def parse_payload(row):
            if not row.get('payload_json'):
                return {}
            try:
                return json.loads(row['payload_json'])
            except Exception:
                return {}

        # ---------- Story nodes ----------
        for s in stories:
            nodes.append({
                'id': f"story_{s['id']}",
                'label': s['name'],
                'title': f"<b>Сюжет: {s['name']}</b><br>{s.get('description') or ''}",
                'color': {
                    'background': '#3b82f6', # Blue
                    'border': '#1d4ed8'
                },
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 14, 'bold': True}
            })

        # ---------- Storyline (Сюжетный шаг) nodes ----------
        # Storylines are the high-level narrative beats that "provide choices".
        for sl in storylines:
            payload = parse_payload(sl)
            name = payload.get('name') or sl['label']
            desc = payload.get('description', '')
            sl_type = payload.get('storyline_type', '')
            tooltip = f"<b>Сюжетная линия: {name}</b>"
            if sl_type:
                tooltip += f" ({sl_type})"
            tooltip += f"<br>{desc}"

            nodes.append({
                'id': f"storyline_{sl['id']}",
                'label': name,
                'title': tooltip,
                'color': {
                    'background': '#0ea5e9', # Sky blue — distinct from Story
                    'border': '#0369a1'
                },
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 13}
            })

        # ---------- Choice nodes ----------
        # "Сюжетный шаг ➔ предоставляет выбор ➔ Choice Node"
        for c in choices:
            payload = parse_payload(c)
            prompt = payload.get('prompt') or c['label']
            options = payload.get('options', [])
            opt_str = "<br>".join([f"- {opt}" for opt in options]) or '—'
            tooltip = f"<b>Выбор:</b> {prompt}<br><b>Варианты:</b><br>{opt_str}"

            nodes.append({
                'id': f"choice_{c['id']}",
                'label': prompt[:30] + '…' if len(prompt) > 30 else prompt,
                'title': tooltip,
                'color': {
                    'background': '#f59e0b', # Amber
                    'border': '#b45309'
                },
                'shape': 'dot',
                'size': 15
            })

            # Story -> Choice ("Story offers this choice").
            story_id = payload.get('story_id')
            if story_id:
                add_edge(f"story_{story_id}", f"choice_{c['id']}", '#f59e0b',
                         width=1.5, label='выбор')

        # ---------- Consequence nodes ----------
        # "Choice Node ➔ приводит к последствиям ➔ Consequence"
        consequence_choice = {}  # consequence_id -> triggering choice_id
        for con in consequences:
            payload = parse_payload(con)
            desc = payload.get('description') or con['label']
            con_type = payload.get('consequence_type', '')
            severity = payload.get('severity', '')
            tooltip = f"<b>Последствие:</b> {desc}"
            if con_type:
                tooltip += f"<br><b>Тип:</b> {con_type}"
            if severity:
                tooltip += f"<br><b>Серьёзность:</b> {severity}"

            nodes.append({
                'id': f"consequence_{con['id']}",
                'label': desc[:30] + '…' if len(desc) > 30 else desc,
                'title': tooltip,
                'color': {
                    'background': '#ec4899', # Pink
                    'border': '#be185d'
                },
                'shape': 'dot',
                'size': 12
            })

            # Choice -> Consequence.
            trigger_choice_id = payload.get('trigger_choice_id')
            if trigger_choice_id:
                consequence_choice[con['id']] = trigger_choice_id
                add_edge(f"choice_{trigger_choice_id}", f"consequence_{con['id']}",
                         '#ec4899', width=1.5)

        # ---------- Plot Branch nodes ----------
        # "Consequence ➔ разветвляет историю ➔ Сюжетный шаг"
        # Each plot branch carries an origin_branch_point_id pointing at the
        # branch_point that spawned it; the branch_point in turn carries the
        # choice_id. We use that chain for Consequence -> Plot Branch links.
        for pb in plot_branches:
            payload = parse_payload(pb)
            name = payload.get('name') or pb['label']
            desc = payload.get('description', '')
            b_type = payload.get('branch_type', '')
            tooltip = f"<b>Сюжетная ветка: {name}</b>"
            if b_type:
                tooltip += f" ({b_type})"
            tooltip += f"<br>{desc}"

            nodes.append({
                'id': f"branch_{pb['id']}",
                'label': name,
                'title': tooltip,
                'color': {
                    'background': '#8b5cf6', # Purple
                    'border': '#6d28d9'
                },
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })

        # ---------- Ending nodes ----------
        # Endings appear as star nodes; type drives color.
        ending_epilogue = {}  # ending_id -> epilogue_id (real FK)
        for e in endings:
            payload = parse_payload(e)
            title = payload.get('title') or e['label']
            desc = payload.get('description', '')
            e_type = payload.get('ending_type', 'neutral')

            bg_color = '#9ca3af' # gray (neutral)
            border_color = '#4b5563'
            if e_type == 'good':
                bg_color = '#10b981' # green
                border_color = '#047857'
            elif e_type == 'bad':
                bg_color = '#ef4444' # red
                border_color = '#b91c1c'

            tooltip = f"<b>Финал: {title}</b> ({e_type})<br>{desc}"

            nodes.append({
                'id': f"ending_{e['id']}",
                'label': title,
                'title': tooltip,
                'color': {
                    'background': bg_color,
                    'border': border_color
                },
                'shape': 'star',
                'size': 20
            })

            # Remember the real epilogue FK for later edge creation.
            epi_id = payload.get('epilogue_id')
            if epi_id is not None:
                ending_epilogue[e['id']] = epi_id

        # ---------- Epilogue nodes ----------
        # Endings reference epilogues via a real payload FK (epilogue_id).
        epilogue_ids = {ep['id'] for ep in epilogues}
        for ep in epilogues:
            epi_type = ep.get('epilogue_type', '')
            tooltip = f"<b>Эпилог: {ep['title']}</b>"
            if epi_type:
                tooltip += f" ({epi_type})"
            tooltip += f"<br>{ep.get('description') or ''}"

            nodes.append({
                'id': f"epilogue_{ep['id']}",
                'label': ep['title'],
                'title': tooltip,
                'color': {
                    'background': '#14b8a6', # Teal — distinct from endings
                    'border': '#0f766e'
                },
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })

        # ---------- Structural edges (real DB fields only, no text matching) ----------

        story_ids = [s['id'] for s in stories]

        # Storyline -> Story: storylines live in the same world as a story.
        # There is no direct storyline->story FK, so we attach a storyline to a
        # story sharing its world_id; if none, to the first story as a hub.
        story_by_world = {}
        for s in stories:
            story_by_world.setdefault(s.get('world_id'), s['id'])
        for sl in storylines:
            payload = parse_payload(sl)
            sl_story_id = story_by_world.get(payload.get('world_id')) or (story_ids[0] if story_ids else None)
            if sl_story_id:
                add_edge(f"storyline_{sl['id']}", f"story_{sl_story_id}",
                         '#0ea5e9', width=1.5, dashes=True, label='часть')

        # Story -> Choice ("story offers this choice") is emitted inline in the
        # Choice loop above via choices.story_id.

        # Choice -> Consequence is emitted inline in the Consequence loop above
        # via consequences.trigger_choice_id.

        # Choice <-> Plot Branch via branch_points (choice_id + branch_ids).
        # The same (branch, choice) pair may be referenced by several
        # branch_points, so add_edge dedups.
        branch_to_choices = {}  # branch_id -> [choice_id, ...]
        for bp in branch_points:
            payload = parse_payload(bp)
            choice_id = payload.get('choice_id')
            branch_ids = payload.get('branch_ids', [])
            if choice_id and isinstance(branch_ids, list):
                for bid in branch_ids:
                    branch_to_choices.setdefault(bid, []).append(choice_id)
                    # Choice -> Plot Branch ("this choice opens a branch").
                    add_edge(f"choice_{choice_id}", f"branch_{bid}",
                             '#d97706', width=1.5, label='открывает')

        # Consequence -> Plot Branch: link a consequence to the branches opened
        # by the same choice that triggered it. Walks the real FK chain:
        # consequence.trigger_choice_id -> branch_point.choice_id -> branch_ids.
        for con_id, trig_choice_id in consequence_choice.items():
            for bid, choice_ids in branch_to_choices.items():
                if trig_choice_id in choice_ids:
                    add_edge(f"consequence_{con_id}", f"branch_{bid}",
                             '#8b5cf6', width=2, dashes=True, label='разветвляет')

        # Ending -> Epilogue via endings.epilogue_id (real payload FK).
        for e_id, epi_id in ending_epilogue.items():
            if epi_id in epilogue_ids:
                add_edge(f"ending_{e_id}", f"epilogue_{epi_id}",
                         '#14b8a6', width=1.5, dashes=True, label='эпилог')

        # Note: there is NO structural consequence->ending link in the schema.
        # The only place endings relate to choices/branches is the free-text
        # `conditions` array, which is not a reliable id reference. We therefore
        # do not synthesise that edge — endings hang off their epilogue and the
        # campaign instead, which are the real relationships the data encodes.

        # Backbone sequence of plot branches ordered by id — gives the tree a
        # readable spine when no explicit ordering field exists.
        if len(plot_branches) > 1:
            sorted_branches = sorted(plot_branches, key=lambda x: x['id'])
            for i in range(len(sorted_branches) - 1):
                add_edge(f"branch_{sorted_branches[i]['id']}",
                         f"branch_{sorted_branches[i+1]['id']}",
                         '#8b5cf6', width=2)
                
    except Exception as e:
        print(f"Error building story branches graph: {e}")
        
    return {'nodes': nodes, 'edges': edges}

def get_timeline_graph():
    nodes = []
    edges = []
    
    try:
        from datetime import datetime
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        
        # 1. Defensive Table Check and Seeding
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='eras'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS eras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    color_code TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
        # Seed if empty (handles partial creation from a failed earlier run)
        cursor.execute("SELECT COUNT(*) FROM eras")
        if cursor.fetchone()[0] == 0:
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO eras (tenant_id, world_id, name, description, start_date, end_date, color_code, created_at, updated_at)
                VALUES 
                (1, 1, 'Первая Эпоха: Эпоха Творения', 'Период создания Горнила Эфира и первых великих кузнецов.', '1000-01-01', '1500-12-31', '#10b981', ?, ?),
                (1, 1, 'Вторая Эпоха: Расцвет Королевств', 'Объединение земель и создание трех великих королевств.', '1501-01-01', '2000-12-31', '#3b82f6', ?, ?),
                (1, 1, 'Третья Эпоха: Нашествие Тьмы', 'Современный период, характеризующийся пробуждением сил тьмы и тёмными ритуалами.', '2001-01-01', NULL, '#ef4444', ?, ?)
            """, (now, now, now, now, now, now))
            
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='era_transitions'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS era_transitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    world_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    from_era_id INTEGER NOT NULL,
                    to_era_id INTEGER NOT NULL,
                    transition_type TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
        # Seed if empty
        cursor.execute("SELECT COUNT(*) FROM era_transitions")
        if cursor.fetchone()[0] == 0:
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO era_transitions (tenant_id, world_id, name, description, from_era_id, to_era_id, transition_type, created_at, updated_at)
                VALUES 
                (1, 1, 'Великий Катаклизм', 'Переход от Эпохи Творения к Расцвету Королевств из-за нестабильности Горнила.', 1, 2, 'catastrophic', ?, ?),
                (1, 1, 'Затмение Светила', 'Тёмный ритуал, положивший начало нашествию Тьмы.', 2, 3, 'magical', ?, ?)
            """, (now, now, now, now))
            
        conn.commit()
        
        # 2. Fetch Data
        cursor.execute("SELECT id, name, description, start_date, end_date, color_code FROM eras")
        eras = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT id, name, description, from_era_id, to_era_id, transition_type FROM era_transitions")
        transitions = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in cursor.fetchall()}
        
        events = []
        if 'events' in tables:
            cursor.execute("SELECT id, name, description, start_date FROM events")
            events = [dict(row) for row in cursor.fetchall()]
            
        world_events = []
        if 'world_events' in tables:
            cursor.execute("SELECT id, label, payload_json FROM world_events")
            world_events = [dict(row) for row in cursor.fetchall()]
            
        conn.close()
        
        # 3. Add Era nodes
        for era in eras:
            s_date = era['start_date'] or 'N/A'
            e_date = era['end_date'] or 'Н.В.'
            tooltip = f"<b>Эпоха: {era['name']}</b><br>{era['description']}<br><b>Период:</b> {s_date} - {e_date}"
            
            nodes.append({
                'id': f"era_{era['id']}",
                'label': era['name'],
                'title': tooltip,
                'color': {
                    'background': era['color_code'] or '#10b981',
                    'border': '#1e293b'
                },
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 14, 'bold': True}
            })
            
        # 4. Add Transition nodes
        for t in transitions:
            tooltip = f"<b>Переход: {t['name']}</b> ({t['transition_type']})<br>{t['description']}"
            nodes.append({
                'id': f"transition_{t['id']}",
                'label': t['name'],
                'title': tooltip,
                'color': {
                    'background': '#8b5cf6', # Purple
                    'border': '#6d28d9'
                },
                'shape': 'diamond',
                'size': 15
            })
            
            # Connect Era -> Transition -> Era
            edges.append({
                'from': f"era_{t['from_era_id']}",
                'to': f"transition_{t['id']}",
                'arrows': 'to',
                'color': '#8b5cf6',
                'width': 2
            })
            edges.append({
                'from': f"transition_{t['id']}",
                'to': f"era_{t['to_era_id']}",
                'arrows': 'to',
                'color': '#8b5cf6',
                'width': 2
            })
            
        # 5. Add Event nodes and link to Eras
        for ev in events:
            date_str = ev['start_date']
            tooltip = f"<b>Событие: {ev['name']}</b><br>{ev['description']}<br><b>Дата:</b> {date_str}"
            
            nodes.append({
                'id': f"event_{ev['id']}",
                'label': ev['name'],
                'title': tooltip,
                'color': {
                    'background': '#f59e0b', # Amber
                    'border': '#b45309'
                },
                'shape': 'dot',
                'size': 12
            })
            
            # Match with Era
            matched_era_id = None
            for era in eras:
                era_start = era['start_date']
                era_end = era['end_date']
                if date_str >= era_start:
                    if not era_end or date_str <= era_end:
                        matched_era_id = era['id']
                        break
            if not matched_era_id:
                matched_era_id = 3
                
            edges.append({
                'from': f"event_{ev['id']}",
                'to': f"era_{matched_era_id}",
                'arrows': 'to',
                'color': '#f59e0b',
                'dashes': True,
                'width': 1.5,
                'label': 'произошло',
                'font': {'align': 'middle', 'color': '#9ca3af', 'size': 8, 'face': 'Inter'}
            })
            
        # 6. Add World Event nodes and link to Eras
        for wev in world_events:
            payload = {}
            if wev.get('payload_json'):
                try:
                    payload = json.loads(wev['payload_json'])
                except: pass
            name = payload.get('name') or wev['label']
            desc = payload.get('description', '')
            date_str = payload.get('start_date') or ''
            
            tooltip = f"<b>Мировое событие: {name}</b><br>{desc}"
            if date_str:
                tooltip += f"<br><b>Дата:</b> {date_str}"
                
            nodes.append({
                'id': f"wevent_{wev['id']}",
                'label': name,
                'title': tooltip,
                'color': {
                    'background': '#06b6d4', # Cyan
                    'border': '#0891b2'
                },
                'shape': 'dot',
                'size': 12
            })
            
            # Match with Era
            matched_era_id = None
            if date_str:
                for era in eras:
                    era_start = era['start_date']
                    era_end = era['end_date']
                    if date_str >= era_start:
                        if not era_end or date_str <= era_end:
                            matched_era_id = era['id']
                            break
            if not matched_era_id:
                matched_era_id = 3
                
            edges.append({
                'from': f"wevent_{wev['id']}",
                'to': f"era_{matched_era_id}",
                'arrows': 'to',
                'color': '#06b6d4',
                'dashes': True,
                'width': 1.5,
                'label': 'произошло',
                'font': {'align': 'middle', 'color': '#9ca3af', 'size': 8, 'face': 'Inter'}
            })
            
    except Exception as e:
        print(f"Error building timeline graph: {e}")
        
    return {'nodes': nodes, 'edges': edges}


def _new_edge_set():
    """Return (add_edge, seen) helper bound to a fresh edge list."""
    seen = set()
    edges = []
    def add_edge(from_id, to_id, color, width=1.5, label=None, dashes=False):
        key = (from_id, to_id, label)
        if key in seen:
            return
        seen.add(key)
        edge = {'from': from_id, 'to': to_id, 'arrows': 'to', 'color': color, 'width': width}
        if dashes:
            edge['dashes'] = True
        if label:
            edge['label'] = label
            edge['font'] = {'align': 'middle', 'color': '#9ca3af', 'size': 9, 'face': 'Inter'}
        edges.append(edge)
    return add_edge, edges


def get_factions_graph():
    """Faction diplomacy & hierarchy graph.

    Built only from real DB fields. Since the schema has no `factions` /
    `faction_memberships` tables, factions are derived from the data that
    actually encodes political structure:

      - `wars` rows name aggressor/defender factions (string names) and
        represent the 'война/вражда' (red) edges from the spec.
      - `character_relationships` rows (`character_from_id`, `character_to_id`,
        `relationship_type`, `relationship_level`) encode inter-character
        diplomacy directly: 'ally'/'friend' -> green, 'rival'/'enemy' -> red.
      - `characters.role` / `characters.status` and `ranks` provide hierarchy
        context; characters linked by a shared role/status form a loose
        'member of the same group' cluster.
    """
    nodes = []
    add_edge, edges = _new_edge_set()

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in cursor.fetchall()}

        def parse(row):
            pj = row.get('payload_json') if isinstance(row, dict) else row['payload_json']
            if not pj:
                return {}
            try:
                return json.loads(pj)
            except Exception:
                return {}

        # ---------- Faction nodes (derived from wars) ----------
        # The DB has no factions table, so the only authoritative source of
        # faction identity is the `wars` payload (aggressor_name / defender_name).
        # Each unique name becomes a faction node.
        faction_ids = {}  # name -> node id
        faction_names = []
        wars = []
        if 'wars' in tables:
            cursor.execute("SELECT id, label, payload_json FROM wars")
            for row in cursor.fetchall():
                payload = parse(row)
                wars.append({
                    'id': row['id'],
                    'name': payload.get('name') or row['label'],
                    'aggressor': payload.get('aggressor_name'),
                    'defender': payload.get('defender_name'),
                    'is_active': payload.get('is_active', True),
                    'war_type': payload.get('war_type', ''),
                    'victor': payload.get('victor_name'),
                    'region': payload.get('conflict_region_name'),
                })
                for fname in (payload.get('aggressor_name'), payload.get('defender_name'), payload.get('victor_name')):
                    if fname and fname not in faction_ids:
                        faction_ids[fname] = f"faction_{len(faction_ids)+1}"
                        faction_names.append(fname)

        for fname in faction_names:
            nodes.append({
                'id': faction_ids[fname],
                'label': fname,
                'title': f"<b>Фракция: {fname}</b>",
                'color': {'background': '#6366f1', 'border': '#4338ca'},  # Indigo
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 14, 'bold': True}
            })

        # ---------- War edges (red: вражда) ----------
        for w in wars:
            aggr = faction_ids.get(w['aggressor'])
            defn = faction_ids.get(w['defender'])
            if aggr and defn and aggr != defn:
                tooltip_lbl = 'война'
                if w.get('war_type'):
                    tooltip_lbl += f" ({w['war_type']})"
                add_edge(aggr, defn, '#ef4444', width=3, label=tooltip_lbl)
                # Note: wars are not mutual-alliance, so only one directed edge.

        # ---------- Characters ----------
        characters = []
        if 'characters' in tables:
            cursor.execute("SELECT id, name, role, status FROM characters")
            characters = [dict(row) for row in cursor.fetchall()]

        for ch in characters:
            tooltip = f"<b>Персонаж: {ch['name']}</b>"
            if ch.get('role'):
                tooltip += f"<br><b>Роль:</b> {ch['role']}"
            if ch.get('status'):
                tooltip += f"<br><b>Статус:</b> {ch['status']}"
            nodes.append({
                'id': f"char_{ch['id']}",
                'label': ch['name'],
                'title': tooltip,
                'color': {'background': '#f59e0b', 'border': '#b45309'},  # Amber
                'shape': 'dot',
                'size': 14
            })

        # ---------- Character relationships (green: ally, red: enemy) ----------
        if 'character_relationships' in tables:
            cursor.execute("""SELECT character_from_id, character_to_id,
                                     relationship_type, relationship_level, description
                              FROM character_relationships""")
            for row in cursor.fetchall():
                rtype = (row['relationship_type'] or '').lower()
                level = row['relationship_level']
                color = '#9ca3af'
                label = row['relationship_type'] or 'связь'
                if rtype in ('ally', 'friend', 'allied', 'friendship', 'bond', 'companion'):
                    color = '#10b981'  # green
                    label = 'альянс'
                elif rtype in ('rival', 'enemy', 'rivalry', 'nemesis', 'foe', 'hostile'):
                    color = '#ef4444'  # red
                    label = 'вражда'
                elif rtype in ('mentor', 'teacher', 'student', 'family', 'parent', 'child', 'sibling'):
                    color = '#3b82f6'  # blue (hierarchy / kinship)
                    label = row['relationship_type']
                add_edge(f"char_{row['character_from_id']}",
                         f"char_{row['character_to_id']}",
                         color, width=2, label=label,
                         dashes=(rtype in ('rival', 'enemy', 'rivalry', 'nemesis', 'foe', 'hostile')))

        # ---------- Ranks as hierarchy context ----------
        # Characters with the same role/status form a soft cluster via shared
        # rank nodes when ranks carry matching data; otherwise ranks appear as
        # standalone hierarchy context nodes.
        if 'ranks' in tables:
            cursor.execute("SELECT id, label, payload_json FROM ranks")
            for row in cursor.fetchall():
                payload = parse(row)
                rname = payload.get('name') or row['label']
                nodes.append({
                    'id': f"rank_{row['id']}",
                    'label': f"🎖️ {rname}",
                    'title': f"<b>Ранг: {rname}</b><br>{payload.get('description') or ''}",
                    'color': {'background': '#fbbf24', 'border': '#d97706'},  # Gold
                    'shape': 'diamond',
                    'size': 12
                })

        conn.close()
    except Exception as e:
        print(f"Error building factions graph: {e}")

    return {'nodes': nodes, 'edges': edges}


def get_crafting_graph():
    """Item crafting & recipes graph.

    Built only from real DB fields:
      - `crafting_recipes.ingredients[].item_id` -> the consumed input item
      - `crafting_recipes.result_item_id`        -> the produced item
      - `crafting_recipes.required_blueprint_id` -> the blueprint needed
      - `blueprints.result_item_id`              -> the item a blueprint yields
      - `components.is_craftable`                -> components link to the
        recipe of the same name when one exists (loose, name-based fallback
        only used to surface otherwise orphaned components)
    """
    nodes = []
    add_edge, edges = _new_edge_set()

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in cursor.fetchall()}

        def parse(row):
            if not row.get('payload_json'):
                return {}
            try:
                return json.loads(row['payload_json'])
            except Exception:
                return {}

        # ---------- Load all five entity types ----------
        items = []
        if 'items' in tables:
            cursor.execute("SELECT id, label, payload_json FROM items")
            items = [dict(row) for row in cursor.fetchall()]
        materials = []
        if 'materials' in tables:
            cursor.execute("SELECT id, label, payload_json FROM materials")
            materials = [dict(row) for row in cursor.fetchall()]
        components = []
        if 'components' in tables:
            cursor.execute("SELECT id, label, payload_json FROM components")
            components = [dict(row) for row in cursor.fetchall()]
        recipes = []
        if 'crafting_recipes' in tables:
            cursor.execute("SELECT id, label, payload_json FROM crafting_recipes")
            recipes = [dict(row) for row in cursor.fetchall()]
        blueprints = []
        if 'blueprints' in tables:
            cursor.execute("SELECT id, label, payload_json FROM blueprints")
            blueprints = [dict(row) for row in cursor.fetchall()]

        item_ids = {it['id'] for it in items}
        material_ids = {m['id'] for m in materials}
        component_ids = {co['id'] for co in components}

        # ---------- Item nodes ----------
        for it in items:
            payload = parse(it)
            itype = payload.get('item_type', '')
            rarity = payload.get('rarity', '')
            tooltip = f"<b>Предмет: {payload.get('name') or it['label']}</b>"
            if itype:
                tooltip += f"<br><b>Тип:</b> {itype}"
            if rarity:
                tooltip += f"<br><b>Редкость:</b> {rarity}"
            nodes.append({
                'id': f"item_{it['id']}",
                'label': payload.get('name') or it['label'],
                'title': tooltip,
                'color': {'background': '#10b981', 'border': '#047857'},  # Green
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })

        # ---------- Material nodes ----------
        for m in materials:
            payload = parse(m)
            tooltip = f"<b>Материал: {payload.get('name') or m['label']}</b>"
            if payload.get('rarity'):
                tooltip += f"<br><b>Редкость:</b> {payload['rarity']}"
            if payload.get('material_type'):
                tooltip += f"<br><b>Тип:</b> {payload['material_type']}"
            nodes.append({
                'id': f"material_{m['id']}",
                'label': payload.get('name') or m['label'],
                'title': tooltip,
                'color': {'background': '#f59e0b', 'border': '#b45309'},  # Amber
                'shape': 'dot',
                'size': 12
            })

        # ---------- Component nodes ----------
        for co in components:
            payload = parse(co)
            tooltip = f"<b>Компонент: {payload.get('name') or co['label']}</b>"
            if payload.get('rarity'):
                tooltip += f"<br><b>Редкость:</b> {payload['rarity']}"
            if payload.get('category'):
                tooltip += f"<br><b>Категория:</b> {payload['category']}"
            nodes.append({
                'id': f"component_{co['id']}",
                'label': payload.get('name') or co['label'],
                'title': tooltip,
                'color': {'background': '#8b5cf6', 'border': '#6d28d9'},  # Purple
                'shape': 'triangle',
                'size': 13
            })

        # ---------- Recipe nodes ----------
        for r in recipes:
            payload = parse(r)
            rname = payload.get('name') or r['label']
            difficulty = payload.get('difficulty', '')
            tooltip = f"<b>Рецепт: {rname}</b>"
            if difficulty:
                tooltip += f"<br><b>Сложность:</b> {difficulty}"
            nodes.append({
                'id': f"recipe_{r['id']}",
                'label': f"⚒️ {rname}",
                'title': tooltip,
                'color': {'background': '#06b6d4', 'border': '#0891b2'},  # Cyan
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12, 'bold': True}
            })

        # ---------- Blueprint nodes ----------
        for b in blueprints:
            payload = parse(b)
            bname = payload.get('name') or b['label']
            btype = payload.get('blueprint_type', '')
            rarity = payload.get('rarity', '')
            tooltip = f"<b>Чертёж: {bname}</b>"
            if btype:
                tooltip += f"<br><b>Тип:</b> {btype}"
            if rarity:
                tooltip += f"<br><b>Редкость:</b> {rarity}"
            nodes.append({
                'id': f"blueprint_{b['id']}",
                'label': f"📐 {bname}",
                'title': tooltip,
                'color': {'background': '#ec4899', 'border': '#be185d'},  # Pink
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })

        # ---------- Structural edges ----------

        # Recipe -> consumed input item ("requires"): crafting_recipes.
        # ingredients[].item_id. Note the schema calls them 'item_id' even
        # when they may reference a material in practice; we resolve to
        # whichever entity table actually owns that id.
        def resolve_node_id(eid):
            if eid in item_ids:
                return f"item_{eid}"
            if eid in material_ids:
                return f"material_{eid}"
            if eid in component_ids:
                return f"component_{eid}"
            return None

        for r in recipes:
            payload = parse(r)
            for ing in payload.get('ingredients', []) or []:
                eid = ing.get('item_id') if isinstance(ing, dict) else None
                qty = ing.get('quantity') if isinstance(ing, dict) else None
                if eid is None:
                    continue
                src = resolve_node_id(eid)
                if src:
                    lbl = f"x{qty}" if qty else 'вход'
                    add_edge(src, f"recipe_{r['id']}", '#f59e0b',
                             width=1.5, label=lbl, dashes=True)

            # Recipe -> produced item ("produces"): result_item_id
            result_id = payload.get('result_item_id')
            if result_id is not None:
                tgt = resolve_node_id(result_id)
                if tgt:
                    qty = payload.get('result_quantity', 1)
                    lbl = f"производит x{qty}" if qty and qty > 1 else 'производит'
                    add_edge(f"recipe_{r['id']}", tgt, '#10b981', width=2.5, label=lbl)

            # Recipe -> required blueprint ("needs blueprint"): required_blueprint_id
            bp_id = payload.get('required_blueprint_id')
            if bp_id is not None:
                add_edge(f"blueprint_{bp_id}", f"recipe_{r['id']}", '#ec4899',
                         width=1.5, label='чертёж', dashes=True)

        # Blueprint -> produced item ("produces"): blueprints.result_item_id
        for b in blueprints:
            payload = parse(b)
            result_id = payload.get('result_item_id')
            if result_id is not None:
                tgt = resolve_node_id(result_id)
                if tgt:
                    qty = payload.get('result_quantity', 1)
                    lbl = f"производит x{qty}" if qty and qty > 1 else 'производит'
                    add_edge(f"blueprint_{b['id']}", tgt, '#10b981',
                             width=2, label=lbl, dashes=True)

        conn.close()
    except Exception as e:
        print(f"Error building crafting graph: {e}")

    return {'nodes': nodes, 'edges': edges}


def get_progression_graph():
    """Progression & skill trees graph.

    Built only from real DB fields. All five progression tables (skills,
    talent_trees, perks, attributes, level_ups) share a single structural
    link: `character_id` -> characters. There are no prerequisite_id /
    talent_node_id FKs in the schema, so the spec's 'ability requires base
    skill' edges do not exist in the data and are not synthesised.

    Real edges used:
      - <entity>.character_id -> character ('принадлежит')
      - skills.minimum_level / talent_trees.required_level -> level_up
        ('требует ур. N') when the character's reached level satisfies it.
      - level_ups.notes.major_stat_increases mentioning an attribute by
        display_name -> attribute ('повысил') — the only cross-entity link
        the data encodes, resolved by name match on the attribute's
        display_name/name.
    """
    nodes = []
    add_edge, edges = _new_edge_set()

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in cursor.fetchall()}

        def parse(row):
            pj = row.get('payload_json') if isinstance(row, dict) else row['payload_json']
            if not pj:
                return {}
            try:
                return json.loads(pj)
            except Exception:
                return {}

        # ---------- Load entities ----------
        skills, talent_trees, perks, attributes, level_ups = [], [], [], [], []
        if 'skills' in tables:
            cursor.execute("SELECT id, label, payload_json FROM skills")
            skills = [dict(r) for r in cursor.fetchall()]
        if 'talent_trees' in tables:
            cursor.execute("SELECT id, label, payload_json FROM talent_trees")
            talent_trees = [dict(r) for r in cursor.fetchall()]
        if 'perks' in tables:
            cursor.execute("SELECT id, label, payload_json FROM perks")
            perks = [dict(r) for r in cursor.fetchall()]
        if 'attributes' in tables:
            cursor.execute("SELECT id, label, payload_json FROM attributes")
            attributes = [dict(r) for r in cursor.fetchall()]
        if 'level_ups' in tables:
            cursor.execute("SELECT id, label, payload_json FROM level_ups")
            level_ups = [dict(r) for r in cursor.fetchall()]
        characters = []
        if 'characters' in tables:
            cursor.execute("SELECT id, name, role, status FROM characters")
            characters = [dict(r) for r in cursor.fetchall()]

        char_ids = {c['id'] for c in characters}

        # ---------- Character (root) nodes ----------
        # Only render characters that are actually referenced by progression
        # entities, so the graph stays focused.
        referenced_chars = set()
        for ents in (skills, talent_trees, perks, attributes, level_ups):
            for ent in ents:
                payload = parse(ent)
                cid = payload.get('character_id')
                if cid is not None:
                    referenced_chars.add(cid)
        for ch in characters:
            if ch['id'] not in referenced_chars:
                continue
            tooltip = f"<b>Персонаж: {ch['name']}</b>"
            if ch.get('role'):
                tooltip += f"<br><b>Роль:</b> {ch['role']}"
            if ch.get('status'):
                tooltip += f"<br><b>Статус:</b> {ch['status']}"
            nodes.append({
                'id': f"char_{ch['id']}",
                'label': ch['name'],
                'title': tooltip,
                'color': {'background': '#f59e0b', 'border': '#b45309'},  # Amber
                'shape': 'star',
                'size': 22
            })

        # ---------- Attribute nodes ----------
        attr_name_to_id = {}  # display_name/lower(name) -> node id (for level_up link)
        for a in attributes:
            payload = parse(a)
            name = payload.get('display_name') or payload.get('name') or a['label']
            atype = payload.get('attribute_type', '')
            tooltip = f"<b>Характеристика: {name}</b>"
            if atype:
                tooltip += f"<br><b>Тип:</b> {atype}"
            tooltip += f"<br><b>Значение:</b> {payload.get('current_value', '?')} / {payload.get('maximum_value', '?')}"
            nodes.append({
                'id': f"attribute_{a['id']}",
                'label': name,
                'title': tooltip,
                'color': {'background': '#3b82f6', 'border': '#1d4ed8'},  # Blue
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })
            attr_name_to_id[name.lower()] = f"attribute_{a['id']}"
            # attribute -> character
            cid = payload.get('character_id')
            if cid in char_ids:
                add_edge(f"attribute_{a['id']}", f"char_{cid}",
                         '#3b82f6', width=1.5, label='принадлежит', dashes=True)

        # ---------- Skill nodes ----------
        for s in skills:
            payload = parse(s)
            name = payload.get('name') or s['label']
            stype = payload.get('skill_type', '')
            tooltip = f"<b>Способность: {name}</b>"
            if stype:
                tooltip += f"<br><b>Тип:</b> {stype}"
            tooltip += f"<br><b>Уровень:</b> {payload.get('level', '?')} / {payload.get('max_level', '?')}"
            if payload.get('minimum_level') is not None:
                tooltip += f"<br><b>Требует ур.:</b> {payload['minimum_level']}"
            nodes.append({
                'id': f"skill_{s['id']}",
                'label': f"⚡ {name}",
                'title': tooltip,
                'color': {'background': '#06b6d4', 'border': '#0891b2'},  # Cyan
                'shape': 'dot',
                'size': 16
            })
            cid = payload.get('character_id')
            if cid in char_ids:
                add_edge(f"skill_{s['id']}", f"char_{cid}",
                         '#06b6d4', width=1.5, label='принадлежит', dashes=True)

        # ---------- Talent tree nodes ----------
        for tt in talent_trees:
            payload = parse(tt)
            name = payload.get('name') or tt['label']
            ttype = payload.get('talent_tree_type', '')
            tooltip = f"<b>Дерево талантов: {name}</b>"
            if ttype:
                tooltip += f"<br><b>Тип:</b> {ttype}"
            if payload.get('required_level') is not None:
                tooltip += f"<br><b>Требует ур.:</b> {payload['required_level']}"
            tooltip += f"<br><b>Очки:</b> {payload.get('points_spent', 0)} / {payload.get('total_points', '?')}"
            nodes.append({
                'id': f"talent_tree_{tt['id']}",
                'label': f"🌲 {name}",
                'title': tooltip,
                'color': {'background': '#10b981', 'border': '#047857'},  # Green
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 13, 'bold': True}
            })
            cid = payload.get('character_id')
            if cid in char_ids:
                add_edge(f"talent_tree_{tt['id']}", f"char_{cid}",
                         '#10b981', width=2, label='принадлежит')

        # ---------- Perk nodes ----------
        for p in perks:
            payload = parse(p)
            name = payload.get('name') or p['label']
            ptype = payload.get('perk_type', '')
            source = payload.get('source', '')
            tooltip = f"<b>Перк: {name}</b>"
            if ptype:
                tooltip += f"<br><b>Тип:</b> {ptype}"
            if source:
                tooltip += f"<br><b>Источник:</b> {source}"
            nodes.append({
                'id': f"perk_{p['id']}",
                'label': f"🏅 {name}",
                'title': tooltip,
                'color': {'background': '#fbbf24', 'border': '#d97706'},  # Gold
                'shape': 'diamond',
                'size': 14
            })
            cid = payload.get('character_id')
            if cid in char_ids:
                add_edge(f"perk_{p['id']}", f"char_{cid}",
                         '#fbbf24', width=1.5, label='принадлежит', dashes=True)

        # ---------- Level-up nodes ----------
        # Each level_up is the character reaching a new level. It can satisfy
        # the minimum_level / required_level gates on skills and talent_trees,
        # and it references attributes by name in major_stat_increases.
        for lu in level_ups:
            payload = parse(lu)
            new_lvl = payload.get('new_level')
            old_lvl = payload.get('old_level')
            lu_type = payload.get('level_up_type', '')
            tooltip = f"<b>Повышение уровня: {old_lvl} ➔ {new_lvl}</b>"
            if lu_type:
                tooltip += f"<br><b>Тип:</b> {lu_type}"
            notes = payload.get('notes')
            # `notes` may be a dict, a JSON string, or a Python-literal string
            # ("{'k': 'v'}" with single quotes). Normalise to a dict.
            if isinstance(notes, str):
                try:
                    notes = json.loads(notes)
                except Exception:
                    try:
                        import ast
                        notes = ast.literal_eval(notes)
                    except Exception:
                        notes = {}
            if isinstance(notes, dict):
                increases = notes.get('major_stat_increases', [])
                if increases:
                    tooltip += f"<br><b>Рост статов:</b> {', '.join(map(str, increases))}"
            nodes.append({
                'id': f"level_up_{lu['id']}",
                'label': f"⬆️ ур. {new_lvl}",
                'title': tooltip,
                'color': {'background': '#a855f7', 'border': '#7e22ce'},  # Purple
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })
            cid = payload.get('character_id')
            if cid in char_ids:
                add_edge(f"char_{cid}", f"level_up_{lu['id']}",
                         '#a855f7', width=2, label=f'достиг ур. {new_lvl}')

            # level_up -> skill/talent_tree: 'requires' is satisfied by this
            # level. Draw the edge from the requirement to the level_up that
            # fulfils it, so the spec's 'prerequisite' concept shows up using
            # the only level-based linkage the schema provides.
            if new_lvl is not None:
                for s in skills:
                    sp = parse(s)
                    min_lvl = sp.get('minimum_level')
                    if min_lvl is not None and new_lvl >= min_lvl:
                        add_edge(f"skill_{s['id']}", f"level_up_{lu['id']}",
                                 '#06b6d4', width=1, label=f'требует ур. {min_lvl}',
                                 dashes=True)
                for tt in talent_trees:
                    tp = parse(tt)
                    req_lvl = tp.get('required_level')
                    if req_lvl is not None and new_lvl >= req_lvl:
                        add_edge(f"talent_tree_{tt['id']}", f"level_up_{lu['id']}",
                                 '#10b981', width=1, label=f'требует ур. {req_lvl}',
                                 dashes=True)

            # level_up -> attribute: 'raised' — the only cross-entity link in
            # the data, encoded as text in major_stat_increases. Resolve by
            # matching the attribute's display_name inside the increase text.
            notes_for_match = notes
            if isinstance(notes_for_match, dict):
                for inc in notes_for_match.get('major_stat_increases', []) or []:
                    inc_lower = str(inc).lower()
                    for aname, aid in attr_name_to_id.items():
                        if aname in inc_lower:
                            add_edge(f"level_up_{lu['id']}", aid,
                                     '#3b82f6', width=1.5, label='повысил')
                            break

        conn.close()
    except Exception as e:
        print(f"Error building progression graph: {e}")

    return {'nodes': nodes, 'edges': edges}


