import httpx
from config import settings

SESSION_ID = "mcp-claude-desktop"


async def chat(message: str) -> str:
    async with httpx.AsyncClient(timeout=60.0) as http:
        resp = await http.post(
            f"{settings.agent_url}/chat",
            headers={"X-API-Key": settings.agent_api_key},
            json={"message": message, "session_id": SESSION_ID},
        )
        resp.raise_for_status()
        return resp.json()["response"]
