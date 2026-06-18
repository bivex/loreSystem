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

*   **Split `src/infrastructure/sqlite_repositories.py`** (~28,916 LOC) — Partition the large database setup and SQLite repository classes into domain-driven sub-repositories.
*   **Split `src/infrastructure/in_memory_repositories.py`** (~16,731 LOC) — Partition fast in-memory mock repositories.
*   ~~**Split `src/application/integration/camel_bridge/rumor_agents.py`** (~16,113 LOC) — DONE 2026-06-17: decomposed into submodules.~~
*   **Split `src/presentation/gui/lore_editor.py`** (~3,172 LOC) — Split GUI editor tabs and views into smaller sub-modules.
*   **Split `tests/test_camel_bridge_rumor_pipeline.py`** (~2,967 LOC) — Decompose monolithic integration tests into domain test files.
*   **Split `src/presentation/gui/lore_data.py`** (~2,229 LOC) — Modularize PyQt model bindings.
*   **Split `scripts/CREATE_POLITICS.py`** (~1,642 LOC) — Modularize bulk data script.
*   **Split `src/presentation/cli.py`** (~1,618 LOC) — Refactor CLI command implementations.
*   **Split `scripts/cli.py`** (~1,597 LOC) — Consolidate or modularize duplicate CLI file.
*   **Split `scripts/APPLY_PARTY4.py`** (~1,345 LOC) — Refactor logic into helper classes.


