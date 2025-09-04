"""GitHub read tools for MCP server."""

import json
from typing import Any, Dict, List

from .github_client import GitHubClient
from .utils import summarize_diff, format_file_size, is_binary_file


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


async def list_pull_requests(owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
    """List pull requests for a repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        state: PR state filter (open, closed, all)
        
    Returns:
        Dictionary containing PR list summary and data
    """
    try:
        client = GitHubClient()
        repository = client.get_repository(owner, repo)
        
        # Get pull requests
        pull_requests = repository.get_pulls(state=state)
        
        pr_list = []
        for pr in pull_requests:
            pr_data = {
                "number": pr.number,
                "title": pr.title,
                "user": pr.user.login,
                "state": pr.state,
                "created_at": pr.created_at.isoformat(),
                "updated_at": pr.updated_at.isoformat(),
                "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
                "closed_at": pr.closed_at.isoformat() if pr.closed_at else None,
                "draft": pr.draft,
                "mergeable": pr.mergeable,
                "mergeable_state": pr.mergeable_state,
                "comments": pr.comments,
                "commits": pr.commits,
                "additions": pr.additions,
                "deletions": pr.deletions,
                "changed_files": pr.changed_files,
                "url": pr.html_url
            }
            pr_list.append(pr_data)
        
        # Create summary
        summary = f"""Pull Requests ({state}): {len(pr_list)} found
Repository: {repository.full_name}

"""
        for pr in pr_list[:5]:  # Show first 5 PRs
            summary += f"#{pr['number']}: {pr['title']} by @{pr['user']} ({pr['state']})\n"
        
        if len(pr_list) > 5:
            summary += f"\n... and {len(pr_list) - 5} more PRs"
        
        return {
            "summary": summary,
            "data": json.dumps(pr_list, indent=2),
            "success": True,
            "count": len(pr_list)
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


async def get_pr_diff(owner: str, repo: str, number: int) -> Dict[str, Any]:
    """Get diff for a specific pull request.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        number: Pull request number
        
    Returns:
        Dictionary containing PR diff summary and data
    """
    try:
        client = GitHubClient()
        repository = client.get_repository(owner, repo)
        
        # Get pull request
        pull_request = repository.get_pull(number)
        
        # Get diff
        diff = pull_request.get_files()
        
        diff_data = []
        total_additions = 0
        total_deletions = 0
        
        for file in diff:
            file_data = {
                "filename": file.filename,
                "status": file.status,
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
                "patch": file.patch[:1000] if file.patch else None,  # Limit patch size
                "raw_url": file.raw_url
            }
            diff_data.append(file_data)
            total_additions += file.additions
            total_deletions += file.deletions
        
        # Create summary
        summary = f"""Pull Request #{number}: {pull_request.title}
Repository: {repository.full_name}
Author: @{pull_request.user.login}
State: {pull_request.state}
Files changed: {len(diff_data)}
Total additions: +{total_additions}
Total deletions: -{total_deletions}

Changed files:
"""
        for file in diff_data[:10]:  # Show first 10 files
            summary += f"  {file['filename']} ({file['status']}) +{file['additions']} -{file['deletions']}\n"
        
        if len(diff_data) > 10:
            summary += f"\n... and {len(diff_data) - 10} more files"
        
        return {
            "summary": summary,
            "data": json.dumps(diff_data, indent=2),
            "success": True,
            "file_count": len(diff_data),
            "total_additions": total_additions,
            "total_deletions": total_deletions
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


async def get_file(owner: str, repo: str, path: str, ref: str = "HEAD") -> Dict[str, Any]:
    """Get file content from a repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        path: File path in repository
        ref: Git reference (branch, tag, or commit SHA)
        
    Returns:
        Dictionary containing file content and metadata
    """
    try:
        client = GitHubClient()
        repository = client.get_repository(owner, repo)
        
        # Get file content
        file_content = repository.get_contents(path, ref=ref)
        
        if isinstance(file_content, list):
            # Directory
            files = []
            for item in file_content:
                file_data = {
                    "name": item.name,
                    "path": item.path,
                    "type": item.type,
                    "size": item.size,
                    "size_formatted": format_file_size(item.size),
                    "url": item.html_url,
                    "download_url": item.download_url
                }
                files.append(file_data)
            
            summary = f"""Directory: {path}
Repository: {repository.full_name}
Reference: {ref}
Files: {len(files)}

Contents:
"""
            for file in files[:10]:  # Show first 10 files
                summary += f"  {file['name']} ({file['type']}, {file['size_formatted']})\n"
            
            if len(files) > 10:
                summary += f"\n... and {len(files) - 10} more items"
            
            return {
                "summary": summary,
                "data": json.dumps(files, indent=2),
                "success": True,
                "type": "directory",
                "file_count": len(files)
            }
        
        else:
            # Single file
            content = file_content.decoded_content
            is_text_content = is_text(content)
            
            file_data = {
                "name": file_content.name,
                "path": file_content.path,
                "type": file_content.type,
                "size": file_content.size,
                "size_formatted": format_file_size(file_content.size),
                "encoding": file_content.encoding,
                "url": file_content.html_url,
                "download_url": file_content.download_url,
                "is_text": is_text_content,
                "is_binary": is_binary_file(file_content.name)
            }
            
            if is_text_content and file_content.size < 1024 * 1024:  # Less than 1MB
                try:
                    file_data["content"] = content.decode('utf-8')
                except UnicodeDecodeError:
                    file_data["content"] = content.decode('utf-8', errors='replace')
            else:
                file_data["content"] = None
                if file_content.size >= 1024 * 1024:
                    file_data["content_note"] = "File too large to display (>1MB)"
                elif not is_text_content:
                    file_data["content_note"] = "Binary file - content not displayed"
            
            summary = f"""File: {path}
Repository: {repository.full_name}
Reference: {ref}
Size: {file_data['size_formatted']}
Type: {'Text' if is_text_content else 'Binary'}

"""
            if file_data["content"]:
                summary += f"Content preview (first 200 chars):\n{file_data['content'][:200]}"
                if len(file_data["content"]) > 200:
                    summary += "..."
            else:
                summary += file_data.get("content_note", "No content preview available")
            
            return {
                "summary": summary,
                "data": json.dumps(file_data, indent=2),
                "success": True,
                "type": "file",
                "file_size": file_content.size
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
