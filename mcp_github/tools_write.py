"""GitHub write tools for MCP server."""

import json
import base64
from typing import Any, Dict, Optional
from datetime import datetime

from github_client import GitHubClient
from utils import validate_file_path


async def create_or_update_file(
    owner: str, 
    repo: str, 
    path: str, 
    content: str, 
    message: str,
    branch: str = "main",
    committer_name: Optional[str] = None,
    committer_email: Optional[str] = None
) -> Dict[str, Any]:
    """Create or update a file in a GitHub repository.

    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        path: File path in repository
        content: File content
        message: Commit message
        branch: Target branch (default: main)
        committer_name: Committer name (optional)
        committer_email: Committer email (optional)

    Returns:
        Dictionary containing operation result
    """
    try:
        # Validate file path
        if not validate_file_path(path):
            return {
                "success": False,
                "error": "Invalid file path",
                "summary": "File path contains invalid characters or is too long"
            }

        client = GitHubClient()
        repository = client.get_repository(owner, repo)
        
        # Check if file exists
        try:
            file = repository.get_contents(path, ref=branch)
            sha = file.sha
            operation = "updated"
        except:
            sha = None
            operation = "created"

        # Create or update file
        if sha:
            # File exists, update it
            result = repository.update_file(
                path=path,
                message=message,
                content=content,
                sha=sha,
                branch=branch
            )
            # PyGithub의 update_file은 딕셔너리를 반환: {'content': ContentFile, 'commit': Commit}
            content_obj = result['content']
            commit_obj = result['commit']
        else:
            # File doesn't exist, create it
            result = repository.create_file(
                path=path,
                message=message,
                content=content,
                branch=branch
            )
            # PyGithub의 create_file은 딕셔너리를 반환: {'content': ContentFile, 'commit': Commit}
            content_obj = result['content']
            commit_obj = result['commit']

        return {
            "success": True,
            "summary": f"File '{path}' {operation} successfully",
            "data": {
                "operation": operation,
                "path": path,
                "commit_sha": commit_obj.sha,
                "commit_message": message,
                "branch": branch,
                "url": content_obj.html_url
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "summary": f"Failed to create/update file: {str(e)}"
        }


async def delete_file(
    owner: str, 
    repo: str, 
    path: str, 
    message: str,
    branch: str = "main",
    committer_name: Optional[str] = None,
    committer_email: Optional[str] = None
) -> Dict[str, Any]:
    """Delete a file from a GitHub repository.

    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        path: File path in repository
        message: Commit message
        branch: Target branch (default: main)
        committer_name: Committer name (optional)
        committer_email: Committer email (optional)

    Returns:
        Dictionary containing operation result
    """
    try:
        client = GitHubClient()
        repository = client.get_repository(owner, repo)
        
        # Get file to delete
        file = repository.get_contents(path, ref=branch)
        
        # Prepare commit data
        commit_data = {
            "message": message,
            "sha": file.sha,
            "branch": branch
        }

        # Add committer info if provided
        if committer_name and committer_email:
            commit_data["committer"] = {
                "name": committer_name,
                "email": committer_email
            }

        # Delete file
        result = repository.delete_file(
            path=path,
            message=message,
            sha=file.sha,
            branch=branch,
            committer=commit_data.get("committer")
        )

        return {
            "success": True,
            "summary": f"File '{path}' deleted successfully",
            "data": {
                "operation": "deleted",
                "path": path,
                "commit_sha": result.commit.sha,
                "commit_message": message,
                "branch": branch
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "summary": f"Failed to delete file: {str(e)}"
        }


async def create_branch(
    owner: str, 
    repo: str, 
    new_branch: str, 
    base_branch: str = "main"
) -> Dict[str, Any]:
    """Create a new branch in a GitHub repository.

    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        new_branch: Name of the new branch
        base_branch: Base branch to create from (default: main)

    Returns:
        Dictionary containing operation result
    """
    try:
        client = GitHubClient()
        repository = client.get_repository(owner, repo)
        
        # Get base branch reference
        base_ref = repository.get_branch(base_branch)
        
        # Create new branch
        repository.create_git_ref(f"refs/heads/{new_branch}", base_ref.commit.sha)

        return {
            "success": True,
            "summary": f"Branch '{new_branch}' created successfully from '{base_branch}'",
            "data": {
                "operation": "branch_created",
                "new_branch": new_branch,
                "base_branch": base_branch,
                "base_commit_sha": base_ref.commit.sha
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "summary": f"Failed to create branch: {str(e)}"
        }


async def create_commit_with_multiple_files(
    owner: str,
    repo: str,
    files: list,
    message: str,
    branch: str = "main",
    committer_name: Optional[str] = None,
    committer_email: Optional[str] = None
) -> Dict[str, Any]:
    """Create a commit with multiple file changes.

    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        files: List of file changes (each with 'path', 'content', 'operation')
        message: Commit message
        branch: Target branch (default: main)
        committer_name: Committer name (optional)
        committer_email: Committer email (optional)

    Returns:
        Dictionary containing operation result
    """
    try:
        client = GitHubClient()
        repository = client.get_repository(owner, repo)
        
        # Get current tree
        branch_ref = repository.get_branch(branch)
        base_tree = branch_ref.commit.commit.tree
        
        # Prepare tree elements
        tree_elements = []
        
        for file_info in files:
            path = file_info["path"]
            operation = file_info["operation"]
            content = file_info.get("content", "")
            
            if operation == "create" or operation == "update":
                # Create or update file
                try:
                    existing_file = repository.get_contents(path, ref=branch)
                    tree_elements.append({
                        "path": path,
                        "mode": "100644",
                        "type": "blob",
                        "sha": repository.create_git_blob(content, "utf-8").sha
                    })
                except:
                    # File doesn't exist, create new
                    tree_elements.append({
                        "path": path,
                        "mode": "100644",
                        "type": "blob",
                        "sha": repository.create_git_blob(content, "utf-8").sha
                    })
            
            elif operation == "delete":
                # Skip deleted files in tree creation
                pass
        
        # Create new tree
        new_tree = repository.create_git_tree(tree_elements, base_tree)
        
        # Create commit
        commit_data = {
            "message": message,
            "tree": new_tree,
            "parents": [branch_ref.commit.sha]
        }
        
        if committer_name and committer_email:
            commit_data["committer"] = {
                "name": committer_name,
                "email": committer_email
            }
        
        new_commit = repository.create_git_commit(**commit_data)
        
        # Update branch reference
        branch_ref.edit(sha=new_commit.sha)
        
        return {
            "success": True,
            "summary": f"Commit created successfully with {len(files)} file changes",
            "data": {
                "operation": "multi_file_commit",
                "commit_sha": new_commit.sha,
                "commit_message": message,
                "branch": branch,
                "files_processed": len(files)
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "summary": f"Failed to create commit: {str(e)}"
        }


async def get_repository_status(
    owner: str, 
    repo: str, 
    ref: str = "HEAD"
) -> Dict[str, Any]:
    """Get repository status including last commit and branch info.

    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        ref: Reference (branch, tag, or commit SHA)

    Returns:
        Dictionary containing repository status
    """
    try:
        client = GitHubClient()
        repository = client.get_repository(owner, repo)
        
        # Get commit
        commit = repository.get_commit(ref)
        
        # Get branch info
        try:
            branch = repository.get_branch(ref)
            branch_name = branch.name
            is_default = branch.name == repository.default_branch
        except:
            branch_name = "detached HEAD"
            is_default = False
        
        return {
            "success": True,
            "summary": f"Repository status for {ref}",
            "data": {
                "commit_sha": commit.sha,
                "commit_message": commit.commit.message,
                "commit_author": commit.commit.author.name,
                "commit_date": commit.commit.author.date.isoformat(),
                "branch": branch_name,
                "is_default_branch": is_default,
                "files_changed": commit.files.totalCount if commit.files else 0,
                "additions": commit.stats.additions,
                "deletions": commit.stats.deletions
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "summary": f"Failed to get repository status: {str(e)}"
        }
