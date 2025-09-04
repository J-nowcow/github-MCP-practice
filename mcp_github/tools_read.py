"""GitHub read tools for MCP server."""

import json
from typing import Any, Dict

from .github_client import GitHubClient


async def get_repo(owner: str, repo: str) -> Dict[str, Any]:
    """Get repository information from GitHub.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        
    Returns:
        Dictionary containing repository summary and full data
    """
    try:
        client = GitHubClient()
        repository = client.get_repository(owner, repo)
        
        # Create summary
        summary = f"""Repository: {repository.full_name}
Description: {repository.description or 'No description'}
Language: {repository.language or 'Not specified'}
Stars: {repository.stargazers_count}
Forks: {repository.forks_count}
Open Issues: {repository.open_issues_count}
Created: {repository.created_at.strftime('%Y-%m-%d')}
Updated: {repository.updated_at.strftime('%Y-%m-%d')}
Default Branch: {repository.default_branch}
License: {repository.license.name if repository.license else 'Not specified'}
Homepage: {repository.homepage or 'Not specified'}"""
        
        # Full repository data as JSON string
        repo_data = {
            "id": repository.id,
            "name": repository.name,
            "full_name": repository.full_name,
            "description": repository.description,
            "language": repository.language,
            "stargazers_count": repository.stargazers_count,
            "forks_count": repository.forks_count,
            "open_issues_count": repository.open_issues_count,
            "created_at": repository.created_at.isoformat(),
            "updated_at": repository.updated_at.isoformat(),
            "default_branch": repository.default_branch,
            "license": repository.license.name if repository.license else None,
            "homepage": repository.homepage,
            "archived": repository.archived,
            "disabled": repository.disabled,
            "private": repository.private,
            "fork": repository.fork,
            "size": repository.size,
            "topics": list(repository.get_topics()),
            "url": repository.html_url,
            "clone_url": repository.clone_url,
            "ssh_url": repository.ssh_url,
        }
        
        return {
            "summary": summary,
            "data": json.dumps(repo_data, indent=2),
            "success": True
        }
        
    except ValueError as e:
        return {
            "summary": f"Error: {str(e)}",
            "data": "",
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "summary": f"Unexpected error: {str(e)}",
            "data": "",
            "success": False,
            "error": str(e)
        }
