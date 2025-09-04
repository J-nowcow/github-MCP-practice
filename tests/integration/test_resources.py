"""리소스 핸들러 통합 테스트."""

import pytest
from unittest.mock import patch, Mock
from mcp_github.resources import (
    parse_gh_uri,
    get_pr_diff_resource,
    get_file_resource
)


class TestResourceHandlers:
    """리소스 핸들러 통합 테스트 클래스."""

    def test_parse_gh_uri_pr_diff(self):
        """PR diff URI 파싱 테스트."""
        uri = "gh-pr-diff://owner/repo/123"
        result = parse_gh_uri(uri)
        
        assert result == ("owner", "repo", "123", None)

    def test_parse_gh_uri_file_with_ref(self):
        """파일 URI 파싱 테스트 (ref 포함)."""
        uri = "gh-file://owner/repo/path/to/file?ref=main"
        result = parse_gh_uri(uri)
        
        assert result == ("owner", "repo", "path/to/file", "main")

    def test_parse_gh_uri_file_without_ref(self):
        """파일 URI 파싱 테스트 (ref 없음)."""
        uri = "gh-file://owner/repo/path/to/file"
        result = parse_gh_uri(uri)
        
        assert result == ("owner", "repo", "path/to/file", "HEAD")

    def test_parse_gh_uri_invalid_format(self):
        """잘못된 URI 형식 테스트."""
        invalid_uris = [
            "invalid://uri",
            "gh-file://",
            "gh-pr-diff://owner",
            "gh-file://owner/repo"
        ]
        
        for uri in invalid_uris:
            with pytest.raises(ValueError):
                parse_gh_uri(uri)

    def test_get_pr_diff_resource_success(self):
        """PR diff 리소스 성공 테스트."""
        with patch('mcp_github.resources.GitHubClient') as mock_client_class:
            mock_client = Mock()
            mock_repo = Mock()
            mock_repo.full_name = "test-owner/test-repo"
            
            mock_pr = Mock()
            mock_pr.title = "Test PR"
            mock_pr.user.login = "test-user"
            mock_pr.state = "open"
            
            mock_file = Mock()
            mock_file.filename = "test.py"
            mock_file.status = "modified"
            mock_file.additions = 10
            mock_file.deletions = 5
            mock_file.changes = 15
            mock_file.patch = "@@ -1,1 +1,1 @@\n-old line\n+new line\n"
            mock_file.raw_url = "https://github.com/test-owner/test-repo/raw/main/test.py"
            
            mock_repo.get_pull.return_value = mock_pr
            mock_pr.get_files.return_value = [mock_file]
            mock_client.get_repository.return_value = mock_repo
            mock_client_class.return_value = mock_client
            
            result = get_pr_diff_resource("test-owner", "test-repo", "1")
            
            assert "content" in result
            assert "metadata" in result
            assert result["metadata"]["name"] == "PR #1 Diff"
            assert result["metadata"]["mime_type"] == "application/json"
            
            # JSON 파싱 테스트
            import json
            content = json.loads(result["content"])
            assert content["success"] is True
            assert content["file_count"] == 1
            assert content["total_additions"] == 10
            assert content["total_deletions"] == 5

    def test_get_pr_diff_resource_error(self):
        """PR diff 리소스 에러 테스트."""
        with patch('mcp_github.resources.GitHubClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_repository.side_effect = Exception("Repository not found")
            mock_client_class.return_value = mock_client
            
            result = get_pr_diff_resource("invalid-owner", "invalid-repo", "1")
            
            assert "content" in result
            assert "metadata" in result
            assert result["metadata"]["error"] is True
            
            # JSON 파싱 테스트
            import json
            content = json.loads(result["content"])
            assert content["success"] is False
            assert "Repository not found" in content["error"]

    def test_get_file_resource_file_success(self):
        """파일 리소스 성공 테스트."""
        with patch('mcp_github.resources.GitHubClient') as mock_client_class:
            mock_client = Mock()
            mock_repo = Mock()
            mock_repo.full_name = "test-owner/test-repo"
            
            mock_file = Mock()
            mock_file.name = "test.py"
            mock_file.path = "test.py"
            mock_file.type = "file"
            mock_file.size = 100
            mock_file.encoding = "utf-8"
            mock_file.decoded_content = b"print('Hello, World!')"
            mock_file.html_url = "https://github.com/test-owner/test-repo/blob/main/test.py"
            mock_file.download_url = "https://github.com/test-owner/test-repo/raw/main/test.py"
            
            mock_repo.get_contents.return_value = mock_file
            mock_client.get_repository.return_value = mock_repo
            mock_client_class.return_value = mock_client
            
            result = get_file_resource("test-owner", "test-repo", "test.py", "main")
            
            assert "content" in result
            assert "metadata" in result
            assert result["metadata"]["name"] == "File: test.py"
            assert result["metadata"]["mime_type"] == "application/json"
            
            # JSON 파싱 테스트
            import json
            content = json.loads(result["content"])
            assert content["success"] is True
            assert content["type"] == "file"
            assert content["data"]["is_text"] is True
            assert content["data"]["content"] is not None

    def test_get_file_resource_directory_success(self):
        """디렉토리 리소스 성공 테스트."""
        with patch('mcp_github.resources.GitHubClient') as mock_client_class:
            mock_client = Mock()
            mock_repo = Mock()
            mock_repo.full_name = "test-owner/test-repo"
            
            # 디렉토리 콘텐츠 모킹
            mock_dir_item1 = Mock()
            mock_dir_item1.name = "file1.py"
            mock_dir_item1.path = "dir/file1.py"
            mock_dir_item1.type = "file"
            mock_dir_item1.size = 100
            mock_dir_item1.html_url = "https://github.com/test-owner/test-repo/blob/main/dir/file1.py"
            mock_dir_item1.download_url = "https://github.com/test-owner/test-repo/raw/main/dir/file1.py"
            
            mock_dir_item2 = Mock()
            mock_dir_item2.name = "file2.py"
            mock_dir_item2.path = "dir/file2.py"
            mock_dir_item2.type = "file"
            mock_dir_item2.size = 200
            mock_dir_item2.html_url = "https://github.com/test-owner/test-repo/blob/main/dir/file2.py"
            mock_dir_item2.download_url = "https://github.com/test-owner/test-repo/raw/main/dir/file2.py"
            
            mock_repo.get_contents.return_value = [mock_dir_item1, mock_dir_item2]
            mock_client.get_repository.return_value = mock_repo
            mock_client_class.return_value = mock_client
            
            result = get_file_resource("test-owner", "test-repo", "dir", "main")
            
            assert "content" in result
            assert "metadata" in result
            assert result["metadata"]["name"] == "Directory: dir"
            assert result["metadata"]["type"] == "directory"
            
            # JSON 파싱 테스트
            import json
            content = json.loads(result["content"])
            assert content["success"] is True
            assert content["type"] == "directory"
            assert content["file_count"] == 2

    def test_get_file_resource_binary_file(self):
        """바이너리 파일 리소스 테스트."""
        with patch('mcp_github.resources.GitHubClient') as mock_client_class:
            mock_client = Mock()
            mock_repo = Mock()
            mock_repo.full_name = "test-owner/test-repo"
            
            mock_binary_file = Mock()
            mock_binary_file.name = "image.png"
            mock_binary_file.path = "image.png"
            mock_binary_file.type = "file"
            mock_binary_file.size = 100 * 1024  # 100KB (1MB 미만)
            mock_binary_file.encoding = None
            mock_binary_file.decoded_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
            mock_binary_file.html_url = "https://github.com/test-owner/test-repo/blob/main/image.png"
            mock_binary_file.download_url = "https://github.com/test-owner/test-repo/raw/main/image.png"
            
            mock_repo.get_contents.return_value = mock_binary_file
            mock_client.get_repository.return_value = mock_repo
            mock_client_class.return_value = mock_client
            
            result = get_file_resource("test-owner", "test-repo", "image.png", "main")
            
            # JSON 파싱 테스트
            import json
            content = json.loads(result["content"])
            assert content["success"] is True
            assert content["data"]["is_binary"] is True
            assert content["data"]["content"] is None
            assert "Binary file" in content["data"]["content_note"]

    def test_get_file_resource_large_file(self):
        """큰 파일 리소스 테스트."""
        with patch('mcp_github.resources.GitHubClient') as mock_client_class:
            mock_client = Mock()
            mock_repo = Mock()
            mock_repo.full_name = "test-owner/test-repo"
            
            mock_large_file = Mock()
            mock_large_file.name = "large_file.txt"
            mock_large_file.path = "large_file.txt"
            mock_large_file.type = "file"
            mock_large_file.size = 2 * 1024 * 1024  # 2MB
            mock_large_file.encoding = "utf-8"
            mock_large_file.decoded_content = b"Large file content..." * 100000
            mock_large_file.html_url = "https://github.com/test-owner/test-repo/blob/main/large_file.txt"
            mock_large_file.download_url = "https://github.com/test-owner/test-repo/raw/main/large_file.txt"
            
            mock_repo.get_contents.return_value = mock_large_file
            mock_client.get_repository.return_value = mock_repo
            mock_client_class.return_value = mock_client
            
            result = get_file_resource("test-owner", "test-repo", "large_file.txt", "main")
            
            # JSON 파싱 테스트
            import json
            content = json.loads(result["content"])
            assert content["success"] is True
            assert content["data"]["content"] is None
            assert "File too large" in content["data"]["content_note"]

    def test_get_file_resource_error(self):
        """파일 리소스 에러 테스트."""
        with patch('mcp_github.resources.GitHubClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_repository.side_effect = Exception("File not found")
            mock_client_class.return_value = mock_client
            
            result = get_file_resource("invalid-owner", "invalid-repo", "invalid-file", "main")
            
            assert "content" in result
            assert "metadata" in result
            assert result["metadata"]["error"] is True
            
            # JSON 파싱 테스트
            import json
            content = json.loads(result["content"])
            assert content["success"] is False
            assert "File not found" in content["error"]
