# 🐳 Docker Deployment Guide

MythWeave supports full containerization using Docker and Docker Compose. This is the recommended way to run the system if you want to avoid manual dependency management and automatically set up supporting services like **Elasticsearch** and **Qdrant**.

## 🚀 Quick Start with Docker

1.  **Prepare Environment**:
    ```bash
    cp .env.example .env
    # Edit .env to add your API keys (OPENROUTER_API_KEY, etc.)
    ```

2.  **Start Services**:
    ```bash
    docker compose up -d
    ```
    This will build the `lore-system` image and start:
    - **lore-system**: The main application (CLI, MCP, Python core).
    - **lore-qdrant**: Vector database for AI memory.
    - **lore-elastic**: Search engine for lore indexing.

## 🛠️ Common Commands

### Running Lore Generation (CAMEL.Bridge)
To generate lore inside the container:
```bash
docker compose exec lore-system python CAMEL.Bridge/run_rumor_pipeline.py --count 3 --output-language ru
```

### Running the MCP Server
The MCP server is exposed on port `12345` by default:
```bash
docker compose exec lore-system python lore_mcp_server/run_server.py
```

### Checking Logs
```bash
docker compose logs -f lore-system
```

### Accessing the Container Shell
```bash
docker compose exec lore-system bash
```

## 🏗️ Services Overview

| Service | Port | Description |
|---------|------|-------------|
| `lore-system` | 8000, 12345 | Main logic, CLI, and MCP tools. |
| `qdrant` | 6333 | Vector storage for long-term AI memory. |
| `elasticsearch` | 9200 | Full-text search and indexing for the lore database. |

## 📁 Data Persistence
- Lore database and exports are stored in the `lore_data` volume.
- Qdrant indexes are stored in `qdrant_data`.
- Elasticsearch data is stored in `es_data`.

To wipe everything and start fresh:
```bash
docker compose down -v
```

## 🔍 Troubleshooting

- **API Keys**: Ensure `OPENROUTER_API_KEY` or `OPENAI_API_KEY` is set in `.env` before starting.
- **Memory Limits**: Elasticsearch requires at least 1GB of RAM. If it fails to start, ensure your Docker Desktop has enough resources.
- **Ports**: If port 12345 or 9200 is already in use, change the mapping in `docker-compose.yml`.
