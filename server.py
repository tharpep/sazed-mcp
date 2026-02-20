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
