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
    Parses docs/FUTURE_GRAPHS_TODO.md and returns a structured list of dictionaries
    representing the planned graph visualizations.
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
    sections = re.split(r'\n##\s+', content)
    todo_items = []
    
    for section in sections:
        # Ignore intro text
        if not section.strip() or section.startswith("#"):
            continue
            
        lines = section.strip().split("\n")
        title_line = lines[0]
        # Match title: e.g. "1. 🌲 Дерево прокачки и талантов (Progression & Skill Trees)"
        title_match = re.match(r'^\d+\.\s*(.*)', title_line)
        title = title_match.group(1) if title_match else title_line
        
        goal = ""
        tables = ""
        connections = []
        benefit = ""
        
        in_connections = False
        
        for line in lines[1:]:
            line_str = line.strip()
            if not line_str:
                continue
            if line_str.startswith("- **Цель**:") or line_str.startswith("- **Цель**"):
                goal = line_str.split(":", 1)[1].strip() if ":" in line_str else line_str
                in_connections = False
            elif line_str.startswith("- **Таблицы**:") or line_str.startswith("- **Таблицы**"):
                tables = line_str.split(":", 1)[1].strip() if ":" in line_str else line_str
                in_connections = False
            elif line_str.startswith("- **Связи**:") or line_str.startswith("- **Связи**"):
                in_connections = True
            elif line_str.startswith("- **Польза**:") or line_str.startswith("- **Польза**"):
                benefit = line_str.split(":", 1)[1].strip() if ":" in line_str else line_str
                in_connections = False
            elif in_connections and (line_str.startswith("-") or line_str.startswith("*")):
                conn_item = line_str.lstrip("-* ").strip()
                connections.append(conn_item)
            elif in_connections and line.startswith("  "):
                conn_item = line_str.lstrip("-* ").strip()
                connections.append(conn_item)
        todo_items.append({
            'title': title,
            'goal': goal,
            'tables': tables,
            'connections': connections,
            'benefit': benefit
        })
        
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

        campaigns = []
        if 'campaigns' in tables:
            cursor.execute("SELECT id, title, description FROM campaigns")
            campaigns = [dict(row) for row in cursor.fetchall()]

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
            
        conn.close()

        # Helper to parse a payload_json blob.
        def parse_payload(row):
            if not row.get('payload_json'):
                return {}
            try:
                return json.loads(row['payload_json'])
            except Exception:
                return {}
        
        # Pre-compute campaign id -> title for tooltip enrichment.
        campaign_titles = {c['id']: c['title'] for c in campaigns}
        
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
        storyline_ids = set()
        for sl in storylines:
            payload = parse_payload(sl)
            name = payload.get('name') or sl['label']
            desc = payload.get('description', '')
            sl_type = payload.get('storyline_type', '')
            tooltip = f"<b>Сюжетная линия: {name}</b>"
            if sl_type:
                tooltip += f" ({sl_type})"
            tooltip += f"<br>{desc}"

            storyline_ids.add(sl['id'])
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
        choice_story = {}  # choice_id -> story_id
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
                choice_story[c['id']] = story_id
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
        branch_origin_choice = {}  # branch_id -> choice_id (via branch_point)
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

        # ---------- Structural edges ----------

        # Storyline -> Story: a storyline belongs to a story/campaign. We link
        # storylines to the matching story via campaign_id (== story id by
        # convention) when available, otherwise to the first story as a hub.
        story_ids = [s['id'] for s in stories]
        for sl in storylines:
            payload = parse_payload(sl)
            sl_story_id = None
            campaign_id = payload.get('campaign_id')
            if campaign_id in story_ids:
                sl_story_id = campaign_id
            elif story_ids:
                sl_story_id = story_ids[0]
            if sl_story_id:
                add_edge(f"storyline_{sl['id']}", f"story_{sl_story_id}",
                         '#0ea5e9', width=1.5, dashes=True, label='часть')

        # Branch points bridge Plot Branch <-> Choice. branch_points carry a
        # choice_id and a list of branch_ids; the same (branch, choice) pair
        # may be referenced by several branch_points, so we dedup via add_edge.
        # This realises "Сюжетный шаг ➔ предоставляет выбор ➔ Choice Node" and
        # its inverse "Consequence ➔ разветвляет ➔ Plot Branch".
        branch_to_choice = {}  # branch_id -> [choice_id, ...]
        for bp in branch_points:
            payload = parse_payload(bp)
            choice_id = payload.get('choice_id')
            branch_ids = payload.get('branch_ids', [])
            if choice_id and isinstance(branch_ids, list):
                for bid in branch_ids:
                    branch_to_choice.setdefault(bid, []).append(choice_id)
                    branch_origin_choice.setdefault(bid, choice_id)
                    # Choice -> Plot Branch ("this choice opens a branch").
                    add_edge(f"choice_{choice_id}", f"branch_{bid}",
                             '#d97706', width=1.5, label='открывает')

        # Consequence -> Plot Branch: link a consequence back to the branches
        # spawned by the same choice that triggered the consequence. This is
        # the "разветвляет историю" step from the spec.
        for con_id, trig_choice_id in consequence_choice.items():
            for bid in branch_to_choice:
                if trig_choice_id in branch_to_choice[bid]:
                    add_edge(f"consequence_{con_id}", f"branch_{bid}",
                             '#8b5cf6', width=2, dashes=True, label='разветвляет')

        # Consequence -> Ending: prefer explicit field matches; fall back to a
        # conservative keyword match on conditions/descriptions. We only draw
        # a link when the consequence description and an ending condition share
        # a concrete story token (character/object/faction name).
        keywords = ["мара", "ивен", "ивон", "валон", "амулет", "культ"]
        for con in consequences:
            payload_con = parse_payload(con)
            con_desc = (payload_con.get('description') or con['label'] or '').lower()
            con_conds = [str(x).lower() for x in payload_con.get('conditions', [])]
            con_text = con_desc + ' ' + ' '.join(con_conds)

            for e in endings:
                payload_e = parse_payload(e)
                e_conds = [str(x).lower() for x in payload_e.get('conditions', [])]
                e_text = ' '.join(e_conds)
                matched = any(kw in con_text and kw in e_text for kw in keywords)
                if matched:
                    add_edge(f"consequence_{con['id']}", f"ending_{e['id']}",
                             '#10b981', width=2, dashes=True, label='ведет к')

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


