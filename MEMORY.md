# Memory: MythWeave Chronicles

## Project Context
This is a comprehensive lore management system for AAA game development, extracting, validating, and managing 200+ entity types across 34 categories from narrative text.

## Lessons Learned & Key Decisions
1.  **Monolith Prevention**: Monolithic files like `server.py` (3.4k LOC), `sqlite_repositories.py` (29k LOC), and `rumor_agents.py` (16k LOC) cause severe editor lag, compilation hazards (indentation mistakes), and merge conflicts. We must modularize early.
2.  **MCP Server Modularization (2026-06-17)**:
    *   Split `server.py` into `db.py`, `tools_list.py`, `tools_call.py`, and a thin `server.py` wrapper.
    *   This keeps repository configuration, schemas, execution, and entry point strictly decoupled.
3.  **Indentation and Multiline String Hazards**:
    *   Found class definitions incorrectly nested inside other class methods due to bad indentation in `sqlite_repositories.py`.
    *   Multiline string literals must use triple quotes `"""` and closing brackets correctly in raw sqlite query scripts.

## Active Backlog (Prioritized Refactoring)
*   **Split `src/infrastructure/sqlite_repositories.py`** (~29,210 LOC) — Partition the large database setup and SQLite repository classes into domain-driven sub-repositories.
*   **Split `src/infrastructure/in_memory_repositories.py`** (~16,731 LOC) — Partition fast in-memory mock repositories.
*   **Split `src/application/integration/camel_bridge/rumor_agents.py`** (~16,113 LOC) — Segment rumor agents, chroniclers, relationship managers, and enrichment managers.
