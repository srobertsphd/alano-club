import csv
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.dateparse import parse_date

from members.models import Member, PaymentMethod, Payment
from .import_logger import ImportLogger


class Command(BaseCommand):
    help = "Import payments from current_payments.csv, linking to existing members"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv-file",
            type=str,
            default="data/2025_09_02/cleaned/current_payments.csv",
            help="Path to payments CSV file",
        )
        parser.add_argument(
            "--clear-existing",
            action="store_true",
            help="Clear existing payments before import",
        )

    def handle(self, *args, **options):
        csv_file = Path(options["csv_file"])

        if not csv_file.exists():
            raise CommandError(f"CSV file not found: {csv_file}")

        if options["clear_existing"]:
            self.stdout.write("🗑️  Clearing existing payments...")
            Payment.objects.all().delete()
            self.stdout.write("   ✅ Payments cleared")

        try:
            with transaction.atomic():
                created_count = self.import_payments(csv_file)
                self.stdout.write(
                    self.style.SUCCESS("\n✅ Payment import completed successfully!")
                )
                self.stdout.write(f"   💰 Payments imported: {created_count}")

        except Exception as e:
            raise CommandError(f"Import failed: {e}")

    def import_payments(self, csv_file):
        """Import payments from CSV file"""
        self.stdout.write(f"\n💰 Importing payments from: {csv_file}")

        # Initialize enhanced logger
        logger = ImportLogger("import_payments", csv_file)

        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row_num, row in enumerate(reader, 2):  # Start at 2 (after header)
                try:
                    # Skip rows without payment data
                    if not row.get("payment_amount") or not row.get("payment_date"):
                        logger.log_skipped(
                            row_num, "Missing payment_amount or payment_date", row
                        )
                        continue

                    # 1. Find member by member_id first, then by name as fallback
                    member = self.find_member(row, row_num, logger)
                    if not member:
                        continue

                    # 2. Find payment method
                    payment_method = self.find_payment_method(row, row_num, logger)
                    if not payment_method:
                        continue

                    # 3. Parse payment amount
                    try:
                        amount = Decimal(str(row["payment_amount"]).strip())
                    except (ValueError, TypeError):
                        logger.log_error(
                            row_num,
                            f"Invalid payment amount '{row.get('payment_amount')}'",
                            row,
                        )
                        continue

                    # 4. Parse payment date
                    payment_date = parse_date(row["payment_date"])
                    if not payment_date:
                        logger.log_error(
                            row_num,
                            f"Invalid payment date '{row.get('payment_date')}'",
                            row,
                        )
                        continue

                    # 5. Get receipt number (optional)
                    receipt_number = row.get("receipt_number", "").strip()

                    # 6. Check for duplicate payments (same member, amount, date)
                    existing_payment = Payment.objects.filter(
                        member=member, amount=amount, date=payment_date
                    ).first()

                    if existing_payment:
                        logger.log_duplicate(
                            row_num,
                            f"Payment already exists: ${amount} on {payment_date} for {member.full_name}",
                            row,
                        )
                        if logger.duplicate_count <= 5:  # Show first 5 duplicates
                            self.stdout.write(
                                f"   ⚠️  Duplicate skipped: ${amount} on {payment_date} for {member.full_name}"
                            )
                    else:
                        # Create payment
                        payment = Payment.objects.create(
                            member=member,
                            payment_method=payment_method,
                            amount=amount,
                            date=payment_date,
                            receipt_number=receipt_number,
                        )
                        logger.log_success(
                            row_num,
                            f"Created payment: ${amount} on {payment_date} for {member.full_name}",
                            payment,
                        )

                        if logger.created_count <= 5:  # Show first 5 created
                            self.stdout.write(f"   ✅ Created: {payment}")

                except Exception as e:
                    logger.log_error(row_num, f"Unexpected error - {e}", row)

        # Write detailed logs
        logger.write_summary({"Total duplicates skipped": logger.duplicate_count})
        logger.print_console_summary(self.stdout)

        return logger.created_count

    def find_member(self, row, row_num, logger):
        """Find member by member_id first, then by name"""
        member_id = row.get("member_id")
        first_name = row.get("first_name", "").strip()
        last_name = row.get("last_name", "").strip()

        # Try to find by member_id first (for active members)
        if member_id:
            try:
                member_id_int = int(member_id)
                member = Member.objects.filter(member_id=member_id_int).first()
                if member:
                    return member
            except (ValueError, TypeError):
                pass

        # Fallback to name lookup (for both active and inactive members)
        if first_name and last_name:
            member = Member.objects.filter(
                first_name__iexact=first_name, last_name__iexact=last_name
            ).first()

            if member:
                return member

        # Member not found
        error_msg = "Member not found - "
        if member_id:
            error_msg += f"ID: {member_id}, "
        error_msg += f"Name: {first_name} {last_name}"
        logger.log_error(row_num, error_msg, row)
        return None

    def find_payment_method(self, row, row_num, logger):
        """Find payment method by name"""
        payment_method_name = row.get("payment_method", "").strip()

        if not payment_method_name:
            logger.log_error(row_num, "Missing payment_method", row)
            return None

        try:
            payment_method = PaymentMethod.objects.get(
                payment_method__iexact=payment_method_name
            )
            return payment_method
        except PaymentMethod.DoesNotExist:
            logger.log_error(
                row_num,
                f"Payment method '{payment_method_name}' not found",
                row,
            )
            return None
        except PaymentMethod.MultipleObjectsReturned:
            # If multiple found, get the first one
            payment_method = PaymentMethod.objects.filter(
                payment_method__iexact=payment_method_name
            ).first()
            return payment_method
