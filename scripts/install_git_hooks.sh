#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -z "$REPO_ROOT" ]; then
    echo "Error: run this script from inside the repository." >&2
    exit 1
fi

HOOKS_DIR="$REPO_ROOT/.githooks"

if [ ! -d "$HOOKS_DIR" ]; then
    echo "Error: hooks directory not found: $HOOKS_DIR" >&2
    exit 1
fi

chmod +x "$HOOKS_DIR"/*

git config core.hooksPath .githooks

echo "Git hooks installed from $HOOKS_DIR"
echo "Active hooks path: $(git config --get core.hooksPath)"
echo "Use 'git config --unset core.hooksPath' to disable them for this clone."
