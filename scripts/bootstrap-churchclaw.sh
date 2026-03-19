#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f ".env" ]]; then
  cp ".env.example" ".env"
  echo "Created .env from .env.example"
fi

if [[ ! -f ".env.churchclaw" ]]; then
  cp ".env.churchclaw.example" ".env.churchclaw"
  echo "Created .env.churchclaw from .env.churchclaw.example"
fi

if [[ ! -f "churchclaw/config/church-profile.yaml" ]]; then
  cp "churchclaw/config/church-profile.example.yaml" "churchclaw/config/church-profile.yaml"
  echo "Created churchclaw/config/church-profile.yaml"
fi

if [[ ! -f "churchclaw/config/providers.yaml" ]]; then
  cp "churchclaw/config/providers.example.yaml" "churchclaw/config/providers.yaml"
  echo "Created churchclaw/config/providers.yaml"
fi

if [[ ! -f "churchclaw/config/bootstrap.json" ]]; then
  cp "churchclaw/config/bootstrap.example.json" "churchclaw/config/bootstrap.json"
  echo "Created churchclaw/config/bootstrap.json"
fi

if [[ ! -f "churchclaw/config/litellm.config.yaml" ]]; then
  cp "churchclaw/config/litellm.config.example.yaml" "churchclaw/config/litellm.config.yaml"
  echo "Created churchclaw/config/litellm.config.yaml"
fi

echo
echo "Bootstrap complete."
echo "Next steps:"
echo "  1) Fill secrets in .env and .env.churchclaw"
echo "  2) Start core stack: docker compose up -d"
echo "  3) Optional providers: docker compose -f docker-compose.yml -f docker-compose.providers.yml --profile providers up -d"
echo "  4) Provision phases 2-5: python3 scripts/provision-churchclaw.py --username <admin> --password <pass>"
