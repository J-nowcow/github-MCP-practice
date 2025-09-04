"""읽기 도구 함수들 단위 테스트."""

import pytest
from unittest.mock import patch, Mock
from mcp_github.tools_read import (
    get_repo,
    list_pull_requests,
    get_pr_diff,
    get_file
)


class TestToolsRead:
    """읽기 도구 함수들 테스트 클래스."""

    @pytest.mark.asyncio
    async def test_get_repo_success(self, mock_github_client, sample_repo_data):
        """get_repo 성공 테스트."""
        with patch('mcp_github.tools_read.GitHubClient') as mock_client_class:
            mock_client_class.return_value = mock_github_client
            
            result = await get_repo("test-owner", "test-repo")
            
            assert result["success"] is True
            assert "summary" in result
            assert "data" in result
            assert "test-repo" in result["summary"]

    @pytest.mark.asyncio
    async def test_get_repo_error(self):
        """get_repo 에러 테스트."""
        with patch('mcp_github.tools_read.GitHubClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_repository.side_effect = Exception("Repository not found")
            mock_client_class.return_value = mock_client
            
            result = await get_repo("invalid-owner", "invalid-repo")
            
            assert result["success"] is False
            assert "error" in result
            assert "Repository not found" in result["error"]

    @pytest.mark.asyncio
    async def test_list_pull_requests_success(self, mock_github_client, sample_pr_data):
        """list_pull_requests 성공 테스트."""
        with patch('mcp_github.tools_read.GitHubClient') as mock_client_class:
            mock_client_class.return_value = mock_github_client
            
            result = await list_pull_requests("test-owner", "test-repo", "open")
            
            assert result["success"] is True
            assert "count" in result
            assert "data" in result
            assert result["count"] >= 0

    @pytest.mark.asyncio
    async def test_list_pull_requests_with_state_filter(self, mock_github_client):
        """상태별 PR 필터링 테스트."""
        with patch('mcp_github.tools_read.GitHubClient') as mock_client_class:
            mock_client_class.return_value = mock_github_client
            
            # open 상태
            result_open = await list_pull_requests("test-owner", "test-repo", "open")
            assert result_open["success"] is True
            
            # closed 상태
            result_closed = await list_pull_requests("test-owner", "test-repo", "closed")
            assert result_closed["success"] is True

    @pytest.mark.asyncio
    async def test_get_pr_diff_success(self, mock_github_client, sample_pr_data):
        """get_pr_diff 성공 테스트."""
        with patch('mcp_github.tools_read.GitHubClient') as mock_client_class:
            mock_client_class.return_value = mock_github_client
            
            result = await get_pr_diff("test-owner", "test-repo", 1)
            
            assert result["success"] is True
            assert "file_count" in result
            assert "total_additions" in result
            assert "total_deletions" in result
            assert result["file_count"] >= 0

    @pytest.mark.asyncio
    async def test_get_pr_diff_invalid_number(self, mock_github_client):
        """잘못된 PR 번호 테스트."""
        with patch('mcp_github.tools_read.GitHubClient') as mock_client_class:
            mock_client_class.return_value = mock_github_client
            
            # PR 번호를 문자열로 전달해도 정수로 변환되어야 함
            result = await get_pr_diff("test-owner", "test-repo", "1")
            
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_get_file_success(self, mock_github_client, sample_file_data):
        """get_file 성공 테스트."""
        with patch('mcp_github.tools_read.GitHubClient') as mock_client_class:
            mock_client_class.return_value = mock_github_client
            
            result = await get_file("test-owner", "test-repo", "test.py", "main")
            
            assert result["success"] is True
            assert "file_size" in result
            assert "type" in result
            assert result["type"] == "file"

    @pytest.mark.asyncio
    async def test_get_file_with_default_ref(self, mock_github_client):
        """기본 ref(HEAD)로 파일 가져오기 테스트."""
        with patch('mcp_github.tools_read.GitHubClient') as mock_client_class:
            mock_client_class.return_value = mock_github_client
            
            result = await get_file("test-owner", "test-repo", "test.py")
            
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_get_file_directory(self, mock_github_client):
        """디렉토리 가져오기 테스트."""
        with patch('mcp_github.tools_read.GitHubClient') as mock_client_class:
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
            
            result = await get_file("test-owner", "test-repo", "dir")
            
            assert result["success"] is True
            assert result["type"] == "directory"
            assert result["file_count"] == 2

    @pytest.mark.asyncio
    async def test_get_file_binary_file(self, mock_github_client):
        """바이너리 파일 테스트."""
        with patch('mcp_github.tools_read.GitHubClient') as mock_client_class:
            mock_client = Mock()
            mock_repo = Mock()
            mock_repo.full_name = "test-owner/test-repo"
            
            # 바이너리 파일 콘텐츠 모킹
            mock_binary_file = Mock()
            mock_binary_file.name = "image.png"
            mock_binary_file.path = "image.png"
            mock_binary_file.type = "file"
            mock_binary_file.size = 1024 * 1024  # 1MB
            mock_binary_file.encoding = None
            mock_binary_file.decoded_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
            mock_binary_file.html_url = "https://github.com/test-owner/test-repo/blob/main/image.png"
            mock_binary_file.download_url = "https://github.com/test-owner/test-repo/raw/main/image.png"
            
            mock_repo.get_contents.return_value = mock_binary_file
            mock_client.get_repository.return_value = mock_repo
            mock_client_class.return_value = mock_client
            
            result = await get_file("test-owner", "test-repo", "image.png")
            
            assert result["success"] is True
            assert result["type"] == "file"
            # data는 JSON 문자열이므로 파싱해야 함
            import json
            data = json.loads(result["data"])
            assert data["is_binary"] is True
            assert data["content"] is None

    @pytest.mark.asyncio
    async def test_get_file_large_file(self, mock_github_client):
        """큰 파일 테스트 (1MB 이상)."""
        with patch('mcp_github.tools_read.GitHubClient') as mock_client_class:
            mock_client = Mock()
            mock_repo = Mock()
            mock_repo.full_name = "test-owner/test-repo"
            
            # 큰 파일 콘텐츠 모킹
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
            
            result = await get_file("test-owner", "test-repo", "large_file.txt")
            
            assert result["success"] is True
            assert result["type"] == "file"
            # data는 JSON 문자열이므로 파싱해야 함
            import json
            data = json.loads(result["data"])
            assert data["content"] is None
            assert "File too large" in data["content_note"]
