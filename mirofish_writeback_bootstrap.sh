#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIROFISH_DIR="$ROOT_DIR/MiroFish"
BACKEND_DIR="$MIROFISH_DIR/backend"
FRONTEND_DIR="$MIROFISH_DIR/frontend"
MIROFISH_ENV_FILE="$MIROFISH_DIR/.env"
DB_PATH="$ROOT_DIR/lore_system.db"
WRITEBACK_HOST="127.0.0.1"
WRITEBACK_PORT="8080"
BACKEND_HOST="0.0.0.0"
BACKEND_PORT="5001"
FRONTEND_HOST="0.0.0.0"
FRONTEND_PORT="3000"
DRY_RUN="false"
PIDS=()
_CLEANED_UP="false"

usage() {
  cat <<'EOF'
Easy bootstrap for loreSystem write-back API + MiroFish backend + frontend.

Usage:
  ./mirofish_writeback_bootstrap.sh
  ./mirofish_writeback_bootstrap.sh --db /path/to/lore_system.db
  ./mirofish_writeback_bootstrap.sh --dry-run

Starts:
  - loreSystem write-back API on http://127.0.0.1:8080
  - MiroFish backend on http://127.0.0.1:5001
  - MiroFish frontend on http://127.0.0.1:3000

The script forces MiroFish write-back env at runtime and points the frontend to
the selected backend URL via VITE_API_BASE_URL.

Options:
  --db PATH               SQLite DB path (default: ./lore_system.db)
  --mirofish-env PATH     MiroFish .env path (default: ./MiroFish/.env)
  --writeback-port PORT   Write-back API port (default: 8080)
  --backend-port PORT     MiroFish backend port (default: 5001)
  --frontend-port PORT    MiroFish frontend port (default: 3000)
  --dry-run               Print the resolved launch plan without starting services
  -h, --help              Show this help message

Stop all services with Ctrl+C.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --db)
      DB_PATH="$2"
      shift 2
      ;;
    --mirofish-env)
      MIROFISH_ENV_FILE="$2"
      shift 2
      ;;
    --writeback-port)
      WRITEBACK_PORT="$2"
      shift 2
      ;;
    --backend-port)
      BACKEND_PORT="$2"
      shift 2
      ;;
    --frontend-port)
      FRONTEND_PORT="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "❌ Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

WRITEBACK_URL="http://127.0.0.1:${WRITEBACK_PORT}"
BACKEND_URL="http://127.0.0.1:${BACKEND_PORT}"
FRONTEND_URL="http://127.0.0.1:${FRONTEND_PORT}"

if [[ -x "$BACKEND_DIR/.venv/bin/python3" ]]; then
  BACKEND_LAUNCHER="$BACKEND_DIR/.venv/bin/python3 run.py"
else
  BACKEND_LAUNCHER="uv run python run.py"
fi

print_plan() {
  cat <<EOF
Bootstrap plan
  root_dir: $ROOT_DIR
  db_path: $DB_PATH
  mirofish_env: $MIROFISH_ENV_FILE
  writeback_url: $WRITEBACK_URL
  backend_url: $BACKEND_URL
  frontend_url: $FRONTEND_URL

Commands
  writeback_api: python3 scripts/run_mirofish_writeback_api.py --host $WRITEBACK_HOST --port $WRITEBACK_PORT --db $DB_PATH
  mirofish_backend: $BACKEND_LAUNCHER
  mirofish_frontend: npm run dev -- --host $FRONTEND_HOST --port $FRONTEND_PORT --strictPort

Runtime overrides
  MIROFISH_WRITEBACK_ENABLED=true
  MIROFISH_WRITEBACK_BASE_URL=$WRITEBACK_URL
  MIROFISH_WRITEBACK_AUTO_PROMOTE_ENABLED=false
  FLASK_PORT=$BACKEND_PORT
  VITE_API_BASE_URL=$BACKEND_URL
EOF
}

if [[ "$DRY_RUN" == "true" ]]; then
  print_plan
  exit 0
fi

if [[ ! -d "$MIROFISH_DIR" ]]; then
  echo "❌ MiroFish directory not found: $MIROFISH_DIR" >&2
  exit 1
fi

if [[ ! -f "$MIROFISH_ENV_FILE" ]]; then
  echo "❌ Missing MiroFish env file: $MIROFISH_ENV_FILE" >&2
  echo "   Create it first, e.g.: cp MiroFish/.env.example MiroFish/.env" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 is required but was not found in PATH." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "❌ npm is required but was not found in PATH." >&2
  exit 1
fi

if [[ ! -x "$BACKEND_DIR/.venv/bin/python3" ]] && ! command -v uv >/dev/null 2>&1; then
  echo "❌ Need either MiroFish/backend/.venv/bin/python3 or uv in PATH." >&2
  exit 1
fi

cleanup() {
  if [[ "$_CLEANED_UP" == "true" ]]; then
    return
  fi
  _CLEANED_UP="true"

  for pid in "${PIDS[@]:-}"; do
    kill "$pid" >/dev/null 2>&1 || true
  done

  wait >/dev/null 2>&1 || true
}

trap 'cleanup; exit 0' INT TERM
trap 'cleanup' EXIT

echo "🚀 Starting loreSystem write-back stack"
echo "📦 Write-back API: $WRITEBACK_URL"
echo "🔌 MiroFish backend: $BACKEND_URL"
echo "🌐 MiroFish frontend: $FRONTEND_URL"
echo "🗃️  DB: $DB_PATH"
echo "🛑 Stop all: Ctrl+C"
echo

(
  cd "$ROOT_DIR"
  exec python3 scripts/run_mirofish_writeback_api.py --host "$WRITEBACK_HOST" --port "$WRITEBACK_PORT" --db "$DB_PATH"
) &
PIDS+=("$!")

(
  cd "$BACKEND_DIR"
  export FLASK_HOST="$BACKEND_HOST"
  export FLASK_PORT="$BACKEND_PORT"
  export MIROFISH_WRITEBACK_ENABLED="true"
  export MIROFISH_WRITEBACK_BASE_URL="$WRITEBACK_URL"
  export MIROFISH_WRITEBACK_AUTO_PROMOTE_ENABLED="false"
  if [[ -x "./.venv/bin/python3" ]]; then
    exec ./.venv/bin/python3 run.py
  fi
  exec uv run python run.py
) &
PIDS+=("$!")

(
  cd "$FRONTEND_DIR"
  export VITE_API_BASE_URL="$BACKEND_URL"
  exec npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT" --strictPort
) &
PIDS+=("$!")

echo "Started PIDs: ${PIDS[*]}"

while true; do
  for pid in "${PIDS[@]}"; do
    if ! kill -0 "$pid" >/dev/null 2>&1; then
      echo "⚠️  Service with PID $pid exited; shutting down the stack." >&2
      exit 1
    fi
  done
  sleep 2
done