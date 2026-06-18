#!/usr/bin/env python3
"""
Lightweight SQLite Web Viewer for MythWeave
Runs a zero-dependency local server and opens a beautiful dark-themed Tabulator.js frontend.
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
    
    <!-- Tabulator CSS (Midnight Dark Theme) -->
    <link href="https://unpkg.com/tabulator-tables@5.5.2/dist/css/tabulator_midnight.min.css" rel="stylesheet">
    <script type="text/javascript" src="https://unpkg.com/tabulator-tables@5.5.2/dist/js/tabulator.min.js"></script>

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
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border-color);
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

        select, input {
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

        .table-wrapper {
            flex-grow: 1;
            background-color: var(--container-bg);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }

        /* Customize Tabulator Styles to fit our theme */
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
    </style>
</head>
<body>

    <header>
        <h1>🎮 MythWeave Lore Explorer</h1>
        <span class="db-badge" id="dbName">lore_system.db</span>
    </header>

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

        <div class="stats-badge" id="statsBadge">
            Записей: <strong id="rowCount">0</strong>
        </div>
    </div>

    <div class="table-wrapper">
        <div id="loreTable"></div>
    </div>

    <script>
        let table = null;
        let currentData = [];

        // Fetch list of tables on load
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

                // Load first table
                if (tables.length > 0) {
                    loadTableData(tables[0]);
                }
            } catch (err) {
                console.error("Failed to load tables", err);
                document.getElementById('tableSelect').innerHTML = '<option value="">Ошибка загрузки</option>';
            }
        }

        // Fetch data for specific table
        async function loadTableData(tableName) {
            if (!tableName) return;
            
            document.getElementById('rowCount').textContent = "Загрузка...";
            
            try {
                const response = await fetch(`/api/data?table=${encodeURIComponent(tableName)}`);
                const data = await response.json();
                currentData = data;
                
                document.getElementById('rowCount').textContent = data.length;
                
                renderTable(data);
            } catch (err) {
                console.error("Failed to load table data", err);
                document.getElementById('rowCount').textContent = "Ошибка";
            }
        }

        // Render Tabulator table dynamically
        function renderTable(data) {
            if (data.length === 0) {
                if (table) table.destroy();
                document.getElementById('loreTable').innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">Таблица пуста</div>';
                return;
            }

            // Auto-generate columns from the first row keys
            const sampleRow = data[0];
            const columns = Object.keys(sampleRow).map(key => {
                const isId = key.toLowerCase() === 'id';
                const isJson = typeof sampleRow[key] === 'string' && (sampleRow[key].startsWith('{') || sampleRow[key].startsWith('['));
                
                let colDef = {
                    title: key,
                    field: key,
                    sorter: isId ? "number" : "string",
                    headerFilter: false
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
                    colDef.width = 70;
                    colDef.hovertarget = true;
                }

                return colDef;
            });

            // Destroy previous instance
            if (table) {
                table.destroy();
            }

            // Create new Tabulator instance
            table = new Tabulator("#loreTable", {
                data: data,
                columns: columns,
                layout: "fitColumns",
                responsiveLayout: "hide",
                pagination: "local",
                paginationSize: 15,
                paginationSizeSelector: [10, 15, 25, 50, 100],
                movableColumns: true,
                initialSort: [
                    {column: "id", dir: "asc"}
                ]
            });
        }

        // Search/Filter binding
        document.getElementById('searchInput').addEventListener('input', function(e) {
            if (!table) return;
            
            const value = e.target.value.toLowerCase();
            
            if (!value) {
                table.clearFilter();
                return;
            }

            // Custom search filter: check if any cell in row contains search term
            table.setFilter(function(data) {
                for (let key in data) {
                    if (data[key] !== null && String(data[key]).toLowerCase().includes(value)) {
                        return true;
                    }
                }
                return false;
            });
        });

        // Table select binding
        document.getElementById('tableSelect').addEventListener('change', function(e) {
            loadTableData(e.target.value);
            document.getElementById('searchInput').value = '';
        });

        // Initialize
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
                # Safeguard: Verify table name exists in sqlite_master
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                valid_tables = [row[0] for row in cursor.fetchall()]
                
                if table_name in valid_tables:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = [dict(row) for row in cursor.fetchall()]
                    
                    # Decouple bytes/blobs
                    for r in rows:
                        for k, v in r.items():
                            if isinstance(v, bytes):
                                r[k] = v.decode('utf-8', errors='ignore')
                conn.close()
            except Exception as e:
                print(f"Error fetching data from {table_name}: {e}")
                
            self.wfile.write(json.dumps(rows, default=str).encode('utf-8'))
            
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
