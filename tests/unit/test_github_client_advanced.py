"""GitHub 클라이언트 고급 테스트."""

import pytest
from unittest.mock import patch

from mcp_github.github_client import GitHubClient


class TestGitHubClientAdvanced:
    """GitHub 클라이언트 고급 기능 테스트."""

    @patch("mcp_github.github_client.Github")
    def test_get_repository_with_connection_error(self, mock_github):
        """연결 에러 시 에러 처리 테스트."""
        mock_github.side_effect = Exception("Connection failed")
        
        # 초기화 실패를 예상하고 테스트
        with pytest.raises(Exception) as exc_info:
            GitHubClient()
        
        assert "Connection failed" in str(exc_info.value)

    @patch("mcp_github.github_client.Github")
    def test_get_repository_with_network_timeout(self, mock_github):
        """네트워크 타임아웃 에러 처리 테스트."""
        mock_github.side_effect = TimeoutError("Request timeout")
        
        # 초기화 실패를 예상하고 테스트
        with pytest.raises(TimeoutError) as exc_info:
            GitHubClient()
        
        assert "Request timeout" in str(exc_info.value)

    @patch("mcp_github.github_client.Github")
    def test_get_repository_with_authentication_error(self, mock_github):
        """인증 에러 처리 테스트."""
        mock_github.side_effect = Exception("Bad credentials")
        
        # 초기화 실패를 예상하고 테스트
        with pytest.raises(Exception) as exc_info:
            GitHubClient()
        
        assert "Bad credentials" in str(exc_info.value)

    @patch("mcp_github.github_client.Github")
    def test_get_repository_with_rate_limit_error(self, mock_github):
        """Rate limit 에러 처리 테스트."""
        mock_github.side_effect = Exception("API rate limit exceeded")
        
        # 초기화 실패를 예상하고 테스트
        with pytest.raises(Exception) as exc_info:
            GitHubClient()
        
        assert "API rate limit exceeded" in str(exc_info.value)

    @patch("mcp_github.github_client.Github")
    def test_get_repository_with_server_error(self, mock_github):
        """서버 에러 처리 테스트."""
        mock_github.side_effect = Exception("Internal server error")
        
        # 초기화 실패를 예상하고 테스트
        with pytest.raises(Exception) as exc_info:
            GitHubClient()
        
        assert "Internal server error" in str(exc_info.value)
