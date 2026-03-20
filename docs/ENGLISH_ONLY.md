# English-only UI (ChurchClaw)

ChurchClaw is configured for **English only** in the web app:

- `frontend/src/i18n/index.ts` — fixed `lng: 'en'`, no Chinese resource bundle, no browser language auto-switch.
- `frontend/src/i18n/zh.json` — removed.
- Language toggle removed from **Layout**, **Login**, and **Company setup**.
- Inline Chinese UI branches in **AgentDetail**, **UserManagement**, **Layout**, etc. were replaced with English.
- `index.html` uses `lang="en"` and an English meta description.

## Backend note

Many **Feishu / WeCom integration** modules under `backend/app/services/` still contain **Chinese strings** in tool descriptions, error messages, and prompts. Those are used when those integrations are enabled. Removing or translating all of that is a larger, separate change. Core API errors, websocket hints, seed templates, and several services were switched to English where they affect general users.
