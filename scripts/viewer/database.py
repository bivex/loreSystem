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
    """Quest tree graph.

    Built only from real DB fields. Uses the full quest domain:
      - quests -> quest_chains (via shared id / quest_id in chain payload)
      - quest_chains -> quest_nodes (via quest_node_ids + nodes' quest_chain_id)
      - quest_nodes -> quest_objectives (via objective_ids)
      - quest_nodes -> quest_reward_tiers (via reward_tier.quest_node_id)
      - quest_chains -> quest_givers (via givers' quest_chain_ids)
      - intra-chain node sequencing (by id when positions tie)
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

        def load(t, cols="id, label, payload_json"):
            if t not in tables:
                return []
            cursor.execute(f"SELECT {cols} FROM {t}")
            return [dict(r) for r in cursor.fetchall()]

        quests = load('quests')
        quest_chains = load('quest_chains')
        quest_nodes = load('quest_nodes')
        prereqs = load('quest_prerequisites', "id, payload_json")
        quest_objectives = load('quest_objectives')
        quest_reward_tiers = load('quest_reward_tiers')
        quest_givers = load('quest_givers')

        chain_ids = {c['id'] for c in quest_chains}
        node_ids = {n['id'] for n in quest_nodes}
        obj_ids = {o['id'] for o in quest_objectives}
        reward_ids = {r['id'] for r in quest_reward_tiers}

        # ---------- Quest nodes ----------
        for q in quests:
            payload = parse(q)
            q_name = payload.get('name', q['label'])
            status = payload.get('status', 'not_started')
            tooltip = f"<b>⚔️ Квест: {q_name}</b>"
            tooltip += f"<br><b>Статус:</b> {status}"
            if payload.get('description'):
                tooltip += f"<br>{payload['description']}"
            nodes.append({
                'id': f"quest_{q['id']}",
                'label': f"⚔️ {q_name}",
                'title': tooltip,
                'shape': 'box',
                'color': {'background': '#f59e0b', 'border': '#b45309'},
                'font': {'color': '#111827', 'size': 14, 'bold': True}
            })

        # ---------- Quest chain -> quest linkage ----------
        chain_to_quest = {}
        for qc in quest_chains:
            payload = parse(qc)
            chain_to_quest[qc['id']] = payload.get('quest_id') or qc['id']

        # ---------- Quest giver nodes (linked to chains) ----------
        referenced_chain_ids = set()
        referenced_giver_chains = {}  # chain_id -> [giver ids]
        for qg in quest_givers:
            payload = parse(qg)
            for cid in _parse_id_list(payload.get('quest_chain_ids')):
                if cid in chain_ids:
                    referenced_chain_ids.add(cid)
                    referenced_giver_chains.setdefault(cid, []).append(qg['id'])
        for qg in quest_givers:
            payload = parse(qg)
            name = payload.get('name') or qg['label']
            tooltip = f"<b>💬 Квестгивер: {name}</b>"
            if payload.get('description'):
                tooltip += f"<br>{payload['description']}"
            if payload.get('greeting_message'):
                tooltip += f"<br><i>«{payload['greeting_message']}»</i>"
            nodes.append({
                'id': f"giver_{qg['id']}",
                'label': f"💬 {name[:18]}",
                'title': tooltip,
                'shape': 'box',
                'color': {'background': '#3b82f6', 'border': '#1d4ed8'},
                'font': {'color': '#ffffff', 'size': 11}
            })

        # ---------- Quest node (step) nodes ----------
        node_chain = {}
        node_position = {}
        node_to_quest_map = {}
        for qn in quest_nodes:
            payload = parse(qn)
            nid = qn['id']
            name = payload.get('name') or qn['label']
            chain_id = payload.get('quest_chain_id')
            node_chain[nid] = chain_id
            node_position[nid] = payload.get('position')
            if chain_id in chain_to_quest:
                node_to_quest_map[nid] = chain_to_quest[chain_id]

            status = payload.get('status', 'active')
            optional = payload.get('is_optional')
            tooltip = f"<b>📋 Шаг: {name}</b>"
            tooltip += f"<br><b>Статус:</b> {status}"
            if optional:
                tooltip += "<br><i>(опциональный)</i>"
            if payload.get('description'):
                tooltip += f"<br>{payload['description']}"
            obj_ids_ref = _parse_id_list(payload.get('objective_ids'))
            if obj_ids_ref:
                tooltip += f"<br><b>Цели:</b> {obj_ids_ref}"

            nodes.append({
                'id': f"node_{nid}",
                'label': f"📋 {name[:18]}",
                'title': tooltip,
                'shape': 'dot',
                'size': 15,
                'color': {'background': '#06b6d4', 'border': '#0891b2'}
            })

            # Step -> quest.
            parent_qid = node_to_quest_map.get(nid)
            if parent_qid is not None:
                add_edge(f"quest_{parent_qid}", f"node_{nid}",
                         '#d97706', width=1.5, dashes=True, label='шаг')

        # ---------- Quest objective nodes (linked to steps) ----------
        # Build a reverse index objective_id -> node_id once, so we don't do
        # an O(nodes * objectives) scan for every objective.
        obj_to_node = {}
        for qn in quest_nodes:
            payload = parse(qn)
            for oid in _parse_id_list(payload.get('objective_ids')):
                if oid in obj_ids:
                    obj_to_node[oid] = qn['id']
        referenced_obj_ids = set(obj_to_node.keys())
        for qo in quest_objectives:
            if qo['id'] not in referenced_obj_ids:
                continue
            payload = parse(qo)
            desc = payload.get('description') or qo['label']
            otype = payload.get('objective_type', '')
            tooltip = f"<b>🎯 Цель: {desc}</b>"
            if otype:
                tooltip += f"<br><b>Тип:</b> {otype}"
            tooltip += f"<br><b>Прогресс:</b> {payload.get('current_progress', 0)} / {payload.get('target_quantity', '?')}"
            if payload.get('status'):
                tooltip += f"<br><b>Статус:</b> {payload['status']}"
            if payload.get('objective_hint'):
                tooltip += f"<br><i>{payload['objective_hint']}</i>"
            nodes.append({
                'id': f"objective_{qo['id']}",
                'label': f"🎯 {desc[:18]}",
                'title': tooltip,
                'shape': 'diamond',
                'size': 12,
                'color': {'background': '#eab308', 'border': '#a16207'}
            })
            # Objective -> step (via reverse index, O(1)).
            parent_nid = obj_to_node.get(qo['id'])
            if parent_nid is not None:
                add_edge(f"node_{parent_nid}", f"objective_{qo['id']}",
                         '#eab308', width=1.5, label='цель')

        # ---------- Reward tier nodes (linked to steps) ----------
        for rt in quest_reward_tiers:
            payload = parse(rt)
            name = payload.get('name') or rt['label']
            qnode_id = payload.get('quest_node_id')
            tooltip = f"<b>🎁 Награда: {name}</b>"
            if payload.get('description'):
                tooltip += f"<br>{payload['description']}"
            tooltip += f"<br><b>Тир:</b> {payload.get('tier_level', '?')}"
            if payload.get('is_guaranteed'):
                tooltip += "<br>(гарантированная)"
            nodes.append({
                'id': f"reward_{rt['id']}",
                'label': f"🎁 {name[:18]}",
                'title': tooltip,
                'shape': 'diamond',
                'size': 13,
                'color': {'background': '#22c55e', 'border': '#15803d'}
            })
            if qnode_id in node_ids:
                add_edge(f"node_{qnode_id}", f"reward_{rt['id']}",
                         '#22c55e', width=1.5, label='награда')

        # ---------- Chain -> givers ----------
        for cid, giver_ids in referenced_giver_chains.items():
            for gid in giver_ids:
                add_edge(f"giver_{gid}", f"node_chain_{cid}",
                         '#3b82f6', width=1.5, label='выдаёт')
        # Render referenced chains as helper nodes so givers have a target.
        for cid in referenced_chain_ids:
            payload = next((parse(c) for c in quest_chains if c['id'] == cid), {})
            cname = payload.get('name') or f"Цепочка {cid}"
            nodes.append({
                'id': f"node_chain_{cid}",
                'label': f"🔗 {cname[:18]}",
                'title': f"<b>Цепочка квестов: {cname}</b>",
                'shape': 'box',
                'color': {'background': '#a855f7', 'border': '#7e22ce'},
                'font': {'color': '#ffffff', 'size': 11}
            })
            # Chain -> quest (it belongs to).
            qid = chain_to_quest.get(cid)
            if qid is not None:
                add_edge(f"node_chain_{cid}", f"quest_{qid}",
                         '#a855f7', width=1, label='часть', dashes=True)

        # ---------- Intra-chain node sequencing ----------
        for qc in quest_chains:
            payload = parse(qc)
            seq = _parse_id_list(payload.get('quest_node_ids'))
            if len(seq) < 2:
                # Reconstruct from nodes referencing this chain, ordered by id.
                cid = qc['id']
                seq = sorted([nid for nid, ccid in node_chain.items()
                              if ccid == cid and nid in node_ids])
            for i in range(len(seq) - 1):
                if seq[i] in node_ids and seq[i+1] in node_ids:
                    add_edge(f"node_{seq[i]}", f"node_{seq[i+1]}",
                             '#06b6d4', width=2.5, label='далее')

        # ---------- Prerequisites (if any target a real quest id) ----------
        for pr in prereqs:
            payload = parse(pr)
            req_ids = _parse_id_list(payload.get('required_quest_ids'))
            target_node = payload.get('quest_node_id')
            for req_qid in req_ids:
                if target_node in node_ids:
                    add_edge(f"quest_{req_qid}", f"node_{target_node}",
                             '#ef4444', width=1.5, dashes=True, label='требует')

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


def _load_entities(cursor, table, tables):
    """Load rows from a table, adapting to whichever schema it has.

    The DB can be created by either the main app (label + payload_json) or
    the Camel lore pipeline (name/description/real columns). This helper:
      - probes the table's columns once
      - builds a SELECT that pulls `id`, a label-like field, and either the
        JSON payload blob OR synthesises one from the real columns
      - returns a list of dicts shaped like the rest of the code expects:
        {'id', 'label', 'payload_json', 'payload'}
    """
    if table not in tables:
        return []
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cursor.fetchall()]
    colset = set(cols)

    # Choose the label-like column.
    label_col = 'label' if 'label' in colset else ('name' if 'name' in colset else 'title')
    # Choose the payload column.
    payload_col = 'payload_json' if 'payload_json' in colset else None

    if payload_col:
        cursor.execute(f"SELECT id, {label_col} AS label, {payload_col} AS payload_json FROM {table}")
        rows = []
        for r in cursor.fetchall():
            d = dict(r)
            pj = d.get('payload_json')
            try:
                d['payload'] = json.loads(pj) if pj else {}
            except Exception:
                d['payload'] = {}
            rows.append(d)
        return rows

    # No payload_json: synthesise a payload from the real columns so the
    # downstream graph code can read entity fields uniformly.
    select_cols = ['id'] + [c for c in cols if c not in ('id', 'tenant_id', 'created_at', 'updated_at', 'version')]
    select_sql = ', '.join(f'"{c}"' for c in select_cols)
    cursor.execute(f"SELECT {select_sql} FROM {table}")
    rows = []
    for r in cursor.fetchall():
        d = dict(r)
        payload = {k: v for k, v in d.items() if k != 'id'}
        # Ensure there's a 'name' for display.
        if 'name' not in payload and label_col in payload:
            payload['name'] = payload[label_col]
        rows.append({
            'id': d['id'],
            'label': d.get(label_col) or d.get('name') or d.get('title') or f"#{d['id']}",
            'payload_json': json.dumps(payload, default=str, ensure_ascii=False),
            'payload': payload,
        })
    return rows


def _character_roles(cursor, tables):
    """Infer each character's narrative role from structural signals.

    The `characters.role` column exists but is empty in the current data,
    so we derive a role from real signals:
      - character.role column (authoritative when present)
      - character_relationships: enemy/rival -> antagonist; ally/friend ->
        ally; 'complicated' counts as ally (tense alliance)
      - wars: a faction name matching a character name on the aggressor
        side marks that character as an antagonist
      - quest_givers.description: keywords like 'вождь'/'поработитель'/
        'культист'/'тёмный' hint antagonist; 'пленник'/'спасти'/'союз'/
        'герой' hint protagonist/ally
      - invasions.invader_name matching a character name -> antagonist

    Returns: dict {character_id: role} where role is one of
      'protagonist', 'ally', 'antagonist', 'npc'.
    """
    roles = {}

    # 1. Direct role column if populated.
    if 'characters' in tables:
        cursor.execute("PRAGMA table_info(characters)")
        char_cols = {r[1] for r in cursor.fetchall()}
        if 'role' in char_cols:
            cursor.execute("SELECT id, name, role, description FROM characters")
            for r in cursor.fetchall():
                d = dict(r)
                role = (d.get('role') or '').strip().lower()
                if role in ('protagonist', 'hero', 'player'):
                    roles[d['id']] = 'protagonist'
                elif role in ('antagonist', 'villain', 'boss', 'enemy'):
                    roles[d['id']] = 'antagonist'
                elif role in ('ally', 'companion', 'friend', 'support'):
                    roles[d['id']] = 'ally'

    # 2. character_relationships.
    if 'character_relationships' in tables:
        cursor.execute("SELECT character_from_id, character_to_id, relationship_type FROM character_relationships")
        for r in cursor.fetchall():
            d = dict(r)
            rtype = (d.get('relationship_type') or '').lower()
            if rtype in ('enemy', 'rival', 'nemesis', 'hostile', 'foe'):
                roles[d['character_from_id']] = 'antagonist'
                roles[d['character_to_id']] = 'antagonist'
            elif rtype in ('ally', 'friend', 'companion', 'bond', 'family', 'mentor', 'complicated'):
                roles.setdefault(d['character_from_id'], 'ally')
                roles.setdefault(d['character_to_id'], 'ally')

    # 3. quest_givers description keywords.
    antagonist_kw = ('вождь', 'поработитель', 'культист', 'тёмный власт', 'тиран', 'захватчик', 'рейдер')
    protagonist_kw = ('пленник', 'спасти', 'союзник', 'герой', 'спасител', 'путник', 'беглец')
    givers = _load_entities(cursor, 'quest_givers', tables)
    char_by_name = {}
    if 'characters' in tables:
        cursor.execute("SELECT id, name FROM characters")
        for r in cursor.fetchall():
            char_by_name[dict(r)['name'].lower()] = dict(r)['id']
    for qg in givers:
        p = qg.get('payload') or {}
        name = (p.get('name') or '').lower()
        desc = (p.get('description') or '').lower()
        cid = p.get('character_id')
        text = name + ' ' + desc
        # Try to match the giver's name to a character.
        matched_cid = cid
        if matched_cid is None:
            for cname, ccid in char_by_name.items():
                if cname and cname in name:
                    matched_cid = ccid
                    break
        if matched_cid is not None and matched_cid not in roles:
            if any(kw in text for kw in antagonist_kw):
                roles[matched_cid] = 'antagonist'
            elif any(kw in text for kw in protagonist_kw):
                roles[matched_cid] = 'protagonist'

    # 4. invasions: aggressor name matching a character name.
    invasions = _load_entities(cursor, 'invasions', tables)
    for inv in invasions:
        p = inv.get('payload') or {}
        invader = (p.get('invader_name') or p.get('name') or '').lower()
        for cname, ccid in char_by_name.items():
            if cname and len(cname) > 3 and cname in invader:
                roles[ccid] = 'antagonist'

    return roles


# Visual style per character role, used by graph builders.
CHAR_ROLE_STYLE = {
    'protagonist': {'background': '#10b981', 'border': '#047857'},   # green
    'ally':        {'background': '#3b82f6', 'border': '#1d4ed8'},    # blue
    'antagonist':  {'background': '#ef4444', 'border': '#b91c1c'},    # red
    'npc':         {'background': '#fbbf24', 'border': '#d97706'},    # gold
}


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


def _parse_id_list(value):
    """Parse a column/payload value that holds a list of ids.

    The narrative tables store id lists in three shapes:
      - a real Python list (from row_factory on a JSON column)
      - a JSON string  '[11, 12]'
      - a comma-separated string '11, 12'
    Returns a list of ints, never None.
    """
    if value is None:
        return []
    if isinstance(value, list):
        out = []
        for v in value:
            try:
                out.append(int(v))
            except (TypeError, ValueError):
                continue
        return out
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return []
        # Try JSON first, then fall back to comma split.
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return _parse_id_list(parsed)
        except Exception:
            pass
        parts = [p.strip() for p in s.strip('[]').split(',') if p.strip()]
        out = []
        for p in parts:
            try:
                out.append(int(p))
            except ValueError:
                continue
        return out
    return []


def get_narrative_graph():
    """Narrative structure graph: campaign -> act -> chapter -> episode,
    plus prologues, flashbacks, flash_forwards and alternate realities.

    Built only from real DB fields. The narrative tables (unlike many
    others) carry rich structural columns:
      - acts.campaign_id, acts.chapter_ids
      - chapters.campaign_id, chapters.act_ids, chapters.episode_ids
      - episodes.chapter_id, episodes.required_previous_episodes
      - prologues.campaign_id
      - alternate_realities.parent_world_id
      - flashbacks/flash_forwards: world_id inside payload
    Campaigns anchor everything via shared world_id / campaign_id.
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

        # ---------- Load ----------
        campaigns = []
        if 'campaigns' in tables:
            cursor.execute("SELECT id, title, description, world_id FROM campaigns")
            campaigns = [dict(r) for r in cursor.fetchall()]
        acts = []
        if 'acts' in tables:
            cursor.execute("SELECT id, title, description, act_type, act_number, "
                           "campaign_id, world_id, chapter_ids FROM acts")
            acts = [dict(r) for r in cursor.fetchall()]
        chapters = []
        if 'chapters' in tables:
            cursor.execute("SELECT id, title, description, chapter_type, "
                           "sequence_number, campaign_id, world_id, episode_ids, act_ids "
                           "FROM chapters")
            chapters = [dict(r) for r in cursor.fetchall()]
        episodes = []
        if 'episodes' in tables:
            cursor.execute("SELECT id, title, description, episode_type, "
                           "sequence_number, chapter_id, world_id, required_previous_episodes "
                           "FROM episodes")
            episodes = [dict(r) for r in cursor.fetchall()]
        prologues = []
        if 'prologues' in tables:
            cursor.execute("SELECT id, title, description, prologue_type, "
                           "campaign_id, world_id, is_required, is_skippable FROM prologues")
            prologues = [dict(r) for r in cursor.fetchall()]
        flashbacks = []
        if 'flashbacks' in tables:
            cursor.execute("SELECT id, label, payload_json FROM flashbacks")
            flashbacks = [dict(r) for r in cursor.fetchall()]
        flash_forwards = []
        if 'flash_forwards' in tables:
            cursor.execute("SELECT id, label, payload_json FROM flash_forwards")
            flash_forwards = [dict(r) for r in cursor.fetchall()]
        alternate_realities = []
        if 'alternate_realities' in tables:
            cursor.execute("SELECT id, label, payload_json FROM alternate_realities")
            alternate_realities = [dict(r) for r in cursor.fetchall()]

        campaign_ids = {c['id'] for c in campaigns}
        act_ids = {a['id'] for a in acts}
        chapter_ids = {ch['id'] for ch in chapters}
        episode_ids = {ep['id'] for ep in episodes}

        # Map world_id -> campaign_id so entities that only carry world_id
        # (flashbacks, flash_forwards, alternate_realities) can still attach
        # to their campaign.
        world_to_campaign = {}
        for c in campaigns:
            if c.get('world_id') is not None:
                world_to_campaign.setdefault(c['world_id'], c['id'])

        # ---------- Campaign (root) nodes ----------
        for c in campaigns:
            tooltip = f"<b>Кампания: {c['title']}</b>"
            if c.get('description'):
                tooltip += f"<br>{c['description']}"
            nodes.append({
                'id': f"campaign_{c['id']}",
                'label': f"🎭 {c['title']}",
                'title': tooltip,
                'color': {'background': '#6366f1', 'border': '#4338ca'},  # Indigo
                'shape': 'star',
                'size': 24
            })

        # ---------- Act nodes ----------
        for a in acts:
            tooltip = f"<b>Акт {a.get('act_number', a['id'])}: {a['title']}</b>"
            if a.get('act_type'):
                tooltip += f"<br><b>Тип:</b> {a['act_type']}"
            if a.get('description'):
                tooltip += f"<br>{a['description']}"
            nodes.append({
                'id': f"act_{a['id']}",
                'label': f"🎬 Акт {a.get('act_number', a['id'])}",
                'title': tooltip,
                'color': {'background': '#3b82f6', 'border': '#1d4ed8'},  # Blue
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 14, 'bold': True}
            })
            # Act -> Campaign
            cid = a.get('campaign_id')
            if cid in campaign_ids:
                add_edge(f"campaign_{cid}", f"act_{a['id']}",
                         '#3b82f6', width=2, label='акт')

        # Act sequence backbone (Act I -> II -> III) by act_number.
        sorted_acts = sorted(acts, key=lambda x: (x.get('act_number') or 0, x['id']))
        for i in range(len(sorted_acts) - 1):
            add_edge(f"act_{sorted_acts[i]['id']}",
                     f"act_{sorted_acts[i+1]['id']}",
                     '#3b82f6', width=1.5, dashes=True, label='далее')

        # ---------- Chapter nodes ----------
        for ch in chapters:
            tooltip = f"<b>Глава {ch.get('sequence_number', ch['id'])}: {ch['title']}</b>"
            if ch.get('chapter_type'):
                tooltip += f"<br><b>Тип:</b> {ch['chapter_type']}"
            if ch.get('description'):
                tooltip += f"<br>{ch['description']}"
            nodes.append({
                'id': f"chapter_{ch['id']}",
                'label': f"📖 Гл. {ch.get('sequence_number', ch['id'])}",
                'title': tooltip,
                'color': {'background': '#0ea5e9', 'border': '#0369a1'},  # Sky
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })

            # Chapter -> Act (via act_ids). This is the primary 'chapter belongs
            # to act' link; acts.chapter_ids is the inverse and we don't need
            # to draw it twice.
            for aid in _parse_id_list(ch.get('act_ids')):
                if aid in act_ids:
                    add_edge(f"act_{aid}", f"chapter_{ch['id']}",
                             '#0ea5e9', width=2, label='глава')

            # Chapter -> Campaign (campaign_id column).
            cid = ch.get('campaign_id')
            if cid in campaign_ids:
                add_edge(f"campaign_{cid}", f"chapter_{ch['id']}",
                         '#0ea5e9', width=1, label='часть', dashes=True)

        # Chapter sequence backbone by sequence_number.
        sorted_chapters = sorted(chapters, key=lambda x: (x.get('sequence_number') or 0, x['id']))
        for i in range(len(sorted_chapters) - 1):
            add_edge(f"chapter_{sorted_chapters[i]['id']}",
                     f"chapter_{sorted_chapters[i+1]['id']}",
                     '#0ea5e9', width=1.5, dashes=True, label='далее')

        # ---------- Episode nodes ----------
        for ep in episodes:
            tooltip = f"<b>Эпизод {ep.get('sequence_number', ep['id'])}: {ep['title']}</b>"
            if ep.get('episode_type'):
                tooltip += f"<br><b>Тип:</b> {ep['episode_type']}"
            if ep.get('description'):
                tooltip += f"<br>{ep['description']}"
            nodes.append({
                'id': f"episode_{ep['id']}",
                'label': f"🎞️ Эп. {ep.get('sequence_number', ep['id'])}",
                'title': tooltip,
                'color': {'background': '#06b6d4', 'border': '#0891b2'},  # Cyan
                'shape': 'dot',
                'size': 14
            })

            # Episode -> Chapter (direct FK chapter_id).
            chid = ep.get('chapter_id')
            if chid in chapter_ids:
                add_edge(f"chapter_{chid}", f"episode_{ep['id']}",
                         '#06b6d4', width=2, label='эпизод')

            # Episode prerequisite chain (required_previous_episodes).
            for prev in _parse_id_list(ep.get('required_previous_episodes')):
                if prev in episode_ids and prev != ep['id']:
                    add_edge(f"episode_{prev}", f"episode_{ep['id']}",
                             '#f59e0b', width=1.5, label='требует', dashes=True)

        # ---------- Prologue nodes ----------
        for p in prologues:
            tooltip = f"<b>Пролог: {p['title']}</b>"
            if p.get('prologue_type'):
                tooltip += f"<br><b>Тип:</b> {p['prologue_type']}"
            req = 'обязательный' if p.get('is_required') else 'необязательный'
            tooltip += f"<br><b>Статус:</b> {req}"
            if p.get('is_skippable'):
                tooltip += ' (можно пропустить)'
            if p.get('description'):
                tooltip += f"<br>{p['description']}"
            nodes.append({
                'id': f"prologue_{p['id']}",
                'label': f"📜 {p['title'][:25]}",
                'title': tooltip,
                'color': {'background': '#10b981', 'border': '#047857'},  # Green
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })
            cid = p.get('campaign_id')
            if cid in campaign_ids:
                add_edge(f"campaign_{cid}", f"prologue_{p['id']}",
                         '#10b981', width=2, label='пролог')

        # ---------- Flashback nodes ----------
        for fb in flashbacks:
            payload = parse(fb)
            name = payload.get('name') or fb['label']
            tooltip = f"<b>Флэшбэк: {name}</b>"
            if payload.get('description'):
                tooltip += f"<br>{payload['description']}"
            nodes.append({
                'id': f"flashback_{fb['id']}",
                'label': f"⏮️ {name[:22]}",
                'title': tooltip,
                'color': {'background': '#a855f7', 'border': '#7e22ce'},  # Purple
                'shape': 'diamond',
                'size': 13
            })
            meta = payload.get('metadata') or {}
            wid = meta.get('world_id') or payload.get('world_id')
            cid = world_to_campaign.get(wid)
            if cid is not None:
                add_edge(f"campaign_{cid}", f"flashback_{fb['id']}",
                         '#a855f7', width=1.5, label='ретроспектива', dashes=True)

        # ---------- Flash-forward nodes ----------
        for ff in flash_forwards:
            payload = parse(ff)
            name = payload.get('name') or ff['label']
            tooltip = f"<b>Флэшфорвард: {name}</b>"
            if payload.get('description'):
                tooltip += f"<br>{payload['description']}"
            if payload.get('is_prophetic'):
                tooltip += "<br><b>Пророческий</b>"
            nodes.append({
                'id': f"flash_forward_{ff['id']}",
                'label': f"⏭️ {name[:22]}",
                'title': tooltip,
                'color': {'background': '#ec4899', 'border': '#be185d'},  # Pink
                'shape': 'diamond',
                'size': 13
            })
            wid = payload.get('world_id')
            cid = world_to_campaign.get(wid)
            if cid is not None:
                add_edge(f"campaign_{cid}", f"flash_forward_{ff['id']}",
                         '#ec4899', width=1.5, label='предвидение', dashes=True)

        # ---------- Alternate reality nodes ----------
        for ar in alternate_realities:
            payload = parse(ar)
            name = payload.get('name') or ar['label']
            rtype = payload.get('reality_type', '')
            is_canon = payload.get('is_canon', False)
            tooltip = f"<b>Альт. реальность: {name}</b>"
            if rtype:
                tooltip += f"<br><b>Тип:</b> {rtype}"
            tooltip += f"<br><b>Канон:</b> {'да' if is_canon else 'нет'}"
            if payload.get('description'):
                tooltip += f"<br>{payload['description']}"
            nodes.append({
                'id': f"alternate_reality_{ar['id']}",
                'label': f"🌀 {name[:22]}",
                'title': tooltip,
                'color': {'background': '#f59e0b', 'border': '#b45309'},  # Amber
                'shape': 'diamond',
                'size': 14
            })
            wid = payload.get('parent_world_id')
            cid = world_to_campaign.get(wid)
            if cid is not None:
                add_edge(f"campaign_{cid}", f"alternate_reality_{ar['id']}",
                         '#f59e0b', width=1.5, label='ветвь реальности', dashes=True)

        conn.close()
    except Exception as e:
        print(f"Error building narrative graph: {e}")

    return {'nodes': nodes, 'edges': edges}


def get_legendary_items_graph():
    """Legendary items & sets graph.

    Built only from real DB fields. The legendary item tables are mostly
    flat entities with no cross-table FKs — only `world_id` is shared.
    The two real structural links are:
      - sockets.item_id -> items (the host item that the socket is cut into)
      - traits.character_id -> characters (a trait belongs to a character)
    Everything else hangs off the shared world. We surface that honestly:
    items/totems are clustered by their rarity tier where the data supports
    it (set pieces via artifact_sets.total_pieces), and the world node acts
    as the hub.
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

        def load_table(t, cols="id, label, payload_json"):
            if t not in tables:
                return []
            cursor.execute(f"SELECT {cols} FROM {t}")
            return [dict(r) for r in cursor.fetchall()]

        legendary_weapons = load_table('legendary_weapons')
        mythical_armors = load_table('mythical_armors')
        divine_items = load_table('divine_items')
        cursed_items = load_table('cursed_items')
        artifact_sets = load_table('artifact_sets')
        enchantments = load_table('enchantments')
        runes = load_table('runes')
        glyphs = load_table('glyphs')
        sockets = load_table('sockets')
        traits = load_table('traits')
        items = load_table('items')           # host items for sockets
        characters = []
        if 'characters' in tables:
            cursor.execute("SELECT id, name FROM characters")
            characters = [dict(r) for r in cursor.fetchall()]

        item_ids = {it['id'] for it in items}
        char_ids = {c['id'] for c in characters}

        # ---------- World hub node ----------
        # All legendary entities share world_id=1; render it once as the hub.
        world_id = None
        for ents in (legendary_weapons, mythical_armors, divine_items,
                     cursed_items, artifact_sets, enchantments, runes, glyphs):
            for e in ents:
                payload = parse(e)
                if payload.get('world_id') is not None:
                    world_id = payload['world_id']
                    break
            if world_id is not None:
                break
        if world_id is not None:
            nodes.append({
                'id': f"world_{world_id}",
                'label': f"🌍 Мир {world_id}",
                'title': f"<b>Мир {world_id}</b><br>Хаб редких предметов",
                'color': {'background': '#64748b', 'border': '#334155'},  # Slate
                'shape': 'star',
                'size': 18
            })

        # ---------- Legendary weapon nodes ----------
        for w in legendary_weapons:
            payload = parse(w)
            name = payload.get('name') or w['label']
            tooltip = f"<b>⚔️ Легендарное оружие: {name}</b>"
            if payload.get('weapon_type'):
                tooltip += f"<br><b>Тип:</b> {payload['weapon_type']}"
            tooltip += f"<br><b>Урон:</b> {payload.get('damage', '?')}"
            if payload.get('rarity'):
                tooltip += f"<br><b>Редкость:</b> {payload['rarity']}"
            if payload.get('special_ability'):
                tooltip += f"<br><b>Способность:</b> {payload['special_ability']}"
            nodes.append({
                'id': f"legendary_weapon_{w['id']}",
                'label': f"⚔️ {name[:20]}",
                'title': tooltip,
                'color': {'background': '#f59e0b', 'border': '#b45309'},  # Amber
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"legendary_weapon_{w['id']}",
                         '#f59e0b', width=1.5, label='оружие')

        # ---------- Mythical armor nodes ----------
        for a in mythical_armors:
            payload = parse(a)
            name = payload.get('name') or a['label']
            tooltip = f"<b>🛡️ Мифическая броня: {name}</b>"
            if payload.get('armor_type'):
                tooltip += f"<br><b>Тип:</b> {payload['armor_type']}"
            tooltip += f"<br><b>Защита:</b> {payload.get('defense', '?')}"
            if payload.get('special_protection'):
                tooltip += f"<br><b>Особая защита:</b> {payload['special_protection']}"
            nodes.append({
                'id': f"mythical_armor_{a['id']}",
                'label': f"🛡️ {name[:20]}",
                'title': tooltip,
                'color': {'background': '#3b82f6', 'border': '#1d4ed8'},  # Blue
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"mythical_armor_{a['id']}",
                         '#3b82f6', width=1.5, label='броня')

        # ---------- Divine item nodes ----------
        for d in divine_items:
            payload = parse(d)
            name = payload.get('name') or d['label']
            tooltip = f"<b>✨ Божественный предмет: {name}</b>"
            if payload.get('item_type'):
                tooltip += f"<br><b>Тип:</b> {payload['item_type']}"
            if payload.get('divine_ability'):
                tooltip += f"<br><b>Способность:</b> {payload['divine_ability']}"
            nodes.append({
                'id': f"divine_item_{d['id']}",
                'label': f"✨ {name[:20]}",
                'title': tooltip,
                'color': {'background': '#eab308', 'border': '#a16207'},  # Yellow
                'shape': 'diamond',
                'size': 14
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"divine_item_{d['id']}",
                         '#eab308', width=1.5, label='артефакт')

        # ---------- Cursed item nodes ----------
        for cu in cursed_items:
            payload = parse(cu)
            name = payload.get('name') or cu['label']
            tooltip = f"<b>💀 Проклятый предмет: {name}</b>"
            if payload.get('item_type'):
                tooltip += f"<br><b>Тип:</b> {payload['item_type']}"
            if payload.get('curse_effect'):
                tooltip += f"<br><b>Проклятие:</b> {payload['curse_effect']}"
            if payload.get('risk_level'):
                tooltip += f"<br><b>Риск:</b> {payload['risk_level']}"
            nodes.append({
                'id': f"cursed_item_{cu['id']}",
                'label': f"💀 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#dc2626', 'border': '#991b1b'},  # Red
                'shape': 'diamond',
                'size': 14
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"cursed_item_{cu['id']}",
                         '#dc2626', width=1.5, label='проклят')

        # ---------- Artifact set nodes ----------
        for s in artifact_sets:
            payload = parse(s)
            name = payload.get('name') or s['label']
            tooltip = f"<b>🔱 Набор артефактов: {name}</b>"
            tooltip += f"<br><b>Всего предметов:</b> {payload.get('total_pieces', '?')}"
            if payload.get('set_bonus'):
                tooltip += f"<br><b>Бонус сета:</b> {payload['set_bonus']}"
            nodes.append({
                'id': f"artifact_set_{s['id']}",
                'label': f"🔱 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#a855f7', 'border': '#7e22ce'},  # Purple
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12, 'bold': True}
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"artifact_set_{s['id']}",
                         '#a855f7', width=2, label='сет')

        # ---------- Enchantment nodes ----------
        for en in enchantments:
            payload = parse(en)
            name = payload.get('name') or en['label']
            tooltip = f"<b>🔷 Зачарование: {name}</b>"
            if payload.get('enchantment_type'):
                tooltip += f"<br><b>Тип:</b> {payload['enchantment_type']}"
            if payload.get('description'):
                tooltip += f"<br>{payload['description']}"
            nodes.append({
                'id': f"enchantment_{en['id']}",
                'label': f"🔷 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#06b6d4', 'border': '#0891b2'},  # Cyan
                'shape': 'dot',
                'size': 12
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"enchantment_{en['id']}",
                         '#06b6d4', width=1, label='зачарование', dashes=True)

        # ---------- Rune nodes ----------
        for rn in runes:
            payload = parse(rn)
            name = payload.get('name') or rn['label']
            tooltip = f"<b>🔺 Руна: {name}</b>"
            if payload.get('rune_type'):
                tooltip += f"<br><b>Тип:</b> {payload['rune_type']}"
            tooltip += f"<br><b>Уровень:</b> {payload.get('level', '?')} / {payload.get('max_level', '?')}"
            nodes.append({
                'id': f"rune_{rn['id']}",
                'label': f"🔺 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#10b981', 'border': '#047857'},  # Green
                'shape': 'dot',
                'size': 12
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"rune_{rn['id']}",
                         '#10b981', width=1, label='руна', dashes=True)

        # ---------- Glyph nodes ----------
        for gl in glyphs:
            payload = parse(gl)
            name = payload.get('name') or gl['label']
            tooltip = f"<b>🔻 Глиф: {name}</b>"
            if payload.get('glyph_school'):
                tooltip += f"<br><b>Школа:</b> {payload['glyph_school']}"
            if payload.get('category'):
                tooltip += f"<br><b>Категория:</b> {payload['category']}"
            nodes.append({
                'id': f"glyph_{gl['id']}",
                'label': f"🔻 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#ec4899', 'border': '#be185d'},  # Pink
                'shape': 'dot',
                'size': 12
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"glyph_{gl['id']}",
                         '#ec4899', width=1, label='глиф', dashes=True)

        # ---------- Socket nodes (linked to host items) ----------
        # The only real cross-table FK in this domain: sockets.item_id.
        for sk in sockets:
            payload = parse(sk)
            host_item_id = payload.get('item_id')
            slot_index = payload.get('slot_index', '?')
            stype = payload.get('socket_type', '')
            tooltip = f"<b>⬡ Слот {slot_index}</b>"
            if stype:
                tooltip += f"<br><b>Тип:</b> {stype}"
            if payload.get('rarity'):
                tooltip += f"<br><b>Редкость:</b> {payload['rarity']}"
            if host_item_id is not None:
                tooltip += f"<br><b>В предмете:</b> item_{host_item_id}"
            nodes.append({
                'id': f"socket_{sk['id']}",
                'label': f"⬡ слот {slot_index}",
                'title': tooltip,
                'color': {'background': '#64748b', 'border': '#334155'},  # Slate
                'shape': 'diamond',
                'size': 10
            })
            # Socket -> host item (real FK sockets.item_id -> items.id).
            if host_item_id in item_ids:
                add_edge(f"item_{host_item_id}", f"socket_{sk['id']}",
                         '#64748b', width=1.5, label='слот', dashes=True)

        # ---------- Host item nodes (only those that own a socket) ----------
        socketed_item_ids = set()
        for sk in sockets:
            payload = parse(sk)
            iid = payload.get('item_id')
            if iid in item_ids:
                socketed_item_ids.add(iid)
        for it in items:
            if it['id'] not in socketed_item_ids:
                continue
            payload = parse(it)
            name = payload.get('name') or it['label']
            nodes.append({
                'id': f"item_{it['id']}",
                'label': f"🎒 {name[:20]}",
                'title': f"<b>Предмет-носитель: {name}</b>",
                'color': {'background': '#14b8a6', 'border': '#0f766e'},  # Teal
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 11}
            })

        # ---------- Trait nodes (linked to characters) ----------
        # Traits belong to characters via character_id, not to items; we
        # surface them here because they describe item-related effects.
        for tr in traits:
            payload = parse(tr)
            name = payload.get('name') or tr['label']
            tooltip = f"<b>🧬 Трейт: {name}</b>"
            if payload.get('category'):
                tooltip += f"<br><b>Категория:</b> {payload['category']}"
            if payload.get('description'):
                tooltip += f"<br>{payload['description']}"
            nodes.append({
                'id': f"trait_{tr['id']}",
                'label': f"🧬 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#f97316', 'border': '#c2410c'},  # Orange
                'shape': 'diamond',
                'size': 12
            })
            cid = payload.get('character_id')
            if cid in char_ids:
                add_edge(f"char_{cid}", f"trait_{tr['id']}",
                         '#f97316', width=1.5, label='трейт', dashes=True)

        # ---------- Character nodes (only those that carry a trait) ----------
        trait_char_ids = set()
        for tr in traits:
            payload = parse(tr)
            cid = payload.get('character_id')
            if cid in char_ids:
                trait_char_ids.add(cid)
        for ch in characters:
            if ch['id'] not in trait_char_ids:
                continue
            nodes.append({
                'id': f"char_{ch['id']}",
                'label': ch['name'],
                'title': f"<b>Персонаж: {ch['name']}</b>",
                'color': {'background': '#fbbf24', 'border': '#d97706'},  # Gold
                'shape': 'dot',
                'size': 14
            })

        conn.close()
    except Exception as e:
        print(f"Error building legendary items graph: {e}")

    return {'nodes': nodes, 'edges': edges}


def get_achievements_graph():
    """Achievements & player progress graph.

    Built only from real DB fields. The progression-meta tables cluster
    around `character_id` (Mara Voss, id=14):
      - masterys.character_id
      - progression_events.character_id
      - experiences.character_id
      - player_metrics.player_id (acts as character_id)
      - progression_states.character_states[<id>]
    Achievements, badges, titles and leaderboards carry only world_id and
    attach to the shared world hub. Quest-completion events link onward to
    the quests table via event_type='quest_complete' (event label matches a
    quest label, but we only draw this when both ids are structural).
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

        def load_table(t):
            if t not in tables:
                return []
            cursor.execute(f"SELECT id, label, payload_json FROM {t}")
            return [dict(r) for r in cursor.fetchall()]

        achievements = load_table('achievements')
        badges = load_table('badges')
        masterys = load_table('masterys')
        titles = load_table('titles')
        progression_events = load_table('progression_events')
        progression_states = load_table('progression_states')
        experiences = load_table('experiences')
        leaderboards = load_table('leaderboards')
        player_metrics = load_table('player_metrics')
        characters = []
        if 'characters' in tables:
            cursor.execute("SELECT id, name FROM characters")
            characters = [dict(r) for r in cursor.fetchall()]
        char_ids = {c['id'] for c in characters}

        # ---------- Character (root) nodes ----------
        # Only render characters that progression entities reference.
        referenced = set()
        for ents, key in ((masterys, 'character_id'),
                          (progression_events, 'character_id'),
                          (experiences, 'character_id'),
                          (player_metrics, 'player_id')):
            for e in ents:
                payload = parse(e)
                cid = payload.get(key)
                if cid is not None:
                    try:
                        referenced.add(int(cid))
                    except (TypeError, ValueError):
                        pass
        for st in progression_states:
            payload = parse(st)
            cs = payload.get('character_states')
            if isinstance(cs, dict):
                for k in cs.keys():
                    try:
                        referenced.add(int(k))
                    except (TypeError, ValueError):
                        pass
        for ch in characters:
            if ch['id'] not in referenced:
                continue
            nodes.append({
                'id': f"char_{ch['id']}",
                'label': f"🧝 {ch['name']}",
                'title': f"<b>Персонаж: {ch['name']}</b><br>ID: {ch['id']}",
                'color': {'background': '#fbbf24', 'border': '#d97706'},  # Gold
                'shape': 'star',
                'size': 22
            })

        # ---------- Achievement nodes ----------
        for a in achievements:
            payload = parse(a)
            name = payload.get('name') or a['label']
            tooltip = f"<b>🏆 Достижение: {name}</b>"
            if payload.get('achievement_type'):
                tooltip += f"<br><b>Тип:</b> {payload['achievement_type']}"
            if payload.get('difficulty'):
                tooltip += f"<br><b>Сложность:</b> {payload['difficulty']}"
            if payload.get('description'):
                tooltip += f"<br>{payload['description']}"
            hidden = payload.get('is_hidden')
            if hidden:
                tooltip += "<br><i>(скрытое)</i>"
            nodes.append({
                'id': f"achievement_{a['id']}",
                'label': f"🏆 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#eab308', 'border': '#a16207'},  # Yellow
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })

        # ---------- Badge nodes ----------
        for b in badges:
            payload = parse(b)
            name = payload.get('name') or b['label']
            tooltip = f"<b>🎖️ Бейдж: {name}</b>"
            if payload.get('badge_type'):
                tooltip += f"<br><b>Тип:</b> {payload['badge_type']}"
            if payload.get('rarity'):
                tooltip += f"<br><b>Редкость:</b> {payload['rarity']}"
            if payload.get('description'):
                tooltip += f"<br>{payload['description']}"
            nodes.append({
                'id': f"badge_{b['id']}",
                'label': f"🎖️ {name[:20]}",
                'title': tooltip,
                'color': {'background': '#a855f7', 'border': '#7e22ce'},  # Purple
                'shape': 'diamond',
                'size': 13
            })

        # ---------- Mastery nodes (linked to character) ----------
        for m in masterys:
            payload = parse(m)
            name = payload.get('name') or m['label']
            tooltip = f"<b>🌟 Мастерство: {name}</b>"
            if payload.get('category'):
                tooltip += f"<br><b>Категория:</b> {payload['category']}"
            tooltip += f"<br><b>Уровень:</b> {payload.get('level', '?')} / {payload.get('max_level', '?')}"
            if payload.get('current_rank'):
                tooltip += f"<br><b>Ранг:</b> {payload['current_rank']}"
            nodes.append({
                'id': f"mastery_{m['id']}",
                'label': f"🌟 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#06b6d4', 'border': '#0891b2'},  # Cyan
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })
            cid = payload.get('character_id')
            if cid in char_ids:
                add_edge(f"char_{cid}", f"mastery_{m['id']}",
                         '#06b6d4', width=2, label='мастерство')

        # ---------- Title nodes ----------
        for ti in titles:
            payload = parse(ti)
            name = payload.get('name') or ti['label']
            tooltip = f"<b>👑 Титул: {name}</b>"
            if payload.get('description'):
                tooltip += f"<br>{payload['description']}"
            nodes.append({
                'id': f"title_{ti['id']}",
                'label': f"👑 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#3b82f6', 'border': '#1d4ed8'},  # Blue
                'shape': 'diamond',
                'size': 13
            })

        # ---------- Progression event nodes (linked to character) ----------
        for pe in progression_events:
            payload = parse(pe)
            etype = payload.get('event_type', '')
            label = pe['label'] or payload.get('description', f'event {pe["id"]}')
            tooltip = f"<b>⚡ Событие прогрессии: {label[:50]}</b>"
            if etype:
                tooltip += f"<br><b>Тип:</b> {etype}"
            reasons = payload.get('reasons')
            if isinstance(reasons, list) and reasons:
                tooltip += f"<br><b>Причины:</b> " + '; '.join(
                    str(r.get('description', r)) if isinstance(r, dict) else str(r)
                    for r in reasons[:3])
            nodes.append({
                'id': f"progression_event_{pe['id']}",
                'label': f"⚡ {etype or 'event'} {pe['id']}",
                'title': tooltip,
                'color': {'background': '#f97316', 'border': '#c2410c'},  # Orange
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 11}
            })
            cid = payload.get('character_id')
            if cid in char_ids:
                add_edge(f"char_{cid}", f"progression_event_{pe['id']}",
                         '#f97316', width=1.5, label=etype or 'событие', dashes=True)

        # ---------- Progression state nodes (linked to character via states map) ----------
        for ps in progression_states:
            payload = parse(ps)
            name = payload.get('name') or ps['label'] or f"State {ps['id']}"
            tp = payload.get('time_point')
            cs = payload.get('character_states')
            tooltip = f"<b>📊 Состояние: {name}</b>"
            if tp is not None:
                tooltip += f"<br><b>Точка времени:</b> t{tp}"
            if isinstance(cs, dict):
                for cid_str, cdata in cs.items():
                    if isinstance(cdata, dict):
                        tooltip += f"<br><b>Персонаж {cid_str}:</b> ур.{cdata.get('level','?')}, xp {cdata.get('experience','?')}"
            nodes.append({
                'id': f"progression_state_{ps['id']}",
                'label': f"📊 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#10b981', 'border': '#047857'},  # Green
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 11}
            })
            if isinstance(cs, dict):
                for cid_str in cs.keys():
                    try:
                        cid = int(cid_str)
                    except (TypeError, ValueError):
                        continue
                    if cid in char_ids:
                        add_edge(f"char_{cid}", f"progression_state_{ps['id']}",
                                 '#10b981', width=1.5, label='состояние', dashes=True)

        # ---------- Experience nodes (linked to character) ----------
        for ex in experiences:
            payload = parse(ex)
            etype = payload.get('experience_type', '')
            tooltip = f"<b>📈 Опыт: {etype}</b>"
            tooltip += f"<br><b>Уровень:</b> {payload.get('current_level', '?')}"
            tooltip += f"<br><b>Текущий XP:</b> {payload.get('current_xp', '?')}"
            tooltip += f"<br><b>Всего XP:</b> {payload.get('total_experience', '?')}"
            tooltip += f"<br><b>До следующего:</b> {payload.get('xp_to_next_level', '?')}"
            nodes.append({
                'id': f"experience_{ex['id']}",
                'label': f"📈 ур.{payload.get('current_level', '?')}",
                'title': tooltip,
                'color': {'background': '#22c55e', 'border': '#15803d'},  # Bright green
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 11}
            })
            cid = payload.get('character_id')
            if cid in char_ids:
                add_edge(f"char_{cid}", f"experience_{ex['id']}",
                         '#22c55e', width=2, label='опыт')

        # ---------- Leaderboard nodes ----------
        for lb in leaderboards:
            payload = parse(lb)
            name = payload.get('name') or lb['label']
            tooltip = f"<b>🏅 Таблица лидеров: {name}</b>"
            if payload.get('board_type'):
                tooltip += f"<br><b>Тип:</b> {payload['board_type']}"
            if payload.get('sort_criterion'):
                tooltip += f"<br><b>Сортировка:</b> {payload['sort_criterion']}"
            tooltip += f"<br><b>Лимит:</b> {payload.get('size_limit', '?')}"
            nodes.append({
                'id': f"leaderboard_{lb['id']}",
                'label': f"🏅 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#dc2626', 'border': '#991b1b'},  # Red
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 11}
            })

        # ---------- Player metric nodes (linked to character) ----------
        for pm in player_metrics:
            payload = parse(pm)
            name = payload.get('name') or pm['label']
            mtype = payload.get('metric_type', '')
            value = payload.get('value')
            unit = payload.get('unit', '')
            tooltip = f"<b>📊 Метрика: {name}</b>"
            if mtype:
                tooltip += f"<br><b>Тип:</b> {mtype}"
            if value is not None:
                tooltip += f"<br><b>Значение:</b> {value} {unit}"
            nodes.append({
                'id': f"player_metric_{pm['id']}",
                'label': f"📊 {mtype or 'metric'}",
                'title': tooltip,
                'color': {'background': '#ec4899', 'border': '#be185d'},  # Pink
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 11}
            })
            pid = payload.get('player_id')
            if pid in char_ids:
                add_edge(f"char_{pid}", f"player_metric_{pm['id']}",
                         '#ec4899', width=1.5, label='метрика', dashes=True)

        conn.close()
    except Exception as e:
        print(f"Error building achievements graph: {e}")

    return {'nodes': nodes, 'edges': edges}


def get_combat_graph():
    """Combat & encounters graph.

    Built only from real DB fields. Real structural links:
      - dungeons.boss_ids / raids.boss_ids -> characters (boss enemies)
      - invasions.invader_name / target_name -> faction names (matched
        against the wars table, the only place faction identity is
        encoded in the schema; mirrors the approach in factions graph)
      - world_id shared by all combat entities -> world hub
    difficulty_curves attach to the world as context; there is no direct
    FK from a curve to a specific encounter.
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

        def load_table(t):
            if t not in tables:
                return []
            cursor.execute(f"SELECT id, label, payload_json FROM {t}")
            return [dict(r) for r in cursor.fetchall()]

        arenas = load_table('arenas')
        dungeons = load_table('dungeons')
        instances = load_table('instances')
        raids = load_table('raids')
        invasions = load_table('invasions')
        difficulty_curves = load_table('difficulty_curves')
        characters = []
        if 'characters' in tables:
            cursor.execute("SELECT id, name FROM characters")
            characters = [dict(r) for r in cursor.fetchall()]
        char_ids = {c['id'] for c in characters}

        # Build the set of faction names from wars (same logic as factions
        # graph) so invasions can resolve their invader/target strings to
        # real nodes.
        faction_name_to_id = {}
        wars_rows = load_table('wars')
        for w in wars_rows:
            payload = parse(w)
            for fname in (payload.get('aggressor_name'), payload.get('defender_name'), payload.get('victor_name')):
                if fname and fname not in faction_name_to_id:
                    faction_name_to_id[fname] = f"faction_{len(faction_name_to_id)+1}"

        # ---------- World hub node ----------
        world_id = None
        for ents in (arenas, dungeons, instances, raids, invasions, difficulty_curves):
            for e in ents:
                payload = parse(e)
                if payload.get('world_id') is not None:
                    world_id = payload['world_id']
                    break
            if world_id is not None:
                break
        if world_id is not None:
            nodes.append({
                'id': f"world_{world_id}",
                'label': f"🌍 Мир {world_id}",
                'title': f"<b>Мир {world_id}</b><br>Хаб боевого контента",
                'color': {'background': '#64748b', 'border': '#334155'},
                'shape': 'star',
                'size': 18
            })

        # ---------- Faction nodes (referenced by invasions) ----------
        invasion_faction_names = set()
        for inv in invasions:
            payload = parse(inv)
            for key in ('invader_name', 'target_name'):
                fn = payload.get(key)
                if fn:
                    invasion_faction_names.add(fn)
        # Register any invasion faction not already in faction_name_to_id.
        for fn in invasion_faction_names:
            if fn not in faction_name_to_id:
                faction_name_to_id[fn] = f"faction_{len(faction_name_to_id)+1}"
        for fn in invasion_faction_names:
            nodes.append({
                'id': faction_name_to_id[fn],
                'label': f"🏛️ {fn}",
                'title': f"<b>Фракция: {fn}</b><br>Участник нашествия",
                'color': {'background': '#6366f1', 'border': '#4338ca'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })

        # ---------- Boss character nodes (referenced by dungeons/raids) ----------
        boss_ids = set()
        for ents in (dungeons, raids):
            for e in ents:
                payload = parse(e)
                for bid in _parse_id_list(payload.get('boss_ids')):
                    if bid in char_ids:
                        boss_ids.add(bid)
        for ch in characters:
            if ch['id'] not in boss_ids:
                continue
            nodes.append({
                'id': f"char_{ch['id']}",
                'label': f"👹 {ch['name']}",
                'title': f"<b>Босс: {ch['name']}</b><br>ID: {ch['id']}",
                'color': {'background': '#dc2626', 'border': '#991b1b'},
                'shape': 'diamond',
                'size': 16
            })

        # ---------- Arena nodes ----------
        for ar in arenas:
            payload = parse(ar)
            name = payload.get('name') or ar['label']
            tooltip = f"<b>⚔️ Арена: {name}</b>"
            if payload.get('match_type'):
                tooltip += f"<br><b>Тип матча:</b> {payload['match_type']}"
            tooltip += f"<br><b>Команд:</b> до {payload.get('max_teams', '?')}"
            tooltip += f"<br><b>Мин. уровень:</b> {payload.get('min_level', '?')}"
            nodes.append({
                'id': f"arena_{ar['id']}",
                'label': f"⚔️ {name[:20]}",
                'title': tooltip,
                'color': {'background': '#f59e0b', 'border': '#b45309'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"arena_{ar['id']}",
                         '#f59e0b', width=1.5, label='арена')

        # ---------- Dungeon nodes (linked to boss) ----------
        for dg in dungeons:
            payload = parse(dg)
            name = payload.get('name') or dg['label']
            tooltip = f"<b>🏰 Подземелье: {name}</b>"
            if payload.get('difficulty'):
                tooltip += f"<br><b>Сложность:</b> {payload['difficulty']}"
            tooltip += f"<br><b>Игроков:</b> до {payload.get('max_players', '?')}"
            tooltip += f"<br><b>Мин. уровень:</b> {payload.get('min_level', '?')}"
            nodes.append({
                'id': f"dungeon_{dg['id']}",
                'label': f"🏰 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#3b82f6', 'border': '#1d4ed8'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"dungeon_{dg['id']}",
                         '#3b82f6', width=1.5, label='данж')
            # Dungeon -> boss (real FK boss_ids).
            for bid in _parse_id_list(payload.get('boss_ids')):
                if bid in char_ids:
                    add_edge(f"dungeon_{dg['id']}", f"char_{bid}",
                             '#dc2626', width=2, label='босс')

        # ---------- Instance nodes ----------
        for ins in instances:
            payload = parse(ins)
            name = payload.get('name') or ins['label']
            tooltip = f"<b>🌀 Инстанс: {name}</b>"
            if payload.get('difficulty'):
                tooltip += f"<br><b>Сложность:</b> {payload['difficulty']}"
            tooltip += f"<br><b>Игроков:</b> до {payload.get('max_players', '?')}"
            if payload.get('recommended_level'):
                tooltip += f"<br><b>Реком. уровень:</b> {payload['recommended_level']}"
            nodes.append({
                'id': f"instance_{ins['id']}",
                'label': f"🌀 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#06b6d4', 'border': '#0891b2'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"instance_{ins['id']}",
                         '#06b6d4', width=1.5, label='инстанс')

        # ---------- Raid nodes (linked to boss) ----------
        for rd in raids:
            payload = parse(rd)
            name = payload.get('name') or rd['label']
            tooltip = f"<b>🐉 Рейд: {name}</b>"
            if payload.get('difficulty'):
                tooltip += f"<br><b>Сложность:</b> {payload['difficulty']}"
            tooltip += f"<br><b>Игроков:</b> {payload.get('min_players', '?')}–{payload.get('max_players', '?')}"
            tooltip += f"<br><b>Мин. уровень:</b> {payload.get('min_level', '?')}"
            nodes.append({
                'id': f"raid_{rd['id']}",
                'label': f"🐉 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#a855f7', 'border': '#7e22ce'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12, 'bold': True}
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"raid_{rd['id']}",
                         '#a855f7', width=2, label='рейд')
            for bid in _parse_id_list(payload.get('boss_ids')):
                if bid in char_ids:
                    add_edge(f"raid_{rd['id']}", f"char_{bid}",
                             '#dc2626', width=2, label='босс')

        # ---------- Invasion nodes (linked to factions) ----------
        for inv in invasions:
            payload = parse(inv)
            name = payload.get('name') or inv['label']
            itype = payload.get('invasion_type', '')
            tooltip = f"<b>💀 Нашествие: {name}</b>"
            if itype:
                tooltip += f"<br><b>Тип:</b> {itype}"
            if payload.get('invader_name'):
                tooltip += f"<br><b>Агрессор:</b> {payload['invader_name']}"
            if payload.get('target_name'):
                tooltip += f"<br><b>Цель:</b> {payload['target_name']}"
            tooltip += f"<br><b>Сила:</b> {payload.get('force_size', '?')}"
            tooltip += f"<br><b>Прогресс:</b> {payload.get('conquest_progress', '?')}%"
            nodes.append({
                'id': f"invasion_{inv['id']}",
                'label': f"💀 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#dc2626', 'border': '#991b1b'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"invasion_{inv['id']}",
                         '#dc2626', width=2, label='нашествие')
            # Invasion -> aggressor faction.
            aggr = payload.get('invader_name')
            if aggr and aggr in faction_name_to_id:
                add_edge(faction_name_to_id[aggr], f"invasion_{inv['id']}",
                         '#6366f1', width=2, label='нападает')
            # Target faction <- invasion.
            tgt = payload.get('target_name')
            if tgt and tgt in faction_name_to_id:
                add_edge(f"invasion_{inv['id']}", faction_name_to_id[tgt],
                         '#6366f1', width=2, label='на цель')

        # ---------- Difficulty curve nodes ----------
        for dc in difficulty_curves:
            payload = parse(dc)
            name = payload.get('name') or dc['label']
            tooltip = f"<b>📈 Кривая сложности: {name}</b>"
            if payload.get('curve_type'):
                tooltip += f"<br><b>Тип:</b> {payload['curve_type']}"
            tooltip += f"<br><b>Макс. уровень:</b> {payload.get('max_level', '?')}"
            tooltip += f"<br><b>Множитель:</b> {payload.get('scaling_factor', '?')}"
            nodes.append({
                'id': f"difficulty_curve_{dc['id']}",
                'label': f"📈 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#10b981', 'border': '#047857'},
                'shape': 'dot',
                'size': 12
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"difficulty_curve_{dc['id']}",
                         '#10b981', width=1, label='сложность', dashes=True)

        conn.close()
    except Exception as e:
        print(f"Error building combat graph: {e}")

    return {'nodes': nodes, 'edges': edges}


def get_economy_graph():
    """Economy & loot graph.

    Built only from real DB fields. Real structural links:
      - inventories.owner_id -> characters (the bag's owner)
      - inventories.slots[<n>].item_id -> items (contents of the bag)
      - quest_reward_tiers.quest_node_id -> quest_nodes (which quest step
        grants the reward)
      - loot_table_weights.loot_table_id -> a logical loot table id (we
        surface it as a hub node since no loot_tables table exists)
      - world_id shared by all economy entities -> world hub
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

        def load_table(t):
            if t not in tables:
                return []
            cursor.execute(f"SELECT id, label, payload_json FROM {t}")
            return [dict(r) for r in cursor.fetchall()]

        inventories = load_table('inventories')
        loot_table_weights = load_table('loot_table_weights')
        drop_rates = load_table('drop_rates')
        quest_reward_tiers = load_table('quest_reward_tiers')
        relic_collections = load_table('relic_collections')
        characters = []
        if 'characters' in tables:
            cursor.execute("SELECT id, name FROM characters")
            characters = [dict(r) for r in cursor.fetchall()]
        items = load_table('items')
        quest_nodes = load_table('quest_nodes')
        char_ids = {c['id'] for c in characters}
        item_ids = {it['id'] for it in items}
        qnode_ids = {qn['id'] for qn in quest_nodes}

        # ---------- World hub node ----------
        world_id = None
        for ents in (loot_table_weights, drop_rates, quest_reward_tiers, relic_collections):
            for e in ents:
                payload = parse(e)
                if payload.get('world_id') is not None:
                    world_id = payload['world_id']
                    break
            if world_id is not None:
                break
        if world_id is not None:
            nodes.append({
                'id': f"world_{world_id}",
                'label': f"🌍 Мир {world_id}",
                'title': f"<b>Мир {world_id}</b><br>Хаб экономики и лута",
                'color': {'background': '#64748b', 'border': '#334155'},
                'shape': 'star',
                'size': 18
            })

        # ---------- Owner character nodes (referenced by inventories) ----------
        owner_ids = set()
        for inv in inventories:
            payload = parse(inv)
            oid = payload.get('owner_id')
            if oid in char_ids:
                owner_ids.add(oid)
        for ch in characters:
            if ch['id'] not in owner_ids:
                continue
            nodes.append({
                'id': f"char_{ch['id']}",
                'label': f"🧝 {ch['name']}",
                'title': f"<b>Владелец: {ch['name']}</b>",
                'color': {'background': '#fbbf24', 'border': '#d97706'},
                'shape': 'star',
                'size': 16
            })

        # ---------- Item nodes (referenced by inventories) ----------
        referenced_item_ids = set()
        for inv in inventories:
            payload = parse(inv)
            slots = payload.get('slots')
            if isinstance(slots, dict):
                for slot in slots.values():
                    if isinstance(slot, dict):
                        iid = slot.get('item_id')
                        if iid in item_ids:
                            referenced_item_ids.add(iid)
        for it in items:
            if it['id'] not in referenced_item_ids:
                continue
            payload = parse(it)
            name = payload.get('name') or it['label']
            nodes.append({
                'id': f"item_{it['id']}",
                'label': f"🎒 {name[:20]}",
                'title': f"<b>Предмет: {name}</b>",
                'color': {'background': '#14b8a6', 'border': '#0f766e'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 11}
            })

        # ---------- Quest node nodes (referenced by reward tiers) ----------
        referenced_qnode_ids = set()
        for qt in quest_reward_tiers:
            payload = parse(qt)
            qid = payload.get('quest_node_id')
            if qid in qnode_ids:
                referenced_qnode_ids.add(qid)
        for qn in quest_nodes:
            if qn['id'] not in referenced_qnode_ids:
                continue
            payload = parse(qn)
            name = payload.get('name') or qn['label']
            nodes.append({
                'id': f"quest_node_{qn['id']}",
                'label': f"📜 {name[:20]}",
                'title': f"<b>Шаг квеста: {name}</b>",
                'color': {'background': '#0ea5e9', 'border': '#0369a1'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 11}
            })

        # ---------- Inventory nodes (linked to owner + items) ----------
        for inv in inventories:
            payload = parse(inv)
            oid = payload.get('owner_id')
            tooltip = f"<b>🎒 Инвентарь #{inv['id']}</b>"
            if oid in char_ids:
                oname = next((c['name'] for c in characters if c['id'] == oid), oid)
                tooltip += f"<br><b>Владелец:</b> {oname}"
            tooltip += f"<br><b>Вместимость:</b> {payload.get('capacity', '?')}"
            tooltip += f"<br><b>Золото:</b> {payload.get('gold', '?')}"
            slots = payload.get('slots')
            if isinstance(slots, dict) and slots:
                tooltip += f"<br><b>Слотов занято:</b> {len(slots)}"
            nodes.append({
                'id': f"inventory_{inv['id']}",
                'label': f"🎒 Инв. #{inv['id']}",
                'title': tooltip,
                'color': {'background': '#f59e0b', 'border': '#b45309'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 11}
            })
            # Inventory -> owner character (real FK owner_id).
            if oid in char_ids:
                add_edge(f"char_{oid}", f"inventory_{inv['id']}",
                         '#fbbf24', width=2, label='инвентарь')
            # Inventory -> contained items (real FK slots[].item_id).
            if isinstance(slots, dict):
                for slot in slots.values():
                    if isinstance(slot, dict):
                        iid = slot.get('item_id')
                        if iid in item_ids:
                            add_edge(f"inventory_{inv['id']}", f"item_{iid}",
                                     '#14b8a6', width=1.5, label='содержит', dashes=True)

        # ---------- Loot table hub + weight nodes ----------
        # loot_table_weights reference a loot_table_id; since there is no
        # loot_tables table, surface each distinct loot_table_id as a hub.
        loot_table_hub_ids = set()
        for lw in loot_table_weights:
            payload = parse(lw)
            ltid = payload.get('loot_table_id')
            if ltid is not None:
                loot_table_hub_ids.add(ltid)
        for ltid in loot_table_hub_ids:
            nodes.append({
                'id': f"loot_table_{ltid}",
                'label': f"📦 Лут-таблица {ltid}",
                'title': f"<b>Лут-таблица #{ltid}</b><br>Группирует дроп-веса",
                'color': {'background': '#ec4899', 'border': '#be185d'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12, 'bold': True}
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"loot_table_{ltid}",
                         '#ec4899', width=1.5, label='лут')
        for lw in loot_table_weights:
            payload = parse(lw)
            name = payload.get('name') or lw['label']
            tooltip = f"<b>⚖️ Вес лута: {name}</b>"
            if payload.get('rarity'):
                tooltip += f"<br><b>Редкость:</b> {payload['rarity']}"
            tooltip += f"<br><b>Вес:</b> {payload.get('weight', '?')}"
            tooltip += f"<br><b>Мин. уровень:</b> {payload.get('min_level', '?')}"
            nodes.append({
                'id': f"loot_weight_{lw['id']}",
                'label': f"⚖️ {name[:20]}",
                'title': tooltip,
                'color': {'background': '#f472b6', 'border': '#be185d'},
                'shape': 'dot',
                'size': 12
            })
            ltid = payload.get('loot_table_id')
            if ltid is not None:
                add_edge(f"loot_table_{ltid}", f"loot_weight_{lw['id']}",
                         '#ec4899', width=1.5, label='вес')

        # ---------- Drop rate nodes ----------
        for dr in drop_rates:
            payload = parse(dr)
            name = payload.get('name') or dr['label']
            tooltip = f"<b>🎰 Дроп-рейт: {name}</b>"
            if payload.get('category'):
                tooltip += f"<br><b>Категория:</b> {payload['category']}"
            tooltip += f"<br><b>Шанс:</b> {payload.get('drop_rate', '?')}"
            if payload.get('is_event_boosted'):
                tooltip += "<br><b>Буст-множитель:</b> " + str(payload.get('boost_multiplier', '?'))
            nodes.append({
                'id': f"drop_rate_{dr['id']}",
                'label': f"🎰 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#22c55e', 'border': '#15803d'},
                'shape': 'dot',
                'size': 12
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"drop_rate_{dr['id']}",
                         '#22c55e', width=1.5, label='дроп', dashes=True)

        # ---------- Quest reward tier nodes (linked to quest_node) ----------
        for qt in quest_reward_tiers:
            payload = parse(qt)
            name = payload.get('name') or qt['label']
            tooltip = f"<b>🎁 Награда: {name}</b>"
            if payload.get('description'):
                tooltip += f"<br>{payload['description']}"
            tooltip += f"<br><b>Тир:</b> {payload.get('tier_level', '?')}"
            if payload.get('is_guaranteed'):
                tooltip += "<br>(гарантированная)"
            nodes.append({
                'id': f"reward_tier_{qt['id']}",
                'label': f"🎁 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#eab308', 'border': '#a16207'},
                'shape': 'diamond',
                'size': 13
            })
            qid = payload.get('quest_node_id')
            if qid in qnode_ids:
                add_edge(f"quest_node_{qid}", f"reward_tier_{qt['id']}",
                         '#0ea5e9', width=2, label='награда')
            elif world_id is not None:
                add_edge(f"world_{world_id}", f"reward_tier_{qt['id']}",
                         '#eab308', width=1, label='награда', dashes=True)

        # ---------- Relic collection nodes ----------
        for rc in relic_collections:
            payload = parse(rc)
            name = payload.get('name') or rc['label']
            tooltip = f"<b>🏺 Коллекция реликвий: {name}</b>"
            if payload.get('collection_type'):
                tooltip += f"<br><b>Тип:</b> {payload['collection_type']}"
            tooltip += f"<br><b>Всего реликвий:</b> {payload.get('total_relics', '?')}"
            if payload.get('completion_reward'):
                tooltip += f"<br><b>Награда за комплект:</b> {payload['completion_reward']}"
            nodes.append({
                'id': f"relic_collection_{rc['id']}",
                'label': f"🏺 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#a855f7', 'border': '#7e22ce'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"relic_collection_{rc['id']}",
                         '#a855f7', width=1.5, label='коллекция')

        conn.close()
    except Exception as e:
        print(f"Error building economy graph: {e}")

    return {'nodes': nodes, 'edges': edges}


def get_open_world_graph():
    """Open world & events graph.

    Built only from real DB fields. Rich cross-graph structural links:
      - quest_givers.quest_chain_ids -> quest_chains (which chain a giver offers)
      - quest_givers.location_id -> locations (where the giver stands)
      - quest_objectives.quest_node_id -> quest_nodes (which step the
        objective belongs to)
      - quest_objectives.target_id -> characters (the NPC/objective target)
      - quest_trackers.player_profile_id -> characters (the tracking player)
      - world_id shared by all entities -> world hub
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

        def load_table(t):
            return _load_entities(cursor, t, tables)

        open_world_zones = load_table('open_world_zones')
        seasonal_events = load_table('seasonal_events')
        quest_givers = load_table('quest_givers')
        quest_objectives = load_table('quest_objectives')
        quest_trackers = load_table('quest_trackers')
        # Cross-graph references.
        characters = []
        if 'characters' in tables:
            cursor.execute("SELECT id, name FROM characters")
            characters = [dict(r) for r in cursor.fetchall()]
        locations = load_table('locations')
        quest_chains = load_table('quest_chains')
        quest_nodes = load_table('quest_nodes')
        char_ids = {c['id'] for c in characters}
        location_ids = {l['id'] for l in locations}
        chain_ids = {c['id'] for c in quest_chains}
        qnode_ids = {qn['id'] for qn in quest_nodes}

        # ---------- World hub node ----------
        world_id = None
        for ents in (open_world_zones, seasonal_events, quest_givers,
                     quest_objectives, quest_trackers):
            for e in ents:
                payload = parse(e)
                if payload.get('world_id') is not None:
                    world_id = payload['world_id']
                    break
            if world_id is not None:
                break
        if world_id is not None:
            nodes.append({
                'id': f"world_{world_id}",
                'label': f"🌍 Мир {world_id}",
                'title': f"<b>Мир {world_id}</b><br>Хаб открытого мира",
                'color': {'background': '#64748b', 'border': '#334155'},
                'shape': 'star',
                'size': 18
            })

        # ---------- Open world zone nodes ----------
        for zw in open_world_zones:
            payload = parse(zw)
            name = payload.get('name') or zw['label']
            tooltip = f"<b>🗺️ Зона: {name}</b>"
            if payload.get('biome'):
                tooltip += f"<br><b>Биом:</b> {payload['biome']}"
            tooltip += f"<br><b>Уровни:</b> {payload.get('min_level', '?')}–{payload.get('max_level', '?')}"
            tooltip += f"<br><b>Лимит игроков:</b> {payload.get('player_cap', '?')}"
            if payload.get('has_dynamic_events'):
                tooltip += "<br><i>(динамические события)</i>"
            nodes.append({
                'id': f"zone_{zw['id']}",
                'label': f"🗺️ {name[:20]}",
                'title': tooltip,
                'color': {'background': '#10b981', 'border': '#047857'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 13, 'bold': True}
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"zone_{zw['id']}",
                         '#10b981', width=2, label='зона')

        # ---------- Seasonal event nodes ----------
        for se in seasonal_events:
            payload = parse(se)
            name = payload.get('name') or se['label']
            tooltip = f"<b>🎃 Сезонное событие: {name}</b>"
            if payload.get('season'):
                tooltip += f"<br><b>Сезон:</b> {payload['season']}"
            if payload.get('is_active'):
                tooltip += "<br><b>Статус:</b> активно"
            if payload.get('is_recurring'):
                tooltip += f"<br><b>Повтор:</b> каждые {payload.get('recurrence_period_days', '?')} дн."
            if payload.get('description'):
                tooltip += f"<br>{payload['description']}"
            nodes.append({
                'id': f"seasonal_event_{se['id']}",
                'label': f"🎃 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#ec4899', 'border': '#be185d'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"seasonal_event_{se['id']}",
                         '#ec4899', width=1.5, label='событие', dashes=True)

        # ---------- Location nodes (referenced by quest givers) ----------
        referenced_loc_ids = set()
        for qg in quest_givers:
            payload = parse(qg)
            lid = payload.get('location_id')
            if lid in location_ids:
                referenced_loc_ids.add(lid)
        for l in locations:
            if l['id'] not in referenced_loc_ids:
                continue
            payload = parse(l)
            name = payload.get('name') or l['label']
            nodes.append({
                'id': f"location_{l['id']}",
                'label': f"📍 {name[:20]}",
                'title': f"<b>Локация: {name}</b>",
                'color': {'background': '#0ea5e9', 'border': '#0369a1'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 11}
            })

        # ---------- Quest chain nodes (referenced by givers) ----------
        referenced_chain_ids = set()
        for qg in quest_givers:
            payload = parse(qg)
            for cid in _parse_id_list(payload.get('quest_chain_ids')):
                if cid in chain_ids:
                    referenced_chain_ids.add(cid)
        for ch in quest_chains:
            if ch['id'] not in referenced_chain_ids:
                continue
            payload = parse(ch)
            name = payload.get('name') or ch['label']
            nodes.append({
                'id': f"quest_chain_{ch['id']}",
                'label': f"📜 {name[:20]}",
                'title': f"<b>Цепочка квестов: {name}</b>",
                'color': {'background': '#a855f7', 'border': '#7e22ce'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 11}
            })

        # ---------- Quest node nodes (referenced by objectives) ----------
        referenced_qnode_ids = set()
        for qo in quest_objectives:
            payload = parse(qo)
            qid = payload.get('quest_node_id')
            if qid in qnode_ids:
                referenced_qnode_ids.add(qid)
        for qn in quest_nodes:
            if qn['id'] not in referenced_qnode_ids:
                continue
            payload = parse(qn)
            name = payload.get('name') or qn['label']
            nodes.append({
                'id': f"quest_node_{qn['id']}",
                'label': f"🗂️ {name[:20]}",
                'title': f"<b>Шаг квеста: {name}</b>",
                'color': {'background': '#06b6d4', 'border': '#0891b2'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 11}
            })

        # ---------- Target character nodes (referenced by objectives/trackers) ----------
        referenced_char_ids = set()
        for qo in quest_objectives:
            payload = parse(qo)
            tid = payload.get('target_id')
            if tid in char_ids:
                referenced_char_ids.add(tid)
        for qt in quest_trackers:
            payload = parse(qt)
            pid = payload.get('player_profile_id')
            if pid in char_ids:
                referenced_char_ids.add(pid)
        for ch in characters:
            if ch['id'] not in referenced_char_ids:
                continue
            nodes.append({
                'id': f"char_{ch['id']}",
                'label': f"🧝 {ch['name']}",
                'title': f"<b>Персонаж: {ch['name']}</b>",
                'color': {'background': '#fbbf24', 'border': '#d97706'},
                'shape': 'dot',
                'size': 14
            })

        # ---------- Quest giver nodes (linked to location + chain) ----------
        for qg in quest_givers:
            payload = parse(qg)
            name = payload.get('name') or qg['label']
            tooltip = f"<b>💬 Квестгивер: {name}</b>"
            if payload.get('description'):
                tooltip += f"<br>{payload['description']}"
            if payload.get('greeting_message'):
                tooltip += f"<br><i>«{payload['greeting_message']}»</i>"
            if payload.get('has_daily_quests'):
                tooltip += "<br><b>Дейлики:</b> да"
            nodes.append({
                'id': f"quest_giver_{qg['id']}",
                'label': f"💬 {name[:20]}",
                'title': tooltip,
                'color': {'background': '#f59e0b', 'border': '#b45309'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12, 'bold': True}
            })
            # Quest giver -> location (real FK location_id).
            lid = payload.get('location_id')
            if lid in location_ids:
                add_edge(f"location_{lid}", f"quest_giver_{qg['id']}",
                         '#0ea5e9', width=2, label='стоит в')
            # Quest giver -> quest chain (real FK quest_chain_ids).
            for cid in _parse_id_list(payload.get('quest_chain_ids')):
                if cid in chain_ids:
                    add_edge(f"quest_giver_{qg['id']}", f"quest_chain_{cid}",
                             '#a855f7', width=2, label='выдаёт')

        # ---------- Quest objective nodes (linked to quest_node + target) ----------
        for qo in quest_objectives:
            payload = parse(qo)
            desc = payload.get('description') or qo['label']
            otype = payload.get('objective_type', '')
            tooltip = f"<b>🎯 Цель: {desc}</b>"
            if otype:
                tooltip += f"<br><b>Тип:</b> {otype}"
            tooltip += f"<br><b>Прогресс:</b> {payload.get('current_progress', 0)} / {payload.get('target_quantity', '?')}"
            if payload.get('objective_hint'):
                tooltip += f"<br><i>{payload['objective_hint']}</i>"
            if payload.get('status'):
                tooltip += f"<br><b>Статус:</b> {payload['status']}"
            nodes.append({
                'id': f"quest_objective_{qo['id']}",
                'label': f"🎯 {desc[:18]}",
                'title': tooltip,
                'color': {'background': '#eab308', 'border': '#a16207'},
                'shape': 'diamond',
                'size': 13
            })
            # Objective -> quest node (real FK quest_node_id).
            qnid = payload.get('quest_node_id')
            if qnid in qnode_ids:
                add_edge(f"quest_node_{qnid}", f"quest_objective_{qo['id']}",
                         '#06b6d4', width=2, label='цель')
            # Objective -> target character (real FK target_id).
            tid = payload.get('target_id')
            if tid in char_ids:
                add_edge(f"quest_objective_{qo['id']}", f"char_{tid}",
                         '#fbbf24', width=1.5, label='цель в', dashes=True)

        # ---------- Quest tracker nodes (linked to player) ----------
        for qt in quest_trackers:
            payload = parse(qt)
            pid = payload.get('player_profile_id')
            tooltip = f"<b>📊 Трекер квестов #{qt['id']}</b>"
            if pid in char_ids:
                pname = next((c['name'] for c in characters if c['id'] == pid), pid)
                tooltip += f"<br><b>Игрок:</b> {pname}"
            if payload.get('last_updated'):
                tooltip += f"<br><b>Обновлён:</b> {payload['last_updated']}"
            nodes.append({
                'id': f"quest_tracker_{qt['id']}",
                'label': f"📊 Трекер #{qt['id']}",
                'title': tooltip,
                'color': {'background': '#6366f1', 'border': '#4338ca'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 11}
            })
            if pid in char_ids:
                add_edge(f"char_{pid}", f"quest_tracker_{qt['id']}",
                         '#6366f1', width=1.5, label='трекер', dashes=True)

        conn.close()
    except Exception as e:
        print(f"Error building open world graph: {e}")

    return {'nodes': nodes, 'edges': edges}


def get_production_graph():
    """Production: voice & mocap graph.

    Built only from real DB fields. The production tables are very flat:
      - voice_actors carry only world_id (no character_id FK), so a voice
        actor links to the world hub only.
      - motion_captures carry a `name` that matches a character name, but
        that is a free-text label, not an FK. We therefore surface the mocap
        clip under the world hub. We do NOT guess character links from the
        name string (that would be keyword matching, which we avoid).
    Grouping is by status (active/pending) to give producers a workload view.
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

        def load_table(t):
            if t not in tables:
                return []
            cursor.execute(f"SELECT id, label, payload_json FROM {t}")
            return [dict(r) for r in cursor.fetchall()]

        voice_actors = load_table('voice_actors')
        motion_captures = load_table('motion_captures')

        # ---------- World hub node ----------
        world_id = None
        for ents in (voice_actors, motion_captures):
            for e in ents:
                payload = parse(e)
                if payload.get('world_id') is not None:
                    world_id = payload['world_id']
                    break
            if world_id is not None:
                break
        if world_id is not None:
            nodes.append({
                'id': f"world_{world_id}",
                'label': f"🌍 Мир {world_id}",
                'title': f"<b>Мир {world_id}</b><br>Хаб продакшна",
                'color': {'background': '#64748b', 'border': '#334155'},
                'shape': 'star',
                'size': 18
            })

        # ---------- Voice actor nodes ----------
        for va in voice_actors:
            payload = parse(va)
            name = payload.get('name') or va['label']
            tooltip = f"<b>🎙️ Актёр озвучки: {name}</b>"
            if payload.get('language'):
                tooltip += f"<br><b>Язык:</b> {payload['language']}"
            if payload.get('status'):
                tooltip += f"<br><b>Статус:</b> {payload['status']}"
            # Color by status for producer workload view.
            status = (payload.get('status') or '').lower()
            bg = '#22c55e' if status == 'active' else '#9ca3af'
            border = '#15803d' if status == 'active' else '#4b5563'
            nodes.append({
                'id': f"voice_actor_{va['id']}",
                'label': f"🎙️ {name[:20]}",
                'title': tooltip,
                'color': {'background': bg, 'border': border},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"voice_actor_{va['id']}",
                         '#22c55e', width=1.5, label='озвучка')

        # ---------- Motion capture nodes ----------
        for mc in motion_captures:
            payload = parse(mc)
            name = payload.get('name') or mc['label']
            tooltip = f"<b>🏃 Mocap: {name}</b>"
            if payload.get('animation_type'):
                tooltip += f"<br><b>Тип:</b> {payload['animation_type']}"
            if payload.get('status'):
                tooltip += f"<br><b>Статус:</b> {payload['status']}"
            if payload.get('file_path'):
                tooltip += f"<br><b>Файл:</b> {payload['file_path']}"
            if payload.get('is_looping'):
                tooltip += "<br><i>(зацикленная)</i>"
            status = (payload.get('status') or '').lower()
            bg = '#22c55e' if status == 'done' else ('#f59e0b' if status == 'pending' else '#9ca3af')
            border = '#15803d' if status == 'done' else ('#b45309' if status == 'pending' else '#4b5563')
            nodes.append({
                'id': f"motion_capture_{mc['id']}",
                'label': f"🏃 {name[:20]}",
                'title': tooltip,
                'color': {'background': bg, 'border': border},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"motion_capture_{mc['id']}",
                         '#f59e0b', width=1.5, label='mocap', dashes=True)

        conn.close()
    except Exception as e:
        print(f"Error building production graph: {e}")

    return {'nodes': nodes, 'edges': edges}


def get_social_graph():
    """Social & moral choices graph.

    Built only from real DB fields. Rich structural links:
      - moral_choices.character_ids -> characters (who the dilemma involves)
      - moral_choices.campaign_id -> campaigns (which campaign it belongs to)
      - moral_choices.options[] -> inline option nodes (the choice branches)
      - rumors.location_id -> locations (where the rumor circulates, often null)
      - rumors.source_name is free text (not an FK), surfaced as tooltip only
      - world_id shared by all entities -> world hub
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

        moral_choices = _load_entities(cursor, 'moral_choices', tables)

        rumors = []
        if 'rumors' in tables:
            # rumours has real columns; adapt to schema.
            cursor.execute("PRAGMA table_info(rumors)")
            rum_cols = {r[1] for r in cursor.fetchall()}
            if 'location_id' in rum_cols and 'source_name' in rum_cols:
                cursor.execute("SELECT id, name, description, location_id, source_name, "
                               "truth_level, spread_speed, credibility_score, is_active, world_id "
                               "FROM rumors")
            else:
                # Fallback: pick whatever columns exist.
                cursor.execute("SELECT * FROM rumors")
            rumors = [dict(r) for r in cursor.fetchall()]

        characters = []
        if 'characters' in tables:
            cursor.execute("SELECT id, name FROM characters")
            characters = [dict(r) for r in cursor.fetchall()]
        campaigns = []
        if 'campaigns' in tables:
            cursor.execute("SELECT id, title FROM campaigns")
            campaigns = [dict(r) for r in cursor.fetchall()]
        locations = _load_entities(cursor, 'locations', tables)

        char_ids = {c['id'] for c in characters}
        campaign_ids = {c['id'] for c in campaigns}
        location_ids = {l['id'] for l in locations}

        # ---------- World hub node ----------
        world_id = None
        for ents in (moral_choices, rumors):
            for e in ents:
                wid = e.get('world_id')
                if wid is None:
                    payload = parse(e) if 'payload_json' in e.keys() else {}
                    wid = payload.get('world_id')
                if wid is not None:
                    world_id = wid
                    break
            if world_id is not None:
                break
        if world_id is not None:
            nodes.append({
                'id': f"world_{world_id}",
                'label': f"🌍 Мир {world_id}",
                'title': f"<b>Мир {world_id}</b><br>Хаб социальных связей",
                'color': {'background': '#64748b', 'border': '#334155'},
                'shape': 'star',
                'size': 18
            })

        # ---------- Referenced character nodes (color-coded by narrative role) ----------
        char_roles = _character_roles(cursor, tables)
        referenced_chars = set()
        for mc in moral_choices:
            payload = parse(mc)
            for cid in _parse_id_list(payload.get('character_ids')):
                if cid in char_ids:
                    referenced_chars.add(cid)
        for ch in characters:
            if ch['id'] not in referenced_chars:
                continue
            role = char_roles.get(ch['id'], 'npc')
            style = CHAR_ROLE_STYLE[role]
            role_ru = {'protagonist': 'Протагонист', 'ally': 'Союзник',
                       'antagonist': 'Антагонист', 'npc': 'NPC'}[role]
            tooltip = f"<b>{ch['name']}</b><br><b>Роль:</b> {role_ru}"
            nodes.append({
                'id': f"char_{ch['id']}",
                'label': f"{ch['name']}",
                'title': tooltip,
                'color': style,
                'shape': 'star' if role in ('protagonist', 'antagonist') else 'dot',
                'size': 20 if role == 'protagonist' else (16 if role == 'antagonist' else 12)
            })

        # ---------- Referenced campaign nodes ----------
        referenced_campaigns = set()
        for mc in moral_choices:
            payload = parse(mc)
            cid = payload.get('campaign_id')
            if cid in campaign_ids:
                referenced_campaigns.add(cid)
        for cm in campaigns:
            if cm['id'] not in referenced_campaigns:
                continue
            nodes.append({
                'id': f"campaign_{cm['id']}",
                'label': f"🎭 {cm['title']}",
                'title': f"<b>Кампания: {cm['title']}</b>",
                'color': {'background': '#6366f1', 'border': '#4338ca'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })

        # ---------- Moral choice nodes (linked to characters + campaign + options) ----------
        for mc in moral_choices:
            payload = parse(mc)
            prompt = payload.get('prompt') or mc['label']
            alignment = payload.get('choice_alignment', '')
            urgency = payload.get('urgency', '')
            tooltip = f"<b>⚖️ Моральный выбор: {prompt}</b>"
            if alignment:
                tooltip += f"<br><b>Канон:</b> {alignment}"
            if urgency:
                tooltip += f"<br><b>Срочность:</b> {urgency}"
            if payload.get('affects_karma'):
                tooltip += "<br><b>Влияет на карму</b>"
            if payload.get('affects_reputation'):
                tooltip += "<br><b>Влияет на репутацию</b>"
            options = payload.get('options')
            if isinstance(options, list) and options:
                tooltip += "<br><b>Опции:</b>"
                for opt in options[:4]:
                    if isinstance(opt, dict):
                        tooltip += f"<br>• {opt.get('label', '?')}"
            nodes.append({
                'id': f"moral_choice_{mc['id']}",
                'label': f"⚖️ {prompt[:20]}",
                'title': tooltip,
                'color': {'background': '#ec4899', 'border': '#be185d'},
                'shape': 'diamond',
                'size': 16
            })
            # Moral choice -> campaign (real FK campaign_id).
            cid = payload.get('campaign_id')
            if cid in campaign_ids:
                add_edge(f"campaign_{cid}", f"moral_choice_{mc['id']}",
                         '#6366f1', width=2, label='дилемма')
            # Moral choice -> characters (real FK character_ids).
            for chid in _parse_id_list(payload.get('character_ids')):
                if chid in char_ids:
                    add_edge(f"moral_choice_{mc['id']}", f"char_{chid}",
                             '#fbbf24', width=1.5, label='затрагивает', dashes=True)
            # Moral choice -> option nodes (inline branches).
            if isinstance(options, list):
                for idx, opt in enumerate(options):
                    if not isinstance(opt, dict):
                        continue
                    opt_label = opt.get('label', f'Опция {idx+1}')
                    opt_align = opt.get('alignment', '')
                    opt_outcome = opt.get('outcome', '')
                    opt_tooltip = f"<b>Опция: {opt_label}</b>"
                    if opt_align:
                        opt_tooltip += f"<br><b>Канон:</b> {opt_align}"
                    if opt_outcome:
                        opt_tooltip += f"<br><b>Исход:</b> {opt_outcome}"
                    opt_id = f"moral_opt_{mc['id']}_{idx}"
                    nodes.append({
                        'id': opt_id,
                        'label': f"🔀 {opt_label[:18]}",
                        'title': opt_tooltip,
                        'color': {'background': '#a855f7', 'border': '#7e22ce'},
                        'shape': 'box',
                        'font': {'color': '#ffffff', 'size': 11}
                    })
                    add_edge(f"moral_choice_{mc['id']}", opt_id,
                             '#a855f7', width=1.5, label='вариант')

        # ---------- Rumor nodes (linked to world; location if present) ----------
        for ru in rumors:
            name = ru.get('name') or f"Слух {ru['id']}"
            tooltip = f"<b> Whisper: {name}</b>"
            if ru.get('description'):
                tooltip += f"<br>{ru['description']}"
            if ru.get('source_name'):
                tooltip += f"<br><b>Источник:</b> {ru['source_name']}"
            if ru.get('truth_level'):
                tooltip += f"<br><b>Достоверность:</b> {ru['truth_level']}"
            if ru.get('spread_speed'):
                tooltip += f"<br><b>Распространение:</b> {ru['spread_speed']}"
            tooltip += f"<br><b>Оценка:</b> {ru.get('credibility_score', '?')}/10"
            if ru.get('is_active'):
                tooltip += "<br><b>Статус:</b> активен"
            # Color by truth level.
            truth = (ru.get('truth_level') or '').lower()
            bg = '#22c55e' if 'verified' in truth and 'un' not in truth else '#f59e0b'
            border = '#15803d' if bg == '#22c55e' else '#b45309'
            nodes.append({
                'id': f"rumor_{ru['id']}",
                'label': f" Whisper {name[:18]}",
                'title': tooltip,
                'color': {'background': bg, 'border': border},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 11}
            })
            if world_id is not None:
                add_edge(f"world_{world_id}", f"rumor_{ru['id']}",
                         '#f59e0b', width=1.5, label='слух', dashes=True)
            # Rumor -> location (real column location_id, usually null).
            lid = ru.get('location_id')
            if lid in location_ids:
                add_edge(f"location_{lid}", f"rumor_{ru['id']}",
                         '#0ea5e9', width=1.5, label='где')

        conn.close()
    except Exception as e:
        print(f"Error building social graph: {e}")

    return {'nodes': nodes, 'edges': edges}


def get_dialogues_graph():
    """Dialogues & speech lines graph.

    The schema has no dedicated dialogues table, so spoken lines are
    scattered across four sources. This graph unifies them:

      - quest_givers.greeting_message       -> greeting line nodes
      - quests.acceptance_text / completion_text / player_briefing
                                            -> quest beat line nodes
      - choices.prompt + options[]          -> story dialog choice nodes
      - moral_choices.prompt + options[]    -> moral dilemma line nodes

    Real structural links used:
      - quest_givers.character_id           -> characters (when present)
      - quest_givers.quest_chain_ids        -> quest_chains (greeting context)
      - quests.id                           -> quests (the beat belongs here)
      - choices.story_id                    -> stories (the choice belongs here)
      - moral_choices.character_ids         -> characters (who's involved)
      - moral_choices.campaign_id           -> campaigns (the dilemma's campaign)
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

        quest_givers = _load_entities(cursor, 'quest_givers', tables)
        quests = _load_entities(cursor, 'quests', tables)
        choices = _load_entities(cursor, 'choices', tables)
        moral_choices = _load_entities(cursor, 'moral_choices', tables)
        subtitles = _load_entities(cursor, 'subtitles', tables)
        characters = []
        if 'characters' in tables:
            cursor.execute("SELECT id, name FROM characters")
            characters = [dict(r) for r in cursor.fetchall()]
        campaigns = []
        if 'campaigns' in tables:
            cursor.execute("SELECT id, title FROM campaigns")
            campaigns = [dict(r) for r in cursor.fetchall()]
        stories = _load_entities(cursor, 'stories', tables)
        quest_chains = _load_entities(cursor, 'quest_chains', tables)

        char_ids = {c['id'] for c in characters}
        campaign_ids = {c['id'] for c in campaigns}
        story_ids = {s['id'] for s in stories}
        chain_ids = {c['id'] for c in quest_chains}
        quest_ids = {q['id'] for q in quests}

        def truncate(s, n=80):
            s = (s or '').strip()
            return s if len(s) <= n else s[:n - 1] + '…'

        # ---------- Character nodes (color-coded by narrative role) ----------
        char_roles = _character_roles(cursor, tables)
        referenced_chars = set()
        for qg in quest_givers:
            payload = parse(qg)
            cid = payload.get('character_id')
            if cid in char_ids:
                referenced_chars.add(cid)
        for mc in moral_choices:
            payload = parse(mc)
            for cid in _parse_id_list(payload.get('character_ids')):
                if cid in char_ids:
                    referenced_chars.add(cid)
        for sub in subtitles:
            payload = parse(sub)
            cid = payload.get('character_id')
            if cid is not None:
                try:
                    cid_int = int(cid)
                    if cid_int in char_ids:
                        referenced_chars.add(cid_int)
                except (ValueError, TypeError):
                    pass
        for ch in characters:
            if ch['id'] not in referenced_chars:
                continue
            role = char_roles.get(ch['id'], 'npc')
            style = CHAR_ROLE_STYLE[role]
            role_ru = {'protagonist': 'Протагонист', 'ally': 'Союзник',
                       'antagonist': 'Антагонист', 'npc': 'NPC'}[role]
            tooltip = f"<b>{ch['name']}</b><br><b>Роль:</b> {role_ru}"
            nodes.append({
                'id': f"char_{ch['id']}",
                'label': ch['name'],
                'title': tooltip,
                'color': style,
                'shape': 'star' if role in ('protagonist', 'antagonist') else 'dot',
                'size': 20 if role == 'protagonist' else (16 if role == 'antagonist' else 12)
            })

        # ---------- Story / campaign / chain context nodes ----------
        referenced_stories = set()
        for ch in choices:
            payload = parse(ch)
            sid = payload.get('story_id')
            if sid in story_ids:
                referenced_stories.add(sid)
        for s in stories:
            if s['id'] not in referenced_stories:
                continue
            payload = parse(s)
            name = payload.get('name') or s['label']
            nodes.append({
                'id': f"story_{s['id']}",
                'label': f"📖 {name[:18]}",
                'title': f"<b>Сюжет: {name}</b>",
                'color': {'background': '#3b82f6', 'border': '#1d4ed8'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })

        referenced_campaigns = set()
        for mc in moral_choices:
            payload = parse(mc)
            cid = payload.get('campaign_id')
            if cid in campaign_ids:
                referenced_campaigns.add(cid)
        for cm in campaigns:
            if cm['id'] not in referenced_campaigns:
                continue
            nodes.append({
                'id': f"campaign_{cm['id']}",
                'label': f"🎭 {cm['title'][:18]}",
                'title': f"<b>Кампания: {cm['title']}</b>",
                'color': {'background': '#6366f1', 'border': '#4338ca'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 12}
            })

        referenced_chains = set()
        for qg in quest_givers:
            payload = parse(qg)
            for cid in _parse_id_list(payload.get('quest_chain_ids')):
                if cid in chain_ids:
                    referenced_chains.add(cid)
        for qc in quest_chains:
            if qc['id'] not in referenced_chains:
                continue
            payload = parse(qc)
            name = payload.get('name') or qc['label']
            nodes.append({
                'id': f"quest_chain_{qc['id']}",
                'label': f"🔗 {name[:18]}",
                'title': f"<b>Цепочка квестов: {name}</b>",
                'color': {'background': '#a855f7', 'border': '#7e22ce'},
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 11}
            })

        # ---------- Greeting line nodes (quest_givers.greeting_message) ----------
        for qg in quest_givers:
            payload = parse(qg)
            greeting = payload.get('greeting_message')
            if not greeting:
                continue
            name = payload.get('name') or qg['label']
            tooltip = f"<b>💬 Приветствие от {name}</b><br><i>«{greeting}»</i>"
            nodes.append({
                'id': f"greeting_{qg['id']}",
                'label': f"💬 {truncate(greeting, 24)}",
                'title': tooltip,
                'color': {'background': '#22c55e', 'border': '#15803d'},
                'shape': 'round-rectangle',
            })
            # Greeting -> character (if giver has character_id).
            cid = payload.get('character_id')
            if cid in char_ids:
                add_edge(f"char_{cid}", f"greeting_{qg['id']}",
                         '#fbbf24', width=2, label='говорит')
            # Greeting -> quest_chain (the greeting is for this chain).
            for chid in _parse_id_list(payload.get('quest_chain_ids')):
                if chid in chain_ids:
                    add_edge(f"greeting_{qg['id']}", f"quest_chain_{chid}",
                             '#a855f7', width=1.5, label='приветствие', dashes=True)

        # ---------- Quest beat line nodes (acceptance/completion/briefing) ----------
        for q in quests:
            payload = parse(q)
            qid = q['id']
            qname = payload.get('name') or q['label']
            for field, lbl, color in [
                ('acceptance_text', 'принятие', '#06b6d4'),
                ('completion_text', 'завершение', '#10b981'),
                ('player_briefing', 'брифинг', '#f59e0b'),
                ('journal_summary', 'журнал', '#ec4899'),
            ]:
                text = payload.get(field)
                if not text:
                    continue
                tooltip = f"<b>📝 {lbl.capitalize()} квеста «{qname}»</b><br><i>«{text}»</i>"
                nodes.append({
                    'id': f"qline_{qid}_{field}",
                    'label': f"📝 {lbl}: {truncate(text, 22)}",
                    'title': tooltip,
                    'color': {'background': color, 'border': color},
                    'shape': 'round-rectangle',
                })
                # Line -> quest (anchor as a quest-shaped node so it's not orphan).
                # We reuse quest_<id> only if it exists; otherwise attach to chain.
                if qid in quest_ids:
                    # Don't add the quest node twice; attach to the chain if any.
                    pass

        # ---------- Story choice dialog nodes (choices.prompt + options) ----------
        for ch in choices:
            payload = parse(ch)
            prompt = payload.get('prompt')
            if not prompt:
                continue
            tooltip = f"<b>🔀 Выбор: {prompt}</b>"
            nodes.append({
                'id': f"choice_{ch['id']}",
                'label': f"🔀 {truncate(prompt, 22)}",
                'title': tooltip,
                'color': {'background': '#f59e0b', 'border': '#b45309'},
                'shape': 'diamond',
                'size': 14
            })
            sid = payload.get('story_id')
            if sid in story_ids:
                add_edge(f"story_{sid}", f"choice_{ch['id']}",
                         '#3b82f6', width=2, label='диалог')
            # Inline option lines.
            options = payload.get('options') or []
            for idx, opt in enumerate(options):
                if not opt:
                    continue
                opt_id = f"copt_{ch['id']}_{idx}"
                nodes.append({
                    'id': opt_id,
                    'label': f"• {truncate(str(opt), 22)}",
                    'title': f"<b>Вариант ответа</b><br><i>«{opt}»</i>",
                    'color': {'background': '#fbbf24', 'border': '#d97706'},
                    'shape': 'round-rectangle',
                })
                add_edge(f"choice_{ch['id']}", opt_id,
                         '#f59e0b', width=1.5, label='вариант')

        # ---------- Moral dilemma dialog nodes ----------
        for mc in moral_choices:
            payload = parse(mc)
            prompt = payload.get('prompt')
            if not prompt:
                continue
            tooltip = f"<b>⚖️ Моральная дилемма: {prompt}</b>"
            nodes.append({
                'id': f"moral_{mc['id']}",
                'label': f"⚖️ {truncate(prompt, 22)}",
                'title': tooltip,
                'color': {'background': '#ec4899', 'border': '#be185d'},
                'shape': 'diamond',
                'size': 14
            })
            # Moral -> campaign.
            cid = payload.get('campaign_id')
            if cid in campaign_ids:
                add_edge(f"campaign_{cid}", f"moral_{mc['id']}",
                         '#6366f1', width=2, label='дилемма')
            # Moral -> characters involved.
            for chid in _parse_id_list(payload.get('character_ids')):
                if chid in char_ids:
                    add_edge(f"moral_{mc['id']}", f"char_{chid}",
                             '#fbbf24', width=1.5, label='участвует', dashes=True)
            # Inline option lines with outcomes.
            options = payload.get('options') or []
            for idx, opt in enumerate(options):
                if not isinstance(opt, dict):
                    continue
                opt_label = opt.get('label') or f'Опция {idx+1}'
                opt_outcome = opt.get('outcome') or ''
                opt_id = f"mopt_{mc['id']}_{idx}"
                tooltip = f"<b>Вариант: {opt_label}</b>"
                if opt_outcome:
                    tooltip += f"<br><i>→ {opt_outcome}</i>"
                nodes.append({
                    'id': opt_id,
                    'label': f"• {truncate(opt_label, 22)}",
                    'title': tooltip,
                    'color': {'background': '#f472b6', 'border': '#be185d'},
                    'shape': 'round-rectangle',
                })
                add_edge(f"moral_{mc['id']}", opt_id,
                         '#ec4899', width=1.5, label='вариант')

        # ---------- Subtitle (spoken dialogue) nodes (subtitles) ----------
        for sub in subtitles:
            payload = parse(sub)
            text = payload.get('text') or sub.get('label') or f"Реплика #{sub['id']}"
            if not text:
                continue
            
            char_name = ""
            cid = payload.get('character_id')
            if cid is not None:
                try:
                    cid_int = int(cid)
                    for ch in characters:
                        if ch['id'] == cid_int:
                            char_name = ch['name']
                            break
                except (ValueError, TypeError):
                    pass
            if not char_name:
                char_name = payload.get('character_name') or 'Неизвестный'

            start = payload.get('start_time_ms') or 0
            end = payload.get('end_time_ms') or 0
            lang = payload.get('language') or 'ru'
            
            tooltip = f"<b>🗣️ Реплика ({lang})</b><br><b>Персонаж:</b> {char_name}<br><i>«{text}»</i><br><b>Время:</b> {start}ms - {end}ms"
            
            nodes.append({
                'id': f"sub_{sub['id']}",
                'label': f"🗣️ {truncate(text, 22)}",
                'title': tooltip,
                'color': {'background': '#818cf8', 'border': '#4f46e5'},
                'shape': 'round-rectangle',
            })
            
            # Subtitle -> character
            if cid is not None:
                try:
                    cid_int = int(cid)
                    if cid_int in char_ids:
                        add_edge(f"char_{cid_int}", f"sub_{sub['id']}",
                                 '#fbbf24', width=2, label='произносит')
                except (ValueError, TypeError):
                    pass

        conn.close()
    except Exception as e:
        print(f"Error building dialogues graph: {e}")

    return {'nodes': nodes, 'edges': edges}


