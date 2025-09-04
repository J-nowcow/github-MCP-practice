"""GitHub MCP server with fastMCP."""

import asyncio
from typing import Any

from fastmcp import FastMCP
from fastmcp.tools import Tool
from .tools_read import get_repo


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
    
    server.add_tool(Tool(
        name="getRepo",
        description="Get repository information from GitHub",
        input_schema={
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repository owner (username or organization)"},
                "repo": {"type": "string", "description": "Repository name"}
            },
            "required": ["owner", "repo"]
        },
        handler=get_repo
    ))
    
    # Start server
    asyncio.run(server.serve_stdio())


if __name__ == "__main__":
    main()
