"""GitHub MCP server with fastMCP."""

from typing import Any

from fastmcp import FastMCP
from mcp_github.tools_read import get_repo, list_pull_requests, get_pr_diff, get_file


def main() -> None:
    """Main entry point."""
    server = FastMCP("mcp-github", "0.1.0")
    
    # Register tools using decorators
    @server.tool
    def health() -> dict[str, str]:
        """Health check tool."""
        return {"status": "ok"}
    
    @server.tool
    def getRepo(owner: str, repo: str) -> dict[str, Any]:
        """Get repository information from GitHub."""
        return get_repo(owner, repo)
    
    @server.tool
    def listPullRequests(owner: str, repo: str, state: str = "open") -> dict[str, Any]:
        """List pull requests for a repository."""
        return list_pull_requests(owner, repo, state)
    
    @server.tool
    def getPRDiff(owner: str, repo: str, number: int) -> dict[str, Any]:
        """Get diff for a specific pull request."""
        return get_pr_diff(owner, repo, number)
    
    @server.tool
    def getFile(owner: str, repo: str, path: str, ref: str = "HEAD") -> dict[str, Any]:
        """Get file content from a repository."""
        return get_file(owner, repo, path, ref)
    
    # Start server
    server.run()


if __name__ == "__main__":
    main()
