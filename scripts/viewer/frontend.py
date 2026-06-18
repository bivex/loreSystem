# -*- coding: utf-8 -*-
"""
HTML/CSS/JS Frontend template for the MythWeave Lore Explorer.
Uses Tabulator.js for grids and Vis.js Network for interactive graphs.
"""

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
            width: 300px;
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

        .legend-box {
            width: 16px;
            height: 12px;
            border-radius: 2px;
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

        /* TODO View Styles */
        .todo-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .todo-card {
            background-color: var(--input-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            transition: transform 0.2s, border-color 0.2s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .todo-card:hover {
            transform: translateY(-4px);
            border-color: var(--accent-color);
        }

        .todo-card h4 {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .todo-card p {
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.5;
        }

        .todo-card-tables {
            font-size: 11px;
            background-color: rgba(255, 255, 255, 0.03);
            padding: 8px;
            border-radius: 6px;
            border: 1px dashed var(--border-color);
            color: #a78bfa;
            font-family: monospace;
            margin-top: auto;
        }

        .todo-card-benefits {
            font-size: 12px;
            color: var(--text-primary);
            background-color: rgba(99, 102, 241, 0.05);
            padding: 8px;
            border-radius: 6px;
            border-left: 3px solid var(--accent-color);
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
            <button class="tab-btn" onclick="switchTab('graphTab', this)">🕸️ Интерактивная сеть</button>
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
                    <h3 style="font-size: 16px; font-weight: 600; border-bottom: 1px solid var(--border-color); padding-bottom: 8px;">Визуализация сети</h3>
                    
                    <div class="control-group" style="margin-top: 4px;">
                        <label for="graphTypeSelect">Тип графа</label>
                        <select id="graphTypeSelect" style="min-width: 100%;">
                            <option value="characters">🕸️ Отношения героев</option>
                            <option value="quests">⚔️ Дерево квестов</option>
                            <option value="locations">🗺️ Карта локаций мира</option>
                            <option value="story_branches">🔀 Развилки сюжета и концовок</option>
                            <option value="timeline">⏳ Хронология исторических эпох</option>
                            <option value="factions">🤝 Дипломатия фракций и альянсы</option>
                            <option value="crafting">⚒️ Схемы крафта и ресурсов</option>
                            <option value="todo">📋 Планируемые графы (TODO)</option>
                        </select>
                    </div>

                    <!-- Dynamic Legend Section -->
                    <div id="legendSection" style="margin-top: 4px; display: flex; flex-direction: column; gap: 12px; flex-grow: 1;">
                        <!-- Content injected by JS -->
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 10px;">
                        <button class="btn btn-secondary" onclick="stabilizeGraph()">🔄 Сбросить симуляцию</button>
                        <button class="btn btn-secondary" onclick="togglePhysics(this)">⏸️ Выключить физику</button>
                    </div>

                    <div class="graph-node-details" id="nodeDetails">
                        <p style="color: var(--text-secondary); text-align: center;">Кликните на узел для просмотра деталей</p>
                    </div>
                </div>

                <div class="graph-canvas-container">
                    <div id="network"></div>
                    <div id="todo-view" style="display: none; padding: 24px; overflow-y: auto; height: 100%;"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let table = null;
        let network = null;
        let physicsEnabled = true;
        let currentGraphType = 'characters';

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

        const legends = {
            characters: `
                <div class="control-group">
                    <label>Стихии героев (Узлы)</label>
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
                    <label>Отношения (Связи)</label>
                    <div style="margin-top: 4px;">
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #10b981;"></div> Друг / Союзник</div>
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #ef4444;"></div> Враг / Соперник</div>
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #9ca3af;"></div> Нейтральные</div>
                    </div>
                </div>
            `,
            quests: `
                <div class="control-group">
                    <label>Типы узлов квестов</label>
                    <div style="margin-top: 4px;">
                        <div class="legend-item"><div class="legend-box" style="background-color: #f59e0b; border: 1px solid #b45309;"></div> Root Квест</div>
                        <div class="legend-item"><div class="legend-color" style="background-color: #06b6d4;"></div> Шаг (Quest Node)</div>
                    </div>
                </div>
                <div class="control-group">
                    <label>Связи переходов</label>
                    <div style="margin-top: 4px;">
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #06b6d4;"></div> Последовательность шагов</div>
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #d97706; border-top: 2px dashed #d97706;"></div> Владелец квеста</div>
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #ef4444; border-top: 2px dashed #ef4444;"></div> Требование (Prerequisite)</div>
                    </div>
                </div>
            `,
            locations: `
                <div class="control-group">
                    <label>Иерархия локаций</label>
                    <div style="margin-top: 4px;">
                        <div class="legend-item"><div class="legend-box" style="background-color: #10b981; border: 1px solid #065f46;"></div> Мир (World)</div>
                        <div class="legend-item"><div class="legend-color" style="background-color: #3b82f6;"></div> Локация (Location)</div>
                    </div>
                </div>
                <div class="control-group">
                    <label>Вложенность</label>
                    <div style="margin-top: 4px;">
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #3b82f6;"></div> Дочерняя связь</div>
                    </div>
                </div>
            `,
            story_branches: `
                <div class="control-group">
                    <label>Типы узлов сюжета</label>
                    <div style="margin-top: 4px;">
                        <div class="legend-item"><div class="legend-box" style="background-color: #3b82f6; border: 1px solid #1d4ed8;"></div> Сюжет (Story)</div>
                        <div class="legend-item"><div class="legend-box" style="background-color: #0ea5e9; border: 1px solid #0369a1;"></div> Сюжетная линия (Storyline)</div>
                        <div class="legend-item"><div class="legend-box" style="background-color: #8b5cf6; border: 1px solid #6d28d9;"></div> Ветка (Plot Branch)</div>
                        <div class="legend-item"><div class="legend-color" style="background-color: #f59e0b;"></div> Выбор (Choice)</div>
                        <div class="legend-item"><div class="legend-color" style="background-color: #ec4899;"></div> Последствие (Consequence)</div>
                        <div class="legend-item"><div class="legend-box" style="background-color: #10b981; border: 1px solid #047857; border-radius: 5px;"></div> Финал: хороший</div>
                        <div class="legend-item"><div class="legend-box" style="background-color: #ef4444; border: 1px solid #b91c1c; border-radius: 5px;"></div> Финал: плохой</div>
                        <div class="legend-item"><div class="legend-box" style="background-color: #9ca3af; border: 1px solid #4b5563; border-radius: 5px;"></div> Финал: нейтральный</div>
                        <div class="legend-item"><div class="legend-box" style="background-color: #14b8a6; border: 1px solid #0f766e;"></div> Эпилог (Epilogue)</div>
                    </div>
                </div>
                <div class="control-group">
                    <label>Связи повествования</label>
                    <div style="margin-top: 4px;">
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #f59e0b;"></div> выбор (Сюжет ➔ Choice)</div>
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #ec4899;"></div> приводит к последствию</div>
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #d97706;"></div> открывает ветку</div>
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #8b5cf6; border-top: 2px dashed #8b5cf6;"></div> разветвляет историю</div>
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #14b8a6; border-top: 2px dashed #14b8a6;"></div> эпилог (Финал ➔ Эпилог)</div>
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #0ea5e9; border-top: 2px dashed #0ea5e9;"></div> часть сюжета</div>
                    </div>
                </div>
            `,
            timeline: `
                <div class="control-group">
                    <label>Хронология (Узлы)</label>
                    <div style="margin-top: 4px;">
                        <div class="legend-item"><div class="legend-box" style="background-color: #10b981; border: 1px solid #1e293b;"></div> Эпоха Творения</div>
                        <div class="legend-item"><div class="legend-box" style="background-color: #3b82f6; border: 1px solid #1e293b;"></div> Королевства</div>
                        <div class="legend-item"><div class="legend-box" style="background-color: #ef4444; border: 1px solid #1e293b;"></div> Нашествие Тьмы</div>
                        <div class="legend-item"><div class="legend-box" style="background-color: #8b5cf6; transform: rotate(45deg); width: 10px; height: 10px; margin-left: 1px;"></div> Переход (Transition)</div>
                        <div class="legend-item"><div class="legend-color" style="background-color: #f59e0b;"></div> Событие (Event)</div>
                        <div class="legend-item"><div class="legend-color" style="background-color: #06b6d4;"></div> Мировое событие</div>
                    </div>
                </div>
                <div class="control-group">
                    <label>Связи времени</label>
                    <div style="margin-top: 4px;">
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #8b5cf6;"></div> Смена эпох</div>
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #9ca3af; border-top: 2px dashed #9ca3af;"></div> Датирование события</div>
                    </div>
                </div>
            `,
            factions: `
                <div class="control-group">
                    <label>Узлы политики</label>
                    <div style="margin-top: 4px;">
                        <div class="legend-item"><div class="legend-box" style="background-color: #6366f1; border: 1px solid #4338ca;"></div> Фракция</div>
                        <div class="legend-item"><div class="legend-color" style="background-color: #f59e0b;"></div> Персонаж</div>
                        <div class="legend-item"><div class="legend-box" style="background-color: #fbbf24; border: 1px solid #d97706; transform: rotate(45deg); width: 12px; height: 12px; margin-left: 0;"></div> Ранг / Иерархия</div>
                    </div>
                </div>
                <div class="control-group">
                    <label>Дипломатические связи</label>
                    <div style="margin-top: 4px;">
                        <div class="legend-item"><div style="width: 20px; height: 3px; background-color: #10b981;"></div> альянс / дружба</div>
                        <div class="legend-item"><div style="width: 20px; height: 3px; background-color: #ef4444; border-top: 3px dashed #ef4444;"></div> война / вражда</div>
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #3b82f6;"></div> родство / иерархия</div>
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #9ca3af;"></div> прочая связь</div>
                    </div>
                </div>
            `,
            crafting: `
                <div class="control-group">
                    <label>Узлы производства</label>
                    <div style="margin-top: 4px;">
                        <div class="legend-item"><div class="legend-box" style="background-color: #06b6d4; border: 1px solid #0891b2;"></div> Рецепт крафта</div>
                        <div class="legend-item"><div class="legend-box" style="background-color: #ec4899; border: 1px solid #be185d;"></div> Чертёж (Blueprint)</div>
                        <div class="legend-item"><div class="legend-box" style="background-color: #10b981; border: 1px solid #047857;"></div> Предмет (финал)</div>
                        <div class="legend-item"><div class="legend-color" style="background-color: #f59e0b;"></div> Материал</div>
                        <div class="legend-item"><div class="legend-box" style="background-color: #8b5cf6; border: 1px solid #6d28d9; transform: rotate(45deg); width: 12px; height: 12px; margin-left: 0;"></div> Компонент</div>
                    </div>
                </div>
                <div class="control-group">
                    <label>Цепочки крафта</label>
                    <div style="margin-top: 4px;">
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #f59e0b; border-top: 2px dashed #f59e0b;"></div> входной ресурс (требуется)</div>
                        <div class="legend-item"><div style="width: 20px; height: 3px; background-color: #10b981;"></div> производит предмет</div>
                        <div class="legend-item"><div style="width: 20px; height: 2px; background-color: #ec4899; border-top: 2px dashed #ec4899;"></div> требует чертёж</div>
                    </div>
                </div>
            `,
            todo: `
                <div class="control-group">
                    <label>О бэклоге</label>
                    <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.4; margin-top: 4px;">
                        Здесь представлены типы графов, планируемые к реализации в следующих обновлениях MythWeave.
                    </p>
                </div>
                <div class="control-group">
                    <label>Источники данных</label>
                    <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.4; margin-top: 4px;">
                        Данные парсятся напрямую из проектной документации <code style="color: #a78bfa;">FUTURE_GRAPHS_TODO.md</code>.
                    </p>
                </div>
            `,

        async function loadGraphData() {
            const type = document.getElementById('graphTypeSelect').value;
            currentGraphType = type;
            
            // Inject legend html
            document.getElementById('legendSection').innerHTML = legends[type] || '';
            
            const networkEl = document.getElementById('network');
            const todoEl = document.getElementById('todo-view');
            
            if (type === 'todo') {
                networkEl.style.display = 'none';
                todoEl.style.display = 'block';
                document.getElementById('nodeDetails').innerHTML = `
                    <div style="font-weight: 700; font-size: 14px; margin-bottom: 4px; color: var(--accent-color);">📋 Бэклог графов</div>
                    <div style="color: var(--text-secondary); font-size: 12px; line-height: 1.4;">
                        Выберите граф в списке справа, чтобы изучить требования, связи и целевые таблицы.
                    </div>
                `;
                
                try {
                    todoEl.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">Загрузка бэклога...</div>';
                    const response = await fetch('/api/todo');
                    const todoData = await response.json();
                    renderTodoCards(todoData);
                } catch (err) {
                    console.error("Failed to load todo data", err);
                    todoEl.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary); color: #ef4444;">Ошибка загрузки бэклога.</div>';
                }
            } else {
                networkEl.style.display = 'block';
                todoEl.style.display = 'none';
                document.getElementById('nodeDetails').innerHTML = '<p style="color: var(--text-secondary); text-align: center;">Кликните на узел для просмотра деталей</p>';
                
                try {
                    const response = await fetch(`/api/graph/${type}`);
                    const graphData = await response.json();
                    renderGraph(graphData);
                } catch (err) {
                    console.error("Failed to load graph data", err);
                    networkEl.innerHTML = `<div style="padding: 40px; text-align: center; color: var(--text-secondary);">Ошибка построения графа "${type}". Проверьте структуру SQLite.</div>`;
                }
            }
        }

        function renderTodoCards(todoData) {
            const todoEl = document.getElementById('todo-view');
            if (todoData.length === 0) {
                todoEl.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">Нет запланированных графов</div>';
                return;
            }
            
            let html = '<div class="todo-grid">';
            todoData.forEach(item => {
                let connList = '';
                if (item.connections && item.connections.length > 0) {
                    connList = '<div style="font-size: 12px; display: flex; flex-direction: column; gap: 4px; margin-top: 4px; color: var(--text-secondary);">';
                    item.connections.forEach(conn => {
                        connList += `<div style="display:flex; align-items:flex-start; gap: 6px;"><span>➔</span><span>${conn}</span></div>`;
                    });
                    connList += '</div>';
                }
                
                html += `
                    <div class="todo-card" onclick="selectTodoCard('${item.title.replace(/'/g, "\\'")}', '${item.goal.replace(/'/g, "\\'")}')" style="cursor: pointer;">
                        <h4>${item.title}</h4>
                        <p style="margin-top: 4px;"><strong>Цель:</strong> ${item.goal}</p>
                        ${connList ? `<div style="margin-top: 6px;"><strong>Связи:</strong>${connList}</div>` : ''}
                        ${item.benefit ? `<div class="todo-card-benefits" style="margin-top: 8px;"><strong>Польза:</strong> ${item.benefit}</div>` : ''}
                        <div class="todo-card-tables" style="margin-top: 10px;"><strong>Таблицы:</strong> ${item.tables}</div>
                    </div>
                `;
            });
            html += '</div>';
            todoEl.innerHTML = html;
        }

        function selectTodoCard(title, goal) {
            document.getElementById('nodeDetails').innerHTML = `
                <div style="font-weight: 700; font-size: 15px; margin-bottom: 8px; color: var(--accent-color);">${title}</div>
                <div style="line-height: 1.4; color: var(--text-secondary); font-size: 12px;">
                    <strong>Детали цели:</strong> ${goal}
                </div>
            `;
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
                        springLength: 120,
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

            // Custom adjustments for graph layouts
            if (currentGraphType === 'locations') {
                options.physics.barnesHut.springLength = 80;
                options.physics.barnesHut.gravitationalConstant = -2000;
            } else if (currentGraphType === 'story_branches') {
                options.layout = {
                    hierarchical: {
                        enabled: true,
                        direction: 'UD',
                        sortMethod: 'directed',
                        nodeSpacing: 160,
                        treeSpacing: 220,
                        levelSeparation: 140
                    }
                };
                options.physics = { enabled: false };
            } else if (currentGraphType === 'timeline') {
                options.layout = {
                    hierarchical: {
                        enabled: true,
                        direction: 'LR',
                        sortMethod: 'directed',
                        nodeSpacing: 100,
                        treeSpacing: 180,
                        levelSeparation: 150
                    }
                };
                options.physics = { enabled: false };
            } else if (currentGraphType === 'factions') {
                // Force-directed for a political map: clusters of allies vs
                // opposed factions spread naturally.
                options.physics = {
                    enabled: true,
                    solver: 'forceAtlas2Based',
                    forceAtlas2Based: {
                        gravitationalConstant: -60,
                        centralGravity: 0.01,
                        springLength: 140,
                        springConstant: 0.04,
                        damping: 0.5,
                        avoidOverlap: 0.6
                    },
                    stabilization: { iterations: 200 }
                };
            } else if (currentGraphType === 'crafting') {
                // Left-to-right flow: inputs (materials/components) on the
                // left, recipes in the middle, produced items on the right.
                options.layout = {
                    hierarchical: {
                        enabled: true,
                        direction: 'LR',
                        sortMethod: 'directed',
                        nodeSpacing: 90,
                        treeSpacing: 160,
                        levelSeparation: 180
                    }
                };
                options.physics = { enabled: false };
            }

            network = new vis.Network(container, graphData, options);

            // Click node event
            network.on("click", function (params) {
                if (params.nodes.length > 0) {
                    const nodeId = params.nodes[0];
                    const selectedNode = graphData.nodes.find(n => n.id === nodeId);
                    
                    if (selectedNode) {
                        const div = document.getElementById('nodeDetails');
                        let nodeColor = '#6366f1';
                        if (selectedNode.color) {
                            nodeColor = typeof selectedNode.color === 'string' ? selectedNode.color : selectedNode.color.background;
                        }
                        
                        div.innerHTML = `
                            <div style="font-weight: 700; font-size: 15px; margin-bottom: 8px; color: ${nodeColor};">${selectedNode.label}</div>
                            <div style="max-height: 180px; overflow-y: auto; line-height: 1.4; color: var(--text-secondary); font-size: 12px;">${selectedNode.title || 'Подробности отсутствуют.'}</div>
                        `;
                    }
                } else {
                    document.getElementById('nodeDetails').innerHTML = '<p style="color: var(--text-secondary); text-align: center;">Кликните на узел для просмотра деталей</p>';
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

        // Graph type select binding
        document.getElementById('graphTypeSelect').addEventListener('change', loadGraphData);

        // Init Load
        loadTables();
    </script>
</body>
</html>
"""
