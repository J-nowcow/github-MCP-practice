"""GitHub MCP resource handlers for URI-based content access."""

import json
import re
from typing import Any, Optional

from github_client import GitHubClient
from utils import is_text, format_file_size, is_binary_file


def parse_gh_uri(uri: str) -> tuple[str, str, str, Optional[str]]:
    """Parse GitHub URI to extract owner, repo, path, and optional ref.

    Args:
        uri: GitHub URI (gh-file://owner/repo/path or gh-pr-diff://owner/repo/number)

    Returns:
        Tuple of (owner, repo, path, ref)
        """
    # gh-file://owner/repo/path[?ref=branch]
    file_pattern = r"^gh-file://([^/]+)/([^/]+)/(.+?)(?:\?ref=([^&]+))?$"
    file_match = re.match(file_pattern, uri)
    if file_match:
        owner, repo, path, ref = file_match.groups()
        return owner, repo, path, ref or "HEAD"

    # gh-pr-diff://owner/repo/number
    pr_pattern = r"^gh-pr-diff://([^/]+)/([^/]+)/(.+)$"
    pr_match = re.match(pr_pattern, uri)
    if pr_match:
        owner, repo, number = pr_match.groups()
        return owner, repo, number, None

    raise ValueError(f"Unsupported URI scheme: {uri}")


def get_pr_diff_resource(owner: str, repo: str, number: str) -> dict[str, Any]:
    """Get PR diff as a resource.

    Args:
        owner: Repository owner
        repo: Repository name
        number: PR number

    Returns:
        Resource data with content and metadata
    """
    try:
        client = GitHubClient()
        repository = client.get_repository(owner, repo)
        pull_request = repository.get_pull(int(number))

        # Get diff
        diff = pull_request.get_files()

        diff_data = []
        total_additions = 0
        total_deletions = 0

        for file in diff:
            # 트렁케이션 정보 추가
            patch_content = file.patch[:2000] if file.patch else None
            truncated = len(file.patch) > 2000 if file.patch else False

            file_data = {
                "filename": file.filename,
                "status": file.status,
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
                "patch": patch_content,
                "truncated": truncated,
                "original_length": len(file.patch) if file.patch else 0,
                "raw_url": file.raw_url,
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

        data = {
            "summary": summary,
            "data": diff_data,
            "success": True,
            "file_count": len(diff_data),
            "total_additions": total_additions,
            "total_deletions": total_deletions,
        }

        # JSON 중복 처리 제거 - 한 번만 생성
        resource_data = json.dumps(data, indent=2)

        metadata = {
            "name": f"PR #{number} Diff",
            "description": f"Diff for pull request #{number} in {owner}/{repo}",
            "mime_type": "application/json",
            "size": len(resource_data),  # 실제 반환 크기
            "uri": f"gh-pr-diff://{owner}/{repo}/{number}",
            "source": f"https://github.com/{owner}/{repo}/pull/{number}",
        }

        return {"content": resource_data, "metadata": metadata}

    except Exception as e:
        error_data = {
            "error": str(e),
            "success": False,
            "uri": f"gh-pr-diff://{owner}/{repo}/{number}",
        }

        resource_data = json.dumps(error_data, indent=2)

        metadata = {
            "name": f"PR #{number} Diff Error",
            "description": f"Error retrieving diff for PR #{number}",
            "mime_type": "application/json",
            "size": len(resource_data),
            "uri": f"gh-pr-diff://{owner}/{repo}/{number}",
            "error": True,
        }

        return {"content": resource_data, "metadata": metadata}


def get_file_resource(
    owner: str, repo: str, path: str, ref: str = "HEAD"
) -> dict[str, Any]:
    """Get file or directory as a resource.

    Args:
        owner: Repository owner
        repo: Repository name
        path: File path in repository
        ref: Git reference (branch, tag, or commit SHA)

    Returns:
        Resource data with content and metadata
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
                    "download_url": item.download_url,
                }
                files.append(file_data)

            summary = f"""Directory: {path}
Repository: {repository.full_name}
Reference: {ref}
Files: {len(files)}

Contents:
"""
            for file in files[:10]:  # Show first 10 files
                summary += (
                    f"  {file['name']} ({file['type']}, {file['size_formatted']})\n"
                )

            if len(files) > 10:
                summary += f"\n... and {len(files) - 10} more items"

            data = {
                "summary": summary,
                "data": files,
                "success": True,
                "type": "directory",
                "file_count": len(files),
            }

            # JSON 중복 처리 제거
            resource_data = json.dumps(data, indent=2)

            metadata = {
                "name": f"Directory: {path}",
                "description": f"Directory contents for {path} in {owner}/{repo}",
                "mime_type": "application/json",
                "size": len(resource_data),
                "uri": f"gh-file://{owner}/{repo}/{path}?ref={ref}",
                "source": f"https://github.com/{owner}/{repo}/tree/{ref}/{path}",
                "type": "directory",
            }

            return {"content": resource_data, "metadata": metadata}

        else:
            # Single file
            content = file_content.decoded_content
            is_text_content = is_text(content)

            # 바이너리 감지 개선
            is_binary = is_binary_file(file_content.name) or (
                hasattr(file_content, "content_type")
                and file_content.content_type
                and not file_content.content_type.startswith("text/")
            )

            file_data = {
                "name": file_content.name,
                "path": file_content.path,
                "type": file_content.type,
                "original_size": file_content.size,  # 원본 크기
                "size_formatted": format_file_size(file_content.size),
                "encoding": file_content.encoding,
                "url": file_content.html_url,
                "download_url": file_content.download_url,
                "is_text": is_text_content,
                "is_binary": is_binary,
            }

            if is_text_content and file_content.size < 1024 * 1024:  # Less than 1MB
                try:
                    file_data["content"] = content.decode("utf-8")
                    file_data["content_size"] = len(
                        file_data["content"]
                    )  # 실제 반환 크기
                except UnicodeDecodeError:
                    file_data["content"] = content.decode("utf-8", errors="replace")
                    file_data["content_size"] = len(file_data["content"])
            else:
                file_data["content"] = None
                file_data["content_size"] = 0
                if file_content.size >= 1024 * 1024:
                    file_data["content_note"] = "File too large to display (>1MB)"
                elif is_binary:
                    file_data["content_note"] = "Binary file - content not displayed"
                else:
                    file_data["content_note"] = "Content not available"

            summary = f"""File: {path}
Repository: {repository.full_name}
Reference: {ref}
Original Size: {file_data["size_formatted"]}
Content Size: {file_data["content_size"]} characters
Type: {"Text" if is_text_content else "Binary"}

"""
            if file_data["content"]:
                summary += (
                    f"Content preview (first 200 chars):\n{file_data['content'][:200]}"
                )
                if len(file_data["content"]) > 200:
                    summary += "..."
            else:
                summary += file_data.get("content_note", "No content preview available")

            data = {
                "summary": summary,
                "data": file_data,
                "success": True,
                "type": "file",
                "file_size": file_content.size,
            }

            # JSON 중복 처리 제거
            resource_data = json.dumps(data, indent=2)

            metadata = {
                "name": f"File: {path}",
                "description": f"File content for {path} in {owner}/{repo}",
                "mime_type": "application/json",
                "size": len(resource_data),
                "uri": f"gh-file://{owner}/{repo}/{path}?ref={ref}",
                "source": f"https://github.com/{owner}/{repo}/blob/{ref}/{path}",
                "type": "file",
                "original_size": file_content.size,
                "content_size": file_data["content_size"],
            }

            return {"content": resource_data, "metadata": metadata}

    except Exception as e:
        error_data = {
            "error": str(e),
            "success": False,
            "uri": f"gh-file://{owner}/{repo}/{path}?ref={ref}",
        }

        resource_data = json.dumps(error_data, indent=2)

        metadata = {
            "name": f"File Error: {path}",
            "description": f"Error retrieving file {path}",
            "mime_type": "application/json",
            "size": len(resource_data),
            "uri": f"gh-file://{owner}/{repo}/{path}?ref={ref}",
            "error": True,
        }

        return {"content": resource_data, "metadata": metadata}
