"""GitHub MCP server with fastMCP."""

import argparse
from typing import Any

from fastmcp import FastMCP
from tools_read import get_repo, list_pull_requests, get_pr_diff, get_file
from tools_write import (
    create_or_update_file, 
    delete_file, 
    create_branch, 
    create_commit_with_multiple_files,
    get_repository_status
)
from tools_local_git import (
    get_git_status,
    stage_all_changes,
    stage_specific_files,
    create_commit,
    push_to_remote,
    get_commit_history,
    check_git_repository,
    get_current_branch,
    get_remote_info
)
from resources import get_pr_diff_resource, get_file_resource


def main() -> None:
    """Main entry point."""
    # 명령행 인수 파싱
    parser = argparse.ArgumentParser(description="GitHub MCP Server")
    parser.add_argument("--transport", choices=["stdio", "http", "sse"], default="stdio", 
                       help="Transport protocol (default: stdio)")
    parser.add_argument("--host", default="127.0.0.1", help="Host for HTTP/SSE transport (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=3000, help="Port for HTTP/SSE transport (default: 3000)")
    parser.add_argument("--path", default="/mcp", help="Path for HTTP transport (default: /mcp)")
    
    args = parser.parse_args()
    
    server = FastMCP("mcp-github", "0.1.0")

    # Register tools using decorators
    @server.tool
    def health() -> dict[str, str]:
        """Health check tool."""
        return {"status": "ok"}

    # Read tools
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

    # Write tools
    @server.tool
    def createOrUpdateFile(
        owner: str, 
        repo: str, 
        path: str, 
        content: str, 
        message: str,
        branch: str = "main",
        committer_name: str = None,
        committer_email: str = None
    ) -> dict[str, Any]:
        """Create or update a file in a GitHub repository."""
        return create_or_update_file(
            owner, repo, path, content, message, branch, committer_name, committer_email
        )

    @server.tool
    def deleteFile(
        owner: str, 
        repo: str, 
        path: str, 
        message: str,
        branch: str = "main",
        committer_name: str = None,
        committer_email: str = None
    ) -> dict[str, Any]:
        """Delete a file from a GitHub repository."""
        return delete_file(
            owner, repo, path, message, branch, committer_name, committer_email
        )

    @server.tool
    def createBranch(
        owner: str, 
        repo: str, 
        new_branch: str, 
        base_branch: str = "main"
    ) -> dict[str, Any]:
        """Create a new branch in a GitHub repository."""
        return create_branch(owner, repo, new_branch, base_branch)

    @server.tool
    def createCommitWithMultipleFiles(
        owner: str,
        repo: str,
        files: list,
        message: str,
        branch: str = "main",
        committer_name: str = None,
        committer_email: str = None
    ) -> dict[str, Any]:
        """Create a commit with multiple file changes."""
        return create_commit_with_multiple_files(
            owner, repo, files, message, branch, committer_name, committer_email
        )

    @server.tool
    def getRepositoryStatus(
        owner: str, 
        repo: str, 
        ref: str = "HEAD"
    ) -> dict[str, Any]:
        """Get repository status including last commit and branch info."""
        return get_repository_status(owner, repo, ref)

    # Local Git tools
    @server.tool
    def getGitStatus(cwd: str = None) -> dict[str, Any]:
        """Get current Git repository status."""
        return get_git_status(cwd)

    @server.tool
    def stageAllChanges(cwd: str = None) -> dict[str, Any]:
        """Stage all changes in the Git repository."""
        return stage_all_changes(cwd)

    @server.tool
    def stageSpecificFiles(files: list[str], cwd: str = None) -> dict[str, Any]:
        """Stage specific files in the Git repository."""
        return stage_specific_files(files, cwd)

    @server.tool
    def createLocalCommit(message: str, cwd: str = None) -> dict[str, Any]:
        """Create a local Git commit."""
        return create_commit(message, cwd)

    @server.tool
    def pushToRemote(branch: str = "main", remote: str = "origin", cwd: str = None) -> dict[str, Any]:
        """Push to remote repository."""
        return push_to_remote(branch, remote, cwd)

    @server.tool
    def getCommitHistory(limit: int = 10, cwd: str = None) -> dict[str, Any]:
        """Get Git commit history."""
        return get_commit_history(limit, cwd)

    @server.tool
    def checkGitRepository(cwd: str = None) -> dict[str, Any]:
        """Check if current directory is a Git repository."""
        return check_git_repository(cwd)

    @server.tool
    def getCurrentBranch(cwd: str = None) -> dict[str, Any]:
        """Get current Git branch."""
        return get_current_branch(cwd)

    @server.tool
    def getRemoteInfo(cwd: str = None) -> dict[str, Any]:
        """Get remote repository information."""
        return get_remote_info(cwd)

    # Note: Resource templates are not supported in this version of FastMCP
    # Tools are available for direct GitHub operations

    # Start server with appropriate transport
    if args.transport == "http":
        print(f"🚀 Starting GitHub MCP Server in HTTP mode on {args.host}:{args.port}{args.path}")
        server.run(transport="http", host=args.host, port=args.port, path=args.path)
    elif args.transport == "sse":
        print(f"🚀 Starting GitHub MCP Server in SSE mode on {args.host}:{args.port}")
        server.run(transport="sse", host=args.host, port=args.port)
    else:
        print("🚀 Starting GitHub MCP Server in STDIO mode")
        server.run()


if __name__ == "__main__":
    main()
