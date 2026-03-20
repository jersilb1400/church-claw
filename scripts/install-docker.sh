#!/usr/bin/env bash
# One-command ChurchClaw install (Docker).
# Usage: bash scripts/install-docker.sh
#    or: cd "$(dirname "$0")/.." && bash scripts/install-docker.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

COMPOSE_FILE="docker-compose.install.yml"
ENV_TARGET=".env"
ENV_EXAMPLE=".env.install.example"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

need_cmd docker
docker compose version >/dev/null 2>&1 || {
  echo "Need Docker Compose v2 (docker compose)." >&2
  exit 1
}

if [[ ! -f "$ENV_EXAMPLE" ]]; then
  echo "Expected $ENV_EXAMPLE in $ROOT" >&2
  exit 1
fi

if [[ ! -f "$ENV_TARGET" ]]; then
  echo "Creating $ENV_TARGET from $ENV_EXAMPLE ..."
  cp "$ENV_EXAMPLE" "$ENV_TARGET"
  # Generate secrets if openssl is available
  if command -v openssl >/dev/null 2>&1; then
    PW="$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 32)"
    SK="$(openssl rand -hex 32)"
    JK="$(openssl rand -hex 32)"
    if grep -q '^POSTGRES_PASSWORD=change-this-strong-db-password' "$ENV_TARGET" 2>/dev/null; then
      sed -i.bak "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$PW|" "$ENV_TARGET" && rm -f "${ENV_TARGET}.bak"
    fi
    if grep -q '^SECRET_KEY=change-this-app-secret' "$ENV_TARGET" 2>/dev/null; then
      sed -i.bak "s|^SECRET_KEY=.*|SECRET_KEY=$SK|" "$ENV_TARGET" && rm -f "${ENV_TARGET}.bak"
    fi
    if grep -q '^JWT_SECRET_KEY=change-this-jwt-secret' "$ENV_TARGET" 2>/dev/null; then
      sed -i.bak "s|^JWT_SECRET_KEY=.*|JWT_SECRET_KEY=$JK|" "$ENV_TARGET" && rm -f "${ENV_TARGET}.bak"
    fi
    echo "Generated random POSTGRES_PASSWORD, SECRET_KEY, JWT_SECRET_KEY."
  else
    echo "Edit $ENV_TARGET and set POSTGRES_PASSWORD, SECRET_KEY, JWT_SECRET_KEY before exposing to the network."
  fi
else
  echo "Using existing $ENV_TARGET"
fi

# docker-compose.install.yml requires POSTGRES_PASSWORD, SECRET_KEY, JWT_SECRET_KEY.
# Older dev-only .env files may omit POSTGRES_PASSWORD — add missing values here.
ensure_compose_secrets() {
  local pw_val sk_val jk_val
  pw_val="$(grep -E '^POSTGRES_PASSWORD=' "$ENV_TARGET" 2>/dev/null | sed 's/^POSTGRES_PASSWORD=//' | tr -d '\r' || true)"
  sk_val="$(grep -E '^SECRET_KEY=' "$ENV_TARGET" 2>/dev/null | sed 's/^SECRET_KEY=//' | tr -d '\r' || true)"
  jk_val="$(grep -E '^JWT_SECRET_KEY=' "$ENV_TARGET" 2>/dev/null | sed 's/^JWT_SECRET_KEY=//' | tr -d '\r' || true)"

  if [[ -n "$pw_val" && -n "$sk_val" && -n "$jk_val" ]]; then
    return 0
  fi

  if ! command -v openssl >/dev/null 2>&1; then
    echo "Your $ENV_TARGET is missing required variables for Docker Compose." >&2
    echo "Add non-empty lines for: POSTGRES_PASSWORD, SECRET_KEY, JWT_SECRET_KEY" >&2
    echo "(see $ENV_EXAMPLE)." >&2
    exit 1
  fi

  echo "Adding missing Compose secrets to $ENV_TARGET ..."
  {
    echo ""
    echo "# --- Added by scripts/install-docker.sh for docker-compose.install.yml ---"
    [[ -z "$pw_val" ]] && echo "POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 32)"
    [[ -z "$sk_val" ]] && echo "SECRET_KEY=$(openssl rand -hex 32)"
    [[ -z "$jk_val" ]] && echo "JWT_SECRET_KEY=$(openssl rand -hex 32)"
  } >>"$ENV_TARGET"
}

ensure_compose_secrets

echo "Building and starting ChurchClaw..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_TARGET" up -d --build

PORT="$(grep -E '^CHURCHCLAW_PORT=' "$ENV_TARGET" 2>/dev/null | cut -d= -f2 || true)"
PORT="${PORT:-8080}"

echo ""
echo "ChurchClaw is starting."
echo "  UI:  http://127.0.0.1:${PORT}"
echo "  Health (via frontend proxy): curl -s http://127.0.0.1:${PORT}/api/health"
echo ""
echo "First user to register becomes platform admin."
echo "Optional host Docker for OpenClaw agents:"
echo "  docker compose -f docker-compose.install.yml -f docker-compose.host-docker.yml --env-file .env up -d"
