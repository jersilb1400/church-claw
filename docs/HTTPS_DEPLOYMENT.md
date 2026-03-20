# HTTPS + single host (ChurchClaw)

Run the **entire app behind one TLS origin**. The SPA and API share the same host so the browser sends **HttpOnly cookies** on `/api/*` and `/ws/*` automatically.

## Goals

1. **TLS termination** at the edge (Caddy or nginx).
2. **`CORS_ORIGINS`** lists only your real `https://your.domain` (never `*` in production).
3. **Backend cookie flags** when using HTTPS:
   - `AUTH_COOKIE_SECURE=true`
   - `AUTH_COOKIE_SAMESITE=lax` (or `strict` if all flows are same-site)

## Environment (backend)

```bash
# Exact browser origin(s) talking to the API (include scheme + host + port if non-443)
CORS_ORIGINS=["https://church.example.org"]

AUTH_COOKIE_ENABLED=true
AUTH_COOKIE_SECURE=true
AUTH_COOKIE_SAMESITE=lax

# Default: omit JWT from JSON; cookies only (XSS-resistant web UI)
AUTH_EXPOSE_ACCESS_TOKEN_IN_BODY=false
```

Set `AUTH_EXPOSE_ACCESS_TOKEN_IN_BODY=true` only for **non-browser** clients that cannot use cookies.

## Caddy (example)

Replace `church.example.org` and upstream ports to match your deployment (e.g. frontend static on `:3008`, backend on `:8008`).

```caddy
church.example.org {
    encode gzip

    # API + WebSocket to FastAPI
    handle /api* {
        reverse_proxy localhost:8008
    }
    handle /ws* {
        reverse_proxy localhost:8008
    }

    # SPA (Vite build or static)
    handle {
        reverse_proxy localhost:3008
    }
}
```

HSTS is enabled by the backend **when the request is HTTPS**. Caddy can add stricter headers if desired:

```caddy
header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
```

## nginx (sketch)

- `proxy_set_header Host $host;`
- For WebSockets: `Upgrade` and `Connection` headers
- Same path split: `/api/` and `/ws/` → backend; `/` → frontend

## Single-host note

If the UI is served from `https://church.example.org` and proxies `/api` to the backend on the **same hostname**, you do not need separate API CORS origins for cookies—only list that one origin in `CORS_ORIGINS`.
