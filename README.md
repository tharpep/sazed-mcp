# Sazed MCP

MCP (Model Context Protocol) server that exposes [Sazed](https://github.com/tharpep/sazed) as a single `ask_sazed` tool for Claude Desktop.

## Ecosystem

Part of a personal AI ecosystem — see [sazed](https://github.com/tharpep/sazed) for the full picture.

## How it works

`server.py` registers one MCP tool:

```
ask_sazed(message: str) → str
```

Calling it sends a message to the Sazed agent's `/chat` endpoint using a deterministic session ID (`mcp-claude-desktop`), so the conversation persists across Claude Desktop sessions.

## Setup

```bash
poetry install
cp .env.example .env
# fill in AGENT_URL and AGENT_API_KEY
```

**.env values:**

```
AGENT_URL=https://your-sazed-agent.run.app
AGENT_API_KEY=your-agent-api-key
```

## Running

```bash
python server.py   # stdio MCP server
```

## Claude Desktop config

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sazed": {
      "command": "python",
      "args": ["/path/to/sazed-mcp/server.py"],
      "env": {
        "AGENT_URL": "https://your-sazed-agent.run.app",
        "AGENT_API_KEY": "your-agent-api-key"
      }
    }
  }
}
```
