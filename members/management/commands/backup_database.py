"""
Django management command to create database backups.

Usage:
    python manage.py backup_database

This command:
1. Detects current database type (dev or prod)
2. Creates JSON backup using dumpdata
3. Saves to backups/{db_type}/ directory with timestamp
"""

from django.core.management.base import BaseCommand
from members.backup_utils import create_backup


class Command(BaseCommand):
    help = "Create database backup"

    def add_arguments(self, parser):
        parser.add_argument(
            "--db-type",
            choices=["dev", "prod"],
            help="Database type (auto-detected if not provided)",
        )

    def handle(self, *args, **options):
        db_type = options.get("db_type")
        result = create_backup(db_type=db_type)

        if result["success"]:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Backup created: {result['filename']} ({result['size']:,} bytes)"
                )
            )
            self.stdout.write(f"  Location: {result['filepath']}")
            self.stdout.write(f"  Database: {result['db_type']}")
        else:
            self.stdout.write(self.style.ERROR(f"✗ Backup failed: {result['error']}"))
