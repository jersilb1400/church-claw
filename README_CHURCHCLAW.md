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

## Quick Start (Mac Mini)

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
```

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
