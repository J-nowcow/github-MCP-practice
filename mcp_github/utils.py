"""Utility functions for GitHub MCP server."""

import re
from typing import Union


def is_text(data: Union[bytes, str]) -> bool:
    """Check if data is text-based content.

    Args:
        data: Data to check (bytes or str)

    Returns:
        True if data appears to be text, False otherwise
    """
    if isinstance(data, str):
        return True

    if isinstance(data, bytes):
        # Check for null bytes (common in binary files)
        if b"\x00" in data:
            return False

        # Try to decode as UTF-8
        try:
            data.decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False

    return False


def summarize_diff(diff_text: str, max_chars: int = 1000) -> str:
    """Summarize a diff text if it's too long.

    Args:
        diff_text: The diff text to summarize
        max_chars: Maximum characters before truncating

    Returns:
        Summarized diff text
    """
    if len(diff_text) <= max_chars:
        return diff_text

    # truncation notice 길이를 고려해서 계산
    truncation_notice = "\n\n... (truncated)"
    max_content_chars = max_chars - len(truncation_notice)
    
    # 문자 수 기반으로 자르기
    lines = diff_text.split("\n")
    summary_lines = []
    current_length = 0

    for line in lines:
        line_length = len(line) + 1  # +1 for newline
        if current_length + line_length > max_content_chars:
            break
        summary_lines.append(line)
        current_length += line_length

    summary = "\n".join(summary_lines)

    # Add truncation notice
    if len(summary) < len(diff_text):
        summary += truncation_notice

    return summary


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def is_binary_file(filename: str) -> bool:
    """Check if a file is likely binary based on extension.

    Args:
        filename: Name of the file

    Returns:
        True if file is likely binary
    """
    binary_extensions = {
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".bin",
        ".obj",
        ".o",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".ico",
        ".svg",
        ".mp3",
        ".mp4",
        ".avi",
        ".mov",
        ".wav",
        ".flac",
        ".zip",
        ".tar",
        ".gz",
        ".rar",
        ".7z",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".db",
        ".sqlite",
        ".sqlite3",
    }

    return any(filename.lower().endswith(ext) for ext in binary_extensions)


def validate_file_path(path: str) -> bool:
    """Validate file path for GitHub operations.
    
    Args:
        path: File path to validate
        
    Returns:
        True if path is valid, False otherwise
    """
    if not path or len(path) > 255:
        return False
    
    # GitHub에서 허용하지 않는 문자들
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\']
    if any(char in path for char in invalid_chars):
        return False
    
    # 경로가 ..로 시작하거나 끝나면 안됨
    if path.startswith('..') or path.endswith('..'):
        return False
    
    # 연속된 슬래시나 백슬래시 방지
    if '//' in path or '\\\\' in path:
        return False
    
    return True


def sanitize_commit_message(message: str) -> str:
    """Sanitize commit message for GitHub.
    
    Args:
        message: Raw commit message
        
    Returns:
        Sanitized commit message
    """
    if not message:
        return "Update files"
    
    # 첫 번째 줄만 사용 (GitHub의 첫 번째 줄 제한)
    lines = message.strip().split('\n')
    first_line = lines[0].strip()
    
    # 길이 제한 (GitHub 권장사항)
    if len(first_line) > 72:
        first_line = first_line[:69] + "..."
    
    return first_line
