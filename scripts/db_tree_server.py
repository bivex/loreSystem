#!/usr/bin/env python3
"""Lightweight SQLite tree viewer for loreSystem bridge databases."""

from __future__ import annotations

import argparse
import html
import json
import sqlite3
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


HTML_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>loreSystem DB Tree</title>
  <style>
    :root {
      --bg: #0d1117;
      --panel: #111827;
      --panel-2: #1f2937;
      --text: #e5e7eb;
      --muted: #9ca3af;
      --accent: #60a5fa;
      --border: #374151;
      --good: #34d399;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: linear-gradient(180deg, #0b1020 0%, var(--bg) 100%);
      color: var(--text);
    }
    header {
      padding: 16px 20px;
      border-bottom: 1px solid var(--border);
      background: rgba(17, 24, 39, 0.9);
      position: sticky;
      top: 0;
      backdrop-filter: blur(12px);
      z-index: 10;
    }
    header h1 {
      margin: 0;
      font-size: 18px;
    }
    header .meta {
      margin-top: 6px;
      color: var(--muted);
      font-size: 13px;
    }
    main {
      display: grid;
      grid-template-columns: 320px 1fr;
      min-height: calc(100vh - 75px);
    }
    aside {
      border-right: 1px solid var(--border);
      padding: 16px;
      background: rgba(17, 24, 39, 0.7);
    }
    section {
      padding: 16px 20px 40px;
    }
    .table-button {
      width: 100%;
      text-align: left;
      margin: 0 0 8px;
      padding: 10px 12px;
      border: 1px solid var(--border);
      border-radius: 10px;
      background: var(--panel);
      color: var(--text);
      cursor: pointer;
    }
    .table-button:hover, .table-button.active {
      border-color: var(--accent);
      background: #172033;
    }
    .table-button .count {
      float: right;
      color: var(--good);
    }
    .toolbar {
      display: flex;
      gap: 12px;
      align-items: center;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }
    input[type="search"], input[type="number"] {
      background: var(--panel);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 8px 10px;
    }
    .row-card {
      background: rgba(17, 24, 39, 0.92);
      border: 1px solid var(--border);
      border-radius: 12px;
      margin-bottom: 12px;
      overflow: hidden;
    }
    .row-card summary {
      cursor: pointer;
      list-style: none;
      padding: 12px 14px;
      background: rgba(31, 41, 55, 0.7);
    }
    .row-card summary::-webkit-details-marker { display: none; }
    .row-title {
      font-weight: 600;
    }
    .row-meta {
      color: var(--muted);
      font-size: 12px;
      margin-top: 4px;
    }
    .tree {
      padding: 12px 14px 16px;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 13px;
      line-height: 1.5;
    }
    .tree details {
      margin-left: 14px;
      border-left: 1px dashed var(--border);
      padding-left: 10px;
    }
    .tree summary {
      cursor: pointer;
      color: var(--accent);
      background: none;
      padding: 2px 0;
    }
    .leaf {
      margin-left: 14px;
      padding-left: 10px;
      border-left: 1px dashed rgba(55, 65, 81, 0.6);
      word-break: break-word;
    }
    .leaf-key { color: var(--muted); }
    .leaf-value.string { color: #fde68a; }
    .leaf-value.number { color: #93c5fd; }
    .leaf-value.boolean { color: #fca5a5; }
    .status {
      color: var(--muted);
      padding: 10px 0;
    }
    @media (max-width: 920px) {
      main { grid-template-columns: 1fr; }
      aside { border-right: none; border-bottom: 1px solid var(--border); }
    }
  </style>
</head>
<body>
  <header>
    <h1>loreSystem DB Tree</h1>
    <div class="meta" id="db-meta">
      <select id="db-selector" style="background:var(--panel);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:4px 8px;margin-left:12px;">
        <option value="">Loading databases…</option>
      </select>
      <span id="db-info"></span>
    </div>
  </header>
  <main>
    <aside>
      <div id="table-list" class="status">Loading tables…</div>
    </aside>
    <section>
      <div class="toolbar">
        <input id="search" type="search" placeholder="Filter tables">
        <label>Rows
          <input id="limit" type="number" min="1" max="500" value="50">
        </label>
      </div>
      <div id="content" class="status">Choose a table on the left.</div>
    </section>
  </main>
  <script>
    const state = { summary: null, activeTable: null, currentDb: null };

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;");
    }

    async function loadDatabaseList() {
      const response = await fetch("/api/databases");
      const dbs = await response.json();
      const selector = document.getElementById("db-selector");
      selector.innerHTML = dbs.map((db, i) =>
        `<option value="${escapeHtml(db)}"${db === state.currentDb ? " selected" : ""}>${escapeHtml(db)}</option>`
      ).join("");
      selector.addEventListener("change", () => {
        const dbFile = selector.value;
        if (dbFile) {
          window.location.href = `/?db=${encodeURIComponent(dbFile)}`;
        }
      });
    }

    function renderNode(key, value) {
      if (Array.isArray(value)) {
        const items = value.map((item, index) => renderNode(index, item)).join("");
        return `<details open><summary>${escapeHtml(key)} [${value.length}]</summary>${items}</details>`;
      }
      if (value && typeof value === "object") {
        const entries = Object.entries(value).map(([childKey, childValue]) => renderNode(childKey, childValue)).join("");
        return `<details open><summary>${escapeHtml(key)}</summary>${entries}</details>`;
      }
      const kind = value === null ? "null" : typeof value;
      return `<div class="leaf"><span class="leaf-key">${escapeHtml(key)}:</span> <span class="leaf-value ${kind}">${escapeHtml(value)}</span></div>`;
    }

    function rowLabel(row) {
      const preferred = row.preview_label || row.row.name || row.row.title || row.row.id || "row";
      return `${preferred}`;
    }

    async function loadSummary() {
      const response = await fetch("/api/summary");
      const summary = await response.json();
      state.summary = summary;
      state.currentDb = summary.db_path.split('/').pop();
      document.getElementById("db-info").textContent = `${summary.table_count} tables`;
      renderTables(summary.tables);
      // Update selector to highlight current DB
      const selector = document.getElementById("db-selector");
      if (selector && state.currentDb) {
        selector.value = state.currentDb;
      }
    }

    function renderTables(tables) {
      const filter = document.getElementById("search").value.trim().toLowerCase();
      const visible = tables.filter((table) => table.name.toLowerCase().includes(filter));
      const list = document.getElementById("table-list");
      if (!visible.length) {
        list.innerHTML = '<div class="status">No tables match the filter.</div>';
        return;
      }
      list.innerHTML = visible.map((table) => `
        <button class="table-button ${state.activeTable === table.name ? "active" : ""}" data-table="${table.name}">
          <span>${escapeHtml(table.name)}</span>
          <span class="count">${table.count}</span>
        </button>
      `).join("");
      document.querySelectorAll(".table-button").forEach((button) => {
        button.addEventListener("click", () => loadTable(button.dataset.table));
      });
    }

    async function loadTable(tableName) {
      state.activeTable = tableName;
      renderTables(state.summary.tables);
      const limit = Number(document.getElementById("limit").value || 50);
      const content = document.getElementById("content");
      content.innerHTML = `<div class="status">Loading ${escapeHtml(tableName)}…</div>`;
      const response = await fetch(`/api/table/${encodeURIComponent(tableName)}?limit=${limit}`);
      const payload = await response.json();
      if (payload.error) {
        content.innerHTML = `<div class="status">${escapeHtml(payload.error)}</div>`;
        return;
      }
      if (!payload.rows.length) {
        content.innerHTML = `<div class="status">${escapeHtml(tableName)} is empty.</div>`;
        return;
      }
      content.innerHTML = payload.rows.map((row) => `
        <details class="row-card">
          <summary>
            <div class="row-title">${escapeHtml(rowLabel(row))}</div>
            <div class="row-meta">row ${row.index} • columns: ${escapeHtml(row.columns.join(", "))}</div>
          </summary>
          <div class="tree">${renderNode(tableName, row.parsed)}</div>
        </details>
      `).join("");
    }

    document.getElementById("search").addEventListener("input", () => {
      if (state.summary) renderTables(state.summary.tables);
    });
    document.getElementById("limit").addEventListener("change", () => {
      if (state.activeTable) loadTable(state.activeTable);
    });
    // Load database list first, then summary
    loadDatabaseList().then(() => loadSummary()).catch((error) => {
      document.getElementById("table-list").textContent = String(error);
      document.getElementById("content").textContent = String(error);
    });
  </script>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve a collapsible tree view for a loreSystem SQLite database.")
    parser.add_argument("--db-path", required=True, help="Path to the SQLite database file")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--limit", type=int, default=50, help="Default row limit per table")
    return parser.parse_args()


class DatabaseExplorer:
    def __init__(self, db_path: str, base_dir: str = "tmp"):
        self.base_dir = Path(base_dir).expanduser().resolve()
        self.db_path = self._resolve_db_path(db_path)

    def _resolve_db_path(self, db_path: str) -> str:
        p = Path(db_path).expanduser()
        if p.is_absolute():
            return str(p.resolve())
        # Relative to base_dir if not found as-is
        candidate = self.base_dir / p
        if candidate.exists():
            return str(candidate.resolve())
        # Fallback to as-is (for backwards compatibility)
        return str(p.resolve()) if p.exists() else str(candidate)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def table_summary(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            ).fetchall()
            tables: list[dict[str, Any]] = []
            for row in rows:
                name = str(row["name"])
                count = conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
                tables.append({"name": name, "count": count})
            return tables

    @staticmethod
    def list_databases(base_dir: str = "tmp") -> list[str]:
        """Return list of .db files in base_dir relative to project root."""
        root = Path(__file__).parent.parent.resolve()
        db_dir = root / base_dir
        if not db_dir.exists():
            return []
        return [f"{base_dir}/{p.name}" for p in sorted(db_dir.glob("*.db"))]

    def fetch_table(self, table_name: str, limit: int) -> list[dict[str, Any]]:
        safe_limit = max(1, min(limit, 500))
        with self._connect() as conn:
            column_rows = conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()
            columns = [str(row["name"]) for row in column_rows]
            if not columns:
                raise KeyError(f"Unknown table: {table_name}")
            has_id = "id" in columns
            order_by = 'ORDER BY "id" DESC' if has_id else ""
            rows = conn.execute(
                f'SELECT * FROM "{table_name}" {order_by} LIMIT ?',
                (safe_limit,),
            ).fetchall()
            return [
                self._serialize_row(index, columns, row)
                for index, row in enumerate(rows, start=1)
            ]

    def _serialize_row(self, index: int, columns: list[str], row: sqlite3.Row) -> dict[str, Any]:
        raw = {column: row[column] for column in columns}
        parsed = {column: self._decode_value(column, row[column]) for column in columns}
        preview_label = self._preview_label(raw, parsed)
        return {
            "index": index,
            "columns": columns,
            "row": raw,
            "parsed": parsed,
            "preview_label": preview_label,
        }

    def _decode_value(self, column: str, value: Any) -> Any:
        if value is None:
            return None
        if column == "payload_json":
            return self._decode_json_value(value)
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        if isinstance(value, str):
            maybe_json = self._decode_json_value(value, only_if_json_like=True)
            return maybe_json
        return value

    def _decode_json_value(self, value: Any, *, only_if_json_like: bool = False) -> Any:
        if isinstance(value, (dict, list, int, float, bool)) or value is None:
            return value
        if isinstance(value, bytes):
            text = value.decode("utf-8", errors="replace").strip()
        else:
            text = str(value).strip()
        if not text:
            return text
        if only_if_json_like and text[:1] not in "{[":
            return text
        try:
            return json.loads(text)
        except Exception:
            return text

    def _preview_label(self, raw: dict[str, Any], parsed: dict[str, Any]) -> str:
        payload = parsed.get("payload_json")
        if isinstance(payload, dict):
            for field in ("name", "title", "prompt", "description"):
                value = payload.get(field)
                if value:
                    return str(value)
        for field in ("name", "title", "prompt", "id"):
            value = raw.get(field)
            if value not in (None, ""):
                return str(value)
        return "row"


class TreeRequestHandler(BaseHTTPRequestHandler):
    default_limit: int
    base_dir: str = "tmp"

    def _get_explorer(self, db_query: str | None = None) -> DatabaseExplorer:
        """Create explorer from query param or use default from server args."""
        if db_query:
            return DatabaseExplorer(db_query, base_dir=self.base_dir)
        # Fallback to server-configured default (passed via class attribute)
        if hasattr(self, "default_db"):
            return DatabaseExplorer(self.default_db, base_dir=self.base_dir)
        raise RuntimeError("No database specified")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        query_params = parse_qs(parsed.query)
        db_query = query_params.get("db", [None])[0]

        if parsed.path == "/":
            self._send_html(HTML_PAGE)
            return
        if parsed.path == "/api/databases":
            self._send_json(DatabaseExplorer.list_databases(base_dir=self.base_dir))
            return
        if parsed.path == "/api/summary":
            explorer = self._get_explorer(db_query)
            self._send_json({
                "db_path": explorer.db_path,
                "table_count": len(explorer.table_summary()),
                "tables": explorer.table_summary(),
            })
            return
        if parsed.path.startswith("/api/table/"):
            table_name = parsed.path.removeprefix("/api/table/")
            params = query_params
            limit = self.default_limit
            if "limit" in params:
                try:
                    limit = int(params["limit"][0])
                except Exception:
                    pass
            explorer = self._get_explorer(db_query)
            try:
                rows = explorer.fetch_table(table_name, limit)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"table": table_name, "rows": rows})
            return
        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _send_html(self, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_json(self, payload: Any, *, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def make_handler(default_db: str, default_limit: int) -> type[TreeRequestHandler]:
    class Handler(TreeRequestHandler):
        pass

    Handler.default_db = default_db
    Handler.default_limit = default_limit
    Handler.base_dir = "tmp"
    return Handler


def main() -> int:
    args = parse_args()
    db_path = Path(args.db_path).expanduser().resolve()
    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}")
    server = ThreadingHTTPServer(
        (args.host, args.port),
        make_handler(str(db_path), args.limit)
    )
    print(f"Serving DB tree for {db_path} on http://{args.host}:{args.port}")
    print(f"Base directory for DB scans: {db_path.parent}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
