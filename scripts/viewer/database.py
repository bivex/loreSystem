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
        
        worlds = []
        if 'worlds' in tables:
            cursor.execute("SELECT id, name, description FROM worlds")
            worlds = [dict(row) for row in cursor.fetchall()]
            
        locations = []
        if 'locations' in tables:
            cursor.execute("SELECT id, name, world_id, parent_location_id, location_type, description FROM locations")
            locations = [dict(row) for row in cursor.fetchall()]
            
        conn.close()
        
        # Add worlds as root nodes
        for w in worlds:
            desc = w.get('description', '')
            if desc and desc.startswith('{'):
                try:
                    desc = json.loads(desc).get('value', desc)
                except Exception:
                    pass
            tooltip = f"<b>Мир: {w['name']}</b><br>Описание: {desc}"
            nodes.append({
                'id': f"world_{w['id']}",
                'label': w['name'],
                'title': tooltip,
                'color': {
                    'background': '#10b981',
                    'border': '#065f46'
                },
                'shape': 'box',
                'font': {'color': '#ffffff', 'size': 14, 'bold': True}
            })
            
        # Add locations
        for loc in locations:
            l_type = loc.get('location_type', 'N/A')
            desc = loc.get('description', '')
            if desc and desc.startswith('{'):
                try:
                    desc = json.loads(desc).get('value', desc)
                except Exception:
                    pass
            tooltip = f"<b>Локация: {loc['name']}</b><br>Тип: {l_type}<br>Описание: {desc}"
            
            nodes.append({
                'id': f"loc_{loc['id']}",
                'label': loc['name'],
                'title': tooltip,
                'color': {
                    'background': '#3b82f6',
                    'border': '#1e3a8a'
                },
                'shape': 'dot',
                'size': 15
            })
            
            parent_id = loc.get('parent_location_id')
            world_id = loc.get('world_id')
            
            if parent_id:
                edges.append({
                    'from': f"loc_{parent_id}",
                    'to': f"loc_{loc['id']}",
                    'arrows': 'to',
                    'color': '#3b82f6',
                    'width': 2
                })
            elif world_id:
                edges.append({
                    'from': f"world_{world_id}",
                    'to': f"loc_{loc['id']}",
                    'arrows': 'to',
                    'color': '#10b981',
                    'width': 2
                })
                
    except Exception as e:
        print(f"Error building location graph: {e}")
        
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
            
        node_to_quest_map = {}
        for qc in quest_chains:
            payload = {}
            if qc.get('payload_json'):
                try:
                    payload = json.loads(qc['payload_json'])
                except Exception:
                    pass
            quest_id = payload.get('quest_id')
            node_ids = payload.get('quest_node_ids', [])
            
            if quest_id and isinstance(node_ids, list):
                for nid in node_ids:
                    node_to_quest_map[nid] = quest_id
                    
        node_id_list = set()
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
                
        for qc in quest_chains:
            payload = {}
            if qc.get('payload_json'):
                try:
                    payload = json.loads(qc['payload_json'])
                except Exception:
                    pass
            node_ids = payload.get('quest_node_ids', [])
            if isinstance(node_ids, list) and len(node_ids) > 1:
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
