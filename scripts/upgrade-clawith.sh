#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TARGET_TAG="${1:-}"
if [[ -z "$TARGET_TAG" ]]; then
  echo "Usage: bash scripts/upgrade-clawith.sh <tag>"
  echo "Example: bash scripts/upgrade-clawith.sh v1.7.1"
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "This script must run inside a git repository."
  exit 1
fi

if ! git remote get-url upstream >/dev/null 2>&1; then
  echo "Adding upstream remote: https://github.com/dataelement/Clawith.git"
  git remote add upstream https://github.com/dataelement/Clawith.git
fi

echo "Fetching upstream tags..."
git fetch upstream --tags

if ! git rev-parse "refs/tags/$TARGET_TAG" >/dev/null 2>&1 && ! git rev-parse "upstream/$TARGET_TAG" >/dev/null 2>&1; then
  echo "Tag not found locally after fetch: $TARGET_TAG"
  echo "Check available tags with: git tag -l | tail -n 20"
  exit 1
fi

echo "Checking out main..."
git checkout main

echo "Merging $TARGET_TAG..."
git merge "$TARGET_TAG"

echo
echo "Upgrade merge complete for $TARGET_TAG"
echo "IMPORTANT: follow sequential upgrades if release notes require version-by-version migration."
echo "Validation checklist:"
echo "  docker compose build backend frontend"
echo "  docker compose up -d"
