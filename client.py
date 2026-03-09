import uuid
from typing import Any

import httpx
from config import settings

# Deterministic UUID for the persistent MCP session — always resolves to the same value
SESSION_ID = str(uuid.uuid5(uuid.NAMESPACE_DNS, "mcp-claude-desktop"))


async def chat(message: str) -> str:
    async with httpx.AsyncClient(timeout=60.0) as http:
        resp = await http.post(
            f"{settings.agent_url}/chat",
            headers={"X-API-Key": settings.agent_api_key},
            json={"message": message, "session_id": SESSION_ID},
        )
        resp.raise_for_status()
        return resp.json()["response"]


async def gateway(method: str, path: str, **params: Any) -> str:
    """Call the api-gateway directly. Path params must already be substituted into `path`."""
    headers = {"X-API-Key": settings.gateway_api_key}
    body = {k: v for k, v in params.items() if v is not None}
    async with httpx.AsyncClient(timeout=30.0) as http:
        if method == "GET":
            resp = await http.get(f"{settings.gateway_url}{path}", headers=headers, params=body)
        elif method == "DELETE":
            resp = await http.delete(f"{settings.gateway_url}{path}", headers=headers)
        else:
            resp = await http.request(method, f"{settings.gateway_url}{path}", headers=headers, json=body)
        resp.raise_for_status()
        return resp.text
