"""
Tests for backup database management command.
"""

from unittest.mock import patch
from io import StringIO
from django.core.management import call_command


class TestBackupDatabaseCommand:
    """Test backup_database management command."""

    @patch("members.management.commands.backup_database.create_backup")
    def test_command_creates_backup_success(self, mock_create_backup):
        """Test command creates backup successfully."""
        mock_create_backup.return_value = {
            "success": True,
            "filename": "backup_dev_2025-01-15_14-30-00.json",
            "filepath": "backups/dev/backup_dev_2025-01-15_14-30-00.json",
            "size": 5000,
            "db_type": "dev",
            "error": None,
        }

        out = StringIO()
        call_command("backup_database", stdout=out)

        output = out.getvalue()
        assert "Backup created" in output
        assert "backup_dev_2025-01-15_14-30-00.json" in output
        assert "5,000" in output  # Number is formatted with comma
        assert "dev" in output

    @patch("members.management.commands.backup_database.create_backup")
    def test_command_handles_failure(self, mock_create_backup):
        """Test command handles backup failure."""
        mock_create_backup.return_value = {
            "success": False,
            "filename": None,
            "filepath": None,
            "size": None,
            "db_type": "dev",
            "error": "Export failed",
        }

        out = StringIO()
        call_command("backup_database", stdout=out)

        output = out.getvalue()
        assert "Backup failed" in output
        assert "Export failed" in output
