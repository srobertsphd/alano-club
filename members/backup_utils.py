"""
Utility functions for database backups.

These functions handle creating and managing database backups using Django's dumpdata.
"""

import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from django.conf import settings


def _detect_database_type():
    """Detect if current database is dev or prod based on DATABASE_URL."""
    current_db = settings.DATABASES["default"]
    current_host = current_db.get("HOST", "")

    # Check if we're connected to production
    prod_url = os.getenv("DATABASE_URL_PROD", "")
    if prod_url and current_host in prod_url:
        return "prod"

    # Default to dev if not production
    return "dev"


def _ensure_backup_directory(db_type):
    """Ensure backup directory exists, create if missing."""
    backup_dir = Path("backups") / db_type
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def create_backup(db_type=None):
    """
    Create backup of current database.

    Args:
        db_type: Optional database type ('dev' or 'prod'). If not provided, auto-detects.

    Returns:
        dict: {
            'success': bool,
            'filepath': str or None,
            'filename': str or None,
            'size': int or None,
            'db_type': str or None,
            'error': str or None
        }
    """
    try:
        # Use provided db_type or detect database type
        if db_type is None:
            db_type = _detect_database_type()

        # Ensure backup directory exists
        backup_dir = _ensure_backup_directory(db_type)

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"backup_{db_type}_{timestamp}.json"
        filepath = backup_dir / filename

        # Prepare environment for subprocess
        env = os.environ.copy()
        # If db_type is 'prod', use DATABASE_URL_PROD for the backup
        if db_type == "prod":
            prod_url = os.getenv("DATABASE_URL_PROD")
            if prod_url:
                env["DATABASE_URL"] = prod_url
            else:
                return {
                    "success": False,
                    "filepath": None,
                    "filename": None,
                    "size": None,
                    "db_type": db_type,
                    "error": "DATABASE_URL_PROD not set in environment",
                }

        # Run dumpdata command
        result = subprocess.run(
            [
                sys.executable,
                "manage.py",
                "dumpdata",
                "--natural-foreign",
                "--natural-primary",
                "--exclude=auth.Permission",
                "--exclude=admin.LogEntry",
                "--exclude=sessions.Session",
            ],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            env=env,
        )

        if result.returncode != 0:
            return {
                "success": False,
                "filepath": None,
                "filename": None,
                "size": None,
                "db_type": db_type,
                "error": result.stderr or "Unknown error",
            }

        # Check if we got data
        if not result.stdout or len(result.stdout.strip()) < 100:
            return {
                "success": False,
                "filepath": None,
                "filename": None,
                "size": None,
                "db_type": db_type,
                "error": "Export seems empty or very small",
            }

        # Write to file
        with open(filepath, "w") as f:
            f.write(result.stdout)

        file_size = os.path.getsize(filepath)

        return {
            "success": True,
            "filepath": str(filepath),
            "filename": filename,
            "size": file_size,
            "db_type": db_type,
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "filepath": None,
            "filename": None,
            "size": None,
            "db_type": None,
            "error": str(e),
        }
