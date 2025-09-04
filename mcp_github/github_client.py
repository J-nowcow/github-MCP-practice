"""GitHub API client for MCP server."""

import os
from typing import Optional

from dotenv import load_dotenv
from github import Github
from github.Repository import Repository
from github.GithubException import GithubException


class GitHubClient:
    """GitHub API client wrapper with error handling."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client.
        
        Args:
            token: GitHub personal access token. If None, tries to load from GITHUB_TOKEN env var.
        """
        # Load environment variables from .env file
        load_dotenv()
        
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError(
                "GitHub token is required. Set GITHUB_TOKEN environment variable "
                "or pass token parameter. Get you token from: "
                "https://github.com/settings/tokens"
            )
        
        self.github = Github(self.token, per_page=100)
    
    def get_repository(self, owner: str, repo: str) -> Repository:
        """Get repository information.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            
        Returns:
            GitHub Repository object
            
        Raises:
            ValueError: If repository not found or access denied
        """
        try:
            return self.github.get_repo(f"{owner}/{repo}")
        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"Repository '{owner}/{repo}' not found")
            elif e.status == 401:
                raise ValueError("Invalid GitHub token. Please check your token.")
            elif e.status == 403:
                raise ValueError(f"Access denied to repository '{owner}/{repo}'")
            else:
                raise ValueError(f"GitHub API error: {e.data.get('message', str(e))}")
    
    def test_connection(self) -> bool:
        """Test GitHub API connection.
        
        Returns:
            True if connection successful
        """
        try:
            user = self.github.get_user()
            return True
        except Exception:
            return False
