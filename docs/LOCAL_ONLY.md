# Local-only deployment (no cloud LLM APIs)

Use this when you want **ChurchClaw and all LLM inference on your own hardware** — no Anthropic/OpenAI keys required for chat/agents.

## What “local-only” means here

| Layer | Local-only approach |
|--------|---------------------|
| **App + DB** | `docker-compose.install.yml` (already local) |
| **LLM** | **Ollama** in Docker (`docker-compose.ollama.yml`) or Ollama installed on the Mac |
| **Provision** | `bootstrap.local-only.json` — only Ollama model entries |
| **Secrets** | Do **not** set `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc. in `.env` for LLM use |

**Note:** Optional features (M365, Rock RMS, web search, etc.) may still call **external** services if you configure them — disable those integrations in the UI or omit API keys.

---

## 1. Run Ollama alongside ChurchClaw (recommended)

From the repo root:

```bash
docker compose -f docker-compose.install.yml -f docker-compose.ollama.yml --env-file .env up -d
```

Pull at least one model (example: `llama3.1:8b` — must match `churchclaw/config/bootstrap.local-only.json`):

```bash
docker compose -f docker-compose.install.yml -f docker-compose.ollama.yml exec ollama ollama pull llama3.1:8b
```

The backend uses **`http://ollama:11434/v1`** inside Docker (same Compose network).

---

## 2. Or use Ollama on the Mac (not in Docker)

1. Install [Ollama](https://ollama.com) on the Mac and pull models.
2. In **Platform Admin → LLM models**, add/edit an Ollama model with base URL:
   - **`http://host.docker.internal:11434/v1`**  
   (lets the backend container reach the Mac’s Ollama.)

Use the same model name(s) you pulled (e.g. `llama3.1:8b`).

---

## 3. Provision with local-only models

```bash
python3 scripts/provision-churchclaw.py \
  --base-url http://localhost:8080 \
  --config churchclaw/config/bootstrap.local-only.json \
  --username YOUR_ADMIN_USER \
  --password YOUR_PASSWORD
```

This registers **only** the Ollama entries from the config (cloud rows in the default `bootstrap.json` are omitted).

If you **already** ran provision with cloud models, open **Enterprise / LLM models** in the UI and **disable or remove** Anthropic/OpenAI entries so agents cannot use them.

---

## 4. Avoid accidental cloud usage

- **`.env`:** leave cloud API keys unset (or remove them) if you don’t want any code path to use them.
- **Do not merge** `docker-compose.providers.yml` with LiteLLM unless you intentionally point LiteLLM at local models only.
- **Agents:** ensure each agent’s primary/fallback models are your **local** labels only.

---

## 5. True air-gapped / no internet

That requires OS-level firewalling, offline images, and no external MCP/tool endpoints — beyond this doc. Start by keeping **LLM traffic** local using the steps above.
