# Install ChurchClaw with Docker (easy path)

Three tiers — pick what fits your users.

## Tier 1 — Easiest (clone + one script)

**Requirements:** Docker Desktop (Mac/Windows) or Docker Engine + Compose v2 (Linux).

```bash
git clone https://github.com/YOUR_ORG/church-claw.git
cd church-claw
bash scripts/install-docker.sh
```

Open **http://localhost:8080** (or the port in `.env`).

The script creates `.env` from `.env.install.example` and, if `openssl` exists, fills random DB and JWT secrets.

**First user** who registers in the UI becomes **platform admin**.

### Optional: OpenClaw agent containers on the host

If staff need backend-managed Docker agents:

```bash
docker compose -f docker-compose.install.yml -f docker-compose.host-docker.yml --env-file .env up -d
```

---

## Tier 2 — Same machine, explicit commands

```bash
cp .env.install.example .env
# Edit .env: set CORS_ORIGINS to match your browser URL (scheme + host + port)
docker compose -f docker-compose.install.yml --env-file .env up -d --build
```

- **No** bind-mounts of source code — suitable for servers.
- Data lives in Docker volumes: `pgdata`, `redisdata`, `agent_data`.

### Production / HTTPS

1. Put a reverse proxy (Caddy, nginx) in front with TLS.
2. In `.env`:
   - `CORS_ORIGINS=["https://your.domain"]`
   - `AUTH_COOKIE_SECURE=true`
3. See **[HTTPS_DEPLOYMENT.md](./HTTPS_DEPLOYMENT.md)**.

Use a **strong** `POSTGRES_PASSWORD` with only URL-safe characters (letters, numbers) to avoid issues in `DATABASE_URL`.

---

## Tier 3 — Pre-built images (no `git clone` of app code)

Maintainers publish images to GitHub Container Registry (see `.github/workflows/docker-publish.yml`).

**Users** only need:

1. `docker-compose.registry.yml`
2. `.env` (copy from `.env.install.example` + set `BACKEND_IMAGE` / `FRONTEND_IMAGE`)

```bash
export BACKEND_IMAGE=ghcr.io/OWNER/churchclaw-backend:v1.0.0
export FRONTEND_IMAGE=ghcr.io/OWNER/churchclaw-frontend:v1.0.0
# Or put those lines in .env
docker compose -f docker-compose.registry.yml --env-file .env pull
docker compose -f docker-compose.registry.yml --env-file .env up -d
```

Release bundles can attach these two files + `.env.install.example` as a zip.

---

## vs. `docker-compose.yml` (developer stack)

The root **`docker-compose.yml`** mounts `./backend` and `./frontend/src` for live coding. Use **`docker-compose.install.yml`** for clean installs on other people’s machines.

---

## Troubleshooting

| Issue | Hint |
|--------|------|
| CORS / login loop | `CORS_ORIGINS` must include the exact URL you use in the browser (including port). |
| 502 on `/api/*` | Wait for Postgres health; check `docker compose logs backend`. |
| Blank page | Frontend build failed — check `docker compose build frontend`. |
