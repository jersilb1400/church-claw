# Upstream Update Playbook

ChurchClaw tracks two upstream ecosystems:

1. **Clawith** (code upstream, direct git sync)
2. **OpenClaw** (feature upstream, selective porting and skills adoption)

## One-Time Git Setup

```bash
git remote add upstream https://github.com/dataelement/Clawith.git
git fetch upstream --tags
```

## Routine Sync

```bash
bash scripts/sync-upstream.sh
```

## Tagged Upgrade

```bash
bash scripts/upgrade-clawith.sh v1.7.1
```

Use sequential upgrades if release notes require version-by-version migration.

## Conflict-Minimizing Rules

- Keep ChurchClaw customizations in additive paths:
  - `churchclaw/config/`
  - `churchclaw/agents/templates/`
  - `churchclaw/docs/`
  - `scripts/`
- Prefer config and templates over core code edits.
- Document any core patch done against upstream files.

## Post-Upgrade Verification

- `docker compose build backend frontend`
- `docker compose up -d`
- Login as admin
- Validate one ministry agent run
- Validate one MCP integration
