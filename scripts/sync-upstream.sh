#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "This script must run inside a git repository."
  exit 1
fi

if ! git remote get-url upstream >/dev/null 2>&1; then
  echo "Adding upstream remote: https://github.com/dataelement/Clawith.git"
  git remote add upstream https://github.com/dataelement/Clawith.git
fi

echo "Fetching upstream..."
git fetch upstream --tags

echo "Checking out main..."
git checkout main

echo "Merging upstream/main..."
git merge upstream/main

echo
echo "Sync complete. Run validation before pushing:"
echo "  docker compose build backend frontend"
echo "  docker compose up -d"
