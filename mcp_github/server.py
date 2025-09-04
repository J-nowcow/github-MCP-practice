"""GitHub MCP server with fastMCP."""

import asyncio
from typing import Any

from fastmcp import FastMCP
from fastmcp.tools import Tool


async def health() -> dict[str, str]:
    """Health check tool."""
    return {"status": "ok"}


def main() -> None:
    """Main entry point."""
    server = FastMCP("mcp-github", "0.1.0")
    
    # Register tools
    server.add_tool(Tool(
        name="health",
        description="Health check for the MCP server",
        input_schema={},
        handler=health
    ))
    
    # Start server
    asyncio.run(server.serve_stdio())


if __name__ == "__main__":
    main()
