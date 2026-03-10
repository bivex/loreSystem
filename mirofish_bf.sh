#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIROFISH_DIR="$ROOT_DIR/MiroFish"

usage() {
  cat <<'EOF'
Easy launcher for MiroFish backend + frontend.

Usage:
  ./mirofish_bf.sh
  ./mirofish_bf.sh --help

Starts:
  - backend on http://localhost:5001
  - frontend on http://localhost:3000

Uses MiroFish/.env for backend config.
Stop both services with Ctrl+C.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ ! -d "$MIROFISH_DIR" ]]; then
  echo "❌ MiroFish directory not found: $MIROFISH_DIR" >&2
  exit 1
fi

if [[ ! -f "$MIROFISH_DIR/package.json" ]]; then
  echo "❌ MiroFish/package.json not found." >&2
  exit 1
fi

if [[ ! -f "$MIROFISH_DIR/.env" ]]; then
  echo "❌ Missing MiroFish/.env" >&2
  echo "   Create it first, e.g.: cp MiroFish/.env.example MiroFish/.env" >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "❌ npm is required but was not found in PATH." >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "❌ uv is required but was not found in PATH." >&2
  exit 1
fi

echo "🚀 Starting MiroFish backend + frontend"
echo "📁 Directory: $MIROFISH_DIR"
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend:  http://localhost:5001"
echo "🛑 Stop: Ctrl+C"
echo

cd "$MIROFISH_DIR"
exec npm run dev