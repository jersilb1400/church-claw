# ChurchClaw Phase Execution Runbook

This runbook executes the remaining phases after base clone/bootstrap.

## Prerequisites

- Docker + Docker Compose installed
- Python 3.10+ installed
- `churchclaw/.env` and `churchclaw/.env.churchclaw` populated
- First admin user created in UI (or via API)

## Phase 2: Core Ministry Agents

1. Update `churchclaw/config/bootstrap.json`:
   - Confirm `llm_models`
   - Confirm `agents` list
2. Run provisioning:

```bash
python3 scripts/provision-churchclaw.py --username <admin> --password <password>
```

3. Verify in UI:
   - Agents visible in dashboard
   - Agent chat works
   - Primary/fallback models assigned

## Phase 3: Integrations and Channels

1. Ensure integration credentials are set in `.env.churchclaw`
2. Enable Teams per agent in `bootstrap.json`:
   - `teams_channel.enabled = true`
   - app/secret/tenant env keys are correct
3. Re-run provisioning script
4. Configure webhook endpoint in Teams/Azure per guide

## Phase 4: Full Roster + Reusability

1. Add or adjust ministry agents in `bootstrap.json`
2. Add church profile defaults in `churchclaw/config/church-profile.yaml`
3. Re-run provisioning script
4. Export invitation codes and onboard staff

## Phase 5: Polish + Handoff

1. Set notification and platform settings:
   - `bootstrap.json -> system_settings`
2. Verify quotas and guardrails in Enterprise settings
3. Document staff-facing SOP:
   - Chat usage
   - Approval workflows
   - Escalation path for errors

## Repeatable Operations

- Upstream sync:
  - `bash scripts/check-upstream-release.sh`
  - `bash scripts/upgrade-clawith.sh <tag>`
- Re-apply ChurchClaw policy/config:
  - `python3 scripts/provision-churchclaw.py --username <admin> --password <pass>`

This keeps local custom policy consistent after each upstream update.
