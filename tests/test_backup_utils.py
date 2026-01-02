"""
Tests for backup utility functions.
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from members.backup_utils import (
    create_backup,
    _detect_database_type,
)


class TestDetectDatabaseType:
    """Test database type detection."""

    @patch("members.backup_utils.settings")
    @patch.dict(
        os.environ,
        {
            "DATABASE_URL_PROD": "postgresql://postgres.xxx@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
        },
    )
    def test_detects_prod_when_host_in_prod_url(self, mock_settings):
        """Test detects production when host matches production URL."""
        mock_settings.DATABASES = {
            "default": {"HOST": "aws-0-us-east-1.pooler.supabase.com"}
        }
        assert _detect_database_type() == "prod"

    @patch("members.backup_utils.settings")
    @patch.dict(
        os.environ,
        {
            "DATABASE_URL_PROD": "postgresql://postgres.xxx@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
        },
    )
    def test_detects_dev_when_host_not_in_prod_url(self, mock_settings):
        """Test detects dev when host doesn't match production URL."""
        mock_settings.DATABASES = {
            "default": {"HOST": "aws-0-us-west-2.pooler.supabase.com"}
        }
        assert _detect_database_type() == "dev"

    @patch("members.backup_utils.settings")
    @patch.dict(os.environ, {}, clear=True)
    def test_detects_dev_when_no_prod_url(self, mock_settings):
        """Test defaults to dev when no production URL configured."""
        mock_settings.DATABASES = {"default": {"HOST": "some-host"}}
        assert _detect_database_type() == "dev"


class TestCreateBackup:
    """Test backup creation."""

    @patch("members.backup_utils.os.path.getsize")
    @patch("members.backup_utils.subprocess.run")
    @patch("members.backup_utils._detect_database_type")
    @patch("members.backup_utils._ensure_backup_directory")
    def test_create_backup_success(
        self, mock_dir, mock_detect, mock_subprocess, mock_getsize
    ):
        """Test successful backup creation."""
        mock_detect.return_value = "dev"
        mock_backup_dir = Path("backups/dev")
        mock_dir.return_value = mock_backup_dir

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"model": "members.member", "pk": 1, "fields": {}}' * 10
        mock_subprocess.return_value = mock_result
        mock_getsize.return_value = 1000

        result = create_backup()

        assert result["success"] is True
        assert result["filename"] is not None
        assert result["filename"].startswith("backup_dev_")
        assert result["filename"].endswith(".json")
        assert result["db_type"] == "dev"
        assert result["error"] is None

    @patch("members.backup_utils.subprocess.run")
    @patch("members.backup_utils._detect_database_type")
    def test_create_backup_failure(self, mock_detect, mock_subprocess):
        """Test backup creation failure."""
        mock_detect.return_value = "dev"

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error occurred"
        mock_subprocess.return_value = mock_result

        result = create_backup()

        assert result["success"] is False
        assert result["error"] == "Error occurred"

    @patch("members.backup_utils.subprocess.run")
    @patch("members.backup_utils._detect_database_type")
    def test_create_backup_empty_output(self, mock_detect, mock_subprocess):
        """Test backup creation with empty output."""
        mock_detect.return_value = "dev"

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_subprocess.return_value = mock_result

        result = create_backup()

        assert result["success"] is False
        assert "empty" in result["error"].lower()
