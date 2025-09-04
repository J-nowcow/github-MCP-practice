"""Unit tests for GitHub write tools."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from mcp_github.tools_write import (
    create_or_update_file,
    delete_file,
    create_branch,
    create_commit_with_multiple_files,
    get_repository_status
)


class TestCreateOrUpdateFile:
    """Test create_or_update_file function."""

    @pytest.mark.asyncio
    @patch('mcp_github.tools_write.GitHubClient')
    @patch('mcp_github.tools_write.validate_file_path')
    async def test_create_file_success(self, mock_validate, mock_client_class):
        """Test successful file creation."""
        # Setup
        mock_validate.return_value = True
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_repo = Mock()
        mock_client.get_repository.return_value = mock_repo
        
        # File doesn't exist
        mock_repo.get_contents.side_effect = Exception("File not found")
        
        mock_result = Mock()
        mock_result.commit.sha = "abc123"
        mock_result.content.html_url = "https://github.com/test/file"
        mock_repo.create_file.return_value = mock_result
        
        # Execute
        result = await create_or_update_file(
            "testowner", "testrepo", "test.txt", "content", "test commit"
        )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["operation"] == "created"
        assert result["data"]["path"] == "test.txt"
        assert result["data"]["commit_sha"] == "abc123"

    @pytest.mark.asyncio
    @patch('mcp_github.tools_write.GitHubClient')
    @patch('mcp_github.tools_write.validate_file_path')
    async def test_update_file_success(self, mock_validate, mock_client_class):
        """Test successful file update."""
        # Setup
        mock_validate.return_value = True
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_repo = Mock()
        mock_client.get_repository.return_value = mock_repo
        
        # File exists
        mock_file = Mock()
        mock_file.sha = "def456"
        mock_repo.get_contents.return_value = mock_file
        
        mock_result = Mock()
        mock_result.commit.sha = "ghi789"
        mock_result.content.html_url = "https://github.com/test/file"
        mock_repo.create_file.return_value = mock_result
        
        # Execute
        result = await create_or_update_file(
            "testowner", "testrepo", "test.txt", "new content", "test update"
        )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["operation"] == "updated"
        assert result["data"]["path"] == "test.txt"
        assert result["data"]["commit_sha"] == "ghi789"

    @pytest.mark.asyncio
    @patch('mcp_github.tools_write.validate_file_path')
    async def test_invalid_file_path(self, mock_validate):
        """Test file creation with invalid path."""
        # Setup
        mock_validate.return_value = False
        
        # Execute
        result = await create_or_update_file(
            "testowner", "testrepo", "invalid/path", "content", "test commit"
        )
        
        # Assert
        assert result["success"] is False
        assert "Invalid file path" in result["error"]


class TestDeleteFile:
    """Test delete_file function."""

    @pytest.mark.asyncio
    @patch('mcp_github.tools_write.GitHubClient')
    async def test_delete_file_success(self, mock_client_class):
        """Test successful file deletion."""
        # Setup
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_repo = Mock()
        mock_client.get_repository.return_value = mock_repo
        
        mock_file = Mock()
        mock_file.sha = "abc123"
        mock_repo.get_contents.return_value = mock_file
        
        mock_result = Mock()
        mock_result.commit.sha = "def456"
        mock_repo.delete_file.return_value = mock_result
        
        # Execute
        result = await delete_file(
            "testowner", "testrepo", "test.txt", "delete commit"
        )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["operation"] == "deleted"
        assert result["data"]["path"] == "test.txt"
        assert result["data"]["commit_sha"] == "def456"


class TestCreateBranch:
    """Test create_branch function."""

    @pytest.mark.asyncio
    @patch('mcp_github.tools_write.GitHubClient')
    async def test_create_branch_success(self, mock_client_class):
        """Test successful branch creation."""
        # Setup
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_repo = Mock()
        mock_client.get_repository.return_value = mock_repo
        
        mock_branch = Mock()
        mock_branch.commit.sha = "abc123"
        mock_repo.get_branch.return_value = mock_branch
        
        # Execute
        result = await create_branch(
            "testowner", "testrepo", "feature-branch", "main"
        )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["operation"] == "branch_created"
        assert result["data"]["new_branch"] == "feature-branch"
        assert result["data"]["base_branch"] == "main"


class TestCreateCommitWithMultipleFiles:
    """Test create_commit_with_multiple_files function."""

    @pytest.mark.asyncio
    @patch('mcp_github.tools_write.GitHubClient')
    async def test_create_commit_success(self, mock_client_class):
        """Test successful multi-file commit creation."""
        # Setup
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_repo = Mock()
        mock_client.get_repository.return_value = mock_repo
        
        mock_branch = Mock()
        mock_branch.commit.sha = "abc123"
        mock_branch.commit.commit.tree = Mock()
        mock_repo.get_branch.return_value = mock_branch
        
        mock_blob = Mock()
        mock_blob.sha = "def456"
        mock_repo.create_git_blob.return_value = mock_blob
        
        mock_tree = Mock()
        mock_repo.create_git_tree.return_value = mock_tree
        
        mock_commit = Mock()
        mock_commit.sha = "ghi789"
        mock_repo.create_git_commit.return_value = mock_commit
        
        files = [
            {"path": "file1.txt", "content": "content1", "operation": "create"},
            {"path": "file2.txt", "content": "content2", "operation": "update"}
        ]
        
        # Execute
        result = await create_commit_with_multiple_files(
            "testowner", "testrepo", files, "multi-file commit"
        )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["operation"] == "multi_file_commit"
        assert result["data"]["commit_sha"] == "ghi789"
        assert result["data"]["files_processed"] == 2


class TestGetRepositoryStatus:
    """Test get_repository_status function."""

    @pytest.mark.asyncio
    @patch('mcp_github.tools_write.GitHubClient')
    async def test_get_status_success(self, mock_client_class):
        """Test successful repository status retrieval."""
        # Setup
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_repo = Mock()
        mock_repo.default_branch = "main"
        mock_client.get_repository.return_value = mock_repo
        
        mock_commit = Mock()
        mock_commit.sha = "abc123"
        mock_commit.commit.message = "test commit"
        mock_commit.commit.author.name = "Test User"
        mock_commit.commit.author.date.isoformat.return_value = "2024-01-01T00:00:00"
        mock_commit.files = []
        mock_commit.stats.additions = 5
        mock_commit.stats.deletions = 2
        mock_repo.get_commit.return_value = mock_commit
        
        mock_branch = Mock()
        mock_branch.name = "main"
        mock_repo.get_branch.return_value = mock_branch
        
        # Execute
        result = await get_repository_status("testowner", "testrepo")
        
        # Assert
        assert result["success"] is True
        assert result["data"]["commit_sha"] == "abc123"
        assert result["data"]["branch"] == "main"
        assert result["data"]["is_default_branch"] is True
        assert result["data"]["additions"] == 5
        assert result["data"]["deletions"] == 2
