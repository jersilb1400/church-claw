# ChurchClaw

ChurchClaw is a church/ministry-focused distribution of Clawith designed for local deployment on a Mac Mini with:

- Multi-user staff support and RBAC
- Ministry-specific agents and workflows
- MCP integrations (Rock RMS, Planning Center, M365, Monday.com, Cloudflare, etc.)
- Upgrade-safe customization layers
- Multi-provider AI support (Anthropic, OpenAI, Google, OpenRouter, LiteLLM, Ollama)

This repository intentionally keeps most upstream Clawith code unchanged and adds ChurchClaw logic in additive paths.

## Project Layout

- `churchclaw/config/` - Church profile and provider examples
- `churchclaw/agents/templates/` - Ministry agent template files
- `churchclaw/docs/` - Operations docs (upgrades, providers, deployment notes)
- `scripts/` - Operational scripts for syncing/upgrade/bootstrap

## Easy install for staff / other machines (Docker, no dev mounts)

For a **production-style** stack on someone else’s computer or a server (Postgres + Redis + built images, no source bind-mounts):

```bash
git clone <your-repo-url>
cd church-claw
bash scripts/install-docker.sh
```

Then open **http://localhost:8080** (or your `CHURCHCLAW_PORT`). First registered user is platform admin.

Full options (HTTPS, pre-built registry images, host Docker for agents): **[docs/INSTALL_DOCKER.md](docs/INSTALL_DOCKER.md)**.

**Local-only LLMs (Ollama, no Anthropic/OpenAI keys):** **[docs/LOCAL_ONLY.md](docs/LOCAL_ONLY.md)** — use `docker-compose.ollama.yml` + `churchclaw/config/bootstrap.local-only.json`.

**English-only UI:** **[docs/ENGLISH_ONLY.md](docs/ENGLISH_ONLY.md)** (Chinese locale bundle and language toggle removed).

---

## Quick Start (Mac Mini — developer stack)

1. Copy base env:

```bash
cp .env.example .env
cp .env.churchclaw.example .env.churchclaw
```

2. Bootstrap local configuration:

```bash
bash scripts/bootstrap-churchclaw.sh
```

3. Start base stack:

```bash
docker compose up -d
```

4. Optional provider abstraction (LiteLLM/Ollama):

```bash
docker compose -f docker-compose.yml -f docker-compose.providers.yml --profile providers up -d
```

5. Provision ChurchClaw phases 2-5 (models, agents, quotas, invite codes):

```bash
python3 scripts/provision-churchclaw.py --username <admin_username> --password <admin_password>
```

Optional flags:

```bash
python3 scripts/provision-churchclaw.py \
  --base-url http://localhost:8000 \
  --config churchclaw/config/bootstrap.json \
  --username <admin_username> \
  --password <admin_password>
```

## Security (cookie sessions + HTTPS)

- The **web UI** uses **HttpOnly cookies** for access/refresh tokens (no JWT in `localStorage`).
- Default **`AUTH_EXPOSE_ACCESS_TOKEN_IN_BODY=false`**: login/refresh JSON omits `access_token`; use `true` only for non-browser API clients.
- Production: terminate TLS on one host, set **`AUTH_COOKIE_SECURE=true`**, and narrow **`CORS_ORIGINS`**. See **[docs/HTTPS_DEPLOYMENT.md](docs/HTTPS_DEPLOYMENT.md)**.

## Upstream Updates

- Sync from Clawith upstream:

```bash
bash scripts/sync-upstream.sh
```

- Upgrade to a tagged Clawith release sequentially:

```bash
bash scripts/upgrade-clawith.sh v1.7.1
```

Do not skip major/minor hops if release notes require sequential upgrades.

## ChurchClaw Branding

- Primary navy: `#1B3A6B`
- Accent gold: `#C8973A`

Brand strings in UI are switched to ChurchClaw in key auth/navigation surfaces while preserving upstream compatibility.
