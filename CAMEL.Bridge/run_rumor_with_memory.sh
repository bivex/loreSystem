#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
cd "$REPO_ROOT"

has_flag() {
    local needle="$1"
    shift
    for arg in "$@"; do
        if [[ "$arg" == "$needle" ]]; then
            return 0
        fi
    done
    return 1
}

print_help() {
    cat <<'EOF'
Usage: CAMEL.Bridge/run_rumor_with_memory.sh --theme "..." [run_rumor_pipeline.py args]

Convenience wrapper around CAMEL.Bridge/run_rumor_pipeline.py that:
  - enables --with-memory automatically
  - defaults CAMEL_MEMORY_QDRANT_URL to http://localhost:6333
  - defaults CAMEL_MEMORY_EMBED_BACKEND to hash
  - injects default --tenant-id/--world-id/--db-path if omitted

Defaults (override via env or explicit CLI args):
  CAMEL_BRIDGE_TENANT_ID=1
  CAMEL_BRIDGE_WORLD_ID=1
  CAMEL_BRIDGE_DB_PATH=lore_system.db
  CAMEL_MEMORY_QDRANT_URL=http://localhost:6333
  CAMEL_MEMORY_EMBED_BACKEND=hash
  CAMEL_MEMORY_QDRANT_COLLECTION=camel_bridge_memory

If .env exists in the repo root and --env-file is not passed, it will be used automatically.

Examples:
  CAMEL.Bridge/run_rumor_with_memory.sh \
    --theme "harbor omens" \
    --context "Sailors insist the harbor bells ring before vanishings." \
    --character "Mara Voss" \
    --character "Iven Hale"

  CAMEL_MEMORY_QDRANT_COLLECTION=camel_smoke \
  CAMEL.Bridge/run_rumor_with_memory.sh \
    --theme "harbor omens aftermath" \
    --character "Mara Voss" \
    --character "Iven Hale" \
    --count 1 \
    --with-systems
EOF
}

if [[ $# -eq 0 ]]; then
    print_help
    exit 1
fi

if has_flag "--help" "$@" || has_flag "-h" "$@"; then
    print_help
    echo
    python3 CAMEL.Bridge/run_rumor_pipeline.py --help
    exit 0
fi

export CAMEL_MEMORY_QDRANT_URL="${CAMEL_MEMORY_QDRANT_URL:-http://localhost:6333}"
export CAMEL_MEMORY_EMBED_BACKEND="${CAMEL_MEMORY_EMBED_BACKEND:-hash}"

DEFAULT_TENANT_ID="${CAMEL_BRIDGE_TENANT_ID:-1}"
DEFAULT_WORLD_ID="${CAMEL_BRIDGE_WORLD_ID:-1}"
DEFAULT_DB_PATH="${CAMEL_BRIDGE_DB_PATH:-lore_system.db}"
DEFAULT_ENV_FILE=""

if [[ -f ".env" ]]; then
    DEFAULT_ENV_FILE=".env"
fi

cmd=(python3 CAMEL.Bridge/run_rumor_pipeline.py "$@")

if ! has_flag "--tenant-id" "$@"; then
    cmd+=(--tenant-id "$DEFAULT_TENANT_ID")
fi

if ! has_flag "--world-id" "$@"; then
    cmd+=(--world-id "$DEFAULT_WORLD_ID")
fi

if ! has_flag "--db-path" "$@"; then
    cmd+=(--db-path "$DEFAULT_DB_PATH")
fi

if [[ -n "$DEFAULT_ENV_FILE" ]] && ! has_flag "--env-file" "$@"; then
    cmd+=(--env-file "$DEFAULT_ENV_FILE")
fi

if ! has_flag "--with-memory" "$@"; then
    cmd+=(--with-memory)
fi

exec "${cmd[@]}"