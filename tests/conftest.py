"""Pytest configuration and common fixtures."""

from unittest.mock import Mock

from datetime import datetime
import pytest

from mcp_github.github_client import GitHubClient


@pytest.fixture
def mock_github_client():
    """Mock GitHub client for testing."""
    client = Mock(spec=GitHubClient)

    # Mock repository
    mock_repo = Mock()
    mock_repo.full_name = "test-owner/test-repo"
    mock_repo.description = "Test repository for MCP server"
    mock_repo.language = "Python"
    mock_repo.stargazers_count = 10
    mock_repo.forks_count = 5
    mock_repo.open_issues_count = 2
    mock_repo.id = 12345
    mock_repo.name = "test-repo"
    mock_repo.created_at = datetime(2024, 1, 1)
    mock_repo.updated_at = datetime(2024, 1, 1)
    mock_repo.clone_url = "https://github.com/test-owner/test-repo.git"
    mock_repo.ssh_url = "git@github.com:test-owner/test-repo.git"
    mock_repo.get_topics.return_value = ["python", "mcp"]
    mock_repo.default_branch = "main"
    mock_repo.license = None
    mock_repo.homepage = None
    mock_repo.archived = False
    mock_repo.disabled = False
    mock_repo.private = False
    mock_repo.fork = False
    mock_repo.size = 1024
    mock_repo.html_url = "https://github.com/test-owner/test-repo"

    # Mock pull request
    mock_pr = Mock()
    mock_pr.title = "Test PR"
    mock_pr.user.login = "test-user"
    mock_pr.state = "open"
    mock_pr.number = 1
    mock_pr.created_at = datetime(2024, 1, 1)
    mock_pr.updated_at = datetime(2024, 1, 1)
    mock_pr.merged_at = None
    mock_pr.closed_at = None
    mock_pr.draft = False
    mock_pr.mergeable = True
    mock_pr.mergeable_state = "clean"
    mock_pr.comments = 0
    mock_pr.commits = 1
    mock_pr.additions = 10
    mock_pr.deletions = 5
    mock_pr.changed_files = 1
    mock_pr.html_url = "https://github.com/test-owner/test-repo/pull/1"

    # Mock file
    mock_file = Mock()
    mock_file.filename = "test.py"
    mock_file.status = "modified"
    mock_file.additions = 10
    mock_file.deletions = 5
    mock_file.changes = 15
    mock_file.patch = "@@ -1,1 +1,1 @@\n-old line\n+new line\n"
    mock_file.raw_url = "https://github.com/test-owner/test-repo/raw/main/test.py"

    # Mock file content
    mock_file_content = Mock()
    mock_file_content.name = "test.py"
    mock_file_content.path = "test.py"
    mock_file_content.type = "file"
    mock_file_content.size = 100
    mock_file_content.encoding = "utf-8"
    mock_file_content.html_url = (
        "https://github.com/test-owner/test-repo/blob/main/test.py"
    )
    mock_file_content.download_url = (
        "https://github.com/test-owner/test-repo/raw/main/test.py"
    )
    mock_file_content.decoded_content = b"print('Hello, World!')"

    # Setup mock methods
    client.get_repository.return_value = mock_repo
    mock_repo.get_pull.return_value = mock_pr
    mock_pr.get_files.return_value = [mock_file]
    mock_repo.get_contents.return_value = mock_file_content
    
    # get_pulls 메서드 설정 (iterable mock)
    mock_pulls = Mock()
    mock_pulls.__iter__ = lambda self: iter([mock_pr])
    mock_pulls.__len__ = lambda self: 1
    mock_repo.get_pulls.return_value = mock_pulls

    return client


@pytest.fixture
def sample_repo_data():
    """Sample repository data for testing."""
    return {
        "owner": "test-owner",
        "repo": "test-repo",
        "name": "test-repo",
        "description": "Test repository for MCP server",
        "language": "Python",
        "stars": 10,
        "forks": 5,
        "issues": 2,
    }


@pytest.fixture
def sample_pr_data():
    """Sample pull request data for testing."""
    return {
        "owner": "test-owner",
        "repo": "test-repo",
        "number": 1,
        "title": "Test PR",
        "author": "test-user",
        "state": "open",
        "files_changed": 1,
        "additions": 10,
        "deletions": 5,
    }


@pytest.fixture
def sample_file_data():
    """Sample file data for testing."""
    return {
        "owner": "test-owner",
        "repo": "test-repo",
        "path": "test.py",
        "ref": "main",
        "name": "test.py",
        "size": 100,
        "type": "file",
        "is_text": True,
    }


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("ENABLE_WRITE", "false")
    return {"GITHUB_TOKEN": "test-token", "ENABLE_WRITE": "false"}
