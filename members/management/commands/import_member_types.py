import csv
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from members.models import MemberType


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

        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            created_count = 0
            error_count = 0
            errors = []

            for row_num, row in enumerate(reader, 2):  # Start at 2 (after header)
                try:
                    # Required fields
                    member_type = row.get("member_type", "").strip()
                    if not member_type:
                        errors.append(f"Row {row_num}: Missing member_type")
                        continue

                    # Parse member_dues
                    try:
                        member_dues = Decimal(str(row["member_dues"]).strip())
                    except (ValueError, TypeError):
                        errors.append(
                            f"Row {row_num}: Invalid member_dues '{row.get('member_dues')}'"
                        )
                        continue

                    # Parse num_months
                    try:
                        num_months = int(row["num_months"])
                    except (ValueError, TypeError):
                        errors.append(
                            f"Row {row_num}: Invalid num_months '{row.get('num_months')}'"
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
                        created_count += 1
                        self.stdout.write(f"   ✅ Created: {member_type_obj}")
                    else:
                        self.stdout.write(f"   ⚠️  Exists: {member_type_obj}")

                except Exception as e:
                    errors.append(f"Row {row_num}: Unexpected error - {e}")
                    error_count += 1

        # Show summary
        self.stdout.write("\n📊 Import Summary:")
        self.stdout.write(f"   🏷️  Member types created: {created_count}")
        self.stdout.write(f"   ❌ Errors: {len(errors)}")

        # Show errors if any
        if errors:
            self.stdout.write("\n❌ Errors encountered:")
            for error in errors:
                self.stdout.write(f"   {error}")
