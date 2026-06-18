#!/usr/bin/env python3
"""
Кросс-табличный валидатор логической целостности лора (Lore Consistency & Logic Validator).
Проверяет базу данных SQLite на наличие логических противоречий, оборванных связей (dangling FK) и нарушений бизнес-правил.
"""

import sqlite3
import json
import os
import sys
import argparse
from datetime import datetime

# Настройка цветов вывода (ANSI escape-коды)
USE_COLOR = sys.stdout.isatty()

def colored(text, color_code):
    if USE_COLOR:
        return f"\033[{color_code}m{text}\033[0m"
    return text

class LoreValidator:
    def __init__(self, db_path='lore_system.db'):
        self.db_path = db_path
        self.conn = None
        self.cur = None
        self.errors = []
        self.tables = set()
        
    def connect(self):
        if not os.path.exists(self.db_path):
            print(colored(f"Ошибка: Файл базы данных не найден по пути {os.path.abspath(self.db_path)}", "91;1"))
            sys.exit(1)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self.tables = self._get_tables()

    def close(self):
        if self.conn:
            self.conn.close()

    def _get_tables(self):
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return {row['name'] for row in self.cur.fetchall()}

    def _has_table(self, table_name):
        return table_name in self.tables

    def add_error(self, table, entity_id, err_type, severity, description):
        self.errors.append({
            "table": table,
            "id": entity_id,
            "type": err_type,
            "severity": severity,
            "description": description
        })

    def run_all_checks(self):
        self.errors = []
        self._check_characters()
        self._check_relationships()
        self._check_events()
        self._check_cursed_items()
        self._check_items()
        self._check_quests_and_nodes()
        self._check_quest_cycles()
        return self.errors

    def _check_characters(self):
        if not self._has_table('characters'):
            return
        try:
            self.cur.execute("SELECT id, name, backstory, status, abilities, rarity, element, role, base_hp, base_atk, base_def, base_speed, energy_cost FROM characters")
            rows = self.cur.fetchall()
            
            for row in rows:
                cid = row['id']
                name = row['name']
                backstory = row['backstory']
                status = row['status']
                abilities_str = row['abilities']
                rarity = row['rarity']
                element = row['element']
                role = row['role']
                hp = row['base_hp']
                atk = row['base_atk']
                defense = row['base_def']
                speed = row['base_speed']
                energy = row['energy_cost']
                
                # Name check
                if not name or not str(name).strip():
                    self.add_error('characters', cid, 'empty_name', 'error', "Имя персонажа не может быть пустым")
                    
                # Backstory check
                if backstory and len(str(backstory).strip()) < 100:
                    self.add_error('characters', cid, 'short_backstory', 'warning', 
                                   f"Предыстория персонажа слишком короткая ({len(str(backstory).strip())} симв., ожидается >= 100)")
                                   
                # Stats check
                for stat_name, val in [('base_hp', hp), ('base_atk', atk), ('base_def', defense), ('base_speed', speed), ('energy_cost', energy)]:
                    if val is not None and val < 0:
                        self.add_error('characters', cid, 'negative_stat', 'error', f"Характеристика '{stat_name}' не может быть отрицательной ({val})")
                        
                # Enums checks
                valid_rarities = {'common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic', 'cursed', 'forbidden'}
                if rarity and str(rarity).lower() not in valid_rarities:
                    self.add_error('characters', cid, 'domain_invariant', 'error', 
                                   f"Недопустимая редкость '{rarity}', ожидается одна из {sorted(list(valid_rarities))}")
                                   
                valid_elements = {'fire', 'water', 'earth', 'wind', 'light', 'dark', 'physical'}
                if element and str(element).lower() not in valid_elements:
                    self.add_error('characters', cid, 'domain_invariant', 'error', 
                                   f"Недопустимая стихия '{element}', ожидается одна из {sorted(list(valid_elements))}")
                                   
                valid_roles = {'dps', 'tank', 'support', 'specialist'}
                if role and str(role).lower() not in valid_roles:
                    self.add_error('characters', cid, 'domain_invariant', 'error', 
                                   f"Недопустимая роль '{role}', ожидается одна из {sorted(list(valid_roles))}")
                                   
                # Abilities check
                if abilities_str:
                    try:
                        abilities = json.loads(abilities_str)
                        if isinstance(abilities, list):
                            ability_names = []
                            for ab in abilities:
                                if isinstance(ab, dict) and 'name' in ab:
                                    ability_names.append(ab['name'])
                                elif isinstance(ab, str):
                                    ability_names.append(ab)
                            
                            dupes = {x for x in ability_names if ability_names.count(x) > 1}
                            if dupes:
                                self.add_error('characters', cid, 'logical_contradiction', 'error', 
                                               f"Персонаж имеет дублирующиеся способности: {sorted(list(dupes))}")
                    except json.JSONDecodeError:
                        self.add_error('characters', cid, 'invalid_json', 'error', "Поле abilities содержит невалидный JSON")
        except sqlite3.OperationalError as e:
            self.add_error('characters', 'N/A', 'operational_error', 'error', f"Ошибка чтения таблицы characters: {e}")

    def _check_relationships(self):
        if not self._has_table('character_relationships'):
            return
        try:
            character_ids = set()
            if self._has_table('characters'):
                self.cur.execute("SELECT id FROM characters")
                character_ids = {r['id'] for r in self.cur.fetchall()}
                
            self.cur.execute("SELECT id, character_from_id, character_to_id, relationship_type, relationship_level, is_mutual FROM character_relationships")
            rows = self.cur.fetchall()
            
            rel_map = {}
            
            for row in rows:
                rid = row['id']
                c_from = row['character_from_id']
                c_to = row['character_to_id']
                r_type = row['relationship_type']
                r_level = row['relationship_level']
                is_mut = row['is_mutual']
                
                # Dangling FKs
                if c_from not in character_ids:
                    self.add_error('character_relationships', rid, 'dangling_fk', 'error', 
                                   f"character_from_id ({c_from}) ссылается на несуществующего персонажа")
                if c_to not in character_ids:
                    self.add_error('character_relationships', rid, 'dangling_fk', 'error', 
                                   f"character_to_id ({c_to}) ссылается на несуществующего персонажа")
                                   
                # Self relationship
                if c_from == c_to:
                    self.add_error('character_relationships', rid, 'logical_contradiction', 'error', 
                                   f"Персонаж {c_from} имеет связь с самим собой")
                                   
                # Semantic level conflict
                if r_type == 'ally' and r_level is not None and r_level < -20:
                    self.add_error('character_relationships', rid, 'semantic_conflict', 'error', 
                                   f"Связь 'ally' (союзник) имеет слишком низкий уровень ({r_level})")
                if r_type == 'enemy' and r_level is not None and r_level > 20:
                    self.add_error('character_relationships', rid, 'semantic_conflict', 'error', 
                                   f"Связь 'enemy' (враг) имеет слишком высокий уровень ({r_level})")
                                   
                rel_map[(c_from, c_to)] = {
                    'id': rid,
                    'type': r_type,
                    'level': r_level,
                    'is_mutual': is_mut
                }
                
            for (c_from, c_to), rel in rel_map.items():
                rid = rel['id']
                r_type = rel['type']
                r_level = rel['level']
                is_mut = rel['is_mutual']
                
                rev_key = (c_to, c_from)
                if rev_key in rel_map:
                    rev_rel = rel_map[rev_key]
                    rev_type = rev_rel['type']
                    rev_level = rev_rel['level']
                    
                    if is_mut:
                        if r_type != rev_type:
                            self.add_error('character_relationships', rid, 'logical_contradiction', 'error', 
                                           f"Взаимная связь ({c_from} -> {c_to}) имеет тип '{r_type}', но обратная связь ({c_to} -> {c_from}) имеет тип '{rev_type}'")
                        elif r_level is not None and rev_level is not None and abs(r_level - rev_level) > 20:
                            self.add_error('character_relationships', rid, 'logical_contradiction', 'warning', 
                                           f"Взаимная связь имеет большую разницу в уровнях симпатии ({r_level} против {rev_level})")
                                       
        except sqlite3.OperationalError as e:
            self.add_error('character_relationships', 'N/A', 'operational_error', 'error', f"Ошибка чтения таблицы character_relationships: {e}")

    def _check_events(self):
        if not self._has_table('events'):
            return
        try:
            character_ids = set()
            if self._has_table('characters'):
                self.cur.execute("SELECT id FROM characters")
                character_ids = {r['id'] for r in self.cur.fetchall()}
                
            self.cur.execute("SELECT id, name, start_date, end_date, outcome, participant_ids FROM events")
            rows = self.cur.fetchall()
            
            for row in rows:
                eid = row['id']
                name = row['name']
                start = row['start_date']
                end = row['end_date']
                outcome = row['outcome']
                parts_str = row['participant_ids']
                
                if not name or not str(name).strip():
                    self.add_error('events', eid, 'empty_name', 'error', "Название события не может быть пустым")
                    
                if parts_str:
                    try:
                        participants = json.loads(parts_str)
                        if not isinstance(participants, list):
                            self.add_error('events', eid, 'invalid_json', 'error', "Поле participant_ids должно содержать JSON список")
                        elif len(participants) == 0:
                            self.add_error('events', eid, 'domain_invariant', 'error', "Событие должно иметь хотя бы одного участника")
                        else:
                            if len(set(participants)) != len(participants):
                                self.add_error('events', eid, 'logical_contradiction', 'error', "Список участников события содержит дубликаты")
                            for pid in participants:
                                if pid not in character_ids:
                                    self.add_error('events', eid, 'dangling_fk', 'error', 
                                                   f"Участник с ID {pid} не существует в таблице characters")
                    except json.JSONDecodeError:
                        self.add_error('events', eid, 'invalid_json', 'error', "Поле participant_ids содержит невалидный JSON")
                else:
                    self.add_error('events', eid, 'domain_invariant', 'error', "Событие не содержит списка участников")
                    
                if start and end:
                    try:
                        def parse_dt(d_str):
                            clean_str = d_str.split('+')[0].split('Z')[0]
                            for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                                try:
                                    return datetime.strptime(clean_str, fmt)
                                except ValueError:
                                    pass
                            return None
                        
                        dt_start = parse_dt(start)
                        dt_end = parse_dt(end)
                        if dt_start and dt_end and dt_end < dt_start:
                            self.add_error('events', eid, 'logical_contradiction', 'error', 
                                           f"Дата окончания события ({end}) раньше даты начала ({start})")
                    except Exception:
                        pass
                        
                valid_outcomes = {'success', 'failure', 'ongoing'}
                if outcome and str(outcome).lower() not in valid_outcomes:
                    self.add_error('events', eid, 'domain_invariant', 'error', 
                                   f"Недопустимый результат события '{outcome}', ожидается один из {sorted(list(valid_outcomes))}")
        except sqlite3.OperationalError as e:
            self.add_error('events', 'N/A', 'operational_error', 'error', f"Ошибка чтения таблицы events: {e}")

    def _check_cursed_items(self):
        if not self._has_table('cursed_items'):
            return
        try:
            self.cur.execute("SELECT id, label, payload_json FROM cursed_items")
            rows = self.cur.fetchall()
            
            for row in rows:
                cid = row['id']
                label = row['label']
                payload_str = row['payload_json']
                
                if not label or not str(label).strip():
                    self.add_error('cursed_items', cid, 'empty_name', 'error', "Ярлык проклятого предмета не может быть пустым")
                    
                if payload_str:
                    try:
                        payload = json.loads(payload_str)
                        name = payload.get('name')
                        rarity = payload.get('rarity')
                        risk = payload.get('risk_level')
                        ctrl = payload.get('control_level')
                        poss = payload.get('possession_chance')
                        corr = payload.get('corruption_level')
                        
                        if not name or not str(name).strip():
                            self.add_error('cursed_items', cid, 'empty_name', 'error', "Имя проклятого предмета в JSON не может быть пустым")
                            
                        valid_rarities = {"rare", "epic", "legendary", "cursed", "forbidden"}
                        valid_risks = {"low", "medium", "high", "extreme"}
                        
                        if rarity and str(rarity).lower() not in valid_rarities:
                            self.add_error('cursed_items', cid, 'domain_invariant', 'error', 
                                           f"Предмет '{name}' имеет невалидную редкость '{rarity}' (ожидается одна из {sorted(list(valid_rarities))})")
                        if risk and str(risk).lower() not in valid_risks:
                            self.add_error('cursed_items', cid, 'domain_invariant', 'error', 
                                           f"Предмет '{name}' имеет невалидный risk_level '{risk}' (ожидается один из {sorted(list(valid_risks))})")
                        
                        for field_name, value in [("control_level", ctrl), ("possession_chance", poss), ("corruption_level", corr)]:
                            if value is not None:
                                try:
                                    val_num = float(value)
                                    if not (0 <= val_num <= 100):
                                        self.add_error('cursed_items', cid, 'bounds_violation', 'error', 
                                                       f"Предмет '{name}': значение '{field_name}' ({val_num}) выходит за рамки [0, 100]")
                                except (ValueError, TypeError):
                                    self.add_error('cursed_items', cid, 'domain_invariant', 'error', 
                                                   f"Предмет '{name}': невалидный тип значения для '{field_name}': {value}")
                    except json.JSONDecodeError:
                        self.add_error('cursed_items', cid, 'invalid_json', 'error', "payload_json содержит невалидный JSON")
        except sqlite3.OperationalError as e:
            self.add_error('cursed_items', 'N/A', 'operational_error', 'error', f"Ошибка чтения таблицы cursed_items: {e}")


    def _check_items(self):
        if not self._has_table('items'):
            return
        try:
            self.cur.execute("SELECT id, label, payload_json FROM items")
            rows = self.cur.fetchall()
            
            for row in rows:
                iid = row['id']
                label = row['label']
                payload_str = row['payload_json']
                
                if not label or not str(label).strip():
                    self.add_error('items', iid, 'empty_name', 'error', "Ярлык предмета не может быть пустым")
                    
                if payload_str:
                    try:
                        payload = json.loads(payload_str)
                        name = payload.get('name')
                        lvl = payload.get('level')
                        atk = payload.get('base_atk')
                        df = payload.get('base_def')
                        hp = payload.get('base_hp')
                        enh = payload.get('enhancement')
                        max_enh = payload.get('max_enhancement')
                        i_type = payload.get('item_type')
                        rarity = payload.get('rarity')
                        
                        if not name or not str(name).strip():
                            self.add_error('items', iid, 'empty_name', 'error', "Имя предмета в payload_json не может быть пустым")
                            
                        if lvl is not None:
                            try:
                                lvl_val = int(lvl)
                                if not (1 <= lvl_val <= 100):
                                    self.add_error('items', iid, 'bounds_violation', 'error', f"Уровень предмета '{name}' ({lvl_val}) выходит за рамки [1, 100]")
                            except (ValueError, TypeError):
                                self.add_error('items', iid, 'domain_invariant', 'error', f"Невалидный тип уровня предмета '{name}': {lvl}")
                                
                        for stat_name, val in [('base_atk', atk), ('base_def', df), ('base_hp', hp), ('enhancement', enh), ('max_enhancement', max_enh)]:
                            if val is not None:
                                try:
                                    val_num = float(val)
                                    if val_num < 0:
                                        self.add_error('items', iid, 'bounds_violation', 'error', f"Характеристика '{stat_name}' предмета '{name}' ({val_num}) не может быть отрицательной")
                                except (ValueError, TypeError):
                                    self.add_error('items', iid, 'domain_invariant', 'error', f"Невалидный тип для характеристики '{stat_name}': {val}")
                                    
                        valid_types = {'weapon', 'armor', 'artifact', 'consumable', 'tool', 'other'}
                        if i_type and str(i_type).lower() not in valid_types:
                            self.add_error('items', iid, 'domain_invariant', 'error', 
                                           f"Предмет '{name}' имеет невалидный тип '{i_type}'")
                                           
                        valid_rarities = {'common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic', 'cursed', 'forbidden'}
                        if rarity and str(rarity).lower() not in valid_rarities:
                            self.add_error('items', iid, 'domain_invariant', 'error', 
                                           f"Предмет '{name}' имеет невалидную редкость '{rarity}'")
                                           
                    except json.JSONDecodeError:
                        self.add_error('items', iid, 'invalid_json', 'error', "payload_json содержит невалидный JSON")
        except sqlite3.OperationalError as e:
            self.add_error('items', 'N/A', 'operational_error', 'error', f"Ошибка чтения таблицы items: {e}")

    def _check_quests_and_nodes(self):
        character_ids = set()
        if self._has_table('characters'):
            try:
                self.cur.execute("SELECT id FROM characters")
                character_ids = {r['id'] for r in self.cur.fetchall()}
            except sqlite3.OperationalError:
                pass
                
        chain_ids = set()
        if self._has_table('quest_chains'):
            try:
                self.cur.execute("SELECT id FROM quest_chains")
                chain_ids = {r['id'] for r in self.cur.fetchall()}
            except sqlite3.OperationalError:
                pass
                
        node_ids = set()
        if self._has_table('quest_nodes'):
            try:
                self.cur.execute("SELECT id FROM quest_nodes")
                node_ids = {r['id'] for r in self.cur.fetchall()}
            except sqlite3.OperationalError:
                pass
                
        objective_ids = set()
        if self._has_table('quest_objectives'):
            try:
                self.cur.execute("SELECT id FROM quest_objectives")
                objective_ids = {r['id'] for r in self.cur.fetchall()}
            except sqlite3.OperationalError:
                pass

        prereq_ids = set()
        if self._has_table('quest_prerequisites'):
            try:
                self.cur.execute("SELECT id FROM quest_prerequisites")
                prereq_ids = {r['id'] for r in self.cur.fetchall()}
            except sqlite3.OperationalError:
                pass

        if self._has_table('quests'):
            try:
                self.cur.execute("SELECT id, label, payload_json FROM quests")
                rows = self.cur.fetchall()
                for row in rows:
                    qid = row['id']
                    label = row['label']
                    payload_str = row['payload_json']
                    
                    if not label or not str(label).strip():
                        self.add_error('quests', qid, 'empty_name', 'error', "Ярлык квеста не может быть пустым")
                        
                    if payload_str:
                        try:
                            payload = json.loads(payload_str)
                            name = payload.get('name')
                            status = payload.get('status')
                            giver_id = payload.get('quest_giver_id')
                            participants = payload.get('participant_ids', [])
                            
                            if not name or not str(name).strip():
                                self.add_error('quests', qid, 'empty_name', 'error', "Имя квеста в JSON не может быть пустым")
                                
                            valid_statuses = {'active', 'completed', 'failed', 'not_started'}
                            if status and str(status).lower() not in valid_statuses:
                                self.add_error('quests', qid, 'domain_invariant', 'error', 
                                               f"Квест '{name}' имеет невалидный статус '{status}'")
                                               
                            if giver_id and giver_id not in character_ids:
                                self.add_error('quests', qid, 'dangling_fk', 'error', 
                                               f"Квест '{name}' ссылается на несуществующего квестодателя (quest_giver_id: {giver_id})")
                                               
                            if isinstance(participants, list):
                                for pid in participants:
                                    if pid not in character_ids:
                                        self.add_error('quests', qid, 'dangling_fk', 'error', 
                                                       f"Квест '{name}' ссылается на несуществующего участника с ID {pid}")
                        except json.JSONDecodeError:
                            self.add_error('quests', qid, 'invalid_json', 'error', "Невалидный JSON в quests.payload_json")
            except sqlite3.OperationalError as e:
                self.add_error('quests', 'N/A', 'operational_error', 'error', f"Ошибка чтения таблицы quests: {e}")

        if self._has_table('quest_chains'):
            try:
                self.cur.execute("SELECT id, label, payload_json FROM quest_chains")
                rows = self.cur.fetchall()
                for row in rows:
                    ccid = row['id']
                    label = row['label']
                    payload_str = row['payload_json']
                    
                    if payload_str:
                        try:
                            payload = json.loads(payload_str)
                            q_node_ids = payload.get('quest_node_ids', [])
                            if isinstance(q_node_ids, list):
                                for nid in q_node_ids:
                                    if nid not in node_ids:
                                        self.add_error('quest_chains', ccid, 'dangling_fk', 'error', 
                                                       f"Цепочка квестов '{label}' ссылается на несуществующий узел (quest_node_id: {nid})")
                        except json.JSONDecodeError:
                            self.add_error('quest_chains', ccid, 'invalid_json', 'error', "Невалидный JSON в quest_chains.payload_json")
            except sqlite3.OperationalError as e:
                self.add_error('quest_chains', 'N/A', 'operational_error', 'error', f"Ошибка чтения таблицы quest_chains: {e}")

        if self._has_table('quest_nodes'):
            try:
                self.cur.execute("SELECT id, label, payload_json FROM quest_nodes")
                rows = self.cur.fetchall()
                for row in rows:
                    nid = row['id']
                    label = row['label']
                    payload_str = row['payload_json']
                    
                    if payload_str:
                        try:
                            payload = json.loads(payload_str)
                            chain_id = payload.get('quest_chain_id')
                            obj_ids = payload.get('objective_ids', [])
                            pr_ids = payload.get('prerequisite_ids', [])
                            
                            if chain_id and chain_id not in chain_ids:
                                self.add_error('quest_nodes', nid, 'dangling_fk', 'error', 
                                               f"Узел '{label}' ссылается на несуществующую цепочку (quest_chain_id: {chain_id})")
                                               
                            if isinstance(obj_ids, list):
                                for oid in obj_ids:
                                    if oid not in objective_ids:
                                        self.add_error('quest_nodes', nid, 'dangling_fk', 'error', 
                                                       f"Узел '{label}' ссылается на несуществующую цель квеста (quest_objective_id: {oid})")
                                                       
                            if isinstance(pr_ids, list):
                                for pid in pr_ids:
                                    if pid not in prereq_ids:
                                        self.add_error('quest_nodes', nid, 'dangling_fk', 'error', 
                                                       f"Узел '{label}' ссылается на несуществующее требование (quest_prerequisite_id: {pid})")
                        except json.JSONDecodeError:
                            self.add_error('quest_nodes', nid, 'invalid_json', 'error', "Невалидный JSON в quest_nodes.payload_json")
            except sqlite3.OperationalError as e:
                self.add_error('quest_nodes', 'N/A', 'operational_error', 'error', f"Ошибка чтения таблицы quest_nodes: {e}")

        if self._has_table('quest_objectives'):
            try:
                self.cur.execute("SELECT id, label, payload_json FROM quest_objectives")
                rows = self.cur.fetchall()
                for row in rows:
                    oid = row['id']
                    label = row['label']
                    payload_str = row['payload_json']
                    
                    if payload_str:
                        try:
                            payload = json.loads(payload_str)
                            node_id = payload.get('quest_node_id')
                            if node_id and node_id not in node_ids:
                                self.add_error('quest_objectives', oid, 'dangling_fk', 'error', 
                                               f"Цель '{label}' ссылается на несуществующий узел (quest_node_id: {node_id})")
                        except json.JSONDecodeError:
                            self.add_error('quest_objectives', oid, 'invalid_json', 'error', "Невалидный JSON в quest_objectives.payload_json")
            except sqlite3.OperationalError as e:
                self.add_error('quest_objectives', 'N/A', 'operational_error', 'error', f"Ошибка чтения таблицы quest_objectives: {e}")

    def _check_quest_cycles(self):
        if not (self._has_table('quest_chains') and self._has_table('quest_nodes') and self._has_table('quest_prerequisites')):
            return
            
        try:
            graph = {}
            
            self.cur.execute("SELECT id FROM quest_chains")
            for r in self.cur.fetchall():
                graph[r['id']] = set()
                
            self.cur.execute("SELECT id, payload_json FROM quest_nodes")
            nodes_map = {}
            for r in self.cur.fetchall():
                try:
                    payload = json.loads(r['payload_json'])
                    nodes_map[r['id']] = {
                        'chain_id': payload.get('quest_chain_id'),
                        'prereq_ids': payload.get('prerequisite_ids', [])
                    }
                except Exception:
                    pass
                    
            self.cur.execute("SELECT id, payload_json FROM quest_prerequisites")
            prereqs_map = {}
            for r in self.cur.fetchall():
                try:
                    payload = json.loads(r['payload_json'])
                    reqs = payload.get('required_quest_ids', [])
                    if isinstance(reqs, list):
                        prereqs_map[r['id']] = reqs
                except Exception:
                    pass
                    
            for nid, node in nodes_map.items():
                chain_id = node['chain_id']
                if not chain_id or chain_id not in graph:
                    continue
                for pid in node['prereq_ids']:
                    if pid in prereqs_map:
                        for req_qid in prereqs_map[pid]:
                            if req_qid:
                                graph[chain_id].add(req_qid)
                                
            visited = {}
            cycle = []
            
            def dfs(node):
                visited[node] = 1
                for neighbor in graph.get(node, []):
                    if visited.get(neighbor) == 1:
                        cycle.append(neighbor)
                        cycle.append(node)
                        return True
                    elif neighbor not in visited:
                        if dfs(neighbor):
                            cycle.append(node)
                            return True
                visited[node] = 2
                return False
                
            has_cycle = False
            for node in graph:
                if node not in visited:
                    if dfs(node):
                        cycle.reverse()
                        has_cycle = True
                        break
                        
            if has_cycle:
                cycle_str = " -> ".join(str(nid) for nid in cycle)
                self.add_error('quest_chains', cycle[0], 'logical_contradiction', 'error', 
                               f"Обнаружен циклический импорт/требование в квестах: {cycle_str}")
                               
        except sqlite3.OperationalError:
            pass

    def print_report(self, errors_list, format_type='text'):
        if format_type == 'json':
            print(json.dumps(errors_list, indent=2, ensure_ascii=False))
            return
            
        if format_type == 'markdown':
            print("| Таблица | ID Сущности | Тип Нарушения | Критичность | Описание |")
            print("| :--- | :--- | :--- | :--- | :--- |")
            for err in errors_list:
                print(f"| {err['table']} | {err['id']} | {err['type']} | {err['severity'].upper()} | {err['description']} |")
            return

        if not errors_list:
            print(colored("\n✅ УСПЕХ: ОШИБОК ИЛИ ПРОТИВОРЕЧИЙ НЕ ОБНАРУЖЕНО!\n", "92;1"))
            return
            
        print(f"\n{colored('НАЙДЕННЫЕ НАРУШЕНИЯ И ПРОТИВОРЕЧИЯ:', '91;1')} ({len(errors_list)})\n")
        
        col_table = max(max(len(e['table']) for e in errors_list), 15)
        col_id = max(max(len(str(e['id'])) for e in errors_list), 5)
        col_type = max(max(len(e['type']) for e in errors_list), 12)
        col_sev = max(max(len(e['severity']) for e in errors_list), 8)
        
        header = f"{'Таблица':<{col_table}} | {'ID':<{col_id}} | {'Тип':<{col_type}} | {'Критич.':<{col_sev}} | Описание"
        print(colored(header, "1"))
        print("-" * (col_table + col_id + col_type + col_sev + 15))
        
        for err in errors_list:
            sev_str = err['severity'].upper()
            table_part = f"{err['table']:<{col_table}}"
            id_part = f"{str(err['id']):<{col_id}}"
            type_part = f"{err['type']:<{col_type}}"
            
            if err['severity'] == 'error':
                sev_part = colored(f"{sev_str:<{col_sev}}", "91;1")
                desc_part = colored(err['description'], "91")
            else:
                sev_part = colored(f"{sev_str:<{col_sev}}", "93;1")
                desc_part = colored(err['description'], "93")
                
            print(f"{table_part} | {id_part} | {type_part} | {sev_part} | {desc_part}")
        print()

    def print_db_stats(self):
        print("\n" + "="*50)
        print("          СТАТИСТИКА БАЗЫ ДАННЫХ ЛОРА          ")
        print("="*50)
        print(f"Путь к файлу: {os.path.abspath(self.db_path)}")
        for tbl in sorted(list(self.tables)):
            try:
                self.cur.execute(f"SELECT count(*) FROM {tbl}")
                count = self.cur.fetchone()[0]
                print(f"Таблица {tbl:<30}: {count} записей")
            except sqlite3.OperationalError:
                pass
        print("="*50)

def run_interactive(validator):
    print("\n" + "="*70)
    print("      ИНТЕРАКТИВНЫЙ ВАЛИДАТОР ЛОГИЧЕСКОЙ ЦЕЛОСТНОСТИ ЛОРА      ")
    print("="*70)
    print(f"База данных: {os.path.abspath(validator.db_path)}")
    print(f"Всего ошибок/предупреждений: {len(validator.errors)}")
    print("="*70)
    
    while True:
        print("\nГлавное меню:")
        print("1. Показать все ошибки и предупреждения")
        print("2. Фильтровать ошибки по таблицам")
        print("3. Фильтровать ошибки по типам нарушений")
        print("4. Фильтровать ошибки по критичности (Error/Warning)")
        print("5. Показать общую статистику базы данных")
        print("6. Выход")
        
        choice = input("\nВыберите пункт меню (1-6): ").strip()
        if choice == '1':
            validator.print_report(validator.errors, format_type='text')
        elif choice == '2':
            tables_with_errors = sorted(list(set(e['table'] for e in validator.errors)))
            if not tables_with_errors:
                print("\nНет ошибок для фильтрации.")
                continue
            print("\nДоступные таблицы с ошибками:")
            for i, tbl in enumerate(tables_with_errors, 1):
                count = sum(1 for e in validator.errors if e['table'] == tbl)
                print(f"{i}. {tbl} ({count} ошибок)")
            try:
                tbl_choice = input(f"Выберите таблицу (1-{len(tables_with_errors)}) или 'c' для отмены: ").strip()
                if tbl_choice.lower() == 'c':
                    continue
                tbl_choice = int(tbl_choice)
                selected_tbl = tables_with_errors[tbl_choice - 1]
                filtered = [e for e in validator.errors if e['table'] == selected_tbl]
                validator.print_report(filtered, format_type='text')
            except (ValueError, IndexError):
                print("Неверный выбор.")
        elif choice == '3':
            types_with_errors = sorted(list(set(e['type'] for e in validator.errors)))
            if not types_with_errors:
                print("\nНет ошибок для фильтрации.")
                continue
            print("\nДоступные типы нарушений:")
            for i, typ in enumerate(types_with_errors, 1):
                count = sum(1 for e in validator.errors if e['type'] == typ)
                print(f"{i}. {typ} ({count} ошибок)")
            try:
                typ_choice = input(f"Выберите тип нарушения (1-{len(types_with_errors)}) или 'c' для отмены: ").strip()
                if typ_choice.lower() == 'c':
                    continue
                typ_choice = int(typ_choice)
                selected_typ = types_with_errors[typ_choice - 1]
                filtered = [e for e in validator.errors if e['type'] == selected_typ]
                validator.print_report(filtered, format_type='text')
            except (ValueError, IndexError):
                print("Неверный выбор.")
        elif choice == '4':
            print("\nВыберите уровень критичности:")
            print("1. Error (Ошибки целостности)")
            print("2. Warning (Предупреждения качества)")
            sev_choice = input("Ваш выбор (1-2) или 'c' для отмены: ").strip()
            if sev_choice.lower() == 'c':
                continue
            if sev_choice == '1':
                filtered = [e for e in validator.errors if e['severity'] == 'error']
                validator.print_report(filtered, format_type='text')
            elif sev_choice == '2':
                filtered = [e for e in validator.errors if e['severity'] == 'warning']
                validator.print_report(filtered, format_type='text')
            else:
                print("Неверный выбор.")
        elif choice == '5':
            validator.print_db_stats()
        elif choice == '6':
            print("\nВыход из валидатора. До свидания!")
            break
        else:
            print("Неверный ввод, введите число от 1 до 6.")

def main():
    parser = argparse.ArgumentParser(description="Кросс-табличный валидатор логической целостности лора (Lore Consistency & Logic Validator)")
    parser.add_argument("db_path", nargs="?", default="lore_system.db", help="Путь к файлу базы данных SQLite (default: lore_system.db)")
    parser.add_argument("-t", "--table", help="Фильтровать ошибки по имени таблицы (например, characters, character_relationships)")
    parser.add_argument("-y", "--type", help="Фильтровать ошибки по типу нарушения (например, dangling_fk, logical_contradiction)")
    parser.add_argument("-s", "--severity", choices=["error", "warning"], help="Фильтровать по уровню критичности (error, warning)")
    parser.add_argument("-f", "--format", choices=["text", "json", "markdown"], default="text", help="Формат вывода отчета (default: text)")
    parser.add_argument("-i", "--interactive", action="store_true", help="Запустить в интерактивном текстовом режиме")
    
    args = parser.parse_args()
    
    validator = LoreValidator(args.db_path)
    validator.connect()
    try:
        validator.run_all_checks()
        
        if args.interactive:
            run_interactive(validator)
        else:
            filtered_errors = validator.errors
            if args.table:
                filtered_errors = [e for e in filtered_errors if e['table'].lower() == args.table.lower()]
            if args.type:
                filtered_errors = [e for e in filtered_errors if e['type'].lower() == args.type.lower()]
            if args.severity:
                filtered_errors = [e for e in filtered_errors if e['severity'].lower() == args.severity.lower()]
                
            validator.print_report(filtered_errors, format_type=args.format)
            
            has_critical = any(e['severity'] == 'error' for e in filtered_errors)
            if has_critical and not args.interactive:
                sys.exit(1)
    finally:
        validator.close()

if __name__ == '__main__':
    main()
