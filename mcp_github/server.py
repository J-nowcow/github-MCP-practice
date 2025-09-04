"""GitHub MCP server with fastMCP."""

import asyncio
from typing import Any

from fastmcp import FastMCP
from fastmcp.tools import Tool
from .tools_read import get_repo, list_pull_requests, get_pr_diff, get_file


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
    
    server.add_tool(Tool(
        name="listPullRequests",
        description="List pull requests for a repository",
        input_schema={
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repository owner (username or organization)"},
                "repo": {"type": "string", "description": "Repository name"},
                "state": {"type": "string", "description": "PR state filter (open, closed, all)", "default": "open"}
            },
            "required": ["owner", "repo"]
        },
        handler=list_pull_requests
    ))
    
    server.add_tool(Tool(
        name="getPRDiff",
        description="Get diff for a specific pull request",
        input_schema={
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repository owner (username or organization)"},
                "repo": {"type": "string", "description": "Repository name"},
                "number": {"type": "integer", "description": "Pull request number"}
            },
            "required": ["owner", "repo", "number"]
        },
        handler=get_pr_diff
    ))
    
    server.add_tool(Tool(
        name="getFile",
        description="Get file content from a repository",
        input_schema={
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repository owner (username or organization)"},
                "repo": {"type": "string", "description": "Repository name"},
                "path": {"type": "string", "description": "File path in repository"},
                "ref": {"type": "string", "description": "Git reference (branch, tag, or commit SHA)", "default": "HEAD"}
            },
            "required": ["owner", "repo", "path"]
        },
        handler=get_file
    ))
    
    # Start server
    asyncio.run(server.serve_stdio())


if __name__ == "__main__":
    main()
