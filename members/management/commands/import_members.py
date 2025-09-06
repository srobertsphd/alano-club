import csv
from datetime import timedelta
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.dateparse import parse_date

from members.models import Member, MemberType
from .import_logger import ImportLogger


class Command(BaseCommand):
    help = "Import members from current_members.csv (active) and current_dead.csv (inactive)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--members-csv",
            type=str,
            default="data/2025_09_02/cleaned/current_members.csv",
            help="Path to active members CSV file",
        )
        parser.add_argument(
            "--dead-csv",
            type=str,
            default="data/2025_09_02/cleaned/current_dead.csv",
            help="Path to inactive members CSV file",
        )
        parser.add_argument(
            "--clear-existing",
            action="store_true",
            help="Clear existing members before import",
        )

    def handle(self, *args, **options):
        members_csv = Path(options["members_csv"])
        dead_csv = Path(options["dead_csv"])

        if not members_csv.exists():
            raise CommandError(f"Active members CSV file not found: {members_csv}")

        if not dead_csv.exists():
            raise CommandError(f"Inactive members CSV file not found: {dead_csv}")

        if options["clear_existing"]:
            self.stdout.write("🗑️  Clearing existing members...")
            Member.objects.all().delete()
            self.stdout.write("   ✅ Members cleared")

        try:
            with transaction.atomic():
                # Import active members first
                active_count = self.import_active_members(members_csv)

                # Import inactive members second (with duplicate checking)
                inactive_count, duplicates_count = self.import_inactive_members(
                    dead_csv
                )

                self.stdout.write(
                    self.style.SUCCESS("\n✅ Member import completed successfully!")
                )
                self.stdout.write(f"   👥 Active members imported: {active_count}")
                self.stdout.write(f"   💀 Inactive members imported: {inactive_count}")
                if duplicates_count > 0:
                    self.stdout.write(f"   ⚠️  Duplicates skipped: {duplicates_count}")

        except Exception as e:
            raise CommandError(f"Import failed: {e}")

    def import_active_members(self, csv_file):
        """Import active members from current_members.csv"""
        self.stdout.write(f"\n👥 Importing ACTIVE members from: {csv_file}")

        # Initialize enhanced logger
        logger = ImportLogger("import_active_members", csv_file)

        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row_num, row in enumerate(reader, 2):  # Start at 2 (after header)
                try:
                    member = self.create_member_from_row(
                        row, row_num, logger, is_active=True
                    )
                    if member:
                        logger.log_success(
                            row_num,
                            f"Created active member: {member.full_name} (ID: {member.member_id})",
                            member,
                        )
                        if logger.created_count <= 5:  # Show first 5
                            self.stdout.write(f"   ✅ Created: {member}")

                except Exception as e:
                    logger.log_error(row_num, f"Unexpected error - {e}", row)

        # Write detailed logs
        logger.write_summary()
        logger.print_console_summary(self.stdout)

        return logger.created_count

    def import_inactive_members(self, csv_file):
        """Import inactive members from current_dead.csv"""
        self.stdout.write(f"\n💀 Importing INACTIVE members from: {csv_file}")

        # Initialize enhanced logger
        logger = ImportLogger("import_inactive_members", csv_file)

        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row_num, row in enumerate(reader, 2):  # Start at 2 (after header)
                try:
                    first_name = row.get("first_name", "").strip()
                    last_name = row.get("last_name", "").strip()

                    # Check for duplicate (same first_name + last_name as active member)
                    if Member.objects.filter(
                        first_name__iexact=first_name, last_name__iexact=last_name
                    ).exists():
                        logger.log_duplicate(
                            row_num,
                            f"Member already exists: {first_name} {last_name}",
                            row,
                        )
                        if logger.duplicate_count <= 5:  # Show first 5 duplicates
                            self.stdout.write(
                                f"   ⚠️  Duplicate skipped: {first_name} {last_name}"
                            )
                        continue

                    member = self.create_member_from_row(
                        row, row_num, logger, is_active=False
                    )
                    if member:
                        logger.log_success(
                            row_num,
                            f"Created inactive member: {member.full_name} (Preferred ID: {member.preferred_member_id})",
                            member,
                        )
                        if logger.created_count <= 5:  # Show first 5
                            self.stdout.write(f"   ✅ Created: {member}")

                except Exception as e:
                    logger.log_error(row_num, f"Unexpected error - {e}", row)

        # Write detailed logs
        logger.write_summary({"Total duplicates skipped": logger.duplicate_count})
        logger.print_console_summary(self.stdout)

        return logger.created_count, logger.duplicate_count

    def create_member_from_row(self, row, row_num, logger, is_active=True):
        """Create a member from CSV row data"""
        # Required fields
        first_name = row.get("first_name", "").strip()
        last_name = row.get("last_name", "").strip()
        member_type_name = row.get("member_type", "").strip()

        if not first_name or not last_name:
            logger.log_error(row_num, "Missing first_name or last_name", row)
            return None

        if not member_type_name:
            logger.log_error(row_num, "Missing member_type", row)
            return None

        # Get member type
        try:
            member_type = MemberType.objects.get(member_type=member_type_name)
        except MemberType.DoesNotExist:
            logger.log_error(
                row_num, f"Member type '{member_type_name}' not found", row
            )
            return None

        # Parse dates
        date_joined = parse_date(row.get("date_joined", ""))
        if not date_joined:
            logger.log_error(row_num, "Invalid or missing date_joined", row)
            return None

        expiration_date = parse_date(row.get("expiration_date", ""))
        if not expiration_date:
            logger.log_error(row_num, "Invalid or missing expiration_date", row)
            return None

        milestone_date = None
        if row.get("milestone_date"):
            milestone_date = parse_date(row.get("milestone_date"))

        # Handle member_id and status
        csv_member_id = row.get("member_id", "").strip()
        member_id = None
        preferred_member_id = None
        status = "active" if is_active else "inactive"
        date_inactivated = None

        if csv_member_id and csv_member_id.isdigit():
            csv_member_id_int = int(csv_member_id)
            if is_active:
                # Active member keeps their ID
                member_id = csv_member_id_int
                preferred_member_id = csv_member_id_int
            else:
                # Inactive member: ID goes to preferred, member_id becomes None
                member_id = None
                preferred_member_id = csv_member_id_int
                # Calculate date_inactivated as expiration_date + 3 months
                date_inactivated = expiration_date + timedelta(days=90)

        # Create member
        member = Member.objects.create(
            # Identity
            member_id=member_id,
            preferred_member_id=preferred_member_id,
            # Basic info
            first_name=first_name,
            last_name=last_name,
            email=row.get("email", "").strip(),
            # Membership info
            member_type=member_type,
            status=status,
            expiration_date=expiration_date,
            # Dates
            milestone_date=milestone_date,
            date_joined=date_joined,
            date_inactivated=date_inactivated,
            # Contact info
            home_address=row.get("home_address", "").strip(),
            home_city=row.get("home_city", "").strip(),
            home_state=row.get("home_state", "").strip(),
            home_zip=row.get("home_zip", "").strip(),
            home_phone=row.get("home_phone", "").strip(),
        )

        return member
