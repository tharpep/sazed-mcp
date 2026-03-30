from typing import Optional

from mcp.server.fastmcp import FastMCP

from client import chat, gateway

mcp = FastMCP("sazed")


# ── Sazed Agent ───────────────────────────────────────────────────────────────


@mcp.tool()
async def ask_sazed(message: str) -> str:
    """
    Send a message to Sazed, your personal AI agent.
    Sazed has access to your calendar, tasks, email, knowledge base,
    and persistent memory. Use this for anything requiring personal
    context, multi-step reasoning, or integrations.
    """
    return await chat(message)


# ── Notifications ─────────────────────────────────────────────────────────────


@mcp.tool()
async def send_notification(
    title: str,
    message: str,
    priority: Optional[int] = None,
    url: Optional[str] = None,
    url_title: Optional[str] = None,
) -> str:
    """
    Send a push notification to the user's phone via Pushover.
    priority: -2=silent, -1=quiet, 0=normal (default), 1=high.
    """
    return await gateway("POST", "/notify", title=title, message=message, priority=priority, url=url, url_title=url_title)


# ── Knowledge Base ────────────────────────────────────────────────────────────


@mcp.tool()
async def search_knowledge_base(
    query: str,
    categories: Optional[list[str]] = None,
    top_k: Optional[int] = None,
) -> str:
    """
    Search the user's personal knowledge base (RAG over their Google Drive documents).
    categories: limit to specific KB subfolders — "general", "projects", "purdue",
    "career", "reference", "conversations". Omit to search all.
    top_k: number of results to return (default 10).
    """
    return await gateway("POST", "/kb/search", query=query, categories=categories, top_k=top_k)


# ── Multi-Platform Search ────────────────────────────────────────────────────


@mcp.tool()
async def aggregate_search(
    query: str,
    max_results: Optional[int] = None,
    platforms: Optional[list[str]] = None,
    since: Optional[str] = None,
) -> str:
    """
    Search across Reddit, Hacker News, Bluesky, and news sources simultaneously.
    Returns normalized results with credibility tiers, corroboration clusters,
    and bias signals (hedge ratio, named source count, content type, fact checks).
    platforms: 'reddit','hn','bluesky','gnews','google_news_rss','rss'. Omit for all.
    since: ISO 8601 timestamp — only return results newer than this (useful for alerts).
    """
    return await gateway(
        "POST", "/multi-search/aggregate",
        query=query, max_results=max_results, platforms=platforms, since=since,
    )


# ── Google Drive ──────────────────────────────────────────────────────────────


@mcp.tool()
async def list_files(
    folder_id: Optional[str] = None,
    query: Optional[str] = None,
    max_results: Optional[int] = None,
) -> str:
    """List files in Google Drive. Filter by folder ID or Drive search query (e.g. 'name contains "resume"')."""
    return await gateway("GET", "/storage/files", folder_id=folder_id, query=query, max_results=max_results)


@mcp.tool()
async def list_folders(
    parent_id: Optional[str] = None,
    query: Optional[str] = None,
    max_results: Optional[int] = None,
) -> str:
    """List Drive folders. Use parent_id to browse into a folder, or query to search by name."""
    return await gateway("GET", "/storage/folders", parent_id=parent_id, query=query, max_results=max_results)


@mcp.tool()
async def create_folder(name: str, parent_id: Optional[str] = None) -> str:
    """Create a new folder in Google Drive, optionally nested inside a parent folder."""
    return await gateway("POST", "/storage/folders", name=name, parent_id=parent_id)


@mcp.tool()
async def get_file_info(file_id: str) -> str:
    """Get metadata for a Drive file — name, MIME type, size, and modified time."""
    return await gateway("GET", f"/storage/files/{file_id}")


@mcp.tool()
async def read_file(file_id: str) -> str:
    """
    Fetch the full text content of a Google Drive file.
    Works with text, Markdown, CSV, JSON, Google Docs, PDFs, and Google Sheets (exported as CSV).
    """
    return await gateway("GET", f"/storage/files/{file_id}/content")


@mcp.tool()
async def create_file(
    name: str,
    content: str,
    folder_id: Optional[str] = None,
    mime_type: Optional[str] = None,
) -> str:
    """
    Create a new file in Google Drive.
    Use mime_type='application/vnd.google-apps.document' for a native Google Doc.
    Defaults to text/plain.
    """
    return await gateway("POST", "/storage/files", name=name, content=content, folder_id=folder_id, mime_type=mime_type)


@mcp.tool()
async def update_file(file_id: str, content: str) -> str:
    """Overwrite the content of an existing Google Drive text file. Replaces the entire file content."""
    return await gateway("PUT", f"/storage/files/{file_id}", content=content)


@mcp.tool()
async def append_to_file(file_id: str, content: str, separator: Optional[str] = None) -> str:
    """Append text to an existing Google Drive file or Google Doc without overwriting its current content."""
    return await gateway("POST", f"/storage/files/{file_id}/append", content=content, separator=separator)


@mcp.tool()
async def delete_file(file_id: str) -> str:
    """Move a Google Drive file to trash."""
    return await gateway("DELETE", f"/storage/files/{file_id}")


@mcp.tool()
async def move_file(
    file_id: str,
    name: Optional[str] = None,
    folder_id: Optional[str] = None,
) -> str:
    """Rename and/or move a Drive file to a different folder. Provide at least one of name or folder_id."""
    return await gateway("PATCH", f"/storage/files/{file_id}", name=name, folder_id=folder_id)


# ── Finance ───────────────────────────────────────────────────────────────────


@mcp.tool()
async def get_subscriptions(all: Optional[bool] = None) -> str:
    """List active subscriptions and bills. Pass all=true to include inactive ones."""
    return await gateway("GET", "/finance/subscriptions", all=all)


@mcp.tool()
async def add_subscription(
    name: str,
    amount: float,
    category: str,
    frequency: Optional[str] = None,
    type: Optional[str] = None,
    variable_amount: Optional[bool] = None,
    billing_day: Optional[int] = None,
    next_billing_date: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """
    Add a new recurring subscription or bill.
    frequency: "monthly" (default), "annual", "weekly", "biweekly".
    type: "subscription" (optional service) or "bill" (financial obligation).
    billing_day: day of month (1–31) for monthly items.
    next_billing_date: YYYY-MM-DD for annual/weekly/biweekly items.
    """
    return await gateway(
        "POST", "/finance/subscriptions",
        name=name, amount=amount, category=category, frequency=frequency,
        type=type, variable_amount=variable_amount, billing_day=billing_day,
        next_billing_date=next_billing_date, notes=notes,
    )


@mcp.tool()
async def update_subscription(
    subscription_id: str,
    name: Optional[str] = None,
    amount: Optional[float] = None,
    frequency: Optional[str] = None,
    category: Optional[str] = None,
    type: Optional[str] = None,
    variable_amount: Optional[bool] = None,
    billing_day: Optional[int] = None,
    next_billing_date: Optional[str] = None,
    active: Optional[bool] = None,
    notes: Optional[str] = None,
) -> str:
    """Update fields on an existing subscription or bill."""
    return await gateway(
        "PATCH", f"/finance/subscriptions/{subscription_id}",
        name=name, amount=amount, frequency=frequency, category=category,
        type=type, variable_amount=variable_amount, billing_day=billing_day,
        next_billing_date=next_billing_date, active=active, notes=notes,
    )


@mcp.tool()
async def delete_subscription(subscription_id: str) -> str:
    """Deactivate (soft-delete) a subscription or bill by ID."""
    return await gateway("DELETE", f"/finance/subscriptions/{subscription_id}")


@mcp.tool()
async def get_budget() -> str:
    """List all budget category limits."""
    return await gateway("GET", "/finance/budget")


@mcp.tool()
async def set_budget_limit(category: str, monthly_limit: float) -> str:
    """Set or update the monthly spending limit for a budget category."""
    return await gateway("PUT", f"/finance/budget/{category}", monthly_limit=monthly_limit)


@mcp.tool()
async def delete_budget(category: str) -> str:
    """Remove a budget category limit."""
    return await gateway("DELETE", f"/finance/budget/{category}")


@mcp.tool()
async def get_income() -> str:
    """List active income sources."""
    return await gateway("GET", "/finance/income")


@mcp.tool()
async def add_income_source(
    source: str,
    amount: float,
    frequency: Optional[str] = None,
) -> str:
    """
    Add a new income source.
    frequency: "monthly" (default), "annual", "weekly", "biweekly".
    """
    return await gateway("POST", "/finance/income", source=source, amount=amount, frequency=frequency)


@mcp.tool()
async def delete_income(income_id: str) -> str:
    """Deactivate (soft-delete) an income source by ID."""
    return await gateway("DELETE", f"/finance/income/{income_id}")


@mcp.tool()
async def get_upcoming_bills(days: Optional[int] = None) -> str:
    """List subscriptions and bills due within the next N days (default 30), sorted by due date."""
    return await gateway("GET", "/finance/upcoming", days=days)


@mcp.tool()
async def get_monthly_summary() -> str:
    """
    Get a computed monthly financial summary: income, subscription/bill costs, net estimated,
    plus full lists of income sources, subscriptions, bills, and budget limits.
    """
    return await gateway("GET", "/finance/summary")


if __name__ == "__main__":
    mcp.run(transport="stdio")
