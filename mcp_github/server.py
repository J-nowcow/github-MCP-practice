"""GitHub MCP server with fastMCP."""

from typing import Any

from fastmcp import FastMCP
from .tools_read import get_repo, list_pull_requests, get_pr_diff, get_file
from .resources import get_pr_diff_resource, get_file_resource


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

    # Register resource templates for URI-based content access
    server.add_resource_template(
        uri_template="gh-pr-diff://{owner}/{repo}/{number}",
        name="PR Diff",
        description="Diff for a GitHub pull request",
        mime_types=["application/json"],
        handler=lambda owner, repo, number: get_pr_diff_resource(owner, repo, number),
    )

    server.add_resource_template(
        uri_template="gh-file://{owner}/{repo}/{path}",
        name="GitHub File",
        description="GitHub file or directory",
        mime_types=["text/plain", "application/json"],
        handler=lambda owner, repo, path, ref="HEAD": get_file_resource(owner, repo, path, ref),
    )

    # Start server
    server.run()


if __name__ == "__main__":
    main()
