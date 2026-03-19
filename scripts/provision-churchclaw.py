#!/usr/bin/env python3
"""Provision ChurchClaw phases 2-5 via API.

This script configures:
1) Platform settings (invites/self-create policy)
2) Tenant quotas and system settings
3) LLM model pool (multi-provider)
4) Ministry agents
5) Optional Teams channel config for selected agents
6) Staff invitation codes
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request


@dataclass
class ApiClient:
    base_url: str
    token: str | None = None

    def _url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}{path}"

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def request_json(self, method: str, path: str, payload: Any | None = None) -> Any:
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self._url(path),
            data=data,
            headers=self._headers(),
            method=method.upper(),
        )
        try:
            with request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                if not raw:
                    return None
                return json.loads(raw.decode("utf-8"))
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"{method} {path} failed: {exc.code} {details}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"{method} {path} failed: {exc}") from exc

    def get(self, path: str) -> Any:
        return self.request_json("GET", path)

    def post(self, path: str, payload: Any) -> Any:
        return self.request_json("POST", path, payload)

    def put(self, path: str, payload: Any) -> Any:
        return self.request_json("PUT", path, payload)

    def patch(self, path: str, payload: Any) -> Any:
        return self.request_json("PATCH", path, payload)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve_secret(model_cfg: dict[str, Any]) -> str | None:
    if model_cfg.get("api_key"):
        return str(model_cfg["api_key"]).strip()
    env_key = model_cfg.get("api_key_env")
    if env_key:
        return os.getenv(str(env_key), "").strip() or None
    return None


def login(client: ApiClient, username: str, password: str) -> dict[str, Any]:
    result = client.post("/api/auth/login", {"username": username, "password": password})
    token = result.get("access_token")
    if not token:
        raise RuntimeError("Login response did not include access_token.")
    client.token = token
    return result


def ensure_tenant(client: ApiClient, cfg: dict[str, Any], user: dict[str, Any]) -> dict[str, Any]:
    tenant_id = user.get("tenant_id")
    if tenant_id:
        return {"tenant_id": tenant_id}

    church_cfg = cfg.get("church", {})
    create_if_missing = bool(church_cfg.get("create_tenant_if_missing", False))
    if not create_if_missing:
        raise RuntimeError(
            "Logged-in user has no tenant. Set church.create_tenant_if_missing=true in config "
            "or create/join a company first in UI."
        )

    tenant_name = church_cfg.get("name", "ChurchClaw")
    tenant = client.post("/api/tenants/self-create", {"name": tenant_name})
    return {"tenant_id": tenant["id"]}


def apply_platform_settings(client: ApiClient, cfg: dict[str, Any]) -> None:
    settings_cfg = cfg.get("platform_settings", {})
    if settings_cfg:
        client.put("/api/admin/platform-settings", settings_cfg)


def apply_tenant_quotas(client: ApiClient, cfg: dict[str, Any]) -> None:
    quotas_cfg = cfg.get("tenant_quotas", {})
    if quotas_cfg:
        client.patch("/api/enterprise/tenant-quotas", quotas_cfg)


def apply_system_settings(client: ApiClient, cfg: dict[str, Any]) -> None:
    settings = cfg.get("system_settings", {})
    for key, value in settings.items():
        client.put(f"/api/enterprise/system-settings/{key}", {"value": value})


def list_llm_models(client: ApiClient) -> list[dict[str, Any]]:
    return client.get("/api/enterprise/llm-models")


def upsert_llm_models(client: ApiClient, cfg: dict[str, Any]) -> dict[str, str]:
    existing = list_llm_models(client)
    by_label = {m.get("label"): m for m in existing}

    label_to_id: dict[str, str] = {}
    for model_cfg in cfg.get("llm_models", []):
        label = str(model_cfg.get("label", "")).strip()
        if not label:
            continue

        api_key = resolve_secret(model_cfg)
        if not api_key:
            print(f"[skip] LLM '{label}' missing api key (api_key/api_key_env).")
            continue

        payload = {
            "provider": model_cfg["provider"],
            "model": model_cfg["model"],
            "api_key": api_key,
            "base_url": model_cfg.get("base_url"),
            "label": label,
            "enabled": bool(model_cfg.get("enabled", True)),
            "supports_vision": bool(model_cfg.get("supports_vision", False)),
        }

        existing_model = by_label.get(label)
        if existing_model:
            model_id = existing_model["id"]
            updated = client.put(f"/api/enterprise/llm-models/{model_id}", payload)
            label_to_id[label] = updated["id"]
            print(f"[ok] Updated LLM model: {label}")
        else:
            created = client.post("/api/enterprise/llm-models", payload)
            label_to_id[label] = created["id"]
            print(f"[ok] Created LLM model: {label}")

    # Refresh mapping with all existing labels for agent references.
    merged = list_llm_models(client)
    for item in merged:
        if item.get("label"):
            label_to_id[item["label"]] = item["id"]
    return label_to_id


def list_agents(client: ApiClient) -> list[dict[str, Any]]:
    return client.get("/api/agents/")


def create_or_update_agent(
    client: ApiClient,
    agent_cfg: dict[str, Any],
    existing_by_name: dict[str, dict[str, Any]],
    model_map: dict[str, str],
) -> str:
    name = str(agent_cfg.get("name", "")).strip()
    if not name:
        raise RuntimeError("Agent config missing name.")

    primary_model_id = model_map.get(agent_cfg.get("primary_model_label", ""))
    fallback_model_id = model_map.get(agent_cfg.get("fallback_model_label", ""))

    create_payload = {
        "name": name,
        "role_description": agent_cfg.get("role_description", ""),
        "personality": agent_cfg.get("personality", ""),
        "boundaries": agent_cfg.get("boundaries", ""),
        "primary_model_id": primary_model_id,
        "fallback_model_id": fallback_model_id,
        "permission_scope_type": agent_cfg.get("permission_scope_type", "company"),
        "permission_scope_ids": [],
    }

    existing = existing_by_name.get(name)
    if existing:
        agent_id = existing["id"]
        update_payload = {
            "role_description": create_payload["role_description"],
            "primary_model_id": create_payload["primary_model_id"],
            "fallback_model_id": create_payload["fallback_model_id"],
        }
        client.patch(f"/api/agents/{agent_id}", update_payload)
        print(f"[ok] Updated agent: {name}")
        return agent_id

    created = client.post("/api/agents/", create_payload)
    print(f"[ok] Created agent: {name}")
    return created["id"]


def configure_teams_if_enabled(client: ApiClient, agent_id: str, agent_cfg: dict[str, Any]) -> None:
    teams_cfg = agent_cfg.get("teams_channel", {})
    if not teams_cfg or not teams_cfg.get("enabled"):
        return

    app_id_env = str(teams_cfg.get("app_id_env", ""))
    app_secret_env = str(teams_cfg.get("app_secret_env", ""))
    tenant_id_env = str(teams_cfg.get("tenant_id_env", ""))

    app_id = os.getenv(app_id_env, "").strip() if app_id_env else ""
    app_secret = os.getenv(app_secret_env, "").strip() if app_secret_env else ""
    tenant_id = os.getenv(tenant_id_env, "").strip() if tenant_id_env else ""

    if not app_id or not app_secret:
        print(f"[skip] Teams config for agent {agent_cfg.get('name')} missing env vars.")
        return

    payload = {
        "app_id": app_id,
        "app_secret": app_secret,
        "tenant_id": tenant_id,
    }
    client.post(f"/api/agents/{agent_id}/teams-channel", payload)
    print(f"[ok] Configured Teams channel for {agent_cfg.get('name')}")


def generate_staff_invites(client: ApiClient, cfg: dict[str, Any]) -> list[str]:
    invites_cfg = cfg.get("staff_invitation_codes", {})
    if not invites_cfg:
        return []

    count = int(invites_cfg.get("count", 0))
    max_uses = int(invites_cfg.get("max_uses", 1))
    if count <= 0:
        return []

    result = client.post(
        "/api/enterprise/invitation-codes",
        {"count": count, "max_uses": max_uses},
    )
    codes = result.get("codes", [])
    print(f"[ok] Generated {len(codes)} invitation code(s)")
    return codes


def main() -> int:
    parser = argparse.ArgumentParser(description="Provision ChurchClaw via API")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Backend base URL")
    parser.add_argument("--username", required=True, help="Admin username")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument(
        "--config",
        default="churchclaw/config/bootstrap.json",
        help="Path to provisioning JSON config",
    )
    args = parser.parse_args()

    cfg_path = Path(args.config)
    if not cfg_path.exists():
        raise RuntimeError(f"Config file not found: {cfg_path}")

    cfg = load_json(cfg_path)
    client = ApiClient(base_url=args.base_url)

    print("[step] Logging in...")
    login_data = login(client, args.username, args.password)
    user = login_data["user"]
    print(f"[ok] Authenticated as {user.get('username')} ({user.get('role')})")

    print("[step] Ensuring tenant assignment...")
    tenant_ctx = ensure_tenant(client, cfg, user)
    print(f"[ok] Using tenant_id={tenant_ctx['tenant_id']}")

    print("[step] Applying platform settings...")
    apply_platform_settings(client, cfg)
    print("[ok] Platform settings applied")

    print("[step] Applying tenant quotas...")
    apply_tenant_quotas(client, cfg)
    print("[ok] Tenant quotas applied")

    print("[step] Applying system settings...")
    apply_system_settings(client, cfg)
    print("[ok] System settings applied")

    print("[step] Upserting LLM models...")
    model_map = upsert_llm_models(client, cfg)
    print(f"[ok] LLM pool ready ({len(model_map)} labeled models available)")

    print("[step] Upserting ministry agents...")
    existing_agents = list_agents(client)
    existing_by_name = {a.get("name"): a for a in existing_agents}
    provisioned_agent_ids: list[str] = []

    for agent_cfg in cfg.get("agents", []):
        agent_id = create_or_update_agent(client, agent_cfg, existing_by_name, model_map)
        provisioned_agent_ids.append(agent_id)
        configure_teams_if_enabled(client, agent_id, agent_cfg)

    print(f"[ok] Agent provisioning complete ({len(provisioned_agent_ids)} processed)")

    print("[step] Generating invitation codes...")
    invites = generate_staff_invites(client, cfg)

    print("\n=== ChurchClaw Provisioning Complete ===")
    print(f"Tenant ID: {tenant_ctx['tenant_id']}")
    print(f"Agents processed: {len(provisioned_agent_ids)}")
    if invites:
        print("Staff invitation codes:")
        for code in invites:
            print(f"  - {code}")
    else:
        print("No invitation codes generated.")
    print("========================================")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[error] {exc}", file=sys.stderr)
        raise SystemExit(1)
