# Local MCP Plan — `local-mcp`

**Role:** Thin bridge from Claude Desktop → Sazed agent. One tool, persistent session, stdio transport.  
**Prerequisite:** Sazed agent deployed and accessible (`POST /chat`).

---

## Architecture

```
Claude Desktop
    │  stdio (JSON-RPC)
    ▼
local-mcp (Docker container)
    │  POST /chat  { message, session_id: "mcp-claude-desktop" }
    ▼
Sazed agent (GCP Cloud Run)
    │  tool_use loop
    ▼
api-gateway → calendar / tasks / email / kb / notify
```

One MCP tool: `ask_sazed`. Claude Desktop sends natural language, Sazed does all reasoning and tool execution, returns a text response. Claude Desktop never sees individual tools — it sees one black box that does everything.

---

## Session Strategy

A single persistent session ID: `mcp-claude-desktop`.  
- All Claude Desktop interactions share context within this session.
- Session resets **weekly** (cron on Sazed, or MCP sends a `new_session` flag).  
- Sazed's post-session processing (fact extraction + KB summarization) runs on the nightly sweep cron — MCP never explicitly closes a session.

---

## Repo Structure

```
local-mcp/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml          # FastMCP + httpx + pydantic-settings
├── .env.example
├── .env                    # gitignored
├── server.py               # entrypoint — MCP server definition
└── client.py               # thin httpx wrapper for Sazed /chat
```

Small enough to be a single-file server with a helper module. No app/ structure needed.

---

## Implementation

### `server.py`

```python
from mcp.server.fastmcp import FastMCP
from client import chat

mcp = FastMCP("sazed")

@mcp.tool()
async def ask_sazed(message: str) -> str:
    """
    Send a message to Sazed, your personal AI agent.
    Sazed has access to your calendar, tasks, email, knowledge base,
    and persistent memory. Use this for anything requiring personal
    context or integrations.
    """
    return await chat(message)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### `client.py`

```python
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
```

### `config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    agent_url: str
    agent_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Docker

### `Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install poetry && poetry install --no-root
COPY . .
CMD ["poetry", "run", "python", "server.py"]
```

### `docker-compose.yml`

```yaml
services:
  local-mcp:
    build: .
    stdin_open: true
    tty: true
    env_file: .env
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

`stdin_open: true` + `tty: true` keeps the container alive for stdio. Logs visible in Docker Desktop.

---

## Claude Desktop Config

`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sazed": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "--env-file", "/absolute/path/to/local-mcp/.env",
        "local-mcp"
      ]
    }
  }
}
```

`-i` keeps stdin open (required for stdio). `--rm` cleans up on exit. Claude Desktop launches this command directly — no daemon needed.

> **Note on Docker vs bare:** Claude Desktop spawns the process itself via stdio, so Docker is just wrapping the launch. The log visibility benefit is real (`docker logs`), but if it becomes annoying to manage image rebuilds, `uv run server.py` works identically — same config, replace `command`/`args` with `["uv", "run", "server.py"]`.

---

## `.env.example`

```
AGENT_URL=https://your-agent.run.app
AGENT_API_KEY=your-agent-api-key
```

---

## Dependencies (`pyproject.toml`)

```toml
[tool.poetry.dependencies]
python = "^3.11"
mcp = {extras = ["cli"], version = "^1.0"}
httpx = "^0.27"
pydantic-settings = "^2.0"
```

---

## Deliverables

- [ ] Repo scaffolded with above structure
- [ ] `server.py` + `client.py` + `config.py` implemented
- [ ] Docker build passes
- [ ] `.env` filled in, `.env.example` committed
- [ ] Claude Desktop config updated
- [ ] End-to-end: "What's on my calendar today?" in Claude Desktop → Sazed response

---

## Future Extensions

These require no MCP changes — just add endpoints to the agent/gateway:

- `reset_session` tool to explicitly clear the MCP session without waiting for weekly reset
- `ingest_file` tool (base64 content → gateway `/kb/ingest/file`) once file ingest is built
- Health-check tool that pings Sazed `/health` — useful for debugging from Claude Desktop

---

## Decision Log

| Decision | Choice | Rationale |
|---|---|---|
| Routing | Through agent `/chat` | Sazed handles all reasoning; MCP stays dumb |
| Tool count | 1 (`ask_sazed`) | Simpler MCP, full agent context per call |
| Session | Persistent `mcp-claude-desktop`, weekly reset | Context within work sessions, bounded growth |
| Transport | stdio | Required by Claude Desktop; no HTTP server needed |
| Runtime | Docker | Log visibility in Docker Desktop; easy rebuild |
| Session processing | Nightly cron sweep on Sazed | MCP has no close event; cron is the fallback |
