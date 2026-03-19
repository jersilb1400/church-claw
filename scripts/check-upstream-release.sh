#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_REPO="https://github.com/dataelement/Clawith.git"

echo "Fetching latest upstream tags from $UPSTREAM_REPO ..."
LATEST_TAG="$(git ls-remote --tags --refs "$UPSTREAM_REPO" | awk -F/ '{print $3}' | sort -V | tail -n 1)"

if [[ -z "${LATEST_TAG}" ]]; then
  echo "Unable to determine latest upstream tag."
  exit 1
fi

echo "Latest upstream Clawith tag: $LATEST_TAG"
echo "Upgrade with: bash scripts/upgrade-clawith.sh $LATEST_TAG"
