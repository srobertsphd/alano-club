import csv
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from members.models import MemberType
from .import_logger import ImportLogger


class Command(BaseCommand):
    help = "Import member types from current_member_types.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv-file",
            type=str,
            default="data/2025_09_02/cleaned/current_member_types.csv",
            help="Path to member types CSV file",
        )
        parser.add_argument(
            "--clear-existing",
            action="store_true",
            help="Clear existing member types before import",
        )

    def handle(self, *args, **options):
        csv_file = Path(options["csv_file"])

        if not csv_file.exists():
            raise CommandError(f"CSV file not found: {csv_file}")

        if options["clear_existing"]:
            self.stdout.write("🗑️  Clearing existing member types...")
            MemberType.objects.all().delete()
            self.stdout.write("   ✅ Member types cleared")

        try:
            with transaction.atomic():
                self.import_member_types(csv_file)
                self.stdout.write(
                    self.style.SUCCESS(
                        "\n✅ Member types import completed successfully!"
                    )
                )

        except Exception as e:
            raise CommandError(f"Import failed: {e}")

    def import_member_types(self, csv_file):
        """Import member types from CSV file"""
        self.stdout.write(f"\n🏷️  Importing member types from: {csv_file}")

        # Initialize enhanced logger
        logger = ImportLogger("import_member_types", csv_file)

        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row_num, row in enumerate(reader, 2):  # Start at 2 (after header)
                try:
                    # Required fields
                    member_type = row.get("member_type", "").strip()
                    if not member_type:
                        logger.log_error(row_num, "Missing member_type", row)
                        continue

                    # Parse member_dues
                    try:
                        member_dues = Decimal(str(row["member_dues"]).strip())
                    except (ValueError, TypeError):
                        logger.log_error(
                            row_num,
                            f"Invalid member_dues '{row.get('member_dues')}'",
                            row,
                        )
                        continue

                    # Parse num_months
                    try:
                        num_months = int(row["num_months"])
                    except (ValueError, TypeError):
                        logger.log_error(
                            row_num,
                            f"Invalid num_months '{row.get('num_months')}'",
                            row,
                        )
                        continue

                    # Create or get member type
                    member_type_obj, created = MemberType.objects.get_or_create(
                        member_type=member_type,
                        defaults={
                            "member_dues": member_dues,
                            "num_months": num_months,
                        },
                    )

                    if created:
                        logger.log_success(
                            row_num,
                            f"Created member type: {member_type}",
                            member_type_obj,
                        )
                        if logger.created_count <= 5:  # Show first 5 on console
                            self.stdout.write(f"   ✅ Created: {member_type_obj}")
                    else:
                        logger.log_skipped(
                            row_num, f"Member type already exists: {member_type}", row
                        )
                        if logger.skipped_count <= 5:  # Show first 5 on console
                            self.stdout.write(f"   ⚠️  Exists: {member_type_obj}")

                except Exception as e:
                    logger.log_error(row_num, f"Unexpected error - {e}", row)

        # Write detailed logs to files
        logger.write_summary()

        # Show console summary
        logger.print_console_summary(self.stdout)
