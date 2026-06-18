#!/usr/bin/env python3
"""
Lightweight SQLite Web Viewer for MythWeave
Runs a zero-dependency local server and opens a beautiful dark-themed Tabulator.js & Vis.js frontend.
"""
import http.server
import socketserver
import sqlite3
import json
import urllib.parse
import os
import sys
import webbrowser

PORT = 8080
DB_PATH = "lore_system.db"

HTML_CONTENT = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MythWeave Lore Explorer</title>
    
    <!-- Google Fonts: Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Tabulator CSS & JS (Midnight Dark Theme) -->
    <link href="https://unpkg.com/tabulator-tables@5.5.2/dist/css/tabulator_midnight.min.css" rel="stylesheet">
    <script type="text/javascript" src="https://unpkg.com/tabulator-tables@5.5.2/dist/js/tabulator.min.js"></script>

    <!-- Vis Network JS for Graph Visualizations -->
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>

    <style>
        :root {
            --bg-color: #0b0f19;
            --container-bg: #151b2c;
            --border-color: #232d45;
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --accent-color: #6366f1;
            --accent-hover: #4f46e5;
            --input-bg: #1e293b;
            --card-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            padding: 24px;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border-color);
        }

        .header-title-container {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        h1 {
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, #a78bfa, #6366f1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .db-badge {
            font-size: 12px;
            font-weight: 500;
            background-color: #1e1b4b;
            color: #c084fc;
            padding: 4px 10px;
            border-radius: 12px;
            border: 1px solid #581c87;
        }

        /* Tabs Styling */
        .tabs {
            display: flex;
            gap: 8px;
            background-color: var(--container-bg);
            padding: 4px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }

        .tab-btn {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 500;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .tab-btn:hover {
            color: var(--text-primary);
            background-color: rgba(255, 255, 255, 0.05);
        }

        .tab-btn.active {
            color: var(--text-primary);
            background-color: var(--accent-color);
        }

        /* Views Container */
        .view-content {
            display: flex;
            flex-direction: column;
            flex-grow: 1;
        }

        .view-pane {
            display: none;
            flex-direction: column;
            flex-grow: 1;
        }

        .view-pane.active {
            display: flex;
        }

        /* Table View Controls */
        .controls-container {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 20px;
            background-color: var(--container-bg);
            padding: 16px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            align-items: center;
        }

        .control-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .control-group label {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        select, input, button.btn {
            background-color: var(--input-bg);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            outline: none;
            transition: all 0.2s;
        }

        select:focus, input:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
        }

        select {
            cursor: pointer;
            min-width: 220px;
        }

        input {
            min-width: 300px;
        }

        button.btn {
            cursor: pointer;
            background-color: var(--accent-color);
            border: 1px solid var(--accent-color);
            font-weight: 600;
            padding: 10px 20px;
        }

        button.btn:hover {
            background-color: var(--accent-hover);
            border-color: var(--accent-hover);
        }

        button.btn-secondary {
            background-color: transparent;
            border-color: var(--border-color);
            color: var(--text-secondary);
        }

        button.btn-secondary:hover {
            background-color: rgba(255, 255, 255, 0.05);
            color: var(--text-primary);
        }

        .stats-badge {
            margin-left: auto;
            font-size: 14px;
            color: var(--text-secondary);
            background-color: rgba(255, 255, 255, 0.05);
            padding: 8px 16px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }

        .stats-badge strong {
            color: var(--text-primary);
        }

        /* Table Wrapper */
        .table-wrapper {
            flex-grow: 1;
            background-color: var(--container-bg);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            overflow: hidden;
            box-shadow: var(--card-shadow);
        }

        /* Customizing Tabulator Dark Theme */
        .tabulator {
            border: none !important;
            background-color: transparent !important;
        }

        .tabulator-header {
            background-color: #0f1423 !important;
            border-bottom: 2px solid var(--border-color) !important;
        }

        .tabulator-col {
            background-color: #0f1423 !important;
            border-right: 1px solid var(--border-color) !important;
        }

        .tabulator-row {
            border-bottom: 1px solid var(--border-color) !important;
        }

        .tabulator-row:nth-child(even) {
            background-color: rgba(255, 255, 255, 0.02) !important;
        }

        .tabulator-row:hover {
            background-color: rgba(99, 102, 241, 0.1) !important;
        }

        .tabulator-cell {
            border-right: 1px solid var(--border-color) !important;
            padding: 12px !important;
            font-size: 14px;
        }

        .tabulator-footer {
            background-color: #0f1423 !important;
            border-top: 1px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }

        .json-cell {
            font-family: monospace;
            font-size: 12px;
            color: #a78bfa;
            max-height: 80px;
            overflow-y: auto;
            white-space: pre-wrap;
        }

        /* Graph Panel Layout */
        .graph-panel {
            display: flex;
            gap: 16px;
            flex-grow: 1;
            height: calc(100vh - 160px);
        }

        .graph-controls {
            width: 280px;
            background-color: var(--container-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            box-shadow: var(--card-shadow);
        }

        .graph-canvas-container {
            flex-grow: 1;
            background-color: var(--container-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            position: relative;
            box-shadow: var(--card-shadow);
            overflow: hidden;
        }

        #network {
            width: 100%;
            height: 100%;
            background-color: #0f1423;
        }

        .graph-node-details {
            background-color: rgba(15, 20, 35, 0.8);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px;
            margin-top: auto;
            font-size: 13px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            margin-bottom: 6px;
        }

        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }

        /* Vis network tooltips customization */
        div.vis-network div.vis-tooltip {
            background-color: #1e293b !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-primary) !important;
            font-family: inherit !important;
            font-size: 12px !important;
            padding: 8px 12px !important;
            border-radius: 6px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
        }
    </style>
</head>
<body>

    <header>
        <div class="header-title-container">
            <h1>🎮 MythWeave Lore Explorer</h1>
            <span class="db-badge" id="dbName">lore_system.db</span>
        </div>
        
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('tableTab', this)">📊 Таблицы</button>
            <button class="tab-btn" onclick="switchTab('graphTab', this)">🕸️ Сеть персонажей</button>
        </div>
    </header>

    <div class="view-content">
        <!-- TABLE VIEW -->
        <div id="tableTab" class="view-pane active">
            <div class="controls-container">
                <div class="control-group">
                    <label for="tableSelect">Таблица лора</label>
                    <select id="tableSelect">
                        <option value="">Загрузка таблиц...</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label for="searchInput">Поиск / Фильтр</label>
                    <input type="text" id="searchInput" placeholder="Введите текст для фильтрации...">
                </div>

                <div class="stats-badge">
                    Записей: <strong id="rowCount">0</strong>
                </div>
            </div>

            <div class="table-wrapper">
                <div id="loreTable"></div>
            </div>
        </div>

        <!-- GRAPH VIEW -->
        <div id="graphTab" class="view-pane">
            <div class="graph-panel">
                <div class="graph-controls">
                    <h3 style="font-size: 16px; font-weight: 600; border-bottom: 1px solid var(--border-color); padding-bottom: 8px;">Связи героев</h3>
                    
                    <div class="control-group" style="margin-top: 8px;">
                        <label>Стихии героев (Легенда)</label>
                        <div style="margin-top: 4px;">
                            <div class="legend-item"><div class="legend-color" style="background-color: #ef4444;"></div> Fire (Огонь)</div>
                            <div class="legend-item"><div class="legend-color" style="background-color: #3b82f6;"></div> Water (Вода)</div>
                            <div class="legend-item"><div class="legend-color" style="background-color: #10b981;"></div> Earth (Земля)</div>
                            <div class="legend-item"><div class="legend-color" style="background-color: #06b6d4;"></div> Wind (Ветер)</div>
                            <div class="legend-item"><div class="legend-color" style="background-color: #f59e0b;"></div> Light (Свет)</div>
                            <div class="legend-item"><div class="legend-color" style="background-color: #8b5cf6;"></div> Dark (Тьма)</div>
                            <div class="legend-item"><div class="legend-color" style="background-color: #6b7280;"></div> Physical (Физ.)</div>
                        </div>
                    </div>

                    <div class="control-group">
                        <label>Типы отношений</label>
                        <div style="margin-top: 4px;">
                            <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #10b981;"></div> Друг / Союзник</div>
                            <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #ef4444;"></div> Враг / Соперник</div>
                            <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #9ca3af;"></div> Нейтральные</div>
                        </div>
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 10px;">
                        <button class="btn btn-secondary" onclick="stabilizeGraph()">🔄 Сбросить симуляцию</button>
                        <button class="btn btn-secondary" onclick="togglePhysics(this)">⏸️ Выключить физику</button>
                    </div>

                    <div class="graph-node-details" id="nodeDetails">
                        <p style="color: var(--text-secondary); text-align: center;">Кликните на героя для просмотра деталей</p>
                    </div>
                </div>

                <div class="graph-canvas-container">
                    <div id="network"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let table = null;
        let network = null;
        let physicsEnabled = true;

        // Switch View Tabs
        function switchTab(tabId, btn) {
            document.querySelectorAll('.view-pane').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');

            if (tabId === 'graphTab') {
                loadGraphData();
            }
        }

        // ==========================================
        // TABLE LOGIC
        // ==========================================

        async function loadTables() {
            try {
                const response = await fetch('/api/tables');
                const tables = await response.json();
                
                const select = document.getElementById('tableSelect');
                select.innerHTML = '';
                
                if (tables.length === 0) {
                    select.innerHTML = '<option value="">Нет таблиц</option>';
                    return;
                }

                tables.forEach(t => {
                    const opt = document.createElement('option');
                    opt.value = t;
                    opt.textContent = t;
                    select.appendChild(opt);
                });

                if (tables.length > 0) {
                    loadTableData(tables[0]);
                }
            } catch (err) {
                console.error("Failed to load tables", err);
                document.getElementById('tableSelect').innerHTML = '<option value="">Ошибка загрузки</option>';
            }
        }

        async function loadTableData(tableName) {
            if (!tableName) return;
            document.getElementById('rowCount').textContent = "Загрузка...";
            
            try {
                const response = await fetch(`/api/data?table=${encodeURIComponent(tableName)}`);
                const data = await response.json();
                
                document.getElementById('rowCount').textContent = data.length;
                renderTable(data);
            } catch (err) {
                console.error("Failed to load table data", err);
                document.getElementById('rowCount').textContent = "Ошибка";
            }
        }

        function renderTable(data) {
            if (data.length === 0) {
                if (table) table.destroy();
                document.getElementById('loreTable').innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">Таблица пуста</div>';
                return;
            }

            const sampleRow = data[0];
            const columns = Object.keys(sampleRow).map(key => {
                const isId = key.toLowerCase() === 'id';
                const isJson = typeof sampleRow[key] === 'string' && (sampleRow[key].startsWith('{') || sampleRow[key].startsWith('['));
                
                let colDef = {
                    title: key,
                    field: key,
                    sorter: isId ? "number" : "string",
                };

                if (isJson) {
                    colDef.formatter = function(cell) {
                        try {
                            const val = cell.getValue();
                            const parsed = JSON.parse(val);
                            return `<div class="json-cell">${JSON.stringify(parsed, null, 2)}</div>`;
                        } catch (e) {
                            return `<div class="json-cell">${cell.getValue()}</div>`;
                        }
                    };
                } else if (isId) {
                    colDef.width = 75;
                }

                return colDef;
            });

            if (table) {
                table.destroy();
            }

            table = new Tabulator("#loreTable", {
                data: data,
                columns: columns,
                layout: "fitColumns",
                responsiveLayout: "hide",
                pagination: "local",
                paginationSize: 15,
                paginationSizeSelector: [10, 15, 25, 50, 100],
                movableColumns: true,
                initialSort: [{column: "id", dir: "asc"}]
            });
        }

        // Search Filter
        document.getElementById('searchInput').addEventListener('input', function(e) {
            if (!table) return;
            const value = e.target.value.toLowerCase();
            if (!value) {
                table.clearFilter();
                return;
            }
            table.setFilter(function(data) {
                for (let key in data) {
                    if (data[key] !== null && String(data[key]).toLowerCase().includes(value)) {
                        return true;
                    }
                }
                return false;
            });
        });

        document.getElementById('tableSelect').addEventListener('change', function(e) {
            loadTableData(e.target.value);
            document.getElementById('searchInput').value = '';
        });

        // ==========================================
        // GRAPH (NETWORK) LOGIC
        // ==========================================

        async function loadGraphData() {
            try {
                const response = await fetch('/api/graph');
                const graphData = await response.json();
                renderGraph(graphData);
            } catch (err) {
                console.error("Failed to load graph data", err);
                document.getElementById('network').innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);">Ошибка построения графа связей. Убедитесь, что таблицы characters и character_relationships существуют.</div>';
            }
        }

        function renderGraph(graphData) {
            const container = document.getElementById('network');
            
            const options = {
                nodes: {
                    borderWidth: 2,
                    shadow: true,
                    font: {
                        face: 'Inter',
                        strokeWidth: 4,
                        strokeColor: '#0b0f19'
                    }
                },
                edges: {
                    width: 2,
                    shadow: true,
                    smooth: {
                        type: 'continuous',
                        roundness: 0.3
                    }
                },
                physics: {
                    enabled: physicsEnabled,
                    barnesHut: {
                        gravitationalConstant: -3000,
                        centralGravity: 0.3,
                        springLength: 150,
                        springConstant: 0.04,
                        damping: 0.09
                    },
                    stabilization: {
                        iterations: 150,
                        fit: true
                    }
                },
                interaction: {
                    hover: true,
                    tooltipDelay: 200,
                    hideEdgesOnDrag: false
                }
            };

            network = new vis.Network(container, graphData, options);

            // Click node event
            network.on("click", function (params) {
                if (params.nodes.length > 0) {
                    const nodeId = params.nodes[0];
                    const selectedNode = graphData.nodes.find(n => n.id === nodeId);
                    
                    if (selectedNode) {
                        const div = document.getElementById('nodeDetails');
                        // Title contains HTML metadata, display it
                        div.innerHTML = `
                            <div style="font-weight: 700; font-size: 16px; margin-bottom: 8px; color: ${selectedNode.color.background};">${selectedNode.label}</div>
                            <div style="max-height: 180px; overflow-y: auto; line-height: 1.4; color: var(--text-secondary);">${selectedNode.title}</div>
                        `;
                    }
                } else {
                    document.getElementById('nodeDetails').innerHTML = '<p style="color: var(--text-secondary); text-align: center;">Кликните на героя для просмотра деталей</p>';
                }
            });
        }

        function stabilizeGraph() {
            if (network) {
                network.stabilize();
            }
        }

        function togglePhysics(btn) {
            physicsEnabled = !physicsEnabled;
            if (physicsEnabled) {
                btn.textContent = "⏸️ Выключить физику";
                btn.classList.remove('btn-secondary');
            } else {
                btn.textContent = "▶️ Включить физику";
                btn.classList.add('btn-secondary');
            }
            if (network) {
                network.setOptions({ physics: { enabled: physicsEnabled } });
            }
        }

        // Init Load
        loadTables();
    </script>
</body>
</html>
"""

class ViewerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        
        # API: List Tables
        if parsed_url.path == "/api/tables":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                tables = [row[0] for row in cursor.fetchall()]
                conn.close()
            except Exception as e:
                tables = []
                print(f"Error listing tables: {e}")
                
            self.wfile.write(json.dumps(tables).encode('utf-8'))
            
        # API: Table Data
        elif parsed_url.path == "/api/data":
            query_params = urllib.parse.parse_qs(parsed_url.query)
            table_name = query_params.get("table", [None])[0]
            
            if not table_name:
                self.send_error(400, "Missing table parameter")
                return
                
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            rows = []
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                valid_tables = [row[0] for row in cursor.fetchall()]
                
                if table_name in valid_tables:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = [dict(row) for row in cursor.fetchall()]
                    
                    for r in rows:
                        for k, v in r.items():
                            if isinstance(v, bytes):
                                r[k] = v.decode('utf-8', errors='ignore')
                conn.close()
            except Exception as e:
                print(f"Error fetching data from {table_name}: {e}")
                
            self.wfile.write(json.dumps(rows, default=str).encode('utf-8'))
            
        # API: Graph (Character Relationships)
        elif parsed_url.path == "/api/graph":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            nodes = []
            edges = []
            
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Fetch characters (if table exists)
                cursor.execute("SELECT id, name, rarity, element, role, backstory FROM characters")
                characters = [dict(row) for row in cursor.fetchall()]
                
                # Fetch relationships (if table exists)
                cursor.execute("SELECT character_from_id, character_to_id, relationship_type, relationship_level, is_mutual FROM character_relationships")
                relationships = [dict(row) for row in cursor.fetchall()]
                conn.close()
                
                # Beautiful element-based colors for nodes
                elem_colors = {
                    'fire': '#ef4444',     # Red
                    'water': '#3b82f6',    # Blue
                    'earth': '#10b981',    # Green
                    'wind': '#06b6d4',     # Cyan
                    'light': '#f59e0b',    # Gold
                    'dark': '#8b5cf6',     # Purple
                    'physical': '#6b7280'  # Gray
                }
                
                for char in characters:
                    elem = str(char.get('element', '')).lower()
                    bg_color = elem_colors.get(elem, '#6366f1')
                    
                    # Tooltip metadata HTML
                    tooltip = f"<b>Роль:</b> {char.get('role', 'N/A')}<br>" \
                              f"<b>Стихия:</b> {char.get('element', 'N/A')}<br>" \
                              f"<b>Редкость:</b> {char.get('rarity', 'N/A')}<br>" \
                              f"<b>Биография:</b> {char.get('backstory', '')}"
                              
                    nodes.append({
                        'id': char['id'],
                        'label': char['name'],
                        'title': tooltip,
                        'color': {
                            'background': bg_color,
                            'border': '#1e293b',
                            'highlight': {
                                'background': '#ec4899',
                                'border': '#fbcfe8'
                            }
                        },
                        'size': 20
                    })
                    
                for rel in relationships:
                    r_type = str(rel.get('relationship_type', '')).lower()
                    level = rel.get('relationship_level')
                    is_mut = rel.get('is_mutual')
                    
                    # Positive (green) vs Negative (red) vs Neutral (gray) relationships
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
                        'from': rel['character_from_id'],
                        'to': rel['character_to_id'],
                        'label': label_str,
                        'color': {
                            'color': line_color,
                            'highlight': '#ec4899'
                        },
                        'font': {'align': 'middle', 'color': '#9ca3af', 'size': 9, 'face': 'Inter'},
                        'width': 2
                    }
                    
                    if not is_mut:
                        edge['arrows'] = 'to'
                        
                    edges.append(edge)
            except Exception as e:
                print(f"Error building graph data: {e}")
                
            self.wfile.write(json.dumps({'nodes': nodes, 'edges': edges}).encode('utf-8'))
            
        # Frontend Page
        elif parsed_url.path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode('utf-8'))
            
        else:
            self.send_error(404, "Not Found")

def run():
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: Database file '{DB_PATH}' not found in the current directory.")
        sys.exit(1)
        
    handler = ViewerHandler
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print("==================================================")
        print("🎮 MythWeave Lightweight Lore Viewer")
        print("==================================================")
        print(f"🔗 URL: http://localhost:{PORT}")
        print(f"📁 Database: {os.path.abspath(DB_PATH)}")
        print("💡 Press Ctrl+C to stop the viewer.")
        print("==================================================")
        
        # Open in browser automatically
        webbrowser.open(f"http://localhost:{PORT}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down viewer server...")

if __name__ == "__main__":
    run()
