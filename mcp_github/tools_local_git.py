import subprocess
import json
import os
from typing import Any, Dict, List, Optional
from pathlib import Path

async def execute_git_command(command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
    """로컬 Git 명령어를 실행하고 결과를 반환합니다."""
    try:
        # 기본 작업 디렉토리를 프로젝트 루트로 설정
        if cwd is None:
            # 현재 스크립트 위치에서 프로젝트 루트 찾기
            current_dir = Path(__file__).parent.parent
            cwd = str(current_dir)
        
        print(f"Executing Git command: {command} in directory: {cwd}")
        
        # Git 명령어 실행
        result = subprocess.run(
            command.split(),
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
            "command": command,
            "cwd": cwd
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "명령어 실행 시간 초과",
            "command": command,
            "cwd": cwd
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": command,
            "cwd": cwd
        }

async def get_git_status(cwd: Optional[str] = None) -> Dict[str, Any]:
    """현재 Git 저장소 상태를 확인합니다."""
    result = await execute_git_command("git status --porcelain", cwd)
    if result["success"]:
        # 변경된 파일들을 파싱
        files = []
        if result["stdout"]:
            for line in result["stdout"].split('\n'):
                if line.strip():
                    status = line[:2]
                    filename = line[3:]
                    files.append({
                        "status": status,
                        "filename": filename
                    })
        
        return {
            "success": True,
            "files": files,
            "raw_output": result["stdout"]
        }
    else:
        return {
            "success": False,
            "error": result.get("error") or result.get("stderr"),
            "raw_output": result.get("stderr", "")
        }

async def stage_all_changes(cwd: Optional[str] = None) -> Dict[str, Any]:
    """모든 변경사항을 스테이징합니다."""
    result = await execute_git_command("git add .", cwd)
    return {
        "success": result["success"],
        "message": "모든 변경사항이 스테이징되었습니다." if result["success"] else "스테이징 실패",
        "error": result.get("error") or result.get("stderr")
    }

async def stage_specific_files(files: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
    """특정 파일들을 스테이징합니다."""
    if not files:
        return {"success": False, "error": "스테이징할 파일이 지정되지 않았습니다."}
    
    command = f"git add {' '.join(files)}"
    result = await execute_git_command(command, cwd)
    return {
        "success": result["success"],
        "message": f"파일들이 스테이징되었습니다: {', '.join(files)}" if result["success"] else "스테이징 실패",
        "error": result.get("error") or result.get("stderr")
    }

async def create_commit(message: str, cwd: Optional[str] = None) -> Dict[str, Any]:
    """커밋을 생성합니다."""
    # 메시지에 따옴표가 포함되어 있으면 이스케이프 처리
    escaped_message = message.replace('"', '\\"')
    
    # Git 명령어를 리스트로 구성하여 공백 문제 해결
    command_parts = ["git", "commit", "-m", escaped_message]
    
    try:
        # 기본 작업 디렉토리를 프로젝트 루트로 설정
        if cwd is None:
            current_dir = Path(__file__).parent.parent
            cwd = str(current_dir)
        
        print(f"Executing Git commit command: {' '.join(command_parts)} in directory: {cwd}")
        
        # Git 명령어 실행
        result = subprocess.run(
            command_parts,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "message": "커밋이 성공적으로 생성되었습니다." if result.returncode == 0 else "커밋 생성 실패",
            "commit_hash": result.stdout.split()[-1] if result.returncode == 0 and "commit" in result.stdout else None,
            "error": result.stderr if result.returncode != 0 else "",
            "command": " ".join(command_parts),
            "cwd": cwd
        }
    except Exception as e:
        return {
            "success": False,
            "message": "커밋 생성 실패",
            "commit_hash": None,
            "error": str(e),
            "command": " ".join(command_parts),
            "cwd": cwd
        }

async def push_to_remote(branch: str = "main", remote: str = "origin", cwd: Optional[str] = None) -> Dict[str, Any]:
    """원격 저장소에 푸시합니다."""
    command = f"git push {remote} {branch}"
    result = await execute_git_command(command, cwd)
    return {
        "success": result["success"],
        "message": f"{branch} 브랜치가 {remote}에 성공적으로 푸시되었습니다." if result["success"] else "푸시 실패",
        "error": result.get("error") or result.get("stderr")
    }

async def get_commit_history(limit: int = 10, cwd: Optional[str] = None) -> Dict[str, Any]:
    """커밋 히스토리를 가져옵니다."""
    command = f"git log --oneline -{limit}"
    result = await execute_git_command(command, cwd)
    if result["success"]:
        commits = []
        if result["stdout"]:
            for line in result["stdout"].split('\n'):
                if line.strip():
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        commits.append({
                            "hash": parts[0],
                            "message": parts[1]
                        })
        
        return {
            "success": True,
            "commits": commits,
            "raw_output": result["stdout"]
        }
    else:
        return {
            "success": False,
            "error": result.get("error") or result.get("stderr"),
            "raw_output": result.get("stderr", "")
        }

async def check_git_repository(cwd: Optional[str] = None) -> Dict[str, Any]:
    """현재 디렉토리가 Git 저장소인지 확인합니다."""
    result = await execute_git_command("git rev-parse --git-dir", cwd)
    return {
        "is_git_repo": result["success"],
        "git_dir": result["stdout"] if result["success"] else None,
        "error": result.get("error") or result.get("stderr")
    }

async def get_current_branch(cwd: Optional[str] = None) -> Dict[str, Any]:
    """현재 브랜치를 가져옵니다."""
    result = await execute_git_command("git branch --show-current", cwd)
    return {
        "success": result["success"],
        "current_branch": result["stdout"].strip() if result["success"] else None,
        "error": result.get("error") or result.get("stderr")
    }

async def get_remote_info(cwd: Optional[str] = None) -> Dict[str, Any]:
    """원격 저장소 정보를 가져옵니다."""
    result = await execute_git_command("git remote -v", cwd)
    if result["success"]:
        remotes = {}
        if result["stdout"]:
            for line in result["stdout"].split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        url = parts[1]
                        remotes[name] = url
        
        return {
            "success": True,
            "remotes": remotes,
            "raw_output": result["stdout"]
        }
    else:
        return {
            "success": False,
            "error": result.get("error") or result.get("stderr"),
            "raw_output": result.get("stderr", "")
        }
