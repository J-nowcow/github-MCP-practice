"""GitHub MCP 리소스 핸들러."""

import json
from typing import Any, Dict, Optional
from .github_client import GitHubClient
from .utils import summarize_diff, format_file_size, is_binary_file, is_text


def get_pr_diff_resource(owner: str, repo: str, number: int) -> Dict[str, Any]:
    """PR diff를 리소스로 제공합니다.
    
    URI 형식: gh-pr-diff://{owner}/{repo}/{number}
    """
    try:
        client = GitHubClient()
        repository = client.get_repository(owner, repo)
        pull_request = repository.get_pull(number)
        
        # diff 정보 수집
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
                "patch": file.patch[:2000] if file.patch else None,  # 더 큰 제한
                "raw_url": file.raw_url
            }
            diff_data.append(file_data)
            total_additions += file.additions
            total_deletions += file.deletions
        
        # 리소스 메타데이터
        resource_data = {
            "type": "pr_diff",
            "owner": owner,
            "repo": repo,
            "pr_number": number,
            "title": pull_request.title,
            "author": pull_request.user.login,
            "state": pull_request.state,
            "files_changed": len(diff_data),
            "total_additions": total_additions,
            "total_deletions": total_deletions,
            "diff_files": diff_data,
            "summary": f"PR #{number}: {pull_request.title} - {len(diff_data)} files changed (+{total_additions} -{total_deletions})"
        }
        
        return {
            "content": json.dumps(resource_data, indent=2),
            "mime_type": "application/json",
            "metadata": {
                "name": f"PR #{number} Diff",
                "description": f"Diff for {owner}/{repo}#{number}",
                "size": len(json.dumps(resource_data)),
                "tags": ["github", "pr", "diff"]
            }
        }
        
    except Exception as e:
        return {
            "content": json.dumps({"error": str(e)}, indent=2),
            "mime_type": "application/json",
            "metadata": {
                "name": f"PR #{number} Diff Error",
                "description": f"Error loading diff: {str(e)}",
                "tags": ["github", "pr", "diff", "error"]
            }
        }


def get_file_resource(owner: str, repo: str, path: str, ref: str = "HEAD") -> Dict[str, Any]:
    """파일을 리소스로 제공합니다.
    
    URI 형식: gh-file://{owner}/{repo}/{path}?ref={ref}
    """
    try:
        client = GitHubClient()
        repository = client.get_repository(owner, repo)
        file_content = repository.get_contents(path, ref=ref)
        
        if isinstance(file_content, list):
            # 디렉토리인 경우
            files = []
            for item in file_content:
                file_data = {
                    "name": item.name,
                    "path": item.path,
                    "type": item.type,
                    "size": item.size,
                    "size_formatted": format_file_size(item.size),
                    "url": item.html_url
                }
                files.append(file_data)
            
            resource_data = {
                "type": "directory",
                "owner": owner,
                "repo": repo,
                "path": path,
                "ref": ref,
                "file_count": len(files),
                "files": files,
                "summary": f"Directory: {path} ({len(files)} items)"
            }
            
            return {
                "content": json.dumps(resource_data, indent=2),
                "mime_type": "application/json",
                "metadata": {
                    "name": f"Directory: {path}",
                    "description": f"Directory listing for {path}",
                    "size": len(json.dumps(resource_data)),
                    "tags": ["github", "directory", "listing"]
                }
            }
        else:
            # 단일 파일인 경우
            content = file_content.decoded_content
            is_text_content = is_text(content)
            
            if is_text_content and file_content.size < 1024 * 1024:  # 1MB 미만
                try:
                    file_text = content.decode('utf-8')
                except UnicodeDecodeError:
                    file_text = content.decode('utf-8', errors='replace')
                
                resource_data = {
                    "type": "file",
                    "owner": owner,
                    "repo": repo,
                    "path": path,
                    "ref": ref,
                    "name": file_content.name,
                    "size": file_content.size,
                    "size_formatted": format_file_size(file_content.size),
                    "encoding": file_content.encoding,
                    "is_text": True,
                    "content": file_text,
                    "url": file_content.html_url,
                    "summary": f"File: {path} ({format_file_size(file_content.size)})"
                }
                
                return {
                    "content": file_text,
                    "mime_type": "text/plain",
                    "metadata": {
                        "name": f"File: {path}",
                        "description": f"File content for {path}",
                        "size": file_content.size,
                        "tags": ["github", "file", "content"]
                    }
                }
            else:
                # 바이너리 파일이거나 너무 큰 파일
                resource_data = {
                    "type": "file",
                    "owner": owner,
                    "repo": repo,
                    "path": path,
                    "ref": ref,
                    "name": file_content.name,
                    "size": file_content.size,
                    "size_formatted": format_file_size(file_content.size),
                    "is_text": False,
                    "is_binary": is_binary_file(file_content.name),
                    "url": file_content.html_url,
                    "note": "Binary file or file too large to display as text"
                }
                
                return {
                    "content": json.dumps(resource_data, indent=2),
                    "mime_type": "application/json",
                    "metadata": {
                        "name": f"File: {path}",
                        "description": f"File metadata for {path}",
                        "size": len(json.dumps(resource_data)),
                        "tags": ["github", "file", "metadata"]
                    }
                }
                
    except Exception as e:
        return {
            "content": json.dumps({"error": str(e)}, indent=2),
            "mime_type": "application/json",
            "metadata": {
                "name": f"File: {path} Error",
                "description": f"Error loading file: {str(e)}",
                "tags": ["github", "file", "error"]
            }
        }


def parse_gh_uri(uri: str) -> Optional[Dict[str, Any]]:
    """GitHub 리소스 URI를 파싱합니다.
    
    지원하는 URI 형식:
    - gh-pr-diff://{owner}/{repo}/{number}
    - gh-file://{owner}/{repo}/{path}?ref={ref}
    """
    if uri.startswith("gh-pr-diff://"):
        # gh-pr-diff://owner/repo/number
        parts = uri[15:].split("/")
        if len(parts) >= 3:
            try:
                number = int(parts[2])
                return {
                    "type": "pr_diff",
                    "owner": parts[0],
                    "repo": parts[1],
                    "number": number
                }
            except ValueError:
                return None
    
    elif uri.startswith("gh-file://"):
        # gh-file://owner/repo/path?ref=ref
        parts = uri[11:].split("/")
        if len(parts) >= 3:
            owner = parts[0]
            repo = parts[1]
            path_parts = parts[2:]
            
            # ref 파라미터 처리
            ref = "HEAD"
            if "?" in path_parts[-1]:
                path_with_ref = path_parts[-1].split("?")
                path_parts[-1] = path_with_ref[0]
                if "ref=" in path_with_ref[1]:
                    ref = path_with_ref[1].split("ref=")[1]
            
            path = "/".join(path_parts)
            
            return {
                "type": "file",
                "owner": owner,
                "repo": repo,
                "path": path,
                "ref": ref
            }
    
    return None
